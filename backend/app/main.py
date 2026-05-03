from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .database import engine, Base
from .routers import portfolio, stocks, indicators, predictions, alerts, backtesting, paper_trading, auth, watchlist
from .stock_cache import get_cache_stats, clear_stock_cache
import time
import uuid 
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Stock Portfolio Tracker API",
    description="""
    ## AI-Powered Stock Portfolio Tracker
    
    ### Features:
    * 📊 Real-time portfolio tracking with P&L
    * 📈 Technical indicators (RSI, MACD, SMA, EMA)
    * 🤖 AI-powered price predictions (LSTM)
    * 🔔 Price alerts and notifications
    * ⚡ Strategy backtesting
    * 💰 Paper trading simulator
    * 📉 Advanced analytics (CAGR, Sharpe Ratio, Beta)
    * ⭐ Stock watchlist
    * 🚀 High-performance caching
    
    ### Authentication:
    All endpoints (except /health and /) require JWT authentication.
    Use `/api/auth/login` or `/api/auth/signup` to get a token.
    """,
    version="2.0.0",
    contact={
        "name": "AMAN",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT"
    }
)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        FRONTEND_URL,
        "*"  # Remove this after deployment
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Generate unique request ID
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    # Log request with ID
    print(f"📥 [{request_id}] {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log response time with ID
    process_time = time.time() - start_time
    status_emoji = "✅" if response.status_code < 400 else "❌"
    print(f"{status_emoji} [{request_id}] {request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.3f}s"
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred. Please try again later.",
            "error_type": type(exc).__name__
        }
    )

# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(x) for x in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["indicators"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(backtesting.router, prefix="/api/backtest", tags=["backtesting"])
app.include_router(paper_trading.router, prefix="/api/paper", tags=["paper_trading"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["watchlist"])

@app.get("/")
def read_root():
    return {
        "message": "Stock Portfolio Tracker API is running!",
        "status": "healthy",
        "version": "2.0.0"
    }

@app.get("/api/info")
def api_info():
    """Get API information and statistics"""
    cache_stats = get_cache_stats()
    
    return {
        "api_name": "Stock Portfolio Tracker API",
        "version": "2.0.0",
        "status": "operational",
        "features": {
            "authentication": True,
            "caching": True,
            "rate_limiting": False,
            "ai_predictions": True,
            "backtesting": True,
            "paper_trading": True,
            "alerts": True,
            "watchlist": True,
            "analytics": True
        },
        "cache": cache_stats,
        "endpoints": {
            "total": 40,
            "public": 3,
            "protected": 37
        }
    }

@app.get("/health")
def health_check():
    cache_info = get_cache_stats()
    return {
        "status": "healthy",
        "version": "2.0.0",
        "cache": cache_info
    }

@app.get("/api/cache/stats")
def cache_stats():
    return get_cache_stats()

@app.post("/api/cache/clear")
def cache_clear():
    clear_stock_cache()
    return {"message": "Cache cleared successfully"}

@app.get("/api/diagnostic")
def diagnostic():
    """System diagnostic endpoint"""
    import sys
    import platform
    
    cache_stats = get_cache_stats()
    
    return {
        "system": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor()
        },
        "api": {
            "version": "2.0.0",
            "status": "healthy"
        },
        "cache": cache_stats,
        "features": {
            "stock_cache": True,
            "validation": True,
            "authentication": True,
            "database_indexes": True
        }
    }