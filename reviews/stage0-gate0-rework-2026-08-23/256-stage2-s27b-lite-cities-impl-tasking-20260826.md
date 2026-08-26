# S2.7-b-lite — 10 地市观察页缩刀实现任务书

- 编号：`256-stage2-s27b-lite-cities-impl-tasking-20260826`
- 前置：`255` 规划 PASS；`docs/46`；用户 **D**
- 用户裁定：**D** + Stage 2 **C**；自主推进

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | 10 城 **`/cities/{slug}`** mock 壳；复用 EvidenceChain + SevenDimGrid + PeerCompareCard |
| 10 城 slug | `nanjing` `suzhou` `wuxi` `nantong` `hangzhou` `ningbo` `wenzhou` `guangzhou` `shenzhen` `dongguan` |
| mart / person 真数据 | **本刀不做**（OPEN → S2.7-b-full）|
| 禁止 | Gate 1/2 PASS；评分/排名；DSH；爬网；改 10 城名单 |

## NOW

1. 落地 `frontend/app/cities/[slug]/page.tsx` + mock + `generateStaticParams`（10 城）
2. 最小 pytest（路由/slug 守门）→ 补 pack → commit → 回执 **`257`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网；不伪造 SHA。
