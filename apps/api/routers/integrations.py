"""
Third-Party Integrations API Router
Credit bureau APIs, marketing automation, and CRM integrations endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import logging
from models.integrations import (
    IntegrationSetupRequest, IntegrationTestRequest, IntegrationResponse,
    IntegrationConfigRequest, SyncRequest, WebhookPayload,
    DisputeSubmission, CreditReportRequest, CRMActivity,
    DisputesSyncRequest, ThirdPartyIntegration
)
from services.integrations import integrations_service
from middleware.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/integrations", summary="Get Organization Integrations")
async def get_organization_integrations(
    current_user: dict = Depends(get_current_user)
):
    """Get all integrations for the organization"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        integrations = await integrations_service.get_integration_status(org_id)
        
        return {
            "success": True,
            "data": [integration.dict() for integration in integrations],
            "count": len(integrations)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching integrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/integrations/setup", summary="Setup New Integration")
async def setup_integration(
    setup_request: IntegrationSetupRequest,
    current_user: dict = Depends(get_current_user)
):
    """Set up a new third-party integration"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        integration = await integrations_service.setup_integration(org_id, setup_request)
        
        return IntegrationResponse(
            success=True,
            message=f"Integration {setup_request.provider} set up successfully",
            data=integration.dict()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting up integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/integrations/{integration_id}", summary="Update Integration Configuration")
async def update_integration(
    integration_id: str,
    config_request: IntegrationConfigRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update integration configuration"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        # In real implementation, would update database
        return IntegrationResponse(
            success=True,
            message="Integration configuration updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/integrations/{integration_id}/test", summary="Test Integration Connection")
async def test_integration(
    integration_id: str,
    test_request: IntegrationTestRequest,
    current_user: dict = Depends(get_current_user)
):
    """Test integration connection"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        # Get integration
        integrations = await integrations_service.get_integration_status(org_id)
        integration = next((i for i in integrations if i.id == integration_id), None)
        
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        # Test connection
        test_result = await integrations_service.test_integration_connection(integration)
        
        return {
            "success": test_result.get('success', False),
            "message": test_result.get('message', 'Test completed'),
            "data": test_result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/integrations/{integration_id}", summary="Delete Integration")
async def delete_integration(
    integration_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an integration"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        # In real implementation, would delete from database
        return IntegrationResponse(
            success=True,
            message="Integration deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Credit Bureau Integration Endpoints
@router.post("/credit-bureau/disputes/submit", summary="Submit Dispute to Bureau")
async def submit_dispute_to_bureau(
    dispute: DisputeSubmission,
    current_user: dict = Depends(get_current_user)
):
    """Submit dispute to credit bureau"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        # Find credit bureau integration
        integrations = await integrations_service.get_integration_status(org_id)
        bureau_integration = next(
            (i for i in integrations if i.type.value == "credit_bureau"), 
            None
        )
        
        if not bureau_integration:
            raise HTTPException(status_code=404, detail="No credit bureau integration found")
        
        response = await integrations_service.submit_dispute_to_bureau(
            bureau_integration.id, 
            dispute
        )
        
        return {
            "success": True,
            "data": response.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting dispute: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/credit-bureau/credit-report", summary="Get Credit Report")
async def get_credit_report(
    request: CreditReportRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get credit report from bureau"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        # Find credit bureau integration
        integrations = await integrations_service.get_integration_status(org_id)
        bureau_integration = next(
            (i for i in integrations if i.type.value == "credit_bureau"), 
            None
        )
        
        if not bureau_integration:
            raise HTTPException(status_code=404, detail="No credit bureau integration found")
        
        response = await integrations_service.get_credit_report(
            bureau_integration.id, 
            request
        )
        
        return {
            "success": True,
            "data": response.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting credit report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/credit-bureau/disputes/bulk-submit", summary="Bulk Submit Disputes")
async def bulk_submit_disputes(
    sync_request: DisputesSyncRequest,
    current_user: dict = Depends(get_current_user)
):
    """Submit multiple disputes to bureau"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        # Find credit bureau integration
        integrations = await integrations_service.get_integration_status(org_id)
        bureau_integration = next(
            (i for i in integrations if i.type.value == "credit_bureau"), 
            None
        )
        
        if not bureau_integration:
            raise HTTPException(status_code=404, detail="No credit bureau integration found")
        
        # Process bulk submission
        results = []
        for dispute in sync_request.disputes:
            try:
                response = await integrations_service.submit_dispute_to_bureau(
                    bureau_integration.id, 
                    dispute
                )
                results.append({
                    "dispute_id": dispute.id,
                    "success": True,
                    "response": response.dict()
                })
            except Exception as e:
                results.append({
                    "dispute_id": dispute.id,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "data": {
                "total_disputes": len(sync_request.disputes),
                "successful": len([r for r in results if r["success"]]),
                "failed": len([r for r in results if not r["success"]]),
                "results": results
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk submitting disputes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Marketing Automation Endpoints
@router.post("/marketing/leads/sync", summary="Sync Leads to Marketing Platform")
async def sync_leads_to_marketing(
    integration_id: str,
    lead_ids: List[str],
    current_user: dict = Depends(get_current_user)
):
    """Sync leads to marketing automation platform"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        # Verify integration exists and is marketing type
        integrations = await integrations_service.get_integration_status(org_id)
        marketing_integration = next(
            (i for i in integrations if i.id == integration_id and i.type.value == "marketing_automation"), 
            None
        )
        
        if not marketing_integration:
            raise HTTPException(status_code=404, detail="Marketing automation integration not found")
        
        result = await integrations_service.sync_leads_to_marketing(integration_id, lead_ids)
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing leads to marketing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# CRM Integration Endpoints
@router.post("/crm/activities", summary="Create CRM Activity")
async def create_crm_activity(
    integration_id: str,
    activity: CRMActivity,
    current_user: dict = Depends(get_current_user)
):
    """Create activity in CRM system"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        # Verify integration exists and is CRM type
        integrations = await integrations_service.get_integration_status(org_id)
        crm_integration = next(
            (i for i in integrations if i.id == integration_id and i.type.value == "crm"), 
            None
        )
        
        if not crm_integration:
            raise HTTPException(status_code=404, detail="CRM integration not found")
        
        result = await integrations_service.create_crm_activity(integration_id, activity)
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating CRM activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Webhook Endpoints
@router.post("/webhooks/{integration_id}", summary="Handle Integration Webhook")
async def handle_integration_webhook(
    integration_id: str,
    payload: WebhookPayload,
    current_user: dict = Depends(get_current_user)
):
    """Handle webhook from third-party service"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        # Verify integration exists
        integrations = await integrations_service.get_integration_status(org_id)
        integration = next((i for i in integrations if i.id == integration_id), None)
        
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        result = await integrations_service.handle_webhook(integration_id, payload)
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Sync Endpoints
@router.post("/integrations/{integration_id}/sync", summary="Sync Data with Integration")
async def sync_integration_data(
    integration_id: str,
    sync_request: SyncRequest,
    current_user: dict = Depends(get_current_user)
):
    """Sync data with integration"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        # Verify integration exists
        integrations = await integrations_service.get_integration_status(org_id)
        integration = next((i for i in integrations if i.id == integration_id), None)
        
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        # Mock sync process
        sync_result = {
            "sync_type": sync_request.sync_type,
            "records_processed": 0,
            "sync_status": "completed",
            "sync_time": "2025-11-06T21:31:50.216Z"
        }
        
        return {
            "success": True,
            "data": sync_result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing integration data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Utility Endpoints
@router.get("/integrations/available-providers", summary="Get Available Integration Providers")
async def get_available_providers():
    """Get list of available integration providers"""
    try:
        providers = {
            "credit_bureaus": [
                {"id": "equifax", "name": "Equifax", "type": "credit_bureau"},
                {"id": "experian", "name": "Experian", "type": "credit_bureau"},
                {"id": "transunion", "name": "TransUnion", "type": "credit_bureau"}
            ],
            "crm": [
                {"id": "salesforce", "name": "Salesforce", "type": "crm"},
                {"id": "hubspot", "name": "HubSpot", "type": "crm"},
                {"id": "pipedrive", "name": "Pipedrive", "type": "crm"}
            ],
            "marketing_automation": [
                {"id": "mailchimp", "name": "Mailchimp", "type": "marketing_automation"},
                {"id": "constant_contact", "name": "Constant Contact", "type": "marketing_automation"}
            ],
            "banking": [
                {"id": "plaid", "name": "Plaid", "type": "banking"},
                {"id": "yodlee", "name": "Yodlee", "type": "banking"}
            ]
        }
        
        return {
            "success": True,
            "data": providers
        }
    except Exception as e:
        logger.error(f"Error fetching available providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/integrations/{integration_id}/logs", summary="Get Integration Activity Logs")
async def get_integration_logs(
    integration_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get activity logs for integration"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        # Mock logs
        logs = [
            {
                "timestamp": "2025-11-06T20:00:00Z",
                "action": "connection_test",
                "status": "success",
                "message": "Integration connected successfully"
            },
            {
                "timestamp": "2025-11-06T19:30:00Z",
                "action": "data_sync",
                "status": "completed",
                "message": "100 records synced"
            }
        ]
        
        return {
            "success": True,
            "data": {
                "integration_id": integration_id,
                "logs": logs
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching integration logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))