# Module 02 — Tools vs. Resources vs. Prompts

**Goal:** expose the same knowledge base through all three MCP primitives and learn when to use each.

**Exam topics:** MCP primitives, resource URIs and templates, model-controlled vs. application-controlled vs. user-controlled capabilities.

## Concepts

| Primitive | Who decides to use it | Good for |
|-----------|----------------------|----------|
| **Tool** | The *model* (Claude chooses to call it) | Actions and queries: search, create, update |
| **Resource** | The *application* or user (attached as context) | Read-only content with a stable URI, like a file or record |
| **Prompt** | The *user* (picked from a menu, e.g. a slash command) | Reusable, parameterized instructions |

A **resource template** like `docs://{slug}` lets one function serve many URIs.

## Exercises

Open `starter.py`.

1. **Resource template `docs://{slug}`** — return the document as Markdown: a `# Title` line, a blank line, then the body.
2. **Static resource `northwind://index`** — return a Markdown bullet list: `- Title (docs://slug)` per document.
3. **Tool `search_docs(query, limit=5)`** — simple keyword search:
   - Split the query into lowercase words; ignore words shorter than 3 characters.
   - Score = 3 × (matches in title) + (matches in body), counting each query word's occurrences.
   - Return `[{"slug", "title", "score", "snippet"}]` with score > 0, sorted by score (high first), then slug. `snippet` is the first body line containing any query word, max 160 characters.
4. **Prompt `summarize_policy(slug)`** — return instructions asking Claude to read `docs://{slug}` and summarize it in 3 bullet points for a new employee.

```bash
pytest modules/02_tools_resources_prompts
```

## Notice the problem

Search for "salary". Anyone connected to this server can read confidential pay data. Module 04 fixes that. Leave it for now, but write down how you would fix it before you get there.

## Check your understanding

- Why is search a *tool* and the document a *resource*?
- In Claude Desktop, how does the user invoke a prompt vs. how does Claude invoke a tool?
- Real search would use embeddings. What would you change in the tool's *interface* (not implementation) if you switched?
