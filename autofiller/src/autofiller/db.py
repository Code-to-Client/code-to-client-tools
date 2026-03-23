#!/usr/bin/env python3
"""
db.py - SQLite database operations for the CONTACTS table.
"""

import sqlite3
import logging
from autofiller.config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DB:
    """SQLite database operations for the CONTACTS table."""

    @staticmethod
    def insert_contact(
        contact_form_url: str,
        vertical: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
    ):
        """
        Insert a new row into CONTACTS table.
        If CONTACT_FORM_URL already exists, do nothing and return the existing row's ID.

        Args:
            contact_form_url: The contact form URL (required).
            vertical: Vertical label to associate with this contact (optional).
            city: Contact city (optional).
            state: Contact state (optional).
            zip_code: Contact postal code (optional).

        Returns:
            int or None: The row's ID (new or existing) if successful, None otherwise.
        """
        connection = None
        try:
            connection = sqlite3.connect(Config.DB_PATH)
            cursor = connection.cursor()

            cursor.execute("SELECT ID FROM CONTACTS WHERE CONTACT_FORM_URL = ? LIMIT 1", (contact_form_url,))
            existing = cursor.fetchone()
            if existing:
                return existing[0]

            if vertical:
                cursor.execute("INSERT OR IGNORE INTO VERTICALS (NAME) VALUES (?)", (vertical,))

            cursor.execute(
                """
                INSERT INTO CONTACTS (
                    CONTACT_FORM_URL, CONTACTED_AT, CONTACT_SOURCE, STATUS, VERTICAL,
                    CONTACT_CITY, CONTACT_STATE, CONTACT_POSTAL_CODE
                )
                VALUES (?, CURRENT_TIMESTAMP, 'CONTACT_FORM', 'CONTACTED', ?, ?, ?, ?)
                """,
                (contact_form_url, vertical, city or None, state or None, zip_code or None),
            )

            connection.commit()

            row_id = cursor.lastrowid
            logger.info(f"Inserted contact ID {row_id} (CONTACT_FORM_URL={contact_form_url})")
            return row_id
        except sqlite3.Error as e:
            logger.error(f"SQLite error occurred: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            return None
        finally:
            if connection:
                connection.close()

    @staticmethod
    def contact_exists(contact_form_url: str) -> bool:
        """
        Check if a contact form URL has already been submitted (exists in CONTACTS).

        Args:
            contact_form_url: The contact form URL to check.

        Returns:
            True if a row exists with this CONTACT_FORM_URL, False otherwise.
        """
        connection = None
        try:
            connection = sqlite3.connect(Config.DB_PATH)
            cursor = connection.cursor()
            cursor.execute(
                "SELECT 1 FROM CONTACTS WHERE CONTACT_FORM_URL = ? LIMIT 1",
                (contact_form_url,),
            )
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logger.error(f"SQLite error in contact_exists: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in contact_exists: {e}")
            return False
        finally:
            if connection:
                connection.close()
