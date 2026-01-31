# Windows Setup Guide - Watson Orchestrate Integration

## 🪟 Windows PowerShell Instructions

### Step 1: Install Dependencies

In PowerShell, navigate to the backend directory and install packages:

```powershell
cd backend
python -m pip install -r requirements.txt
```

**Note**: On Windows, use `python -m pip` instead of just `pip`

If you get "python is not recognized", you may need to use `py` instead:

```powershell
py -m pip install -r requirements.txt
```

### Step 2: Create .env File

In PowerShell, copy the example file:

```powershell
Copy-Item .env.example .env
```

Or manually:

1. Open `.env.example` in VS Code
2. Copy the contents
3. Create a new file named `.env` in the root directory
4. Paste the contents
5. Replace `your_ibm_cloud_api_key_here` with your actual API key

Your `.env` should look like:

```env
IBM_CLOUD_API_KEY=your_actual_key_here
WATSON_ORCHESTRATE_AGENT_ID=638256ff-9626-4012-bb71-0a111f64ecf9
WATSON_ORCHESTRATE_HOST_URL=https://dl.watson-orchestrate.ibm.com
WATSON_ORCHESTRATE_INSTANCE_ID=20260130-1647-0257-7054-5539941574fb
CORS_ORIGINS=*
```

### Step 3: Test Watson Connection

From the root directory:

```powershell
python test_watson_orchestrate.py
```

Or if `python` doesn't work:

```powershell
py test_watson_orchestrate.py
```

### Step 4: Start the Backend

```powershell
cd backend
python -m uvicorn main:app --reload
```

Or:

```powershell
py -m uvicorn main:app --reload
```

### Step 5: Open in Browser

Navigate to: `http://localhost:8000/`

---

## 🔧 Common Windows Issues

### Issue: "pip is not recognized"

**Solution**: Use `python -m pip` or `py -m pip` instead

### Issue: "python is not recognized"

**Solution**:

1. Try using `py` instead of `python`
2. Or install Python from python.org and check "Add to PATH"

### Issue: PowerShell execution policy error

**Solution**:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Can't create .env file

**Solution**: Create it manually in VS Code:

1. File → New File
2. Save as `.env` (include the dot!)
3. Add your configuration

---

## 📋 Complete Windows Command Sequence

```powershell
# 1. Install dependencies
cd backend
python -m pip install -r requirements.txt

# 2. Go back to root
cd ..

# 3. Create .env file (manually in VS Code or use Copy-Item)
Copy-Item .env.example .env
# Then edit .env to add your API key

# 4. Test Watson connection
python test_watson_orchestrate.py

# 5. Start backend
cd backend
python -m uvicorn main:app --reload

# 6. Open browser to http://localhost:8000/
```

---

## 🎯 Alternative: Using py Command

If `python` doesn't work, use `py`:

```powershell
# Install dependencies
cd backend
py -m pip install -r requirements.txt

# Test Watson
cd ..
py test_watson_orchestrate.py

# Start backend
cd backend
py -m uvicorn main:app --reload
```

---

## ✅ Verification Checklist

- [ ] Python installed (check with `python --version` or `py --version`)
- [ ] Dependencies installed (`python -m pip install -r backend/requirements.txt`)
- [ ] `.env` file created in root directory
- [ ] IBM Cloud API key added to `.env`
- [ ] Terminal test passes (`python test_watson_orchestrate.py`)
- [ ] Backend starts (`python -m uvicorn main:app --reload` from backend folder)
- [ ] Browser opens `http://localhost:8000/`

---

## 🚀 Quick Test Commands

Test if Python is working:

```powershell
python --version
# or
py --version
```

Test if pip is working:

```powershell
python -m pip --version
# or
py -m pip --version
```

List installed packages:

```powershell
python -m pip list
# or
py -m pip list
```

---

## 📁 File Locations (Windows Paths)

```
C:\Users\YourName\YourProject\
├── .env                          ← Create this (your API key)
├── .env.example                  ← Template provided
├── test_watson_orchestrate.py    ← Test script
└── backend\
    ├── main.py                   ← FastAPI app
    ├── watson_orchestrate_service.py
    └── requirements.txt
```

---

## 💡 Windows-Specific Tips

1. **Use VS Code Terminal**: Open VS Code terminal (Ctrl + `) - it's already in PowerShell
2. **Path separators**: Windows uses `\` but Python accepts `/` too
3. **File extensions**: Make sure `.env` doesn't become `.env.txt`
4. **Antivirus**: May need to allow Python through firewall
5. **Virtual environment** (optional but recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   python -m pip install -r backend/requirements.txt
   ```

---

## 🆘 Still Having Issues?

1. **Check Python installation**:
   - Download from python.org
   - During install, check "Add Python to PATH"
   - Restart PowerShell after installing

2. **Use VS Code's integrated terminal**:
   - Press Ctrl + `
   - Should automatically be in your project directory

3. **Try Command Prompt instead**:
   - Open CMD instead of PowerShell
   - Same commands work in CMD

4. **Check file paths**:
   - Make sure you're in the correct directory
   - Use `pwd` to see current directory
   - Use `ls` to list files

---

## 📞 Next Steps After Setup

Once everything is installed and running:

1. See [WATSON_SETUP.md](WATSON_SETUP.md) for architecture details
2. See [QUICK_START.md](QUICK_START.md) for usage guide
3. See [README.md](README.md) for project overview
