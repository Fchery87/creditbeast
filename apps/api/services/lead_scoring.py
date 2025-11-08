"""
Lead Scoring Service for CreditBeast
Advanced lead qualification and scoring system
"""

import re
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID
import json
import statistics

logger = logging.getLogger(__name__)

class LeadScoringService:
    """Lead scoring and qualification service"""
    
    def __init__(self, db_client):
        self.db = db_client
    
    async def score_lead(self, lead_data: Dict[str, Any], organization_id: str, profile_id: Optional[str] = None) -> Dict[str, Any]:
        """Score a lead using configured scoring profile"""
        try:
            # Get scoring profile
            if not profile_id:
                profile = await self._get_default_scoring_profile(organization_id)
            else:
                profile = await self._get_scoring_profile(profile_id, organization_id)
            
            if not profile:
                raise ValueError("No scoring profile found")
            
            # Score the lead
            score_result = await self._calculate_lead_score(lead_data, profile)
            
            # Determine qualification status
            qualification_status = self._determine_qualification_status(score_result, profile)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(score_result, qualification_status, lead_data)
            
            # Save scoring result
            saved_result = await self._save_scoring_result(
                lead_data, score_result, qualification_status, profile, organization_id
            )
            
            return {
                "lead_id": saved_result.get('id'),
                "score": score_result['total_score'],
                "max_score": 10.0,
                "percentage": (score_result['total_score'] / 10.0) * 100,
                "breakdown": score_result['criteria_scores'],
                "qualification_status": qualification_status,
                "confidence_level": score_result['confidence'],
                "recommended_actions": recommendations,
                "scoring_profile_used": profile.get('name', 'unknown'),
                "scored_at": datetime.utcnow().isoformat(),
                "reasoning": score_result.get('reasoning', [])
            }
            
        except Exception as e:
            logger.error(f"Error scoring lead: {e}")
            # Return safe default
            return {
                "score": 5.0,
                "max_score": 10.0,
                "percentage": 50.0,
                "breakdown": {},
                "qualification_status": "manual_review",
                "confidence_level": 0.5,
                "recommended_actions": ["Manual review required due to scoring error"],
                "scoring_profile_used": "error_fallback",
                "scored_at": datetime.utcnow().isoformat(),
                "reasoning": ["Scoring error occurred, manual review recommended"]
            }
    
    async def _get_default_scoring_profile(self, organization_id: str) -> Optional[Dict]:
        """Get default scoring profile for organization"""
        result = await self.db.table("lead_scoring_profiles").select("*")\
            .eq("organization_id", organization_id)\
            .eq("is_default", True)\
            .eq("is_active", True)\
            .execute()
        return result.data[0] if result.data else await self._create_default_profile(organization_id)
    
    async def _create_default_profile(self, organization_id: str) -> Dict:
        """Create default scoring profile"""
        default_criteria = [
            {
                "criteria_type": "email_domain",
                "weight": 2.0,
                "positive_values": ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"],
                "negative_values": ["tempmail.com", "10minutemail.com", "guerrillamail.com"],
                "threshold_score": 1.0
            },
            {
                "criteria_type": "phone_format",
                "weight": 1.5,
                "positive_values": ["valid"],
                "negative_values": ["invalid", "placeholder"],
                "threshold_score": 1.0
            },
            {
                "criteria_type": "address_validity",
                "weight": 1.0,
                "positive_values": ["complete"],
                "negative_values": ["incomplete", "invalid"],
                "threshold_score": 0.5
            },
            {
                "criteria_type": "utm_source",
                "weight": 1.0,
                "positive_values": ["google", "facebook", "referral", "partner"],
                "negative_values": ["spam", "bot"],
                "threshold_score": 0.5
            }
        ]
        
        profile_data = {
            "organization_id": organization_id,
            "name": "Default Credit Repair Lead Profile",
            "description": "Default profile for credit repair lead qualification",
            "criteria": default_criteria,
            "auto_qualify_threshold": 7.0,
            "require_review_threshold": 5.0,
            "disqualify_threshold": 3.0,
            "is_default": True,
            "is_active": True
        }
        
        result = await self.db.table("lead_scoring_profiles").insert(profile_data).execute()
        return result.data[0] if result.data else profile_data
    
    async def _get_scoring_profile(self, profile_id: str, organization_id: str) -> Optional[Dict]:
        """Get specific scoring profile"""
        result = await self.db.table("lead_scoring_profiles").select("*")\
            .eq("id", profile_id)\
            .eq("organization_id", organization_id)\
            .eq("is_active", True)\
            .execute()
        return result.data[0] if result.data else None
    
    async def _calculate_lead_score(self, lead_data: Dict, profile: Dict) -> Dict[str, Any]:
        """Calculate lead score based on profile criteria"""
        criteria_scores = {}
        total_score = 0.0
        max_possible_score = 0.0
        reasoning = []
        
        criteria_list = profile.get('criteria', [])
        
        for criteria in criteria_list:
            score_result = await self._score_criteria(lead_data, criteria)
            criteria_scores[criteria['criteria_type']] = score_result
            total_score += score_result['score']
            max_possible_score += criteria['weight']
            reasoning.extend(score_result.get('reasoning', []))
        
        # Normalize score to 0-10 scale
        normalized_score = (total_score / max_possible_score) * 10 if max_possible_score > 0 else 0
        
        # Calculate confidence based on data completeness
        confidence = self._calculate_confidence(lead_data, criteria_scores)
        
        return {
            "total_score": round(normalized_score, 2),
            "raw_score": total_score,
            "max_possible_score": max_possible_score,
            "criteria_scores": criteria_scores,
            "confidence": confidence,
            "reasoning": reasoning
        }
    
    async def _score_criteria(self, lead_data: Dict, criteria: Dict) -> Dict[str, Any]:
        """Score individual criteria"""
        criteria_type = criteria['criteria_type']
        weight = criteria['weight']
        positive_values = criteria.get('positive_values', [])
        negative_values = criteria.get('negative_values', [])
        threshold_score = criteria.get('threshold_score', 0)
        
        score = 0.0
        reasoning = []
        
        if criteria_type == "email_domain":
            score, reasoning = self._score_email_domain(lead_data, positive_values, negative_values)
        elif criteria_type == "phone_format":
            score, reasoning = self._score_phone_format(lead_data)
        elif criteria_type == "address_validity":
            score, reasoning = self._score_address_validity(lead_data)
        elif criteria_type == "utm_source":
            score, reasoning = self._score_utm_source(lead_data, positive_values, negative_values)
        elif criteria_type == "lead_source":
            score, reasoning = self._score_lead_source(lead_data, positive_values, negative_values)
        elif criteria_type == "name_completeness":
            score, reasoning = self._score_name_completeness(lead_data)
        elif criteria_type == "credit_concern_level":
            score, reasoning = self._score_credit_concern_level(lead_data)
        elif criteria_type == "demographic_fit":
            score, reasoning = self._score_demographic_fit(lead_data)
        else:
            # Unknown criteria type
            score = threshold_score
            reasoning = [f"Unknown criteria type: {criteria_type}, using threshold score"]
        
        # Apply weight
        weighted_score = score * weight
        
        return {
            "score": weighted_score,
            "raw_score": score,
            "weight": weight,
            "reasoning": reasoning
        }
    
    def _score_email_domain(self, lead_data: Dict, positive_domains: List[str], negative_domains: List[str]) -> Tuple[float, List[str]]:
        """Score email domain quality"""
        email = lead_data.get('email', '').lower()
        score = 0.0
        reasoning = []
        
        if not email:
            reasoning.append("No email provided")
            return 0.0, reasoning
        
        # Extract domain
        domain = email.split('@')[1] if '@' in email else ''
        
        if not domain:
            reasoning.append("Invalid email format")
            return 0.0, reasoning
        
        # Check for positive domains
        if domain in positive_domains:
            score = 1.0
            reasoning.append(f"Email domain {domain} is in positive list")
        elif domain in negative_domains:
            score = 0.0
            reasoning.append(f"Email domain {domain} is in negative list")
        else:
            # Unknown domain, moderate score
            score = 0.5
            reasoning.append(f"Email domain {domain} is not in known lists")
        
        return score, reasoning
    
    def _score_phone_format(self, lead_data: Dict) -> Tuple[float, List[str]]:
        """Score phone number format"""
        phone = lead_data.get('phone', '')
        score = 0.0
        reasoning = []
        
        if not phone:
            reasoning.append("No phone number provided")
            return 0.0, reasoning
        
        # Remove all non-digits
        digits_only = re.sub(r'\D', '', phone)
        
        if len(digits_only) == 10:
            score = 1.0
            reasoning.append("Valid 10-digit phone number")
        elif len(digits_only) == 11 and digits_only.startswith('1'):
            score = 0.9
            reasoning.append("Valid 11-digit phone number with country code")
        elif len(digits_only) >= 10:
            score = 0.7
            reasoning.append("Phone number format needs verification")
        else:
            score = 0.0
            reasoning.append("Invalid phone number format")
        
        return score, reasoning
    
    def _score_address_validity(self, lead_data: Dict) -> Tuple[float, List[str]]:
        """Score address completeness"""
        address_fields = ['street_address', 'city', 'state', 'zip_code']
        score = 0.0
        reasoning = []
        provided_fields = 0
        
        for field in address_fields:
            value = lead_data.get(field, '').strip()
            if value:
                provided_fields += 1
        
        completeness = provided_fields / len(address_fields)
        score = completeness
        
        if completeness == 1.0:
            reasoning.append("Complete address provided")
        elif completeness >= 0.75:
            reasoning.append("Nearly complete address provided")
        elif completeness >= 0.5:
            reasoning.append("Partial address provided")
        else:
            reasoning.append("Incomplete address provided")
        
        return score, reasoning
    
    def _score_utm_source(self, lead_data: Dict, positive_sources: List[str], negative_sources: List[str]) -> Tuple[float, List[str]]:
        """Score UTM source quality"""
        utm_source = lead_data.get('utm_source', '').lower()
        score = 0.0
        reasoning = []
        
        if not utm_source:
            reasoning.append("No UTM source provided")
            return 0.0, reasoning
        
        if utm_source in positive_sources:
            score = 1.0
            reasoning.append(f"UTM source {utm_source} is high quality")
        elif utm_source in negative_sources:
            score = 0.0
            reasoning.append(f"UTM source {utm_source} is low quality")
        else:
            score = 0.5
            reasoning.append(f"UTM source {utm_source} is moderate quality")
        
        return score, reasoning
    
    def _score_lead_source(self, lead_data: Dict, positive_sources: List[str], negative_sources: List[str]) -> Tuple[float, List[str]]:
        """Score lead source quality"""
        lead_source = lead_data.get('lead_source', '').lower()
        score = 0.0
        reasoning = []
        
        if not lead_source:
            reasoning.append("No lead source specified")
            return 0.0, reasoning
        
        if lead_source in positive_sources:
            score = 1.0
            reasoning.append(f"Lead source {lead_source} is high quality")
        elif lead_source in negative_sources:
            score = 0.0
            reasoning.append(f"Lead source {lead_source} is low quality")
        else:
            score = 0.5
            reasoning.append(f"Lead source {lead_source} is moderate quality")
        
        return score, reasoning
    
    def _score_name_completeness(self, lead_data: Dict) -> Tuple[float, List[str]]:
        """Score name completeness"""
        first_name = lead_data.get('first_name', '').strip()
        last_name = lead_data.get('last_name', '').strip()
        score = 0.0
        reasoning = []
        
        if first_name and last_name:
            score = 1.0
            reasoning.append("Complete name provided")
        elif first_name or last_name:
            score = 0.5
            reasoning.append("Partial name provided")
        else:
            score = 0.0
            reasoning.append("No name provided")
        
        return score, reasoning
    
    def _score_credit_concern_level(self, lead_data: Dict) -> Tuple[float, List[str]]:
        """Score level of credit concern based on available indicators"""
        score = 0.5  # Neutral score
        reasoning = []
        
        # Look for indicators in custom fields or other sources
        custom_fields = lead_data.get('custom_fields', {})
        
        # Check for urgency indicators
        urgency_indicators = ['urgent', 'asap', 'immediately', 'soon']
        concern_level = custom_fields.get('concern_level', '').lower()
        
        if any(indicator in concern_level for indicator in urgency_indicators):
            score = 0.8
            reasoning.append("High concern level indicated")
        elif concern_level in ['low', 'minor', 'curious']:
            score = 0.3
            reasoning.append("Low concern level indicated")
        
        return score, reasoning
    
    def _score_demographic_fit(self, lead_data: Dict) -> Tuple[float, List[str]]:
        """Score demographic fit for credit repair services"""
        score = 0.5  # Default neutral score
        reasoning = []
        
        # Basic demographic scoring (this could be enhanced with real demographic data)
        state = lead_data.get('state', '').upper()
        
        # States with higher credit repair demand (simplified example)
        high_demand_states = ['CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI']
        
        if state in high_demand_states:
            score = 0.8
            reasoning.append(f"State {state} has high credit repair demand")
        elif state:
            score = 0.6
            reasoning.append(f"State {state} has moderate credit repair demand")
        else:
            reasoning.append("No state information provided")
        
        return score, reasoning
    
    def _calculate_confidence(self, lead_data: Dict, criteria_scores: Dict) -> float:
        """Calculate confidence in the scoring result"""
        data_completeness = 0.0
        max_fields = 10  # Expected number of important fields
        
        important_fields = ['email', 'phone', 'first_name', 'last_name', 'street_address', 'city', 'state', 'zip_code', 'utm_source', 'lead_source']
        for field in important_fields:
            if lead_data.get(field, '').strip():
                data_completeness += 1
        
        completeness_ratio = data_completeness / max_fields
        
        # Also consider how many criteria were successfully scored
        criteria_count = len([score for score in criteria_scores.values() if score['raw_score'] > 0])
        criteria_ratio = criteria_count / max(len(criteria_scores), 1)
        
        # Combined confidence
        confidence = (completeness_ratio + criteria_ratio) / 2
        return max(0.1, min(1.0, confidence))
    
    def _determine_qualification_status(self, score_result: Dict, profile: Dict) -> str:
        """Determine lead qualification status based on score and profile"""
        score = score_result['total_score']
        confidence = score_result['confidence']
        
        # Adjust thresholds based on confidence
        auto_qualify_threshold = profile.get('auto_qualify_threshold', 7.0)
        require_review_threshold = profile.get('require_review_threshold', 5.0)
        disqualify_threshold = profile.get('disqualify_threshold', 3.0)
        
        # Reduce thresholds if confidence is low
        if confidence < 0.5:
            auto_qualify_threshold -= 1.0
            require_review_threshold -= 0.5
        
        if score >= auto_qualify_threshold:
            return "auto_qualified"
        elif score >= require_review_threshold:
            return "review_required"
        elif score <= disqualify_threshold:
            return "auto_disqualified"
        else:
            return "manual_review"
    
    async def _generate_recommendations(self, score_result: Dict, qualification_status: str, lead_data: Dict) -> List[str]:
        """Generate recommended actions based on scoring result"""
        recommendations = []
        score = score_result['total_score']
        criteria_scores = score_result['criteria_scores']
        
        if qualification_status == "auto_qualified":
            recommendations.append("Automatically qualify and add to nurture sequence")
            recommendations.append("Assign to sales team for immediate follow-up")
        elif qualification_status == "review_required":
            recommendations.append("Schedule manual review within 24 hours")
            recommendations.append("Add to review queue for sales team")
        elif qualification_status == "manual_review":
            recommendations.append("Manual review required - gather additional information")
        elif qualification_status == "auto_disqualified":
            recommendations.append("Auto-disqualified - do not pursue")
        
        # Specific recommendations based on weak criteria
        for criteria_type, score_data in criteria_scores.items():
            if score_data['raw_score'] < 0.5:
                if criteria_type == "email_domain":
                    recommendations.append("Verify email address and request alternative contact")
                elif criteria_type == "phone_format":
                    recommendations.append("Request valid phone number for contact")
                elif criteria_type == "address_validity":
                    recommendations.append("Request complete address information")
        
        return recommendations
    
    async def _save_scoring_result(self, lead_data: Dict, score_result: Dict, qualification_status: str, profile: Dict, organization_id: str) -> Dict:
        """Save lead scoring result to database"""
        scoring_data = {
            "organization_id": organization_id,
            "lead_data": json.dumps(lead_data),
            "score": score_result['total_score'],
            "breakdown": json.dumps(score_result['criteria_scores']),
            "qualification_status": qualification_status,
            "confidence_level": score_result['confidence'],
            "scoring_profile_id": profile['id'],
            "recommended_actions": json.dumps(await self._generate_recommendations(score_result, qualification_status, lead_data)),
            "scored_at": datetime.utcnow().isoformat()
        }
        
        result = await self.db.table("lead_scoring_results").insert(scoring_data).execute()
        return result.data[0] if result.data else {}
    
    async def get_scoring_analytics(self, organization_id: str, date_range: Optional[Tuple[date, date]] = None) -> Dict[str, Any]:
        """Get analytics on lead scoring performance"""
        try:
            # Build query
            query = self.db.table("lead_scoring_results").select("*")\
                .eq("organization_id", organization_id)
            
            if date_range:
                start_date, end_date = date_range
                query = query.gte("scored_at", start_date.isoformat())\
                           .lte("scored_at", end_date.isoformat())
            
            result = await query.execute()
            scores = result.data or []
            
            if not scores:
                return {
                    "total_leads": 0,
                    "average_score": 0,
                    "qualification_rates": {},
                    "score_distribution": {}
                }
            
            # Calculate analytics
            total_leads = len(scores)
            scores_only = [s['score'] for s in scores]
            average_score = statistics.mean(scores_only)
            
            # Qualification rates
            qualification_rates = {}
            for status in ['auto_qualified', 'review_required', 'manual_review', 'auto_disqualified']:
                count = sum(1 for s in scores if s['qualification_status'] == status)
                qualification_rates[status] = {
                    "count": count,
                    "percentage": (count / total_leads) * 100 if total_leads > 0 else 0
                }
            
            # Score distribution
            score_ranges = [
                (0, 2, "Very Low"),
                (2, 4, "Low"),
                (4, 6, "Medium"),
                (6, 8, "High"),
                (8, 10, "Very High")
            ]
            
            score_distribution = {}
            for min_score, max_score, label in score_ranges:
                count = sum(1 for s in scores_only if min_score <= s < max_score)
                score_distribution[label] = {
                    "count": count,
                    "percentage": (count / total_leads) * 100 if total_leads > 0 else 0,
                    "range": f"{min_score}-{max_score}"
                }
            
            return {
                "total_leads": total_leads,
                "average_score": round(average_score, 2),
                "qualification_rates": qualification_rates,
                "score_distribution": score_distribution,
                "date_range": {
                    "start": date_range[0].isoformat() if date_range else None,
                    "end": date_range[1].isoformat() if date_range else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting scoring analytics: {e}")
            return {
                "total_leads": 0,
                "average_score": 0,
                "qualification_rates": {},
                "score_distribution": {},
                "error": str(e)
            }