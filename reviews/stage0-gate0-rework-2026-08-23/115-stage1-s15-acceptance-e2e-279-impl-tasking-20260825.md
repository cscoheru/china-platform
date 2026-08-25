# S1.15 — docs/10 §2.7–2.9 e2e 实现任务书

- 编号：`115-stage1-s15-acceptance-e2e-279-impl-tasking-20260825`
- 前置：`114` 规划通过；`docs/30`

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| §2.8 复核队列表 | 按 `docs/30` §2：**migration 007**（幂等 `IF NOT EXISTS`；优先 `cegr.*`） |
| confidence 门 | docs/10 常量 **0.70**（0–1）；**不改** `gate_thresholds.json` |
| §2.7 | 检出型 pytest（可无 insert 触发器） |
| §2.9 | 依现有 CHECK + pytest 正/负例 |

## NOW

0. 补回执 **`113`**（规划）；可选把 `docs/107-*.md` **移到** `reviews/`（或新交正确路径说明）
1. migration 007（若需）+ pytest：**≥10** 覆盖 2.7/2.8/2.9（对齐 docs/30 §4）
2. 全链 apply 仍绿；回归 `test_source_disagreement_s141` + `test_admin_upload_s131`
3. commit → origin → 回执 **`116-stage0-cc-s15-impl-receipt-*.md`**（路径：`reviews/`）
4. → **`84` POLL**

## 红线

不 Gate 1 PASS；不 DSH；不爬网；不改 `gate_thresholds.json`。
