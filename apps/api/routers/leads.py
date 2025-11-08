"""
Leads router
Handles lead capture and conversion
"""

from fastapi import APIRouter, HTTPException, status
from models.schemas import ClientCreate, ClientResponse, BaseResponse
from services.database import db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/capture", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def capture_lead(lead_data: ClientCreate):
    """
    Capture a new lead (public endpoint - no auth required)
    This endpoint is used by the landing page to capture potential clients
    """
    try:
        # Create lead with 'lead' status
        # Note: This would need a default organization or handle public leads differently
        lead_dict = lead_data.dict(exclude_none=True)
        lead_dict["status"] = "lead"
        
        # For now, we'll use a default organization ID
        # In production, this might create a lead in a holding area
        # or associate with the organization from a hidden field/URL parameter
        default_org_id = "00000000-0000-0000-0000-000000000001"
        
        client = await db.create_client(
            organization_id=default_org_id,
            user_id=default_org_id,  # System user
            client_data=lead_dict
        )
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to capture lead"
            )
        
        return ClientResponse(**client)
    except Exception as e:
        logger.error(f"Error capturing lead: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{lead_id}/convert", response_model=ClientResponse)
async def convert_lead_to_client(lead_id: str):
    """
    Convert a lead to an active client
    This happens after agreement signing
    """
    try:
        # Update lead status to 'active'
        updated_client = await db.admin_client.table("clients")\
            .update({"status": "active"})\
            .eq("id", lead_id)\
            .eq("status", "lead")\
            .execute()
        
        if not updated_client.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found or already converted"
            )
        
        return ClientResponse(**updated_client.data[0])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting lead: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
