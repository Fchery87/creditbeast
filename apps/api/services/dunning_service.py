"""
Dunning Service
Handles payment failure recovery and customer communication
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from services.database import db

logger = logging.getLogger(__name__)


class DunningService:
    """Service for managing payment failure recovery (dunning)"""

    # Dunning retry schedule (in days)
    RETRY_SCHEDULE = [3, 7, 14, 30]  # Days after payment failure

    # Maximum retry attempts before cancellation
    MAX_RETRY_ATTEMPTS = 4

    @staticmethod
    async def handle_payment_failure(
        payment_intent_id: str,
        customer_id: str,
        amount: int,
        failure_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle payment failure with dunning logic

        Args:
            payment_intent_id: Stripe payment intent ID
            customer_id: Stripe customer ID
            amount: Failed amount in cents
            failure_reason: Reason for payment failure

        Returns:
            Dunning action result
        """
        try:
            # Get invoice and organization details
            invoice_result = await db.admin_client.table("billing_invoices")\
                .select("*, organizations(*)")\
                .eq("stripe_payment_intent_id", payment_intent_id)\
                .limit(1)\
                .execute()

            if not invoice_result.data:
                logger.error(f"Invoice not found for payment intent: {payment_intent_id}")
                return {"success": False, "error": "Invoice not found"}

            invoice = invoice_result.data[0]
            organization = invoice.get("organizations", {})
            attempt_count = invoice.get("attempt_count", 0) + 1

            # Determine next action based on attempt count
            if attempt_count >= DunningService.MAX_RETRY_ATTEMPTS:
                # Maximum retries reached - suspend account
                await DunningService._suspend_account(organization.get("id"), invoice)
                return {
                    "success": True,
                    "action": "account_suspended",
                    "attempt_count": attempt_count
                }
            else:
                # Schedule retry
                next_retry_days = DunningService.RETRY_SCHEDULE[min(
                    attempt_count - 1,
                    len(DunningService.RETRY_SCHEDULE) - 1
                )]
                next_retry_date = datetime.utcnow() + timedelta(days=next_retry_days)

                # Update invoice with retry information
                await db.admin_client.table("billing_invoices")\
                    .update({
                        "status": "payment_failed",
                        "attempt_count": attempt_count,
                        "next_retry_at": next_retry_date.isoformat(),
                        "last_failure_reason": failure_reason or "Unknown"
                    })\
                    .eq("stripe_payment_intent_id", payment_intent_id)\
                    .execute()

                # Send dunning email
                await DunningService._send_dunning_email(
                    organization=organization,
                    invoice=invoice,
                    attempt_count=attempt_count,
                    next_retry_date=next_retry_date,
                    failure_reason=failure_reason
                )

                return {
                    "success": True,
                    "action": "retry_scheduled",
                    "attempt_count": attempt_count,
                    "next_retry_date": next_retry_date.isoformat(),
                    "retry_days": next_retry_days
                }

        except Exception as e:
            logger.error(f"Error in dunning process: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    async def _suspend_account(organization_id: str, invoice: Dict[str, Any]):
        """
        Suspend account after maximum retry attempts

        Args:
            organization_id: Organization ID to suspend
            invoice: Invoice data
        """
        try:
            # Update organization status
            await db.admin_client.table("organizations")\
                .update({
                    "subscription_status": "suspended",
                    "suspended_at": datetime.utcnow().isoformat(),
                    "suspension_reason": "payment_failure"
                })\
                .eq("id", organization_id)\
                .execute()

            # Cancel subscription in database
            await db.admin_client.table("billing_subscriptions")\
                .update({
                    "status": "suspended",
                    "suspended_at": datetime.utcnow().isoformat()
                })\
                .eq("organization_id", organization_id)\
                .execute()

            # Send account suspension email
            await DunningService._send_suspension_email(organization_id, invoice)

            logger.info(f"Account suspended for organization: {organization_id}")

        except Exception as e:
            logger.error(f"Error suspending account: {e}")
            raise

    @staticmethod
    async def _send_dunning_email(
        organization: Dict[str, Any],
        invoice: Dict[str, Any],
        attempt_count: int,
        next_retry_date: datetime,
        failure_reason: Optional[str] = None
    ):
        """
        Send payment failure notification email

        Args:
            organization: Organization data
            invoice: Invoice data
            attempt_count: Current retry attempt number
            next_retry_date: Date of next retry
            failure_reason: Reason for payment failure
        """
        try:
            # Get organization owner/admin email
            users_result = await db.admin_client.table("users")\
                .select("email")\
                .eq("organization_id", organization.get("id"))\
                .eq("role", "owner")\
                .limit(1)\
                .execute()

            if not users_result.data:
                logger.warning(f"No owner found for organization: {organization.get('id')}")
                return

            admin_email = users_result.data[0].get("email")
            if not admin_email:
                return

            # Prepare email content based on attempt count
            if attempt_count == 1:
                subject = "Payment Failed - Action Required"
                urgency = "We noticed your recent payment didn't go through."
            elif attempt_count == 2:
                subject = "Second Notice: Payment Failed"
                urgency = "This is the second time we've attempted to process your payment."
            elif attempt_count == 3:
                subject = "Final Notice: Payment Failed - Account at Risk"
                urgency = "This is your final notice. Your account will be suspended if payment is not resolved."
            else:
                subject = "Final Warning: Payment Failed"
                urgency = "Your account will be suspended after the next failed payment attempt."

            amount_formatted = f"${invoice.get('amount_due_cents', 0) / 100:.2f}"

            email_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #d32f2f;">Payment Failed</h2>
                <p>{urgency}</p>

                <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-left: 4px solid #d32f2f;">
                    <strong>Invoice Details:</strong><br>
                    Amount Due: {amount_formatted}<br>
                    Attempt: {attempt_count} of {DunningService.MAX_RETRY_ATTEMPTS}<br>
                    Next Retry: {next_retry_date.strftime('%B %d, %Y')}
                    {f'<br>Reason: {failure_reason}' if failure_reason else ''}
                </div>

                <p><strong>What you need to do:</strong></p>
                <ol>
                    <li>Log in to your CreditBeast dashboard</li>
                    <li>Navigate to Billing Settings</li>
                    <li>Update your payment method or retry the payment</li>
                </ol>

                <p style="color: #d32f2f;"><strong>Important:</strong> If payment is not resolved, your account will be suspended after {DunningService.MAX_RETRY_ATTEMPTS} failed attempts.</p>

                <p>If you have questions or need assistance, please contact our support team.</p>

                <p>Thank you,<br>The CreditBeast Team</p>
            </body>
            </html>
            """

            # Send email via email service
            from services.email_service import email_service
            await email_service.send_email(
                to_email=admin_email,
                subject=subject,
                body_html=email_body,
                organization_id=organization.get("id")
            )

            logger.info(f"Dunning email sent to {admin_email} (attempt {attempt_count})")

        except Exception as e:
            logger.error(f"Error sending dunning email: {e}")
            # Don't raise - email failure shouldn't break the dunning process

    @staticmethod
    async def _send_suspension_email(organization_id: str, invoice: Dict[str, Any]):
        """
        Send account suspension notification

        Args:
            organization_id: Organization ID
            invoice: Invoice data
        """
        try:
            # Get organization owner email
            users_result = await db.admin_client.table("users")\
                .select("email")\
                .eq("organization_id", organization_id)\
                .eq("role", "owner")\
                .limit(1)\
                .execute()

            if not users_result.data:
                return

            admin_email = users_result.data[0].get("email")
            if not admin_email:
                return

            amount_formatted = f"${invoice.get('amount_due_cents', 0) / 100:.2f}"

            email_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #d32f2f;">Account Suspended</h2>
                <p>Your CreditBeast account has been suspended due to payment failure.</p>

                <div style="background-color: #ffebee; padding: 15px; margin: 20px 0; border-left: 4px solid #d32f2f;">
                    <strong>Outstanding Invoice:</strong><br>
                    Amount Due: {amount_formatted}<br>
                    Status: Payment Failed After {DunningService.MAX_RETRY_ATTEMPTS} Attempts
                </div>

                <p><strong>To reactivate your account:</strong></p>
                <ol>
                    <li>Log in to your CreditBeast dashboard</li>
                    <li>Navigate to Billing Settings</li>
                    <li>Update your payment method and clear the outstanding balance</li>
                    <li>Your account will be automatically reactivated once payment is received</li>
                </ol>

                <p style="color: #666;"><em>While your account is suspended, you will not be able to access your client data or generate dispute letters.</em></p>

                <p>If you need assistance, please contact our support team immediately.</p>

                <p>Thank you,<br>The CreditBeast Team</p>
            </body>
            </html>
            """

            # Send email
            from services.email_service import email_service
            await email_service.send_email(
                to_email=admin_email,
                subject="Account Suspended - Payment Required",
                body_html=email_body,
                organization_id=organization_id
            )

            logger.info(f"Suspension email sent to {admin_email}")

        except Exception as e:
            logger.error(f"Error sending suspension email: {e}")

    @staticmethod
    async def check_and_process_retries():
        """
        Background job to check and process scheduled payment retries
        This should be called by a cron job or scheduler
        """
        try:
            # Find invoices due for retry
            now = datetime.utcnow()

            invoices_result = await db.admin_client.table("billing_invoices")\
                .select("*")\
                .eq("status", "payment_failed")\
                .lte("next_retry_at", now.isoformat())\
                .execute()

            for invoice in invoices_result.data:
                try:
                    # Attempt to retry payment via Stripe
                    import stripe
                    from config import settings

                    stripe.api_key = settings.stripe_secret_key

                    payment_intent = stripe.PaymentIntent.retrieve(
                        invoice["stripe_payment_intent_id"]
                    )

                    # Retry the payment
                    if payment_intent.status == "requires_payment_method":
                        # Need to retry with existing payment method
                        stripe.PaymentIntent.confirm(invoice["stripe_payment_intent_id"])
                        logger.info(f"Retry initiated for invoice: {invoice['id']}")

                except Exception as e:
                    logger.error(f"Error retrying payment for invoice {invoice['id']}: {e}")

        except Exception as e:
            logger.error(f"Error in retry processing: {e}")


# Singleton instance
dunning_service = DunningService()
