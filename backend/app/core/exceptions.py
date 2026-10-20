"""
Custom exception handlers
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

class CustomHTTPException(HTTPException):
    """Custom HTTP exception with additional details"""
    
    def __init__(self, status_code: int, detail: str, error_code: str = None, headers: dict = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code

class ValidationError(CustomHTTPException):
    """Validation error exception"""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=422,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )

class AuthenticationError(CustomHTTPException):
    """Authentication error exception"""
    
    def __init__(self, detail: str = "Authentication failed", headers: dict = None):
        default_headers = {"WWW-Authenticate": "Bearer"}
        if headers:
            default_headers.update(headers)
        super().__init__(
            status_code=401,
            detail=detail,
            error_code="AUTHENTICATION_ERROR",
            headers=default_headers
        )

class AuthorizationError(CustomHTTPException):
    """Authorization error exception"""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=403,
            detail=detail,
            error_code="AUTHORIZATION_ERROR"
        )

class NotFoundError(CustomHTTPException):
    """Not found error exception"""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=404,
            detail=detail,
            error_code="NOT_FOUND"
        )

class ConflictError(CustomHTTPException):
    """Conflict error exception"""
    
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(
            status_code=409,
            detail=detail,
            error_code="CONFLICT"
        )

async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
    """Handle custom HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle standard HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers if hasattr(exc, 'headers') else None,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation exceptions"""
    # Extract error details in a serializable format
    error_details = []
    for error in exc.errors():
        error_details.append({
            "loc": list(error.get("loc", [])),
            "msg": str(error.get("msg", "")),
            "type": str(error.get("type", ""))
        })
    
    # Get the main error message
    main_message = "Validation failed"
    if error_details:
        main_message = error_details[0].get("msg", "Validation failed")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": main_message,
                "details": error_details,
                "status_code": 422
            }
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    # Log the full exception with traceback
    import traceback
    error_trace = traceback.format_exc()
    logger.error(f"Unhandled exception: {exc}")
    logger.error(f"Traceback: {error_trace}")
    
    # Get error message
    error_message = str(exc) if exc else "Internal server error"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": error_message,
                "status_code": 500
            }
        }
    )

def setup_exception_handlers(app: FastAPI):
    """Setup all exception handlers"""
    app.add_exception_handler(CustomHTTPException, custom_http_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
