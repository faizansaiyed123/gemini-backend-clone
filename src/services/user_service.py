from sqlalchemy.orm import Session
from sqlalchemy import select
from src.services.tables import Tables
from src.common.app_constants import AppConstants
from src.common.app_response import AppResponse
from src.common.messages import Messages
from src.logs.logger import log_message

tables = Tables()
app_response = AppResponse()

def get_me_service(current_user_id: str, db: Session):
    api_name = "get_me"

    try:
        log_message("info", "API called: get_me_service", data={"user_id": current_user_id}, api_name=api_name)

        result = db.execute(
            select(tables.users).where(tables.users.c.id == current_user_id)
        ).fetchone()

        if not result:
            log_message("warning", "User not found", data={"user_id": current_user_id}, api_name=api_name)
            app_response.set_response(
                AppConstants.DATA_NOT_FOUND,
                {},
                Messages.NOT_FOUND_USER_DETAILS,
                False
            )
            return app_response

        user_data = {
            "user_id": str(result.id),
            "mobile": result.mobile,
            "full_name": result.full_name,
            "is_verified": result.is_verified,
            "created_at": result.created_at
        }

        log_message("success", "Fetched user info", data=user_data, api_name=api_name)
        app_response.set_response(
            AppConstants.CODE_SUCCESS,
            user_data,
            Messages.FOUND_USER_DETAILS,
            True
        )
        return app_response

    except Exception as e:
        log_message("error", f"Failed to get user info: {str(e)}", api_name=api_name)
        app_response.set_response(
            AppConstants.CODE_INTERNAL_SERVER_ERROR,
            {},
            Messages.SOMETHING_WENT_WRONG,
            False
        )
        return app_response
