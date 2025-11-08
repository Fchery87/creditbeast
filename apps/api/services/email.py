"""
Email Service for CreditBeast
Handles email sending, template processing, and delivery tracking
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any, List
from datetime import datetime
import re
from jinja2 import Template
from config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending and tracking emails"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        self.from_name = settings.smtp_from_name
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        to_name: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Send an email via SMTP
        
        Returns:
            Dict with status and message_id
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = f"{to_name} <{to_email}>" if to_name else to_email
            message['Subject'] = subject
            
            if cc_emails:
                message['Cc'] = ', '.join(cc_emails)
            if bcc_emails:
                message['Bcc'] = ', '.join(bcc_emails)
            
            # Attach plain text and HTML parts
            if body_text:
                text_part = MIMEText(body_text, 'plain')
                message.attach(text_part)
            
            html_part = MIMEText(body_html, 'html')
            message.attach(html_part)
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                all_recipients = [to_email]
                if cc_emails:
                    all_recipients.extend(cc_emails)
                if bcc_emails:
                    all_recipients.extend(bcc_emails)
                
                server.sendmail(self.from_email, all_recipients, message.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            
            return {
                'success': True,
                'status': 'sent',
                'message_id': f"msg_{datetime.utcnow().timestamp()}",
                'sent_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {
                'success': False,
                'status': 'failed',
                'error': str(e)
            }
    
    def render_template(
        self,
        template_html: str,
        template_text: Optional[str],
        variables: Dict[str, Any]
    ) -> tuple[str, Optional[str]]:
        """
        Render email template with variables using Jinja2
        
        Args:
            template_html: HTML template with {{variable}} placeholders
            template_text: Plain text template
            variables: Dict of variable name/value pairs
            
        Returns:
            Tuple of (rendered_html, rendered_text)
        """
        try:
            # Render HTML
            html_template = Template(template_html)
            rendered_html = html_template.render(**variables)
            
            # Render text if provided
            rendered_text = None
            if template_text:
                text_template = Template(template_text)
                rendered_text = text_template.render(**variables)
            
            return rendered_html, rendered_text
            
        except Exception as e:
            logger.error(f"Failed to render template: {str(e)}")
            raise
    
    def extract_variables(self, template: str) -> List[str]:
        """
        Extract variable names from template
        
        Args:
            template: Template string with {{variable}} placeholders
            
        Returns:
            List of unique variable names
        """
        # Find all {{variable}} patterns
        pattern = r'\{\{\s*(\w+)\s*\}\}'
        matches = re.findall(pattern, template)
        return list(set(matches))
    
    async def send_template_email(
        self,
        to_email: str,
        template_html: str,
        template_text: Optional[str],
        subject: str,
        variables: Dict[str, Any],
        to_name: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Send email using template with variable substitution
        
        Args:
            to_email: Recipient email address
            template_html: HTML template
            template_text: Plain text template
            subject: Email subject (can also contain variables)
            variables: Variables to substitute in template
            to_name: Recipient name
            cc_emails: CC recipients
            bcc_emails: BCC recipients
            
        Returns:
            Dict with send status
        """
        try:
            # Render templates
            rendered_html, rendered_text = self.render_template(
                template_html, template_text, variables
            )
            
            # Render subject
            subject_template = Template(subject)
            rendered_subject = subject_template.render(**variables)
            
            # Send email
            result = await self.send_email(
                to_email=to_email,
                subject=rendered_subject,
                body_html=rendered_html,
                body_text=rendered_text,
                to_name=to_name,
                cc_emails=cc_emails,
                bcc_emails=bcc_emails
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send template email: {str(e)}")
            return {
                'success': False,
                'status': 'failed',
                'error': str(e)
            }
    
    def validate_email(self, email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


# Global email service instance
email_service = EmailService()


# ==========================================
# AUTOMATED EMAIL TRIGGERS
# ==========================================

async def send_onboarding_welcome_email(
    client_data: Dict[str, Any],
    organization_name: str
) -> Dict[str, Any]:
    """Send welcome email to new client"""
    variables = {
        'client_name': f"{client_data.get('first_name', '')} {client_data.get('last_name', '')}".strip(),
        'organization_name': organization_name
    }
    
    # This would fetch from database in production
    template_html = '''
    <h2>Welcome {{client_name}}!</h2>
    <p>We're excited to help you improve your credit score with {{organization_name}}.</p>
    <p>Our team will review your credit report and start disputing inaccurate items within 24 hours.</p>
    <p>You can track your progress anytime in your client portal.</p>
    <p>If you have any questions, feel free to reach out to us!</p>
    <br>
    <p>Best regards,<br>The {{organization_name}} Team</p>
    '''
    
    return await email_service.send_template_email(
        to_email=client_data['email'],
        template_html=template_html,
        template_text=None,
        subject='Welcome to {{organization_name}} - Let\'s Start Your Credit Repair Journey',
        variables=variables,
        to_name=variables['client_name']
    )


async def send_dispute_created_notification(
    client_data: Dict[str, Any],
    dispute_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Send notification when dispute is created"""
    variables = {
        'client_name': f"{client_data.get('first_name', '')} {client_data.get('last_name', '')}".strip(),
        'bureau': dispute_data.get('bureau', '').title(),
        'account_name': dispute_data.get('account_name', 'your account'),
        'dispute_type': dispute_data.get('dispute_type', '').replace('_', ' ').title()
    }
    
    template_html = '''
    <h2>Good News, {{client_name}}!</h2>
    <p>We've filed a new dispute with <strong>{{bureau}}</strong> regarding <strong>{{account_name}}</strong>.</p>
    <p><strong>Dispute Type:</strong> {{dispute_type}}</p>
    <p>We'll notify you as soon as we receive a response, typically within 30-45 days.</p>
    <p>You can view the status of this dispute in your client portal anytime.</p>
    <br>
    <p>Thank you for your trust!</p>
    '''
    
    return await email_service.send_template_email(
        to_email=client_data['email'],
        template_html=template_html,
        template_text=None,
        subject='New Dispute Filed on Your Behalf',
        variables=variables,
        to_name=variables['client_name']
    )


async def send_payment_reminder(
    client_data: Dict[str, Any],
    invoice_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Send payment reminder email"""
    amount = invoice_data.get('amount_cents', 0) / 100
    
    variables = {
        'client_name': f"{client_data.get('first_name', '')} {client_data.get('last_name', '')}".strip(),
        'amount': f"{amount:.2f}",
        'due_date': invoice_data.get('due_date', 'soon')
    }
    
    template_html = '''
    <h2>Payment Reminder</h2>
    <p>Hi {{client_name}},</p>
    <p>This is a friendly reminder that your payment of <strong>${{amount}}</strong> is due on <strong>{{due_date}}</strong>.</p>
    <p>Please make your payment to avoid service interruption.</p>
    <p>If you've already paid, please disregard this message.</p>
    <br>
    <p>Thank you!</p>
    '''
    
    return await email_service.send_template_email(
        to_email=client_data['email'],
        template_html=template_html,
        template_text=None,
        subject='Payment Reminder - Invoice Due',
        variables=variables,
        to_name=variables['client_name']
    )


async def send_admin_alert(
    admin_emails: List[str],
    alert_type: str,
    alert_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Send alert to admin team"""
    results = []
    
    for admin_email in admin_emails:
        result = await email_service.send_email(
            to_email=admin_email,
            subject=f"CreditBeast Alert: {alert_type}",
            body_html=f"<h3>Alert: {alert_type}</h3><pre>{alert_data}</pre>",
            body_text=f"Alert: {alert_type}\n\n{alert_data}"
        )
        results.append(result)
    
    return results
