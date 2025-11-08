"""
Unit tests for security features
Tests for MFA, SSO, audit logging, security incidents, and session management
"""

import pytest
import asyncio
import pyotp
import secrets
from datetime import datetime
from unittest.mock import Mock, AsyncMock
from services.security import (
    MFAService,
    SSOService,
    AuditLogService,
    SecurityIncidentService,
    SessionManagementService
)

class TestMFAService:
    """Test Multi-Factor Authentication service"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    @pytest.fixture
    def mfa_service(self, mock_db):
        return MFAService(mock_db)
    
    @pytest.mark.asyncio
    async def test_setup_totp_mfa(self, mfa_service, mock_db):
        """Test TOTP MFA setup"""
        user_id = "user-123"
        organization_id = "org-123"
        mfa_method = "totp"
        
        mock_db.table.return_value.insert.return_value.execute.return_value.data = [{"id": "mfa-456"}]
        
        result = await mfa_service.setup_mfa(user_id, organization_id, mfa_method)
        
        assert result["mfa_method"] == "totp"
        assert result["secret"] is not None
        assert len(result["secret"]) > 0
        assert result["provisioning_uri"] is not None
        assert "otpauth://" in result["provisioning_uri"]
        assert result["qr_code"] is not None
        assert "data:image/png;base64," in result["qr_code"]
        assert len(result["backup_codes"]) == 10
    
    @pytest.mark.asyncio
    async def test_verify_totp_token(self, mfa_service, mock_db):
        """Test TOTP token verification"""
        user_id = "user-123"
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        valid_token = totp.now()
        
        # Mock MFA config
        mfa_config = {
            "id": "mfa-456",
            "user_id": user_id,
            "mfa_method": "totp",
            "secret": secret,
            "backup_codes": '["CODE1", "CODE2", "CODE3"]',
            "is_enabled": True
        }
        
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [mfa_config]
        
        result = await mfa_service.verify_mfa_token(user_id, valid_token)
        
        assert result["verified"] is True
        assert result["method"] == "totp"
    
    @pytest.mark.asyncio
    async def test_verify_backup_code(self, mfa_service, mock_db):
        """Test backup code verification"""
        user_id = "user-123"
        backup_codes = ["CODE1", "CODE2", "CODE3"]
        
        mfa_config = {
            "id": "mfa-456",
            "user_id": user_id,
            "mfa_method": "totp",
            "secret": "secret123",
            "backup_codes": str(backup_codes),
            "is_enabled": True
        }
        
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [mfa_config]
        mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value.data = []
        
        result = await mfa_service.verify_mfa_token(user_id, "", backup_code="CODE1")
        
        assert result["verified"] is True
        assert result["method"] == "backup_code"
        assert result["remaining_codes"] == 2


class TestSSOService:
    """Test Single Sign-On service"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    @pytest.fixture
    def sso_service(self, mock_db):
        return SSOService(mock_db)
    
    @pytest.mark.asyncio
    async def test_configure_google_sso(self, sso_service, mock_db):
        """Test Google SSO configuration"""
        organization_id = "org-123"
        sso_config = {
            "provider": "google",
            "client_id": "google-client-123",
            "client_secret": "google-secret-456",
            "is_enabled": True,
            "domain_restrictions": ["company.com"],
            "auto_provision_users": True,
            "default_role": "member"
        }
        
        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []  # No existing config
        mock_db.table.return_value.insert.return_value.execute.return_value.data = [{"id": "sso-789"}]
        
        result = await sso_service.configure_sso(organization_id, sso_config)
        
        assert result["provider"] == "google"
        assert result["is_enabled"] is True
        assert result["configuration_saved"] is True
    
    @pytest.mark.asyncio
    async def test_sso_callback_processing(self, sso_service, mock_db):
        """Test SSO callback processing"""
        organization_id = "org-123"
        sso_response = {
            "email": "user@company.com",
            "name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "sub": "google-user-123",
            "picture": "https://example.com/avatar.jpg"
        }
        
        sso_config = {
            "id": "sso-789",
            "provider": "google",
            "is_enabled": True,
            "domain_restrictions": ["company.com"],
            "auto_provision_users": True,
            "default_role": "member"
        }
        
        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [sso_config]
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []  # No existing user
        mock_db.table.return_value.insert.return_value.execute.return_value.data = [{"id": "user-456"}]
        
        # Mock JWT generation
        with pytest.MonkeyPatch().context() as m:
            m.setattr("services.security.jwt.encode", Mock(return_value="mock-jwt-token"))
            
            result = await sso_service.process_sso_callback(organization_id, sso_response)
        
        assert result["authenticated"] is True
        assert result["sso_provider"] == "google"
        assert "session_token" in result
    
    @pytest.mark.asyncio
    async def test_domain_restriction_check(self, sso_service):
        """Test domain restriction validation"""
        sso_config = {
            "domain_restrictions": '["company.com", "subsidiary.com"]'
        }
        
        # Test allowed domain
        assert await sso_service._check_domain_restrictions("user@company.com", sso_config) is True
        
        # Test disallowed domain
        assert await sso_service._check_domain_restrictions("user@other.com", sso_config) is False
        
        # Test no restrictions
        sso_config_empty = {"domain_restrictions": "[]"}
        assert await sso_service._check_domain_restrictions("user@any.com", sso_config_empty) is True


class TestAuditLogService:
    """Test audit logging service"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    @pytest.fixture
    def audit_service(self, mock_db):
        return AuditLogService(mock_db)
    
    @pytest.mark.asyncio
    async def test_log_security_event(self, audit_service, mock_db):
        """Test security event logging"""
        organization_id = "org-123"
        event_data = {
            "event_type": "user_login",
            "event_category": "authentication",
            "severity": "info",
            "user_id": "user-123",
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0",
            "action": "login_success",
            "status": "success"
        }
        
        mock_db.table.return_value.insert.return_value.execute.return_value.data = [{"id": "log-456"}]
        mock_db.table.return_value.insert.return_value.execute.return_value.data = []  # Auto-response log
        
        result = await audit_service.log_security_event(organization_id, event_data)
        
        assert result["logged"] is True
        assert result["log_id"] == "log-456"
    
    @pytest.mark.asyncio
    async def test_get_audit_logs_with_filters(self, audit_service, mock_db):
        """Test retrieving audit logs with filtering"""
        organization_id = "org-123"
        filters = {
            "event_type": "user_login",
            "severity": "info",
            "date_from": "2023-01-01",
            "date_to": "2023-12-31",
            "page": 1,
            "page_size": 10
        }
        
        # Mock log data
        mock_logs = [
            {
                "id": "log-1",
                "event_type": "user_login",
                "severity": "info",
                "timestamp": "2023-06-01T10:00:00Z",
                "user_id": "user-123"
            }
        ]
        
        mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = mock_logs
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.count.return_value.execute.return_value.data = [{"count": 1}]
        
        result = await audit_service.get_audit_logs(organization_id, filters)
        
        assert "logs" in result
        assert "pagination" in result
        assert len(result["logs"]) == 1
        assert result["pagination"]["total"] == 1


class TestSecurityIncidentService:
    """Test security incident service"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    @pytest.fixture
    def incident_service(self, mock_db):
        return SecurityIncidentService(mock_db)
    
    @pytest.mark.asyncio
    async def test_create_security_incident(self, incident_service, mock_db):
        """Test creating security incident"""
        organization_id = "org-123"
        incident_data = {
            "incident_type": "data_breach",
            "severity": "critical",
            "title": "Unauthorized access detected",
            "description": "Suspicious login activity from unknown IP",
            "affected_users": ["user-123", "user-456"],
            "affected_systems": ["api", "database"],
            "reported_by": "admin-789"
        }
        
        mock_db.table.return_value.insert.return_value.execute.return_value.data = [{"id": "incident-999"}]
        
        result = await incident_service.create_incident(organization_id, incident_data)
        
        assert result["status"] == "open"
        assert result["incident_id"] == "incident-999"
        assert result["notifications_sent"] is True
    
    @pytest.mark.asyncio
    async def test_update_incident_status(self, incident_service, mock_db):
        """Test updating incident status"""
        incident_id = "incident-999"
        organization_id = "org-123"
        status_data = {
            "status": "resolved",
            "resolution": "Access revoked and systems secured",
            "resolved_by": "admin-789",
            "old_status": "investigating"
        }
        
        mock_db.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        mock_db.table.return_value.insert.return_value.execute.return_value.data = []
        
        result = await incident_service.update_incident_status(incident_id, organization_id, status_data)
        
        assert result["status"] == "resolved"
        assert result["updated"] is True


class TestSessionManagementService:
    """Test session management service"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    @pytest.fixture
    def session_service(self, mock_db):
        return SessionManagementService(mock_db)
    
    @pytest.mark.asyncio
    async def test_create_user_session(self, session_service, mock_db):
        """Test creating user session"""
        user_id = "user-123"
        organization_id = "org-123"
        session_data = {
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0",
            "device_info": {"browser": "Chrome", "os": "Windows"}
        }
        
        # Mock session config
        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []  # No existing config
        mock_db.table.return_value.insert.return_value.execute.return_value.data = [{
            "max_session_duration_hours": 8,
            "max_concurrent_sessions": 3
        }]
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.gt.return_value.execute.return_value.data = []  # No active sessions
        mock_db.table.return_value.insert.return_value.execute.return_value.data = [{
            "session_id": "session-456",
            "session_token": "token-789"
        }]
        
        result = await session_service.create_session(user_id, organization_id, session_data)
        
        assert "session_id" in result
        assert "session_token" in result
        assert "expires_at" in result
        assert result["created"] is True
    
    @pytest.mark.asyncio
    async def test_validate_session(self, session_service, mock_db):
        """Test session validation"""
        session_token = "valid-token-123"
        organization_id = "org-123"
        
        # Mock active session
        session = {
            "session_id": "session-456",
            "user_id": "user-123",
            "session_token": session_token,
            "expires_at": int(asyncio.get_event_loop().time()) + 3600,  # 1 hour from now
            "status": "active",
            "last_activity": int(asyncio.get_event_loop().time())
        }
        
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [session]
        mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value.data = []
        
        result = await session_service.validate_session(session_token, organization_id)
        
        assert result["valid"] is True
        assert result["user_id"] == "user-123"
        assert result["session_id"] == "session-456"
    
    @pytest.mark.asyncio
    async def test_validate_expired_session(self, session_service, mock_db):
        """Test validation of expired session"""
        session_token = "expired-token-123"
        organization_id = "org-123"
        
        # Mock expired session
        session = {
            "session_id": "session-456",
            "user_id": "user-123",
            "session_token": session_token,
            "expires_at": int(asyncio.get_event_loop().time()) - 3600,  # 1 hour ago
            "status": "active"
        }
        
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [session]
        mock_db.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        
        result = await session_service.validate_session(session_token, organization_id)
        
        assert result["valid"] is False
        assert "Session expired" in result["error"]
    
    @pytest.mark.asyncio
    async def test_terminate_session(self, session_service, mock_db):
        """Test session termination"""
        session_token = "token-to-terminate"
        organization_id = "org-123"
        
        mock_db.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        
        result = await session_service.terminate_session(session_token, organization_id)
        
        assert result["terminated"] is True
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, session_service, mock_db):
        """Test expired session cleanup"""
        organization_id = "org-123"
        
        # Mock expired sessions
        mock_db.table.return_value.update.return_value.lt.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.gte.return_value.execute.return_value.data = [{"count": 5}]
        
        result = await session_service.cleanup_expired_sessions(organization_id)
        
        assert result["cleaned_sessions"] == 5
        assert result["cleanup_completed"] is True


# Integration tests that test multiple components working together

class TestSecurityIntegration:
    """Integration tests for security features"""
    
    @pytest.mark.asyncio
    async def test_mfa_and_session_integration(self):
        """Test MFA and session management working together"""
        # This would test the flow where MFA verification creates a session
        pass
    
    @pytest.mark.asyncio
    async def test_sso_and_audit_integration(self):
        """Test SSO and audit logging working together"""
        # This would test SSO events being properly logged
        pass
    
    @pytest.mark.asyncio
    async def test_incident_workflow_integration(self):
        """Test complete incident response workflow"""
        # This would test incident creation, status updates, and resolution
        pass