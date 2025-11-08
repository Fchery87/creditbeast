"""
Analytics Service for CreditBeast
Business intelligence and reporting capabilities
Migrated to use official Supabase patterns
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging
from services.database import db

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for generating business intelligence and analytics using Supabase"""
    
    def __init__(self):
        self.client = db.admin_client

    async def get_revenue_analytics(self, org_id: str, days: int = 30) -> Dict:
        """Get revenue forecasting and trends"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Revenue by day using Supabase patterns
        try:
            # Query billing invoices for the period
            response = self.client.table("billing_invoices")\
                .select("created_at, amount, status")\
                .eq("organization_id", org_id)\
                .eq("status", "paid")\
                .gte("created_at", start_date.isoformat())\
                .lte("created_at", end_date.isoformat())\
                .execute()
            
            # Process daily revenue data
            daily_revenue_data = {}
            total_revenue = 0
            
            for invoice in response.data or []:
                invoice_date = invoice["created_at"][:10]  # Get date part
                amount = float(invoice["amount"] or 0)
                total_revenue += amount
                
                if invoice_date not in daily_revenue_data:
                    daily_revenue_data[invoice_date] = 0
                daily_revenue_data[invoice_date] += amount
            
            # Convert to list format
            daily_revenue = [
                {
                    'date': date_str,
                    'revenue': revenue
                }
                for date_str, revenue in sorted(daily_revenue_data.items())
            ]
            
        except Exception as e:
            logger.error(f"Error fetching daily revenue: {e}")
            daily_revenue = []
            total_revenue = 0
        
        # Monthly recurring revenue
        try:
            mrr_response = self.client.table("billing_subscriptions")\
                .select("price")\
                .eq("organization_id", org_id)\
                .eq("status", "active")\
                .execute()
            
            mrr = sum(float(sub.get("price", 0)) for sub in (mrr_response.data or []))
            
        except Exception as e:
            logger.error(f"Error fetching MRR: {e}")
            mrr = 0
        
        # Revenue growth rate calculation
        prev_start = start_date - timedelta(days=days)
        try:
            prev_response = self.client.table("billing_invoices")\
                .select("amount")\
                .eq("organization_id", org_id)\
                .eq("status", "paid")\
                .gte("created_at", prev_start.isoformat())\
                .lt("created_at", start_date.isoformat())\
                .execute()
            
            prev_revenue = sum(float(inv.get("amount", 0)) for inv in (prev_response.data or []))
            
        except Exception as e:
            logger.error(f"Error fetching previous revenue: {e}")
            prev_revenue = 0
        
        growth_rate = 0
        if prev_revenue > 0:
            growth_rate = ((total_revenue - prev_revenue) / prev_revenue) * 100
        
        return {
            'daily_revenue': daily_revenue,
            'monthly_recurring_revenue': float(mrr),
            'total_revenue_30d': float(total_revenue),
            'revenue_growth_rate': round(growth_rate, 2),
            'currency': 'USD'
        }

    async def get_dispute_analytics(self, org_id: str, days: int = 30) -> Dict:
        """Get dispute success rate analytics"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        try:
            # Get all disputes in period
            disputes_response = self.client.table("disputes")\
                .select("id, status, bureau_target, created_at")\
                .eq("organization_id", org_id)\
                .gte("created_at", start_date.isoformat())\
                .lte("created_at", end_date.isoformat())\
                .execute()
            
            disputes = disputes_response.data or []
            total_disputes = len(disputes)
            
            # Calculate successful disputes
            successful_disputes = len([
                d for d in disputes 
                if d.get("status") == "resolved_positive"
            ])
            
            success_rate = (successful_disputes / total_disputes * 100) if total_disputes > 0 else 0
            
            # Success rate by bureau
            bureau_stats = {}
            for dispute in disputes:
                bureau = dispute.get("bureau_target", "Unknown") or "Unknown"
                if bureau not in bureau_stats:
                    bureau_stats[bureau] = {"total": 0, "successful": 0}
                bureau_stats[bureau]["total"] += 1
                if dispute.get("status") == "resolved_positive":
                    bureau_stats[bureau]["successful"] += 1
            
            # Format bureau data
            by_bureau = [
                {
                    "bureau": bureau,
                    "total": stats["total"],
                    "successful": stats["successful"],
                    "success_rate": round((stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0, 2)
                }
                for bureau, stats in bureau_stats.items()
            ]
            
            # Monthly trends (last 12 months)
            monthly_stats = {}
            twelve_months_ago = end_date - timedelta(days=365)
            
            for dispute in disputes:
                if dispute["created_at"] >= twelve_months_ago.isoformat():
                    month = dispute["created_at"][:7]  # YYYY-MM format
                    if month not in monthly_stats:
                        monthly_stats[month] = {"total": 0, "successful": 0}
                    monthly_stats[month]["total"] += 1
                    if dispute.get("status") == "resolved_positive":
                        monthly_stats[month]["successful"] += 1
            
            monthly_trends = [
                {
                    "month": month,
                    "total": stats["total"],
                    "successful": stats["successful"],
                    "success_rate": round((stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0, 2)
                }
                for month, stats in sorted(monthly_stats.items())
            ]
            
        except Exception as e:
            logger.error(f"Error fetching dispute analytics: {e}")
            total_disputes = 0
            successful_disputes = 0
            success_rate = 0
            by_bureau = []
            monthly_trends = []
        
        return {
            'success_rate_overall': round(success_rate, 2),
            'total_disputes': total_disputes,
            'successful_disputes': successful_disputes,
            'by_bureau': by_bureau,
            'monthly_trends': monthly_trends
        }

    async def get_client_ltv_analytics(self, org_id: str) -> Dict:
        """Get client lifetime value calculations"""
        try:
            # Get clients with their billing data
            clients_response = self.client.table("clients")\
                .select("id, created_at, status")\
                .eq("organization_id", org_id)\
                .execute()
            
            if not clients_response.data:
                return {
                    'average_ltv': 0,
                    'total_clients': 0,
                    'paying_clients': 0
                }
            
            clients = clients_response.data
            total_clients = len(clients)
            
            # Get billing data for revenue calculations
            invoices_response = self.client.table("billing_invoices")\
                .select("client_id, amount, status")\
                .eq("organization_id", org_id)\
                .eq("status", "paid")\
                .execute()
            
            # Process client revenue data
            client_revenue = {}
            paying_clients = set()
            
            for invoice in invoices_response.data or []:
                client_id = invoice.get("client_id")
                amount = float(invoice.get("amount", 0))
                
                if client_id:
                    paying_clients.add(client_id)
                    if client_id not in client_revenue:
                        client_revenue[client_id] = 0
                    client_revenue[client_id] += amount
            
            # Calculate LTV statistics
            ltv_values = list(client_revenue.values())
            average_ltv = sum(ltv_values) / len(ltv_values) if ltv_values else 0
            
            # Client cohort analysis
            cohort_analysis = {}
            for client in clients:
                created_month = client["created_at"][:7]  # YYYY-MM
                if created_month not in cohort_analysis:
                    cohort_analysis[created_month] = {
                        "clients": 0,
                        "total_revenue": 0,
                        "avg_ltv": 0
                    }
                cohort_analysis[created_month]["clients"] += 1
                
                # Add revenue if client has paid invoices
                client_id = client["id"]
                if client_id in client_revenue:
                    cohort_analysis[created_month]["total_revenue"] += client_revenue[client_id]
            
            # Calculate average LTV per cohort
            for cohort in cohort_analysis.values():
                cohort["avg_ltv"] = cohort["total_revenue"] / cohort["clients"] if cohort["clients"] > 0 else 0
            
            return {
                'average_ltv': round(average_ltv, 2),
                'total_clients': total_clients,
                'paying_clients': len(paying_clients),
                'ltv_distribution': ltv_values,
                'cohort_analysis': [
                    {
                        'cohort': cohort,
                        **data
                    }
                    for cohort, data in sorted(cohort_analysis.items())
                ]
            }
            
        except Exception as e:
            logger.error(f"Error fetching LTV analytics: {e}")
            return {
                'average_ltv': 0,
                'total_clients': 0,
                'paying_clients': 0,
                'ltv_distribution': [],
                'cohort_analysis': []
            }

    async def get_churn_analysis(self, org_id: str) -> Dict:
        """Get churn analysis and prevention insights"""
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        
        try:
            # Get churned clients
            churned_response = self.client.table("clients")\
                .select("id, status, updated_at, churn_reason")\
                .eq("organization_id", org_id)\
                .eq("status", "churned")\
                .gte("updated_at", start_date.isoformat())\
                .lte("updated_at", end_date.isoformat())\
                .execute()
            
            churned_clients = churned_response.data or []
            churned_clients_count = len(churned_clients)
            
            # Get active clients at start
            active_start_response = self.client.table("clients")\
                .select("id", count="exact")\
                .eq("organization_id", org_id)\
                .eq("status", "active")\
                .lte("created_at", start_date.isoformat())\
                .execute()
            
            active_start = active_start_response.count or 0
            
            # Calculate churn rate
            churn_rate = (churned_clients_count / active_start * 100) if active_start > 0 else 0
            
            # Churn reasons analysis
            churn_reasons = {}
            for client in churned_clients:
                reason = client.get("churn_reason", "Unknown") or "Unknown"
                churn_reasons[reason] = churn_reasons.get(reason, 0) + 1
            
            # Inactive clients (no recent activity)
            thirty_days_ago = end_date - timedelta(days=30)
            inactive_response = self.client.table("clients")\
                .select("id", count="exact")\
                .eq("organization_id", org_id)\
                .eq("status", "active")\
                .lt("updated_at", thirty_days_ago.isoformat())\
                .execute()
            
            inactive_clients = inactive_response.count or 0
            
        except Exception as e:
            logger.error(f"Error fetching churn analysis: {e}")
            churned_clients_count = 0
            churn_rate = 0
            churn_reasons = {}
            inactive_clients = 0
        
        return {
            'churn_rate_90d': round(churn_rate, 2),
            'churned_clients_90d': churned_clients_count,
            'total_clients_at_risk': inactive_clients,
            'high_risk_clients': 0,  # Would need more complex logic
            'churn_reasons': [
                {'reason': reason, 'count': count}
                for reason, count in sorted(churn_reasons.items(), key=lambda x: x[1], reverse=True)
            ],
            'retention_score': max(0, 100 - churn_rate)
        }

    async def get_operational_analytics(self, org_id: str) -> Dict:
        """Get operational analytics dashboard"""
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        try:
            # Client onboarding funnel
            leads_response = self.client.table("clients")\
                .select("id", count="exact")\
                .eq("organization_id", org_id)\
                .in_("status", ["lead", "active"])\
                .gte("created_at", start_date.isoformat())\
                .lte("created_at", end_date.isoformat())\
                .execute()
            
            leads_total = leads_response.count or 0
            
            # Completed onboarding (active clients)
            active_response = self.client.table("clients")\
                .select("id", count="exact")\
                .eq("organization_id", org_id)\
                .eq("status", "active")\
                .gte("created_at", start_date.isoformat())\
                .lte("created_at", end_date.isoformat())\
                .execute()
            
            onboarding_completed = active_response.count or 0
            
            # System metrics
            users_response = self.client.table("organizations")\
                .select("owner_user_id", count="exact")\
                .eq("id", org_id)\
                .execute()
            
            total_users = 1  # Simplified - would need proper user table
            active_subscriptions = 1  # Simplified - would need proper subscription table
            
        except Exception as e:
            logger.error(f"Error fetching operational analytics: {e}")
            leads_total = 0
            onboarding_completed = 0
            total_users = 1
            active_subscriptions = 1
        
        return {
            'onboarding': {
                'total_leads_30d': leads_total,
                'completed_onboarding_30d': onboarding_completed,
                'onboarding_rate': round((onboarding_completed / leads_total * 100) if leads_total > 0 else 0, 2)
            },
            'system_usage': {
                'total_users': total_users,
                'active_subscriptions': active_subscriptions,
                'avg_clients_per_user': round(leads_total / total_users, 1) if total_users > 0 else 0
            },
            'daily_activity': [],  # Would need audit logs table
            'performance_score': 85
        }

    async def get_all_analytics(self, org_id: str) -> Dict:
        """Get comprehensive analytics summary"""
        try:
            revenue = await self.get_revenue_analytics(org_id)
            disputes = await self.get_dispute_analytics(org_id)
            ltv = await self.get_client_ltv_analytics(org_id)
            churn = await self.get_churn_analysis(org_id)
            operational = await self.get_operational_analytics(org_id)
            
            return {
                'revenue': revenue,
                'disputes': disputes,
                'client_ltv': ltv,
                'churn': churn,
                'operational': operational,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive analytics: {e}")
            return {
                'revenue': {},
                'disputes': {},
                'client_ltv': {},
                'churn': {},
                'operational': {},
                'generated_at': datetime.now().isoformat(),
                'error': str(e)
            }

# Global analytics service instance
analytics_service = AnalyticsService()