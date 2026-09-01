# 00-COMPASS — 会话常驻罗盘（唯一热记忆）

> **预算：全文 ≤ 80 行 / 6 KB。**

## 愿景（PRD）

可查询、可回溯研究底座。不以抓取页数为完成标准。

## 现行里程碑

| 项 | 值 |
|---|---|
| 计划 | `docs/54` 主计划 · `docs/68` spike 链 master |
| 阶段 | M4.x/M5/M6 spike 链（638-646 九刀交付；**646 审计 PASS·有限通过**） |
| NOW | **647** M4.10 v4 省扩展 + 646 审计 P2/P3 修正 |
| KPI 现状 | 省级 COVERED **31/31**（M2-c+d+e per 635 AUDITED） |
| Gate | **未 PASS**（M2 各子刀 AUDITED，未宣布 M2 PASS） |

## 红线

禁：目录/首页 FETCHED；补零；静默硬编码 value；自动 Gate/M2/M4.x/M5.x/M6 PASS；删既有 OPEN 行；碰 4 fixture 锁值（e30ee811/9232efdb/937255a5/9056001c）；数据源非政府/统计局/研究机构自取。

## NOW

647：zhejiang + shandong 第 7/8 样本 16 INSERT（chain_id `real_647_m4_10_policy_detail_v4`；UUID **f 段**；已用省 HLJ/HENAN/YUNNAN/FUJIAN/GD 不得重复）+ 646 审计修正（**P2-1 F7 补登记** docs/70 §4 表尾 + P3-2 §6 措辞尾注，行内 append 不删行）+ **O1 零动作**（live-candidate 沿用 646 登记，O1 仍 OPEN）。任务书 `647-stage0-architect-m4-10-v4-f7-p2-fixes-tasking-20260901.md`。

## POINTERS

- `docs/33` §3.2 sentinel · `docs/52` drift/B路 · `docs/68`+`docs/70`（646 master）
- 646 回执 / **646 审计 PASS** / 647 任务书
- `00-DUAL-POLL-PROTOCOL` · `dual_poll_status.sh` · `00-EXEC-QUEUE.md` rev78

## 压缩后自检

阶段？NOW？禁做什么？

