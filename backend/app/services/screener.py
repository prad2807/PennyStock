"""Indian small-cap and micro-cap universe filters."""

from __future__ import annotations

from app.domain import Stock


def passes_universe_constraints(stock: Stock) -> bool:
    """Apply the MVP universe constraints before scoring a stock."""

    return all(
        [
            100 <= stock.market_cap_crore <= 5000,
            stock.debt_equity < 0.3,
            stock.operating_cash_flow_positive,
            stock.sales_growth_percent > 0,
            stock.promoter_holding_percent > 45,
            stock.promoter_pledge_percent <= 5,
            not stock.is_bank_or_nbfc,
            not stock.is_asm_gsm,
            stock.suspicious_filings_count == 0,
        ]
    )


def screen_stocks(stocks: list[Stock]) -> list[Stock]:
    """Return stocks that pass all hard universe constraints."""

    return [stock for stock in stocks if passes_universe_constraints(stock)]
