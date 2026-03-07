import calendar
import json
import random
from datetime import datetime

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import crud, models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")


def get_funny_title(count: int) -> str:
    if count == 0:
        return "Production Guardian"
    if count == 1:
        return "Baby Production Assassin"
    if count == 2:
        return "Junior Outage Engineer"
    if count == 3:
        return "Certified Production Menace"
    if count == 4:
        return "Professional Chaos Agent"
    if count == 5:
        return "Senior Chaos Architect"
    if count == 6:
        return "Principal Disruption Engineer"
    if count <= 8:
        return "Staff Apocalypse Engineer"
    if count <= 12:
        return "Legendary Production Destroyer"
    if count <= 19:
        return "Living Legend of Broken Prod"
    return "The Nuclear Option"



_INCIDENT_EPITAPHS = [
    "{name} cried till their sleep that night.",
    "{name} has never been the same since.",
    "Sources say {name} blamed it on a cosmic ray.",
    "{name} quietly pushed a fix and hoped nobody noticed.",
    "{name} updated their resume that afternoon.",
    "{name} stared at the ceiling for three hours after this.",
    "{name} considered a career change. Briefly.",
    "The on-call team still has nightmares because of {name}.",
    "{name} told their therapist about this one.",
    "{name} briefly considered becoming a goat farmer.",
    "Legend has it {name} is still googling the error.",
    "{name} blamed it on DNS. It was not DNS.",
    "{name} discovered that rm -rf does exactly what it says.",
    "After this, {name}'s rubber duck quit.",
    "{name} insisted it worked on their machine.",
    "{name} opened an incognito window and pretended it wasn't them.",
    "{name} has since developed a strong opinion on feature flags.",
    "This was the day {name} finally read the documentation.",
    "{name} swore to write tests. They did not write tests.",
    "The Slack thread from that day is still pinned as a warning.",
    "{name} refreshed the dashboard 47 times hoping it would fix itself.",
    "{name} learned what 'idempotent' means the hard way.",
    "Nobody spoke to {name} for the rest of the sprint.",
    "{name} started every sentence that week with 'in hindsight...'",
    "{name} is now legally required to have a buddy when deploying.",
]


def get_incident_epitaph(name: str) -> str:
    return random.choice(_INCIDENT_EPITAPHS).format(name=name)


def get_funny_team_title(count: int) -> str:
    if count <= 2:
        return "Mostly Harmless"
    if count <= 5:
        return "Known Troublemakers"
    if count <= 10:
        return "Certified Chaos Unit"
    if count <= 20:
        return "Elite Destruction Division"
    if count <= 30:
        return "Most Killer Team"
    return "The Architects of Doom"


templates.env.globals["get_funny_title"] = get_funny_title
templates.env.globals["get_funny_team_title"] = get_funny_team_title


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    recent = crud.get_incidents(db, limit=8)
    total = crud.count_incidents(db)
    this_month = crud.count_incidents_this_month(db)
    this_year = crud.count_incidents_this_year(db)
    teams = crud.count_teams(db)
    monthly_lb = crud.get_monthly_leaderboard(db, now.year, now.month)
    top_offender = monthly_lb[0] if monthly_lb else None

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "recent_incidents": recent,
            "total": total,
            "this_month": this_month,
            "this_year": this_year,
            "teams": teams,
            "top_offender": top_offender,
        },
    )


# ── Incidents ─────────────────────────────────────────────────────────────────

@app.get("/incidents", response_class=HTMLResponse)
async def incidents_list(
    request: Request,
    q: str = "",
    user_id: int = 0,
    date_from: str = "",
    date_to: str = "",
    team: str = "",
    db: Session = Depends(get_db),
):
    incidents = crud.search_incidents(db, q=q, user_id=user_id, date_from=date_from, date_to=date_to, team=team)
    teams = crud.get_teams(db)
    users = crud.get_users(db)
    return templates.TemplateResponse(
        "incidents/list.html",
        {
            "request": request,
            "incidents": incidents,
            "teams": teams,
            "users": users,
            "q": q,
            "selected_user_id": user_id,
            "date_from": date_from,
            "date_to": date_to,
            "selected_team": team,
        },
    )


@app.get("/incidents/partial", response_class=HTMLResponse)
async def incidents_partial(
    request: Request,
    q: str = "",
    user_id: int = 0,
    date_from: str = "",
    date_to: str = "",
    team: str = "",
    db: Session = Depends(get_db),
):
    incidents = crud.search_incidents(db, q=q, user_id=user_id, date_from=date_from, date_to=date_to, team=team)
    return templates.TemplateResponse(
        "partials/incidents_table.html",
        {"request": request, "incidents": incidents},
    )


@app.get("/incidents/new", response_class=HTMLResponse)
async def new_incident_form(request: Request, db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return templates.TemplateResponse(
        "incidents/new.html", {"request": request, "users": users}
    )


@app.post("/incidents")
async def create_incident(
    user_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    discovered_by: str = Form(...),
    resolved_by: str = Form(...),
    helpers: str = Form(""),
    links: str = Form(""),
    occurred_at: str = Form(...),
    db: Session = Depends(get_db),
):
    occurred_dt = datetime.fromisoformat(occurred_at)
    incident = crud.create_incident(
        db,
        user_id=user_id,
        title=title,
        description=description,
        discovered_by=discovered_by,
        resolved_by=resolved_by,
        helpers=helpers,
        links=links,
        occurred_at=occurred_dt,
    )
    return RedirectResponse(f"/incidents/{incident.id}?new=1", status_code=303)


@app.get("/incidents/{incident_id}", response_class=HTMLResponse)
async def incident_detail(
    request: Request,
    incident_id: int,
    new: int = 0,
    db: Session = Depends(get_db),
):
    incident = crud.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    epitaph = get_incident_epitaph(incident.user.name)
    return templates.TemplateResponse(
        "incidents/detail.html",
        {"request": request, "incident": incident, "just_created": bool(new), "epitaph": epitaph},
    )


# ── Users ─────────────────────────────────────────────────────────────────────

@app.get("/users", response_class=HTMLResponse)
async def users_list(request: Request, created: int = 0, db: Session = Depends(get_db)):
    users = crud.get_users_with_counts(db)
    teams = crud.get_teams(db)
    return templates.TemplateResponse(
        "users/list.html",
        {"request": request, "users": users, "teams": teams, "just_created": bool(created)},
    )


@app.post("/users")
async def create_user(
    name: str = Form(...),
    team: str = Form(...),
    nickname: str = Form(""),
    db: Session = Depends(get_db),
):
    crud.create_user(db, name=name, team=team, nickname=nickname)
    return RedirectResponse("/users?created=1", status_code=303)


# ── Leaderboard ───────────────────────────────────────────────────────────────

@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard(
    request: Request, period: str = "monthly", db: Session = Depends(get_db)
):
    now = datetime.utcnow()
    if period == "yearly":
        rankings = crud.get_yearly_leaderboard(db, now.year)
        team_rankings = crud.get_yearly_team_leaderboard(db, now.year)
        label = str(now.year)
    else:
        rankings = crud.get_monthly_leaderboard(db, now.year, now.month)
        team_rankings = crud.get_monthly_team_leaderboard(db, now.year, now.month)
        label = f"{calendar.month_name[now.month]} {now.year}"
    return templates.TemplateResponse(
        "leaderboard.html",
        {
            "request": request,
            "rankings": rankings,
            "team_rankings": team_rankings,
            "period": period,
            "label": label,
        },
    )


@app.get("/leaderboard/partial", response_class=HTMLResponse)
async def leaderboard_partial(
    request: Request, period: str = "monthly", db: Session = Depends(get_db)
):
    now = datetime.utcnow()
    if period == "yearly":
        rankings = crud.get_yearly_leaderboard(db, now.year)
        team_rankings = crud.get_yearly_team_leaderboard(db, now.year)
        label = str(now.year)
    else:
        rankings = crud.get_monthly_leaderboard(db, now.year, now.month)
        team_rankings = crud.get_monthly_team_leaderboard(db, now.year, now.month)
        label = f"{calendar.month_name[now.month]} {now.year}"
    return templates.TemplateResponse(
        "partials/lb_table.html",
        {
            "request": request,
            "rankings": rankings,
            "team_rankings": team_rankings,
            "period": period,
            "label": label,
        },
    )


# ── Stats ─────────────────────────────────────────────────────────────────────

@app.get("/stats", response_class=HTMLResponse)
async def stats(request: Request, db: Session = Depends(get_db)):
    users_stats = crud.get_users_with_counts(db)
    team_stats = crud.get_team_stats(db)
    monthly_data = crud.get_monthly_incident_counts(db)
    chart_labels = json.dumps(
        [f"{calendar.month_abbr[d['month']]} {d['year']}" for d in monthly_data]
    )
    chart_data = json.dumps([d["count"] for d in monthly_data])
    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "users_stats": users_stats,
            "team_stats": team_stats,
            "chart_labels": chart_labels,
            "chart_data": chart_data,
        },
    )
