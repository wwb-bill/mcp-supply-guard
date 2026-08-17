"""Tool-definition fingerprinting — normalized content hashes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .types import ToolDef, ToolFingerprint


def normalize(tool: ToolDef) -> str:
    """Stable serialization: sorted keys, compact JSON."""
    return json.dumps(tool.to_dict(), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def fingerprint(tool: ToolDef) -> ToolFingerprint:
    """Content hash of a tool definition (name + description + schema)."""
    digest = hashlib.sha256(normalize(tool).encode("utf-8")).hexdigest()
    return ToolFingerprint(name=tool.name, sha256=digest)


def load_tools(path: str | Path) -> list[ToolDef]:
    """Load tool definitions from a JSON file.

    Accepts: {"tools": [...]}, a bare list, or a tools list where each
    entry has {name, description?, inputSchema?} (schema key aliases).
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        items = data.get("tools", [])
    else:
        items = data
    tools = []
    for d in items:
        schema = d.get("inputSchema") or d.get("input_schema") or {}
        tools.append(ToolDef(name=d.get("name", ""),
                             description=d.get("description", ""),
                             input_schema=schema))
    return tools


def save_fingerprints(items: list[ToolFingerprint], path: str | Path) -> None:
    payload = [i.to_dict() for i in items]
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_fingerprints(path: str | Path) -> list[ToolFingerprint]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [ToolFingerprint.from_dict(d) for d in data]
