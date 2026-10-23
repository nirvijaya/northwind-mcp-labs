import re

import pytest

from common.labtools import load_target

lab = load_target(__file__)


def _tool(name):
    tools = {t["name"]: t for t in lab.TOOLS}
    assert name in tools, f"TOOLS is missing '{name}'"
    return tools[name]


# ---------- schema quality ----------

def test_exactly_two_snake_case_tools():
    names = sorted(t["name"] for t in lab.TOOLS)
    assert names == ["get_ticket", "search_tickets"]
    for n in names:
        assert re.fullmatch(r"[a-z][a-z0-9_]*", n)


@pytest.mark.parametrize("name", ["search_tickets", "get_ticket"])
def test_descriptions_and_strict_schemas(name):
    tool = _tool(name)
    assert len(tool["description"]) >= 100, "say what it does, when to use it, what it returns"
    schema = tool["input_schema"]
    assert schema["type"] == "object"
    assert schema.get("additionalProperties") is False
    for prop, spec in schema["properties"].items():
        assert spec.get("description"), f"{name}.{prop} needs a description"


def test_search_tickets_schema():
    schema = _tool("search_tickets")["input_schema"]
    props = schema["properties"]
    assert schema.get("required", []) == [], "filters should be optional"
    assert set(props["status"]["enum"]) == {"open", "in_progress", "resolved", "closed"}
    assert set(props["priority"]["enum"]) == {"low", "medium", "high", "critical"}
    assert set(props["department"]["enum"]) == {"Engineering", "Finance", "HR", "Operations", "Sales"}
    assert props["limit"]["type"] == "integer"
    assert props["limit"]["minimum"] == 1 and props["limit"]["maximum"] == 50


def test_get_ticket_schema():
    schema = _tool("get_ticket")["input_schema"]
    assert schema["required"] == ["ticket_id"]
    pattern = schema["properties"]["ticket_id"]["pattern"]
    assert re.match(pattern, "NW-104")
    assert not re.match(pattern, "104")
    assert not re.match(pattern, "nw-104x")


# ---------- implementation ----------

def test_search_filters_combine():
    ids = [t["id"] for t in lab.search_tickets(status="open", priority="critical", department="Engineering")]
    assert ids == ["NW-104"]


def test_search_sorting():
    ids = [t["id"] for t in lab.search_tickets(department="Engineering")]
    assert ids == ["NW-104", "NW-103", "NW-120", "NW-105", "NW-106", "NW-121"]


def test_search_text_is_case_insensitive():
    assert [t["id"] for t in lab.search_tickets(text="vpn")] == ["NW-101"]


def test_search_limit_is_clamped():
    assert len(lab.search_tickets(limit=0)) == 1
    assert len(lab.search_tickets(limit=999)) == 24


def test_helpful_validation_errors():
    with pytest.raises(ValueError) as err:
        lab.search_tickets(status="pending")
    msg = str(err.value)
    assert "pending" in msg and "in_progress" in msg


def test_get_ticket():
    assert lab.get_ticket("NW-117")["title"] == "Forklift 3 hydraulic leak"
    with pytest.raises(ValueError, match="NW-104"):
        lab.get_ticket("117")
    with pytest.raises(ValueError, match="not found"):
        lab.get_ticket("NW-999")
