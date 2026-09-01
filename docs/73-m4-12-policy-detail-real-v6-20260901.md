# 73 — M4.12 政策详情 v6 真实化 spike (架构师级审查)

> **刀号**: 649
> **Milestone**: M4.12（沿用 642/643/644/645/646/647/648 spike 模式；spike 第 8 次）
> **类型**: 架构师级 §1-§6 审查文档
> **日期**: 2026-09-01
> **依据**:
> - `docs/72-m4-11-policy-detail-real-v5-20260901.md` (648 M4.11 政策详情 v5)
> - `648-stage0-cursor-s648-m4-11-v5-audit-PASS-20260901.md` (648 审计 PASS·有限通过)
> - `649-stage0-architect-m4-12-v6-pool-activation-tasking-20260901.md` §1.649-A.0 / 649-A.1 / 649-A.2 / 649-A.3 / 649-A.4
> **前置**: 648 DELIVERED + 审计 PASS（有限通过）
> **架构师综合**: 649 = A.0 docs/72 §7 行内 append (P3-1 口径统一 + P3-2 回填) + A.1 M4.12 v6 hubei/jilin 16 INSERT (chain_id='real_649_m4_12_policy_detail_v6' UUID h 段; hubei→liaoning 跨省 substitute 池首次激活) + A.2 O1 零动作 + A.3 本文档 (docs/73) + A.4 evidence ×2 (含附属复验产物指针)
> **chain_id**: `real_649_m4_12_policy_detail_v6` (末段 `_v6` ≠ 648 `_v5` ≠ 647 `_v4` ≠ 646 `_v3` ≠ 645 `_v2`)
> **UUID prefix**: h 段 (h02-h62) ≠ 648 g 段 (g02-g62) ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段
> **不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M6 PASS。

---

## 1. M4.12 v6 落地终态

| 子刀 | 文件 / 范围 | 状态 | 说明 |
|---|---|---|---|
| 649-A.0 | docs/72 §7 行内 append 尾注（648 审计 PASS·有限通过 + P3-1 口径统一 + P3-2 回填 + P4-1/3/4 登记） | DONE | 红线 13 固化附属产物指针条款（per 648 审计 P3-1）；rev81 三处回填缺口已由审验端 rev82 全面修复（登记即可） |
| 649-A.1 | `scripts/fetch_m4_12_policy_detail_v6_2024.py` + `scripts/seed_m4_12_policy_detail_real_v6.sql` + `evidence_pack/m4_12_policy_detail_real_v6_20260901.json` + `docs/reports/m4_12_policy_detail_real_v6_20260901.md` | DONE | M4.12 政策详情 v6 真实化；2 样本 (hubei + jilin 第 11/12 样本) × 6 政策表 + 2 source_registry + 2 source_document = **16 INSERT**；**hubei 跨省 substitute 池首次激活** → liaoning (412+412 → 404 → / 200 REACHABLE)；jilin 直接 REACHABLE；http_count=6/12；fetched_count=2；fetch_status=REAL_FETCHED |
| 649-A.2 | O1 零动作（沿用 646 登记，O1 仍 OPEN） | DONE | 不新增 probe、不启用、不改 registry/connector；回执 O1 = OPEN |
| 649-A.3 | 本文档（docs/73） | DONE | §1-§6 架构师级审查 |
| 649-A.4 | `docs/reports/m4_12_policy_detail_real_v6_20260901.md` + `evidence_pack/m4_12_policy_detail_real_v6_20260901.json` | DONE | evidence × 2；主 evidence methodology 含附属产物指针（per 648 审计 P3-1 口径统一条款） |
| 649-B | ≥8 新测试 + 81 回归 = ≥89 | DONE | **≥89 pytest green** (M4.12 新 ≥8 + 648 回归 81) |
| 649-C | 回执 + commit + 双推 + backfill 三齐 | DONE | `649-stage0-cc-m4-12-v6-pool-activation-receipt-20260901.md` §PHOTO-1..N + 4 commits + EXEC-QUEUE rev82→rev83→rev84 backfill 三齐 |

---

## 2. substitute 跨省代换登记（§2 落地, per 649 任务书 §0.13 红线 13）

### 2.1 跨省 substitute 触发事实

Per 649 任务书 §0.13: **跨省 substitute 仅限递补池**（liaoning/shaanxi/sichuan/guizhou/jiangsu），触发即 evidence `substitute_reason` + docs/73 §2 登记。

**触发事件**: hubei 首选 `https://www.hubei.gov.cn/zwgk/` 412 (Precondition Failed) + 备用 `https://www.hubei.gov.cn/` 412 (Precondition Failed) → 递补池按序取 liaoning → liaoning `https://www.ln.gov.cn/zwgk/` 404 → 备用 `https://www.ln.gov.cn/` **200 REACHABLE** (148399 bytes, SHA `b22d1fb4d291e9e134166602757e5184c99f4a4d67c66abd2fdd20a5371d4f82`)

### 2.2 递补池触发顺序

| 池成员 | ICP 标志 | 触发顺序 | 实际是否激活 |
|---|---|---|---|
| **liaoning** | 辽ICP备 | 1 | **✓ 激活** (hubei 412+412 → ln /zwgk/ 404 → ln / 200 REACHABLE) |
| shaanxi | 陕ICP备 | 2 | 备而未触发（liaoning 1 步激活即止） |
| sichuan | 川ICP备 | 3 | 备而未触发 |
| guizhou | 黔ICP备 | 4 | 备而未触发 |
| jiangsu | 苏ICP备 | 5 | 备而未触发 |

### 2.3 跨省 substitute 完整审计链

| 维度 | 原始请求 (hubei) | substitute 实际抓取 (liaoning) | 关联 |
|---|---|---|---|
| **cell.province** | hubei (≠ 改写) | — | 沿用红线 1：原始请求省不可改写 |
| **cell.actual_province** | — | liaoning | NEW 字段（per 648 审计反馈"代换前后不透明"） |
| **substitute_used** | true | — | lineage.substitute_used=true |
| **substitute_reason** | "原试点省 hubei 两级 fallback 均返回 412 (Precondition Failed); 按 649 任务书 §0.13 递补池按序取 liaoning (省府根 / 200 REACHABLE; 396 锚点命中)" | 同左 | evidence cells[0].substitute_reason + docs/73 §2 双向登记 |
| **SHA** | (hubei 站 WAF/precondition 拦截层, 无落地 SHA) | `b22d1fb4d291e9e1...` (liaoning 省府根) | 真实抓取 SHA = liaoning 站 |
| **size** | — | 148399 bytes | file_size_bytes = liaoning 站 |
| **fetch_log attempt_province** | hubei × 2 + liaoning × 2 | — | per-attempt provenance 透明 |
| **fallback_chain_used** | ["zwgk_root", "province_root", "substitute[liaoning]/zwgk_root", "substitute[liaoning]/province_root"] | — | 完整链路留痕 |

### 2.4 已用省全集 (沿用 648 红线 4 + 649 增量)

| 类别 | 成员 |
|---|---|
| 已用省 (不得重复): | HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH |
| 649 增量: | hubei (substitute) + jilin (直接) → substitute 实际抓取 liaoning |
| **新进入** 已用省全集 (per 649 后): | **HUBEI / JILIN / LIAONING** (递补池首次激活) |

### 2.5 替代不宣告条款

- docs/52 零改动（per 红线 12：registry 行 SHA 零漂移；本次 seed 增量落 staging 蓝本）
- 不宣告 substitute = 真实化（substitute 性质上跨域抓取 = 仅作 fallback；不宣布任意 M4.x "真实化 PASS"）
- 后续 650+ 若需 substitute，应再次登记 docs/73 §2 增量并保持 hubei→liaoning 链路证据完整

---

## 3. M4.12 v6 spike 边界（vs 649 tasking 规划）

### 3.1 649 tasking 规划 vs 实测对比

**649 tasking 规划**：

- 沿用 648 fetch/seed 模式：**2 新样本**（≤12 total）
  - hubei 首选: `https://www.hubei.gov.cn/zwgk/`；fallback #1 `https://www.hubei.gov.cn/`
  - jilin 首选: `https://www.jl.gov.cn/zwgk/`；fallback #1 `https://www.jl.gov.cn/`
  - 两级均 BLOCKED → 递补池按序 liaoning → shaanxi → sichuan → guizhou → jiangsu
- = **12 INSERT planned**（6 表 × 2 真实）
- + 2 source_registry + 2 source_document = **16 INSERT total**
- ≤12 HTTP total (2 cells × 1 HTTP each = 2-9 actual)
- chain_id='real_649_m4_12_policy_detail_v6' (末段 `_v6`，≠ 648 `_v5`)
- UUID prefix h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段
- 2 新 SHA 全 distinct ≠ 638-648 全部 SHA
- substitute 预授权池: liaoning → shaanxi → sichuan → guizhou → jiangsu（实际仅 liaoning 触发）

**649 实测反发现**：

- 2 真实样本落地（2 distinct SHA）：
  - hubei → liaoning substitute `b22d1fb4d291e9e1...` (liaoning 省府根 / 200 REACHABLE; 148399 bytes) — 全新 SHA；与 638-648 全部 distinct
  - jilin 直接 `a1e49a91172927df...` (jilin 省府根 / 200 REACHABLE; 69943 bytes) — 全新 SHA；与 638-648 全部 distinct
- 1 样本 /zwgk/ + / 两级均 412 (Precondition Failed) → 跨省 substitute 池首次激活 → liaoning 1 步 REACHABLE (hubei)
- 1 样本 /zwgk/ 0 timeout → fallback #1 / 200 REACHABLE (jilin)
- **substitute 预授权池按序取 liaoning 1 步激活** (剩余 shaanxi/sichuan/guizhou/jiangsu 备而未触发)
- spike 边界 **实测 16 INSERT** = **规划 16 INSERT = 0 调整**

### 3.2 625 fall-through chain 注记 (per knife 625 fall-through substitute policy)

| 样本 | 首选 /zwgk/ | fallback #1 (省府根) | substitute chain index=2+ (递补池) |
|---|---|---|---|
| hubei | 412 (Precondition Failed) | 412 (Precondition Failed) | **REACHABLE_VIA_SUBSTITUTE** (chain_index=2 → liaoning /zwgk/ 404 → chain_index=3 → liaoning / 200 REACHABLE) |
| jilin | 0 (timeout) | 200 (jilin 省府根 /) | **REACHABLE** (chain_index=1 fallback) |

hubei 走完整 4 级 chain (zwgk → / → substitute[ln]/zwgk → substitute[ln]/); jilin 走 2 级 chain (zwgk → /)。总 HTTP 6/12 (hubei 4 + jilin 2)。

### 3.3 spike 边界明细（16 INSERT total）

| 表 | 行数 | lineage.is_demo | UUID prefix | 区别 vs 648 |
|---|---|---|---|---|
| source_registry | 2 | `'false'` (NEW) | h0eebc99-...h02/h03 | 648 = g02/g03 |
| source_document | 2 | `'false'` (NEW) | h0eebc99-...h04/h05 | 648 = g04/g05 |
| policy_document | **2** | `'false'` (spike) | h1eebc99-...h11/h12 | 648 = g11/g12 |
| policy_target | **2** | `'false'` (spike) | h2eebc99-...h21/h22 | 648 = g21/g22 |
| policy_measure | **2** | `'false'` (spike) | h3eebc99-...h31/h32 | 648 = g31/g32 |
| government_commitment | **2** | `'false'` (spike) | h4eebc99-...h41/h42 | 648 = g41/g42 |
| commitment_progress | **2** | `'false'` (spike) | h5eebc99-...h51/h52 | 648 = g51/g52 |
| project_event | **2** | `'false'` (spike) | h6eebc99-...h61/h62 | 648 = g61/g62 |

**总计**：2 × 6 = **12 INSERT** (政策表) + 4 source = **16 INSERT total** ✓ 与 648 一致

### 3.4 真实样本 (2 distinct SHA → 2 用于 seed)

| 序号 | 试点省 | slot | URL | SHA (前 16) | file_size | 649 seed 用 | 备注 |
|---|---|---|---|---|---|---|---|
| 1 | hubei | hubei→liaoning | `/zwgk/` (412) → `/` (412) → ln `/zwgk/` (404) → ln `/` (200) | `b22d1fb4` | 148,399 | ✓ | **全新 SHA (第 11 样本)** chain_index=3 跨省 substitute |
| 2 | jilin | jilin_zwgk_chain | `/zwgk/` (0 timeout) → `/` (200) | `a1e49a91` | 69,943 | ✓ | **全新 SHA (第 12 样本)** chain_index=1 fallback |

**2 SHA distinct vs 638-648 SHA**：

- 649 `b22d1fb4` ≠ 648 `4006439e / a06e174f` ≠ 647 `8016ef08 / 56481050` ≠ 646 `fceb8c0a / 49eed23e` ≠ 645 `6237cd48 / dfa38998 / bd4c4c51 / f33eba53` ≠ 644 `bad8be51 / dfa38998 / f33eba53` ≠ 643 `e68099df / 63109491 / 93fe23b3` ≠ 642 `cd6aff30 / 4349ee0f / fede03ba` ≠ 641 `26e5379d...` ≠ 640 demo `0…02` ≠ 639 demo `0…01` ✓
- 649 `a1e49a91` ≠ 全部 638-648 SHA ✓
- 2 SHA 全部 distinct ≠ 638-648 全部 SHA

---

## 4. lineage 真实化 sentinel + chain_id 区分 + 真实 SHA 区分表

### 4.1 12 真实化刀 lineage 沿用 (per docs/33 §3.2)

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
| **649** | **`real_649_m4_12_policy_detail_v6`** | **false** | **hubei (→liaoning substitute) + jilin** | **h 段 (h02-h62)** |

### 4.2 真实 SHA 区分表（2 新 SHA + 21 既有）

| 序号 | 刀 | 试点省 | URL | SHA (前 16) | 备注 |
|---|---|---|---|---|---|
| 1-18 | (沿用 638-647) | (略) | (略) | (略) | (见 docs/71 §4.2 / docs/72 §4.2) |
| 19 | 638 (probe) | various | 23 试点省 | n/a (probe only) | 638 = `real_638_m4_1_people` chain_id 计入全链表 |
| 20 | 648 | hunan-zwgk-v5 | /zwgk/ (404) → / | `4006439e...` | chain_index=1 fallback |
| 21 | 648 | anhui-zwgk-v5 | /zwgk/ (timeout) → / | `a06e174f...` | chain_index=1 fallback |
| **22** | **649** | **hubei→liaoning** | **/zwgk/ (412) → / (412) → ln /zwgk/ (404) → ln / (200)** | **`b22d1fb4...`** | **NEW 649 第 11 样本** chain_index=3 substitute |
| **23** | **649** | **jilin-zwgk-v6** | **/zwgk/ (timeout) → / (200)** | **`a1e49a91...`** | **NEW 649 第 12 样本** chain_index=1 fallback |

**23 SHA 全部 distinct** (✓ 不撞 638-648)

### 4.3 UUID prefix 严格递增

```
demo → real → b → c → d → e → f → g (648) → h (649)
638-640 demo + real  →  641 real  →  642 b1-b6  →  643 c1-c2  →  644 c1-c2  →  645 d21-d94  →  646 e02-e62  →  647 f02-f62  →  648 g02-g62  →  649 h02-h62
```

**649 h 段** (`h0eebc99` / `h1eebc99` / `h2eebc99` / `h3eebc99` / `h4eebc99` / `h5eebc99` / `h6eebc99`) **≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段 ≠ 643 c 段** ✓

### 4.4 649 substitute 预授权池 (首次激活: liaoning)

Per 649 任务书 §A.1 显式 substitute 预授权池:

| 池成员 | 状态 | 备注 |
|---|---|---|
| **liaoning** | **✓ 激活** | hubei 412+412 → 递补 ln /zwgk/ 404 → ln / 200 REACHABLE |
| shaanxi | 备而未触发 | 优先留给 650+ |
| sichuan | 备而未触发 | 优先留给 650+ |
| guizhou | 备而未触发 | 优先留给 650+ |
| jiangsu | 备而未触发 | 优先留给 650+ |

**已用省全集** (不得重复): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH  
**649 增量**: HUBEI / JILIN / LIAONING (跨省 substitute 实际抓取)  
**649 首选**: hubei + jilin → hubei 412+412 触发 substitute 池取 liaoning (1 步); jilin / fallback REACHABLE

### 4.5 649-A.4 evidence 落地（附属产物指针）

- ✓ `evidence_pack/m4_12_policy_detail_real_v6_20260901.json` (主 evidence; `summary.methodology` 含附属产物指针)
- ✓ `docs/reports/m4_12_policy_detail_real_v6_20260901.md` (附属 report; 主 evidence methodology 引用)
- ✓ 主 evidence `methodology` 字段: "Per 649 §0.13: 附属复验/验证产物允许独立文件, 但主 evidence methodology 必须含指针. 指针 → docs/reports/m4_12_policy_detail_real_v6_20260901.md"

---

## 5. 650 下一步

### 5.1 650 候选 scope

- **scope A (推荐)**: 沿用 649 模式 + substitute 池扩展（shaanxi/sichuan/guizhou/jiangsu 任选 1-2 个）— spike 第 9 次扩展；优先 1-2 个 REACHABLE + 1-2 个 substitute 验证双 pattern
- **scope B**: O1 B路 live-candidate 启用（per 646-A.2 data.stats.gov.cn PENDING_CANDIDATE → 等用户裁定启用）
- **scope C**: Gate 1 启动（M2 Gate 后才合法, 当前阻塞；沿用 646/647/648/649 §5）
- **scope D**: docs/45/50 spike 文档清空收口（沿用 M6 收口模式）
- **scope E**: 5W1H 分析 + 沿用 638-649 模式扩展（spec 推演）

### 5.2 当前未落地（红线守护）

- **Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M5 / M5.1 / M5.2 / M5.3 / M6** — 17 个里程碑不宣布 PASS
- O1 仍 OPEN (B路 live-candidate 仅登记, 不切换/启用)
- dbt mart flip: 60 行 demo 中仅 1 行（nanjing + CONDITION）真实化 pilot, O1 全量未启动
- 4 fixture 锁值永不动（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
- 不动 registry.csv / mart 既有 638-648 行
- 不写 cegr.* 生产表
- chain_id 区分: 649 '_v6' ≠ 648 '_v5' ≠ 647 '_v4' ≠ 646 '_v3' ≠ 645 '_v2' ≠ 644 '_policy_detail' ≠ 643 '_govreport' ≠ 642 '_renmian' ≠ 641 '_heilongjiang'
- UUID h 段 (h02-h62) ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段

---

## 6. 下一步 + 不宣称 PASS

**649 完成**:

- M4.12 政策详情 v6 真实化（2 样本 × 6 政策表 = 12 INSERT + 4 source = 16 INSERT total; chain_id='real_649_m4_12_policy_detail_v6'; UUID h 段; 2 NEW SHA: b22d1fb4/a1e49a91; ≤12 HTTP total actual=6）
- **跨省 substitute 池首次激活**: hubei 412+412 → 递补 liaoning /zwgk/ 404 → ln / 200 REACHABLE (148399 bytes; SHA b22d1fb4...)
- jilin 直接 /zwgk/ timeout → fallback / 200 REACHABLE (69943 bytes; SHA a1e49a91...)
- 648 审计 P3-1 口径统一落地：附属复验产物允许独立文件，主 evidence `summary.methodology` 必须含指针
- **≥89 pytest green**（M4.12 新 ≥8 + 648 回归 81）
- evidence_pack × 1 + docs/reports × 1 + docs/72 §7 行内 append + docs/73 + docs/52 零改动 全部落地
- backfill 完整性三齐（per 649-C + 648 审计 P3-2）

**不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线）。

**O1 仍 OPEN** — B路 live-candidate 仅登记, 不切换/启用; 等用户/架构师裁定。

---

### 6.1 649 审计裁定登记（per 650-A.0 + 650 任务书 §1.650-A.0）

- **审验端**: Cursor 端 (`reviews/stage0-gate0-rework-2026-08-23/649-stage0-cursor-s649-m4-12-v6-audit-PASS-20260901.md`)
- **裁定**: **PASS（有限通过）** — 98/98 独立复跑 green；4 commits 双推 origin→github=`6ddd5a2`；递补池首次激活合规（hubei 412+412 → liaoning 序位 #1）；backfill 三齐实质达成；evidence 代换留痕结构为全链最佳
- **P3-1 蓝图更正（per 649 审计）**: 代换样本 h02 registry 行 province='HUBEI' + source_name="湖北省人民政府..." 与 source_url=https://www.ln.gov.cn/ 错位 → **650-A.0 行内更正**: h02 province→'LIAONING'、source_name 改辽宁口径; 同文件 h04/h11/h41/h51/h61 policy 表行 '湖北省'/'湖北' 字样同步更正; **红线 13 规范固化**: source_registry `province`/`source_name` 一律用 actual_province（URL 归属省），original_province 仅存 lineage JSONB
- **P4×3 (rev84 陈旧三处)**: 650-C 顺手修 — EXEC-QUEUE 顶部 `> **rev N**` header 行同步 §META 的 `rev: 85/86`；status 行写"649 DELIVERED + 4 commits 双推 + backfill 三齐 已完成"；§NOW 措辞不再自指陈旧
- **合并归档视图**: 649 审计 + 650 任务书 = `reviews/stage0-gate0-rework-2026-08-23/649-audit-650-tasking-consolidated-20260901.md`（148 行；用户指示 2026-09-01 起单文件模式）

---

— End 73 — M4.12 v6 真实化 spike 审查 20260901 —