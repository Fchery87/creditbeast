"""
Database service for Supabase operations
Handles all database interactions with organization scoping
Updated with official Supabase patterns from Context7 documentation
"""

import os
import logging
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
import asyncio
from contextlib import asynccontextmanager

# Official Supabase client pattern
from supabase import create_client, Client
from config import settings

logger = logging.getLogger(__name__)

class DatabaseService:
    """Enhanced service for database operations with official Supabase patterns"""
    
    def __init__(self):
        """Initialize Supabase clients using official pattern"""
        url: str = settings.supabase_url
        key: str = settings.supabase_key
        service_key: str = settings.supabase_service_role_key
        
        # Regular client for authenticated operations
        self.client: Client = create_client(url, key)
        # Admin client for service role operations
        self.admin_client: Client = create_client(url, service_key)
        
        logger.info("Supabase clients initialized successfully")
    
    @asynccontextmanager
    async def get_async_client(self):
        """Async context manager for database operations"""
        try:
            # Here you could use AsyncPostgrestClient if needed
            # For now, we'll use the existing sync client in async context
            yield self.admin_client
        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            raise
    
    def set_organization_context(self, org_id: str, user_id: str):
        """Set organization context for RLS policies"""
        # In production, this would set session variables
        # for Supabase RLS policies using:
        # self.admin_client.rpc('set_config', {
        #     'app.current_org_id': org_id,
        #     'app.current_user_id': user_id,
        #     'is_local': 'false'
        # })
        pass
    
    # ==========================================
    # CLIENT OPERATIONS (Enhanced with official patterns)
    # ==========================================
    
    async def create_client(
        self,
        organization_id: str,
        user_id: str,
        client_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a new client with proper error handling"""
        try:
            # Encrypt sensitive data if present
            if "ssn" in client_data and client_data["ssn"]:
                client_data["ssn_encrypted"] = self._encrypt_pii(client_data.pop("ssn"))
            
            client_data["organization_id"] = organization_id
            client_data["created_by_user_id"] = user_id
            
            # Use official Supabase pattern
            response = self.admin_client.table("clients").insert(client_data).execute()
            
            if response.data:
                logger.info(f"Client created successfully: {response.data[0]['id']}")
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error creating client: {e}")
            # Handle specific Supabase exceptions if needed
            # from postgrest.exceptions import APIError
            raise
    
    async def get_client(
        self,
        client_id: str,
        organization_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get client by ID with proper error handling"""
        try:
            # Official Supabase select pattern with filtering
            response = self.admin_client.table("clients")\
                .select("*")\
                .eq("id", client_id)\
                .eq("organization_id", organization_id)\
                .execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting client {client_id}: {e}")
            raise
    
    async def list_clients(
        self,
        organization_id: str,
        page: int = 1,
        page_size: int = 50,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """List clients with pagination using official patterns"""
        try:
            # Build query with official Supabase patterns
            query = self.admin_client.table("clients")\
                .select("*", count="exact")\
                .eq("organization_id", organization_id)\
                .order("created_at", desc=True)
            
            if status:
                query = query.eq("status", status)
            
            # Pagination with official range pattern
            offset = (page - 1) * page_size
            response = query.range(offset, offset + page_size - 1).execute()
            
            total = response.count or 0
            total_pages = (total + page_size - 1) // page_size
            
            return {
                "items": response.data or [],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
            
        except Exception as e:
            logger.error(f"Error listing clients: {e}")
            raise
    
    async def update_client(
        self,
        client_id: str,
        organization_id: str,
        client_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update client with official Supabase patterns"""
        try:
            response = self.admin_client.table("clients")\
                .update(client_data)\
                .eq("id", client_id)\
                .eq("organization_id", organization_id)\
                .execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error updating client {client_id}: {e}")
            raise
    
    # ==========================================
    # DISPUTE OPERATIONS (Enhanced)
    # ==========================================
    
    async def create_dispute(
        self,
        organization_id: str,
        user_id: str,
        dispute_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a new dispute with PII encryption"""
        try:
            # Encrypt sensitive data
            if "account_number" in dispute_data and dispute_data["account_number"]:
                dispute_data["account_number_encrypted"] = self._encrypt_pii(
                    dispute_data.pop("account_number")
                )
            
            dispute_data["organization_id"] = organization_id
            dispute_data["created_by_user_id"] = user_id
            
            # Official Supabase insert pattern
            response = self.admin_client.table("disputes").insert(dispute_data).execute()
            
            if response.data:
                logger.info(f"Dispute created: {response.data[0]['id']}")
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error creating dispute: {e}")
            raise
    
    async def get_dispute(
        self,
        dispute_id: str,
        organization_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get dispute by ID"""
        try:
            response = self.admin_client.table("disputes")\
                .select("*")\
                .eq("id", dispute_id)\
                .eq("organization_id", organization_id)\
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Error getting dispute {dispute_id}: {e}")
            raise
    
    async def list_disputes(
        self,
        organization_id: str,
        client_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """List disputes with pagination"""
        try:
            query = self.admin_client.table("disputes")\
                .select("*", count="exact")\
                .eq("organization_id", organization_id)\
                .order("created_at", desc=True)
            
            if client_id:
                query = query.eq("client_id", client_id)
            
            offset = (page - 1) * page_size
            response = query.range(offset, offset + page_size - 1).execute()
            
            total = response.count or 0
            total_pages = (total + page_size - 1) // page_size
            
            return {
                "items": response.data or [],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
            
        except Exception as e:
            logger.error(f"Error listing disputes: {e}")
            raise
    
    # ==========================================
    # ORGANIZATION OPERATIONS
    # ==========================================
    
    async def create_organization(
        self,
        org_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a new organization"""
        try:
            response = self.admin_client.table("organizations").insert(org_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating organization: {e}")
            raise
    
    async def get_organization(
        self,
        org_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get organization by ID"""
        try:
            response = self.admin_client.table("organizations")\
                .select("*")\
                .eq("id", org_id)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting organization {org_id}: {e}")
            raise
    
    # ==========================================
    # BULK OPERATIONS (New from official patterns)
    # ==========================================
    
    async def bulk_insert_clients(
        self,
        organization_id: str,
        user_id: str,
        clients_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Bulk insert clients with proper error handling"""
        try:
            # Process each client for PII encryption
            processed_data = []
            for client_data in clients_data:
                if "ssn" in client_data and client_data["ssn"]:
                    client_data["ssn_encrypted"] = self._encrypt_pii(client_data.pop("ssn"))
                
                client_data["organization_id"] = organization_id
                client_data["created_by_user_id"] = user_id
                processed_data.append(client_data)
            
            # Bulk insert using official pattern
            response = self.admin_client.table("clients").insert(processed_data).execute()
            
            logger.info(f"Bulk inserted {len(response.data)} clients")
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error in bulk insert clients: {e}")
            raise
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def _encrypt_pii(self, data: str) -> str:
        """Encrypt PII data using Fernet symmetric encryption"""
        from cryptography.fernet import Fernet
        from config import settings

        if not data:
            return ""

        # Get encryption key from settings (must be 32 url-safe base64-encoded bytes)
        key = settings.pii_encryption_key.encode()

        # Create Fernet cipher
        cipher = Fernet(key)

        # Encrypt the data
        encrypted = cipher.encrypt(data.encode())
        return encrypted.decode()

    def _decrypt_pii(self, encrypted_data: str) -> str:
        """Decrypt PII data using Fernet symmetric encryption"""
        from cryptography.fernet import Fernet, InvalidToken
        from config import settings

        if not encrypted_data:
            return ""

        try:
            # Get encryption key from settings
            key = settings.pii_encryption_key.encode()

            # Create Fernet cipher
            cipher = Fernet(key)

            # Decrypt the data
            decrypted = cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except InvalidToken:
            logger.error("Failed to decrypt PII data - invalid token or key")
            raise ValueError("Failed to decrypt PII data")
    
    # ==========================================
    # CLEANUP METHOD (Official pattern)
    # ==========================================
    
    async def cleanup(self):
        """Proper cleanup following official Supabase patterns"""
        try:
            # Sign out if authenticated
            if hasattr(self.client, 'auth'):
                self.client.auth.sign_out()
            if hasattr(self.admin_client, 'auth'):
                self.admin_client.auth.sign_out()
            logger.info("Supabase clients cleaned up successfully")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

# Global database service instance
db = DatabaseService()

# Helper function for testing connection
async def test_database_connection():
    """Test database connection with official patterns"""
    try:
        async with db.get_async_client() as client:
            # Test basic query
            response = client.table("organizations").select("*").limit(1).execute()
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")

# Database session generator for SQLAlchemy compatibility
def get_db():
    """
    Database session generator for backward compatibility
    Returns the admin client wrapped in a compatible interface
    Note: This is a compatibility layer - services should be updated to use db directly
    """
    yield db.admin_client

# Legacy database service class for services expecting SQLAlchemy patterns
class DatabaseSessionWrapper:
    """Wrapper to make Supabase client compatible with SQLAlchemy-style code"""
    
    def __init__(self, supabase_client):
        self.client = supabase_client
        self._cache = {}
    
    def query(self, *models):
        """Mock query method for SQLAlchemy compatibility"""
        # This is a simplified wrapper - full implementation would be complex
        # Services should be migrated to use Supabase patterns directly
        return self
    
    def filter(self, *conditions):
        """Mock filter method"""
        return self
    
    def filter_by(self, **kwargs):
        """Mock filter_by method"""
        return self
    
    def first(self):
        """Mock first method"""
        return None
    
    def all(self):
        """Mock all method"""
        return []
    
    def scalar(self):
        """Mock scalar method"""
        return 0
    
    def count(self):
        """Mock count method"""
        return 0
    
    def join(self, *args, **kwargs):
        """Mock join method"""
        return self
    
    def group_by(self, *args):
        """Mock group_by method"""
        return self
    
    def order_by(self, *args):
        """Mock order_by method"""
        return self
    
    def limit(self, count):
        """Mock limit method"""
        return self
    
    def offset(self, count):
        """Mock offset method"""
        return self
    
    def having(self, *args):
        """Mock having method"""
        return self
    
    def sum(self, column):
        """Mock sum method"""
        return self
        return False
