"""
FastAPI Main Application

REST API for WordPress SEO Publishing System.
Provides endpoints for multi-project management and content publishing.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from api.core.config import get_settings
from api.routes import health, projects, publishing

# Get settings
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
)

# Add CORS middleware
if settings.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()

    # Log request
    logger.info(f"→ {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log response
    logger.info(f"← {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")

    # Add timing header
    response.headers["X-Process-Time"] = str(duration)

    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.LOG_LEVEL == "DEBUG" else "An unexpected error occurred",
        }
    )


# Include routers
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(projects.router, prefix=settings.API_PREFIX)
app.include_router(publishing.router, prefix=settings.API_PREFIX)


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "WordPress SEO Publishing API",
        "version": settings.API_VERSION,
        "docs": f"{settings.API_PREFIX}/docs",
        "health": f"{settings.API_PREFIX}/health",
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("=" * 80)
    logger.info(f"🚀 {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info("=" * 80)
    logger.info(f"📡 Server: {settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"📚 Docs: http://{settings.API_HOST}:{settings.API_PORT}{settings.API_PREFIX}/docs")
    logger.info(f"🔐 Auth: API Key {'enabled' if settings.API_KEYS else 'disabled (development mode)'}")
    logger.info(f"🌐 CORS: {'enabled' if settings.ENABLE_CORS else 'disabled'}")
    logger.info("=" * 80)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("👋 Shutting down API server")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,  # Enable auto-reload for development
        log_level=settings.LOG_LEVEL.lower(),
    )
