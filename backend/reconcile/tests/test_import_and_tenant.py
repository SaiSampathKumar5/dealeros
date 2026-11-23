from pathlib import Path

import pytest
from rest_framework.test import APIClient

from reconcile.importer import import_all
from reconcile.models import SystemARecord, SystemBEntry

DATA = Path(__file__).resolve().parents[2] / "data"
pytestmark = pytest.mark.django_db


def get(org, **params):
    resp = APIClient().get("/api/disagreements/", {"org": org, **params})
    assert resp.status_code == 200
    return resp.json()


def test_import_keeps_every_row_and_is_idempotent():
    s = import_all(DATA)
    assert (s["a_read"], s["a_saved"], s["b_read"], s["b_saved"]) == (120, 120, 121, 121)
    import_all(DATA)
    assert SystemARecord.objects.count() == 120 and SystemBEntry.objects.count() == 121
    assert SystemBEntry.objects.filter(value__isnull=True).count() == 1  # blank kept as null
    assert SystemARecord.objects.filter(actor_id__isnull=True).count() == 1


def test_expected_disagreements_on_real_data():
    import_all(DATA)
    found = {(r["reason"], r["record_id"]) for org in ("ORG-A", "ORG-B") for r in get(org)}
    assert ("MISSING_IN_B", "REC-1015") in found
    assert ("MISSING_IN_B", "REC-1061") in found
    assert ("DUPLICATE_IN_B", "REC-1042") in found
    assert ("VALUE_MISMATCH", "REC-1050") in found
    assert not any(rid == "REC-1055" for _, rid in found)  # split that sums is fine


def test_tenant_isolation_both_ways():
    import_all(DATA)
    for org, other in (("ORG-A", "LOC-2"), ("ORG-B", "LOC-1")):
        rows = get(org)
        assert rows
        for r in rows:
            assert not (r["location"] or "").startswith(other)
            assert not (r["b_location"] or "").startswith(other)


def test_cross_org_row_hides_other_orgs_side():
    import_all(DATA)
    row = next(r for r in get("ORG-A") if r["record_id"] == "REC-1077")
    assert row["location"] == "LOC-102" and row["b_location"] is None and row["b_value"] is None
    assert all(r["record_id"] != "REC-1077" for r in get("ORG-B"))


def test_org_is_required():
    assert APIClient().get("/api/disagreements/").status_code == 400
