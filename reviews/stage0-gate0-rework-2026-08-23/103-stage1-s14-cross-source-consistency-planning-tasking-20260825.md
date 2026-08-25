# S1.14 — 跨来源一致性（docs/10 §2.4）规划任务书

- 编号：`103-stage1-s14-cross-source-consistency-planning-tasking-20260825`
- 前置：`102` S1.13.1 通过；`docs/27` §4.1 剩余严重缺口 #2；用户裁定 A
- 范围：**规划 only**

## NOW（CC 交付）

0. **补** `101-stage0-cc-s13-impl-receipt-*.md`（若仍缺）
1. 起草 **`docs/29-stage1-s14-cross-source-consistency-plan-20260825.md`**（CC 拥有）
2. 须覆盖：
   - 目标：跨来源差异阈值（docs/10 §2.4：5% 阈值；>2% 记 `source_disagreement`）
   - dbt test / model 形状（对接 `cegr_staging`）；与已有 `source_disagreement` 表衔接
   - 空表诚实；与 GE / API 边界
   - 测试策略；不批量爬取；不 Gate 1 PASS
3. 规划 only — 实现另开

## 红线

不 Gate 1 PASS；不 DSH；不爬网；Cursor 不写 `docs/29` 正文。
