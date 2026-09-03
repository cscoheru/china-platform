# 00-COMPASS — 会话常驻罗盘（唯一热记忆）

> **预算：全文 ≤ 80 行 / 6 KB。**

## 愿景（PRD）

可查询、可回溯研究底座。不以抓取页数为完成标准。

## 现行里程碑

| 项 | 值 |
|---|---|
| 计划 | `docs/54` 主计划 · `docs/68` spike 链 master |
| 阶段 | 661 审计 **PASS·有限通过**〔P1 上线, 用户回执〕→ **662 P1 收尾刀** |
| NOW | **662** P1 收尾: 血缘全露+指标定义+覆盖矩阵+demo 横幅+F2 脚本验收 |
| KPI 现状 | 省级 COVERED **31/31**（M2-c+d+e per 635 AUDITED） |
| Gate | **未 PASS**（M2 各子刀 AUDITED，未宣布 M2 PASS） |

## 红线

禁：目录/首页 FETCHED；补零；静默硬编码 value；自动 Gate/M2/M4.x/M5.x/M6 PASS；删既有 OPEN 行；碰 4 fixture 锁值（e30ee811/9232efdb/937255a5/9056001c）；数据源非政府/统计局/研究机构自取。

## NOW

662：**P1 收尾刀**（用户指令「尽快按 PRD 呈现现有数据」）——① 血缘 popover 补 lineage_source/origin（PRD §3.3）② /indicators 定义页（5 指标+来源等级三分布, mart 导出禁手写）③ 31×5 覆盖矩阵+3 缺公示（PRD §7.2）④ 排序口径提示（禁榜单化 docs/05 §8.3）⑤ four demo 页横幅+导航 LIVE/DEMO 分组 ⑥ verify-live.sh F2 公网 12 项断言（#832 SSH 或用户代跑）⑦ tests ≥14 → ≥391 底限 ≥385 + smoke §18 + m2 零 diff×2。红线: 全数据库/mart 导出; **P2/P3 禁开**（需 user_ruling）; O1 OPEN。任务书 = `661-audit-662-tasking-consolidated-20260903.md` PART 2。

## POINTERS

- `docs/33` §3.2 sentinel · `docs/52` drift/B路 · `docs/81`（U6 ruling）· **`docs/china-economy-...-prd-v0.1.md`（PRD 原文）**
- 661 合并件（审计 PART 1 + **662 任务书 PART 2**）
- `00-DUAL-POLL-PROTOCOL` · `dual_poll_status.sh` · `00-EXEC-QUEUE.md` rev110

## 压缩后自检

阶段？NOW？禁做什么？

