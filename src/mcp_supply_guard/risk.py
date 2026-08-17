"""Risk scan — danger signals in tool definitions (43% of MCP servers have command injection)."""

from __future__ import annotations

import re
from typing import Any

from .types import ToolDef, SupplyFinding

_DANGER_DESC = re.compile(
    r"\b(exec|shell|bash|system|spawn|eval|child_process|run_command|subprocess|os\.system)\b",
    re.IGNORECASE)
_DANGER_PARAM = re.compile(
    r"\b(cmd|command|shell|script|executable|binary|program|path|dir|file)\b",
    re.IGNORECASE)
_FREE_TEXT = re.compile(r"\b(prompt|instructions|content|text|query)\b", re.IGNORECASE)


def scan_risk(tools: list[ToolDef]) -> list[SupplyFinding]:
    """Flag definitions whose description/schema signal command-execution danger."""
    findings: list[SupplyFinding] = []
    for t in tools:
        if not t.name:
            findings.append(SupplyFinding("risky", "error", t.name,
                                          "tool has no name"))
            continue
        if _DANGER_DESC.search(t.description):
            findings.append(SupplyFinding(
                "risky", "error", t.name,
                "description mentions command execution primitives — verify intent"))
        props = t.input_schema.get("properties", {})
        for pname, p in props.items():
            if _DANGER_PARAM.search(pname) and not _FREE_TEXT.search(pname):
                if p.get("type") == "string":
                    findings.append(SupplyFinding(
                        "risky", "warning", t.name,
                        f"string parameter '{pname}' may carry executable input"))
    return findings
