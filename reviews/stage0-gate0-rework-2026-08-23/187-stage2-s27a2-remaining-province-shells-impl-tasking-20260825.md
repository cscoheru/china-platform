# S2.7-a2 — 补齐三省省级路由壳 实现任务书

- 编号：`187-stage2-s27a2-remaining-province-shells-impl-tasking-20260825`
- 前置：`186` S2.1-lite PASS；`168`/`170` S2.7-a（江苏满段 + 浙江壳 + 5 省列表）
- 用户裁定：**D**（S2.1 缩刀仍有效）；Stage 2 前进承 **C**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 范围 | `frontend/app/provinces/{guangdong,sichuan,shandong}/page.tsx` 路由壳 |
| 证据链 | 挂 `<EvidenceChain />`；六段可全空（「未覆盖」）；复用 `mock_evidence_chain` |
| 禁 | 评分/排名/总分；不接 S2.1 person 真数据（留给 S2.7-b） |
| 首页 | 5 省列表链接须全部可点进真实路由（非死链） |

## NOW

1. 落地广东 / 四川 / 山东三省页壳 + mock（可全空六段）
2. 扩展 smoke / pytest；既有 S2.7-a 套件仍绿
3. commit → origin → 回执 **`188`** 进 `reviews/`
4. → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网；不改 `gate_thresholds.json`；不扩 S2.1-full。
