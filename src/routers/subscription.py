from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from src.configs.config import get_db
from src.utils.token import get_current_user
from src.services.subscription import subscribe_pro_service ,subscription_status_service
from src.common.app_response import AppResponse
from src.common.app_constants import AppConstants
from src.common.messages import Messages
from src.configs.settings import settings
from sqlalchemy import update
from src.services.tables import Tables
from src.logs.logger import log_message
import stripe
from stripe.error import SignatureVerificationError

app_response = AppResponse()
router = APIRouter()
tables = Tables()


@router.post("/pro")
def subscribe_pro(
    request: Request,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)  # ✅ use your custom dependency
):
    return subscribe_pro_service(user_id, db, request)




@router.post("/webhook/stripe", include_in_schema=False)
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        app_response.set_response(
            AppConstants.CODE_UNAUTHORIZED,
            {},
            "Missing Stripe signature",
            Messages.FALSE
        )
        return app_response

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        app_response.set_response(
            AppConstants.CODE_UNAUTHORIZED,
            {},
            "Invalid Stripe signature",
            Messages.FALSE
        )
        return app_response

    if event["type"] == "checkout.session.completed":
        session_data = event["data"]["object"]
        user_id = session_data.get("client_reference_id")

        if user_id:
            db.execute(
                update(tables.users)
                .where(tables.users.c.id == user_id)
                .values(subscription_tier="pro")
            )
            db.commit()

            log_message("success", "User upgraded to Pro", data={"user_id": user_id}, api_name="stripe_webhook")

    app_response.set_response(
        AppConstants.CODE_SUCCESS,
        {},
        "Webhook processed",
        Messages.TRUE
    )
    return app_response



@router.get("/subscription/status")
def subscription_status(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return subscription_status_service(user_id, db)