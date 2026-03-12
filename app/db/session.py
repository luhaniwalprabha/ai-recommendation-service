from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.database_url, echo=settings.environment == "local")
SessionLocal = sessionmaker(bind=engine)