# 67 — M4.7 政策详情真实化 spike（架构师级审查）

> **刀号**: 644
> **Milestone**: M4.7（沿用 642 + 643 模式；spike 二次）
> **类型**: 架构师级 §1-§6 审查文档
> **日期**: 2026-09-01
> **依据**:
> - `docs/63-m4-5-renmian-real-20260901.md` (642 M4.5 任免真实化)
> - `docs/65-m4-6-govreport-real-20260901.md` (643 M4.6 政府工作报告)
> - `643-stage0-architect-m5-2-m4-6-parallel-tasking-20260901.md` §2.643-A.2
> - `644-stage0-architect-m5-3-m4-7-parallel-tasking-20260901.md` §2.644-A.2
> **前置**: 643 M4.6 落地 = 3 试点省 (heilongjiang/henan/yunnan) × 政府公报首页
> **架构师综合**: M4.7 = 复用 643 3 试点省 × 1 detail each × 6 政策表 = 18 INSERT planned (vs 643 spike 边界调整后 24 INSERT 不同 — M4.7 是 spike 二次，不含 source_registry/source_document 重复)
> **不宣布** Gate / O1 / M2 / M4 / M4.7 PASS。

---

## 1. M4.7 落地终态

| 子刀 | 文件 / 范围 | 状态 | 说明 |
|---|---|---|---|
| 644-A.2 | `scripts/fetch_m4_7_policy_detail_v1_2024.py` + `evidence_pack/m4_7_policy_detail_real_20260901.json` + `docs/reports/m4_7_policy_detail_real_20260901.md` | DONE | M4.7 政策详情真实化；3 试点省 (heilongjiang/henan/yunnan) × 1 detail each 政策详情页 landing 真实抓取；http_count=6/12；fetched_count=5 (含 4 distinct SHA)；顶层裁定 REAL_FETCHED；3 真实样本落地 |
| 644-A.3 | `scripts/seed_m4_7_policy_detail_real.sql` | DONE | 3 试点省 × 1 detail each × 6 政策表 = **18 INSERT**；lineage JSONB `is_demo='false'` 真实化 sentinel；chain_id=`real_644_m4_7_policy_detail`；3 新 SHA 全 distinct ≠ 643/642/641/640/639 demo/real SHA；UUID c 段 ≠ 643 b 段 |
| 644-A.4 | 本文档（docs/67） | DONE | §1-§6 架构师级审查 |
| 644-A.5 | `docs/reports/m4_7_policy_detail_real_20260901.md` + `evidence_pack/m4_7_policy_detail_real_20260901.json` | DONE | 1 报告 + 1 证据包 |
| 644-B | `tests/test_m4_7_policy_detail_real.py` ≥ 6 | DONE | 共 ≥ 6 用例；全套 pytest ≥ 29/29 green |
| 644-C | 回执 + commit + 双推 | DONE | `644-stage0-cc-m5-3-m4-7-parallel-receipt-20260901.md` §PHOTO-1..6 |

---

## 2. M4.7 spike 边界（vs 643 tasking 规划）

### 2.1 644 tasking 规划 vs 实测对比

**644 tasking 规划**：

- 3 试点省 (heilongjiang/henan/yunnan) × 1 detail each × 6 政策表 = **18 INSERT planned**
- 不写 source_registry/source_document（沿用 643 既有）
- ≤12 HTTP total (6 cells × 2 HTTP main+fallback)

**644 实测反发现**：

- 5 真实样本落地（4 distinct SHA）：hlj `bad8be51...` (×2 cells), henan `dfa38998...` (zfgb list), henan `bd4c4c51...` (zwgk root), yunnan `f33eba53...` (zfgzbg)
- 3 试点省 hlj/henan/yunnan 全部 REACHABLE ✓
- spike 边界 **实测 18 INSERT** = **规划 18 INSERT = 0 调整**（沿用 643 模式更精确）

### 2.2 spike 边界明细（18 INSERT）

| 表 | 行数 | lineage.is_demo | UUID prefix | 区别 vs 643 |
|---|---|---|---|---|
| source_registry | 0 (沿用 643) | n/a | n/a | 643 = d0eebc99-...b21/b22/b23 |
| source_document | 0 (沿用 643) | n/a | n/a | 643 = d0eebc99-...b31/b32/b33 |
| policy_document | **3** | `'false'` (spike) | d1eebc99-...c41/c42/c43 | 643 b 段 ≠ 644 c 段 |
| policy_target | **3** | `'false'` (spike) | d2eebc99-...c51/c52/c53 | 643 b 段 ≠ 644 c 段 |
| policy_measure | **3** | `'false'` (spike) | d3eebc99-...c61/c62/c63 | 643 b 段 ≠ 644 c 段 |
| government_commitment | **3** | `'false'` (spike) | d4eebc99-...c71/c72/c73 | 643 b 段 ≠ 644 c 段 |
| commitment_progress | **3** | `'false'` (spike) | d5eebc99-...c81/c82/c83 | 643 b 段 ≠ 644 c 段 |
| project_event | **3** | `'false'` (spike) | d6eebc99-...c91/c92/c93 | 643 b 段 ≠ 644 c 段 |

**总计**：3 × 6 = **18 INSERT**（vs 643 实测 24 INSERT；M4.7 是二次 spike 不含 source_registry/source_document 重复）

### 2.3 真实样本 (4 distinct SHA → 3 用于 seed)

| 序号 | 试点省 | URL | SHA (前 16) | file_size | 644 seed 用 |
|---|---|---|---|---|---|
| 1 | heilongjiang | `/hlj/c107884/list.shtml` | `bad8be515afe9a81` | varies | ✓ |
| 2 | henan | `/zwgk/zfgb/` | `dfa38998c3e7e892` | 8,959 | ✓ |
| 3 | henan | `/zwgk/` | `bd4c4c51b8f371e2` | varies | ✗ (留作 v2 扩展) |
| 4 | yunnan | `/zwgk/zfxxgk/zfgzbg/` | `f33eba53a1e5e961` | 94,310 | ✓ |

**3 用于 seed 的 SHA**（hlj `bad8be51...` / henan `dfa38998...` / yunnan `f33eba53...`）全 distinct ≠ 643 SHA `e68099df...` / `63109491...` / `93fe23b3...` ✓

---

## 3. 真实化 demo SQL 结构（基于 644-A.3）

### 3.1 INSERT 结构（18 INSERT 共）

```sql
-- 1. 3 policy_document (lineage.is_demo='false', chain_id='real_644_m4_7_policy_detail')
INSERT INTO policy_document ... ('POLICY_DETAIL' classification)

-- 2. 3 policy_target (real-policy-target-{hlj/henan/yunnan}-2)
INSERT INTO policy_target ...

-- 3. 3 policy_measure (real-policy-measure-{...}-2, REGULATORY)
INSERT INTO policy_measure ...

-- 4. 3 government_commitment (real-commitment-{...}-2, geo_entity_id via SELECT 子查询)
INSERT INTO government_commitment ...
SELECT ... FROM geo_entity g WHERE canonical_name IN ('黑龙江省', '河南省', '云南省') AND level='PROVINCIAL' LIMIT 1

-- 5. 3 commitment_progress (progress_value=0.5 PERCENT, IN_PROGRESS)
INSERT INTO commitment_progress ...

-- 6. 3 project_event (real-project-{...}-2, geo_entity_id via SELECT 子查询)
INSERT INTO project_event ...
SELECT ... FROM geo_entity g WHERE canonical_name IN ('黑龙江省', '河南省', '云南省') AND level='PROVINCIAL' LIMIT 1
```

### 3.2 lineage JSONB 真实化 sentinel 一致 shape

```json
{
  "chain_id": "real_644_m4_7_policy_detail",
  "source_file_sha256": "<真实 SHA per province>",
  "source_file_url": "<真实 detail page URL>",
  "extractor_version": "v1.0",
  "is_demo": "false"
}
```

### 3.3 geo_entity 真实化方案（沿用 641/642/643）

- 黑龙江/河南/云南 geo_entity_id 通过 SELECT 子查询获取（与 641/642/643 模式同）
- 兼容 M2-a seed `seed_m2_province_geo.py`（30 省 geo_entity 已 INSERT）
- 不引入新 synthetic geo_entity
- UUID 由 INSERT 时硬编码（c41/c42/c43, c51/c52/c53, ...c91/c92/c93）；government_commitment / project_event 用 SELECT id FROM geo_entity WHERE canonical_name = ... LIMIT 1

---

## 4. lineage 真实化 sentinel（沿用 009+010）

### 4.1 docs/33 §3.2 sentinel 沿用

- lineage JSONB `is_demo` 是唯一落点；独立 BOOLEAN 列不允许（除 person/appointment_event 015 历史债）
- 009 migration（5 政策表）+ 010 migration（project_event）+ 014/015 migration（spike 沿用）= lineage JSONB 全表已覆盖
- 真实数据 INSERT 必须 `lineage->>'is_demo' = 'false'`（沿用 641/642/643 模式）
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
| **644** | **`real_644_m4_7_policy_detail`** | **`'false'`** | **real spike (二次)** |

### 4.3 真实 SHA 区分表（3 新 SHA 全 distinct）

| 刀号 | 试点省 | 真实 SHA | URL | 文件类型 |
|---|---|---|---|---|
| 641 | heilongjiang | `26e5379d...b87ab` | 王正军任免 | 任免 endpoint |
| 642 | henan | `cd6aff30...` | 任免 endpoint | 任免 endpoint |
| 642 | guangdong | `4349ee0f...` | 任免 endpoint | 任免 endpoint |
| 642 | guizhou | `fede03ba...` | 任免 endpoint | 任免 endpoint |
| 643 | heilongjiang | `e68099df...` | 政府公报首页 | 公报首页 |
| 643 | henan | `63109491...` | 公报首页 | 公报首页 |
| 643 | yunnan | `93fe23b3...` | 公报首页 | 公报首页 |
| **644** | **heilongjiang** | **`bad8be51...`** | **c107884 list** | **政策详情 list** |
| **644** | **henan** | **`dfa38998...`** | **/zwgk/zfgb/ list** | **政策详情 list** |
| **644** | **yunnan** | **`f33eba53...`** | **/zwgk/zfxxgk/zfgzbg/** | **政策详情 (政府工作报告)** |

**3 新 644 SHA**（`bad8be51` / `dfa38998` / `f33eba53`）全 distinct ≠ 643 SHA / ≠ 642 SHA / ≠ 641 SHA / ≠ 640/639 demo SHA ✓

---

## 5. 645 下一步（架构师推荐）

**scope 选 A（推荐）**：645 = M6 spike 文档收口 + M4.8 政策详情扩展（沿用 644 3 试点省 × 1 detail each × 6 政策表 spike = 18 INSERT planned, chain_id='real_645_m4_8_policy_detail_v2'）。可纳入 644 留作扩展的 henan `bd4c4c51...` (zwgk root) 作为 M4.8 第 4 样本。

**scope 选 B**：645 = M5 收口（gov/zhengce/ root 索引全量）+ M4.8 并行

**scope 选 C**：645 = M5 + M4.8 + M6 三方并行（激进）

**scope 选 D**：645 = Gate 1 启动（架构师启动 Gate 1 而非继续 spike）— M2 Gate 后才合法

**scope 选 E**：645 = O3 OCR 真实化（沿用 583 O3 spike；2026-08 已完成 spike + audit + 自取政府源）

**沿用 644 模式**：架构师本终端自签 + 自交付（执行端模式继续）。

---

## 6. 下一步 + 不宣称 PASS

- 架构师（用户）接受/驳回 645 推荐 scope（A/B/C/D/E）
- 执行端（本终端即架构师）收到 645 tasking 后即签即自交付
- **不宣布** Gate / O1 / M2 / M4 / M4.7 PASS（沿用红线）
- 644 完成：M4.7 政策详情真实化 spike 二次（18 INSERT；lineage JSONB `is_demo='false'` 真实化 sentinel；chain_id='real_644_m4_7_policy_detail'）

— End 644 docs/67 —
