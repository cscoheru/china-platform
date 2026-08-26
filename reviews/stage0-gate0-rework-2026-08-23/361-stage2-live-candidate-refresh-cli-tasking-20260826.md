# LIVE_CANDIDATE 一键刷新 — 缩刀任务书

- 编号：`361-stage2-live-candidate-refresh-cli-tasking-20260826`
- 前置：`360` PASS；双轨已通；产品目标①自动拉取
- 用户裁定：**D** + Cursor 代判

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) CLI/子命令（可挂在 `auto_ingest_public_source.py`）：`--refresh-live-candidate`：NBS live（过壳/deeplink）→ WORM → extract → 写 `NATIONAL_BULLETIN_LIVE_CANDIDATE.json` + 同步 `frontend/lib/public_extract_nbs_live_candidate.json`；(2) **绝不**改 sample JSON/fixture/registry sample 哈希；(3) drift/AUTH/tech-blocked 路径照旧；(4) ≥4 pytest；(5) 回执 **`362`**（`-cc-`）|
| 本刀不做 | 自动 O1 收口；改 sample；Gate PASS；headless |
| 禁止 | 覆盖 sample；伪造 O1 |

## NOW

1. 落地刷新 CLI + 测
2. 补 pack → 回执 **`362`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；sample 分轨锁定。
