# api_client.py
from __future__ import annotations
import httpx
from typing import Optional, Dict, Any
import asyncio


class BaseAPIClient:
    """Core client that manages HTTPX sync/async clients and shared config."""

    def __init__(
        self,
        base_url: str,
        *,
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 10.0,
        follow_redirects: bool = True,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.follow_redirects = follow_redirects

        self._default_headers = {
            "Accept": "application/json",
            "User-Agent": "MyAPIClient/2.0",
            **(headers or {}),
        }
        if api_key:
            self._default_headers["Authorization"] = f"Bearer {api_key}"

        self._sync_client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None

    # Context managers
    def __enter__(self) -> "BaseAPIClient":
        self._sync_client = httpx.Client(
            base_url=self.base_url,
            headers=self._default_headers,
            timeout=self.timeout,
            follow_redirects=self.follow_redirects,
        )
        return self

    def __exit__(self, *args):
        if self._sync_client:
            self._sync_client.close()

    async def __aenter__(self) -> "BaseAPIClient":
        self._async_client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._default_headers,
            timeout=self.timeout,
            follow_redirects=self.follow_redirects,
        )
        return self

    async def __aexit__(self, *args):
        if self._async_client:
            await self._async_client.aclose()

    # Internal helpers
    def _client(self) -> httpx.Client:
        if not self._sync_client:
            raise RuntimeError("Use 'with client:' for sync methods")
        return self._sync_client

    def _aclient(self) -> httpx.AsyncClient:
        if not self._async_client:
            raise RuntimeError("Use 'async with client:' for async methods")
        return self._async_client

    # Resources will be attached here
    tasks = None  # Will be replaced with TasksResource instance


class TasksResource:
    """Handles /tasks endpoint – both sync and async."""

    def __init__(self, client: BaseAPIClient):
        self._client = client

    # ── Sync methods ─────────────────────────────────────
    def list(
        self, *, status: Optional[str] = None, page: int = 1, limit: int = 50
    ) -> dict:
        params = {"page": page, "limit": limit}
        if status:
            params["status"] = status
        r = self._client._client().get("/tasks", params=params)
        r.raise_for_status()
        return r.json()

    def get(self, task_id: int) -> dict:
        r = self._client._client().get(f"/tasks/{task_id}")
        r.raise_for_status()
        return r.json()

    def create(self, title: str, description: str = "", **extra: Any) -> dict:
        payload = {"title": title, "description": description, **extra}
        r = self._client._client().post("/tasks", json=payload)
        r.raise_for_status()
        return r.json()

    def update(self, task_id: int, **fields: Any) -> dict:
        r = self._client._client().put(f"/tasks/{task_id}", json=fields)
        r.raise_for_status()
        return r.json()

    def delete(self, task_id: int) -> None:
        r = self._client._client().delete(f"/tasks/{task_id}")
        r.raise_for_status()

    # ── Async methods ────────────────────────────────────
    async def alist(
        self, *, status: Optional[str] = None, page: int = 1, limit: int = 50
    ) -> dict:
        params = {"page": page, "limit": limit}
        if status:
            params["status"] = status
        r = await self._client._aclient().get("/tasks", params=params)
        r.raise_for_status()
        return r.json()

    async def aget(self, task_id: int) -> dict:
        r = await self._client._aclient().get(f"/tasks/{task_id}")
        r.raise_for_status()
        return r.json()

    async def acreate(self, title: str, description: str = "", **extra: Any) -> dict:
        payload = {"title": title, "description": description, **extra}
        r = await self._client._aclient().post("/tasks", json=payload)
        r.raise_for_status()
        return r.json()

    async def aupdate(self, task_id: int, **fields: Any) -> dict:
        r = await self._client._aclient().put(f"/tasks/{task_id}", json=fields)
        r.raise_for_status()
        return r.json()

    async def adelete(self, task_id: int) -> None:
        r = await self._client._aclient().delete(f"/tasks/{task_id}")
        r.raise_for_status()


# ── Final client with resources attached ─────────────────────────────
class TaskAPIClient(BaseAPIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Attach resource classes – they all share the same client instance
        self.tasks = TasksResource(self)

        # Easy to add more:
        # self.users = UsersResource(self)
        # self.projects = ProjectsResource(self)


if __name__ == "__main__":
    # Synchronous
    with TaskAPIClient("https://jsonplaceholder.typicode.com") as api:
        tasks = api.tasks.list(limit=3)
        task = api.tasks.get(1)
        new_task = api.tasks.create(title="Learn resource pattern")

    # Asynchronous
    async def main():
        async with TaskAPIClient("https://jsonplaceholder.typicode.com") as api:
            t1, t2, t3 = await asyncio.gather(
                api.tasks.aget(1),
                api.tasks.aget(2),
                api.tasks.aget(3),
            )
            print(t1["title"])

            # Create 20 tasks concurrently
            await asyncio.gather(
                *[api.tasks.acreate(title=f"Bulk task {i}") for i in range(20)]
            )
