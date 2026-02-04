# Backend API

FastAPI REST API with JWT auth, role-based access, and task CRUD.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/tasks` - List tasks
- `POST /api/v1/tasks` - Create task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `GET /api/v1/tasks/admin/stats` - Admin statistics (admin only)

Docs: http://localhost:8000/docs

## Database Schema

Users table: id, username (unique), email (unique), hashed_password, role (user/admin), is_active, created_at, updated_at

Tasks table: id, user_id (FK), title, description, status (pending/in_progress/completed), priority (low/medium/high), created_at, updated_at

## Security

- Bcrypt password hashing
- JWT authentication with 30-minute expiry
- Input validation with Pydantic
- SQL injection protection via parameterized queries
- CORS enabled
- Automatic connection lifecycle management

### Performance Optimizations
- Async/await for non-blocking operations
- Connection pooling to reduce database connection overhead
- Indexed primary and foreign keys

### Deployment Considerations

1. Use environment variables for sensitive data
2. Implement proper logging for monitoring
3. Set up database backups
4. Use production-grade ASGI server (Uvicorn with multiple workers)
5. Implement rate limiting for API endpoints
6. Add request/response caching where appropriate
7. Use reverse proxy (Nginx) for load balancing
8. Containerize with Docker for consistent deployment

### Scaling Strategies

1. Horizontal scaling with multiple API instances behind load balancer
2. Database replication for read scaling
3. Cache layer (Redis) for frequently accessed data
4. Message queue (RabbitMQ/Kafka) for async operations
5. Microservices architecture for independent scaling

## Testing

Run tests with:
```bash
pytest
```

## Deployment with Docker

Build Docker image:
```bash
docker build -t task-api .
```

Run container:
```bash
docker run -p 8000:8000 --env-file .env task-api
```

