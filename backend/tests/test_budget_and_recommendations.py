from datetime import date

from app.domain import Stock, StockScore
from app.services.budget import BudgetState, CAP_REACHED_MESSAGE, clamp_monthly_limit, weekly_allocation
from app.services.recommendations import NO_OPPORTUNITY_MESSAGE, generate_weekly_recommendations


def stock(symbol="ALPHA"):
    return Stock(symbol, f"{symbol} Ltd", "Industrials", 500, 0.05, True, 20, 60, 0)


def score(symbol="ALPHA", conviction=80, risk=10):
    return StockScore(symbol, 80, 75, 80, risk, conviction)


def test_monthly_limit_is_clamped_to_1000():
    assert clamp_monthly_limit(5000) == 1000
    assert clamp_monthly_limit(700) == 700


def test_budget_cap_forces_watchlist_only_mode():
    budget = BudgetState(monthly_invested=1000)
    assert budget.remaining_budget == 0
    assert budget.message == CAP_REACHED_MESSAGE

    response = generate_weekly_recommendations([stock()], {"ALPHA": score()}, budget, date(2026, 5, 4))

    assert response["mode"] == "watchlist_only"
    assert response["message"] == CAP_REACHED_MESSAGE
    assert response["recommendations"] == []


def test_weekly_allocation_never_exceeds_remaining_budget():
    assert weekly_allocation(500, BudgetState(monthly_invested=700)) == 250
    assert weekly_allocation(500, BudgetState(monthly_invested=800)) == 200


def test_recommendations_are_limited_to_two_fresh_buys():
    stocks = [stock("AAA"), stock("BBB"), stock("CCC")]
    scores = {item.symbol: score(item.symbol, 82, 8) for item in stocks}

    response = generate_weekly_recommendations(stocks, scores, BudgetState(monthly_invested=0), date(2026, 5, 4))

    assert len(response["recommendations"]) == 2
    assert all(item.allocation_amount == 250 for item in response["recommendations"])


def test_no_valid_setup_returns_hold_cash_message():
    response = generate_weekly_recommendations([stock()], {"ALPHA": score(conviction=40, risk=10)}, BudgetState(0), date(2026, 5, 4))

    assert response["message"] == NO_OPPORTUNITY_MESSAGE
    assert response["recommendations"] == []
