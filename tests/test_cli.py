"""Tests for CLI."""

import json
import os

import pytest

from mcp_supply_guard.cli import main


def _write_tools(tmp_path, tools):
    p = tmp_path / "tools.json"
    p.write_text(json.dumps(tools), encoding="utf-8")
    return p


class TestCLI:
    def _setup(self, tmp_path, capsys):
        os.chdir(tmp_path)
        p = _write_tools(tmp_path, [
            {"name": "search", "description": "Search the index",
             "inputSchema": {"type": "object", "properties": {"q": {"type": "string"}}}},
        ])
        main(["lock", str(p), "baseline.json"])
        capsys.readouterr()
        return p

    def test_lock(self, tmp_path, capsys):
        self._setup(tmp_path, capsys)
        assert (tmp_path / "baseline.json").exists()

    def test_verify_clean(self, tmp_path, capsys):
        p = self._setup(tmp_path, capsys)
        with pytest.raises(SystemExit) as exc:
            main(["verify", str(p), "baseline.json"])
        assert exc.value.code == 0
        assert "✅" in capsys.readouterr().out

    def test_verify_modified(self, tmp_path, capsys):
        self._setup(tmp_path, capsys)
        p = _write_tools(tmp_path, [
            {"name": "search", "description": "now executes shell commands",
             "inputSchema": {"type": "object", "properties": {"q": {"type": "string"}}}},
        ])
        with pytest.raises(SystemExit) as exc:
            main(["verify", str(p), "baseline.json", "--json"])
        assert exc.value.code == 1
        d = json.loads(capsys.readouterr().out)
        assert any(f["kind"] == "modified" for f in d["findings"])

    def test_risk_clean(self, tmp_path, capsys):
        p = self._setup(tmp_path, capsys)
        with pytest.raises(SystemExit) as exc:
            main(["risk", str(p)])
        assert exc.value.code == 0

    def test_risk_danger(self, tmp_path, capsys):
        os.chdir(tmp_path)
        p = _write_tools(tmp_path, [
            {"name": "exec", "description": "Run commands via os.system",
             "inputSchema": {"type": "object", "properties": {"cmd": {"type": "string"}}}},
        ])
        with pytest.raises(SystemExit) as exc:
            main(["risk", str(p), "--json"])
        assert exc.value.code == 1
        d = json.loads(capsys.readouterr().out)
        assert len(d) >= 1
