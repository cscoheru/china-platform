# 00-COMPASS — 会话常驻罗盘（唯一热记忆）

> **预算：全文 ≤ 80 行 / 6 KB。**

## 愿景（PRD）

可查询、可回溯研究底座。不以抓取页数为完成标准。

## 现行里程碑

| 项 | 值 |
|---|---|
| 计划 | `docs/54` 主计划 · `docs/68` spike 链 master |
| 阶段 | M4 spike 链收官（638-657 二十刀；**657 审计 PASS·有限通过〔金丝雀 5/5 批量解锁〕**）→ M2 批量 |
| NOW | **658** M2 批量（26 省 × 5 指标真实入库 via U6 + 国家锚 + P3-1 修正） |
| KPI 现状 | 省级 COVERED **31/31**（M2-c+d+e per 635 AUDITED） |
| Gate | **未 PASS**（M2 各子刀 AUDITED，未宣布 M2 PASS） |

## 红线

禁：目录/首页 FETCHED；补零；静默硬编码 value；自动 Gate/M2/M4.x/M5.x/M6 PASS；删既有 OPEN 行；碰 4 fixture 锁值（e30ee811/9232efdb/937255a5/9056001c）；数据源非政府/统计局/研究机构自取。

## NOW

658：**M2 批量刀**——26 省 × 5 指标（GDP 总量+增速+三次产业）hongheiku 转载页**真实入库** observation + source_registry（lineage 三重：hongheiku_tjgb/XX省统计局/U6）；category-first 发现（禁 /tag/）；HTTP ≤32 限速；缺省整省 BLOCKED 禁补零；**国家锚**（31 省加总 vs NBS 1,349,084.0 亿）+ 省内自洽（三产和≈总量 0.5% 容差）；**P3-1 修正** docs/82 §1.2 重写 31 行对账（25R+4B+2M2）；M2.3 升级评估（只读 31/31）；规范 **v3.4**（§META 五字段对链自检）首签。O1 零动作；≥326 green（底限 ≥316；m2 零 diff×2；19 文件集）。任务书 = `657-audit-658-tasking-consolidated-20260902.md` PART 2。659 预告 = mart flip + 前端切源。

## POINTERS

- `docs/33` §3.2 sentinel · `docs/52` drift/B路 · `docs/81`（**U6 ruling** hongheiku 源）
- 657 合并件（审计 PART 1 + **658 任务书 PART 2**）
- `00-DUAL-POLL-PROTOCOL` · `dual_poll_status.sh` · `00-EXEC-QUEUE.md` rev101

## 压缩后自检

阶段？NOW？禁做什么？

