"""
Billing router
Handles subscription management and payment operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from models.schemas import SubscriptionCreate, SubscriptionResponse, InvoiceResponse, BaseResponse
from middleware.auth import get_current_user
from config import settings
import stripe
import logging

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key

router = APIRouter()

@router.post("/subscribe", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new subscription"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        # Get organization from database
        from services.database import db
        org = await db.get_organization(org_id)
        
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Create or get Stripe customer
        stripe_customer_id = org.get("stripe_customer_id")
        if not stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.get("email"),
                name=org.get("name"),
                metadata={"organization_id": org_id}
            )
            stripe_customer_id = customer.id
            
            # Update organization with Stripe customer ID
            await db.admin_client.table("organizations")\
                .update({"stripe_customer_id": stripe_customer_id})\
                .eq("id", org_id)\
                .execute()
        
        # Define pricing based on plan
        plan_prices = {
            "starter": 9900,  # $99/month
            "professional": 29900,  # $299/month
            "enterprise": 99900  # $999/month
        }
        
        price_cents = plan_prices.get(subscription_data.plan_name.lower(), 9900)
        
        # Create Stripe subscription
        stripe_subscription = stripe.Subscription.create(
            customer=stripe_customer_id,
            items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"CreditBeast {subscription_data.plan_name}"
                    },
                    "unit_amount": price_cents,
                    "recurring": {
                        "interval": subscription_data.billing_interval
                    }
                }
            }],
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice.payment_intent"]
        )
        
        # Extract client_secret from payment intent
        client_secret = None
        if stripe_subscription.latest_invoice:
            if hasattr(stripe_subscription.latest_invoice, 'payment_intent'):
                payment_intent = stripe_subscription.latest_invoice.payment_intent
                if hasattr(payment_intent, 'client_secret'):
                    client_secret = payment_intent.client_secret
        
        # Save subscription to database
        subscription_record = await db.admin_client.table("billing_subscriptions").insert({
            "organization_id": org_id,
            "stripe_subscription_id": stripe_subscription.id,
            "stripe_customer_id": stripe_customer_id,
            "plan_name": subscription_data.plan_name,
            "plan_price_cents": price_cents,
            "billing_interval": subscription_data.billing_interval,
            "status": stripe_subscription.status,
            "current_period_start": stripe_subscription.current_period_start,
            "current_period_end": stripe_subscription.current_period_end
        }).execute()
        
        if not subscription_record.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create subscription"
            )
        
        # Return subscription data with client_secret
        response_data = subscription_record.data[0]
        response_data["client_secret"] = client_secret
        
        return response_data
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/subscription", response_model=SubscriptionResponse)
async def get_current_subscription(user: Dict[str, Any] = Depends(get_current_user)):
    """Get current organization's subscription"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        from services.database import db
        result = await db.admin_client.table("billing_subscriptions")\
            .select("*")\
            .eq("organization_id", org_id)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription found"
            )
        
        return SubscriptionResponse(**result.data[0])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/subscription/cancel", response_model=BaseResponse)
async def cancel_subscription(user: Dict[str, Any] = Depends(get_current_user)):
    """Cancel subscription at period end"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        from services.database import db
        # Get current subscription
        result = await db.admin_client.table("billing_subscriptions")\
            .select("*")\
            .eq("organization_id", org_id)\
            .eq("status", "active")\
            .limit(1)\
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        subscription = result.data[0]
        stripe_sub_id = subscription.get("stripe_subscription_id")
        
        if stripe_sub_id:
            # Cancel in Stripe
            stripe.Subscription.modify(
                stripe_sub_id,
                cancel_at_period_end=True
            )
        
        # Update database
        await db.admin_client.table("billing_subscriptions")\
            .update({"cancel_at_period_end": True})\
            .eq("id", subscription["id"])\
            .execute()
        
        return BaseResponse(
            success=True,
            message="Subscription will be canceled at the end of the current period"
        )
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
