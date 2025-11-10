#!/bin/bash
# Quick Start Script for Ethio Bingo

echo "🎉 Ethio Bingo - Quick Start Setup"
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your configuration:"
    echo "   - TELEGRAM_BOT_TOKEN (required)"
    echo "   - TELEGRAM_WEBHOOK_URL (required for production)"
    echo "   - SECRET_KEY (auto-generated if not set)"
    echo "   - JWT_SECRET_KEY (auto-generated if not set)"
    echo ""
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo "❌ Python 3.9+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Check if PostgreSQL is available
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL found"
else
    echo "⚠️  PostgreSQL not found. Please install PostgreSQL 12+"
    echo "   Ubuntu/Debian: sudo apt-get install postgresql"
    echo "   macOS: brew install postgresql"
fi

# Check if Redis is available
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is installed but not running"
        echo "   Start with: sudo systemctl start redis"
    fi
else
    echo "⚠️  Redis not found. Please install Redis 6+"
    echo "   Ubuntu/Debian: sudo apt-get install redis-server"
    echo "   macOS: brew install redis"
fi

# Ask user what they want to do
echo ""
echo "What would you like to do?"
echo "1. Setup database"
echo "2. Run tests"
echo "3. Start development server"
echo "4. Start production server (Docker)"
echo "5. Exit"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🗄️  Setting up database..."
        python3 -c "from src.core.database import init_db; init_db(); print('✅ Database initialized successfully!')"
        ;;
    2)
        echo ""
        echo "🧪 Running tests..."
        pytest -v
        ;;
    3)
        echo ""
        echo "🚀 Starting development server..."
        echo "   Make sure PostgreSQL and Redis are running!"
        echo "   Press Ctrl+C to stop"
        echo ""
        python3 main.py
        ;;
    4)
        echo ""
        if command -v docker-compose &> /dev/null; then
            echo "🐳 Starting with Docker Compose..."
            docker-compose up -d
            echo "✅ Services started!"
            echo "   View logs: docker-compose logs -f"
            echo "   Stop: docker-compose down"
        else
            echo "❌ Docker Compose not found. Please install Docker and Docker Compose"
        fi
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "📖 For more information, see:"
echo "   - ETHIO_BINGO_GUIDE.md - Complete user guide"
echo "   - DEPLOYMENT.md - Production deployment guide"
echo "   - README.md - Original specification"
echo ""
