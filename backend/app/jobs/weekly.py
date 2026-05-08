"""Weekly automation entrypoint for Sunday-night refreshes."""

from __future__ import annotations

from datetime import date

from app.services.budget import BudgetState
from app.services.recommendations import generate_weekly_recommendations
from app.services.scoring import score_stock
from app.services.screener import screen_stocks
from app.services.data_ingestion import get_stocks_from_db
from app.services.penny_stock_discovery import auto_detect_and_sync_penny_stocks


def auto_discover_and_refresh() -> dict[str, object]:
    """🤖 WEEKLY AUTOMATION (runs every Sunday night):
    
    1. Auto-discover new penny stocks from NSE/BSE
    2. Download their data
    3. Generate Monday morning recommendations
    4. Alert user to best buy opportunities
    """
    
    print("\n" + "="*60)
    print("🤖 WEEKLY AUTOMATION STARTED")
    print("="*60)
    
    # STEP 1: Auto-discover new penny stocks
    print("\n📡 Step 1: Auto-discovering penny stocks from NSE/BSE...")
    discovery_result = auto_detect_and_sync_penny_stocks()
    print(f"   Result: {discovery_result['synced']} stocks synced")
    
    # STEP 2: Fetch all stocks from database (both new and existing)
    print("\n📊 Step 2: Fetching all stocks from database...")
    stocks, metrics = get_stocks_from_db()
    print(f"   Total stocks in database: {len(stocks)}")
    
    # STEP 3: Apply screener filters
    print("\n🔍 Step 3: Applying universe filters...")
    screened = screen_stocks(stocks)
    print(f"   ✅ {len(screened)} stocks passed all 9 filters")
    
    # STEP 4: Score each qualified stock
    print("\n📈 Step 4: Scoring all qualified stocks...")
    scores = {}
    for stock in screened:
        if stock.symbol in metrics:
            scores[stock.symbol] = score_stock(stock, metrics[stock.symbol])
    print(f"   ✅ Scored {len(scores)} stocks")
    
    # STEP 5: Generate recommendations
    print("\n💡 Step 5: Generating weekly recommendations...")
    recommendations = generate_weekly_recommendations(
        screened, 
        scores, 
        BudgetState(0),  # Assuming fresh month
        date.today()
    )
    
    print("\n" + "="*60)
    print("✅ WEEKLY AUTOMATION COMPLETE")
    print("="*60)
    print(f"\nRecommendations ready:")
    print(f"  • Buy signals: {len([r for r in recommendations.get('recommendations', []) if r.get('action') == 'BUY'])}")
    print(f"  • Watch list: {len(recommendations.get('watchlist', []))}")
    
    return recommendations


def refresh_weekly_recommendations(monthly_invested: int = 0) -> dict[str, object]:
    """Fetch data, score the universe, and generate Monday recommendations.
    
    (Called manually or by scheduler)
    """
    
    stocks, metrics = get_stocks_from_db()
    screened = screen_stocks(stocks)
    scores = {stock.symbol: score_stock(stock, metrics[stock.symbol]) for stock in screened}
    return generate_weekly_recommendations(screened, scores, BudgetState(monthly_invested), date.today())

