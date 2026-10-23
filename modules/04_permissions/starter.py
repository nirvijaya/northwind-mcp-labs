"""Module 04 starter: permission-aware MCP server.

Identity comes from the NORTHWIND_USER_ID environment variable, never from a tool argument.
"""
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
    # TODO: read NORTHWIND_USER_ID; raise PermissionError if missing or unknown.
    raise NotImplementedError


def can_view_doc(user: dict, meta: dict) -> bool:
    # TODO: apply the document rules from README.md
    raise NotImplementedError


def can_view_ticket(user: dict, ticket: dict) -> bool:
    # TODO: apply the ticket rules from README.md
    raise NotImplementedError


@mcp.tool()
def whoami() -> dict:
    """Return the name, role and department of the person using this assistant."""
    # TODO
    raise NotImplementedError


@mcp.tool()
def search_docs(query: str, limit: int = 5) -> list[dict]:
    """Keyword search over the Northwind documents the current user may read."""
    # TODO: only search docs that pass can_view_doc. Use keyword_search(docs, query, limit).
    raise NotImplementedError


@mcp.tool()
def get_doc(slug: str) -> str:
    """Read one Northwind document (as Markdown) by slug, if the current user may read it."""
    # TODO: raise LookupError(NOT_FOUND.format(slug=slug)) for BOTH missing and forbidden docs.
    raise NotImplementedError


@mcp.tool()
def search_tickets(status: str | None = None, limit: int = 20) -> list[dict]:
    """List Northwind tickets visible to the current user, optionally filtered by status."""
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    mcp.run()
