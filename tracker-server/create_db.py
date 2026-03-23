#!/usr/bin/env python3
"""
create_db.py - Initialize the shared contacts database.

Creates the SQLite database and all tables if they do not already exist.
Safe to call on every startup - uses CREATE TABLE IF NOT EXISTS throughout.

Usage:
    python create_db.py
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent / "contacts.db"

SQL = """
CREATE TABLE IF NOT EXISTS CONTACTS (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    CONTACT_FORM_URL TEXT UNIQUE,
    URL TEXT,
    VERTICAL TEXT,
    CONTACTED_AT TIMESTAMP,
    CONTACT_SOURCE TEXT CHECK(CONTACT_SOURCE IN ('CONTACT_FORM', 'MANUAL')),
    STATUS TEXT CHECK(STATUS IN ('CONTACTED', 'DESIGN_PARTNER_PROSPECT', 'WAITLISTED', 'OTHER_PROSPECT', 'DISCOVERY_CALL', 'DESIGN_PARTNER', 'CUSTOMER', 'NOT_INTERESTED')),
    NOTES TEXT,
    NEXT_ACTION TEXT,
    DESIGN_PARTNER_PROSPECT_AT TIMESTAMP,
    WAITLISTED_AT TIMESTAMP,
    OTHER_PROSPECT_AT TIMESTAMP,
    DISCOVERY_CALL_AT TIMESTAMP,
    DESIGN_PARTNER_AT TIMESTAMP,
    CUSTOMER_AT TIMESTAMP,
    NOT_INTERESTED_AT TIMESTAMP,
    CONTACT_NAME TEXT,
    CONTACT_COMPANY TEXT,
    CONTACT_EMAIL TEXT,
    CONTACT_PHONE TEXT,
    CONTACT_CITY TEXT,
    CONTACT_STATE TEXT,
    CONTACT_POSTAL_CODE TEXT,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS update_contacts_updated_at
AFTER UPDATE ON CONTACTS
BEGIN
    UPDATE CONTACTS SET UPDATED_AT = CURRENT_TIMESTAMP WHERE ID = NEW.ID;
END;

CREATE TABLE IF NOT EXISTS VERTICALS (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME TEXT NOT NULL UNIQUE,
    WEBSITE_VISITORS INTEGER,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS update_verticals_updated_at
AFTER UPDATE ON VERTICALS
BEGIN
    UPDATE VERTICALS SET UPDATED_AT = CURRENT_TIMESTAMP WHERE ID = NEW.ID;
END;

"""


def create_db(db_path: Path = DB_PATH) -> None:
    """Create the database and all tables at the given path."""
    connection = sqlite3.connect(db_path)
    try:
        connection.executescript(SQL)
        connection.commit()
        logger.info(f"Database ready: {db_path}")
    finally:
        connection.close()


if __name__ == "__main__":
    create_db()
    print("Database created successfully")
