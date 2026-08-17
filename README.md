# 🧬 mcp-supply-guard

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![CI](https://github.com/wwb-bill/mcp-supply-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/wwb-bill/mcp-supply-guard/actions/workflows/ci.yml)
[![No Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)](#)

**MCP tool-definition supply-chain integrity.** 2026 security data point: **43% of MCP servers have command injection vulnerabilities**, and tool definitions can mutate after approval — a rug-pull vector. This library locks a baseline of tool-definition content hashes after review, then verifies later loads: flagging **added / removed / modified** tools, plus a risk scan for command-execution danger signals.

> Zero dependencies. Pure Python stdlib.

## Quick Start

```bash
pip install mcp-supply-guard
```

## Usage

```python
from mcp_supply_guard import load_tools, fingerprint, verify, scan_risk

baseline = [fingerprint(t) for t in load_tools("approved.json")]  # lock after review
report = verify(load_tools("current.json"), baseline)
print(report.clean)          # False if any tool added/modified
for f in report.findings:
    print(f.kind, f.tool, f.message)

risks = scan_risk(load_tools("current.json"))
```

## CLI

```bash
mcp-supply-guard lock approved.json baseline.json
mcp-supply-guard verify current.json baseline.json --json    # CI exit 1 on added/modified
mcp-supply-guard risk current.json --json
```

### tools.json

```json
{"tools": [{"name": "search", "description": "Search the index",
            "inputSchema": {"type": "object", "properties": {"q": {"type": "string"}}}}]}
```

## Findings

| Kind | Severity | Meaning |
|------|:--:|--------|
| `added` | **error** | tool added after baseline locked |
| `modified` | **error** | definition hash changed (rug-pull vector) |
| `removed` | warning | baseline tool missing now |
| `risky` | error/warning | command-execution danger signals in description/schema |

## License

MIT © [wwb-bill](https://github.com/wwb-bill)
