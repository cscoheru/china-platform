# M6 spike 文档系列收口 master + M4.8 政策详情 v2 真实化 — 报告（2026-09-01，knife 645 M6 side）

> **类型**: 645-A.5 M6 master 报告 (architecture-level; **不写 cegr.* 表**)
> **前置**: 638-644 全部 DELIVERED (M4.1-M4.7 + M5.1-M5.3)
> **范围**: M6 spike 文档系列收口 master + 互链补登 (5 处)
> **架构师依据**: 645 tasking §2.645-A.1 + §3.645-A.1b

## 0. 顶层裁定

**REAL_DELIVERED (read-only on production; no cegr.* mutation)** — 645-A.1 docs/68 M6 master §1-§6 + 645-A.4 docs/69 M4.8 §1-§6 双文档 + 645-A.1b 4 处互链补登 (docs/45/50/53 + docs/66/67 §6 末尾注) + 645-A.6 EXEC-QUEUE rev74 → rev75 落地。

## 1. 645-A.1 docs/68 M6 master §1-§6

### 1.1 §1 M4.x + M5 spike 链落地终态（8 刀全链表）

| 刀号 | milestone | docs | 关键反发现 | 状态 |
|---|---|---|---|---|
| 638 | M4.1 | docs/58 | 23/32 REACHABLE; WAF 假设修正 | DELIVERED |
| 639 | M4.2 | docs/59 | 二次 probe (6 REACHABLE + 8 PARTIAL + 15 BLOCKED); 5 demo is_demo=true | DELIVERED |
| 640 | M4.3 | docs/60 | 6 表 × 3 demo each lineage.is_demo=true; 71/71 pytest green | DELIVERED |
| 641 | M4.4 | docs/61 | hlj 政务公开 landing 真实抓; lineage.is_demo=false; 78/78 pytest green | DELIVERED |
| 642 | M5 + M4.5 | docs/62 + docs/63 | M5 WAF 10 cells MIXED (8 BLOCKED + 2 REACHABLE); 国务院 /zhengce/ + /zwgk/ 403 网防G01 marker 真出现; 福建/河南 /zwgk/ 200 REACHABLE; 16/16 pytest green | DELIVERED |
| 643 | M5.2 + M4.6 | docs/64 + docs/65 | M5.2 WAF 10 cells MIXED; 国务院 /zhengceku/ 403 网防G01 marker; 17/17 pytest green | DELIVERED |
| 644 | M5.3 + M4.7 | docs/66 + docs/67 | M5.3 WAF 10 cells MIXED (7 BLOCKED + 3 REACHABLE); 国务院 /zhengce/zhengceku/ 403 第三次确认; 18/18 pytest green | DELIVERED |
| **645** | **M6 + M4.8** | **docs/68 + docs/69** | **M6 spike 文档系列收口 master + M4.8 政策详情 v2 spike 三次 (24 INSERT + 8 source = 32 INSERT total; chain_id='real_645_m4_8_policy_detail_v2'; UUID d 段)** | **OPEN → DELIVERED** |

### 1.2 §2 spike 边界统一表（8 刀）

| 刀号 | milestone | ≤ HTTP | cells | INSERT | chain_id | UUID prefix | 真实化 sentinel |
|---|---|---|---|---|---|---|---|
| 638 | M4.1 (probe) | ≤10 | 23 | n/a | n/a | n/a | n/a |
| 639 | M4.2 (demo) | ≤10 | 23 | 5 demo | `demo_639` | demo prefix | is_demo='true' |
| 640 | M4.3 (demo) | ≤10 | 6 | 18 demo | `demo_640` | demo prefix | is_demo='true' |
| 641 | M4.4 (real spike) | ≤4 | 1 | 6 real | `real_641_heilongjiang` | real prefix | is_demo='false' |
| 642 | M5 (probe) + M4.5 (real) | ≤10 + ≤10 | 10 + 6 | 18 real | `real_642_m4_5_renmian` | b 段 | is_demo='false' |
| 643 | M5.2 (probe) + M4.6 (real) | ≤10 + ≤12 | 10 + 9 | 24 real | `real_643_m4_6_govreport` | b 段 | is_demo='false' |
| 644 | M5.3 (probe) + M4.7 (real) | ≤10 + ≤12 | 10 + 5 | 18 real | `real_644_m4_7_policy_detail` | c 段 | is_demo='false' |
| **645** | **M6 (master) + M4.8 (real v2)** | **≤12** | **4** | **24 real** | **`real_645_m4_8_policy_detail_v2`** | **d 段** | **is_demo='false'** |

### 1.3 §3 lineage JSONB `is_demo='false'` 真实化 sentinel 沿用链

- docs/33 §3.2 sentinel 沿用 5 刀 (641/642/643/644/645)
- 009 migration (5 政策表) + 010 migration (project_event) + 014/015 migration (spike 沿用) = lineage JSONB 全表已覆盖
- 真实数据 INSERT 必须 `lineage->>'is_demo' = 'false'`
- 沿用 sentinel 一致性更高；**不新写 016 migration**

### 1.4 §4 chain_id 区分裁定

8 个 distinct chain_id (638-645 各唯一) — 不撞 ✓

### 1.5 §5 真实 SHA 区分表（17 条，4 SHA 漂移事件）

- 645 hlj `c107884/list.shtml` SHA drift: 644 `bad8be51` → 645 `6237cd48` (per docs/52 (a)/(b) policy)
- 645 seed SQL 使用 645 实际抓取的 SHA `6237cd48`，不沿用 644 的 `bad8be51`
- drift 不影响 lineage JSONB `is_demo='false'` 真实化判定

### 1.6 §6 646 下一步 + 不宣称 PASS

646 scope 候选: A (推荐) / C / E / D (沿用 644 docs/67 §5)

## 2. 645-A.1b 4 处互链补登

| 文档 | 节 | append 内容 |
|---|---|---|
| docs/45 | §6.2 表末 | M4.x + M5 spike 文档系列收口 docs/45 §6.2 表末 +1 行 per 645 |
| docs/50 | §4.4 第 48 项 | docs/53 §5 第 48 项 M6 master 互链补登 per 645 |
| docs/53 | §5 第 48 项 | M6 master + M4.8 互链补登 per 645 (含 7 子节 A-G) |
| docs/66 | §6 末 | → 645 docs/68 (M6 master 尾注) |
| docs/67 | §6 末 | → 645 docs/69 (M4.8 尾注) |

## 3. 645-A.4 docs/69 M4.8 §1-§6

- §1 M4.8 落地终态 (8 子刀表)
- §2 M4.8 spike 边界 (vs 644 tasking 规划 / 实测对比 / 32 INSERT total / 4 distinct SHA)
- §3 真实化 demo SQL 结构 (24 INSERT 政策表 + 8 source = 32 INSERT total; lineage JSONB 真实化 sentinel 一致 shape; geo_entity 真实化方案)
- §4 lineage 真实化 sentinel (沿用 009+010+014+015) + chain_id 区分裁定 + 真实 SHA 区分表 (645 drift event)
- §5 646 下一步 (架构师推荐)
- §6 下一步 + 不宣称 PASS

## 4. 645-A.6 EXEC-QUEUE rev74 → rev75

- commit `8fc0737` 双推完成 (origin → github SSH fallback; HTTPS 443 blocked)
- §META rev: 75
- §CURRENT: 645 tasking OPEN · 架构师自签 + 自交付
- cc_head chain extended with `51569d7` (645 tasking)
- m4_decision: 645 = M6 spike 文档收口 + M4.8 政策详情 v2 真实化 (24 INSERT + 8 source = 32 INSERT total)
- §NOW rewritten for 645-A.1 through 645-C
- §CHAIN_TAIL 645 OPEN row appended
- §ACK: 645 tasking entry + 用户 ACK "收644，下发645 A"

## 5. 红线遵守

- ✓ 不发布 Gate / O1 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS
- ✓ 不补零 / 不静默硬编码 value
- ✓ 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED
- ✓ 不改 docs/45/50/53/66/67 §5/6 正文 (仅 append 互链)
- ✓ 不碰 4 fixture 锁值 (nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c)
- ✓ 数据源治理铁律 2026-08-29: 数据源唯一=政府/统计局/研究机构自取; 用户零裁定; 执行端不可提任何用户裁定事项
- ✓ 不删既有 OPEN 行
- ✓ 完成 = observation SUCCESS (no PARTIAL)

## 6. 不宣称 PASS

- 645 完成：M6 spike 文档系列收口 master (docs/68) + M4.8 政策详情 v2 真实化 (24 INSERT + 8 source = 32 INSERT total; chain_id='real_645_m4_8_policy_detail_v2'; UUID d 段 ≠ 644 c 段; 4 NEW SHA 6237cd48/dfa38998/bd4c4c51/f33eba53)
- 架构师（用户）接受/驳回 646 推荐 scope
- **不宣布** Gate / O1 / M2 / M4 / M4.5 / M4.6 / M4.7 / M4.8 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线）

— End 645 docs/reports/m6_spike_docs_closure_20260901.md —