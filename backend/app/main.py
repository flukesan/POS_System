"""
AgriPOS System - Main Application Entry Point
FastAPI Application for Agricultural POS System
"""
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
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


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Return real error details instead of generic 500."""
    tb = traceback.format_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"{type(exc).__name__}: {str(exc)}", "traceback": tb},
    )


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
