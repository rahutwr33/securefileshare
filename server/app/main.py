import logging
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import os
import ssl
from .routes import auth, admin, user
from .database import engine, Base, get_db
from .config import settings
from .utils.init_admin import init_admin
from fastapi.security import OAuth2PasswordBearer
from .dependencies.auth import check_role
from .models.user import UserRole

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

description = """
🔐 Secure File Storage API 🗄️

This API provides secure file storage capabilities with the following features:

## Authentication
* User registration and login with 2FA
* Admin authentication
* JWT token-based security

## File Management
* Secure file upload with encryption
* File download with decryption
* File sharing capabilities
* Guest access links

## User Management
* Role-based access control (Admin/User)
* User profile management
* Admin user management

## Security Features
* Two-factor authentication
* File encryption at rest
* Secure file sharing
* Role-based permissions
"""

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"] = {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    }
    
    openapi_schema["security"] = [
        {
            "bearerAuth": []
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title="Secure File Storage API",
    description=description,
    version="1.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "API Support",
        "url": "http://example.com/contact/",
        "email": "support@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Operations for user authentication and registration",
        },
        {
            "name": "Admin",
            "description": "Administrative operations for user management",
        },
        {
            "name": "Files",
            "description": "File management operations",
        },
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Override the default openapi schema
app.openapi = custom_openapi

# Create upload directory if it doesn't exist
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)  # Only creates tables that don't exist

# Create dependencies here
get_admin_user = check_role([UserRole.ADMIN])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc)
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")
    try:
        # Initialize admin user only if it doesn't exist
        db_session = next(get_db())  # Create a new session
        try:
            init_admin(db_session)
            logger.info("Admin initialization completed")
        finally:
            db_session.close()  # Make sure to close the session
    except Exception as e:
        logger.error(f"Admin initialization failed: {str(e)}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")
    # Add any cleanup code here

@app.get("/")
async def root():
    return JSONResponse(
        content={
            "message": "Welcome to Secure File Storage API",
            "status": "running"
        }
    )

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api/user")
app.include_router(admin.router, prefix="/api/admin")

# SSL Context
ssl_context = None
cert_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cert.pem")
key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "key.pem")

if os.path.exists(cert_path) and os.path.exists(key_path):
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    try:
        ssl_context.load_cert_chain(cert_path, keyfile=key_path)
        logger.info("SSL certificates loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load SSL certificates: {str(e)}")
        raise RuntimeError("SSL certificates are required but failed to load")
else:
    logger.error("SSL certificates not found. HTTPS is required")
    raise RuntimeError(f"SSL certificates not found at {cert_path}. Please generate them using generate_ssl.py")

# Add this new middleware before the security headers middleware
@app.middleware("http")
async def https_redirect(request: Request, call_next):
    if request.url.scheme == "http":
        url = request.url.replace(scheme="https")
        return RedirectResponse(url=str(url), status_code=301)
    return await call_next(request)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"  # Enhanced HSTS
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

if __name__ == "__main__":
    import uvicorn
    host = "0.0.0.0"
    port = 8000
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        ssl_keyfile=key_path,
        ssl_certfile=cert_path,
        log_level="info"
    )