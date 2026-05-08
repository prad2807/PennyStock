"""FastAPI application exposing MVP contracts."""

from __future__ import annotations

from datetime import date

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.config import DEFAULT_WEEKLY_ALLOCATION_INR
from app.domain import HabitSaving, PortfolioEntry, Stock, StockMetrics
from app.services.ai_insights import build_company_note_prompt
from app.services.budget import BudgetState, clamp_monthly_limit
from app.services.recommendations import generate_weekly_recommendations
from app.services.scoring import score_stock
from app.services.screener import screen_stocks
from app.database import init_db
from app.services.data_ingestion import get_stocks_from_db, sync_stocks_from_universe
from app.services.penny_stock_discovery import auto_detect_and_sync_penny_stocks

app = FastAPI(title="PennyStock Hidden Growth Platform")

# Initialize database on startup
@app.on_event("startup")
def startup():
    """Initialize database tables."""
    init_db()
    print("✓ Database initialized")

HABIT_SAVINGS: list[HabitSaving] = []
PORTFOLIO: list[PortfolioEntry] = []


@app.get("/")
def root() -> dict[str, object]:
    """Welcome to the PennyStock API."""
    return {
        "message": "Welcome to PennyStock Hidden Growth Platform",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "0.1.0",
        "endpoints": {
            "recommendations": "/weekly-recommendations",
            "top_ranked": "/top-ranked",
            "portfolio": "/portfolio",
            "add_habit_saving": "POST /habit-saving",
            "add_buy_entry": "POST /buy-entry"
        }
    }


class HabitSavingRequest(BaseModel):
    amount: int = Field(gt=0, le=DEFAULT_WEEKLY_ALLOCATION_INR)
    reason: str = Field(min_length=2, max_length=160)


class BuyEntryRequest(BaseModel):
    symbol: str
    buy_price: float = Field(gt=0)
    amount: int = Field(gt=0, le=DEFAULT_WEEKLY_ALLOCATION_INR)
    thesis: str
    catalyst: str
    why_selected: str
    expected_timeline: str
    risk_factors: str
    emotional_note: str


def demo_universe() -> tuple[list[Stock], dict[str, object]]:
    """Return deterministic seed data until live market-data ingestion is connected."""

    stocks = [
        Stock("KILITCH", "Kilitch Drugs", "Healthcare", 830, 0.05, True, 18, 69, 0),
        Stock("PIXTRANS", "Pix Transmissions", "Industrials", 1850, 0.08, True, 21, 61, 0),
        Stock("RISKY", "Risky Circuits Ltd", "Industrials", 420, 0.02, True, 30, 58, 0, suspicious_filings_count=2),
    ]
    metrics = {
        "KILITCH": StockMetrics(72, 66, 58, 76, 70, 62, 55, True, True, 1.7, True, 9, 63, 13, liquidity_quality=78),
        "PIXTRANS": StockMetrics(65, 70, 61, 72, 68, 66, 60, True, True, 1.4, True, 10, 59, 16, liquidity_quality=82),
        "RISKY": StockMetrics(80, 75, 70, 30, 40, 60, 62, True, True, 7, True, 12, 86, 4, suspicious_volume_spike=True, repeated_circuits=True, liquidity_quality=35),
    }
    return stocks, metrics


def get_universe() -> tuple[list[Stock], dict[str, object]]:
    """Get stocks and metrics from database, fallback to demo data if database is empty."""
    try:
        stocks, metrics = get_stocks_from_db()
        if stocks:  # If database has data, use it
            return stocks, metrics
    except Exception as e:
        print(f"Note: Using demo data (database: {e})")
    
    # Fallback to demo data
    return demo_universe()


@app.get("/weekly-recommendations")
def weekly_recommendations(monthly_invested: int = 0) -> dict[str, object]:
    stocks, metrics = get_universe()
    screened = screen_stocks(stocks)
    scores = {stock.symbol: score_stock(stock, metrics[stock.symbol]) for stock in screened}
    return generate_weekly_recommendations(screened, scores, BudgetState(monthly_invested), date.today())


@app.get("/top-ranked")
def top_ranked() -> list[dict[str, object]]:
    stocks, metrics = get_universe()
    screened = screen_stocks(stocks)
    scored = sorted((score_stock(stock, metrics[stock.symbol]) for stock in screened), key=lambda item: item.conviction_score, reverse=True)
    return [score.__dict__ for score in scored]


@app.get("/portfolio")
def portfolio() -> dict[str, object]:
    invested = sum(entry.amount for entry in PORTFOLIO)
    return {"invested_amount": invested, "active_positions": len({entry.symbol for entry in PORTFOLIO}), "entries": PORTFOLIO}


@app.post("/habit-saving")
def add_habit_saving(payload: HabitSavingRequest) -> dict[str, object]:
    saving = HabitSaving(amount=payload.amount, reason=payload.reason)
    HABIT_SAVINGS.append(saving)
    return {"investment_pool": sum(item.amount for item in HABIT_SAVINGS), "saving": saving}


@app.post("/buy-entry")
def add_buy_entry(payload: BuyEntryRequest) -> dict[str, object]:
    monthly_invested = sum(
        entry.amount
        for entry in PORTFOLIO
        if entry.created_at.date().replace(day=1) == date.today().replace(day=1)
    )
    limit = clamp_monthly_limit(None)
    budget = BudgetState(monthly_invested, limit)
    allowed = min(budget.remaining_budget, budget.weekly_recommendation_limit)
    amount = min(payload.amount, allowed)
    entry = PortfolioEntry(**payload.model_dump(), amount=amount)
    if amount > 0:
        PORTFOLIO.append(entry)
    return {
        "accepted_amount": amount,
        "remaining_monthly_budget": BudgetState(monthly_invested + amount, limit).remaining_budget,
        "weekly_recommendation_limit": budget.weekly_recommendation_limit,
        "entry": entry if amount > 0 else None,
    }


@app.get("/stock/{symbol}")
def stock_detail(symbol: str) -> dict[str, object]:
    stocks, metrics = get_universe()
    stock = next(item for item in stocks if item.symbol == symbol.upper())
    score = score_stock(stock, metrics[stock.symbol])
    return {"stock": stock, "scores": score, "ai_prompt": build_company_note_prompt(stock, score, [])}


@app.post("/sync-data")
def sync_live_data(symbols: list[str] = None) -> dict[str, object]:
    """Sync stock data from live market feeds.
    
    Default NSE universe if symbols not provided.
    """
    if not symbols:
        # Default NSE small-cap/micro-cap symbols
        symbols = ["KILITCH", "PIXTRANS", "RISKY"]
    
    try:
        sync_stocks_from_universe(symbols)
        return {
            "status": "success",
            "message": f"Syncing {len(symbols)} stocks from live market data",
            "symbols": symbols,
            "next_step": "Check /weekly-recommendations for updated data"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Sync failed: {str(e)}",
            "note": "Make sure PostgreSQL is running at localhost:5432"
        }


@app.post("/auto-discover-penny-stocks")
def auto_discover() -> dict[str, object]:
    """🤖 AI AUTO-DISCOVERY: Find penny stocks automatically from NSE/BSE.
    
    This endpoint:
    1. Scans NSE/BSE for all small-cap & micro-cap stocks
    2. Downloads their data automatically
    3. Stores in database
    4. Will be automatically filtered + scored on next call to /weekly-recommendations
    
    No manual stock list needed! AI finds them for you.
    """
    
    try:
        result = auto_detect_and_sync_penny_stocks()
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "✅ Auto-discovery complete!",
                "stocks_synced": result["synced"],
                "stocks_skipped": result["skipped"],
                "total_processed": result["synced"] + result["skipped"],
                "next_step": "Call /weekly-recommendations to see AI-filtered results",
                "details": f"✅ {result['synced']} stocks added to database"
            }
        else:
            return result
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Auto-discovery failed: {str(e)}",
            "root_cause": "Might need Finnhub API key or NSE data access setup"
        }
