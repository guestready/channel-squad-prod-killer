# prod-killer

An internal post-mortem tracker for when someone breaks production.
Document the incident, name the culprit, and let the leaderboard do the rest.

> Built as a team culture / shame-driven accountability tool.

---

## Features

- **Incident log** — title, description, how it was discovered, how it was resolved, who helped, relevant links
- **Incident editing** — full edit and delete support for any logged incident
- **User profiles** — name, team, optional nickname, automatic incident counter
- **User management** — create, edit, and delete users (deletion blocked if they have incidents)
- **Funny titles** — engineers earn progressively worse titles as their incident count grows
- **Epitaphs** — a random personalized roast shown on every incident detail page
- **Leaderboards** — monthly, yearly, and all-time rankings for individuals and teams, with HTMX tab switching
- **Stats** — time-series bar chart of incidents, breakdowns by user and team
- **Password auth** — simple single-password gate, session-based

---

## Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI + SQLAlchemy |
| Database | SQLite (single file, no setup) |
| Frontend | Jinja2 templates + HTMX + Chart.js |
| Runtime | Python 3.12 |
| Auth | Starlette `SessionMiddleware` + single shared password |

---

## Quickstart

### Docker (recommended)

Copy the example env file and fill in your values:

```bash
cp .env.example .env
# edit .env — set APP_PASSWORD and SECRET_KEY
```

Then start:

```bash
docker compose up
```

Open http://localhost:8742

### Local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env
mkdir -p data
uvicorn app.main:app --reload
```

Open http://localhost:8000

---

## Configuration

All config is via environment variables (or a `.env` file in the project root).

| Variable | Required | Description |
|---|---|---|
| `APP_PASSWORD` | Yes | Password to access the app |
| `SECRET_KEY` | Yes | Secret for signing session cookies. Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `SEED_DATA` | No | Set to `true` to seed the database with 100 test incidents on first startup |

---

## Pages

| Route | Description |
|---|---|
| `/login` | Password login |
| `/` | Dashboard — recent incidents + stats snapshot |
| `/incidents` | Full incident history with filters |
| `/incidents/new` | Log a new incident |
| `/incidents/{id}` | Incident detail with epitaph |
| `/incidents/{id}/edit` | Edit an existing incident |
| `/users` | Add and view users with their titles |
| `/users/{id}/edit` | Edit a user |
| `/leaderboard` | Monthly / yearly / all-time shame rankings |
| `/stats` | Time-series chart + per-user and per-team breakdowns |

---

## Funny Titles

### Individual

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
| 20–29 | The Nuclear Option |
| 30–39 | Extinction-Level Engineer |
| 40–49 | Distinguished Fellow of Catastrophe |
| 50–74 | Chaos Emeritus |
| 75–99 | Grand Architect of Downtime |
| 100–149 | Immortal Destroyer of SLAs |
| 150–199 | The One Who Must Not Deploy |
| 200+ | Production's Final Boss |

### Team

| Team Incidents | Title |
|---|---|
| 0–2 | Mostly Harmless |
| 3–5 | Known Troublemakers |
| 6–10 | Certified Chaos Unit |
| 11–20 | Elite Destruction Division |
| 21–30 | Most Killer Team |
| 31–50 | The Architects of Doom |
| 51–75 | Unstoppable Force of Nature |
| 76–100 | Designated Disaster Response Team |
| 101–150 | The Scorched Earth Division |
| 151–200 | Hall of Flame |
| 200+ | The Final Incident |

---

## Data

SQLite database at `data/prod_killer.db`, persisted via Docker volume mount.
To reset: delete the file and restart.

Setting `SEED_DATA=true` seeds 100 incidents across 10 users on first startup (only runs on an empty database).
