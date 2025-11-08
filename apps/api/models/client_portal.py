"""
Client Self-Service Portal models
Client-facing interface for progress tracking and document management
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Types of documents clients can upload"""
    CREDIT_REPORT = "credit_report"
    ID_VERIFICATION = "id_verification"
    BANK_STATEMENT = "bank_statement"
    PAY_STUB = "pay_stub"
    DISPUTE_LETTER = "dispute_letter"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Status of uploaded documents"""
    UPLOADED = "uploaded"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSED = "processed"


class CommunicationType(str, Enum):
    """Types of client communications"""
    MESSAGE = "message"
    NOTE = "note"
    STATUS_UPDATE = "status_update"
    DOCUMENT_REQUEST = "document_request"
    APPOINTMENT = "appointment"


class CommunicationDirection(str, Enum):
    """Direction of communication"""
    CLIENT_TO_PROFESSIONAL = "client_to_professional"
    PROFESSIONAL_TO_CLIENT = "professional_to_client"


class DisputeStatus(str, Enum):
    """Status of disputes for client view"""
    IN_PROGRESS = "in_progress"
    WAITING_RESPONSE = "waiting_response"
    RESPONSE_RECEIVED = "response_received"
    RESOLVED_POSITIVE = "resolved_positive"
    RESOLVED_NEGATIVE = "resolved_negative"
    ESCALATED = "escalated"


class ClientPortalUser(BaseModel):
    """Client portal user information"""
    id: str
    client_id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ClientPortalDocument(BaseModel):
    """Document uploaded by client"""
    id: str
    client_id: str
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    document_type: DocumentType
    status: DocumentStatus
    uploaded_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    notes: Optional[str] = None
    download_url: Optional[str] = None
    is_confidential: bool = True


class ClientPortalCommunication(BaseModel):
    """Communication between client and professional"""
    id: str
    client_id: str
    professional_id: Optional[str] = None
    type: CommunicationType
    direction: CommunicationDirection
    subject: Optional[str] = None
    message: str
    is_read: bool = False
    created_at: datetime
    read_at: Optional[datetime] = None
    attachments: List[str] = Field(default_factory=list)
    related_dispute_id: Optional[str] = None


class ClientPortalDispute(BaseModel):
    """Dispute information for client view"""
    id: str
    client_id: str
    dispute_type: str
    bureau: str
    account_name: str
    creditor: str
    status: DisputeStatus
    current_round: int
    total_rounds: int
    created_at: datetime
    last_updated: datetime
    next_action: Optional[str] = None
    next_action_date: Optional[datetime] = None
    description: Optional[str] = None
    is_visible_to_client: bool = True


class ClientPortalProgress(BaseModel):
    """Client's overall progress summary"""
    client_id: str
    total_disputes: int
    active_disputes: int
    resolved_disputes: int
    success_rate: float
    credit_score_start: Optional[int] = None
    credit_score_current: Optional[int] = None
    credit_score_change: Optional[int] = None
    documents_needed: List[str] = Field(default_factory=list)
    upcoming_actions: List[str] = Field(default_factory=list)
    last_activity: Optional[datetime] = None
    next_update_due: Optional[datetime] = None


class ClientPortalBilling(BaseModel):
    """Client billing information for portal"""
    client_id: str
    subscription_status: str
    monthly_fee: float
    next_billing_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    invoice_history: List[Dict[str, Any]] = Field(default_factory=list)
    payment_upcoming: bool = False
    payment_overdue: bool = False


class ClientPortalDashboard(BaseModel):
    """Complete client dashboard data"""
    user: ClientPortalUser
    progress: ClientPortalProgress
    disputes: List[ClientPortalDispute]
    recent_communications: List[ClientPortalCommunication]
    documents: List[ClientPortalDocument]
    billing: Optional[ClientPortalBilling] = None
    next_steps: List[str] = Field(default_factory=list)
    urgent_items: List[str] = Field(default_factory=list)


# Request/Response Models
class ClientPortalLoginRequest(BaseModel):
    """Client portal login request"""
    email: str
    password: str
    remember_me: bool = False


class ClientPortalLoginResponse(BaseModel):
    """Client portal login response"""
    success: bool
    access_token: str
    refresh_token: str
    user: ClientPortalUser
    dashboard: ClientPortalDashboard
    message: Optional[str] = None


class DocumentUploadRequest(BaseModel):
    """Document upload request"""
    document_type: DocumentType
    description: Optional[str] = None
    is_confidential: bool = True


class CommunicationRequest(BaseModel):
    """Send message to professional"""
    type: CommunicationType
    subject: Optional[str] = None
    message: str
    related_dispute_id: Optional[str] = None
    attachments: List[str] = Field(default_factory=list)


class ClientSettingsUpdate(BaseModel):
    """Client portal settings update"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email_notifications: bool = True
    sms_notifications: bool = False
    language: str = "en"
    timezone: str = "UTC"


class ClientPortalResponse(BaseModel):
    """Base response for client portal operations"""
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None


class ClientPortalDocumentsResponse(BaseModel):
    """Response for document operations"""
    success: bool
    documents: List[ClientPortalDocument]
    total_count: int
    message: Optional[str] = None


class ClientPortalDisputesResponse(BaseModel):
    """Response for dispute operations"""
    success: bool
    disputes: List[ClientPortalDispute]
    total_count: int
    active_count: int
    message: Optional[str] = None


class ClientPortalCommunicationsResponse(BaseModel):
    """Response for communication operations"""
    success: bool
    communications: List[ClientPortalCommunication]
    unread_count: int
    message: Optional[str] = None


class ClientPortalDashboardResponse(BaseModel):
    """Response for dashboard data"""
    success: bool
    dashboard: ClientPortalDashboard
    message: Optional[str] = None