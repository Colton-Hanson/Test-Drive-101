#!/bin/bash

# Bill Dashboard Quick Start Script

echo "🚀 Starting Bill Payment Dashboard..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before running the app!"
    exit 1
fi

# Initialize database if needed
if [ ! -f "database/bills.db" ]; then
    echo "🗄️  Initializing database..."
    mkdir -p database
    python -c "from backend.app import app, db; app.app_context().push(); db.create_all(); print('✅ Database initialized!')"
fi

# Start the application
echo "✨ Starting Flask server..."
echo "📱 Open http://localhost:5000 in your browser"
echo ""
python backend/app.py
