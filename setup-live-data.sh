#!/bin/bash

set -e

echo "🚀 PennyStock Live Data Setup"
echo "================================"
echo ""

# Check if running from correct directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the PennyStock root directory"
    exit 1
fi

echo "📦 Step 1: Installing backend dependencies..."
cd backend
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

echo "🗄️  Step 2: Initializing PostgreSQL database..."
python3 << 'EOF'
import sys
try:
    from app.database import init_db
    init_db()
    print("✓ Database tables created successfully!")
except Exception as e:
    print(f"⚠️  Note: {e}")
    print("Make sure PostgreSQL is running:")
    print("  - Docker: docker run -d --name pennystock-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=pennystock -p 5432:5432 postgres:15")
    print("  - Or local: psql -U postgres -c 'CREATE DATABASE pennystock;'")
    sys.exit(1)
EOF
echo ""

cd ..

echo "📊 Summary of what was set up:"
echo "================================"
echo ""
echo "✓ Backend dependencies installed"
echo "✓ Database schema created"
echo ""
echo "🎯 Next steps:"
echo ""
echo "Terminal 1 - Start Backend API:"
echo "  $ cd backend"
echo "  $ python3 -m uvicorn app.api.main:app --reload --port 8000"
echo ""
echo "Terminal 2 - Sync Live Data (after backend starts):"
echo "  $ curl -X POST 'http://localhost:8000/sync-data' \\\"
echo "    -H 'Content-Type: application/json' \\\"
echo "    -d '[\"KILITCH\", \"PIXTRANS\", \"RISKY\"]'"
echo ""
echo "Terminal 3 - Start Frontend:"
echo "  $ cd frontend"
echo "  $ npm install  # first time only"
echo "  $ npm run dev"
echo ""
echo "🌐 Then visit: http://localhost:3000"
echo ""
echo "📖 For detailed setup instructions, see: LIVE_DATA_SETUP.md"
