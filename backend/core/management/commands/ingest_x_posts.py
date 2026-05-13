from django.core.management.base import BaseCommand

from core.ingestion.twitter_ingestion import (
    fetch_posts,
    save_posts,
)

from core.models import Country


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        country = Country.objects.get(isoa2_code="IN")

        # posts = fetch_posts("MEAIndia", since_date="2022-02-01", until_date="2026-04-28")
        posts = fetch_posts("MEAIndia", since_date="2026-01-01")

        save_posts(posts, country, "MEAIndia")

        self.stdout.write(
            self.style.SUCCESS("Posts ingested")
        )
