"""
Automation services for CreditBeast
Advanced automation features for dispute generation, bureau targeting, and payment recovery
"""

import re
import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID
from statistics import mean
import math

logger = logging.getLogger(__name__)

class LetterGenerationService:
    """Template-based letter generation service"""
    
    def __init__(self, db_client):
        self.db = db_client
    
    async def generate_letter(self, dispute_id: str, organization_id: str, template_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate a dispute letter using templates and client data"""
        try:
            # Get dispute data
            dispute_data = await self._get_dispute_data(dispute_id, organization_id)
            if not dispute_data:
                raise ValueError("Dispute not found")
            
            # Get client data
            client_data = await self._get_client_data(dispute_data['client_id'], organization_id)
            if not client_data:
                raise ValueError("Client not found")
            
            # Select template (if not provided, use AI/ML selection)
            if not template_id:
                template_id = await self._select_optimal_template(
                    dispute_data, client_data, organization_id
                )
            
            # Get template
            template = await self._get_template(template_id, organization_id)
            if not template:
                raise ValueError("Template not found")
            
            # Generate letter content
            letter_content = await self._render_template(template, dispute_data, client_data)
            
            # Save generated letter
            letter_record = await self._save_generated_letter(
                dispute_id, organization_id, letter_content, template_id
            )
            
            return {
                "letter_id": letter_record['id'],
                "content": letter_content,
                "template_used": template['name'],
                "variables_used": template.get('variables', []),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating letter: {e}")
            raise
    
    async def _get_dispute_data(self, dispute_id: str, organization_id: str) -> Optional[Dict]:
        """Get dispute data with all related information"""
        result = await self.db.table("disputes").select("""
            *,
            client:clients(*)
        """).eq("id", dispute_id).eq("organization_id", organization_id).execute()
        
        return result.data[0] if result.data else None
    
    async def _get_client_data(self, client_id: str, organization_id: str) -> Optional[Dict]:
        """Get client data"""
        result = await self.db.table("clients").select("*").eq("id", client_id).execute()
        return result.data[0] if result.data else None
    
    async def _select_optimal_template(self, dispute_data: Dict, client_data: Dict, organization_id: str) -> str:
        """AI/ML-based template selection for optimal dispute success"""
        # Get active templates
        templates = await self._get_active_templates(organization_id)
        
        if not templates:
            # Fallback to default template
            return "default_dispute_template"
        
        # Score templates based on historical success
        scored_templates = []
        for template in templates:
            score = await self._calculate_template_score(
                template, dispute_data, client_data, organization_id
            )
            scored_templates.append((template, score))
        
        # Sort by score and return highest
        scored_templates.sort(key=lambda x: x[1], reverse=True)
        return scored_templates[0][0]['id'] if scored_templates else templates[0]['id']
    
    async def _get_active_templates(self, organization_id: str) -> List[Dict]:
        """Get active letter templates for organization"""
        result = await self.db.table("letter_templates").select("*")\
            .eq("organization_id", organization_id)\
            .eq("is_active", True)\
            .order("priority", desc=True)\
            .execute()
        return result.data or []
    
    async def _calculate_template_score(self, template: Dict, dispute_data: Dict, client_data: Dict, organization_id: str) -> float:
        """Calculate template suitability score"""
        score = 0.0
        
        # Base score from template priority
        score += template.get('priority', 0) * 0.3
        
        # Score based on dispute type match
        if dispute_data.get('dispute_type') in template.get('dispute_types', []):
            score += 2.0
        
        # Score based on bureau targeting
        if dispute_data.get('bureau') in template.get('bureau_targets', []):
            score += 1.5
        
        # Score based on round optimization
        if template.get('round_optimized') and dispute_data.get('round_number', 1) <= 3:
            score += 1.0
        
        # Score based on historical success rate
        success_rate = template.get('success_rate', 0.5)
        score += success_rate * 2.0
        
        # Score based on recent usage (prefer templates with recent success)
        usage_count = template.get('usage_count', 0)
        if usage_count > 0:
            recent_usage_bonus = min(usage_count * 0.1, 1.0)
            score += recent_usage_bonus
        
        return score
    
    async def _get_template(self, template_id: str, organization_id: str) -> Optional[Dict]:
        """Get template by ID"""
        result = await self.db.table("letter_templates").select("*")\
            .eq("id", template_id)\
            .eq("organization_id", organization_id)\
            .eq("is_active", True)\
            .execute()
        return result.data[0] if result.data else None
    
    async def _render_template(self, template: Dict, dispute_data: Dict, client_data: Dict) -> str:
        """Render template with data"""
        content = template.get('content', '')
        variables = template.get('variables', [])
        
        # Create variable mapping
        variable_map = {
            'client_first_name': client_data.get('first_name', ''),
            'client_last_name': client_data.get('last_name', ''),
            'client_full_name': f"{client_data.get('first_name', '')} {client_data.get('last_name', '')}",
            'client_email': client_data.get('email', ''),
            'client_phone': client_data.get('phone', ''),
            'client_address': self._format_address(client_data),
            'dispute_type': dispute_data.get('dispute_type', ''),
            'account_name': dispute_data.get('account_name', ''),
            'dispute_reason': dispute_data.get('dispute_reason', ''),
            'bureau_name': self._get_bureau_full_name(dispute_data.get('bureau', '')),
            'round_number': dispute_data.get('round_number', 1),
            'current_date': datetime.utcnow().strftime('%B %d, %Y'),
            'organization_name': 'CreditBeast',
        }
        
        # Replace variables in content
        for variable in variables:
            if variable in variable_map:
                content = content.replace(f"{{{{{variable}}}}}", str(variable_map[variable]))
            else:
                # Log missing variable
                logger.warning(f"Template variable {variable} not found in data")
        
        return content
    
    def _format_address(self, client_data: Dict) -> str:
        """Format client address for letters"""
        address_parts = [
            client_data.get('street_address', ''),
            client_data.get('city', ''),
            client_data.get('state', ''),
            client_data.get('zip_code', '')
        ]
        return ', '.join(part for part in address_parts if part)
    
    def _get_bureau_full_name(self, bureau_code: str) -> str:
        """Get full bureau name from code"""
        bureau_names = {
            'equifax': 'Equifax Information Services LLC',
            'experian': 'Experian',
            'transunion': 'TransUnion LLC',
            'all': 'All Credit Reporting Agencies'
        }
        return bureau_names.get(bureau_code.lower(), bureau_code.title())
    
    async def _save_generated_letter(self, dispute_id: str, organization_id: str, content: str, template_id: str) -> Dict:
        """Save generated letter to database"""
        result = await self.db.table("generated_letters").insert({
            "dispute_id": dispute_id,
            "organization_id": organization_id,
            "template_id": template_id,
            "content": content,
            "status": "generated",
            "generated_at": datetime.utcnow().isoformat()
        }).execute()
        return result.data[0] if result.data else {}


class BureauTargetingService:
    """Automated bureau targeting logic service"""
    
    def __init__(self, db_client):
        self.db = db_client
    
    async def recommend_bureaus(self, dispute_data: Dict, client_history: Optional[Dict] = None) -> Dict[str, Any]:
        """Recommend optimal bureau targeting based on dispute type and client history"""
        try:
            # Get targeting rules
            rules = await self._get_targeting_rules(dispute_data.get('organization_id'))
            
            # Apply rules to get recommendations
            recommendations = await self._apply_targeting_rules(
                dispute_data, rules, client_history
            )
            
            return {
                "recommended_bureaus": recommendations['bureaus'],
                "confidence_score": recommendations['confidence'],
                "rule_applied": recommendations['rule_name'],
                "alternatives": recommendations.get('alternatives', []),
                "reasoning": recommendations.get('reasoning', [])
            }
            
        except Exception as e:
            logger.error(f"Error in bureau targeting: {e}")
            # Return safe default
            return {
                "recommended_bureaus": ["all"],
                "confidence_score": 0.5,
                "rule_applied": "default",
                "alternatives": ["equifax", "experian", "transunion"],
                "reasoning": ["Default fallback recommendation"]
            }
    
    async def _get_targeting_rules(self, organization_id: str) -> List[Dict]:
        """Get active bureau targeting rules"""
        result = await self.db.table("bureau_targeting_rules").select("*")\
            .eq("organization_id", organization_id)\
            .eq("is_active", True)\
            .order("confidence_score", desc=True)\
            .execute()
        return result.data or []
    
    async def _apply_targeting_rules(self, dispute_data: Dict, rules: List[Dict], client_history: Optional[Dict]) -> Dict:
        """Apply targeting rules to generate recommendations"""
        if not rules:
            # Default rule: target all bureaus for most dispute types
            return {
                "bureaus": ["all"],
                "confidence": 0.6,
                "rule_name": "default_all_bureaus",
                "alternatives": ["equifax", "experian", "transunion"],
                "reasoning": ["Default recommendation - target all bureaus"]
            }
        
        # Apply most relevant rule
        best_rule = None
        best_score = 0
        
        for rule in rules:
            score = await self._calculate_rule_relevance(rule, dispute_data, client_history)
            if score > best_score:
                best_score = score
                best_rule = rule
        
        if not best_rule or best_score < 0.3:
            # Fallback to safe default
            return {
                "bureaus": ["all"],
                "confidence": 0.5,
                "rule_name": "fallback_default",
                "alternatives": ["equifax", "experian", "transunion"],
                "reasoning": ["No specific rule matched, using safe default"]
            }
        
        return {
            "bureaus": best_rule.get('recommended_bureaus', ['all']),
            "confidence": best_rule.get('confidence_score', 0.5),
            "rule_name": best_rule.get('name', 'unknown'),
            "alternatives": self._get_alternative_bureaus(best_rule.get('recommended_bureaus', ['all'])),
            "reasoning": [f"Applied rule: {best_rule.get('name', 'unknown')}"]
        }
    
    async def _calculate_rule_relevance(self, rule: Dict, dispute_data: Dict, client_history: Optional[Dict]) -> float:
        """Calculate how relevant a rule is for the current dispute"""
        relevance = 0.0
        rule_type = rule.get('rule_type', '')
        criteria = rule.get('criteria', {})
        
        # Match rule type to dispute characteristics
        if rule_type == 'dispute_type_based':
            if dispute_data.get('dispute_type') in criteria.get('dispute_types', []):
                relevance += 0.8
                
        elif rule_type == 'account_based':
            # Check account-specific criteria
            account_name = dispute_data.get('account_name', '').lower()
            for keyword in criteria.get('account_keywords', []):
                if keyword.lower() in account_name:
                    relevance += 0.6
                    break
        
        elif rule_type == 'client_history_based':
            if client_history:
                # Check client-specific criteria
                avg_disputes = client_history.get('avg_disputes_per_month', 0)
                if avg_disputes < criteria.get('max_avg_disputes', 10):
                    relevance += 0.4
        
        # Bonus for rule success history
        success_rate = rule.get('success_history', 0) / max(rule.get('total_applications', 1), 1)
        relevance += success_rate * 0.3
        
        return min(relevance, 1.0)
    
    def _get_alternative_bureaus(self, recommended_bureaus: List[str]) -> List[str]:
        """Get alternative bureau options"""
        all_bureaus = ['equifax', 'experian', 'transunion']
        if 'all' in recommended_bureaus:
            # If all recommended, provide individual options
            return all_bureaus
        
        # Return bureaus not in primary recommendation
        return [b for b in all_bureaus if b not in recommended_bureaus]


class AutomatedSchedulingService:
    """Automated dispute round scheduling and follow-ups"""
    
    def __init__(self, db_client):
        self.db = db_client
    
    async def schedule_next_round(self, dispute_id: str, organization_id: str) -> Dict[str, Any]:
        """Schedule the next dispute round based on rules and client history"""
        try:
            # Get current dispute data
            dispute_data = await self._get_dispute_data(dispute_id, organization_id)
            if not dispute_data:
                raise ValueError("Dispute not found")
            
            current_round = dispute_data.get('round_number', 1)
            next_round = current_round + 1
            
            # Get scheduling rules for next round
            rule = await self._get_scheduling_rule(next_round, organization_id)
            
            if not rule:
                # Use default scheduling
                return await self._apply_default_scheduling(dispute_data, next_round)
            
            # Calculate optimal timing
            schedule_date = await self._calculate_optimal_schedule(
                dispute_data, rule, organization_id
            )
            
            # Create scheduled task
            scheduled_task = await self._create_scheduled_task(
                dispute_id, organization_id, next_round, schedule_date, rule
            )
            
            return {
                "next_round": next_round,
                "scheduled_date": schedule_date.isoformat(),
                "rule_applied": rule.get('name', 'default'),
                "follow_up_strategy": rule.get('follow_up_strategy', 'standard'),
                "task_id": scheduled_task.get('id'),
                "estimated_success_probability": await self._estimate_success_probability(dispute_data, next_round)
            }
            
        except Exception as e:
            logger.error(f"Error scheduling next round: {e}")
            # Return safe default
            from datetime import datetime, timedelta
            return {
                "next_round": dispute_data.get('round_number', 1) + 1,
                "scheduled_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "rule_applied": "emergency_default",
                "follow_up_strategy": "standard",
                "task_id": None,
                "estimated_success_probability": 0.5
            }
    
    async def _get_dispute_data(self, dispute_id: str, organization_id: str) -> Optional[Dict]:
        """Get current dispute data"""
        result = await self.db.table("disputes").select("*")\
            .eq("id", dispute_id)\
            .eq("organization_id", organization_id)\
            .execute()
        return result.data[0] if result.data else None
    
    async def _get_scheduling_rule(self, round_number: int, organization_id: str) -> Optional[Dict]:
        """Get scheduling rule for specific round"""
        result = await self.db.table("scheduling_rules").select("*")\
            .eq("organization_id", organization_id)\
            .eq("round_number", round_number)\
            .eq("is_active", True)\
            .execute()
        return result.data[0] if result.data else None
    
    async def _apply_default_scheduling(self, dispute_data: Dict, next_round: int) -> Dict[str, Any]:
        """Apply default scheduling when no specific rule exists"""
        from datetime import datetime, timedelta
        
        # Default timing based on round number
        base_delay = 30 + (next_round - 1) * 15  # Progressive delay
        schedule_date = datetime.utcnow() + timedelta(days=base_delay)
        
        return {
            "next_round": next_round,
            "scheduled_date": schedule_date.isoformat(),
            "rule_applied": "default_progressive",
            "follow_up_strategy": "standard",
            "task_id": None,
            "estimated_success_probability": max(0.1, 0.8 - (next_round * 0.1))
        }
    
    async def _calculate_optimal_schedule(self, dispute_data: Dict, rule: Dict, organization_id: str) -> date:
        """Calculate optimal scheduling date based on rule and factors"""
        from datetime import datetime, timedelta
        
        # Base timing from rule
        min_days = rule.get('min_wait_days', 30)
        max_days = rule.get('max_wait_days', 45)
        
        # Adjust based on dispute type (some disputes need faster follow-up)
        dispute_type = dispute_data.get('dispute_type', '')
        if dispute_type in ['collection', 'charge_off']:
            min_days = max(20, min_days - 5)
            max_days = max(30, max_days - 5)
        
        # Adjust based on client communication preferences
        client_id = dispute_data.get('client_id')
        if client_id:
            client_prefs = await self._get_client_preferences(client_id, organization_id)
            if client_prefs.get('prefers_frequent_updates'):
                min_days = max(14, min_days - 10)
        
        # Calculate schedule date
        base_delay = (min_days + max_days) / 2
        schedule_date = datetime.utcnow() + timedelta(days=int(base_delay))
        
        return schedule_date.date()
    
    async def _get_client_preferences(self, client_id: str, organization_id: str) -> Dict:
        """Get client communication preferences"""
        result = await self.db.table("client_preferences").select("*")\
            .eq("client_id", client_id)\
            .eq("organization_id", organization_id)\
            .execute()
        return result.data[0] if result.data else {}
    
    async def _create_scheduled_task(self, dispute_id: str, organization_id: str, round_number: int, schedule_date: date, rule: Dict) -> Dict:
        """Create scheduled task for next round"""
        result = await self.db.table("scheduled_tasks").insert({
            "organization_id": organization_id,
            "dispute_id": dispute_id,
            "task_type": "dispute_round",
            "task_data": {
                "round_number": round_number,
                "rule_applied": rule.get('name'),
                "follow_up_strategy": rule.get('follow_up_strategy')
            },
            "scheduled_date": schedule_date.isoformat(),
            "status": "scheduled",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        return result.data[0] if result.data else {}
    
    async def _estimate_success_probability(self, dispute_data: Dict, round_number: int) -> float:
        """Estimate success probability for next round"""
        # Base probability decreases with each round
        base_prob = max(0.1, 0.7 - (round_number - 1) * 0.1)
        
        # Adjust based on dispute type
        dispute_type = dispute_data.get('dispute_type', '')
        type_modifiers = {
            'inquiry': 1.1,
            'late_payment': 0.9,
            'collection': 0.7,
            'charge_off': 0.6
        }
        modifier = type_modifiers.get(dispute_type, 1.0)
        
        # Adjust based on client responsiveness
        client_responsiveness = dispute_data.get('client_responsiveness_score', 0.5)
        responsiveness_modifier = 0.8 + (client_responsiveness * 0.4)
        
        estimated_prob = base_prob * modifier * responsiveness_modifier
        return max(0.05, min(0.95, estimated_prob))


class PaymentRetryService:
    """Smart payment retry logic service"""
    
    def __init__(self, db_client):
        self.db = db_client
    
    async def get_next_retry_strategy(self, failed_payment_id: str, organization_id: str) -> Dict[str, Any]:
        """Get optimal retry strategy for failed payment"""
        try:
            # Get failed payment data
            payment_data = await self._get_failed_payment(failed_payment_id, organization_id)
            if not payment_data:
                raise ValueError("Failed payment not found")
            
            # Get retry configuration
            config = await self._get_retry_config(organization_id)
            if not config:
                config = await self._create_default_config(organization_id)
            
            # Calculate retry strategy
            retry_strategy = await self._calculate_retry_strategy(
                payment_data, config, organization_id
            )
            
            return {
                "retry_count": retry_strategy['retry_count'],
                "next_retry_date": retry_strategy['next_retry_date'],
                "strategy": retry_strategy['strategy'],
                "amount_to_charge": retry_strategy['amount_to_charge'],
                "payment_method": retry_strategy['payment_method'],
                "dunning_email_sequence": retry_strategy.get('dunning_step'),
                "estimated_success_rate": retry_strategy['success_rate']
            }
            
        except Exception as e:
            logger.error(f"Error calculating retry strategy: {e}")
            # Return safe default
            from datetime import datetime, timedelta
            return {
                "retry_count": 1,
                "next_retry_date": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                "strategy": "safe_default",
                "amount_to_charge": 0,
                "payment_method": "none",
                "dunning_email_sequence": None,
                "estimated_success_rate": 0.3
            }
    
    async def _get_failed_payment(self, payment_id: str, organization_id: str) -> Optional[Dict]:
        """Get failed payment data"""
        result = await self.db.table("payment_attempts").select("*")\
            .eq("id", payment_id)\
            .eq("organization_id", organization_id)\
            .eq("status", "failed")\
            .execute()
        return result.data[0] if result.data else None
    
    async def _get_retry_config(self, organization_id: str) -> Optional[Dict]:
        """Get payment retry configuration"""
        result = await self.db.table("payment_retry_configs").select("*")\
            .eq("organization_id", organization_id)\
            .eq("is_active", True)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        return result.data[0] if result.data else None
    
    async def _create_default_config(self, organization_id: str) -> Dict:
        """Create default retry configuration"""
        default_config = {
            "organization_id": organization_id,
            "name": "Default Retry Strategy",
            "strategy": "exponential",
            "initial_delay_hours": 24,
            "max_retries": 3,
            "success_threshold": 0.5,
            "amount_tiers": {
                "low": {"max_amount": 100, "strategy": "fixed", "delay_multiplier": 0.5},
                "medium": {"min_amount": 100, "max_amount": 500, "strategy": "linear", "delay_multiplier": 1.0},
                "high": {"min_amount": 500, "strategy": "exponential", "delay_multiplier": 1.5}
            },
            "is_active": True
        }
        
        result = await self.db.table("payment_retry_configs").insert(default_config).execute()
        return result.data[0] if result.data else default_config
    
    async def _calculate_retry_strategy(self, payment_data: Dict, config: Dict, organization_id: str) -> Dict:
        """Calculate optimal retry strategy"""
        from datetime import datetime, timedelta
        
        retry_count = payment_data.get('retry_count', 0)
        amount_cents = payment_data.get('amount_cents', 0)
        amount_dollars = amount_cents / 100
        
        # Determine amount tier
        tier = self._get_amount_tier(amount_dollars, config.get('amount_tiers', {}))
        
        # Calculate delay
        initial_delay = config.get('initial_delay_hours', 24)
        strategy = tier.get('strategy', config.get('strategy', 'exponential'))
        multiplier = tier.get('delay_multiplier', 1.0)
        
        if strategy == 'exponential':
            delay_hours = initial_delay * (2 ** retry_count) * multiplier
        elif strategy == 'linear':
            delay_hours = initial_delay * (retry_count + 1) * multiplier
        else:  # fixed
            delay_hours = initial_delay * multiplier
        
        next_retry_date = datetime.utcnow() + timedelta(hours=delay_hours)
        
        # Estimate success rate
        success_rate = self._estimate_success_rate(retry_count, strategy, amount_dollars)
        
        # Get dunning email step
        dunning_step = await self._get_dunning_email_step(retry_count, organization_id)
        
        return {
            "retry_count": retry_count + 1,
            "next_retry_date": next_retry_date,
            "strategy": strategy,
            "amount_to_charge": amount_cents,
            "payment_method": "same_as_failed",
            "dunning_step": dunning_step,
            "success_rate": success_rate
        }
    
    def _get_amount_tier(self, amount: float, amount_tiers: Dict) -> Dict:
        """Determine amount tier for retry configuration"""
        for tier_name, tier_config in amount_tiers.items():
            min_amount = tier_config.get('min_amount', 0)
            max_amount = tier_config.get('max_amount', float('inf'))
            
            if min_amount <= amount < max_amount:
                return tier_config
        
        # Default to medium tier
        return amount_tiers.get('medium', {
            "strategy": "exponential",
            "delay_multiplier": 1.0
        })
    
    def _estimate_success_rate(self, retry_count: int, strategy: str, amount: float) -> float:
        """Estimate success rate for retry attempt"""
        # Base success rate decreases with retries
        base_rates = {
            0: 0.7,  # First attempt
            1: 0.5,  # Second attempt
            2: 0.3,  # Third attempt
            3: 0.2,  # Fourth attempt
        }
        
        base_rate = base_rates.get(min(retry_count, 3), 0.1)
        
        # Adjust for strategy
        strategy_modifiers = {
            'exponential': 0.9,
            'linear': 1.0,
            'fixed': 1.1
        }
        strategy_modifier = strategy_modifiers.get(strategy, 1.0)
        
        # Adjust for amount (smaller amounts have higher success rates)
        amount_modifier = max(0.5, 1.2 - (amount / 1000))
        
        estimated_rate = base_rate * strategy_modifier * amount_modifier
        return max(0.05, min(0.95, estimated_rate))
    
    async def _get_dunning_email_step(self, retry_count: int, organization_id: str) -> Optional[Dict]:
        """Get dunning email sequence step for this retry"""
        result = await self.db.table("dunning_sequences").select("*")\
            .eq("organization_id", organization_id)\
            .eq("step_number", retry_count + 1)\
            .eq("is_active", True)\
            .execute()
        return result.data[0] if result.data else None


class DunningEmailService:
    """Dunning email sequence management"""
    
    def __init__(self, db_client):
        self.db = db_client
    
    async def process_dunning_sequence(self, failed_payment_id: str, organization_id: str) -> Dict[str, Any]:
        """Process dunning email sequence for failed payment"""
        try:
            # Get current sequence state
            sequence_state = await self._get_sequence_state(failed_payment_id, organization_id)
            
            if not sequence_state:
                # Start new sequence
                sequence_state = await self._start_new_sequence(failed_payment_id, organization_id)
            
            # Get next step
            next_step = await self._get_next_sequence_step(
                sequence_state['current_step'] + 1, organization_id
            )
            
            if not next_step:
                # Sequence complete
                return {
                    "action": "sequence_complete",
                    "message": "Dunning email sequence completed",
                    "escalation_required": True
                }
            
            # Check if step should be triggered
            should_trigger = await self._should_trigger_step(
                next_step, sequence_state, organization_id
            )
            
            if should_trigger:
                # Send email and advance sequence
                email_result = await self._send_dunning_email(
                    next_step, failed_payment_id, organization_id
                )
                
                # Update sequence state
                await self._update_sequence_state(
                    failed_payment_id, next_step['step_number'], organization_id
                )
                
                return {
                    "action": "email_sent",
                    "step_number": next_step['step_number'],
                    "email_template": next_step['email_template_key'],
                    "email_result": email_result,
                    "is_final_step": next_step.get('is_final', False)
                }
            else:
                return {
                    "action": "wait",
                    "message": "Conditions not met for next step",
                    "next_check_date": await self._get_next_check_date(next_step)
                }
                
        except Exception as e:
            logger.error(f"Error processing dunning sequence: {e}")
            return {
                "action": "error",
                "message": f"Error processing dunning sequence: {str(e)}"
            }
    
    async def _get_sequence_state(self, failed_payment_id: str, organization_id: str) -> Optional[Dict]:
        """Get current state of dunning sequence"""
        result = await self.db.table("dunning_sequence_states").select("*")\
            .eq("failed_payment_id", failed_payment_id)\
            .eq("organization_id", organization_id)\
            .eq("status", "active")\
            .execute()
        return result.data[0] if result.data else None
    
    async def _start_new_sequence(self, failed_payment_id: str, organization_id: str) -> Dict:
        """Start new dunning email sequence"""
        result = await self.db.table("dunning_sequence_states").insert({
            "organization_id": organization_id,
            "failed_payment_id": failed_payment_id,
            "current_step": 0,
            "status": "active",
            "started_at": datetime.utcnow().isoformat()
        }).execute()
        return result.data[0] if result.data else {}
    
    async def _get_next_sequence_step(self, step_number: int, organization_id: str) -> Optional[Dict]:
        """Get next step in dunning sequence"""
        result = await self.db.table("dunning_sequences").select("*")\
            .eq("organization_id", organization_id)\
            .eq("step_number", step_number)\
            .eq("is_active", True)\
            .execute()
        return result.data[0] if result.data else None
    
    async def _should_trigger_step(self, step: Dict, sequence_state: Dict, organization_id: str) -> bool:
        """Check if step should be triggered based on conditions"""
        conditions = step.get('conditions', {})
        
        # Check time-based conditions
        if 'delay_hours' in conditions:
            time_condition_met = await self._check_time_condition(
                sequence_state, conditions['delay_hours']
            )
            if not time_condition_met:
                return False
        
        # Check payment amount conditions
        if 'min_amount' in conditions:
            payment_data = await self._get_payment_data(
                sequence_state['failed_payment_id'], organization_id
            )
            if payment_data.get('amount_cents', 0) < conditions['min_amount'] * 100:
                return False
        
        return True
    
    async def _check_time_condition(self, sequence_state: Dict, required_hours: int) -> bool:
        """Check if time condition is met"""
        from datetime import datetime, timedelta
        
        last_step_time = sequence_state.get('last_step_at')
        if not last_step_time:
            # First step, check against sequence start
            start_time = datetime.fromisoformat(sequence_state['started_at'])
        else:
            last_step_time = datetime.fromisoformat(last_step_time)
            start_time = last_step_time
        
        time_elapsed = datetime.utcnow() - start_time
        return time_elapsed.total_seconds() >= (required_hours * 3600)
    
    async def _get_payment_data(self, failed_payment_id: str, organization_id: str) -> Dict:
        """Get payment data for conditions checking"""
        result = await self.db.table("payment_attempts").select("*")\
            .eq("id", failed_payment_id)\
            .eq("organization_id", organization_id)\
            .execute()
        return result.data[0] if result.data else {}
    
    async def _send_dunning_email(self, step: Dict, failed_payment_id: str, organization_id: str) -> Dict:
        """Send dunning email for step"""
        # This would integrate with the email service
        # For now, return a mock result
        return {
            "success": True,
            "message_id": f"dunning_{step['step_number']}_{failed_payment_id}",
            "sent_at": datetime.utcnow().isoformat()
        }
    
    async def _update_sequence_state(self, failed_payment_id: str, step_number: int, organization_id: str):
        """Update sequence state after sending email"""
        await self.db.table("dunning_sequence_states").update({
            "current_step": step_number,
            "last_step_at": datetime.utcnow().isoformat()
        }).eq("failed_payment_id", failed_payment_id)\
          .eq("organization_id", organization_id)\
          .execute()
    
    async def _get_next_check_date(self, step: Dict) -> str:
        """Get next date to check conditions"""
        from datetime import datetime, timedelta
        
        delay_hours = step.get('conditions', {}).get('delay_hours', 24)
        next_check = datetime.utcnow() + timedelta(hours=delay_hours)
        return next_check.isoformat()