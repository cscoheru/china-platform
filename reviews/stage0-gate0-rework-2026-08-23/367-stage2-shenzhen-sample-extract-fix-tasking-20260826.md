# 深圳样本表抽取修复 — 缩刀任务书

- 编号：`367-stage2-shenzhen-sample-extract-fix-tasking-20260826`
- 前置：里程碑 POLL `151`；自主推进 **C** 恢复下刀；深圳 `MUNICIPAL_BULLETIN` sample 有 `<table>` 但 extract **0 行**
- 用户裁定：**D** + Cursor 代判

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 修 `extract_html_tables` / `MUNICIPAL_BULLETIN` 抽取，使 `spikes/03-municipal-bulletin/sample.html` → **≥1 行**（保留现有 NBS 63 行回归）；(2) 重跑 `--from-local-sample` 写 `data/public_extracts/sz.gov.cn/MUNICIPAL_BULLETIN.json`（可增前端 fixture 小节，标 REGISTRY_SAMPLE）；(3) ≥3 pytest（深圳 ≥1 行 + NBS 不回归）；(4) 回执 **`368`**（`-cc-`）|
| 本刀不做 | 深圳 HTTPS live（SSL 仍暂缓）；Gate/O1 PASS；覆盖 NBS sample |
| 禁止 | 伪造行；headless；破坏 NBS 双轨 |

## NOW

1. 修抽取 + 重跑深圳 local-sample + 测
2. 补 pack → 回执 **`368`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；不碰 NBS live 候选契约。
