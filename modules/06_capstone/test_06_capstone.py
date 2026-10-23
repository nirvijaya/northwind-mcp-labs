"""Offline tests for the capstone. No API key needed: Claude is replaced by a scripted fake."""
import json
from types import SimpleNamespace as NS

import pytest

from common.labtools import load_target
from common.northwind import get_employee

lab = load_target(__file__)


# ---------- a scripted fake of client.messages.create ----------

def text_block(text):
    return NS(type="text", text=text)


def tool_block(id_, name, input_):
    return NS(type="tool_use", id=id_, name=name, input=input_)


def response(blocks, stop_reason, cache_read=0):
    usage = NS(input_tokens=100, output_tokens=20, cache_read_input_tokens=cache_read, cache_creation_input_tokens=None)
    return NS(content=blocks, stop_reason=stop_reason, usage=usage)


class FakeClient:
    def __init__(self, script):
        self.script = list(script)
        self.calls = []
        self.messages = self

    def create(self, **kwargs):
        self.calls.append(json.loads(json.dumps(kwargs, default=lambda o: vars(o))))
        return self.script.pop(0)


# ---------- system prompt and caching ----------

def test_system_prompt_covers_the_essentials():
    p = lab.SYSTEM_PROMPT.lower()
    assert "todo" not in p
    assert "untrusted" in p, "tell Claude that <document trust=\"untrusted\"> content is data"
    assert "access" in p, "tell Claude how to handle 'no access' errors"


def test_build_system_enables_caching():
    blocks = lab.build_system()
    assert blocks[-1]["type"] == "text"
    assert blocks[-1]["cache_control"] == {"type": "ephemeral"}


# ---------- dispatch ----------

def test_dispatch_success_and_errors():
    priya = get_employee("E003")
    content, err = lab.dispatch("get_doc", {"slug": "deploy-runbook"}, priya)
    assert not err and "nwctl rollback" in content

    content, err = lab.dispatch("get_doc", {"slug": "salary-bands-2026"}, priya)
    assert err and "58,000" not in content

    content, err = lab.dispatch("search_tickets", {"status": "pending"}, priya)
    assert err and "in_progress" in content

    content, err = lab.dispatch("delete_everything", {}, priya)
    assert err and "search_docs" in content

    content, err = lab.dispatch("get_doc", {"slug": "x", "user_id": "E001"}, priya)
    assert err, "unexpected arguments (like a smuggled user_id) must be rejected, not crash"


# ---------- the tool loop ----------

def test_ask_runs_tools_and_returns_answer():
    fake = FakeClient([
        response([text_block("Let me check."), tool_block("t1", "search_docs", {"query": "remote"}),
                  tool_block("t2", "get_doc", {"slug": "remote-work-policy"})], "tool_use"),
        response([text_block("Up to 3 days per week (Remote Work Policy).")], "end_turn", cache_read=80),
    ])
    result = lab.ask("How many remote days?", "E003", client=fake)

    assert result["answer"] == "Up to 3 days per week (Remote Work Policy)."
    assert [c["name"] for c in result["tool_calls"]] == ["search_docs", "get_doc"]
    assert result["usage"]["input_tokens"] == 200
    assert result["usage"]["cache_read_input_tokens"] == 80

    second = fake.calls[1]
    tool_results = second["messages"][-1]["content"]
    assert second["messages"][-1]["role"] == "user"
    assert [r["tool_use_id"] for r in tool_results] == ["t1", "t2"], "send all results in ONE user message"
    assert all(r["type"] == "tool_result" for r in tool_results)
    assert "3 days" in tool_results[1]["content"]
    assert second["tools"] and second["system"][-1].get("cache_control")


def test_ask_reports_tool_errors_to_claude():
    fake = FakeClient([
        response([tool_block("t1", "get_doc", {"slug": "q4-workforce-planning"})], "tool_use"),
        response([text_block("I couldn't find that or you may not have access.")], "end_turn"),
    ])
    result = lab.ask("Layoff plans?", "C102", client=fake)
    sent = fake.calls[1]["messages"][-1]["content"][0]
    assert sent["is_error"] is True
    assert "12 roles" not in sent["content"]
    assert result["tool_calls"][0]["is_error"] is True


def test_identity_is_not_model_controlled():
    for tool in lab.TOOLS if hasattr(lab, "TOOLS") else []:
        assert "user_id" not in tool["input_schema"]["properties"]
    with pytest.raises(PermissionError):
        lab.ask("hi", "X999", client=FakeClient([]))


def test_loop_stops_after_max_turns():
    looping = [response([tool_block(f"t{i}", "whoami", {})], "tool_use") for i in range(3)]
    with pytest.raises(RuntimeError):
        lab.ask("loop", "E003", client=FakeClient(looping), max_turns=3)
