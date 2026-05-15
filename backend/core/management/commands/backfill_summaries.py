from django.core.management.base import BaseCommand

from core.models import Statement

from core.tasks import regenerate_summary_task


class Command(BaseCommand):

    help = "Backfill all country-event summaries"

    def handle(self, *args, **kwargs):

        pairs = (
            Statement.objects
            .values_list('country_id', 'event_id')
            .distinct()
        )

        total = len(pairs)

        self.stdout.write(
            self.style.SUCCESS(
                f"Found {total} unique pairs"
            )
        )

        for idx, (country_id, event_id) in enumerate(pairs, start=1):

            regenerate_summary_task.delay(
                country_id,
                event_id
            )

            self.stdout.write(
                f"[{idx}/{total}] queued"
            )

        self.stdout.write(
            self.style.SUCCESS(
                "All summaries queued"
            )
        )
