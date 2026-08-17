"""CLI for mcp-supply-guard."""

from __future__ import annotations

import json
import sys

from .fingerprint import load_tools, fingerprint, save_fingerprints, load_fingerprints
from .verify import verify
from .risk import scan_risk


def _utf8_stdout() -> None:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def main(argv: list[str] | None = None) -> None:
    args = list(argv) if argv is not None else sys.argv[1:]
    if not args or args[0] in ("--help", "-h"):
        print("mcp-supply-guard — MCP tool-definition supply-chain integrity")
        print("\nUsage:")
        print("  mcp-supply-guard lock <tools.json> <baseline.json>")
        print("  mcp-supply-guard verify <tools.json> <baseline.json> [--json]")
        print("  mcp-supply-guard risk <tools.json> [--json]")
        sys.exit(0)

    cmd = args[0]

    if cmd == "lock" and len(args) >= 3:
        tools = load_tools(args[1])
        fps = [fingerprint(t) for t in tools]
        save_fingerprints(fps, args[2])
        print(f"locked {len(fps)} tool fingerprint(s) -> {args[2]}")

    elif cmd == "verify" and len(args) >= 3:
        tools = load_tools(args[1])
        baseline = load_fingerprints(args[2])
        report = verify(tools, baseline)
        if "--json" in args:
            print(json.dumps(report.summary(), indent=2, ensure_ascii=False))
        else:
            icon = "✅" if report.clean else "⚠️"
            print(f"  {icon} {report.current_count} current vs {report.locked_count} locked")
            for f in report.findings:
                sev = {"info": "ℹ️", "warning": "🟡", "error": "❌"}[f.severity]
                print(f"  {sev} [{f.severity.upper()}] {f.kind} {f.tool}: {f.message}")
        sys.exit(0 if report.clean else 1)

    elif cmd == "risk" and len(args) >= 2:
        tools = load_tools(args[1])
        findings = scan_risk(tools)
        if "--json" in args:
            print(json.dumps([f.to_dict() for f in findings], indent=2, ensure_ascii=False))
        else:
            for f in findings:
                print(f"  [{f.severity.upper()}] {f.tool}: {f.message}")
        sys.exit(0 if not findings else 1)

    else:
        print(f"Unknown: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _utf8_stdout()
    main()
