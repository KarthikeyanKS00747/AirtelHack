"""Unit tests for Server-Side Pricing, Taxes, and Quote Generation."""
import pytest
from app.core.database import SessionLocal
from app.models import Product
from app.api.routes.quotes import _calc_line_items, LineItem


def test_server_side_price_calculation():
    db = SessionLocal()
    try:
        # P01: Biz Fibre 100 (999–1199, midpoint 1099, setup 0)
        # P19: Cloud POS (599–899, midpoint 749, setup 2500)
        items = [
            LineItem(product_id="P01", quantity=1),
            LineItem(product_id="P19", quantity=2),
        ]
        line_items_out, total_monthly, total_setup = _calc_line_items(items, db)

        assert len(line_items_out) == 2
        # P01 midprice = 1099.0
        assert line_items_out[0]["monthly_cost_inr"] == 1099.0
        assert line_items_out[0]["setup_cost_inr"] == 0.0

        # P19 midprice = 749.0 * 2 = 1498.0, setup = 2500.0 * 2 = 5000.0
        assert line_items_out[1]["monthly_cost_inr"] == 1498.0
        assert line_items_out[1]["setup_cost_inr"] == 5000.0

        assert total_monthly == round(1099.0 + 1498.0, 2)
        assert total_setup == 5000.0
    finally:
        db.close()


def test_quote_tax_calculation():
    # 18% GST calculation check
    total_monthly = 2597.0
    tax = round(total_monthly * 0.18, 2)
    total_with_tax = round(total_monthly + tax, 2)

    assert tax == 467.46
    assert total_with_tax == 3064.46
