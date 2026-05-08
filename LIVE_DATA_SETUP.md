# PennyStock - Live Data Setup Guide

This guide walks you through setting up the PennyStock application to run with **live market data** instead of demo data.

## Prerequisites

- PostgreSQL 12+ (local or Docker)
- Python 3.9+
- Node.js 18+

---

## Step 1: Set Up PostgreSQL Database

### Option A: Using Docker (Recommended)

```bash
# Install Docker if you haven't already, then:

docker run -d \
  --name pennystock-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=pennystock \
  -p 5432:5432 \
  postgres:15
```

Wait 10 seconds for PostgreSQL to start, then verify:

```bash
psql -h localhost -U postgres -d pennystock -c "SELECT version();"
```

### Option B: Local PostgreSQL Installation

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
sudo -u postgres createdb pennystock
```

**macOS (with Homebrew):**
```bash
brew install postgresql
brew services start postgresql
createdb pennystock
```

**Verify the connection:**
```bash
psql -h localhost -U postgres -d pennystock -c "SELECT version();"
```

---

## Step 2: Install Backend Dependencies

```bash
cd /workspaces/PennyStock/backend
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

This installs:
- `SQLAlchemy` - ORM for database
- `psycopg2-binary` - PostgreSQL driver
- `requests` - For live data APIs

---

## Step 3: Initialize the Database

Run this Python script to create tables:

```bash
cd /workspaces/PennyStock/backend

python3 << 'EOF'
from app.database import init_db
init_db()
print("✓ Database tables created successfully!")
EOF
```

---

## Step 4: Start the Backend Server

```bash
cd /workspaces/PennyStock/backend
python3 -m uvicorn app.api.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
✓ Database initialized
```

---

## Step 5: Sync Live Market Data

Open **new terminal** and run:

```bash
curl -X POST "http://localhost:8000/sync-data" \
  -H "Content-Type: application/json" \
  -d '["KILITCH", "PIXTRANS", "RISKY"]'
```

Or use the API docs at `http://localhost:8000/docs`:
1. Go to `POST /sync-data`
2. Click "Try it out"
3. Click "Execute"

You should see:
```json
{
  "status": "success",
  "message": "Syncing 3 stocks from live market data",
  "symbols": ["KILITCH", "PIXTRANS", "RISKY"]
}
```

---

## Step 6: Verify Live Data

Check that data was synced:

```bash
# Get top-ranked stocks (now from database!)
curl http://localhost:8000/top-ranked | python3 -m json.tool

# Get weekly recommendations
curl "http://localhost:8000/weekly-recommendations?monthly_invested=0" | python3 -m json.tool
```

---

## Step 7: Start Frontend Dashboard

In a **new terminal**:

```bash
cd /workspaces/PennyStock/frontend
npm install  # First time only
npm run dev
```

Open: `http://localhost:3000`

---

## Architecture

```
dashboard (localhost:3000)
         ↓
   API (localhost:8000)
         ↓
   PostgreSQL (localhost:5432)
         ↓
   Live Market Data APIs (Yahoo Finance, etc.)
```

---

## Common Issues & Fixes

### "Connection refused" error
```
Problem: PostgreSQL not running
Fix: docker ps OR sudo service postgresql status
```

### "Database error" on /sync-data
```
Problem: Database not initialized
Fix: Run Step 3 (database initialization)
```

### "No such file or directory" app module
```
Problem: Not in backend directory
Fix: cd /workspaces/PennyStock/backend
```

### "Module not found: requests"
```
Problem: Dependencies not installed
Fix: pip install -r requirements.txt
```

---

## Adding Your Own Stocks

Edit the `/sync-data` endpoint call:

```bash
curl -X POST "http://localhost:8000/sync-data" \
  -H "Content-Type: application/json" \
  -d '["SBIN", "RELIANCE", "TCS", "INFY"]'
```

---

## Data Sources

The app uses:
1. **Yahoo Finance** (free, no API key)
2. **Finnhub** (free tier, requires API key)
3. **Custom data import** (DIY)

To use Finnhub:
```bash
export FINNHUB_API_KEY="your_api_key_here"
python3 -m uvicorn app.api.main:app --reload --port 8000
```

---

## Development Workflow

1. **Make database changes** → Edit `app/database.py`
2. **Test new endpoints** → Call `http://localhost:8000/docs`
3. **Add data fields** → Update `StockModel` in `database.py`
4. **Resync data** → Call `POST /sync-data`

---

## Next Steps

- [ ] Set up PostgreSQL
- [ ] Install dependencies
- [ ] Initialize database
- [ ] Start backend
- [ ] Sync live data
- [ ] Start frontend
- [ ] Visit `http://localhost:3000`

Good luck! 🚀
