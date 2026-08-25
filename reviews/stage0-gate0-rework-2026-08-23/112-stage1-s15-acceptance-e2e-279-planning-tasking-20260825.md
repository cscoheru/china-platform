# S1.15 — docs/10 §2.7–2.9 e2e 规划任务书

- 编号：`112-stage1-s15-acceptance-e2e-279-planning-tasking-20260825`
- 前置：`111` S1.14 PASS；`docs/27` §4.1 剩余缺口；用户裁定 A
- 范围：**规划 only**

## NOW（CC 交付）

0. **补** `107-stage0-cc-s14-impl-receipt-*.md`（若仍缺）
1. 起草 **`docs/30-stage1-s15-acceptance-e2e-279-plan-20260825.md`**（CC 拥有）
2. 须覆盖：
   - §2.7 行政区划有效期 e2e
   - §2.8 OCR 置信度分流（与 ingest / upload 衔接；不降 `gate_thresholds`）
   - §2.9 缺失值不补零 + `missing_reason`
   - 测试落点（pytest / 现有 schema·dbt）、空表诚实、与 S1.12/S1.13 边界
3. 规划 only — 实现另开

## 红线

不 Gate 1 PASS；不 DSH；不爬网；不改 `gate_thresholds.json`；Cursor 不写 `docs/30` 正文。
