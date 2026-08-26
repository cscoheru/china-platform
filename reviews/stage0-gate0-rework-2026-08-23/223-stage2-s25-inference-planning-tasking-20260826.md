# S2.5 — inference_record 规划任务书

- 编号：`223-stage2-s25-inference-planning-tasking-20260826`
- 前置：`222` S2.4-lite PASS；`docs/34` §4 序 9；`docs/04` inference 位
- 用户裁定：Stage 2 **C**；缩刀节奏 **D**（本刀只规划）

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 交付 | **`docs/40-stage2-s25-inference-plan-YYYYMMDD.md`** |
| 表范围 | `inference_record` + `claim_evidence_link`（最小关联）；**不**扩 Gate 2 全量 UI |
| 契约 | 对齐 `docs/04`；INFERENCE/JUDGMENT 标注；无官员评分 |
| 本刀 | **只规划**；不写 migration |

## NOW

1. 起草 `docs/40`：表契约、推断 API 形态、验收、红线
2. 补 pack；commit → origin → 回执 **`224`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网；不改 `gate_thresholds.json`；本刀不写 migration。
