"""Module 03 starter: well-designed tool schemas and implementations."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.northwind import load_tickets

STATUSES = ["open", "in_progress", "resolved", "closed"]
PRIORITIES = ["low", "medium", "high", "critical"]   # ordered from least to most severe
DEPARTMENTS = ["Engineering", "Finance", "HR", "Operations", "Sales"]

# TODO: two Claude API tool definitions: {"name", "description", "input_schema"}.
# search_tickets: optional filters text, status, priority, department, assignee_id, limit (1–50).
# get_ticket: required ticket_id matching the pattern NW-<3 digits>.
TOOLS: list[dict] = []


def search_tickets(
    text: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    department: str | None = None,
    assignee_id: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """Return tickets matching all given filters.

    - `text` matches title or description, case-insensitive.
    - An invalid status/priority/department raises ValueError whose message
      names the bad value and lists the allowed values.
    - `limit` is clamped to 1..50.
    - Sort by priority (critical first), then by ticket id.
    """
    # TODO
    raise NotImplementedError


def get_ticket(ticket_id: str) -> dict:
    """Return one ticket.

    - Raise ValueError mentioning the expected format (e.g. NW-104) if the id is malformed.
    - Raise ValueError containing "not found" if no such ticket exists.
    """
    # TODO
    raise NotImplementedError
