import pytest
from httpx import AsyncClient
from app.main import app
from app.database.connection import database

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def setup_db():
    await database.connect()
    yield
    await database.disconnect()

class TestAuthentication:
    
    @pytest.mark.asyncio
    async def test_register_user(self, client, setup_db):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPassword123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client, setup_db):
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test1@example.com",
                "password": "TestPassword123"
            }
        )
        
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test2@example.com",
                "password": "TestPassword123"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_short_password(self, client, setup_db):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "short"
            }
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_success(self, client, setup_db):
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPassword123"
            }
        )
        
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "TestPassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client, setup_db):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "password"
            }
        )
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

class TestTasks:
    
    @pytest.fixture
    async def auth_token(self, client, setup_db):
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPassword123"
            }
        )
        
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "TestPassword123"
            }
        )
        return response.json()["access_token"]

    @pytest.mark.asyncio
    async def test_create_task(self, client, setup_db, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "description": "Task description",
                "status": "pending",
                "priority": "high"
            },
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Task description"
        assert data["status"] == "pending"
        assert data["priority"] == "high"

    @pytest.mark.asyncio
    async def test_create_task_without_auth(self, client, setup_db):
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "description": "Task description",
                "status": "pending",
                "priority": "high"
            }
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_tasks(self, client, setup_db, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        await client.post(
            "/api/v1/tasks",
            json={
                "title": "Task 1",
                "description": "Description 1",
                "status": "pending",
                "priority": "high"
            },
            headers=headers
        )
        
        await client.post(
            "/api/v1/tasks",
            json={
                "title": "Task 2",
                "description": "Description 2",
                "status": "in_progress",
                "priority": "medium"
            },
            headers=headers
        )
        
        response = await client.get(
            "/api/v1/tasks",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_get_task(self, client, setup_db, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        create_response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "description": "Task description",
                "status": "pending",
                "priority": "high"
            },
            headers=headers
        )
        task_id = create_response.json()["id"]
        
        response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"

    @pytest.mark.asyncio
    async def test_update_task(self, client, setup_db, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        create_response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "description": "Task description",
                "status": "pending",
                "priority": "high"
            },
            headers=headers
        )
        task_id = create_response.json()["id"]
        
        response = await client.put(
            f"/api/v1/tasks/{task_id}",
            json={
                "status": "completed",
                "priority": "low"
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["priority"] == "low"

    @pytest.mark.asyncio
    async def test_delete_task(self, client, setup_db, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        create_response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "description": "Task description",
                "status": "pending",
                "priority": "high"
            },
            headers=headers
        )
        task_id = create_response.json()["id"]
        
        response = await client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=headers
        )
        assert response.status_code == 204
        
        get_response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_user_cannot_access_other_tasks(self, client, setup_db):
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "user1",
                "email": "user1@example.com",
                "password": "TestPassword123"
            }
        )
        
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "user2",
                "email": "user2@example.com",
                "password": "TestPassword123"
            }
        )
        
        token1_response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "user1",
                "password": "TestPassword123"
            }
        )
        token1 = token1_response.json()["access_token"]
        
        token2_response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "user2",
                "password": "TestPassword123"
            }
        )
        token2 = token2_response.json()["access_token"]
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        create_response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "User1 Task",
                "description": "Description",
                "status": "pending",
                "priority": "high"
            },
            headers=headers1
        )
        task_id = create_response.json()["id"]
        
        headers2 = {"Authorization": f"Bearer {token2}"}
        response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=headers2
        )
        assert response.status_code == 404
