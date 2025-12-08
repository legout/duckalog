"""Background task management for dashboard operations."""

from __future__ import annotations

import asyncio
import datetime as _dt
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

from .state import DashboardContext


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BackgroundTask:
    """Represents a background task."""

    id: str
    task_type: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: _dt.datetime = field(default_factory=lambda: _dt.datetime.now(_dt.timezone.utc))
    started_at: Optional[_dt.datetime] = None
    completed_at: Optional[_dt.datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: float = 0.0  # 0.0 to 1.0

    @property
    def duration_seconds(self) -> Optional[float]:
        """Get task duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (_dt.datetime.now(_dt.timezone.utc) - self.started_at).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "task_type": self.task_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "progress": self.progress,
            "error": self.error,
            "has_result": self.result is not None,
        }


class TaskManager:
    """Manages background tasks for the dashboard."""

    def __init__(self, context: DashboardContext):
        self.context = context
        self.tasks: Dict[str, BackgroundTask] = {}
        self._lock = asyncio.Lock()

    def create_task(self, task_type: str) -> str:
        """Create a new background task and return its ID."""
        task_id = str(uuid.uuid4())
        task = BackgroundTask(id=task_id, task_type=task_type)
        self.tasks[task_id] = task
        return task_id

    async def run_catalog_build(self, task_id: str) -> None:
        """Run catalog build as a background task."""
        async with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return

            task.status = TaskStatus.RUNNING
            task.started_at = _dt.datetime.now(_dt.timezone.utc)
            task.progress = 0.1

        try:
            # Update progress
            async with self._lock:
                task = self.tasks.get(task_id)
                if task:
                    task.progress = 0.5

            # Run the actual build
            build_result = self.context.trigger_build()

            async with self._lock:
                task = self.tasks.get(task_id)
                if task:
                    task.status = TaskStatus.COMPLETED if build_result.success else TaskStatus.FAILED
                    task.completed_at = _dt.datetime.now(_dt.timezone.utc)
                    task.progress = 1.0
                    task.result = build_result
                    if not build_result.success:
                        task.error = build_result.message

        except Exception as e:
            async with self._lock:
                task = self.tasks.get(task_id)
                if task:
                    task.status = TaskStatus.FAILED
                    task.completed_at = _dt.datetime.now(_dt.timezone.utc)
                    task.progress = 1.0
                    task.error = str(e)

    def get_task(self, task_id: str) -> Optional[BackgroundTask]:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def get_tasks_by_type(self, task_type: str) -> list[BackgroundTask]:
        """Get all tasks of a specific type."""
        return [task for task in self.tasks.values() if task.task_type == task_type]

    def get_recent_tasks(self, limit: int = 10) -> list[BackgroundTask]:
        """Get the most recent tasks."""
        return sorted(
            self.tasks.values(),
            key=lambda t: t.created_at,
            reverse=True
        )[:limit]

    def cleanup_old_tasks(self, max_age_hours: int = 24) -> int:
        """Remove old tasks and return count of removed tasks."""
        cutoff_time = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=max_age_hours)
        old_task_ids = [
            task_id for task_id, task in self.tasks.items()
            if task.created_at < cutoff_time and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
        ]

        for task_id in old_task_ids:
            del self.tasks[task_id]

        return len(old_task_ids)


# Global task manager instance (will be initialized per dashboard context)
_task_managers: Dict[str, TaskManager] = {}


def get_task_manager(context: DashboardContext) -> TaskManager:
    """Get or create a task manager for a given context."""
    # Use the config path as a unique key for the context
    context_key = str(context.config_path) or "in-memory"

    if context_key not in _task_managers:
        _task_managers[context_key] = TaskManager(context)

    return _task_managers[context_key]


__all__ = [
    "BackgroundTask",
    "TaskManager",
    "TaskStatus",
    "get_task_manager",
]