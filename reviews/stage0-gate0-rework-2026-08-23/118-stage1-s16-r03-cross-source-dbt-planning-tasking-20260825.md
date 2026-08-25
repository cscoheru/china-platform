# S1.16 — R03 / docs/10 §2.4 跨源一致性 dbt 规划任务书

- 编号：`118-stage1-s16-r03-cross-source-dbt-planning-tasking-20260825`
- 前置：`117` S1.15 PASS；用户裁定 **A**；`docs/27` §4.1 剩余缺口
- 范围：**规划 only**

## 背景（勿重复造轮）

- S1.14 已交：`006` `cegr.source_disagreement` + staging/marts + pytest 9
- **仍缺**（`docs/26` §1.4 / `docs/27` §4）：dbt **`test_cross_source_consistency_threshold`**（§2.4 阈值）与 R03 **运行时可重复**冲突检测（非仅 spike 人工）

## NOW（CC 交付）

1. 起草 **`docs/31-stage1-s16-r03-cross-source-dbt-plan-20260825.md`**（CC 拥有）
2. 须覆盖：
   - 与 S1.14 marts 的边界（复用 vs 新 model/test）
   - docs/10 §2.4 阈值语义（相对偏差 / 绝对；与 `gate_thresholds` **无关**）
   - dbt test 落点 + 空表诚实 + seed/fixture 策略（不爬网）
   - R03「自动化」最小可验收定义（pytest 调用 dbt test 或 CI 一步）
3. 规划 only — 实现另开；回执 **`119`** 进 `reviews/`
4. → **`84` POLL**

## 红线

不 Gate 1 PASS；不 DSH；不爬网；不改 `gate_thresholds.json`；Cursor 不写 `docs/31` 正文。
