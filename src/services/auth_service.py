from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
import uuid
from src.services.tables import Tables
from sqlalchemy import update
from src.common.app_response import AppResponse
from src.common.app_constants import AppConstants
from src.common.messages import Messages
import random
from src.utils.token import create_access_token
from passlib.hash import bcrypt
from datetime import datetime, timedelta
from src.logs.logger import log_message
from src.schemas.auth import ChangePasswordRequest ,ResetPasswordRequest
app_response = AppResponse()
tables = Tables()

def signup_service(user, db: Session):
    api_name = "signup"
    tables = Tables()

    try:
        log_message("info", "API called: signup_service", data={"mobile": user.mobile}, api_name=api_name)

        if not user.mobile or not user.password:
            log_message("warning", "Signup failed: Missing required fields", data={"user": user}, api_name=api_name)
            app_response.set_response(AppConstants.CODE_INVALID_REQUEST, {}, Messages.VALIDATE_DATA, False)
            return app_response

        # Check if user already exists
        existing_user = db.execute(
            select(tables.users).where(tables.users.c.mobile == user.mobile)
        ).fetchone()

        if existing_user:
            log_message("warning", "Signup failed: Mobile already exists", data={"user": user.mobile}, api_name=api_name)
            app_response.set_response(AppConstants.CODE_CONFLICT, {}, Messages.MOBILE_ALREADY_EXISTS, False)
            return app_response

        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = bcrypt.hash(user.password)

        db.execute(
            tables.users.insert().values(
                id=user_id,
                mobile=user.mobile,
                full_name=user.full_name,
                password_hash=hashed_password,
                created_at=datetime.utcnow()
            )
        )
        db.commit()

        # Generate JWT Token
        token = create_access_token({"sub": user_id})

        log_message("success", "User registered", data={"user_id": user_id}, api_name=api_name)

        app_response.set_response(
            AppConstants.CODE_SUCCESS,
            {
                "user_id": user_id,
                "token": token
            },
            Messages.SIGNUP_SUCCESS,
            True
        )
        return app_response

    except Exception as e:
        log_message("error", f"Signup failed with error: {str(e)}", api_name=api_name)
        app_response.set_response(AppConstants.CODE_INTERNAL_SERVER_ERROR, {}, Messages.INTERNAL_SERVER_ERROR, False)
        return app_response




def send_otp_service(user, db: Session):
    api_name = "send_otp"
    tables = Tables()

    try:
        log_message("info", "API called: send_otp_service", data={"mobile": user.mobile}, api_name=api_name)

        result = db.execute(
            select(tables.users).where(tables.users.c.mobile == user.mobile)
        ).fetchone()

        if not result:
            log_message("warning", "OTP send failed: Mobile not found", data={"mobile": user.mobile}, api_name=api_name)
            app_response.set_response(
                AppConstants.DATA_NOT_FOUND,
                {},
                Messages.NOT_FOUND_USER_DETAILS,
                Messages.FALSE
            )
            return app_response

        otp = str(random.randint(100000, 999999))

        db.execute(
            update(tables.users)
            .where(tables.users.c.mobile == user.mobile)
            .values(otp_code=otp, otp_created_at=datetime.utcnow())
        )
        db.commit()

        log_message("success", "OTP sent (mocked)", data={"mobile": user.mobile, "otp": otp}, api_name=api_name)

        app_response.set_response(
            AppConstants.CODE_SUCCESS,
            {"otp": otp},
            Messages.OTP_SENT_SUCCESSFULLY,
            Messages.TRUE
        )
        return app_response

    except Exception as e:
        log_message("error", f"OTP send failed with error: {str(e)}", api_name=api_name)
        app_response.set_response(
            AppConstants.CODE_INTERNAL_SERVER_ERROR,
            {},
            Messages.SOMETHING_WENT_WRONG,
            Messages.FALSE
        )
        return app_response




def verify_otp_service(payload, db: Session):
    api_name = "verify_otp"
    tables = Tables()

    try:
        log_message("info", "API called: verify_otp_service", data={"mobile": payload.mobile}, api_name=api_name)

        result = db.execute(
            select(tables.users).where(tables.users.c.mobile == payload.mobile)
        ).fetchone()

        if not result:
            log_message("warning", "Mobile not found", data={"mobile": payload.mobile}, api_name=api_name)
            app_response.set_response(AppConstants.DATA_NOT_FOUND, {}, Messages.NOT_FOUND_USER_DETAILS, Messages.FALSE)
            return app_response

        user = result._mapping

        if user["otp_code"] != payload.otp:
            app_response.set_response(AppConstants.CODE_INVALID_REQUEST, {}, Messages.OTP_INCORRECT_OR_EXPIRED, Messages.FALSE)
            return app_response

        if not user["otp_created_at"] or (datetime.utcnow() - user["otp_created_at"]) > timedelta(minutes=5):
            app_response.set_response(AppConstants.CODE_INVALID_REQUEST, {}, Messages.OTP_INCORRECT_OR_EXPIRED, Messages.FALSE)
            return app_response

        db.execute(
            update(tables.users)
            .where(tables.users.c.mobile == payload.mobile)
            .values(
                is_verified=True,
                otp_code=None,
                otp_created_at=None
            )
        )
        db.commit()

        access_token = create_access_token({"sub": str(user["id"])})
        app_response.set_response(AppConstants.CODE_SUCCESS, {"access_token": access_token}, Messages.OTP_VERIFIED_SUCCESSFULLY, Messages.TRUE)
        return app_response

    except Exception as e:
        log_message("error", f"OTP verification failed: {str(e)}", api_name=api_name)
        app_response.set_response(AppConstants.CODE_INTERNAL_SERVER_ERROR, {}, Messages.SOMETHING_WENT_WRONG, Messages.FALSE)
        return app_response


def forgot_password_service(user, db: Session):
    api_name = "forgot_password"
    tables = Tables()

    try:
        log_message("info", "API called: forgot_password_service", data={"mobile": user.mobile}, api_name=api_name)

        result = db.execute(
            select(tables.users).where(tables.users.c.mobile == user.mobile)
        ).fetchone()

        if not result:
            log_message("warning", "Forgot password failed: Mobile not found", data={"mobile": user.mobile}, api_name=api_name)
            app_response.set_response(
                AppConstants.DATA_NOT_FOUND,
                {},
                Messages.NOT_FOUND_USER_DETAILS,
                Messages.FALSE
            )
            return app_response

        otp = str(random.randint(100000, 999999))

        db.execute(
            update(tables.users)
            .where(tables.users.c.mobile == user.mobile)
            .values(otp_code=otp, otp_created_at=datetime.utcnow())
        )
        db.commit()

        log_message("success", "OTP sent for password reset (mocked)", data={"mobile": user.mobile, "otp": otp}, api_name=api_name)

        app_response.set_response(
            AppConstants.CODE_SUCCESS,
            {"otp": otp},
            Messages.OTP_SENT_SUCCESSFULLY,
            Messages.TRUE
        )
        return app_response

    except Exception as e:
        log_message("error", f"Forgot password OTP send failed with error: {str(e)}", api_name=api_name)
        app_response.set_response(
            AppConstants.CODE_INTERNAL_SERVER_ERROR,
            {},
            Messages.SOMETHING_WENT_WRONG,
            Messages.FALSE
        )
        return app_response



def change_password_service(user_id: str, request: ChangePasswordRequest, db: Session):
    api_name = "change_password"
    tables = Tables()

    try:
        log_message("info", "API called: change_password_service", data={"user_id": user_id}, api_name=api_name)

        result = db.execute(
            select(tables.users).where(tables.users.c.id == user_id)
        ).fetchone()

        if not result:
            log_message("warning", "User not found", data={"user_id": user_id}, api_name=api_name)
            app_response.set_response(
                AppConstants.DATA_NOT_FOUND,
                {},
                Messages.NOT_FOUND_USER_DETAILS,
                False
            )
            return app_response

        if not bcrypt.verify(request.old_password, result.password_hash):
            log_message("warning", "Incorrect old password", data={"user_id": user_id}, api_name=api_name)
            app_response.set_response(
                AppConstants.CODE_UNAUTHORIZED,
                {},
                Messages.INCORRECT_OLD_PASSWORD,
                False
            )
            return app_response

        hashed_new_password = bcrypt.hash(request.new_password)

        db.execute(
            update(tables.users)
            .where(tables.users.c.id == user_id)
            .values(password_hash=hashed_new_password)
        )
        db.commit()

        log_message("success", "Password changed successfully", data={"user_id": user_id}, api_name=api_name)
        app_response.set_response(
            AppConstants.CODE_SUCCESS,
            {},
            Messages.PASSWORD_CHANGED_SUCCESSFULLY,
            True
        )
        return app_response

    except Exception as e:
        log_message("error", f"Password change failed: {str(e)}", api_name=api_name)
        app_response.set_response(
            AppConstants.CODE_INTERNAL_SERVER_ERROR,
            {},
            Messages.SOMETHING_WENT_WRONG,
            False
        )
        return app_response



def reset_password_service(user_id: str, request: ResetPasswordRequest, db: Session):
    api_name = "reset_password"
    tables = Tables()

    try:
        log_message("info", "API called: reset_password_service", data={"user_id": user_id}, api_name=api_name)

        result = db.execute(
            select(tables.users).where(tables.users.c.id == user_id)
        ).fetchone()

        if not result:
            log_message("warning", "User not found for password reset", data={"user_id": user_id}, api_name=api_name)
            app_response.set_response(
                AppConstants.DATA_NOT_FOUND,
                {},
                Messages.NOT_FOUND_USER_DETAILS,
                Messages.FALSE
            )
            return app_response

        hashed_password = bcrypt.hash(request.new_password)

        db.execute(
            update(tables.users)
            .where(tables.users.c.id == user_id)
            .values(password_hash=hashed_password)
        )
        db.commit()

        log_message("success", "Password reset successfully", data={"user_id": user_id}, api_name=api_name)
        app_response.set_response(
            AppConstants.CODE_SUCCESS,
            {},
            Messages.PASSWORD_RESET_SUCCESSFULLY,
            Messages.TRUE
        )
        return app_response

    except Exception as e:
        log_message("error", f"Password reset failed: {str(e)}", api_name=api_name)
        app_response.set_response(
            AppConstants.CODE_INTERNAL_SERVER_ERROR,
            {},
            Messages.SOMETHING_WENT_WRONG,
            Messages.FALSE
        )
        return app_response
