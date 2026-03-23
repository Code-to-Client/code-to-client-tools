"""Pydantic schemas for API request/response."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

# Status and source sets for validation (must match db.STATUSES and db.CONTACT_SOURCES)
VALID_STATUSES = {
    "CONTACTED", "DESIGN_PARTNER_PROSPECT", "WAITLISTED", "OTHER_PROSPECT",
    "DISCOVERY_CALL", "DESIGN_PARTNER", "CUSTOMER", "NOT_INTERESTED",
}


class ContactCreate(BaseModel):
    company_name: str
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    url: str | None = None
    contact_url: str | None = None
    vertical: str | None = None
    contacted_at: str | None = None
    status: str = "CONTACTED"
    notes: str | None = None
    next_action: str | None = None


class ContactUpdate(BaseModel):
    company_name: str | None = None
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    url: str | None = None
    contact_url: str | None = None
    vertical: str | None = None
    contacted_at: str | None = None
    status: str | None = None
    notes: str | None = None
    next_action: str | None = None


class VerticalCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    website_visitors: int | None = None


class VerticalUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    website_visitors: int | None = None

    @model_validator(mode="after")
    def at_least_one_field(self):
        if self.name is None and self.website_visitors is None:
            raise ValueError("At least one of name or website_visitors must be provided")
        return self
