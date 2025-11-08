"""
Webhooks router
Handles webhook events from external services (Stripe, CloudMail, etc.)
"""

from fastapi import APIRouter, Request, HTTPException, status, Header
from typing import Optional
from config import settings
import stripe
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature")
):
    """Handle Stripe webhook events"""
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature"
        )
    
    try:
        # Get raw body
        body = await request.body()
        
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            body,
            stripe_signature,
            settings.stripe_webhook_secret
        )
        
        logger.info(f"Received Stripe webhook: {event['type']}")
        
        # Handle different event types
        if event["type"] == "payment_intent.succeeded":
            await handle_payment_success(event["data"]["object"])
        
        elif event["type"] == "payment_intent.payment_failed":
            await handle_payment_failure(event["data"]["object"])
        
        elif event["type"] == "invoice.payment_succeeded":
            await handle_invoice_paid(event["data"]["object"])
        
        elif event["type"] == "invoice.payment_failed":
            await handle_invoice_failed(event["data"]["object"])
        
        elif event["type"] == "customer.subscription.updated":
            await handle_subscription_updated(event["data"]["object"])
        
        elif event["type"] == "customer.subscription.deleted":
            await handle_subscription_deleted(event["data"]["object"])
        
        return {"success": True, "message": "Webhook processed"}
    
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid Stripe signature: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# WEBHOOK EVENT HANDLERS
# ==========================================

async def handle_payment_success(payment_intent):
    """Handle successful payment"""
    logger.info(f"Payment succeeded: {payment_intent['id']}")
    
    from services.database import db
    
    # Update invoice status
    await db.admin_client.table("billing_invoices")\
        .update({
            "status": "paid",
            "amount_paid_cents": payment_intent["amount"],
            "paid_at": "now()"
        })\
        .eq("stripe_payment_intent_id", payment_intent["id"])\
        .execute()

async def handle_payment_failure(payment_intent):
    """Handle failed payment"""
    logger.warning(f"Payment failed: {payment_intent['id']}")

    from services.dunning_service import dunning_service

    # Execute dunning logic
    result = await dunning_service.handle_payment_failure(
        payment_intent_id=payment_intent["id"],
        customer_id=payment_intent.get("customer"),
        amount=payment_intent.get("amount", 0),
        failure_reason=payment_intent.get("last_payment_error", {}).get("message")
    )

    if result.get("success"):
        action = result.get("action")
        if action == "account_suspended":
            logger.warning(f"Account suspended after {result.get('attempt_count')} failed attempts")
        elif action == "retry_scheduled":
            logger.info(f"Payment retry scheduled for {result.get('next_retry_date')}")
    else:
        logger.error(f"Dunning process failed: {result.get('error')}")

async def handle_invoice_paid(invoice):
    """Handle paid invoice"""
    logger.info(f"Invoice paid: {invoice['id']}")
    
    from services.database import db
    from datetime import datetime
    
    await db.admin_client.table("billing_invoices")\
        .update({
            "status": "paid",
            "amount_paid_cents": invoice["amount_paid"],
            "paid_at": datetime.utcnow().isoformat()
        })\
        .eq("stripe_invoice_id", invoice["id"])\
        .execute()

async def handle_invoice_failed(invoice):
    """Handle failed invoice"""
    logger.warning(f"Invoice failed: {invoice['id']}")
    
    from services.database import db
    from datetime import datetime, timedelta
    
    # Increment attempt count and schedule next retry
    next_retry = datetime.utcnow() + timedelta(days=3)
    
    await db.admin_client.table("billing_invoices")\
        .update({
            "status": "open",
            "attempt_count": "attempt_count + 1",
            "next_retry_at": next_retry.isoformat()
        })\
        .eq("stripe_invoice_id", invoice["id"])\
        .execute()

async def handle_subscription_updated(subscription):
    """Handle subscription update"""
    logger.info(f"Subscription updated: {subscription['id']}")
    
    from services.database import db
    
    await db.admin_client.table("billing_subscriptions")\
        .update({
            "status": subscription["status"],
            "current_period_start": subscription["current_period_start"],
            "current_period_end": subscription["current_period_end"],
            "cancel_at_period_end": subscription.get("cancel_at_period_end", False)
        })\
        .eq("stripe_subscription_id", subscription["id"])\
        .execute()

async def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    logger.info(f"Subscription deleted: {subscription['id']}")
    
    from services.database import db
    from datetime import datetime
    
    await db.admin_client.table("billing_subscriptions")\
        .update({
            "status": "canceled",
            "canceled_at": datetime.utcnow().isoformat()
        })\
        .eq("stripe_subscription_id", subscription["id"])\
        .execute()
    
    # Update organization subscription status
    org_result = await db.admin_client.table("billing_subscriptions")\
        .select("organization_id")\
        .eq("stripe_subscription_id", subscription["id"])\
        .limit(1)\
        .execute()
    
    if org_result.data:
        org_id = org_result.data[0]["organization_id"]
        await db.admin_client.table("organizations")\
            .update({"subscription_status": "canceled"})\
            .eq("id", org_id)\
            .execute()
