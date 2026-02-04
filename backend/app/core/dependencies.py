from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from app.core.security import decode_access_token, is_token_blacklisted
from app.core.redis import redis_client
from app.core.config import CACHE_USER_TTL
from app.core.logging import cache_logger
from app.database.connection import database
import json

security: HTTPBearer = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get user from JWT token, check blacklist, then cache or DB"""
    token: str = credentials.credentials
    
    # Check if token is blacklisted (logout)
    if await is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload: Optional[Dict[str, Any]] = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: Optional[str] = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Try to get user from cache first
    cached_user = await redis_client.get(f"user:{username}")
    if cached_user:
        cache_logger.info("cache_hit", extra={"key": f"user:{username}"})
        return json.loads(cached_user)
    
    # If not in cache, fetch from database
    user: Optional[Dict[str, Any]] = await database.fetchrow(
        "SELECT id, username, email, role, is_active FROM users WHERE username = $1",
        username
    )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Convert asyncpg Record to dict for JSON serialization
    user_dict = dict(user)
    await redis_client.set_json(f"user:{username}", user_dict, expire=CACHE_USER_TTL)
    
    return user_dict

async def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Check user is admin, raise 403 if not"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access this resource"
        )
    return current_user
