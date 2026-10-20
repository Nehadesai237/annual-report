"""
Report service for generating reports
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.report import Report, ReportCreate, ReportStats
import os
# import weasyprint  # Disabled for Windows compatibility
from jinja2 import Environment, FileSystemLoader
import json

class ReportService:
    """Report service for generating reports"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.reports
        self.activities_collection = db.activities
        self.users_collection = db.users
        
        # Setup Jinja2 environment
        # Get the directory where this file is located
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'templates')
        
        # Ensure templates directory exists
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir, exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True
        )
    
    async def get_activity_for_report(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """Get activity data for report generation"""
        activity_doc = await self.activities_collection.find_one({
            "_id": ObjectId(activity_id)
        })
        
        if not activity_doc:
            return None
        
        # Get user info (creator)
        user_doc = await self.users_collection.find_one({
            "_id": ObjectId(activity_doc["user_id"])
        })
        
        activity_doc["_id"] = str(activity_doc["_id"])
        activity_doc["user"] = user_doc
        
        # Get group members info if this is a group activity
        group_members_list = []
        if activity_doc.get("achievement_type") == "group" and activity_doc.get("group_members"):
            group_member_ids = activity_doc["group_members"]
            if isinstance(group_member_ids, list) and len(group_member_ids) > 0:
                # Fetch all group members
                for member_id in group_member_ids:
                    try:
                        member_doc = await self.users_collection.find_one({
                            "_id": ObjectId(member_id)
                        })
                        if member_doc:
                            # Remove sensitive fields
                            member_doc.pop("password_hash", None)
                            member_doc.pop("login_attempts", None)
                            member_doc.pop("locked_until", None)
                            member_doc["_id"] = str(member_doc["_id"])
                            group_members_list.append(member_doc)
                    except Exception as e:
                        print(f"Error fetching group member {member_id}: {e}")
                        continue
        
        activity_doc["group_members_details"] = group_members_list
        
        return activity_doc
    
    async def generate_individual_html(self, activity: Dict[str, Any]) -> str:
        """Generate HTML for individual activity report"""
        template = self.jinja_env.get_template('individual_report.html')
        
        # Get API base URL from environment or use default
        api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
        
        html_content = template.render(
            activity=activity,
            generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            api_base_url=api_base_url
        )
        
        return html_content
    
    async def generate_individual_pdf(self, activity: Dict[str, Any]) -> str:
        """Generate PDF for individual activity report"""
        # Generate HTML
        html_content = await self.generate_individual_html(activity)
        
        # Create reports directory
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # For now, save as HTML file (PDF generation requires weasyprint or reportlab)
        # The endpoint will handle the content type
        pdf_path = os.path.join(reports_dir, f"activity_{activity['_id']}_report.html")
        
        with open(pdf_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return pdf_path
    
    async def generate_group_html(
        self, 
        department: Optional[str] = None,
        year: Optional[int] = None,
        type: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """Generate HTML for group report"""
        # Build base filter
        base_filter: Dict[str, Any] = {}
        if department:
            base_filter["department"] = department
        if year:
            base_filter["year"] = year
        if type:
            base_filter["type"] = type
        
        filter_dict: Dict[str, Any] = base_filter.copy()
        
        # Restrict to specific user (either owner or group member)
        # For students, only show accepted activities
        if user_id:
            user_filters: List[Dict[str, Any]] = []
            
            own_filter = base_filter.copy()
            own_filter["user_id"] = user_id
            own_filter["status"] = "accepted"  # Only accepted activities for students
            own_filter["is_admin_created"] = {"$ne": True}  # Exclude admin-created activities
            user_filters.append(own_filter)
            
            group_filter = base_filter.copy()
            group_filter["achievement_type"] = "group"
            group_filter["group_members"] = user_id
            group_filter["status"] = "accepted"  # Only accepted activities for students
            group_filter["is_admin_created"] = {"$ne": True}  # Exclude admin-created activities
            user_filters.append(group_filter)
            
            filter_dict = {"$or": user_filters}
        
        # Get activities
        activities = []
        cursor = self.activities_collection.find(filter_dict).sort("created_at", -1)
        
        async for activity_doc in cursor:
            activity_doc["_id"] = str(activity_doc["_id"])
            
            # Get user info (creator)
            user_doc = await self.users_collection.find_one({
                "_id": ObjectId(activity_doc["user_id"])
            })
            activity_doc["user"] = user_doc
            
            # Get group members info if this is a group activity
            group_members_list = []
            if activity_doc.get("achievement_type") == "group" and activity_doc.get("group_members"):
                group_member_ids = activity_doc["group_members"]
                if isinstance(group_member_ids, list) and len(group_member_ids) > 0:
                    # Fetch all group members
                    for member_id in group_member_ids:
                        try:
                            member_doc = await self.users_collection.find_one({
                                "_id": ObjectId(member_id)
                            })
                            if member_doc:
                                # Remove sensitive fields
                                member_doc.pop("password_hash", None)
                                member_doc.pop("login_attempts", None)
                                member_doc.pop("locked_until", None)
                                member_doc["_id"] = str(member_doc["_id"])
                                group_members_list.append(member_doc)
                        except Exception as e:
                            print(f"Error fetching group member {member_id}: {e}")
                            continue
            
            activity_doc["group_members_details"] = group_members_list
            
            activities.append(activity_doc)
        
        # Get statistics
        stats = await self.get_group_stats(filter_dict)
        
        template = self.jinja_env.get_template('group_report.html')
        
        # Get API base URL from environment or use default
        api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
        
        html_content = template.render(
            activities=activities,
            stats=stats,
            department=department,
            year=year,
            type=type,
            generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            api_base_url=api_base_url
        )
        
        return html_content
    
    async def generate_group_pdf(
        self, 
        department: Optional[str] = None,
        year: Optional[int] = None,
        type: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """Generate PDF for group report"""
        # Generate HTML
        html_content = await self.generate_group_html(department, year, type, user_id)
        
        # Create reports directory
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # For now, save as HTML file (PDF generation requires weasyprint or reportlab)
        # The endpoint will handle the content type
        filename = f"group_report_{department or 'all'}_{year or 'all'}.html"
        pdf_path = os.path.join(reports_dir, filename)
        
        with open(pdf_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return pdf_path
    
    async def get_group_stats(self, filter_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics for group report"""
        # Get total count
        total_activities = await self.activities_collection.count_documents(filter_dict)
        
        # Get status counts
        status_pipeline = [
            {"$match": filter_dict},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        status_counts = {}
        async for doc in self.activities_collection.aggregate(status_pipeline):
            status_counts[doc["_id"]] = doc["count"]
        
        # Get department stats
        dept_pipeline = [
            {"$match": filter_dict},
            {
                "$group": {
                    "_id": "$department",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        department_stats = []
        async for doc in self.activities_collection.aggregate(dept_pipeline):
            department_stats.append({
                "department": doc["_id"],
                "count": doc["count"]
            })
        
        # Get type stats
        type_pipeline = [
            {"$match": filter_dict},
            {
                "$group": {
                    "_id": "$type",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        type_stats = []
        async for doc in self.activities_collection.aggregate(type_pipeline):
            type_stats.append({
                "type": doc["_id"],
                "count": doc["count"]
            })
        
        return {
            "total_activities": total_activities,
            "accepted_activities": status_counts.get("accepted", 0),
            "rejected_activities": status_counts.get("rejected", 0),
            "pending_activities": status_counts.get("pending", 0),
            "department_stats": department_stats,
            "type_stats": type_stats
        }
    
    async def get_all_stats(self) -> ReportStats:
        """Get statistics for all activities"""
        # Get total counts
        total_activities = await self.activities_collection.count_documents({})
        total_users = await self.users_collection.count_documents({})
        
        # Get status counts
        status_pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        status_counts = {}
        async for doc in self.activities_collection.aggregate(status_pipeline):
            status_counts[doc["_id"]] = doc["count"]
        
        # Get department stats
        dept_pipeline = [
            {
                "$group": {
                    "_id": "$department",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        departments = []
        async for doc in self.activities_collection.aggregate(dept_pipeline):
            departments.append({
                "department": doc["_id"],
                "count": doc["count"]
            })
        
        # Get type stats
        type_pipeline = [
            {
                "$group": {
                    "_id": "$type",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        activity_types = []
        async for doc in self.activities_collection.aggregate(type_pipeline):
            activity_types.append({
                "type": doc["_id"],
                "count": doc["count"]
            })
        
        # Get monthly stats
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
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        
        monthly_stats = []
        async for doc in self.activities_collection.aggregate(monthly_pipeline):
            monthly_stats.append({
                "year": doc["_id"]["year"],
                "month": doc["_id"]["month"],
                "count": doc["count"]
            })
        
        return ReportStats(
            total_activities=total_activities,
            accepted_activities=status_counts.get("accepted", 0),
            rejected_activities=status_counts.get("rejected", 0),
            pending_activities=status_counts.get("pending", 0),
            total_users=total_users,
            departments=departments,
            activity_types=activity_types,
            monthly_stats=monthly_stats
        )
    
    async def get_user_stats(self, user_id: str) -> ReportStats:
        """Get statistics for a specific user's activities (including group activities where user is a member)"""
        # Build filter for user's own activities OR group activities where user is a member
        # Exclude admin-created activities
        user_activities_filter = {
            "user_id": user_id,
            "is_admin_created": {"$ne": True}
        }
        
        group_activities_filter = {
            "achievement_type": "group",
            "group_members": user_id,
            "is_admin_created": {"$ne": True}
        }
        
        filter_dict = {"$or": [user_activities_filter, group_activities_filter]}
        
        # Get total counts
        total_activities = await self.activities_collection.count_documents(filter_dict)
        
        # Get status counts
        status_pipeline = [
            {"$match": filter_dict},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        status_counts = {}
        async for doc in self.activities_collection.aggregate(status_pipeline):
            status_counts[doc["_id"]] = doc["count"]
        
        # Get type stats
        type_pipeline = [
            {"$match": filter_dict},
            {
                "$group": {
                    "_id": "$type",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        activity_types = []
        async for doc in self.activities_collection.aggregate(type_pipeline):
            activity_types.append({
                "type": doc["_id"],
                "count": doc["count"]
            })
        
        # Get department stats (departments of user's activities)
        dept_pipeline = [
            {"$match": filter_dict},
            {
                "$group": {
                    "_id": "$department",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        departments = []
        async for doc in self.activities_collection.aggregate(dept_pipeline):
            if doc["_id"]:
                departments.append({
                    "department": doc["_id"],
                    "count": doc["count"]
                })
        
        # Get monthly stats
        monthly_pipeline = [
            {"$match": filter_dict},
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        
        monthly_stats = []
        async for doc in self.activities_collection.aggregate(monthly_pipeline):
            monthly_stats.append({
                "year": doc["_id"]["year"],
                "month": doc["_id"]["month"],
                "count": doc["count"]
            })
        
        return ReportStats(
            total_activities=total_activities,
            accepted_activities=status_counts.get("accepted", 0),
            rejected_activities=status_counts.get("rejected", 0),
            pending_activities=status_counts.get("pending", 0),
            total_users=1,  # Single user
            departments=departments,
            activity_types=activity_types,
            monthly_stats=monthly_stats
        )
    
    async def get_department_stats(self, department: str) -> ReportStats:
        """Get statistics for a specific department"""
        filter_dict = {"department": department}
        
        # Get total counts
        total_activities = await self.activities_collection.count_documents(filter_dict)
        total_users = await self.users_collection.count_documents({"department": department})
        
        # Get status counts
        status_pipeline = [
            {"$match": filter_dict},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        status_counts = {}
        async for doc in self.activities_collection.aggregate(status_pipeline):
            status_counts[doc["_id"]] = doc["count"]
        
        # Get type stats
        type_pipeline = [
            {"$match": filter_dict},
            {
                "$group": {
                    "_id": "$type",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        activity_types = []
        async for doc in self.activities_collection.aggregate(type_pipeline):
            activity_types.append({
                "type": doc["_id"],
                "count": doc["count"]
            })
        
        # Get monthly stats
        monthly_pipeline = [
            {"$match": filter_dict},
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        
        monthly_stats = []
        async for doc in self.activities_collection.aggregate(monthly_pipeline):
            monthly_stats.append({
                "year": doc["_id"]["year"],
                "month": doc["_id"]["month"],
                "count": doc["count"]
            })
        
        return ReportStats(
            total_activities=total_activities,
            accepted_activities=status_counts.get("accepted", 0),
            rejected_activities=status_counts.get("rejected", 0),
            pending_activities=status_counts.get("pending", 0),
            total_users=total_users,
            departments=[{"department": department, "count": total_activities}],
            activity_types=activity_types,
            monthly_stats=monthly_stats
        )
    
    async def get_all_departments(self) -> List[Dict[str, Any]]:
        """Get all unique departments from activities for dropdown"""
        departments_set = set()
        
        # Get departments from activities
        dept_pipeline = [
            {
                "$group": {
                    "_id": "$department"
                }
            },
            {
                "$match": {
                    "_id": {"$ne": None, "$ne": ""}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        async for doc in self.activities_collection.aggregate(dept_pipeline):
            if doc["_id"]:
                departments_set.add(doc["_id"])
        
        # Also get departments from users
        users_pipeline = [
            {
                "$group": {
                    "_id": "$department"
                }
            },
            {
                "$match": {
                    "_id": {"$ne": None, "$ne": ""}
                }
            }
        ]
        
        async for doc in self.users_collection.aggregate(users_pipeline):
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
        
        # Convert to list of dicts in the format expected by frontend
        departments = [
            {"department": dept, "count": 0} 
            for dept in sorted(departments_set)
        ]
        
        return departments
    
    async def create_report(self, report_data: ReportCreate, user_id: str) -> Report:
        """Create a new report"""
        report_doc = {
            "type": report_data.type.value,
            "title": report_data.title,
            "description": report_data.description,
            "generated_by": user_id,
            "params": report_data.params,
            "status": "generating",
            "generated_at": datetime.utcnow()
        }
        
        result = await self.collection.insert_one(report_doc)
        report_doc["_id"] = str(result.inserted_id)
        
        return Report(**report_doc)
    
    async def get_reports(self, skip: int = 0, limit: int = 100) -> List[Report]:
        """Get all reports"""
        cursor = self.collection.find().skip(skip).limit(limit).sort("generated_at", -1)
        reports = []
        
        async for report_doc in cursor:
            report_doc["_id"] = str(report_doc["_id"])
            reports.append(Report(**report_doc))
        
        return reports
    
    async def get_user_reports(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Report]:
        """Get reports for a specific user"""
        cursor = self.collection.find(
            {"generated_by": user_id}
        ).skip(skip).limit(limit).sort("generated_at", -1)
        
        reports = []
        async for report_doc in cursor:
            report_doc["_id"] = str(report_doc["_id"])
            reports.append(Report(**report_doc))
        
        return reports
