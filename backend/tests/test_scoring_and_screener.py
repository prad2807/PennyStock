from app.domain import Stock, StockMetrics
from app.services.scoring import final_conviction, score_stock
from app.services.screener import passes_universe_constraints


def test_universe_constraints_exclude_nbfc_and_pledged_names():
    eligible = Stock("GOOD", "Good Ltd", "Industrials", 900, 0.1, True, 15, 55, 0)
    nbfc = Stock("BANK", "Bank Ltd", "Financials", 900, 0.1, True, 15, 55, 0, is_bank_or_nbfc=True)
    pledged = Stock("PLEDGE", "Pledge Ltd", "Industrials", 900, 0.1, True, 15, 55, 8)

    assert passes_universe_constraints(eligible)
    assert not passes_universe_constraints(nbfc)
    assert not passes_universe_constraints(pledged)


def test_final_conviction_uses_risk_as_penalty():
    low_risk = final_conviction(80, 80, 80, 5)
    high_risk = final_conviction(80, 80, 80, 60)

    assert low_risk > high_risk


def test_parabolic_momentum_is_penalized():
    stock = Stock("MOMO", "Momentum Ltd", "Industrials", 900, 0.1, True, 15, 55, 0)
    clean = StockMetrics(70, 70, 60, 70, 65, 60, 60, True, True, 1.5, True, 10, 62, 15, liquidity_quality=80)
    parabolic = StockMetrics(70, 70, 60, 70, 65, 60, 60, True, True, 8, True, 10, 88, 15, liquidity_quality=80)

    assert score_stock(stock, clean).momentum_score > score_stock(stock, parabolic).momentum_score
