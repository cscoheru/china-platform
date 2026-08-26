# 首页导航 smoke 守门 — 缩刀任务书

- 编号：`280-stage2-home-nav-smoke-tasking-20260826`
- 前置：`279` 七维/对比导航 PASS；`276` 十城导航 PASS
- 用户裁定：**D**；自主推进

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | `frontend/smoke-check.py` 增加首页守门：含 10 城 `/cities/` 链接 + `/seven-dim` + `/peer-compare` |
| 本刀不做 | UI 改版；真数据；CF |
| 禁止 | Gate 1/2 PASS；评分/排名；DSH；爬网 |

## NOW

1. 扩展 smoke-check → 本地跑通
2. 补 pack → commit → 回执 **`281`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网。
