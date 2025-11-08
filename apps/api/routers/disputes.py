"""
Disputes router
Handles dispute generation and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, Optional
from uuid import UUID
from models.schemas import (
    DisputeCreate, DisputeUpdate, DisputeResponse, DisputeListResponse, BaseResponse
)
from services.database import db
from services.letter_templates import LetterTemplates
from middleware.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=DisputeResponse, status_code=status.HTTP_201_CREATED)
async def create_dispute(
    dispute_data: DisputeCreate,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new dispute"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        # Verify client exists and belongs to organization
        client = await db.get_client(
            client_id=str(dispute_data.client_id),
            organization_id=org_id
        )
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        # Create dispute
        dispute = await db.create_dispute(
            organization_id=org_id,
            user_id=user["user_id"],
            dispute_data=dispute_data.dict(exclude_none=True)
        )
        
        if not dispute:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create dispute"
            )
        
        return DisputeResponse(**dispute)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating dispute: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", response_model=DisputeListResponse)
async def list_disputes(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    client_id: Optional[UUID] = Query(None),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """List all disputes for the organization"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        result = await db.list_disputes(
            organization_id=org_id,
            client_id=str(client_id) if client_id else None,
            page=page,
            page_size=page_size
        )
        
        return DisputeListResponse(
            items=[DisputeResponse(**item) for item in result["items"]],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
    except Exception as e:
        logger.error(f"Error listing disputes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{dispute_id}", response_model=DisputeResponse)
async def get_dispute(
    dispute_id: UUID,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific dispute by ID"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        dispute = await db.get_dispute(
            dispute_id=str(dispute_id),
            organization_id=org_id
        )
        
        if not dispute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute not found"
            )
        
        return DisputeResponse(**dispute)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dispute: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{dispute_id}/generate", response_model=DisputeResponse)
async def generate_dispute_letter(
    dispute_id: UUID,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate dispute letter for a dispute"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        # Get dispute
        dispute = await db.get_dispute(
            dispute_id=str(dispute_id),
            organization_id=org_id
        )
        
        if not dispute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute not found"
            )
        
        # Get client data for letter personalization
        client = await db.get_client(
            client_id=dispute.get('client_id'),
            organization_id=org_id
        )

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found for this dispute"
            )

        # Get organization data for branding
        org_result = await db.admin_client.table("organizations")\
            .select("*")\
            .eq("id", org_id)\
            .execute()

        organization = org_result.data[0] if org_result.data else {}

        # Decrypt client PII for letter generation
        client_data = {
            "full_name": client.get("full_name", ""),
            "ssn": db._decrypt_pii(client.get("ssn_encrypted", "")) if client.get("ssn_encrypted") else "",
            "date_of_birth": client.get("date_of_birth", ""),
            "street_address": client.get("street_address", ""),
            "city": client.get("city", ""),
            "state": client.get("state", ""),
            "zip_code": client.get("zip_code", ""),
        }

        # Decrypt account number if present
        dispute_data = {
            **dispute,
            "account_number": db._decrypt_pii(dispute.get("account_number_encrypted", "")) if dispute.get("account_number_encrypted") else ""
        }

        # Generate letter using template service
        try:
            letter_content = LetterTemplates.generate_letter(
                dispute_data=dispute_data,
                client_data=client_data,
                organization_data=organization
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to generate letter: {str(e)}"
            )

        # Update dispute with generated letter
        from datetime import datetime
        updated_dispute = await db.admin_client.table("disputes")\
            .update({
                "letter_content": letter_content,
                "generated_at": datetime.utcnow().isoformat(),
                "status": "pending",
                "letter_template_id": f"{dispute_data.get('dispute_type', 'standard')}_template"
            })\
            .eq("id", str(dispute_id))\
            .eq("organization_id", org_id)\
            .execute()
        
        if not updated_dispute.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to generate letter"
            )
        
        return DisputeResponse(**updated_dispute.data[0])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating dispute letter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
