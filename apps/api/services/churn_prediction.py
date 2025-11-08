"""
Churn Prediction Service for CreditBeast
Advanced client churn prediction and prevention analytics
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID
import json
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)

class ChurnPredictionService:
    """Churn prediction and risk analysis service"""
    
    def __init__(self, db_client):
        self.db = db_client
    
    async def predict_churn(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate churn predictions for clients"""
        try:
            organization_id = request_data['organization_id']
            client_ids = request_data.get('client_ids')
            horizon_days = request_data.get('prediction_horizon_days', 30)
            include_factors = request_data.get('include_factors', True)
            include_recommendations = request_data.get('include_recommendations', True)
            
            # Get clients to analyze
            clients = await self._get_clients_for_analysis(organization_id, client_ids)
            if not clients:
                raise ValueError("No clients found for analysis")
            
            # Generate predictions for each client
            predictions = []
            for client in clients:
                prediction = await self._predict_client_churn(
                    client, organization_id, horizon_days, include_factors, include_recommendations
                )
                predictions.append(prediction)
            
            # Calculate summary statistics
            summary_stats = self._calculate_summary_statistics(predictions)
            
            return {
                "organization_id": organization_id,
                "prediction_date": date.today().isoformat(),
                "horizon_days": horizon_days,
                "total_clients": len(clients),
                "high_risk_clients": summary_stats['high_risk_count'],
                "medium_risk_clients": summary_stats['medium_risk_count'],
                "low_risk_clients": summary_stats['low_risk_count'],
                "predictions": predictions,
                "summary_statistics": summary_stats,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating churn predictions: {e}")
            return {
                "organization_id": request_data.get('organization_id', ''),
                "prediction_date": date.today().isoformat(),
                "horizon_days": request_data.get('prediction_horizon_days', 30),
                "total_clients": 0,
                "high_risk_clients": 0,
                "medium_risk_clients": 0,
                "low_risk_clients": 0,
                "predictions": [],
                "summary_statistics": {},
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
    
    async def _get_clients_for_analysis(self, organization_id: str, client_ids: Optional[List[str]]) -> List[Dict]:
        """Get clients for churn analysis"""
        if client_ids:
            # Get specific clients
            result = await self.db.table("clients").select("*")\
                .eq("organization_id", organization_id)\
                .in_("id", client_ids)\
                .eq("status", "active")\
                .execute()
        else:
            # Get all active clients
            result = await self.db.table("clients").select("*")\
                .eq("organization_id", organization_id)\
                .eq("status", "active")\
                .execute()
        
        return result.data or []
    
    async def _predict_client_churn(self, client: Dict, organization_id: str, horizon_days: int, 
                                  include_factors: bool, include_recommendations: bool) -> Dict[str, Any]:
        """Predict churn for a specific client"""
        try:
            # Get client history and activity data
            client_history = await self._get_client_history(client['id'], organization_id)
            
            # Calculate risk factors
            risk_factors = []
            if include_factors:
                risk_factors = await self._analyze_risk_factors(client, client_history)
            
            # Calculate churn probability
            churn_probability = self._calculate_churn_probability(client, client_history, risk_factors)
            
            # Determine risk level
            risk_level = self._determine_risk_level(churn_probability)
            
            # Generate recommendations
            recommended_actions = []
            if include_recommendations:
                recommended_actions = self._generate_recommendations(risk_level, risk_factors, client)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(client_history, risk_factors)
            
            return {
                "client_id": client['id'],
                "client_name": f"{client.get('first_name', '')} {client.get('last_name', '')}".strip(),
                "churn_probability": round(churn_probability, 3),
                "risk_level": risk_level,
                "prediction_date": date.today().isoformat(),
                "horizon_days": horizon_days,
                "factors": risk_factors if include_factors else [],
                "recommended_actions": recommended_actions if include_recommendations else [],
                "confidence_score": round(confidence_score, 3),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting churn for client {client.get('id')}: {e}")
            return {
                "client_id": client['id'],
                "client_name": f"{client.get('first_name', '')} {client.get('last_name', '')}".strip(),
                "churn_probability": 0.5,
                "risk_level": "medium",
                "prediction_date": date.today().isoformat(),
                "horizon_days": horizon_days,
                "factors": [],
                "recommended_actions": ["Manual review required due to prediction error"],
                "confidence_score": 0.1,
                "last_updated": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    async def _get_client_history(self, client_id: str, organization_id: str) -> Dict[str, Any]:
        """Get comprehensive client history for analysis"""
        # Get dispute history
        disputes_result = await self.db.table("disputes").select("*")\
            .eq("client_id", client_id)\
            .eq("organization_id", organization_id)\
            .order("created_at", desc=True)\
            .execute()
        
        # Get payment history
        payments_result = await self.db.table("billing_payments").select("*")\
            .eq("client_id", client_id)\
            .eq("organization_id", organization_id)\
            .order("created_at", desc=True)\
            .execute()
        
        # Get communication history
        communications_result = await self.db.table("email_logs").select("*")\
            .eq("client_id", client_id)\
            .eq("organization_id", organization_id)\
            .order("created_at", desc=True)\
            .limit(50)\
            .execute()
        
        # Get document activity
        documents_result = await self.db.table("documents").select("*")\
            .eq("client_id", client_id)\
            .eq("organization_id", organization_id)\
            .order("created_at", desc=True)\
            .execute()
        
        return {
            "disputes": disputes_result.data or [],
            "payments": payments_result.data or [],
            "communications": communications_result.data or [],
            "documents": documents_result.data or []
        }
    
    async def _analyze_risk_factors(self, client: Dict, client_history: Dict) -> List[Dict]:
        """Analyze various risk factors for churn prediction"""
        risk_factors = []
        
        # 1. Communication Engagement
        engagement_factor = self._analyze_engagement_risk(client_history)
        if engagement_factor:
            risk_factors.append(engagement_factor)
        
        # 2. Payment Behavior
        payment_factor = self._analyze_payment_risk(client_history)
        if payment_factor:
            risk_factors.append(payment_factor)
        
        # 3. Dispute Success Rate
        dispute_factor = self._analyze_dispute_risk(client_history)
        if dispute_factor:
            risk_factors.append(dispute_factor)
        
        # 4. Service Utilization
        utilization_factor = self._analyze_utilization_risk(client_history)
        if utilization_factor:
            risk_factors.append(utilization_factor)
        
        # 5. Tenure and Lifecycle
        tenure_factor = self._analyze_tenure_risk(client, client_history)
        if tenure_factor:
            risk_factors.append(tenure_factor)
        
        # 6. Support Interactions
        support_factor = self._analyze_support_risk(client_history)
        if support_factor:
            risk_factors.append(support_factor)
        
        return risk_factors
    
    def _analyze_engagement_risk(self, client_history: Dict) -> Optional[Dict]:
        """Analyze communication engagement risk"""
        communications = client_history.get('communications', [])
        
        if not communications:
            return {
                "factor_name": "communication_engagement",
                "description": "Client communication and email engagement",
                "weight": 2.0,
                "current_value": "no_data",
                "risk_level": "medium",
                "impact_score": 0.5
            }
        
        # Analyze email engagement
        sent_emails = [c for c in communications if c.get('status') in ['sent', 'delivered']]
        opened_emails = [c for c in communications if c.get('opened_at')]
        clicked_emails = [c for c in communications if c.get('click_count', 0) > 0]
        
        if not sent_emails:
            return {
                "factor_name": "communication_engagement",
                "description": "No email communication recorded",
                "weight": 2.0,
                "current_value": "no_communication",
                "risk_level": "high",
                "impact_score": 0.8
            }
        
        open_rate = len(opened_emails) / len(sent_emails) if sent_emails else 0
        click_rate = len(clicked_emails) / len(sent_emails) if sent_emails else 0
        
        # Recent activity (last 30 days)
        recent_cutoff = datetime.utcnow() - timedelta(days=30)
        recent_communications = [
            c for c in communications 
            if datetime.fromisoformat(c['created_at'].replace('Z', '+00:00')) > recent_cutoff
        ]
        
        if not recent_communications:
            risk_level = "high"
            impact_score = 0.9
            current_value = "no_recent_engagement"
        elif open_rate < 0.2 and click_rate < 0.05:
            risk_level = "medium"
            impact_score = 0.6
            current_value = f"low_engagement_{round(open_rate*100)}%_open"
        else:
            risk_level = "low"
            impact_score = 0.2
            current_value = f"good_engagement_{round(open_rate*100)}%_open"
        
        return {
            "factor_name": "communication_engagement",
            "description": f"Email engagement: {round(open_rate*100)}% open rate, {round(click_rate*100)}% click rate",
            "weight": 2.0,
            "current_value": current_value,
            "risk_level": risk_level,
            "impact_score": impact_score
        }
    
    def _analyze_payment_risk(self, client_history: Dict) -> Optional[Dict]:
        """Analyze payment behavior risk"""
        payments = client_history.get('payments', [])
        
        if not payments:
            return {
                "factor_name": "payment_behavior",
                "description": "No payment history available",
                "weight": 2.5,
                "current_value": "no_history",
                "risk_level": "medium",
                "impact_score": 0.5
            }
        
        # Analyze payment patterns
        failed_payments = [p for p in payments if p.get('status') == 'failed']
        late_payments = [p for p in payments if p.get('status') == 'late']
        successful_payments = [p for p in payments if p.get('status') == 'paid']
        
        total_attempts = len(payments)
        failure_rate = len(failed_payments) / total_attempts if total_attempts > 0 else 0
        
        # Recent payment issues (last 60 days)
        recent_cutoff = datetime.utcnow() - timedelta(days=60)
        recent_failures = [
            p for p in failed_payments
            if datetime.fromisoformat(p['created_at'].replace('Z', '+00:00')) > recent_cutoff
        ]
        
        if recent_failures:
            risk_level = "high"
            impact_score = 0.9
            current_value = f"recent_failures_{len(recent_failures)}"
        elif failure_rate > 0.3:
            risk_level = "high"
            impact_score = 0.8
            current_value = f"high_failure_rate_{round(failure_rate*100)}%"
        elif failure_rate > 0.1:
            risk_level = "medium"
            impact_score = 0.6
            current_value = f"moderate_failure_rate_{round(failure_rate*100)}%"
        else:
            risk_level = "low"
            impact_score = 0.2
            current_value = f"good_payment_history_{round((1-failure_rate)*100)}%_success"
        
        return {
            "factor_name": "payment_behavior",
            "description": f"Payment failure rate: {round(failure_rate*100)}% over {total_attempts} attempts",
            "weight": 2.5,
            "current_value": current_value,
            "risk_level": risk_level,
            "impact_score": impact_score
        }
    
    def _analyze_dispute_risk(self, client_history: Dict) -> Optional[Dict]:
        """Analyze dispute success rate risk"""
        disputes = client_history.get('disputes', [])
        
        if not disputes:
            return {
                "factor_name": "dispute_success",
                "description": "No dispute history available",
                "weight": 1.5,
                "current_value": "no_disputes",
                "risk_level": "low",
                "impact_score": 0.2
            }
        
        # Analyze dispute outcomes
        successful_disputes = [d for d in disputes if d.get('result') == 'success']
        failed_disputes = [d for d in disputes if d.get('result') == 'failed']
        
        success_rate = len(successful_disputes) / len(disputes) if disputes else 0
        
        # Check for pattern of failures
        recent_disputes = disputes[:5]  # Last 5 disputes
        recent_failures = [d for d in recent_disputes if d.get('result') == 'failed']
        
        if len(recent_failures) >= 3:
            risk_level = "high"
            impact_score = 0.8
            current_value = "pattern_of_failures"
        elif success_rate < 0.3:
            risk_level = "high"
            impact_score = 0.7
            current_value = f"low_success_rate_{round(success_rate*100)}%"
        elif success_rate < 0.6:
            risk_level = "medium"
            impact_score = 0.5
            current_value = f"moderate_success_rate_{round(success_rate*100)}%"
        else:
            risk_level = "low"
            impact_score = 0.2
            current_value = f"good_success_rate_{round(success_rate*100)}%"
        
        return {
            "factor_name": "dispute_success",
            "description": f"Dispute success rate: {round(success_rate*100)}% over {len(disputes)} disputes",
            "weight": 1.5,
            "current_value": current_value,
            "risk_level": risk_level,
            "impact_score": impact_score
        }
    
    def _analyze_utilization_risk(self, client_history: Dict) -> Optional[Dict]:
        """Analyze service utilization risk"""
        disputes = client_history.get('disputes', [])
        documents = client_history.get('documents', [])
        
        # Calculate utilization metrics
        total_disputes = len(disputes)
        total_documents = len(documents)
        
        # Recent activity (last 30 days)
        recent_cutoff = datetime.utcnow() - timedelta(days=30)
        recent_activity = [
            d for d in disputes + documents
            if datetime.fromisoformat(d['created_at'].replace('Z', '+00:00')) > recent_cutoff
        ]
        
        if not recent_activity:
            risk_level = "high"
            impact_score = 0.8
            current_value = "no_recent_activity"
        elif len(recent_activity) == 1:
            risk_level = "medium"
            impact_score = 0.6
            current_value = "low_recent_activity"
        elif len(recent_activity) <= 3:
            risk_level = "low"
            impact_score = 0.3
            current_value = "moderate_recent_activity"
        else:
            risk_level = "low"
            impact_score = 0.1
            current_value = "high_recent_activity"
        
        return {
            "factor_name": "service_utilization",
            "description": f"Service activity: {len(recent_activity)} activities in last 30 days",
            "weight": 1.0,
            "current_value": current_value,
            "risk_level": risk_level,
            "impact_score": impact_score
        }
    
    def _analyze_tenure_risk(self, client: Dict, client_history: Dict) -> Optional[Dict]:
        """Analyze client tenure and lifecycle risk"""
        created_at = client.get('created_at')
        if not created_at:
            return None
        
        client_start = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        days_since_start = (datetime.utcnow() - client_start).days
        
        # Risk based on tenure
        if days_since_start < 30:
            # New clients - higher risk
            risk_level = "medium"
            impact_score = 0.6
            current_value = f"new_client_{days_since_start}_days"
        elif days_since_start < 90:
            # Early stage - moderate risk
            risk_level = "medium"
            impact_score = 0.4
            current_value = f"early_stage_{days_since_start}_days"
        elif days_since_start > 365:
            # Long-term clients - lower risk if satisfied
            risk_level = "low"
            impact_score = 0.2
            current_value = f"long_term_{days_since_start}_days"
        else:
            # Established clients
            risk_level = "low"
            impact_score = 0.3
            current_value = f"established_{days_since_start}_days"
        
        return {
            "factor_name": "client_tenure",
            "description": f"Client tenure: {days_since_start} days",
            "weight": 1.0,
            "current_value": current_value,
            "risk_level": risk_level,
            "impact_score": impact_score
        }
    
    def _analyze_support_risk(self, client_history: Dict) -> Optional[Dict]:
        """Analyze support interaction risk"""
        communications = client_history.get('communications', [])
        
        # Count support-related communications
        support_indicators = ['support', 'help', 'issue', 'problem', 'complaint', 'frustrated']
        support_contacts = []
        
        for comm in communications:
            subject = comm.get('subject', '').lower()
            body = comm.get('body_text', '').lower()
            combined_text = f"{subject} {body}"
            
            if any(indicator in combined_text for indicator in support_indicators):
                support_contacts.append(comm)
        
        recent_support = [
            c for c in support_contacts
            if datetime.fromisoformat(c['created_at'].replace('Z', '+00:00')) > 
            (datetime.utcnow() - timedelta(days=30))
        ]
        
        if len(recent_support) >= 3:
            risk_level = "high"
            impact_score = 0.8
            current_value = f"frequent_support_{len(recent_support)}_recent"
        elif len(recent_support) >= 1:
            risk_level = "medium"
            impact_score = 0.5
            current_value = f"some_support_{len(recent_support)}_recent"
        else:
            risk_level = "low"
            impact_score = 0.2
            current_value = "minimal_support_issues"
        
        return {
            "factor_name": "support_interactions",
            "description": f"Support contacts: {len(recent_support)} in last 30 days",
            "weight": 1.5,
            "current_value": current_value,
            "risk_level": risk_level,
            "impact_score": impact_score
        }
    
    def _calculate_churn_probability(self, client: Dict, client_history: Dict, risk_factors: List[Dict]) -> float:
        """Calculate churn probability based on risk factors"""
        if not risk_factors:
            return 0.5  # Default medium probability
        
        # Calculate weighted risk score
        total_weighted_risk = 0.0
        total_weight = 0.0
        
        for factor in risk_factors:
            weight = factor.get('weight', 1.0)
            impact_score = factor.get('impact_score', 0.5)
            
            # Convert impact score to risk contribution
            risk_contribution = impact_score * weight
            total_weighted_risk += risk_contribution
            total_weight += weight
        
        if total_weight == 0:
            return 0.5
        
        # Normalize to 0-1 probability
        normalized_risk = total_weighted_risk / total_weight
        
        # Apply sigmoid function to get probability
        import math
        probability = 1 / (1 + math.exp(-6 * (normalized_risk - 0.5)))
        
        return max(0.0, min(1.0, probability))
    
    def _determine_risk_level(self, churn_probability: float) -> str:
        """Determine risk level based on churn probability"""
        if churn_probability >= 0.7:
            return "critical"
        elif churn_probability >= 0.5:
            return "high"
        elif churn_probability >= 0.3:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, risk_level: str, risk_factors: List[Dict], client: Dict) -> List[str]:
        """Generate specific recommendations for risk mitigation"""
        recommendations = []
        
        # Risk level-based recommendations
        if risk_level in ["critical", "high"]:
            recommendations.append("Immediate outreach required - schedule personal call within 24 hours")
            recommendations.append("Offer special retention incentives or service upgrades")
            recommendations.append("Escalate to account management team")
        
        elif risk_level == "medium":
            recommendations.append("Proactive check-in within 1 week")
            recommendations.append("Send targeted value-add content or resources")
            recommendations.append("Review service satisfaction and address concerns")
        
        # Factor-specific recommendations
        for factor in risk_factors:
            factor_name = factor.get('factor_name', '')
            risk_level = factor.get('risk_level', 'medium')
            
            if factor_name == "communication_engagement" and risk_level in ["high", "critical"]:
                recommendations.append("Implement multi-channel communication strategy")
                recommendations.append("Personalize email content based on client interests")
            
            elif factor_name == "payment_behavior" and risk_level in ["high", "critical"]:
                recommendations.append("Offer flexible payment options or payment plans")
                recommendations.append("Provide financial education resources")
                recommendations.append("Consider service tier adjustment")
            
            elif factor_name == "dispute_success" and risk_level in ["high", "critical"]:
                recommendations.append("Review dispute strategy and set realistic expectations")
                recommendations.append("Provide regular progress updates and success stories")
                recommendations.append("Consider additional services or consultations")
            
            elif factor_name == "service_utilization" and risk_level in ["high", "critical"]:
                recommendations.append("Engage client with usage tips and best practices")
                recommendations.append("Highlight underutilized features that could add value")
                recommendations.append("Schedule onboarding or refresher training")
            
            elif factor_name == "support_interactions" and risk_level in ["high", "critical"]:
                recommendations.append("Address all outstanding support issues immediately")
                recommendations.append("Assign dedicated support representative")
                recommendations.append("Implement proactive support check-ins")
        
        # Default recommendations if none specific
        if not recommendations:
            if risk_level == "low":
                recommendations.append("Continue current engagement strategy")
                recommendations.append("Consider upselling or cross-selling opportunities")
            else:
                recommendations.append("Monitor closely and gather feedback")
                recommendations.append("Review service delivery and client satisfaction")
        
        return recommendations
    
    def _calculate_confidence(self, client_history: Dict, risk_factors: List[Dict]) -> float:
        """Calculate confidence in the prediction"""
        # Base confidence on data availability
        data_completeness = 0.0
        
        # Check for key data types
        has_disputes = len(client_history.get('disputes', [])) > 0
        has_payments = len(client_history.get('payments', [])) > 0
        has_communications = len(client_history.get('communications', [])) > 0
        has_documents = len(client_history.get('documents', [])) > 0
        
        data_points = sum([has_disputes, has_payments, has_communications, has_documents])
        data_completeness = data_points / 4.0  # 4 key data types
        
        # Adjust based on factor count and quality
        factor_count = len(risk_factors)
        if factor_count == 0:
            factor_confidence = 0.1
        elif factor_count <= 2:
            factor_confidence = 0.4
        elif factor_count <= 4:
            factor_confidence = 0.7
        else:
            factor_confidence = 0.9
        
        # Combined confidence
        confidence = (data_completeness + factor_confidence) / 2
        return max(0.1, min(1.0, confidence))
    
    def _calculate_summary_statistics(self, predictions: List[Dict]) -> Dict[str, Any]:
        """Calculate summary statistics for all predictions"""
        if not predictions:
            return {
                "high_risk_count": 0,
                "medium_risk_count": 0,
                "low_risk_count": 0,
                "average_churn_probability": 0.0,
                "total_potential_revenue_at_risk": 0.0
            }
        
        # Count by risk level
        risk_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        churn_probabilities = []
        
        for prediction in predictions:
            risk_level = prediction.get('risk_level', 'medium')
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1
            churn_probabilities.append(prediction.get('churn_probability', 0.5))
        
        # Calculate averages
        avg_churn_prob = statistics.mean(churn_probabilities) if churn_probabilities else 0.0
        
        # Calculate potential revenue at risk (simplified)
        high_and_critical = risk_counts["critical"] + risk_counts["high"]
        estimated_monthly_revenue = 200  # Average monthly revenue per client
        revenue_at_risk = high_and_critical * estimated_monthly_revenue
        
        return {
            "high_risk_count": risk_counts["high"],
            "medium_risk_count": risk_counts["medium"],
            "low_risk_count": risk_counts["low"],
            "critical_risk_count": risk_counts["critical"],
            "average_churn_probability": round(avg_churn_prob, 3),
            "total_potential_revenue_at_risk": revenue_at_risk,
            "risk_distribution": risk_counts
        }