import logging
import time
from queue import Queue, Empty
from threading import Event, Thread

from celery import Celery
from celery.events import EventReceiver
from celery.events.state import State

from vidra_kit.celery_app.config.base import BaseConfig
from vidra_kit import logger

logger.setLevel(logging.INFO)


state = State(
    max_tasks_in_memory=BaseConfig.max_tasks,
    max_workers_in_memory=BaseConfig.max_workers,
)

IMPORTANT_EVENTS = {
    "task-received",
    "task-started",
    "task-succeeded",
    "task-failed",
    "task-retried",
    "worker-online",
    "worker-offline",
}


class EventProcessor(Thread):
    def __init__(self, queue: Queue, stop_signal: Event):
        super().__init__(daemon=True)
        self.queue = queue
        self.stop_signal = stop_signal

    def run(self):
        logger.info("Event processor started")
        while not self.stop_signal.is_set():
            try:
                event = self.queue.get(timeout=1)
                self.process_event(event)
                self.queue.task_done()
            except Empty:
                continue
            except Exception:
                logger.exception("Failed processing event")

    def process_event(self, event: dict):
        logger.info(f"Processing event {event['type']}")


class CeleryEventReceiver(Thread):
    """Thread for consuming events from a Celery cluster."""

    def __init__(self, app: Celery, processor=None):
        super().__init__()
        self.app = app
        self._stop_signal = Event()
        self.queue = Queue(maxsize=10_000)
        self.receiver = None
        if processor:
            self.processor = processor(self.queue, self._stop_signal)
        else:
            self.processor = EventProcessor(self.queue, self._stop_signal)

    def run(self):
        self.processor.start()
        logger.info("Starting event consumer...")
        while not self._stop_signal.is_set():
            try:
                self.consume_events()
            except Exception:
                logger.exception("Consumer crashed, retrying")
                time.sleep(10)

    def on_event(self, event: dict) -> None:
        state.event(event)
        try:
            self.queue.put(event, timeout=1)
            logger.debug("Event queued")
        except Exception:
            logger.warning("Queue full, dropping event")

    def stop(self) -> None:
        logger.info("Stopping consumer...")
        if self.receiver:
            self.receiver.should_stop = True
        self._stop_signal.set()
        self.join()

    def consume_events(self):
        logger.info("Connecting to celery cluster...")
        with self.app.connection() as connection:
            handlers = {event_type: self.on_event for event_type in IMPORTANT_EVENTS}
            self.receiver = EventReceiver(
                channel=connection,
                app=self.app,
                handlers=handlers,
            )
            logger.info("Starting to consume events...")
            self.receiver.capture(limit=None, timeout=None, wakeup=True)


if __name__ == "__main__":
    from vidra_kit.celery_app import get_celery_app

    app = get_celery_app("production")
    receiver = CeleryEventReceiver(app)
    receiver.start()
