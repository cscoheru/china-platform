# 645 待 Cursor 审验 — 指令汇总（knife 645, 2026-09-01）

> **角色**: 架构师 → Cursor (审验端)
> **范围**: 645 M6 master + M4.8 v2 双刀并行 DELIVERED（5 commits + 双推完成）
> **用途**: Cursor 单文件审验 handoff；本文件为唯一裁定入口
> **架构师豁免**: 不主动 commit/push 已被用户豁免 (2026-08-31 21:50); 645 架构师自签 + 自交付

---

## §0. 项目背景（Cursor 复原后必读）

### §0.1 项目愿景

**china-platform（国窖 / CEGR 治理仓）** — 中国地方政府公开数据治理仓，定位为政府/统计局/研究机构一手数据源的 **真实化 ETL + lineage 治理** 系统。

**核心原则**（沿用 638-644 + 645, 不变量）:
- **数据源唯一 = 政府/统计局/研究机构自取**；用户零裁定（除注册/登录/付费/UI 人工验收）；执行端不可提任何用户裁定事项（2026-08-29 数据源治理铁律）
- **lineage JSONB `is_demo='false'` 真实化 sentinel** 沿用 docs/33 §3.2，9 真实化刀（641/642/643/644/645）一致 shape
- **完成 = observation SUCCESS, 禁止 PARTIAL**（沿用红线）
- **零爬网 / 零镀铬四轨 / 不把目录页标 FETCHED**（沿用红线）
- **4 fixture 锁值永不动**：nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c（沿用红线）

**技术栈**:
- PostgreSQL schemas: `cegr` (production) + `cegr_staging` (spike 沙盒)
- dbt mart 模型: `mart_city_evidence_chain` / `mart_city_seven_dim_overview` (10 城市 × 6 维度)
- Migrations: 009 (5 政策表) + 010 (project_event) + 014/015 (spike 沿用)
- 后端: Python 3.14 + pytest 9.0.2
- 前端: skeleton mode by design（不渲染，仅 schema 占位）

### §0.2 三角色机制

```
架构师（本终端，Claude Opus）         执行端（另开 CC 实例）           用户（人类裁决者）
       │                                  │                              │
       │ ── tasking (645-tasking) ──────► │                              │
       │                                  │ ── 5 commits + 双推 ───────► │
       │ ◄─ 回执 + 红线自审 ──────────── │                              │
       │                                  │                              │
       │ ── 5 commits 已就绪 ──────────────────────────────────────────► │
       │                                  │                              │
       │ ◄── 接受/驳回 + 下发 646 scope ──────────────────────────────────│
```

- **架构师**：本终端（Claude Opus），负责 tasking + 审验裁定 + 红线守护
- **执行端**：另开 CC 实例，负责落地 (commits / 双推 / pytest)（645 由豁免机制合并入本终端）
- **用户**：人类裁决者，接受/驳回 scope，下发新刀
- **交接队列**：`reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` (当前 rev 75)
- **轮询协议**：`reviews/stage0-gate0-rework-2026-08-23/00-DUAL-POLL-PROTOCOL.md`
- **用户休息协议**（2026-08-29 立）：用户说"去休息"→ 架构师继续 ARCH-PULSE 30min cadence → 3 次心跳（≈90min）执行端无 ACK/DELIVERED 则暂停所有新刀签发

### §0.3 关键里程碑文件（必读，按层级）

| 层 | 文件 | 作用 |
|---|---|---|
| **总纲** | `docs/00-COMPASS.md` | 热记忆；架构师每轮必读 |
| **策略** | `docs/33-stage2-s210-lite-lineage-sentinel-20260826.md` | §3.2 lineage JSONB sentinel 沿用链 |
| **漂移** | `docs/52-stage2-s210-lite-source-doc-drift-policy-20260826.md` | SHA drift (a) update / (b) flag 策略 |
| **Gate2 索引** | `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | §6.2 表末 645 互链 +1 行 |
| **Gate2 packet** | `docs/50-stage2-gate2-review-packet-draft-20260826.md` | §4.4 第 48 项 645 互链 |
| **运维手册** | `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | §5 第 48 项 645 互链（7 子节 A-G）|
| **M4.1 人物表** | `docs/58-m4-1-people-schema-gov-report-probe-20260901.md` | 638 DELIVERED |
| **M4.2 任免 demo** | `docs/59-m4-2-renmian-demo-second-probe-20260901.md` | 639 DELIVERED |
| **M4.3 政策 demo** | `docs/60-m4-3-policy-project-demo-20260901.md` | 640 DELIVERED |
| **M4.4 hlj 真实化** | `docs/61-m4-4-heilongjiang-real-spike-20260901.md` | 641 DELIVERED |
| **M5.1 WAF + M4.5** | `docs/62 + docs/63` | 642 DELIVERED |
| **M5.2 + M4.6** | `docs/64 + docs/65` | 643 DELIVERED |
| **M5.3 + M4.7** | `docs/66 + docs/67` | 644 DELIVERED |
| **M6 master + M4.8** | `docs/68 + docs/69` | **645 DELIVERED (本次审验)** |

### §0.4 现状（截至 2026-09-01）

**已落地（8 刀）**:
- 638-640: 3 spike demo 隔离 (`demo_639` / `demo_640` lineage.is_demo=true)
- 641-645: 5 真实化 spike (`real_641_heilongjiang` / `real_642_m4_5_renmian` / `real_643_m4_6_govreport` / `real_644_m4_7_policy_detail` / `real_645_m4_8_policy_detail_v2`)
- 638-645 共 8 chain_id 全部 distinct, UUID prefix 沿 demo→real→b→c→d 段严格递增
- 22/22 pytest green（645 累计）；71 → 78 → 16 → 17 → 18 → 22 测试规模递增

**未落地（红线守护）**:
- **Gate / O1 / O2 / O3 / M2 / M4 / M4.5 / M4.6 / M4.7 / M4.8 / M5 / M5.1 / M5.2 / M5.3 / M6 — 15 个里程碑不宣布 PASS**
- Gate 1 启动需要 M2 Gate 后才合法（当前 M2 仅 M2-a/M2-b/M2-c+d+e/M2-f AUDITED，未 M2 PASS）
- dbt mart flip: 60 行 demo 中仅 1 行（nanjing + CONDITION）真实化 pilot，O1 全量未启动

**646 待定**:
- 当前 645 全部 DELIVERED，架构师（用户）接受/驳回 scope 后下发 646
- scope A 推荐（M6 收口收口收口 + M4.9 政策详情 v3 试点省扩展）
- 候选 scope: A / B / C / D / E（详见 §G）

### §0.5 与 645 相关的关键背景

**为何 645 选 d 段 UUID？** — 沿用 638-644 UUID prefix 严格递增（demo→real→b→c→d），保证未来 e/f/g 段仍可扩展。d 段（d1eebc99-d6eebc99）≠ 644 c 段（c1eebc99-c2eebc99）= 零碰撞保证。

**为何 645 chain_id 末段加 `_v2`？** — 645 沿用 644 M4.7 模式（3 试点省 × 1 detail each × 6 政策表 = 18 INSERT），但额外纳入 henan zwgk root 第 4 样本 = 24 INSERT。`_v2` 标记这是 644 模式的 v2 扩展版本（不是 v1 重复）。

**为何 hlj SHA drift？** — docs/52 (a) policy: 政府公开页面 SHA 每次抓取可能微变（CDN / 时间戳 / 广告脚本）。644 抓 `bad8be51`，645 重抓得 `6237cd48` = 漂移事件，不影响 `lineage.is_demo='false'` 真实化判定，仅标记需文档化。

**为何 4 fixture 锁值永不动？** — `nbs / nbs_live / sz / hb` 是 4 个前端骨架的 fixture 锁值（4 SHA: e30ee811 / 9232efdb / 937255a5 / 9056001c），任何修改都会导致前端骨架渲染错位。spike 数据真实化与前端 fixture 完全解耦。

---

## §A. 645 概览

### A.1 范围
- **M6 spike 文档系列收口 master** (`docs/68-m6-spike-docs-closure-20260901.md` §1-§6)
  - 8 刀全链表 (638-645) / spike 边界统一表 / lineage JSONB sentinel / chain_id 区分裁定 / 真实 SHA 区分表 (17 行) / 646 下一步
- **M4.8 政策详情 v2 真实化** (`docs/69-m4-8-policy-detail-real-v2-20260901.md` §1-§6)
  - 4 样本 (heilongjiang c107884 + henan zfgb + henan zwgk root NEW + yunnan zfgzbg)
  - 32 INSERT total: 24 政策表 + 4 source_registry + 4 source_document
  - 4 distinct SHA: 6237cd48 (hlj drift) / dfa38998 (henan zfgb reuse) / bd4c4c51 (henan zwgk root NEW) / f33eba53 (yunnan reuse)
- **4 处互链补登 closure**: docs/45 §6.2 表末 / docs/50 §4.4 第 48 项 / docs/53 §5 第 48 项 / docs/66 §6 末 / docs/67 §6 末
- **22/22 pytest green** (M6 10 + M4.8 12)
- **EXEC-QUEUE rev 75**: §CURRENT status DELIVERED; §CHAIN_TAIL 645 OPEN → DELIVERED; §ACK entry appended

### A.2 5 commits 全部双推

| # | SHA | role | origin | github |
|---|-----|------|--------|--------|
| 1 | `a235f94` | delivery (15 files, 1866 insertions) | ✓ | ✓ |
| 2 | `73c74bc` | cc_head (cc_head chain +645 delivery) | ✓ | ✓ |
| 3 | `0677111` | receipt (`645-stage0-cc-m6-m4-8-parallel-receipt-20260901.md`, 175 行) | ✓ | ✓ |
| 4 | `dffdea5` | receipt-backfill (cc_head chain +73c74bc +0677111) | ✓ | ✓ |
| 5 | `6383da6` | DELIVERED + CHAIN_TAIL + ACK entry | ✓ | ✓ |

---

## §B. Cursor 审验文件清单（按审验顺序）

### B.1 第一组: 核心 spike 文档 (2 文件)
1. `docs/68-m6-spike-docs-closure-20260901.md` — M6 master (161 行, 6 §)
2. `docs/69-m4-8-policy-detail-real-v2-20260901.md` — M4.8 v2 (217 行, 6 §)

### B.2 第二组: 互链补登 (5 文件, append-only)
3. `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` — §6.2 表末 +1 行
4. `docs/50-stage2-gate2-review-packet-draft-20260826.md` — §4.4 第 48 项
5. `docs/53-stage2-public-ingest-ops-handbook-20260826.md` — §5 第 48 项 (含 7 子节 A-G)
6. `docs/66-m5-waf-third-pass-20260901.md` — §6 末尾注
7. `docs/67-m4-7-policy-detail-real-20260901.md` — §6 末尾注

### B.3 第三组: 代码 / 脚本 / SQL (3 文件)
8. `scripts/fetch_m4_8_policy_detail_v2_2024.py` — fetch script 4 cells (≤12 HTTP)
9. `scripts/seed_m4_8_policy_detail_real_v2.sql` — 32 INSERT total (14 INSERT 语句 × 多行 VALUES)
10. `evidence_pack/m4_8_policy_detail_real_v2_20260901.json` — 4 cells REAL_FETCHED + spike_boundary

### B.4 第四组: 报告 + evidence (4 文件)
11. `docs/reports/m6_spike_docs_closure_20260901.md` — M6 报告 (6 §)
12. `docs/reports/m4_8_policy_detail_real_v2_20260901.md` — M4.8 报告
13. `evidence_pack/m6_spike_docs_closure_20260901.json` — knife=645 / milestone=M6 / chain_ids 8 distinct
14. `evidence_pack/m4_8_policy_detail_real_v2_20260901.json` — knife=645 / milestone=M4.8 / spike_boundary 32 INSERT

### B.5 第五组: 测试 (2 文件, 22 用例)
15. `tests/test_m6_spike_docs_closure.py` — 10 用例
16. `tests/test_m4_8_policy_detail_real_v2.py` — 12 用例

### B.6 第六组: 回执 + 队列 (2 文件)
17. `reviews/stage0-gate0-rework-2026-08-23/645-stage0-cc-m6-m4-8-parallel-receipt-20260901.md` — 回执 (175 行, §PHOTO-1..6)
18. `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` — 队列 rev 75

### B.7 第七组: 上下游参考 (4 文件, 已 DELIVERED 仅参照)
19. `reviews/stage0-gate0-rework-2026-08-23/645-stage0-architect-m6-m4-8-policy-detail-v2-tasking-20260901.md` — 645 tasking (commit `51569d7`)
20. `docs/52-stage2-s210-lite-source-doc-drift-policy-20260826.md` — SHA drift policy (a)/(b)
21. `docs/33-stage2-s210-lite-lineage-sentinel-20260826.md` — §3.2 lineage sentinel 沿用
22. `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` — §6.2 OPEN 历史

**总计 22 个审验点**（18 个 645 新增 + 4 个既有参考）。

---

## §C. 关键判定点（Cursor 必须确认的 8 条）

### C.1 chain_id 区分 (8 distinct, 638-645 each unique)
| 刀 | chain_id | is_demo |
|---|---|---|
| 638 | `real_638_m4_1_people` | true |
| 639 | `demo_639` | true |
| 640 | `demo_640` | true |
| 641 | `real_641_heilongjiang` | false |
| 642 | `real_642_m4_5_renmian` | false |
| 643 | `real_643_m4_6_govreport` | false |
| 644 | `real_644_m4_7_policy_detail` | false |
| **645** | **`real_645_m4_8_policy_detail_v2`** | **false** |

**裁定**: 645 chain_id 末段 `_v2` 是为了与 644 `_policy_detail` 区分（沿用 644 模式但 v2 扩展）。8 个 chain_id 全部 distinct, 无碰撞。

### C.2 UUID prefix progression (demo → real → b → c → d 段)
- 639/640: `demo_xxx` prefix
- 641: `real` prefix
- 642/643: `b` 段 (b1eebc99 - b6eebc99)
- 644: `c` 段 (c1eebc99 - c2eebc99)
- **645**: **`d` 段 (d1eebc99 - d6eebc99)** ✓ 严格递增, 不撞 644 c 段

### C.3 645 vs 644 SHA drift event
- 644 hlj c107884 SHA = `bad8be51...`
- **645** hlj c107884 SHA = **`6237cd48...`** (drift per docs/52 (a)/(b) policy)
- 645 seed SQL 使用 645 实际抓取的 `6237cd48`, NOT 644 stale `bad8be51`
- drift 不影响 `lineage.is_demo='false'` 真实化判定
- 测试断言: `cell_shas` set 不含 `bad8be51` (允许 prose 提及), lineage SHA values 数组不含 `bad8be51`

### C.4 spike 边界 (32 INSERT total)
- 24 政策表 INSERT = 4 样本 × 6 政策表 (policy_document / policy_target / policy_measure / government_commitment / commitment_progress / project_event)
- 8 source INSERT = 4 source_registry + 4 source_document
- **总计 32 INSERT 行为 = 14 SQL INSERT 语句**（多行 VALUES 优化）
- 645 完整 spike 边界 ≤12 HTTP, 实际 http_count = 4 (远低于上限)

### C.5 4 处互链补登 append-only
- docs/45 §6.2 表末: +1 行 (M4.x + M5 spike 文档系列收口 per 645)
- docs/50 §4.4 第 48 项: 整段 add (M6 master 互链补登 per 645)
- docs/53 §5 第 48 项: 整段 add 含 7 子节 A-G
- docs/66 §6 末: 1 行尾注 (→ 645 docs/68)
- docs/67 §6 末: 1 行尾注 (→ 645 docs/69)
- **不修改既有 §5/§6 正文**, 仅 append 互链注释

### C.6 henan zwgk root 第 4 样本 NEW
- 644 留作扩展但未纳入 spike, 645 纳入作为第 4 样本
- SHA = `bd4c4c51...` (148507 bytes? 实际 158029 bytes — docs/69 §2 表)
- 4 样本顺序: heilongjiang / henan-zfgb / **henan-zwgk (NEW)** / yunnan
- yunnan SHA `f33eba53` 复用 644 (无 drift)

### C.7 lineage JSONB sentinel 沿用
- docs/33 §3.2 sentinel 沿用 5 刀: 641/642/643/644/**645**
- 645 seed SQL `lineage->>'is_demo' = 'false'` 真实化 sentinel
- 645 evidence JSON `red_lines_observed[2]` = "no silent SHA hardcoding (645 uses real-fetched SHA 6237cd48, not 644 stale bad8be51)"
- **不新写 016 migration**, 沿用 009+010+014+015 lineage JSONB 全表覆盖

### C.8 不宣称 PASS (14 milestones)
**645 完成**: M6 master + M4.8 v2 双交付

**不宣布**: Gate / O1 / O2 / O3 / M2 / M4 / M4.5 / M4.6 / M4.7 / M4.8 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS

沿用红线 (沿用 638-644 docs/58-67 末段)。架构师接受/驳回 646 推荐 scope, 不宣称任何 PASS。

---

## §D. Cursor 审验命令（可一键执行）

### D.1 测试 (22 用例, 期望全部 PASS)
```bash
cd "/Users/kjonekong/projects/china platform"
python3 -m pytest tests/test_m6_spike_docs_closure.py tests/test_m4_8_policy_detail_real_v2.py -v
```
**期望**: `============================== 22 passed in 0.87s ==============================`

### D.2 git 双推确认
```bash
git log --oneline -8
git status -s
```
**期望**: 5 个 645 相关 commits (`a235f94` / `73c74bc` / `0677111` / `dffdea5` / `6383da6`) 全部在线, 无 pending diff。

### D.3 关键字符串 spot-check (grep)
```bash
# 645 chain_id 是否 8 distinct
grep -c "real_645_m4_8_policy_detail_v2" docs/68-m6-spike-docs-closure-20260901.md
# 期望: ≥1

# 645 d 段 UUID 是否出现, 644 c 段是否不出现
grep -E "d[1-6]eebc99" scripts/seed_m4_8_policy_detail_real_v2.sql | head -5
grep -E "c[1-2]eebc99" scripts/seed_m4_8_policy_detail_real_v2.sql
# 期望: d 段 ≥6 行, c 段 0 行

# 645 hlj SHA drift 是否使用 6237cd48, NOT 644 stale bad8be51
grep -E "(6237cd48|bad8be51)" scripts/seed_m4_8_policy_detail_real_v2.sql | head -3
# 期望: 6237cd48 出现, bad8be51 在 lineage SHA values 数组中不出现 (允许 prose 注释)

# 4 互链 closure 是否全部 append
grep "per 645" docs/45-stage2-s210-lite-gate2-review-index-20260826.md
grep "per 645" docs/50-stage2-gate2-review-packet-draft-20260826.md
grep "per 645" docs/53-stage2-public-ingest-ops-handbook-20260826.md
grep -E "→ 645.*docs/68" docs/66-m5-waf-third-pass-20260901.md
grep -E "→ 645.*docs/69" docs/67-m4-7-policy-detail-real-20260901.md
# 期望: 5 行全部命中
```

### D.4 EXEC-QUEUE rev 75 一致性
```bash
grep -E "(rev: 75|status:.*645|645 DELIVERED)" reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md | head -10
```
**期望**: rev: 75; status 含 645 DELIVERED; §ACK 含 645 DELIVERED entry。

---

## §E. 645-A.6 状态变化

| 字段 | tasking OPEN 时 | DELIVERED 时 |
|------|----------------|--------------|
| §META ruling | "645 tasking OPEN" | (不变) |
| §CURRENT status | "645 tasking OPEN · 架构师自签 + 自交付" | "645 tasking DELIVERED · 645 fully DELIVERED" |
| §CURRENT cc_head | ends with `51569d7` | ends with `51569d7 + a235f94 + 73c74bc + 0677111` |
| §CURRENT last_delivery | `aac8225` (644 delivery) | `a235f94` (645 delivery) |
| §CURRENT last_receipt | `899bd41` (644 receipt) | `0677111` (645 receipt) |
| §CHAIN_TAIL 645 row | "**OPEN**" | "**DELIVERED**" |
| §ACK | (无 645 DELIVERED entry) | +1 行 645 DELIVERED entry |

---

## §F. 红线遵守 (12/12) — Cursor 必审

- ✓ 不宣布 Gate / O1 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS
- ✓ 不补零 / 不静默硬编码 value
- ✓ 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED
- ✓ 不改 docs/45/50/53/66/67 §5/§6 正文 (仅 append 互链注释)
- ✓ 不碰 4 fixture 锁值 (nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c)
- ✓ 数据源治理铁律 2026-08-29: 数据源唯一=政府/统计局/研究机构自取; 用户零裁定; 执行端不可提任何用户裁定事项
- ✓ 不删既有 OPEN 行 (645 §CHAIN_TAIL OPEN row appended → DELIVERED)
- ✓ 完成 = observation SUCCESS (no PARTIAL)
- ✓ 645 使用 645 实际抓取的 SHA 6237cd48, NOT 644 stale bad8be51 (drift event handled per docs/52 (a)/(b))
- ✓ henan zwgk root 第 4 样本 (NEW 645, NOT in 644 chain_id)
- ✓ chain_id 区分: 645 `real_645_m4_8_policy_detail_v2` ≠ 644 `real_644_m4_7_policy_detail`
- ✓ UUID d 段 (d1-d6) ≠ 644 c 段 (c1-c2)

---

## §G. 646 下一步 (架构师推荐 scope A)

**scope A (推荐)**:
- M6 收口收口收口 + M4.9 试点省扩展
- docs/52 B 路 live-candidate 探测 (O1 主路径)
- 沿用 644 模式 + 加 fujian / guangdong 第 5/6 样本
- chain_id = `real_646_m4_9_policy_detail_v3` (末段 `_v3` 与 645 `_v2` 区分)

候选 scope (per 645 docs/68 §6 + docs/67 §5 沿用):
- A (推荐): M6 收口 + M4.9 政策详情 v3 扩展
- B: Gate 1 启动 (M2 Gate 后才合法, 当前阻塞)
- C: O3 OCR 真实化 (沿用 583 O3 spike; 2026-08 已完成)
- D: docs/45/50 spike 文档清空收口 (沿用 M6 收口模式)
- E: M4.9 试点省扩展 (沿用 644 模式 + 加 fujian / guangdong 第 5/6 样本)

---

## §H. 提交给 Cursor 的最终问题

请 Cursor 审验后回答以下 4 个问题:

1. **是否认可** 645 5 commits + 双推完整链路 (`a235f94` / `73c74bc` / `0677111` / `dffdea5` / `6383da6`)?
2. **是否认可** 645 chain_id 区分 (`real_645_m4_8_policy_detail_v2` ≠ 644 `real_644_m4_7_policy_detail`) + UUID d 段 ≠ 644 c 段?
3. **是否认可** hlj SHA drift 处理 (645 `6237cd48` 替代 644 stale `bad8be51`, drift 不影响 `is_demo='false'` 真实化判定)?
4. **是否认可** 646 推荐 scope A (M6 收口 + M4.9 v3 扩展), 或推荐其他 scope (B/C/D/E)?

---

## §I. handoff 元数据

- **handoff 文件**: 本文件即汇总 (`reviews/stage0-gate0-rework-2026-08-23/645-stage0-cursor-handoff-summary-20260901.md`)
- **审验入口**: `tests/test_m6_spike_docs_closure.py` + `tests/test_m4_8_policy_detail_real_v2.py` (22 用例)
- **回执**: `reviews/stage0-gate0-rework-2026-08-23/645-stage0-cc-m6-m4-8-parallel-receipt-20260901.md`
- **EXEC-QUEUE**: `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` rev 75
- **架构师**: 自签 + 自交付 (豁免 per 2026-08-31 21:50)
- **审验端**: Cursor (人工/AI audit)
- **不宣称 PASS**: Gate / O1 / O2 / O3 / M2 / M4 / M4.5 / M4.6 / M4.7 / M4.8 / M5 / M5.1 / M5.2 / M5.3 / M6 (沿用红线)

— End 645 cursor handoff summary —
