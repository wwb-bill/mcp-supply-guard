"""Tests for fingerprinting."""

import json
from pathlib import Path

from mcp_supply_guard import (
    ToolDef, normalize, fingerprint, load_tools, save_fingerprints, load_fingerprints,
)


class TestNormalize:
    def test_stable_serialization(self):
        a = ToolDef(name="search", description="d", input_schema={"type": "object"})
        b = ToolDef(name="search", description="d", input_schema={"type": "object"})
        assert normalize(a) == normalize(b)

    def test_key_order_insensitive(self):
        a = ToolDef(name="x", description="d", input_schema={"b": 1, "a": 2})
        b = ToolDef(name="x", description="d", input_schema={"a": 2, "b": 1})
        assert normalize(a) == normalize(b)


class TestFingerprint:
    def test_deterministic(self):
        t = ToolDef(name="search", description="d", input_schema={})
        assert fingerprint(t).sha256 == fingerprint(t).sha256

    def test_differs_on_description(self):
        a = ToolDef(name="search", description="safe")
        b = ToolDef(name="search", description="exec shell commands")
        assert fingerprint(a).sha256 != fingerprint(b).sha256

    def test_differs_on_schema(self):
        a = ToolDef(name="x", input_schema={"properties": {}})
        b = ToolDef(name="x", input_schema={"properties": {"cmd": {"type": "string"}}})
        assert fingerprint(a).sha256 != fingerprint(b).sha256

    def test_sha_format(self):
        f = fingerprint(ToolDef(name="x"))
        assert len(f.sha256) == 64  # hex sha256


class TestLoadTools:
    def test_list_format(self, tmp_path: Path):
        p = tmp_path / "tools.json"
        p.write_text(json.dumps([
            {"name": "search", "description": "d", "inputSchema": {"type": "object"}},
        ]), encoding="utf-8")
        tools = load_tools(p)
        assert len(tools) == 1
        assert tools[0].name == "search"

    def test_object_format(self, tmp_path: Path):
        p = tmp_path / "tools.json"
        p.write_text(json.dumps({"tools": [
            {"name": "a", "input_schema": {}},
        ]}), encoding="utf-8")
        assert load_tools(p)[0].name == "a"

    def test_schema_alias(self, tmp_path: Path):
        p = tmp_path / "tools.json"
        p.write_text(json.dumps([
            {"name": "a", "inputSchema": {"type": "object"}},
        ]), encoding="utf-8")
        tools = load_tools(p)
        assert tools[0].input_schema == {"type": "object"}


class TestPersistence:
    def test_roundtrip(self, tmp_path: Path):
        p = tmp_path / "baseline.json"
        t = ToolDef(name="search", description="d")
        save_fingerprints([fingerprint(t)], p)
        loaded = load_fingerprints(p)
        assert len(loaded) == 1
        assert loaded[0].name == "search"
        assert loaded[0].sha256 == fingerprint(t).sha256
