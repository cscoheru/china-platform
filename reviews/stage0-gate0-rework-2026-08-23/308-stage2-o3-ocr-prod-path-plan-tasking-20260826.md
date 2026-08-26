# O3 OCR 生产路径规划 — 缩刀任务书

- 编号：`308-stage2-o3-ocr-prod-path-plan-tasking-20260826`
- 前置：`307` docs/45 PASS；docs/45 §3 O3 OPEN；docs/34 Stage 1 OPEN
- 用户裁定：**D**；自主推进；**不爬网**；**O1 仍 OPEN**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | 写 **`docs/49`**：O3 OCR 生产路径规划（输入=用户/admin 已上传 PDF 扫描件；流水线步骤；与 `is_demo`/SHA lineage 衔接；验收清单；**明确禁止** HTTP 爬源 / 登录绕过）|
| 本刀不做 | 实装 OCR 引擎；伪造样本；宣布 Gate/O1/O3 收口；改业务 UI |
| 禁止 | Gate 1/2 PASS；爬网；伪造；擅自收口 OPEN |

## NOW

1. 落地 `docs/49` 规划
2. 补 pack → 回执 **`309`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不爬网；不伪造；本刀只规划不落地 OCR。
