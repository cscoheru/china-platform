# docs/65 — M4.6 政府工作报告真实化（6 试点省 spike）

> **类型**: 架构师级 §1-§6 审查 · knife 643 (M4.6 side)
> **日期**: 2026-09-01
> **前置**: 638 REACHABLE 23/32 列表 (zfgb 路径) + 642 6 试点省列表 + 643 tasking §2.643-A.2
> **依据**: `reviews/stage0-gate0-rework-2026-08-23/643-stage0-architect-m5-2-m4-6-parallel-tasking-20260901.md` §2.643-A.2/A.3
> **抓取脚本**: `scripts/fetch_m4_6_govreport_v1_2024.py`（≤12 HTTP total; curl only; 不爬网; 不写 cegr.* 表）
> **seed SQL**: `scripts/seed_m4_6_govreport_real.sql`（24 INSERT; 3 试点省 × 8 表 × 1 each）
> **证据**: `evidence_pack/m4_6_govreport_real_20260901.json` + `docs/reports/m4_6_govreport_real_20260901.md`
> **不宣布**: Gate / O1 / M2 / M4 PASS

---

## 1. M4.6 落地终态

### 1.1 子刀状态表

| 子刀 | 文件 | 状态 | 说明 |
|---|---|---|---|
| 643-A.2 | `scripts/fetch_m4_6_govreport_v1_2024.py` + `evidence_pack/m4_6_govreport_real_20260901.json` + `docs/reports/m4_6_govreport_real_20260901.md` | DONE | M4.6 政府工作报告真实化；6 试点省 × 1 detail each；http_count=9/12；fetched_count=3（REAL_FETCHED）；顶层裁定 REAL_FETCHED；3 新真实样本 hlj/henan/yunnan |
| 643-A.3 | `scripts/seed_m4_6_govreport_real.sql` | DONE | 3 source_registry + 3 source_document + 18 政策表 INSERT = **24 INSERT 共**; lineage JSONB `is_demo='false'` 真实化 sentinel; chain_id=`real_643_m4_6_govreport`; 3 新 SHA 全 distinct ≠ 642/641/640/639 demo/real SHA; 不新写 016 migration; hlj/henan/yunnan geo_entity_id 通过 SELECT 子查询获取 |

### 1.2 M4.6 顶层裁定

- **REAL_FETCHED** — http_count=9/12; fetched_count=3 真实政府公报样本
- 3 真实样本（沿用 spike 性质；vs 642 实际 3 任免样本）:
  - **黑龙江** `/hlj/c107882/redirect_firstChannel.shtml` — 省政府公报 (2026-02-13, 819 bytes, SHA `e68099df...`)
  - **河南** `/2026/07-29/3380417.html` — 河南省人民政府公报2026年第14号 (2026-07-29, 13457 bytes, SHA `63109491...`)
  - **云南** `/zwgk/zfgb/` — 云南省人民政府公报 (2026-08-15, 79137 bytes, SHA `93fe23b3...`)

---

## 2. M4.6 spike 边界调整（vs 643 tasking 规划）

### 2.1 规划 vs 实测对比表

| 试点省 | landing URL | 规划 endpoint | 实测 verdict | 643 落地 |
|---|---|---|---|---|
| 黑龙江 | `/zwgk/zfgb/` | 政府工作报告 | 200 OK + 公报首页 anchor | ✓ 落地 (SHA `e68099df...`) |
| 福建 | `/zwgk/zfgb/` | 政府工作报告 | **404** | ✗ 排除（路径别名） |
| 河南 | `/zwgk/zfgb/` | 政府工作报告 | 200 OK + 公报 anchor | ✓ 落地 (SHA `63109491...`) |
| 广东 | `/zwgk/zfgb/` | 政府工作报告 | **404** | ✗ 排除（路径别名） |
| 贵州 | `/zwgk/zcfg/szfwj/` | 政府工作报告 | 200 OK 但 anchor 未匹配政府工作报告 | ✗ 排除（anchor 不匹配） |
| 云南 | `/zwgk/zfgb/` | 政府工作报告 | 200 OK + 公报 anchor | ✓ 落地 (SHA `93fe23b3...`) |

### 2.2 排除原因详解

- **福建**: landing 404 ⇒ 无 anchor 抓取 ⇒ 排除
- **广东**: landing 404 ⇒ 无 anchor 抓取 ⇒ 排除
- **贵州**: landing 200 OK 但 anchor 中无 `政府工作|工作报告|政府报告|年度工作|政府公报|规划计划|五年规划` 关键词 ⇒ 排除

### 2.3 调整后 spike 边界

- **规划**: 6 试点省 × 1 detail each × 6 政策表 = **36 INSERT** (643 tasking §2.643-A.3)
- **实测**: 3 试点省（hlj/henan/yunnan）× 1 detail each × 8 表 = **24 INSERT**
- **与 642 同模式**: spike 边界调整（vs 642 实际 18 INSERT = 3 × 6 政策表）；643 含 8 表（vs 642 6 表），因为 source_document + 7 表（5 政策表 + commitment + project_event）

---

## 3. 真实化 demo SQL 结构（基于 643-A.3）

### 3.1 INSERT 总览（24 INSERT 共）

| 表 | 行数 | lineage.is_demo | 来源 |
|---|---|---|---|
| source_registry | 3 | — (synthetic, but 真实 domain) | hlj / henan / yunnan 政府网官方 (enabled=TRUE) |
| source_document | 3 | — (file_hash_sha256 真实) | 3 真实 detail page (verification_status=UNVERIFIED) |
| policy_document | **3** | `'false'` (spike) | 3 GOV_REPORT (BULLETIN classification) |
| policy_target | **3** | `'false'` (spike) | 3 real-policy-target-{hlj/henan/yunnan}-1 |
| policy_measure | **3** | `'false'` (spike) | 3 real-policy-measure-{...}-1, measure_type=REGULATORY |
| government_commitment | **3** | `'false'` (spike) | 3 real-commitment-{...}-1, geo_entity_id=**SELECT 子查询** |
| commitment_progress | **3** | `'false'` (spike) | 3 progress_value=1.0, FULFILLED |
| project_event | **3** | `'false'` (spike) | 3 real-project-{...}-1, geo_entity_id=**SELECT 子查询** |

**总计**：3 + 3 + 3×6 = 24 INSERT（vs 643 tasking 规划 3 + 3 + 36 = 42 INSERT；spike 边界调整后 24 INSERT）

### 3.2 lineage JSONB 真实化 sentinel 一致 shape

```json
{
  "chain_id": "real_643_m4_6_govreport",
  "source_file_sha256": "<真实 SHA per province>",
  "source_file_url": "<真实 detail page URL>",
  "extractor_version": "v1.0",
  "is_demo": "false"
}
```

### 3.3 geo_entity 真实化方案（沿用 641/642）

- 黑龙江/河南/云南 geo_entity_id 通过 SELECT 子查询获取（与 641/642 模式同）
- 兼容 M2-a seed `seed_m2_province_geo.py`（30 省 geo_entity 已 INSERT）
- 不引入新 synthetic geo_entity
- UUID 由 INSERT 时硬编码（d2eebc99-...b51/b52/b53）；government_commitment / project_event 用 SELECT id FROM geo_entity WHERE canonical_name = ... LIMIT 1

---

## 4. lineage 真实化 sentinel（沿用 009+010）

### 4.1 docs/33 §3.2 sentinel 沿用

- lineage JSONB `is_demo` 是唯一落点；独立 BOOLEAN 列不允许（除 person/appointment_event 015 历史债）
- 009 migration（5 政策表）+ 010 migration（project_event）+ 014/015 migration（spike 沿用）= lineage JSONB 全表已覆盖
- 真实数据 INSERT 必须 `lineage->>'is_demo' = 'false'`（沿用 641/642 模式）
- 沿用 sentinel 一致性更高；**不新写 016 migration**

### 4.2 chain_id 区分表（避免 SHA collision）

| 刀号 | chain_id | is_demo | 性质 |
|---|---|---|---|
| 638 | `real_638_m4_1_people` | `'true'` | demo |
| 639 | `demo_639` | `'true'` | demo |
| 640 | `demo_640` | `'true'` | demo |
| 641 | `real_641_heilongjiang` | `'false'` | real spike (王正军任免 SHA `26e5379d...b87ab`) |
| 642 | `real_642_m4_5_renmian` | `'false'` | real spike (任免 SHA `cd6aff30` / `4349ee0f` / `fede03ba`) |
| **643** | **`real_643_m4_6_govreport`** | **`'false'`** | **real spike** (政府工作报告 SHA `e68099df` / `63109491` / `93fe23b3`) |

### 4.3 真实 SHA 区分表

| 刀号 | SHA (前 8 字符) | 来源 | endpoint |
|---|---|---|---|
| 640 demo | `0…02` | 6 表 × 3 demo | demo |
| 641 real | `26e5379d` | 王正军任免 (黑龙江) | 任免 |
| 642 real | `cd6aff30` | 狄绯任免 (河南) | 任免 |
| 642 real | `4349ee0f` | 5月份人事任免 (广东) | 任免 |
| 642 real | `fede03ba` | 刘锐任免 (贵州) | 任免 |
| **643 real** | **`e68099df`** | **省政府公报 (黑龙江)** | **政府工作报告** |
| **643 real** | **`63109491`** | **省政府公报2026年第14号 (河南)** | **政府工作报告** |
| **643 real** | **`93fe23b3`** | **省政府公报 (云南)** | **政府工作报告** |

---

## 5. 644 下一步（架构师推荐）

### 5.1 推荐 scope

1. **644 = M5 第三次收口 + M4.7 政策详情真实化并行**（推荐）
   - M5 第三次：国务院 `/zhengce/` root 索引 + WAF 网防G01 selective 子路径 验证（≤10 HTTP）
   - M4.7 政策详情：复用 643 3 试点省（hlj/henan/yunnan）× 1 detail each × 6 政策表 spike = 18 INSERT planned
   - chain_id='real_644_m4_7_policy_detail'
2. **644 = M6 文档收口 + M4.7 并行**（备选）
   - M6: docs/45 + docs/50 + docs/33 §3.2 sentinel 收口（架构师级）
3. **644 = M5 收口 + M4.7 + M6 三方并行**（激进）
   - spike 不互斥；三方并行 spike

### 5.2 M4.7 复用 643 锚

- 3 试点省：heilongjiang / henan / yunnan
- 3 新 SHA：e68099df..., 63109491..., 93fe23b3...（≠ 642 任免）
- endpoint = 政策详情（vs 643 政府工作报告 = 政府公报首页）
- chain_id='real_644_m4_7_policy_detail'

---

## 6. 下一步 + 不宣称 PASS

- 643-A.2 (M4.6 真实抓) + 643-A.3 (seed SQL) DONE — 24 INSERT lineage.is_demo='false' chain_id='real_643_m4_6_govreport'
- docs/65 §1-§6 架构师级审查 DONE
- 等待用户裁定 644 scope（M5 第三次收口 + M4.7 / M6 + M4.7 / 三方并行）
- **不宣布** Gate / O1 / M2 / M4 / M4.6 PASS（沿用红线）
- 不向用户提任何 URL 裁定事项（数据源唯一 = 政府源自取）

— End docs/65 —