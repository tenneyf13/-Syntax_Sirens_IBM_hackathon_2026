# Syntax Sirens - WCAG Standards Checker

## IBM Hackathon 2026

An AI-powered web accessibility checker that uses Watson Orchestrate to analyze websites for WCAG 2.1 Level AA compliance.

## Features

- 🤖 **AI-Powered Analysis**: Uses Watson Orchestrate agent for intelligent WCAG compliance checking
- 🌐 **Real-time URL Analysis**: Fetch and analyze any public website
- 📊 **Detailed Reports**: Get specific findings and actionable recommendations
- 🎨 **User-Friendly Interface**: Clean, accessible UI built with Bootstrap
- ⚡ **Fast API Backend**: Built with FastAPI for high performance

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Watson Orchestrate

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Add your IBM Cloud API key to `.env`:

```env
IBM_CLOUD_API_KEY=your_api_key_here
```

### 3. Test Watson Connection (Terminal Test)

```bash
python test_watson_orchestrate.py
```

This will verify your Watson Orchestrate connection before running the full app.

### 4. Start the Backend

```bash
cd backend
uvicorn main:app --reload
```

### 5. Open in Browser

Navigate to: `http://localhost:8000/`

## Documentation

📖 **Full Setup Guide**: See [WATSON_SETUP.md](WATSON_SETUP.md) for detailed instructions, troubleshooting, and architecture overview.

## Project Structure

```
├── backend/
│   ├── main.py                          # FastAPI application
│   ├── watson_orchestrate_service.py    # Watson integration
│   ├── requirements.txt                 # Python dependencies
│   └── .env                            # Environment variables (create this)
├── Frontend/
│   ├── Page/
│   │   └── homePage.html               # Main UI
│   └── Style/
│       └── awesome.css                 # Styles
├── test_watson_orchestrate.py          # Terminal test script
├── .env.example                        # Environment template
├── WATSON_SETUP.md                     # Detailed setup guide
└── README.md                           # This file
```

## Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **AI/ML**: IBM Watson Orchestrate
- **Frontend**: HTML5, Bootstrap 5, Vanilla JavaScript
- **Authentication**: IBM Cloud IAM
- **HTTP Client**: httpx, requests

## Watson Orchestrate Configuration

- **Agent ID**: `638256ff-9626-4012-bb71-0a111f64ecf9`
- **Host URL**: `https://dl.watson-orchestrate.ibm.com`
- **Instance ID**: `20260130-1647-0257-7054-5539941574fb`

## API Endpoints

- `GET /` - Frontend interface
- `GET /health` - Health check
- `POST /api/check-wcag` - Analyze URL for WCAG compliance
- `POST /fetch` - Fetch raw HTML from URL

## How It Works

1. User enters a website URL in the frontend
2. Backend fetches the HTML content from the URL
3. HTML is sent to Watson Orchestrate agent for WCAG analysis
4. Agent analyzes for accessibility issues (alt text, contrast, labels, etc.)
5. Results are formatted and displayed to the user

## Testing in Terminal First

Before running the full application, test your Watson Orchestrate connection:

```bash
python test_watson_orchestrate.py
```

This script will:

- ✅ Authenticate with IBM Cloud
- ✅ Connect to your Watson Orchestrate agent
- ✅ Send sample HTML for analysis
- ✅ Display the response

If this works, your integration is ready!

## Team

**Syntax Sirens** - IBM Hackathon 2026

## Support

For setup issues, see [WATSON_SETUP.md](WATSON_SETUP.md) troubleshooting section.

## License

MIT License
