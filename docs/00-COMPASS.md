# 00-COMPASS — 会话常驻罗盘（唯一热记忆）

> **预算：全文 ≤ 80 行 / 6 KB。**

## 愿景（PRD）

可查询、可回溯研究底座。不以抓取页数为完成标准。

## 现行里程碑

| 项 | 值 |
|---|---|
| 计划 | `docs/54` 主计划 · `docs/68` spike 链 master |
| 阶段 | M4.x/M5/M6 spike 链（638-647 十刀交付；**647 审计 PASS·有限通过**） |
| NOW | **648** M4.11 v5 + jiangxi 复验 + 卫生收口（三合一） |
| KPI 现状 | 省级 COVERED **31/31**（M2-c+d+e per 635 AUDITED） |
| Gate | **未 PASS**（M2 各子刀 AUDITED，未宣布 M2 PASS） |

## 红线

禁：目录/首页 FETCHED；补零；静默硬编码 value；自动 Gate/M2/M4.x/M5.x/M6 PASS；删既有 OPEN 行；碰 4 fixture 锁值（e30ee811/9232efdb/937255a5/9056001c）；数据源非政府/统计局/研究机构自取。

## NOW

648 三合一：A.0 jiangxi "403" 样本复验（1×HTTP，SHA 对比 + 内容锚点）+ A.1 M4.11 v5 **hunan + anhui** 第 9/10 样本 16 INSERT（chain_id `real_648_m4_11_policy_detail_v5`；UUID **g 段**；已用省 HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX 不重复；substitute 预授权池 jilin/liaoning/hubei/shaanxi/sichuan/guizhou/jiangsu）+ A.2 m2 报告生成测试卫生收口（tmp 路径或默认 skip；禁全量挂起套件）。O1 零动作。任务书 `648-stage0-architect-m4-11-v5-quality-hygiene-tasking-20260901.md`。

## POINTERS

- `docs/33` §3.2 sentinel · `docs/52` drift/B路 · `docs/68`+`docs/71`（647 master）
- 647 回执 / **647 审计 PASS** / 648 任务书
- `00-DUAL-POLL-PROTOCOL` · `dual_poll_status.sh` · `00-EXEC-QUEUE.md` rev80

## 压缩后自检

阶段？NOW？禁做什么？

