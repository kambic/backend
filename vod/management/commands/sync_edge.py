from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from vidra_kit.backends.api import EdgewareApi

from ...models import Edge, Stream


class Command(BaseCommand):
    help = "Sync a single Edge + its Streams from API JSON"
    edge_rows = []
    stream_rows = []

    def add_arguments(self, parser):
        parser.add_argument("--one",  action="store_true", default=False, help="Sync only one page Edge")

    def handle(self, one, *args, **options):
        offset = Edge.objects.all().count()
        offset = 0
        edgeware = EdgewareApi(offset)


        while edgeware.has_next_page:
            self.stdout.write(self.style.WARNING(f"Fetching: {edgeware.OFFSET}"))

            data = edgeware.next_page()
            for row in data:
                idd = row["content_id"]
                obj = Edge.objects.filter(content_id=idd)
                if obj.exists():
                    self.update_row(obj.get(),row)
                else:

                    self.add_row(row)

            Edge.objects.bulk_create(
                self.edge_rows,
            )
            Stream.objects.bulk_create(
                self.stream_rows,
            )
            self.edge_rows.clear()
            self.stream_rows.clear()

            if one:
                break
    def update_row(self,obj,row):
        obj.content_duration = self._get_duration(row)
        obj.save()

    def add_row(self, raw):

        # ---------------------------
        # MAP API → Edge model fields
        # ---------------------------
        edge_data = {
            "content_id": raw["content_id"],
            "title": raw.get("title"),
            "status": raw.get("state"),  # maps to Edge.Status
            "playable": raw.get("playable", False),
            "content_duration": self._get_duration(raw),
            "creation_time": parse_datetime(raw.get("creation_time")),
            "modification_time": parse_datetime(raw.get("modification_time")),
        }
        content = raw.get("content_id")
        if Edge.objects.filter(content_id=content).exists():
            self.stdout.write(self.style.WARNING(f"Skipping: {content}"))
            return

        # ---------------------------
        # UPSERT Edge
        # ---------------------------
        edge = Edge(
            **edge_data,
        )
        self.edge_rows.append(edge)

        # ---------------------------
        # UPSERT Stream children
        # ---------------------------
        delivery = raw.get("delivery_uris", {})

        for protocol, uri in delivery.items():
            if protocol not in ["hls", "dash", "mss"]:
                continue  # ignore unrecognized protocols

            stream = Stream(edge=edge, stream_protocol=protocol, uri=uri)
            self.stream_rows.append(stream)

    def _get_duration(self, raw) -> int | None:
        try:
            ms_ = int(raw["content_duration_ms"])
            return int(ms_ / 1000)
        except:
            return 0
