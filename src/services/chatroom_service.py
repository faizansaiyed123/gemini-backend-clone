import uuid
from datetime import datetime
from sqlalchemy import select
from src.services.tables import Tables
from src.logs.logger import log_message
from src.common.app_response import AppResponse
from src.common.app_constants import AppConstants
from src.common.messages import Messages
from sqlalchemy.orm import Session
from src.configs.redis_config import redis_client
import json
tables = Tables()
app_response = AppResponse()

def create_chatroom_service(user_id: str, payload, db):
    api_name = "create_chatroom"
    tables = Tables()

    try:
        log_message("info", "API called: create_chatroom_service", data={"user_id": user_id}, api_name=api_name)

        chatroom_id = str(uuid.uuid4())
        db.execute(
            tables.chatrooms.insert().values(
                id=chatroom_id,
                user_id=user_id,
                title=payload.title,
                created_at=datetime.utcnow()
            )
        )
        db.commit()

        log_message("success", "Chatroom created", data={"chatroom_id": chatroom_id}, api_name=api_name)

        app_response.set_response(
            AppConstants.CODE_SUCCESS,
            {"chatroom_id": chatroom_id},
            Messages.CHATROOM_CREATED,
            Messages.TRUE
        )
        return app_response

    except Exception as e:
        log_message("error", f"Chatroom creation failed: {str(e)}", api_name=api_name)

        app_response.set_response(
            AppConstants.CODE_INTERNAL_SERVER_ERROR,
            {},
            Messages.SOMETHING_WENT_WRONG,
            Messages.FALSE
        )
        return app_response





def list_chatrooms_service(user_id: str, db: Session):
    api_name = "list_chatrooms"

    try:
        log_message("info", "API called: list_chatrooms_service", data={"user_id": user_id}, api_name=api_name)

        cache_key = f"chatrooms:{user_id}"
        cached = redis_client.get(cache_key)

        if cached:
            chatrooms = json.loads(cached)
            log_message("info", "Returned chatrooms from cache", api_name=api_name)
        else:
            result = db.execute(
                select(tables.chatrooms).where(tables.chatrooms.c.user_id == user_id)
            ).fetchall()

            chatrooms = [
                {
                    "chatroom_id": str(row.id),
                    "name": row.title,
                    "created_at": row.created_at.isoformat()
                }
                for row in result
            ]

            redis_client.setex(cache_key, 600, json.dumps(chatrooms))  # TTL 10 minutes
            log_message("info", "Chatrooms fetched from DB and cached", api_name=api_name)

        app_response.set_response(
            AppConstants.CODE_SUCCESS,
            chatrooms,
            Messages.CHATROOMS_FETCHED_SUCCESSFULLY,
            True
        )
        return app_response

    except Exception as e:
        log_message("error", f"Failed to list chatrooms: {str(e)}", api_name=api_name)
        app_response.set_response(
            AppConstants.CODE_INTERNAL_SERVER_ERROR,
            {},
            Messages.SOMETHING_WENT_WRONG,
            False
        )
        return app_response


def get_chatroom_details_service(chatroom_id: str, user_id: str, db: Session):
    api_name = "get_chatroom_details"
    tables = Tables()

    try:
        log_message("info", "API called: get_chatroom_details_service", data={"chatroom_id": chatroom_id}, api_name=api_name)

        # Fetch the chatroom owned by user
        result = db.execute(
            select(tables.chatrooms).where(
                (tables.chatrooms.c.id == chatroom_id) &
                (tables.chatrooms.c.user_id == user_id)
            )
        ).fetchone()

        if not result:
            log_message("warning", "Chatroom not found or unauthorized", data={"chatroom_id": chatroom_id}, api_name=api_name)
            app_response.set_response(
                AppConstants.DATA_NOT_FOUND,
                {},
                Messages.CHATROOM_NOT_FOUND,
                Messages.FALSE
            )
            return app_response

        # Fetch all messages from the chatroom
        messages = db.execute(
            select(tables.chat_messages)
            .where(tables.chat_messages.c.chatroom_id == chatroom_id)
            .order_by(tables.chat_messages.c.created_at.asc())
        ).fetchall()

        message_data = [
            {
                "message_id": str(m.id),
                "content": m.content,
                "sender": m.sender,
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ]

        data = {
            "chatroom_id": str(result.id),
            "name": result.title,
            "created_at": result.created_at.isoformat(),
            "messages": message_data
        }

        log_message("success", "Chatroom details fetched", data=data, api_name=api_name)

        app_response.set_response(
            AppConstants.CODE_SUCCESS,
            data,
            Messages.CHATROOM_DETAILS_FETCHED,
            Messages.TRUE
        )
        return app_response

    except Exception as e:
        log_message("error", f"Failed to fetch chatroom details: {str(e)}", api_name=api_name)
        app_response.set_response(
            AppConstants.CODE_INTERNAL_SERVER_ERROR,
            {},
            Messages.SOMETHING_WENT_WRONG,
            Messages.FALSE
        )
        return app_response
