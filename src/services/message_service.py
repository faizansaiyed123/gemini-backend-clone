from sqlalchemy.orm import Session
from sqlalchemy import insert, select
import uuid
from datetime import datetime
from src.utils.rate_limiter import check_and_increment_rate_limit
from src.services.tables import Tables
from src.common.app_response import AppResponse
from src.common.app_constants import AppConstants
from src.common.messages import Messages
from src.logs.logger import log_message
from src.schemas.message import SendMessageRequest
from src.queue.queue import push_to_queue

tables = Tables()
app_response = AppResponse()

def send_message_service(user_id: str, chatroom_id: str, payload: SendMessageRequest, db: Session):
    api_name = "send_message"

    try:
        log_message("info", "API called: send_message_service", data={
            "chatroom_id": chatroom_id,
            "user_id": user_id
        }, api_name=api_name)


        user_tier = db.execute(
            select(tables.users.c.subscription_tier)
            .where(tables.users.c.id == user_id)
        ).scalar_one_or_none()


        if user_tier == "basic":
            allowed = check_and_increment_rate_limit(user_id)
            if not allowed:
                app_response.set_response(
                    AppConstants.CODE_TOO_MANY_REQUESTS,
                    {},
                    "Rate limit exceeded: Only 5 messages allowed per day on Basic plan.",
                    Messages.FALSE
                )
                return app_response


        chatroom = db.execute(
            select(tables.chatrooms).where(
                (tables.chatrooms.c.id == chatroom_id) &
                (tables.chatrooms.c.user_id == user_id)
            )
        ).fetchone()

        if not chatroom:
            app_response.set_response(
                AppConstants.DATA_NOT_FOUND,
                {},
                Messages.CHATROOM_NOT_FOUND,
                Messages.FALSE
            )
            return app_response


        message_id = str(uuid.uuid4())
        db.execute(
            insert(tables.chat_messages).values(
                id=message_id,
                chatroom_id=chatroom_id,
                sender="user",
                content=payload.content,
                created_at=datetime.utcnow()
            )
        )
        db.commit()

        #Push message to async processing queue
        push_to_queue({
            "chatroom_id": chatroom_id,
            "user_id": user_id,
            "message_id": message_id,
            "content": payload.content
        })

        log_message("success", "Message saved and pushed to queue", data={"message_id": message_id}, api_name=api_name)

        app_response.set_response(
            AppConstants.CODE_SUCCESS,
            {"message_id": message_id},
            Messages.MESSAGE_SENT_SUCCESSFULLY,
            Messages.TRUE
        )
        return app_response

    except Exception as e:
        log_message("error", f"Failed to send message: {str(e)}", api_name=api_name)
        app_response.set_response(
            AppConstants.CODE_INTERNAL_SERVER_ERROR,
            {},
            Messages.SOMETHING_WENT_WRONG,
            Messages.FALSE
        )
        return app_response
