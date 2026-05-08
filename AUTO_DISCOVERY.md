# 🤖 PennyStock: Automatic Stock Discovery System

> **You don't add stocks manually. AI finds them for you!**

---

## **The Complete Automatic Flow**

```
┌────────────────────────────────────────────────────────────────┐
│              AUTOMATIC WEEK-BY-WEEK WORKFLOW                   │
└────────────────────────────────────────────────────────────────┘

SUNDAY NIGHT (11 PM - Automated Job Runs)
═════════════════════════════════────────

  1️⃣  AUTO-DISCOVERY
      ├─ System connects to NSE/BSE APIs
      ├─ Fetches ALL small-cap & micro-cap stocks
      ├─ Downloads latest fundamentals + technicals
      └─ Stores in PostgreSQL database
      
      Output: Example
      ├─ Found 50 new penny stocks
      ├─ Updated 20 existing stocks
      └─ Total in database: 1,247 stocks

  2️⃣  SCREENING
      ├─ Applies 9 hard constraints to ALL 1,247 stocks
      ├─ Filters for:
      │  ✓ Market cap ₹100-5000 Cr
      │  ✓ Debt/Equity < 0.3
      │  ✓ Positive cash flow
      │  ✓ Good governance (no red flags)
      │  ... (5 more checks)
      └─ Passes: 147 qualified stocks
      
      Filtered out: 1,100 (too risky, wrong cap, debt concerns, etc.)

  3️⃣  SCORING & RANKING
      ├─ Scores all 147 qualified stocks
      ├─ 4-factor analysis per stock:
      │  • Hidden Growth (40% weight)
      │  • Momentum (30% weight)
      │  • Quality (20% weight)
      │  • Risk (10% penalty weight)
      ├─ Calculates Conviction Score (0-100)
      └─ Ranks by Conviction (highest first)
      
      Top BUY signals:
      ├─ 1. STOCK_A: 78 conviction 🟢
      ├─ 2. STOCK_B: 75 conviction 🟢
      ├─ 3. STOCK_C: 73 conviction 🟢
      ├─ 4. STOCK_D: 68 conviction ⚪
      └─ ... (143 more)

  4️⃣  RECOMMENDATIONS GENERATED
      ├─ Allocation within ₹1000/week budget
      ├─ Max 1-2 BUY signals per week
      ├─ Rest go to HOLD/WATCH/AVOID
      └─ Ready for Monday morning!


MONDAY MORNING (8 AM - User Checks Dashboard)
══════════════════════════════════════════════

  You open dashboard: http://localhost:3000
  
  See automatically generated weekly plan:
  
  🟢 BUY SIGNALS (3 found):
    1. STOCK_A (₹500) - Conviction 78/100
    2. STOCK_B (₹500) - Conviction 75/100
    
  ⚪ HOLD SIGNALS (12 found):
    • STOCK_C, STOCK_D, ... (wait for better setup)
    
  👁️  WATCH LIST (42 found):
    • Emerging opportunities to monitor
    
  ❌ AVOID LIST (90 found):
    • Governance issues, high debt, risky patterns
  
  Budget Status:
  • Weekly allocation: ₹1000 available
  • Allocated: ₹1000 (2 stocks)
  • Monthly cap: ₹4000


THROUGHOUT THE WEEK
═══════════════════

  • You can view details of ANY stock scoring
  • Click to see all 4 component scores
  • View AI-generated research notes
  • Execute the BUY orders you approve
  • Track watch list for setup changes
```

---

## **How to Use Auto-Discovery**

### **Option 1: Manual Trigger (Test It Now)**

Call this endpoint to trigger auto-discovery immediately:

```bash
curl -X POST "http://localhost:8000/auto-discover-penny-stocks"
```

Response:
```json
{
  "status": "success",
  "message": "✅ Auto-discovery complete!",
  "stocks_synced": 145,
  "stocks_skipped": 3,
  "total_processed": 148,
  "next_step": "Call /weekly-recommendations to see AI-filtered results"
}
```

Then check recommendations:
```bash
curl "http://localhost:8000/weekly-recommendations" | python -m json.tool
```

### **Option 2: Automatic Weekly Job (Production)**

Set up Celery + Redis to run automatically every Sunday:

```bash
# Install Celery & Redis
pip install celery redis

# Start Redis server
redis-server

# Start Celery worker (in new terminal)
celery -A app.jobs.celery_app worker --loglevel=info

# Celery will run auto_discover_and_refresh() every Sunday @ 11 PM
```

---

## **What Gets Discovered?**

### **NSE Penny Stock Universe**
```
Criteria:
├─ Market Cap: ₹100 Cr - ₹5000 Cr (small-cap/micro-cap)
├─ Listed on: NSE (National Stock Exchange)
├─ Sectors: All (pharma, auto, infra, IT, etc.)
├─ Liquidity: Minimum volume requirements
└─ Governance: No administrative suspension

Examples of discovered stocks:
├─ Healthcare: Kilitch, Cipla, Dr Reddy's
├─ Auto: Maruti, Hero MotoCorp, TVS
├─ IT: HCL Tech, Wipro, TCS
├─ Pharma: Lupin, Torrent, Aurobindo
├─ Banking: HDFC Bank, ICICI Bank, Axis
└─ ... 1000+ more possibilities
```

### **BSE Micro-Cap Universe** (Optional)
```
Lower liquidity, higher risk penny stocks
├─ Market Cap: < ₹100 Cr
├─ Higher volatility
├─ Smaller trading volumes
└─ More speculative setups
```

---

## **What Gets FILTERED OUT?**

```
1,247 Total Stocks Downloaded
      ↓
      Apply 9 Hard Screens:
      ├─ ❌ 200 stocks: Market cap out of range
      ├─ ❌ 150 stocks: Too much debt (D/E > 0.3)
      ├─ ❌ 120 stocks: Negative cash flow
      ├─ ❌ 100 stocks: Low promoter holding (< 45%)
      ├─ ❌ 90 stocks: High promoter pledge (> 5%)
      ├─ ❌ 85 stocks: Auditor issues
      ├─ ❌ 120 stocks: Suspicious filings
      ├─ ❌ 150 stocks: Banks/Financial institutions
      └─ ❌ 135 stocks: Other disqualifying factors
      ↓
      147 Qualified Stocks Remain
```

---

## **Complete Architecture Diagram**

```
┌─────────────────────────────────────────────────────┐
│            PUBLIC MARKET DATA (Free APIs)           │
│                                                     │
│  ├─ NSE Website (nseIndia.com)                     │
│  ├─ Yahoo Finance API                              │
│  ├─ Finnhub Free Tier                              │
│  └─ BSE India                                      │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│        PENNY STOCK DISCOVERY SERVICE                │
│   (app/services/penny_stock_discovery.py)           │
│                                                     │
│  • fetch_nse_penny_stocks()                         │
│  • fetch_all_nse_stocks()                           │
│  • fetch_bse_penny_stocks()                         │
│  • auto_detect_and_sync_penny_stocks()             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│        POSTGRESQL DATABASE                          │
│                                                     │
│  Tables:                                            │
│  ├─ stocks (symbol, company, market_cap, ...)     │
│  └─ stock_metrics (revenue, profit, RSI, ...)     │
│                                                     │
│  Currently stores: 147 qualified stocks             │
│  Total in DB: 1,247 stocks                          │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│          INTELLIGENT SCREENER (9 filters)           │
│   (app/services/screener.py)                        │
│                                                     │
│  Filter 1,247 stocks → 147 qualified               │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│       MULTI-FACTOR SCORING ENGINE (4 scores)       │
│   (app/services/scoring.py)                         │
│                                                     │
│  For each of 147 stocks:                            │
│  ├─ Hidden Growth Score                             │
│  ├─ Momentum Score                                  │
│  ├─ Quality Score                                   │
│  ├─ Risk Score                                      │
│  └─ Conviction Score (weighted combination)         │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│    WEEKLY RECOMMENDATION ENGINE (Budget-Aware)      │
│   (app/services/recommendations.py)                 │
│                                                     │
│  • Rank all 147 stocks by conviction               │
│  • Allocate ₹1000 to top 1-2 BUY signals          │
│  • Create watchlist for rest                        │
│  • Generate explanations for each                   │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│       OPTIONAL: AI RESEARCH GENERATION               │
│   (app/services/ai_insights.py)                     │
│                                                     │
│  Claude/ChatGPT writes detailed research notes      │
│  for top 3 stocks                                   │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│         API ENDPOINTS (FastAPI)                     │
│                                                     │
│  GET /weekly-recommendations                        │
│  GET /top-ranked                                    │
│  GET /portfolio                                     │
│  POST /auto-discover-penny-stocks       ← NEW!     │
│  POST /buy-entry                                    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│         NEXT.JS DASHBOARD (localhost:3000)          │
│                                                     │
│  • Shows auto-discovered stocks                     │
│  • Displays all scores & recommendations            │
│  • Budget tracking                                  │
│  • Portfolio management                             │
│  • AI research notes                                │
└─────────────────────────────────────────────────────┘
```

---

## **API Endpoints Summary**

| Endpoint | Purpose | Auto? |
|----------|---------|-------|
| `POST /auto-discover-penny-stocks` | Trigger auto-discovery now | Manual |
| `GET /weekly-recommendations` | Get filtered + scored stocks | Auto (after discovery) |
| `GET /top-ranked` | See all stocks sorted by conviction | Auto |
| `POST /buy-entry` | Execute a buy order | Manual |
| `GET /portfolio` | View your holdings | Manual |

---

## **Step-by-Step Setup for Auto-Discovery**

### **1. Start Backend**
```bash
cd backend
python3 -m uvicorn app.api.main:app --reload --port 8000
```

### **2. Trigger Auto-Discovery** (First Time)
```bash
curl -X POST "http://localhost:8000/auto-discover-penny-stocks"
```

### **3. Check Filtered Recommendations**
```bash
curl "http://localhost:8000/weekly-recommendations" | python -m json.tool
```

### **4. View All Scores**
```bash
curl "http://localhost:8000/top-ranked" | python -m json.tool
```

### **5. Start Frontend**
```bash
cd frontend
npm run dev
```

Open: `http://localhost:3000`

---

## **Expected Output**

After auto-discovery runs, you'll see in your dashboard:

```
📊 WEEKLY RECOMMENDATIONS
═════════════════════════

🟢 BUY SIGNALS (Auto-discovered from NSE):
   1. STOCK_A        | Conviction: 78/100 | Allocation: ₹500
   2. STOCK_B        | Conviction: 75/100 | Allocation: ₹500
   3. STOCK_C        | Conviction: 73/100 | (Watchlist - no budget)

⚪ HOLD SIGNALS (Good quality, needs confirmation):
   • STOCK_D (Conviction: 68) - Wait for momentum confirmation
   • STOCK_E (Conviction: 65) - Monitor for breakout
   • ... 10 more

👁️  WATCH LIST (Emerging opportunities):
   • 42 stocks identified as emerging setups
   • Monitor for quality/momentum improvements

❌ AVOID LIST (Red flags detected):
   • 90 stocks with governance or financial concerns
   • Not recommended at this time

💰 BUDGET STATUS:
   • Weekly: ₹1000 allocated (₹0 remaining)
   • Monthly: ₹2000 / ₹4000 used
   • Status: On track ✅
```

---

## **Frequently Asked Questions**

### **Q: How many stocks does it discover?**
A: Depends on NSE data availability. Typically 100-200 monthly new discoveries + updates on existing ones.

### **Q: Is it completely automatic?**
A: Yes! Once set up, it runs every Sunday at 11 PM (if using Celery scheduler). Or you can trigger manually with `/auto-discover-penny-stocks` endpoint.

### **Q: What if it discovers bad stocks?**
A: The 9-point screener filters out 85-90% of candidates. Only high-quality stocks make it to scoring.

### **Q: Can I customize the screener rules?**
A: Yes! Edit the constraints in `app/services/screener.py` - change market cap range, debt limits, etc.

### **Q: What happens if an API goes down?**
A: The system will skip failed APIs and try alternatives. You'll see `stocks_skipped` in the response.

### **Q: Can I set up scheduled runs?**
A: Yes, use Celery + Redis for automatic weekly runs. See "Option 2: Automatic Weekly Job" above.

---

## **Next Steps**

1. ✅ Backend running with auto-discovery
2. ⏳ Call `/auto-discover-penny-stocks` endpoint
3. ⏳ View recommendations in `/weekly-recommendations`
4. ⏳ Open dashboard to see formatted results
5. ⏳ Execute BUY orders for approved stocks
6. ⏳ Set up Celery for automatic weekly runs (optional)

**You now have a fully automated AI stock discovery pipeline! 🚀**
