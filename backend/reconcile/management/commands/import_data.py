from pathlib import Path

from django.core.management.base import BaseCommand

from reconcile.importer import import_all


class Command(BaseCommand):
    help = "Import locations.csv, system_a.csv and system_b.csv (safe to re-run)."

    def add_arguments(self, parser):
        parser.add_argument("--dir", default=str(Path(__file__).resolve().parents[3] / "data"))

    def handle(self, *args, **opts):
        s = import_all(opts["dir"])
        self.stdout.write(
            f"A: {s['a_read']} read, {s['a_saved']} saved; "
            f"B: {s['b_read']} read, {s['b_saved']} saved; "
            f"locations: {s['loc_read']} read, {s['loc_saved']} saved; "
            f"B values left empty: {s['values_left_empty']}; B refs cleaned: {s['refs_cleaned']}; "
            f"A null actor_id: {s['null_actor']}")
