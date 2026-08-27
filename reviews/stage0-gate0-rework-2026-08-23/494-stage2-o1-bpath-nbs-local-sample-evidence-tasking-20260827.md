# O1 B 路 NATIONAL_BULLETIN --from-local-sample 证据 — 缩刀任务书

- 编号：`494-stage2-o1-bpath-nbs-local-sample-evidence-tasking-20260827`
- 前置：`493` PASS；POLL ~9m → 续刀
- 用户裁定：**C** + **D**；preview 容器化 **择机**；**O1=公开源 B 路（docs/52），不等用户投喂**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 跑 `scripts/auto_ingest_public_source.py --from-local-sample --pilot-domain=stats.gov.cn --pilot-category=NATIONAL_BULLETIN --confirm-live=reviews/stage0-gate0-rework-2026-08-23/20260827T-nbs-national-bulletin-local-sample-lineage.jsonl`（**无网络**；读 registry `local_sample_path`；写 lineage；`intake_status=REGISTRY_SAMPLE_INTAKED`，**`is_demo=true`**）；(2) 回执粘贴命令 + exit code + 关键 stdout + lineage 路径；(3) `docs/53` §5 新增 **第 23 项**登记（显式 demo/sample，非 O1 收口）；(4) `docs/45` 刷新四处；(5) 回执 **`494`**（`-cc-`）|
| 本刀不做 | `--live`；改 fixture 字节；改 registry `enabled`；启用 Hubei；Gate/O1 PASS |
| 禁止 | 谎称 O1 已收口；静默失败；绕过红线 |

## NOW

1. local-sample（无网络）+ docs
2. pack → 回执 **`494`**
3. **必须双推** → **`84` POLL**

## 红线

不 Gate/O1 PASS；不 live；`is_demo=true` 不得谎称真 SHA 收口。
