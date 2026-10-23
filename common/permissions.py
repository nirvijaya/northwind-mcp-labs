"""Permission rules (the Module 04 solution), shared by Modules 05 and 06.

If you haven't finished Module 04 yet, do that first — this file is its answer.
"""
from __future__ import annotations

import os

from common.northwind import get_employee

ROLE_CLASSIFICATIONS = {
    "contractor": {"public"},
    "employee": {"public", "internal"},
    "manager": {"public", "internal", "confidential"},
    "admin": {"public", "internal", "confidential", "restricted"},
}


def current_user() -> dict:
    user_id = os.environ.get("NORTHWIND_USER_ID")
    if not user_id:
        raise PermissionError("No user identity configured (NORTHWIND_USER_ID is not set).")
    user = get_employee(user_id)
    if user is None:
        raise PermissionError(f"Unknown user id '{user_id}'.")
    return user


def can_view_doc(user: dict, meta: dict) -> bool:
    role, classification = user["role"], meta["classification"]
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
