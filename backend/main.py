from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import httpx
import os
from dotenv import load_dotenv
from pathlib import Path

# absolute path for frontend
BASE_DIR = Path(__file__).resolve().parent.parent
# Load environment variables
load_dotenv()

# Import Watson Orchestrate service
try:
    from watson_orchestrate_service import get_watson_orchestrate_service
    WATSON_AVAILABLE = True
    print("✅ Watson Orchestrate service loaded successfully")
except ImportError as e:
    WATSON_AVAILABLE = False
    print(f"⚠️  Watson Orchestrate service not available: {e}")
    print("   Install dependencies: pip install -r requirements.txt")

app = FastAPI(title="WCAG Checker Backend", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

# --- CORS: allow your frontend domain to call the backend ---
# For hackathon, you can allow "*" temporarily. Better: set to your frontend URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
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

    # 2) Run WCAG analysis using Watson Orchestrate
    if WATSON_AVAILABLE:
        try:
            watson_service = get_watson_orchestrate_service()
            findings, recommendations = watson_service.analyze_wcag(html, str(req.url))
        except Exception as e:
            # If Watson fails, fall back to stub
            print(f"Watson Orchestrate error: {e}")
            findings, recommendations = run_wcag_analysis_stub(html)
    else:
        # Fall back to stub if Watson not available
        findings, recommendations = run_wcag_analysis_stub(html)

    # 3) Return to frontend
    return {
        "findings": findings,
        "recommendations": recommendations
    }


def run_wcag_analysis_stub(html: str):
    """
    Fallback stub function for WCAG analysis when Watson Orchestrate is not available.
    This provides basic feedback so the UI works end-to-end.
    """
    findings = """Fetched HTML successfully.

⚠️  Watson Orchestrate is not configured or unavailable.

To enable AI-powered WCAG analysis:
1. Install dependencies: pip install -r requirements.txt
2. Create a .env file with your IBM_CLOUD_API_KEY
3. Restart the backend server

Basic HTML structure detected. For detailed WCAG analysis, please configure Watson Orchestrate."""
    
    recommendations = """Configuration Steps:

1. Copy .env.example to .env
2. Add your IBM Cloud API key to .env
3. Verify Watson Orchestrate agent ID is correct
4. Run: python test_watson_orchestrate.py (to test connection)
5. Restart this backend server

Once configured, you'll receive detailed WCAG 2.1 Level AA compliance analysis."""
    
    return findings, recommendations