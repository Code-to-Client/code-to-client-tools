"""Contact Form Outreach Tracker — FastAPI backend.

Serves the same SQLite database (contacts.db) used by the contact-form autofiller script.
Run with: python -m tracker_server.main
"""

import importlib.util
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from tracker_server.db import DB
from tracker_server.config import Config


def _init_db() -> None:
    """Initialize the shared database via create_db.py."""
    script = Path(__file__).resolve().parents[2] / "create_db.py"
    spec = importlib.util.spec_from_file_location("create_db", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.create_db(Config.DB_PATH)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _init_db()
    yield
from tracker_server.schemas import (
    VALID_STATUSES,
    ContactCreate,
    ContactUpdate,
    VerticalCreate,
    VerticalUpdate,
)

app = FastAPI(
    title="Contact Form Outreach Tracker API",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----- Contacts -----

@app.get("/api/v1/locations")
def list_locations(vertical: str | None = Query(None)):
    return DB.list_locations(vertical=vertical)


@app.get("/api/v1/contacts")
def list_contacts(
    status: str | None = Query(None),
    vertical: str | None = Query(None),
    postal_code: str | None = Query(None),
    city_state: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    if status is not None and status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    return DB.list_contacts(
        status=status, vertical=vertical,
        postal_code=postal_code, city_state=city_state,
        limit=limit, offset=offset,
    )


@app.post("/api/v1/contacts", status_code=201)
def create_contact(body: ContactCreate):
    if body.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status: {body.status}")
    try:
        return DB.create_contact(
            body.company_name,
            contact_name=body.contact_name,
            email=body.email,
            phone=body.phone,
            city=body.city,
            state=body.state,
            postal_code=body.postal_code,
            url=body.url,
            contact_url=body.contact_url,
            vertical=body.vertical,
            contacted_at=body.contacted_at,
            status=body.status,
            notes=body.notes,
            next_action=body.next_action,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _build_status_history(c: dict) -> list[dict]:
    """Build status_history from contact *_at fields. Includes all statuses with a non-null timestamp, sorted descending."""
    entries = [
        ("CONTACTED", c.get("contacted_at")),
        ("DESIGN_PARTNER_PROSPECT", c.get("design_partner_prospect_at")),
        ("WAITLISTED", c.get("waitlisted_at")),
        ("OTHER_PROSPECT", c.get("other_prospect_at")),
        ("DISCOVERY_CALL", c.get("discovery_call_at")),
        ("DESIGN_PARTNER", c.get("design_partner_at")),
        ("CUSTOMER", c.get("customer_at")),
        ("NOT_INTERESTED", c.get("not_interested_at")),
    ]
    out = []
    for status, val in entries:
        if not val:
            continue
        s = val if isinstance(val, str) else str(val)
        out.append({"status": status, "changed_at": s})
    out.sort(key=lambda e: e["changed_at"], reverse=True)
    return out


@app.get("/api/v1/contacts/{contact_id:int}")
def get_contact(contact_id: int):
    c = DB.get_contact(contact_id)
    if c is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    c["status_history"] = _build_status_history(c)
    return c


@app.patch("/api/v1/contacts/{contact_id:int}")
def update_contact(contact_id: int, body: ContactUpdate):
    if body.status is not None and body.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status: {body.status}")
    try:
        out = DB.update_contact(
            contact_id,
            contact_name=body.contact_name,
            email=body.email,
            phone=body.phone,
            city=body.city,
            state=body.state,
            postal_code=body.postal_code,
            company_name=body.company_name,
            url=body.url,
            contact_url=body.contact_url,
            vertical=body.vertical,
            contacted_at=body.contacted_at,
            status=body.status,
            notes=body.notes,
            next_action=body.next_action,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if out is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return out


@app.delete("/api/v1/contacts/{contact_id:int}", status_code=204)
def delete_contact(contact_id: int):
    if not DB.delete_contact(contact_id):
        raise HTTPException(status_code=404, detail="Contact not found")
    return None


# ----- Dashboard -----

@app.get("/api/v1/dashboard")
def get_dashboard(
    vertical: str | None = Query(None),
    postal_code: str | None = Query(None),
    city_state: str | None = Query(None),
):
    return DB.get_dashboard(vertical=vertical, postal_code=postal_code, city_state=city_state)


# ----- Verticals -----

@app.get("/api/v1/verticals")
def list_verticals():
    return DB.list_verticals()


@app.post("/api/v1/verticals", status_code=201)
def create_vertical(body: VerticalCreate):
    try:
        return DB.create_vertical(body.name, website_visitors=body.website_visitors)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except sqlite3.IntegrityError as e:
        if "UNIQUE" in str(e).upper():
            raise HTTPException(status_code=400, detail="A vertical with this name already exists")
        raise HTTPException(status_code=400, detail=str(e))


@app.patch("/api/v1/verticals/{vertical_id:int}")
def update_vertical(vertical_id: int, body: VerticalUpdate):
    try:
        out = DB.update_vertical(
            vertical_id,
            name=body.name,
            website_visitors=body.website_visitors,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except sqlite3.IntegrityError as e:
        if "UNIQUE" in str(e).upper():
            raise HTTPException(status_code=400, detail="A vertical with this name already exists")
        raise HTTPException(status_code=400, detail=str(e))
    if out is None:
        raise HTTPException(status_code=404, detail="Vertical not found")
    return out


@app.delete("/api/v1/verticals/{vertical_id:int}", status_code=204)
def delete_vertical(vertical_id: int):
    try:
        if not DB.delete_vertical(vertical_id):
            raise HTTPException(status_code=404, detail="Vertical not found")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "tracker_server.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
