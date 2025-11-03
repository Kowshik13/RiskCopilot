#!/usr/bin/env python3
"""
Risk Copilot - Installation Verification Script
Checks if all required files and dependencies are in place
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Colors for terminal output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def print_status(status, message):
    if status == "success":
        print(f"{GREEN}✅ {message}{NC}")
    elif status == "warning":
        print(f"{YELLOW}⚠️  {message}{NC}")
    elif status == "error":
        print(f"{RED}❌ {message}{NC}")
    elif status == "info":
        print(f"{BLUE}ℹ️  {message}{NC}")

def check_file_exists(filepath, description):
    if os.path.exists(filepath):
        print_status("success", f"{description} found")
        return True
    else:
        print_status("error", f"{description} missing: {filepath}")
        return False

def check_python_version():
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print_status("success", f"Python {version.major}.{version.minor} installed")
        return True
    else:
        print_status("error", f"Python 3.10+ required, found {version.major}.{version.minor}")
        return False

def check_node_version():
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print_status("success", f"Node.js {version} installed")
        return True
    except FileNotFoundError:
        print_status("error", "Node.js not installed")
        return False

def verify_backend_structure():
    print(f"\n{BLUE}Checking Backend Structure...{NC}")
    backend_files = [
        ("backend/app/main.py", "Main FastAPI application"),
        ("backend/app/config.py", "Configuration file"),
        ("backend/app/models.py", "Pydantic models"),
        ("backend/app/api/chat.py", "Chat endpoint"),
        ("backend/app/api/health.py", "Health endpoint"),
        ("backend/app/api/traces.py", "Traces endpoint"),
        ("backend/core/faiss_index.py", "FAISS index implementation"),
        ("backend/data/policies/model_risk_management_policy.md", "MRM Policy"),
        ("backend/data/policies/ai_governance_policy.md", "AI Policy"),
        ("backend/requirements.txt", "Python dependencies"),
        ("backend/Dockerfile", "Docker configuration"),
        ("backend/.env.example", "Environment example")
    ]
    
    all_good = True
    for filepath, desc in backend_files:
        if not check_file_exists(filepath, desc):
            all_good = False
    return all_good

def verify_frontend_structure():
    print(f"\n{BLUE}Checking Frontend Structure...{NC}")
    frontend_files = [
        ("frontend/src/App.jsx", "Main App component"),
        ("frontend/src/main.jsx", "React entry point"),
        ("frontend/src/index.css", "Tailwind CSS"),
        ("frontend/src/components/ChatInterface.jsx", "Chat component"),
        ("frontend/src/components/RiskBadge.jsx", "Risk badge component"),
        ("frontend/src/components/CitationPanel.jsx", "Citation component"),
        ("frontend/src/services/api.js", "API service"),
        ("frontend/package.json", "NPM configuration"),
        ("frontend/vite.config.js", "Vite configuration"),
        ("frontend/tailwind.config.js", "Tailwind configuration"),
        ("frontend/index.html", "HTML entry point")
    ]
    
    all_good = True
    for filepath, desc in frontend_files:
        if not check_file_exists(filepath, desc):
            all_good = False
    return all_good

def check_env_setup():
    print(f"\n{BLUE}Checking Environment Setup...{NC}")
    
    # Check if .env exists
    if os.path.exists("backend/.env"):
        print_status("success", "Backend .env file exists")
        # Check if it has required keys
        with open("backend/.env", "r") as f:
            content = f.read()
            if "USE_MOCK_LLM" in content:
                print_status("success", "Mock LLM configured")
            else:
                print_status("warning", "Add USE_MOCK_LLM=True to backend/.env for testing")
    else:
        print_status("warning", "Backend .env not found - copy from .env.example")
        print(f"    Run: cp backend/.env.example backend/.env")
    
    if os.path.exists("frontend/.env"):
        print_status("success", "Frontend .env file exists")
    else:
        print_status("warning", "Frontend .env not found")
        print(f'    Run: echo "VITE_API_URL=http://localhost:8000" > frontend/.env')

def check_git_setup():
    print(f"\n{BLUE}Checking Git Setup...{NC}")
    
    if os.path.exists(".git"):
        print_status("success", "Git repository initialized")
        
        # Check remote
        try:
            result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
            if 'github.com/Kowshik13' in result.stdout:
                print_status("success", "GitHub remote configured")
            else:
                print_status("warning", "GitHub remote not set")
                print("    Run: git remote add origin https://github.com/Kowshik13/multi-agent-risk-reporting.git")
        except:
            pass
    else:
        print_status("warning", "Git not initialized")
        print("    Run: git init")
    
    if os.path.exists(".gitignore"):
        print_status("success", ".gitignore file exists")
        with open(".gitignore", "r") as f:
            content = f.read()
            if ".env" in content:
                print_status("success", ".env files excluded from git")
            else:
                print_status("error", ".env not in .gitignore - add it!")

def main():
    print(f"{BLUE}{'='*50}{NC}")
    print(f"{BLUE}Risk Copilot - Installation Verification{NC}")
    print(f"{BLUE}{'='*50}{NC}")
    
    # Check prerequisites
    print(f"\n{BLUE}Checking Prerequisites...{NC}")
    check_python_version()
    check_node_version()
    
    # Check project structure
    backend_ok = verify_backend_structure()
    frontend_ok = verify_frontend_structure()
    
    # Check environment
    check_env_setup()
    
    # Check git
    check_git_setup()
    
    # Summary
    print(f"\n{BLUE}{'='*50}{NC}")
    if backend_ok and frontend_ok:
        print_status("success", "All required files are in place!")
        print(f"\n{GREEN}Ready to run!{NC}")
        print(f"\n{YELLOW}Next steps:{NC}")
        print("1. Set up environment: ./setup.sh")
        print("2. Start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload")
        print("3. Start frontend: cd frontend && npm run dev")
        print("4. Open browser: http://localhost:5173")
    else:
        print_status("error", "Some files are missing. Please check the errors above.")
        print(f"\n{YELLOW}Need to re-download files from the outputs folder{NC}")
    
    print(f"{BLUE}{'='*50}{NC}")

if __name__ == "__main__":
    main()
