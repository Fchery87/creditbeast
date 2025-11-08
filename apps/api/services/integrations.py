"""
Third-Party Integration Service
Handle credit bureau APIs, marketing automation, and CRM integrations
"""

import uuid
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import aiohttp
import asyncio

from models.integrations import (
    ThirdPartyIntegration, CreditBureauRequest, CreditBureauResponse,
    DisputeSubmission, CreditReportRequest, BankAccountVerification,
    IncomeVerification, EmailCampaign, LeadScore, ContactSync,
    CRMContact, CRMActivity, CRMDeal, IntegrationSetupRequest,
    IntegrationTestRequest, WebhookPayload, IntegrationType, Bureau,
    IntegrationStatus, DisputeStatus, IntegrationValidationRequest,
    IntegrationValidationResponse
)
from services.database import db

logger = logging.getLogger(__name__)


class IntegrationsService:
    """Service for managing third-party integrations"""

    def __init__(self):
        self.db = None
        self.active_integrations: Dict[str, ThirdPartyIntegration] = {}

    async def setup_integration(
        self, 
        org_id: str, 
        setup_request: IntegrationSetupRequest
    ) -> ThirdPartyIntegration:
        """Set up a new third-party integration"""
        try:
            integration_id = str(uuid.uuid4())
            
            integration = ThirdPartyIntegration(
                id=integration_id,
                organization_id=org_id,
                name=setup_request.name,
                type=setup_request.type,
                provider=setup_request.provider,
                status=IntegrationStatus.PENDING_SETUP,
                config=setup_request.config,
                credentials=setup_request.credentials,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Validate integration setup
            validation = await self.validate_integration_setup(setup_request)
            if not validation.is_valid:
                raise ValueError(f"Integration validation failed: {', '.join(validation.errors)}")
            
            # Test connection
            test_result = await self.test_integration_connection(integration)
            if not test_result.get('success', False):
                integration.status = IntegrationStatus.ERROR
            else:
                integration.status = IntegrationStatus.ACTIVE
            
            # Store integration (in real implementation, would save to database)
            self.active_integrations[integration_id] = integration
            
            logger.info(f"Integration {setup_request.provider} set up for organization {org_id}")
            return integration
            
        except Exception as e:
            logger.error(f"Error setting up integration: {e}")
            raise

    async def validate_integration_setup(
        self, 
        setup_request: IntegrationSetupRequest
    ) -> IntegrationValidationResponse:
        """Validate integration setup configuration"""
        try:
            errors = []
            warnings = []
            test_results = {}
            
            # Validate based on provider type
            if setup_request.provider in ['equifax', 'experian', 'transunion']:
                # Credit bureau validation
                if 'api_key' not in (setup_request.credentials or {}):
                    errors.append("API key is required for credit bureau integrations")
                if 'client_id' not in (setup_request.credentials or {}):
                    errors.append("Client ID is required for credit bureau integrations")
                
                test_results['api_endpoint'] = "https://api.creditbureau.com"
                test_results['auth_method'] = "OAuth 2.0"
                
            elif setup_request.provider in ['salesforce', 'hubspot', 'pipedrive']:
                # CRM validation
                if 'api_key' not in (setup_request.credentials or {}):
                    errors.append("API key is required for CRM integrations")
                if 'instance_url' not in (setup_request.config or {}):
                    warnings.append("Instance URL not provided - using default")
                
                test_results['api_endpoint'] = "https://api.crm.com"
                test_results['auth_method'] = "API Key + OAuth"
                
            elif setup_request.provider in ['mailchimp', 'constant_contact']:
                # Marketing automation validation
                if 'api_key' not in (setup_request.credentials or {}):
                    errors.append("API key is required for marketing automation")
                if 'list_id' not in (setup_request.config or {}):
                    warnings.append("No default list configured")
                
                test_results['api_endpoint'] = "https://api.marketing.com"
                test_results['auth_method'] = "API Key"
                
            elif setup_request.provider in ['plaid', 'yodlee']:
                # Banking validation
                if 'client_id' not in (setup_request.credentials or {}):
                    errors.append("Client ID is required for banking integrations")
                if 'client_secret' not in (setup_request.credentials or {}):
                    errors.append("Client secret is required for banking integrations")
                
                test_results['api_endpoint'] = "https://api.banking.com"
                test_results['auth_method'] = "OAuth 2.0"
                test_results['security_level'] = "Bank-grade encryption"
            
            return IntegrationValidationResponse(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                test_results=test_results
            )
            
        except Exception as e:
            logger.error(f"Error validating integration setup: {e}")
            return IntegrationValidationResponse(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[],
                test_results={}
            )

    async def test_integration_connection(
        self, 
        integration: ThirdPartyIntegration
    ) -> Dict[str, Any]:
        """Test connection to third-party service"""
        try:
            # Mock connection test based on provider
            if integration.provider in ['equifax', 'experian', 'transunion']:
                # Test credit bureau API
                return await self._test_credit_bureau_connection(integration)
            elif integration.provider in ['salesforce', 'hubspot']:
                # Test CRM API
                return await self._test_crm_connection(integration)
            elif integration.provider in ['mailchimp']:
                # Test marketing automation API
                return await self._test_marketing_connection(integration)
            elif integration.provider in ['plaid', 'yodlee']:
                # Test banking API
                return await self._test_banking_connection(integration)
            else:
                return {
                    'success': True,
                    'message': f"Mock connection test successful for {integration.provider}",
                    'response_time_ms': 150
                }
                
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return {
                'success': False,
                'error': str(e),
                'response_time_ms': 0
            }

    async def submit_dispute_to_bureau(
        self, 
        integration_id: str, 
        dispute: DisputeSubmission
    ) -> CreditBureauResponse:
        """Submit dispute to credit bureau"""
        try:
            integration = self.active_integrations.get(integration_id)
            if not integration:
                raise ValueError(f"Integration {integration_id} not found")
            
            if integration.type != IntegrationType.CREDIT_BUREAU:
                raise ValueError("Integration is not a credit bureau type")
            
            request_id = str(uuid.uuid4())
            
            # Mock bureau submission
            if integration.provider == 'equifax':
                response = await self._submit_to_equifax(dispute)
            elif integration.provider == 'experian':
                response = await self._submit_to_experian(dispute)
            elif integration.provider == 'transunion':
                response = await self._submit_to_transunion(dispute)
            else:
                raise ValueError(f"Unsupported bureau: {integration.provider}")
            
            # Update integration sync time
            integration.last_sync = datetime.now()
            
            logger.info(f"Dispute submitted to {integration.provider} for client {dispute.client_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error submitting dispute: {e}")
            raise

    async def get_credit_report(
        self, 
        integration_id: str, 
        request: CreditReportRequest
    ) -> CreditBureauResponse:
        """Get credit report from bureau"""
        try:
            integration = self.active_integrations.get(integration_id)
            if not integration:
                raise ValueError(f"Integration {integration_id} not found")
            
            request_id = str(uuid.uuid4())
            
            # Mock credit report retrieval
            mock_report = {
                'score': 720,
                'accounts': [
                    {
                        'type': 'credit_card',
                        'lender': 'Capital One',
                        'balance': 1500,
                        'credit_limit': 5000,
                        'status': 'current'
                    }
                ],
                'inquiries': [
                    {
                        'date': '2025-10-15',
                        'type': 'soft',
                        'lender': 'CreditBeast'
                    }
                ]
            }
            
            response = CreditBureauResponse(
                request_id=request_id,
                bureau=request.bureau,
                status="success",
                response_code="200",
                message="Credit report retrieved successfully",
                data=mock_report,
                timestamp=datetime.now(),
                processing_time_ms=500
            )
            
            logger.info(f"Credit report retrieved from {integration.provider} for client {request.client_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error getting credit report: {e}")
            raise

    async def sync_leads_to_marketing(
        self, 
        integration_id: str, 
        lead_ids: List[str]
    ) -> Dict[str, Any]:
        """Sync leads to marketing automation platform"""
        try:
            integration = self.active_integrations.get(integration_id)
            if not integration:
                raise ValueError(f"Integration {integration_id} not found")
            
            if integration.type != IntegrationType.MARKETING_AUTOMATION:
                raise ValueError("Integration is not a marketing automation type")
            
            # Mock lead sync
            sync_results = {
                'total_leads': len(lead_ids),
                'synced_successfully': len(lead_ids) - 2,  # Mock 2 failures
                'failed_leads': 2,
                'sync_time': datetime.now().isoformat()
            }
            
            logger.info(f"Synced {sync_results['synced_successfully']} leads to {integration.provider}")
            return sync_results
            
        except Exception as e:
            logger.error(f"Error syncing leads to marketing: {e}")
            raise

    async def create_crm_activity(
        self, 
        integration_id: str, 
        activity: CRMActivity
    ) -> Dict[str, Any]:
        """Create activity in CRM system"""
        try:
            integration = self.active_integrations.get(integration_id)
            if not integration:
                raise ValueError(f"Integration {integration_id} not found")
            
            if integration.type != IntegrationType.CRM:
                raise ValueError("Integration is not a CRM type")
            
            # Mock CRM activity creation
            crm_activity_id = f"crm_act_{uuid.uuid4().hex[:8]}"
            
            result = {
                'success': True,
                'crm_activity_id': crm_activity_id,
                'message': f"Activity created in {integration.provider}",
                'created_at': datetime.now().isoformat()
            }
            
            logger.info(f"CRM activity created in {integration.provider} for organization {activity.organization_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating CRM activity: {e}")
            raise

    async def handle_webhook(
        self, 
        integration_id: str, 
        payload: WebhookPayload
    ) -> Dict[str, Any]:
        """Handle webhook from third-party service"""
        try:
            integration = self.active_integrations.get(integration_id)
            if not integration:
                raise ValueError(f"Integration {integration_id} not found")
            
            # Process webhook based on event type and provider
            if payload.event_type == "dispute_status_update":
                return await self._handle_dispute_status_webhook(payload)
            elif payload.event_type == "lead_scored":
                return await self._handle_lead_scored_webhook(payload)
            elif payload.event_type == "contact_created":
                return await self._handle_contact_created_webhook(payload)
            else:
                logger.info(f"Received webhook {payload.event_type} from {integration.provider}")
                return {"success": True, "message": "Webhook processed"}
            
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            raise

    async def get_integration_status(self, org_id: str) -> List[ThirdPartyIntegration]:
        """Get all integrations for organization with status"""
        try:
            org_integrations = [
                integration for integration in self.active_integrations.values()
                if integration.organization_id == org_id
            ]
            
            # Update status of each integration
            for integration in org_integrations:
                await self._update_integration_status(integration)
            
            return org_integrations
            
        except Exception as e:
            logger.error(f"Error getting integration status: {e}")
            raise

    # Private helper methods
    async def _test_credit_bureau_connection(self, integration: ThirdPartyIntegration) -> Dict[str, Any]:
        """Test credit bureau API connection"""
        # Mock API call
        await asyncio.sleep(0.1)  # Simulate network delay
        return {
            'success': True,
            'message': f"Connected to {integration.provider} API",
            'response_time_ms': 120,
            'api_version': 'v2.1',
            'rate_limit_remaining': 9900
        }

    async def _test_crm_connection(self, integration: ThirdPartyIntegration) -> Dict[str, Any]:
        """Test CRM API connection"""
        await asyncio.sleep(0.15)
        return {
            'success': True,
            'message': f"Connected to {integration.provider} CRM",
            'response_time_ms': 180,
            'instance_url': integration.config.get('instance_url', 'https://crm.example.com'),
            'user_count': 25
        }

    async def _test_marketing_connection(self, integration: ThirdPartyIntegration) -> Dict[str, Any]:
        """Test marketing automation API connection"""
        await asyncio.sleep(0.2)
        return {
            'success': True,
            'message': f"Connected to {integration.provider} marketing platform",
            'response_time_ms': 200,
            'list_count': 5,
            'campaign_count': 12
        }

    async def _test_banking_connection(self, integration: ThirdPartyIntegration) -> Dict[str, Any]:
        """Test banking API connection"""
        await asyncio.sleep(0.3)
        return {
            'success': True,
            'message': f"Connected to {integration.provider} banking API",
            'response_time_ms': 250,
            'security_level': 'bank-grade',
            'supported_accounts': ['checking', 'savings', 'credit']
        }

    async def _submit_to_equifax(self, dispute: DisputeSubmission) -> CreditBureauResponse:
        """Submit dispute to Equifax"""
        request_id = str(uuid.uuid4())
        return CreditBureauResponse(
            request_id=request_id,
            bureau=Bureau.EQUIFAX,
            status="submitted",
            response_code="200",
            message="Dispute submitted to Equifax",
            data={"dispute_id": f"EQF_{request_id[:8]}"},
            timestamp=datetime.now(),
            processing_time_ms=300
        )

    async def _submit_to_experian(self, dispute: DisputeSubmission) -> CreditBureauResponse:
        """Submit dispute to Experian"""
        request_id = str(uuid.uuid4())
        return CreditBureauResponse(
            request_id=request_id,
            bureau=Bureau.EXPERIAN,
            status="submitted",
            response_code="200",
            message="Dispute submitted to Experian",
            data={"dispute_id": f"EXP_{request_id[:8]}"},
            timestamp=datetime.now(),
            processing_time_ms=350
        )

    async def _submit_to_transunion(self, dispute: DisputeSubmission) -> CreditBureauResponse:
        """Submit dispute to TransUnion"""
        request_id = str(uuid.uuid4())
        return CreditBureauResponse(
            request_id=request_id,
            bureau=Bureau.TRANSUNION,
            status="submitted",
            response_code="200",
            message="Dispute submitted to TransUnion",
            data={"dispute_id": f"TRU_{request_id[:8]}"},
            timestamp=datetime.now(),
            processing_time_ms=400
        )

    async def _handle_dispute_status_webhook(self, payload: WebhookPayload) -> Dict[str, Any]:
        """Handle dispute status update webhook"""
        dispute_data = payload.event_data
        logger.info(f"Dispute status updated: {dispute_data}")
        return {"success": True, "message": "Dispute status updated"}

    async def _handle_lead_scored_webhook(self, payload: WebhookPayload) -> Dict[str, Any]:
        """Handle lead scored webhook"""
        lead_data = payload.event_data
        logger.info(f"Lead scored: {lead_data}")
        return {"success": True, "message": "Lead scored processed"}

    async def _handle_contact_created_webhook(self, payload: WebhookPayload) -> Dict[str, Any]:
        """Handle contact created webhook"""
        contact_data = payload.event_data
        logger.info(f"Contact created: {contact_data}")
        return {"success": True, "message": "Contact creation processed"}

    async def _update_integration_status(self, integration: ThirdPartyIntegration):
        """Update integration status based on last sync and health checks"""
        if integration.last_sync:
            time_since_sync = datetime.now() - integration.last_sync
            if time_since_sync > timedelta(hours=24):
                # Test connection if last sync was more than 24 hours ago
                test_result = await self.test_integration_connection(integration)
                if not test_result.get('success', False):
                    integration.status = IntegrationStatus.ERROR
                else:
                    integration.status = IntegrationStatus.ACTIVE


# Global integrations service instance
integrations_service = IntegrationsService()