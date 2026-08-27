# O1 B 路 NATIONAL_BULLETIN live-candidate 探测证据 — 缩刀任务书

- 编号：`510-stage2-o1-bpath-nbs-live-candidate-probe-evidence-tasking-20260827`
- 前置：`509` PASS；POLL ~9m → 续刀
- 用户裁定：**C** + **D**；preview 容器化 **择机**；**O1=公开源 B 路（docs/52），不等用户投喂**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 跑 `scripts/auto_ingest_public_source.py --live --pilot-domain=stats.gov.cn --pilot-category=NATIONAL_BULLETIN --confirm-live=reviews/stage0-gate0-rework-2026-08-23/20260827T-nbs-national-bulletin-live-candidate-lineage.jsonl`（**有网络**；写 lineage；遇 AUTH/TECH 阻停如实报告）；(2) 回执粘贴命令 + exit code + 关键 stdout + lineage 路径；(3) `docs/53` §5 新增 **第 26 项**登记（live-candidate 探测证据，非 O1 收口）；(4) `docs/45` 刷新四处；(5) 回执 **`510`**（`-cc-`）|
| 本刀不做 | 改 registry `enabled`；启用 Hubei live；Gate/O1 PASS；绕过 AUTH |
| 禁止 | 谎称 O1 已收口；静默失败；绕过红线 |

## NOW

1. live probe + docs
2. pack → 回执 **`510`**
3. **必须双推** → **`84` POLL**

## 红线

不 Gate/O1 PASS；live drift 不自动改 registry；遇 AUTH 阻停报告不绕过；不等用户投喂。
