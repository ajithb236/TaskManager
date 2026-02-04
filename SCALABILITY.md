# Scalability Notes

## Horizontal Scaling

The API is stateless and runs in Docker containers. Multiple instances can be deployed behind a load balancer (Nginx, HAProxy, or cloud provider load balancer). Database connections use asyncpg connection pooling, configured for concurrent requests.

## Database Optimization

PostgreSQL handles the current scale. For growth:
- Indexes on user queries are implemented (username, email)
- Task queries are indexed on user_id for faster lookups
- Read replicas can be added for read-heavy operations
- Connection pooling uses PgBouncer or similar for production

## Caching Strategy

Redis caches user objects (5 min TTL) and task lists (1 min TTL). Cache invalidation happens on mutations. For distributed caching, Redis Cluster can replace single instances.

## Rate Limiting

Slowapi enforces per-minute limits: 5/min for auth, 50/min for tasks, 100/min for general endpoints. Token bucket algorithm prevents abuse. Limits can be adjusted based on load testing.

## Monitoring and Logging

Structured JSON logging captures all requests, errors, and database operations. Logs can be shipped to ELK Stack or Datadog. Health check endpoints at /health and /docs are available for monitoring.

## Microservices Path

Currently monolithic. Future separation:
- Auth service handles registration/login only
- Task service handles CRUD operations
- Separate database per service for independent scaling

## Deployment

Docker Compose is for development. For production: Kubernetes with separate deployments for API, PostgreSQL, and Redis. Use managed services (AWS RDS, ElastiCache) instead of self-hosted databases.

## JWT Token Strategy

Tokens expire in 30 minutes. Refresh tokens can be implemented for longer sessions. Token blacklist stored in Redis with configurable expiry.
