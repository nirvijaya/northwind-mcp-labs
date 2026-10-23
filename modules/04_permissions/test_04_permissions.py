import pytest

from common.labtools import load_target
from common.northwind import get_employee, read_doc

lab = load_target(__file__)


def can(uid, slug):
    return lab.can_view_doc(get_employee(uid), read_doc(slug)[0])


# ---------- pure permission rules ----------

@pytest.mark.parametrize("uid, slug, expected", [
    ("C101", "employee-handbook", True),       # contractor, public
    ("C101", "remote-work-policy", False),     # contractor, internal
    ("E003", "remote-work-policy", True),      # employee, internal
    ("E003", "salary-bands-2026", False),      # employee, confidential
    ("E006", "salary-bands-2026", False),      # HR employee, still not a manager
    ("E005", "salary-bands-2026", True),       # HR manager, own department
    ("E002", "salary-bands-2026", False),      # Eng manager, other department
    ("E007", "vendor-contract-acme-freight", True),
    ("E007", "sales-commission-plan", False),
    ("E005", "q4-workforce-planning", True),   # restricted, in allowed_ids
    ("E011", "q4-workforce-planning", False),  # restricted, Operations manager
    ("E001", "q4-workforce-planning", True),   # admin
    ("E001", "sales-commission-plan", True),   # admin bypasses department
])
def test_doc_rules(uid, slug, expected):
    assert can(uid, slug) is expected


def visible_ticket_ids(uid):
    from common.northwind import load_tickets
    user = get_employee(uid)
    return sorted(t["id"] for t in load_tickets() if lab.can_view_ticket(user, t))


def test_ticket_rules():
    assert visible_ticket_ids("C103") == ["NW-115", "NW-116"]
    assert visible_ticket_ids("C102") == ["NW-117", "NW-119"]
    assert visible_ticket_ids("E010") == ["NW-101", "NW-113", "NW-114", "NW-115", "NW-116"]
    assert len(visible_ticket_ids("E001")) == 24


# ---------- identity ----------

def test_identity_comes_from_environment(monkeypatch):
    monkeypatch.delenv("NORTHWIND_USER_ID", raising=False)
    with pytest.raises(PermissionError):
        lab.current_user()
    monkeypatch.setenv("NORTHWIND_USER_ID", "X999")
    with pytest.raises(PermissionError):
        lab.current_user()
    monkeypatch.setenv("NORTHWIND_USER_ID", "E003")
    assert lab.whoami() == {"id": "E003", "name": "Priya Nair", "role": "employee", "department": "Engineering"}


def test_tools_have_no_user_id_parameter():
    import inspect
    for fn in (lab.search_docs, lab.get_doc, lab.search_tickets, lab.whoami):
        assert "user_id" not in inspect.signature(fn).parameters, "identity must not be a model-controlled argument"


# ---------- tools respect permissions ----------

def test_search_docs_filters(monkeypatch):
    monkeypatch.setenv("NORTHWIND_USER_ID", "C101")
    slugs = [r["slug"] for r in lab.search_docs("salary bands engineer")]
    assert "salary-bands-2026" not in slugs
    monkeypatch.setenv("NORTHWIND_USER_ID", "E005")
    assert lab.search_docs("salary bands")[0]["slug"] == "salary-bands-2026"


def test_get_doc_same_error_for_missing_and_forbidden(monkeypatch):
    monkeypatch.setenv("NORTHWIND_USER_ID", "E003")
    with pytest.raises(LookupError) as forbidden:
        lab.get_doc("q4-workforce-planning")
    with pytest.raises(LookupError) as missing:
        lab.get_doc("does-not-exist")
    assert str(forbidden.value).replace("q4-workforce-planning", "X") == \
           str(missing.value).replace("does-not-exist", "X")
    assert "Deploy Runbook" in lab.get_doc("deploy-runbook")


def test_get_doc_blocks_path_traversal(monkeypatch):
    monkeypatch.setenv("NORTHWIND_USER_ID", "E001")
    with pytest.raises(LookupError):
        lab.get_doc("../permissions")


def test_search_tickets_filters(monkeypatch):
    monkeypatch.setenv("NORTHWIND_USER_ID", "C103")
    assert [t["id"] for t in lab.search_tickets()] == ["NW-115", "NW-116"]
    monkeypatch.setenv("NORTHWIND_USER_ID", "E010")
    assert [t["id"] for t in lab.search_tickets(status="in_progress")] == ["NW-114"]
