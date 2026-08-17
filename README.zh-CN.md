# 🧬 mcp-supply-guard

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**MCP 工具定义供应链完整性。** 2026 安全数据:**43% 的 MCP 服务器存在命令注入漏洞**,且工具定义可在审批后变更——rug-pull 向量。本库在审查后锁定工具定义内容哈希基线,之后验证加载:标记**新增 / 移除 / 修改**工具,外加命令执行危险信号的风险扫描。

> 零依赖。纯 Python 标准库。

```python
from mcp_supply_guard import load_tools, fingerprint, verify, scan_risk
baseline = [fingerprint(t) for t in load_tools("approved.json")]  # 审查后锁定
report = verify(load_tools("current.json"), baseline)
print(report.clean)
risks = scan_risk(load_tools("current.json"))
```

```bash
pip install mcp-supply-guard
mcp-supply-guard lock approved.json baseline.json
mcp-supply-guard verify current.json baseline.json --json
mcp-supply-guard risk current.json --json
```

MIT © [wwb-bill](https://github.com/wwb-bill)
