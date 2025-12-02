from vidra_kit.celery_app import app
from vidra_kit.celery_app.celery_manager import CeleryManager

manager = CeleryManager(app)

# For API, dashboard, or monitoring
summary = manager.get_summary()
print(summary)

# # Management
# manager.grow_pool(n=4)
# manager.revoke_task("abc123")
# manager.purge_queues()
