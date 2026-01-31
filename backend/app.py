from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import httpx
import os

app = FastAPI(title="WCAG Checker Backend", version="1.0.0")

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

@app.get("/health")
def health():
    return {"ok": True}

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
    # Replace this stub with your actual agent call.
    # Options:
    #   A) call watsonx agent API here
    #   B) run local rules-based checks here
    #   C) call Bright Data analysis service here
    findings, recommendations = run_wcag_analysis_stub(html)

    # 3) Return to frontend
    return {
        "findings": findings,
        "recommendations": recommendations
    }


def run_wcag_analysis_stub(html: str):
    # TODO: Replace with your real analysis.
    # For now, just a placeholder so the UI works end-to-end.
    findings = "Fetched HTML successfully.\n\n(Replace this with WCAG findings.)"
    recommendations = "Hook up watsonx analysis here.\n\n(Replace this with remediation guidance.)"
    return findings, recommendations
