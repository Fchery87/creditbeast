"""
Email API Router
Endpoints for email template management, email logs, and notification settings
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import logging
from math import ceil

from models.schemas import (
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplateResponse,
    EmailTemplateListResponse,
    EmailLogResponse,
    EmailLogListResponse,
    EmailAnalyticsResponse,
    NotificationSettingsUpdate,
    NotificationSettingsResponse,
    EmailSendRequest,
    EmailSendResponse,
    BaseResponse,
    ErrorResponse
)
from middleware.auth import get_current_user, get_organization_id
from services.database import DatabaseService
from services.email import email_service, send_onboarding_welcome_email, send_dispute_created_notification

logger = logging.getLogger(__name__)
router = APIRouter()
db = DatabaseService()


# ==========================================
# EMAIL TEMPLATE ENDPOINTS
# ==========================================

@router.get("/templates", response_model=EmailTemplateListResponse)
async def list_email_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    active_only: bool = True,
    current_user: dict = Depends(get_current_user),
    org_id: UUID = Depends(get_organization_id)
):
    """List all email templates for organization"""
    try:
        offset = (page - 1) * page_size
        
        # Build query
        query = "SELECT * FROM email_templates WHERE organization_id = $1"
        params = [str(org_id)]
        param_count = 1
        
        if category:
            param_count += 1
            query += f" AND category = ${param_count}"
            params.append(category)
        
        if active_only:
            query += " AND is_active = true"
        
        query += f" ORDER BY created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
        params.extend([page_size, offset])
        
        # Execute query
        templates = await db.fetch_all(query, *params)
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM email_templates WHERE organization_id = $1"
        count_params = [str(org_id)]
        
        if category:
            count_query += " AND category = $2"
            count_params.append(category)
        if active_only:
            count_query += " AND is_active = true"
        
        total = await db.fetch_val(count_query, *count_params)
        
        return EmailTemplateListResponse(
            items=templates,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=ceil(total / page_size)
        )
        
    except Exception as e:
        logger.error(f"Error listing email templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list email templates"
        )


@router.post("/templates", response_model=EmailTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_email_template(
    template_data: EmailTemplateCreate,
    current_user: dict = Depends(get_current_user),
    org_id: UUID = Depends(get_organization_id)
):
    """Create new email template"""
    try:
        # Extract variables from template
        variables_html = email_service.extract_variables(template_data.body_html)
        variables_subject = email_service.extract_variables(template_data.subject)
        all_variables = list(set(variables_html + variables_subject))
        
        query = """
            INSERT INTO email_templates (
                organization_id, name, template_key, description, category,
                subject, body_html, body_text, variables, is_active,
                created_by_user_id
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING *
        """
        
        template = await db.fetch_one(
            query,
            str(org_id),
            template_data.name,
            template_data.template_key,
            template_data.description,
            template_data.category,
            template_data.subject,
            template_data.body_html,
            template_data.body_text,
            all_variables,
            template_data.is_active,
            str(current_user['id'])
        )
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create template"
            )
        
        return template
        
    except Exception as e:
        logger.error(f"Error creating email template: {str(e)}")
        if "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Template with this key already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create email template"
        )


@router.get("/templates/{template_id}", response_model=EmailTemplateResponse)
async def get_email_template(
    template_id: UUID,
    current_user: dict = Depends(get_current_user),
    org_id: UUID = Depends(get_organization_id)
):
    """Get email template by ID"""
    try:
        query = "SELECT * FROM email_templates WHERE id = $1 AND organization_id = $2"
        template = await db.fetch_one(query, str(template_id), str(org_id))
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting email template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get email template"
        )


@router.patch("/templates/{template_id}", response_model=EmailTemplateResponse)
async def update_email_template(
    template_id: UUID,
    template_data: EmailTemplateUpdate,
    current_user: dict = Depends(get_current_user),
    org_id: UUID = Depends(get_organization_id)
):
    """Update email template"""
    try:
        # Check if template exists and is not a system template
        check_query = """
            SELECT is_system_template FROM email_templates 
            WHERE id = $1 AND organization_id = $2
        """
        existing = await db.fetch_one(check_query, str(template_id), str(org_id))
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        if existing['is_system_template']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify system template"
            )
        
        # Build update query dynamically
        updates = []
        params = []
        param_count = 0
        
        update_data = template_data.dict(exclude_unset=True)
        
        # Re-extract variables if template content changed
        if 'body_html' in update_data or 'subject' in update_data:
            # Get current template for variables
            current_template = await db.fetch_one(
                "SELECT subject, body_html FROM email_templates WHERE id = $1",
                str(template_id)
            )
            
            subject = update_data.get('subject', current_template['subject'])
            body_html = update_data.get('body_html', current_template['body_html'])
            
            variables_html = email_service.extract_variables(body_html)
            variables_subject = email_service.extract_variables(subject)
            all_variables = list(set(variables_html + variables_subject))
            update_data['variables'] = all_variables
        
        for field, value in update_data.items():
            param_count += 1
            updates.append(f"{field} = ${param_count}")
            params.append(value)
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        param_count += 1
        updates.append(f"last_modified_by_user_id = ${param_count}")
        params.append(str(current_user['id']))
        
        # Add WHERE clause parameters
        params.extend([str(template_id), str(org_id)])
        
        query = f"""
            UPDATE email_templates 
            SET {', '.join(updates)}
            WHERE id = ${param_count + 1} AND organization_id = ${param_count + 2}
            RETURNING *
        """
        
        template = await db.fetch_one(query, *params)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating email template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update email template"
        )


@router.delete("/templates/{template_id}", response_model=BaseResponse)
async def delete_email_template(
    template_id: UUID,
    current_user: dict = Depends(get_current_user),
    org_id: UUID = Depends(get_organization_id)
):
    """Delete email template (if not system template)"""
    try:
        # Check if it's a system template
        check_query = """
            SELECT is_system_template FROM email_templates 
            WHERE id = $1 AND organization_id = $2
        """
        existing = await db.fetch_one(check_query, str(template_id), str(org_id))
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        if existing['is_system_template']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete system template"
            )
        
        # Delete template
        query = "DELETE FROM email_templates WHERE id = $1 AND organization_id = $2"
        await db.execute(query, str(template_id), str(org_id))
        
        return BaseResponse(
            success=True,
            message="Template deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting email template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete email template"
        )


# ==========================================
# EMAIL LOG ENDPOINTS
# ==========================================

@router.get("/logs", response_model=EmailLogListResponse)
async def list_email_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    client_id: Optional[UUID] = None,
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    org_id: UUID = Depends(get_organization_id)
):
    """List email logs for organization"""
    try:
        offset = (page - 1) * page_size
        
        # Build query
        query = "SELECT * FROM email_logs WHERE organization_id = $1"
        params = [str(org_id)]
        param_count = 1
        
        if client_id:
            param_count += 1
            query += f" AND client_id = ${param_count}"
            params.append(str(client_id))
        
        if status_filter:
            param_count += 1
            query += f" AND status = ${param_count}"
            params.append(status_filter)
        
        query += f" ORDER BY created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
        params.extend([page_size, offset])
        
        logs = await db.fetch_all(query, *params)
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM email_logs WHERE organization_id = $1"
        count_params = [str(org_id)]
        
        if client_id:
            count_query += " AND client_id = $2"
            count_params.append(str(client_id))
        if status_filter:
            count_query += f" AND status = ${len(count_params) + 1}"
            count_params.append(status_filter)
        
        total = await db.fetch_val(count_query, *count_params)
        
        return EmailLogListResponse(
            items=logs,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=ceil(total / page_size)
        )
        
    except Exception as e:
        logger.error(f"Error listing email logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list email logs"
        )


@router.get("/analytics", response_model=EmailAnalyticsResponse)
async def get_email_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user),
    org_id: UUID = Depends(get_organization_id)
):
    """Get email analytics for organization"""
    try:
        query = """
            SELECT 
                COUNT(*) as total_sent,
                COUNT(*) FILTER (WHERE status = 'delivered') as total_delivered,
                COUNT(*) FILTER (WHERE status = 'bounced') as total_bounced,
                COUNT(*) FILTER (WHERE opened_at IS NOT NULL) as total_opened,
                COUNT(*) FILTER (WHERE first_clicked_at IS NOT NULL) as total_clicked
            FROM email_logs
            WHERE organization_id = $1 
            AND created_at >= NOW() - INTERVAL '%s days'
        """ % days
        
        stats = await db.fetch_one(query, str(org_id))
        
        if not stats or stats['total_sent'] == 0:
            return EmailAnalyticsResponse(
                total_sent=0,
                total_delivered=0,
                total_bounced=0,
                total_opened=0,
                total_clicked=0,
                delivery_rate=0.0,
                open_rate=0.0,
                click_rate=0.0,
                bounce_rate=0.0
            )
        
        total_sent = stats['total_sent']
        total_delivered = stats['total_delivered']
        total_bounced = stats['total_bounced']
        total_opened = stats['total_opened']
        total_clicked = stats['total_clicked']
        
        return EmailAnalyticsResponse(
            total_sent=total_sent,
            total_delivered=total_delivered,
            total_bounced=total_bounced,
            total_opened=total_opened,
            total_clicked=total_clicked,
            delivery_rate=round((total_delivered / total_sent) * 100, 2) if total_sent > 0 else 0.0,
            open_rate=round((total_opened / total_delivered) * 100, 2) if total_delivered > 0 else 0.0,
            click_rate=round((total_clicked / total_opened) * 100, 2) if total_opened > 0 else 0.0,
            bounce_rate=round((total_bounced / total_sent) * 100, 2) if total_sent > 0 else 0.0
        )
        
    except Exception as e:
        logger.error(f"Error getting email analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get email analytics"
        )


# ==========================================
# NOTIFICATION SETTINGS ENDPOINTS
# ==========================================

@router.get("/settings", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    current_user: dict = Depends(get_current_user),
    org_id: UUID = Depends(get_organization_id)
):
    """Get notification settings for organization"""
    try:
        query = "SELECT * FROM notification_settings WHERE organization_id = $1"
        settings = await db.fetch_one(query, str(org_id))
        
        # Create default settings if they don't exist
        if not settings:
            create_query = """
                INSERT INTO notification_settings (organization_id)
                VALUES ($1)
                RETURNING *
            """
            settings = await db.fetch_one(create_query, str(org_id))
        
        return settings
        
    except Exception as e:
        logger.error(f"Error getting notification settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notification settings"
        )


@router.patch("/settings", response_model=NotificationSettingsResponse)
async def update_notification_settings(
    settings_data: NotificationSettingsUpdate,
    current_user: dict = Depends(get_current_user),
    org_id: UUID = Depends(get_organization_id)
):
    """Update notification settings"""
    try:
        # Build update query
        updates = []
        params = []
        param_count = 0
        
        for field, value in settings_data.dict(exclude_unset=True).items():
            param_count += 1
            updates.append(f"{field} = ${param_count}")
            params.append(value)
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        params.append(str(org_id))
        
        query = f"""
            UPDATE notification_settings 
            SET {', '.join(updates)}
            WHERE organization_id = ${param_count + 1}
            RETURNING *
        """
        
        settings = await db.fetch_one(query, *params)
        
        if not settings:
            # Create settings if they don't exist
            create_query = """
                INSERT INTO notification_settings (organization_id)
                VALUES ($1)
                RETURNING *
            """
            settings = await db.fetch_one(create_query, str(org_id))
        
        return settings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notification settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification settings"
        )


# ==========================================
# EMAIL SENDING ENDPOINT
# ==========================================

@router.post("/send", response_model=EmailSendResponse)
async def send_email(
    email_data: EmailSendRequest,
    current_user: dict = Depends(get_current_user),
    org_id: UUID = Depends(get_organization_id)
):
    """Send email using template"""
    try:
        # Get template
        template_query = """
            SELECT * FROM email_templates 
            WHERE template_key = $1 AND organization_id = $2 AND is_active = true
        """
        template = await db.fetch_one(
            template_query,
            email_data.template_key,
            str(org_id)
        )
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found or inactive"
            )
        
        # Send email
        result = await email_service.send_template_email(
            to_email=email_data.to_email,
            template_html=template['body_html'],
            template_text=template['body_text'],
            subject=template['subject'],
            variables=email_data.variables,
            to_name=email_data.to_name,
            cc_emails=email_data.cc_emails,
            bcc_emails=email_data.bcc_emails
        )
        
        # Log email
        log_query = """
            INSERT INTO email_logs (
                organization_id, client_id, dispute_id, template_id, template_key,
                to_email, to_name, subject, body_html, body_text,
                provider, provider_message_id, status, sent_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            RETURNING id
        """
        
        log_id = await db.fetch_val(
            log_query,
            str(org_id),
            str(email_data.client_id) if email_data.client_id else None,
            str(email_data.dispute_id) if email_data.dispute_id else None,
            str(template['id']),
            email_data.template_key,
            email_data.to_email,
            email_data.to_name,
            template['subject'],
            template['body_html'],
            template['body_text'],
            'smtp',
            result.get('message_id'),
            result.get('status'),
            datetime.utcnow() if result.get('success') else None
        )
        
        return EmailSendResponse(
            success=result.get('success', False),
            message="Email sent successfully" if result.get('success') else result.get('error', 'Failed to send email'),
            email_log_id=log_id,
            status=result.get('status')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )
