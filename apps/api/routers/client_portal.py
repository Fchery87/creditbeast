"""
Client Portal API Router
Client self-service interface endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from typing import List, Optional
import logging
import os
import uuid
from datetime import datetime

from models.client_portal import (
    ClientPortalLoginRequest, ClientPortalLoginResponse, DocumentUploadRequest,
    CommunicationRequest, ClientSettingsUpdate, ClientPortalDashboardResponse,
    ClientPortalDocumentsResponse, ClientPortalDisputesResponse,
    ClientPortalCommunicationsResponse, ClientPortalResponse
)
from services.client_portal import client_portal_service
from middleware.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", summary="Client Portal Login")
async def client_portal_login(login_request: ClientPortalLoginRequest):
    """Authenticate client and return dashboard data"""
    try:
        user = await client_portal_service.authenticate_client(
            login_request.email, 
            login_request.password
        )
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        dashboard = await client_portal_service.get_client_dashboard(user.client_id)
        
        return ClientPortalLoginResponse(
            success=True,
            access_token=f"mock_token_{user.client_id}",
            refresh_token=f"mock_refresh_{user.client_id}",
            user=user,
            dashboard=dashboard,
            message="Login successful"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in client login: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", summary="Get Client Dashboard")
async def get_client_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get complete client dashboard data"""
    try:
        client_id = current_user.get("client_id")
        if not client_id:
            raise HTTPException(status_code=400, detail="Client ID required")
        
        dashboard = await client_portal_service.get_client_dashboard(client_id)
        
        return ClientPortalDashboardResponse(
            success=True,
            dashboard=dashboard,
            message="Dashboard data retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching client dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/disputes", summary="Get Client Disputes")
async def get_client_disputes(
    current_user: dict = Depends(get_current_user)
):
    """Get all disputes for the client"""
    try:
        client_id = current_user.get("client_id")
        if not client_id:
            raise HTTPException(status_code=400, detail="Client ID required")
        
        disputes = await client_portal_service.get_client_disputes(client_id)
        
        active_count = len([d for d in disputes if d.status.value in ['in_progress', 'waiting_response']])
        
        return ClientPortalDisputesResponse(
            success=True,
            disputes=disputes,
            total_count=len(disputes),
            active_count=active_count,
            message="Disputes retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching client disputes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", summary="Get Client Documents")
async def get_client_documents(
    current_user: dict = Depends(get_current_user)
):
    """Get all documents for the client"""
    try:
        client_id = current_user.get("client_id")
        if not client_id:
            raise HTTPException(status_code=400, detail="Client ID required")
        
        documents = await client_portal_service.get_client_documents(client_id)
        
        return ClientPortalDocumentsResponse(
            success=True,
            documents=documents,
            total_count=len(documents),
            message="Documents retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching client documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/upload", summary="Upload Document")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = "other",
    description: Optional[str] = None,
    is_confidential: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """Upload document for client"""
    try:
        client_id = current_user.get("client_id")
        if not client_id:
            raise HTTPException(status_code=400, detail="Client ID required")
        
        # Validate file type
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Validate file size (5MB limit)
        if file.size and file.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 5MB)")
        
        # Read file data
        file_data = await file.read()
        
        # Create upload request
        upload_request = DocumentUploadRequest(
            document_type=document_type,
            description=description,
            is_confidential=is_confidential
        )
        
        # Process upload
        document = await client_portal_service.upload_document(
            client_id, 
            file.filename, 
            file_data, 
            upload_request
        )
        
        return ClientPortalResponse(
            success=True,
            data=document,
            message="Document uploaded successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/communications", summary="Get Client Communications")
async def get_client_communications(
    current_user: dict = Depends(get_current_user)
):
    """Get communications for the client"""
    try:
        client_id = current_user.get("client_id")
        if not client_id:
            raise HTTPException(status_code=400, detail="Client ID required")
        
        communications = await client_portal_service.get_recent_communications(client_id)
        unread_count = len([c for c in communications if not c.is_read])
        
        return ClientPortalCommunicationsResponse(
            success=True,
            communications=communications,
            unread_count=unread_count,
            message="Communications retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching communications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/communications/send", summary="Send Message")
async def send_message(
    message_request: CommunicationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send message from client to professional"""
    try:
        client_id = current_user.get("client_id")
        if not client_id:
            raise HTTPException(status_code=400, detail="Client ID required")
        
        communication = await client_portal_service.send_message(client_id, message_request)
        
        return ClientPortalResponse(
            success=True,
            data=communication,
            message="Message sent successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/communications/{communication_id}/read", summary="Mark Communication as Read")
async def mark_communication_read(
    communication_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a communication as read"""
    try:
        client_id = current_user.get("client_id")
        if not client_id:
            raise HTTPException(status_code=400, detail="Client ID required")
        
        success = await client_portal_service.mark_communication_read(client_id, communication_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Communication not found")
        
        return ClientPortalResponse(
            success=True,
            message="Communication marked as read"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking communication as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings", summary="Get Client Settings")
async def get_client_settings(
    current_user: dict = Depends(get_current_user)
):
    """Get client portal settings"""
    try:
        client_id = current_user.get("client_id")
        if not client_id:
            raise HTTPException(status_code=400, detail="Client ID required")
        
        user = await client_portal_service.get_client_user(client_id)
        
        # Extract settings from user (in real implementation, would be separate)
        settings = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "email_notifications": True,
            "sms_notifications": False,
            "language": "en",
            "timezone": "UTC"
        }
        
        return ClientPortalResponse(
            success=True,
            data=settings,
            message="Settings retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching client settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings", summary="Update Client Settings")
async def update_client_settings(
    settings: ClientSettingsUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update client portal settings"""
    try:
        client_id = current_user.get("client_id")
        if not client_id:
            raise HTTPException(status_code=400, detail="Client ID required")
        
        updated_user = await client_portal_service.update_client_settings(client_id, settings)
        
        return ClientPortalResponse(
            success=True,
            data={
                "first_name": updated_user.first_name,
                "last_name": updated_user.last_name,
                "phone": updated_user.phone
            },
            message="Settings updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}/download", summary="Download Document")
async def download_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Download a document (placeholder - would implement actual file serving)"""
    try:
        client_id = current_user.get("client_id")
        if not client_id:
            raise HTTPException(status_code=400, detail="Client ID required")
        
        # In real implementation, would verify document belongs to client and serve file
        # For now, return a mock response
        return {
            "success": True,
            "download_url": f"/mock-download/{document_id}",
            "message": "Document download link generated"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating download link: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress", summary="Get Client Progress Summary")
async def get_client_progress(
    current_user: dict = Depends(get_current_user)
):
    """Get client's progress summary"""
    try:
        client_id = current_user.get("client_id")
        if not client_id:
            raise HTTPException(status_code=400, detail="Client ID required")
        
        progress = await client_portal_service.get_client_progress(client_id)
        
        return ClientPortalResponse(
            success=True,
            data=progress,
            message="Progress retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching client progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout", summary="Client Portal Logout")
async def client_portal_logout(
    current_user: dict = Depends(get_current_user)
):
    """Logout client from portal"""
    try:
        # In real implementation, would invalidate tokens, etc.
        return ClientPortalResponse(
            success=True,
            message="Logged out successfully"
        )
    except Exception as e:
        logger.error(f"Error in client logout: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Public client portal routes (no authentication required for signup)
@router.post("/register", summary="Register New Client Account")
async def register_client_account(
    email: str,
    first_name: str,
    last_name: str,
    phone: Optional[str] = None
):
    """Register a new client account (in real implementation)"""
    try:
        # Mock registration - in real implementation, would create account and send welcome email
        client_id = f"client_{uuid.uuid4().hex[:8]}"
        
        return {
            "success": True,
            "client_id": client_id,
            "message": "Account created successfully. Please check your email to verify your account."
        }
    except Exception as e:
        logger.error(f"Error registering client: {e}")
        raise HTTPException(status_code=500, detail=str(e))