# S2.10-lite — Gate 2 评审索引缩刀任务书

- 编号：`250-stage2-s210-lite-gate2-index-tasking-20260826`
- 前置：`249` 规划 PASS；`docs/44`；用户 **D**
- 用户裁定：**D** + Stage 2 **C**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 交付 | Gate 2 **评审索引**（markdown；映射 7 条验收 → 证据路径 + OPEN） |
| 路径建议 | `reviews/.../gate2-review-index-YYYYMMDD.md` 或 `docs/45-...` |
| **禁止** | 文件中出现「Gate 2 PASS」宣称 |
| 本刀不做 | 伪造证据；关闭 Stage 1 OPEN；全量 dbt/UI 补齐 |

## NOW

1. 落地评审索引（对齐 docs/44 §2–§7）
2. 补 pack → commit → origin → 回执 **`251`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网；不伪造 SHA。
