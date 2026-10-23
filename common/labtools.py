"""Test helper: lets every test run against either your starter or the solution.

    pytest modules/01_hello_mcp                       # tests your starter.py
    LAB_TARGET=solution pytest modules/01_hello_mcp   # tests solution.py
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_target(test_file: str):
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    here = Path(test_file).resolve().parent
    target = os.environ.get("LAB_TARGET", "starter")
    path = here / f"{target}.py"
    name = f"lab_{here.name}_{target}"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
