"""
Report generation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List, Optional
from app.models.report import Report, ReportCreate, ReportFilters, ReportStats
from app.services.report_service import ReportService
from app.services.database import get_database
from app.core.security import get_current_active_user, require_faculty_or_admin, TokenData
from motor.motor_asyncio import AsyncIOMotorDatabase
import os

router = APIRouter()

@router.get("/individual/{activity_id}", response_model=dict)
async def get_individual_report(
    activity_id: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get individual activity report (HTML)"""
    report_service = ReportService(db)
    
    # Check if activity exists and user has access
    activity = await report_service.get_activity_for_report(activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    # Users can only view their own reports unless they're admin
    if (current_user.user_id != activity["user_id"] and 
        current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Generate HTML report
    html_content = await report_service.generate_individual_html(activity)
    return {"html": html_content}

@router.get("/individual/{activity_id}/pdf")
async def get_individual_report_pdf(
    activity_id: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Download individual activity report as PDF"""
    report_service = ReportService(db)
    
    # Check if activity exists and user has access
    activity = await report_service.get_activity_for_report(activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    # Users can only view their own reports unless they're admin
    if (current_user.user_id != activity["user_id"] and 
        current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Generate report (currently returns HTML, can be converted to PDF later)
    pdf_path = await report_service.generate_individual_pdf(activity)
    
    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report"
        )
    
    # Read the generated file
    with open(pdf_path, "rb") as f:
        file_content = f.read()
    
    # Determine content type based on file extension
    if pdf_path.endswith('.html'):
        media_type = "text/html"
        filename = f"activity_{activity_id}_report.html"
    else:
        media_type = "application/pdf"
        filename = f"activity_{activity_id}_report.pdf"
    
    return Response(
        content=file_content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.get("/group", response_model=dict)
async def get_group_report(
    department: Optional[str] = None,
    year: Optional[int] = None,
    type: Optional[str] = None,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get group report (HTML)"""
    report_service = ReportService(db)
    
    user_id_filter: Optional[str] = None
    effective_department = department
    
    if current_user.role in ["admin", "faculty"]:
        # Faculty can only view their department unless specified
        if current_user.role == "faculty" and effective_department and current_user.department != effective_department:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other department's reports"
            )
        if current_user.role == "faculty" and not effective_department:
            effective_department = current_user.department
    else:
        # Students can ONLY view their own achievements - ignore all filters
        # Force user_id filter and ignore department/year/type filters for students
        user_id_filter = current_user.user_id
        effective_department = None  # Ignore department filter for students
        year = None  # Ignore year filter for students
        type = None  # Ignore type filter for students
    
    # Generate HTML report
    html_content = await report_service.generate_group_html(
        department=effective_department,
        year=year,
        type=type,
        user_id=user_id_filter
    )
    return {"html": html_content}

@router.get("/group/pdf")
async def get_group_report_pdf(
    department: Optional[str] = None,
    year: Optional[int] = None,
    type: Optional[str] = None,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Download group report as PDF"""
    report_service = ReportService(db)
    
    user_id_filter: Optional[str] = None
    effective_department = department
    
    if current_user.role in ["admin", "faculty"]:
        if current_user.role == "faculty" and effective_department and current_user.department != effective_department:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other department's reports"
            )
        if current_user.role == "faculty" and not effective_department:
            effective_department = current_user.department
    else:
        # Students can ONLY view their own achievements - ignore all filters
        # Force user_id filter and ignore department/year/type filters for students
        user_id_filter = current_user.user_id
        effective_department = None  # Ignore department filter for students
        year = None  # Ignore year filter for students
        type = None  # Ignore type filter for students
    
    # Generate report (currently returns HTML, can be converted to PDF later)
    pdf_path = await report_service.generate_group_pdf(
        department=effective_department,
        year=year,
        type=type,
        user_id=user_id_filter
    )
    
    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report"
        )
    
    # Read the generated file
    with open(pdf_path, "rb") as f:
        file_content = f.read()
    
    # Determine content type based on file extension
    if pdf_path.endswith('.html'):
        media_type = "text/html"
        filename = f"group_report_{department or 'all'}_{year or 'all'}.html"
    else:
        media_type = "application/pdf"
        filename = f"group_report_{department or 'all'}_{year or 'all'}.pdf"
    
    return Response(
        content=file_content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.get("/stats")
async def get_report_stats(
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get report statistics with error handling and all departments for dropdown"""
    try:
        report_service = ReportService(db)
        stats = None

        # Logic: Admins see all, Faculty see their Department stats, Students see their own stats
        if current_user.role == "admin":
            stats = await report_service.get_all_stats()
        elif current_user.role == "faculty":
            # Faculty see their department stats
            if not current_user.department:
                # Return empty stats but still include all departments for dropdown
                all_departments = await report_service.get_all_departments()
                return {
                    "total_activities": 0,
                    "accepted_activities": 0,
                    "rejected_activities": 0,
                    "pending_activities": 0,
                    "total_users": 0,
                    "departments": all_departments,
                    "activity_types": [],
                    "monthly_stats": []
                }
            stats = await report_service.get_department_stats(current_user.department)
        else:
            # Students see their own activities stats (including group activities where they're members)
            stats = await report_service.get_user_stats(current_user.user_id)

        # SAFETY CHECK: If service returns None (empty DB), return defaults
        if not stats:
            all_departments = await report_service.get_all_departments()
            return {
                "total_activities": 0,
                "accepted_activities": 0,
                "rejected_activities": 0,
                "pending_activities": 0,
                "total_users": 0,
                "departments": all_departments,
                "activity_types": [],
                "monthly_stats": []
            }

        # For non-admin users, replace departments list with all departments for dropdown
        # but keep the stats filtered to their department
        if current_user.role != "admin":
            all_departments = await report_service.get_all_departments()
            # Convert stats to dict and update departments
            try:
                # Try Pydantic v1 method
                stats_dict = stats.dict()
            except AttributeError:
                try:
                    # Try Pydantic v2 method
                    stats_dict = stats.model_dump()
                except AttributeError:
                    # Fallback: construct dict manually
                    stats_dict = {
                        "total_activities": stats.total_activities,
                        "accepted_activities": stats.accepted_activities,
                        "rejected_activities": stats.rejected_activities,
                        "pending_activities": stats.pending_activities,
                        "total_users": stats.total_users,
                        "departments": stats.departments,
                        "activity_types": stats.activity_types,
                        "monthly_stats": stats.monthly_stats
                    }
            stats_dict["departments"] = all_departments
            return stats_dict

        # For admin, return stats as dict
        try:
            return stats.dict()
        except AttributeError:
            try:
                return stats.model_dump()
            except AttributeError:
                return {
                    "total_activities": stats.total_activities,
                    "accepted_activities": stats.accepted_activities,
                    "rejected_activities": stats.rejected_activities,
                    "pending_activities": stats.pending_activities,
                    "total_users": stats.total_users,
                    "departments": stats.departments,
                    "activity_types": stats.activity_types,
                    "monthly_stats": stats.monthly_stats
                }

    except Exception as e:
        # This prints the REAL error to your VS Code Terminal
        print(f"❌ CRITICAL ERROR in /stats endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Try to get departments even on error
        try:
            report_service = ReportService(db)
            all_departments = await report_service.get_all_departments()
        except:
            all_departments = []
        
        # Return empty data so the Frontend doesn't break
        return {
            "total_activities": 0,
            "accepted_activities": 0,
            "rejected_activities": 0,
            "pending_activities": 0,
            "total_users": 0,
            "departments": all_departments,
            "activity_types": [],
            "monthly_stats": [],
            "error": str(e) # This will help you see the error in Network tab too
        }

@router.post("/generate", response_model=Report)
async def generate_report(
    report_data: ReportCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Generate a new report"""
    report_service = ReportService(db)
    
    # Generate report
    report = await report_service.create_report(
        report_data, 
        current_user.user_id
    )
    
    return report

@router.get("/templates")
async def get_report_templates(
    current_user: TokenData = Depends(get_current_active_user)
):
    """Get available report templates"""
    templates = [
        {
            "id": "individual",
            "name": "Individual Activity Report",
            "description": "Report for a single activity"
        },
        {
            "id": "group",
            "name": "Group Report",
            "description": "Report for multiple activities"
        },
        {
            "id": "department",
            "name": "Department Report",
            "description": "Report for a department"
        },
        {
            "id": "yearly",
            "name": "Yearly Report",
            "description": "Annual report for the institution"
        }
    ]
    
    return {"templates": templates}
