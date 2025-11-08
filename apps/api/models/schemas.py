"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from uuid import UUID

# ==========================================
# BASE MODELS
# ==========================================

class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

# ==========================================
# CLIENT MODELS
# ==========================================

class ClientCreate(BaseModel):
    """Client creation request"""
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    ssn: Optional[str] = None  # Will be encrypted
    date_of_birth: Optional[date] = None
    street_address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    tags: Optional[List[str]] = []
    notes: Optional[str] = None

class ClientUpdate(BaseModel):
    """Client update request"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=255)
    last_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    street_address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class ClientResponse(BaseModel):
    """Client response"""
    id: UUID
    organization_id: UUID
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    date_of_birth: Optional[date]
    street_address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    status: str
    tags: List[str]
    notes: Optional[str]
    onboarding_completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ==========================================
# DISPUTE MODELS
# ==========================================

class DisputeCreate(BaseModel):
    """Dispute creation request"""
    client_id: UUID
    dispute_type: str = Field(..., description="inquiry, charge_off, late_payment, collection, etc.")
    bureau: str = Field(..., description="equifax, experian, transunion, all")
    account_name: Optional[str] = Field(None, max_length=255)
    account_number: Optional[str] = None  # Will be encrypted
    dispute_reason: str = Field(..., min_length=10)
    letter_template_id: Optional[str] = None

class DisputeUpdate(BaseModel):
    """Dispute update request"""
    dispute_type: Optional[str] = None
    bureau: Optional[str] = None
    account_name: Optional[str] = None
    dispute_reason: Optional[str] = None
    status: Optional[str] = None
    result: Optional[str] = None
    result_notes: Optional[str] = None

class DisputeResponse(BaseModel):
    """Dispute response"""
    id: UUID
    organization_id: UUID
    client_id: UUID
    dispute_type: str
    bureau: str
    account_name: Optional[str]
    dispute_reason: str
    status: str
    round_number: int
    letter_template_id: Optional[str]
    generated_at: Optional[datetime]
    sent_at: Optional[datetime]
    result: Optional[str]
    result_date: Optional[date]
    result_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ==========================================
# LETTER MODELS
# ==========================================

class LetterCreate(BaseModel):
    """Letter creation request"""
    client_id: UUID
    dispute_id: Optional[UUID] = None
    letter_type: str = Field(..., description="dispute, followup, confirmation, general")
    template_id: Optional[str] = None
    content: str
    recipient_name: str
    recipient_address: str

class LetterResponse(BaseModel):
    """Letter response"""
    id: UUID
    organization_id: UUID
    client_id: UUID
    dispute_id: Optional[UUID]
    letter_type: str
    template_id: Optional[str]
    status: str
    recipient_name: str
    mail_provider: Optional[str]
    tracking_number: Optional[str]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    expected_delivery_date: Optional[date]
    cost_cents: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==========================================
# AGREEMENT MODELS
# ==========================================

class AgreementCreate(BaseModel):
    """Agreement creation request"""
    client_id: UUID
    agreement_type: str = Field(..., description="service_agreement, authorization, terms_of_service")
    agreement_version: str
    content: str
    signed_by_name: str
    signed_by_email: EmailStr

class AgreementResponse(BaseModel):
    """Agreement response"""
    id: UUID
    organization_id: UUID
    client_id: UUID
    agreement_type: str
    agreement_version: str
    status: str
    signed_at: Optional[datetime]
    signed_by_name: Optional[str]
    signed_by_email: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==========================================
# BILLING MODELS
# ==========================================

class SubscriptionCreate(BaseModel):
    """Subscription creation request"""
    plan_name: str
    billing_interval: str = Field(..., description="month or year")
    payment_method_id: Optional[str] = None  # Stripe payment method ID (optional for incomplete payment flow)

class SubscriptionResponse(BaseModel):
    """Subscription response"""
    id: UUID
    organization_id: UUID
    stripe_subscription_id: Optional[str]
    plan_name: str
    plan_price_cents: int
    billing_interval: str
    status: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class InvoiceResponse(BaseModel):
    """Invoice response"""
    id: UUID
    organization_id: UUID
    stripe_invoice_id: Optional[str]
    amount_cents: int
    amount_paid_cents: int
    currency: str
    status: str
    invoice_date: date
    due_date: Optional[date]
    paid_at: Optional[datetime]
    description: Optional[str]
    invoice_pdf_url: Optional[str]
    attempt_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==========================================
# AUTH MODELS
# ==========================================

class OrganizationCreate(BaseModel):
    """Organization creation request"""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100)

class OrganizationResponse(BaseModel):
    """Organization response"""
    id: UUID
    name: str
    slug: str
    subscription_tier: str
    subscription_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    """User response"""
    id: UUID
    clerk_user_id: str
    email: str
    full_name: Optional[str]
    role: str
    organization_id: Optional[UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==========================================
# LIST RESPONSES
# ==========================================

class PaginatedResponse(BaseModel):
    """Paginated list response"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

class ClientListResponse(BaseModel):
    """Client list response"""
    items: List[ClientResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class DisputeListResponse(BaseModel):
    """Dispute list response"""
    items: List[DisputeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class LetterListResponse(BaseModel):
    """Letter list response"""
    items: List[LetterResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==========================================
# EMAIL TEMPLATE MODELS
# ==========================================

class EmailTemplateCreate(BaseModel):
    """Email template creation request"""
    name: str = Field(..., min_length=1, max_length=255)
    template_key: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: str = Field(..., description="client_communication, internal_notification, billing")
    subject: str = Field(..., min_length=1, max_length=500)
    body_html: str = Field(..., min_length=1)
    body_text: Optional[str] = None
    is_active: bool = True

class EmailTemplateUpdate(BaseModel):
    """Email template update request"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=500)
    body_html: Optional[str] = Field(None, min_length=1)
    body_text: Optional[str] = None
    is_active: Optional[bool] = None

class EmailTemplateResponse(BaseModel):
    """Email template response"""
    id: UUID
    organization_id: UUID
    name: str
    template_key: str
    description: Optional[str]
    category: str
    subject: str
    body_html: str
    body_text: Optional[str]
    variables: List[str]
    is_active: bool
    is_system_template: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class EmailTemplateListResponse(BaseModel):
    """Email template list response"""
    items: List[EmailTemplateResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# ==========================================
# EMAIL LOG MODELS
# ==========================================

class EmailLogResponse(BaseModel):
    """Email log response"""
    id: UUID
    organization_id: UUID
    client_id: Optional[UUID]
    dispute_id: Optional[UUID]
    template_id: Optional[UUID]
    template_key: Optional[str]
    to_email: str
    to_name: Optional[str]
    subject: str
    status: str
    provider: Optional[str]
    provider_message_id: Optional[str]
    queued_at: datetime
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    opened_at: Optional[datetime]
    bounce_reason: Optional[str]
    error_message: Optional[str]
    open_count: int
    click_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class EmailLogListResponse(BaseModel):
    """Email log list response"""
    items: List[EmailLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class EmailAnalyticsResponse(BaseModel):
    """Email analytics summary"""
    total_sent: int
    total_delivered: int
    total_bounced: int
    total_opened: int
    total_clicked: int
    delivery_rate: float
    open_rate: float
    click_rate: float
    bounce_rate: float

# ==========================================
# NOTIFICATION SETTINGS MODELS
# ==========================================

class NotificationSettingsUpdate(BaseModel):
    """Notification settings update request"""
    client_onboarding_enabled: Optional[bool] = None
    client_dispute_updates_enabled: Optional[bool] = None
    client_payment_reminders_enabled: Optional[bool] = None
    client_monthly_reports_enabled: Optional[bool] = None
    admin_new_client_alert: Optional[bool] = None
    admin_payment_failed_alert: Optional[bool] = None
    admin_dispute_milestone_alert: Optional[bool] = None
    admin_system_alerts_enabled: Optional[bool] = None
    admin_emails: Optional[List[str]] = None
    daily_digest_enabled: Optional[bool] = None
    max_emails_per_day: Optional[int] = None
    max_emails_per_client_per_day: Optional[int] = None

class NotificationSettingsResponse(BaseModel):
    """Notification settings response"""
    id: UUID
    organization_id: UUID
    client_onboarding_enabled: bool
    client_dispute_updates_enabled: bool
    client_payment_reminders_enabled: bool
    client_monthly_reports_enabled: bool
    admin_new_client_alert: bool
    admin_payment_failed_alert: bool
    admin_dispute_milestone_alert: bool
    admin_system_alerts_enabled: bool
    admin_emails: List[str]
    daily_digest_enabled: bool
    max_emails_per_day: int
    max_emails_per_client_per_day: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ==========================================
# EMAIL SEND MODELS
# ==========================================

class EmailSendRequest(BaseModel):
    """Email send request"""
    template_key: str
    to_email: str
    to_name: Optional[str] = None
    variables: Dict[str, Any] = {}
    cc_emails: Optional[List[str]] = None
    bcc_emails: Optional[List[str]] = None
    client_id: Optional[UUID] = None
    dispute_id: Optional[UUID] = None

class EmailSendResponse(BaseModel):
    """Email send response"""
    success: bool
    message: str
    email_log_id: Optional[UUID] = None
    status: Optional[str] = None

# ==========================================
# AUTOMATION MODELS
# ==========================================

class LetterTemplateCreate(BaseModel):
    """Letter template creation request"""
    name: str = Field(..., min_length=1, max_length=255)
    template_key: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    dispute_types: List[str] = Field(..., description="List of dispute types this template applies to")
    bureau_targets: List[str] = Field(..., description="List of bureaus this template works with")
    content: str = Field(..., min_length=1)
    variables: List[str] = Field(..., description="List of variables used in template")
    is_active: bool = True
    priority: int = Field(default=0, description="Higher numbers = higher priority")
    round_optimized: bool = Field(default=False, description="Template optimized for specific rounds")

class LetterTemplateUpdate(BaseModel):
    """Letter template update request"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    dispute_types: Optional[List[str]] = None
    bureau_targets: Optional[List[str]] = None
    content: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    round_optimized: Optional[bool] = None

class LetterTemplateResponse(BaseModel):
    """Letter template response"""
    id: UUID
    organization_id: UUID
    name: str
    template_key: str
    description: Optional[str]
    dispute_types: List[str]
    bureau_targets: List[str]
    content: str
    variables: List[str]
    is_active: bool
    priority: int
    round_optimized: bool
    usage_count: int
    success_rate: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class BureauTargetingRule(BaseModel):
    """Bureau targeting rule for dispute automation"""
    id: Optional[UUID] = None
    name: str
    rule_type: str = Field(..., description="dispute_type_based, account_based, client_history_based")
    criteria: Dict[str, Any] = Field(..., description="Rule criteria and conditions")
    recommended_bureaus: List[str] = Field(..., description="Recommended bureau targets")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in recommendation")
    success_history: int = Field(default=0, description="Number of successful applications")
    is_active: bool = True

class AutomatedSchedulingRule(BaseModel):
    """Automated scheduling rule for dispute rounds"""
    id: Optional[UUID] = None
    name: str
    round_number: int = Field(..., ge=1, le=12, description="Which round this rule applies to")
    min_wait_days: int = Field(default=30, description="Minimum days between rounds")
    max_wait_days: int = Field(default=45, description="Maximum days between rounds")
    follow_up_strategy: str = Field(..., description="aggressive, standard, conservative")
    auto_schedule: bool = True
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Conditions for scheduling")
    is_active: bool = True

class PaymentRetryConfig(BaseModel):
    """Payment retry configuration"""
    id: Optional[UUID] = None
    name: str
    strategy: str = Field(..., description="exponential, linear, fixed")
    initial_delay_hours: int = Field(default=24, description="Hours to wait after initial failure")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    success_threshold: float = Field(default=0.5, description="Success rate threshold for strategy")
    amount_tiers: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Different strategies for different amount tiers"
    )
    is_active: bool = True

class DunningEmailSequence(BaseModel):
    """Dunning email sequence configuration"""
    id: Optional[UUID] = None
    name: str
    step_number: int = Field(..., ge=1, le=10, description="Step in the sequence")
    delay_hours: int = Field(..., ge=0, description="Hours after previous step or failure")
    email_template_key: str = Field(..., description="Template to use for this step")
    subject_template: str = Field(..., description="Subject line for email")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Conditions to trigger this step")
    is_final: bool = Field(default=False, description="Is this the final step before escalation")
    escalation_action: Optional[str] = None
    is_active: bool = True

class LeadScoringCriteria(BaseModel):
    """Lead scoring criteria"""
    criteria_type: str = Field(..., description="email_domain, phone_format, address_validity, etc.")
    weight: float = Field(..., ge=0, le=10, description="Weight of this criteria in scoring")
    positive_values: List[str] = Field(default_factory=list, description="Values that add points")
    negative_values: List[str] = Field(default_factory=list, description="Values that subtract points")
    regex_pattern: Optional[str] = None
    threshold_score: float = Field(default=0, description="Minimum score to pass this criteria")

class LeadScoringProfile(BaseModel):
    """Lead scoring profile"""
    id: Optional[UUID] = None
    name: str
    description: Optional[str]
    criteria: List[LeadScoringCriteria] = Field(..., description="Scoring criteria")
    auto_qualify_threshold: float = Field(default=7.0, ge=0, le=10, description="Score to auto-qualify leads")
    require_review_threshold: float = Field(default=5.0, ge=0, le=10, description="Score requiring manual review")
    disqualify_threshold: float = Field(default=3.0, ge=0, le=10, description="Score to auto-disqualify leads")
    is_default: bool = False
    is_active: bool = True

class LeadScoringRequest(BaseModel):
    """Lead scoring request"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    lead_source: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

class LeadScoringResult(BaseModel):
    """Lead scoring result"""
    lead_id: Optional[UUID] = None
    score: float = Field(ge=0, le=10, description="Total score out of 10")
    breakdown: Dict[str, float] = Field(default_factory=dict, description="Score breakdown by criteria")
    qualification_status: str = Field(..., description="auto_qualified, review_required, auto_disqualified, manual_review")
    recommended_actions: List[str] = Field(default_factory=list)
    confidence_level: float = Field(ge=0, le=1, description="Confidence in scoring")
    scoring_profile_used: str
    created_at: datetime

class ChurnPredictionRequest(BaseModel):
    """Churn prediction request"""
    organization_id: UUID
    client_ids: Optional[List[UUID]] = None
    prediction_horizon_days: int = Field(default=30, ge=7, le=180, description="Days ahead to predict")
    include_factors: bool = True
    include_recommendations: bool = True

class ChurnRiskFactor(BaseModel):
    """Individual churn risk factor"""
    factor_name: str
    description: str
    weight: float
    current_value: Union[str, int, float, bool]
    risk_level: str  # "low", "medium", "high", "critical"
    impact_score: float  # How much this factor contributes to risk

class ChurnPredictionResult(BaseModel):
    """Churn prediction result"""
    client_id: UUID
    churn_probability: float = Field(ge=0, le=1, description="Probability of churn (0-1)")
    risk_level: str = Field(description="low, medium, high, critical")
    prediction_date: date
    factors: List[ChurnRiskFactor] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0, le=1, description="Confidence in prediction")
    last_updated: datetime

class ChurnPredictionResponse(BaseModel):
    """Churn prediction response"""
    organization_id: UUID
    prediction_date: date
    horizon_days: int
    total_clients: int
    high_risk_clients: int
    medium_risk_clients: int
    low_risk_clients: int
    predictions: List[ChurnPredictionResult]
    summary_statistics: Dict[str, Any]
    generated_at: datetime

# ==========================================
# SECURITY ENHANCEMENT MODELS
# ==========================================

class MFAConfig(BaseModel):
    """MFA configuration"""
    id: Optional[UUID] = None
    organization_id: UUID
    mfa_method: str = Field(description="totp, sms, email, authenticator_app")
    is_required: bool = False
    is_enabled: bool = True
    backup_codes: Optional[List[str]] = None
    trusted_devices: List[str] = Field(default_factory=list)
    max_backup_codes: int = Field(default=10, ge=1, le=20)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SSOSettings(BaseModel):
    """SSO configuration"""
    id: Optional[UUID] = None
    organization_id: UUID
    provider: str = Field(description="google, microsoft, okta, auth0, custom")
    is_enabled: bool = False
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    authority: Optional[str] = None
    scopes: List[str] = Field(default_factory=lambda: ["openid", "profile", "email"])
    domain_restrictions: List[str] = Field(default_factory=list)
    auto_provision_users: bool = True
    default_role: str = Field(default="member")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SecurityEventType(BaseModel):
    """Security event type definition"""
    event_type: str
    description: str
    severity: str  # "low", "medium", "high", "critical"
    auto_respond: bool = False
    notification_channels: List[str] = Field(default_factory=list)
    retention_days: int = Field(default=90)
    escalation_rules: Dict[str, Any] = Field(default_factory=dict)

class SecurityIncident(BaseModel):
    """Security incident report"""
    id: Optional[UUID] = None
    organization_id: UUID
    incident_type: str
    severity: str
    title: str
    description: str
    reported_by: UUID
    affected_users: List[UUID] = Field(default_factory=list)
    affected_systems: List[str] = Field(default_factory=list)
    status: str = Field(default="open", description="open, investigating, resolved, closed")
    resolution: Optional[str] = None
    resolved_by: Optional[UUID] = None
    resolution_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SessionConfig(BaseModel):
    """Session management configuration"""
    id: Optional[UUID] = None
    organization_id: UUID
    max_session_duration_hours: int = Field(default=8, ge=1, le=168)
    max_concurrent_sessions: int = Field(default=3, ge=1, le=10)
    session_timeout_warn_minutes: int = Field(default=15, ge=5, le=60)
    enforce_device_trust: bool = False
    require_fresh_login: bool = False
    ip_whitelist: List[str] = Field(default_factory=list)
    geo_restrictions: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
