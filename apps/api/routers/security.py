"""
Security API Router
Enhanced security features: MFA, SSO, audit logging, incidents, and session management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from services.security import (
    MFAService,
    SSOService,
    AuditLogService,
    SecurityIncidentService,
    SessionManagementService
)
from services.database import db
from middleware.auth import get_current_user
from models.schemas import (
    MFAConfig, SSOSettings, SecurityIncident, SessionConfig
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
mfa_service = MFAService(db)
sso_service = SSOService(db)
audit_service = AuditLogService(db)
incident_service = SecurityIncidentService(db)
session_service = SessionManagementService(db)

# ==========================================
# MFA ENDPOINTS
# ==========================================

@router.post("/mfa/setup")
async def setup_mfa(
    mfa_data: Dict[str, Any],
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Set up MFA for user"""
    org_id = user.get("organization_id")
    user_id = user.get("user_id")
    
    if not org_id or not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        mfa_method = mfa_data.get("mfa_method")
        result = await mfa_service.setup_mfa(user_id, org_id, mfa_method)
        return {
            "success": True,
            "message": "MFA setup initiated",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error setting up MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/mfa/verify")
async def verify_mfa_token(
    verification_data: Dict[str, Any],
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Verify MFA token or backup code"""
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID required"
        )
    
    try:
        token = verification_data.get("token")
        backup_code = verification_data.get("backup_code")
        
        result = await mfa_service.verify_mfa_token(user_id, token, backup_code)
        return {
            "success": result.get("verified", False),
            "message": "MFA verification completed",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error verifying MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# SSO ENDPOINTS
# ==========================================

@router.post("/sso/configure")
async def configure_sso(
    sso_config: Dict[str, Any],
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Configure SSO for organization"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    # Check if user is admin
    if user.get("role") not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can configure SSO"
        )
    
    try:
        result = await sso_service.configure_sso(org_id, sso_config)
        return {
            "success": True,
            "message": "SSO configuration saved",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error configuring SSO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/sso/callback")
async def sso_callback(
    sso_response: Dict[str, Any],
    organization_id: str
):
    """Process SSO callback"""
    try:
        result = await sso_service.process_sso_callback(organization_id, sso_response)
        
        if result.get("authenticated"):
            return {
                "success": True,
                "message": "SSO authentication successful",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.get("error", "SSO authentication failed")
            )
    except Exception as e:
        logger.error(f"Error processing SSO callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# AUDIT LOGGING ENDPOINTS
# ==========================================

@router.post("/audit/log-event")
async def log_security_event(
    event_data: Dict[str, Any],
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Log security event"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        # Add context to event
        event_data.update({
            "user_id": user.get("user_id"),
            "organization_id": org_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        result = await audit_service.log_security_event(org_id, event_data)
        return {
            "success": True,
            "message": "Security event logged",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error logging security event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/audit/logs")
async def get_audit_logs(
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    user_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    ip_address: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get audit logs with filtering"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        filters = {
            "event_type": event_type,
            "severity": severity,
            "user_id": user_id,
            "date_from": date_from,
            "date_to": date_to,
            "ip_address": ip_address,
            "page": page,
            "page_size": page_size
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        result = await audit_service.get_audit_logs(org_id, filters)
        return {
            "success": True,
            "message": "Audit logs retrieved",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# SECURITY INCIDENT ENDPOINTS
# ==========================================

@router.post("/incidents")
async def create_security_incident(
    incident_data: Dict[str, Any],
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Create new security incident"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        # Add reporter info
        incident_data["reported_by"] = user.get("user_id")
        
        result = await incident_service.create_incident(org_id, incident_data)
        return {
            "success": True,
            "message": "Security incident created",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error creating security incident: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/incidents")
async def get_security_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    incident_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get security incidents with filtering"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        filters = {
            "status": status,
            "severity": severity,
            "incident_type": incident_type,
            "date_from": date_from,
            "date_to": date_to,
            "page": page,
            "page_size": page_size
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        result = await incident_service.get_incidents(org_id, filters)
        return {
            "success": True,
            "message": "Security incidents retrieved",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error getting security incidents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/incidents/{incident_id}/status")
async def update_incident_status(
    incident_id: str,
    status_data: Dict[str, Any],
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Update incident status"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        # Add updater info
        status_data["changed_by"] = user.get("user_id")
        
        result = await incident_service.update_incident_status(incident_id, org_id, status_data)
        return {
            "success": True,
            "message": "Incident status updated",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error updating incident status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# SESSION MANAGEMENT ENDPOINTS
# ==========================================

@router.post("/sessions")
async def create_user_session(
    session_data: Dict[str, Any],
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Create new user session"""
    org_id = user.get("organization_id")
    user_id = user.get("user_id")
    
    if not org_id or not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        result = await session_service.create_session(user_id, org_id, session_data)
        return {
            "success": True,
            "message": "Session created",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/sessions/validate")
async def validate_session(
    validation_data: Dict[str, Any],
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Validate session token"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        session_token = validation_data.get("session_token")
        result = await session_service.validate_session(session_token, org_id)
        return {
            "success": result.get("valid", False),
            "message": "Session validation completed",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error validating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/sessions/{session_token}")
async def terminate_session(
    session_token: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Terminate session"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        result = await session_service.terminate_session(session_token, org_id)
        return {
            "success": result.get("terminated", False),
            "message": "Session termination completed",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error terminating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/sessions/cleanup")
async def cleanup_expired_sessions(
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Clean up expired sessions"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    # Check if user is admin
    if user.get("role") not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can cleanup sessions"
        )
    
    try:
        result = await session_service.cleanup_expired_sessions(org_id)
        return {
            "success": True,
            "message": "Session cleanup completed",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# SECURITY CONFIGURATION ENDPOINTS
# ==========================================

@router.get("/security/config")
async def get_security_config(
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get security configuration for organization"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        # Get MFA config
        mfa_config = await _get_org_mfa_config(org_id)
        
        # Get SSO config
        sso_config = await _get_org_sso_config(org_id)
        
        # Get session config
        session_config = await _get_org_session_config(org_id)
        
        return {
            "success": True,
            "data": {
                "mfa": mfa_config,
                "sso": sso_config,
                "session": session_config
            }
        }
    except Exception as e:
        logger.error(f"Error getting security config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# HELPER FUNCTIONS
# ==========================================

async def _get_org_mfa_config(organization_id: str) -> Optional[Dict]:
    """Get MFA configuration for organization"""
    result = await db.table("mfa_configs").select("*")\
        .eq("organization_id", organization_id)\
        .eq("is_enabled", True)\
        .execute()
    return result.data[0] if result.data else None

async def _get_org_sso_config(organization_id: str) -> Optional[Dict]:
    """Get SSO configuration for organization"""
    result = await db.table("sso_settings").select("*")\
        .eq("organization_id", organization_id)\
        .execute()
    return result.data[0] if result.data else None

async def _get_org_session_config(organization_id: str) -> Optional[Dict]:
    """Get session configuration for organization"""
    result = await db.table("session_configs").select("*")\
        .eq("organization_id", organization_id)\
        .execute()
    return result.data[0] if result.data else None