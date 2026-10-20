"""Debug endpoints for testing"""
from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/database-info")
async def database_info(request: Request):
    """Get database connection info"""
    try:
        db = request.app.state.database
        client = request.app.state.db
        db_name = db.name
        
        count = await db.users.count_documents({})
        
        return {
            "database_name": db_name,
            "client": str(client),
            "users_count": count,
            "connection_string": str(request.app.state.db)
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/list-users")
async def list_users(request: Request):
    """List all users"""
    try:
        db = request.app.state.database
        users = []
        async for user_doc in db.users.find():
            users.append({
                "email": user_doc.get("email"),
                "name": user_doc.get("name"),
                "role": user_doc.get("role"),
                "is_active": user_doc.get("is_active")
            })
        return {"users": users, "count": len(users)}
    except Exception as e:
        return {"error": str(e)}
