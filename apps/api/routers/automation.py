"""
Automation API Router
Advanced automation features for disputes, payments, and lead management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, Optional
from uuid import UUID
from services.automation import (
    LetterGenerationService,
    BureauTargetingService,
    AutomatedSchedulingService,
    PaymentRetryService,
    DunningEmailService
)
from services.database import db
from middleware.auth import get_current_user
from models.schemas import (
    LeadScoringRequest, LeadScoringResult,
    ChurnPredictionRequest, ChurnPredictionResponse
)
from services.lead_scoring import LeadScoringService as LeadScoringServiceClass
from services.churn_prediction import ChurnPredictionService as ChurnPredictionServiceClass
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
letter_service = LetterGenerationService(db)
bureau_service = BureauTargetingService(db)
scheduling_service = AutomatedSchedulingService(db)
payment_service = PaymentRetryService(db)
dunning_service = DunningEmailService(db)
lead_scoring_service = LeadScoringServiceClass(db)
churn_service = ChurnPredictionServiceClass(db)

# ==========================================
# LETTER GENERATION ENDPOINTS
# ==========================================

@router.post("/letters/generate")
async def generate_dispute_letter(
    dispute_id: str,
    template_id: Optional[str] = None,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate dispute letter using templates and client data"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        result = await letter_service.generate_letter(dispute_id, org_id, template_id)
        return {
            "success": True,
            "message": "Letter generated successfully",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error generating letter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# BUREAU TARGETING ENDPOINTS
# ==========================================

@router.post("/disputes/bureau-targeting/recommend")
async def recommend_bureau_targeting(
    dispute_data: Dict[str, Any],
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get bureau targeting recommendations for dispute"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        # Add organization_id to dispute data
        dispute_data["organization_id"] = org_id
        
        # Get client history if available
        client_history = None
        if dispute_data.get("client_id"):
            client_history = await _get_client_history(dispute_data["client_id"], org_id)
        
        result = await bureau_service.recommend_bureaus(dispute_data, client_history)
        return {
            "success": True,
            "message": "Bureau recommendations generated",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error generating bureau recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# AUTOMATED SCHEDULING ENDPOINTS
# ==========================================

@router.post("/disputes/{dispute_id}/schedule-next-round")
async def schedule_next_dispute_round(
    dispute_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Schedule next dispute round based on automation rules"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        result = await scheduling_service.schedule_next_round(dispute_id, org_id)
        return {
            "success": True,
            "message": "Next round scheduled successfully",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error scheduling next round: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# PAYMENT RETRY ENDPOINTS
# ==========================================

@router.post("/payments/{payment_id}/retry-strategy")
async def get_payment_retry_strategy(
    payment_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get smart retry strategy for failed payment"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        result = await payment_service.get_next_retry_strategy(payment_id, org_id)
        return {
            "success": True,
            "message": "Retry strategy calculated",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error calculating retry strategy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# DUNNING EMAIL SEQUENCE ENDPOINTS
# ==========================================

@router.post("/payments/{payment_id}/dunning-sequence")
async def process_dunning_sequence(
    payment_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Process dunning email sequence for failed payment"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        result = await dunning_service.process_dunning_sequence(payment_id, org_id)
        return {
            "success": True,
            "message": "Dunning sequence processed",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error processing dunning sequence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# LEAD SCORING ENDPOINTS
# ==========================================

@router.post("/leads/score")
async def score_lead(
    lead_data: LeadScoringRequest,
    profile_id: Optional[str] = Query(None),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Score and qualify a lead"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        # Convert lead data to dict
        lead_dict = lead_data.dict()
        
        result = await lead_scoring_service.score_lead(lead_dict, org_id, profile_id)
        return {
            "success": True,
            "message": "Lead scored successfully",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error scoring lead: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/leads/scoring-analytics")
async def get_lead_scoring_analytics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get lead scoring analytics and performance metrics"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        from datetime import date
        
        date_range = None
        if start_date and end_date:
            date_range = (date.fromisoformat(start_date), date.fromisoformat(end_date))
        
        result = await lead_scoring_service.get_scoring_analytics(org_id, date_range)
        return {
            "success": True,
            "message": "Analytics retrieved successfully",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error getting lead scoring analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# CHURN PREDICTION ENDPOINTS
# ==========================================

@router.post("/analytics/churn-prediction", response_model=ChurnPredictionResponse)
async def predict_churn(
    request: ChurnPredictionRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate churn predictions for clients"""
    org_id = user.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    try:
        request_dict = request.dict()
        result = await churn_service.predict_churn(request_dict)
        return result
    except Exception as e:
        logger.error(f"Error generating churn predictions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# HELPER FUNCTIONS
# ==========================================

async def _get_client_history(client_id: str, organization_id: str) -> Optional[Dict]:
    """Get client history data for bureau targeting"""
    try:
        # This would fetch actual client history from database
        # For now, return empty dict
        return {}
    except Exception as e:
        logger.error(f"Error getting client history: {e}")
        return None