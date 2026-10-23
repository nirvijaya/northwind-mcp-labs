# Northwind MCP Labs

Hands-on practice for the **Claude Certified Developer – Foundations** exam: build a secure internal-knowledge MCP server for a fictional company, then a Claude API app on top of it.

## The scenario

**Northwind Logistics** is a mid-size freight company in Espoo. Employees keep asking the same questions ("How do I roll back a deploy?", "What's the meal allowance?") and the answers are scattered across docs and tickets. You'll give Claude secure access to that knowledge, so each person sees only what they're allowed to.

## Modules

| # | Module | You'll learn |
|---|--------|--------------|
| 01 | `01_hello_mcp` | First MCP server, stdio, connecting to Claude Desktop |
| 02 | `02_tools_resources_prompts` | When to use tools vs. resources vs. prompts |
| 03 | `03_schema_design` | Tool schemas Claude uses correctly; recoverable errors |
| 04 | `04_permissions` | Identity outside the model, role-based filtering, no data leaks |
| 05 | `05_security` | Prompt injection defenses, trust boundaries, audit logs |
| 06 | `06_capstone` | Claude API tool loop, prompt caching, guardrails, evals |

Each module has a `README.md` (concepts + exercises), `starter.py` (your work, with TODOs), `solution.py` (reference answer) and tests. Try the starter first; open the solution only after the tests make you think.

## Setup (uv)

This project uses [uv](https://docs.astral.sh/uv/). It reads `pyproject.toml` and `.python-version` (3.12), creates `.venv` and installs everything, including pytest.

```bash
cd ai-api-starter-mcp-labs
uv sync
```

Commit `uv.lock` (created by `uv sync`) so the exact versions are reproducible.

Without uv: `python3.12 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`, then replace `uv run` with nothing in the commands below.

Module 06's live runs also need an API key: `export ANTHROPIC_API_KEY=sk-ant-...`

## Running tests

```bash
uv run pytest modules/01_hello_mcp                        # test YOUR starter.py
LAB_TARGET=solution uv run pytest modules/01_hello_mcp    # test the reference solution
LAB_TARGET=solution uv run pytest                         # every module's solution
```

`uv run` always uses the project's `.venv`, so there's no need to activate it and no risk of picking up Conda or a global pytest.

Other commands work the same way, e.g. `uv run python modules/06_capstone/solution.py E003 "How many remote days?"`.

For Claude Desktop configs, point `command` at `/full/path/to/ai-api-starter-mcp-labs/.venv/bin/python` (uv creates it there), or use `"command": "uv", "args": ["run", "--directory", "/full/path/to/ai-api-starter-mcp-labs", "python", "modules/01_hello_mcp/starter.py"]`.

Starter tests fail until you complete the TODOs. That's expected.

## The data (`data/`)

- `employees.json` — 18 people across Engineering, HR, Finance, Operations and Sales, with roles `contractor`, `employee`, `manager`, `admin`.
- `tickets.json` — 24 support tickets.
- `permissions.json` — the access rules (used in Module 04).
- `docs/` — 12 Markdown documents, classified `public`, `internal`, `confidential` or `restricted`. **Two contain hidden prompt-injection attacks.** Can you find them before Module 05?

Useful test identities:

| Id | Who | Why they're interesting |
|----|-----|------------------------|
| E001 | Aino, IT admin | Sees everything, so injections are most dangerous here |
| E003 | Priya, engineer | Typical employee |
| E005 | Sofia, Head of People | Only non-admin who can read the restricted Q4 plan |
| E002 | Marcus, Eng manager | Manager, but salary bands belong to HR |
| C101 | Alex, contractor | Public docs only, own tickets only |

## Shared code (`common/`)

- `northwind.py` — data loaders.
- `search.py` — keyword search (the Module 02 solution).
- `permissions.py` — permission rules (the Module 04 solution; don't peek early).
- `labtools.py` — lets tests switch between starter and solution.

## Map to the exam

The Foundations exam weighs application building and integration heavily. These labs cover the MCP and API side: MCP primitives and servers (01–02), tool design (03), security and authorization (04–05), and the Messages API, tool use, caching and evaluation (06). Pair them with Anthropic's official course material for the rest, such as Claude Code workflows, batching and streaming.

## Ideas to go further

- Turn the Module 05 server into a **remote** MCP server (Streamable HTTP) with OAuth instead of an environment variable.
- Add a **write** tool (`create_ticket`) that requires human confirmation.
- Use the **Message Batches API** to summarize all 24 tickets overnight at lower cost.
- Add **streaming** to the capstone so answers appear as they're generated.
