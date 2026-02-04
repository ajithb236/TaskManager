from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    """Task status enumeration"""
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class TaskPriority(str, Enum):
    """Task priority enumeration"""
    low = "low"
    medium = "medium"
    high = "high"

class UserRole(str, Enum):
    """User role enumeration"""
    user = "user"
    admin = "admin"

class UserRegister(BaseModel):
    """User registration request schema"""
    username: str = Field(..., min_length=3, max_length=50, description="Username between 3 and 50 characters")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password minimum 8 characters")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username contains only alphanumeric characters and underscores"""
        if not all(c.isalnum() or c == '_' for c in v):
            raise ValueError('Username must be alphanumeric or contain underscores only')
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password has mixed case and numeric characters"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    """User login request schema"""
    username: str = Field(..., min_length=1, description="Username for login")
    password: str = Field(..., min_length=1, description="Password for login")

class UserResponse(BaseModel):
    """User response schema (no password)"""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="User email")
    role: str = Field(..., description="User role (user or admin)")
    is_active: bool = Field(..., description="Account active status")
    created_at: datetime = Field(..., description="Account creation timestamp")

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Authentication token response schema"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="Authenticated user information")

class TaskCreate(BaseModel):
    """Task creation request schema"""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.pending, description="Task status")
    priority: TaskPriority = Field(default=TaskPriority.medium, description="Task priority")
    
    @field_validator('title')
    @classmethod
    def validate_title_no_xss(cls, v: str) -> str:
        """Ensure title doesn't contain HTML/script tags"""
        dangerous_chars = ['<', '>', '"', "'", '&']
        if any(char in v for char in dangerous_chars):
            raise ValueError('Title contains invalid characters')
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description_no_xss(cls, v: Optional[str]) -> Optional[str]:
        """Ensure description doesn't contain HTML/script tags"""
        if v is None:
            return v
        dangerous_chars = ['<', '>', '"', "'", '&']
        if any(char in v for char in dangerous_chars):
            raise ValueError('Description contains invalid characters')
        return v.strip()

class TaskUpdate(BaseModel):
    """Task update request schema (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated task title")
    description: Optional[str] = Field(None, max_length=2000, description="Updated task description")
    status: Optional[TaskStatus] = Field(None, description="Updated task status")
    priority: Optional[TaskPriority] = Field(None, description="Updated task priority")
    
    @field_validator('title')
    @classmethod
    def validate_title_no_xss(cls, v: Optional[str]) -> Optional[str]:
        """Ensure title doesn't contain HTML/script tags"""
        if v is None:
            return v
        dangerous_chars = ['<', '>', '"', "'", '&']
        if any(char in v for char in dangerous_chars):
            raise ValueError('Title contains invalid characters')
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description_no_xss(cls, v: Optional[str]) -> Optional[str]:
        """Ensure description doesn't contain HTML/script tags"""
        if v is None:
            return v
        dangerous_chars = ['<', '>', '"', "'", '&']
        if any(char in v for char in dangerous_chars):
            raise ValueError('Description contains invalid characters')
        return v.strip()

class TaskResponse(BaseModel):
    """Task response schema"""
    id: int = Field(..., description="Task ID")
    user_id: int = Field(..., description="Owner user ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: str = Field(..., description="Task status")
    priority: str = Field(..., description="Task priority")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Task last update timestamp")

    class Config:
        from_attributes = True
