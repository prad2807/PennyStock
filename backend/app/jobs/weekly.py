"""Weekly automation entrypoint for Sunday-night refreshes."""

from __future__ import annotations

from datetime import date

from app.api.main import demo_universe
from app.services.budget import BudgetState
from app.services.recommendations import generate_weekly_recommendations
from app.services.scoring import score_stock
from app.services.screener import screen_stocks


def refresh_weekly_recommendations(monthly_invested: int = 0) -> dict[str, object]:
    """Fetch data, score the universe, and generate Monday recommendations."""

    stocks, metrics = demo_universe()
    screened = screen_stocks(stocks)
    scores = {stock.symbol: score_stock(stock, metrics[stock.symbol]) for stock in screened}
    return generate_weekly_recommendations(screened, scores, BudgetState(monthly_invested), date.today())
