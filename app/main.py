import calendar
import json
import os
import random
import secrets
from datetime import datetime

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()

from . import crud, models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

_SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
_APP_PASSWORD = os.getenv("APP_PASSWORD", "")

app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# ── Auth helpers ───────────────────────────────────────────────────────────────

def _is_authenticated(request: Request) -> bool:
    return request.session.get("authenticated") is True


@app.middleware("http")
async def auth_guard(request, call_next):
    path = request.url.path
    if path.startswith("/static") or path in ("/login", "/logout"):
        return await call_next(request)
    if not request.session.get("authenticated"):
        return RedirectResponse("/login", status_code=302)
    return await call_next(request)


app.add_middleware(SessionMiddleware, secret_key=_SECRET_KEY, session_cookie="pk_session")


@app.on_event("startup")
async def on_startup():
    if os.getenv("SEED_DATA", "").lower() == "true":
        from .database import SessionLocal
        from .seed import seed_database
        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: int = 0):
    if _is_authenticated(request):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": bool(error)})


@app.post("/login")
async def login(request: Request, password: str = Form(...)):
    if _APP_PASSWORD and password == _APP_PASSWORD:
        request.session["authenticated"] = True
        return RedirectResponse("/", status_code=303)
    return RedirectResponse("/login?error=1", status_code=303)


@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


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
    # classics
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
    # new batch
    "{name} said 'it's just a one-liner' before this happened.",
    "{name} deployed on a Friday. Bold. Catastrophic.",
    "This is why we can't have nice things, {name}.",
    "{name} and the senior engineer no longer make eye contact.",
    "Somewhere, a SRE wept. Because of {name}.",
    "{name} is still explaining this in standups three weeks later.",
    "{name} thought rollback was something skaters did.",
    "The logs were clear. {name} was not.",
    "{name} skipped the staging environment. History will remember.",
    "To this day, {name} flinches at the sound of PagerDuty.",
    "{name} replied 'on it' in Slack and then went completely silent.",
    "This incident was sponsored by {name}'s misplaced confidence.",
    "{name} was last seen muttering 'but the tests passed locally'.",
    "{name} single-handedly increased the company's AWS bill by 40%.",
    "A moment of silence for {name}'s annual performance review.",
    "{name} merged directly to main. The vibes were off.",
    "{name} told the team it was a 'minor change'. It was not minor.",
    "Fun fact: {name} also broke prod the previous Tuesday.",
    "{name}'s pull request description said 'should be fine'.",
    "{name} is the reason the deployment checklist now has 47 items.",
    "Witnesses report {name} laughed nervously and closed the laptop.",
    "{name} asked if anyone had tried turning it off and on again.",
    "This was {name}'s character development arc.",
    "{name} added 'resilient under pressure' to their LinkedIn.",
    "The postmortem document written by {name} conveniently omits {name}.",
    "{name} blamed the intern. There was no intern.",
    "Three monitors. One {name}. Zero uptime.",
    "{name} once again proved that confidence is not competence.",
    "The Kubernetes cluster is still processing {name}'s feelings.",
    "{name} types fast. Unfortunately.",
    "If production is a crime scene, {name} is the fingerprints.",
    "{name} deployed without reading the diff. Classic {name}.",
    "In a parallel universe, {name} tested this in staging first.",
    "{name} has been asked to narrate the next disaster recovery drill.",
    "Graph goes down. {name} goes quiet. Coincidence? No.",
    "{name} thought 'LGTM' applied to infrastructure changes too.",
    "Security called. It was about {name}.",
    "{name} is now the default example in the incident response training.",
    "They asked {name} what happened. {name} said 'good question'.",
    "{name} did not read the runbook. {name} wrote the runbook.",
    "Production died so {name} could learn. Was it worth it? Unclear.",
    "{name} called it a 'hotfix'. The hotfix needed a hotfix.",
    "The dashboard was red. {name} called it 'a strong shade of success'.",
    "{name} has since switched to a standing desk to cope.",
    "It took a village to clean up after {name}.",
    "{name} pressed enter and immediately left for lunch.",
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

_DASHBOARD_PER_PAGE = 25


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, page: int = 1, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    total = crud.count_incidents(db)
    total_pages = max(1, -(-total // _DASHBOARD_PER_PAGE))  # ceil division
    page = max(1, min(page, total_pages))
    offset = (page - 1) * _DASHBOARD_PER_PAGE
    recent = crud.get_incidents(db, limit=_DASHBOARD_PER_PAGE, offset=offset)
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
            "page": page,
            "total_pages": total_pages,
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
    deleted: int = 0,
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
            "just_deleted": bool(deleted),
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
    edited: int = 0,
    db: Session = Depends(get_db),
):
    incident = crud.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    epitaph = get_incident_epitaph(incident.user.name)
    return templates.TemplateResponse(
        "incidents/detail.html",
        {
            "request": request,
            "incident": incident,
            "just_created": bool(new),
            "just_edited": bool(edited),
            "epitaph": epitaph,
        },
    )


@app.get("/incidents/{incident_id}/edit", response_class=HTMLResponse)
async def edit_incident_form(request: Request, incident_id: int, db: Session = Depends(get_db)):
    incident = crud.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    users = crud.get_users(db)
    return templates.TemplateResponse(
        "incidents/edit.html", {"request": request, "incident": incident, "users": users}
    )


@app.post("/incidents/{incident_id}/edit")
async def update_incident(
    incident_id: int,
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
    incident = crud.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    crud.update_incident(
        db,
        incident_id=incident_id,
        user_id=user_id,
        title=title,
        description=description,
        discovered_by=discovered_by,
        resolved_by=resolved_by,
        helpers=helpers,
        links=links,
        occurred_at=datetime.fromisoformat(occurred_at),
    )
    return RedirectResponse(f"/incidents/{incident_id}?edited=1", status_code=303)


@app.post("/incidents/{incident_id}/delete")
async def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = crud.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    crud.delete_incident(db, incident_id)
    return RedirectResponse("/incidents?deleted=1", status_code=303)


# ── Users ─────────────────────────────────────────────────────────────────────

@app.get("/users", response_class=HTMLResponse)
async def users_list(
    request: Request,
    created: int = 0,
    edited: int = 0,
    deleted: int = 0,
    cant_delete: int = 0,
    db: Session = Depends(get_db),
):
    users = crud.get_users_with_counts(db)
    teams = crud.get_teams(db)
    blocked_user = crud.get_user(db, cant_delete) if cant_delete else None
    return templates.TemplateResponse(
        "users/list.html",
        {
            "request": request,
            "users": users,
            "teams": teams,
            "just_created": bool(created),
            "just_edited": bool(edited),
            "just_deleted": bool(deleted),
            "blocked_user": blocked_user,
        },
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


@app.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_form(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    teams = crud.get_teams(db)
    return templates.TemplateResponse(
        "users/edit.html", {"request": request, "user": user, "teams": teams}
    )


@app.post("/users/{user_id}/edit")
async def update_user(
    user_id: int,
    name: str = Form(...),
    team: str = Form(...),
    nickname: str = Form(""),
    db: Session = Depends(get_db),
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    crud.update_user(db, user_id=user_id, name=name, team=team, nickname=nickname)
    return RedirectResponse("/users?edited=1", status_code=303)


@app.post("/users/{user_id}/delete")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.incidents:
        return RedirectResponse(f"/users?cant_delete={user_id}", status_code=303)
    crud.delete_user(db, user_id)
    return RedirectResponse("/users?deleted=1", status_code=303)


# ── Leaderboard ───────────────────────────────────────────────────────────────

def _build_lb_context(db, period: str, view: str, now) -> dict:
    if period == "yearly":
        rankings = crud.get_yearly_leaderboard(db, now.year)
        team_rankings = crud.get_yearly_team_leaderboard(db, now.year)
        label = str(now.year)
    elif period == "alltime":
        rankings = crud.get_alltime_leaderboard(db)
        team_rankings = crud.get_alltime_team_leaderboard(db)
        label = "All Time"
    else:
        rankings = crud.get_monthly_leaderboard(db, now.year, now.month)
        team_rankings = crud.get_monthly_team_leaderboard(db, now.year, now.month)
        label = f"{calendar.month_name[now.month]} {now.year}"
    return {"rankings": rankings, "team_rankings": team_rankings, "period": period, "view": view, "label": label}


@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard(
    request: Request, period: str = "monthly", view: str = "individuals", db: Session = Depends(get_db)
):
    ctx = _build_lb_context(db, period, view, datetime.utcnow())
    return templates.TemplateResponse("leaderboard.html", {"request": request, **ctx})


@app.get("/leaderboard/partial", response_class=HTMLResponse)
async def leaderboard_partial(
    request: Request, period: str = "monthly", view: str = "individuals", db: Session = Depends(get_db)
):
    ctx = _build_lb_context(db, period, view, datetime.utcnow())
    return templates.TemplateResponse("partials/lb_table.html", {"request": request, **ctx})


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
