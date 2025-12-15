"""
Authentication API Routes

This module contains all authentication-related API endpoints:
- User registration with email verification
- Email verification
- Login
- Token refresh
- Password reset request
- Password reset confirmation
- Logout

All endpoints follow REST API best practices with proper HTTP status codes.
"""

from datetime import timedelta, timezone, datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import TokenResponse
from app.auth.dependencies import get_current_active_user
from app.auth.email import email_service
from app.auth.redis import blacklist_token
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new user account with email verification.
    
    Process:
    1. Validate user data
    2. Create user account (unverified)
    3. Generate verification token
    4. Send verification email in background
    5. Return user data
    
    Args:
        user_data: User registration data (email, username, password, etc.)
        background_tasks: FastAPI background tasks for async email sending
        db: Database session
        
    Returns:
        UserResponse: Created user data (without password)
        
    Raises:
        HTTPException: 400 if username/email exists or validation fails
    """
    try:
        # Register user and get verification token
        user, verification_token = User.register(
            db,
            user_data.model_dump(),
            send_verification_email=True
        )
        db.commit()
        db.refresh(user)
        
        # Send verification email in background (non-blocking)
        if verification_token:
            background_tasks.add_task(
                email_service.send_verification_email,
                to_email=user.email,
                username=user.username,
                verification_token=verification_token,
                base_url=settings.BASE_URL
            )
        
        return user
        
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )


@router.get("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(
    token: str = Query(..., description="Email verification token"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Verify user's email address using the token sent via email.
    
    Args:
        token: Verification token from email link
        background_tasks: FastAPI background tasks for welcome email
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 400 if token is invalid or expired
    """
    # Find user with this verification token
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    # Verify the token
    if not user.verify_email_token(token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired. Please request a new one."
        )
    
    db.commit()
    
    # Send welcome email in background
    if background_tasks:
        background_tasks.add_task(
            email_service.send_welcome_email,
            to_email=user.email,
            username=user.username,
            first_name=user.first_name
        )
    
    return {
        "message": "Email verified successfully! You can now log in.",
        "email": user.email,
        "is_verified": True
    }


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
def resend_verification_email(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Resend verification email to user.
    
    Args:
        email: User's email address
        background_tasks: FastAPI background tasks for email sending
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 400 if email not found or already verified
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Don't reveal if email exists for security
        return {"message": "If the email exists, a verification link has been sent."}
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # Generate new verification token
    verification_token = user.generate_verification_token()
    db.commit()
    
    # Send verification email
    background_tasks.add_task(
        email_service.send_verification_email,
        to_email=user.email,
        username=user.username,
        verification_token=verification_token,
        base_url=settings.BASE_URL
    )
    
    return {"message": "Verification email sent successfully"}


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.
    
    Args:
        form_data: OAuth2 form with username and password
        db: Database session
        
    Returns:
        TokenResponse: Access token, refresh token, and user data
        
    Raises:
        HTTPException: 401 if credentials are invalid or email not verified
    """
    # Authenticate user
    auth_result = User.authenticate(
        db,
        form_data.username,
        form_data.password
    )
    
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_result["user"]
    
    # Check if email is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in. Check your inbox for the verification link.",
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support.",
        )
    
    db.commit()
    
    return {
        "access_token": auth_result["access_token"],
        "refresh_token": auth_result["refresh_token"],
        "token_type": auth_result["token_type"],
        "expires_at": auth_result["expires_at"],
        "user": user
    }


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token: Valid refresh token
        db: Database session
        
    Returns:
        TokenResponse: New access token and refresh token
        
    Raises:
        HTTPException: 401 if refresh token is invalid
    """
    # Verify refresh token
    user_id = User.verify_token(refresh_token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens
    access_token = User.create_access_token({"sub": str(user.id)})
    new_refresh_token = User.create_refresh_token({"sub": str(user.id)})
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_at": expires_at,
        "user": user
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_active_user),
    # You could pass the token here if you want to blacklist it
):
    """
    Logout current user.
    
    Note: Since we're using JWT tokens, we can't truly "revoke" them.
    In production, you'd want to:
    1. Add token to Redis blacklist
    2. Set short token expiration times
    3. Implement token versioning
    
    Args:
        current_user: Currently authenticated user
        
    Returns:
        dict: Success message
    """
    # In production, blacklist the token in Redis
    # await blacklist_token(token)
    
    return {
        "message": "Logged out successfully",
        "user": current_user.username
    }


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request password reset email.
    
    Args:
        email: User's email address
        background_tasks: FastAPI background tasks for email sending
        db: Database session
        
    Returns:
        dict: Success message (generic for security)
    """
    user = db.query(User).filter(User.email == email).first()
    
    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If the email exists, a password reset link has been sent."}
    
    # Generate reset token
    reset_token = user.generate_reset_token()
    db.commit()
    
    # Send password reset email
    background_tasks.add_task(
        email_service.send_password_reset_email,
        to_email=user.email,
        username=user.username,
        reset_token=reset_token,
        base_url=settings.BASE_URL
    )
    
    return {"message": "If the email exists, a password reset link has been sent."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """
    Reset password using reset token.
    
    Args:
        token: Password reset token
        new_password: New password
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 400 if token is invalid or expired
    """
    # Find user with this reset token
    user = db.query(User).filter(User.reset_token == token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    # Verify the token
    if not user.verify_reset_token(token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired. Please request a new one."
        )
    
    # Validate new password
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    # Update password
    user.password = User.hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {"message": "Password reset successfully. You can now log in with your new password."}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's information.
    
    Args:
        current_user: Currently authenticated user
        
    Returns:
        UserResponse: User data
    """
    return current_user
