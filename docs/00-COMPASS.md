# 00-COMPASS — 会话常驻罗盘（唯一热记忆）

> **预算：全文 ≤ 80 行 / 6 KB。**

## 愿景（PRD）

可查询、可回溯研究底座。不以抓取页数为完成标准。

## 现行里程碑

| 项 | 值 |
|---|---|
| 计划 | `docs/54` 主计划 · `docs/68` spike 链 master |
| 阶段 | M2 批量完成（**658 审计 PASS·有限通过〔23 省入库+国家锚/自洽 PASS〕**）→ 659 前端真实化 |
| NOW | **659** mart flip + 前端切源（页面 GDP 真实化收官刀）+ P3-2 终修 |
| KPI 现状 | 省级 COVERED **31/31**（M2-c+d+e per 635 AUDITED） |
| Gate | **未 PASS**（M2 各子刀 AUDITED，未宣布 M2 PASS） |

## 红线

禁：目录/首页 FETCHED；补零；静默硬编码 value；自动 Gate/M2/M4.x/M5.x/M6 PASS；删既有 OPEN 行；碰 4 fixture 锁值（e30ee811/9232efdb/937255a5/9056001c）；数据源非政府/统计局/研究机构自取。

## NOW

659：**mart flip + 前端切源**（页面 GDP 真实化收官刀）——① `dbt/models/marts/mart_province_gdp_2024.sql`（28 省真数据 + 3 省 DATA_MISSING〔LN/HAINAN/GUIZHOU 源缺文〕禁补零；31 行守门）② 前端切源（`api.ts` USE_MOCK 默认 **false**；`page.tsx` 去 MOCK_PROVINCE_LIST 默认渲染〔mock 保留〕；3 省「数据暂缺」；`layout.tsx` 横幅 + `smoke-check.py` 更新）③ **P3-2 终修** docs/82 §1.2 rows 12-19 + §3 归属按链 SHA 实证（651=陕/川 d13b3229、652=新/蒙 04721b7、LN=649 substitute 936640d、653=SD/HB、654=GS/QH、655=NX/XZ；删循环自证）④ ≥342 green（底限 ≥336；m2 零 diff×2；20 文件集）；docs/84。O1 零动作。任务书 = `658-audit-659-tasking-consolidated-20260902.md` PART 2。

## POINTERS

- `docs/33` §3.2 sentinel · `docs/52` drift/B路 · `docs/81`（**U6 ruling** hongheiku 源）
- 658 合并件（审计 PART 1 + **659 任务书 PART 2**）
- `00-DUAL-POLL-PROTOCOL` · `dual_poll_status.sh` · `00-EXEC-QUEUE.md` rev103

## 压缩后自检

阶段？NOW？禁做什么？

