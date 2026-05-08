"""Database models and setup for live data."""

from __future__ import annotations

from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/pennystock"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class StockModel(Base):
    """Live stock data from market feed."""
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    company_name = Column(String)
    sector = Column(String)
    market_cap_crore = Column(Float)
    debt_equity = Column(Float)
    operating_cash_flow_positive = Column(Boolean)
    sales_growth_percent = Column(Float)
    promoter_holding_percent = Column(Float)
    promoter_pledge_percent = Column(Float)
    is_bank_or_nbfc = Column(Boolean, default=False)
    is_asm_gsm = Column(Boolean, default=False)
    suspicious_filings_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC))


class StockMetricsModel(Base):
    """Technical and fundamental metrics for stocks."""
    __tablename__ = "stock_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    revenue_growth = Column(Float)
    profit_growth = Column(Float)
    margin_improvement = Column(Float)
    cash_flow_quality = Column(Float)
    promoter_confidence = Column(Float)
    sector_tailwind = Column(Float)
    quarterly_acceleration = Column(Float)
    price_above_50_dma = Column(Boolean)
    price_above_200_dma = Column(Boolean)
    volume_spike = Column(Float)
    consolidation_breakout = Column(Boolean)
    high_52w_proximity = Column(Float)
    rsi = Column(Float)
    delivery_increase = Column(Float)
    auditor_resignation = Column(Boolean, default=False)
    promoter_pledge_increase = Column(Boolean, default=False)
    related_party_spike = Column(Boolean, default=False)
    equity_dilution = Column(Boolean, default=False)
    repeated_circuits = Column(Boolean, default=False)
    suspicious_volume_spike = Column(Boolean, default=False)
    ocf_divergence = Column(Boolean, default=False)
    liquidity_quality = Column(Float, default=75)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC))


# Create all tables
def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
