from django.core.management.base import BaseCommand
from core.models import Statement
from core.services.embedding_service import embed_statement


class Command(BaseCommand):
    help = 'Generate and store embeddings for all Statement objects'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-embed even if chunks already exist'
        )

    def handle(self, *args, **options):
        force = options['force']

        if force:
            statements = Statement.objects.all()
        else:
            # Only embed statements that have no chunks yet
            statements = (
                Statement.objects
                .filter(chunks__isnull=True)
                .distinct()
            )

        total = statements.count()
        self.stdout.write(f"Embedding {total} statements...")

        for i, statement in enumerate(statements, 1):
            self.stdout.write(f"[{i}/{total}] Statement ID {statement.id}")
            count = embed_statement(statement)
            self.stdout.write(
                self.style.SUCCESS(
                    f"  → {count} chunks created"
                )
            )

        self.stdout.write(self.style.SUCCESS("Done! All statements embedded."))
