"""Commodity Forecasting Lab API.

A FastAPI application for AI-powered commodity price forecasting,
portfolio tracking, and market intelligence.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router


def create_application() -> FastAPI:
    """Create and configure the FastAPI application.

    Sets up CORS, mounts the v1 API router, and configures docs URLs.

    Returns:
        Configured FastAPI application instance.
    """
    app = FastAPI(
        title="Commodity Forecasting Lab",
        version="1.0.0",
        description="AI-powered commodity forecasting and portfolio management",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS: exact origins + regex for Vercel preview deployments (*.vercel.app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "https://ai-saas-fawn-kappa.vercel.app",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_origin_regex=r"https://[a-z0-9-]+\.vercel\.app",
    )

    # Include API routes
    app.include_router(api_router)

    return app


# Create application instance
app = create_application()


@app.get("/")
def root():
    """Return basic API information and links to documentation.

    Returns:
        Dict with message, status, version, and docs URL.
    """
    return {
        "message": "Commodity Forecasting Lab API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint for monitoring and load balancers.

    Returns:
        Dict with status key (e.g. 'healthy').
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
