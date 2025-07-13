from fastapi import APIRouter, Depends
from src.schemas.message import SendMessageRequest
from src.services.message_service import send_message_service
from src.configs.config import get_db
from src.utils.token import get_current_user

router = APIRouter()

@router.post("/{chatroom_id}/message")
def send_message(chatroom_id: str, payload: SendMessageRequest, db=Depends(get_db), user_id: str = Depends(get_current_user)):
    return send_message_service(user_id, chatroom_id, payload, db)