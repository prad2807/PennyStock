"""Budget enforcement for the behavioral finance guardrail."""

from __future__ import annotations

from dataclasses import dataclass

from app.config import DEFAULT_WEEKLY_ALLOCATION_INR, MONTHLY_INVESTMENT_LIMIT_INR
from app.domain import RecommendationMode

CAP_REACHED_MESSAGE = "Monthly experimental allocation limit reached"


@dataclass(frozen=True)
class BudgetState:
    """Current monthly budget state with hard monthly and weekly guardrails."""

    monthly_invested: int
    monthly_limit: int = MONTHLY_INVESTMENT_LIMIT_INR

    def __post_init__(self) -> None:
        """Clamp every BudgetState instance to the platform's ₹4000 monthly limit."""

        object.__setattr__(self, "monthly_limit", clamp_monthly_limit(self.monthly_limit))
        object.__setattr__(self, "monthly_invested", max(self.monthly_invested, 0))

    @property
    def remaining_budget(self) -> int:
        """Return the non-negative budget still available this month."""

        return max(self.monthly_limit - self.monthly_invested, 0)

    @property
    def weekly_recommendation_limit(self) -> int:
        """Return this week's maximum recommendation, capped at ₹1000 and monthly remainder."""

        return min(DEFAULT_WEEKLY_ALLOCATION_INR, self.remaining_budget)

    @property
    def mode(self) -> RecommendationMode:
        """Return active mode unless the hard cap is already reached."""

        if self.remaining_budget <= 0:
            return RecommendationMode.WATCHLIST_ONLY
        return RecommendationMode.ACTIVE

    @property
    def message(self) -> str | None:
        """Return the cap message only when new buys must be blocked."""

        if self.mode == RecommendationMode.WATCHLIST_ONLY:
            return CAP_REACHED_MESSAGE
        return None


def clamp_monthly_limit(requested_limit: int | None) -> int:
    """Never allow the persisted user limit to exceed ₹4000."""

    if requested_limit is None:
        return MONTHLY_INVESTMENT_LIMIT_INR
    return min(max(requested_limit, 0), MONTHLY_INVESTMENT_LIMIT_INR)


def weekly_allocation(
    calculated_position_size: int, budget: BudgetState, weekly_remaining: int | None = None
) -> int:
    """Cap a recommendation by the remaining weekly and monthly allocation.

    The monthly hard cap remains ₹4000, but a single weekly recommendation cycle
    must never allocate more than the ₹1000 default weekly discipline budget.
    """

    available_this_week = (
        budget.weekly_recommendation_limit
        if weekly_remaining is None
        else min(weekly_remaining, budget.weekly_recommendation_limit)
    )
    desired = min(calculated_position_size, DEFAULT_WEEKLY_ALLOCATION_INR)
    return max(min(desired, available_this_week, budget.remaining_budget), 0)
