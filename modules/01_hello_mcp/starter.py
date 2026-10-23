"""Module 01 starter: your first MCP server.

Run directly:  python modules/01_hello_mcp/starter.py
Run tests:     pytest modules/01_hello_mcp
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP

from common.northwind import list_doc_slugs, read_doc

mcp = FastMCP("northwind-knowledge")


@mcp.tool()
def list_docs() -> list[dict]:
    """TODO: write a description Claude can use to decide when to call this tool."""
    # TODO: for each slug from list_doc_slugs(), call read_doc(slug) and
    # return {"slug": ..., "title": ..., "department": ...}. Sorted by slug.
    raise NotImplementedError


@mcp.tool()
def count_docs_by_department() -> dict[str, int]:
    """TODO: write a description."""
    # TODO: return {"Engineering": 3, "HR": 4, ...}
    raise NotImplementedError


if __name__ == "__main__":
    mcp.run()  # stdio transport by default
