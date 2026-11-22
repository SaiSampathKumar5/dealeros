"""Comparison rules. Plain Python: no database, no web code.

a_rows: {record_id: {'total', 'location', 'date', 'state'}}
b_rows: [{'entry_id', 'ref', 'value', 'location', 'date'}]   (ref already cleaned)
known_ids: every record_id that exists in A for ANY org (ids only, no data).
           Lets a tenant-scoped run tell a real orphan from an entry that
           points at another org's record. Defaults to a_rows' keys.
Each result: dict(reason, record_id, a_location, b_location, a_value, b_value, entry_ids)
"""
from decimal import Decimal

MISSING_IN_B = "MISSING_IN_B"
ORPHAN_IN_B = "ORPHAN_IN_B"
DUPLICATE_IN_B = "DUPLICATE_IN_B"
VALUE_MISMATCH = "VALUE_MISMATCH"
LOCATION_MISMATCH = "LOCATION_MISMATCH"
DATE_MISMATCH = "DATE_MISMATCH"
VOIDED_IN_B = "VOIDED_IN_B"

REASONS = [MISSING_IN_B, ORPHAN_IN_B, DUPLICATE_IN_B, VALUE_MISMATCH,
           LOCATION_MISMATCH, DATE_MISMATCH, VOIDED_IN_B]


def _row(reason, rid, a, entries, b_value):
    return {
        "reason": reason,
        "record_id": rid,
        "a_location": a["location"] if a else None,
        "b_location": entries[0]["location"] if entries else None,
        "a_value": a["total"] if a else None,
        "b_value": b_value,
        "entry_ids": [e["entry_id"] for e in entries],
    }


def compare(a_rows, b_rows, known_ids=None):
    known_ids = set(a_rows) if known_ids is None else set(known_ids)
    by_ref = {}
    for e in b_rows:
        by_ref.setdefault(e["ref"], []).append(e)

    out = []
    for ref, entries in by_ref.items():
        if ref not in known_ids:  # no A record anywhere (ref may also be None)
            for e in entries:
                out.append(_row(ORPHAN_IN_B, ref or e["entry_id"], None, [e], e["value"]))

    for rid, a in a_rows.items():
        entries = by_ref.get(rid, [])
        voided = a.get("state") == "VOIDED"
        if not entries:
            if not voided:  # a voided record is expected to have no B entry
                out.append(_row(MISSING_IN_B, rid, a, [], None))
            continue
        vals = [e["value"] for e in entries]
        total_b = None if any(v is None for v in vals) else sum(vals, Decimal("0"))
        if voided:
            out.append(_row(VOIDED_IN_B, rid, a, entries, total_b))
            continue
        if total_b is None:  # blank is unknown, never 0
            out.append(_row(VALUE_MISMATCH, rid, a, entries, None))
            continue
        if len(entries) > 1:
            if total_b != a["total"]:  # a split that adds up is fine
                out.append(_row(DUPLICATE_IN_B, rid, a, entries, total_b))
            continue
        e = entries[0]
        if e["value"] != a["total"]:
            out.append(_row(VALUE_MISMATCH, rid, a, entries, e["value"]))
        if e["location"] != a["location"]:
            out.append(_row(LOCATION_MISMATCH, rid, a, entries, e["value"]))
        if e["date"] != a["date"]:
            out.append(_row(DATE_MISMATCH, rid, a, entries, e["value"]))
    return out
