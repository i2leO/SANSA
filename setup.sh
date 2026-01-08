#!/bin/bash

# SANSA System Setup Script
# Run this after cloning the repository

set -e  # Exit on error

echo "🚀 SANSA System Setup"
echo "===================="
echo ""

# Check prerequisites
echo "✓ Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }
command -v mysql >/dev/null 2>&1 || { echo "❌ MySQL is required but not installed."; exit 1; }
echo "✅ All prerequisites found"
echo ""

# Backend setup
echo "📦 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

echo "  Activating virtual environment..."
source venv/bin/activate

echo "  Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

if [ ! -f ".env" ]; then
    echo "  Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit backend/.env with your database credentials and JWT secret!"
    echo "   - DATABASE_URL: Update username, password, database name"
    echo "   - JWT_SECRET_KEY: Generate a secure random string (min 32 chars)"
    echo ""
    read -p "Press Enter after editing backend/.env to continue..."
fi

echo "  Running database migrations..."
alembic upgrade head

echo "  Seeding database with default data..."
python scripts/seed.py

echo "✅ Backend setup complete"
cd ..
echo ""

# Frontend setup
echo "📦 Setting up frontend..."
cd frontend

echo "  Installing npm dependencies..."
npm install --silent

if [ ! -f ".env" ]; then
    echo "  Creating .env file..."
    cp .env.example .env
fi

echo "✅ Frontend setup complete"
cd ..
echo ""

# Final instructions
echo "✅ Setup Complete!"
echo ""
echo "📚 Next Steps:"
echo ""
echo "1. Start Backend (in terminal 1):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo "   → API: http://localhost:8000"
echo "   → Docs: http://localhost:8000/docs"
echo ""
echo "2. Start Frontend (in terminal 2):"
echo "   cd frontend"
echo "   npm run dev"
echo "   → App: http://localhost:5173"
echo ""
echo "3. Default Admin Login:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   ⚠️  Change password after first login!"
echo ""
echo "📖 Documentation: See docs/ directory and README.md"
echo ""
