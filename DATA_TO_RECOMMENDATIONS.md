# 📊 PennyStock: Data to AI Recommendations Pipeline

## Complete Architecture: Live Data → AI-Powered Buy Decisions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LIVE DATA EXTRACTION LAYER                              │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
     │  Yahoo Finance   │    │   Finnhub API    │    │  Custom Sources  │
     │   (Free, No      │    │  (Free tier with │    │  (CSV/DB/etc)    │
     │   API key)       │    │   API key)       │    │                  │
     └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
              │                       │                       │
              │ GET /NSE/SYMBOL       │ GET /quote?symbol=X  │
              │                       │                       │
              └───────────────────────┼───────────────────────┘
                                      │
                                      ▼
              ┌───────────────────────────────────────────┐
              │  data_ingestion.py                        │
              │  ├─ fetch_stock_from_yfinance()          │
              │  ├─ fetch_stock_from_finnhub()           │
              │  └─ sync_stocks_from_universe()          │
              └───────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴──────────────────┐
                    │                                    │
                    ▼                                    ▼
        ┌──────────────────────┐      ┌──────────────────────┐
        │  StockModel (DB)     │      │  StockMetricsModel   │
        │                      │      │      (DB)            │
        │ • Symbol             │      │                      │
        │ • Company Name       │      │ • Revenue Growth     │
        │ • Market Cap         │      │ • Profit Growth      │
        │ • Debt/Equity Ratio  │      │ • Momentum Indicators│
        │ • Promoter Holding % │      │ • RSI, DMA           │
        │ • Sales Growth       │      │ • Volume Spike       │
        │ • Risk Flags         │      │ • Liquidity Quality  │
        └──────────────────────┘      └──────────────────────┘
                    │                                    │
                    └─────────────────┬──────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│               INTELLIGENT FILTERING & SCREENING LAYER                       │
└─────────────────────────────────────────────────────────────────────────────┘

        ┌──────────────────────────────────────────────────┐
        │  screener.py: passes_universe_constraints()      │
        │  ─────────────────────────────────────────────   │
        │  Hard filters (must pass ALL):                   │
        │  ✓ Market cap: ₹100Cr - ₹5000Cr                  │
        │  ✓ Debt/Equity < 0.3 (low debt)                  │
        │  ✓ Operating cash flow is positive               │
        │  ✓ Sales growth > 0%                             │
        │  ✓ Promoter holding > 45%                        │
        │  ✓ Promoter pledge ≤ 5%                          │
        │  ✓ NOT a bank/NBFC                               │
        │  ✓ NOT an ASM/GSM share                          │
        │  ✓ NO suspicious filings                         │
        │                                                   │
        │  → Returns: Screened stocks pool                 │
        └──────────────────────────────────────────────────┘
                            │
         Only HIGH-QUALITY candidates proceed
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              MULTI-FACTOR SCORING ENGINE (Rule-Based AI)                    │
└─────────────────────────────────────────────────────────────────────────────┘

Each screened stock gets 4 INDEPENDENT SCORES (0-100):

┌──────────────────────────────────────────────────┐
│  1. HIDDEN GROWTH SCORE (40% weight)             │
│  ────────────────────────────────────────────    │
│  Detects emerging revenue/profit acceleration    │
│                                                   │
│  Components:                                     │
│  • Revenue Growth: 25% weight                    │
│  • Profit Growth: 20% weight                     │
│  • Margin Improvement: 15% weight                │
│  • Cash Flow Quality: 15% weight                 │
│  • Promoter Confidence: 10% weight               │
│  • Sector Tailwind: 15% weight                   │
│  • Quarterly Acceleration: 10% weight            │
│                                                   │
│  Formula: 0-100 score based on weighted sum      │
│  Example: Strong revenue growth = higher score   │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  2. MOMENTUM SCORE (30% weight)                  │
│  ────────────────────────────────────────────    │
│  Confirms clean breakout + suppresses pump-fakes │
│                                                   │
│  Components:                                     │
│  • Price above 50-day MA: +18 points             │
│  • Price above 200-day MA: +18 points            │
│  • Volume spike quality: +18 points              │
│  • Consolidation breakout: +18 points            │
│  • High 52-week proximity: +12 points            │
│  • RSI momentum: +10 points                      │
│  • Delivery % increase: +12 points               │
│                                                   │
│  PENALTIES:                                      │
│  • Volume spike > 5x: -20 points (pump alert)    │
│  • RSI > 82: -20 points (overbought alert)       │
│                                                   │
│  Result: 0-100 score (detects real strength)    │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  3. QUALITY SCORE (20% weight)                   │
│  ────────────────────────────────────────────    │
│  Measures financial health & promoter alignment  │
│                                                   │
│  Components:                                     │
│  • Low debt (D/E < 0.3): +30 points              │
│  • Positive OCF: +25 points                      │
│  • Sales growth: +20 points                      │
│  • High promoter holding: +20 points             │
│  • Liquidity quality: +5 points                  │
│                                                   │
│  Result: 0-100 quality rating                    │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  4. RISK SCORE (10% weight, as penalty)          │
│  ────────────────────────────────────────────    │
│  Identifies governance/red flags                 │
│                                                   │
│  RED FLAGS (penalties):                          │
│  • Auditor resignation: +20 points               │
│  • Promoter pledge increase: +15 points          │
│  • Related party transactions spike: +12 points  │
│  • Equity dilution: +10 points                   │
│  • Circuit breakers hit: +15 points              │
│  • Suspicious volume spike: +12 points           │
│  • OCF vs profit divergence: +16 points          │
│  • High promoter pledge: variable                │
│  • Suspicious filings: variable                  │
│                                                   │
│  Result: 0-100 RISK (higher = more risky)        │
└──────────────────────────────────────────────────┘

                            │
                            │ All 4 scores calculated
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │  CONVICTION SCORE (Final Decision)    │
        │  ───────────────────────────────────  │
        │                                       │
        │  Formula:                             │
        │  ┌─────────────────────────────────┐  │
        │  │ Conviction = (Hidden Growth×40% │  │
        │  │            + Momentum×30%       │  │
        │  │            + Quality×20%        │  │
        │  │            - Risk×10%)          │  │
        │  │                                 │  │
        │  │ Range: 0-100 points             │  │
        │  └─────────────────────────────────┘  │
        │                                       │
        │  Higher score = MORE CONFIDENT BUY   │
        └───────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              AI RECOMMENDATION ENGINE (Decision Rules)                       │
└─────────────────────────────────────────────────────────────────────────────┘

action_for_score() Decision Tree:

     ┌─ Is Risk Score ≥ 55?
     │  YES → AVOID ❌ (Too risky, regardless of other scores)
     │  NO ↓
     │
     ├─ Is Conviction Score ≥ 72?
     │  YES → BUY 🟢 (Strong buy signal!)
     │  NO ↓
     │
     ├─ Is Conviction Score ≥ 60?
     │  YES → HOLD ⚪ (Good, but wait for better setup)
     │  NO ↓
     │
     ├─ Is Conviction Score ≥ 45?
     │  YES → WATCH 👁️ (On radar, monitor closely)
     │  NO ↓
     │
     └─ DEFAULT → AVOID ❌


DECISION THRESHOLDS:
┌─────────────────────────────────────────────────────┐
│ Conviction Score    │ Action       │ Market Signal  │
├─────────────────────────────────────────────────────┤
│ 72-100              │ BUY 🟢       │ HIGH CONVICTION│
│ 60-71               │ HOLD ⚪      │ GOOD QUALITY   │
│ 45-59               │ WATCH 👁️    │ EMERGING       │
│ Below 45            │ AVOID ❌     │ SKIP           │
│ Risk ≥ 55           │ AVOID ❌     │ TOO RISKY      │
└─────────────────────────────────────────────────────┘

                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              WEEKLY RECOMMENDATION ENGINE                                    │
└─────────────────────────────────────────────────────────────────────────────┘

        ┌────────────────────────────────────────────────────────┐
        │  generate_weekly_recommendations()                      │
        │  ──────────────────────────────────────────────────    │
        │  Additional AI Logic:                                  │
        │                                                        │
        │  1. BUDGET CONSTRAINTS:                                │
        │     • Monthly cap: ₹4000 total                          │
        │     • Weekly cap: ₹1000 max per week                    │
        │     • If monthly cap reached → Watch-list ONLY mode    │
        │                                                        │
        │  2. POSITION LIMITS:                                   │
        │     • Max 1-2 fresh buys per week                       │
        │     • Prefer existing high-conviction holdings          │
        │     • Avoid portfolio churn                             │
        │                                                        │
        │  3. RANKING:                                           │
        │     • Sort by conviction score (descending)             │
        │     • Prioritize existing positions                     │
        │     • Select top 1-2 BUY signals                        │
        │                                                        │
        │  4. OUTPUT: Recommendation object with:                │
        │     • Symbol & Company name                             │
        │     • Action (BUY/HOLD/WATCH/AVOID)                     │
        │     • Allocation amount (₹)                             │
        │     • Detailed reasons (why you should buy)             │
        │     • All scores transparently shown                    │
        │     • Risk flags explicitly listed                      │
        └────────────────────────────────────────────────────────┘

                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              AI INSIGHTS LAYER (Future Enhancement)                          │
└─────────────────────────────────────────────────────────────────────────────┘

        ┌────────────────────────────────────────────────┐
        │  build_company_note_prompt()                   │
        │  ──────────────────────────────────────────    │
        │  Generates AI prompt for deeper analysis:      │
        │                                                │
        │  "Write a concise, institutional, analytical   │
        │   note for KILITCH DRUGS (KILITCH).            │
        │                                                │
        │   Include:                                     │
        │   • Business model overview                    │
        │   • Bull case                                  │
        │   • Bear case                                  │
        │   • Key risks to monitor                       │
        │   • What would invalidate the thesis           │
        │                                                │
        │   Avoid hype, guaranteed returns, or trading   │
        │   recommendations.                             │
        │                                                │
        │   Scores: Hidden Growth: 72, Momentum: 76,     │
        │           Quality: 70, Risk: 13,               │
        │           Conviction: 72                       │
        │                                                │
        │   Risk flags: Promoter pledge increased 2%     │
        │              Volume spike last week             │
        │  ────────────────────────────────────────────  │
        │                                                │
        │  This prompt is sent to:                       │
        │  • OpenAI (GPT-4) for in-depth analysis        │
        │  • Anthropic Claude for research notes         │
        │  • Any LLM for more detailed investment thesis │
        │                                                │
        │  Result: Detailed company research note        │
        │  generated by AI based on our data signals     │
        └────────────────────────────────────────────────┘

                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    END USER DASHBOARD                                       │
└─────────────────────────────────────────────────────────────────────────────┘

    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃    PENNYSTOCK DASHBOARD (localhost:3000)         ┃
    ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
    ┃                                                    ┃
    ┃  📊 Weekly Recommendations                        ┃
    ┃  ─────────────────────────────────────────────   ┃
    ┃                                                    ┃
    ┃  🟢 BUY: KILITCH (₹500)                          ┃
    ┃  ├─ Conviction: 72/100                            ┃
    ┃  ├─ Hidden Growth: 72 | Momentum: 76              ┃
    ┃  ├─ Quality: 70 | Risk: 13                        ┃
    ┃  └─ Reason: Strong fundamental acceleration      ┃
    ┃             with constructive momentum            ┃
    ┃                                                    ┃
    ┃  ⚪ HOLD: PIXTRANS                               ┃
    ┃  ├─ Conviction: 65/100                            ┃
    ┃  ├─ Good quality but wait for better setup        ┃
    ┃                                                    ┃
    ┃  👁️  WATCH: RISKY CIRCUITS                       ┃
    ┃  ├─ Conviction: 52/100                            ┃
    ┃  ├─ Emerging setup, monitor closely               ┃
    ┃                                                    ┃
    ┃  ❌ AVOID: [Some competitor stock]               ┃
    ┃  ├─ Risk Score: 65 (too high)                     ┃
    ┃  ├─ Auditor resigned recently                     ┃
    ┃                                                    ┃
    ┃  💰 Budget Status                                 ┃
    ┃  ├─ Monthly Used: ₹1500 / ₹4000                  ┃
    ┃  └─ Weekly Remaining: ₹500                        ┃
    ┃                                                    ┃
    ┃  📝 View detailed AI-generated research notes →  ┃
    ┃                                                    ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 🧠 AI Usage - Three Layers

### **Layer 1: Rule-Based Scoring (Intelligent Rules)**
✅ **Currently Active** - Uses math formulas to evaluate stocks

```python
# Example: How KILITCH gets a 72 conviction score

Hidden Growth = (18% revenue growth × 0.25) 
              + (15% profit growth × 0.20) 
              + ... = 72/100

Momentum = (Price above 200-day MA: +18)
         + (RSI 65: +10)
         + (Delivery increase: +12) 
         + ... = 76/100

Quality = (Low debt: +30)
        + (Positive OCF: +25)
        + (18% sales growth: +18)
        + ... = 70/100

Risk = 0 (No red flags detected) = 13/100 ⬅️ Low risk!

CONVICTION = (72×0.40) + (76×0.30) + (70×0.20) - (13×0.10)
           = 28.8 + 22.8 + 14.0 - 1.3
           = **72.3 → BUY!** 🟢
```

### **Layer 2: AI-Generated Research Notes (LLM Integration)**
⏳ **Planned** - Will use OpenAI/Claude to write research

```python
# After the algorithm identifies KILITCH as a BUY at 72 conviction,
# the AI generates a detailed note:

Prompt to Claude:
"Write an institutional research note for KILITCH (Kilitch Drugs).
Include business model, bull case, bear case, key risks.
Scores: Hidden Growth 72, Momentum 76, Quality 70, Risk 13.
Risk flags: None identified."

Claude Response:
"Kilitch Drugs: Hidden Growth Opportunity
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUSINESS MODEL:
Kilitch is a specialty pharma company focused on dermatology 
and respiratory therapeutics...

BULL CASE:
- 18% revenue growth with improving margins suggests pricing power
- 69% promoter holding shows strong alignment
- No governance red flags identified

BEAR CASE:
- Competitive pressure in the dermatology space
- Reliance on a few key SKUs

RISKS:
- Regulatory approvals for new drugs
- Patent cliff risks in 3-4 years

VERDICT: Entry point attractive for disciplined portfolios"
```

### **Layer 3: Portfolio Optimization (Future AI)**
⏳ **Planned** - ML models for allocation sizing

---

## 🔄 Complete Data Flow Diagram

```mermaid
Data Source → Screener → Scorer → Decision Engine → Portfolio → Dashboard
   ↓            ↓         ↓         ↓                 ↓           ↓
Yahoo       Hard Pass   4-Factor  Conviction  Budget &   User
Finance    Universe    Scoring    Decision    Allocation Review
Finnhub    Filters     (0-100)    Tree        Rules
```

---

## 📈 Real Example: Why KILITCH Gets BUY ✅

| Metric | Value | Analysis |
|--------|-------|----------|
| **Market Cap** | ₹830 Cr | ✅ In sweet spot (₹100-5000 Cr) |
| **Debt/Equity** | 0.05 | ✅ Very low (< 0.3 required) |
| **Revenue Growth** | 18% | ✅ Strong acceleration |
| **Profit Growth** | 15% | ✅ Profits growing |
| **Promoter Holding** | 69% | ✅ Highly aligned (> 45% required) |
| **Promoter Pledge** | 0% | ✅ No risk (≤ 5% required) |
| **OCF** | Positive | ✅ Real cash generation |
| **Auditor Issues** | None | ✅ No red flags |
| **Volume Spike** | Normal | ✅ Organic, not pump |

**Scores Generated:**
- Hidden Growth: 72 (emerging fundamentals ✅)
- Momentum: 76 (clean momentum ✅)
- Quality: 70 (strong balance sheet ✅)
- Risk: 13 (very safe ✅)
- **Conviction: 72 → BUY!** 🟢

---

## ❌ Real Example: Why RISKY Gets AVOID

| Metric | Value | Analysis |
|--------|-------|----------|
| **Suspicious Filings** | 2 | ❌ Red flag! |
| **Risk Score** | 42 | ⚠️ Elevated |
| **Volume Spike** | 7x average | ❌ Pump alert! |
| **Repeated Circuits** | Yes | ❌ Stock locked limit up/down |
| **Conviction** | 52 | ⚠️ Below 60 threshold |

**Decision:** `WATCH` 👁️ (Wait for red flags to clear)

---

## 🎯 Key Takeaways

| Aspect | How It Works |
|--------|-------------|
| **Data Collection** | Multiple APIs (Yahoo Finance, Finnhub) + custom sources |
| **Stock Screening** | Hard filters for quality universe (market cap, debt, growth, etc.) |
| **Scoring** | 4 independent AI scoring models (Hidden Growth, Momentum, Quality, Risk) |
| **Buy Decision** | Conviction score ≥ 72 = BUY; Scores transparent & explainable |
| **AI Insights** | LLM prompts generate research notes (optional enhancement) |
| **Budget Control** | ₹4000/month cap, ₹1000/week cap, position limits |
| **Portfolio** | Balanced risk management, no portfolio churn |

**Bottom Line:** It's not black-box AI trading. It's **transparent, rule-based intelligent analysis** with optional AI research notes for deeper understanding. YOU stay in control! 📊
