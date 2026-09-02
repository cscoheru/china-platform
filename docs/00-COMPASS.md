# 00-COMPASS — 会话常驻罗盘（唯一热记忆）

> **预算：全文 ≤ 80 行 / 6 KB。**

## 愿景（PRD）

可查询、可回溯研究底座。不以抓取页数为完成标准。

## 现行里程碑

| 项 | 值 |
|---|---|
| 计划 | `docs/54` 主计划 · `docs/68` spike 链 master |
| 阶段 | 659 审计 **PASS·有限通过**〔代码层真实化完成〕→ **660 生产部署切源刀** |
| NOW | **660** 生产部署: 让生产站显示 28 省真数据（§1.660-0 前置三问 BLOCKER） |
| KPI 现状 | 省级 COVERED **31/31**（M2-c+d+e per 635 AUDITED） |
| Gate | **未 PASS**（M2 各子刀 AUDITED，未宣布 M2 PASS） |

## 红线

禁：目录/首页 FETCHED；补零；静默硬编码 value；自动 Gate/M2/M4.x/M5.x/M6 PASS；删既有 OPEN 行；碰 4 fixture 锁值（e30ee811/9232efdb/937255a5/9056001c）；数据源非政府/统计局/研究机构自取。

## NOW

660：**生产部署切源刀**——用户质询直答（659 切源=代码层〔仓库 frontend/ 应用〕; 生产站=旧构建产物, NEXT_PUBLIC_* 构建时内联, 仓库无部署管线, 本机 curl 双域名 000 不可达）→ ① **§1.660-0 用户前置三问**〔部署在哪/怎么部署/可否触达; 未答只产部署包不上线〕② 轨道 A（FastAPI+DB 后端部署）/ 轨道 B（`output:'export'` 静态导出内联 mart 数据）③ `deploy/` 四件〔build_static.sh|compose.yml + ENV.md + VERIFY.sh 三标记断言 + 回滚〕+ docs/85 runbook + N-1 layout title 去 demo ④ **v3.5 裁定权条款首签**〔裁定字样禁执行端写〕⑤ tests ≥8 → **≥359 底限 ≥355** + m2 零 diff×2〔21 文件集〕。红线: 生产 env 禁 USE_MOCK=true〔回滚除外〕; **24 里程碑不宣布**〔上线≠Gate PASS〕; O1 仍 OPEN。任务书 = `659-audit-660-tasking-consolidated-20260902.md` PART 2。

## POINTERS

- `docs/33` §3.2 sentinel · `docs/52` drift/B路 · `docs/81`（**U6 ruling** hongheiku 源）
- 659 合并件（审计 PART 1 + **660 任务书 PART 2**）
- `00-DUAL-POLL-PROTOCOL` · `dual_poll_status.sh` · `00-EXEC-QUEUE.md` rev106

## 压缩后自检

阶段？NOW？禁做什么？

