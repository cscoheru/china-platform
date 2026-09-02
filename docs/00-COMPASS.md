# 00-COMPASS — 会话常驻罗盘（唯一热记忆）

> **预算：全文 ≤ 80 行 / 6 KB。**

## 愿景（PRD）

可查询、可回溯研究底座。不以抓取页数为完成标准。

## 现行里程碑

| 项 | 值 |
|---|---|
| 计划 | `docs/54` 主计划 · `docs/68` spike 链 master |
| 阶段 | M4.x/M5/M6 spike 链（638-652 十五刀交付；**652 审计 PASS·有限通过**） |
| NOW | **653** M4.16 v10（shandong+hubei 双复试）BLOCKED_NO_POOL 真网首触发 |
| KPI 现状 | 省级 COVERED **31/31**（M2-c+d+e per 635 AUDITED） |
| Gate | **未 PASS**（M2 各子刀 AUDITED，未宣布 M2 PASS） |

## 红线

禁：目录/首页 FETCHED；补零；静默硬编码 value；自动 Gate/M2/M4.x/M5.x/M6 PASS；删既有 OPEN 行；碰 4 fixture 锁值（e30ee811/9232efdb/937255a5/9056001c）；数据源非政府/统计局/研究机构自取。

## NOW

653：M4.16 v10 **shandong + hubei 双复试**第 19/20 样本（647 shandong 4 连 BLOCKED 史 + 649 hubei 槽被代换史；**真网 BLOCKED_NO_POOL 首触发最佳概率**——两态合法：双 REACHABLE→16 INSERT / 任一 BLOCKED→0 INSERT+留痕不代换 per 红线 14；lineage 全行 `retry_of`；chain_id `real_653_m4_16_policy_detail_v10`；UUID **l 段**）+ 652 审计 P4 处置规范 v2（status 收口与 §NOW 同 commit 原子完成 + "待复核"复核后必清）+ docs/77 §1-§6。O1 零动作；≥179 green（底限 ≥175）。单文件模式：任务书 = `652-audit-653-tasking-consolidated-20260902.md` PART 2。

## POINTERS

- `docs/33` §3.2 sentinel · `docs/52` drift/B路 · `docs/76`（652 master）
- 652 合并件（审计 PART 1 + **653 任务书 PART 2**）
- `00-DUAL-POLL-PROTOCOL` · `dual_poll_status.sh` · `00-EXEC-QUEUE.md` rev91

## 压缩后自检

阶段？NOW？禁做什么？

