# DealerOS reconciliation (Django + React)

Finds rows where System A and System B disagree, per org, without leaking across orgs.

## Run it (from a clean clone)
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd backend
python manage.py makemigrations reconcile   # commit the generated migration
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
(Write this yourself: which agent, what you asked, what you wrote, how you checked it.)

## The three answers (write these yourself, from your own session)
a. One thing the AI agent got wrong:
b. The part I am least confident about:
c. If I had a second day:
