# prod-killer

An internal post-mortem tracker for when someone breaks production.
Document the incident, name the culprit, and let the leaderboard do the rest.

> Built as a team culture / shame-driven accountability tool. No auth required — it's internal.

---

## Features

- **Incident log** — title, description, how it was discovered, how it was resolved, who helped, relevant links
- **User profiles** — name, team, optional nickname, automatic incident counter
- **Funny titles** — engineers earn progressively worse titles as their incident count grows (from _Production Guardian_ to _The Nuclear Option_)
- **Leaderboards** — monthly and yearly rankings with HTMX tab switching
- **Stats** — bar chart of incidents over time, breakdowns by user and team
- **Achievement popup** — a random roast message slides in every time an incident is filed

---

## Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI + SQLAlchemy |
| Database | SQLite (single file, no setup) |
| Frontend | Jinja2 templates + HTMX + Chart.js |
| Runtime | Python 3.12 |

---

## Quickstart

### Docker (recommended)

```bash
docker compose up
```

Open http://localhost:8742

### Local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p data
uvicorn app.main:app --reload
```

Open http://localhost:8000

---

## Pages

| Route | Description |
|---|---|
| `/` | Dashboard — recent incidents + stats snapshot |
| `/incidents` | Full incident history |
| `/incidents/new` | Log a new incident |
| `/users` | Add and view users + their titles |
| `/leaderboard` | Monthly / yearly shame rankings |
| `/stats` | Time series chart + per-user and per-team breakdowns |

---

## Funny Titles

| Incidents | Title |
|---|---|
| 0 | Production Guardian |
| 1 | Baby Production Assassin |
| 2 | Junior Outage Engineer |
| 3 | Certified Production Menace |
| 4 | Professional Chaos Agent |
| 5 | Senior Chaos Architect |
| 6 | Principal Disruption Engineer |
| 7–8 | Staff Apocalypse Engineer |
| 9–12 | Legendary Production Destroyer |
| 13–19 | Living Legend of Broken Prod |
| 20+ | The Nuclear Option |

---

## Data

SQLite database at `data/prod_killer.db`, persisted via Docker volume mount.
To reset: delete the file and restart.
