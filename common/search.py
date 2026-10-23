"""Ready-made keyword search (the Module 02 solution), reused by later modules."""
from __future__ import annotations


def keyword_search(docs: list[tuple[dict, str]], query: str, limit: int = 5) -> list[dict]:
    words = [w for w in query.lower().split() if len(w) >= 3]
    if not words:
        return []
    results = []
    for meta, body in docs:
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
