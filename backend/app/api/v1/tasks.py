from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import List, Optional, Dict, Any
import json
from app.schemas.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.database.connection import database
from app.core.dependencies import get_current_user, get_admin_user
from app.core.redis import redis_client
from app.core.config import CACHE_TASKS_TTL, RATE_LIMIT_TASKS
from app.core.logging import task_logger, cache_logger
from app.core.rate_limit import limiter

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

async def verify_task_ownership(task_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    task: Optional[Dict[str, Any]] = await database.fetchrow(
        "SELECT id FROM tasks WHERE id = $1 AND user_id = $2",
        task_id,
        user_id
    )
    return task

async def invalidate_user_tasks_cache(user_id: int) -> None:
    keys = await redis_client.client.keys(f"tasks:{user_id}:page:*")
    if keys:
        for key in keys:
            await redis_client.delete(key)

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RATE_LIMIT_TASKS)
async def create_task(request: Request, task_data: TaskCreate, current_user: Dict[str, Any] = Depends(get_current_user)) -> TaskResponse:
    task: Dict[str, Any] = await database.fetchrow(
        """INSERT INTO tasks (user_id, title, description, status, priority)
           VALUES ($1, $2, $3, $4, $5)
           RETURNING id, user_id, title, description, status, priority, created_at, updated_at""",
        current_user["id"],
        task_data.title,
        task_data.description,
        task_data.status.value,
        task_data.priority.value
    )
    
    await invalidate_user_tasks_cache(current_user["id"])
    
    task_logger.info("task_created", extra={"task_id": task["id"], "user_id": current_user["id"]})
    return TaskResponse(**task)

@router.get("", response_model=List[TaskResponse])
@limiter.limit(RATE_LIMIT_TASKS)
async def list_tasks(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max tasks to return (max 100)")
) -> List[TaskResponse]:
    cache_key: str = f"tasks:{current_user['id']}:page:{skip}:{limit}"
    
    cached_tasks = await redis_client.get(cache_key)
    if cached_tasks:
        tasks_data: List[Dict[str, Any]] = json.loads(cached_tasks)
        cache_logger.info("cache_hit", extra={"key": cache_key, "user_id": current_user["id"], "count": len(tasks_data)})
        return [TaskResponse(**task) for task in tasks_data]
    
    tasks: List[Dict[str, Any]] = await database.fetch(
        """SELECT id, user_id, title, description, status, priority, created_at, updated_at
           FROM tasks WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3""",
        current_user["id"],
        limit,
        skip
    )
    
    if tasks:
        tasks_serializable = [{**dict(task), 'created_at': task['created_at'].isoformat(), 'updated_at': task['updated_at'].isoformat()} for task in tasks]
        await redis_client.set(cache_key, json.dumps(tasks_serializable), expire=CACHE_TASKS_TTL)
        cache_logger.info("cache_set", extra={"key": cache_key, "user_id": current_user["id"], "ttl": CACHE_TASKS_TTL})
    
    task_logger.info("tasks_listed", extra={"user_id": current_user["id"], "count": len(tasks), "skip": skip, "limit": limit})
    return [TaskResponse(**task) for task in tasks]

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, current_user: Dict[str, Any] = Depends(get_current_user)) -> TaskResponse:
    task: Optional[Dict[str, Any]] = await database.fetchrow(
        """SELECT id, user_id, title, description, status, priority, created_at, updated_at
           FROM tasks WHERE id = $1 AND user_id = $2""",
        task_id,
        current_user["id"]
    )
    
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return TaskResponse(**task)

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_data: TaskUpdate, current_user: Dict[str, Any] = Depends(get_current_user)) -> TaskResponse:
    existing_task: Optional[Dict[str, Any]] = await verify_task_ownership(task_id, current_user["id"])
    
    if not existing_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    update_fields: List[str] = []
    update_values: List[Any] = []
    param_count: int = 1
    
    if task_data.title is not None:
        update_fields.append(f"title = ${param_count}")
        update_values.append(task_data.title)
        param_count += 1
    
    if task_data.description is not None:
        update_fields.append(f"description = ${param_count}")
        update_values.append(task_data.description)
        param_count += 1
    
    if task_data.status is not None:
        update_fields.append(f"status = ${param_count}")
        update_values.append(task_data.status.value)
        param_count += 1
    
    if task_data.priority is not None:
        update_fields.append(f"priority = ${param_count}")
        update_values.append(task_data.priority.value)
        param_count += 1
    
    if not update_fields:
        existing_data: Dict[str, Any] = await database.fetchrow(
            "SELECT id, user_id, title, description, status, priority, created_at, updated_at FROM tasks WHERE id = $1 AND user_id = $2",
            task_id,
            current_user["id"]
        )
        return TaskResponse(**existing_data)
    
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    update_values.extend([task_id, current_user["id"]])
    
    query: str = f"""UPDATE tasks SET {', '.join(update_fields)}
                WHERE id = ${param_count} AND user_id = ${param_count + 1}
                RETURNING id, user_id, title, description, status, priority, created_at, updated_at"""
    
    task: Dict[str, Any] = await database.fetchrow(query, *update_values)
    await invalidate_user_tasks_cache(current_user["id"])
    
    return TaskResponse(**task)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, current_user: Dict[str, Any] = Depends(get_current_user)) -> None:
    existing_task: Optional[Dict[str, Any]] = await verify_task_ownership(task_id, current_user["id"])
    
    if not existing_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    await database.execute("DELETE FROM tasks WHERE id = $1 AND user_id = $2", task_id, current_user["id"])
    await invalidate_user_tasks_cache(current_user["id"])

@router.get("/admin/stats", tags=["admin"])
async def get_admin_stats(admin_user: Dict[str, Any] = Depends(get_admin_user)) -> Dict[str, Any]:
    """Get statistics on all tasks and users. Admin only."""
    cache_key = "admin:stats"
    
    # Try to get from cache first
    cached_stats = await redis_client.get(cache_key)
    if cached_stats:
        cache_logger.info("cache_hit", extra={"key": cache_key})
        stats_dict = json.loads(cached_stats)
        stats_dict["cached"] = True
        return stats_dict
    
    # If not cached, fetch from database
    total_tasks = await database.fetchval("SELECT COUNT(*) FROM tasks")
    total_users = await database.fetchval("SELECT COUNT(*) FROM users")
    completed_tasks = await database.fetchval("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
    
    stats = {
        "total_users": total_users,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "admin_id": admin_user["id"],
        "cached": False
    }
    
    # Cache for 5 minutes (300 seconds)
    await redis_client.set(cache_key, json.dumps(stats), expire=300)
    cache_logger.info("cache_set", extra={"key": cache_key, "ttl": 300})
    
    return stats
