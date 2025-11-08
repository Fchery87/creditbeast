"""
Clients router
Handles client management operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, Optional
from uuid import UUID
from models.schemas import (
    ClientCreate, ClientUpdate, ClientResponse, ClientListResponse, BaseResponse
)
from services.database import db
from middleware.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new client"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        client = await db.create_client(
            organization_id=org_id,
            user_id=user["user_id"],
            client_data=client_data.dict(exclude_none=True)
        )
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create client"
            )
        
        return ClientResponse(**client)
    except Exception as e:
        logger.error(f"Error creating client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", response_model=ClientListResponse)
async def list_clients(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """List all clients for the organization"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        result = await db.list_clients(
            organization_id=org_id,
            page=page,
            page_size=page_size,
            status=status_filter
        )
        
        return ClientListResponse(
            items=[ClientResponse(**item) for item in result["items"]],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
    except Exception as e:
        logger.error(f"Error listing clients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific client by ID"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        client = await db.get_client(
            client_id=str(client_id),
            organization_id=org_id
        )
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        return ClientResponse(**client)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    client_data: ClientUpdate,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a client"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        # Verify client exists and belongs to organization
        existing_client = await db.get_client(
            client_id=str(client_id),
            organization_id=org_id
        )
        
        if not existing_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        # Update client
        updated_client = await db.update_client(
            client_id=str(client_id),
            organization_id=org_id,
            client_data=client_data.dict(exclude_none=True)
        )
        
        if not updated_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update client"
            )
        
        return ClientResponse(**updated_client)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{client_id}", response_model=BaseResponse)
async def delete_client(
    client_id: UUID,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a client (soft delete by changing status)"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        # Verify client exists
        client = await db.get_client(
            client_id=str(client_id),
            organization_id=org_id
        )
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        # Soft delete by setting status to 'churned'
        await db.update_client(
            client_id=str(client_id),
            organization_id=org_id,
            client_data={"status": "churned"}
        )
        
        return BaseResponse(
            success=True,
            message="Client deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
