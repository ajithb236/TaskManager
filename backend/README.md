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

POST /api/v1/auth/register - Register user
POST /api/v1/auth/login - Login user
POST /api/v1/auth/logout - Logout user
GET /api/v1/tasks - List tasks
POST /api/v1/tasks - Create task
PUT /api/v1/tasks/{id} - Update task
DELETE /api/v1/tasks/{id} - Delete task

Docs: http://localhost:8000/docs

The API will be available at `http://localhost:8000`
Swagger documentation: `http://localhost:8000/docs`

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and receive JWT token

### Tasks

- `POST /api/v1/tasks` - Create a new task
- `GET /api/v1/tasks` - List all tasks for current user
- `GET /api/v1/tasks/{task_id}` - Get a specific task
- `PUT /api/v1/tasks/{task_id}` - Update a task
- `DELETE /api/v1/tasks/{task_id}` - Delete a task

## Database Schema

### Users Table
- id: Auto-incrementing primary key
- username: Unique username
- email: Unique email address
- hashed_password: Bcrypt hashed password with salt
- role: User role (user or admin)
- is_active: Account status
- created_at: Creation timestamp
- updated_at: Last update timestamp

### Tasks Table
- id: Auto-incrementing primary key
- user_id: Foreign key referencing users
- title: Task title
- description: Task description
- status: Task status (pending, in_progress, completed)
- priority: Task priority (low, medium, high)
- created_at: Creation timestamp
- updated_at: Last update timestamp

## Security Considerations

- Passwords are hashed with bcrypt using salt
- JWT tokens for stateless authentication
- HTTPOnly bearer token authentication
- Input validation with Pydantic
- SQL injection protection via parameterized queries
- CORS enabled for frontend integration

## Scalability

### Database Connection Pooling
- asyncpg pool with 5-20 connections
- Configurable pool size for different load scenarios
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

## Error Handling

All endpoints return appropriate HTTP status codes:
- 200: Success
- 201: Resource created
- 400: Bad request
- 401: Unauthorized
- 403: Forbidden
- 404: Not found
- 500: Internal server error

Error responses include a detail field explaining the error.

## License

This project is created as part of the Backend Developer Intern assignment.
