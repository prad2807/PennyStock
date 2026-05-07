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

app = FastAPI(title="PennyStock Hidden Growth Platform")

HABIT_SAVINGS: list[HabitSaving] = []
PORTFOLIO: list[PortfolioEntry] = []


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


@app.get("/weekly-recommendations")
def weekly_recommendations(monthly_invested: int = 0) -> dict[str, object]:
    stocks, metrics = demo_universe()
    screened = screen_stocks(stocks)
    scores = {stock.symbol: score_stock(stock, metrics[stock.symbol]) for stock in screened}
    return generate_weekly_recommendations(screened, scores, BudgetState(monthly_invested), date.today())


@app.get("/top-ranked")
def top_ranked() -> list[dict[str, object]]:
    stocks, metrics = demo_universe()
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
    stocks, metrics = demo_universe()
    stock = next(item for item in stocks if item.symbol == symbol.upper())
    score = score_stock(stock, metrics[stock.symbol])
    return {"stock": stock, "scores": score, "ai_prompt": build_company_note_prompt(stock, score, [])}
