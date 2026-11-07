from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Product

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/")
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_active == True).order_by(Product.category, Product.id).all()
    return [_product_out(p) for p in products]


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Product.category).filter(Product.is_active == True).distinct().all()
    return [c[0] for c in cats]


@router.get("/{product_id}")
def get_product(product_id: str, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id.upper()).first()
    if not p:
        from fastapi import HTTPException
        raise HTTPException(404, "Product not found")
    return _product_out(p)


def _product_out(p: Product) -> dict:
    return {
        "id": p.id,
        "category": p.category,
        "product_name": p.product_name,
        "description": p.description,
        "unit": p.unit,
        "price_min_inr": p.price_min_inr_per_month,
        "price_max_inr": p.price_max_inr_per_month,
        "price_display": f"₹{int(p.price_min_inr_per_month):,}–{int(p.price_max_inr_per_month):,}/mo",
        "one_time_setup_inr": p.one_time_setup_inr,
        "min_contract_months": p.min_contract_months,
        "available_city_tiers": p.available_city_tiers,
        "min_employees": p.min_employees,
        "min_sites": p.min_sites,
        "requires_gstin": p.requires_gstin,
        "requires_one_of": p.requires_one_of or "",
        "typical_install_days": p.typical_install_days,
        "target_segments": p.target_segments,
    }
