"""Configuration for the Contact Form Tracker API."""

from pathlib import Path


class Config:
    """App configuration."""

    DB_PATH: Path = Path(__file__).resolve().parents[3] / "contacts.db"

    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
