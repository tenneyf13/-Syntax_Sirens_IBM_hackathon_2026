# ♿ AccessAI — WCAG Accessibility Checker

> **IBM Hackathon 2026 · Team Syntax Sirens**

AccessAI is an AI-powered web accessibility auditing tool. Paste any URL and instantly receive a structured WCAG 2.1 AA compliance report — findings mapped to specific WCAG criteria, plus actionable code-level recommendations — all powered by **IBM watsonx.ai**.

---

## 🎥 Demo

1. Open `http://localhost:8000` in your browser
2. Paste any website URL (e.g. `https://example.com`)
3. Click **Check Now**
4. Receive:
   - 🔍 **Findings** — WCAG 2.1 AA violations with criterion references
   - 💡 **Recommendations** — Concrete fixes with code snippets
   - 📊 **Score badge** — Pass / Needs Work / Fail
   - ⬇ **Download Report** — Export as `.txt`

---

## 🏗️ Architecture

```
Browser (Frontend)
  └── HTML + CSS + Vanilla JS  (Frontend/Page/homePage.html)
        │
        │  POST /api/check-wcag  { url }
        ▼
FastAPI Backend  (main.py)
  ├── Fetches HTML from target URL
  ├── Authenticates with IBM Cloud IAM
  └── Calls IBM watsonx.ai (Llama 3.3 70B Instruct)
        │
        │  Returns { findings, recommendations }
        ▼
Frontend renders markdown, shows score badge, enables download
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3.11, FastAPI, Uvicorn |
| AI Model | `meta-llama/llama-3-3-70b-instruct` via IBM watsonx.ai |
| Auth | IBM Cloud IAM (API key → Bearer token) |
| HTTP Client | `httpx` (async) |
| Container | Docker |

---

## 🚀 Quick Start

### Option A — Docker (recommended)

```bash
# 1. Clone the repo
git clone https://github.com/your-org/syntax-sirens-accessai.git
cd syntax-sirens-accessai

# 2. Copy and fill in your credentials
cp .env.example .env
# Edit .env — add IBM_CLOUD_API_KEY and WATSONX_PROJECT_ID

# 3. Build and run
docker build -t accessai .
docker run -p 8000:8000 --env-file .env accessai

# 4. Open in browser
open http://localhost:8000
```

### Option B — Local Python

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and fill in your credentials
cp .env.example .env
# Edit .env — add IBM_CLOUD_API_KEY and WATSONX_PROJECT_ID

# 4. Run the server
uvicorn main:app --host 0.0.0.0 --port 8000

# 5. Open in browser
open http://localhost:8000
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in your values:

```env
# Required
IBM_CLOUD_API_KEY=<your-ibm-cloud-api-key>
WATSONX_PROJECT_ID=<your-watsonx-project-id>
WATSONX_URL=https://eu-de.ml.cloud.ibm.com   # change region if needed
```

### Getting your credentials

| Credential | Where to get it |
|---|---|
| `IBM_CLOUD_API_KEY` | [cloud.ibm.com](https://cloud.ibm.com) → Manage → Access (IAM) → API keys |
| `WATSONX_PROJECT_ID` | [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com) → Projects → your project → Manage → General |
| `WATSONX_URL` | Use your region: `us-south`, `eu-de`, `eu-gb`, `jp-tok` |

> **Important:** Your watsonx.ai project must have a **watsonx.ai Runtime** service associated.  
> Project → Manage → Services & integrations → Associate service → watsonx.ai Runtime

---

## 📂 Project Structure

```
├── main.py                        ← FastAPI backend (API + AI integration)
├── requirements.txt               ← Python dependencies
├── Dockerfile                     ← Container definition
├── .env.example                   ← Credentials template
├── .env                           ← Your credentials (not committed)
└── Frontend/
    ├── Page/
    │   └── homePage.html          ← Main UI (form, results, download)
    ├── Style/
    │   └── awesome.css            ← Styles
    └── Assets/
        └── neat.png               ← Assets
```

---

## 🔌 API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Serves the frontend UI |
| `GET` | `/health` | Health check `{ ok: true }` |
| `POST` | `/api/check-wcag` | Main endpoint — body: `{ "url": "https://..." }` |
| `POST` | `/fetch` | Fetch raw HTML from a URL |
| `GET` | `/debug/env` | Check which env vars are set |
| `GET` | `/docs` | Interactive Swagger API docs |

### Example request

```bash
curl -X POST http://localhost:8000/api/check-wcag \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Example response

```json
{
  "findings": "FINDINGS:\n1. **1.1.1 Non-text Content**: ...",
  "recommendations": "RECOMMENDATIONS:\n1. **For 1.1.1**: ..."
}
```

---

## 👩‍💻 Team

**Syntax Sirens** — IBM Hackathon 2026

---

## 📄 License

MIT
