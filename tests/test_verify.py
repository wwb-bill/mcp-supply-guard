"""Tests for baseline verification."""

from mcp_supply_guard import (
    ToolDef, fingerprint, verify, load_tools, scan_risk,
)


def _base(tools):
    return [fingerprint(t) for t in tools]


class TestVerify:
    def test_identical_clean(self):
        tools = [ToolDef(name="search", description="d", input_schema={})]
        report = verify(tools, _base(tools))
        assert report.clean is True
        assert report.findings == []

    def test_added_tool(self):
        base = [ToolDef(name="search", description="d")]
        cur = [ToolDef(name="search", description="d"), ToolDef(name="delete", description="x")]
        report = verify(cur, _base(base))
        assert any(f.kind == "added" and f.severity == "error" for f in report.findings)
        assert report.clean is False

    def test_removed_tool(self):
        base = [ToolDef(name="search", description="d"), ToolDef(name="audit", description="a")]
        cur = [ToolDef(name="search", description="d")]
        report = verify(cur, _base(base))
        assert any(f.kind == "removed" for f in report.findings)

    def test_modified_tool(self):
        base = [ToolDef(name="search", description="safe description")]
        cur = [ToolDef(name="search", description="now executes arbitrary shell commands")]
        report = verify(cur, _base(base))
        modified = [f for f in report.findings if f.kind == "modified"]
        assert len(modified) == 1
        assert modified[0].severity == "error"
        assert modified[0].old_sha != modified[0].new_sha

    def test_empty_current(self):
        base = [ToolDef(name="a", description="d")]
        report = verify([], _base(base))
        assert any(f.kind == "removed" for f in report.findings)

    def test_summary_shape(self):
        base = [ToolDef(name="a", description="d")]
        cur = [ToolDef(name="a", description="changed!"), ToolDef(name="b", description="x")]
        s = verify(cur, _base(base)).summary()
        assert s["clean"] is False
        assert s["current_count"] == 2
        assert "findings" in s


class TestRiskScan:
    def test_clean(self):
        tools = [ToolDef(name="search", description="Search the index",
                         input_schema={"properties": {"q": {"type": "string"}}})]
        assert scan_risk(tools) == []

    def test_danger_description(self):
        tools = [ToolDef(name="run", description="Execute shell commands via subprocess")]
        findings = scan_risk(tools)
        assert any(f.severity == "error" for f in findings)

    def test_danger_param(self):
        tools = [ToolDef(name="x", input_schema={
            "properties": {"cmd": {"type": "string"}},
        })]
        findings = scan_risk(tools)
        assert any(f.kind == "risky" and f.severity == "warning" for f in findings)

    def test_text_param_not_flagged(self):
        tools = [ToolDef(name="x", input_schema={
            "properties": {"prompt": {"type": "string"}},
        })]
        assert scan_risk(tools) == []

    def test_no_name(self):
        tools = [ToolDef(name="", description="d")]
        findings = scan_risk(tools)
        assert any("no name" in f.message for f in findings)
