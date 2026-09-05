from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import httpx
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the .env file next to this script,
# regardless of what directory uvicorn is started from.
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# Browser-like headers to avoid bot-blocking on target sites
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
}

app = FastAPI(title="WCAG Checker Backend", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

# --- CORS ---
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

@app.get("/debug/env")
def debug_env():
    return {
        "ibm_cloud_api_key_set": bool(os.getenv("IBM_CLOUD_API_KEY")),
        "watsonx_project_id_set": bool(os.getenv("WATSONX_PROJECT_ID")),
        "watsonx_url": os.getenv("WATSONX_URL", "Not set"),
    }

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.post("/fetch", response_class=PlainTextResponse)
async def fetch(req: FetchRequest):
    """Fetch raw HTML for a URL and return it as text/plain."""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            r = await client.get(str(req.url), headers=BROWSER_HEADERS)
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
    Fetches HTML from the given URL, runs WCAG analysis via watsonx.ai,
    and returns { findings, recommendations }.
    """
    # 1) Fetch the target page HTML
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            r = await client.get(str(req.url), headers=BROWSER_HEADERS)
            r.raise_for_status()
            html = r.content.decode(r.encoding or "utf-8", errors="replace")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Could not fetch target URL")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Network error fetching target URL")

    # 2) Analyse with watsonx.ai
    findings, recommendations = await run_wcag_analysis_watsonx(html)

    return {"findings": findings, "recommendations": recommendations}


async def get_iam_token(client: httpx.AsyncClient) -> str:
    """Exchange IBM Cloud API key for a short-lived IAM Bearer token."""
    ibm_cloud_api_key = os.getenv("IBM_CLOUD_API_KEY")
    if not ibm_cloud_api_key:
        raise ValueError("IBM_CLOUD_API_KEY is not set.")

    r = await client.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": ibm_cloud_api_key,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if r.status_code != 200:
        raise ValueError(f"IAM token error {r.status_code}: {r.text[:200]}")
    return r.json()["access_token"]


async def run_wcag_analysis_watsonx(html: str):
    """Analyse HTML using IBM watsonx.ai (ibm/granite-13b-instruct-v2)."""
    project_id = os.getenv("WATSONX_PROJECT_ID")
    watsonx_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

    if not project_id:
        return (
            "Missing WATSONX_PROJECT_ID.",
            "Add WATSONX_PROJECT_ID to your .env file."
        )

    prompt = (
        "You are an expert web accessibility auditor.\n"
        "Analyze the HTML below for WCAG 2.1 Level AA compliance issues.\n\n"
        "Structure your response in TWO clearly labelled sections:\n"
        "1. FINDINGS: List each accessibility issue found, referencing the specific "
        "WCAG criterion (e.g. 1.1.1 Non-text Content, 4.1.2 Name, Role, Value).\n"
        "2. RECOMMENDATIONS: For each finding provide a concrete, actionable fix "
        "with a corrected code snippet where applicable.\n\n"
        f"HTML to audit:\n{html[:4000]}\n\n"
        "Begin your response with 'FINDINGS:'"
    )

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            access_token = await get_iam_token(client)

            payload = {
                "model_id": "meta-llama/llama-3-3-70b-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are an expert web accessibility auditor specialising in WCAG 2.1 Level AA. "
                            "Always structure your response with two clearly labelled sections: "
                            "FINDINGS: and RECOMMENDATIONS:"
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "parameters": {
                    "max_new_tokens": 1024,
                    "temperature": 0.2,
                },
                "project_id": project_id,
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            url = f"{watsonx_url}/ml/v1/text/chat?version=2023-05-29"
            resp = await client.post(url, json=payload, headers=headers)

            if resp.status_code == 200:
                data = resp.json()
                text = (
                    data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    or data.get("results", [{}])[0].get("generated_text", "")
                    or str(data)
                )
                return _split_findings_recommendations(text)

            # Fallback: try mistral-small
            payload["model_id"] = "mistralai/mistral-small-3-1-24b-instruct-2503"
            resp2 = await client.post(url, json=payload, headers=headers)
            if resp2.status_code == 200:
                data = resp2.json()
                text = (
                    data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    or str(data)
                )
                return _split_findings_recommendations(text)

            return (
                f"watsonx.ai error ({resp.status_code}): {resp.text[:300]}",
                "Check WATSONX_PROJECT_ID and WATSONX_URL in your .env file."
            )

    except ValueError as e:
        return str(e), "Check your IBM_CLOUD_API_KEY in the .env file."
    except httpx.TimeoutException:
        return "watsonx.ai request timed out.", "The model took too long. Try again."
    except Exception as e:
        return f"Unexpected error: {str(e)}", "Check server logs for details."


def _split_findings_recommendations(text: str):
    """Split AI response into (findings, recommendations) at the RECOMMENDATIONS marker."""
    lower = text.lower()
    markers = ["2. recommendations", "recommendations:", "recommendation:", "suggested fix",
               "how to fix", "remediation", "actionable fix"]
    for marker in markers:
        idx = lower.find(marker)
        if idx != -1:
            return text[:idx].strip(), text[idx:].strip()
    # No clear split — return full text as findings
    return text.strip(), "See findings above for detailed recommendations."
