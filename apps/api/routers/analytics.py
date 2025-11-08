"""
Analytics API Router
Business intelligence and reporting endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from typing import Dict, List
from datetime import datetime
import logging
from services.analytics import analytics_service
from services.export_service import ExportService
from middleware.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/revenue", summary="Revenue Analytics")
async def get_revenue_analytics(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get revenue forecasting and trends"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        revenue_data = await analytics_service.get_revenue_analytics(org_id, days)
        return {
            "success": True,
            "data": revenue_data
        }
    except Exception as e:
        logger.error(f"Error fetching revenue analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/disputes", summary="Dispute Analytics")
async def get_dispute_analytics(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get dispute success rate analytics"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        dispute_data = await analytics_service.get_dispute_analytics(org_id, days)
        return {
            "success": True,
            "data": dispute_data
        }
    except Exception as e:
        logger.error(f"Error fetching dispute analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/client-ltv", summary="Client LTV Analytics")
async def get_client_ltv_analytics(
    current_user: dict = Depends(get_current_user)
):
    """Get client lifetime value calculations"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        ltv_data = await analytics_service.get_client_ltv_analytics(org_id)
        return {
            "success": True,
            "data": ltv_data
        }
    except Exception as e:
        logger.error(f"Error fetching LTV analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/churn", summary="Churn Analysis")
async def get_churn_analysis(
    current_user: dict = Depends(get_current_user)
):
    """Get churn analysis and prevention insights"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        churn_data = await analytics_service.get_churn_analysis(org_id)
        return {
            "success": True,
            "data": churn_data
        }
    except Exception as e:
        logger.error(f"Error fetching churn analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/operational", summary="Operational Analytics")
async def get_operational_analytics(
    current_user: dict = Depends(get_current_user)
):
    """Get operational analytics dashboard"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        operational_data = await analytics_service.get_operational_analytics(org_id)
        return {
            "success": True,
            "data": operational_data
        }
    except Exception as e:
        logger.error(f"Error fetching operational analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", summary="Analytics Summary")
async def get_analytics_summary(
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive analytics summary"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        summary_data = await analytics_service.get_all_analytics(org_id)
        return {
            "success": True,
            "data": summary_data
        }
    except Exception as e:
        logger.error(f"Error fetching analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{report_type}", summary="Export Analytics Report")
async def export_analytics_report(
    report_type: str,
    format: str = "json",
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Export analytics report in various formats"""
    try:
        org_id = current_user.get("org_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="Organization ID required")
        
        valid_reports = ["revenue", "disputes", "client_ltv", "churn", "operational", "summary"]
        if report_type not in valid_reports:
            raise HTTPException(status_code=400, detail=f"Invalid report type. Choose from: {', '.join(valid_reports)}")
        
        if report_type == "revenue":
            data = await analytics_service.get_revenue_analytics(org_id, days)
        elif report_type == "disputes":
            data = await analytics_service.get_dispute_analytics(org_id, days)
        elif report_type == "client_ltv":
            data = await analytics_service.get_client_ltv_analytics(org_id)
        elif report_type == "churn":
            data = await analytics_service.get_churn_analysis(org_id)
        elif report_type == "operational":
            data = await analytics_service.get_operational_analytics(org_id)
        else:  # summary
            data = await analytics_service.get_all_analytics(org_id)
        
        # Get organization name for branding
        org_name = "CreditBeast"  # Default
        try:
            from services.database import db
            org_result = await db.admin_client.table("organizations")\
                .select("name")\
                .eq("id", org_id)\
                .execute()
            if org_result.data:
                org_name = org_result.data[0].get("name", "CreditBeast")
        except Exception as e:
            logger.warning(f"Could not fetch organization name: {e}")

        if format == "csv":
            # Export to CSV
            csv_content = ExportService.export_analytics_report(
                data=data,
                report_type=report_type,
                format="csv",
                org_name=org_name
            )
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={report_type}_analytics_{datetime.now().strftime('%Y%m%d')}.csv"
                }
            )
        elif format == "pdf":
            # Export to PDF
            pdf_content = ExportService.export_analytics_report(
                data=data,
                report_type=report_type,
                format="pdf",
                org_name=org_name
            )
            return Response(
                content=pdf_content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={report_type}_analytics_{datetime.now().strftime('%Y%m%d')}.pdf"
                }
            )

        # Default JSON response
        return {
            "success": True,
            "data": data,
            "export_format": format,
            "report_type": report_type
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting analytics report: {e}")
        raise HTTPException(status_code=500, detail=str(e))