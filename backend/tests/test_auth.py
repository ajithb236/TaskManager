import pytest
from httpx import AsyncClient
from app.main import app
from app.database.connection import database

@pytest.mark.asyncio
async def test_register_user(test_user_data):
    """Test successful user registration"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        await database.connect()
        try:
            response = await client.post(
                "/api/v1/auth/register",
                json=test_user_data
            )
            assert response.status_code == 201
            data = response.json()
            assert data["username"] == test_user_data["username"]
            assert data["email"] == test_user_data["email"]
            assert "hashed_password" not in data
        finally:
            await database.disconnect()

@pytest.mark.asyncio
async def test_register_duplicate_username(test_user_data):
    """Test registration fails with duplicate username"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        await database.connect()
        try:
            # First registration
            response1 = await client.post(
                "/api/v1/auth/register",
                json=test_user_data
            )
            assert response1.status_code == 201
            
            # Second registration with same username
            duplicate_data = test_user_data.copy()
            duplicate_data["email"] = "different@example.com"
            
            response2 = await client.post(
                "/api/v1/auth/register",
                json=duplicate_data
            )
            assert response2.status_code == 400
            assert "already registered" in response2.json()["detail"]
        finally:
            await database.disconnect()

@pytest.mark.asyncio
async def test_login_successful(test_user_data):
    """Test successful login"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        await database.connect()
        try:
            # Register first
            await client.post("/api/v1/auth/register", json=test_user_data)
            
            # Then login
            login_data = {
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
            response = await client.post("/api/v1/auth/login", json=login_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert data["user"]["username"] == test_user_data["username"]
        finally:
            await database.disconnect()

@pytest.mark.asyncio
async def test_login_invalid_password(test_user_data):
    """Test login fails with invalid password"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        await database.connect()
        try:
            # Register first
            await client.post("/api/v1/auth/register", json=test_user_data)
            
            # Try login with wrong password
            login_data = {
                "username": test_user_data["username"],
                "password": "WrongPassword123"
            }
            response = await client.post("/api/v1/auth/login", json=login_data)
            
            assert response.status_code == 401
            assert "Invalid username or password" in response.json()["detail"]
        finally:
            await database.disconnect()

@pytest.mark.asyncio
async def test_password_strength_validation():
    """Test password must contain uppercase and digit"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        await database.connect()
        try:
            # Password without uppercase
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "weakpassword123"
                }
            )
            assert response.status_code == 422
            
            # Password without digit
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "username": "testuser2",
                    "email": "test2@example.com",
                    "password": "WeakPassword"
                }
            )
            assert response.status_code == 422
        finally:
            await database.disconnect()
