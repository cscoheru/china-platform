# 00-COMPASS — 会话常驻罗盘（唯一热记忆）

> **预算：全文 ≤ 80 行 / 6 KB。**

## 愿景（PRD）

可查询、可回溯研究底座。不以抓取页数为完成标准。

## 现行里程碑

| 项 | 值 |
|---|---|
| 计划 | `docs/54` 主计划 · `docs/68` spike 链 master |
| 阶段 | M4.x/M5/M6 spike 链（638-645 八刀交付；**645 审计 PASS**） |
| NOW | **646** M4.9 v3 + O1 B路 live-candidate + P3 修正 |
| KPI 现状 | 省级 COVERED **31/31**（M2-c+d+e per 635 AUDITED） |
| Gate | **未 PASS**（M2 各子刀 AUDITED，未宣布 M2 PASS） |

## 红线

禁：目录/首页 FETCHED；补零；静默硬编码 value；自动 Gate/M2/M4.x/M5.x/M6 PASS；删既有 OPEN 行；碰 4 fixture 锁值（e30ee811/9232efdb/937255a5/9056001c）；数据源非政府/统计局/研究机构自取。

## NOW

646：fujian + gd(首选/fallback 链) 第 5/6 样本 16 INSERT（chain_id `real_646_m4_9_policy_detail_v3`；UUID **e 段**）+ docs/52 B路 live-candidate **只登记不启用**（O1 仍 OPEN）+ 645 审计 P3 修正（7→8 distinct 等，行内 append）。任务书 `646-stage0-architect-m4-9-v3-o1-live-candidate-tasking-20260901.md`。

## POINTERS

- `docs/33` §3.2 sentinel · `docs/52` drift/B路 · `docs/68`+`docs/69`（645 master）
- 645 回执 / **645 审计 PASS** / 646 任务书
- `00-DUAL-POLL-PROTOCOL` · `dual_poll_status.sh` · `00-EXEC-QUEUE.md` rev76

## 压缩后自检

阶段？NOW？禁做什么？

