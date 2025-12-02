# vidra_kit/celery_manager.py
from __future__ import annotations

import time
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import requests
from celery import Celery, current_app


# ----------------------------------------------------------------------
# Shared Data Structures (JSON-serializable)
# ----------------------------------------------------------------------
@dataclass
class QueueInfo:
    name: str
    messages_ready: int = 0
    messages_unacknowledged: int = 0
    messages: int = 0
    consumers: int = 0
    state: str = "running"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BrokerStats:
    queues: List[QueueInfo] = field(default_factory=list)
    total_messages: int = 0
    total_consumers: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "queues": [q.to_dict() for q in self.queues],
            "total_messages": self.total_messages,
            "total_consumers": self.total_consumers,
        }


@dataclass
class WorkerStats:
    pid: int
    hostname: str
    active: int
    processed: int
    failed: int = 0
    cancelled: int = 0
    load: float = 0.0
    prefetch_count: int = 0
    uptime_seconds: int = 0
    pool_type: str = "prefork"
    max_tasks_per_child: Optional[int] = None
    max_memory_per_child: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ActiveTask:
    id: str
    name: str
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    worker: str = ""
    hostname: str = ""
    time_start: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkerStatus:
    hostname: str
    is_alive: bool = False
    active_tasks_count: int = 0
    processed_tasks: int = 0
    stats: Optional[WorkerStats] = None
    active_tasks: List[ActiveTask] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hostname": self.hostname,
            "is_alive": self.is_alive,
            "active_tasks_count": self.active_tasks_count,
            "processed_tasks": self.processed_tasks,
            "stats": self.stats.to_dict() if self.stats else None,
            "active_tasks": [t.to_dict() for t in self.active_tasks],
        }


# ----------------------------------------------------------------------
# RabbitMQ Management API (lightweight, no Django)
# ----------------------------------------------------------------------
class RabbitMQMonitor:
    def __init__(self, broker_url: str):
        parsed = urlparse(broker_url)
        if parsed.scheme not in {"amqp", "amqps"}:
            raise ValueError("Broker URL must be amqp:// or amqps://")

        self.host = parsed.hostname or "localhost"
        self.port = parsed.port or 5672
        self.user = parsed.username or "guest"
        self.password = parsed.password or "guest"
        self.vhost = parsed.path.lstrip("/") or "/"

        protocol = "https" if parsed.scheme == "amqps" else "http"
        mgmt_port = 15671 if parsed.scheme == "amqps" else 15672
        self.base_url = f"{protocol}://{self.host}:{mgmt_port}/api/"
        self.session = requests.Session()
        self.session.auth = (self.user, self.password)

    def _get(self, endpoint: str) -> Any:
        url = self.base_url + endpoint
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_queue_lengths(self, vhost: Optional[str] = None) -> BrokerStats:
        vhost = vhost or self.vhost
        data = self._get(f"queues/{vhost}")

        queues: List[QueueInfo] = []
        total_msg = total_con = 0

        for q in data:
            qi = QueueInfo(
                name=q["name"],
                messages_ready=q.get("messages_ready", 0),
                messages_unacknowledged=q.get("messages_unacknowledged", 0),
                messages=q.get("messages", 0),
                consumers=q.get("consumers", 0),
                state=q.get("state", "running"),
            )
            queues.append(qi)
            total_msg += qi.messages
            total_con += qi.consumers

        return BrokerStats(
            queues=queues,
            total_messages=total_msg,
            total_consumers=total_con,
        )


# ----------------------------------------------------------------------
# Main CeleryManager (No Django, pure Python)
# ----------------------------------------------------------------------
class CeleryManager:
    """
    Unified Celery monitor + manager for non-Django environments.
    Use in vidra-kit, CLI tools, FastAPI, monitoring services, etc.
    """

    def __init__(self, app: Optional[Celery] = None):
        self.app = app or current_app
        if not self.app:
            raise ValueError("Celery app must be provided or available as current_app")

        self.inspect = self.app.control.inspect()
        self.control = self.app.control
        self.broker = self.create_broker_monitor(self.app.conf.broker_url)

    def create_broker_monitor(self, broker_url: str):
        if broker_url.startswith(("amqp", "amqps")):
            from vidra_kit.backends.api import RabbitMQMonitor
            return RabbitMQMonitor(broker_url)
        else:
            from .redis_monitor import RedisMonitor
            return RedisMonitor(broker_url)
    # ------------------------------------------------------------------
    # Core Monitoring
    # ------------------------------------------------------------------
    def get_workers(self) -> List[WorkerStatus]:
        """Get full status of all workers (alive + stats + active tasks)."""
        ping_data = self.inspect.ping() or {}
        stats_data = self.inspect.stats() or {}
        active_data = self.inspect.active() or {}

        all_hostnames = set(ping_data.keys()) | set(stats_data.keys()) | set(active_data.keys())
        workers: List[WorkerStatus] = []

        for hostname in all_hostnames:
            is_alive = ping_data.get(hostname, {}).get("ok") == "pong"
            stats = stats_data.get(hostname, {})
            active_tasks_raw = active_data.get(hostname, [])

            # Parse stats
            pool = stats.get("pool", {})
            total = stats.get("total", {})

            processed = 0
            failed = 0
            if isinstance(total, dict):
                processed = sum(v for k, v in total.items() if k not in ("failed", "rejected"))
                failed = total.get("failed", 0)

            worker_stats = None
            if stats:
                worker_stats = WorkerStats(
                    pid=stats.get("pid", 0),
                    hostname=hostname,
                    active=pool.get("max-concurrency", 0),
                    processed=processed,
                    failed=failed,
                    cancelled=total.get("rejected", 0),
                    load=stats.get("loadaverage", 0.0),
                    prefetch_count=stats.get("prefetch_count", 0),
                    uptime_seconds=int(stats.get("uptime", 0)),
                    pool_type=pool.get("name", "prefork"),
                    max_tasks_per_child=pool.get("max-tasks-per-child"),
                    max_memory_per_child=pool.get("max-memory-per-child"),
                )

            # Parse active tasks
            active_tasks = [
                ActiveTask(
                    id=t["id"],
                    name=t["name"],
                    args=t.get("args", []),
                    kwargs=t.get("kwargs", {}),
                    worker=t.get("worker", hostname),
                    hostname=hostname,
                    time_start=t.get("time_start"),
                )
                for t in active_tasks_raw
            ]

            workers.append(
                WorkerStatus(
                    hostname=hostname,
                    is_alive=is_alive,
                    active_tasks_count=len(active_tasks),
                    processed_tasks=processed,
                    stats=worker_stats,
                    active_tasks=active_tasks,
                )
            )

        return workers

    def get_queues(self) -> BrokerStats:
        """Get accurate queue stats via RabbitMQ Management API."""
        return self.broker.get_queue_lengths()

    def get_summary(self) -> Dict[str, Any]:
        """High-level health summary (ideal for APIs or dashboards)."""
        workers = self.get_workers()
        queues = self.get_queues()

        return {
            "timestamp": time.time(),
            "workers": {
                "total": len(workers),
                "alive": sum(1 for w in workers if w.is_alive),
                "dead": sum(1 for w in workers if not w.is_alive),
                "active_tasks": sum(w.active_tasks_count for w in workers),
                "total_processed": sum(w.processed_tasks for w in workers if w.processed_tasks),
            },
            "queues": queues.to_dict(),
            "workers_detail": [w.to_dict() for w in workers],
        }

    # ------------------------------------------------------------------
    # Management Actions
    # ------------------------------------------------------------------
    def restart_workers(self, destination: Optional[List[str]] = None) -> Dict:
        result = self.control.pool_restart(destination=destination, reply=True, timeout=10)
        time.sleep(2)
        return {"action": "pool_restart", "result": result}

    def shutdown_workers(self, destination: Optional[List[str]] = None) -> Dict:
        result = self.control.shutdown(destination=destination, reply=True, timeout=10)
        time.sleep(1)
        return {"action": "shutdown", "result": result}

    def grow_pool(self, n: int = 1, destination: Optional[List[str]] = None) -> Dict:
        return {"action": "pool_grow", "result": self.control.pool_grow(n=n, destination=destination)}

    def shrink_pool(self, n: int = 1, destination: Optional[List[str]] = None) -> Dict:
        return {"action": "pool_shrink", "result": self.control.pool_shrink(n=n, destination=destination)}

    def revoke_task(self, task_id: Union[str, List[str]], terminate: bool = False) -> Dict:
        result = self.control.revoke(task_id, terminate=terminate, reply=True)
        return {"action": "revoke", "task_id": task_id, "result": result}

    def purge_queues(self) -> int:
        """Purge all tasks from all queues."""
        return self.app.control.purge()

    def enable_events(self):
        self.control.enable_events()

    def disable_events(self):
        self.control.disable_events()


# ----------------------------------------------------------------------
# Convenience function
# ----------------------------------------------------------------------
def get_celery_manager(app: Optional[Celery] = None) -> CeleryManager:
    """Helper to get manager instance (useful in scripts)."""
    return CeleryManager(app=app)
