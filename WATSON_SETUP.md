# Watson Orchestrate Integration Setup Guide

This guide will help you integrate Watson Orchestrate with your WCAG Standards Checker application.

## Prerequisites

- IBM Cloud account with Watson Orchestrate access
- IBM Cloud API Key
- Watson Orchestrate agent configured for WCAG analysis
- Python 3.8 or higher

## What You Have

Based on your configuration:

- **Agent ID**: `638256ff-9626-4012-bb71-0a111f64ecf9`
- **Host URL**: `https://dl.watson-orchestrate.ibm.com`
- **Instance ID**: `20260130-1647-0257-7054-5539941574fb`

## Step-by-Step Setup

### 1. Install Dependencies

Navigate to the backend directory and install required packages:

```bash
cd backend
pip install -r requirements.txt
```

This will install:

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `httpx` - HTTP client
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management
- `requests` - HTTP library for Watson API calls
- `ibm-cloud-sdk-core` - IBM Cloud authentication

### 2. Configure Environment Variables

Create a `.env` file in the **root directory** (not in backend):

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your IBM Cloud API key:

```env
# IBM Cloud & Watson Orchestrate Configuration
IBM_CLOUD_API_KEY=your_actual_api_key_here

# Watson Orchestrate Configuration (already set)
WATSON_ORCHESTRATE_AGENT_ID=638256ff-9626-4012-bb71-0a111f64ecf9
WATSON_ORCHESTRATE_HOST_URL=https://dl.watson-orchestrate.ibm.com
WATSON_ORCHESTRATE_INSTANCE_ID=20260130-1647-0257-7054-5539941574fb

# Backend Configuration
CORS_ORIGINS=*
```

**Important**: Replace `your_actual_api_key_here` with your real IBM Cloud API key.

### 3. Test Watson Orchestrate Connection (Terminal Test)

Before integrating with your app, test the connection in your terminal:

```bash
# From the root directory
python test_watson_orchestrate.py
```

**What this script does:**

1. ✅ Authenticates with IBM Cloud using your API key
2. ✅ Connects to your Watson Orchestrate agent
3. ✅ Sends a sample HTML snippet for WCAG analysis
4. ✅ Displays the agent's response

**Expected Output:**

```
============================================================
Watson Orchestrate Connection Test
============================================================
🔐 Authenticating with IBM Cloud...
✅ Authentication successful!

🤖 Testing Watson Orchestrate Agent...
   Agent ID: 638256ff-9626-4012-bb71-0a111f64ecf9
   Host URL: https://dl.watson-orchestrate.ibm.com
   Instance ID: 20260130-1647-0257-7054-5539941574fb

📤 Sending test request to agent...
📥 Response Status: 200
✅ Agent responded successfully!

📊 Agent Response:
{
  "output": {
    "text": "WCAG analysis results..."
  }
}
============================================================
✅ SUCCESS! Watson Orchestrate is working correctly.
============================================================
```

**Troubleshooting:**

- ❌ **401 Error**: Check your API key in `.env`
- ❌ **404 Error**: Verify Agent ID and Instance ID
- ❌ **Timeout**: Agent may be slow - try again
- ❌ **Import Error**: Run `pip install -r backend/requirements.txt`

### 4. Start the Backend Server

Once the terminal test succeeds, start your backend:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Server will start at**: `http://localhost:8000`

**Test endpoints:**

- Health check: `http://localhost:8000/health`
- API info: `http://localhost:8000/api`
- Frontend: `http://localhost:8000/`

### 5. Test the Full Integration

1. **Open your browser**: Navigate to `http://localhost:8000/`
2. **Enter a URL**: Type a website URL (e.g., `https://example.com`)
3. **Click "Submit url"**: The app will:
   - Fetch the HTML from the URL
   - Send it to Watson Orchestrate for WCAG analysis
   - Display findings and recommendations

### 6. Verify Watson Integration

Check the backend terminal output for:

```
✅ Watson Orchestrate service loaded successfully
```

If you see:

```
⚠️  Watson Orchestrate service not available
```

Then:

1. Verify all dependencies are installed
2. Check `.env` file exists and has correct values
3. Restart the backend server

## Architecture Overview

```
┌─────────────┐
│   Browser   │
│  (Frontend) │
└──────┬──────┘
       │ POST /api/check-wcag
       ▼
┌─────────────────┐
│  FastAPI        │
│  Backend        │
│  (main.py)      │
└────────┬────────┘
         │
         ├─► Fetch HTML from target URL
         │
         ▼
┌─────────────────────────┐
│ Watson Orchestrate      │
│ Service Module          │
│ (watson_orchestrate_    │
│  service.py)            │
└────────┬────────────────┘
         │
         │ IBM Cloud API Key Auth
         ▼
┌─────────────────────────┐
│ Watson Orchestrate      │
│ Agent (IBM Cloud)       │
│ Agent ID: 638256ff...   │
└────────┬────────────────┘
         │
         │ WCAG Analysis
         ▼
┌─────────────────────────┐
│ Response:               │
│ - Findings              │
│ - Recommendations       │
└─────────────────────────┘
```

## Files Created

1. **`.env.example`** - Template for environment variables
2. **`test_watson_orchestrate.py`** - Terminal test script
3. **`backend/watson_orchestrate_service.py`** - Watson integration module
4. **`backend/main.py`** - Updated with Watson integration
5. **`backend/requirements.txt`** - Updated with dependencies
6. **`WATSON_SETUP.md`** - This documentation

## API Endpoints

### POST /api/check-wcag

Analyzes a URL for WCAG compliance.

**Request:**

```json
{
  "url": "https://example.com"
}
```

**Response:**

```json
{
  "findings": "WCAG compliance issues found...",
  "recommendations": "Specific fixes for each issue..."
}
```

## Watson Orchestrate Agent Configuration

Your agent should be configured to:

1. Accept HTML content as input
2. Analyze for WCAG 2.1 Level AA compliance
3. Return structured findings and recommendations
4. Focus on:
   - Missing alt text
   - Color contrast issues
   - Form labels
   - Keyboard accessibility
   - Semantic HTML
   - ARIA attributes
   - Heading hierarchy

## Common Issues & Solutions

### Issue: "Watson Orchestrate service not available"

**Solution**:

```bash
pip install python-dotenv requests ibm-cloud-sdk-core
```

### Issue: "IBM_CLOUD_API_KEY not found"

**Solution**:

1. Create `.env` file in root directory
2. Add: `IBM_CLOUD_API_KEY=your_key_here`

### Issue: Agent returns unexpected format

**Solution**:
The `watson_orchestrate_service.py` module handles multiple response formats. Check the terminal test output to see the actual response structure.

### Issue: Timeout errors

**Solution**:

- Increase timeout in `watson_orchestrate_service.py` (line 119)
- Check Watson Orchestrate agent is deployed and active
- Reduce HTML content size (currently limited to 5000 chars)

## Next Steps

1. ✅ Run terminal test: `python test_watson_orchestrate.py`
2. ✅ Start backend: `cd backend && uvicorn main:app --reload`
3. ✅ Test in browser: `http://localhost:8000/`
4. ✅ Submit a URL and verify Watson analysis works
5. 🚀 Deploy to production (Heroku, IBM Cloud, etc.)

## Support

If you encounter issues:

1. Check the terminal test output
2. Review backend logs for error messages
3. Verify Watson Orchestrate agent is active in IBM Cloud
4. Check IBM Cloud API key permissions

## About LangFlow

You asked about LangFlow - it's a visual tool for building LLM applications. While it could simplify some aspects, your current setup with Watson Orchestrate is more direct and doesn't require additional tools. LangFlow would be useful if you wanted to:

- Build complex multi-step AI workflows visually
- Experiment with different LLM models
- Create custom prompt chains

For your use case (single agent WCAG analysis), the direct Watson Orchestrate integration is simpler and more maintainable.
