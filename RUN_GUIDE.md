# 🚀 Risk Copilot - Complete Setup & Run Guide

## Prerequisites Check
Make sure you have:
- Python 3.10+ (`python --version` or `python3 --version`)
- Node.js 18+ (`node --version`)
- Git (`git --version`)

## 📦 Step 1: Backend Setup

### Option A: Using the setup script (Recommended)
```bash
# Make script executable (Mac/Linux)
chmod +x setup.sh
./setup.sh

# For Windows, run the commands manually (see Option B)
```

### Option B: Manual Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
# or
python3 -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env
# On Windows: copy .env.example .env

# Edit .env file and set:
# USE_MOCK_LLM=True (for testing without API keys)
# Or add your OpenAI key: OPENAI_API_KEY=sk-...
```

## 📱 Step 2: Frontend Setup

```bash
# Open new terminal and navigate to frontend
cd frontend

# Install dependencies
npm install

# If you get errors, try:
npm install --legacy-peer-deps

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env
```

## 🏃 Step 3: Run the Application

### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

You should see:
```
VITE v5.0.8  ready in xxx ms
➜  Local:   http://localhost:5173/
```

## ✅ Step 4: Verify Everything Works

1. **Backend Health Check**: http://localhost:8000/api/v1/health
2. **API Documentation**: http://localhost:8000/docs
3. **Frontend**: http://localhost:5173

## 🐛 Common Issues & Solutions

### Issue 1: ModuleNotFoundError in Backend
```bash
# Make sure you're in virtual environment
which python  # Should show venv path
pip list  # Check if packages are installed
pip install -r requirements.txt  # Reinstall
```

### Issue 2: Port Already in Use
```bash
# Kill process on port 8000 (backend)
# Mac/Linux:
lsof -i :8000
kill -9 <PID>
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change port in uvicorn command:
uvicorn app.main:app --reload --port 8001
# Then update frontend .env: VITE_API_URL=http://localhost:8001
```

### Issue 3: CORS Errors in Browser
```python
# Edit backend/app/config.py
CORS_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "*"  # Temporary for testing
]
```

### Issue 4: npm install fails
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install --legacy-peer-deps
```

## 📤 Push to GitHub

### Step 1: Initialize Git (if not done)
```bash
# In project root
git init
git config user.name "Kowshik Raja"
git config user.email "kowshikraja.dev@gmail.com"
```

### Step 2: Add Files
```bash
# Add all files
git add .

# Check status
git status

# Make sure .env files are NOT included (should be in .gitignore)
```

### Step 3: Commit
```bash
git commit -m "Initial commit: Risk Copilot Phase 1 - Multi-agent architecture"
```

### Step 4: Add Remote Repository
```bash
# Add your GitHub repo
git remote add origin https://github.com/Kowshik13/multi-agent-risk-reporting.git

# Verify remote
git remote -v
```

### Step 5: Push to GitHub
```bash
# Push to main branch
git push -u origin main

# If main doesn't exist, try master:
git push -u origin master

# If you get errors about existing content:
git pull origin main --allow-unrelated-histories
git push origin main
```

## 🔒 Security Before Pushing

### Check these files exist and are correct:

**.gitignore** must include:
```
.env
.env.local
.env.production
*.pyc
__pycache__/
venv/
node_modules/
```

**backend/.env** should NOT be pushed (only .env.example)

## 🎯 Quick Test Commands

### Test Backend API
```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test chat endpoint (with mock LLM)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is model risk?"}'
```

### Test Frontend Build
```bash
cd frontend
npm run build  # Should create dist/ folder
npm run preview  # Test production build
```

## 📊 Project Structure Verification
```
multi-agent-risk-reporting/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py ✅
│   │   │   ├── health.py ✅
│   │   │   └── traces.py ✅
│   │   ├── __init__.py ✅
│   │   ├── config.py ✅
│   │   ├── main.py ✅
│   │   └── models.py ✅
│   ├── core/
│   │   ├── __init__.py ✅
│   │   └── faiss_index.py ✅
│   ├── data/
│   │   └── policies/
│   │       ├── ai_governance_policy.md ✅
│   │       └── model_risk_management_policy.md ✅
│   ├── requirements.txt ✅
│   ├── Dockerfile ✅
│   └── .env.example ✅
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx ✅
│   │   │   ├── CitationPanel.jsx ✅
│   │   │   └── RiskBadge.jsx ✅
│   │   ├── services/
│   │   │   └── api.js ✅
│   │   ├── App.jsx ✅
│   │   ├── main.jsx ✅
│   │   └── index.css ✅
│   ├── index.html ✅
│   ├── package.json ✅
│   ├── vite.config.js ✅
│   ├── tailwind.config.js ✅
│   ├── postcss.config.js ✅
│   └── netlify.toml ✅
├── docs/
│   └── PHASE1_LEARNING_NOTES.md ✅
├── README.md ✅
├── setup.sh ✅
└── .gitignore ✅
```

## 🚦 Success Checklist
- [ ] Backend runs without errors
- [ ] Frontend loads in browser
- [ ] API docs accessible at /docs
- [ ] Chat interface shows up
- [ ] Can send a test message
- [ ] No .env files in git status
- [ ] Successfully pushed to GitHub

## 💡 Next Steps After Push
1. Go to https://github.com/Kowshik13/multi-agent-risk-reporting
2. Add a description: "Multi-agent LLM system for risk management - Demo for SG internship"
3. Add topics: `langgraph`, `fastapi`, `react`, `rag`, `risk-management`
4. Make it public (if appropriate)

## 📞 Still Having Issues?
Common fixes:
```bash
# Full reset
rm -rf backend/venv frontend/node_modules
./setup.sh

# Python version issues
python3.10 -m venv venv  # Use specific version

# Permission issues
sudo chown -R $(whoami) .  # Mac/Linux only
```
