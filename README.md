# DealerOS reconciliation (Django + React)

Finds rows where System A and System B disagree, per org, without leaking across orgs.

## Run it (from a clean clone)
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd backend
python manage.py migrate
python manage.py import_data          # safe to run twice; prints read/saved counts
python manage.py runserver            # API at http://127.0.0.1:8000/api/disagreements/?org=ORG-A
# new terminal
cd frontend && npm install && npm run dev
# tests (from backend/)
pytest
```

## What I built
Importer (nothing dropped; bad values become null with raw text kept), a pure `compare()` function,
one API endpoint (`org`, `reason`, `sort=value|-value`), and a plain React table.
Expected result on the supplied data: 12 rows (see `reconcile/tests`).

## What I deliberately did not build
Auth, pagination, Docker, CSS, extra filters.

## How I worked with the agent
I used Claude (Sonnet 5.5). I gave it the assignment brief and the three CSV files and asked it to build the importer, the comparison rules, the API, a simple React table and the tests. It first read the CSVs and listed the problems: messy references, the blank and 1,25,400.00 values, the orphan, the split, the duplicate, the voided record and the cross-org row. I ran everything myself on my PC: the importer twice (120 A and 121 B rows both times), the tests, and the API for both orgs. I checked the API output against the CSV rows and confirmed that ORG-A never shows LOC-2xx locations and ORG-B never shows LOC-1xx. I made the Git commits step by step myself and fixed the errors that came up.

## The three answers (write these yourself, from your own session)
a. One thing the AI agent got wrong: The agent's settings.py left out django.contrib.auth and STATIC_URL. Running pytest gave 4 failed and 18 passed, with an error about Permission not being in INSTALLED_APPS. After I fixed that, runserver crashed with a missing STATIC_URL error. I added both settings and all 22 tests passed.
b. The part I am least confident about:The cross-org row, REC-1077. A is at LOC-102 (ORG-A) and B is at LOC-201 (ORG-B). I show it only to ORG-A with B's location and value hidden, and ORG-B sees nothing. I'm unsure ORG-B should get no signal about its own B entry. I would ask the reviewers what the business rule is, and check with a test that no ORG-B detail ever reaches ORG-A in any field.
c. If I had a second day:I would decide what ORG-B should see for REC-1077, for example an "unmatched entry" row that shows only its own entry and not ORG-A's data. This comes first because it is the one place where the tenant rules and the reconciliation result are in conflict.
