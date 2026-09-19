from django.core.management.base import BaseCommand, CommandError

from apps.marketplace.retention import enforce_marketplace_analytics_retention


class Command(BaseCommand):
    help = "Delete marketplace analytics events older than the approved 90-day pilot window."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--batch-size", type=int, default=500)

    def handle(self, *args, **options):
        try:
            result = enforce_marketplace_analytics_retention(
                dry_run=options["dry_run"],
                batch_size=options["batch_size"],
            )
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(f"RETENTION_DRY_RUN={'YES' if result.dry_run else 'NO'}")
        self.stdout.write(f"RETENTION_ELIGIBLE={result.eligible}")
        self.stdout.write(f"RETENTION_PROCESSED={result.processed}")
        self.stdout.write(f"RETENTION_BATCHES={result.batches}")
        self.stdout.write("RETENTION_STRATEGY=DELETE")
