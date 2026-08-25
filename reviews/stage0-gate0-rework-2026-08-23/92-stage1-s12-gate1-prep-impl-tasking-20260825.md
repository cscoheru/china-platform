# S1.12 — Gate 1 准备组装实现任务书

- 编号：`92-stage1-s12-gate1-prep-impl-tasking-20260825`
- 前置：`91` 规划通过；`docs/26`
- 目标：组装 **Gate 1 准备包**（可演示 + 可审计），**不**宣布 Gate 1 PASS

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 来源表述 | **4 类中国代表性 + 1 OCR 压力样本**（见 `91` §1） |
| 演示数据 | 允许 **受控 seed / 已有样本入库**（不批量爬 2020–2025；不 HTTP 爬源站） |
| PASS 声称 | **禁止** |

## NOW

0. **补** `90-stage0-cc-s12-plan-receipt-*.md`（若仍缺）+ 可选 pack 纳入 `docs/26`
1. 按 `docs/26` §3.3 高优先级落地：
   - **真实研究问题 seed**（至少 1 条可答：建议「近 5 年江苏 GDP」或等价；数据来自已有样本/手工 seed，不爬网）
   - **演示 step-by-step**（`docs/` 或 `scripts/`：curl/API + 预期响应要点）
2. 产出 **Gate 1 prep 索引**（单页 md：快照路径、测试报告索引、演示步骤、§3 缺口原文引用）
3. 定向验证（API series 对 seed；相关 pytest）→ commit → **origin 优先** → 回执 **`93-stage0-cc-s12-impl-receipt-*.md`**
4. → **立即再进 `84` while-POLL**

## 本刀不做

`/admin/upload` 全量、URL 探针产品化、Next.js UI、宣布 Gate 1 PASS（可列 S1.13+ 遗留）。

## 红线

不 Gate 1 PASS；不 DSH；不批量爬取；不改 `gate_thresholds.json`。
