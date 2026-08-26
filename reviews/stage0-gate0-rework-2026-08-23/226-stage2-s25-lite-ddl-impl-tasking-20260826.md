# S2.5-lite — inference DDL 缩刀实现任务书

- 编号：`226-stage2-s25-lite-ddl-impl-tasking-20260826`
- 前置：`225` 规划 PASS；`docs/40` §2；用户 **D**
- 用户裁定：**D** + Stage 2 **C**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 表 | `inference_record` + `claim_evidence_link`（**ALTER additive**；对齐 docs/40 §2） |
| migration | **本刀必交**（建议 `012_*`） |
| seed | 空/骨架 OK；禁止爬网 |
| dbt / 首批行 | **本刀不做** |
| UI | **不接** EvidenceChain |

## NOW

1. 落地 migration（+ 可选空 seed）；不写 dbt
2. 最小 pytest（≥3）：layer 守门 / 无 score 字段；建议含 `import psycopg2.extras`
3. 补 pack；commit → origin → 回执 **`227`**
4. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网；不改 `gate_thresholds.json`；不扩全量 S2.5。
