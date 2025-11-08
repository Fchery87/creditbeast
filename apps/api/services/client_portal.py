"""
Client Self-Service Portal Service
Handle client-facing interface for progress tracking and communication
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from models.client_portal import (
    ClientPortalUser, ClientPortalDocument, ClientPortalCommunication,
    ClientPortalDispute, ClientPortalProgress, ClientPortalBilling,
    ClientPortalDashboard, DocumentType, DocumentStatus, CommunicationType,
    CommunicationDirection, DisputeStatus, ClientPortalLoginRequest,
    DocumentUploadRequest, CommunicationRequest, ClientSettingsUpdate
)
from services.database import db

logger = logging.getLogger(__name__)


class ClientPortalService:
    """Service for managing client self-service portal"""

    def __init__(self):
        self.db = None

    async def authenticate_client(self, email: str, password: str) -> Optional[ClientPortalUser]:
        """Authenticate client and return user info"""
        try:
            # In a real implementation, this would verify credentials against database
            # For now, return mock data based on email
            if email and password:  # Simple validation
                return ClientPortalUser(
                    id=f"client_{email.split('@')[0]}",
                    client_id=f"client_{email.split('@')[0]}",
                    email=email,
                    first_name="John",
                    last_name="Doe",
                    is_active=True,
                    last_login=datetime.now(),
                    created_at=datetime.now() - timedelta(days=30),
                    updated_at=datetime.now()
                )
            return None
        except Exception as e:
            logger.error(f"Error authenticating client {email}: {e}")
            return None

    async def get_client_dashboard(self, client_id: str) -> ClientPortalDashboard:
        """Get complete dashboard data for client"""
        try:
            # Mock data - in real implementation, fetch from database
            user = await self.get_client_user(client_id)
            progress = await self.get_client_progress(client_id)
            disputes = await self.get_client_disputes(client_id)
            communications = await self.get_recent_communications(client_id, limit=5)
            documents = await self.get_client_documents(client_id, limit=10)
            billing = await self.get_client_billing(client_id)
            
            # Generate next steps and urgent items
            next_steps = self._generate_next_steps(disputes, documents, communications)
            urgent_items = self._generate_urgent_items(disputes, documents)
            
            return ClientPortalDashboard(
                user=user,
                progress=progress,
                disputes=disputes,
                recent_communications=communications,
                documents=documents,
                billing=billing,
                next_steps=next_steps,
                urgent_items=urgent_items
            )
        except Exception as e:
            logger.error(f"Error fetching dashboard for client {client_id}: {e}")
            raise

    async def get_client_user(self, client_id: str) -> ClientPortalUser:
        """Get client user information"""
        return ClientPortalUser(
            id=client_id,
            client_id=client_id,
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
            phone="+1-555-0123",
            is_active=True,
            last_login=datetime.now() - timedelta(hours=2),
            created_at=datetime.now() - timedelta(days=30),
            updated_at=datetime.now()
        )

    async def get_client_progress(self, client_id: str) -> ClientPortalProgress:
        """Get client progress summary"""
        return ClientPortalProgress(
            client_id=client_id,
            total_disputes=12,
            active_disputes=3,
            resolved_disputes=9,
            success_rate=75.0,
            credit_score_start=650,
            credit_score_current=710,
            credit_score_change=60,
            documents_needed=[
                "Updated credit report",
                "Recent bank statement"
            ],
            upcoming_actions=[
                "Review new dispute response",
                "Schedule follow-up call",
                "Upload missing documents"
            ],
            last_activity=datetime.now() - timedelta(hours=3),
            next_update_due=datetime.now() + timedelta(days=7)
        )

    async def get_client_disputes(self, client_id: str, limit: Optional[int] = None) -> List[ClientPortalDispute]:
        """Get client's disputes"""
        disputes = [
            ClientPortalDispute(
                id="dispute_1",
                client_id=client_id,
                dispute_type="late_payment",
                bureau="equifax",
                account_name="Capital One Credit Card",
                creditor="Capital One",
                status=DisputeStatus.IN_PROGRESS,
                current_round=1,
                total_rounds=3,
                created_at=datetime.now() - timedelta(days=14),
                last_updated=datetime.now() - timedelta(days=2),
                next_action="Wait for bureau response",
                next_action_date=datetime.now() + timedelta(days=15),
                description="Disputing late payment reporting",
                is_visible_to_client=True
            ),
            ClientPortalDispute(
                id="dispute_2",
                client_id=client_id,
                dispute_type="incorrect_balance",
                bureau="experian",
                account_name="Chase Bank Account",
                creditor="Chase Bank",
                status=DisputeStatus.RESPONSE_RECEIVED,
                current_round=1,
                total_rounds=3,
                created_at=datetime.now() - timedelta(days=21),
                last_updated=datetime.now() - timedelta(days=1),
                next_action="Review bureau response",
                next_action_date=datetime.now() + timedelta(days=3),
                description="Incorrect account balance reporting",
                is_visible_to_client=True
            ),
            ClientPortalDispute(
                id="dispute_3",
                client_id=client_id,
                dispute_type="identity_theft",
                bureau="transunion",
                account_name="Fraudulent Account",
                creditor="Unknown Creditor",
                status=DisputeStatus.RESOLVED_POSITIVE,
                current_round=1,
                total_rounds=1,
                created_at=datetime.now() - timedelta(days=45),
                last_updated=datetime.now() - timedelta(days=5),
                next_action=None,
                next_action_date=None,
                description="Fraudulent account removed from credit report",
                is_visible_to_client=True
            )
        ]
        
        if limit:
            return disputes[:limit]
        return disputes

    async def get_recent_communications(self, client_id: str, limit: int = 10) -> List[ClientPortalCommunication]:
        """Get recent communications for client"""
        communications = [
            ClientPortalCommunication(
                id="comm_1",
                client_id=client_id,
                professional_id="prof_1",
                type=CommunicationType.STATUS_UPDATE,
                direction=CommunicationDirection.PROFESSIONAL_TO_CLIENT,
                subject="Dispute Update",
                message="Your dispute with Equifax has been submitted. We expect a response within 30 days.",
                is_read=True,
                created_at=datetime.now() - timedelta(days=2),
                read_at=datetime.now() - timedelta(days=1),
                attachments=[],
                related_dispute_id="dispute_1"
            ),
            ClientPortalCommunication(
                id="comm_2",
                client_id=client_id,
                professional_id=None,
                type=CommunicationType.MESSAGE,
                direction=CommunicationDirection.CLIENT_TO_PROFESSIONAL,
                subject="Question about timeline",
                message="How long does the typical dispute process take?",
                is_read=False,
                created_at=datetime.now() - timedelta(hours=6),
                read_at=None,
                attachments=[],
                related_dispute_id=None
            ),
            ClientPortalCommunication(
                id="comm_3",
                client_id=client_id,
                professional_id="prof_1",
                type=CommunicationType.DOCUMENT_REQUEST,
                direction=CommunicationDirection.PROFESSIONAL_TO_CLIENT,
                subject="Additional Documents Needed",
                message="Please upload a recent bank statement to help with your dispute.",
                is_read=True,
                created_at=datetime.now() - timedelta(days=5),
                read_at=datetime.now() - timedelta(days=4),
                attachments=[],
                related_dispute_id="dispute_2"
            )
        ]
        
        return communications[:limit]

    async def get_client_documents(self, client_id: str, limit: Optional[int] = None) -> List[ClientPortalDocument]:
        """Get client's documents"""
        documents = [
            ClientPortalDocument(
                id="doc_1",
                client_id=client_id,
                filename="credit_report_2025.pdf",
                original_filename="credit_report_dec_2025.pdf",
                file_size=2048576,  # 2MB
                file_type="application/pdf",
                document_type=DocumentType.CREDIT_REPORT,
                status=DocumentStatus.APPROVED,
                uploaded_at=datetime.now() - timedelta(days=10),
                reviewed_at=datetime.now() - timedelta(days=8),
                reviewed_by="prof_1",
                notes="Original credit report from all three bureaus",
                download_url="/api/client-portal/documents/doc_1/download",
                is_confidential=True
            ),
            ClientPortalDocument(
                id="doc_2",
                client_id=client_id,
                filename="id_verification.jpg",
                original_filename="drivers_license.jpg",
                file_size=512000,  # 512KB
                file_type="image/jpeg",
                document_type=DocumentType.ID_VERIFICATION,
                status=DocumentStatus.PENDING_REVIEW,
                uploaded_at=datetime.now() - timedelta(days=3),
                reviewed_at=None,
                reviewed_by=None,
                notes="ID verification document",
                download_url="/api/client-portal/documents/doc_2/download",
                is_confidential=True
            ),
            ClientPortalDocument(
                id="doc_3",
                client_id=client_id,
                filename="bank_statement_nov.pdf",
                original_filename="chase_statement_nov_2025.pdf",
                file_size=1536000,  # 1.5MB
                file_type="application/pdf",
                document_type=DocumentType.BANK_STATEMENT,
                status=DocumentStatus.PROCESSED,
                uploaded_at=datetime.now() - timedelta(days=7),
                reviewed_at=datetime.now() - timedelta(days=6),
                reviewed_by="prof_1",
                notes="November bank statement for dispute verification",
                download_url="/api/client-portal/documents/doc_3/download",
                is_confidential=True
            )
        ]
        
        if limit:
            return documents[:limit]
        return documents

    async def get_client_billing(self, client_id: str) -> Optional[ClientPortalBilling]:
        """Get client billing information"""
        return ClientPortalBilling(
            client_id=client_id,
            subscription_status="active",
            monthly_fee=99.00,
            next_billing_date=datetime.now() + timedelta(days=15),
            payment_method="Visa ending in 4242",
            invoice_history=[
                {
                    "id": "inv_001",
                    "date": datetime.now() - timedelta(days=30),
                    "amount": 99.00,
                    "status": "paid",
                    "description": "Monthly subscription - December 2025"
                },
                {
                    "id": "inv_002",
                    "date": datetime.now() - timedelta(days=60),
                    "amount": 99.00,
                    "status": "paid",
                    "description": "Monthly subscription - November 2025"
                }
            ],
            payment_upcoming=False,
            payment_overdue=False
        )

    async def upload_document(self, client_id: str, filename: str, file_data: bytes, upload_request: DocumentUploadRequest) -> ClientPortalDocument:
        """Handle document upload from client"""
        try:
            document_id = str(uuid.uuid4())
            
            document = ClientPortalDocument(
                id=document_id,
                client_id=client_id,
                filename=f"{document_id}_{filename}",
                original_filename=filename,
                file_size=len(file_data),
                file_type="application/pdf",  # Would be determined from actual file
                document_type=upload_request.document_type,
                status=DocumentStatus.UPLOADED,
                uploaded_at=datetime.now(),
                reviewed_at=None,
                reviewed_by=None,
                notes=upload_request.description,
                download_url=f"/api/client-portal/documents/{document_id}/download",
                is_confidential=upload_request.is_confidential
            )
            
            logger.info(f"Document uploaded for client {client_id}: {filename}")
            return document
        except Exception as e:
            logger.error(f"Error uploading document for client {client_id}: {e}")
            raise

    async def send_message(self, client_id: str, message_request: CommunicationRequest) -> ClientPortalCommunication:
        """Send message from client to professional"""
        try:
            communication_id = str(uuid.uuid4())
            
            communication = ClientPortalCommunication(
                id=communication_id,
                client_id=client_id,
                professional_id="prof_1",  # Would be determined from client assignment
                type=message_request.type,
                direction=CommunicationDirection.CLIENT_TO_PROFESSIONAL,
                subject=message_request.subject,
                message=message_request.message,
                is_read=False,
                created_at=datetime.now(),
                read_at=None,
                attachments=message_request.attachments,
                related_dispute_id=message_request.related_dispute_id
            )
            
            logger.info(f"Message sent from client {client_id} to professional")
            return communication
        except Exception as e:
            logger.error(f"Error sending message for client {client_id}: {e}")
            raise

    async def mark_communication_read(self, client_id: str, communication_id: str) -> bool:
        """Mark communication as read by client"""
        try:
            # In real implementation, update database
            logger.info(f"Communication {communication_id} marked as read by client {client_id}")
            return True
        except Exception as e:
            logger.error(f"Error marking communication as read: {e}")
            return False

    async def update_client_settings(self, client_id: str, settings: ClientSettingsUpdate) -> ClientPortalUser:
        """Update client portal settings"""
        try:
            current_user = await self.get_client_user(client_id)
            
            # Apply updates
            update_data = settings.dict(exclude_unset=True)
            updated_user = current_user.copy(update=update_data)
            updated_user.updated_at = datetime.now()
            
            logger.info(f"Settings updated for client {client_id}")
            return updated_user
        except Exception as e:
            logger.error(f"Error updating settings for client {client_id}: {e}")
            raise

    async def request_document(self, client_id: str, document_type: str, reason: str) -> CommunicationRequest:
        """Request client to upload specific document"""
        try:
            message = f"We need you to upload a {document_type.replace('_', ' ')}. Reason: {reason}"
            
            return CommunicationRequest(
                type=CommunicationType.DOCUMENT_REQUEST,
                subject=f"Document Request: {document_type.replace('_', ' ').title()}",
                message=message,
                related_dispute_id=None,
                attachments=[]
            )
        except Exception as e:
            logger.error(f"Error requesting document for client {client_id}: {e}")
            raise

    def _generate_next_steps(self, disputes: List[ClientPortalDispute], documents: List[ClientPortalDocument], communications: List[ClientPortalCommunication]) -> List[str]:
        """Generate next steps for client based on current status"""
        next_steps = []
        
        # Check for disputed needing action
        for dispute in disputes:
            if dispute.status == DisputeStatus.RESPONSE_RECEIVED:
                next_steps.append(f"Review response for {dispute.dispute_type} dispute")
            elif dispute.status == DisputeStatus.WAITING_RESPONSE:
                next_steps.append(f"Wait for bureau response on {dispute.dispute_type} dispute")
        
        # Check for pending documents
        pending_docs = [doc for doc in documents if doc.status == DocumentStatus.PENDING_REVIEW]
        if pending_docs:
            next_steps.append("Upload any missing documents")
        
        # Check for unread communications
        unread_msgs = [comm for comm in communications if not comm.is_read]
        if unread_msgs:
            next_steps.append("Review new messages from your credit specialist")
        
        if not next_steps:
            next_steps.append("Continue monitoring your dispute progress")
        
        return next_steps[:5]  # Limit to 5 items

    def _generate_urgent_items(self, disputes: List[ClientPortalDispute], documents: List[ClientPortalDocument]) -> List[str]:
        """Generate urgent items that need immediate attention"""
        urgent_items = []
        
        # Check for overdue responses
        now = datetime.now()
        for dispute in disputes:
            if dispute.next_action_date and dispute.next_action_date < now:
                urgent_items.append(f"URGENT: Response deadline passed for {dispute.dispute_type} dispute")
        
        # Check for rejected documents
        rejected_docs = [doc for doc in documents if doc.status == DocumentStatus.REJECTED]
        for doc in rejected_docs:
            urgent_items.append(f"Document rejected: Please re-upload {doc.document_type.replace('_', ' ')}")
        
        return urgent_items[:3]  # Limit to 3 urgent items


# Global client portal service instance
client_portal_service = ClientPortalService()