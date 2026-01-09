"""
Commodity Forecasting Lab API

A FastAPI application for AI-powered commodity price forecasting,
portfolio tracking, and market intelligence.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.config import settings


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Commodity Forecasting Lab",
        version="1.0.0",
        description="AI-powered commodity forecasting and portfolio management",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "https://ai-saas-fawn-kappa.vercel.app",
            "https://*.vercel.app",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router)
    
    return app


# Create application instance
app = create_application()


@app.get("/")
def root():
    """
    API root endpoint.
    
    Returns basic information about the API.
    """
    return {
        "message": "Commodity Forecasting Lab API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        Health status indicator
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
