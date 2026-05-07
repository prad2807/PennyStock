"""Core domain models for the PennyStock research workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import StrEnum


class RecommendationAction(StrEnum):
    """Allowed recommendation actions."""

    BUY = "Buy"
    HOLD = "Hold"
    WATCH = "Watch"
    AVOID = "Avoid"


class RecommendationMode(StrEnum):
    """Budget-aware recommendation mode."""

    ACTIVE = "active"
    WATCHLIST_ONLY = "watchlist_only"


@dataclass(frozen=True)
class Stock:
    """A screened Indian NSE/BSE stock candidate."""

    symbol: str
    company_name: str
    sector: str
    market_cap_crore: float
    debt_equity: float
    operating_cash_flow_positive: bool
    sales_growth_percent: float
    promoter_holding_percent: float
    promoter_pledge_percent: float
    is_bank_or_nbfc: bool = False
    is_asm_gsm: bool = False
    suspicious_filings_count: int = 0


@dataclass(frozen=True)
class StockMetrics:
    """Fundamental, technical, and risk inputs used by the scoring engine."""

    revenue_growth: float
    profit_growth: float
    margin_improvement: float
    cash_flow_quality: float
    promoter_confidence: float
    sector_tailwind: float
    quarterly_acceleration: float
    price_above_50_dma: bool
    price_above_200_dma: bool
    volume_spike: float
    consolidation_breakout: bool
    high_52w_proximity: float
    rsi: float
    delivery_increase: float
    auditor_resignation: bool = False
    promoter_pledge_increase: bool = False
    related_party_spike: bool = False
    equity_dilution: bool = False
    repeated_circuits: bool = False
    suspicious_volume_spike: bool = False
    ocf_divergence: bool = False
    liquidity_quality: float = 75


@dataclass(frozen=True)
class StockScore:
    """Calculated stock score suite on a 0-100 scale."""

    symbol: str
    hidden_growth_score: float
    momentum_score: float
    quality_score: float
    risk_score: float
    conviction_score: float
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class PortfolioEntry:
    """Recorded experimental investment with thesis metadata."""

    symbol: str
    buy_price: float
    amount: int
    thesis: str
    catalyst: str
    why_selected: str
    expected_timeline: str
    risk_factors: str
    emotional_note: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class HabitSaving:
    """Skipped unhealthy spending converted into the investment pool."""

    amount: int
    reason: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class Recommendation:
    """Weekly stock recommendation response item."""

    symbol: str
    company_name: str
    action: RecommendationAction
    allocation_amount: int
    reason: list[str]
    week_start: date
    conviction_score: float
