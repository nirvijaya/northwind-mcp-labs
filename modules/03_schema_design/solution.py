"""Module 03 reference solution.

Problems in bad_schemas.py (at least these):
 doStuff
  1. camelCase, meaningless name.
  2. Description says nothing about when to use it or what it returns.
  3. Parameter `q` is cryptic and undescribed.
 ticket
  4. Name is a noun, not an action, and collides conceptually with the others.
  5. One-word description.
  6. `id` has no description or format, and isn't required although the tool can't work without it.
 Find_Tickets_By_Filter_v2
  7. Inconsistent casing and a version suffix in the name.
  8. status / priority / dept are free strings, so Claude will guess values ("urgent", "eng").
  9. `max` is a number (allows 2.5) with no bounds.
 10. Every filter is required, forcing Claude to invent values it doesn't need.
 11. `dept` and `priority` have no descriptions.
 All
 12. No additionalProperties: false, so made-up arguments pass silently.
 13. doStuff and Find_Tickets overlap: two tools for one capability confuses tool choice.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.northwind import load_tickets

STATUSES = ["open", "in_progress", "resolved", "closed"]
PRIORITIES = ["low", "medium", "high", "critical"]
DEPARTMENTS = ["Engineering", "Finance", "HR", "Operations", "Sales"]
TICKET_ID_PATTERN = r"^NW-\d{3}$"

TOOLS: list[dict] = [
    {
        "name": "search_tickets",
        "description": (
            "Search Northwind's internal support tickets (IT, engineering, finance, HR, operations, sales). "
            "Use this when the user asks about open issues, incidents, workload or the status of a problem. "
            "All filters are optional and combined with AND; omit a filter rather than guessing its value. "
            "Returns a list of tickets sorted by priority (critical first), each with id, title, status, "
            "priority, department, reporter_id, assignee_id and created date."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Free-text keywords matched against ticket title and description, e.g. 'VPN' or 'forklift'.",
                },
                "status": {"type": "string", "enum": STATUSES, "description": "Ticket workflow status."},
                "priority": {"type": "string", "enum": PRIORITIES, "description": "Ticket priority."},
                "department": {"type": "string", "enum": DEPARTMENTS, "description": "Department that owns the ticket."},
                "assignee_id": {
                    "type": "string",
                    "description": "Employee id of the assignee, e.g. 'E004' or contractor id 'C101'.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                    "description": "Maximum number of tickets to return.",
                },
            },
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_ticket",
        "description": (
            "Fetch the full details of a single Northwind ticket by its id. "
            "Use this when the user mentions a specific ticket id (like NW-104) or after search_tickets "
            "when you need one ticket's full description. Returns all ticket fields, or an error if it doesn't exist."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "string",
                    "pattern": TICKET_ID_PATTERN,
                    "description": "Ticket id in the form NW-<3 digits>, e.g. 'NW-104'.",
                },
            },
            "required": ["ticket_id"],
            "additionalProperties": False,
        },
    },
]


def _check(value: str | None, allowed: list[str], field: str) -> None:
    if value is not None and value not in allowed:
        raise ValueError(f"Unknown {field} '{value}'. Use one of: {', '.join(allowed)}")


def search_tickets(
    text: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    department: str | None = None,
    assignee_id: str | None = None,
    limit: int = 10,
) -> list[dict]:
    _check(status, STATUSES, "status")
    _check(priority, PRIORITIES, "priority")
    _check(department, DEPARTMENTS, "department")
    limit = max(1, min(int(limit), 50))

    results = []
    for t in load_tickets():
        if status and t["status"] != status:
            continue
        if priority and t["priority"] != priority:
            continue
        if department and t["department"] != department:
            continue
        if assignee_id and t["assignee_id"] != assignee_id:
            continue
        if text and text.lower() not in (t["title"] + " " + t["description"]).lower():
            continue
        results.append(t)

    results.sort(key=lambda t: (-PRIORITIES.index(t["priority"]), t["id"]))
    return results[:limit]


def get_ticket(ticket_id: str) -> dict:
    if not re.match(TICKET_ID_PATTERN, ticket_id or ""):
        raise ValueError(f"Malformed ticket id '{ticket_id}'. Expected the format NW-104.")
    for t in load_tickets():
        if t["id"] == ticket_id:
            return t
    raise ValueError(f"Ticket {ticket_id} not found. Use search_tickets to find valid ids.")
