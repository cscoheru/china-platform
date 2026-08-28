# 合刀：post-(a) live refresh 实跑 + docs/53 第 33 项证据 + docs/45 — 任务书

- 编号：`560-stage2-o1-bpath-nbs-posta-live-refresh-evidence-bundle-tasking-20260828`
- 前置：`559` PASS；用户裁定：**合刀**；第 32 项已登记下一轴 = post-(a) live refresh → mart 真 SHA（per `554`）
- 用户裁定：**C** + **D** + **合刀**；**O1=公开源 B 路**；SHA drift **(a) 已执行**（registry a7e4029d…/180165）

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做（合刀 · 一步交卷） | **A.** 跑 `scripts/auto_ingest_public_source.py --live --pilot-domain=stats.gov.cn --pilot-category=NATIONAL_BULLETIN --confirm-live=reviews/stage0-gate0-rework-2026-08-23/20260828T-nbs-national-bulletin-posta-live-refresh-lineage.jsonl`（**有网络**；写 lineage；遇 AUTH/TECH 阻停如实报告；期望 hash 匹配 registry `a7e4029d…`）；**B.** `docs/53` §5 新增第 33 项 blockquote（post-(a) live refresh 证据；非 O1 收口）；**C.** `docs/45` 文首/§1/§6.2/§7 四处同步；**D.** 回执粘贴命令 + exit code + 关键 stdout + lineage 路径；**E.** 回执 **仅 `560`**（`-cc-`）|
| 本刀不做 | 改 registry；启用 Hubei live；Gate/O1 PASS；绕过 AUTH；拆多回执 |
| 偏差 | 若本机 `--live` 被阻：回执写明偏差 + 引用 Cursor 本机复验路径（同 `538` D1–D5 模式），**不得**谎称已跑通 |
| 禁止 | 谎称 O1/mart 真 SHA 已收口；静默失败 |

## NOW

1. live refresh（A）+ docs（B+C）同交卷
2. pack → 回执 **`560`**
3. **必须双推** → **`84` POLL**

## 红线

合刀仍单槽单回执；hash 匹配 ≠ O1 收口（mart 真 SHA 入仓语义须回执写明实测）；遇 AUTH 阻停报告不绕过。
