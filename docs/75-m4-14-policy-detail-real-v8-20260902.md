# 75 — M4.14 政策详情 v8 真实化 spike (架构师级审查)

> **刀号**: 651
> **Milestone**: M4.14（沿用 642/643/644/645/646/647/648/649/650 spike 模式；spike 第 10 次扩展；递补池收官）
> **类型**: 架构师级 §1-§6 审查文档
> **日期**: 2026-09-02
> **依据**:
> - `docs/74-m4-13-policy-detail-real-v7-20260901.md` (650 M4.13 政策详情 v7)
> - `reviews/stage0-gate0-rework-2026-08-23/650-audit-651-tasking-consolidated-20260902.md` (合并件: 650 审计 PASS·有限通过 + 651 任务书)
> - `651-stage0-architect-m4-14-v8-pool-depletion-tasking-20260902.md` (651 任务书 §1.651-A.0/A.1/A.2/A.3/A.4)
> **前置**: 650 DELIVERED + 审计 PASS（有限通过）+ 650 审计 P4×2 落地（docs/74 "sha anxi" typo + §4.4 口径尾注）
> **架构师综合**: 651 = A.0 650 审计 P4×2 行内更正 + 尾注（docs/74 §2.1 + §4.4 口径澄清）+ A.1 M4.14 v8 shaanxi/sichuan 16 INSERT（chain_id='real_651_m4_14_policy_detail_v8' UUID j 段; shaanxi /zwgk/ 404 → / 200 REACHABLE; sichuan /zwgk/ 403 WAF → / 200 REACHABLE; **递补池 [EXHAUSTED]** per 红线 14 增补, substitute_used=0; http_count=4/12）+ A.2 O1 零动作 + A.3 本文档 (docs/75) + A.4 evidence ×2 (含附属复验产物指针)
> **chain_id**: `real_651_m4_14_policy_detail_v8` (末段 `_v8` ≠ 650 `_v7` ≠ 649 `_v6` ≠ 648 `_v5` ≠ 647 `_v4` ≠ 646 `_v3` ≠ 645 `_v2`)
> **UUID prefix**: j 段 (j02-j62) ≠ 650 i 段 (i02-i62) ≠ 649 h 段 (h02-h62) ≠ 648 g 段 (g02-g62) ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段
> **递补池状态**: **EXHAUSTED [正式耗尽]**（per 651 §0.14 红线 14 增补; 649 激活 liaoning + 650 备而未触发 shaanxi/sichuan + 651 转正 shaanxi/sichuan → 池耗尽）
> **不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M6 PASS。

---

## 1. M4.14 v8 落地终态

| 子刀 | 文件 / 范围 | 状态 | 说明 |
|---|---|---|---|
| 651-A.0 | `docs/74-m4-13-policy-detail-real-v7-20260901.md` §2.1 + §2.4 + §4.4 行内 append 尾注 | DONE | per 650 审计 P4-1 (省名 typo) + P4-2 (槽名/actual_province 口径歧义); 不删既有正文; P4-1 grep "sha anxi" 残留 = 0 |
| 651-A.1 | `scripts/fetch_m4_14_policy_detail_v8_2024.py` + `scripts/seed_m4_14_policy_detail_real_v8.sql` + `evidence_pack/m4_14_policy_detail_real_v8_20260902.json` + `docs/reports/m4_14_policy_detail_real_v8_20260902.md` | DONE | M4.14 政策详情 v8 真实化；2 样本 (shaanxi + sichuan 第 15/16 样本) × 6 政策表 + 2 source_registry + 2 source_document = **16 INSERT**；shaanxi /zwgk/ 404 → / 200 REACHABLE (87956 bytes; SHA `9d0ad78a...`)；sichuan /zwgk/ 403 WAF → / 200 REACHABLE (100536 bytes; SHA `f58a3384...`)；substitute_used_count=0；**递补池 [EXHAUSTED]**（per 红线 14 增补；本次未触发也永不触发）；http_count=4/12 (33% usage) |
| 651-A.2 | O1 零动作（沿用 646/647/648/649/650 登记，O1 仍 OPEN） | DONE | 不新增 probe、不启用、不改 registry/connector；回执 O1 = OPEN |
| 651-A.3 | 本文档（docs/75） | DONE | §1-§6 架构师级审查；§2 含**递补池生命周期收官登记**（激活 1 次〔649 liaoning〕/ 备而未触发〔650〕/ 转正〔651〕/ **耗尽 + 红线 14 生效〔651 后〕**） |
| 651-A.4 | `docs/reports/m4_14_policy_detail_real_v8_20260902.md` + `evidence_pack/m4_14_policy_detail_real_v8_20260902.json` | DONE | evidence × 2；主 evidence methodology 含附属产物指针（per 648 审计 P3-1 口径统一条款 + 649 审计 P3-1 代换行标注规范固化入红线 13 + **651 红线 14 增补登记**） |

---

## 2. substitute 跨省代换登记 + 递补池生命周期收官 (per 649 任务书 §0.13 + 650 任务书 §0.13 + **651 任务书 §0.14 红线 14 增补**)

### 2.1 跨省 substitute 触发事实

Per 651 任务书 §0.14 红线 14 增补: **SUBSTITUTE_POOL 显式 [EXHAUSTED]**（递补池正式耗尽）。两级 fallback 全失败 → **BLOCKED_NO_POOL 留痕，不跨省代换**（不调用 substitute, evidence 记 `blocked_reason`，`substitute_used=false`）。

**651 触发事件**: **无 substitute 触发**（也不可能触发 — 池耗尽）。本次 2 样本 (shaanxi + sichuan) 均在原生 fallback chain #1 内 REACHABLE:

- shaanxi: `/zwgk/` 404 → fallback `/` 200 (chain_index=1 fallback REACHABLE)
- sichuan: `/zwgk/` 403 WAF → fallback `/` 200 (chain_index=1 fallback REACHABLE)

递补池 [EXHAUSTED] 备而**永不触发**（per 红线 14 增补: 651 后任一样本槽两级 fallback 全失败 → BLOCKED_NO_POOL 留痕，不再跨省代换）。

### 2.2 递补池生命周期收官登记 (per 651 §2.1 红线 14 收官)

| 阶段 | 状态 | 事件 |
|---|---|---|
| **649 阶段** | 递补池首次激活 | hubei 412+412 → 递补池 #1 liaoning /zwgk/ 404 → ln / 200 REACHABLE; substitute_used=1 (hubei→liaoning) |
| **650 阶段** | 备而未触发 | 650 首选 guizhou + jiangsu 均原生 fallback REACHABLE; 递补池按序 shaanxi → sichuan 备而未触发 (双原生 REACHABLE) |
| **651 阶段** | 收官转正 | 651 首选 shaanxi + sichuan (递补池前 #1/#2 候选 → 转正为原生首选 slot); 双样本 fallback #1 REACHABLE; substitute_used=0 |
| **651 后** | **EXHAUSTED [正式耗尽]** | 649 liaoning 激活 + 650 shaanxi/sichuan 备而未触发 + 651 shaanxi/sichuan 转正消耗 → 池清空; 红线 14 生效; 此后任一样本槽两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换 |

### 2.3 递补池成员最终状态

| 池成员 | 状态 (650 后) | 状态 (651 后) | 备注 |
|---|---|---|---|
| **liaoning** | ✓ 649 激活 | ✓ 649 激活（已 consumed） | hubei 412+412 → ln /zwgk/ 404 → ln / 200 REACHABLE |
| **shaanxi** | 备而未触发 | ✓ **651 转正首选** (chain_index=1 fallback REACHABLE) | shaanxi /zwgk/ 404 → / 200 (87956 bytes; SHA 9d0ad78a...) |
| **sichuan** | 备而未触发 | ✓ **651 转正首选** (chain_index=1 fallback REACHABLE) | sichuan /zwgk/ 403 WAF → / 200 (100536 bytes; SHA f58a3384...) |
| guizhou | ✓ 650 直接 REACHABLE | ✓ 650 直接 REACHABLE (chain_index=0) | guizhou /zwgk/ 200 (原生 slot; 非递补) |
| jiangsu | ✓ 650 fallback REACHABLE | ✓ 650 fallback REACHABLE (chain_index=1) | jiangsu /zwgk/ 404 → / 200 (原生 slot; 非递补) |

**递补池正式耗尽 [EXHAUSTED]**: 5 个原始池成员 (649 候选) 中:
- liaoning 已激活 (649)
- guizhou + jiangsu 升格为原生 slot (650)
- shaanxi + sichuan 转正消耗 (651)
- → **0 个剩余候选**; 红线 14 生效; 此后两级 fallback 全失败 → BLOCKED_NO_POOL 留痕

### 2.4 649 P3-1 蓝图更正 + 650 P4×2 行内更正 跨刀登记

**649 P3-1 + 650 蓝图更正**:
- h02 source_registry.province HUBEI→LIAONING + source_name 同步更正 + h04/h11/h41/h51/h61 policy 表行 '湖北' 字样同步更正 + h41/h61 geo_entity FK lookup 同步更正 + lineage JSONB provenance 留痕 (per 红线 13 增补)

**650 审计 P4×2** (per 651-A.0 落地):
- P4-1: docs/74 §2.1 "sha anxi" 行内更正为 "shaanxi" + 尾注 (650 编写笔误); grep "sha anxi" 残留 = 0
- P4-2: docs/74 §2.4 + §4.4 "649 增量" 行 append 尾注 (HUBEI 为槽名 consumed; actual_province=liaoning per 红线 13; 跨省 substitute 槽消耗 HUBEI → actual=LIAONING)

### 2.5 已用省全集 (沿用 648-650 红线 + 651 增量)

| 类别 | 成员 |
|---|---|
| 已用省 (不得重复): | HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH |
| 649 增量: | HUBEI (substitute 槽名 consumed) + JILIN (直接) + LIAONING (substitute 实际抓取) |
| 650 增量: | GUIZHOU / JIANGSU (双直接 REACHABLE) |
| **新进入** 已用省全集 (per 651 后): | **SHAANXI / SICHUAN** (651 fallback #1 REACHABLE) |

**总已用省 (实际抓取 actual_province 口径, 16 省)**: HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / **LN** / JL / GUIZHOU / JIANGSU / **SHAANXI / SICHUAN** = **15 省 + LN (substitute 抓取) = 16 省**  
（按 actual_province 计数; 不计 HUBEI 因 HUBEI 是 substitute 槽名, 非 actual 抓取省）

### 2.6 替代不宣告条款 (per 649/650 沿用 + 651 增补)

- docs/52 零改动（per 红线 12: registry 行 SHA 零漂移; 本次 seed 增量落 staging 蓝本）
- 不宣告 substitute = 真实化（substitute 性质上跨域抓取 = 仅作 fallback; 不宣布任意 M4.x "真实化 PASS"）
- 后续 652+ 若需 substitute → **[EXHAUSTED] 留痕**, 不跨省代换（per 红线 14 增补）
- 651 增量: docs/74 §2.1 + §2.4 + §4.4 已行内 append 尾注（per 650 审计 P4×2）

---

## 3. M4.14 v8 spike 边界（vs 651 tasking 规划）

### 3.1 651 tasking 规划 vs 实测对比

**651 tasking 规划**：

- 沿用 650 fetch/seed 模式：**2 新样本**（≤12 total）
  - shaanxi 首选: `https://www.shaanxi.gov.cn/zwgk/`；fallback #1 `https://www.shaanxi.gov.cn/`（省府根）
  - sichuan 首选: `https://www.sc.gov.cn/zwgk/`；fallback #1 `https://www.sc.gov.cn/`（省府根）
  - 两级均 BLOCKED → **无池可递补 → BLOCKED 留痕** (红线 14 首次执行)
- = **12 INSERT planned**（6 表 × 2 真实）
- + 2 source_registry + 2 source_document = **16 INSERT total**
- ≤12 HTTP total (2 cells × 1-2 HTTP each = 2-10 actual)
- chain_id='real_651_m4_14_policy_detail_v8' (末段 `_v8`，≠ 650 `_v7`)
- UUID prefix j 段 ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段
- 2 新 SHA 全 distinct ≠ 638-650 全部 SHA
- 递补池 (SUBSTITUTE_POOL) [EXHAUSTED] — 649 liaoning 已激活 + 650 备而未触发 + 651 转正 → 池耗尽

**651 实测反发现**：

- 2 真实样本落地（2 distinct SHA）：
  - shaanxi fallback `9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5` (shaanxi /zwgk/ 404 → / 200 REACHABLE; 87956 bytes) — 全新 SHA；与 638-650 全部 distinct
  - sichuan fallback `f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5` (sichuan /zwgk/ 403 WAF → / 200 REACHABLE; 100536 bytes) — 全新 SHA；与 638-650 全部 distinct
- 2 样本均 /zwgk/ 失败 (shaanxi 404 / sichuan 403 WAF) → fallback #1 / 200 REACHABLE
- **递补池 [EXHAUSTED] 永不触发** (双样本 fallback #1 命中; substitute_used_count=0; blocked_no_pool_count=0)
- spike 边界 **实测 16 INSERT** = **规划 16 INSERT = 0 调整**
- **HTTP 实测 4/12 = 33% usage** (vs 650 3/12 = 25% usage; vs 649 6/12 = 50% usage)

### 3.2 625 fall-through chain 注记 (per knife 625 fall-through substitute policy)

| 样本 | 首选 /zwgk/ | fallback #1 (省府根) | substitute chain (递补池) |
|---|---|---|---|
| shaanxi | 404 (Not Found) | **200 REACHABLE** (chain_index=1) | [EXHAUSTED] 永不触发 (per 红线 14 增补) |
| sichuan | 403 WAF (网防G01 marker) | **200 REACHABLE** (chain_index=1) | [EXHAUSTED] 永不触发 (per 红线 14 增补) |

shaanxi 走 2 级 chain (zwgk 404 → /); sichuan 走 2 级 chain (zwgk 403 WAF → /)。**总 HTTP 4/12** (shaanxi 2 + sichuan 2)。比 650 guizhou 1 + jiangsu 2 = 3/12 多 1 (shaanxi 双 fallback #1; jiangsu 仅 1 fallback #1 命中)。

### 3.3 spike 边界明细（16 INSERT total）

| 表 | 行数 | lineage.is_demo | UUID prefix | 区别 vs 650 |
|---|---|---|---|---|
| source_registry | 2 | `'false'` (NEW) | j0eebc99-...j02/j03 | 650 = i02/i03 |
| source_document | 2 | `'false'` (NEW) | j0eebc99-...j04/j05 | 650 = i04/i05 |
| policy_document | **2** | `'false'` (spike) | j1eebc99-...j11/j12 | 650 = i11/i12 |
| policy_target | **2** | `'false'` (spike) | j2eebc99-...j21/j22 | 650 = i21/i22 |
| policy_measure | **2** | `'false'` (spike) | j3eebc99-...j31/j32 | 650 = i31/i32 |
| government_commitment | **2** | `'false'` (spike) | j4eebc99-...j41/j42 | 650 = i41/i42 |
| commitment_progress | **2** | `'false'` (spike) | j5eebc99-...j51/j52 | 650 = i51/i52 |
| project_event | **2** | `'false'` (spike) | j6eebc99-...j61/j62 | 650 = i61/i62 |

**总计**：2 × 6 = **12 INSERT** (政策表) + 4 source = **16 INSERT total** ✓ 与 650 一致

### 3.4 真实样本 (2 distinct SHA → 2 用于 seed)

| 序号 | 试点省 | slot | URL | SHA (前 16) | file_size | 651 seed 用 | 备注 |
|---|---|---|---|---|---|---|---|
| **26** | **shaanxi** | shaanxi_zwgk_chain | `/zwgk/` (404) → `/` (200) | `9d0ad78a...` | 87,956 | ✓ | **全新 SHA (第 15 样本)** chain_index=1 fallback REACHABLE |
| **27** | **sichuan** | sichuan_zwgk_chain | `/zwgk/` (403 WAF) → `/` (200) | `f58a3384...` | 100,536 | ✓ | **全新 SHA (第 16 样本)** chain_index=1 fallback REACHABLE |

**2 SHA distinct vs 638-650 SHA**：

- 651 `9d0ad78a` ≠ 650 `5c5b1295 / def18a2f` ≠ 649 `b22d1fb4 / a1e49a91` ≠ 648 `4006439e / a06e174f` ≠ 647 `8016ef08 / 56481050` ≠ 646 `fceb8c0a / 49eed23e` ≠ 645 `6237cd48 / dfa38998 / bd4c4c51 / f33eba53` ≠ 644 `bad8be51 / dfa38998 / f33eba53` ≠ 643 `e68099df / 63109491 / 93fe23b3` ≠ 642 `cd6aff30 / 4349ee0f / fede03ba` ≠ 641 `26e5379d...` ≠ 640 demo `0…02` ≠ 639 demo `0…01` ✓
- 651 `f58a3384` ≠ 全部 638-650 SHA ✓
- 2 SHA 全部 distinct ≠ 638-650 全部 SHA

---

## 4. lineage 真实化 sentinel + chain_id 区分 + 真实 SHA 区分表

### 4.1 14 真实化刀 lineage 沿用 (per docs/33 §3.2)

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
| 650 | `real_650_m4_13_policy_detail_v7` | false | guizhou + jiangsu (双 REACHABLE, 无 substitute) | i 段 (i02-i62) |
| **651** | **`real_651_m4_14_policy_detail_v8`** | **false** | **shaanxi + sichuan (双 fallback #1 REACHABLE, 递补池 [EXHAUSTED])** | **j 段 (j02-j62)** |

### 4.2 真实 SHA 区分表（2 新 SHA + 25 既有）

| 序号 | 刀 | 试点省 | URL | SHA (前 16) | 备注 |
|---|---|---|---|---|---|
| 1-18 | (沿用 638-647) | (略) | (略) | (略) | (见 docs/71 §4.2 / docs/72 §4.2 / docs/73 §4.2) |
| 19 | 638 (probe) | various | 23 试点省 | n/a (probe only) | 638 = `real_638_m4_1_people` chain_id 计入全链表 |
| 20 | 648 | hunan-zwgk-v5 | /zwgk/ (404) → / | `4006439e...` | chain_index=1 fallback |
| 21 | 648 | anhui-zwgk-v5 | /zwgk/ (timeout) → / | `a06e174f...` | chain_index=1 fallback |
| 22 | 649 | hubei→liaoning | /zwgk/ (412) → / (412) → ln /zwgk/ (404) → ln / (200) | `b22d1fb4...` | chain_index=3 substitute (per 650-A.0 P3-1 行内更正: province=LIAONING) |
| 23 | 649 | jilin-zwgk-v6 | /zwgk/ (timeout) → / | `a1e49a91...` | chain_index=1 fallback |
| 24 | 650 | guizhou-zwgk-v7 | /zwgk/ (200) | `5c5b1295...` | chain_index=0 直接 REACHABLE |
| 25 | 650 | jiangsu-zwgk-v7 | /zwgk/ (404) → / (200) | `def18a2f...` | chain_index=1 fallback REACHABLE |
| **26** | **651** | **shaanxi-zwgk-v8** | **/zwgk/ (404) → / (200)** | **`9d0ad78a...`** | **NEW 651 第 15 样本** chain_index=1 fallback REACHABLE |
| **27** | **651** | **sichuan-zwgk-v8** | **/zwgk/ (403 WAF) → / (200)** | **`f58a3384...`** | **NEW 651 第 16 样本** chain_index=1 fallback REACHABLE |

**27 SHA 全部 distinct** (✓ 不撞 638-650)

### 4.3 UUID prefix 严格递增

```
demo → real → b → c → d → e → f → g (648) → h (649) → i (650) → j (651)
638-640 demo + real  →  641 real  →  642 b1-b6  →  643 c1-c2  →  644 c1-c2  →  645 d21-d94  →  646 e02-e62  →  647 f02-f62  →  648 g02-g62  →  649 h02-h62  →  650 i02-i62  →  651 j02-j62
```

**651 j 段** (`j0eebc99` / `j1eebc99` / `j2eebc99` / `j3eebc99` / `j4eebc99` / `j5eebc99` / `j6eebc99`) **≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段 ≠ 643 c 段** ✓

### 4.4 649 substitute 预授权池状态更新 (递补池收官)

Per 649 §4.4 + 650 增量 + **651 收官 + 红线 14 增补** substitute 状态:

| 池成员 | 状态 (649 后) | 状态 (650 后) | 状态 (651 后) | 备注 |
|---|---|---|---|---|
| **liaoning** | **✓ 649 激活** | ✓ 649 激活（已 consumed） | ✓ 649 激活（已 consumed） | hubei 412+412 → ln /zwgk/ 404 → ln / 200 REACHABLE |
| **shaanxi** | 备而未触发 | 备而未触发 (优先级 1) | ✓ **651 转正首选** (chain_index=1 fallback REACHABLE) | shaanxi /zwgk/ 404 → / 200 (87956 bytes) |
| **sichuan** | 备而未触发 | 备而未触发 (优先级 2) | ✓ **651 转正首选** (chain_index=1 fallback REACHABLE) | sichuan /zwgk/ 403 WAF → / 200 (100536 bytes) |
| guizhou | 备而未触发 | ✓ **650 直接 REACHABLE** (chain_index=0) | ✓ 650 直接 REACHABLE (chain_index=0) | guizhou /zwgk/ 200 |
| jiangsu | 备而未触发 | ✓ **650 fallback REACHABLE** (chain_index=1) | ✓ 650 fallback REACHABLE (chain_index=1) | jiangsu /zwgk/ 404 → / 200 |

**递补池正式耗尽 [EXHAUSTED]**: 5 个原始池成员 (649 候选) 全部落定 (liaoning 激活 + guizhou/jiangsu 升格 + shaanxi/sichuan 转正消耗); 池清空; **红线 14 生效**; 此后任一样本槽两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换。

**已用省全集** (不得重复, 按 actual_province 口径, 16 省): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL / GUIZHOU / JIANGSU / SHAANXI / SICHUAN  
**649 增量**: HUBEI (substitute 槽名 consumed) / JILIN / LIAONING (跨省 substitute 实际抓取)  
**650 增量**: GUIZHOU / JIANGSU (双直接 REACHABLE)  
**651 增量**: SHAANXI / SICHUAN (双 fallback #1 REACHABLE)  
**651 首选**: shaanxi + sichuan → 双样本 fallback #1 REACHABLE (无 substitute 触发); HTTP 4/12 (33% usage)

### 4.5 651-A.4 evidence 落地（附属产物指针）

- ✓ `evidence_pack/m4_14_policy_detail_real_v8_20260902.json` (主 evidence; `summary.methodology` 含附属产物指针)
- ✓ `docs/reports/m4_14_policy_detail_real_v8_20260902.md` (附属 report; 主 evidence methodology 引用)
- ✓ 主 evidence `methodology` 字段: "Per 650 §0.13: 附属复验/验证产物允许独立文件, 但主 evidence methodology 必须含指针. 代换行 source_registry province/source_name 一律用 actual_province (per 649 P3-1). Per 651 §0.14: BLOCKED_NO_POOL 留痕不代换. 递补池 [EXHAUSTED] 永不触发."
- ✓ 主 evidence `summary.substitute_pool_status = "EXHAUSTED"` (显式登记)

---

## 5. 后续 652+ BLOCKED 留痕口径

### 5.1 后续候选 scope

- **scope A (后续 652+ 推荐)**: 沿用 651 模式, 但**递补池 [EXHAUSTED]**, 任一样本槽两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换 (per 红线 14 增补)
- **scope B**: O1 B路 live-candidate 启用（per 646-A.2 data.stats.gov.cn PENDING_CANDIDATE → 等用户裁定启用）
- **scope C**: Gate 1 启动（M2 Gate 后才合法, 当前阻塞；沿用 646/647/648/649/650/651 §5）
- **scope D**: docs/45/50 spike 文档清空收口（沿用 M6 收口模式）
- **scope E**: 5W1H 分析 + 沿用 638-651 模式扩展（spec 推演）

### 5.2 当前未落地（红线守护）

- **Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M4.13 / M4.14 / M5 / M5.1 / M5.2 / M5.3 / M6** — 19 个里程碑不宣布 PASS
- O1 仍 OPEN (B路 live-candidate 仅登记, 不切换/启用)
- dbt mart flip: 60 行 demo 中仅 1 行（nanjing + CONDITION）真实化 pilot, O1 全量未启动
- 4 fixture 锁值永不动（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
- 不动 registry.csv / mart 既有 638-650 行
- 不写 cegr.* 生产表
- chain_id 区分: 651 '_v8' ≠ 650 '_v7' ≠ 649 '_v6' ≠ 648 '_v5' ≠ 647 '_v4' ≠ 646 '_v3' ≠ 645 '_v2' ≠ 644 '_policy_detail' ≠ 643 '_govreport' ≠ 642 '_renmian' ≠ 641 '_heilongjiang'
- UUID j 段 (j02-j62) ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段
- 递补池 [EXHAUSTED]: 后续两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换

---

## 6. 下一步 + 不宣称 PASS

**651 完成**:

- M4.14 政策详情 v8 真实化（2 样本 × 6 政策表 = 12 INSERT + 4 source = 16 INSERT total; chain_id='real_651_m4_14_policy_detail_v8'; UUID j 段; 2 NEW SHA: 9d0ad78a/f58a3384; ≤12 HTTP total actual=4 (33% usage)）
- 650 审计 P4×2 行内更正 + 尾注落地: docs/74 §2.1 "sha anxi" 行内更正; §2.4 + §4.4 "649 增量" 槽名/actual_province 口径歧义尾注; grep "sha anxi" 残留 = 0
- shaanxi /zwgk/ 404 → fallback / 200 REACHABLE (87956 bytes; SHA 9d0ad78a...)
- sichuan /zwgk/ 403 WAF → fallback / 200 REACHABLE (100536 bytes; SHA f58a3384...)
- **递补池正式耗尽 [EXHAUSTED]**（649 激活 liaoning + 650 备而未触发 + 651 转正 shaanxi/sichuan → 池耗尽）; substitute_used_count=0; blocked_no_pool_count=0
- docs/74 §2.1 + §2.4 + §4.4 行内 append 尾注（P4-1 typo 更正 + P4-2 槽名/actual 口径澄清）
- evidence_pack × 1 + docs/reports × 1 + docs/75 §1-§6 + docs/52 零改动 全部落地
- **≥126 pytest green** (M4.14 新 ≥8 + 650 回归 118)
- backfill 完整性三齐（per 650 审计 P4 + 651 任务书 §C）

**不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M4.13 / M4.14 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线）。

**O1 仍 OPEN** — B路 live-candidate 仅登记, 不切换/启用; 等用户/架构师裁定。

> **[per 652-A.0 P4×2 规范固化 / 2026-09-02]:** 651 审计定案 PASS（有限通过）+ 2×P4 教训沉淀:
> - **P4-1** — rev88 §CURRENT status 行 pin 中间 SHA `eb6b012`（vs 终态 HEAD=`8ae20de`），陈旧；**规范固化**: status/§CURRENT/§NOW 措辞**不 pin 中间 SHA**, 仅以"三 ref 全等 + 最终 HEAD"表述（commit 末尾 ref 即可; 中间 SHA 一律不入 status 文本）。同类: 649 P4 自指陈旧模式的轻量复发。
> - **P4-2** — cc_head 链错录 amend 孤儿 SHA `ea64640`（`git log NOT_IN_HISTORY`; 与真实 `eb6b012` 同信息差 9 秒, 是 amend 前的占位 commit, 已 `git commit --amend` 替换）。**规范固化**: cc_head 链 SHA 一律 `git log --format=%H -n <n>` 实测, 严禁凭"应该会变成"推理; receipt-backfill 阶段的 amend 操作必须**先 amend 完成后再写链文本**（或先 `git log` 取 SHA 再 amend）。
> - **O-1 预测命中**: 审验端复跑后 m2 crosscheck 报告 4+/4- churn → `git checkout HEAD -- docs/reports/m2_2024_gdp_crosscheck_20260831.md` 即还原（持续观察第 2 次命中）; 加固建议仍开放: crosscheck 测试 tmpdir isolation。
> - **O-2 未复发**: 650 幽灵并发 flake 本刀未复发（任务书集合首跑 144 全绿），关闭观察。

---

— End 75 — M4.14 v8 真实化 spike 审查 20260902 —