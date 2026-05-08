# 🚀 PennyStock: Demo vs Live Data

## Quick Comparison

| Feature | Demo Mode | Live Data Mode |
|---------|-----------|-----------------|
| **Data Source** | Hardcoded 3 stocks | PostgreSQL Database |
| **Updates** | Static | Real-time from market APIs |
| **Database** | ❌ None | ✅ PostgreSQL |
| **Setup Time** | 5 minutes | 15 minutes |
| **Real Recommendations** | ❌ Test data | ✅ Actual market analysis |

---

## 🎯 You Are Currently In: Demo Mode

Your app is running with **test data** (demo universe):
- KILITCH
- PIXTRANS  
- RISKY

These are hardcoded in the code.

---

## ✅ To Switch to Live Data Mode:

### Quick Start (5 steps)

#### 1️⃣ Start PostgreSQL
```bash
docker run -d --name pennystock-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=pennystock \
  -p 5432:5432 postgres:15
```

#### 2️⃣ Install additional dependencies
```bash
cd /workspaces/PennyStock/backend
pip install psycopg2-binary requests
```

#### 3️⃣ Initialize database
```bash
cd /workspaces/PennyStock/backend
python3 << 'EOF'
from app.database import init_db
init_db()
print("✓ Database ready!")
EOF
```

#### 4️⃣ Start backend (it will auto-initialize DB on startup)
```bash
cd /workspaces/PennyStock/backend
python3 -m uvicorn app.api.main:app --reload --port 8000
```

#### 5️⃣ Sync live data
```bash
curl -X POST "http://localhost:8000/sync-data" \
  -H "Content-Type: application/json" \
  -d '["KILITCH", "PIXTRANS", "RISKY"]'
```

---

## 📡 How It Works Now

```
🔄 Old Flow (Demo)
┌─────────────────────────────────────┐
│ FastAPI Endpoint                    │
│  /weekly-recommendations            │
└────────────┬────────────────────────┘
             │
             ├─> demo_universe() ← Hardcoded data
             │
             ├─> screen_stocks()
             │
             ├─> score_stock()
             │
             └─> generate_weekly_recommendations()
                    │
                    └─> Return to dashboard


🔄 New Flow (Live Data)
┌─────────────────────────────────────┐
│ FastAPI Endpoint                    │
│  /weekly-recommendations            │
└────────────┬────────────────────────┘
             │
             ├─> get_universe()
             │    │
             │    └─> get_stocks_from_db()
             │         │
             │         └─> PostgreSQL 🗄️
             │
             ├─> screen_stocks()
             │
             ├─> score_stock()
             │
             └─> generate_weekly_recommendations()
                    │
                    └─> Return REAL recommendations!
```

---

## 🔗 New Endpoints (Live Data Mode)

### Get Live Data Status
```bash
curl http://localhost:8000
```
Returns: Welcome message + available endpoints

### Sync Stocks from APIs
```bash
curl -X POST "http://localhost:8000/sync-data" \
  -H "Content-Type: application/json" \
  -d '["SBIN", "RELIANCE", "TCS"]'
```

### Get Recommendations (Now from Live Data!)
```bash
curl "http://localhost:8000/weekly-recommendations"
```

### View Database Data
```sql
-- Connect to PostgreSQL
psql -h localhost -U postgres -d pennystock

-- View stocks
SELECT * FROM stocks;

-- View metrics
SELECT * FROM stock_metrics;
```

---

## 🎓 Understanding the Architecture

### Backend Services

1. **`app/database.py`** - SQLAlchemy ORM definitions
   - `StockModel` - Stores stock fundamentals
   - `StockMetricsModel` - Stores technical/risk metrics

2. **`app/services/data_ingestion.py`** - Market data fetching
   - `fetch_stock_from_yfinance()` - Yahoo Finance API
   - `fetch_stock_from_finnhub()` - Finnhub API
   - `sync_stocks_from_universe()` - Batch sync
   - `get_stocks_from_db()` - Database retrieval

3. **`app/api/main.py`** - API endpoints
   - `get_universe()` - Smart fallback (DB → demo)
   - `/sync-data` - Trigger data sync
   - `/weekly-recommendations` - Get recommendations

---

## 🌍 Market Data Sources

### Yahoo Finance (Free, No API Key)
- ✅ Free
- ✅ No registration
- ❌ Rate limited
- Ticker format: `SYMBOL.NS` (NSE)

### Finnhub (Free Tier)
- ✅ Free tier available
- ✅ More data points
- ⚠️ Requires API key signup at https://finnhub.io
- Usage:
  ```bash
  export FINNHUB_API_KEY="your_key"
  python3 -m uvicorn app.api.main:app --reload --port 8000
  ```

### Custom Data Import
- Load CSV/Excel with stock data
- Use `POST /import-data` endpoint (future)

---

## 🐛 Troubleshooting

### PostgreSQL Connection Error
```
Error: could not connect to server
```
**Fix:** Start PostgreSQL
```bash
docker ps | grep pennystock-db
# If not running:
docker start pennystock-db
```

### No Stocks in Database
```
Solution:
1. Ensure backend is running with `init_db()` on startup
2. Call `/sync-data` endpoint to populate
3. Check database: psql -h localhost -U postgres -d pennystock -c "SELECT COUNT(*) FROM stocks;"
```

### Module Import Errors
```
ModuleNotFoundError: No module named 'app.database'
```
**Fix:** Make sure you:
1. `cd /workspaces/PennyStock/backend`
2. `pip install -r requirements.txt`

---

## 📝 Next Steps

- [x] Understand demo vs live mode difference
- [ ] Set up PostgreSQL
- [ ] Install dependencies
- [ ] Initialize database
- [ ] Sync live stock data
- [ ] View real recommendations
- [ ] Customize stock universe
- [ ] Add more data sources

---

## 🎯 FAQ

**Q: Can I use both demo and live data?**
A: Yes! The app automatically falls back to demo data if the database is empty.

**Q: How often does data update?**
A: You control it! Call `/sync-data` whenever you want to refresh.

**Q: Can I add my own stocks?**
A: Yes! Just pass them to `/sync-data`:
```bash
curl -X POST "http://localhost:8000/sync-data" \
  -H "Content-Type: application/json" \
  -d '["SBIN", "INFY", "TATAMOTORS", "YOURSTOCK"]'
```

**Q: What if I don't want a database?**
A: The demo mode will continue to work! Just don't set up PostgreSQL.

---

For detailed setup instructions, see [LIVE_DATA_SETUP.md](LIVE_DATA_SETUP.md)
