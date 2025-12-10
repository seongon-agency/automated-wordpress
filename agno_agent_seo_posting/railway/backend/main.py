"""
WordPress SEO Publishing System - Python Backend
FastAPI microservice for heavy processing tasks
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from routers import publish, patterns, history, projects
from database.db import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting WordPress SEO Publishing Backend...")
    try:
        init_database()
    except Exception as e:
        print(f"[WARNING] Database initialization failed: {e}")
        print("Backend will start but database operations may fail")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="WordPress SEO Publishing API",
    description="Backend API for WordPress SEO Publishing System",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(publish.router, prefix="/api/publish", tags=["Publishing"])
app.include_router(patterns.router, prefix="/api/patterns", tags=["Patterns"])
app.include_router(history.router, prefix="/api/history", tags=["History"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "WordPress SEO Publishing API",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
