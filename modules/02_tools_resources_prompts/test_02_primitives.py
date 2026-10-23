import asyncio

from common.labtools import load_target

lab = load_target(__file__)


def test_doc_resource():
    text = lab.get_doc_resource("expense-policy")
    assert text.startswith("# Expense Policy\n\n")
    assert "EUR 45" in text


def test_index_resource():
    index = lab.doc_index()
    lines = index.strip().splitlines()
    assert len(lines) == 12
    assert "- Deploy Runbook (docs://deploy-runbook)" in lines


def test_search_ranks_best_match_first():
    assert lab.search_docs("rollback")[0]["slug"] == "deploy-runbook"
    assert lab.search_docs("meal allowance")[0]["slug"] == "expense-policy"


def test_search_result_shape_and_limit():
    results = lab.search_docs("policy", limit=2)
    assert len(results) <= 2
    for r in results:
        assert set(r) == {"slug", "title", "score", "snippet"}
        assert r["score"] > 0
        assert len(r["snippet"]) <= 160


def test_search_ignores_short_words_and_no_match():
    assert lab.search_docs("a an") == []
    assert lab.search_docs("zebra quantum") == []


def test_prompt_mentions_resource():
    text = lab.summarize_policy("remote-work-policy")
    assert "docs://remote-work-policy" in text


def test_everything_is_registered():
    templates = [t.uriTemplate for t in asyncio.run(lab.mcp.list_resource_templates())]
    resources = [str(r.uri) for r in asyncio.run(lab.mcp.list_resources())]
    prompts = [p.name for p in asyncio.run(lab.mcp.list_prompts())]
    tools = [t.name for t in asyncio.run(lab.mcp.list_tools())]
    assert "docs://{slug}" in templates
    assert "northwind://index" in resources
    assert "summarize_policy" in prompts
    assert "search_docs" in tools
