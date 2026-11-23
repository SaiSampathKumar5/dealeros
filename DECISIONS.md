# Decisions

## Decision: compare B's value with A's total_value
-Rejected: compare with base_value
-Why: B equals A's total_value (base + adjustment) on almost every row I checked; a test pins this (B carrying the base is flagged).

## Decision: blank B value is null and flagged as VALUE_MISMATCH, never 0
-Rejected: treating blank as 0 (would hide a real unknown, or invent a difference)
-Why: blank means unknown. The importer stores null plus the original text in `value_raw`; the UI shows an empty cell.

## Decision: clean references by taking the digits and rebuilding `REC-<digits>`
-Rejected: exact string match on `record_ref`
-Why: `rec1034`, ` REC - 1070 ` and `1112` are the same record. The raw text is kept in `record_ref_raw`.

## Decision: several B entries are DUPLICATE_IN_B only if their sum differs from A's total
-Rejected: flag every record with two entries
-Why: REC-1055 is a split ("part 2 of 2") that sums exactly to A's total, so it is fine. REC-1042 is the same amount twice (sum is double A's total), so it is flagged.

## Decision: a VOIDED A record with no B entry is expected; with a B entry it is flagged as VOIDED_IN_B (extra reason)
-Rejected: flagging it as MISSING_IN_B, or ignoring a B entry that exists for a voided record
-Why: B should not still carry something A voided. I added a separate reason so it is not confused with the four required ones.

## Decision: date and location differences are extra reasons (DATE_MISMATCH, LOCATION_MISMATCH)
-Rejected: ignoring them
-Why: they are real disagreements between the systems. They are reported alongside, not instead of, a value check.

## Decision: tenant = org of A's location; filtering happens in the DB query
-Rejected: filtering in React, or guessing the org from the LOC-1xx/2xx pattern
-Why: only locations.csv defines ownership. Orphans use B's own location. Every API call needs `?org=`.

## Decision: cross-org row (REC-1077: A at LOC-102/ORG-A, B at LOC-201/ORG-B)
-Rejected: showing "A says LOC-102, B says LOC-201" to ORG-A, or showing the row to ORG-B
-Why: ORG-A sees the row (its record is affected) but B's location and value are blanked and marked as hidden. ORG-B does not see it. Weak spot: ORG-B gets no signal about its own entry.

## Decision: SQLite, DecimalField, nullable location FKs with the raw text kept
-Rejected: float, a foreign key from B to A
-Why: money must compare exactly; an orphan B entry would break an FK to A. Nothing needs a bigger database here.
