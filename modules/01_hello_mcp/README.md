# Module 01 — Hello MCP

**Goal:** build your first MCP server, run it, and connect it to Claude Desktop.

**Exam topics:** what MCP is, the server/client split, stdio transport, how tool docstrings become tool descriptions.

## Concepts (5-minute read)

An MCP server is a small program that *offers capabilities* (tools, resources, prompts) to an MCP client such as Claude Desktop or Claude Code. The client starts your server as a subprocess and they talk over **stdio** (standard input/output) using JSON-RPC.

With the Python SDK's `FastMCP`, a tool is just a decorated function:

- The **function name** becomes the tool name.
- The **docstring** becomes the description Claude reads when deciding whether to call it. Write it for Claude, not for humans.
- **Type hints** become the input schema.

> ⚠️ Never `print()` to stdout in a stdio server. Stdout is the protocol channel, so stray prints corrupt messages. Log to stderr instead.

## Exercises

Open `starter.py`.

1. **`list_docs()`** — return one dict per document with keys `slug`, `title`, `department`, sorted by `slug`. Do **not** include the body (keep tool output small; Claude can fetch bodies later).
2. **`count_docs_by_department()`** — return a dict like `{"Engineering": 3, "HR": 4, ...}`.
3. Improve both docstrings so Claude would know *when* to use each tool.

Run the tests:

```bash
pytest modules/01_hello_mcp
```

## Connect it to Claude Desktop

Add this inside `mcpServers` in `claude_desktop_config.json` (adjust the paths to where you keep the labs and your Python):

```json
"northwind": {
  "command": "/full/path/to/.venv/bin/python",
  "args": ["/full/path/to/ai-api-starter-mcp-labs/modules/01_hello_mcp/starter.py"]
}
```

Quit Claude Desktop fully (Cmd+Q), reopen, and ask: *"What documents does Northwind have?"*

Alternatively, test without Claude using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector .venv/bin/python modules/01_hello_mcp/starter.py
```

## Check your understanding

- Why does the client start the server, not the other way around?
- What would happen if `list_docs` returned the full text of every doc?
- Where does Claude see your docstring?
