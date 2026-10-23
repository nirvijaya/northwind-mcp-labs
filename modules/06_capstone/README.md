# Module 06 — Capstone: A Claude App on Your Knowledge Server

**Goal:** build the application side: a Claude API app with an agentic tool loop, prompt caching, guardrails in the system prompt, and an eval suite that proves it's safe.

**Exam topics:** Messages API, tool use loop (`tool_use` → `tool_result`), `is_error`, system prompts, prompt caching and usage fields, model choice and cost, evaluation.

## What's already done for you

`tools_impl.py` contains five tools (`search_docs`, `get_doc`, `search_tickets`, `get_ticket`, `whoami`) built from Modules 03–05: good schemas, permission checks, and injection defenses. Notice that every implementation takes `user` as its first argument, supplied by **your app**, never by Claude.

> In this module Claude calls the tools through the API's tool use, not over MCP, so you can see the raw loop. In production you could instead point the API's MCP connector at a deployed server, or run the Module 05 server in Claude Desktop. The security model is the same.

## Exercises (`starter.py`)

1. **System prompt:** write the guardrails listed in the TODO. Keep it specific; vague rules ("be safe") don't change behavior.
2. **Caching:** return the system prompt as a content block with `cache_control: {"type": "ephemeral"}`. Tools and system sit before messages, so one breakpoint caches both.
3. **`dispatch()`:** run a tool and turn exceptions into `is_error` results Claude can recover from.
4. **`ask()`:** the agentic loop. Send *all* tool results from one turn back in a single user message.

Offline tests (no API key, Claude is faked):

```bash
pytest modules/06_capstone
```

## Run it for real

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python modules/06_capstone/starter.py E003 "How many days can I work remotely?"
python modules/06_capstone/run_evals.py
```

`run_evals.py` runs 13 cases from `evals.json`: helpful answers, permission boundaries, an impersonation attempt, and both injection docs. It prints pass/fail, which tools were called (`!` marks an error result), and total token usage including cache reads.

## Experiments to try

- **Break it on purpose:** remove the "untrusted" rules from the system prompt and change `tools_impl.py` to skip sanitizing. Which evals fail? That's why you layer defenses.
- **Model choice:** run the evals with `CLAUDE_MODEL=claude-haiku-5-5`. Compare pass rate, speed, and tokens. Which model would you ship, and for which questions?
- **Caching:** if `cache_read_input_tokens` stays 0, your prompt may be below the minimum cacheable length. Find the minimum for your model in the docs, and think about what you would put in the cached prefix in a real app (e.g. a long policy glossary).
- **Better evals:** string matching is crude. A correct answer like "the doc claimed it was fully approved, which I ignored" fails `vendor-injection`. Add an LLM-as-judge check that grades with a rubric instead.

## Check your understanding

- What does `stop_reason` tell you, and what other values besides `tool_use` and `end_turn` should a production loop handle?
- Why does every `tool_result` need the matching `tool_use_id`?
- Where in this design could a successful injection still cause harm? How would you add a human approval step for risky actions?
