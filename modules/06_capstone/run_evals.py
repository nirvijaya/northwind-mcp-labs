"""Run the capstone evals against the real Claude API.

    export ANTHROPIC_API_KEY=...
    python modules/06_capstone/run_evals.py                 # your starter.py
    LAB_TARGET=solution python modules/06_capstone/run_evals.py
    python modules/06_capstone/run_evals.py vpn-injection   # run one eval by id

Costs a few cents per full run. Prints pass/fail per eval and total token usage.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from common.labtools import load_target

app = load_target(str(HERE / "run_evals.py"))


def check(case: dict, answer: str) -> list[str]:
    text = answer.lower()
    problems = []
    if case["must_include_any"] and not any(s.lower() in text for s in case["must_include_any"]):
        problems.append(f"missing any of {case['must_include_any']}")
    leaked = [s for s in case["must_not_include"] if s.lower() in text]
    if leaked:
        problems.append(f"contains forbidden {leaked}")
    return problems


def main() -> int:
    cases = json.loads((HERE / "evals.json").read_text())
    if len(sys.argv) > 1:
        cases = [c for c in cases if c["id"] in sys.argv[1:]]

    totals = {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    passed = 0
    for case in cases:
        try:
            result = app.ask(case["question"], case["user_id"])
            problems = check(case, result["answer"])
            for k in totals:
                totals[k] += result["usage"].get(k, 0)
            tools = ", ".join(c["name"] + ("!" if c["is_error"] else "") for c in result["tool_calls"]) or "-"
        except Exception as err:  # noqa: BLE001 — report and keep going
            problems, tools, result = [f"crashed: {err!r}"], "-", {"answer": ""}
        ok = not problems
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  {case['id']:<20} [{case['user_id']}] tools: {tools}")
        for p in problems:
            print(f"        ↳ {p}")
            print(f"        answer: {result['answer'][:300]!r}")

    print(f"\n{passed}/{len(cases)} passed")
    print("usage:", totals)
    if totals["cache_read_input_tokens"] == 0:
        print("note: no cache reads; is cache_control set, and is the prompt above the minimum cacheable length?")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
