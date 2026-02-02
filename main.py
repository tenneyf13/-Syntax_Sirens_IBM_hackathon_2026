from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="WCAG Checker Backend", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

# --- CORS: allow your frontend domain to call the backend ---
# For hackathon, you can allow "*" temporarily. Better: set to your frontend URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FetchRequest(BaseModel):
    url: HttpUrl

class CheckWCAGRequest(BaseModel):
    url: HttpUrl

@app.get("/")
def root():
    return FileResponse("Frontend/Page/homePage.html")

@app.get("/api")
def api_info():
    return {"message": "WCAG Checker Backend", "version": "1.0.0", "endpoints": ["/health", "/fetch", "/api/check-wcag"]}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/favicon.ico")
def favicon():
    return {"message": "No favicon"}

@app.get("/doc")
def doc_redirect():
    return {"message": "Use /docs for API documentation"}

@app.get("/debug/env")
def debug_env():
    return {
        "watson_api_key_set": bool(os.getenv("WATSON_API_KEY")),
        "ibm_cloud_api_key_set": bool(os.getenv("IBM_CLOUD_API_KEY")),
        "agent_endpoint_set": bool(os.getenv("AGENT_ENDPOINT_URL")),
        "watson_url": os.getenv("WATSON_URL", "Not set")
    }

@app.get("/debug/watson-test")
async def test_watson_connection():
    """Test Watson connection and authentication."""
    agent_api_key = os.getenv("Agent_API_KEY")
    ibm_cloud_api_key = os.getenv("IBM_CLOUD_API_KEY")
    agent_endpoint = os.getenv("AGENT_ENDPOINT_URL")
    
    results = {
        "agent_api_key_set": bool(agent_api_key),
        "ibm_cloud_api_key_set": bool(ibm_cloud_api_key),
        "agent_endpoint": agent_endpoint
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Get IBM Cloud access token first
            if ibm_cloud_api_key:
                token_data = {
                    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                    "apikey": ibm_cloud_api_key
                }
                
                token_response = await client.post(
                    "https://iam.cloud.ibm.com/identity/token",
                    data=token_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                results["ibm_token_test"] = {
                    "status": token_response.status_code,
                    "success": token_response.status_code == 200,
                    "response": "Token obtained" if token_response.status_code == 200 else token_response.text[:200]
                }
                
                # If token obtained, test Watson agent with Bearer token
                if token_response.status_code == 200:
                    access_token = token_response.json()["access_token"]
                    
                    test_payload = {"input": "Test connection"}
                    
                    agent_response = await client.post(
                        agent_endpoint,
                        json=test_payload,
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "application/json"
                        }
                    )
                    
                    results["agent_auth_test"] = {
                        "status": agent_response.status_code,
                        "success": agent_response.status_code == 200,
                        "response": agent_response.text[:200] if agent_response.status_code != 200 else "Success"
                    }
            
            return results
            
    except Exception as e:
        results["error"] = str(e)
        return results

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q, "message": "This is a test endpoint"}

@app.post("/fetch", response_class=PlainTextResponse)
async def fetch(req: FetchRequest):
    """Fetch raw HTML for a URL and return it as text/plain."""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            r = await client.get(
                str(req.url),
                headers={"User-Agent": "WCAG-Audit-Bot/1.0"}
            )
            r.raise_for_status()
            html = r.content.decode(r.encoding or "utf-8", errors="replace")
            return html
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Upstream HTTP error")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Network error fetching URL")


@app.post("/api/check-wcag")
async def check_wcag(req: CheckWCAGRequest):
    """
    Called by your frontend. Fetches HTML, runs analysis, returns JSON:
    { findings: "...", recommendations: "..." }
    """

    # 1) Fetch HTML (reuse internal function via HTTP call OR call fetch logic directly)
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            r = await client.get(str(req.url), headers={"User-Agent": "WCAG-Audit-Bot/1.0"})
            r.raise_for_status()
            html = r.content.decode(r.encoding or "utf-8", errors="replace")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Could not fetch target URL")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Network error fetching target URL")

    # 2) Run your AI analysis
    findings, recommendations = await run_wcag_analysis_watson(html)

    # 3) Return to frontend
    return {
        "findings": findings,
        "recommendations": recommendations
    }


async def run_wcag_analysis_watson(html: str):
    """Analyze HTML using Watson AI for WCAG compliance."""
    ibm_cloud_api_key = os.getenv("IBM_CLOUD_API_KEY")
    agent_endpoint = os.getenv("AGENT_ENDPOINT_URL")
    
    if not all([ibm_cloud_api_key, agent_endpoint]):
        return "Missing IBM Cloud API key or agent endpoint.", "Configure IBM_CLOUD_API_KEY and AGENT_ENDPOINT_URL in your .env file."
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            # Get IBM Cloud access token
            token_data = {
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": ibm_cloud_api_key
            }
            
            token_response = await client.post(
                "https://iam.cloud.ibm.com/identity/token",
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if token_response.status_code != 200:
                return f"Token error: {token_response.status_code} - {token_response.text}", "Failed to get IBM Cloud access token."
            
            access_token = token_response.json()["access_token"]
            
            # Try primary agent endpoint first
            payload = {
                "input": f"Analyze this HTML for WCAG 2.1 AA accessibility compliance. Provide specific findings and recommendations:\n\n{html[:2000]}"
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Try primary endpoint
            agent_response = await client.post(agent_endpoint, json=payload, headers=headers)
            
            if agent_response.status_code == 200:
                result = agent_response.json()
                return parse_watson_response(result)
            
            # Try fallback chat endpoint (as seen in logs)
            fallback_endpoint = agent_endpoint.replace("/agents/", "/api/chat/v1/agents/").replace("/run", "/messages")
            
            chat_payload = {
                "messages": [{
                    "role": "user",
                    "content": f"Analyze this HTML for WCAG 2.1 AA accessibility compliance:\n\n{html[:2000]}"
                }]
            }
            
            fallback_response = await client.post(fallback_endpoint, json=chat_payload, headers=headers)
            
            if fallback_response.status_code == 200:
                result = fallback_response.json()
                return parse_watson_response(result)
            
            # If both fail, return error details
            return f"Both endpoints failed. Primary: {agent_response.status_code}, Fallback: {fallback_response.status_code}", "Watson agent authentication failed."
        
    except httpx.TimeoutException:
        return "Watson request timeout.", "The Watson service took too long to respond."
    except Exception as e:
        return f"Watson connection error: {str(e)}", "Unable to connect to Watson services."

def parse_watson_response(result):
    """Parse Watson response in various formats."""
    if "output" in result:
        return result["output"], "Analysis completed using Watson AI."
    elif "result" in result:
        return result["result"], "Watson AI analysis completed."
    elif "response" in result:
        return result["response"], "Watson response received."
    elif "messages" in result and result["messages"]:
        last_message = result["messages"][-1]
        content = last_message.get("content", str(last_message))
        return content, "Watson chat response received."
    else:
        return str(result), "Raw Watson response."

