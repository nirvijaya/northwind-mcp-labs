"""Module 04 reference solution: permission-aware MCP server."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP

from common.northwind import get_employee, load_all_docs, load_tickets, read_doc
from common.search import keyword_search

mcp = FastMCP("northwind-knowledge")

ROLE_CLASSIFICATIONS = {
    "contractor": {"public"},
    "employee": {"public", "internal"},
    "manager": {"public", "internal", "confidential"},
    "admin": {"public", "internal", "confidential", "restricted"},
}
NOT_FOUND = "Document '{slug}' not found or you don't have access to it."


def current_user() -> dict:
    user_id = os.environ.get("NORTHWIND_USER_ID")
    if not user_id:
        raise PermissionError("No user identity configured (NORTHWIND_USER_ID is not set).")
    user = get_employee(user_id)
    if user is None:
        raise PermissionError(f"Unknown user id '{user_id}'.")
    return user


def can_view_doc(user: dict, meta: dict) -> bool:
    role = user["role"]
    classification = meta["classification"]

    if classification == "restricted":
        return role == "admin" or user["id"] in meta.get("allowed_ids", [])

    if classification not in ROLE_CLASSIFICATIONS.get(role, set()):
        return False

    if classification == "confidential" and role != "admin":
        return user["department"] == meta["department"]

    return True


def can_view_ticket(user: dict, ticket: dict) -> bool:
    if user["role"] == "admin":
        return True
    involved = user["id"] in (ticket["reporter_id"], ticket["assignee_id"])
    if user["role"] == "contractor":
        return involved
    return involved or ticket["department"] == user["department"]


@mcp.tool()
def whoami() -> dict:
    """Return the name, role and department of the person using this assistant.

    Use this when you need to know whose permissions apply, or to personalize an answer.
    """
    u = current_user()
    return {"id": u["id"], "name": u["name"], "role": u["role"], "department": u["department"]}


@mcp.tool()
def search_docs(query: str, limit: int = 5) -> list[dict]:
    """Keyword search over the Northwind documents the current user is allowed to read.

    Use for questions about policies, runbooks, guides and other company documentation.
    Documents the user can't access are never included.
    """
    user = current_user()
    visible = [(meta, body) for meta, body in load_all_docs() if can_view_doc(user, meta)]
    return keyword_search(visible, query, limit)


@mcp.tool()
def get_doc(slug: str) -> str:
    """Read one Northwind document as Markdown by its slug (from search_docs).

    Returns an error if the document doesn't exist or the user can't access it.
    """
    user = current_user()
    try:
        meta, body = read_doc(slug)
    except FileNotFoundError:
        raise LookupError(NOT_FOUND.format(slug=slug)) from None
    if not can_view_doc(user, meta):
        raise LookupError(NOT_FOUND.format(slug=slug))
    return f"# {meta['title']}\n\n{body}"


@mcp.tool()
def search_tickets(status: str | None = None, limit: int = 20) -> list[dict]:
    """List Northwind tickets the current user is allowed to see, optionally filtered by status
    (open, in_progress, resolved, closed). Sorted by ticket id."""
    user = current_user()
    tickets = [
        t for t in load_tickets()
        if can_view_ticket(user, t) and (status is None or t["status"] == status)
    ]
    tickets.sort(key=lambda t: t["id"])
    return tickets[: max(1, min(limit, 50))]


if __name__ == "__main__":
    mcp.run()
