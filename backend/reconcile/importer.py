"""CSV -> database. Every CSV row becomes one DB row; bad fields become null."""
import csv
from pathlib import Path

from .cleaning import normalize_ref, parse_amount, parse_date
from .models import Location, SystemARecord, SystemBEntry


def _rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            yield {k.strip(): (v or "").strip() for k, v in row.items()}


def import_all(data_dir):
    d = Path(data_dir)
    s = dict(loc_read=0, loc_saved=0, a_read=0, a_saved=0, b_read=0, b_saved=0,
             values_left_empty=0, refs_cleaned=0, null_actor=0)

    for r in _rows(d / "locations.csv"):
        s["loc_read"] += 1
        Location.objects.update_or_create(
            location_id=r["location_id"],
            defaults={"org_id": r["org_id"], "name": r.get("location_name", "")})
        s["loc_saved"] += 1
    locs = {l.location_id: l for l in Location.objects.all()}

    for r in _rows(d / "system_a.csv"):
        s["a_read"] += 1
        if not r["actor_id"]:
            s["null_actor"] += 1
        SystemARecord.objects.update_or_create(
            record_id=r["record_id"],
            defaults={
                "location": locs.get(r["location_id"]), "location_raw": r["location_id"],
                "event_date": parse_date(r["event_date"]),
                "category_code": r["category_code"],
                "actor_id": r["actor_id"] or None,
                "base_value": parse_amount(r["base_value"]),
                "adjustment": parse_amount(r["adjustment"]),
                "total_value": parse_amount(r["total_value"]),
                "state": r["state"].upper(),
            })
        s["a_saved"] += 1

    for r in _rows(d / "system_b.csv"):
        s["b_read"] += 1
        ref = normalize_ref(r["record_ref"])
        if ref != r["record_ref"]:
            s["refs_cleaned"] += 1
        value = parse_amount(r["value"])
        if value is None:
            s["values_left_empty"] += 1
        SystemBEntry.objects.update_or_create(
            entry_id=r["entry_id"],
            defaults={
                "record_ref_raw": r["record_ref"], "record_ref": ref,
                "location": locs.get(r["location_id"]), "location_raw": r["location_id"],
                "recorded_on": parse_date(r["recorded_on"]),
                "value_raw": r["value"], "value": value, "label": r["label"],
            })
        s["b_saved"] += 1
    return s
