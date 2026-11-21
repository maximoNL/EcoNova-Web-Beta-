"""Dataclasses shared across EcoNova: database content blocks and feedback."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urlparse


def is_valid_http_url(value: str | None) -> bool:
    """Return True only for absolute http/https URLs (so "No hay" is rejected)."""
    if not value:
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


@dataclass(frozen=True)
class ContentBlock:
    """One publishable row of the Excel content database."""

    id: int
    section: str
    topic: str
    information: str  # rendered literally and verbatim
    source: str
    link: str

    @property
    def has_valid_link(self) -> bool:
        return is_valid_http_url(self.link)


@dataclass
class FeedbackSubmission:
    """A feedback form submission from a student or teacher."""

    message: str
    visited_before: str = "No"
    rating: int = 3
    name: str = "Anonymous"
    submitted_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        # Single-line, trimmed name (also prevents header injection in emails).
        cleaned = " ".join((self.name or "").split())
        self.name = cleaned or "Anonymous"
        self.message = (self.message or "").strip()
        self.rating = max(1, min(5, int(self.rating)))
        if self.visited_before not in ("Yes", "No"):
            self.visited_before = "No"
