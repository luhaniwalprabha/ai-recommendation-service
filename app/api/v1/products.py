from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])

@router.get("")
def list_products(db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    service = ProductService(repo)
    return service.get_products()
