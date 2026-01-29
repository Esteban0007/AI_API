"""
Billing and subscription management endpoints (Stripe integration ready).
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import logging

from ...core.security import validate_api_key
from ...db.session import get_db_session
from ...models.user import Plan, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


class PlanResponse(BaseModel):
    id: int
    name: str
    display_name: str
    price_monthly: float
    price_yearly: float
    searches_per_day: int
    searches_per_month: int
    max_documents: int
    max_api_keys: int
    features: list

    class Config:
        from_attributes = True


class SubscriptionResponse(BaseModel):
    plan_name: str
    plan_display_name: str
    status: str
    price_monthly: float
    next_billing_date: str | None


@router.get("/plans", response_model=List[PlanResponse])
async def list_plans(db: Session = Depends(get_db_session)) -> List[PlanResponse]:
    """
    List all available subscription plans.

    Public endpoint - no authentication required.
    """
    plans = db.query(Plan).filter(Plan.is_active == True).all()
    return [PlanResponse.model_validate(plan) for plan in plans]


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    user_context: dict = Depends(validate_api_key),
    db: Session = Depends(get_db_session),
) -> SubscriptionResponse:
    """
    Get current subscription details.
    """
    if user_context["user_id"] is None:
        return SubscriptionResponse(
            plan_name="free",
            plan_display_name="Free Plan",
            status="active",
            price_monthly=0.0,
            next_billing_date=None,
        )

    user = db.query(User).filter(User.id == user_context["user_id"]).first()
    plan = user.plan

    return SubscriptionResponse(
        plan_name=plan.name,
        plan_display_name=plan.display_name,
        status=user.subscription_status,
        price_monthly=plan.price_monthly,
        next_billing_date=(
            user.subscription_expires_at.isoformat()
            if user.subscription_expires_at
            else None
        ),
    )


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db_session)):
    """
    Stripe webhook endpoint for payment events.

    Handles:
    - checkout.session.completed
    - invoice.payment_succeeded
    - invoice.payment_failed
    - customer.subscription.updated
    - customer.subscription.deleted

    **Setup in Stripe Dashboard:**
    1. Go to Developers > Webhooks
    2. Add endpoint: https://readyapi.net/api/v1/billing/webhook/stripe
    3. Select events to listen for
    4. Save webhook signing secret in .env as STRIPE_WEBHOOK_SECRET
    """
    import os

    # Get Stripe signature
    signature = request.headers.get("stripe-signature")

    # Get webhook secret from environment
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if not webhook_secret:
        logger.error("STRIPE_WEBHOOK_SECRET not configured")
        raise HTTPException(status_code=500, detail="Webhook not configured")

    try:
        # Parse webhook payload
        payload = await request.body()

        # Verify webhook signature (when Stripe SDK is installed)
        # import stripe
        # event = stripe.Webhook.construct_event(
        #     payload, signature, webhook_secret
        # )

        # For now, just parse the JSON
        import json

        event = json.loads(payload)

        event_type = event.get("type")

        logger.info(f"Received Stripe webhook: {event_type}")

        # Handle different event types
        if event_type == "checkout.session.completed":
            await handle_checkout_completed(event, db)
        elif event_type == "invoice.payment_succeeded":
            await handle_payment_succeeded(event, db)
        elif event_type == "invoice.payment_failed":
            await handle_payment_failed(event, db)
        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(event, db)
        elif event_type == "customer.subscription.deleted":
            await handle_subscription_canceled(event, db)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


async def handle_checkout_completed(event: dict, db: Session):
    """Handle successful checkout."""
    session = event["data"]["object"]
    customer_id = session.get("customer")

    # Find user by Stripe customer ID
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

    if user:
        user.subscription_status = "active"
        db.commit()
        logger.info(f"Subscription activated for user {user.email}")


async def handle_payment_succeeded(event: dict, db: Session):
    """Handle successful payment."""
    from ...models.user import PaymentHistory
    from datetime import datetime

    invoice = event["data"]["object"]
    customer_id = invoice.get("customer")

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

    if user:
        # Record payment
        payment = PaymentHistory(
            user_id=user.id,
            stripe_payment_intent_id=invoice.get("payment_intent"),
            stripe_invoice_id=invoice.get("id"),
            amount=invoice.get("amount_paid") / 100,  # Convert from cents
            status="succeeded",
            paid_at=datetime.utcnow(),
        )
        db.add(payment)

        # Update subscription status
        user.subscription_status = "active"
        db.commit()

        logger.info(f"Payment recorded for user {user.email}: ${payment.amount}")


async def handle_payment_failed(event: dict, db: Session):
    """Handle failed payment."""
    invoice = event["data"]["object"]
    customer_id = invoice.get("customer")

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

    if user:
        user.subscription_status = "past_due"
        db.commit()
        logger.warning(f"Payment failed for user {user.email}")


async def handle_subscription_updated(event: dict, db: Session):
    """Handle subscription update."""
    subscription = event["data"]["object"]
    customer_id = subscription.get("customer")

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

    if user:
        user.subscription_status = subscription.get("status")
        db.commit()
        logger.info(f"Subscription updated for user {user.email}")


async def handle_subscription_canceled(event: dict, db: Session):
    """Handle subscription cancellation."""
    subscription = event["data"]["object"]
    customer_id = subscription.get("customer")

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

    if user:
        # Downgrade to free plan
        free_plan = db.query(Plan).filter(Plan.name == "free").first()
        user.plan_id = free_plan.id
        user.subscription_status = "canceled"
        db.commit()
        logger.info(
            f"Subscription canceled for user {user.email}, downgraded to free plan"
        )
