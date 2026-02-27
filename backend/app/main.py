"""
AgriPOS System - Main Application Entry Point
FastAPI Application for Agricultural POS System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.api.v1.endpoints import auth, products, stock, sales, customers, reports

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ระบบ POS สำหรับร้านจำหน่ายปุ๋ยเคมี สารเคมีเกษตร และเครื่องมือเกษตร",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (uploaded images)
uploads_dir = Path(settings.UPLOAD_DIR)
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# API Routes
PREFIX = "/api/v1"
app.include_router(auth.router, prefix=PREFIX)
app.include_router(products.router, prefix=PREFIX)
app.include_router(stock.router, prefix=PREFIX)
app.include_router(sales.router, prefix=PREFIX)
app.include_router(customers.router, prefix=PREFIX)
app.include_router(reports.router, prefix=PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/")
async def root():
    return {
        "message": "AgriPOS API",
        "docs": "/api/docs",
        "version": settings.APP_VERSION
    }
