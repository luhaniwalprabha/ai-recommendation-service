from fastapi import FastAPI
from app.config import settings
from app.api.v1.health import router as health_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.products import router as products_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.service_name,
        version="1.0.0",
    )

    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(
        recommendations_router,
        prefix="/v1/recommendations",
        tags=["recommendations"],
    )
    app.include_router(products_router, prefix="/v1")

    return app


app = create_app()
