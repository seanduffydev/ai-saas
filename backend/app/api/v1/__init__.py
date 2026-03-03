"""API version 1 router aggregation.

Mounts all v1 endpoint routers: commodities, forecast, news, portfolio, watchlist.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import commodities, forecast, news, portfolio, watchlist

api_router = APIRouter()

api_router.include_router(commodities.router, tags=["commodities"])
api_router.include_router(forecast.router, tags=["forecast"])
api_router.include_router(news.router, tags=["news"])
api_router.include_router(portfolio.router, tags=["portfolio"])
api_router.include_router(watchlist.router, tags=["watchlist"])
