# prod-killer

Internal post-mortem tracker. Document who broke production, when, and how badly.

## Stack

- **Backend**: FastAPI + SQLAlchemy
- **Database**: SQLite
- **Frontend**: Jinja2 + HTMX + Chart.js
- **Runtime**: Python 3.12

## Run with Docker (recommended)

```bash
docker compose up
```

Open http://localhost:8000

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p data
uvicorn app.main:app --reload
```

Open http://localhost:8000

## Pages

| Route | Description |
|---|---|
| `/` | Dashboard — recent incidents, stats |
| `/incidents` | All incidents |
| `/incidents/new` | Log a new incident |
| `/users` | Manage users |
| `/leaderboard` | Monthly / yearly rankings |
| `/stats` | Charts and team breakdowns |

## Data

SQLite database stored at `data/prod_killer.db`. Persisted via Docker volume mount.
To reset: delete the file and restart.
