#!/usr/bin/env python3
"""Test script to verify all imports work correctly."""

import sys
import traceback

print("Testing PennyStock imports...")
print("=" * 60)

try:
    print("1. Testing app.config...")
    from app.config import DEFAULT_WEEKLY_ALLOCATION_INR
    print("   ✓ app.config imports successfully")
except Exception as e:
    print(f"   ✗ ERROR in app.config: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("2. Testing app.domain...")
    from app.domain import Stock, StockMetrics, StockScore
    print("   ✓ app.domain imports successfully")
except Exception as e:
    print(f"   ✗ ERROR in app.domain: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("3. Testing app.services.screener...")
    from app.services.screener import screen_stocks
    print("   ✓ app.services.screener imports successfully")
except Exception as e:
    print(f"   ✗ ERROR in app.services.screener: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("4. Testing app.services.scoring...")
    from app.services.scoring import score_stock
    print("   ✓ app.services.scoring imports successfully")
except Exception as e:
    print(f"   ✗ ERROR in app.services.scoring: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("5. Testing app.services.recommendations...")
    from app.services.recommendations import generate_weekly_recommendations
    print("   ✓ app.services.recommendations imports successfully")
except Exception as e:
    print(f"   ✗ ERROR in app.services.recommendations: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("6. Testing app.services.budget...")
    from app.services.budget import BudgetState
    print("   ✓ app.services.budget imports successfully")
except Exception as e:
    print(f"   ✗ ERROR in app.services.budget: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("7. Testing app.services.ai_insights...")
    from app.services.ai_insights import build_company_note_prompt
    print("   ✓ app.services.ai_insights imports successfully")
except Exception as e:
    print(f"   ✗ ERROR in app.services.ai_insights: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("8. Testing app.api.main...")
    from app.api.main import app
    print("   ✓ app.api.main imports successfully")
except Exception as e:
    print(f"   ✗ ERROR in app.api.main: {e}")
    traceback.print_exc()
    sys.exit(1)

print("=" * 60)
print("✓ All imports successful! Backend is ready to run.")
print("\nTo start the server, run:")
print("  python3 -m uvicorn app.api.main:app --reload --port 8000")
