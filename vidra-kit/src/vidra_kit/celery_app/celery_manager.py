from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse

import requests
from django.utils import timezone

# from apps.vod.models import ActiveTaskRecord, WorkerStatus, QueueStatus


@dataclass
class QueueInfo:
    name: str
    messages_ready: int
    messages_unacknowledged: int
    messages: int
    consumers: int
    state: str


@dataclass
class BrokerStats:
    queues: List[QueueInfo]
    total_messages: int
    total_consumers: int


@dataclass
class WorkerStats:
    """Structured worker statistics from Celery inspect.stats()."""

    pid: int
    hostname: str
    state: str  # Can be derived from ping or set to 'online'
    active: int  # Concurrency from pool
    processed: int  # Total processed tasks
    cancelled: int
    failed: int
    load: float
    prefetch_count: int
    uptime: int  # In seconds
    pool: str  # Pool implementation
    max_tasks_per_child: Optional[str]
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


def bulk_update_or_create(model, objs, update_fields, match_field):
    match_values = [getattr(o, match_field) for o in objs]

    existing = model.objects.in_bulk(match_values, field_name=match_field)

    to_create = []
    to_update = []

    for obj in objs:
        key = getattr(obj, match_field)
        if key in existing:
            obj.pk = existing[key].pk
            to_update.append(obj)
        else:
            to_create.append(obj)

    if to_create:
        model.objects.bulk_create(to_create)

    if to_update:
        model.objects.bulk_update(to_update, update_fields)


class RabbitMQMonitor:
    """
    RabbitMQ monitor using the management HTTP API.
    Parses the Celery broker URL to extract connection details.
    """

    def __init__(self, broker_url: str):
        parsed = urlparse(broker_url)
        if parsed.scheme not in ("amqp", "amqps"):
            raise ValueError("Broker URL must be an AMQP scheme (amqp:// or amqps://)")

        self.host = parsed.hostname
        self.port = parsed.port or 5672
        self.user = parsed.username or "guest"
        self.password = parsed.password or "guest"
        self.vhost = parsed.path.lstrip("/") or "/"

        # Management API uses HTTP/HTTPS, port 15672/15671 by default
        protocol = "https" if parsed.scheme == "amqps" else "http"
        mgmt_port = 15671 if parsed.scheme == "amqps" else 15672
        self.api_base_url = f"{protocol}://{self.host}:{mgmt_port}/api/"
        self.auth = (self.user, self.password)
        self.session = requests.Session()
        self.session.auth = self.auth

    def _request(self, endpoint: str) -> Dict:
        """Make a request to the management API."""
        url = self.api_base_url + endpoint
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_queue_lengths(self, vhost: Optional[str] = None) -> BrokerStats:
        """
        Fetch queue information for the specified vhost (defaults to broker's vhost).
        Returns structured BrokerStats using dataclass.
        """
        vhost = vhost or self.vhost
        queues_data = self._request(f"queues/{vhost}")

        queues = []
        total_messages = 0
        total_consumers = 0

        for q in queues_data:

            queue_info = QueueInfo(
                name=q["name"],
                messages_ready=q["messages_ready"],
                messages_unacknowledged=q["messages_unacknowledged"],
                messages=q["messages"],
                consumers=q["consumers"],
                state=q["state"],
            )
            queues.append(queue_info)
            total_messages += q["messages"]
            total_consumers += q["consumers"]

        return BrokerStats(
            queues=queues,
            total_messages=total_messages,
            total_consumers=total_consumers,
        )


class CeleryManager:
    """
    Extended Celery manager combining monitoring (inspect) and management (control) capabilities.
    Integrated with Django ORM for persisting statuses and stats.
    Uses RabbitMQ management API for queue lengths via broker URL.
    """

    def __init__(self, app=None):
        self.app = app
        self.inspect = self.app.control.inspect()
        self.control = self.app.control
        self.broker = RabbitMQMonitor(self.app.conf.broker_url)

    # ORM Integration Methods for Updating Statuses
    def _update_worker_status_orm(
        self, hostname: str, stats: WorkerStats, is_active: bool
    ):
        """Update or create WorkerStatus in Django ORM."""
        worker, created = WorkerStatus.objects.update_or_create(
            hostname=hostname,
            defaults={
                "pid": stats.pid,
                "state": stats.state,
                "is_active": is_active,
                "active_concurrency": stats.active,
                "total_processed": stats.processed,
                "total_cancelled": stats.cancelled,
                "total_failed": stats.failed,
                "load_avg": stats.load,
                "prefetch_count": stats.prefetch_count,
                "uptime_seconds": stats.uptime,
                "pool_type": stats.pool,
                "max_tasks_per_child": stats.max_tasks_per_child,
                "max_memory_per_child": stats.max_memory_per_child,
                "last_ping": timezone.now() if is_active else None,
            },
        )
        return worker, created

    def _update_queue_status_orm(self, queues: List[QueueInfo]):
        """Bulk update or create QueueStatus in Django ORM."""
        queue_data = []
        for q in queues:
            queue_data.append(
                {
                    "name": q.name,
                    "messages_ready": q.messages_ready,
                    "messages_unacknowledged": q.messages_unacknowledged,
                    "total_messages": q.messages,
                    "consumers": q.consumers,
                    "state": q.state,
                }
            )
        bulk_update_or_create(
            QueueStatus,
            queue_data,
            update_fields=[
                "messages_ready",
                "messages_unacknowledged",
                "total_messages",
                "consumers",
                "state",
            ],
            match_field="name",
        )

    def _update_active_tasks_orm(self, worker_tasks: Dict[str, List[ActiveTask]]):
        """Update active tasks in Django ORM (upsert)."""
        now = timezone.now()
        for hostname, tasks in worker_tasks.items():
            for task in tasks:
                ActiveTaskRecord.objects.update_or_create(
                    task_id=task.id,
                    defaults={
                        "name": task.name,
                        "args": task.args,
                        "kwargs": task.kwargs,
                        "worker_hostname": hostname,
                        "last_seen": now,
                        "status": "active",
                    },
                )

    # Monitoring methods with ORM updates
    def get_worker_stats(self, update_orm: bool = True) -> Dict[str, WorkerStats]:
        """
        Get detailed statistics for all active workers.
        Optionally updates Django ORM if update_orm=True.
        Returns a dict of hostname -> WorkerStats.
        """
        stats = self.inspect.stats()
        if not stats:
            return {}

        worker_stats = {}
        pings = self.ping_workers()
        for hostname, data in stats.items():
            if data:  # Skip if no data
                total_tasks = data["total"]
                processed = (
                    sum(total_tasks.values())
                    if isinstance(total_tasks, dict)
                    else total_tasks.get("succeeded", 0)
                )
                ws = WorkerStats(
                    pid=data["pid"],
                    hostname=hostname,
                    state="online",  # Default; can be enhanced
                    active=data["pool"]["max-concurrency"],
                    processed=processed,
                    cancelled=total_tasks.get("rejected", 0),
                    failed=total_tasks.get("failed", 0),
                    load=data.get("load", 0.0),
                    prefetch_count=data["prefetch_count"],
                    uptime=data.get("uptime", 0),
                    pool=data["pool"].get("implementation", "prefork"),
                    max_tasks_per_child=data["pool"].get("max-tasks-per-child"),
                    max_memory_per_child=data["pool"].get("max-memory-per-child"),
                )
                worker_stats[hostname] = ws

                if update_orm:
                    is_active = pings.get(hostname, {}).get("ok", False)
                    self._update_worker_status_orm(hostname, ws, is_active)

        return worker_stats

    def ping_workers(self, update_orm: bool = True) -> Dict[str, Dict[str, bool]]:
        """
        Ping all workers to check if they are alive.
        Optionally updates is_active in Django ORM if update_orm=True.
        Returns dict of hostname -> {'ok': True/False}.
        """
        pings = self.inspect.ping()
        if not pings:
            return {}

        result = {hostname: {"ok": bool(data)} for hostname, data in pings.items()}

        if update_orm:
            now = timezone.now()
            for hostname, ping_data in result.items():
                is_active = ping_data["ok"]
                worker = WorkerStatus.objects.filter(hostname=hostname).first()
                if worker:
                    worker.is_active = is_active
                    worker.last_ping = now if is_active else None
                    worker.save(update_fields=["is_active", "last_ping"])

        return result

    def get_active_tasks(self, update_orm: bool = True) -> Dict[str, List[ActiveTask]]:
        """
        Get currently active tasks per worker.
        Optionally updates Django ORM if update_orm=True.
        Returns dict of hostname -> list of ActiveTask.
        """
        active_tasks = self.inspect.active()
        if not active_tasks:
            return {}

        worker_tasks = {}
        if update_orm:
            # First, mark old tasks as inactive if needed (simple cleanup: tasks older than 1 hour)
            ActiveTaskRecord.objects.filter(
                last_seen__lt=timezone.now() - timezone.timedelta(hours=1)
            ).update(status="completed")

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
                if update_orm:
                    self._update_active_tasks_orm({hostname: worker_tasks[hostname]})

        return worker_tasks

    def get_worker_overview(self, update_orm: bool = True) -> List[WorkerInfo]:
        """
        Get a high-level overview of all workers, combining ping and stats.
        Optionally updates Django ORM if update_orm=True.
        Returns list of WorkerInfo.
        """
        if update_orm:
            self.get_worker_stats(update_orm=True)
            self.ping_workers(update_orm=True)

        # Fetch from ORM for overview
        workers = []
        orm_workers = WorkerStatus.objects.all()
        for w in orm_workers:
            workers.append(
                WorkerInfo(
                    hostname=w.hostname,
                    active=w.is_active,
                    stats=(
                        WorkerStats(
                            pid=w.pid,
                            hostname=w.hostname,
                            state=w.state,
                            active=w.active_concurrency,
                            processed=w.total_processed,
                            cancelled=w.total_cancelled,
                            failed=w.total_failed,
                            load=w.load_avg,
                            prefetch_count=w.prefetch_count,
                            uptime=w.uptime_seconds,
                            pool=w.pool_type,
                            max_tasks_per_child=w.max_tasks_per_child,
                            max_memory_per_child=w.max_memory_per_child,
                        )
                        if w.is_active
                        else None
                    ),
                )
            )
        return workers

    def get_active_queues(self, update_orm: bool = True) -> BrokerStats:
        """
        Get active queue stats from RabbitMQ broker.
        Optionally updates Django ORM if update_orm=True.
        """
        queues = self.broker.get_queue_lengths()
        if update_orm:
            self._update_queue_status_orm(queues.queues)
        return queues

    # Management methods using Celery control (unchanged, but can trigger ORM updates post-action)
    def restart_workers(
        self,
        destination: Optional[List[str]] = None,
        reply: bool = True,
        timeout: float = 1.0,
        update_orm_after: bool = True,
    ) -> Optional[Dict]:
        """
        Restart the execution pools of worker(s).
        Optionally updates ORM after action if update_orm_after=True.
        """
        result = self.control.pool_restart(
            destination=destination, reply=reply, timeout=timeout
        )
        if update_orm_after:
            self.ping_workers(update_orm=True)  # Update statuses post-restart
        return result

    def shutdown_workers(
        self,
        destination: Optional[List[str]] = None,
        reply: bool = True,
        timeout: float = 1.0,
        update_orm_after: bool = True,
    ) -> Optional[Dict]:
        """
        Gracefully shut down worker(s).
        Optionally updates ORM after action if update_orm_after=True.
        """
        result = self.control.shutdown(
            destination=destination, reply=reply, timeout=timeout
        )
        if update_orm_after:
            self.ping_workers(update_orm=True)  # Mark as inactive
        return result

    # ... (other management methods remain unchanged; add update_orm_after param similarly if needed)

    def subscribe_queue(
        self,
        queue: str,
        exchange: Optional[str] = None,
        exchange_type: str = "direct",
        routing_key: Optional[str] = None,
        options: Optional[Dict] = None,
        destination: Optional[List[str]] = None,
        reply: bool = True,
        timeout: float = 1.0,
    ) -> Optional[Dict]:
        """
        Tell workers to start consuming from a new queue (subscribe).
        """
        return self.control.add_consumer(
            queue=queue,
            exchange=exchange,
            exchange_type=exchange_type,
            routing_key=routing_key,
            options=options,
            destination=destination,
            reply=reply,
            timeout=timeout,
        )

    def unsubscribe_queue(
        self,
        queue: str,
        destination: Optional[List[str]] = None,
        reply: bool = True,
        timeout: float = 1.0,
    ) -> Optional[Dict]:
        """
        Stop workers from consuming from a specified queue (unsubscribe).
        """
        return self.control.cancel_consumer(
            queue=queue, destination=destination, reply=reply, timeout=timeout
        )

    def autoscale_workers(
        self,
        min_workers: int,
        max_workers: int,
        destination: Optional[List[str]] = None,
        reply: bool = True,
        timeout: float = 1.0,
    ) -> Optional[Dict]:
        """
        Change autoscale settings for worker(s) (min/max workers).
        """
        return self.control.autoscale(
            max=max_workers,
            min=min_workers,
            destination=destination,
            reply=reply,
            timeout=timeout,
        )

    def grow_pool(
        self,
        n: int = 1,
        destination: Optional[List[str]] = None,
        reply: bool = True,
        timeout: float = 1.0,
    ) -> Optional[Dict]:
        """
        Increase worker pool size by n processes/threads.
        """
        return self.control.pool_grow(
            n=n, destination=destination, reply=reply, timeout=timeout
        )

    def shrink_pool(
        self,
        n: int = 1,
        destination: Optional[List[str]] = None,
        reply: bool = True,
        timeout: float = 1.0,
    ) -> Optional[Dict]:
        """
        Decrease worker pool size by n processes/threads.
        """
        return self.control.pool_shrink(
            n=n, destination=destination, reply=reply, timeout=timeout
        )

    def revoke_task(
        self,
        task_id: Union[str, List[str]],
        terminate: bool = False,
        signal: str = "SIGTERM",
        destination: Optional[List[str]] = None,
        reply: bool = True,
        timeout: float = 1.0,
    ) -> Optional[Dict]:
        """
        Revoke a task by ID (or list of IDs). If terminate=True, kills the task process.
        """
        result = self.control.revoke(
            task_id=task_id,
            terminate=terminate,
            signal=signal,
            destination=destination,
            reply=reply,
            timeout=timeout,
        )
        # Update ORM for revoked task
        if isinstance(task_id, str):
            ActiveTaskRecord.objects.filter(task_id=task_id).update(status="revoked")
        elif isinstance(task_id, list):
            ActiveTaskRecord.objects.filter(task_id__in=task_id).update(
                status="revoked"
            )
        return result

    def set_rate_limit(
        self,
        task_name: str,
        rate_limit: Union[int, str],
        destination: Optional[List[str]] = None,
        reply: bool = True,
        timeout: float = 1.0,
    ) -> Optional[Dict]:
        """
        Set a new rate limit for a task type (e.g., 100 or '100/m').
        """
        return self.control.rate_limit(
            task_name=task_name,
            rate_limit=rate_limit,
            destination=destination,
            reply=reply,
            timeout=timeout,
        )

    def enable_events(
        self,
        destination: Optional[List[str]] = None,
        reply: bool = True,
        timeout: float = 1.0,
    ) -> Optional[Dict]:
        """
        Enable event reporting on workers.
        """
        return self.control.enable_events(
            destination=destination, reply=reply, timeout=timeout
        )

    def disable_events(
        self,
        destination: Optional[List[str]] = None,
        reply: bool = True,
        timeout: float = 1.0,
    ) -> Optional[Dict]:
        """
        Disable event reporting on workers.
        """
        return self.control.disable_events(
            destination=destination, reply=reply, timeout=timeout
        )

    def purge_tasks(self, connection=None) -> int:
        """
        Discard all waiting tasks from all queues.
        """
        purged = self.control.purge(connection=connection)
        # Optionally clear queue statuses in ORM
        QueueStatus.objects.update(
            total_messages=0, messages_ready=0, messages_unacknowledged=0
        )
        return purged
