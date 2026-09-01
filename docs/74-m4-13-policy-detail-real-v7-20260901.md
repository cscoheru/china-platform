# 74 — M4.13 政策详情 v7 真实化 spike (架构师级审查)

> **刀号**: 650
> **Milestone**: M4.13（沿用 642/643/644/645/646/647/648/649 spike 模式；spike 第 9 次扩展）
> **类型**: 架构师级 §1-§6 审查文档
> **日期**: 2026-09-01
> **依据**:
> - `docs/73-m4-12-policy-detail-real-v6-20260901.md` (649 M4.12 政策详情 v6)
> - `reviews/stage0-gate0-rework-2026-08-23/649-audit-650-tasking-consolidated-20260901.md` (合并件: 649 审计 PASS·有限通过 + 650 任务书)
> - `649-stage0-cursor-s649-m4-12-v6-audit-PASS-20260901.md` (649 审计 PASS·有限通过)
> - `650-stage0-architect-m4-13-v7-substitute-labeling-tasking-20260901.md` (650 任务书 §1.650-A.0/A.1/A.2/A.3/A.4)
> **前置**: 649 DELIVERED + 审计 PASS（有限通过）
> **架构师综合**: 650 = A.0 649 审计 P3-1 蓝图更正（seed_m4_12 h02 行 province/name + 同文件 h04/h11/h41/h51/h61 同步更正; 红线 13 增补: 代换行 source_registry 一律用 actual_province）+ docs/73 §6.1 尾注登记 + A.1 M4.13 v7 guizhou/jiangsu 16 INSERT（chain_id='real_650_m4_13_policy_detail_v7' UUID i 段; guizhou /zwgk/ 200 直接 REACHABLE; jiangsu /zwgk/ 404 → / 200 REACHABLE; substitute 池备而未触发; http_count=3/12）+ A.2 O1 零动作 + A.3 本文档 (docs/74) + A.4 evidence ×2 (含附属复验产物指针)
> **chain_id**: `real_650_m4_13_policy_detail_v7` (末段 `_v7` ≠ 649 `_v6` ≠ 648 `_v5` ≠ 647 `_v4` ≠ 646 `_v3` ≠ 645 `_v2`)
> **UUID prefix**: i 段 (i02-i62) ≠ 649 h 段 (h02-h62) ≠ 648 g 段 (g02-g62) ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段
> **不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M6 PASS。

---

## 1. M4.13 v7 落地终态

| 子刀 | 文件 / 范围 | 状态 | 说明 |
|---|---|---|---|
| 650-A.0 | `scripts/seed_m4_12_policy_detail_real_v6.sql` h02 行 province HUBEI→LIAONING + source_name 同步更正 + h04/h11/h41/h51/h61 policy 表行 '湖北' 字样同步更正 + 行尾尾注标记 + `docs/73-m4-12-policy-detail-real-v6-20260901.md` §6.1 尾注登记 649 审计结果 | DONE | per 649 审计 P3-1；红线 13 增补: source_registry province/source_name 一律用 actual_province；lineage JSONB 内 original_province 仅作 provenance 留痕 |
| 650-A.1 | `scripts/fetch_m4_13_policy_detail_v7_2024.py` + `scripts/seed_m4_13_policy_detail_real_v7.sql` + `evidence_pack/m4_13_policy_detail_real_v7_20260901.json` + `docs/reports/m4_13_policy_detail_real_v7_20260901.md` | DONE | M4.13 政策详情 v7 真实化；2 样本 (guizhou + jiangsu 第 13/14 样本) × 6 政策表 + 2 source_registry + 2 source_document = **16 INSERT**；guizhou /zwgk/ 200 直接 REACHABLE (170166 bytes; SHA `5c5b1295...`)；jiangsu /zwgk/ 404 → fallback / 200 REACHABLE (82985 bytes; SHA `def18a2f...`)；substitute_used_count=0；递补池 shaanxi → sichuan 备而未触发；http_count=3/12 (25% usage) |
| 650-A.2 | O1 零动作（沿用 646 登记，O1 仍 OPEN） | DONE | 不新增 probe、不启用、不改 registry/connector；回执 O1 = OPEN |
| 650-A.3 | 本文档（docs/74） | DONE | §1-§6 架构师级审查 |
| 650-A.4 | `docs/reports/m4_13_policy_detail_real_v7_20260901.md` + `evidence_pack/m4_13_policy_detail_real_v7_20260901.json` | DONE | evidence × 2；主 evidence methodology 含附属产物指针（per 648 审计 P3-1 口径统一条款 + 649 审计 P3-1 代换行标注规范固化入红线 13） |

---

## 2. substitute 跨省代换登记（per 649 任务书 §0.13 + 650 任务书 §0.13 红线 13）

### 2.1 跨省 substitute 触发事实

Per 650 任务书 §0.13: **跨省 substitute 仅限递补池**（649 池成员 liaoning/shaanxi/sichuan/guizhou/jiangsu 中: 649 liaoning 已激活 → 650 池按序缩为 shaanxi → sichuan），触发即 evidence `substitute_reason` + docs/74 §2 登记。

**650 触发事件**: **无 substitute 触发**。本次 2 样本 (guizhou + jiangsu) 均在原生 fallback chain 内 REACHABLE:
- guizhou: `/zwgk/` 200 (chain_index=0 直接 REACHABLE)
- jiangsu: `/zwgk/` 404 → fallback `/` 200 (chain_index=1 fallback REACHABLE)

递补池按序 sha anxi → sichuan 备而未触发。Guizhou 槽与 jiangsu 槽均无 substitute 落地。

### 2.2 递补池状态更新（per 649 §4.4 + 650 增量）

| 池成员 | 状态 (649 后) | 状态 (650 后) | 备注 |
|---|---|---|---|
| **liaoning** | **✓ 649 激活** | ✓ 649 激活 | hubei 412+412 → ln /zwgk/ 404 → ln / 200 REACHABLE |
| shaanxi | 备而未触发 | 备而未触发 (优先级 1; 留给 651+) | — |
| sichuan | 备而未触发 | 备而未触发 (优先级 2; 留给 651+) | — |
| guizhou | 备而未触发 | ✓ **650 直接 REACHABLE** (无 substitute 触发) | guizhou /zwgk/ 200 直接 REACHABLE |
| jiangsu | 备而未触发 | ✓ **650 fallback REACHABLE** (无 substitute 触发) | jiangsu /zwgk/ 404 → / 200 REACHABLE |

### 2.3 649 P3-1 蓝图更正（per 650-A.0）

| 项 | 更正前 | 更正后 | 范围 |
|---|---|---|---|
| h02 source_registry.province | `'HUBEI'` | `'LIAONING'` | 主线 |
| h02 source_registry.source_name | `'湖北省人民政府 政务公开 landing (hubei 412+412 → liaoning 递补省府根 /)'` | `'辽宁省人民政府 政务公开 landing (hubei 槽 412×2 递补 per 649; per 650-A.0 P3-1 更正)'` | 主线 |
| h04 source_document.title | `'湖北省人民政府 政务公开 landing (hubei→liaoning 递补)'` | `'辽宁省人民政府 政务公开 landing (hubei 槽 412×2 递补 per 649; per 650-A.0 P3-1 更正)'` | 同步 |
| h11 policy_document.title | `'省政府政策详情 v6（湖北政务公开 landing, hubei→liaoning 递补）'` | `'省政府政策详情 v7（辽宁政务公开 landing, hubei 槽 412×2 递补 per 649; per 650-A.0 P3-1 更正）'` | 同步 |
| h11 policy_document.publisher | `'湖北省人民政府'` | `'辽宁省人民政府'` | 同步 |
| h41 government_commitment.commitment_text | `'real-commitment-hubei-v6 (政策详情 v6 第 11 样本; 湖北省政府, hubei→liaoning 递补)'` | `'real-commitment-hubei-v6 (政策详情 v6 第 11 样本; 辽宁省政府, hubei 槽 412×2 递补 per 649; per 650-A.0 P3-1 更正)'` | 同步 |
| h51 commitment_progress.reporting_org | `'湖北省人民政府 (hubei→liaoning 递补)'` | `'辽宁省人民政府 (hubei 槽 412×2 递补 per 649; per 650-A.0 P3-1 更正)'` | 同步 |
| h61 project_event.description | `'湖北省政府政策详情页落地; ...'` | `'辽宁省政府政策详情页落地 (hubei 槽 412×2 递补 per 649; per 650-A.0 P3-1 更正); ...'` | 同步 |
| h41 + h61 geo_entity.canonical_name (FK lookup) | `'湖北省'` | `'辽宁省'` | 同步（口径与 publisher 对齐）|
| lineage JSONB `original_province='hubei'` / `actual_province='liaoning'` | 保留 | 保留 | per 红线 13 增补: original_province 仅存 lineage JSONB; 不删行 |
| 文件末尾 尾注块 | (无) | 增补: `650-A.0 行内更正 尾注 (per 649 审计 P3-1 / 2026-09-01)` | 行内 append |

**红线 13 规范固化**（per 649 审计 P3-1）: **代换行 source_registry `province`/`source_name` 一律用 actual_province（URL 归属省），original_province 仅存 lineage JSONB**。本次 650 落地零 substitute（2 样本均原生 REACHABLE），故 seed_m4_13 全部行 province/source_name/publisher 字段均直接用 actual_province 口径（与 province 一致）。

### 2.4 已用省全集 (沿用 648 红线 + 649 + 650 增量)

| 类别 | 成员 |
|---|---|
| 已用省 (不得重复): | HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH |
| 649 增量: | HUBEI (substitute) + JILIN (直接) → substitute 实际抓取 LIAONING |
| **新进入** 已用省全集 (per 650 后): | **GUIZHOU / JIANGSU** (650 直接 REACHABLE; substitute 池 shaanxi/sichuan 备而未触发) |

### 2.5 替代不宣告条款

- docs/52 零改动（per 红线 12：registry 行 SHA 零漂移；本次 seed 增量落 staging 蓝本）
- 不宣告 substitute = 真实化（substitute 性质上跨域抓取 = 仅作 fallback；不宣布任意 M4.x "真实化 PASS"）
- 后续 651+ 若需 substitute，应再次登记 docs/74 §2 增量并保持代换行 provenance 透明（province/source_name 用 actual_province）
- 650 增量: docs/73 §6.1 已行内 append 登记 649 审计结果

---

## 3. M4.13 v7 spike 边界（vs 650 tasking 规划）

### 3.1 650 tasking 规划 vs 实测对比

**650 tasking 规划**：

- 沿用 649 fetch/seed 模式：**2 新样本**（≤12 total）
  - guizhou 首选: `https://www.guizhou.gov.cn/zwgk/`；fallback #1 `https://www.guizhou.gov.cn/`（省府根）
  - jiangsu 首选: `https://www.jiangsu.gov.cn/zwgk/`；fallback #1 `https://www.jiangsu.gov.cn/`（省府根）
  - 两级均 BLOCKED → 递补池按序 shaanxi → sichuan
- = **12 INSERT planned**（6 表 × 2 真实）
- + 2 source_registry + 2 source_document = **16 INSERT total**
- ≤12 HTTP total (2 cells × 1 HTTP each = 2-10 actual)
- chain_id='real_650_m4_13_policy_detail_v7' (末段 `_v7`，≠ 649 `_v6`)
- UUID prefix i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段
- 2 新 SHA 全 distinct ≠ 638-649 全部 SHA
- substitute 预授权池: shaanxi → sichuan (649 池减 2: guizhou/jiangsu 升格为原生 slot + liaoning 649 已用)

**650 实测反发现**：

- 2 真实样本落地（2 distinct SHA）：
  - guizhou 直接 `5c5b12952db6b4af8f63a8478100d1000765fcb8460f574dd8b480ce2aa56cc0` (guizhou /zwgk/ 200 REACHABLE; 170166 bytes) — 全新 SHA；与 638-649 全部 distinct
  - jiangsu fallback `def18a2f8f025b5ae11c685725b96cbf181c19c4771ab56d5d4be12974c7e534` (jiangsu /zwgk/ 404 → fallback / 200 REACHABLE; 82985 bytes) — 全新 SHA；与 638-649 全部 distinct
- 1 样本 /zwgk/ 直接 REACHABLE (guizhou)
- 1 样本 /zwgk/ 404 → fallback / 200 REACHABLE (jiangsu)
- **substitute 池按序 shaanxi → sichuan 备而未触发** (双样本均原生 REACHABLE; 实测 substitute_used_count=0)
- spike 边界 **实测 16 INSERT** = **规划 16 INSERT = 0 调整**
- **HTTP 实测 3/12 = 25% usage** (vs 649 6/12 = 50% usage; 本次更省)

### 3.2 625 fall-through chain 注记 (per knife 625 fall-through substitute policy)

| 样本 | 首选 /zwgk/ | fallback #1 (省府根) | substitute chain (递补池) |
|---|---|---|---|
| guizhou | **200 REACHABLE** (chain_index=0) | — | 备而未触发 (chain_index=0 直接命中; 无需 fallback/substitute) |
| jiangsu | 404 (Not Found) | **200 REACHABLE** (chain_index=1) | 备而未触发 (chain_index=1 fallback 命中; 无需 substitute) |

guizhou 走 1 级 chain (zwgk 200); jiangsu 走 2 级 chain (zwgk → /)。**总 HTTP 3/12** (guizhou 1 + jiangsu 2)。比 649 hubei 4 + jilin 2 = 6/12 更省。

### 3.3 spike 边界明细（16 INSERT total）

| 表 | 行数 | lineage.is_demo | UUID prefix | 区别 vs 649 |
|---|---|---|---|---|
| source_registry | 2 | `'false'` (NEW) | i0eebc99-...i02/i03 | 649 = h02/h03 |
| source_document | 2 | `'false'` (NEW) | i0eebc99-...i04/i05 | 649 = h04/h05 |
| policy_document | **2** | `'false'` (spike) | i1eebc99-...i11/i12 | 649 = h11/h12 |
| policy_target | **2** | `'false'` (spike) | i2eebc99-...i21/i22 | 649 = h21/h22 |
| policy_measure | **2** | `'false'` (spike) | i3eebc99-...i31/i32 | 649 = h31/h32 |
| government_commitment | **2** | `'false'` (spike) | i4eebc99-...i41/i42 | 649 = h41/h42 |
| commitment_progress | **2** | `'false'` (spike) | i5eebc99-...i51/i52 | 649 = h51/h52 |
| project_event | **2** | `'false'` (spike) | i6eebc99-...i61/i62 | 649 = h61/h62 |

**总计**：2 × 6 = **12 INSERT** (政策表) + 4 source = **16 INSERT total** ✓ 与 649 一致

### 3.4 真实样本 (2 distinct SHA → 2 用于 seed)

| 序号 | 试点省 | slot | URL | SHA (前 16) | file_size | 650 seed 用 | 备注 |
|---|---|---|---|---|---|---|---|
| **24** | **guizhou** | guizhou_zwgk_chain | `/zwgk/` (200) | `5c5b1295...` | 170,166 | ✓ | **全新 SHA (第 13 样本)** chain_index=0 直接 REACHABLE |
| **25** | **jiangsu** | jiangsu_zwgk_chain | `/zwgk/` (404) → `/` (200) | `def18a2f...` | 82,985 | ✓ | **全新 SHA (第 14 样本)** chain_index=1 fallback REACHABLE |

**2 SHA distinct vs 638-649 SHA**：

- 650 `5c5b1295` ≠ 649 `b22d1fb4 / a1e49a91` ≠ 648 `4006439e / a06e174f` ≠ 647 `8016ef08 / 56481050` ≠ 646 `fceb8c0a / 49eed23e` ≠ 645 `6237cd48 / dfa38998 / bd4c4c51 / f33eba53` ≠ 644 `bad8be51 / dfa38998 / f33eba53` ≠ 643 `e68099df / 63109491 / 93fe23b3` ≠ 642 `cd6aff30 / 4349ee0f / fede03ba` ≠ 641 `26e5379d...` ≠ 640 demo `0…02` ≠ 639 demo `0…01` ✓
- 650 `def18a2f` ≠ 全部 638-649 SHA ✓
- 2 SHA 全部 distinct ≠ 638-649 全部 SHA

---

## 4. lineage 真实化 sentinel + chain_id 区分 + 真实 SHA 区分表

### 4.1 13 真实化刀 lineage 沿用 (per docs/33 §3.2)

| 刀 | chain_id | is_demo | 试点省 | UUID prefix |
|---|---|---|---|---|
| 641 | `real_641_heilongjiang` | false | heilongjiang | real prefix |
| 642 | `real_642_m4_5_renmian` | false | henan/guangdong/guizhou | b 段 (b1-b6) |
| 643 | `real_643_m4_6_govreport` | false | hlj/henan/yunnan | c 段 (c41-c41) |
| 644 | `real_644_m4_7_policy_detail` | false | hlj/henan/yunnan | c 段 (c41-c93) |
| 645 | `real_645_m4_8_policy_detail_v2` | false | hlj/henan-zfgb/henan-zwgk/yunnan | d 段 (d21-d94) |
| 646 | `real_646_m4_9_policy_detail_v3` | false | fujian + guangdong | e 段 (e02-e62) |
| 647 | `real_647_m4_10_policy_detail_v4` | false | zhejiang + jiangxi (substitute) | f 段 (f02-f62) |
| 648 | `real_648_m4_11_policy_detail_v5` | false | hunan + anhui | g 段 (g02-g62) |
| 649 | `real_649_m4_12_policy_detail_v6` | false | hubei (→liaoning substitute) + jilin | h 段 (h02-h62) |
| **650** | **`real_650_m4_13_policy_detail_v7`** | **false** | **guizhou + jiangsu (双 REACHABLE, 无 substitute)** | **i 段 (i02-i62)** |

### 4.2 真实 SHA 区分表（2 新 SHA + 23 既有）

| 序号 | 刀 | 试点省 | URL | SHA (前 16) | 备注 |
|---|---|---|---|---|---|
| 1-18 | (沿用 638-647) | (略) | (略) | (略) | (见 docs/71 §4.2 / docs/72 §4.2 / docs/73 §4.2) |
| 19 | 638 (probe) | various | 23 试点省 | n/a (probe only) | 638 = `real_638_m4_1_people` chain_id 计入全链表 |
| 20 | 648 | hunan-zwgk-v5 | /zwgk/ (404) → / | `4006439e...` | chain_index=1 fallback |
| 21 | 648 | anhui-zwgk-v5 | /zwgk/ (timeout) → / | `a06e174f...` | chain_index=1 fallback |
| 22 | 649 | hubei→liaoning | /zwgk/ (412) → / (412) → ln /zwgk/ (404) → ln / (200) | `b22d1fb4...` | chain_index=3 substitute (per 650-A.0 P3-1 行内更正: province=LIAONING) |
| 23 | 649 | jilin-zwgk-v6 | /zwgk/ (timeout) → / | `a1e49a91...` | chain_index=1 fallback |
| **24** | **650** | **guizhou-zwgk-v7** | **/zwgk/ (200)** | **`5c5b1295...`** | **NEW 650 第 13 样本** chain_index=0 直接 REACHABLE |
| **25** | **650** | **jiangsu-zwgk-v7** | **/zwgk/ (404) → / (200)** | **`def18a2f...`** | **NEW 650 第 14 样本** chain_index=1 fallback REACHABLE |

**25 SHA 全部 distinct** (✓ 不撞 638-649)

### 4.3 UUID prefix 严格递增

```
demo → real → b → c → d → e → f → g (648) → h (649) → i (650)
638-640 demo + real  →  641 real  →  642 b1-b6  →  643 c1-c2  →  644 c1-c2  →  645 d21-d94  →  646 e02-e62  →  647 f02-f62  →  648 g02-g62  →  649 h02-h62  →  650 i02-i62
```

**650 i 段** (`i0eebc99` / `i1eebc99` / `i2eebc99` / `i3eebc99` / `i4eebc99` / `i5eebc99` / `i6eebc99`) **≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段 ≠ 643 c 段** ✓

### 4.4 649 substitute 预授权池状态更新

Per 649 §4.4 + 650 增量 substitute 状态:

| 池成员 | 状态 (649 后) | 状态 (650 后) | 备注 |
|---|---|---|---|
| **liaoning** | **✓ 649 激活** | ✓ 649 激活 | hubei 412+412 → ln /zwgk/ 404 → ln / 200 REACHABLE |
| shaanxi | 备而未触发 | 备而未触发 (优先级 1) | 留给 651+ |
| sichuan | 备而未触发 | 备而未触发 (优先级 2) | 留给 651+ |
| guizhou | 备而未触发 | ✓ **650 直接 REACHABLE** (chain_index=0) | guizhou /zwgk/ 200 |
| jiangsu | 备而未触发 | ✓ **650 fallback REACHABLE** (chain_index=1) | jiangsu /zwgk/ 404 → / 200 |

**已用省全集** (不得重复, 按 actual_province 口径): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL  
**649 增量**: HUBEI / JILIN / LIAONING (跨省 substitute 实际抓取)  
**650 增量**: GUIZHOU / JIANGSU (双直接 REACHABLE)  
**650 首选**: guizhou + jiangsu → 双样本均原生 REACHABLE (无 substitute 触发); HTTP 3/12 (25% usage)

### 4.5 650-A.4 evidence 落地（附属产物指针）

- ✓ `evidence_pack/m4_13_policy_detail_real_v7_20260901.json` (主 evidence; `summary.methodology` 含附属产物指针)
- ✓ `docs/reports/m4_13_policy_detail_real_v7_20260901.md` (附属 report; 主 evidence methodology 引用)
- ✓ 主 evidence `methodology` 字段: "Per 650 §0.13: 附属复验/验证产物允许独立文件, 但主 evidence methodology 必须含指针. 代换行 source_registry province/source_name 一律用 actual_province (per 649 P3-1)."

---

## 5. 651 下一步

### 5.1 651 候选 scope

- **scope A (推荐)**: 沿用 650 模式 + 递补池按序 shaanxi → sichuan（shaanxi/sichuan 任选 1-2 个 REACHABLE; substitute 池 651 触发优先级 1 = shaanxi, 优先级 2 = sichuan）— spike 第 10 次扩展；优先 1-2 个 REACHABLE + 1-2 个 substitute 验证双 pattern
- **scope B**: O1 B路 live-candidate 启用（per 646-A.2 data.stats.gov.cn PENDING_CANDIDATE → 等用户裁定启用）
- **scope C**: Gate 1 启动（M2 Gate 后才合法, 当前阻塞；沿用 646/647/648/649/650 §5）
- **scope D**: docs/45/50 spike 文档清空收口（沿用 M6 收口模式）
- **scope E**: 5W1H 分析 + 沿用 638-650 模式扩展（spec 推演）

### 5.2 当前未落地（红线守护）

- **Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M4.13 / M5 / M5.1 / M5.2 / M5.3 / M6** — 18 个里程碑不宣布 PASS
- O1 仍 OPEN (B路 live-candidate 仅登记, 不切换/启用)
- dbt mart flip: 60 行 demo 中仅 1 行（nanjing + CONDITION）真实化 pilot, O1 全量未启动
- 4 fixture 锁值永不动（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
- 不动 registry.csv / mart 既有 638-649 行
- 不写 cegr.* 生产表
- chain_id 区分: 650 '_v7' ≠ 649 '_v6' ≠ 648 '_v5' ≠ 647 '_v4' ≠ 646 '_v3' ≠ 645 '_v2' ≠ 644 '_policy_detail' ≠ 643 '_govreport' ≠ 642 '_renmian' ≠ 641 '_heilongjiang'
- UUID i 段 (i02-i62) ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段

---

## 6. 下一步 + 不宣称 PASS

**650 完成**:

- M4.13 政策详情 v7 真实化（2 样本 × 6 政策表 = 12 INSERT + 4 source = 16 INSERT total; chain_id='real_650_m4_13_policy_detail_v7'; UUID i 段; 2 NEW SHA: 5c5b1295/def18a2f; ≤12 HTTP total actual=3 (25%)）
- 649 审计 P3-1 蓝图更正落地: seed_m4_12 h02 行 province/source_name + h04/h11/h41/h51/h61 policy 表行 '湖北' 字样 + h41/h61 geo_entity FK lookup 同步更正为辽宁口径; 红线 13 规范固化: source_registry province/source_name 一律用 actual_province; lineage JSONB 内 original_province 仅作 provenance 留痕
- guizhou /zwgk/ 200 直接 REACHABLE (170166 bytes; SHA 5c5b1295...)
- jiangsu /zwgk/ 404 → fallback / 200 REACHABLE (82985 bytes; SHA def18a2f...)
- 递补池按序 shaanxi → sichuan 备而未触发（substitute_used_count=0）
- docs/73 §6.1 行内 append 登记 649 审计结果（PASS·有限通过 + P3-1 + P4×3 已修/登记）
- evidence_pack × 1 + docs/reports × 1 + docs/74 §1-§6 + docs/52 零改动 全部落地
- **≥106 pytest green** (M4.13 新 ≥8 + 649 回归 98)
- backfill 完整性三齐（per 649 审计 P3-2 + 650 任务书 §C）

**不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M4.13 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线）。

**O1 仍 OPEN** — B路 live-candidate 仅登记, 不切换/启用; 等用户/架构师裁定。

---

— End 74 — M4.13 v7 真实化 spike 审查 20260901 —