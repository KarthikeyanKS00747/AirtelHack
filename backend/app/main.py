from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.api.routes import auth, advisor, recommendations, quotes, orders, kyc, leads, analytics, products

app = FastAPI(
    title="Udyam Digital API",
    description="Accel Business — MSME Digital Onboarding Platform (Airtel SYNC Hackathon 2026)",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(advisor.router)
app.include_router(recommendations.router)
app.include_router(products.router)
app.include_router(quotes.router)
app.include_router(orders.router)
app.include_router(kyc.router)
app.include_router(leads.router)
app.include_router(analytics.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "version": settings.APP_VERSION, "env": settings.APP_ENV}


@app.get("/")
def root():
    return {"message": "Udyam Digital API. Visit /api/docs for documentation."}
