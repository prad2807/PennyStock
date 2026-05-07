"""Weekly recommendation engine with budget and churn controls."""

from __future__ import annotations

from datetime import date

from app.config import DEFAULT_WEEKLY_ALLOCATION_INR, MAX_WEEKLY_FRESH_BUYS
from app.domain import Recommendation, RecommendationAction, RecommendationMode, Stock, StockScore
from app.services.budget import BudgetState, weekly_allocation

NO_OPPORTUNITY_MESSAGE = "No good opportunities this week. Hold cash."


def action_for_score(score: StockScore) -> RecommendationAction:
    """Map conviction and risk scores to the platform action taxonomy."""

    if score.risk_score >= 55:
        return RecommendationAction.AVOID
    if score.conviction_score >= 72:
        return RecommendationAction.BUY
    if score.conviction_score >= 60:
        return RecommendationAction.HOLD
    if score.conviction_score >= 45:
        return RecommendationAction.WATCH
    return RecommendationAction.AVOID


def build_reasons(stock: Stock, score: StockScore) -> list[str]:
    """Create concise, anti-hype explanation bullets for a recommendation."""

    reasons = [
        f"Conviction score {score.conviction_score}/100 after quality, momentum, and risk checks",
        f"Debt/equity {stock.debt_equity:.2f} with promoter holding {stock.promoter_holding_percent:.1f}%",
    ]
    if score.hidden_growth_score >= 65:
        reasons.append("Hidden-growth metrics show improving fundamental acceleration")
    if score.momentum_score >= 65:
        reasons.append("Momentum layer confirms constructive breakout or accumulation behavior")
    if score.risk_score <= 25:
        reasons.append("Risk engine shows no major governance or liquidity penalty")
    return reasons


def generate_weekly_recommendations(
    stocks: list[Stock],
    scores: dict[str, StockScore],
    budget: BudgetState,
    week_start: date,
    existing_holdings: set[str] | None = None,
) -> dict[str, object]:
    """Recommend at most 1-2 stocks, preferring existing high-conviction holdings."""

    existing_holdings = existing_holdings or set()
    ranked = sorted(
        (stock for stock in stocks if stock.symbol in scores),
        key=lambda stock: (stock.symbol not in existing_holdings, -scores[stock.symbol].conviction_score),
    )

    recommendations: list[Recommendation] = []
    if budget.mode == RecommendationMode.WATCHLIST_ONLY:
        return {
            "mode": budget.mode,
            "message": budget.message,
            "remaining_monthly_budget": budget.remaining_budget,
            "weekly_recommendation_limit": budget.weekly_recommendation_limit,
            "recommendations": [],
            "watchlist": [stock.symbol for stock in ranked[:10]],
        }

    fresh_buys = 0
    weekly_remaining = budget.weekly_recommendation_limit
    buy_candidates = [
        stock for stock in ranked if action_for_score(scores[stock.symbol]) == RecommendationAction.BUY
    ]
    buy_slots = min(len(buy_candidates), MAX_WEEKLY_FRESH_BUYS) or 1
    target_buy_allocation = max(weekly_remaining // buy_slots, 0)

    for stock in ranked:
        score = scores[stock.symbol]
        action = action_for_score(score)
        is_existing = stock.symbol in existing_holdings
        if action == RecommendationAction.BUY and not is_existing:
            if fresh_buys >= MAX_WEEKLY_FRESH_BUYS:
                continue
            fresh_buys += 1
        if action not in {RecommendationAction.BUY, RecommendationAction.HOLD}:
            continue
        allocation = 0
        if action == RecommendationAction.BUY:
            allocation = weekly_allocation(
                target_buy_allocation or DEFAULT_WEEKLY_ALLOCATION_INR, budget, weekly_remaining
            )
            if allocation <= 0:
                continue
            weekly_remaining -= allocation
        recommendations.append(
            Recommendation(
                symbol=stock.symbol,
                company_name=stock.company_name,
                action=action,
                allocation_amount=allocation,
                reason=build_reasons(stock, score),
                week_start=week_start,
                conviction_score=score.conviction_score,
            )
        )
        if len([item for item in recommendations if item.action == RecommendationAction.BUY]) >= MAX_WEEKLY_FRESH_BUYS:
            break

    if not recommendations:
        return {
            "mode": RecommendationMode.WATCHLIST_ONLY,
            "message": NO_OPPORTUNITY_MESSAGE,
            "remaining_monthly_budget": budget.remaining_budget,
            "weekly_recommendation_limit": budget.weekly_recommendation_limit,
            "recommendations": [],
            "watchlist": [stock.symbol for stock in ranked[:10]],
        }

    return {
        "mode": RecommendationMode.ACTIVE,
        "message": None,
        "remaining_monthly_budget": budget.remaining_budget,
        "weekly_recommendation_limit": budget.weekly_recommendation_limit,
        "recommendations": recommendations,
        "watchlist": [stock.symbol for stock in ranked if stock.symbol not in {r.symbol for r in recommendations}][:10],
    }
