"""Glue between the database and the pure compare() function. Tenant scoping lives here."""
from .compare import compare
from .models import Location, SystemARecord, SystemBEntry

REDACTED = None


def disagreements_for_org(org):
    """All disagreement rows ORG `org` is allowed to see. Filtering happens in the DB queries."""
    org_locs = Location.objects.filter(org_id=org)
    a_qs = SystemARecord.objects.filter(location__in=org_locs)
    a_rows = {
        a.record_id: {"total": a.total_value, "location": a.location_raw,
                      "date": a.event_date, "state": a.state}
        for a in a_qs}
    # B entries: those pointing at this org's A records, plus this org's own B entries (orphans).
    from django.db.models import Q
    b_qs = SystemBEntry.objects.filter(Q(record_ref__in=list(a_rows)) | Q(location__in=org_locs))
    b_rows = [{"entry_id": e.entry_id, "ref": e.record_ref, "value": e.value,
               "location": e.location_raw, "date": e.recorded_on} for e in b_qs]
    # Ids only (no data) so an entry pointing at another org's record is not called an orphan.
    known = set(SystemARecord.objects.values_list("record_id", flat=True))
    rows = compare(a_rows, b_rows, known_ids=known)

    mine = set(org_locs.values_list("location_id", flat=True))
    out = []
    for r in rows:
        if r["a_location"] is not None and r["a_location"] not in mine:
            continue  # defensive: never emit a row whose A side is another org's
        if r["a_location"] is None and r["b_location"] not in mine:
            continue  # orphan belongs to B's own org
        if r["b_location"] is not None and r["b_location"] not in mine:
            # Cross-org row: keep it for the org that owns A, hide everything from B's side.
            r = dict(r, b_location=REDACTED, b_value=REDACTED, entry_ids=[])
            r["cross_org"] = True
        out.append(r)
    return out
