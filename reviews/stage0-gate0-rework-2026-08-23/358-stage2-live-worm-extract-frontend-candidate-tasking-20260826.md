# live WORM → 结构化候选 + 前端并列 — 缩刀任务书

- 编号：`358-stage2-live-worm-extract-frontend-candidate-tasking-20260826`
- 前置：`357` PASS；`data/public_archives/2026-08/stats.gov.cn/zxfb`（live deeplink 文章，435KB，drift）
- 用户裁定：**D** + Cursor `341`（列表/文章 drift 不自动毁 sample 锚定）

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 从已归档 `zxfb`（或等价 live WORM）跑 extract → 写 `data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN_LIVE_CANDIDATE.json`（含 sha/path/row_count/rows；`intake_status` 语义 = live candidate）；(2) **禁止**覆盖 `NATIONAL_BULLETIN.json` sample 与 `frontend/lib/public_extract_nbs.json`；(3) 前端 `/public-extracts` 增加 **LIVE_CANDIDATE** 区块/页（显式非 O1；可与 sample 同页分节）；(4) ≥3 pytest + smoke/build 证据；(5) 回执 **`359`**（`-cc-`）|
| 本刀不做 | 改 registry sample 哈希；O1_AUTO_INTAKED；Gate PASS；headless |
| 禁止 | 覆盖 sample fixture；谎称 live 收口 |

## NOW

1. live WORM extract + 前端并列
2. 补 pack → 回执 **`359`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；sample 与 live candidate 分轨；不伪造。
