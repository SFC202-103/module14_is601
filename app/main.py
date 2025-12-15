"""
FastAPI Main Application Module

This is a professional REST API implementation with:
- JWT authentication with email verification
- Modular API routes (auth, calculations)
- Email confirmation for new users
- Password reset functionality
- Web interface for frontend
- Swagger/ReDoc API documentation

Architecture:
- app/api/ - REST API routes (modular)
- app/models/ - Database models
- app/schemas/ - Pydantic validation schemas
- app/auth/ - Authentication and email services
- templates/ - Web interface (optional)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

# Application imports
from app.database import Base, engine
from app.core.config import get_settings
from app.api.auth import router as auth_router
from app.api.calculations import router as calculations_router


settings = get_settings()


# ------------------------------------------------------------------------------
# Lifespan Event: Database Initialization
# ------------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize database tables on startup.
    """
    print("🚀 Starting FastAPI Calculator API...")
    print("📊 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    print(f"📧 Email service configured: {settings.SMTP_HOST}")
    print(f"🔐 JWT authentication enabled")
    yield
    print("👋 Shutting down FastAPI Calculator API...")


# ------------------------------------------------------------------------------
# FastAPI Application Initialization
# ------------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## Professional REST API with JWT Authentication
    
    ### Features:
    - 🔐 JWT Authentication with Email Verification
    - 📧 Email Confirmation for New Users
    - 🔑 Password Reset Functionality
    - 🧮 Calculation Management (BREAD operations)
    - 📊 User Statistics and Analytics
    - 🔒 Secure Password Hashing
    - 🚀 Fast and Scalable
    
    ### Getting Started:
    1. Register a new account at `/api/auth/register`
    2. Check your email for verification link
    3. Verify your email at `/api/auth/verify-email?token=YOUR_TOKEN`
    4. Login at `/api/auth/login`
    5. Use the access token to make authenticated requests
    
    ### Authentication:
    - All calculation endpoints require authentication
    - Include token in header: `Authorization: Bearer YOUR_ACCESS_TOKEN`
    - Access tokens expire after 30 minutes
    - Use refresh tokens to get new access tokens
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# ------------------------------------------------------------------------------
# CORS Middleware
# ------------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------------------
# Include API Routers
# ------------------------------------------------------------------------------
app.include_router(auth_router)
app.include_router(calculations_router)


# ------------------------------------------------------------------------------
# Static Files and Templates (Optional Web Interface)
# ------------------------------------------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ------------------------------------------------------------------------------
# Web Interface Routes (Optional)
# ------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, tags=["Web Interface"])
def index(request: Request):
    """Landing page with API information."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse, tags=["Web Interface"])
def login_page(request: Request):
    """Login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse, tags=["Web Interface"])
def register_page(request: Request):
    """Registration page."""
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse, tags=["Web Interface"])
def dashboard(request: Request):
    """User dashboard."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/dashboard/view/{calc_id}", response_class=HTMLResponse, tags=["Web Interface"])
def view_calculation(request: Request, calc_id: str):
    """View calculation page."""
    return templates.TemplateResponse("view_calculation.html", 
                                     {"request": request, "calc_id": calc_id})


@app.get("/dashboard/edit/{calc_id}", response_class=HTMLResponse, tags=["Web Interface"])
def edit_calculation(request: Request, calc_id: str):
    """Edit calculation page."""
    return templates.TemplateResponse("edit_calculation.html", 
                                     {"request": request, "calc_id": calc_id})


# ------------------------------------------------------------------------------
# Health Check Endpoint
# ------------------------------------------------------------------------------
@app.get("/health", tags=["System"])
def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# ------------------------------------------------------------------------------
# API Documentation
# ------------------------------------------------------------------------------
@app.get("/api", tags=["System"])
def api_info():
    """
    API information and quick start guide.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Professional REST API with JWT Authentication and Email Verification",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "authentication": {
                "register": "POST /api/auth/register",
                "verify_email": "GET /api/auth/verify-email?token=TOKEN",
                "login": "POST /api/auth/login",
                "refresh": "POST /api/auth/refresh",
                "forgot_password": "POST /api/auth/forgot-password",
                "reset_password": "POST /api/auth/reset-password",
                "me": "GET /api/auth/me"
            },
            "calculations": {
                "create": "POST /api/calculations",
                "list": "GET /api/calculations",
                "get": "GET /api/calculations/{id}",
                "update": "PUT /api/calculations/{id}",
                "delete": "DELETE /api/calculations/{id}",
                "stats": "GET /api/calculations/stats/summary"
            }
        },
        "features": [
            "JWT Authentication",
            "Email Verification",
            "Password Reset",
            "BREAD Operations",
            "User Statistics",
            "Secure Password Hashing"
        ]
    }


# ------------------------------------------------------------------------------
# Main Block to Run the Server
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, log_level="info")
