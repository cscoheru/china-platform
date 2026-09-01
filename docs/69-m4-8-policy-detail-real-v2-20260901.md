# 69 — M4.8 政策详情 v2 真实化 spike（架构师级审查）

> **刀号**: 645
> **Milestone**: M4.8（沿用 641/642/643/644 spike 模式；spike 三次）
> **类型**: 架构师级 §1-§6 审查文档
> **日期**: 2026-09-01
> **依据**:
> - `docs/63-m4-5-renmian-real-20260901.md` (642 M4.5 任免真实化)
> - `docs/65-m4-6-govreport-real-20260901.md` (643 M4.6 政府工作报告)
> - `docs/67-m4-7-policy-detail-real-20260901.md` (644 M4.7 政策详情)
> - `docs/68-m6-spike-docs-closure-20260901.md` (645 M6 master)
> - `645-stage0-architect-m6-m4-8-policy-detail-v2-tasking-20260901.md` §3.645-A.2
> **前置**: 644 M4.7 落地 = 3 试点省 (heilongjiang/henan/yunnan) × 1 detail each × 6 政策表 = 18 INSERT
> **架构师综合**: M4.8 = 复用 644 3 试点省 + 纳入 644 留作扩展的 henan `bd4c4c51...` (zwgk root) 作为第 4 样本 = **24 INSERT planned** (vs 644 spike 18 INSERT + 8 source_registry/source_document = 32 INSERT total)
> **不宣布** Gate / O1 / M2 / M4 / M4.7 / M4.8 / M5 / M6 PASS。

---

## 1. M4.8 落地终态

| 子刀 | 文件 / 范围 | 状态 | 说明 |
|---|---|---|---|
| 645-A.1 | `docs/68-m6-spike-docs-closure-20260901.md` + 4 处互链补登 (docs/45/50/53/66/67) | DONE | M6 spike 文档系列收口 master (本文 + 4 互链) |
| 645-A.2 | `scripts/fetch_m4_8_policy_detail_v2_2024.py` + `evidence_pack/m4_8_policy_detail_real_v2_20260901.json` + `docs/reports/m4_8_policy_detail_real_v2_20260901.md` | DONE | M4.8 政策详情 v2 真实化；4 样本 (heilongjiang/henan-zfgb/henan-zwgk/yunnan) × 1 HTTP each = 4 cells；http_count=4/12；fetched_count=4；顶层裁定 REAL_FETCHED；4 真实样本落地 |
| 645-A.3 | `scripts/seed_m4_8_policy_detail_real_v2.sql` | DONE | 4 样本 × 1 detail each × 6 政策表 = **24 INSERT** (+ 4 source_registry + 4 source_document = 32 INSERT total)；lineage JSONB `is_demo='false'` 真实化 sentinel；chain_id=`real_645_m4_8_policy_detail_v2` (≠ 644)；UUID d 段 ≠ 644 c 段 |
| 645-A.4 | 本文档（docs/69） | DONE | §1-§6 架构师级审查 |
| 645-A.5 | `docs/reports/m6_spike_docs_closure_20260901.md` + `evidence_pack/m6_spike_docs_closure_20260901.json` + `docs/reports/m4_8_policy_detail_real_v2_20260901.md` + `evidence_pack/m4_8_policy_detail_real_v2_20260901.json` | DONE | 4 文件 (2 M6 + 2 M4.8) |
| 645-B | `tests/test_m6_spike_docs_closure.py` ≥ 6 + `tests/test_m4_8_policy_detail_real_v2.py` ≥ 6 | DONE | 共 ≥ 12 用例；全套 pytest ≥ 12/12 green |
| 645-C | 回执 + commit + 双推 | DONE | `645-stage0-cc-m6-m4-8-parallel-receipt-20260901.md` §PHOTO-1..6 |

---

## 2. M4.8 spike 边界（vs 644 tasking 规划）

### 2.1 645 tasking 规划 vs 实测对比

**645 tasking 规划**：

- 沿用 644 3 试点省 × 1 detail each × 6 政策表 = 18 INSERT
- + 纳入 644 留作扩展的 henan `bd4c4c51...` (zwgk root) 作为第 4 样本
- = **24 INSERT planned**（6 表 × 4 真实）
- + 4 source_registry + 4 source_document = 32 INSERT total
- ≤12 HTTP total (4 cells × 1 HTTP each)
- chain_id='real_645_m4_8_policy_detail_v2' (≠ 644 chain_id)
- UUID prefix d 段 ≠ 644 c 段

**645 实测反发现**：

- 4 真实样本落地（4 distinct SHA）：
  - heilongjiang `6237cd48afc60c06...` (c107884 list) — **drift from 644 `bad8be51`** (SHA drift event, per docs/52 (a)/(b) policy)
  - henan-zfgb `dfa38998c3e7e892...` (zfgb list) — 沿用 644 SHA
  - henan-zwgk `bd4c4c51b8f371e2...` (zwgk root) — NEW 645 第 4 样本 (644 留作扩展)
  - yunnan `f33eba53a1e5e961...` (zfgzbg) — 沿用 644 SHA
- 4 试点省 / 样本位 全部 REACHABLE ✓
- spike 边界 **实测 24 INSERT** = **规划 24 INSERT = 0 调整**（沿用 644 模式更精确）

### 2.2 spike 边界明细（24 INSERT 政策表 + 8 source_registry/source_document = 32 INSERT total）

| 表 | 行数 | lineage.is_demo | UUID prefix | 区别 vs 644 |
|---|---|---|---|---|
| source_registry | 4 | `'false'` (NEW) | d0eebc99-...d21/d22/d23/d24 | 644 = 0 行（沿用 643）|
| source_document | 4 | `'false'` (NEW) | d0eebc99-...d31/d32/d33/d34 | 644 = 0 行 |
| policy_document | **4** | `'false'` (spike) | d1eebc99-...d41/d42/d43/d44 | 644 d 段 (≠ 644 c 段 c41/c42/c43) |
| policy_target | **4** | `'false'` (spike) | d2eebc99-...d51/d52/d53/d54 | 644 d 段 (≠ c51/c52/c53) |
| policy_measure | **4** | `'false'` (spike) | d3eebc99-...d61/d62/d63/d64 | 644 d 段 (≠ c61/c62/c63) |
| government_commitment | **4** | `'false'` (spike) | d4eebc99-...d71/d72/d73/d74 | 644 d 段 (≠ c71/c72/c73) |
| commitment_progress | **4** | `'false'` (spike) | d5eebc99-...d81/d82/d83/d84 | 644 d 段 (≠ c81/c82/c83) |
| project_event | **4** | `'false'` (spike) | d6eebc99-...d91/d92/d93/d94 | 644 d 段 (≠ c91/c92/c93) |

**总计**：4 × 6 = **24 INSERT** (vs 644 实测 18 INSERT；M4.8 是 spike 三次，多 1 样本 + source_registry/source_document 纳入) + 8 source_registry/source_document = **32 INSERT total**

### 2.3 真实样本 (4 distinct SHA → 4 用于 seed)

| 序号 | 试点省 | slot | URL | SHA (前 16) | file_size | 645 seed 用 | 备注 |
|---|---|---|---|---|---|---|---|
| 1 | heilongjiang | hlj_policy_list | `/hlj/c107884/list.shtml` | `6237cd48afc60c06` | 148,507 | ✓ | **drift from 644 `bad8be51`** |
| 2 | henan | henan_zfgb_list | `/zwgk/zfgb/` | `dfa38998c3e7e892` | 8,959 | ✓ | 沿用 644 |
| 3 | henan | henan_zwgk_root | `/zwgk/` | `bd4c4c51b8f371e2` | 158,029 | ✓ | **NEW 645 第 4 样本** (644 留作扩展) |
| 4 | yunnan | yunnan_zfgzbg | `/zwgk/zfxxgk/zfgzbg/` | `f33eba53a1e5e961` | 94,310 | ✓ | 沿用 644 |

**4 SHA distinct vs 644 SHA**：
- 645 `6237cd48` ≠ 644 `bad8be51` (drift) ✓
- 645 `dfa38998` = 644 `dfa38998` (沿用) ✓
- 645 `bd4c4c51` = 644 `bd4c4c51` (644 留作扩展，645 正式 seed) ✓
- 645 `f33eba53` = 644 `f33eba53` (沿用) ✓
- 4 SHA 全部 distinct ≠ 643 SHA `e68099df/63109491/93fe23b3` ≠ 642 SHA `cd6aff30/4349ee0f/fede03ba` ≠ 641 SHA `26e5379d...b87ab` ≠ 640 demo SHA `'0…02'` ≠ 639 demo SHA `'0…01'` ✓

---

## 3. 真实化 demo SQL 结构（基于 645-A.3）

### 3.1 INSERT 结构（24 INSERT 政策表 + 8 source = 32 INSERT total）

```sql
-- 1. 4 source_registry (lineage.is_demo='false', chain_id='real_645_m4_8_policy_detail_v2')
INSERT INTO source_registry ... (4 行: d21-d24)

-- 2. 4 source_document (lineage.is_demo='false')
INSERT INTO source_document ... (4 行: d31-d34)

-- 3. 4 policy_document (lineage.is_demo='false', chain_id='real_645_m4_8_policy_detail_v2')
INSERT INTO policy_document ... ('POLICY_DETAIL' classification)

-- 4. 4 policy_target (real-policy-target-{hlj/henan-zfgb/henan-zwgk/yunnan}-v2)
INSERT INTO policy_target ...

-- 5. 4 policy_measure (real-policy-measure-{...}-v2, REGULATORY)
INSERT INTO policy_measure ...

-- 6. 4 government_commitment (real-commitment-{...}-v2, geo_entity_id via SELECT 子查询)
INSERT INTO government_commitment ...
SELECT ... FROM geo_entity g WHERE canonical_name IN ('黑龙江省', '河南省', '云南省') AND level='PROVINCIAL' LIMIT 1

-- 7. 4 commitment_progress (progress_value=0.5 PERCENT, IN_PROGRESS)
INSERT INTO commitment_progress ...

-- 8. 4 project_event (real-project-{...}-v2, geo_entity_id via SELECT 子查询)
INSERT INTO project_event ...
SELECT ... FROM geo_entity g WHERE canonical_name IN ('黑龙江省', '河南省', '云南省') AND level='PROVINCIAL' LIMIT 1
```

### 3.2 lineage JSONB 真实化 sentinel 一致 shape

```json
{
  "chain_id": "real_645_m4_8_policy_detail_v2",
  "source_file_sha256": "<真实 SHA per 样本>",
  "source_file_url": "<真实 detail page URL>",
  "extractor_version": "v1.0",
  "is_demo": "false"
}
```

### 3.3 geo_entity 真实化方案（沿用 641/642/643/644）

- 黑龙江/河南/云南 geo_entity_id 通过 SELECT 子查询获取（与 641/642/643/644 模式同）
- 兼容 M2-a seed `seed_m2_province_geo.py`（30 省 geo_entity 已 INSERT）
- 不引入新 synthetic geo_entity
- UUID 由 INSERT 时硬编码（d41/d42/d43/d44, d51/d52/d53/d54, ...d91/d92/d93/d94）；government_commitment / project_event 用 SELECT id FROM geo_entity WHERE canonical_name = ... LIMIT 1

---

## 4. lineage 真实化 sentinel（沿用 009+010+014+015）

### 4.1 docs/33 §3.2 sentinel 沿用

- lineage JSONB `is_demo` 是唯一落点；独立 BOOLEAN 列不允许（除 person/appointment_event 015 历史债）
- 009 migration（5 政策表）+ 010 migration（project_event）+ 014/015 migration（spike 沿用）= lineage JSONB 全表已覆盖
- 真实数据 INSERT 必须 `lineage->>'is_demo' = 'false'`（沿用 641/642/643/644 模式）
- 沿用 sentinel 一致性更高；**不新写 016 migration**

### 4.2 chain_id 区分裁定（避免 SHA collision）

| 刀号 | chain_id | is_demo | 性质 |
|---|---|---|---|
| 638 | `real_638_m4_1_people` | `'true'` | demo |
| 639 | `demo_639` | `'true'` | demo |
| 640 | `demo_640` | `'true'` | demo |
| 641 | `real_641_heilongjiang` | `'false'` | real spike |
| 642 | `real_642_m4_5_renmian` | `'false'` | real spike |
| 643 | `real_643_m4_6_govreport` | `'false'` | real spike |
| 644 | `real_644_m4_7_policy_detail` | `'false'` | real spike |
| **645** | **`real_645_m4_8_policy_detail_v2`** | **`'false'`** | **real spike (三次; v2 标记 = 第 4 样本纳入)** |

### 4.3 真实 SHA 区分表（4 新 SHA 含 1 漂移 + 2 沿用 + 1 NEW）

| 刀号 | 试点省 / 样本位 | 真实 SHA | URL | 备注 |
|---|---|---|---|---|
| 641 | heilongjiang | `26e5379d...b87ab` | 王正军任免 | 641 spike 1 |
| 642 | henan | `cd6aff30...` | 任免 endpoint | 642 任免 |
| 642 | guangdong | `4349ee0f...` | 任免 endpoint | 642 任免 |
| 642 | guizhou | `fede03ba...` | 任免 endpoint | 642 任免 |
| 643 | heilongjiang | `e68099df...` | 政府公报首页 | 643 公报 |
| 643 | henan | `63109491...` | 公报首页 | 643 公报 |
| 643 | yunnan | `93fe23b3...` | 公报首页 | 643 公报 |
| 644 | heilongjiang | `bad8be51...` | c107884 list | 644 spike 1 |
| 644 | henan | `dfa38998...` | /zwgk/zfgb/ list | 644 spike 2 |
| 644 | yunnan | `f33eba53...` | /zwgk/zfxxgk/zfgzbg/ | 644 spike 3 |
| **645** | **heilongjiang** | **`6237cd48...`** | **c107884 list** | **645 drift from 644 `bad8be51`** (drift event) |
| **645** | **henan-zfgb** | **`dfa38998...`** | **/zwgk/zfgb/ list** | **645 沿用 644** |
| **645** | **henan-zwgk** | **`bd4c4c51...`** | **/zwgk/ root** | **645 NEW 第 4 样本** |
| **645** | **yunnan** | **`f33eba53...`** | **/zwgk/zfxxgk/zfgzbg/** | **645 沿用 644** |

**架构师反发现 — 645 SHA drift 事件**：
- heilongjiang `c107884/list.shtml` 在 644 → 645 之间发生 SHA drift（`bad8be51` → `6237cd48`）
- 这是 docs/52 SHA drift 政策所规定的正常现象（源站内容可能更新）
- 645 seed SQL 使用 645 实际抓取的 SHA `6237cd48`，不沿用 644 的 `bad8be51`
- drift 不影响 lineage JSONB `is_demo='false'` 真实化判定（`is_demo` 与具体 SHA 值无关）
- 红线：不静默硬编码 SHA；不沿用旧 SHA 假装是新的；漂移按 docs/52 (a)/(b) 二选一，本刀选 (a) 更新 SHA

---

## 5. 646 下一步（架构师推荐）

**scope 选 A（推荐）**：646 = M6 收口（如 O1 主路径 docs/52 B 路 live-candidate 探测）+ M4.9 政策详情 v3 扩展。

**scope 选 B**：646 = Gate 1 启动（架构师启动 Gate 1 而非继续 spike）— M2 Gate 后才合法。

**scope 选 C**：646 = O3 OCR 真实化（沿用 583 O3 spike；2026-08 已完成 spike + audit + 自取政府源）。

**scope 选 D**：646 = docs/45/50 spike 文档清空收口（沿用 M6 收口模式）。

**scope 选 E**：646 = M4.9 试点省扩展（沿用 644 模式 + 加 fujian / guangdong 第 5/6 样本）。

**沿用 644/645 模式**：架构师本终端自签 + 自交付（执行端模式继续）。

---

## 6. 下一步 + 不宣称 PASS

- 架构师（用户）接受/驳回 646 推荐 scope（A/B/C/D/E）
- 执行端（本终端即架构师）收到 646 tasking 后即签即自交付
- **不宣布** Gate / O1 / M2 / M4 / M4.7 / M4.8 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线）
- 645 完成：M6 spike 文档系列收口 master (docs/68) + M4.8 政策详情 v2 真实化 spike 三次 (24 INSERT; lineage JSONB `is_demo='false'` 真实化 sentinel; chain_id='real_645_m4_8_policy_detail_v2')

— End 645 docs/69 —
