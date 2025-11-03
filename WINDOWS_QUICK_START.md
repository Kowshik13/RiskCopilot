# 🚀 QUICK START GUIDE - Windows

## Step 1: Extract Files Correctly

1. **Download the ZIP file** from the outputs folder
2. **Extract to a new folder** (e.g., `D:\RiskCopilot`)
3. **Navigate to that folder** in PowerShell/Terminal:
   ```powershell
   cd D:\RiskCopilot
   ```

## Step 2: Verify Files Are in Place

Run the verification script FROM THE PROJECT ROOT:
```powershell
python verify.py
```

You should see all green checkmarks. If not, make sure you extracted correctly.

## Step 3: Backend Setup (PowerShell)

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\Activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt

# Create .env from example
copy .env.example .env

# Edit .env with notepad
notepad .env
# Set: USE_MOCK_LLM=True
# Save and close

# Run backend
uvicorn app.main:app --reload
```

Keep this terminal open!

## Step 4: Frontend Setup (New PowerShell)

Open a NEW PowerShell window:
```powershell
# Navigate to your project
cd D:\RiskCopilot\frontend

# Install dependencies
npm install

# If errors, try:
npm install --legacy-peer-deps

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Run frontend
npm run dev
```

## Step 5: Test It!

- Open browser: http://localhost:5173
- You should see the Risk Copilot interface
- Try sending a message like "What is model risk?"

## Step 6: Push to GitHub

```powershell
# Go back to root directory
cd D:\RiskCopilot

# Initialize git
git init

# Configure git
git config user.name "Kowshik Raja"
git config user.email "kowshikraja.dev@gmail.com"

# Add all files
git add .

# Check status (no .env files should appear)
git status

# Commit
git commit -m "Initial commit: Risk Copilot Phase 1"

# Add remote
git remote add origin https://github.com/Kowshik13/multi-agent-risk-reporting.git

# Push
git push -u origin main
```

## 🔧 Common Windows Issues:

### PowerShell Execution Policy Error
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Already in Use
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with the number you found)
taskkill /PID [PID] /F

# Or use different port
uvicorn app.main:app --reload --port 8001
# Update frontend .env to match: VITE_API_URL=http://localhost:8001
```

### NPM Install Fails
```powershell
# Clear cache
npm cache clean --force

# Delete node_modules and package-lock
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json

# Reinstall
npm install --legacy-peer-deps
```

## Success Checklist
- [ ] All files extracted to correct folders
- [ ] Backend runs on http://localhost:8000
- [ ] Frontend runs on http://localhost:5173
- [ ] Can send messages in chat interface
- [ ] Pushed to GitHub successfully

## Project Structure Should Look Like:
```
D:\RiskCopilot\
├── backend\
│   ├── app\
│   │   ├── api\
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   ├── health.py
│   │   │   └── traces.py
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── main.py
│   │   └── models.py
│   ├── core\
│   ├── data\
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend\
│   ├── src\
│   ├── package.json
│   └── ...
├── docs\
├── README.md
├── setup.sh
├── verify.py
└── .gitignore
```
