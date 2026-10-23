"""Module 02 starter: tools, resources and prompts."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP

from common.northwind import list_doc_slugs, load_all_docs, read_doc

mcp = FastMCP("northwind-knowledge")


@mcp.resource("docs://{slug}")
def get_doc_resource(slug: str) -> str:
    """A single Northwind document as Markdown."""
    # TODO: return "# <title>\n\n<body>"
    raise NotImplementedError


@mcp.resource("northwind://index")
def doc_index() -> str:
    """Index of all Northwind documents."""
    # TODO: one line per doc: "- <title> (docs://<slug>)"
    raise NotImplementedError


@mcp.tool()
def search_docs(query: str, limit: int = 5) -> list[dict]:
    """TODO: describe when Claude should use this tool."""
    # TODO: implement the scoring described in README.md
    raise NotImplementedError


@mcp.prompt()
def summarize_policy(slug: str) -> str:
    """Summarize a Northwind policy for a new employee."""
    # TODO: return the instruction text
    raise NotImplementedError


if __name__ == "__main__":
    mcp.run()
