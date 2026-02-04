from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database.connection import database
from app.database.schema import init_database
from app.core.redis import redis_client
from app.core.logging import setup_logging, request_logger
from app.core.rate_limit import limiter
from app.core.config import DEBUG, ALLOWED_ORIGINS
from app.api.v1.auth import router as auth_router
from app.api.v1.tasks import router as tasks_router
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
import time

# Initialize logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    request_logger.info("application_starting", extra={"debug": DEBUG})
    await database.connect()
    request_logger.info("database_connected")
    await redis_client.connect()
    request_logger.info("redis_connected")
    await init_database()
    request_logger.info("database_initialized")
    
    yield
    
    request_logger.info("application_shutting_down")
    await database.disconnect()
    await redis_client.disconnect()
    request_logger.info("application_stopped")

app = FastAPI(
    title="Task Management API",
    description="Scalable REST API with authentication, role-based access, and task management",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded", "detail": exc.detail}
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log successful requests
        request_logger.info(
            "http_request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "client_ip": request.client.host if request.client else "unknown"
            }
        )
        
        return response
    except Exception as e:
        duration = time.time() - start_time
        request_logger.error(
            "http_request_error",
            extra={
                "method": request.method,
                "path": request.url.path,
                "duration_ms": round(duration * 1000, 2),
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        raise

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tasks_router)

@app.get("/", tags=["health"])
async def root():
    """Health check and API info endpoint"""
    return {"message": "Task Management API is running", "version": "1.0.0"}

@app.get("/health", tags=["health"])
async def health_check():
    """Detailed health check endpoint"""
    return {"status": "healthy"}
