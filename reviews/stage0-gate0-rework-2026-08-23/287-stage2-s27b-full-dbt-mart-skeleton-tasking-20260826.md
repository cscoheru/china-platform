# S2.7-b-full-dbt-skel — city mart SQL 骨架缩刀任务书

- 编号：`287-stage2-s27b-full-dbt-mart-skeleton-tasking-20260826`
- 前置：`286` docs/45 O1 登记 PASS；`docs/47` §3.1/§3.2；前端 mart-shape 已交（`266`）
- 用户裁定：**D**；自主推进；**O1 持续 OPEN、不伪造、不爬网**
- 动机：CC 空等 POLL；下一刀做实质 dbt 骨架（非首页微刀）

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | 按 `docs/47` §3.1/§3.2：新增 dbt **view** 骨架 `mart_city_evidence_chain.sql` + `mart_city_seven_dim_overview.sql`（`dbt/models/marts/`）；字段对齐规划；`is_demo` sentinel；`source_file_sha256` **仅**占位 `'0'*64` 注释/常量；最小 pytest 守门（文件存在、无 score/rank 列、无真 SHA 伪造）|
| 本刀不做 | O1 真样本；person/tenure 真 JOIN 数据填充；全量 seed；接前端真表；宣布 Gate PASS |
| 禁止 | Gate 1/2 PASS；评分/排名；DSH；爬网；伪造非零 SHA |

## NOW

1. 落地两份 mart SQL view 骨架（可先 SELECT … WHERE false / 空结果，但列契约完整；或 JOIN 现有 staging 表且强制 `is_demo`）
2. 最小 pytest（建议 `tests/test_mart_city_dbt_skel_s27bf.py`）→ 补 pack → commit → 回执 **`288`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分/排名；不 DSH；不爬网；不伪造 SHA；不擅自收口 O1。
