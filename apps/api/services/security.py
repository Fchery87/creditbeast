"""
Security Enhancement Services for CreditBeast
MFA, SSO, audit logging, security incidents, and session management
"""

import secrets
import hashlib
import hmac
import time
import base64
import qrcode
import io
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID
import json
import pyotp
import jwt
from config import settings

logger = logging.getLogger(__name__)

class MFAService:
    """Multi-Factor Authentication service"""
    
    def __init__(self, db_client):
        self.db = db_client
    
    async def setup_mfa(self, user_id: str, organization_id: str, mfa_method: str) -> Dict[str, Any]:
        """Set up MFA for user"""
        try:
            # Generate secret based on method
            if mfa_method == "totp":
                secret = pyotp.random_base32()
                provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                    name=f"user_{user_id}@creditbeast.com",
                    issuer_name="CreditBeast"
                )
                
                # Generate QR code
                qr_code_data = await self._generate_qr_code(provisioning_uri)
                
            elif mfa_method in ["sms", "email"]:
                # For SMS/Email, we'll need phone/email verification
                secret = secrets.token_urlsafe(32)
                provisioning_uri = None
                qr_code_data = None
                
            else:
                raise ValueError(f"Unsupported MFA method: {mfa_method}")
            
            # Generate backup codes
            backup_codes = await self._generate_backup_codes()
            
            # Save MFA configuration
            mfa_config = {
                "user_id": user_id,
                "organization_id": organization_id,
                "mfa_method": mfa_method,
                "secret": secret,
                "backup_codes": json.dumps(backup_codes),
                "is_enabled": True,
                "is_required": False,
                "max_backup_codes": len(backup_codes),
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = await self.db.table("mfa_configs").insert(mfa_config).execute()
            
            return {
                "mfa_config_id": result.data[0]['id'] if result.data else None,
                "mfa_method": mfa_method,
                "secret": secret,
                "provisioning_uri": provisioning_uri,
                "qr_code": qr_code_data,
                "backup_codes": backup_codes,
                "setup_completed": True
            }
            
        except Exception as e:
            logger.error(f"Error setting up MFA: {e}")
            raise
    
    async def verify_mfa_token(self, user_id: str, token: str, backup_code: Optional[str] = None) -> Dict[str, Any]:
        """Verify MFA token or backup code"""
        try:
            # Get user's MFA config
            mfa_config = await self._get_user_mfa_config(user_id)
            if not mfa_config:
                return {"verified": False, "error": "MFA not configured"}
            
            mfa_method = mfa_config['mfa_method']
            secret = mfa_config['secret']
            
            # Check backup code first if provided
            if backup_code:
                return await self._verify_backup_code(mfa_config, backup_code)
            
            # Verify based on method
            if mfa_method == "totp":
                return await self._verify_totp_token(secret, token)
            elif mfa_method == "sms":
                return await self._verify_sms_token(user_id, token)
            elif mfa_method == "email":
                return await self._verify_email_token(user_id, token)
            else:
                return {"verified": False, "error": f"Unsupported MFA method: {mfa_method}"}
                
        except Exception as e:
            logger.error(f"Error verifying MFA token: {e}")
            return {"verified": False, "error": str(e)}
    
    async def _get_user_mfa_config(self, user_id: str) -> Optional[Dict]:
        """Get user's MFA configuration"""
        result = await self.db.table("mfa_configs").select("*")\
            .eq("user_id", user_id)\
            .eq("is_enabled", True)\
            .execute()
        return result.data[0] if result.data else None
    
    async def _verify_totp_token(self, secret: str, token: str) -> Dict[str, Any]:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        is_valid = totp.verify(token, valid_window=1)
        
        return {
            "verified": is_valid,
            "method": "totp",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _verify_sms_token(self, user_id: str, token: str) -> Dict[str, Any]:
        """Verify SMS token (simplified - would integrate with SMS service)"""
        # In real implementation, this would check against stored SMS codes
        # For now, return a simplified response
        return {
            "verified": len(token) == 6 and token.isdigit(),
            "method": "sms",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _verify_email_token(self, user_id: str, token: str) -> Dict[str, Any]:
        """Verify email token"""
        # In real implementation, this would check against stored email codes
        return {
            "verified": len(token) == 6 and token.isdigit(),
            "method": "email",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _verify_backup_code(self, mfa_config: Dict, backup_code: str) -> Dict[str, Any]:
        """Verify backup code"""
        stored_codes = json.loads(mfa_config.get('backup_codes', '[]'))
        
        if backup_code in stored_codes:
            # Remove used backup code
            stored_codes.remove(backup_code)
            await self._update_backup_codes(mfa_config['id'], stored_codes)
            
            return {
                "verified": True,
                "method": "backup_code",
                "remaining_codes": len(stored_codes),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {"verified": False, "error": "Invalid backup code"}
    
    async def _generate_backup_codes(self) -> List[str]:
        """Generate secure backup codes"""
        codes = []
        for _ in range(10):
            code = secrets.token_hex(3).upper()  # 6-character hex code
            codes.append(code)
        return codes
    
    async def _update_backup_codes(self, mfa_config_id: str, codes: List[str]):
        """Update backup codes for user"""
        await self.db.table("mfa_configs").update({
            "backup_codes": json.dumps(codes)
        }).eq("id", mfa_config_id).execute()
    
    async def _generate_qr_code(self, provisioning_uri: str) -> str:
        """Generate QR code for TOTP setup"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 string
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"


class SSOService:
    """Single Sign-On service"""
    
    def __init__(self, db_client):
        self.db = db_client
    
    async def configure_sso(self, organization_id: str, sso_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure SSO for organization"""
        try:
            # Validate provider
            provider = sso_config.get('provider')
            if provider not in ['google', 'microsoft', 'okta', 'auth0', 'custom']:
                raise ValueError(f"Unsupported SSO provider: {provider}")
            
            # Prepare SSO configuration
            sso_data = {
                "organization_id": organization_id,
                "provider": provider,
                "client_id": sso_config.get('client_id'),
                "client_secret": sso_config.get('client_secret'),
                "authority": sso_config.get('authority'),
                "scopes": json.dumps(sso_config.get('scopes', ['openid', 'profile', 'email'])),
                "domain_restrictions": json.dumps(sso_config.get('domain_restrictions', [])),
                "auto_provision_users": sso_config.get('auto_provision_users', True),
                "default_role": sso_config.get('default_role', 'member'),
                "is_enabled": sso_config.get('is_enabled', False),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Check if SSO config already exists
            existing = await self._get_sso_config(organization_id)
            if existing:
                # Update existing
                result = await self.db.table("sso_settings").update(sso_data)\
                    .eq("organization_id", organization_id)\
                    .execute()
            else:
                # Create new
                result = await self.db.table("sso_settings").insert(sso_data).execute()
            
            return {
                "sso_config_id": result.data[0]['id'] if result.data else None,
                "provider": provider,
                "is_enabled": sso_config.get('is_enabled', False),
                "configuration_saved": True
            }
            
        except Exception as e:
            logger.error(f"Error configuring SSO: {e}")
            raise
    
    async def process_sso_callback(self, organization_id: str, sso_response: Dict[str, Any]) -> Dict[str, Any]:
        """Process SSO callback and authenticate user"""
        try:
            # Get SSO configuration
            sso_config = await self._get_sso_config(organization_id)
            if not sso_config:
                raise ValueError("SSO not configured for organization")
            
            if not sso_config.get('is_enabled'):
                raise ValueError("SSO is not enabled")
            
            # Validate SSO response based on provider
            provider = sso_config['provider']
            if provider == 'google':
                user_info = await self._validate_google_sso(sso_response, sso_config)
            elif provider == 'microsoft':
                user_info = await self._validate_microsoft_sso(sso_response, sso_config)
            else:
                # Generic validation
                user_info = await self._validate_generic_sso(sso_response, sso_config)
            
            if not user_info:
                return {"authenticated": False, "error": "Invalid SSO response"}
            
            # Check domain restrictions
            if not await self._check_domain_restrictions(user_info.get('email'), sso_config):
                return {"authenticated": False, "error": "Email domain not allowed"}
            
            # Create or update user
            user = await self._create_or_update_sso_user(user_info, organization_id, sso_config)
            
            # Generate session token
            session_token = await self._generate_sso_session_token(user, organization_id)
            
            return {
                "authenticated": True,
                "user": user,
                "session_token": session_token,
                "sso_provider": provider
            }
            
        except Exception as e:
            logger.error(f"Error processing SSO callback: {e}")
            return {"authenticated": False, "error": str(e)}
    
    async def _get_sso_config(self, organization_id: str) -> Optional[Dict]:
        """Get SSO configuration for organization"""
        result = await self.db.table("sso_settings").select("*")\
            .eq("organization_id", organization_id)\
            .execute()
        return result.data[0] if result.data else None
    
    async def _validate_google_sso(self, sso_response: Dict, config: Dict) -> Optional[Dict]:
        """Validate Google SSO response"""
        # In real implementation, this would validate JWT with Google's public keys
        # For now, return simplified user info
        email = sso_response.get('email')
        if not email or not email.endswith('@gmail.com'):
            return None
        
        return {
            "email": email,
            "full_name": sso_response.get('name', ''),
            "first_name": sso_response.get('given_name', ''),
            "last_name": sso_response.get('family_name', ''),
            "provider_user_id": sso_response.get('sub', ''),
            "picture": sso_response.get('picture', '')
        }
    
    async def _validate_microsoft_sso(self, sso_response: Dict, config: Dict) -> Optional[Dict]:
        """Validate Microsoft SSO response"""
        email = sso_response.get('email') or sso_response.get('preferred_username')
        if not email:
            return None
        
        return {
            "email": email,
            "full_name": sso_response.get('name', ''),
            "first_name": sso_response.get('given_name', ''),
            "last_name": sso_response.get('family_name', ''),
            "provider_user_id": sso_response.get('sub', ''),
            "tenant_id": sso_response.get('tid', '')
        }
    
    async def _validate_generic_sso(self, sso_response: Dict, config: Dict) -> Optional[Dict]:
        """Validate generic SSO response"""
        email = sso_response.get('email')
        if not email:
            return None
        
        return {
            "email": email,
            "full_name": sso_response.get('name', ''),
            "first_name": sso_response.get('given_name', '') or sso_response.get('first_name', ''),
            "last_name": sso_response.get('family_name', '') or sso_response.get('last_name', ''),
            "provider_user_id": sso_response.get('sub', '') or sso_response.get('id', ''),
            "picture": sso_response.get('picture', '') or sso_response.get('avatar', '')
        }
    
    async def _check_domain_restrictions(self, email: str, config: Dict) -> bool:
        """Check if email domain is allowed"""
        if not email:
            return False
        
        domain_restrictions = json.loads(config.get('domain_restrictions', '[]'))
        if not domain_restrictions:
            return True  # No restrictions
        
        email_domain = email.split('@')[1].lower()
        return email_domain in [d.lower() for d in domain_restrictions]
    
    async def _create_or_update_sso_user(self, user_info: Dict, organization_id: str, config: Dict) -> Dict[str, Any]:
        """Create or update user from SSO"""
        email = user_info['email']
        
        # Check if user exists
        existing_user = await self._get_user_by_email(email, organization_id)
        
        if existing_user:
            # Update existing user
            user_data = {
                "full_name": user_info.get('full_name', ''),
                "first_name": user_info.get('first_name', ''),
                "last_name": user_info.get('last_name', ''),
                "avatar_url": user_info.get('picture', ''),
                "last_login_at": datetime.utcnow().isoformat(),
                "sso_provider": config['provider'],
                "sso_user_id": user_info.get('provider_user_id', '')
            }
            
            result = await self.db.table("users").update(user_data)\
                .eq("id", existing_user['id'])\
                .execute()
            user_id = existing_user['id']
        else:
            # Create new user
            if not config.get('auto_provision_users', True):
                raise ValueError("Auto-provisioning disabled")
            
            user_data = {
                "organization_id": organization_id,
                "email": email,
                "full_name": user_info.get('full_name', ''),
                "first_name": user_info.get('first_name', ''),
                "last_name": user_info.get('last_name', ''),
                "role": config.get('default_role', 'member'),
                "avatar_url": user_info.get('picture', ''),
                "last_login_at": datetime.utcnow().isoformat(),
                "sso_provider": config['provider'],
                "sso_user_id": user_info.get('provider_user_id', ''),
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = await self.db.table("users").insert(user_data).execute()
            user_id = result.data[0]['id'] if result.data else None
        
        return {"id": user_id, "email": email, **user_info}
    
    async def _get_user_by_email(self, email: str, organization_id: str) -> Optional[Dict]:
        """Get user by email"""
        result = await self.db.table("users").select("*")\
            .eq("email", email)\
            .eq("organization_id", organization_id)\
            .execute()
        return result.data[0] if result.data else None
    
    async def _generate_sso_session_token(self, user: Dict, organization_id: str) -> str:
        """Generate session token for SSO user"""
        payload = {
            "user_id": user['id'],
            "organization_id": organization_id,
            "sso_authenticated": True,
            "exp": int(time.time()) + (8 * 60 * 60)  # 8 hours
        }
        
        return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


class AuditLogService:
    """Advanced audit logging service"""
    
    def __init__(self, db_client):
        self.db = db_client
    
    async def log_security_event(self, organization_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log security event with full context"""
        try:
            audit_log = {
                "organization_id": organization_id,
                "event_type": event_data.get('event_type'),
                "event_category": event_data.get('event_category', 'security'),
                "severity": event_data.get('severity', 'info'),
                "user_id": event_data.get('user_id'),
                "session_id": event_data.get('session_id'),
                "ip_address": event_data.get('ip_address'),
                "user_agent": event_data.get('user_agent'),
                "resource_type": event_data.get('resource_type'),
                "resource_id": event_data.get('resource_id'),
                "action": event_data.get('action'),
                "status": event_data.get('status', 'success'),
                "details": json.dumps(event_data.get('details', {})),
                "timestamp": datetime.utcnow().isoformat(),
                "source": event_data.get('source', 'api'),
                "correlation_id": event_data.get('correlation_id')
            }
            
            result = await self.db.table("audit_logs").insert(audit_log).execute()
            
            # Check if this event requires automatic response
            await self._check_auto_response(event_data, organization_id)
            
            return {
                "log_id": result.data[0]['id'] if result.data else None,
                "logged": True,
                "auto_response_triggered": event_data.get('auto_response_triggered', False)
            }
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
            raise
    
    async def get_audit_logs(self, organization_id: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve audit logs with filtering"""
        try:
            # Build query
            query = self.db.table("audit_logs").select("*")\
                .eq("organization_id", organization_id)
            
            # Apply filters
            if filters.get('event_type'):
                query = query.eq('event_type', filters['event_type'])
            
            if filters.get('severity'):
                query = query.eq('severity', filters['severity'])
            
            if filters.get('user_id'):
                query = query.eq('user_id', filters['user_id'])
            
            if filters.get('date_from'):
                query = query.gte('timestamp', filters['date_from'])
            
            if filters.get('date_to'):
                query = query.lte('timestamp', filters['date_to'])
            
            if filters.get('ip_address'):
                query = query.eq('ip_address', filters['ip_address'])
            
            # Pagination
            page = filters.get('page', 1)
            page_size = min(filters.get('page_size', 50), 100)
            offset = (page - 1) * page_size
            
            query = query.order('timestamp', desc=True)\
                        .range(offset, offset + page_size - 1)
            
            result = await query.execute()
            logs = result.data or []
            
            # Get total count for pagination
            count_query = self.db.table("audit_logs").select("id", count="exact")\
                .eq("organization_id", organization_id)
            
            # Apply same filters for count
            if filters.get('event_type'):
                count_query = count_query.eq('event_type', filters['event_type'])
            if filters.get('severity'):
                count_query = count_query.eq('severity', filters['severity'])
            if filters.get('user_id'):
                count_query = count_query.eq('user_id', filters['user_id'])
            if filters.get('date_from'):
                count_query = count_query.gte('timestamp', filters['date_from'])
            if filters.get('date_to'):
                count_query = count_query.lte('timestamp', filters['date_to'])
            if filters.get('ip_address'):
                count_query = count_query.eq('ip_address', filters['ip_address'])
            
            count_result = await count_query.execute()
            total = count_result.count if count_result.count else 0
            
            return {
                "logs": logs,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size
                },
                "filters_applied": filters
            }
            
        except Exception as e:
            logger.error(f"Error retrieving audit logs: {e}")
            raise
    
    async def _check_auto_response(self, event_data: Dict, organization_id: str):
        """Check if event triggers automatic response"""
        event_type = event_data.get('event_type')
        severity = event_data.get('severity')
        
        # Define auto-response rules
        if event_type in ['multiple_failed_logins', 'brute_force_attempt'] and severity in ['high', 'critical']:
            await self._trigger_auto_response('account_lockout', event_data, organization_id)
        elif event_type in ['privilege_escalation', 'unauthorized_access'] and severity == 'critical':
            await self._trigger_auto_response('immediate_alert', event_data, organization_id)
        elif event_type in ['data_exfiltration', 'suspicious_download'] and severity == 'critical':
            await self._trigger_auto_response('data_protection', event_data, organization_id)
    
    async def _trigger_auto_response(self, response_type: str, event_data: Dict, organization_id: str):
        """Trigger automatic security response"""
        # This would integrate with actual security response systems
        logger.info(f"Auto-response triggered: {response_type} for organization {organization_id}")
        
        # Log the auto-response action
        await self.db.table("security_responses").insert({
            "organization_id": organization_id,
            "trigger_event_id": event_data.get('event_id'),
            "response_type": response_type,
            "status": "triggered",
            "triggered_at": datetime.utcnow().isoformat(),
            "details": json.dumps(event_data)
        }).execute()


class SecurityIncidentService:
    """Security incident response service"""
    
    def __init__(self, db_client):
        self.db = db_client
    
    async def create_incident(self, organization_id: str, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new security incident"""
        try:
            incident = {
                "organization_id": organization_id,
                "incident_type": incident_data.get('incident_type'),
                "severity": incident_data.get('severity', 'medium'),
                "title": incident_data.get('title'),
                "description": incident_data.get('description'),
                "reported_by": incident_data.get('reported_by'),
                "affected_users": json.dumps(incident_data.get('affected_users', [])),
                "affected_systems": json.dumps(incident_data.get('affected_systems', [])),
                "status": "open",
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = await self.db.table("security_incidents").insert(incident).execute()
            incident_id = result.data[0]['id'] if result.data else None
            
            # Trigger initial notifications
            await self._trigger_incident_notifications(incident_id, incident, organization_id)
            
            return {
                "incident_id": incident_id,
                "status": "open",
                "notifications_sent": True,
                "created_at": incident['created_at']
            }
            
        except Exception as e:
            logger.error(f"Error creating security incident: {e}")
            raise
    
    async def update_incident_status(self, incident_id: str, organization_id: str, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update incident status and add resolution notes"""
        try:
            update_data = {
                "status": status_data.get('status'),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if status_data.get('status') in ['resolved', 'closed']:
                update_data["resolution"] = status_data.get('resolution')
                update_data["resolved_by"] = status_data.get('resolved_by')
                update_data["resolution_time"] = datetime.utcnow().isoformat()
            
            await self.db.table("security_incidents").update(update_data)\
                .eq("id", incident_id)\
                .eq("organization_id", organization_id)\
                .execute()
            
            # Log status change
            await self._log_incident_status_change(incident_id, status_data, organization_id)
            
            return {
                "incident_id": incident_id,
                "status": status_data.get('status'),
                "updated": True
            }
            
        except Exception as e:
            logger.error(f"Error updating incident status: {e}")
            raise
    
    async def get_incidents(self, organization_id: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get security incidents with filtering"""
        try:
            query = self.db.table("security_incidents").select("*")\
                .eq("organization_id", organization_id)
            
            # Apply filters
            if filters.get('status'):
                query = query.eq('status', filters['status'])
            
            if filters.get('severity'):
                query = query.eq('severity', filters['severity'])
            
            if filters.get('incident_type'):
                query = query.eq('incident_type', filters['incident_type'])
            
            if filters.get('date_from'):
                query = query.gte('created_at', filters['date_from'])
            
            if filters.get('date_to'):
                query = query.lte('created_at', filters['date_to'])
            
            # Pagination
            page = filters.get('page', 1)
            page_size = min(filters.get('page_size', 50), 100)
            offset = (page - 1) * page_size
            
            query = query.order('created_at', desc=True)\
                        .range(offset, offset + page_size - 1)
            
            result = await query.execute()
            incidents = result.data or []
            
            # Parse JSON fields
            for incident in incidents:
                incident['affected_users'] = json.loads(incident.get('affected_users', '[]'))
                incident['affected_systems'] = json.loads(incident.get('affected_systems', '[]'))
            
            return {
                "incidents": incidents,
                "filters_applied": filters
            }
            
        except Exception as e:
            logger.error(f"Error retrieving incidents: {e}")
            raise
    
    async def _trigger_incident_notifications(self, incident_id: str, incident: Dict, organization_id: str):
        """Send notifications for new incident"""
        # This would integrate with notification system
        logger.info(f"Incident notifications triggered: {incident_id}")
    
    async def _log_incident_status_change(self, incident_id: str, status_data: Dict, organization_id: str):
        """Log incident status change"""
        await self.db.table("incident_status_changes").insert({
            "incident_id": incident_id,
            "organization_id": organization_id,
            "old_status": status_data.get('old_status'),
            "new_status": status_data.get('status'),
            "changed_by": status_data.get('changed_by'),
            "notes": status_data.get('notes', ''),
            "changed_at": datetime.utcnow().isoformat()
        }).execute()


class SessionManagementService:
    """Session management and timeout service"""
    
    def __init__(self, db_client):
        self.db = db_client
    
    async def create_session(self, user_id: str, organization_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user session"""
        try:
            session_token = secrets.token_urlsafe(32)
            session_id = secrets.token_urlsafe(16)
            
            # Get session configuration
            config = await self._get_session_config(organization_id)
            if not config:
                config = await self._create_default_session_config(organization_id)
            
            # Calculate expiry
            max_duration = config.get('max_session_duration_hours', 8) * 3600  # Convert to seconds
            expires_at = int(time.time()) + max_duration
            
            session = {
                "session_id": session_id,
                "user_id": user_id,
                "organization_id": organization_id,
                "session_token": session_token,
                "ip_address": session_data.get('ip_address'),
                "user_agent": session_data.get('user_agent'),
                "device_info": json.dumps(session_data.get('device_info', {})),
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": expires_at,
                "last_activity": int(time.time()),
                "max_concurrent_sessions": config.get('max_concurrent_sessions', 3)
            }
            
            # Check concurrent session limit
            active_sessions = await self._get_active_sessions(user_id, organization_id)
            if len(active_sessions) >= config.get('max_concurrent_sessions', 3):
                # Remove oldest session
                oldest_session = min(active_sessions, key=lambda x: x.get('last_activity', 0))
                await self._terminate_session(oldest_session['session_id'], organization_id)
            
            result = await self.db.table("user_sessions").insert(session).execute()
            
            return {
                "session_id": session_id,
                "session_token": session_token,
                "expires_at": expires_at,
                "created": True
            }
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    async def validate_session(self, session_token: str, organization_id: str) -> Dict[str, Any]:
        """Validate session token and return session info"""
        try:
            # Get session by token
            result = await self.db.table("user_sessions").select("*")\
                .eq("session_token", session_token)\
                .eq("organization_id", organization_id)\
                .execute()
            
            if not result.data:
                return {"valid": False, "error": "Session not found"}
            
            session = result.data[0]
            
            # Check if expired
            if session.get('expires_at', 0) < int(time.time()):
                await self._terminate_session(session['session_id'], organization_id)
                return {"valid": False, "error": "Session expired"}
            
            # Check if session is active
            if session.get('status') == 'terminated':
                return {"valid": False, "error": "Session terminated"}
            
            # Update last activity
            await self.db.table("user_sessions").update({
                "last_activity": int(time.time())
            }).eq("session_id", session['session_id']).execute()
            
            return {
                "valid": True,
                "session_id": session['session_id'],
                "user_id": session['user_id'],
                "organization_id": organization_id,
                "expires_at": session.get('expires_at'),
                "last_activity": session.get('last_activity')
            }
            
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return {"valid": False, "error": str(e)}
    
    async def terminate_session(self, session_token: str, organization_id: str) -> Dict[str, Any]:
        """Terminate session"""
        try:
            await self._terminate_session_by_token(session_token, organization_id)
            return {"terminated": True}
        except Exception as e:
            logger.error(f"Error terminating session: {e}")
            return {"terminated": False, "error": str(e)}
    
    async def cleanup_expired_sessions(self, organization_id: str) -> Dict[str, Any]:
        """Clean up expired sessions"""
        try:
            current_time = int(time.time())
            
            # Mark expired sessions as terminated
            await self.db.table("user_sessions").update({
                "status": "terminated",
                "terminated_at": datetime.utcnow().isoformat(),
                "termination_reason": "expired"
            }).lt("expires_at", current_time)\
              .eq("organization_id", organization_id)\
              .eq("status", "active")\
              .execute()
            
            # Get count of cleaned sessions
            result = await self.db.table("user_sessions").select("id", count="exact")\
                .eq("organization_id", organization_id)\
                .eq("status", "terminated")\
                .gte("terminated_at", (datetime.utcnow() - timedelta(hours=1)).isoformat())\
                .execute()
            
            cleaned_count = result.count if result.count else 0
            
            return {
                "cleaned_sessions": cleaned_count,
                "cleanup_completed": True
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")
            raise
    
    async def _get_session_config(self, organization_id: str) -> Optional[Dict]:
        """Get session configuration for organization"""
        result = await self.db.table("session_configs").select("*")\
            .eq("organization_id", organization_id)\
            .execute()
        return result.data[0] if result.data else None
    
    async def _create_default_session_config(self, organization_id: str) -> Dict:
        """Create default session configuration"""
        default_config = {
            "organization_id": organization_id,
            "max_session_duration_hours": 8,
            "max_concurrent_sessions": 3,
            "session_timeout_warn_minutes": 15,
            "enforce_device_trust": False,
            "require_fresh_login": False,
            "ip_whitelist": json.dumps([]),
            "geo_restrictions": json.dumps([]),
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = await self.db.table("session_configs").insert(default_config).execute()
        return result.data[0] if result.data else default_config
    
    async def _get_active_sessions(self, user_id: str, organization_id: str) -> List[Dict]:
        """Get active sessions for user"""
        result = await self.db.table("user_sessions").select("*")\
            .eq("user_id", user_id)\
            .eq("organization_id", organization_id)\
            .eq("status", "active")\
            .gt("expires_at", int(time.time()))\
            .execute()
        return result.data or []
    
    async def _terminate_session(self, session_id: str, organization_id: str):
        """Terminate session by ID"""
        await self.db.table("user_sessions").update({
            "status": "terminated",
            "terminated_at": datetime.utcnow().isoformat(),
            "termination_reason": "manual"
        }).eq("session_id", session_id)\
          .eq("organization_id", organization_id)\
          .execute()
    
    async def _terminate_session_by_token(self, session_token: str, organization_id: str):
        """Terminate session by token"""
        await self.db.table("user_sessions").update({
            "status": "terminated",
            "terminated_at": datetime.utcnow().isoformat(),
            "termination_reason": "manual"
        }).eq("session_token", session_token)\
          .eq("organization_id", organization_id)\
          .execute()