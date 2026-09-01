# 00-COMPASS — 会话常驻罗盘（唯一热记忆）

> **预算：全文 ≤ 80 行 / 6 KB。**

## 愿景（PRD）

可查询、可回溯研究底座。不以抓取页数为完成标准。

## 现行里程碑

| 项 | 值 |
|---|---|
| 计划 | `docs/54` 主计划 · `docs/68` spike 链 master |
| 阶段 | M4.x/M5/M6 spike 链（638-649 十二刀交付；**649 审计 PASS·有限通过**） |
| NOW | **650** M4.13 v7（guizhou+jiangsu）+ P3-1 蓝图更正 |
| KPI 现状 | 省级 COVERED **31/31**（M2-c+d+e per 635 AUDITED） |
| Gate | **未 PASS**（M2 各子刀 AUDITED，未宣布 M2 PASS） |

## 红线

禁：目录/首页 FETCHED；补零；静默硬编码 value；自动 Gate/M2/M4.x/M5.x/M6 PASS；删既有 OPEN 行；碰 4 fixture 锁值（e30ee811/9232efdb/937255a5/9056001c）；数据源非政府/统计局/研究机构自取。

## NOW

650：M4.13 v7——**guizhou + jiangsu** 第 13/14 样本 16 INSERT（chain_id `real_650_m4_13_policy_detail_v7`；UUID **i 段**；已用省〔actual 口径〕HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX/HUN/AH/LN/JL 不重复；递补池 shaanxi→sichuan）+ **P3-1 蓝图更正**（seed_m4_12 代换行 province/name → LIAONING/辽宁省…+尾注）+ 规范固化：代换行 registry 标注 = actual_province。O1 零动作；backfill 三齐 + rev header 同步。任务书 `650-stage0-architect-m4-13-v7-substitute-labeling-tasking-20260901.md`。

## POINTERS

- `docs/33` §3.2 sentinel · `docs/52` drift/B路 · `docs/68`+`docs/73`（649 master）
- 649 回执 / **649 审计 PASS** / 650 任务书
- `00-DUAL-POLL-PROTOCOL` · `dual_poll_status.sh` · `00-EXEC-QUEUE.md` rev85

## 压缩后自检

阶段？NOW？禁做什么？

