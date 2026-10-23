"""Shared loaders for the fictional Northwind Logistics dataset.

You don't need to edit this file. Every module imports from it so you can
focus on MCP and Claude, not on file parsing.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DOCS_DIR = DATA_DIR / "docs"


def load_employees() -> list[dict]:
    return json.loads((DATA_DIR / "employees.json").read_text(encoding="utf-8"))


def get_employee(employee_id: str) -> dict | None:
    return next((e for e in load_employees() if e["id"] == employee_id), None)


def load_tickets() -> list[dict]:
    return json.loads((DATA_DIR / "tickets.json").read_text(encoding="utf-8"))


def load_permissions() -> dict:
    return json.loads((DATA_DIR / "permissions.json").read_text(encoding="utf-8"))


def _parse_frontmatter(raw: str) -> tuple[dict, str]:
    """Parse a tiny YAML-like header between '---' lines. No PyYAML needed."""
    meta: dict = {}
    if not raw.startswith("---"):
        return meta, raw
    _, header, body = raw.split("---", 2)
    for line in header.strip().splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if key.strip() == "allowed_ids":
            meta["allowed_ids"] = [v.strip() for v in value.split(",") if v.strip()]
        else:
            meta[key.strip()] = value
    return meta, body.lstrip("\n")


def list_doc_slugs() -> list[str]:
    return sorted(p.stem for p in DOCS_DIR.glob("*.md"))


def read_doc(slug: str) -> tuple[dict, str]:
    """Return (metadata, body) for a doc. Raises FileNotFoundError if missing."""
    path = DOCS_DIR / f"{slug}.md"
    if not path.is_file() or path.parent != DOCS_DIR:
        raise FileNotFoundError(f"No doc named '{slug}'")
    meta, body = _parse_frontmatter(path.read_text(encoding="utf-8"))
    meta["slug"] = slug
    meta.setdefault("allowed_ids", [])
    return meta, body


def load_all_docs() -> list[tuple[dict, str]]:
    return [read_doc(slug) for slug in list_doc_slugs()]
