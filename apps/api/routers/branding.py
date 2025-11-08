"""
Branding API Router
White-label and customization endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List
import logging
from models.branding import (
    BrandingUpdateRequest, BrandingPreviewRequest, BrandingValidationRequest,
    OrganizationBranding, BrandingTemplate, BrandingValidationResponse
)
from services.branding import branding_service
from middleware.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/branding", summary="Get Organization Branding")
async def get_organization_branding(
    current_user: dict = Depends(get_current_user)
):
    """Get current branding configuration for organization"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        branding = await branding_service.get_organization_branding(org_id)
        return {
            "success": True,
            "data": branding.dict()
        }
    except Exception as e:
        logger.error(f"Error fetching branding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/branding", summary="Update Organization Branding")
async def update_organization_branding(
    updates: BrandingUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update organization branding configuration"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        updated_branding = await branding_service.update_organization_branding(org_id, updates)
        return {
            "success": True,
            "data": updated_branding.dict(),
            "message": "Branding updated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating branding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/branding/preview", summary="Preview Branding Changes")
async def preview_branding_changes(
    request: BrandingPreviewRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate preview of branding changes"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        preview = await branding_service.preview_branding_changes(org_id, request)
        return {
            "success": True,
            **preview
        }
    except Exception as e:
        logger.error(f"Error generating preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/branding/validate", summary="Validate Branding Updates")
async def validate_branding_updates(
    request: BrandingValidationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Validate branding updates for correctness"""
    try:
        validation_response = await branding_service.validate_branding_updates(request)
        return {
            "success": True,
            **validation_response.dict()
        }
    except Exception as e:
        logger.error(f"Error validating branding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates", summary="Get Branding Templates")
async def get_branding_templates():
    """Get available branding templates"""
    try:
        templates = await branding_service.get_branding_templates()
        return {
            "success": True,
            "data": [template.dict() for template in templates]
        }
    except Exception as e:
        logger.error(f"Error fetching templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates/{template_id}/apply", summary="Apply Branding Template")
async def apply_branding_template(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Apply a branding template to organization"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        updated_branding = await branding_service.apply_branding_template(org_id, template_id)
        return {
            "success": True,
            "data": updated_branding.dict(),
            "message": f"Template '{template_id}' applied successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error applying template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/custom-css", summary="Generate Custom CSS")
async def generate_custom_css(
    current_user: dict = Depends(get_current_user)
):
    """Generate custom CSS from current branding configuration"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        branding = await branding_service.get_organization_branding(org_id)
        custom_css = await branding_service.generate_custom_css(branding)
        
        return {
            "success": True,
            "data": {
                "css": custom_css,
                "branding": branding.dict()
            }
        }
    except Exception as e:
        logger.error(f"Error generating custom CSS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/branding/{branding_id}", summary="Get Specific Branding Configuration")
async def get_branding_by_id(
    branding_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get branding configuration by ID (for template preview)"""
    try:
        # This would look up branding by ID in a real implementation
        # For now, return default branding
        default_branding = OrganizationBranding(
            id=branding_id,
            organization_id=current_user.get("org_id", ""),
            company_name="Preview Branding",
            created_at=branding_service.get_organization_branding("default").created_at,
            updated_at=branding_service.get_organization_branding("default").updated_at
        )
        
        return {
            "success": True,
            "data": default_branding.dict()
        }
    except Exception as e:
        logger.error(f"Error fetching branding by ID: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/branding", summary="Reset to Default Branding")
async def reset_branding(
    current_user: dict = Depends(get_current_user)
):
    """Reset organization branding to default configuration"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        # Create default branding
        default_branding = OrganizationBranding(
            id=f"branding_{org_id}",
            organization_id=org_id,
            company_name="CreditBeast",
            primary_color="#2563eb",
            secondary_color="#64748b",
            accent_color="#0ea5e9",
            background_color="#ffffff",
            font_family="Inter",
            show_creditbeast_branding=True,
            created_at=branding_service.get_organization_branding(org_id).created_at,
            updated_at=branding_service.get_organization_branding(org_id).updated_at
        )
        
        return {
            "success": True,
            "data": default_branding.dict(),
            "message": "Branding reset to default successfully"
        }
    except Exception as e:
        logger.error(f"Error resetting branding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/branding/export", summary="Export Branding Configuration")
async def export_branding_configuration(
    current_user: dict = Depends(get_current_user)
):
    """Export current branding configuration as JSON"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        branding = await branding_service.get_organization_branding(org_id)
        
        return {
            "success": True,
            "data": {
                "branding": branding.dict(),
                "exported_at": "2025-11-06T21:24:37.547Z",
                "version": "1.0"
            },
            "message": "Branding configuration exported successfully"
        }
    except Exception as e:
        logger.error(f"Error exporting branding: {e}")
        raise HTTPException(status_code=500, detail=str(e))