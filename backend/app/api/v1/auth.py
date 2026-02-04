from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta
from typing import Optional, Dict, Any
from app.schemas.schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from app.core.security import hash_password, verify_password, create_access_token, blacklist_token
from app.core.config import JWT_ACCESS_TOKEN_EXPIRE_MINUTES, RATE_LIMIT_AUTH, RATE_LIMIT_GENERAL
from app.core.dependencies import get_current_user
from app.core.redis import redis_client
from app.core.logging import auth_logger
from app.core.rate_limit import limiter
from app.database.connection import database

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
security: HTTPBearer = HTTPBearer()

async def validate_user_availability(username: str, email: str) -> Optional[dict]:
    existing_user = await database.fetchrow(
        "SELECT id FROM users WHERE username = $1 OR email = $2",
        username.lower(),
        email.lower()
    )
    return existing_user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RATE_LIMIT_AUTH)
async def register_user(request: Request, user_data: UserRegister) -> UserResponse:
    auth_logger.info("user_registration_attempt", extra={"username": user_data.username})
    
    existing_user: Optional[dict] = await validate_user_availability(user_data.username, user_data.email)
    
    if existing_user:
        auth_logger.warning("user_registration_failed", extra={
            "username": user_data.username,
            "reason": "username_or_email_already_exists"
        })
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    hashed_password: str = hash_password(user_data.password)
    
    user: dict = await database.fetchrow(
        """INSERT INTO users (username, email, hashed_password, role, is_active)
           VALUES ($1, $2, $3, $4, $5)
           RETURNING id, username, email, role, is_active, created_at""",
        user_data.username.lower(),
        user_data.email.lower(),
        hashed_password,
        "user",
        True
    )
    
    auth_logger.info("user_registered_successfully", extra={"user_id": user["id"], "username": user["username"]})
    
    return UserResponse(**user)

@router.post("/login", response_model=TokenResponse)
@limiter.limit(RATE_LIMIT_AUTH)
async def login_user(request: Request, credentials: UserLogin) -> TokenResponse:
    """Authenticate user and return JWT token"""
    auth_logger.info("login_attempt", extra={"username": credentials.username})
    
    user: Optional[dict] = await database.fetchrow(
        "SELECT id, username, email, hashed_password, role, is_active, created_at FROM users WHERE username = $1",
        credentials.username.lower()
    )
    
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        auth_logger.warning("login_failed", extra={
            "username": credentials.username,
            "reason": "invalid_credentials"
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user["is_active"]:
        auth_logger.warning("login_failed", extra={
            "username": credentials.username,
            "reason": "user_inactive"
        })
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    access_token_expires: timedelta = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token: str = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    user_response: UserResponse = UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        role=user["role"],
        is_active=user["is_active"],
        created_at=user["created_at"]
    )
    
    auth_logger.info("login_successful", extra={"user_id": user["id"], "username": user["username"]})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@router.post("/logout", status_code=status.HTTP_200_OK)
@limiter.limit(RATE_LIMIT_GENERAL)
async def logout_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """Blacklist token and clear user cache"""
    auth_logger.info("logout_attempt", extra={"user_id": current_user["id"], "username": current_user["username"]})
    
    # Blacklist the token to prevent reuse
    token = credentials.credentials
    await blacklist_token(token)
    
    # Clear the user cache
    await redis_client.delete(f"user:{current_user['username']}")
    
    auth_logger.info("logout_successful", extra={"user_id": current_user["id"]})
    
    return {"message": "Logged out successfully"}
