#!/bin/bash

# SANSA Development Helper Script
# Quick commands for common development tasks

BACKEND_DIR="backend"
FRONTEND_DIR="frontend"

function show_help() {
    echo "SANSA Development Helper"
    echo ""
    echo "Usage: ./dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start-backend     Start FastAPI backend server"
    echo "  start-frontend    Start React frontend dev server"
    echo "  start-all         Start both backend and frontend (requires tmux)"
    echo "  migrate           Run database migrations"
    echo "  seed              Seed database with default data"
    echo "  reset-db          Reset database (downgrade + upgrade + seed)"
    echo "  test-backend      Run backend tests"
    echo "  build-frontend    Build frontend for production"
    echo "  install           Install all dependencies"
    echo "  clean             Clean build artifacts and caches"
    echo "  logs              Show recent logs"
    echo "  help              Show this help message"
    echo ""
}

function start_backend() {
    echo "🚀 Starting backend server..."
    cd $BACKEND_DIR
    source venv/bin/activate
    uvicorn app.main:app --reload
}

function start_frontend() {
    echo "🚀 Starting frontend dev server..."
    cd $FRONTEND_DIR
    npm run dev
}

function start_all() {
    if ! command -v tmux &> /dev/null; then
        echo "❌ tmux is required for start-all. Install with: brew install tmux"
        echo "Or start backend and frontend in separate terminals:"
        echo "  Terminal 1: ./dev.sh start-backend"
        echo "  Terminal 2: ./dev.sh start-frontend"
        exit 1
    fi

    tmux new-session -d -s sansa
    tmux rename-window -t sansa:0 'SANSA'
    tmux split-window -h -t sansa:0
    tmux send-keys -t sansa:0.0 "cd $BACKEND_DIR && source venv/bin/activate && uvicorn app.main:app --reload" C-m
    tmux send-keys -t sansa:0.1 "cd $FRONTEND_DIR && npm run dev" C-m
    tmux attach-session -t sansa
}

function migrate() {
    echo "🔄 Running database migrations..."
    cd $BACKEND_DIR
    source venv/bin/activate
    alembic upgrade head
    echo "✅ Migrations complete"
}

function seed() {
    echo "🌱 Seeding database..."
    cd $BACKEND_DIR
    source venv/bin/activate
    python scripts/seed.py
    echo "✅ Seeding complete"
}

function reset_db() {
    echo "⚠️  WARNING: This will delete all data!"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Cancelled"
        exit 0
    fi
    
    echo "🔄 Resetting database..."
    cd $BACKEND_DIR
    source venv/bin/activate
    alembic downgrade base
    alembic upgrade head
    python scripts/seed.py
    echo "✅ Database reset complete"
}

function test_backend() {
    echo "🧪 Running backend tests..."
    cd $BACKEND_DIR
    source venv/bin/activate
    pytest
}

function build_frontend() {
    echo "🏗️  Building frontend for production..."
    cd $FRONTEND_DIR
    npm run build
    echo "✅ Build complete: $FRONTEND_DIR/dist"
}

function install_deps() {
    echo "📦 Installing backend dependencies..."
    cd $BACKEND_DIR
    python3 -m venv venv 2>/dev/null || true
    source venv/bin/activate
    pip install --quiet -r requirements.txt
    cd ..
    
    echo "📦 Installing frontend dependencies..."
    cd $FRONTEND_DIR
    npm install --silent
    cd ..
    
    echo "✅ All dependencies installed"
}

function clean() {
    echo "🧹 Cleaning build artifacts..."
    
    # Backend
    cd $BACKEND_DIR
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    cd ..
    
    # Frontend
    cd $FRONTEND_DIR
    rm -rf dist node_modules/.cache 2>/dev/null || true
    cd ..
    
    echo "✅ Cleanup complete"
}

function show_logs() {
    echo "📋 Recent logs (if logging is configured):"
    echo ""
    if [ -d "$BACKEND_DIR/logs" ]; then
        tail -n 50 $BACKEND_DIR/logs/*.log 2>/dev/null || echo "No logs found"
    else
        echo "Log directory not configured"
    fi
}

# Main command router
case "$1" in
    start-backend)
        start_backend
        ;;
    start-frontend)
        start_frontend
        ;;
    start-all)
        start_all
        ;;
    migrate)
        migrate
        ;;
    seed)
        seed
        ;;
    reset-db)
        reset_db
        ;;
    test-backend)
        test_backend
        ;;
    build-frontend)
        build_frontend
        ;;
    install)
        install_deps
        ;;
    clean)
        clean
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        if [ -z "$1" ]; then
            show_help
        else
            echo "❌ Unknown command: $1"
            echo ""
            show_help
            exit 1
        fi
        ;;
esac
