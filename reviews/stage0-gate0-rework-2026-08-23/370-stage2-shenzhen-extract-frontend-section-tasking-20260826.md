# 深圳 REGISTRY_SAMPLE 前端分节 — 缩刀任务书

- 编号：`370-stage2-shenzhen-extract-frontend-section-tasking-20260826`
- 前置：`369` PASS；深圳 extract 71 行已落盘
- 用户裁定：**D**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) `frontend/lib/public_extract_sz.json` 快照自深圳 MUNICIPAL extract；(2) `/public-extracts` 增深圳 REGISTRY_SAMPLE 分节（显式 demo；不覆盖 NBS sample/live）；(3) ≥2 pytest + smoke；(4) 回执 **`371`**（`-cc-`）|
| 本刀不做 | 深圳 HTTPS live；改 NBS 双轨；Gate/O1 PASS |
| 禁止 | 覆盖 NBS fixture；谎称 live |

## NOW

1. fixture + 页面分节 + 测
2. 补 pack → 回执 **`371`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；不破坏 NBS 双轨。
