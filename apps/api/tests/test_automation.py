"""
Unit tests for automation features
Tests for letter generation, bureau targeting, scheduling, and other automation services
"""

import pytest
import asyncio
from datetime import datetime, date
from unittest.mock import Mock, AsyncMock
from services.automation import (
    LetterGenerationService,
    BureauTargetingService,
    AutomatedSchedulingService,
    PaymentRetryService,
    DunningEmailService
)
from services.lead_scoring import LeadScoringService
from services.churn_prediction import ChurnPredictionService

class TestLetterGenerationService:
    """Test letter generation automation"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    @pytest.fixture
    def letter_service(self, mock_db):
        return LetterGenerationService(mock_db)
    
    @pytest.mark.asyncio
    async def test_letter_generation_basic(self, letter_service, mock_db):
        """Test basic letter generation"""
        # Mock dispute data
        dispute_data = {
            "id": "dispute-123",
            "client_id": "client-456",
            "dispute_type": "late_payment",
            "bureau": "equifax",
            "account_name": "Test Account",
            "dispute_reason": "Incorrect payment date"
        }
        
        # Mock client data
        client_data = {
            "id": "client-456",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "street_address": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip_code": "12345"
        }
        
        # Mock template
        template = {
            "id": "template-789",
            "name": "Standard Dispute Letter",
            "content": "Dear {{bureau_name}}, I am writing to dispute {{dispute_type}} for account {{account_name}}...",
            "variables": ["bureau_name", "dispute_type", "account_name"]
        }
        
        # Mock database responses
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [dispute_data]
        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [client_data]
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [template]
        mock_db.table.return_value.insert.return_value.execute.return_value.data = [{"id": "letter-999"}]
        
        # Test letter generation
        result = await letter_service.generate_letter("dispute-123", "org-123")
        
        # Assertions
        assert result["letter_id"] == "letter-999"
        assert "John Doe" in result["content"]
        assert "Equifax" in result["content"]
        assert result["template_used"] == "Standard Dispute Letter"
    
    @pytest.mark.asyncio
    async def test_template_selection(self, letter_service, mock_db):
        """Test optimal template selection"""
        dispute_data = {"dispute_type": "late_payment", "bureau": "equifax", "round_number": 2}
        client_data = {}
        
        templates = [
            {"id": "t1", "dispute_types": ["late_payment"], "bureau_targets": ["equifax"], "priority": 10, "success_rate": 0.8},
            {"id": "t2", "dispute_types": ["collection"], "bureau_targets": ["all"], "priority": 5, "success_rate": 0.6}
        ]
        
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = templates
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [templates[0]]
        
        score = await letter_service._calculate_template_score(templates[0], dispute_data, client_data, "org-123")
        assert score > 0  # Should have positive score


class TestBureauTargetingService:
    """Test bureau targeting automation"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    @pytest.fixture
    def bureau_service(self, mock_db):
        return BureauTargetingService(mock_db)
    
    @pytest.mark.asyncio
    async def test_bureau_recommendation_basic(self, bureau_service, mock_db):
        """Test basic bureau recommendation"""
        dispute_data = {
            "dispute_type": "collection",
            "account_name": "Capital One Credit Card",
            "organization_id": "org-123"
        }
        
        # Mock targeting rules
        rules = [
            {
                "rule_type": "dispute_type_based",
                "recommended_bureaus": ["equifax", "experian"],
                "confidence_score": 0.8,
                "criteria": {"dispute_types": ["collection"]},
                "name": "Collection Rule"
            }
        ]
        
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = rules
        
        result = await bureau_service.recommend_bureaus(dispute_data)
        
        assert "equifax" in result["recommended_bureaus"]
        assert "experian" in result["recommended_bureaus"]
        assert result["confidence_score"] > 0.7
        assert result["rule_applied"] == "Collection Rule"


class TestAutomatedSchedulingService:
    """Test automated dispute scheduling"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    @pytest.fixture
    def scheduling_service(self, mock_db):
        return AutomatedSchedulingService(mock_db)
    
    @pytest.mark.asyncio
    async def test_next_round_scheduling(self, scheduling_service, mock_db):
        """Test scheduling next dispute round"""
        dispute_data = {
            "id": "dispute-123",
            "round_number": 1,
            "dispute_type": "late_payment",
            "client_id": "client-456"
        }
        
        # Mock scheduling rule
        rule = {
            "min_wait_days": 25,
            "max_wait_days": 35,
            "follow_up_strategy": "standard",
            "name": "Round 2 Rule"
        }
        
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [dispute_data]
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [rule]
        mock_db.table.return_value.insert.return_value.execute.return_value.data = [{"id": "task-789"}]
        
        result = await scheduling_service.schedule_next_round("dispute-123", "org-123")
        
        assert result["next_round"] == 2
        assert result["rule_applied"] == "Round 2 Rule"
        assert "scheduled_date" in result
        assert 0 < result["estimated_success_probability"] < 1


class TestPaymentRetryService:
    """Test payment retry automation"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    @pytest.fixture
    def payment_service(self, mock_db):
        return PaymentRetryService(mock_db)
    
    @pytest.mark.asyncio
    async def test_retry_strategy_calculation(self, payment_service, mock_db):
        """Test payment retry strategy calculation"""
        payment_data = {
            "id": "payment-123",
            "retry_count": 1,
            "amount_cents": 9900,  # $99
            "organization_id": "org-123"
        }
        
        config = {
            "strategy": "exponential",
            "initial_delay_hours": 24,
            "max_retries": 3,
            "amount_tiers": {
                "medium": {"min_amount": 100, "max_amount": 500, "strategy": "exponential"}
            }
        }
        
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [payment_data]
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [config]
        
        result = await payment_service.get_next_retry_strategy("payment-123", "org-123")
        
        assert result["retry_count"] == 2
        assert result["strategy"] == "exponential"
        assert result["amount_to_charge"] == 9900
        assert result["estimated_success_rate"] > 0
        assert result["estimated_success_rate"] < 1


class TestDunningEmailService:
    """Test dunning email sequence automation"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    @pytest.fixture
    def dunning_service(self, mock_db):
        return DunningEmailService(mock_db)
    
    @pytest.mark.asyncio
    async def test_dunning_sequence_processing(self, dunning_service, mock_db):
        """Test dunning email sequence processing"""
        failed_payment_id = "payment-123"
        organization_id = "org-123"
        
        # Mock sequence state
        sequence_state = {
            "current_step": 0,
            "status": "active",
            "started_at": datetime.utcnow().isoformat()
        }
        
        # Mock next step
        next_step = {
            "step_number": 1,
            "email_template_key": "payment_failed_initial",
            "delay_hours": 24,
            "is_final": False
        }
        
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [sequence_state]
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [next_step]
        mock_db.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        
        result = await dunning_service.process_dunning_sequence(failed_payment_id, organization_id)
        
        assert result["action"] in ["email_sent", "wait"]
        assert result["step_number"] == 1
        assert "email_template" in result


class TestLeadScoringService:
    """Test lead scoring automation"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    @pytest.fixture
    def lead_service(self, mock_db):
        return LeadScoringService(mock_db)
    
    @pytest.mark.asyncio
    async def test_lead_scoring_basic(self, lead_service, mock_db):
        """Test basic lead scoring"""
        lead_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@gmail.com",
            "phone": "555-123-4567",
            "street_address": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip_code": "12345",
            "utm_source": "google"
        }
        
        profile = {
            "id": "profile-123",
            "name": "Default Profile",
            "criteria": [
                {
                    "criteria_type": "email_domain",
                    "weight": 2.0,
                    "positive_values": ["gmail.com"],
                    "negative_values": [],
                    "threshold_score": 1.0
                },
                {
                    "criteria_type": "phone_format",
                    "weight": 1.5,
                    "positive_values": ["valid"],
                    "negative_values": [],
                    "threshold_score": 1.0
                }
            ],
            "auto_qualify_threshold": 7.0,
            "require_review_threshold": 5.0,
            "disqualify_threshold": 3.0
        }
        
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [profile]
        mock_db.table.return_value.insert.return_value.execute.return_value.data = [{"id": "scoring-123"}]
        
        result = await lead_service.score_lead(lead_data, "org-123")
        
        assert result["score"] > 0
        assert result["score"] <= 10
        assert "breakdown" in result
        assert "qualification_status" in result
        assert result["qualification_status"] in ["auto_qualified", "review_required", "manual_review", "auto_disqualified"]


class TestChurnPredictionService:
    """Test churn prediction analytics"""
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    @pytest.fixture
    def churn_service(self, mock_db):
        return ChurnPredictionService(mock_db)
    
    @pytest.mark.asyncio
    async def test_churn_prediction_basic(self, churn_service, mock_db):
        """Test basic churn prediction"""
        client = {
            "id": "client-123",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        
        client_history = {
            "disputes": [],
            "payments": [{"status": "paid", "created_at": datetime.utcnow().isoformat()}],
            "communications": [],
            "documents": []
        }
        
        # Mock database responses
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [client]
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []  # disputes
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = client_history["payments"]
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
        
        result = await churn_service.predict_client_churn(client, "org-123", 30, True, True)
        
        assert 0 <= result["churn_probability"] <= 1
        assert result["risk_level"] in ["low", "medium", "high", "critical"]
        assert "factors" in result
        assert "recommended_actions" in result
        assert 0 <= result["confidence_score"] <= 1