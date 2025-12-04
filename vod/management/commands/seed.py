from django.core.management.base import BaseCommand
from faker import Faker
from django.utils.text import slugify
from django.utils import timezone
import random

from ...models import Provider, Edge, Stream, Worker

from zoneinfo import ZoneInfo

LJUBLJANA_TZ = ZoneInfo("Europe/Ljubljana")

faker = Faker("sl_SI")  # Slovenian locale


class Command(BaseCommand):
    help = "Seed the database with Providers, Edges, Streams and Workers (Slovenian locale)"

    def add_arguments(self, parser):
        parser.add_argument("--providers", type=int, default=10)
        parser.add_argument("--edges", type=int, default=30)
        parser.add_argument("--workers", type=int, default=5)

    # -------------------------------------------------------------------------
    # PROVIDER
    # -------------------------------------------------------------------------
    def create_provider(self):
        name = faker.unique.company()
        vidra_task = faker.unique.word()
        queue = faker.unique.word()

        provider = Provider.objects.create(
            name=name,
            slug=slugify(name),
            active=faker.boolean(),
            vidra_task=vidra_task,
            queue=queue,
        )
        return provider

    # -------------------------------------------------------------------------
    # EDGE
    # -------------------------------------------------------------------------
    def create_edge(self, provider: Provider):
        title = faker.sentence(nb_words=4)
        creation = faker.date_time_between(start_date="-2y", end_date="now", tzinfo=LJUBLJANA_TZ)
        modification = faker.date_time_between(start_date=creation, end_date="now", tzinfo=LJUBLJANA_TZ)

        edge = Edge.objects.create(
            content_id=faker.unique.uuid4(),
            title=title,
            creation_time=creation,
            modification_time=modification,
            status=random.choice(["error", "done"]),
            playable=faker.boolean(),
            content_duration_ms=random.randint(5_000, 5_000_000),
            provider=provider,
            expiry_date=faker.date_time_between(start_date="-1y", end_date="+1y", tzinfo=LJUBLJANA_TZ),
            offer_id=faker.unique.bothify("OF-####-????"),
        )
        return edge

    # -------------------------------------------------------------------------
    # STREAM
    # -------------------------------------------------------------------------
    def create_streams_for_edge(self, edge: Edge):
        protocols = ["hls", "dash", "mss"]
        random.shuffle(protocols)

        count = random.randint(1, 3)
        for proto in protocols[:count]:
            Stream.objects.create(
                edge=edge,
                stream_protocol=proto,
                uri=faker.url(),
            )

    # -------------------------------------------------------------------------
    # WORKER
    # -------------------------------------------------------------------------
    def create_worker(self):
        Worker.objects.create(
            name=faker.unique.first_name() + "-worker",
            status=random.choice(["running", "idle", "offline"]),
            last_heartbeat=faker.date_time_between(start_date="-3h", end_date="now", tzinfo=LJUBLJANA_TZ),
            is_alive=faker.boolean(),
            active_tasks=[faker.word() for _ in range(random.randint(0, 3))],
        )

    # -------------------------------------------------------------------------
    # HANDLE
    # -------------------------------------------------------------------------
    def handle(self, *args, **opts):
        providers_count = opts["providers"]
        edges_count = opts["edges"]
        workers_count = opts["workers"]

        self.stdout.write(self.style.NOTICE("Seeding Slovenian test data…"))

        # Providers
        providers = [self.create_provider() for _ in range(providers_count)]
        self.stdout.write(self.style.SUCCESS(f"✔ Created {providers_count} providers"))

        # Edges + Streams
        for _ in range(edges_count):
            provider = random.choice(providers)
            edge = self.create_edge(provider)
            self.create_streams_for_edge(edge)
        self.stdout.write(self.style.SUCCESS(f"✔ Created {edges_count} edges + streams"))

        # Workers
        for _ in range(workers_count):
            self.create_worker()
        self.stdout.write(self.style.SUCCESS(f"✔ Created {workers_count} workers"))

        self.stdout.write(self.style.SUCCESS("🎉 Seeding complete!"))
