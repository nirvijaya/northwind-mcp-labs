"""Module 02 reference solution."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP

from common.northwind import list_doc_slugs, load_all_docs, read_doc

mcp = FastMCP("northwind-knowledge")


@mcp.resource("docs://{slug}")
def get_doc_resource(slug: str) -> str:
    """A single Northwind document as Markdown."""
    meta, body = read_doc(slug)
    return f"# {meta['title']}\n\n{body}"


@mcp.resource("northwind://index")
def doc_index() -> str:
    """Index of all Northwind documents."""
    lines = []
    for slug in list_doc_slugs():
        meta, _ = read_doc(slug)
        lines.append(f"- {meta['title']} (docs://{slug})")
    return "\n".join(lines)


def _query_words(query: str) -> list[str]:
    return [w for w in query.lower().split() if len(w) >= 3]


@mcp.tool()
def search_docs(query: str, limit: int = 5) -> list[dict]:
    """Keyword search across Northwind's internal documents (policies, runbooks, guides).

    Use when the user asks a question that company documentation could answer,
    e.g. about expenses, remote work, deploys or safety. Returns the best
    matches with a short snippet; read the full document via its docs://{slug}
    resource if the snippet isn't enough.
    """
    words = _query_words(query)
    if not words:
        return []
    results = []
    for meta, body in load_all_docs():
        title_l, body_l = meta["title"].lower(), body.lower()
        score = sum(3 * title_l.count(w) + body_l.count(w) for w in words)
        if score == 0:
            continue
        snippet = next(
            (line.strip() for line in body.splitlines() if any(w in line.lower() for w in words)),
            "",
        )[:160]
        results.append({"slug": meta["slug"], "title": meta["title"], "score": score, "snippet": snippet})
    results.sort(key=lambda r: (-r["score"], r["slug"]))
    return results[: max(1, min(limit, 20))]


@mcp.prompt()
def summarize_policy(slug: str) -> str:
    """Summarize a Northwind policy for a new employee."""
    return (
        f"Read the document at docs://{slug}. Summarize it for a new Northwind employee "
        "in exactly 3 bullet points of plain language. Mention any numbers, deadlines "
        "or approval rules. If something is unclear in the document, say so rather than guessing."
    )


if __name__ == "__main__":
    mcp.run()
