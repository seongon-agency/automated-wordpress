"""
FastAPI Backend - WordPress SEO Publishing System

Main entry point for the FastAPI application.
Provides REST API endpoints for the frontend.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from routers import projects_router, publish_router, patterns_router, history_router
from database import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - initialize database on startup."""
    print("Starting up...")
    try:
        init_database()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
    yield
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="WordPress SEO Publishing API",
    description="API for publishing Google Docs to WordPress with AI-powered HTML transformations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects_router, prefix="/api/projects", tags=["Projects"])
app.include_router(publish_router, prefix="/api/publish", tags=["Publishing"])
app.include_router(patterns_router, prefix="/api/patterns", tags=["AI Patterns"])
app.include_router(history_router, prefix="/api/history", tags=["History"])


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "WordPress SEO Publishing API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
