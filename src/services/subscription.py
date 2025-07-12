import stripe
from fastapi import Request
from sqlalchemy.orm import Session
from src.common.app_response import AppResponse
from src.common.app_constants import AppConstants
from src.common.messages import Messages
from src.configs.settings import settings
from src.logs.logger import log_message
from src.services.tables import Tables
from sqlalchemy import update ,select
app_response = AppResponse()
tables = Tables()
stripe.api_key = settings.STRIPE_SECRET_KEY

def subscribe_pro_service(user_id: str, db: Session, request: Request):
    api_name = "subscribe_pro"
    try:
        YOUR_DOMAIN = settings.FRONTEND_URL or "http://localhost:3000"

        # Create Stripe Checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='subscription',
            customer_email=None,  # Optionally pass user's email
            line_items=[{
                'price': settings.STRIPE_PRICE_ID,  # From Stripe dashboard
                'quantity': 1,
            }],
            client_reference_id=user_id,
            metadata={"user_id": user_id},
            success_url=f"{YOUR_DOMAIN}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{YOUR_DOMAIN}/payment/cancel",
        )

        log_message("success", "Stripe checkout session created", data={"session_id": checkout_session.id}, api_name=api_name)

        app_response.set_response(
            AppConstants.CODE_SUCCESS,
            {"checkout_url": checkout_session.url},
            Messages.CHECKOUT_SESSION_CREATED,
            True
        )
        return app_response

    except Exception as e:
        log_message("error", f"Stripe session creation failed: {str(e)}", api_name=api_name)
        app_response.set_response(
            AppConstants.CODE_INTERNAL_SERVER_ERROR,
            {},
            str(e),
            False
        )
        return app_response








def subscription_status_service(user_id: str, db: Session):
    api_name = "subscription_status"
    try:
        user = db.execute(
            select(tables.users.c.subscription_tier)
            .where(tables.users.c.id == user_id)
        ).fetchone()

        if not user:
            app_response.set_response(
                AppConstants.DATA_NOT_FOUND,
                {},
                "User not found",
                Messages.FALSE
            )
            return app_response

        app_response.set_response(
            AppConstants.CODE_SUCCESS,
            {"subscription_tier": user.subscription_tier},
            "Subscription tier fetched",
            Messages.TRUE
        )
        return app_response
    except Exception as e:
        log_message("error", f"Subscription status failed: {str(e)}", api_name=api_name)
        app_response.set_response(
            AppConstants.CODE_INTERNAL_SERVER_ERROR,
            {},
            Messages.SOMETHING_WENT_WRONG,
            Messages.FALSE
        )
        return app_response

