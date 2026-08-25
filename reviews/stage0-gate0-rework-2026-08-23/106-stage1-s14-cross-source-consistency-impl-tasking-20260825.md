# S1.14 — 跨来源一致性实现任务书

- 编号：`106-stage1-s14-cross-source-consistency-impl-tasking-20260825`
- 前置：`105` 规划通过；`docs/29`

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| migration | **`006_source_disagreement.sql`**（`cegr.source_disagreement`） |
| dbt | staging candidate + mart（阈值分级）；**可写** disagreement 结果表 |
| 阈值 | **2% / 5%** 按 docs/29；不改 `gate_thresholds.json` |
| API | **本刀可选**；有余力再加只读 list |
| GE suite | 按 docs/29 §2.4 子集即可 |

## NOW

0. **补** `104-stage0-cc-s14-plan-receipt-*.md`（若仍缺）
1. migration 006 + dbt models/tests（空表诚实）
2. **≥5** pytest（schema / <2% 不记 / 2–5% RECORDED / >5% NEEDS_REVIEW / 空表诚实）
3. 可选：GE suite 或 stub
4. commit → **origin 优先** → 回执 **`107-stage0-cc-s14-impl-receipt-*.md`**
5. → **立即再进 `84` while-POLL**

## 红线

不 Gate 1 PASS；不 DSH；不爬网；不改 `gate_thresholds.json`。
