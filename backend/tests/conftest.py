import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.main import app
from app.database.connection import database
from app.core.config import Environment, ENVIRONMENT
import os

# Override environment for testing
os.environ["ENVIRONMENT"] = "testing"
os.environ["RATE_LIMIT_ENABLED"] = "false"

@pytest_asyncio.fixture
async def client():
    """Create test client with database connection"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def setup_database():
    """Set up database for testing"""
    await database.connect()
    yield
    await database.disconnect()

@pytest.fixture
def test_user_data():
    """Test user credentials"""
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "TestPassword123"
    }

@pytest.fixture
def test_task_data():
    """Test task data"""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "status": "pending",
        "priority": "medium"
    }
