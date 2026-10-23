"""Module 06: ready-made tool definitions and implementations for the capstone app.

These combine Modules 03–05: good schemas, permission checks and injection defenses.
You don't need to edit this file; your work is in starter.py.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from common.northwind import load_all_docs, load_tickets, read_doc
from common.permissions import can_view_doc, can_view_ticket
from common.search import keyword_search


def _load_security():
    path = HERE.parent / "05_security" / "solution.py"
    spec = importlib.util.spec_from_file_location("capstone_security", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


security = _load_security()

STATUSES = ["open", "in_progress", "resolved", "closed"]
PRIORITIES = ["low", "medium", "high", "critical"]
DEPARTMENTS = ["Engineering", "Finance", "HR", "Operations", "Sales"]
DOC_NOT_FOUND = "Document '{slug}' not found or you don't have access to it."
TICKET_NOT_FOUND = "Ticket {tid} not found or you don't have access to it."

TOOLS: list[dict] = [
    {
        "name": "search_docs",
        "description": (
            "Keyword search over Northwind's internal documents (policies, runbooks, guides) that the "
            "current user may read. Use for any question company documentation could answer. Returns "
            "slug, title and a short snippet; call get_doc with the slug for the full text."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "A few keywords, e.g. 'meal allowance' or 'rollback'."},
                "limit": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Max results (default 5)."},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_doc",
        "description": (
            "Read the full text of one Northwind document by slug. Returns the document wrapped in "
            "<document trust=\"untrusted\"> tags, or an error if it doesn't exist or the user lacks access."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"slug": {"type": "string", "description": "Document slug from search_docs, e.g. 'deploy-runbook'."}},
            "required": ["slug"],
            "additionalProperties": False,
        },
    },
    {
        "name": "search_tickets",
        "description": (
            "Search Northwind support tickets the current user may see. Use for questions about issues, "
            "incidents or workload. All filters are optional; omit rather than guess. Returns tickets "
            "sorted by priority, critical first."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Keywords matched in title or description."},
                "status": {"type": "string", "enum": STATUSES, "description": "Workflow status."},
                "priority": {"type": "string", "enum": PRIORITIES, "description": "Priority."},
                "department": {"type": "string", "enum": DEPARTMENTS, "description": "Owning department."},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "description": "Max results (default 10)."},
            },
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_ticket",
        "description": "Fetch one ticket by id (e.g. NW-104) if the current user may see it.",
        "input_schema": {
            "type": "object",
            "properties": {"ticket_id": {"type": "string", "pattern": r"^NW-\d{3}$", "description": "Ticket id like NW-104."}},
            "required": ["ticket_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "whoami",
        "description": "Return the current user's name, role and department. Use to explain what they can access.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]


# ---------- implementations: `user` always comes from the app session, never from the model ----------

def tool_search_docs(user: dict, query: str, limit: int = 5) -> list[dict]:
    visible = [(m, security.sanitize_document(b)[0]) for m, b in load_all_docs() if can_view_doc(user, m)]
    return keyword_search(visible, query, limit)


def tool_get_doc(user: dict, slug: str) -> str:
    try:
        meta, body = read_doc(slug)
    except FileNotFoundError:
        raise LookupError(DOC_NOT_FOUND.format(slug=slug)) from None
    if not can_view_doc(user, meta):
        raise LookupError(DOC_NOT_FOUND.format(slug=slug))
    clean, _ = security.sanitize_document(body)
    return security.wrap_untrusted(slug, f"# {meta['title']}\n\n{clean}")


def tool_search_tickets(user: dict, text=None, status=None, priority=None, department=None, limit: int = 10) -> list[dict]:
    for value, allowed, field in ((status, STATUSES, "status"), (priority, PRIORITIES, "priority"), (department, DEPARTMENTS, "department")):
        if value is not None and value not in allowed:
            raise ValueError(f"Unknown {field} '{value}'. Use one of: {', '.join(allowed)}")
    out = []
    for t in load_tickets():
        if not can_view_ticket(user, t):
            continue
        if status and t["status"] != status or priority and t["priority"] != priority:
            continue
        if department and t["department"] != department:
            continue
        if text and text.lower() not in (t["title"] + " " + t["description"]).lower():
            continue
        out.append(t)
    out.sort(key=lambda t: (-PRIORITIES.index(t["priority"]), t["id"]))
    return out[: max(1, min(int(limit), 50))]


def tool_get_ticket(user: dict, ticket_id: str) -> dict:
    if not re.match(r"^NW-\d{3}$", ticket_id or ""):
        raise ValueError(f"Malformed ticket id '{ticket_id}'. Expected the format NW-104.")
    for t in load_tickets():
        if t["id"] == ticket_id and can_view_ticket(user, t):
            return t
    raise LookupError(TICKET_NOT_FOUND.format(tid=ticket_id))


def tool_whoami(user: dict) -> dict:
    return {k: user[k] for k in ("id", "name", "role", "department")}


IMPLEMENTATIONS = {
    "search_docs": tool_search_docs,
    "get_doc": tool_get_doc,
    "search_tickets": tool_search_tickets,
    "get_ticket": tool_get_ticket,
    "whoami": tool_whoami,
}


def to_text(result) -> str:
    return result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
