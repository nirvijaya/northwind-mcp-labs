import asyncio

from common.labtools import load_target

lab = load_target(__file__)


def test_server_name():
    assert lab.mcp.name == "northwind-knowledge"


def test_list_docs_shape():
    docs = lab.list_docs()
    assert len(docs) == 12
    assert docs == sorted(docs, key=lambda d: d["slug"])
    for d in docs:
        assert set(d) == {"slug", "title", "department"}, "only slug, title, department — no body"


def test_list_docs_content():
    by_slug = {d["slug"]: d for d in lab.list_docs()}
    assert by_slug["deploy-runbook"]["title"] == "Deploy Runbook"
    assert by_slug["deploy-runbook"]["department"] == "Engineering"


def test_count_by_department():
    assert lab.count_docs_by_department() == {
        "Engineering": 3, "Finance": 2, "HR": 4, "Operations": 2, "Sales": 1,
    }


def test_tools_are_registered_with_real_descriptions():
    tools = {t.name: t for t in asyncio.run(lab.mcp.list_tools())}
    assert {"list_docs", "count_docs_by_department"} <= set(tools)
    for name in ("list_docs", "count_docs_by_department"):
        desc = tools[name].description or ""
        assert "TODO" not in desc, f"{name}: replace the TODO docstring"
        assert len(desc) >= 60, f"{name}: a description this short won't help Claude choose the tool"
