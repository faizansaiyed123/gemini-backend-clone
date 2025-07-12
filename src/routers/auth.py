from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.configs.config import get_db
from src.schemas.auth import UserSignup,SendOTPResponse,SendOTPRequest,VerifyOTPRequest,MobileRequest,ChangePasswordRequest,ResetPasswordRequest
from src.services.auth_service import signup_service,send_otp_service,verify_otp_service,forgot_password_service,change_password_service,reset_password_service
from src.utils.token import get_current_user

router = APIRouter()

@router.post("/signup")
async def signup(user: UserSignup, db: Session = Depends(get_db)):
    return signup_service(user, db)


@router.post("/send-otp")  # 🔁 remove response_model=SendOTPResponse
async def send_otp(user: SendOTPRequest, db: Session = Depends(get_db)):
    return send_otp_service(user, db)



@router.post("/verify-otp")
async def verify_otp(payload: VerifyOTPRequest, db: Session = Depends(get_db)):
    return verify_otp_service(payload, db)


@router.post("/forgot-password")
async def forgot_password(payload: MobileRequest, db: Session = Depends(get_db)):
    return forgot_password_service(payload, db)



@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return change_password_service(current_user_id, payload, db)



@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return reset_password_service(current_user_id, request, db)
