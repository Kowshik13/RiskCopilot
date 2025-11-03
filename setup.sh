#!/bin/bash

# Risk Copilot Setup Script
# This script sets up both backend and frontend environments

echo "🚀 Setting up Risk Copilot..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"

# Backend setup
echo -e "\n${YELLOW}Setting up backend...${NC}"
cd backend

# Create virtual environment
python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
echo "✅ Python dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env file created from .env.example"
    echo -e "${YELLOW}⚠️  Please update .env with your API keys${NC}"
fi

# Create data directories
mkdir -p data/policies data/index data/audit
echo "✅ Data directories created"

# Deactivate virtual environment
deactivate

cd ..

# Frontend setup
echo -e "\n${YELLOW}Setting up frontend...${NC}"
cd frontend

# Install npm dependencies
npm install
echo "✅ Node dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "VITE_API_URL=http://localhost:8000" > .env
    echo "✅ Frontend .env file created"
fi

cd ..

echo -e "\n${GREEN}🎉 Setup complete!${NC}"
echo -e "\nTo start the application:"
echo -e "${YELLOW}Backend:${NC}"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo -e "\n${YELLOW}Frontend:${NC}"
echo "  cd frontend"
echo "  npm run dev"
echo -e "\n${YELLOW}Then open:${NC} http://localhost:5173"
