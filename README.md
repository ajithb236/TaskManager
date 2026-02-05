# Task Management API

FastAPI backend with JWT auth, role-based access, task CRUD, and vanilla HTML/JS frontend.

- Frontend  https://task-manager-v4wh.onrender.com
- API Docs : https://taskmanager-7eql.onrender.com/docs
## Quick Start

```bash
docker-compose up
```

- Frontend: http://localhost:3000
- API: http://127.0.0.1:9500
- Docs: http://127.0.0.1:9500/docs

## Stack

FastAPI | PostgreSQL | Redis | Alembic | Docker

## Setup (Without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## API Endpoints

**Authentication**
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout

**Tasks**
- `GET /api/v1/tasks` - List tasks (paginated)
- `POST /api/v1/tasks` - Create task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `GET /api/v1/tasks/admin/stats` - Admin stats (admin only)

## Auth Headers

```
Authorization: Bearer {access_token}
```

## Database

PostgreSQL with async connection pooling. Alembic for schema management.

## Features

- JWT authentication with 30-min expiry
- Role-based access control (user/admin)
- Rate limiting (5/min auth, 50/min tasks, 100/min general)
- Redis caching for users, tasks, and stats
- Structured JSON logging
- Input validation (username, email, password)
- Password hashing with bcrypt


