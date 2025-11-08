"""
Authentication middleware for CreditBeast API
Handles JWT verification and organization scoping
"""

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import jwt
from config import settings
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

class AuthMiddleware:
    """Authentication and authorization middleware"""
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify JWT token and extract payload
        In production, this should verify against Clerk's public keys
        """
        try:
            # For Clerk integration, you would verify against Clerk's JWKS
            # This is a simplified version for demonstration
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials
    ) -> Dict[str, Any]:
        """Extract current user from token"""
        token = credentials.credentials
        payload = AuthMiddleware.verify_token(token)
        
        user_id = payload.get("sub")
        organization_id = payload.get("org_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return {
            "user_id": user_id,
            "organization_id": organization_id,
            "email": payload.get("email"),
            "role": payload.get("role", "member")
        }
    
    @staticmethod
    def require_organization(user: Dict[str, Any]) -> str:
        """Ensure user has an organization"""
        org_id = user.get("organization_id")
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User must belong to an organization"
            )
        return org_id
    
    @staticmethod
    def require_role(user: Dict[str, Any], required_roles: list) -> None:
        """Ensure user has required role"""
        user_role = user.get("role", "member")
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of these roles: {', '.join(required_roles)}"
            )

# Dependency for protected routes
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Dependency to get current authenticated user"""
    return await AuthMiddleware.get_current_user(credentials)

async def get_current_organization(
    user: Dict[str, Any] = Depends(get_current_user)
) -> str:
    """Dependency to get current user's organization"""
    return AuthMiddleware.require_organization(user)

async def get_organization_id(
    user: Dict[str, Any] = Depends(get_current_user)
) -> str:
    """Dependency to get current user's organization ID (alias for get_current_organization)"""
    return AuthMiddleware.require_organization(user)
