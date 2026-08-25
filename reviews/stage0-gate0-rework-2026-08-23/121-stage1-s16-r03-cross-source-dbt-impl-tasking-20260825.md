# S1.16 — R03 / §2.4 dbt 阈值测试 实现任务书

- 编号：`121-stage1-s16-r03-cross-source-dbt-impl-tasking-20260825`
- 前置：`120` 规划通过；`docs/31`

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| models | **不改** S1.14 candidate/mart |
| migration | **无** |
| 新构件 | `dbt/tests/test_cross_source_consistency_threshold.sql`（+ 可选轻量 companion） |
| 执行环境 | `.venv-dbt`（python3.11）+ `requirements-dbt.txt` 钉版本；venv **不**入 pack |
| 自动化入口 | `tests/test_r03_cross_source_dbt.py`（docs/31 §3.2 ≥5 用例；缺环境 **skip** 不 fail） |
| 阈值 | docs/10 常量 2%/5%；**不改** `gate_thresholds.json` |

## NOW

1. 建 `.venv-dbt` + 钉版本 requirements；`dbt run --select mart_source_disagreement+` 绿
2. 落地 singular test（**含 S0↔S0 过滤**）+ pytest wrapper（干净 / PENDING 红 / RESOLVED 绿 / S0↔S1 不断言）
3. 回归：`test_source_disagreement_s141` 仍绿
4. commit → origin → 回执 **`122`** 进 `reviews/`
5. → **`84` POLL**

## 红线

不 Gate 1 PASS；不 DSH；不爬网；不改 `gate_thresholds.json`；不改 S1.14 mart 行为。
