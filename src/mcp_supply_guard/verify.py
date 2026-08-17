"""Verification — compare current tool fingerprints against the locked baseline."""

from __future__ import annotations

from .types import ToolFingerprint, SupplyFinding, SupplyReport
from .fingerprint import fingerprint


def verify(current_tools, baseline: list[ToolFingerprint]) -> SupplyReport:
    """Compare current tool definitions against a locked baseline.

    - added: tool exists now but not in baseline (post-approval addition)
    - removed: in baseline but gone now (possible capability loss)
    - modified: hash changed (definition mutated after approval = rug-pull vector)
    """
    current = [fingerprint(t) for t in current_tools]
    base_map = {f.name: f.sha256 for f in baseline}
    cur_map = {f.name: f.sha256 for f in current}

    report = SupplyReport(locked_count=len(baseline), current_count=len(current))

    for name in sorted(cur_map.keys() - base_map.keys()):
        report.findings.append(SupplyFinding(
            "added", "error", name,
            "tool added after baseline was locked — verify it was approved"))
    for name in sorted(base_map.keys() - cur_map.keys()):
        report.findings.append(SupplyFinding(
            "removed", "warning", name,
            "tool present in baseline but missing now"))
    for name in sorted(base_map.keys() & cur_map.keys()):
        if base_map[name] != cur_map[name]:
            report.findings.append(SupplyFinding(
                "modified", "error", name,
                "tool definition changed after approval — possible rug-pull",
                old_sha=base_map[name], new_sha=cur_map[name]))

    return report
