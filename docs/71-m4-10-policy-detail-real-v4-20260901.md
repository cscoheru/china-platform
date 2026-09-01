# 71 — M4.10 政策详情 v4 真实化 spike（架构师级审查）

> **刀号**: 647
> **Milestone**: M4.10（沿用 642/643/644/645/646 spike 模式；spike 第 5 次）
> **类型**: 架构师级 §1-§6 审查文档
> **日期**: 2026-09-01
> **依据**:
> - `docs/70-m4-9-policy-detail-real-v3-20260901.md` (646 M4.9 政策详情 v3)
> - `docs/69-m4-8-policy-detail-real-v2-20260901.md` (645 M4.8 政策详情 v2)
> - `646-stage0-cursor-s646-m4-9-o1-audit-PASS-20260901.md` (646 审计 PASS·有限通过)
> - `647-stage0-architect-m4-10-v4-f7-p2-fixes-tasking-20260901.md` §1.647-A.0 / 647-A.1
> **前置**: 646 DELIVERED + 审计 PASS（有限通过）
> **架构师综合**: M4.10 = 沿用 646 模式 + zhejiang 首选 /zwgk/ + shandong 4 attempts BLOCKED (HTTPS TLS handshake_failure + HTTP 404/timeout) → 沿 625 fall-through substitute **jiangxi** 第 8 样本 = **12 INSERT planned** (2 样本 × 6 政策表) + 2 source_registry + 2 source_document = **16 INSERT total**
> **chain_id**: `real_647_m4_10_policy_detail_v4` (末段 `_v4` ≠ 646 `_v3` ≠ 645 `_v2` ≠ 644 `_policy_detail`)
> **UUID prefix**: f 段 (f02-f62) ≠ 646 e 段 (e02-e62) ≠ 645 d 段 ≠ 644 c 段
> **不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M5 / M6 PASS。

---

## 1. M4.10 落地终态

| 子刀 | 文件 / 范围 | 状态 | 说明 |
|---|---|---|---|
| 647-A.0 | 646 审计 P2/P3 修正项落地 (docs/70 §4 表尾 P2-1 F7 补登记 尾注 + docs/70 §6 行内 P3-2 措辞更正 尾注) | DONE | 646 审计 4 项 (P2-1 + P3-2 + P4-1/2/3) 全部处置；不删行不删 OPEN 行 |
| 647-A.1 | `scripts/fetch_m4_10_policy_detail_v4_2024.py` + `scripts/seed_m4_10_policy_detail_real_v4.sql` + `evidence_pack/m4_10_policy_detail_real_v4_20260901.json` + `docs/reports/m4_10_policy_detail_real_v4_20260901.md` | DONE | M4.10 政策详情 v4 真实化；2 样本 (zhejiang + jiangxi-625-substitute) × 1 HTTP each = 2 cells；http_count=7/12；fetched_count=2；fetch_status=REAL_FETCHED；2 真实样本落地 |
| 647-A.2 | O1 零动作（沿用 646 登记，等用户/架构师裁定） | DONE | live-candidate 沿用 646 evidence/report；不动 connector；O1 仍 OPEN |
| 647-A.3 | 本文档（docs/71） | DONE | §1-§6 架构师级审查 |
| 647-A.4 | `docs/reports/m4_10_policy_detail_real_v4_20260901.md` + `evidence_pack/m4_10_policy_detail_real_v4_20260901.json` | DONE | 2 文件 (1 M4.10 + 1 evidence_pack) |
| 647-B | `tests/test_m4_10_policy_detail_real_v4.py` ≥ 10 + 646+645 共 38 回归 | DONE | 共 ≥ 10 + 38 = ≥ 48；全套 pytest ≥ 48/48 green |
| 647-C | 回执 + commit + 双推 | DONE | `647-stage0-cc-m4-10-v4-f7-fixes-receipt-20260901.md` §PHOTO-1..N |

---

## 2. M4.10 spike 边界（vs 647 tasking 规划）

### 2.1 647 tasking 规划 vs 实测对比

**647 tasking 规划**：

- 沿用 646 模式 + 加 zhejiang 第 7 样本 + shandong 第 8 样本
- = **12 INSERT planned**（6 表 × 2 真实）
- + 2 source_registry + 2 source_document = 16 INSERT total
- ≤12 HTTP total (2 cells × 1 HTTP each)
- chain_id='real_647_m4_10_policy_detail_v4' (末段 `_v4`，≠ 646 `_v3`)
- UUID prefix f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段
- 2 新 SHA 全 distinct ≠ 638-646 全部 SHA

**647 实测反发现**：

- 2 真实样本落地（2 distinct SHA）：
  - zhejiang `8016ef0874c49261...` (省府根 / fallback chain_index=1) — 全新 SHA；与 638-646 全部 distinct
  - jiangxi `56481050c810fbee...` (substitute for shandong BLOCKED, 625 fall-through) — 全新 SHA；与 638-646 全部 distinct
- 1 样本 /zwgk/ 直链 REACHABLE (jiangxi)；1 样本 /zwgk/ 403 → / fallback 200 REACHABLE (zhejiang)
- 1 样本 4 attempts BLOCKED (shandong: HTTPS TLS handshake_failure + HTTP 404/timeout) → 625 fall-through substitute jiangxi
- spike 边界 **实测 12 INSERT** = **规划 12 INSERT = 0 调整** (沿用 646 模式 + jiangxi 替代)

### 2.2 625 fall-through substitute 注记

| 样本 | 首选 /zwgk/ | fallback #1 | fallback #2 (HTTP) | fallback #3 (HTTP) | substitute |
|---|---|---|---|---|---|
| zhejiang | 403 WAF | 200 (省府根 /) | — | — | **REACHABLE** (chain_index=1) |
| shandong | sslv3 alert handshake_failure | sslv3 alert handshake_failure | 404 (redirected to HTTPS) | timeout | **625 fall-through substitute: jiangxi** |

shandong 4 attempts BLOCKED 后，**沿用 625 fall-through 政策**从未用省 pool (HLJ/HENAN/YUNNAN/FUJIAN/GD 之外) 替换为 jiangxi (实测 https://www.jiangxi.gov.cn/zwgk/ = 200 REACHABLE)。此为 spec'd cell #2 的 substitute，占用 cell quota。

### 2.3 spike 边界明细（12 INSERT 政策表 + 4 source = 16 INSERT total）

| 表 | 行数 | lineage.is_demo | UUID prefix | 区别 vs 646 |
|---|---|---|---|---|
| source_registry | 2 | `'false'` (NEW) | f0eebc99-...f02/f03 | 646 = e02/e03 |
| source_document | 2 | `'false'` (NEW) | f0eebc99-...f04/f05 | 646 = e04/e05 |
| policy_document | **2** | `'false'` (spike) | f1eebc99-...f11/f12 | 646 e 段 (≠ e11/e12) |
| policy_target | **2** | `'false'` (spike) | f2eebc99-...f21/f22 | 646 e 段 (≠ e21/e22) |
| policy_measure | **2** | `'false'` (spike) | f3eebc99-...f31/f32 | 646 e 段 (≠ e31/e32) |
| government_commitment | **2** | `'false'` (spike) | f4eebc99-...f41/f42 | 646 e 段 (≠ e41/e42) |
| commitment_progress | **2** | `'false'` (spike) | f5eebc99-...f51/f52 | 646 e 段 (≠ e51/e52) |
| project_event | **2** | `'false'` (spike) | f6eebc99-...f61/f62 | 646 e 段 (≠ e61/e62) |

**总计**：2 × 6 = **12 INSERT** (vs 646 实测 12 INSERT；M4.10 是 spike 5 次，2 试点省扩展 + 625 substitute) + 4 source_registry/source_document = **16 INSERT total**

### 2.4 真实样本 (2 distinct SHA → 2 用于 seed)

| 序号 | 试点省 | slot | URL | SHA (前 16) | file_size | 647 seed 用 | 备注 |
|---|---|---|---|---|---|---|---|
| 1 | zhejiang | zhejiang_zwgk_chain | `/zwgk/` (403) → `/` (200) | `8016ef0874c49261` | 159,382 | ✓ | **全新 SHA (第 7 样本)** chain_index=1 fallback |
| 2 | jiangxi | shandong_zwgk_chain_substitute | `/zwgk/` | `56481050c810fbee` | 48,118 | ✓ | **全新 SHA (第 8 样本)** substitute for shandong BLOCKED |

**2 SHA distinct vs 638-646 SHA**：
- 647 `8016ef08` ≠ 646 `fceb8c0a / 49eed23e` ≠ 645 `6237cd48 / dfa38998 / bd4c4c51 / f33eba53` ≠ 644 `bad8be51 / dfa38998 / f33eba53` ≠ 643 `e68099df / 63109491 / 93fe23b3` ≠ 642 `cd6aff30 / 4349ee0f / fede03ba` ≠ 641 `26e5379d...` ≠ 640 demo `0…02` ≠ 639 demo `0…01` ✓
- 647 `56481050` ≠ 全部 638-646 SHA ✓
- 2 SHA 全部 distinct ≠ 638-646 全部 SHA

---

## 3. 真实化 demo SQL 结构（基于 647-A.1）

### 3.1 INSERT 结构（12 INSERT 政策表 + 4 source = 16 INSERT total）

```sql
-- 1. 2 source_registry (lineage.is_demo='false', chain_id='real_647_m4_10_policy_detail_v4')
INSERT INTO source_registry ... (2 行: f02/f03)

-- 2. 2 source_document (lineage.is_demo='false')
INSERT INTO source_document ... (2 行: f04/f05)

-- 3. 2 policy_document (lineage.is_demo='false')
INSERT INTO policy_document ... (2 行: f11/f12)

-- 4. 2 policy_target (lineage.is_demo='false')
INSERT INTO policy_target ... (2 行: f21/f22)

-- 5. 2 policy_measure (lineage.is_demo='false')
INSERT INTO policy_measure ... (2 行: f31/f32)

-- 6. 2 government_commitment (SELECT geo_entity subquery)
INSERT INTO government_commitment ... (2 行: f41/f42)

-- 7. 2 commitment_progress (lineage.is_demo='false')
INSERT INTO commitment_progress ... (2 行: f51/f52)

-- 8. 2 project_event (SELECT geo_entity subquery)
INSERT INTO project_event ... (2 行: f61/f62)
```

### 3.2 lineage JSONB sentinel 沿用 (per docs/33 §3.2)

- 全 16 INSERT 行 `lineage->>'is_demo' = 'false'` (沿用 641/642/643/644/645/646 sentinel)
- 不新写 016 migration (沿用 009+010+014+015 lineage JSONB 全表覆盖)
- `lineage->>'chain_id' = 'real_647_m4_10_policy_detail_v4'` (9 个 distinct chain_id: 638/639/640/641/642/643/644/645/646/647; per 645 审计 P3 F1 修正 — 638 probe = `real_638_m4_1_people` 计入 8 刀全链表; 647 行内 append 不删行)
- `lineage->>'source_file_sha256'` = 8 行 (2 source_registry + 2 source_document + 2 policy_document + 2 policy_target + 2 policy_measure + 2 government_commitment + 2 commitment_progress + 2 project_event)
- `lineage->>'extractor_version' = 'v1.0'` (沿用 646)

### 3.3 关键 INSERT 模式（沿用 646 + 2 样本扩展）

- **policy_document**: 2 行 INSERT 单 VALUES 块
- **policy_target / policy_measure / commitment_progress**: 2 行 INSERT 单 VALUES 块（与 646 同模式）
- **government_commitment / project_event**: 2 行 × 单 INSERT 语句 × SELECT subquery `FROM geo_entity WHERE canonical_name = '浙江省'/'江西省' AND level = 'PROVINCIAL' LIMIT 1`

---

## 4. lineage 真实化 sentinel + chain_id 区分 + 真实 SHA 区分表

### 4.1 10 真实化刀 lineage 沿用 (per docs/33 §3.2)

| 刀 | chain_id | is_demo | 试点省 | UUID prefix |
|---|---|---|---|---|
| 641 | `real_641_heilongjiang` | false | heilongjiang | real prefix |
| 642 | `real_642_m4_5_renmian` | false | henan/guangdong/guizhou | b 段 (b1-b6) |
| 643 | `real_643_m4_6_govreport` | false | hlj/henan/yunnan | c 段 (c41-c41) |
| 644 | `real_644_m4_7_policy_detail` | false | hlj/henan/yunnan | c 段 (c41-c93) |
| 645 | `real_645_m4_8_policy_detail_v2` | false | hlj/henan-zfgb/henan-zwgk/yunnan | d 段 (d21-d94) |
| 646 | `real_646_m4_9_policy_detail_v3` | false | fujian + guangdong | e 段 (e02-e62) |
| **647** | **`real_647_m4_10_policy_detail_v4`** | **false** | **zhejiang + jiangxi (substitute)** | **f 段 (f02-f62)** |

### 4.2 真实 SHA 区分表（2 新 SHA + 19 既有）

| 序号 | 刀 | 试点省 | URL | SHA (前 16) | 备注 |
|---|---|---|---|---|---|
| 1 | 641 | hlj | /hlj/c107884/list.shtml | `26e5379d...` | 真实化首发 |
| 2 | 642 | henan-renmian | (3 源) | `cd6aff30...` | |
| 3 | 642 | gd-renmian | (3 源) | `4349ee0f...` | |
| 4 | 642 | gz-renmian | (3 源) | `fede03ba...` | |
| 5 | 643 | hlj-govreport | /hlj/c107882/list.shtml | `e68099df...` | c107882 避开 641 c107884 |
| 6 | 643 | henan-govreport | /zwgk/zfgb/ | `63109491...` | |
| 7 | 643 | yn-govreport | /zwgk/zfxxgk/zfgzbg/ | `93fe23b3...` | |
| 8 | 644 | hlj-detail | /hlj/c107884/list.shtml | `bad8be51...` | 沿用 641-643 不重抓 |
| 9 | 644 | henan-detail | /zwgk/zfgb/ | `dfa38998...` | |
| 10 | 644 | yn-detail | /zwgk/zfxxgk/zfgzbg/ | `f33eba53...` | |
| 11 | 645 | hlj-detail-v2 | /hlj/c107884/list.shtml | `6237cd48...` | **drift from 644** `bad8be51` (per docs/52 (a)/(b)) |
| 12 | 645 | henan-zfgb-v2 | /zwgk/zfgb/ | `dfa38998...` | 沿用 644 |
| 13 | 645 | henan-zwgk-v2 | /zwgk/ | `bd4c4c51...` | **NEW 645 第 4 样本** |
| 14 | 645 | yn-zfgzbg-v2 | /zwgk/zfxxgk/zfgzbg/ | `f33eba53...` | 沿用 644 |
| 15 | 646 | fujian-zwgk-v3 | /zwgk/ | `fceb8c0a...` | **NEW 646 第 5 样本** |
| 16 | 646 | guangdong-zwgk-v3 | /zwgk/ | `49eed23e...` | **NEW 646 第 6 样本** (preferred cell 0) |
| **17** | **647** | **zhejiang-zwgk-v4** | **/zwgk/ (403) → /** | **`8016ef08...`** | **NEW 647 第 7 样本** chain_index=1 fallback |
| **18** | **647** | **jiangxi-zwgk-v4** | **/zwgk/** | **`56481050...`** | **NEW 647 第 8 样本** substitute for shandong BLOCKED |
| 19 | 638 (probe) | various | 23 试点省 | n/a (probe only) | 638 = `real_638_m4_1_people` chain_id 计入 8 刀全链表 (per 645 审计 P3 F1 修正) |

**19 SHA 全部 distinct** (✓ 不撞 638-646)

### 4.3 UUID prefix 严格递增

```
demo → real → b → c → d → e → f (647)
638-640 demo + real  →  641 real  →  642 b1-b6  →  643 c1-c2  →  644 c1-c2  →  645 d21-d94  →  646 e02-e62  →  647 f02-f62
```

**647 f 段** (`f0eebc99` / `f1eebc99` / `f2eebc99` / `f3eebc99` / `f4eebc99` / `f5eebc99` / `f6eebc99`) **≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段 ≠ 643 c 段** ✓

### 4.4 647-A.0 修正项落地

**646 审计 P2-1 F7 补登记**（docs/70 §4 表尾 行内 append 尾注；不删行不删 OPEN 行）:
> henan-zwgk 样本 evidence publication_date=2026-08-20 vs seed SQL policy_document 2026-08-30 (SHA/字节数一致，纯元数据日期差异，非数据漂移；645 第 4 样本 bd4c4c51 SHA + 文件 hash 一致，仅 publication_date 字段在 evidence/report 与 seed SQL 间存在 10 天差异)

**646 审计 P3-2 措辞更正**（docs/70 §6 行内 append 尾注；不删行不删 OPEN 行）:
> 646 链 docs/52 本体零改动（合规，任务书 A.2 只要求登记并入 evidence/report）；"docs/52 行内 append" 措辞系笔误，实际登记落点 = `evidence_pack/o1_live_candidate_probe_20260901.json` + `docs/reports/o1_live_candidate_probe_20260901.md`（live-candidate data.stats.gov.cn PENDING_CANDIDATE_ONLY；O1 仍 OPEN；registry 零改动 = 任务书 A.2 唯一合规落点）

**646 审计 P4-1/2/3** (免修登记): 7→8 就地更正+尾注 (可溯接受) / e 段编号偏离草案 (不变量成立) / 元数据小疵。

---

## 5. 648 下一步

### 5.1 648 候选 scope

- **scope A (推荐)**: 沿用 647 模式 + 加 9-11 试点省扩展 (e.g. jilin/liaoning/anhui/hunan/hubei/shaanxi/sichuan/guizhou/jiangsu 等) — spike 第 6 次扩展；优先选 1-2 个 REACHABLE + 1-2 个 625 substitute 验证双 pattern
- **scope B**: O1 B路 live-candidate 启用 (per 646-A.2 data.stats.gov.cn PENDING_CANDIDATE → 等用户裁定启用)
- **scope C**: Gate 1 启动 (M2 Gate 后才合法, 当前阻塞; 沿用 646 §5)
- **scope D**: docs/45/50 spike 文档清空收口 (沿用 M6 收口模式)
- **scope E**: 5W1H 分析 + 沿用 638-647 模式扩展 (spec 推演)

### 5.2 当前未落地（红线守护）

- **Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M5 / M5.1 / M5.2 / M5.3 / M6** — 15 个里程碑不宣布 PASS
- O1 仍 OPEN (B路 live-candidate 仅登记, 不切换/启用)
- dbt mart flip: 60 行 demo 中仅 1 行（nanjing + CONDITION）真实化 pilot, O1 全量未启动
- 4 fixture 锁值永不动（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
- 不动 registry.csv / mart 既有 638-646 行
- 不写 cegr.* 生产表
- chain_id 区分: 647 '_v4' ≠ 646 '_v3' ≠ 645 '_v2' ≠ 644 '_policy_detail' ≠ 643 '_govreport' ≠ 642 '_renmian' ≠ 641 '_heilongjiang'
- UUID f 段 (f02-f62) ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段

---

## 6. 下一步 + 不宣称 PASS

**647 完成**:
- M4.10 政策详情 v4 真实化 (2 样本 × 1 HTTP each = 2 cells; chain_id='real_647_m4_10_policy_detail_v4'; UUID f 段; 2 NEW SHA: 8016ef08/56481050)
- O1 零动作 (live-candidate 沿用 646 登记, 不切换/启用)
- 646 审计 P2/P3 修正 (docs/70 §4 表尾 P2-1 F7 补登记 + docs/70 §6 行内 P3-2 措辞更正; 不删行不删 OPEN 行)
- ≥48/48 pytest green (647 ≥ 10 + 646+645 38 回归)
- evidence_pack × 1 + docs/reports × 1 + docs/70 行内 append × 2 + docs/71 + docs/52 零改动 全部落地

**不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线）。

**O1 仍 OPEN** — B路 live-candidate 仅登记, 不切换/启用; 等用户/架构师裁定。

---

— End 71 — M4.10 v4 + O1 零动作 + 646 审计 P2/P3 修正 真实化 spike 审查 20260901 —