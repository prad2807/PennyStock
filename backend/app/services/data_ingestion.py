"""Live market data ingestion from public APIs."""

from __future__ import annotations

import os
from typing import Optional
import requests
from datetime import datetime, timedelta
from app.domain import Stock, StockMetrics
from app.database import SessionLocal, StockModel, StockMetricsModel


# Popular free Indian stock market data APIs
NSEDATA_API = "https://api.nse2.com"  # NSE API (requires API key)
YFINANCE_API = "https://query1.finance.yahoo.com"  # Yahoo Finance (free)
FINNHUB_API = "https://finnhub.io/api/v1"  # Finnhub (requires API key)


def fetch_stock_from_yfinance(symbol: str) -> Optional[dict]:
    """Fetch stock data from Yahoo Finance API (free, no API key needed)."""
    try:
        # Yahoo Finance ticker for Indian stocks: SYMBOL.NS (NSE) or SYMBOL.BO (BSE)
        ticker = f"{symbol}.NS"
        url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
        
        params = {
            "modules": "price,summaryDetail,financialData"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "quoteSummary" in data and "result" in data["quoteSummary"]:
                return data["quoteSummary"]["result"][0]
        
        return None
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


def fetch_stock_from_finnhub(symbol: str, api_key: str) -> Optional[dict]:
    """Fetch stock data from Finnhub API (requires free API key)."""
    try:
        url = f"https://finnhub.io/api/v1/quote"
        params = {
            "symbol": f"{symbol}",
            "token": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        
        return None
    except Exception as e:
        print(f"Error fetching {symbol} from Finnhub: {e}")
        return None


def sync_stocks_from_universe(symbols: list[str]) -> None:
    """Sync a list of stock symbols from live market data."""
    db = SessionLocal()
    
    try:
        # Try to use Finnhub if API key available, fallback to Yahoo Finance
        api_key = os.getenv("FINNHUB_API_KEY")
        
        for symbol in symbols:
            print(f"Syncing {symbol}...")
            
            if api_key:
                data = fetch_stock_from_finnhub(symbol, api_key)
            else:
                data = fetch_stock_from_yfinance(symbol)
            
            if data:
                # Update or create stock record
                existing = db.query(StockModel).filter(StockModel.symbol == symbol).first()
                
                if existing:
                    existing.updated_at = datetime.utcnow()
                    db.commit()
                else:
                    # Create new record with placeholder values
                    # You'll need to enrich this with actual fundamentals data
                    stock = StockModel(
                        symbol=symbol,
                        company_name=symbol,  # Get real company name from API
                        sector="Unknown",
                        market_cap_crore=0,
                        debt_equity=0,
                        operating_cash_flow_positive=True,
                        sales_growth_percent=0,
                        promoter_holding_percent=0,
                        promoter_pledge_percent=0,
                    )
                    db.add(stock)
                    db.commit()
                
                print(f"  ✓ {symbol} synced")
            else:
                print(f"  ✗ Failed to fetch {symbol}")
    
    finally:
        db.close()


def get_stocks_from_db() -> tuple[list[Stock], dict[str, StockMetrics]]:
    """Fetch all stocks and metrics from database."""
    db = SessionLocal()
    
    try:
        stocks_db = db.query(StockModel).all()
        metrics_db = db.query(StockMetricsModel).all()
        
        # Convert database models to domain models
        stocks = [
            Stock(
                symbol=s.symbol,
                company_name=s.company_name,
                sector=s.sector,
                market_cap_crore=s.market_cap_crore,
                debt_equity=s.debt_equity,
                operating_cash_flow_positive=s.operating_cash_flow_positive,
                sales_growth_percent=s.sales_growth_percent,
                promoter_holding_percent=s.promoter_holding_percent,
                promoter_pledge_percent=s.promoter_pledge_percent,
                is_bank_or_nbfc=s.is_bank_or_nbfc,
                is_asm_gsm=s.is_asm_gsm,
                suspicious_filings_count=s.suspicious_filings_count,
            )
            for s in stocks_db
        ]
        
        metrics = {
            m.symbol: StockMetrics(
                revenue_growth=m.revenue_growth,
                profit_growth=m.profit_growth,
                margin_improvement=m.margin_improvement,
                cash_flow_quality=m.cash_flow_quality,
                promoter_confidence=m.promoter_confidence,
                sector_tailwind=m.sector_tailwind,
                quarterly_acceleration=m.quarterly_acceleration,
                price_above_50_dma=m.price_above_50_dma,
                price_above_200_dma=m.price_above_200_dma,
                volume_spike=m.volume_spike,
                consolidation_breakout=m.consolidation_breakout,
                high_52w_proximity=m.high_52w_proximity,
                rsi=m.rsi,
                delivery_increase=m.delivery_increase,
                auditor_resignation=m.auditor_resignation,
                promoter_pledge_increase=m.promoter_pledge_increase,
                related_party_spike=m.related_party_spike,
                equity_dilution=m.equity_dilution,
                repeated_circuits=m.repeated_circuits,
                suspicious_volume_spike=m.suspicious_volume_spike,
                ocf_divergence=m.ocf_divergence,
                liquidity_quality=m.liquidity_quality,
            )
            for m in metrics_db
        }
        
        return stocks, metrics
    
    finally:
        db.close()
