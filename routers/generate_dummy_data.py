from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session
# from models import User
from db.dummy_generator import generate_dummy_data_for_user
from sqlmodel import Session, select
from db.connection import engine
from db.models import User
from routers.auth import get_current_user
from fastapi import Query


router = APIRouter()

@router.post("/")
def generate_my_dummy_data(
    user = Depends(get_current_user),
    products: int = Query(default=10, ge=0, le=100),
    sales: int = Query(default=15, ge=0, le=200),
    finances: int = Query(default=10, ge=0, le=100),
    budgets: int = Query(default=2, ge=0, le=20)
):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user["id"])).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        try:
            business_id = generate_dummy_data_for_user(
                user_id=user.id,
                session=session,
                products_count=products,
                sales_count=sales,
                finances_count=finances,
                budgets_count=budgets
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return {"status": "success", "business_id": business_id}