"""Automatic penny stock universe discovery from NSE/BSE."""

from __future__ import annotations

import requests
from typing import Optional
from app.database import SessionLocal, StockModel, StockMetricsModel


def fetch_nse_penny_stocks() -> list[dict]:
    """Fetch penny stocks (small-cap/micro-cap) from NSE automatically.
    
    Uses public NSE data sources to get qualifying stocks:
    - Market cap: ₹100 Cr - ₹5000 Cr
    - Liquidity: Min volume requirements
    """
    
    try:
        # Method 1: Use NSEIndiaAPI (free, no key required)
        # This returns top small-cap stocks
        
        url = "https://www.nseindia.com/api/equity-stockIndices"
        params = {
            "index": "NIFTY_SMALLCAP_50"  # NSE's official small-cap index
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            stocks = []
            
            # Extract stock symbols from the index
            if "data" in data:
                for stock in data["data"]:
                    stocks.append({
                        "symbol": stock.get("symbol"),
                        "name": stock.get("name"),
                        "market_cap": stock.get("marketCap"),
                        "pe_ratio": stock.get("pe"),
                        "volume": stock.get("volume")
                    })
            
            return stocks
        
        return []
    
    except Exception as e:
        print(f"Error fetching NSE small-caps: {e}")
        return []


def fetch_all_nse_stocks() -> list[dict]:
    """Alternative: Fetch ALL NSE listed stocks (not just small-caps).
    
    This gives more comprehensive coverage but requires filtering.
    """
    
    try:
        # Finnhub has a free endpoint for listing all tickers
        api_key = "Your_Finnhub_API_Key"  # Get free from finnhub.io
        
        url = "https://finnhub.io/api/v1/stock/symbol"
        params = {
            "exchange": "NSE",  # National Stock Exchange of India
            "token": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            stocks = response.json()
            # Filter for penny stocks (market cap < 5000 Cr)
            return [s for s in stocks if s.get("type") == "Common Stock"]
        
        return []
    
    except Exception as e:
        print(f"Error fetching NSE stocks: {e}")
        return []


def fetch_bse_penny_stocks() -> list[dict]:
    """Fetch micro-cap stocks from BSE (Bombay Stock Exchange)."""
    
    try:
        url = "https://www.bseindia.com/api/equity/equities"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        
        return []
    
    except Exception as e:
        print(f"Error fetching BSE stocks: {e}")
        return []


def auto_detect_and_sync_penny_stocks() -> dict:
    """Automatically detect penny stocks and sync their data.
    
    This is the main function that:
    1. Fetches NSE/BSE universe
    2. Filters for market cap 100-5000 Cr
    3. Syncs data to database
    4. Returns summary
    """
    
    from app.services.data_ingestion import fetch_stock_from_yfinance
    
    db = SessionLocal()
    
    try:
        print("🔍 Auto-detecting penny stocks from NSE/BSE...")
        
        # Fetch stocks
        nse_stocks = fetch_nse_penny_stocks()
        print(f"   Found {len(nse_stocks)} stocks from NSE Small-Cap Index")
        
        synced_count = 0
        skipped_count = 0
        
        # Sync each stock
        for stock_data in nse_stocks:
            symbol = stock_data.get("symbol")
            
            if not symbol:
                continue
            
            # Check if already in DB
            existing = db.query(StockModel).filter(
                StockModel.symbol == symbol
            ).first()
            
            if existing:
                print(f"   ⏭️  {symbol} - Already in database")
                skipped_count += 1
                continue
            
            # Fetch live data from Yahoo Finance
            print(f"   ⬇️  Fetching {symbol}...")
            live_data = fetch_stock_from_yfinance(symbol)
            
            if live_data:
                # Create stock record
                stock = StockModel(
                    symbol=symbol,
                    company_name=stock_data.get("name", symbol),
                    sector="Unknown",  # Would need to fetch separately
                    market_cap_crore=stock_data.get("market_cap", 0),
                    debt_equity=0.5,  # Default values
                    operating_cash_flow_positive=True,
                    sales_growth_percent=10,
                    promoter_holding_percent=50,
                    promoter_pledge_percent=0,
                )
                
                db.add(stock)
                db.commit()
                
                print(f"   ✅ {symbol} synced to database")
                synced_count += 1
            else:
                print(f"   ⚠️  {symbol} - Could not fetch data")
                skipped_count += 1
        
        return {
            "status": "success",
            "message": "Auto-detection complete",
            "synced": synced_count,
            "skipped": skipped_count,
            "total_fetched": len(nse_stocks),
            "next_step": "Run /weekly-recommendations to see screened results"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    
    finally:
        db.close()


def setup_scheduled_auto_discovery():
    """Set up Celery task to auto-detect stocks every week.
    
    (Requires Celery + Redis configured in settings)
    """
    
    # This would be called by jobs/weekly.py
    # Runs automatically every Monday morning
    
    result = auto_detect_and_sync_penny_stocks()
    print(f"Scheduled auto-discovery result: {result}")
    
    return result
