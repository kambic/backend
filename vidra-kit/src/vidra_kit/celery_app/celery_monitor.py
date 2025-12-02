from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any

import redis
from celery import current_app

from vidra_kit.backends.api import RabbitMQMonitor
from vidra_kit.celery_app import app
from vidra_kit.celery_app.celery_manager import BrokerStats


@dataclass
class WorkerStatus:
    """Dataclass for worker status: liveness, active tasks, and basic stats."""

    name: str
    is_alive: bool = False
    active_tasks_count: int = 0
    processed_tasks: int = 0  # From stats
    uptime: Optional[str] = None  # e.g., "1h 23m"
    # Optional: active task names (list)
    active_tasks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dict for JSON serialization."""
        return asdict(self)


@dataclass
class WorkerStats:
    """Structured worker statistics from Celery inspect.stats()."""

    pid: int
    hostname: str
    state: str
    active: int
    processed: int
    cancelled: int
    failed: int
    load: float
    prefetch_count: int
    uptime: str
    pool: str
    max_tasks_per_child: Optional[int]
    max_memory_per_child: Optional[int]


@dataclass
class ActiveTask:
    """Structured active task information."""

    id: str
    name: str
    args: List[Any]
    kwargs: Dict[str, Any]
    worker: str
    hostname: str


@dataclass
class WorkerInfo:
    """Overview of worker health and status."""

    hostname: str
    active: bool  # From ping
    stats: Optional[WorkerStats]


@dataclass
class QueueInfo:
    """Dataclass for queue info: name and enqueued task count."""

    name: str
    length: int = 0

    def to_dict(self) -> Dict:
        """Convert to dict for JSON serialization."""
        return asdict(self)


class CeleryMonitor:
    """
    Enhanced Celery monitor with dataclasses for structured results.
    Assumes Redis broker for queue lengths.
    """

    def __init__(self, app=None):
        self.app = app or current_app
        self.inspect = self.app.control.inspect()
        self.redis_client = redis.Redis(decode_responses=False, db=1)
        # self.broker = RabbitMQMonitor(self.app.conf.broker_url)

    def get_workers_status(self) -> List[WorkerStatus]:
        """
        Get status for all workers as a list of WorkerStatus dataclasses.
        Combines ping, active tasks, and stats.
        """
        pings = self.inspect.ping() or {}
        actives = self.inspect.active() or {}
        stats = self.inspect.stats() or {}

        workers = []
        for worker_name in set(
            list(pings.keys()) + list(actives.keys()) + list(stats.keys())
        ):
            worker_stats = stats.get(worker_name, {})
            uptime = worker_stats.get("pool", {}).get("uptime")  # Simplified uptime
            processed = (
                worker_stats.get("total", {}).get("tasks", {}).get("completed", 0)
            )

            active_tasks = [
                task.get("name", "unknown") for task in actives.get(worker_name, [])
            ]

            workers.append(
                WorkerStatus(
                    name=worker_name,
                    is_alive=pings.get(worker_name, {}).get("ok") == "pong",
                    active_tasks_count=len(active_tasks),
                    processed_tasks=processed,
                    uptime=uptime,
                    active_tasks=active_tasks,
                )
            )
        return workers

    def get_queue_infos(self, queues: Optional[List[str]] = None) -> List[QueueInfo]:
        """
        Get queue lengths as a list of QueueInfo dataclasses.
        """
        if queues is None:
            queues = (
                list(self.app.conf.task_queues.keys())
                if self.app.conf.task_queues
                else ["celery"]
            )
        # return queues
        infos = []
        for queue in queues:
            length = self.redis_client.llen(queue)
            infos.append(QueueInfo(name=queue, length=length))
        return infos

    def get_active_tasks(self):
        actives = self.inspect.active() or {}


class CeleryMonitora:
    """
    Enhanced Celery monitor with dataclasses for structured results.
    Monitors workers using Celery's inspect API.
    Uses RabbitMQ management API for queue lengths via broker URL.
    """

    def __init__(self, app=None):
        self.app = app or current_app
        self.inspect = self.app.control.inspect()
        self.broker = RabbitMQMonitor(self.app.conf.broker_url)

    def get_worker_stats(self) -> Dict[str, WorkerStats]:
        """
        Get detailed statistics for all active workers.
        Returns a dict of hostname -> WorkerStats.
        """
        stats = self.inspect.stats()
        if not stats:
            return {}

        worker_stats = {}
        for hostname, data in stats.items():
            if data:  # Skip if no data
                worker_stats[hostname] = WorkerStats(
                    pid=data["pid"],
                    hostname=hostname,
                    state=data["state"],
                    active=data["pool"]["max-concurrency"] or data.get("active", 0),
                    processed=data["total"]["tasks"],
                    cancelled=data["total"].get("cancelled", 0),
                    failed=data["total"].get("failed", 0),
                    load=data["load"],
                    prefetch_count=data["prefetch_count"],
                    uptime=data["pool"]["max-concurrency"]
                    or "N/A",  # Simplified; adjust as needed
                    pool=data["pool"]["name"],
                    max_tasks_per_child=data["pool"].get("max_tasks_per_child"),
                    max_memory_per_child=data["pool"].get("max_memory_per_child"),
                )
        return worker_stats

    def ping_workers(self) -> Dict[str, Dict[str, bool]]:
        """
        Ping all workers to check if they are alive.
        Returns dict of hostname -> {'ok': True/False}.
        """
        pings = self.inspect.ping()
        if not pings:
            return {}
        return {hostname: {"ok": bool(data)} for hostname, data in pings.items()}

    def get_active_tasks(self) -> Dict[str, List[ActiveTask]]:
        """
        Get currently active tasks per worker.
        Returns dict of hostname -> list of ActiveTask.
        """
        active_tasks = self.inspect.active()
        if not active_tasks:
            return {}

        worker_tasks = {}
        for hostname, tasks in active_tasks.items():
            if tasks:
                worker_tasks[hostname] = [
                    ActiveTask(
                        id=task["id"],
                        name=task["name"],
                        args=task["args"],
                        kwargs=task["kwargs"],
                        worker=task["worker"],
                        hostname=hostname,
                    )
                    for task in tasks
                ]
        return worker_tasks

    def get_worker_overview(self) -> List[WorkerInfo]:
        """
        Get a high-level overview of all workers, combining ping and stats.
        Returns list of WorkerInfo.
        """
        pings = self.ping_workers()
        stats = self.get_worker_stats()

        workers = []
        all_hostnames = set(pings.keys()) | set(stats.keys())
        for hostname in all_hostnames:
            ping_ok = pings.get(hostname, {}).get("ok", False)
            worker_stat = stats.get(hostname)
            workers.append(
                WorkerInfo(hostname=hostname, active=ping_ok, stats=worker_stat)
            )
        return workers

    def get_active_queues(self) -> BrokerStats:
        """Get active queue stats from RabbitMQ broker (unchanged)."""
        return self.broker.get_queue_lengths()


# Example usage function (enhanced with dataclasses)
def monitor_celery_summary():
    monitor = CeleryMonitor(app=app)
    workers = monitor.get_workers_status()
    queues = monitor.get_queue_infos()

    print("=== Workers ===")
    for w in workers:
        status = "Alive" if w.is_alive else "Dead"
        print(
            f"{w.name}: {status} | Active: {w.active_tasks_count} | Processed: {w.processed_tasks} | Uptime: {w.uptime}"
        )

    print("\n=== Queues ===")
    for q in queues:
        print(f"{q}: tasks")

    # Example: Serialize to JSON-like dict
    summary = {
        "workers": [w.to_dict() for w in workers],
        "queues": [q.to_dict() for q in queues],
    }
    print("\n=== JSON Summary ===", summary)

monitor_celery_summary()
