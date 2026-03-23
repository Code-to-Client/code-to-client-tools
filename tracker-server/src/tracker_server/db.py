"""Database access for the Contact Form Tracker.

Uses the same SQLite database (CONTACTS table) as the contact-form autofiller script.
Schema is created by db_migration.py; this module only reads and writes.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator

from tracker_server.config import Config


class DB:
    """SQLite database access for CONTACTS and waitlist_entries. All methods are static."""

    # Status and source enums (must match Technical Requirements and contact-form usage)
    STATUSES = frozenset({
        "CONTACTED", "DESIGN_PARTNER_PROSPECT", "WAITLISTED", "OTHER_PROSPECT",
        "DISCOVERY_CALL", "DESIGN_PARTNER", "CUSTOMER", "NOT_INTERESTED",
    })
    CONTACT_SOURCES = frozenset({"CONTACT_FORM", "MANUAL"})

    @staticmethod
    @contextmanager
    def _conn() -> Generator[sqlite3.Connection, None, None]:
        """Yield a SQLite connection to Config.DB_PATH. Closes on exit."""
        conn = sqlite3.connect(str(Config.DB_PATH))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    @staticmethod
    def _row_to_contact(row: sqlite3.Row) -> dict[str, Any]:
        """Map CONTACTS row (and tracker columns) to API contact shape."""
        r = dict(row)

        def ts(col: str) -> str | None:
            val = r.get(col)
            if val is None:
                return None
            return val if isinstance(val, str) else str(val)

        status = r.get("STATUS") or "CONTACTED"
        source = r.get("CONTACT_SOURCE") or "CONTACT_FORM"

        return {
            "id": r["ID"],
            "contact_name": r.get("CONTACT_NAME") or "",
            "company_name": r.get("CONTACT_COMPANY") or "",
            "email": r.get("CONTACT_EMAIL"),
            "phone": r.get("CONTACT_PHONE"),
            "city": r.get("CONTACT_CITY"),
            "state": r.get("CONTACT_STATE"),
            "postal_code": r.get("CONTACT_POSTAL_CODE"),
            "url": r.get("URL"),
            "contact_url": r.get("CONTACT_FORM_URL"),
            "vertical": r.get("VERTICAL"),
            "status": status,
            "contact_source": source,
            "contacted_at": ts("CONTACTED_AT"),
            "design_partner_prospect_at": ts("DESIGN_PARTNER_PROSPECT_AT"),
            "waitlisted_at": ts("WAITLISTED_AT"),
            "other_prospect_at": ts("OTHER_PROSPECT_AT"),
            "discovery_call_at": ts("DISCOVERY_CALL_AT"),
            "design_partner_at": ts("DESIGN_PARTNER_AT"),
            "customer_at": ts("CUSTOMER_AT"),
            "not_interested_at": ts("NOT_INTERESTED_AT"),
            "notes": r.get("NOTES"),
            "next_action": r.get("NEXT_ACTION"),
            "created_at": ts("CREATED_AT"),
            "updated_at": ts("UPDATED_AT"),
        }

    @staticmethod
    def _set_status_date(cursor: sqlite3.Cursor, contact_id: int, status: str) -> None:
        """Set the corresponding *_at column to now if not already set."""
        col = {
            "DESIGN_PARTNER_PROSPECT": "DESIGN_PARTNER_PROSPECT_AT",
            "WAITLISTED": "WAITLISTED_AT",
            "OTHER_PROSPECT": "OTHER_PROSPECT_AT",
            "DISCOVERY_CALL": "DISCOVERY_CALL_AT",
            "DESIGN_PARTNER": "DESIGN_PARTNER_AT",
            "CUSTOMER": "CUSTOMER_AT",
            "NOT_INTERESTED": "NOT_INTERESTED_AT",
        }.get(status)
        if not col:
            return
        cursor.execute(
            f"UPDATE CONTACTS SET {col} = COALESCE({col}, CURRENT_TIMESTAMP) WHERE ID = ?",
            (contact_id,),
        )

    # ---- Contacts ----

    @staticmethod
    def list_locations(vertical: str | None = None) -> dict[str, list[str]]:
        """Return unique postal codes and city/state combinations, optionally filtered by vertical.
        Prepends 'N/A' if any contacts have a missing value for that field."""
        vertical_clause = " AND VERTICAL = ?" if vertical else ""
        vertical_params = [vertical] if vertical else []
        with DB._conn() as conn:
            cursor = conn.cursor()

            cursor.execute(
                f"SELECT COUNT(*) FROM CONTACTS WHERE (CONTACT_POSTAL_CODE IS NULL OR CONTACT_POSTAL_CODE = ''){vertical_clause}",
                vertical_params,
            )
            has_missing_zip = cursor.fetchone()[0] > 0
            cursor.execute(
                "SELECT DISTINCT CONTACT_POSTAL_CODE FROM CONTACTS "
                f"WHERE CONTACT_POSTAL_CODE IS NOT NULL AND CONTACT_POSTAL_CODE != ''{vertical_clause} "
                "ORDER BY CONTACT_POSTAL_CODE",
                vertical_params,
            )
            zips = (["N/A"] if has_missing_zip else []) + [r[0] for r in cursor.fetchall()]

            cursor.execute(
                f"SELECT COUNT(*) FROM CONTACTS WHERE (CONTACT_CITY IS NULL OR CONTACT_CITY = ''){vertical_clause}",
                vertical_params,
            )
            has_missing_city = cursor.fetchone()[0] > 0
            cursor.execute(
                "SELECT DISTINCT CONTACT_CITY, CONTACT_STATE FROM CONTACTS "
                f"WHERE CONTACT_CITY IS NOT NULL AND CONTACT_CITY != ''{vertical_clause} "
                "ORDER BY CONTACT_CITY, CONTACT_STATE",
                vertical_params,
            )
            city_states = (["N/A"] if has_missing_city else []) + [
                f"{r[0]}, {r[1]}" if r[1] else r[0]
                for r in cursor.fetchall()
            ]
            return {"zips": zips, "city_states": city_states}

    @staticmethod
    def list_contacts(
        *,
        status: str | None = None,
        vertical: str | None = None,
        postal_code: str | None = None,
        city_state: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List contacts with optional filters by status, vertical, postal code, and city/state."""
        with DB._conn() as conn:
            cursor = conn.cursor()
            q = "SELECT * FROM CONTACTS WHERE 1=1"
            params: list[Any] = []
            if status:
                q += " AND (STATUS = ? OR (STATUS IS NULL AND ? = 'contacted'))"
                params.extend([status, status])
            if vertical:
                q += " AND VERTICAL = ?"
                params.append(vertical)
            if postal_code == "N/A":
                q += " AND (CONTACT_POSTAL_CODE IS NULL OR CONTACT_POSTAL_CODE = '')"
            elif postal_code:
                q += " AND CONTACT_POSTAL_CODE = ?"
                params.append(postal_code)
            if city_state == "N/A":
                q += " AND (CONTACT_CITY IS NULL OR CONTACT_CITY = '')"
            elif city_state:
                parts = city_state.rsplit(", ", 1)
                q += " AND CONTACT_CITY = ?"
                params.append(parts[0])
                if len(parts) == 2:
                    q += " AND CONTACT_STATE = ?"
                    params.append(parts[1])
            q += " ORDER BY COALESCE(CONTACTED_AT, CREATED_AT) DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            cursor.execute(q, params)
            return [DB._row_to_contact(r) for r in cursor.fetchall()]

    @staticmethod
    def get_contact(contact_id: int) -> dict[str, Any] | None:
        """Return one contact by ID, or None if not found."""
        with DB._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM CONTACTS WHERE ID = ?", (contact_id,))
            row = cursor.fetchone()
            return DB._row_to_contact(row) if row else None

    @staticmethod
    def create_contact(
        company_name: str,
        *,
        contact_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        city: str | None = None,
        state: str | None = None,
        postal_code: str | None = None,
        url: str | None = None,
        contact_url: str | None = None,
        vertical: str | None = None,
        contacted_at: str | None = None,
        status: str = "CONTACTED",
        notes: str | None = None,
        next_action: str | None = None,
    ) -> dict[str, Any]:
        """Create a new contact. Status defaults to 'CONTACTED'. Contact source is MANUAL."""
        if status not in DB.STATUSES:
            raise ValueError(f"Invalid status: {status}")
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with DB._conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO CONTACTS (
                    CONTACT_NAME, CONTACT_EMAIL, CONTACT_PHONE, CONTACT_COMPANY,
                    CONTACT_CITY, CONTACT_STATE, CONTACT_POSTAL_CODE,
                    URL, CONTACT_FORM_URL, VERTICAL,
                    CONTACTED_AT, STATUS, CONTACT_SOURCE, NOTES, NEXT_ACTION,
                    CREATED_AT, UPDATED_AT
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'MANUAL', ?, ?, ?, ?)
                """,
                (
                    contact_name or "",
                    email or "",
                    phone or "",
                    company_name,
                    city,
                    state,
                    postal_code,
                    url,
                    contact_url,
                    vertical,
                    contacted_at or now,
                    status,
                    notes,
                    next_action,
                    now,
                    now,
                ),
            )
            conn.commit()
            cid = cursor.lastrowid
            DB._set_status_date(cursor, cid, status)
            conn.commit()
            out = DB.get_contact(cid)
            assert out is not None
            return out

    @staticmethod
    def update_contact(
        contact_id: int,
        *,
        contact_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        city: str | None = None,
        state: str | None = None,
        postal_code: str | None = None,
        company_name: str | None = None,
        url: str | None = None,
        contact_url: str | None = None,
        vertical: str | None = None,
        contacted_at: str | None = None,
        status: str | None = None,
        notes: str | None = None,
        next_action: str | None = None,
    ) -> dict[str, Any] | None:
        """Update a contact by ID. Only provided fields are updated. Returns None if not found."""
        if status is not None and status not in DB.STATUSES:
            raise ValueError(f"Invalid status: {status}")
        with DB._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ID FROM CONTACTS WHERE ID = ?", (contact_id,))
            if cursor.fetchone() is None:
                return None
            updates: list[str] = ["UPDATED_AT = CURRENT_TIMESTAMP"]
            params: list[Any] = []
            if contact_name is not None:
                updates.append("CONTACT_NAME = ?")
                params.append(contact_name)
            if email is not None:
                updates.append("CONTACT_EMAIL = ?")
                params.append(email)
            if phone is not None:
                updates.append("CONTACT_PHONE = ?")
                params.append(phone)
            if city is not None:
                updates.append("CONTACT_CITY = ?")
                params.append(city)
            if state is not None:
                updates.append("CONTACT_STATE = ?")
                params.append(state)
            if postal_code is not None:
                updates.append("CONTACT_POSTAL_CODE = ?")
                params.append(postal_code)
            if company_name is not None:
                updates.append("CONTACT_COMPANY = ?")
                params.append(company_name)
            if url is not None:
                updates.append("URL = ?")
                params.append(url)
            if contact_url is not None:
                updates.append("CONTACT_FORM_URL = ?")
                params.append(contact_url)
            if vertical is not None:
                updates.append("VERTICAL = ?")
                params.append(vertical)
            if contacted_at is not None:
                updates.append("CONTACTED_AT = ?")
                params.append(contacted_at)
            if status is not None:
                updates.append("STATUS = ?")
                params.append(status)
                DB._set_status_date(cursor, contact_id, status)
            if notes is not None:
                updates.append("NOTES = ?")
                params.append(notes)
            if next_action is not None:
                updates.append("NEXT_ACTION = ?")
                params.append(next_action)
            params.append(contact_id)
            cursor.execute(
                f"UPDATE CONTACTS SET {', '.join(updates)} WHERE ID = ?",
                params,
            )
            conn.commit()
        return DB.get_contact(contact_id)

    @staticmethod
    def delete_contact(contact_id: int) -> bool:
        """Delete a contact by ID. Returns True if deleted, False if not found."""
        with DB._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM CONTACTS WHERE ID = ?", (contact_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ---- Dashboard ----

    @staticmethod
    def get_dashboard(
        vertical: str | None = None,
        postal_code: str | None = None,
        city_state: str | None = None,
    ) -> dict[str, Any]:
        """Return aggregate metrics for the dashboard (counts, response rate, by_status).
        Optionally filtered by vertical, postal code, and/or city/state.
        """
        conditions: list[str] = []
        params: list[Any] = []
        if vertical:
            conditions.append("VERTICAL = ?")
            params.append(vertical)
        if postal_code == "N/A":
            conditions.append("(CONTACT_POSTAL_CODE IS NULL OR CONTACT_POSTAL_CODE = '')")
        elif postal_code:
            conditions.append("CONTACT_POSTAL_CODE = ?")
            params.append(postal_code)
        if city_state == "N/A":
            conditions.append("(CONTACT_CITY IS NULL OR CONTACT_CITY = '')")
        elif city_state:
            parts = city_state.rsplit(", ", 1)
            conditions.append("CONTACT_CITY = ?")
            params.append(parts[0])
            if len(parts) == 2:
                conditions.append("CONTACT_STATE = ?")
                params.append(parts[1])
        where = ("WHERE " + " AND ".join(conditions)) if conditions else "WHERE 1=1"

        with DB._conn() as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT COUNT(*) FROM CONTACTS {where}", params)
            contacts_sent = cursor.fetchone()[0]

            # Visitor count from VERTICALS
            if vertical:
                cursor.execute("SELECT COALESCE(WEBSITE_VISITORS, 0) FROM VERTICALS WHERE NAME = ?", [vertical])
                row = cursor.fetchone()
                visitor_count = row[0] if row else 0
            else:
                cursor.execute("SELECT COALESCE(SUM(WEBSITE_VISITORS), 0) FROM VERTICALS")
                visitor_count = cursor.fetchone()[0]

            # Per-status counts
            by_status: dict[str, int] = {}
            for s in ("CONTACTED", "DESIGN_PARTNER_PROSPECT", "WAITLISTED", "OTHER_PROSPECT",
                      "DISCOVERY_CALL", "DESIGN_PARTNER", "CUSTOMER", "NOT_INTERESTED"):
                cursor.execute(f"SELECT COUNT(*) FROM CONTACTS {where} AND STATUS = ?", params + [s])
                by_status[s] = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(*) FROM CONTACTS {where} AND DESIGN_PARTNER_PROSPECT_AT IS NOT NULL", params)
            design_partner_prospects = cursor.fetchone()[0]
            cursor.execute(f"SELECT COUNT(*) FROM CONTACTS {where} AND WAITLISTED_AT IS NOT NULL", params)
            waitlist_signups = cursor.fetchone()[0]
            cursor.execute(f"SELECT COUNT(*) FROM CONTACTS {where} AND OTHER_PROSPECT_AT IS NOT NULL", params)
            other_prospects = cursor.fetchone()[0]
            total_responses = design_partner_prospects + waitlist_signups + other_prospects

            response_rate = round(total_responses / max(contacts_sent, 1) * 100, 1)

            def pct(val: int) -> float:
                return round(val / contacts_sent * 100, 1) if contacts_sent else 0.0

            return {
                "vertical": vertical,
                "contacts_sent": contacts_sent,
                "visitor_count": visitor_count,
                "total_responses": total_responses,
                "design_partner_prospects": design_partner_prospects,
                "waitlist_signups": waitlist_signups,
                "other_prospects": other_prospects,
                "response_rate_pct": response_rate,
                "pct_of_contacts_sent": {
                    "visitor_count": pct(visitor_count),
                    "total_responses": pct(total_responses),
                    "design_partner_prospects": pct(design_partner_prospects),
                    "waitlist_signups": pct(waitlist_signups),
                    "other_prospects": pct(other_prospects),
                },
                "by_status": by_status,
            }

    # ---- Verticals ----

    @staticmethod
    def list_verticals() -> list[dict[str, Any]]:
        """Return all verticals ordered by name, with contact_count (contacts referencing this vertical)."""
        with DB._conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT v.ID, v.NAME, v.WEBSITE_VISITORS, v.CREATED_AT, v.UPDATED_AT,
                       (SELECT COUNT(*) FROM CONTACTS c WHERE c.VERTICAL = v.NAME) AS contact_count
                FROM VERTICALS v
                ORDER BY v.NAME
                """
            )
            return [
                {
                    "id": r["ID"],
                    "name": r["NAME"],
                    "website_visitors": r["WEBSITE_VISITORS"],
                    "created_at": r["CREATED_AT"],
                    "updated_at": r["UPDATED_AT"],
                    "contact_count": r["contact_count"] or 0,
                }
                for r in cursor.fetchall()
            ]

    @staticmethod
    def get_vertical(vertical_id: int) -> dict[str, Any] | None:
        """Return one vertical by ID, or None if not found."""
        with DB._conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ID, NAME, WEBSITE_VISITORS, CREATED_AT, UPDATED_AT FROM VERTICALS WHERE ID = ?",
                (vertical_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row["ID"],
                "name": row["NAME"],
                "website_visitors": row["WEBSITE_VISITORS"],
                "created_at": row["CREATED_AT"],
                "updated_at": row["UPDATED_AT"],
            }

    @staticmethod
    def create_vertical(name: str, website_visitors: int | None = None) -> dict[str, Any]:
        """Create a vertical. Name must be unique. Returns the created vertical."""
        name_trimmed = name.strip()
        if not name_trimmed:
            raise ValueError("Vertical name is required")
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with DB._conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO VERTICALS (NAME, WEBSITE_VISITORS, CREATED_AT, UPDATED_AT) VALUES (?, ?, ?, ?)",
                (name_trimmed, website_visitors, now, now),
            )
            conn.commit()
            vid = cursor.lastrowid
            out = DB.get_vertical(vid)
            assert out is not None
            return out

    @staticmethod
    def update_vertical(
        vertical_id: int,
        name: str | None = None,
        website_visitors: int | None = None,
    ) -> dict[str, Any] | None:
        """Update a vertical by ID. Provide name and/or website_visitors. Returns None if not found."""
        with DB._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ID, NAME, WEBSITE_VISITORS FROM VERTICALS WHERE ID = ?", (vertical_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            new_name = row["NAME"] if name is None else name.strip()
            if not new_name:
                raise ValueError("Vertical name is required")
            new_visitors = row["WEBSITE_VISITORS"] if website_visitors is None else website_visitors
            cursor.execute(
                "UPDATE VERTICALS SET NAME = ?, WEBSITE_VISITORS = ?, UPDATED_AT = ? WHERE ID = ?",
                (new_name, new_visitors, now, vertical_id),
            )
            conn.commit()
        return DB.get_vertical(vertical_id)

    @staticmethod
    def delete_vertical(vertical_id: int) -> bool:
        """Delete a vertical by ID. Returns True if deleted, False if not found.
        Raises ValueError if at least one contact references this vertical.
        """
        with DB._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT NAME FROM VERTICALS WHERE ID = ?", (vertical_id,))
            row = cursor.fetchone()
            if row is None:
                return False
            name = row["NAME"]
            cursor.execute("SELECT COUNT(*) FROM CONTACTS WHERE VERTICAL = ?", (name,))
            count = cursor.fetchone()[0]
            if count > 0:
                raise ValueError(
                    f"Cannot delete: {count} contact(s) use this vertical. Reassign or clear their vertical first."
                )
            cursor.execute("DELETE FROM VERTICALS WHERE ID = ?", (vertical_id,))
            conn.commit()
            return cursor.rowcount > 0
