# 首页十城导航入口 — 缩刀任务书

- 编号：`274-stage2-home-cities-nav-tasking-20260826`
- 前置：`273` 前端 build 硬化 PASS；预览 `china.3strategy.cc`
- 用户裁定：**D**；自主推进；O1 无材料保持 OPEN

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | 首页增加 **10 地市**导航表（对齐 `CITY_SLUG_LIST` / docs/46）|
| 本刀不做 | 真数据；改评分/排名；改 CF/nginx |
| 禁止 | Gate 1/2 PASS；DSH；爬网 |

## NOW

1. 改 `frontend/app/page.tsx`（或等价）加十城链接区
2. smoke 不破 → 补 pack → commit → 回执 **`275`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网。
