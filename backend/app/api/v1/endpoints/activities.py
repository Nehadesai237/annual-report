"""
Activity management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
from app.models.activity import (
    Activity, ActivityCreate, ActivityUpdate, ActivityList, 
    ActivityFilters, ActivityStatus
)
from app.services.activity_service import ActivityService
from app.services.database import get_database
from app.services.certificate_validator import certificate_validator
from app.core.security import get_current_active_user, require_faculty_or_admin, TokenData
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import os
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=Activity, status_code=status.HTTP_201_CREATED)
async def create_activity(
    title: str = Form(...),
    description: str = Form(...),
    type: str = Form(...),
    year: int = Form(...),
    achievement_type: str = Form("individual"),
    group_members: Optional[str] = Form(None),  # JSON string array of user IDs
    has_certificate: bool = Form(False),
    files: List[UploadFile] = File(...),
    certificate: Optional[UploadFile] = File(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new activity with images and optional certificate"""
    activity_service = ActivityService(db)
    
    # Parse group_members if provided
    group_members_list = []
    if achievement_type == "group" and group_members:
        import json
        try:
            group_members_list = json.loads(group_members)
            if not isinstance(group_members_list, list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="group_members must be a JSON array"
                )
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid group_members JSON format"
            )
    
    # Validate file types and sizes
    for file in files:
        if file.content_type not in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {file.content_type}"
            )
        
        # Check file size (10MB limit)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # Reset file pointer
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} is too large"
            )
    
    # Handle certificate if provided
    certificate_path = None
    certificate_validated = False
    certificate_validation_result = None
    
    # Only process certificate if user indicated they have one AND provided the file
    if has_certificate and certificate:
        # Validate certificate file type
        allowed_cert_types = [
            "image/jpeg", "image/png", "image/gif", "image/webp",
            "application/pdf"
        ]
        
        if certificate.content_type not in allowed_cert_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Certificate must be an image or PDF"
            )
        
        # Check file size (15MB limit for certificates)
        cert_content = await certificate.read()
        cert_size = len(cert_content)
        await certificate.seek(0)
        
        if cert_size > 15 * 1024 * 1024:  # 15MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Certificate file is too large (max 15MB)"
            )
        
        # Save certificate file
        file_extension = certificate.filename.split('.')[-1]
        unique_filename = f"cert_{uuid.uuid4()}.{file_extension}"
        certificate_file_path = os.path.join("uploads", "certificates", unique_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(certificate_file_path), exist_ok=True)
        
        # Write certificate file
        with open(certificate_file_path, "wb") as f:
            f.write(cert_content)
        
        # Validate certificate with ML (use file system path)
        validation_result = certificate_validator.validate_certificate(
            certificate_path=certificate_file_path,
            activity_title=title,
            activity_description=description
        )
        
        certificate_validated = validation_result["valid"]
        certificate_validation_result = validation_result
        
        # If certificate doesn't match, reject the activity
        if not certificate_validated:
            # Delete uploaded certificate
            if os.path.exists(certificate_file_path):
                os.remove(certificate_file_path)
            certificate_path = None
            
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": {
                        "code": "CERTIFICATE_VALIDATION_FAILED",
                        "message": "Certificate does not match the activity details. Please upload a certificate that matches your activity.",
                        "details": validation_result
                    }
                }
            )
        else:
            # Store URL-friendly path for certificate (only if validated)
            certificate_path = f"/uploads/certificates/{unique_filename}"
    
    # Create activity data
    activity_data_dict = {
        "title": title,
        "description": description,
        "type": type,
        "year": year,
        "achievement_type": achievement_type,
        "group_members": group_members_list
    }
    activity_data = ActivityCreate(**activity_data_dict)
    
    # Create activity with ML verification
    activity = await activity_service.create_activity_with_certificate(
        activity_data,
        current_user.user_id,
        files,
        certificate_path=certificate_path,
        has_certificate=has_certificate,
        certificate_validated=certificate_validated,
        certificate_validation_result=certificate_validation_result
    )
    
    return activity

@router.get("/", response_model=ActivityList)
async def get_activities(
    user_id: Optional[str] = None,
    department: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    year: Optional[int] = None,
    page: int = 1,
    size: int = 10,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get activities with filters - includes admin-created public activities"""
    activity_service = ActivityService(db)
    
    # Debug logging
    print(f"[DEBUG] Current user: user_id={current_user.user_id}, role={current_user.role}")
    print(f"[DEBUG] Request user_id parameter: {user_id}")
    
    # For non-admin users, show ONLY their own activities (NOT admin-created events)
    include_public = False
    if current_user.role != "admin":
        # If user_id is specified and it's not the current user, only show if admin
        if user_id and user_id != current_user.user_id:
            user_id = current_user.user_id
        # DO NOT include public admin-created activities - students should only see their own achievements
        include_public = False
        # Set user_id to current user to show their own activities
        if not user_id:
            user_id = current_user.user_id
    
    # Handle empty strings - convert to None
    type_enum = None
    if type and type.strip():
        try:
            from app.models.activity import ActivityType
            type_enum = ActivityType(type)
        except ValueError:
            type_enum = None
    
    status_enum = None
    if status and status.strip():
        try:
            from app.models.activity import ActivityStatus
            status_enum = ActivityStatus(status)
        except ValueError:
            status_enum = None
    
    filters = ActivityFilters(
        user_id=user_id,
        department=department if department and department.strip() else None,
        type=type_enum,
        status=status_enum,
        year=year,
        page=page,
        size=size
    )
    
    activities = await activity_service.get_activities(filters, include_public=include_public)
    return activities

@router.get("/public", response_model=ActivityList)
async def get_public_activities(
    department: Optional[str] = None,
    type: Optional[str] = None,
    year: Optional[int] = None,
    page: int = 1,
    size: int = 10,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get public activities - approved student achievements and admin-created public activities (no authentication required)"""
    activity_service = ActivityService(db)
    
    print(f"[DEBUG] Public activities endpoint called: page={page}, size={size}, department={department}, type={type}, year={year}")
    
    # Show approved student achievements (status=accepted) OR admin-created public activities
    # This allows guests to see real student achievements that have been approved
    base_filters = {}
    if department:
        base_filters["department"] = department
    if type:
        base_filters["type"] = type
    if year:
        base_filters["year"] = year
    
    # Build $or conditions with base filters applied to each
    or_conditions = [
        {
            "status": "accepted",
            "is_admin_created": {"$ne": True}  # Student-created activities that are accepted
        },
        {
            "is_public": True,
            "is_admin_created": True,
            "status": "accepted"  # Admin-created public activities
        }
    ]
    
    # Apply base filters to each condition
    for condition in or_conditions:
        condition.update(base_filters)
    
    filter_dict = {"$or": or_conditions}
    
    print(f"[DEBUG] Filter dict: {filter_dict}")
    
    skip = (page - 1) * size
    total = await activity_service.collection.count_documents(filter_dict)
    print(f"[DEBUG] Total activities found: {total}")
    
    cursor = activity_service.collection.find(filter_dict).skip(skip).limit(size).sort("created_at", -1)
    activities = []
    
    # Get user service to fetch user names
    from app.services.user_service import UserService
    user_service = UserService(db)
    
    async for activity_doc in cursor:
        try:
            print(f"[DEBUG] Processing activity: {activity_doc.get('_id')}, title: {activity_doc.get('title')}, status: {activity_doc.get('status')}")
            normalized_doc = activity_service._normalize_activity_doc(activity_doc)
            
            # Populate user_name if user_id exists
            if normalized_doc.get("user_id"):
                try:
                    user = await user_service.get_by_id(normalized_doc["user_id"])
                    if user:
                        normalized_doc["user_name"] = user.name
                        print(f"[DEBUG] Found user: {user.name}")
                except Exception as e:
                    print(f"[WARNING] Could not fetch user {normalized_doc.get('user_id')}: {e}")
                    normalized_doc["user_name"] = None
            
            activity = Activity(**normalized_doc)
            activities.append(activity)
            print(f"[DEBUG] Added activity: {activity.title}")
        except Exception as e:
            print(f"[ERROR] Error processing activity {activity_doc.get('_id')}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"[DEBUG] Returning {len(activities)} activities")
    
    return ActivityList(
        activities=activities,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )

@router.get("/{activity_id}", response_model=Activity)
async def get_activity(
    activity_id: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get activity by ID"""
    try:
        print(f"[DEBUG] Getting activity {activity_id} for user {current_user.user_id} (role: {current_user.role})")
        activity_service = ActivityService(db)
        
        # Validate ObjectId format
        try:
            # Try to create ObjectId - this will raise if invalid
            activity_object_id = ObjectId(activity_id)
            print(f"[DEBUG] Valid ObjectId: {activity_id}")
        except Exception as e:
            print(f"[ERROR] Invalid activity ID format: {activity_id}, error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid activity ID format: {str(e)}"
            )
        
        print(f"[DEBUG] Calling get_by_id with: {activity_id}")
        activity = await activity_service.get_by_id(activity_id)
        if not activity:
            print(f"[ERROR] Activity {activity_id} not found in database")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found"
            )
        
        print(f"[DEBUG] Found activity: user_id={activity.user_id}, current_user_id={current_user.user_id}")
        
        # Check if activity is public admin-created by checking raw document
        try:
            activity_doc = await activity_service.collection.find_one({"_id": ObjectId(activity_id)})
            is_public_admin = activity_doc and activity_doc.get("is_public", False) and activity_doc.get("is_admin_created", False)
        except Exception as e:
            print(f"[ERROR] Error checking activity document: {e}")
            is_public_admin = False
        
        print(f"[DEBUG] is_public_admin={is_public_admin}, activity.user_id={activity.user_id}, current_user.user_id={current_user.user_id}")
        
        # Users can view their own activities, admin-created public activities, or if they're admin
        if (current_user.user_id != activity.user_id and 
            current_user.role != "admin" and
            not is_public_admin):
            print(f"[ERROR] Permission denied: user {current_user.user_id} cannot view activity {activity_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to view this activity"
            )
        
        print(f"[DEBUG] Returning activity {activity_id}")
        return activity
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error getting activity {activity_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching activity: {str(e)}"
        )

@router.put("/{activity_id}", response_model=Activity)
async def update_activity(
    activity_id: str,
    activity_update: ActivityUpdate,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update activity"""
    activity_service = ActivityService(db)
    
    # Check if activity exists
    activity = await activity_service.get_by_id(activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    # Users can only update their own activities unless they're admin
    if (current_user.user_id != activity.user_id and 
        current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Cannot update accepted activities
    if activity.status == ActivityStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update accepted activities"
        )
    
    # Update activity
    updated_activity = await activity_service.update_activity(activity_id, activity_update)
    return updated_activity

@router.delete("/{activity_id}")
async def delete_activity(
    activity_id: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete activity"""
    activity_service = ActivityService(db)
    
    # Check if activity exists
    activity = await activity_service.get_by_id(activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    # Users can only delete their own activities unless they're admin
    if (current_user.user_id != activity.user_id and 
        current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Cannot delete accepted activities
    if activity.status == ActivityStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete accepted activities"
        )
    
    # Delete activity
    await activity_service.delete_activity(activity_id)
    return {"message": "Activity deleted successfully"}

@router.get("/user/{user_id}/activities", response_model=List[Activity])
async def get_user_activities(
    user_id: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get activities for a specific user"""
    activity_service = ActivityService(db)
    
    # Users can only view their own activities unless they're admin
    if current_user.user_id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    activities = await activity_service.get_user_activities(user_id)
    return activities

@router.get("/department/{department}/activities", response_model=List[Activity])
async def get_department_activities(
    department: str,
    current_user: TokenData = Depends(require_faculty_or_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get activities for a specific department"""
    activity_service = ActivityService(db)
    
    # Faculty can only view their own department's activities
    if (current_user.role == "faculty" and 
        current_user.department != department):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view other department's activities"
        )
    
    activities = await activity_service.get_department_activities(department)
    return activities
