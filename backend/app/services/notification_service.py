"""
Notification service for user notifications
"""

from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.notification import Notification, NotificationCreate

class NotificationService:
    """Notification service for database operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.notifications
    
    async def create_notification(
        self, 
        user_id: str, 
        title: str, 
        message: str, 
        type: str = "info"
    ) -> Notification:
        """Create a new notification"""
        notification_doc = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": type,
            "read": False,
            "created_at": datetime.utcnow()
        }
        
        result = await self.collection.insert_one(notification_doc)
        notification_doc["_id"] = str(result.inserted_id)
        
        return Notification(**notification_doc)
    
    async def get_user_notifications(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for a user"""
        cursor = self.collection.find(
            {"user_id": user_id}
        ).skip(skip).limit(limit).sort("created_at", -1)
        
        notifications = []
        async for notification_doc in cursor:
            notification_doc["_id"] = str(notification_doc["_id"])
            notifications.append(Notification(**notification_doc))
        
        return notifications
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read"""
        result = await self.collection.update_one(
            {
                "_id": ObjectId(notification_id),
                "user_id": user_id
            },
            {"$set": {"read": True}}
        )
        
        return result.matched_count > 0
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        result = await self.collection.update_many(
            {"user_id": user_id, "read": False},
            {"$set": {"read": True}}
        )
        
        return result.modified_count
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications"""
        return await self.collection.count_documents({
            "user_id": user_id,
            "read": False
        })
    
    async def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        result = await self.collection.delete_one({
            "_id": ObjectId(notification_id),
            "user_id": user_id
        })
        
        return result.deleted_count > 0
    
    async def delete_old_notifications(self, days: int = 30) -> int:
        """Delete notifications older than specified days"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.collection.delete_many({
            "created_at": {"$lt": cutoff_date}
        })
        
        return result.deleted_count
    
    # Admin operations
    async def create_notification_by_admin(
        self,
        user_id: Optional[str],
        title: str,
        message: str,
        type: str = "info",
        created_by: Optional[str] = None
    ) -> Notification:
        """Create a notification by admin (can target specific user or all users)"""
        notification_doc = {
            "title": title,
            "message": message,
            "type": type,
            "read": False,
            "created_at": datetime.utcnow(),
            "created_by_admin": True,
            "created_by": created_by
        }
        
        # If user_id is None, it's a broadcast notification
        if user_id:
            notification_doc["user_id"] = user_id
        else:
            # For broadcast, we'll create individual notifications for all users
            # For now, store as broadcast and let endpoint handle distribution
            notification_doc["user_id"] = None  # Broadcast notification
        
        result = await self.collection.insert_one(notification_doc)
        notification_doc["_id"] = str(result.inserted_id)
        
        return Notification(**notification_doc)
    
    async def get_all_notifications(
        self,
        skip: int = 0,
        limit: int = 50,
        type: Optional[str] = None,
        read: Optional[bool] = None,
        user_id: Optional[str] = None
    ) -> tuple[List[Notification], int]:
        """Get all notifications with filters (admin only)"""
        query = {}
        
        if type:
            query["type"] = type
        if read is not None:
            query["read"] = read
        if user_id:
            query["user_id"] = user_id
        
        # Get total count
        total = await self.collection.count_documents(query)
        
        # Get notifications
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        
        notifications = []
        async for notification_doc in cursor:
            try:
                # Ensure all required fields are present
                notification_doc["_id"] = str(notification_doc["_id"])
                
                # Set defaults for optional fields if missing
                if "created_by_admin" not in notification_doc:
                    notification_doc["created_by_admin"] = False
                if "created_by" not in notification_doc:
                    notification_doc["created_by"] = None
                
                # Ensure user_id is present (can be None for broadcast)
                if "user_id" not in notification_doc:
                    notification_doc["user_id"] = None
                
                # Parse to Notification model
                notification = Notification(**notification_doc)
                notifications.append(notification)
            except Exception as e:
                # Log error but continue processing other notifications
                print(f"Error parsing notification: {e}, doc: {notification_doc}")
                continue
        
        return notifications, total
    
    async def update_notification(
        self,
        notification_id: str,
        title: Optional[str] = None,
        message: Optional[str] = None,
        type: Optional[str] = None
    ) -> Optional[Notification]:
        """Update a notification (admin only)"""
        update_data = {}
        
        if title:
            update_data["title"] = title
        if message:
            update_data["message"] = message
        if type:
            update_data["type"] = type
        
        if not update_data:
            return None
        
        result = await self.collection.update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        # Fetch updated notification
        notification_doc = await self.collection.find_one({"_id": ObjectId(notification_id)})
        if notification_doc:
            notification_doc["_id"] = str(notification_doc["_id"])
            return Notification(**notification_doc)
        
        return None
    
    async def delete_notification_admin(self, notification_id: str) -> bool:
        """Delete a notification (admin only)"""
        result = await self.collection.delete_one({
            "_id": ObjectId(notification_id)
        })
        
        return result.deleted_count > 0
    
    async def mark_notifications_read_admin(
        self,
        notification_ids: List[str]
    ) -> int:
        """Mark multiple notifications as read (admin only)"""
        object_ids = [ObjectId(nid) for nid in notification_ids]
        
        result = await self.collection.update_many(
            {"_id": {"$in": object_ids}},
            {"$set": {"read": True}}
        )
        
        return result.modified_count
    
    async def get_notification_stats(self) -> dict:
        """Get notification statistics (admin only)"""
        total = await self.collection.count_documents({})
        unread = await self.collection.count_documents({"read": False})
        read = await self.collection.count_documents({"read": True})
        
        # Count by type
        type_counts = {}
        pipeline = [
            {"$group": {"_id": "$type", "count": {"$sum": 1}}}
        ]
        async for result in self.collection.aggregate(pipeline):
            type_counts[result["_id"]] = result["count"]
        
        return {
            "total": total,
            "unread": unread,
            "read": read,
            "by_type": type_counts
        }