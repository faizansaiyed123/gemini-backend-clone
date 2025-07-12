from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.configs.config import get_db
from src.services.user_service import get_me_service
from src.utils.token import get_current_user

router = APIRouter()

@router.get("/user/me")
def get_me(current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    app_response = get_me_service(current_user_id, db)
    return app_response
