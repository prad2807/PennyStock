"""AI insight prompt construction for OpenAI or Claude providers."""

from __future__ import annotations

from app.domain import Stock, StockScore

SYSTEM_TONE = "concise, institutional, analytical, anti-hype"


def build_company_note_prompt(stock: Stock, score: StockScore, risk_flags: list[str]) -> str:
    """Build a provider-neutral prompt for company research notes."""

    flags = ", ".join(risk_flags) if risk_flags else "None identified by the rules engine"
    return (
        f"Write a {SYSTEM_TONE} note for {stock.company_name} ({stock.symbol}). "
        "Include business model, bull case, bear case, key risks, and what would invalidate the thesis. "
        "Avoid guaranteed returns, hype, meme-stock language, or trading instructions. "
        f"Scores: hidden growth {score.hidden_growth_score}, momentum {score.momentum_score}, "
        f"quality {score.quality_score}, risk {score.risk_score}, conviction {score.conviction_score}. "
        f"Risk flags: {flags}."
    )
