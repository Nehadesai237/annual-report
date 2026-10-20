"""
Event enrollment endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional
from app.services.database import get_database
from app.core.security import get_current_active_user, TokenData
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

class EventEnrollment(BaseModel):
    event_id: str
    user_id: str
    enrolled_at: datetime

@router.post("/events/{event_id}/enroll")
async def enroll_in_event(
    event_id: str,
    body: dict = Body(...),
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Enroll current user in an event with additional details"""
    activities_collection = db.activities
    
    # Check if event exists and is admin-created
    event = await activities_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if not event.get("is_admin_created"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This is not an event"
        )
    
    # Validate required fields
    phone = body.get("phone", "").strip()
    reason = body.get("reason", "").strip()
    
    if not phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is required"
        )
    
    if not reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reason for participation is required"
        )
    
    if len(reason) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reason must be at least 20 characters long"
        )
    
    # Initialize attendees array if it doesn't exist
    if "attendees" not in event:
        event["attendees"] = []
    
    # Check if user is already enrolled
    existing_enrollment = None
    for attendee in event["attendees"]:
        if isinstance(attendee, dict) and attendee.get("user_id") == current_user.user_id:
            existing_enrollment = attendee
            break
        elif attendee == current_user.user_id:  # Legacy format
            existing_enrollment = {"user_id": attendee}
            break
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already enrolled in this event"
        )
    
    # Get user details
    from app.services.user_service import UserService
    user_service = UserService(db)
    user = await user_service.get_by_id(current_user.user_id)
    
    # Create enrollment object with details
    enrollment = {
        "user_id": current_user.user_id,
        "name": user.name if user else current_user.email,
        "email": user.email if user else current_user.email,
        "phone": phone,
        "department": user.department if user else "",
        "student_id": user.student_id if user else "",
        "reason": reason,
        "enrolled_at": datetime.utcnow()
    }
    
    # Add enrollment to attendees
    await activities_collection.update_one(
        {"_id": ObjectId(event_id)},
        {
            "$push": {"attendees": enrollment},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return {"message": "Successfully enrolled in event", "event_id": event_id}

@router.post("/events/{event_id}/unenroll")
async def unenroll_from_event(
    event_id: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Unenroll current user from an event"""
    activities_collection = db.activities
    
    # Check if event exists
    event = await activities_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if user is enrolled
    attendees = event.get("attendees", [])
    user_enrolled = False
    
    # Check both new format (dict) and legacy format (string)
    for attendee in attendees:
        if isinstance(attendee, dict) and attendee.get("user_id") == current_user.user_id:
            user_enrolled = True
            break
        elif attendee == current_user.user_id:
            user_enrolled = True
            break
    
    if not user_enrolled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not enrolled in this event"
        )
    
    # Remove user from attendees (handle both formats)
    # First, get the current attendees array
    event = await activities_collection.find_one({"_id": ObjectId(event_id)})
    attendees = event.get("attendees", [])
    
    # Filter out the user's enrollment (handle both dict and string formats)
    updated_attendees = [
        att for att in attendees 
        if (isinstance(att, dict) and att.get("user_id") != current_user.user_id) 
        or (not isinstance(att, dict) and att != current_user.user_id)
    ]
    
    # Update the event with filtered attendees
    await activities_collection.update_one(
        {"_id": ObjectId(event_id)},
        {
            "$set": {
                "attendees": updated_attendees,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Successfully unenrolled from event", "event_id": event_id}

@router.get("/events/public")
async def get_public_events(
    page: int = 1,
    size: int = 20,
    type: Optional[str] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all public events (admin-created activities) - no authentication required"""
    activities_collection = db.activities
    
    # Build filter dictionary
    filter_dict = {
        "is_admin_created": True,
        "status": "accepted"
    }
    
    # Apply type filter
    if type and type.strip():
        filter_dict["type"] = type.strip().lower()
    
    # Apply department filter
    if department and department.strip():
        filter_dict["department"] = department.strip()
    
    # Apply search filter (search in title and description)
    if search and search.strip():
        search_query = search.strip()
        search_condition = {
            "$or": [
                {"title": {"$regex": search_query, "$options": "i"}},
                {"description": {"$regex": search_query, "$options": "i"}}
            ]
        }
        # Use $and to combine base filters with search
        filter_dict = {
            "$and": [
                filter_dict,
                search_condition
            ]
        }
    
    # Calculate pagination
    skip = (page - 1) * size
    total = await activities_collection.count_documents(filter_dict)
    
    # Get events sorted by date (upcoming first)
    cursor = activities_collection.find(filter_dict).skip(skip).limit(size).sort("activity_date", 1)
    
    events = []
    
    async for event_doc in cursor:
        attendees = event_doc.get("attendees", [])
        
        event = {
            "id": str(event_doc["_id"]),
            "title": event_doc.get("title"),
            "description": event_doc.get("description"),
            "type": event_doc.get("type"),
            "department": event_doc.get("department"),
            "year": event_doc.get("year"),
            "activity_date": event_doc.get("activity_date"),
            "date": event_doc.get("date"),
            "venue": event_doc.get("venue"),
            "organizer": event_doc.get("organizer"),
            "created_at": event_doc.get("created_at"),
            "attendees_count": len(attendees)
        }
        events.append(event)
    
    return {
        "events": events,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.get("/events/upcoming")
async def get_upcoming_events(
    page: int = 1,
    size: int = 20,
    type: Optional[str] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all upcoming events (admin-created activities) with optional filters"""
    activities_collection = db.activities
    
    # Get current date
    now = datetime.utcnow()
    
    # Build filter dictionary
    filter_dict = {
        "is_admin_created": True,
        "status": "accepted"
    }
    
    # Apply type filter
    if type and type.strip():
        filter_dict["type"] = type.strip().lower()
    
    # Apply department filter
    if department and department.strip():
        filter_dict["department"] = department.strip()
    
    # Apply search filter (search in title and description)
    if search and search.strip():
        search_query = search.strip()
        search_condition = {
            "$or": [
                {"title": {"$regex": search_query, "$options": "i"}},
                {"description": {"$regex": search_query, "$options": "i"}}
            ]
        }
        # Use $and to combine base filters with search
        filter_dict = {
            "$and": [
                filter_dict,
                search_condition
            ]
        }
    
    # Calculate pagination
    skip = (page - 1) * size
    total = await activities_collection.count_documents(filter_dict)
    
    # Get events sorted by date (upcoming first)
    cursor = activities_collection.find(filter_dict).skip(skip).limit(size).sort("activity_date", 1)
    
    events = []
    from app.services.user_service import UserService
    user_service = UserService(db)
    
    async for event_doc in cursor:
        # Get attendee details
        attendees = event_doc.get("attendees", [])
        attendee_details = []
        is_enrolled = False
        
        for attendee in attendees:
            if isinstance(attendee, dict):
                # New format with enrollment details
                attendee_details.append({
                    "id": attendee.get("user_id"),
                    "name": attendee.get("name"),
                    "email": attendee.get("email"),
                    "department": attendee.get("department"),
                    "phone": attendee.get("phone"),
                    "student_id": attendee.get("student_id"),
                    "reason": attendee.get("reason"),
                    "enrolled_at": attendee.get("enrolled_at")
                })
                if attendee.get("user_id") == current_user.user_id:
                    is_enrolled = True
            else:
                # Legacy format - just user_id string
                try:
                    user = await user_service.get_by_id(attendee)
                    if user:
                        attendee_details.append({
                            "id": attendee,
                            "name": user.name,
                            "email": user.email,
                            "department": user.department
                        })
                    if attendee == current_user.user_id:
                        is_enrolled = True
                except:
                    pass
        
        event = {
            "id": str(event_doc["_id"]),
            "title": event_doc.get("title"),
            "description": event_doc.get("description"),
            "type": event_doc.get("type"),
            "department": event_doc.get("department"),
            "year": event_doc.get("year"),
            "activity_date": event_doc.get("activity_date"),
            "date": event_doc.get("date"),
            "venue": event_doc.get("venue"),
            "organizer": event_doc.get("organizer"),
            "created_at": event_doc.get("created_at"),
            "attendees_count": len(attendees),
            "attendees": attendee_details,
            "is_enrolled": is_enrolled
        }
        events.append(event)
    
    return {
        "events": events,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.get("/events/{event_id}/attendees")
async def get_event_attendees(
    event_id: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get attendees for an event (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view event attendees"
        )
    
    activities_collection = db.activities
    
    # Check if event exists
    event = await activities_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    attendees = event.get("attendees", [])
    from app.services.user_service import UserService
    user_service = UserService(db)
    
    attendee_details = []
    for attendee in attendees:
        if isinstance(attendee, dict):
            # New format with enrollment details
            attendee_details.append({
                "id": attendee.get("user_id"),
                "name": attendee.get("name"),
                "email": attendee.get("email"),
                "department": attendee.get("department"),
                "phone": attendee.get("phone", ""),
                "student_id": attendee.get("student_id", ""),
                "reason": attendee.get("reason", ""),
                "enrolled_at": attendee.get("enrolled_at")
            })
        else:
            # Legacy format - just user_id string
            try:
                user = await user_service.get_by_id(attendee)
                if user:
                    attendee_details.append({
                        "id": attendee,
                        "name": user.name,
                        "email": user.email,
                        "department": user.department,
                        "student_id": user.student_id,
                        "phone": user.phone
                    })
            except:
                pass
    
    return {
        "event_id": event_id,
        "event_title": event.get("title"),
        "attendees": attendee_details,
        "total": len(attendee_details)
    }

