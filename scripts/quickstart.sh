#!/bin/bash

# CreditBeast Quick Start Script
# This script helps you set up the development environment quickly

set -e  # Exit on error

echo "=================================="
echo "CreditBeast Quick Start"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from project root
if [ ! -f "README.md" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

echo "Step 1: Checking prerequisites..."
echo ""

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js ${NODE_VERSION} found${NC}"
else
    echo -e "${RED}✗ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ ${PYTHON_VERSION} found${NC}"
else
    echo -e "${RED}✗ Python3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

# Check pnpm (optional)
if command -v pnpm &> /dev/null; then
    PNPM_VERSION=$(pnpm --version)
    echo -e "${GREEN}✓ pnpm ${PNPM_VERSION} found${NC}"
    PKG_MANAGER="pnpm"
else
    echo -e "${YELLOW}! pnpm not found, using npm${NC}"
    PKG_MANAGER="npm"
fi

echo ""
echo "Step 2: Setting up backend..."
echo ""

# Backend setup
cd apps/api

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}! Please edit apps/api/.env with your actual credentials${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

cd ../..

echo ""
echo "Step 3: Setting up frontend..."
echo ""

# Frontend setup
cd apps/web

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    $PKG_MANAGER install
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Dependencies already installed${NC}"
fi

if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file from template..."
    cp .env.example .env.local
    echo -e "${YELLOW}! Please edit apps/web/.env.local with your actual credentials${NC}"
else
    echo -e "${GREEN}✓ .env.local file already exists${NC}"
fi

cd ../..

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Configure your environment variables:"
echo "   - Edit apps/api/.env with Supabase, Clerk, and Stripe credentials"
echo "   - Edit apps/web/.env.local with frontend credentials"
echo ""
echo "2. Set up your database:"
echo "   - Create a Supabase project at https://supabase.com"
echo "   - Run the SQL schema from docs/DATABASE_SCHEMA.sql"
echo ""
echo "3. Start the development servers:"
echo ""
echo "   Terminal 1 (Backend):"
echo "   $ cd apps/api"
echo "   $ source venv/bin/activate"
echo "   $ uvicorn main:app --reload"
echo ""
echo "   Terminal 2 (Frontend):"
echo "   $ cd apps/web"
echo "   $ $PKG_MANAGER dev"
echo ""
echo "4. Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/api/docs"
echo ""
echo "For detailed instructions, see docs/SETUP.md"
echo ""
echo -e "${GREEN}Happy coding!${NC}"
echo ""
