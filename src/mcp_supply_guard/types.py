"""Core types for mcp-supply-guard."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class ToolDef:
    """A normalized MCP tool definition."""

    name: str
    description: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description,
                "input_schema": self.input_schema}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ToolDef:
        return cls(name=d.get("name", ""),
                   description=d.get("description", ""),
                   input_schema=d.get("input_schema", {}))


@dataclass
class ToolFingerprint:
    """A content hash of one tool definition."""

    name: str
    sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ToolFingerprint:
        return cls(name=d.get("name", ""), sha256=d.get("sha256", ""))


@dataclass
class SupplyFinding:
    """A supply-chain integrity finding."""

    kind: str  # added | modified | removed | risky
    severity: str  # info | warning | error
    tool: str
    message: str
    old_sha: str = ""
    new_sha: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SupplyReport:
    """Verification report: current tools vs locked baseline."""

    locked_count: int = 0
    current_count: int = 0
    findings: list[SupplyFinding] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not any(f.severity in ("warning", "error") for f in self.findings)

    def summary(self) -> dict[str, Any]:
        return {
            "locked_count": self.locked_count,
            "current_count": self.current_count,
            "clean": self.clean,
            "findings": [f.to_dict() for f in self.findings],
        }
