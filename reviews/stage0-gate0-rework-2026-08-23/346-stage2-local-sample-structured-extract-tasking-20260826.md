# registry 本地样本结构化提取 + NBS 再探 — 缩刀任务书

- 编号：`346-stage2-local-sample-structured-extract-tasking-20260826`
- 前置：`345` PASS；湖北 JS 暂缓；深圳 SSL 暂缓；Cursor `341` 代判
- 用户裁定：**D** + 源工程 Cursor 代判

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) connector 增 `--from-local-sample`：读 registry `local_sample_path`，SHA 必须匹配 `file_hash_sha256`，否则 fail；(2) 归档 WORM + extract + observation：`intake_status=REGISTRY_SAMPLE_INTAKED`，`is_demo=true`（诚实：样本≠ live 收口）；另写 `data/public_extracts/{domain}/{category}.json`（表格行结构化）；(3) 对 **NBS + 深圳** 各跑一次（enabled 行）；湖北允许 `--allow-disabled-local-sample` 只抽本地 xlsx 样本（仍 is_demo）；(4) registry 深圳 `failure_handling` 注明「2026-08-26 HTTPS BAD_ecPOINT；Cursor 暂缓 live；禁 HTTP pin」；(5) **一次** NBS `--live`（非 local）：若得稳定文章/非壳 → 按 `341` 可 pin；否则 drift/tech-blocked 照旧；(6) ≥8 pytest；(7) 回执 **`347`** |
| 本刀不做 | HTTP 降级 pin 深圳；headless；Gate/O1 PASS；把样本标 O1_AUTO_INTAKED |
| 禁止 | SHA 不匹配仍入库；伪造 live；绕 AUTH |

## NOW

1. 落地 `--from-local-sample` + extracts JSON + registry 深圳 SSL 注记
2. 跑 NBS/深圳/（可选）湖北本地样本；NBS 再 live 一次
3. 补 pack → 回执 **`347`**
4. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；样本≠ live 收口；不 HTTP pin；不 headless。
