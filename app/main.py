from fastapi import FastAPI
from app.config import settings
from app.api.v1.health import router as health_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.products import router as products_router
from app.api.v1.feedback import router as feedback_router
from app.middleware.logging_middleware import LoggingMiddleware



def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.service_name,
        version="1.0.0",
        redirect_slashes=False,
    )

    app.include_router(health_router, prefix="/api/v1")
    app.include_router(recommendations_router, prefix="/v1/recommendations", tags=["recommendations"],)
    app.include_router(products_router, prefix="/v1")
    app.include_router(feedback_router, prefix="/v1")
    

    return app


app = create_app()
app.add_middleware(LoggingMiddleware)
