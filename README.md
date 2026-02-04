# Task Management API

A FastAPI backend with JWT authentication, role-based access, and task CRUD operations. Includes a vanilla HTML/JS frontend for testing.

## Quick Start

```bash
docker-compose up
```

Access:
- Frontend: http://localhost:3000
- API: http://127.0.0.1:9500
- Docs: http://127.0.0.1:9500/docs

## Setup (Without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Stack

Backend: FastAPI, PostgreSQL, Redis, Alembic
Frontend: Vanilla HTML/JS
Container: Docker, docker-compose
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tasks Table
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(50) DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Installation & Setup

### Prerequisites

- Python 3.9+
- Node.js 14+
- PostgreSQL 12+
- pip and npm package managers

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create PostgreSQL database:
```bash
psql -U postgres
CREATE DATABASE taskdb;
```

5. Configure environment variables in `.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/taskdb
SECRET_KEY=your-secure-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
```

6. Run the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
Swagger documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```
REACT_APP_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm start
```

The application will open at `http://localhost:3000`

## API Endpoints

### Authentication Endpoints

```
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123"
}

Response 201:
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2024-02-04T10:30:00"
}
```

```
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePassword123"
}

Response 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2024-02-04T10:30:00"
  }
}
```

### Task Endpoints

All task endpoints require authentication with Bearer token.

```
POST /api/v1/tasks
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Complete project",
  "description": "Finish the backend implementation",
  "status": "pending",
  "priority": "high"
}

Response 201:
{
  "id": 1,
  "user_id": 1,
  "title": "Complete project",
  "description": "Finish the backend implementation",
  "status": "pending",
  "priority": "high",
  "created_at": "2024-02-04T10:35:00",
  "updated_at": "2024-02-04T10:35:00"
}
```

```
GET /api/v1/tasks
Authorization: Bearer {token}

Response 200:
[
  {
    "id": 1,
    "user_id": 1,
    "title": "Complete project",
    "description": "Finish the backend implementation",
    "status": "pending",
    "priority": "high",
    "created_at": "2024-02-04T10:35:00",
    "updated_at": "2024-02-04T10:35:00"
  }
]
```

```
GET /api/v1/tasks/{task_id}
Authorization: Bearer {token}

Response 200: [Task object]
```

```
PUT /api/v1/tasks/{task_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "in_progress",
  "priority": "medium"
}

Response 200: [Updated Task object]
```

```
DELETE /api/v1/tasks/{task_id}
Authorization: Bearer {token}

Response 204: No Content
```

## Security Implementation

### Password Hashing

Passwords are securely hashed using bcrypt with automatic salt generation:

```python
from app.core.security import hash_password, verify_password

hashed_password = hash_password("user_password")
is_valid = verify_password("user_password", hashed_password)
```

The bcrypt algorithm automatically generates and stores the salt within the hash, making it resistant to rainbow table attacks.

### JWT Authentication

- Tokens expire after 30 minutes by default
- Tokens contain user information (username and role)
- All protected endpoints validate token authenticity
- HTTPOnly flag recommended for production deployment

### Input Validation

Pydantic models ensure all inputs are validated before processing:
- Email format validation
- Password minimum length (8 characters)
- Username length constraints (3-50 characters)
- Type checking for all fields

### SQL Injection Protection

All database queries use parameterized statements:
```python
await database.fetchrow(
    "SELECT * FROM users WHERE username = $1",
    username
)
```

## Database Connection Pooling

asyncpg connection pool configuration:
- Minimum connections: 5
- Maximum connections: 20
- Command timeout: 60 seconds
- Automatic connection reuse
- Connection lifecycle management

Connection pooling reduces overhead and improves performance under load.

## Error Handling

Consistent error responses across all endpoints:

```
400 Bad Request: Invalid input
{
  "detail": "Username or email already registered"
}

401 Unauthorized: Authentication failed
{
  "detail": "Invalid username or password"
}

403 Forbidden: Insufficient permissions
{
  "detail": "Only administrators can access this resource"
}

404 Not Found: Resource does not exist
{
  "detail": "Task not found"
}

500 Internal Server Error: Server error
{
  "detail": "Internal server error"
}
```

## Scalability Considerations

### Current Architecture

- Single database instance with connection pooling
- Stateless API servers (can scale horizontally)
- JWT tokens enable distributed authentication
- User-specific data isolation (users can only access their own tasks)

### Scaling Strategies

1. Horizontal Scaling
   - Run multiple FastAPI instances behind a load balancer
   - Use Nginx or AWS ALB for request distribution
   - Stateless design ensures seamless scaling

2. Database Scaling
   - PostgreSQL replication for read scaling
   - Primary-replica setup with read replicas
   - Connection pooling on each server instance

3. Caching Layer
   - Redis for session caching
   - Cache frequently accessed user data
   - Reduce database load

4. Microservices Architecture
   - Separate authentication service
   - Independent task service
   - Independent user service
   - Event-driven communication

5. Asynchronous Processing
   - Message queue (RabbitMQ/Kafka) for async operations
   - Background workers for heavy operations
   - Email notifications for task updates

6. Monitoring & Logging
   - Centralized logging with ELK stack
   - Application performance monitoring (APM)
   - Database query monitoring
   - Alert systems for anomalies

## Deployment

### Docker Deployment

1. Build the Docker image:
```bash
cd backend
docker build -t task-api:latest .
```

2. Run the container:
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/taskdb \
  -e SECRET_KEY=your-secret-key \
  task-api:latest
```

### Production Deployment

1. Use environment-specific configuration
2. Set DEBUG=False in production
3. Use strong SECRET_KEY (generate with `openssl rand -hex 32`)
4. Enable HTTPS/TLS
5. Set up proper CORS policies
6. Implement rate limiting
7. Enable logging and monitoring

### Docker Compose (Optional)

Create a `docker-compose.yml` for complete stack:
```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: taskdb
      POSTGRES_PASSWORD: password
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/taskdb
    depends_on:
      - db
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
```

Run with:
```bash
docker-compose up
```

## Testing

### Backend Testing

Run pytest to execute tests:
```bash
pytest
```

### Frontend Testing

Run React tests:
```bash
npm test
```

## Performance Optimization

1. Database Query Optimization
   - Use indexed primary and foreign keys
   - Avoid N+1 queries
   - Use connection pooling

2. API Response Optimization
   - Return only necessary fields
   - Implement pagination for large datasets
   - Use compression (gzip)

3. Frontend Optimization
   - Code splitting with React
   - Lazy loading components
   - Minification and compression

## API Documentation

Auto-generated Swagger documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Code Quality

- Clean code following PEP 8 standards
- No comments in production code (self-documenting through naming)
- Modular structure for maintainability
- Type hints for better IDE support
- Proper separation of concerns

## Troubleshooting

### Database Connection Issues

If you get a connection error:
1. Verify PostgreSQL is running
2. Check DATABASE_URL in .env
3. Verify database exists
4. Check user credentials

### CORS Errors

CORS is enabled for all origins in development. For production:
- Specify allowed origins in CORS middleware
- Configure frontend URL properly

### Token Expiration

If receiving 401 errors:
1. Login again to get a fresh token
2. Check token expiration settings in config.py
3. Verify token is stored in localStorage

## Future Enhancements

1. Email verification for registration
2. Password reset functionality
3. Two-factor authentication
4. Task categories and tags
5. Task assignment to other users
6. Task notifications
7. Collaboration features
8. File attachments for tasks
9. Task templates
10. Advanced filtering and search

## License

This project is created as part of the Backend Developer Intern assignment at Primetrade.

## Support

For issues or questions, please refer to the README files in backend and frontend directories for specific setup instructions.

---

Created: February 4, 2026
Version: 1.0.0
