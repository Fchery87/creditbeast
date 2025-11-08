"""
Third-Party Integration models
Credit bureau APIs, marketing automation, and CRM integrations
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class IntegrationType(str, Enum):
    """Types of third-party integrations"""
    CREDIT_BUREAU = "credit_bureau"
    BANKING = "banking"
    MARKETING_AUTOMATION = "marketing_automation"
    CRM = "crm"
    DOCUMENT_PROCESSING = "document_processing"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"
    PAYMENT = "payment"


class Bureau(str, Enum):
    """Credit bureau identifiers"""
    EQUIFAX = "equifax"
    EXPERIAN = "experian"
    TRANSUNION = "transunion"
    ALL = "all"


class IntegrationStatus(str, Enum):
    """Integration status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    ERROR = "error"
    PENDING_SETUP = "pending_setup"


class DisputeStatus(str, Enum):
    """Dispute status from bureaus"""
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    RESPONDED = "responded"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"


# Base Integration Models
class ThirdPartyIntegration(BaseModel):
    """Base integration configuration"""
    id: str
    organization_id: str
    name: str
    type: IntegrationType
    provider: str  # e.g., "equifax", "mailchimp", "salesforce"
    status: IntegrationStatus
    config: Dict[str, Any]
    credentials: Optional[Dict[str, str]] = None  # Encrypted
    webhook_url: Optional[str] = None
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class IntegrationCredential(BaseModel):
    """Encrypted credential storage"""
    key: str
    value: str  # Encrypted
    created_at: datetime
    expires_at: Optional[datetime] = None


# Credit Bureau Integration Models
class CreditBureauRequest(BaseModel):
    """Credit bureau API request"""
    integration_id: str
    client_id: str
    bureau: Bureau
    request_type: str  # "dispute", "credit_report", "monitoring"
    data: Dict[str, Any]
    priority: str = "normal"  # "low", "normal", "high", "urgent"


class CreditBureauResponse(BaseModel):
    """Credit bureau API response"""
    request_id: str
    bureau: Bureau
    status: str
    response_code: Optional[str] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime
    processing_time_ms: int = 0


class DisputeSubmission(BaseModel):
    """Dispute submission to credit bureau"""
    id: str
    client_id: str
    integration_id: str
    bureau: Bureau
    dispute_type: str
    account_info: Dict[str, Any]
    disputed_information: str
    supporting_documents: List[str] = Field(default_factory=list)
    status: DisputeStatus
    submitted_at: datetime
    expected_response_date: Optional[datetime] = None
    response_received: bool = False
    response_data: Optional[Dict[str, Any]] = None


class CreditReportRequest(BaseModel):
    """Request for credit report from bureau"""
    client_id: str
    integration_id: str
    bureau: Bureau
    report_type: str = "full"  # "full", "summary", "score_only"
    include_disputes: bool = False
    monitoring_enabled: bool = False


# Banking Integration Models
class BankAccountVerification(BaseModel):
    """Bank account verification request"""
    id: str
    client_id: str
    integration_id: str
    account_number: str
    routing_number: str
    account_type: str  # "checking", "savings"
    verification_method: str  # "micro_deposits", "plaid", "yodlee"
    status: str  # "pending", "verified", "failed"
    verified_at: Optional[datetime] = None
    account_data: Optional[Dict[str, Any]] = None


class IncomeVerification(BaseModel):
    """Income verification request"""
    id: str
    client_id: str
    integration_id: str
    verification_type: str  # "bank_transaction", "payroll", "tax_document"
    time_period: str  # "3_months", "6_months", "12_months"
    status: str  # "pending", "verified", "failed"
    verified_income: Optional[float] = None
    verification_data: Optional[Dict[str, Any]] = None
    verified_at: Optional[datetime] = None


# Marketing Automation Models
class EmailCampaign(BaseModel):
    """Email campaign configuration"""
    id: str
    organization_id: str
    integration_id: str
    name: str
    subject: str
    content: str
    recipient_list: str  # Campaign ID from provider
    status: str  # "draft", "scheduled", "sending", "sent", "paused"
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    metrics: Dict[str, int] = Field(default_factory=dict)  # opens, clicks, etc.


class LeadScore(BaseModel):
    """Lead scoring configuration"""
    id: str
    organization_id: str
    integration_id: str
    name: str
    criteria: Dict[str, Any]
    score_weights: Dict[str, float]
    auto_action_threshold: float
    status: str  # "active", "inactive"
    created_at: datetime
    updated_at: datetime


class ContactSync(BaseModel):
    """Contact synchronization status"""
    id: str
    organization_id: str
    integration_id: str
    sync_type: str  # "full", "incremental"
    last_sync: Optional[datetime] = None
    records_processed: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_failed: int = 0
    sync_status: str  # "pending", "running", "completed", "failed"
    error_log: List[str] = Field(default_factory=list)


# CRM Integration Models
class CRMContact(BaseModel):
    """CRM contact data"""
    id: str
    external_id: str  # CRM system ID
    crm_system: str  # "salesforce", "hubspot", "pipedrive"
    contact_data: Dict[str, Any]
    last_sync: datetime
    sync_status: str  # "synced", "pending", "failed"


class CRMActivity(BaseModel):
    """CRM activity tracking"""
    id: str
    organization_id: str
    integration_id: str
    contact_id: str
    activity_type: str  # "call", "email", "meeting", "note"
    subject: str
    description: str
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    crm_activity_id: Optional[str] = None


class CRMDeal(BaseModel):
    """CRM deal/pipeline tracking"""
    id: str
    organization_id: str
    integration_id: str
    contact_id: str
    deal_name: str
    amount: Optional[float] = None
    stage: str  # "lead", "qualified", "proposal", "negotiation", "closed_won", "closed_lost"
    close_date: Optional[datetime] = None
    crm_deal_id: Optional[str] = None
    probability: Optional[float] = None


# Integration Response Models
class IntegrationSetupRequest(BaseModel):
    """Request to set up an integration"""
    name: str
    type: IntegrationType
    provider: str
    config: Dict[str, Any]
    credentials: Optional[Dict[str, str]] = None


class IntegrationTestRequest(BaseModel):
    """Test integration connectivity"""
    integration_id: str
    test_type: str  # "connection", "auth", "webhook", "data_sync"


class IntegrationResponse(BaseModel):
    """Generic integration response"""
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class WebhookPayload(BaseModel):
    """Webhook payload from third-party services"""
    integration_id: str
    event_type: str
    event_data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    signature: Optional[str] = None  # Webhook signature for verification


# Request/Response Models for API
class IntegrationConfigRequest(BaseModel):
    """Request to update integration configuration"""
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[IntegrationStatus] = None
    webhook_url: Optional[str] = None


class SyncRequest(BaseModel):
    """Request to sync data with integration"""
    sync_type: str  # "full", "incremental", "specific_records"
    record_ids: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None


class DisputesSyncRequest(BaseModel):
    """Request to sync disputes with credit bureau"""
    disputes: List[DisputeSubmission]
    bureau: Bureau
    priority: str = "normal"


# Validation Models
class IntegrationValidationRequest(BaseModel):
    """Request to validate integration setup"""
    provider: str
    config: Dict[str, Any]
    credentials: Optional[Dict[str, str]] = None


class IntegrationValidationResponse(BaseModel):
    """Response from integration validation"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    test_results: Dict[str, Any] = Field(default_factory=dict)