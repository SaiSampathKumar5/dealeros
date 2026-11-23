from rest_framework.decorators import api_view
from rest_framework.response import Response

from .compare import REASONS
from .models import Location
from .services import disagreements_for_org


def _num(v):
    return None if v is None else str(v)


@api_view(["GET"])
def disagreements(request):
    org = request.query_params.get("org")
    if not org or not Location.objects.filter(org_id=org).exists():
        return Response({"error": "org is required and must be a known org, e.g. ORG-A"}, status=400)
    reason = request.query_params.get("reason")
    if reason and reason not in REASONS:
        return Response({"error": f"unknown reason; use one of {REASONS}"}, status=400)
    rows = disagreements_for_org(org)
    if reason:
        rows = [r for r in rows if r["reason"] == reason]

    sort = request.query_params.get("sort", "")
    if sort.lstrip("-") == "value":
        key = lambda r: r["a_value"] if r["a_value"] is not None else r["b_value"]
        has = [r for r in rows if key(r) is not None]
        none = [r for r in rows if key(r) is None]  # unknown values always last
        rows = sorted(has, key=key, reverse=sort.startswith("-")) + none
    else:
        rows = sorted(rows, key=lambda r: (r["reason"], r["record_id"]))

    return Response([{
        "reason": r["reason"], "record_id": r["record_id"],
        "location": r["a_location"] or r["b_location"],
        "b_location": r["b_location"],
        "a_value": _num(r["a_value"]), "b_value": _num(r["b_value"]),
        "difference": _num(r["b_value"] - r["a_value"]) if r["a_value"] is not None and r["b_value"] is not None else None,
        "cross_org": r.get("cross_org", False),
    } for r in rows])
