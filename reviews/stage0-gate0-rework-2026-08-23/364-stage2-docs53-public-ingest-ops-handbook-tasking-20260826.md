# 公开源自动获取 ops 手册 — 缩刀任务书

- 编号：`364-stage2-docs53-public-ingest-ops-handbook-tasking-20260826`
- 前置：`363` PASS；预览 `/public-extracts` 双轨已通
- 用户裁定：**D**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 写 `docs/53-stage2-public-ingest-ops-handbook-20260826.md`：dry-run / local-sample / live / `--refresh-live-candidate` 命令例；AUTH/tech/drift 出口码；sample vs LIVE_CANDIDATE 分轨；预览 URL；(2) `docs/45` 索引登记 docs/52+53 + 公开提取双轨（仍不宣布 Gate PASS）；(3) 回执 **`365`**（`-cc-`）|
| 本刀不做 | 改 connector 行为；Gate/O1 PASS；改 CF |
| 禁止 | PASS 宣告；覆盖 sample 契约说明错误 |

## NOW

1. docs/53 + docs/45 刷新
2. 补 pack → 回执 **`365`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；手册诚实标注 demo/candidate。
