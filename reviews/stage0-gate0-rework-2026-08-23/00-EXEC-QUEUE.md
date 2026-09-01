# 00-EXEC-QUEUE — 架构师 ↔ 执行端 交接队列

> **rev 75 · 2026-09-01。**  
> 热记忆：`docs/00-COMPASS.md`。轮询：`00-DUAL-POLL-PROTOCOL`。  
> **禁止宣布 Gate / O1 / M2 / M4 / M4.8 / M5 / M6 PASS。**

## §META

- rev: 75
- updated: 2026-09-01
- ruling: 645 tasking OPEN (用户 ACK 收644 + 下发645 A；架构师本终端自签 + 自交付) → M6 spike 文档收口 (docs/68 master) + M4.8 政策详情 v2 真实化 (24 INSERT, 4 样本含 henan zwgk root; chain_id='real_645_m4_8_policy_detail_v2'; UUID d 段 ≠ 644 c 段) 并行

## §CURRENT

- status: **645 tasking DELIVERED · cc_head pending**
- cc_head: `f57712f` (638 tasking) + `f1fdad5` (638 delivery) + `4123fcb` (638 cc_head) + `ee86977` (638 receipt) + `c3968ec` (639 tasking) + `f70ac95` (639 EXEC-QUEUE) + `1fca08e` (639 delivery) + `37aa148` (639 cc_head) + `11778db` (639 receipt) + `b09a511` (640 tasking) + `51cf5ea` (640 delivery) + `96c6d89` (640 cc_head) + `a644e47` (640 receipt) + `60e2eb8` (641 tasking) + `5269364` (641 EXEC-QUEUE) + `a1c489a` (641 delivery) + `65ec238` (641 cc_head) + `da0e77a` (641 receipt) + `4c605d5` (642 tasking) + `f6c5668` (642 delivery) + `2d6f0da` (642 cc_head) + `ca5a4a0` (642 receipt) + `c7b8aa5` (643 tasking) + `834bc30` (643 delivery) + `ac2e8e6` (643 cc_head) + `57fa859` (643 receipt) + `cd6dffc` (644 tasking) + `aac8225` (644 delivery) + `a66215b` (644 cc_head) + `899bd41` (644 receipt) + `51569d7` (645 tasking) + `a235f94` (645 delivery)
- last_audit: `634-stage0-cursor-s633-m2-b-audit-PASS-20260831.md`
- tasking: `645-stage0-architect-m6-m4-8-policy-detail-v2-tasking-20260901.md` (OPEN — 架构师自签)
- last_delivery: `a235f94` (645 delivery)
- last_receipt: `899bd41` (644 receipt — `644-stage0-cc-m5-3-m4-7-parallel-receipt-20260901.md`)
- m4_decision: 645 = M6 spike 文档收口 (docs/68 master + docs/45/50/53/66/67 互链) + M4.8 政策详情 v2 真实化 (沿用 644 3 试点省 × 1 detail each × 6 政策表 = 18 INSERT + 纳入 644 留作扩展的 henan `bd4c4c51...` (zwgk root) 作为第 4 样本 = 24 INSERT planned, chain_id='real_645_m4_8_policy_detail_v2'; UUID d 段 ≠ 644 c 段) 并行

## §NOW

CC 落地 645-A.1 (M6 spike 文档收口: docs/68 master §1-§6 + docs/66/67 §6 末「→ 645 docs/68」尾注 + docs/45 §6.2 表末 +1 行 + docs/50 §4.4 末 +1 行 + docs/53 §5 末 +1 项 M6 互链) + 645-A.2 (M4.8 fetch: 4 样本 = heilongjiang c107884 + henan zfgb + henan zwgk root (NEW 644 留作扩展) + yunnan zfgzbg；fetched_count=4；4 distinct SHA = bad8be51 / dfa38998 / bd4c4c51 / f33eba53；http_count≤12) + 645-A.3 (M4.8 seed SQL 24 INSERT 6 政策表 × 4 真实 each；lineage.is_demo='false' 真实化 sentinel；chain_id='real_645_m4_8_policy_detail_v2'；UUID d 段 ≠ 644 c 段) + 645-A.4 (docs/68 + docs/69 §1-§6 双文档架构师级审查) + 645-A.5 (4 文件: M6 report+evidence + M4.8 report+evidence) + 645-A.6 (EXEC-QUEUE rev74 → rev75 — 645 tasking OPEN) + 645-B (12 用例 = ≥6 M6 + ≥6 M4.8，12/12 pytest green) + 645-C (回执 + commit + 双推)。

## §CHAIN_TAIL

| 刀 | 状态 | 一句话 |
|---|---|---|
| 631 | AUDITED | M2-a |
| 633 | **AUDITED** | M2-b 5/31；634 PASS |
| 635 | **AUDITED** | M2-c+d+e：31/31 ≥ 20/31 + QUARANTINED-WEAK 跨源核对 + q1 研究页 |
| 636 | **AUDITED** | M2-f：文档收口 + 2001-onwards probe（适用 cell 1541: REACHABLE 0 / PARTIAL 770 / BLOCKED 771） |
| 637 | **DELIVERED** | M3 启动审查：架构师推荐路径 C（维持现状 + 转向 M4-M5）；详见 docs/57 |
| 638 | **DELIVERED** | M4.1 人物表 schema 收口 + 政府工作报告/任免公告可达性 probe (23/32 REACHABLE)；WAF 假设修正 |
| 639 | **DELIVERED** | M4.2 任免数据 demo: 二次 probe (REACHABLE 6 试点省 + PARTIAL 8 + BLOCKED 15) + 5 demo is_demo=true 隔离 + docs/59 |
| 640 | **DELIVERED** | M4.3 政策项目 demo (6 表 × 3 demo each, lineage JSONB sentinel is_demo='true' 隔离, demo SHA 0…02 区分) + 二次 probe (REACHABLE 2 = 黑龙江 zfwj/zfgb; 关键反发现: 6 任免源 ≠ 政策源; 仅 1 试点省政策 REACHABLE) + 71/71 pytest green |
| 641 | **DELIVERED** | M4.4 黑龙江政策真实化 spike (hlj.gov.cn 政务公开 landing 真实抓取 4 HTTP / 3 cell SHA + 6 政策表 × 1 real each lineage.is_demo='false' 真实化 sentinel + 真实 SHA `26e5379d...b87ab` ≠ 640 demo SHA `0…02` + docs/61 架构师级审查 + 78/78 pytest green) |
| 642 | **DELIVERED** | M5 WAF spike (10 cells ≤10 HTTP, MIXED verdict = 8 BLOCKED + 2 REACHABLE; 5 省 zfwj 404 路径别名; 国务院 /zhengce/content/ + /zwgk/ 403 WAF 网防G01 marker 真出现; 福建/河南 /zwgk/ 200 REACHABLE) + M4.5 任免真实化 (3 试点省 henan/guangdong/guizhou × 6 政策表 spike 18 INSERT lineage.is_demo='false' chain_id='real_642_m4_5_renmian'; 3 新真实 SHA 全 distinct ≠ 640/641/639 demo/real SHA; docs/62 + docs/63 §1-§6 架构师级审查; 16/16 pytest green) |
| 643 | **DELIVERED** | M5 WAF 网防G01 假设验证二次 (10 cells MIXED = 8 BLOCKED + 2 REACHABLE; 4 BLOCKED 省 zfwj/zfgb/zcwj/szfwj/wjzl 全部 404 路径别名; henan /zwgk/zfgb/ 200 REACHABLE 验证河南路径别名 = zfwj; 国务院 /zhengceku/ 403 WAF 网防G01 marker 真出现; 国务院 /zhengce/ root 200 REACHABLE 验证 WAF selective) + M4.6 政府工作报告真实化 (3 试点省 hlj/henan/yunnan × 8 表 = 24 INSERT lineage.is_demo='false' chain_id='real_643_m4_6_govreport', 3 新真实 SHA e68099df/63109491/93fe23b3 全 distinct ≠ 642/641/640/639; fujian/gd 路径别名 404 排除; guizhou anchor 不匹配排除; docs/64 + docs/65 §1-§6 架构师级审查; 17/17 pytest green; 643-C 双推完成) |
| 644 | **DELIVERED** | M5 WAF spike 第三次收口 (10 cells ≤10 HTTP, MIXED = 7 BLOCKED + 3 REACHABLE; 国务院 /zhengce/zhengceku/ 403 WAF 网防G01 marker 第三次确认; /zhengce/content_xxx.htm 404 (content_id 不存在 非 WAF marker); /zwgk/ 替代 retry 路径 (zcwj/zcfg/2026-08/...) 全部 404 (路径不存在 非 WAF marker); 3 BLOCKED 省 /zwgk/ root REACHABLE 第三次确认 (fujian/henan/yunnan)) + M4.7 政策详情真实化 (3 试点省 hlj/henan/yunnan × 1 detail each × 6 政策表 = 18 INSERT lineage.is_demo='false' chain_id='real_644_m4_7_policy_detail', 3 新真实 SHA bad8be51/dfa38998/f33eba53 全 distinct ≠ 643/642/641/640/639 demo/real SHA; UUID c 段 ≠ 643 b 段; hlj c107884 避开 643 c107882; docs/66 + docs/67 §1-§6 架构师级审查; 18/18 pytest green; 644-C 双推完成 delivery `aac8225`) |
| 645 | **OPEN** | M6 spike 文档收口 (docs/68 master + docs/45/50/53/66/67 互链补登) + M4.8 政策详情 v2 真实化 (沿用 644 3 试点省 × 1 detail each × 6 政策表 = 18 INSERT + 纳入 644 留作扩展的 henan `bd4c4c51...` (zwgk root) 作为第 4 样本 = **24 INSERT planned**, chain_id='real_645_m4_8_policy_detail_v2' ≠ 644 chain_id; UUID d 段 ≠ 644 c 段; 4 新真实 SHA bad8be51/dfa38998/bd4c4c51/f33eba53 复用 644 SHA + 1 NEW henan zwgk root; docs/68 + docs/69 §1-§6 双文档架构师级审查; 架构师本终端自签 + 自交付) |

## §ACK

- 2026-09-01 / 用户 / 收644，下发645 A
- 2026-09-01 / CC / 645 tasking OPEN — `reviews/stage0-gate0-rework-2026-08-23/645-stage0-architect-m6-m4-8-policy-detail-v2-tasking-20260901.md` (commit `51569d7` 双推完成); M6 spike 文档收口 + M4.8 政策详情 v2 真实化 (24 INSERT, 4 样本含 henan zwgk root 第 4 样本)。
- 2026-09-01 / CC / 644 DELIVERED — `reviews/stage0-gate0-rework-2026-08-23/644-stage0-cc-m5-3-m4-7-parallel-receipt-20260901.md` (待 cc_head backfill 后写入); 18/18 pytest green; delivery commit `aac8225` (已双推 origin→github, SSH fallback HTTPS 443 阻塞); M5 第三次收口 + M4.7 政策详情真实化 (18 INSERT)。
- 2026-09-01 / CC / 643 DELIVERED — `reviews/stage0-gate0-rework-2026-08-23/643-stage0-cc-m5-2-m4-6-parallel-receipt-20260901.md`; 17/17 pytest green; commit `834bc30`; github push via SSH (HTTPS 443 blocked)。
- 2026-09-01 / 用户 / 保持现状，继续644 (M5 WAF 第三次收口 + M4.7 政策详情真实化 并行 spike；架构师推荐 scope A)
- 2026-09-01 / CC / 642 DELIVERED — `reviews/stage0-gate0-rework-2026-08-23/642-stage0-cc-m5-m4-5-parallel-receipt-20260901.md`; 16/16 pytest green。
- 2026-09-01 / 用户 / 接受 642 scope (M5 WAF spike + M4.5 任免真实化 并行)
- 2026-09-01 / 用户 / 接收 640 = M4.3 政策项目 demo，签 640 tasking
- 2026-09-01 / CC / 639 DELIVERED — `reviews/stage0-gate0-rework-2026-08-23/639-stage0-cc-m4-2-renmian-demo-receipt-20260901.md`; 64/64 pytest green。
- 2026-09-01 / 用户 / 接收 639 scope（ccdi 公告列表 + 23 试点省 + ≤5 条 demo）
- 2026-09-01 / 用户 / 接收 638 → 进入 639 (M4.2)
- 2026-09-01 / CC / 638 DELIVERED — `reviews/stage0-gate0-rework-2026-08-23/638-stage0-cc-m4-1-people-schema-gov-report-probe-receipt-20260901.md`; 57/57 pytest green。
- 2026-09-01 / 用户 / 接收 637 路径 C, 进入 638
- 2026-09-01 / CC / 637 DELIVERED — `reviews/stage0-gate0-rework-2026-08-23/637-stage0-cc-m3-launch-conditions-review-receipt-20260901.md`; 架构师推荐路径 C。
- 2026-09-01 / CC / 636 DELIVERED — `reviews/stage0-gate0-rework-2026-08-23/636-stage0-cc-m2-f-docs-closure-backfill-feasibility-receipt-20260901.md`; 40/40 pytest green。
- 2026-08-31 / CC / 635 DELIVERED — `reviews/stage0-gate0-rework-2026-08-23/635-stage0-cc-m2-cde-coverage-crosscheck-page-receipt-20260831.md`; 32/32 pytest green。
- 2026-08-31 / 用户 / 审 633 并签大任务
