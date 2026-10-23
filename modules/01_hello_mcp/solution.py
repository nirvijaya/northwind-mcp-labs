"""Module 01 reference solution."""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP

from common.northwind import list_doc_slugs, read_doc

mcp = FastMCP("northwind-knowledge")


@mcp.tool()
def list_docs() -> list[dict]:
    """List every document in Northwind Logistics' internal knowledge base.

    Returns slug, title and owning department for each document, without the
    body text. Use this first when the user asks what documentation exists or
    when you need a document's slug before reading it.
    """
    docs = []
    for slug in list_doc_slugs():
        meta, _body = read_doc(slug)
        docs.append({"slug": slug, "title": meta["title"], "department": meta["department"]})
    return docs


@mcp.tool()
def count_docs_by_department() -> dict[str, int]:
    """Count Northwind documents per owning department.

    Use when the user asks which teams own documentation or how much
    documentation each department has.
    """
    counts = Counter(read_doc(slug)[0]["department"] for slug in list_doc_slugs())
    return dict(sorted(counts.items()))


if __name__ == "__main__":
    mcp.run()
