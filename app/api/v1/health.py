from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.cache.redis_client import get_redis_client
from sqlalchemy import text

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/ready")
def readiness_check():
    status = {"database": "ok", "redis": "ok"}

    # Check DB
    try:
        db: Session = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:
        status["database"] = "down"

    # Check Redis
    try:
        redis = get_redis_client()
        redis.ping()
    except Exception:
        status["redis"] = "down"

    return status