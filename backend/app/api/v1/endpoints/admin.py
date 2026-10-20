"""
Admin endpoints for activity review and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.models.activity import Activity, ActivityStatus
from app.models.user import User, UserRole, UserUpdate
from app.models.notification import NotificationUpdate
from app.services.activity_service import ActivityService
from app.services.user_service import UserService
from app.services.database import get_database
from app.core.security import require_admin, TokenData
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

@router.get("/rejected", response_model=List[Activity])
async def get_rejected_activities(
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all rejected activities for admin review"""
    activity_service = ActivityService(db)
    
    activities = await activity_service.get_rejected_activities()
    return activities

@router.get("/pending", response_model=List[Activity])
async def get_pending_activities(
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all pending activities"""
    activity_service = ActivityService(db)
    
    activities = await activity_service.get_pending_activities()
    return activities

@router.post("/approve/{activity_id}")
async def approve_activity(
    activity_id: str,
    body: Optional[dict] = Body(default=None),
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Approve an activity (can approve pending or rejected activities)"""
    activity_service = ActivityService(db)
    
    # Get comments from body
    comments = body.get("comments") if body and isinstance(body, dict) else None
    
    # Check if activity exists
    activity = await activity_service.get_by_id(activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    # Can approve pending or rejected activities
    if activity.status == ActivityStatus.ACCEPTED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activity is already accepted"
        )
    
    # Update status to accepted
    update_data = {
        "status": ActivityStatus.ACCEPTED.value,
        "admin_reviewed_at": datetime.utcnow(),
        "admin_reviewed_by": current_user.user_id,
        "admin_comments": comments,
        "updated_at": datetime.utcnow()
    }
    
    await activity_service.collection.update_one(
        {"_id": ObjectId(activity_id)},
        {"$set": update_data}
    )
    
    # Create notification
    from app.services.notification_service import NotificationService
    notification_service = NotificationService(db)
    await notification_service.create_notification(
        user_id=activity.user_id,
        title="Activity Approved",
        message=f"Your activity '{activity.title}' has been approved by admin." + (f" Comments: {comments}" if comments else ""),
        type="activity_approved"
    )
    
    return {"message": "Activity approved successfully"}

@router.post("/discard/{activity_id}")
async def discard_activity(
    activity_id: str,
    comments: str = None,
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Permanently discard a rejected activity"""
    activity_service = ActivityService(db)
    
    # Check if activity exists
    activity = await activity_service.get_by_id(activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    # Can only discard rejected activities
    if activity.status != ActivityStatus.REJECTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only discard rejected activities"
        )
    
    # Discard activity
    await activity_service.discard_activity(
        activity_id, 
        current_user.user_id, 
        comments
    )
    
    return {"message": "Activity discarded successfully"}

@router.get("/stats")
async def get_admin_stats(
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get admin dashboard statistics"""
    activity_service = ActivityService(db)
    
    stats = await activity_service.get_admin_stats()
    return stats

@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get audit logs"""
    activity_service = ActivityService(db)
    
    logs = await activity_service.get_audit_logs(skip=skip, limit=limit)
    return logs

@router.post("/bulk-approve")
async def bulk_approve_activities(
    activity_ids: List[str],
    comments: str = None,
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Bulk approve multiple activities"""
    activity_service = ActivityService(db)
    
    results = []
    for activity_id in activity_ids:
        try:
            activity = await activity_service.get_by_id(activity_id)
            if not activity:
                results.append({
                    "activity_id": activity_id,
                    "status": "error",
                    "message": "Activity not found"
                })
                continue
            
            if activity.status != ActivityStatus.REJECTED:
                results.append({
                    "activity_id": activity_id,
                    "status": "error",
                    "message": "Can only approve rejected activities"
                })
                continue
            
            await activity_service.approve_activity(
                activity_id, 
                current_user.user_id, 
                comments
            )
            
            results.append({
                "activity_id": activity_id,
                "status": "success",
                "message": "Activity approved"
            })
            
        except Exception as e:
            results.append({
                "activity_id": activity_id,
                "status": "error",
                "message": str(e)
            })
    
    return {"results": results}

@router.post("/bulk-discard")
async def bulk_discard_activities(
    activity_ids: List[str],
    comments: str = None,
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Bulk discard multiple activities"""
    activity_service = ActivityService(db)
    
    results = []
    for activity_id in activity_ids:
        try:
            activity = await activity_service.get_by_id(activity_id)
            if not activity:
                results.append({
                    "activity_id": activity_id,
                    "status": "error",
                    "message": "Activity not found"
                })
                continue
            
            if activity.status != ActivityStatus.REJECTED:
                results.append({
                    "activity_id": activity_id,
                    "status": "error",
                    "message": "Can only discard rejected activities"
                })
                continue
            
            await activity_service.discard_activity(
                activity_id, 
                current_user.user_id, 
                comments
            )
            
            results.append({
                "activity_id": activity_id,
                "status": "success",
                "message": "Activity discarded"
            })
            
        except Exception as e:
            results.append({
                "activity_id": activity_id,
                "status": "error",
                "message": str(e)
            })
    
    return {"results": results}

@router.get("/all-activities")
async def get_all_activities(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    department: Optional[str] = None,
    type: Optional[str] = None,
    year: Optional[int] = None,
    search: Optional[str] = None,
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all activities with filters"""
    activity_service = ActivityService(db)
    
    # Build filters
    filters_dict = {}
    if status:
        filters_dict["status"] = status
    if department:
        filters_dict["department"] = department
    if type:
        filters_dict["type"] = type
    if year:
        filters_dict["year"] = year
    
    # Get activities
    cursor = activity_service.collection.find(filters_dict).skip(skip).limit(limit).sort("created_at", -1)
    activities = []
    
    async for activity_doc in cursor:
        activity_id = str(activity_doc["_id"])
        activity_doc["_id"] = activity_id
        activity_doc["id"] = activity_id  # Add id field for consistency
        
        # Get user info
        if "user_id" in activity_doc:
            try:
                user = await db.users.find_one({"_id": ObjectId(activity_doc["user_id"])})
                if user:
                    activity_doc["user_name"] = user.get("name", "Unknown")
                    activity_doc["user_email"] = user.get("email", "")
            except:
                pass
        
        # Apply search filter if provided (client-side filtering for title/user)
        if search:
            search_lower = search.lower()
            title_match = search_lower in activity_doc.get("title", "").lower()
            user_match = search_lower in activity_doc.get("user_name", "").lower() or search_lower in activity_doc.get("user_email", "").lower()
            if not (title_match or user_match):
                continue
        
        activities.append(activity_doc)
    
    # For total count, we need to apply search filter too
    total = await activity_service.collection.count_documents(filters_dict)
    if search:
        # Recalculate total with search filter
        all_activities = []
        cursor_all = activity_service.collection.find(filters_dict).sort("created_at", -1)
        async for activity_doc in cursor_all:
            activity_doc["_id"] = str(activity_doc["_id"])
            if "user_id" in activity_doc:
                try:
                    user = await db.users.find_one({"_id": ObjectId(activity_doc["user_id"])})
                    if user:
                        activity_doc["user_name"] = user.get("name", "Unknown")
                        activity_doc["user_email"] = user.get("email", "")
                except:
                    pass
            
            search_lower = search.lower()
            title_match = search_lower in activity_doc.get("title", "").lower()
            user_match = search_lower in activity_doc.get("user_name", "").lower() or search_lower in activity_doc.get("user_email", "").lower()
            if title_match or user_match:
                all_activities.append(activity_doc)
        total = len(all_activities)
    
    return {
        "activities": activities,
        "total": total,
        "page": (skip // limit) + 1,
        "size": limit
    }

@router.get("/analytics")
async def get_analytics(
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get comprehensive analytics for admin dashboard"""
    activity_service = ActivityService(db)
    user_service = UserService(db)
    
    # Get activity stats
    activity_stats = await activity_service.get_admin_stats()
    
    # Get user stats
    total_users = await user_service.get_user_count()
    department_stats = await user_service.get_department_stats()
    
    # Get activities by month
    monthly_pipeline = [
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"}
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}},
        {"$limit": 12}
    ]
    
    monthly_activities = []
    async for doc in activity_service.collection.aggregate(monthly_pipeline):
        monthly_activities.append({
            "year": doc["_id"]["year"],
            "month": doc["_id"]["month"],
            "count": doc["count"]
        })
    
    # Get activities by type
    type_pipeline = [
        {
            "$group": {
                "_id": "$type",
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}}
    ]
    
    type_stats = []
    async for doc in activity_service.collection.aggregate(type_pipeline):
        type_stats.append({
            "type": doc["_id"],
            "count": doc["count"]
        })
    
    # Get department activity distribution
    dept_activity_pipeline = [
        {
            "$group": {
                "_id": "$department",
                "total": {"$sum": 1},
                "accepted": {
                    "$sum": {"$cond": [{"$eq": ["$status", "accepted"]}, 1, 0]}
                },
                "pending": {
                    "$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}
                },
                "rejected": {
                    "$sum": {"$cond": [{"$eq": ["$status", "rejected"]}, 1, 0]}
                }
            }
        },
        {"$sort": {"total": -1}}
    ]
    
    dept_distribution = []
    async for doc in activity_service.collection.aggregate(dept_activity_pipeline):
        dept_distribution.append({
            "department": doc["_id"],
            "total": doc["total"],
            "accepted": doc["accepted"],
            "pending": doc["pending"],
            "rejected": doc["rejected"]
        })
    
    # Get user roles distribution
    users_by_role = {}
    role_pipeline = [
        {"$group": {"_id": "$role", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    async for doc in user_service.collection.aggregate(role_pipeline):
        users_by_role[doc["_id"]] = doc["count"]
    
    return {
        "activity_stats": activity_stats,
        "total_users": total_users,
        "users_by_role": users_by_role,
        "monthly_activities": monthly_activities,
        "type_distribution": type_stats,
        "department_distribution": dept_distribution,
        "department_user_stats": department_stats
    }

@router.get("/users/all")
async def get_all_users(
    skip: int = 0,
    limit: int = 50,
    role: Optional[str] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all users with filters"""
    user_service = UserService(db)
    
    # Build MongoDB filter
    filter_dict = {}
    if department:
        filter_dict["department"] = department
    if role:
        filter_dict["role"] = role
    
    # Add search filter using MongoDB regex
    # If we have both search and other filters, we need to combine them properly
    if search:
        search_regex = {"$regex": search, "$options": "i"}
        search_conditions = [
            {"name": search_regex},
            {"email": search_regex}
        ]
        # If we have other filters, combine with $and
        if filter_dict:
            filter_dict = {
                "$and": [
                    filter_dict,
                    {"$or": search_conditions}
                ]
            }
        else:
            filter_dict["$or"] = search_conditions
    
    # Debug logging
    print(f"[DEBUG] User filter: {filter_dict}")
    print(f"[DEBUG] Skip: {skip}, Limit: {limit}")
    
    # Get total count with filters
    total = await user_service.collection.count_documents(filter_dict)
    print(f"[DEBUG] Total users found: {total}")
    
    # Get paginated users
    cursor = user_service.collection.find(filter_dict).skip(skip).limit(limit)
    users = []
    async for user_doc in cursor:
        try:
            user_doc["_id"] = str(user_doc["_id"])
            user_doc.pop("password_hash", None)
            user_doc.pop("login_attempts", None)
            user_doc.pop("locked_until", None)
            # Convert to User model
            user = User(**user_doc)
            users.append(user)
        except Exception as e:
            # Log error but continue processing other users
            print(f"[ERROR] Error processing user {user_doc.get('_id', 'unknown')}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"[DEBUG] Processed {len(users)} users")
    
    # Get activity count for each user and convert to dict
    activity_service = ActivityService(db)
    result_users = []
    for user in users:
        activity_count = await activity_service.collection.count_documents({"user_id": user.id})
        # Convert User to dict
        user_dict = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "department": user.department,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "student_id": user.student_id,
            "phone": user.phone,
            "year_of_study": user.year_of_study,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "activity_count": activity_count
        }
        result_users.append(user_dict)
    
    return {
        "users": result_users,
        "total": total,
        "page": (skip // limit) + 1,
        "size": limit
    }

@router.post("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: str,
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Activate or deactivate a user"""
    user_service = UserService(db)
    
    # Get user
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Cannot deactivate self
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    # Toggle status
    new_status = not user.is_active
    await user_service.update_user(user_id, UserUpdate(is_active=new_status))
    
    return {"message": f"User {('activated' if new_status else 'deactivated')} successfully"}

@router.post("/activities/{activity_id}/reject")
async def reject_activity(
    activity_id: str,
    body: Optional[dict] = Body(default=None),
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Reject an activity"""
    activity_service = ActivityService(db)
    
    # Get comments from body
    comments = body.get("comments") if body and isinstance(body, dict) else None
    
    # Check if activity exists
    activity = await activity_service.get_by_id(activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    # Can reject pending activities
    if activity.status == ActivityStatus.REJECTED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activity is already rejected"
        )
    
    # Update status
    update_data = {
        "status": ActivityStatus.REJECTED.value,
        "admin_reviewed_at": datetime.utcnow(),
        "admin_reviewed_by": current_user.user_id,
        "admin_comments": comments,
        "updated_at": datetime.utcnow()
    }
    
    await activity_service.collection.update_one(
        {"_id": ObjectId(activity_id)},
        {"$set": update_data}
    )
    
    # Create notification
    from app.services.notification_service import NotificationService
    notification_service = NotificationService(db)
    await notification_service.create_notification(
        user_id=activity.user_id,
        title="Activity Rejected",
        message=f"Your activity '{activity.title}' has been rejected." + (f" Comments: {comments}" if comments else ""),
        type="activity_rejected"
    )
    
    return {"message": "Activity rejected successfully"}

@router.post("/activities/{activity_id}/verify-image")
async def verify_image(
    activity_id: str,
    body: dict = Body(...),
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Manually verify or update verification status of an image in an activity"""
    activity_service = ActivityService(db)
    
    image_index = body.get("image_index")
    verdict = body.get("verdict")  # "normal" or "abnormal"
    
    if image_index is None or verdict not in ["normal", "abnormal"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request. image_index and verdict (normal/abnormal) are required"
        )
    
    # Check if activity exists
    activity = await activity_service.get_by_id(activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    # Get activity document
    activity_doc = await activity_service.collection.find_one({"_id": ObjectId(activity_id)})
    if not activity_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    # Check if image index is valid
    images = activity_doc.get("images", [])
    if image_index < 0 or image_index >= len(images):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image index. Activity has {len(images)} images"
        )
    
    # Update the image verdict
    images[image_index]["verdict"] = verdict
    images[image_index]["admin_verified"] = True
    images[image_index]["admin_verified_at"] = datetime.utcnow()
    images[image_index]["admin_verified_by"] = current_user.user_id
    
    # Update activity
    await activity_service.collection.update_one(
        {"_id": ObjectId(activity_id)},
        {"$set": {"images": images, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": f"Image {image_index} verification updated to {verdict}"}

@router.post("/activities/create")
async def create_activity_by_admin(
    title: str = Body(...),
    description: str = Body(...),
    type: str = Body(...),
    department: str = Body(...),
    year: int = Body(...),
    date: Optional[str] = Body(None),
    organizer: Optional[str] = Body(None),
    venue: Optional[str] = Body(None),
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create an activity by admin (visible to all users)"""
    activity_service = ActivityService(db)
    
    # Create activity document
    activity_doc = {
        "_id": ObjectId(),
        "title": title,
        "description": description,
        "type": type,
        "department": department,
        "year": year,
        "status": ActivityStatus.ACCEPTED.value,  # Admin-created activities are auto-approved
        "user_id": current_user.user_id,  # Admin user ID
        "is_admin_created": True,  # Flag to identify admin-created activities
        "is_public": True,  # Make it visible to all users
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "achievement_type": "individual",
        "has_certificate": False,
        "certificate_validated": False,
        "images": [],  # Empty images array for admin-created activities
        "group_members": [],
        "admin_reviewed_at": datetime.utcnow(),
        "admin_reviewed_by": current_user.user_id,
        "admin_comments": None,
        "ml_checked_at": None,
        "certificate_path": None,
        "certificate_validation_result": None,
        "attendees": []  # Initialize empty attendees array for events
    }
    
    # Add optional fields
    if date:
        try:
            activity_doc["activity_date"] = datetime.fromisoformat(date.replace('Z', '+00:00'))
        except:
            pass
    if organizer:
        activity_doc["organizer"] = organizer
    if venue:
        activity_doc["venue"] = venue
    
    # Insert activity
    result = await activity_service.collection.insert_one(activity_doc)
    activity_id = str(result.inserted_id)
    
    # Get user info for response
    user = await db.users.find_one({"_id": ObjectId(current_user.user_id)})
    activity_doc["_id"] = activity_id
    activity_doc["id"] = activity_id  # Add id field
    activity_doc["user_name"] = user.get("name", "Admin") if user else "Admin"
    activity_doc["user_email"] = user.get("email", "") if user else ""
    
    return {
        "message": "Activity created successfully",
        "activity": activity_doc
    }

@router.get("/departments")
async def get_all_departments(
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all departments from users and activities"""
    departments_set = set()
    
    # Get departments from users
    users_pipeline = [
        {"$group": {"_id": "$department"}},
        {"$match": {"_id": {"$ne": None, "$ne": ""}}},
        {"$sort": {"_id": 1}}
    ]
    
    async for doc in db.users.aggregate(users_pipeline):
        if doc["_id"]:
            departments_set.add(doc["_id"])
    
    # Get departments from activities
    activities_pipeline = [
        {"$group": {"_id": "$department"}},
        {"$match": {"_id": {"$ne": None, "$ne": ""}}},
        {"$sort": {"_id": 1}}
    ]
    
    async for doc in db.activities.aggregate(activities_pipeline):
        if doc["_id"]:
            departments_set.add(doc["_id"])
    
    # If no departments found, provide default list
    if not departments_set:
        departments_set = {
            "Computer Science",
            "Mechanical Engineering",
            "Electronics & Communication",
            "Civil Engineering",
            "Electrical Engineering",
            "Information Technology"
        }
    
    departments = sorted(list(departments_set))
    return {"departments": departments}

# Notification Management Endpoints
@router.get("/notifications", response_model=dict)
async def get_all_notifications(
    skip: int = 0,
    limit: int = 50,
    type: Optional[str] = None,
    read: Optional[bool] = None,
    user_id: Optional[str] = None,
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all notifications with filters (admin only)"""
    from app.services.notification_service import NotificationService
    
    notification_service = NotificationService(db)
    notifications, total = await notification_service.get_all_notifications(
        skip=skip,
        limit=limit,
        type=type,
        read=read,
        user_id=user_id
    )
    
    return {
        "notifications": notifications,
        "total": total,
        "page": (skip // limit) + 1,
        "size": limit
    }

@router.get("/notifications/stats", response_model=dict)
async def get_notification_stats(
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get notification statistics (admin only)"""
    from app.services.notification_service import NotificationService
    
    notification_service = NotificationService(db)
    stats = await notification_service.get_notification_stats()
    
    return stats

@router.post("/notifications/create")
async def create_notification(
    title: str = Body(...),
    message: str = Body(...),
    type: str = Body("info"),
    user_id: Optional[str] = Body(None),
    target_all_users: bool = Body(False),
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a notification (admin only)"""
    from app.services.notification_service import NotificationService
    from app.services.user_service import UserService
    
    notification_service = NotificationService(db)
    
    # If target_all_users is True, create notifications for all users
    if target_all_users:
        user_service = UserService(db)
        # Get all active users (limit to 1000 to avoid timeout)
        all_users = await user_service.get_users(
            skip=0,
            limit=1000,
            active_only=True
        )
        
        created_count = 0
        for user in all_users:
            await notification_service.create_notification_by_admin(
                user_id=user.id,
                title=title,
                message=message,
                type=type,
                created_by=current_user.user_id
            )
            created_count += 1
        
        return {
            "message": f"Notification created and sent to {created_count} users",
            "notifications_created": created_count
        }
    else:
        # Create for specific user or broadcast
        notification = await notification_service.create_notification_by_admin(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            created_by=current_user.user_id
        )
        
        return {
            "message": "Notification created successfully",
            "notification": notification
        }

@router.put("/notifications/{notification_id}")
async def update_notification(
    notification_id: str,
    update_data: NotificationUpdate,
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update a notification (admin only)"""
    from app.services.notification_service import NotificationService
    
    notification_service = NotificationService(db)
    notification = await notification_service.update_notification(
        notification_id=notification_id,
        title=update_data.title,
        message=update_data.message,
        type=update_data.type  # Already a string from frontend
    )
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {
        "message": "Notification updated successfully",
        "notification": notification
    }

@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a notification (admin only)"""
    from app.services.notification_service import NotificationService
    
    notification_service = NotificationService(db)
    deleted = await notification_service.delete_notification_admin(notification_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification deleted successfully"}

@router.post("/notifications/bulk-read")
async def mark_notifications_read(
    notification_ids: List[str] = Body(...),
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Mark multiple notifications as read (admin only)"""
    from app.services.notification_service import NotificationService
    
    notification_service = NotificationService(db)
    count = await notification_service.mark_notifications_read_admin(notification_ids)
    
    return {
        "message": f"{count} notification(s) marked as read",
        "count": count
    }

@router.post("/notifications/bulk-delete")
async def bulk_delete_notifications(
    notification_ids: List[str] = Body(...),
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete multiple notifications (admin only)"""
    from app.services.notification_service import NotificationService
    from bson import ObjectId
    
    notification_service = NotificationService(db)
    deleted_count = 0
    
    for notification_id in notification_ids:
        if await notification_service.delete_notification_admin(notification_id):
            deleted_count += 1
    
    return {
        "message": f"{deleted_count} notification(s) deleted successfully",
        "count": deleted_count
    }