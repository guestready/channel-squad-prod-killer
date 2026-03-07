from datetime import datetime
from sqlalchemy import func, extract
from sqlalchemy.orm import Session, joinedload
from . import models


# ── Users ─────────────────────────────────────────────────────────────────────

def get_users(db: Session) -> list[models.User]:
    return db.query(models.User).order_by(models.User.name).all()


def get_users_with_counts(db: Session) -> list[tuple]:
    return (
        db.query(models.User, func.count(models.Incident.id).label("incident_count"))
        .outerjoin(models.Incident, models.User.id == models.Incident.user_id)
        .group_by(models.User.id)
        .order_by(func.count(models.Incident.id).desc())
        .all()
    )


def get_teams(db: Session) -> list[str]:
    rows = db.query(models.User.team).distinct().order_by(models.User.team).all()
    return [r.team for r in rows]


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, name: str, team: str, nickname: str | None = None) -> models.User:
    user = models.User(name=name, team=team, nickname=nickname or None)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Incidents ─────────────────────────────────────────────────────────────────

def get_incidents(db: Session, limit: int = 100) -> list[models.Incident]:
    return (
        db.query(models.Incident)
        .options(joinedload(models.Incident.user))
        .order_by(models.Incident.occurred_at.desc())
        .limit(limit)
        .all()
    )


def get_incident(db: Session, incident_id: int) -> models.Incident | None:
    return (
        db.query(models.Incident)
        .options(joinedload(models.Incident.user))
        .filter(models.Incident.id == incident_id)
        .first()
    )


def create_incident(
    db: Session,
    user_id: int,
    title: str,
    description: str,
    discovered_by: str,
    resolved_by: str,
    helpers: str,
    links: str,
    occurred_at: datetime,
) -> models.Incident:
    incident = models.Incident(
        user_id=user_id,
        title=title,
        description=description,
        discovered_by=discovered_by,
        resolved_by=resolved_by,
        helpers=helpers or None,
        links=links or None,
        occurred_at=occurred_at,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def count_incidents(db: Session) -> int:
    return db.query(func.count(models.Incident.id)).scalar() or 0


def count_incidents_this_month(db: Session) -> int:
    now = datetime.utcnow()
    return (
        db.query(func.count(models.Incident.id))
        .filter(
            extract("year", models.Incident.occurred_at) == now.year,
            extract("month", models.Incident.occurred_at) == now.month,
        )
        .scalar()
        or 0
    )


def count_incidents_this_year(db: Session) -> int:
    now = datetime.utcnow()
    return (
        db.query(func.count(models.Incident.id))
        .filter(extract("year", models.Incident.occurred_at) == now.year)
        .scalar()
        or 0
    )


def count_teams(db: Session) -> int:
    return db.query(func.count(func.distinct(models.User.team))).scalar() or 0


# ── Leaderboards ──────────────────────────────────────────────────────────────

def get_monthly_leaderboard(db: Session, year: int, month: int) -> list[tuple]:
    return (
        db.query(models.User, func.count(models.Incident.id).label("count"))
        .join(models.Incident, models.User.id == models.Incident.user_id)
        .filter(
            extract("year", models.Incident.occurred_at) == year,
            extract("month", models.Incident.occurred_at) == month,
        )
        .group_by(models.User.id)
        .order_by(func.count(models.Incident.id).desc())
        .all()
    )


def get_yearly_leaderboard(db: Session, year: int) -> list[tuple]:
    return (
        db.query(models.User, func.count(models.Incident.id).label("count"))
        .join(models.Incident, models.User.id == models.Incident.user_id)
        .filter(extract("year", models.Incident.occurred_at) == year)
        .group_by(models.User.id)
        .order_by(func.count(models.Incident.id).desc())
        .all()
    )


# ── Stats ─────────────────────────────────────────────────────────────────────

def get_team_stats(db: Session) -> list[tuple]:
    return (
        db.query(models.User.team, func.count(models.Incident.id).label("count"))
        .join(models.Incident, models.User.id == models.Incident.user_id)
        .group_by(models.User.team)
        .order_by(func.count(models.Incident.id).desc())
        .all()
    )


def get_monthly_incident_counts(db: Session) -> list[dict]:
    results = (
        db.query(
            extract("year", models.Incident.occurred_at).label("year"),
            extract("month", models.Incident.occurred_at).label("month"),
            func.count(models.Incident.id).label("count"),
        )
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )
    return [{"year": int(r.year), "month": int(r.month), "count": int(r.count)} for r in results]
