# S2.1 — person / tenure / position 规划任务书

- 编号：`171-stage2-s21-person-tenure-planning-tasking-20260825`
- 前置：`170` S2.7-a PASS；`docs/34` §4 序 4；`docs/04` §3.6+
- 用户裁定：**C**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 交付 | 规划文档 **`docs/36-stage2-s21-person-tenure-plan-YYYYMMDD.md`**（CC 起草） |
| 表范围 | `person` / `tenure` / `position`（及必要关联事件）；**不**扩 policy/budget/project |
| 契约 | 对齐 `docs/04`；钉死字段、重叠任期合法性、与六段证据链（尤其 COMMITMENT/PROCESS）的消费形状 |
| dbt | staging candidate 路径（S1.19 约束）；**不**直接改 mart |
| 首批数据 | 规划须写明：来源（公开履历/手工 seed）、条数上限、`is_demo` 策略 |
| UI | 本刀**只规划**；实现与接 UI 分属后续 S2.1 实现刀 / S2.7-b |

## NOW

1. 起草 `docs/36`：表契约、迁移边界、验收清单、与 S2.7-a mock 字段对照、风险/红线
2. 补 pack（documentation +1）；invariant 保持
3. commit → origin → 回执 **`172`** 进 `reviews/`
4. → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分 / 排名；不 DSH；不爬网抓履历；不改 `gate_thresholds.json`；本刀**不写**生产 migration（规划即可）。
