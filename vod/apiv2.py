# api_client.py
import asyncio

import httpx
from typing import Optional, Dict, Any


class APIClient:
    def __init__(
        self, base_url: str, *, api_key: Optional[str] = None, timeout: float = 10.0
    ):
        self.base_url = base_url.rstrip("/")
        headers = {"Accept": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self._sync = None
        self._async = None
        self._cfg = dict(base_url=self.base_url, headers=headers, timeout=timeout)

    def __enter__(self):
        self._sync = httpx.Client(**self._cfg)
        return self

    def __exit__(self, *a):
        self._sync.close()

    async def __aenter__(self):
        self._async = httpx.AsyncClient(**self._cfg)
        return self

    async def __aexit__(self, *a):
        await self._async.aclose()

    # Helper
    def _req(self, method: str, path: str, **kwargs):
        return getattr(self._sync or self._async, method)(path, **kwargs)


class Resource:
    def __init__(self, client: APIClient, path: str):
        self.client = client
        self.path = path

    def _call(self, method: str, id: Any = None, **kwargs):
        path = f"{self.path}/{id}" if id else self.path
        return self.client._req(method, path, **kwargs)

    # Sync
    def list(self, **kw):
        return self._call("get", **kw).raise_for_status().json()

    def get(self, id):
        return self._call("get", id).raise_for_status().json()

    def create(self, **data):
        return self._call("post", json=data).raise_for_status().json()

    def update(self, id, **d):
        return self._call("put", id, json=d).raise_for_status().json()

    def delete(self, id):
        return self._call("delete", id).raise_for_status()

    # Async
    async def alist(self, **kw):
        r = self._call("get", **kw)
        return (await r).raise_for_status().json()

    async def aget(self, id):
        r = self._call("get", id)
        return (await r).raise_for_status().json()

    async def acreate(self, **data):
        r = self._call("post", json=data)
        return (await r).raise_for_status().json()

    async def aupdate(self, id, **d):
        r = self._call("put", id, json=d)
        return (await r).raise_for_status().json()

    async def adelete(self, id):
        r = self._call("delete", id)
        await r.raise_for_status()


# Final client with resources
class TaskAPIClient(APIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasks = Resource(self, "/tasks")
        # Add more: self.users = Resource(self, "/users")


if __name__ == "__main__":
    # Sync
    with TaskAPIClient("https://jsonplaceholder.typicode.com") as api:
        api.tasks.create(title="Hello")
        print(api.tasks.get(1)["title"])

    # Async
    async def main():
        async with TaskAPIClient("https://jsonplaceholder.typicode.com") as api:
            await asyncio.gather(
                api.tasks.acreate(title="A"),
                api.tasks.acreate(title="B"),
            )
            print(await api.tasks.alist(limit=5))

    asyncio.run(main())
