"""Scoring engine for hidden growth, momentum, quality, and risk."""

from __future__ import annotations

from app.domain import Stock, StockMetrics, StockScore


def _clamp(value: float, lower: float = 0, upper: float = 100) -> float:
    return round(max(lower, min(value, upper)), 2)


def score_hidden_growth(metrics: StockMetrics) -> float:
    """Score emerging growth using weighted fundamental acceleration inputs."""

    return _clamp(
        metrics.revenue_growth * 0.25
        + metrics.profit_growth * 0.20
        + metrics.margin_improvement * 0.15
        + metrics.cash_flow_quality * 0.15
        + metrics.promoter_confidence * 0.10
        + metrics.sector_tailwind * 0.15
        + metrics.quarterly_acceleration * 0.10
    )


def score_momentum(metrics: StockMetrics) -> float:
    """Score clean breakout and accumulation behavior while limiting pump-like setups."""

    score = 0
    score += 18 if metrics.price_above_50_dma else 0
    score += 18 if metrics.price_above_200_dma else 0
    score += _clamp(metrics.volume_spike * 12, 0, 18)
    score += 18 if metrics.consolidation_breakout else 0
    score += _clamp(metrics.high_52w_proximity, 0, 12)
    score += _clamp((metrics.rsi - 45) * 0.8, 0, 10)
    score += _clamp(metrics.delivery_increase * 0.6, 0, 12)
    if metrics.volume_spike > 5 or metrics.rsi > 82:
        score -= 20
    return _clamp(score)


def score_quality(stock: Stock, metrics: StockMetrics) -> float:
    """Score balance sheet conservatism, cash generation, and promoter alignment."""

    score = 30 if stock.debt_equity < 0.3 else 0
    score += 25 if stock.operating_cash_flow_positive else 0
    score += _clamp(stock.sales_growth_percent, 0, 20)
    score += _clamp((stock.promoter_holding_percent - 45) * 1.2, 0, 20)
    score += _clamp(metrics.liquidity_quality * 0.05, 0, 5)
    return _clamp(score)


def score_risk(stock: Stock, metrics: StockMetrics) -> float:
    """Generate a penalty-style risk score where higher means riskier."""

    risk = 0
    risk += 20 if metrics.auditor_resignation else 0
    risk += 15 if metrics.promoter_pledge_increase else 0
    risk += 12 if metrics.related_party_spike else 0
    risk += 10 if metrics.equity_dilution else 0
    risk += 15 if metrics.repeated_circuits else 0
    risk += 12 if metrics.suspicious_volume_spike else 0
    risk += 16 if metrics.ocf_divergence else 0
    risk += _clamp(stock.promoter_pledge_percent * 2, 0, 20)
    risk += stock.suspicious_filings_count * 8
    risk += _clamp(100 - metrics.liquidity_quality, 0, 30) * 0.4
    return _clamp(risk)


def final_conviction(hidden_growth: float, momentum: float, quality: float, risk: float) -> float:
    """Combine scores using the specified 40/30/20/10 risk-penalty blend."""

    return _clamp(hidden_growth * 0.40 + momentum * 0.30 + quality * 0.20 - risk * 0.10)


def score_stock(stock: Stock, metrics: StockMetrics) -> StockScore:
    """Return all calculated scores for a stock."""

    hidden_growth = score_hidden_growth(metrics)
    momentum = score_momentum(metrics)
    quality = score_quality(stock, metrics)
    risk = score_risk(stock, metrics)
    return StockScore(
        symbol=stock.symbol,
        hidden_growth_score=hidden_growth,
        momentum_score=momentum,
        quality_score=quality,
        risk_score=risk,
        conviction_score=final_conviction(hidden_growth, momentum, quality, risk),
    )
