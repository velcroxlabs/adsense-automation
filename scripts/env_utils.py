#!/usr/bin/env python3
"""
Minimal environment loader for local scripts.

Falls back to parsing .env files directly when python-dotenv is not installed.
"""

from __future__ import annotations

import os
from pathlib import Path


def _load_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def load_project_env() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv()
        return
    except ImportError:
        pass

    root = Path(__file__).resolve().parents[1]
    _load_file(root / ".env")
    _load_file(root / "website" / ".env")
