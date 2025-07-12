from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.common.app_response import AppResponse
from src.services.chatroom_service import create_chatroom_service,list_chatrooms_service,get_chatroom_details_service
from src.configs.config import get_db
from src.utils.token import get_current_user
from src.schemas.chatroom import ChatroomCreateRequest

router = APIRouter()

@router.post("/chatroom")
def create_chatroom(
    payload: ChatroomCreateRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    app_response = create_chatroom_service(current_user_id, payload, db)
    return app_response






@router.get("/chatroom")
async def list_chatrooms(current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    app_response = list_chatrooms_service(current_user_id, db)
    return app_response



@router.get("/chatroom/{chatroom_id}")
def get_chatroom_details(chatroom_id: str, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    app_response = get_chatroom_details_service(chatroom_id, current_user_id, db)
    return app_response
