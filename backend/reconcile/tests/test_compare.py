from datetime import date
from decimal import Decimal as D

from reconcile.cleaning import normalize_ref, parse_amount
from reconcile.compare import compare

L1, L2 = "LOC-101", "LOC-102"
DAY = date(2026, 3, 1)


def a(total="100.00", loc=L1, day=DAY, state="CONFIRMED"):
    return {"total": D(total), "location": loc, "date": day, "state": state}


def b(entry_id, ref="REC-1", value="100.00", loc=L1, day=DAY):
    return {"entry_id": entry_id, "ref": ref, "value": None if value is None else D(value),
            "location": loc, "date": day}


def reasons(result):
    return [r["reason"] for r in result]


def test_clean_row_is_not_flagged():
    assert compare({"REC-1": a()}, [b("E1")]) == []


def test_missing_in_b():
    assert reasons(compare({"REC-1": a()}, [])) == ["MISSING_IN_B"]


def test_orphan_in_b():
    res = compare({"REC-1": a()}, [b("E1"), b("E2", ref="REC-999")])
    assert reasons(res) == ["ORPHAN_IN_B"]
    assert res[0]["entry_ids"] == ["E2"]


def test_duplicate_same_amount_twice_is_flagged():
    res = compare({"REC-1": a()}, [b("E1"), b("E2")])
    assert reasons(res) == ["DUPLICATE_IN_B"]


def test_split_that_sums_is_not_an_error():
    assert compare({"REC-1": a()}, [b("E1", value="40.00"), b("E2", value="60.00")]) == []


def test_split_that_does_not_sum_is_flagged():
    res = compare({"REC-1": a()}, [b("E1", value="40.00"), b("E2", value="50.00")])
    assert reasons(res) == ["DUPLICATE_IN_B"]


def test_value_mismatch():
    res = compare({"REC-1": a()}, [b("E1", value="99.00")])
    assert reasons(res) == ["VALUE_MISMATCH"]
    assert res[0]["a_value"] == D("100.00") and res[0]["b_value"] == D("99.00")


def test_b_equal_to_base_instead_of_total_is_flagged():
    # base 80 + adjustment 20 = total 100; B carrying 80 must be a mismatch
    assert reasons(compare({"REC-1": a("100.00")}, [b("E1", value="80.00")])) == ["VALUE_MISMATCH"]


def test_blank_value_is_flagged_and_not_zero():
    res = compare({"REC-1": a()}, [b("E1", value=None)])
    assert reasons(res) == ["VALUE_MISMATCH"]
    assert res[0]["b_value"] is None


def test_location_mismatch():
    assert reasons(compare({"REC-1": a()}, [b("E1", loc=L2)])) == ["LOCATION_MISMATCH"]


def test_date_mismatch():
    assert reasons(compare({"REC-1": a()}, [b("E1", day=date(2026, 3, 3))])) == ["DATE_MISMATCH"]


def test_voided_without_b_entry_is_expected():
    assert compare({"REC-1": a(state="VOIDED")}, []) == []


def test_voided_with_b_entry_is_flagged():
    assert reasons(compare({"REC-1": a(state="VOIDED")}, [b("E1")])) == ["VOIDED_IN_B"]


def test_entry_pointing_at_other_orgs_record_is_not_an_orphan():
    # org-scoped run: REC-2 is not in a_rows but is known to exist in A
    res = compare({"REC-1": a()}, [b("E1"), b("E2", ref="REC-2")], known_ids={"REC-1", "REC-2"})
    assert res == []


def test_messy_references_match_and_are_not_flagged():
    assert normalize_ref("rec1034") == "REC-1034"
    assert normalize_ref(" REC - 1070 ") == "REC-1070"
    assert normalize_ref("1112") == "REC-1112"
    assert normalize_ref("") is None
    a_rows = {"REC-1034": a(), "REC-1070": a(), "REC-1112": a()}
    b_rows = [b("E1", ref=normalize_ref("rec1034")), b("E2", ref=normalize_ref(" REC - 1070 ")),
              b("E3", ref=normalize_ref("1112"))]
    assert compare(a_rows, b_rows) == []


def test_indian_commas_are_parsed_before_comparing():
    assert parse_amount("1,25,400.00") == D("125400.00")
    assert compare({"REC-1": a("125400.00")}, [b("E1", value=str(parse_amount("1,25,400.00")))]) == []


def test_blank_and_junk_amounts_are_none_not_zero():
    assert parse_amount("") is None and parse_amount("  ") is None and parse_amount("abc") is None
