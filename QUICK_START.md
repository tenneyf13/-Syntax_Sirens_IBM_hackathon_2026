# Quick Start Guide - Watson Orchestrate Integration

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (2 minutes)

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure API Key (1 minute)

1. Copy the example file:

```bash
cp .env.example .env
```

2. Edit `.env` and add your IBM Cloud API key:

```env
IBM_CLOUD_API_KEY=paste_your_key_here
```

### Step 3: Test in Terminal (1 minute)

```bash
python test_watson_orchestrate.py
```

**Expected output:**

```
✅ Authentication successful!
✅ Agent responded successfully!
✅ SUCCESS! Watson Orchestrate is working correctly.
```

### Step 4: Start Backend (30 seconds)

```bash
cd backend
uvicorn main:app --reload
```

### Step 5: Test in Browser (30 seconds)

1. Open: `http://localhost:8000/`
2. Enter a URL: `https://example.com`
3. Click "Submit url"
4. View WCAG analysis results!

---

## ✅ Verification Checklist

- [ ] Dependencies installed (`pip install -r backend/requirements.txt`)
- [ ] `.env` file created with IBM_CLOUD_API_KEY
- [ ] Terminal test passes (`python test_watson_orchestrate.py`)
- [ ] Backend starts without errors
- [ ] Frontend loads at `http://localhost:8000/`
- [ ] URL submission returns Watson analysis

---

## 🐛 Quick Troubleshooting

### "Import Error: dotenv"

```bash
pip install python-dotenv
```

### "IBM_CLOUD_API_KEY not found"

- Check `.env` file exists in root directory
- Verify API key is on the line: `IBM_CLOUD_API_KEY=your_key`
- No quotes needed around the key

### "Watson Orchestrate service not available"

```bash
pip install ibm-cloud-sdk-core requests
```

### Backend won't start

```bash
cd backend
pip install fastapi uvicorn httpx pydantic
```

---

## 📁 File Locations

```
Your Project/
├── .env                          ← Create this (your API key)
├── .env.example                  ← Template provided
├── test_watson_orchestrate.py    ← Terminal test script
├── README.md                     ← Main documentation
├── WATSON_SETUP.md              ← Detailed guide
└── backend/
    ├── main.py                   ← FastAPI app (updated)
    ├── watson_orchestrate_service.py  ← Watson integration
    └── requirements.txt          ← Dependencies (updated)
```

---

## 🎯 What Each File Does

| File                                    | Purpose                                 |
| --------------------------------------- | --------------------------------------- |
| `test_watson_orchestrate.py`            | Test Watson connection in terminal      |
| `backend/watson_orchestrate_service.py` | Handles Watson API calls                |
| `backend/main.py`                       | FastAPI backend with Watson integration |
| `.env`                                  | Your secret API key (don't commit!)     |
| `.env.example`                          | Template for `.env`                     |

---

## 💡 Pro Tips

1. **Always test in terminal first** - Run `python test_watson_orchestrate.py` before starting the backend
2. **Check backend logs** - Look for "✅ Watson Orchestrate service loaded successfully"
3. **Use the health endpoint** - Visit `http://localhost:8000/health` to verify backend is running
4. **Keep .env secure** - Never commit your `.env` file to git (it's in `.gitignore`)

---

## 🔗 Next Steps

- ✅ Got it working? See [WATSON_SETUP.md](WATSON_SETUP.md) for architecture details
- 🚀 Ready to deploy? Check deployment section in WATSON_SETUP.md
- 🐛 Having issues? See troubleshooting in WATSON_SETUP.md

---

## 📞 Need Help?

1. Check terminal test output: `python test_watson_orchestrate.py`
2. Review backend logs when starting server
3. See [WATSON_SETUP.md](WATSON_SETUP.md) troubleshooting section
4. Verify Watson Orchestrate agent is active in IBM Cloud

---

**Time to first working demo: ~5 minutes** ⏱️
