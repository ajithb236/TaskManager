import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

class Environment(str, Enum):
    development = "development"
    testing = "testing"
    production = "production"

ENVIRONMENT = Environment(os.getenv("ENVIRONMENT", Environment.development))

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "taskdb")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
DATABASE_POOL_MIN_SIZE = int(os.getenv("DATABASE_POOL_MIN_SIZE", "10"))
DATABASE_POOL_MAX_SIZE = int(os.getenv("DATABASE_POOL_MAX_SIZE", "50"))
DATABASE_COMMAND_TIMEOUT = int(os.getenv("DATABASE_COMMAND_TIMEOUT", "60"))

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}")

CACHE_USER_TTL = 300
CACHE_TASKS_TTL = 60

if ENVIRONMENT == Environment.production:
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    if not jwt_secret:
        raise ValueError("JWT_SECRET_KEY environment variable must be set in production")
    JWT_SECRET_KEY = jwt_secret
else:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-unsafe-do-not-use-in-production")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
TOKEN_BLACKLIST_EXPIRE_MINUTES = JWT_ACCESS_TOKEN_EXPIRE_MINUTES

RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_AUTH = "5/minute"
RATE_LIMIT_GENERAL = "100/minute"
RATE_LIMIT_TASKS = "50/minute"

DEBUG = ENVIRONMENT == Environment.development
MAX_REQUEST_SIZE = 10_000_000
REQUEST_TIMEOUT = 60

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
if ALLOWED_ORIGINS != "*":
    ALLOWED_ORIGINS = ALLOWED_ORIGINS.split(",")
