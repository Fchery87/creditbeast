"""
Authentication router
Handles user authentication and organization management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from models.schemas import OrganizationCreate, OrganizationResponse, UserResponse, BaseResponse
from services.database import db
from middleware.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/verify", response_model=BaseResponse)
async def verify_token(user: Dict[str, Any] = Depends(get_current_user)):
    """Verify authentication token"""
    return BaseResponse(
        success=True,
        message="Token is valid"
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=user["user_id"],
        clerk_user_id=user["user_id"],
        email=user.get("email", ""),
        full_name=user.get("name"),
        role=user.get("role", "member"),
        organization_id=user.get("organization_id"),
        created_at=None  # Would be fetched from database
    )

@router.post("/organizations", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new organization"""
    try:
        org = await db.create_organization({
            "name": org_data.name,
            "slug": org_data.slug,
            "owner_user_id": user["user_id"]
        })
        
        if not org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create organization"
            )
        
        return OrganizationResponse(**org)
    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/organizations/current", response_model=OrganizationResponse)
async def get_current_organization(user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user's organization"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not belong to an organization"
        )
    
    org = await db.get_organization(org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return OrganizationResponse(**org)
