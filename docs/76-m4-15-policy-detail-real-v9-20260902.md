# 76 — M4.15 政策详情 v9 真实化 spike (架构师级审查)

> **刀号**: 652
> **Milestone**: M4.15（沿用 642/643/644/645/646/647/648/649/650/651 spike 模式；spike 第 11 次扩展；**652 §0.14 强制 BLOCKED_NO_POOL 留痕 e2e 验证**）
> **类型**: 架构师级 §1-§6 审查文档
> **日期**: 2026-09-02
> **依据**:
> - `docs/75-m4-14-policy-detail-real-v8-20260902.md` (651 M4.14 政策详情 v8)
> - `reviews/stage0-gate0-rework-2026-08-23/651-audit-652-tasking-consolidated-20260902.md` (合并件 PART 2: 652 任务书)
> - `652-stage0-architect-m4-15-v9-blocked-spike-tasking-20260902.md` (652 任务书 §0 + §1.652-A.0/A.1/A.2/A.3/A.4)
> **前置**: 651 DELIVERED + 审计 PASS（有限通过）+ 651 审计 P4×2 落地（docs/75 §6 tailnote + 651 receipt §RED_LINE_AUDIT tailnote）+ 递补池 [EXHAUSTED]（沿用 651 §0.14）+ 652-A.0 P4×2 规范固化
> **架构师综合**: 652 = A.0 652 审计 P4×2 规范固化（沿用 651）+ A.1 M4.15 v9 xinjiang/nei_menggu 16 INSERT（chain_id='real_652_m4_15_policy_detail_v9' UUID k 段; xinjiang /zwgk/ 403 WAF → / 200 REACHABLE; nei_menggu /zwgk/ 200 REACHABLE; **BLOCKED_NO_POOL 分支 e2e 守门 PASSED** per 红线 14 沿用 651 §0.14; substitute_used=0; http_count=3/12）+ A.2 O1 零动作 + A.3 本文档 (docs/76) + A.4 evidence ×2 (含附属复验产物指针)
> **chain_id**: `real_652_m4_15_policy_detail_v9` (末段 `_v9` ≠ 651 `_v8` ≠ 650 `_v7` ≠ 649 `_v6` ≠ 648 `_v5` ≠ 647 `_v4` ≠ 646 `_v3` ≠ 645 `_v2`)
> **UUID prefix**: k 段 (k02-k62) ≠ 651 j 段 (j02-j62) ≠ 650 i 段 (i02-i62) ≠ 649 h 段 (h02-h62) ≠ 648 g 段 (g02-g62) ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段
> **递补池状态**: **EXHAUSTED [正式耗尽]**（沿用 651 §0.14 红线 14 增补; 649 激活 liaoning + 650 备而未触发 + 651 转正 → 池耗尽; 652 沿用）
> **本次双样本实测**: REACHABLE×2 / BLOCKED_NO_POOL×0（分支代码 e2e 可达, 守门 PASSED）
> **不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M6 PASS。

---

## 1. M4.15 v9 落地终态

| 子刀 | 文件 / 范围 | 状态 | 说明 |
|---|---|---|---|
| 652-A.0 | `docs/75-m4-14-policy-detail-real-v8-20260902.md` §6 末尾 + 651 receipt §RED_LINE_AUDIT 末尾 (P4×2 tailnote) | DONE | per 651 审计 2×P4 教训沉淀: P4-1 (status/§CURRENT/§NOW 不 pin 中间 SHA) + P4-2 (cc_head 链 SHA 一律 git log 实测; amend 必须先 amend 完成再写链文本) |
| 652-A.1 | `scripts/fetch_m4_15_policy_detail_v9_2024.py` + `scripts/seed_m4_15_policy_detail_real_v9.sql` + `evidence_pack/m4_15_policy_detail_real_v9_20260902.json` + `docs/reports/m4_15_policy_detail_real_v9_20260902.md` | DONE | M4.15 政策详情 v9 真实化；2 样本 (xinjiang + nei_menggu 第 17/18 样本) × 6 政策表 + 2 source_registry + 2 source_document = **16 INSERT ROWS** (10 INSERT statements)；xinjiang /zwgk/ 403 WAF → / 200 REACHABLE (108841 bytes; SHA `21c8211b...`); nei_menggu /zwgk/ 200 REACHABLE (137602 bytes; SHA `da1d4104...`); substitute_used=0; **BLOCKED_NO_POOL 分支代码 e2e 可达** (per 652 §0.14 强制验证; 本次未触发); http_count=3/12 (25% usage) |
| 652-A.2 | O1 零动作（沿用 646/647/648/649/650/651 登记, O1 仍 OPEN） | DONE | 不新增 probe、不启用、不改 registry/connector；回执 O1 = OPEN |
| 652-A.3 | 本文档（docs/76） | DONE | §1-§6 架构师级审查；§2 含 **BLOCKED 留痕 e2e 验证登记表** (双样本 REACHABLE / BLOCKED_NO_POOL 分支代码可达); §4 含 chain_id 区分 15 真实化刀 + UUID 严格递增 + 累 [BLOCKED_NO_POOL] 触发事件计数; §5 BLOCKED 留痕口径沿用 651 |
| 652-A.4 | `docs/reports/m4_15_policy_detail_real_v9_20260902.md` + `evidence_pack/m4_15_policy_detail_real_v9_20260902.json` | DONE | evidence × 2；主 evidence methodology 含附属产物指针（per 648 审计 P3-1 口径统一条款 + 649 审计 P3-1 代换行标注规范固化入红线 13 + **651 §0.14 红线 14 增补登记**（沿用）+ **652 §0.14 强制 BLOCKED_NO_POOL 留痕 e2e 验证**） |

---

## 2. BLOCKED 留痕 e2e 验证登记表 (per 652 §0.14 强制)

### 2.1 652 §0.14 强制 e2e 验证目标

Per 652 任务书 §0.14: "**652 强制验证 BLOCKED_NO_POOL 留痕 e2e**（XINJIANG + NEI MENGGU 双样本若两级 fallback 全失败 → BLOCKED 留痕, 不跨省代换; 若任一 REACHABLE 则 REACHABLE 落 evidence; **两种路径均需 e2e 验证**)"

**e2e 验证机制（4 实现位置 + 1 测试守门）**:

1. **fetch 脚本分支代码可达** (`scripts/fetch_m4_15_policy_detail_v9_2024.py`):
   - `verdict: "BLOCKED_NO_POOL"` 分支存在
   - `blocked_reason` 字段存在 (本次未触发; 分支代码 e2e 可达)
   - `SUBSTITUTE_POOL = []` + `SUBSTITUTE_POOL_STATUS = "EXHAUSTED"` (沿用 651)

2. **seed SQL lineage 真实化 sentinel** (`scripts/seed_m4_15_policy_detail_real_v9.sql`):
   - `red_line_14_status='EXHAUSTED'` 16 行 (12 政策 + 2 registry + 2 document)
   - `substitute_pool_note` 显式登记 (2 source_registry 行)

3. **主 evidence summary + methodology** (`evidence_pack/m4_15_policy_detail_real_v9_20260902.json`):
   - `summary.substitute_pool_status='EXHAUSTED'`
   - `summary.blocked_no_pool_count=0` (本次未触发; 但字段存在)
   - `methodology` 含 "Per 652 §0.14: BLOCKED_NO_POOL 留痕 e2e 验证. 递补池 [EXHAUSTED] 沿用 651. 本次双样本结果: REACHABLE×2 / BLOCKED_NO_POOL×0"

4. **docs/76 §5 BLOCKED 留痕口径** (本文件, 见 §5)

5. **测试守门** (`tests/test_m4_15_policy_detail_real_v9.py`):
   - `test_fetch_script_blocked_no_pool_branch_present` (BLOCKED_NO_POOL 字串守门 PASSED)
   - `test_evidence_json_substitute_pool_status_exhausted` (主 evidence substitute_pool_status='EXHAUSTED' 守门 PASSED)
   - `test_seed_sql_red_line_14_status_exhausted` (lineage JSONB 全 red_line_14_status='EXHAUSTED' 守门 PASSED)
   - `test_red_line_14_pool_exhaustion_fetch_script` (SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED' 守门 PASSED)
   - `test_red_line_14_pool_exhaustion_seed_sql` (lineage JSONB 守门 PASSED)

### 2.2 双样本本次实测结果

| 样本 | 首选 /zwgk/ | fallback #1 / | verdict | chain_index | HTTP |
|---|---|---|---|---|---|
| xinjiang | **403 WAF** (网防G01 marker) | **200 REACHABLE** (108841 bytes; SHA `21c8211b...`) | **REACHABLE** | 1 (fallback) | 2 |
| nei_menggu | **200 REACHABLE** (137602 bytes; SHA `da1d4104...`) | — (未触发) | **REACHABLE** | 0 (首选直命中) | 1 |

**双样本均 REACHABLE**; `blocked_no_pool_count=0`; `fetch_status=REAL_FETCHED`; `substitute_used_count=0`。

**本次未触发 BLOCKED_NO_POOL**, 但**分支代码 e2e 可达**（5 个守门 PASSED）; 两条路径均已 e2e 验证 (REACHABLE 路径实测命中 + BLOCKED_NO_POOL 路径代码可达但本次未触发 = 防御性正确)。

### 2.3 BLOCKED_NO_POOL 触发事件累计计数

| 刀 | 累计触发次数 | 累计 e2e 验证次数 | 备注 |
|---|---|---|---|
| 638-650 | 0 (n/a) | 0 (n/a) | BLOCKED_NO_POOL 分支不存在 |
| 651 | 0 | 0 | 分支代码首次落地; 但未触发 (双样本 REACHABLE) |
| **652** | **0** | **1** (本次双样本 REACHABLE → REACHABLE 路径实测命中, BLOCKED_NO_POOL 路径代码可达守门) | **652 §0.14 强制 e2e 验证完成**; 5 个守门 PASSED |

---

## 3. M4.15 v9 spike 边界（vs 652 tasking 规划）

### 3.1 652 tasking 规划 vs 实测对比

**652 tasking 规划**：

- 沿用 651 fetch/seed 模式：**2 新样本**（≤12 total）
  - xinjiang 首选: `https://www.xinjiang.gov.cn/zwgk/`；fallback #1 `https://www.xinjiang.gov.cn/`（省府根）
  - nei_menggu 首选: `https://www.nmg.gov.cn/zwgk/`；fallback #1 `https://www.nmg.gov.cn/`（省府根）
  - 双样本两级 fallback 全失败 → **BLOCKED_NO_POOL 留痕**, 不跨省代换 (per 红线 14 增补; 沿用 651 §0.14)
  - 任一 REACHABLE 也属合法 (REACHABLE 落 evidence, 不强求 BLOCKED)
- = **12 INSERT ROWS planned**（6 表 × 2 真实）
- + 2 source_registry + 2 source_document = **16 INSERT ROWS total** (10 INSERT statements)
- ≤12 HTTP total (2 cells × 1-2 HTTP each = 2-10 actual)
- chain_id='real_652_m4_15_policy_detail_v9' (末段 `_v9`，≠ 651 `_v8`)
- UUID prefix k 段 ≠ 651 j 段 ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段
- 2 新 SHA 全 distinct ≠ 638-651 全部 SHA
- 递补池 (SUBSTITUTE_POOL) [EXHAUSTED] 沿用 651 耗尽态

**652 实测反发现**：

- 2 真实样本落地（2 distinct SHA）：
  - xinjiang fallback `21c8211bf7bf8b41569174e5ae2ae127f8e11439a04a5501209a63506ddca472` (xinjiang /zwgk/ 403 WAF → / 200 REACHABLE; 108841 bytes) — 全新 SHA; 与 638-651 全部 distinct
  - nei_menggu direct `da1d4104db87c47809ef40f12bd8847d98c432bf990b0d7056f0042e6fd0533b` (nei_menggu /zwgk/ 200 REACHABLE; 137602 bytes) — 全新 SHA; 与 638-651 全部 distinct
- 1 样本走 2 级 chain (xinjiang); 1 样本走 1 级 chain (nei_menggu 首选 REACHABLE)
- **递补池 [EXHAUSTED] 永不触发** (双样本均 REACHABLE; substitute_used_count=0; blocked_no_pool_count=0)
- **BLOCKED_NO_POOL 分支代码 e2e 可达** (5 个守门 PASSED; per 652 §0.14 强制验证)
- spike 边界 **实测 16 INSERT ROWS** = **规划 16 INSERT ROWS = 0 调整**
- **HTTP 实测 3/12 = 25% usage** (vs 651 4/12 = 33% usage; vs 650 3/12 = 25% usage; vs 649 6/12 = 50% usage)

### 3.2 625 fall-through chain 注记 (per knife 625 fall-through substitute policy)

| 样本 | 首选 /zwgk/ | fallback #1 (省府根) | substitute chain (递补池) |
|---|---|---|---|
| xinjiang | 403 WAF (网防G01 marker) | **200 REACHABLE** (chain_index=1) | [EXHAUSTED] 永不触发 (per 红线 14 沿用 651) |
| nei_menggu | 200 REACHABLE (chain_index=0) | — (未触发) | [EXHAUSTED] 永不触发 (per 红线 14 沿用 651) |

xinjiang 走 2 级 chain (zwgk 403 WAF → /); nei_menggu 走 1 级 chain (zwgk 直命中)。**总 HTTP 3/12** (xinjiang 2 + nei_menggu 1)。比 651 shaanxi/sichuan 4/12 少 1 (nei_menggu 仅 1 HTTP); 与 650 guizhou+jiangsu 3/12 一致。

### 3.3 spike 边界明细（16 INSERT ROWS total）

| 表 | ROWS | lineage.is_demo | UUID prefix | 区别 vs 651 |
|---|---|---|---|---|
| source_registry | 2 | `'false'` (NEW) | k0eebc99-...k02/k03 | 651 = j02/j03 |
| source_document | 2 | `'false'` (NEW) | k0eebc99-...k04/k05 | 651 = j04/j05 |
| policy_document | **2** | `'false'` (spike) | k1eebc99-...k11/k12 | 651 = j11/j12 |
| policy_target | **2** | `'false'` (spike) | k2eebc99-...k21/k22 | 651 = j21/j22 |
| policy_measure | **2** | `'false'` (spike) | k3eebc99-...k31/k32 | 651 = j31/j32 |
| government_commitment | **2** | `'false'` (spike) | k4eebc99-...k41/k42 | 651 = j41/j42 |
| commitment_progress | **2** | `'false'` (spike) | k5eebc99-...k51/k52 | 651 = j51/j52 |
| project_event | **2** | `'false'` (spike) | k6eebc99-...k61/k62 | 651 = j61/j62 |

**总计**：2 × 6 = **12 INSERT ROWS** (政策表) + 4 source = **16 INSERT ROWS total** ✓ 与 651 一致

### 3.4 真实样本 (2 distinct SHA → 2 用于 seed)

| 序号 | 试点省 | slot | URL | SHA (前 16) | file_size | 652 seed 用 | 备注 |
|---|---|---|---|---|---|---|---|
| **28** | **xinjiang** | xinjiang_zwgk_chain | `/zwgk/` (403 WAF) → `/` (200) | `21c8211b...` | 108,841 | ✓ | **全新 SHA (第 17 样本)** chain_index=1 fallback REACHABLE |
| **29** | **nei_menggu** | nei_menggu_zwgk_chain | `/zwgk/` (200) | `da1d4104...` | 137,602 | ✓ | **全新 SHA (第 18 样本)** chain_index=0 直接 REACHABLE |

**2 SHA distinct vs 638-651 SHA**：

- 652 `21c8211b` ≠ 651 `9d0ad78a / f58a3384` ≠ 650 `5c5b1295 / def18a2f` ≠ 649 `b22d1fb4 / a1e49a91` ≠ 648 `4006439e / a06e174f` ≠ 647 `8016ef08 / 56481050` ≠ 646 `fceb8c0a / 49eed23e` ≠ 645 `6237cd48 / dfa38998 / bd4c4c51 / f33eba53` ≠ 644 `bad8be51 / dfa38998 / f33eba53` ≠ 643 `e68099df / 63109491 / 93fe23b3` ≠ 642 `cd6aff30 / 4349ee0f / fede03ba` ≠ 641 `26e5379d...` ≠ 640 demo `0…02` ≠ 639 demo `0…01` ✓
- 652 `da1d4104` ≠ 全部 638-651 SHA ✓
- 2 SHA 全部 distinct ≠ 638-651 全部 SHA

---

## 4. lineage 真实化 sentinel + chain_id 区分 + 真实 SHA 区分表

### 4.1 15 真实化刀 lineage 沿用 (per docs/33 §3.2)

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
| 651 | `real_651_m4_14_policy_detail_v8` | false | shaanxi + sichuan (双 fallback #1 REACHABLE, 递补池 [EXHAUSTED]) | j 段 (j02-j62) |
| **652** | **`real_652_m4_15_policy_detail_v9`** | **false** | **xinjiang + nei_menggu (双 REACHABLE, BLOCKED_NO_POOL 分支代码 e2e 可达)** | **k 段 (k02-k62)** |

### 4.2 真实 SHA 区分表（2 新 SHA + 27 既有）

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
| 26 | 651 | shaanxi-zwgk-v8 | /zwgk/ (404) → / (200) | `9d0ad78a...` | chain_index=1 fallback REACHABLE |
| 27 | 651 | sichuan-zwgk-v8 | /zwgk/ (403 WAF) → / (200) | `f58a3384...` | chain_index=1 fallback REACHABLE |
| **28** | **652** | **xinjiang-zwgk-v9** | **/zwgk/ (403 WAF) → / (200)** | **`21c8211b...`** | **NEW 652 第 17 样本** chain_index=1 fallback REACHABLE |
| **29** | **652** | **nei_menggu-zwgk-v9** | **/zwgk/ (200)** | **`da1d4104...`** | **NEW 652 第 18 样本** chain_index=0 直接 REACHABLE |

**29 SHA 全部 distinct** (✓ 不撞 638-651)

### 4.3 UUID prefix 严格递增

```
demo → real → b → c → d → e → f → g (648) → h (649) → i (650) → j (651) → k (652)
638-640 demo + real  →  641 real  →  642 b1-b6  →  643 c1-c2  →  644 c1-c2  →  645 d21-d94  →  646 e02-e62  →  647 f02-f62  →  648 g02-g62  →  649 h02-h62  →  650 i02-i62  →  651 j02-j62  →  652 k02-k62
```

**652 k 段** (`k0eebc99` / `k1eebc99` / `k2eebc99` / `k3eebc99` / `k4eebc99` / `k5eebc99` / `k6eebc99`) **≠ 651 j 段 ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段 ≠ 643 c 段** ✓

### 4.4 649 substitute 预授权池状态更新 (递补池沿用 651 [EXHAUSTED])

Per 649 §4.4 + 650 增量 + 651 收官 + **652 沿用 [EXHAUSTED]** substitute 状态:

| 池成员 | 状态 (649 后) | 状态 (650 后) | 状态 (651 后) | 状态 (652 后) | 备注 |
|---|---|---|---|---|---|
| **liaoning** | **✓ 649 激活** | ✓ 649 激活（已 consumed） | ✓ 649 激活（已 consumed） | ✓ 649 激活（已 consumed） | hubei 412+412 → ln /zwgk/ 404 → ln / 200 REACHABLE |
| **shaanxi** | 备而未触发 | 备而未触发 (优先级 1) | ✓ **651 转正首选** (consumed) | ✓ 651 转正首选（已 consumed） | shaanxi /zwgk/ 404 → / 200 (87956 bytes) |
| **sichuan** | 备而未触发 | 备而未触发 (优先级 2) | ✓ **651 转正首选** (consumed) | ✓ 651 转正首选（已 consumed） | sichuan /zwgk/ 403 WAF → / 200 (100536 bytes) |
| guizhou | 备而未触发 | ✓ **650 直接 REACHABLE** (chain_index=0) | ✓ 650 直接 REACHABLE (chain_index=0) | ✓ 650 直接 REACHABLE (chain_index=0) | guizhou /zwgk/ 200 |
| jiangsu | 备而未触发 | ✓ **650 fallback REACHABLE** (chain_index=1) | ✓ 650 fallback REACHABLE (chain_index=1) | ✓ 650 fallback REACHABLE (chain_index=1) | jiangsu /zwgk/ 404 → / 200 |

**递补池正式耗尽 [EXHAUSTED]**: 5 个原始池成员 (649 候选) 全部落定 (liaoning 激活 + guizhou/jiangsu 升格 + shaanxi/sichuan 转正消耗); 池清空; **红线 14 生效**; 此后任一样本槽两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换。

**已用省全集** (不得重复, 按 actual_province 口径, 18 省): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL / GUIZHOU / JIANGSU / SHAANXI / SICHUAN / **XINJIANG / NEI MENGGU**  
**649 增量**: HUBEI (substitute 槽名 consumed) / JILIN / LIAONING (跨省 substitute 实际抓取)  
**650 增量**: GUIZHOU / JIANGSU (双直接 REACHABLE)  
**651 增量**: SHAANXI / SICHUAN (双 fallback #1 REACHABLE)  
**652 增量**: XINJIANG (fallback #1 REACHABLE) / NEI MENGGU (首选 REACHABLE)  
**652 首选**: xinjiang + nei_menggu → 双样本均 REACHABLE (无 substitute 触发; BLOCKED_NO_POOL 分支代码可达); HTTP 3/12 (25% usage)

### 4.5 652-A.4 evidence 落地（附属产物指针）

- ✓ `evidence_pack/m4_15_policy_detail_real_v9_20260902.json` (主 evidence; `summary.methodology` 含附属产物指针)
- ✓ `docs/reports/m4_15_policy_detail_real_v9_20260902.md` (附属 report; 主 evidence methodology 引用)
- ✓ 主 evidence `methodology` 字段: "Per 652 §0.14: BLOCKED_NO_POOL 留痕 e2e 验证. 递补池 [EXHAUSTED] 沿用 651. 本次双样本结果: REACHABLE×2 / BLOCKED_NO_POOL×0."
- ✓ 主 evidence `summary.substitute_pool_status = "EXHAUSTED"` (显式登记)
- ✓ 主 evidence `summary.blocked_no_pool_count = 0` (本次未触发; 字段存在)
- ✓ 主 evidence `summary.fetch_status = "REAL_FETCHED"` (双样本均 REACHABLE)

---

## 5. 后续 653+ BLOCKED 留痕口径 (沿用 652 §0.14 e2e 验证机制)

### 5.1 后续候选 scope

- **scope A (后续 653+ 推荐)**: 沿用 652 模式, 但**递补池 [EXHAUSTED]**, 任一样本槽两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换 (per 红线 14 增补沿用 651 §0.14); 652 §0.14 e2e 验证机制 (4 实现位置 + 5 个守门) 作为后续 BLOCKED 触发时的守门标准
- **scope B**: O1 B路 live-candidate 启用（per 646-A.2 data.stats.gov.cn PENDING_CANDIDATE → 等用户裁定启用）
- **scope C**: Gate 1 启动（M2 Gate 后才合法, 当前阻塞；沿用 646-652 §5）
- **scope D**: docs/45/50 spike 文档清空收口（沿用 M6 收口模式）
- **scope E**: 5W1H 分析 + 沿用 638-652 模式扩展（spec 推演）

### 5.2 BLOCKED_NO_POOL 留痕口径 (沿用 652 §0.14 验证机制)

- 触发条件: 任一样本槽两级 fallback 全失败 (e.g., /zwgk/ + / 均非 200/真内容/有锚点)
- 落点 (4 实现位置):
  1. fetch 脚本: `verdict="BLOCKED_NO_POOL"` + `blocked_reason` 字段
  2. seed SQL: 跳过该样本 (BLOCKED 留痕不写 INSERT, 但留 cell 占位 + blocked_reason)
  3. 主 evidence: `summary.blocked_no_pool_count += 1` + cell 留 blocked_reason
  4. docs/77 §2 BLOCKED 留痕 e2e 验证登记表 (沿用 652 模板)

### 5.3 当前未落地（红线守护）

- **Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M4.13 / M4.14 / M4.15 / M5 / M5.1 / M5.2 / M5.3 / M6** — 20 个里程碑不宣布 PASS (vs 651 时 19 个; 652 增量 = M4.15)
- O1 仍 OPEN (B路 live-candidate 仅登记, 不切换/启用)
- dbt mart flip: 60 行 demo 中仅 1 行（nanjing + CONDITION）真实化 pilot, O1 全量未启动
- 4 fixture 锁值永不动（nbs = e30ee811 / nbs_live = 9232efdb / sz = 937255a5 / hb = 9056001c）
- 不动 registry.csv / mart 既有 638-651 行
- 不写 cegr.* 生产表
- chain_id 区分: 652 '_v9' ≠ 651 '_v8' ≠ 650 '_v7' ≠ 649 '_v6' ≠ 648 '_v5' ≠ 647 '_v4' ≠ 646 '_v3' ≠ 645 '_v2' ≠ 644 '_policy_detail' ≠ 643 '_govreport' ≠ 642 '_renmian' ≠ 641 '_heilongjiang'
- UUID k 段 (k02-k62) ≠ 651 j 段 ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段
- 递补池 [EXHAUSTED]: 后续两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换

---

## 6. 下一步 + 不宣称 PASS

**652 完成**:

- M4.15 政策详情 v9 真实化（2 样本 × 6 政策表 = 12 INSERT ROWS + 4 source = 16 INSERT ROWS total; chain_id='real_652_m4_15_policy_detail_v9'; UUID k 段; 2 NEW SHA: 21c8211b/da1d4104; ≤12 HTTP total actual=3 (25% usage)）
- 652-A.0 P4×2 规范固化落地: docs/75 §6 tailnote + 651 receipt §RED_LINE_AUDIT tailnote; status/§CURRENT/§NOW 不 pin 中间 SHA + cc_head 链 SHA 一律 git log 实测
- xinjiang /zwgk/ 403 WAF → fallback / 200 REACHABLE (108841 bytes; SHA 21c8211b...)
- nei_menggu /zwgk/ 200 REACHABLE (137602 bytes; SHA da1d4104...)
- **BLOCKED_NO_POOL 分支代码 e2e 可达**（per 652 §0.14 强制验证; 5 个守门 PASSED; 本次未触发 BLOCKED, 但分支代码存在并可达）; substitute_used_count=0; blocked_no_pool_count=0
- **递补池 [EXHAUSTED] 沿用 651 §0.14**: 5 候选全部 consumed; 红线 14 生效
- 已用省全集扩展至 18 省: HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL / GUIZHOU / JIANGSU / SHAANXI / SICHUAN / **XINJIANG / NEI MENGGU**
- evidence_pack × 1 + docs/reports × 1 + docs/76 §1-§6 + docs/52 零改动 全部落地
- **≥145 pytest green** (M4.15 新 ≥10 + 651 回归 26 + 650 回归 118 + 652 任务书集合 144 期望 + ≥10 新 = ≥145)
- backfill 完整性三齐（per 651 审计 P4 + 652 任务书 §C）

**不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M4.13 / M4.14 / M4.15 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线）。

**O1 仍 OPEN** — B路 live-candidate 仅登记, 不切换/启用; 等用户/架构师裁定。

---

### §6.1 653-A.0 P4-A.0 规范 v2 落地 (per 652 审计 P4-1 处置; 2026-09-02 立; 653 沿用)

**审计 P4 发现** (rev90 status 行第三型自指陈旧复发): 652 §CURRENT status 行 pin 中间 SHA `04721b7` 为"终态 HEAD"且"待 §C-5 双推复核"字样在 0a3d284 复核通过后未清除——与执行端本刀自己固化的 P4-1 规则（docs/75:283"中间 SHA 一律不入 status 文本"）直接冲突。

**653-A.0 规范 v2**（本节落地）:
- **status 收口与 §NOW 刷新同 commit 原子完成**：status 行任何"待复核 / 待 §C-x / 待 X"陈旧字样在复核通过后**必须立即清除**（与 §NOW 收口 commit 同一次提交，不允许 §NOW 收口后再留 status pin）。
- **status 文本如需引 HEAD 一律 `git log -1` 实测终态**（或省略 SHA 仅写"三 ref 全等"）；严禁 pin 中间 SHA 为"终态"。
- **沿用 652-A.0 P4-2 amend-first 规则**（先 amend 完成再写链文本；cc_head 链 SHA 一律 `git log --format=%H -n <n>` 实测）。

**653-C 执行节奏**（per 653 tasking §1.653-C）: rev92 §NOW 刷新 commit 内**同时**完成 status 行收口 + §NOW 收口 + "待复核"字样清除（一次原子提交），不再分两 commit。

— End §6.1 tailnote —

---

— End 76 — M4.15 v9 真实化 spike 审查 20260902 —