# S2.6-lite — 反例守门缩刀实现任务书

- 编号：`232-stage2-s26-lite-counterexample-gate-tasking-20260826`
- 前置：`231` 规划 PASS；`docs/41` §2.5；用户 **D**
- 用户裁定：**D** + Stage 2 **C**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | 反例守门函数/触发器（per docs/41 §2.5）+ 最小 pytest（≥3：CONTRADICTS 可插 / 无 score / polarity 一致） |
| migration | 可选 `013_*`（仅触发器/函数；无新业务表） |
| admin UI / dbt mart | **本刀不做** |
| seed | 空/骨架 OK；禁止爬网 |

## NOW

1. 落地守门（+ 可选空 seed）；不写 dbt / 不全量 UI
2. 最小 pytest → 全绿
3. 补 pack；commit → origin → 回执 **`233`**
4. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网；不扩全量 S2.6 UI。
