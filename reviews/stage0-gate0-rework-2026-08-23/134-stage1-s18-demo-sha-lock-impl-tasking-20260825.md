# S1.18 — DEMO `is_demo` sentinel 实现任务书

- 编号：`134-stage1-s18-demo-sha-lock-impl-tasking-20260825`
- 前置：`133` 规划通过；`docs/33`（路径 **A**）

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| migration | **无** |
| 路径 | **A**：`lineage.is_demo=true`；`file_hash_sha256` 仍全零 |
| mart | `WHERE NOT is_demo` **过滤** DEMO 出跨源冲突池（不强留 is_demo 行） |
| 新测试 | `tests/test_demo_sha_sentinel.py`（≥5 用例；docs/33 §3.3） |
| 真实替换 CLI | **不**交付（§3.6 Stage 2） |

## NOW

1. 改 seed JSON + `seed_jiangsu_gdp_demo.py`（透传 `is_demo`；`--status` 扩展）
2. 改 `mart_source_disagreement` 过滤 DEMO；补 pack（含 `docs/33`）
3. pytest `test_demo_sha_sentinel` + 回归 s141 / r03 / ingest_monitor（按需）
4. commit → origin → 回执 **`135`** 进 `reviews/`
5. → **`84` POLL**

## 红线

不 Gate 1 PASS；不爬网；不伪造 SHA；不把 DEMO 标 `VERIFIED`；不改 `gate_thresholds.json`。
