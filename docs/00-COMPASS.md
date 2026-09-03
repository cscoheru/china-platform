# 00-COMPASS — 会话常驻罗盘（唯一热记忆）

> **预算：全文 ≤ 80 行 / 6 KB。**

## 愿景（PRD）

可查询、可回溯研究底座。不以抓取页数为完成标准。

## 现行里程碑

| 项 | 值 |
|---|---|
| 计划 | `docs/54` 主计划 · `docs/68` spike 链 master |
| 阶段 | 660 审计 **PASS·有限通过**〔生产站已显真数据, 用户回执〕→ **661 PRD 对齐重排刀** |
| NOW | **661** PRD 产品差距重排（docs/87）+ 首个产品化切片（多指标+国家锚+溯源 UI） |
| KPI 现状 | 省级 COVERED **31/31**（M2-c+d+e per 635 AUDITED） |
| Gate | **未 PASS**（M2 各子刀 AUDITED，未宣布 M2 PASS） |

## 红线

禁：目录/首页 FETCHED；补零；静默硬编码 value；自动 Gate/M2/M4.x/M5.x/M6 PASS；删既有 OPEN 行；碰 4 fixture 锁值（e30ee811/9232efdb/937255a5/9056001c）；数据源非政府/统计局/研究机构自取。

## NOW

661：**PRD 对齐重排刀**（回应用户「与设计初衷差十万八千里」）——① `docs/87-prd-product-gap-replan-20260903.md`: PRD §7.1-7.7 逐项 ×现状×数据就绪度×依赖×建议刀次 + 在库未上页盘点（115 observation 5 指标/国家锚/5 省静态页/3 demo 壳）+ 三期路线〔P1 产品化纯前端 / P2 数据扩展〔多年度+M3 城市〕/ P3 深水区〔人物任期/政策承诺/治理效能观察, 9-18 月级〕〕**交用户裁定优先级** + docs/54 补呈现层里程碑 ② 首个产品化切片: 首页多指标切换（5 指标）+ 国家锚行 + 溯源 UI（source_url+SHA 前缀+lineage_ruling）③ tests ≥10 → **≥374 底限 ≥370** + smoke §17 + m2 零 diff×2。红线: 多指标只准库/mart 导出; 溯源禁编造; **P3 深水区不得自行开刀**; 24 里程碑不宣布; O1 仍 OPEN。任务书 = `660-audit-661-tasking-consolidated-20260903.md` PART 2。

## POINTERS

- `docs/33` §3.2 sentinel · `docs/52` drift/B路 · `docs/81`（U6 ruling）· **`docs/china-economy-...-prd-v0.1.md`（PRD 原文）**
- 660 合并件（审计 PART 1 + **661 任务书 PART 2**）
- `00-DUAL-POLL-PROTOCOL` · `dual_poll_status.sh` · `00-EXEC-QUEUE.md` rev108

## 压缩后自检

阶段？NOW？禁做什么？

