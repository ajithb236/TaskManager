import pytest
from httpx import AsyncClient
from app.main import app
from app.database.connection import database

@pytest.mark.asyncio
async def test_create_task(test_user_data, test_task_data):
    """Test creating a task"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        await database.connect()
        try:
            # Register and login
            await client.post("/api/v1/auth/register", json=test_user_data)
            login_response = await client.post(
                "/api/v1/auth/login",
                json={
                    "username": test_user_data["username"],
                    "password": test_user_data["password"]
                }
            )
            token = login_response.json()["access_token"]
            
            # Create task
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.post(
                "/api/v1/tasks",
                json=test_task_data,
                headers=headers
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == test_task_data["title"]
            assert data["status"] == "pending"
            assert "id" in data
        finally:
            await database.disconnect()

@pytest.mark.asyncio
async def test_list_tasks(test_user_data, test_task_data):
    """Test listing tasks"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        await database.connect()
        try:
            # Register and login
            await client.post("/api/v1/auth/register", json=test_user_data)
            login_response = await client.post(
                "/api/v1/auth/login",
                json={
                    "username": test_user_data["username"],
                    "password": test_user_data["password"]
                }
            )
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create task
            await client.post("/api/v1/tasks", json=test_task_data, headers=headers)
            
            # List tasks
            response = await client.get("/api/v1/tasks", headers=headers)
            
            assert response.status_code == 200
            tasks = response.json()
            assert len(tasks) > 0
            assert tasks[0]["title"] == test_task_data["title"]
        finally:
            await database.disconnect()

@pytest.mark.asyncio
async def test_get_task(test_user_data, test_task_data):
    """Test getting a specific task"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        await database.connect()
        try:
            # Register and login
            await client.post("/api/v1/auth/register", json=test_user_data)
            login_response = await client.post(
                "/api/v1/auth/login",
                json={
                    "username": test_user_data["username"],
                    "password": test_user_data["password"]
                }
            )
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create task
            create_response = await client.post(
                "/api/v1/tasks",
                json=test_task_data,
                headers=headers
            )
            task_id = create_response.json()["id"]
            
            # Get task
            response = await client.get(f"/api/v1/tasks/{task_id}", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == task_id
            assert data["title"] == test_task_data["title"]
        finally:
            await database.disconnect()

@pytest.mark.asyncio
async def test_update_task(test_user_data, test_task_data):
    """Test updating a task"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        await database.connect()
        try:
            # Register and login
            await client.post("/api/v1/auth/register", json=test_user_data)
            login_response = await client.post(
                "/api/v1/auth/login",
                json={
                    "username": test_user_data["username"],
                    "password": test_user_data["password"]
                }
            )
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create task
            create_response = await client.post(
                "/api/v1/tasks",
                json=test_task_data,
                headers=headers
            )
            task_id = create_response.json()["id"]
            
            # Update task
            update_data = {"status": "in_progress", "priority": "high"}
            response = await client.put(
                f"/api/v1/tasks/{task_id}",
                json=update_data,
                headers=headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "in_progress"
            assert data["priority"] == "high"
        finally:
            await database.disconnect()

@pytest.mark.asyncio
async def test_delete_task(test_user_data, test_task_data):
    """Test deleting a task"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        await database.connect()
        try:
            # Register and login
            await client.post("/api/v1/auth/register", json=test_user_data)
            login_response = await client.post(
                "/api/v1/auth/login",
                json={
                    "username": test_user_data["username"],
                    "password": test_user_data["password"]
                }
            )
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create task
            create_response = await client.post(
                "/api/v1/tasks",
                json=test_task_data,
                headers=headers
            )
            task_id = create_response.json()["id"]
            
            # Delete task
            response = await client.delete(f"/api/v1/tasks/{task_id}", headers=headers)
            assert response.status_code == 204
            
            # Verify deleted
            get_response = await client.get(f"/api/v1/tasks/{task_id}", headers=headers)
            assert get_response.status_code == 404
        finally:
            await database.disconnect()

@pytest.mark.asyncio
async def test_unauthorized_access():
    """Test accessing protected endpoints without token"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/tasks")
        assert response.status_code == 403  # Forbidden without token
