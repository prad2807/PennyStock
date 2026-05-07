from datetime import date

from app.config import DEFAULT_WEEKLY_ALLOCATION_INR, MONTHLY_INVESTMENT_LIMIT_INR
from app.domain import Stock, StockScore
from app.services.budget import BudgetState, CAP_REACHED_MESSAGE, clamp_monthly_limit, weekly_allocation
from app.services.recommendations import NO_OPPORTUNITY_MESSAGE, generate_weekly_recommendations


def stock(symbol="ALPHA"):
    return Stock(symbol, f"{symbol} Ltd", "Industrials", 500, 0.05, True, 20, 60, 0)


def score(symbol="ALPHA", conviction=80, risk=10):
    return StockScore(symbol, 80, 75, 80, risk, conviction)


def test_configured_caps_are_4000_monthly_and_1000_weekly():
    assert MONTHLY_INVESTMENT_LIMIT_INR == 4000
    assert DEFAULT_WEEKLY_ALLOCATION_INR == 1000


def test_monthly_limit_is_clamped_to_4000():
    assert clamp_monthly_limit(5000) == 4000
    assert clamp_monthly_limit(3700) == 3700


def test_budget_cap_forces_watchlist_only_mode():
    budget = BudgetState(monthly_invested=4000)
    assert budget.remaining_budget == 0
    assert budget.message == CAP_REACHED_MESSAGE

    response = generate_weekly_recommendations([stock()], {"ALPHA": score()}, budget, date(2026, 5, 4))

    assert response["mode"] == "watchlist_only"
    assert response["message"] == CAP_REACHED_MESSAGE
    assert response["recommendations"] == []


def test_weekly_allocation_never_exceeds_weekly_or_remaining_monthly_budget():
    assert weekly_allocation(5000, BudgetState(monthly_invested=0)) == 1000
    assert weekly_allocation(1500, BudgetState(monthly_invested=3100)) == 900
    assert weekly_allocation(500, BudgetState(monthly_invested=3800)) == 200


def test_budget_state_clamps_monthly_limit_to_4000():
    budget = BudgetState(monthly_invested=0, monthly_limit=5000)

    assert budget.monthly_limit == 4000
    assert budget.remaining_budget == 4000
    assert budget.weekly_recommendation_limit == 1000


def test_recommendations_are_limited_to_two_fresh_buys():
    stocks = [stock("AAA"), stock("BBB"), stock("CCC")]
    scores = {item.symbol: score(item.symbol, 82, 8) for item in stocks}

    response = generate_weekly_recommendations(stocks, scores, BudgetState(monthly_invested=0), date(2026, 5, 4))

    assert len(response["recommendations"]) == 2
    assert sum(item.allocation_amount for item in response["recommendations"]) == 1000
    assert all(item.allocation_amount <= 500 for item in response["recommendations"])
    assert response["weekly_recommendation_limit"] == 1000


def test_no_valid_setup_returns_hold_cash_message():
    response = generate_weekly_recommendations([stock()], {"ALPHA": score(conviction=40, risk=10)}, BudgetState(0), date(2026, 5, 4))

    assert response["message"] == NO_OPPORTUNITY_MESSAGE
    assert response["recommendations"] == []
