from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse, parse_qs

import redis


@dataclass
class RedisQueueInfo:
    name: str
    length: int = 0
    consumers: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RedisBrokerStats:
    queues: List[RedisQueueInfo]
    total_messages: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "queues": [q.to_dict() for q in self.queues],
            "total_messages": self.total_messages,
        }


class RedisMonitor:
    """
    Simple Redis monitor for Celery (when using Redis as broker).
    Provides queue lengths using LLEN — accurate and fast.
    Works with redis://, rediss://, sentinel://, and redis+socket:// URLs.
    """

    def __init__(self, broker_url: str):
        self.broker_url = broker_url
        self.client = self._create_client(broker_url)

    def _create_client(self, broker_url: str) -> redis.Redis:
        """Create a redis-py client supporting common URL schemes."""
        parsed = urlparse(broker_url)

        if parsed.scheme == "redis+socket":
            # Unix socket: redis+socket:///path/to/socket?db=0
            socket_path = parsed.path

            # FIX: Correctly parse query params for 'db'
            query_params = parse_qs(parsed.query)
            db = int(query_params.get("db", ["0"])[0])

            # decode_responses=False is generally safer when dealing with raw keys and lengths
            return redis.Redis(unix_socket_path=socket_path, db=db, decode_responses=False)

        if parsed.scheme == "sentinel":
            # sentinel://:password@host:port/0/service_name
            from redis.sentinel import Sentinel

            password = parsed.password or None
            # Default Sentinel port is 26379
            hosts = [(parsed.hostname, parsed.port or 26379)]
            service_name = parsed.path.lstrip("/") or "mymaster"
            sentinel = Sentinel(hosts, socket_timeout=0.1, password=password)
            return sentinel.master_for(service_name)

        # Standard redis:// or rediss://
        kwargs = {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 6379,
            "password": parsed.password,
            # DB is often the path part of the URL (e.g., redis://host:port/1)
            "db": int(parsed.path.lstrip("/") or 0),
            "ssl": parsed.scheme == "rediss",
            "socket_timeout": 5.0,
            "socket_connect_timeout": 5.0,
        }
        # print(kwargs) # Removed print statements
        # print(broker_url) # Removed print statements
        # decode_responses=False is generally safer when dealing with raw keys and lengths
        return redis.Redis(decode_responses=False, **kwargs)

    def get_queue_lengths(
            self,
            queue_names: Optional[List[str]] = None,
            prefix: str = "celery",
    ) -> RedisBrokerStats:
        """
        Get queue lengths for Celery queues in Redis.

        Args:
            queue_names: Explicit list of queue names (e.g. ['celery', 'high-priority'])
            prefix: Auto-discover queues starting with this prefix (default: 'celery')

        Returns:
            RedisBrokerStats with accurate message counts
        """
        keys_to_check: List[str] = []

        if queue_names:
            # When explicit names are given, only check those
            keys_to_check = queue_names
        else:
            # Safer auto-discovery using SCAN_ITER instead of KEYS
            pattern = f"*{prefix}*" if "*" not in prefix else prefix
            try:
                # scan_iter yields bytes keys, so we decode them
                keys_iter = self.client.scan_iter(match=pattern)
                # Decode keys from bytes to string
                keys_to_check = [k.decode() for k in keys_iter]
            except Exception:
                # Fallback to the most common default name if connection fails
                keys_to_check = [prefix]

        # Ensure we check at least the default queue name if nothing was discovered
        if not keys_to_check:
            keys_to_check = [prefix]

        queues: List[RedisQueueInfo] = []
        total_messages = 0

        # Use a pipeline for efficient batch retrieval of TYPE and LLEN commands
        with self.client.pipeline() as pipe:
            for q_name in keys_to_check:
                # print(q_name) # Removed print statements
                # Step 1: Check the key TYPE
                pipe.type(q_name)

            # Execute all TYPE commands
            types = pipe.execute()

            # Step 2: Use a second pipeline for LLEN only on keys that are lists
            llen_pipe = self.client.pipeline()
            # Store the names of the keys we actually ran LLEN on
            list_keys: List[str] = []

            for q_name, key_type_bytes in zip(keys_to_check, types):
                # Check if the key type is 'list' (returned as b'list' when decode_responses=False)
                # The _kombu.binding keys that caused the error will be type 'set' (b'set')
                if key_type_bytes == b'list':
                    llen_pipe.llen(q_name)
                    list_keys.append(q_name)

            # Execute all LLEN commands for the list keys
            lengths = llen_pipe.execute()

        # Combine results from the LLEN pipeline
        for name, length in zip(list_keys, lengths):
            # LLEN returns the length (int) or None/Error if the key does not exist (not a list, etc.)
            # Due to the type check, we mostly expect an int length.
            length = int(length) if length is not None else 0

            # Only report queues that exist (length > 0) or are explicitly requested
            if length > 0 or name in (queue_names or [prefix]):
                queues.append(RedisQueueInfo(name=name, length=length))
                total_messages += length

        # Final check: remove duplicates and ensure only one instance of the default queue is present
        seen_names = set()
        unique_queues = []
        for q in queues:
            if q.name not in seen_names:
                seen_names.add(q.name)
                unique_queues.append(q)

        return RedisBrokerStats(queues=unique_queues, total_messages=total_messages)

    def ping(self) -> bool:
        """Test Redis connectivity."""
        try:
            self.client.ping()
            return True
        except Exception:
            return False


# ----------------------------------------------------------------------
# Convenience function
# ----------------------------------------------------------------------
def get_redis_monitor(broker_url: str) -> RedisMonitor:
    return RedisMonitor(broker_url)
