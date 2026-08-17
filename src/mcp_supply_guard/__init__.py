"""mcp-supply-guard — MCP tool-definition supply-chain integrity.

2026 security data point: 43% of MCP servers have command injection
vulnerabilities, and tool definitions can mutate after approval (rug-pull
vector). This library locks a baseline of tool-definition content hashes
after review, then verifies later loads — flagging added / removed /
modified tools — plus a risk scan for command-execution danger signals.

Usage:
    from mcp_supply_guard import load_tools, fingerprint, verify, scan_risk

    baseline = [fingerprint(t) for t in load_tools("approved.json")]
    report = verify(load_tools("current.json"), baseline)
    print(report.clean, report.findings)
"""

from .types import ToolDef, ToolFingerprint, SupplyFinding, SupplyReport
from .fingerprint import normalize, fingerprint, load_tools, save_fingerprints, load_fingerprints
from .verify import verify
from .risk import scan_risk

__version__ = "0.1.0"

__all__ = [
    "ToolDef",
    "ToolFingerprint",
    "SupplyFinding",
    "SupplyReport",
    "normalize",
    "fingerprint",
    "load_tools",
    "save_fingerprints",
    "load_fingerprints",
    "verify",
    "scan_risk",
]
