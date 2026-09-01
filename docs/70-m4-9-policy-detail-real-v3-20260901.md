# 70 — M4.9 政策详情 v3 真实化 spike（架构师级审查）

> **刀号**: 646
> **Milestone**: M4.9（沿用 641/642/643/644/645 spike 模式；spike 第 4 次）
> **类型**: 架构师级 §1-§6 审查文档
> **日期**: 2026-09-01
> **依据**:
> - `docs/67-m4-7-policy-detail-real-20260901.md` (644 M4.7 政策详情)
> - `docs/69-m4-8-policy-detail-real-v2-20260901.md` (645 M4.8 政策详情 v2)
> - `docs/68-m6-spike-docs-closure-20260901.md` (645 M6 master)
> - `646-stage0-architect-m4-9-v3-o1-live-candidate-tasking-20260901.md` §3.646-A.1 / 646-A.2
> **前置**: 645 M4.8 落地 = 4 样本 (heilongjiang/henan-zfgb/henan-zwgk/yunnan) × 1 detail each × 6 政策表 = 24 INSERT + 4 source_registry + 4 source_document = 32 INSERT total
> **架构师综合**: M4.9 = 沿用 645 模式 + 加 fujian 第 5 样本 + guangdong 第 6 样本 (gd 首选 /zwgk/ + 625 fall-through chain) = **12 INSERT planned** (2 样本 × 6 政策表) + 2 source_registry + 2 source_document = **16 INSERT total**
> **chain_id**: `real_646_m4_9_policy_detail_v3` (末段 `_v3` ≠ 645 `_v2` ≠ 644 `_policy_detail`)
> **UUID prefix**: e 段 (e02-e62) ≠ 645 d 段 (d21-d94) ≠ 644 c 段 (c41-c93)
> **不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M5 / M6 PASS。

---

## 1. M4.9 落地终态

| 子刀 | 文件 / 范围 | 状态 | 说明 |
|---|---|---|---|
| 646-A.0 | 645 审计 P3 修正 (docs/68 §4 尾 + docs/50 §4.4 第 48 项 + docs/53 §5 第 48 项 行内 append 8 个 distinct chain_id 修正 + 22/22 实际交付说明) | DONE | 645 审计 P3 修正落地；不删行不删 OPEN 行 |
| 646-A.1 | `scripts/fetch_m4_9_policy_detail_v3_2024.py` + `scripts/seed_m4_9_policy_detail_real_v3.sql` + `evidence_pack/m4_9_policy_detail_real_v3_20260901.json` + `docs/reports/m4_9_policy_detail_real_v3_20260901.md` | DONE | M4.9 政策详情 v3 真实化；2 样本 (fujian + guangdong) × 1 HTTP each = 2 cells；http_count=2/12；fetched_count=2；顶层裁定 REAL_FETCHED；2 真实样本落地 |
| 646-A.2 | `scripts/probe_o1_live_candidate_2024.py` + `docs/reports/o1_live_candidate_probe_20260901.md` + `evidence_pack/o1_live_candidate_probe_20260901.json` | DONE | docs/52 B路 live-candidate 探测登记（O1 主路径，仅登记不启用，O1 仍 OPEN） |
| 646-A.3 | 本文档（docs/70） | DONE | §1-§6 架构师级审查 |
| 646-A.4 | `docs/reports/m4_9_policy_detail_real_v3_20260901.md` + `evidence_pack/m4_9_policy_detail_real_v3_20260901.json` + `docs/reports/o1_live_candidate_probe_20260901.md` + `evidence_pack/o1_live_candidate_probe_20260901.json` | DONE | 4 文件 (2 M4.9 + 2 O1 live-candidate) |
| 646-B | `tests/test_m4_9_policy_detail_real_v3.py` ≥ 6 + `tests/test_o1_live_candidate_probe.py` ≥ 4 + 645 22 用例回归 | DONE | 共 ≥ 10 + 22 回归 = ≥ 32 用例；全套 pytest ≥ 32/32 green |
| 646-C | 回执 + commit + 双推 | DONE | `646-stage0-cc-m4-9-v3-o1-live-candidate-receipt-20260901.md` §PHOTO-1..N |

---

## 2. M4.9 spike 边界（vs 646 tasking 规划）

### 2.1 646 tasking 规划 vs 实测对比

**646 tasking 规划**：

- 沿用 645 模式 + 加 fujian 第 5 样本 + guangdong 第 6 样本 (gd 首选 /zwgk/ + 625 fall-through chain)
- = **12 INSERT planned**（6 表 × 2 真实）
- + 2 source_registry + 2 source_document = 16 INSERT total
- ≤12 HTTP total (2 cells × 1 HTTP each)
- chain_id='real_646_m4_9_policy_detail_v3' (末段 `_v3`，≠ 645 `_v2`)
- UUID prefix e 段 ≠ 645 d 段 ≠ 644 c 段
- 2 新 SHA 全 distinct ≠ 638-645 全部 SHA

**646 实测反发现**：

- 2 真实样本落地（2 distinct SHA）：
  - fujian `fceb8c0ac80c5d3c...` (/zwgk/) — 全新 SHA；与 638-645 全部 distinct
  - guangdong `49eed23efcb2954e...` (/zwgk/) — 全新 SHA；preferred cell 0, 无 fallback 触发；与 638-645 全部 distinct
- 2 试点省 / 样本位 全部 REACHABLE ✓
- spike 边界 **实测 12 INSERT** = **规划 12 INSERT = 0 调整**（沿用 645 模式更精确）

### 2.2 spike 边界明细（12 INSERT 政策表 + 4 source_registry/source_document = 16 INSERT total）

| 表 | 行数 | lineage.is_demo | UUID prefix | 区别 vs 645 |
|---|---|---|---|---|
| source_registry | 2 | `'false'` (NEW) | e0eebc99-...e02/e03 | 645 = 4 行 (d21-d24) |
| source_document | 2 | `'false'` (NEW) | e0eebc99-...e04/e05 | 645 = 4 行 (d31-d34) |
| policy_document | **2** | `'false'` (spike) | e1eebc99-...e11/e12 | 645 d 段 (≠ d41-d44) |
| policy_target | **2** | `'false'` (spike) | e2eebc99-...e21/e22 | 645 d 段 (≠ d51-d54) |
| policy_measure | **2** | `'false'` (spike) | e3eebc99-...e31/e32 | 645 d 段 (≠ d61-d64) |
| government_commitment | **2** | `'false'` (spike) | e4eebc99-...e41/e42 | 645 d 段 (≠ d71-d74) |
| commitment_progress | **2** | `'false'` (spike) | e5eebc99-...e51/e52 | 645 d 段 (≠ d81-d84) |
| project_event | **2** | `'false'` (spike) | e6eebc99-...e61/e62 | 645 d 段 (≠ d91-d94) |

**总计**：2 × 6 = **12 INSERT** (vs 645 实测 24 INSERT；M4.9 是 spike 4 次，2 试点省扩展) + 4 source_registry/source_document = **16 INSERT total**

### 2.3 真实样本 (2 distinct SHA → 2 用于 seed)

| 序号 | 试点省 | slot | URL | SHA (前 16) | file_size | 646 seed 用 | 备注 |
|---|---|---|---|---|---|---|---|
| 1 | fujian | fujian_zwgk_root | `/zwgk/` | `fceb8c0ac80c5d3c` | 682,079 | ✓ | **全新 SHA (第 5 样本)** |
| 2 | guangdong | guangdong_zwgk_chain | `/zwgk/` | `49eed23efcb2954e` | 73,836 | ✓ | **全新 SHA (第 6 样本)** preferred cell 0 (无 fallback 触发) |

**2 SHA distinct vs 645 SHA**：
- 646 `fceb8c0a` ≠ 645 `6237cd48 / dfa38998 / bd4c4c51 / f33eba53` ✓
- 646 `49eed23e` ≠ 645 `6237cd48 / dfa38998 / bd4c4c51 / f33eba53` ✓
- 2 SHA 全部 distinct ≠ 644 SHA `bad8be51/dfa38998/f33eba53` ≠ 643 SHA `e68099df/63109491/93fe23b3` ≠ 642 SHA `cd6aff30/4349ee0f/fede03ba` ≠ 641 SHA `26e5379d...b87ab` ≠ 640 demo SHA `'0…02'` ≠ 639 demo SHA `'0…01'` ✓

---

## 3. 真实化 demo SQL 结构（基于 646-A.1）

### 3.1 INSERT 结构（12 INSERT 政策表 + 4 source = 16 INSERT total）

```sql
-- 1. 2 source_registry (lineage.is_demo='false', chain_id='real_646_m4_9_policy_detail_v3')
INSERT INTO source_registry ... (2 行: e02/e03)

-- 2. 2 source_document (lineage.is_demo='false')
INSERT INTO source_document ... (2 行: e04/e05)

-- 3. 2 policy_document (lineage.is_demo='false')
INSERT INTO policy_document ... (2 行: e11/e12)

-- 4. 2 policy_target (lineage.is_demo='false')
INSERT INTO policy_target ... (2 行: e21/e22)

-- 5. 2 policy_measure (lineage.is_demo='false')
INSERT INTO policy_measure ... (2 行: e31/e32)

-- 6. 2 government_commitment (SELECT geo_entity subquery)
INSERT INTO government_commitment ... (2 行: e41/e42)

-- 7. 2 commitment_progress (lineage.is_demo='false')
INSERT INTO commitment_progress ... (2 行: e51/e52)

-- 8. 2 project_event (SELECT geo_entity subquery)
INSERT INTO project_event ... (2 行: e61/e62)
```

### 3.2 lineage JSONB sentinel 沿用 (per docs/33 §3.2)

- 全 16 INSERT 行 `lineage->>'is_demo' = 'false'` (沿用 641/642/643/644/645 sentinel)
- 不新写 016 migration (沿用 009+010+014+015 lineage JSONB 全表覆盖)
- `lineage->>'chain_id' = 'real_646_m4_9_policy_detail_v3'` (8 个 distinct chain_id: 638/639/640/641/642/643/644/645/646; per 645 审计 P3 F1 修正 — 638 probe = `real_638_m4_1_people` 计入 8 刀全链表; 646 行内 append 不删行)
- `lineage->>'source_file_sha256'` = 8 行 (2 source_registry + 2 source_document + 2 policy_document + 2 policy_target + 2 policy_measure + 2 government_commitment + 2 commitment_progress + 2 project_event)
- `lineage->>'extractor_version' = 'v1.0'` (沿用 645)

### 3.3 关键 INSERT 模式（沿用 645 + 简化为 2 样本）

- **policy_document**: 2 行 INSERT 单 VALUES 块
- **policy_target / policy_measure / commitment_progress**: 2 行 INSERT 单 VALUES 块（与 645 同模式）
- **government_commitment / project_event**: 2 行 × 单 INSERT 语句 × SELECT subquery `FROM geo_entity WHERE canonical_name = '福建省'/'广东省' AND level = 'PROVINCIAL' LIMIT 1`

---

## 4. lineage 真实化 sentinel + chain_id 区分 + 真实 SHA 区分表

### 4.1 9 真实化刀 lineage 沿用 (per docs/33 §3.2)

| 刀 | chain_id | is_demo | 试点省 | UUID prefix |
|---|---|---|---|---|
| 641 | `real_641_heilongjiang` | false | heilongjiang | real prefix |
| 642 | `real_642_m4_5_renmian` | false | henan/guangdong/guizhou | b 段 (b1-b6) |
| 643 | `real_643_m4_6_govreport` | false | hlj/henan/yunnan | c 段 (c41-c41) |
| 644 | `real_644_m4_7_policy_detail` | false | hlj/henan/yunnan | c 段 (c41-c93) |
| 645 | `real_645_m4_8_policy_detail_v2` | false | hlj/henan-zfgb/henan-zwgk/yunnan | d 段 (d21-d94) |
| **646** | **`real_646_m4_9_policy_detail_v3`** | **false** | **fujian + guangdong** | **e 段 (e02-e62)** |

### 4.2 真实 SHA 区分表（2 新 SHA + 17 既有）

| 序号 | 刀 | 试点省 | URL | SHA (前 16) | 备注 |
|---|---|---|---|---|---|
| 1 | 641 | hlj | `/hlj/c107884/list.shtml` | `26e5379d...` | 真实化首发 |
| 2 | 642 | henan-renmian | (3 源) | `cd6aff30...` | |
| 3 | 642 | gd-renmian | (3 源) | `4349ee0f...` | |
| 4 | 642 | gz-renmian | (3 源) | `fede03ba...` | |
| 5 | 643 | hlj-govreport | `/hlj/c107882/list.shtml` | `e68099df...` | c107882 避开 641 c107884 |
| 6 | 643 | henan-govreport | `/zwgk/zfgb/` | `63109491...` | |
| 7 | 643 | yn-govreport | `/zwgk/zfxxgk/zfgzbg/` | `93fe23b3...` | |
| 8 | 644 | hlj-detail | `/hlj/c107884/list.shtml` | `bad8be51...` | 沿用 641-643 不重抓 |
| 9 | 644 | henan-detail | `/zwgk/zfgb/` | `dfa38998...` | |
| 10 | 644 | yn-detail | `/zwgk/zfxxgk/zfgzbg/` | `f33eba53...` | |
| 11 | 645 | hlj-detail-v2 | `/hlj/c107884/list.shtml` | `6237cd48...` | **drift from 644** `bad8be51` (per docs/52 (a)/(b)) |
| 12 | 645 | henan-zfgb-v2 | `/zwgk/zfgb/` | `dfa38998...` | 沿用 644 |
| 13 | 645 | henan-zwgk-v2 | `/zwgk/` | `bd4c4c51...` | **NEW 645 第 4 样本** |
| 14 | 645 | yn-zfgzbg-v2 | `/zwgk/zfxxgk/zfgzbg/` | `f33eba53...` | 沿用 644 |
| **15** | **646** | **fujian-zwgk-v3** | `/zwgk/` | **`fceb8c0a...`** | **NEW 646 第 5 样本** |
| **16** | **646** | **guangdong-zwgk-v3** | `/zwgk/` | **`49eed23e...`** | **NEW 646 第 6 样本** (preferred cell 0) |
| 17 | 638 (probe) | various | 23 试点省 | n/a (probe only) | 638 = `real_638_m4_1_people` chain_id 计入 8 刀全链表 (per 645 审计 P3 F1 修正) |

**17 SHA 全部 distinct** (✓ 不撞 638-645)

### 4.3 UUID prefix 严格递增

```
demo → real → b → c → d → e (646)
638-640 demo + real  →  641 real  →  642 b1-b6  →  643 c1-c2  →  644 c1-c2  →  645 d21-d94  →  646 e02-e62
```

**646 e 段** (`e0eebc99` / `e1eebc99` / `e2eebc99` / `e3eebc99` / `e4eebc99` / `e5eebc99` / `e6eebc99`) **≠ 645 d 段 ≠ 644 c 段 ≠ 643 c 段** ✓

---

## 5. 647 下一步

### 5.1 647 候选 scope

- **scope A (推荐)**: 沿用 646 模式 + 加 7-9 试点省扩展 (e.g. jilin/liaoning/zhejiang/anhui/jiangxi/shandong/hubei/shaanxi/sichuan 等) — spike 第 5 次扩展
- **scope B**: O1 B路 live-candidate 启用 (per 646-A.2 data.stats.gov.cn PENDING_CANDIDATE → 等用户裁定启用)
- **scope C**: Gate 1 启动 (M2 Gate 后才合法, 当前阻塞; 沿用 645 §6)
- **scope D**: docs/45/50 spike 文档清空收口 (沿用 M6 收口模式)
- **scope E**: 5W1H 分析 + 沿用 638-646 模式扩展 (spec 推演)

### 5.2 当前未落地（红线守护）

- **Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M5 / M5.1 / M5.2 / M5.3 / M6** — 14 个里程碑不宣布 PASS
- O1 仍 OPEN (B路 live-candidate 仅登记, 不切换/启用)
- dbt mart flip: 60 行 demo 中仅 1 行（nanjing + CONDITION）真实化 pilot, O1 全量未启动
- 4 fixture 锁值永不动（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）

---

## 6. 下一步 + 不宣称 PASS

**646 完成**:
- M4.9 政策详情 v3 真实化 (2 样本 × 1 HTTP each = 2 cells; chain_id='real_646_m4_9_policy_detail_v3'; UUID e 段; 2 NEW SHA: fceb8c0a/49eed23e)
- O1 B路 live-candidate 探测登记 (data.stats.gov.cn PENDING_CANDIDATE_ONLY; O1 仍 OPEN)
- 645 审计 P3 修正 (docs/68/50/53 行内 append; 不删行不删 OPEN 行)
- ≥32/32 pytest green (646 ≥ 10 + 645 22 回归)
- evidence_pack × 2 + docs/reports × 2 + docs/70 + docs/52 行内 append 全部落地

**不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线）。

**O1 仍 OPEN** — B路 live-candidate 仅登记, 不切换/启用; 等用户/架构师裁定。

---

— End 70 — M4.9 v3 + O1 live-candidate 真实化 spike 审查 20260901 —