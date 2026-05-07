# PennyStock Hidden Growth Platform

A disciplined, AI-assisted research platform for Indian small-cap and micro-cap investing experiments. The app is intentionally **not** a trading app: it combines hidden-growth fundamentals, momentum confirmation, governance/liquidity risk checks, journaling, and a strict behavioral budget framework.

## Core rule

The monthly experimental allocation is hard-capped at **₹4000**. Weekly recommendations are separately capped at **₹1000 total per week**, split across one or two ideas when two fresh buys are valid. When the user reaches the monthly cap, buy recommendations are disabled and the platform moves to watchlist-only mode with the message:

> Monthly experimental allocation limit reached

## Architecture

- **Frontend:** Next.js, TypeScript, Tailwind, Recharts-ready structure
- **Backend:** FastAPI, SQLAlchemy-style domain boundaries, Pydantic schemas
- **Jobs:** Celery/Redis-ready weekly task module
- **AI:** Provider abstraction for OpenAI/Claude generated company notes
- **Database target:** PostgreSQL

## MVP modules

1. Screener and stock universe filters
2. Scoring engine for hidden growth, momentum, quality, and risk
3. Weekly recommendation engine with 1–2 stock maximum and ₹1000 total weekly allocation cap
4. Budget enforcement and habit savings
5. Portfolio and journal tracking contracts
6. AI insight layer interface
7. Watchlist-only behavior when no valid setup exists or the monthly cap is reached

## Development

```bash
python -m pytest backend/tests
```

Frontend scaffolding lives in `frontend/` and is ready for dependency installation in a Next.js environment.
