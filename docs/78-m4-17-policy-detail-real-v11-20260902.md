# 78 — M4.17 政策详情 v11 西北双省 spike (架构师级审查)

> **刀号**: 654
> **Milestone**: M4.17（沿用 642/643/644/645/646/647/648/649/650/651/652/653 spike 模式；spike 第 13 次扩展；**654 §0.14 沿用 653 §0.14 BLOCKED_NO_POOL 留痕 e2e 验证 + 沿用 653 模板 + 西北五省区叙事收官 [XINJIANG/NEIMENGGU/SHAANXI/GANSU/QINGHAI]**）
> **类型**: 架构师级 §1-§6 审查文档
> **日期**: 2026-09-02
> **依据**:
> - `docs/77-m4-16-policy-detail-real-v10-20260902.md` (653 M4.16 政策详情 v10 审查)
> - `reviews/stage0-gate0-rework-2026-08-23/653-audit-654-tasking-consolidated-20260902.md` PART 1 (653 审计 PASS 有限通过) + PART 2 (654 任务书)
> - `652-stage0-architect-m4-16-v10-retry-spike-tasking-20260902.md` (653 任务书 §0 + §1.653-A.0/A.1/A.2/A.3/A.4)
> **前置**: 653 DELIVERED + 审计 **PASS（有限通过）**（2×P4：§META 回填不全 + status 第四型 SHA pin 陈旧; rev93 修正 + 654-A.0 规范 v3 落地）+ 653 §0.14 红线 14 e2e 验证模板化 + 递补池 [EXHAUSTED]（沿用 653）
> **架构师综合**: 654 = A.0 653 审计 P4×2 处置 + 规范 v3 (§META 五字段原子更新 + status 行禁含任何具体 SHA + 沿用 amend-first) + A.1 M4.17 v11 西北双省 spike (gansu + qinghai 第 21/22 样本; chain_id='real_654_m4_17_policy_detail_v11' UUID m 段; gansu 412×2 + qinghai Connection reset by peer ×2 — **真网首试省首触发 BLOCKED_NO_POOL 双例** per 654 §0.14 沿用 653; 0 INSERT ROWS 双首试省均 BLOCKED 留痕; retry_of=N/A 双首试省无前史; blocked_no_pool_count=2; HTTP 4/12 = 33% usage) + A.2 O1 零动作 + A.3 本文档 (docs/78) + A.4 evidence ×2 (含附属复验产物指针)
> **chain_id**: `real_654_m4_17_policy_detail_v11` (末段 `_v11` ≠ 653 `_v10` ≠ 652 `_v9` ≠ 651 `_v8`)
> **UUID prefix**: m 段 (m02-m62) ≠ 653 l 段 (l02-l62) ≠ 652 k 段 (k02-k62) ≠ 651 j 段
> **递补池状态**: **EXHAUSTED [正式耗尽]**（沿用 653 §0.14 红线 14 增补; 654 双首试省均 BLOCKED 真网首试省首触发）
> **本次双首试省实测**: BLOCKED_NO_POOL×2 (双首试省均真网首触发双例; gansu 412×2 + qinghai Connection reset by peer ×2 — 失败形式库第二例首见; retry_of=N/A lineage 全行; 0 INSERT ROWS)
> **不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M6 PASS。

---

## 1. M4.17 v11 西北双省落地终态

| 子刀 | 文件 / 范围 | 状态 | 说明 |
|---|---|---|---|
| 654-A.0 | `reviews/stage0-gate0-rework-2026-08-23/653-audit-654-tasking-consolidated-20260902.md` PART 1 (653 审计 P4×2 处置) + 规范 v3 落地 | DONE | per 653 审计 2×P4 (§META 回填不全 + status 第四型 SHA pin 陈旧) 教训沉淀: 规范 v3 (§META 五字段原子更新 [rev/status/last_delivery/last_receipt/tasking 状态行] 与 cc_head 同 commit + status 行禁含任何具体 SHA 终极条款 + 沿用 amend-first 规则); commit 9b54dbd (rev93) |
| 654-A.1 | `scripts/fetch_m4_17_policy_detail_v11_2024.py` + `scripts/seed_m4_17_policy_detail_real_v11.sql` + `evidence_pack/m4_17_policy_detail_real_v11_20260902.json` + `docs/reports/m4_17_policy_detail_real_v11_20260902.md` | DONE | M4.17 政策详情 v11 西北双省; 2 首试省 (gansu + qinghai 第 21/22 样本) — **双首试省均 BLOCKED_NO_POOL 真网首试省首触发**; gansu /zwgk/ + / 均 412 (412×2); qinghai /zwgk/ + / 均 Connection reset by peer (0/0 — 失败形式库第二例首见; 继 653 shandong SSL handshake failure 后); retry_of=N/A 双首试省无前史; 0 INSERT ROWS (per 654 §1.654-A.1 "任一 BLOCKED → 该省 0 INSERT"); substitute_used=0; **首试省首触发 BLOCKED_NO_POOL 双例** (per 654 §0.14 沿用 653 §0.14 红线 14); blocked_no_pool_count=2; http_count=4/12 (33% usage) |
| 654-A.2 | O1 零动作（沿用 646/647/648/649/650/651/652/653 登记, O1 仍 OPEN） | DONE | 不新增 probe、不启用、不改 registry/connector; 回执 O1 = OPEN |
| 654-A.3 | 本文档（docs/78） | DONE | §1-§6 架构师级审查; §2 含 **首试省 BLOCKED 留痕登记表** (双样本均 BLOCKED + retry_of=N/A + 实测触发累计); §4 chain_id 区分 17 真实化刀 + UUID 严格递增至 m 段 + 累 [BLOCKED_NO_POOL] 触发事件计数; §5 BLOCKED 留痕口径沿用 653 + 失败形式库登记 qinghai Connection reset by peer; **西北五省区叙事收官表** (XINJIANG 652 + NEI MENGGU 652 + SHAANXI 651 邻接 + GANSU 654 + QINGHAI 654) |
| 654-A.4 | `docs/reports/m4_17_policy_detail_real_v11_20260902.md` + `evidence_pack/m4_17_policy_detail_real_v11_20260902.json` | DONE | evidence × 2; 主 evidence methodology 含附属产物指针 (per 648 审计 P3-1 口径统一条款 + 649 审计 P3-1 代换行标注规范固化入红线 13 + **653 §0.14 红线 14 增补登记** (沿用) + **654 §0.14 首试省 BLOCKED_NO_POOL 留痕 e2e 验证 沿用 653 + retry_of=N/A 说明**) |

---

## 2. 首试省 BLOCKED 留痕登记表 (per 654 §0.14 沿用 653 §0.14 + 沿用 653 e2e 验证模板)

### 2.1 654 §0.14 强制 e2e 验证目标 (沿用 653 §0.14 复试)

Per 654 任务书 §0.14: "**654 首试省若两级 fallback 全失败 → BLOCKED_NO_POOL 留痕**（不跨省代换; seed 该省 0 INSERT + cell 占位 + blocked_reason); **三态均合法** (双 REACHABLE → 16 INSERT + 2 NEW SHA; 混合 → 按省实报; 双 BLOCKED → 0 INSERT + 三重留痕); **retry_of=N/A** (双省无前史首试; per 654 §1.654-A.1)"

**e2e 验证机制（4 实现位置 + 8 测试守门）**（沿用 653 §0.14 模板）:

1. **fetch 脚本分支代码可达** (`scripts/fetch_m4_17_policy_detail_v11_2024.py`):
   - `verdict: "BLOCKED_NO_POOL"` 分支存在
   - `blocked_reason` 字段存在 (本次**真网首试省首触发双例**; 2 个 BLOCKED cell 均含 blocked_reason)
   - `SUBSTITUTE_POOL = []` + `SUBSTITUTE_POOL_STATUS = "EXHAUSTED"` (沿用 653)
   - `RETRY_OF_NOTES` 全行 retry_of=N/A (gansu ← N/A; qinghai ← N/A)

2. **seed SQL 0 INSERT ROWS BLOCKED 留痕** (`scripts/seed_m4_17_policy_detail_real_v11.sql`):
   - 0 INSERT ROWS (per 654 §1.654-A.1 "任一 BLOCKED → 该省 0 INSERT"; 双首试省均 BLOCKED = 0 INSERT total)
   - 头部 documentation 完整记录 BLOCKED 实测 (gansu 412×2 + qinghai Connection reset by peer ×2)
   - lineage / chain_id / retry_of=N/A 信息保留在 evidence + docs/78 + receipt (非 seed 内)

3. **主 evidence summary + methodology** (`evidence_pack/m4_17_policy_detail_real_v11_20260902.json`):
   - `summary.substitute_pool_status='EXHAUSTED'`
   - `summary.blocked_no_pool_count=2` (本次**真网首试省首触发双例**)
   - `summary.fetch_status='ALL_BLOCKED_NO_POOL'` (双首试省均 BLOCKED)
   - `summary.retry_of_annotation` 字段含双首试省 retry_of=N/A 注解
   - `methodology` 含 "Per 654 §0.14: 首试省 BLOCKED_NO_POOL 留痕 e2e 验证 (沿用 653 §0.14 模板, docs/77 §5.2 + 654 §0.14 复试). 递补池 [EXHAUSTED] 沿用 653. 本次双样本结果: REACHABLE×0 / BLOCKED_NO_POOL×2 (真网首试省首触发双例)."

4. **docs/78 §5 BLOCKED 留痕口径** (本文件, 见 §5)

5. **测试守门** (`tests/test_m4_17_policy_detail_real_v11.py`):
   - `test_fetch_script_blocked_no_pool_branch_present` (BLOCKED_NO_POOL 字串守门 PASSED)
   - `test_evidence_json_substitute_pool_status_exhausted` (主 evidence substitute_pool_status='EXHAUSTED' 守门 PASSED)
   - `test_evidence_json_blocked_no_pool_count_two_real_first_trigger` (blocked_no_pool_count=2 + 真网首试省首触发守门 PASSED)
   - `test_seed_sql_zero_insert_blocked_retry` (0 INSERT ROWS + retry_of=N/A 守门 PASSED)
   - `test_p4_a0_v3_tailnote_654_a0_landed` (P4-A.0 规范 v3 守门 PASSED — §META 五字段原子更新 + status 行禁含任何具体 SHA)
   - `test_red_line_14_pool_exhaustion_fetch_script` (SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED' 守门 PASSED)
   - `test_retry_of_lineage_annotation_na` (RETRY_OF_NOTES 双样本 N/A 注解守门 PASSED)
   - `test_chain_id_uuid_prefix_m_distinct` (m 段 8 表前缀守门 PASSED)

### 2.2 双首试省本次实测结果 (真网首试省首触发 BLOCKED 双例)

| 样本 | 首选 /zwgk/ | fallback #1 / | verdict | chain_index | HTTP | retry_of |
|---|---|---|---|---|---|---|
| **gansu** | **412 Precondition Failed** | **412 Precondition Failed** | **BLOCKED_NO_POOL** | -1 (双失败) | 2 | retry_of=N/A (无前史首试省) |
| **qinghai** | **Connection reset by peer (0)** (curl recv failure, 全链第二例首见) | **Connection reset by peer (0)** (同) | **BLOCKED_NO_POOL** | -1 (双失败) | 2 | retry_of=N/A (无前史首试省) |

**双首试省均 BLOCKED_NO_POOL 真网首试省首触发双例**; `blocked_no_pool_count=2`; `fetch_status=ALL_BLOCKED_NO_POOL`; `substitute_used_count=0`; `distinct_shas=[]` (无 REACHABLE → 无 SHA)。

**retry_of lineage 注解全行**: gansu ← N/A (无前史首试省); qinghai ← N/A (无前史首试省); 均经 fetch_cell 返回值注入 + evidence summary.retry_of_annotation + cell.retry_of 双口径落地。

### 2.3 BLOCKED_NO_POOL 触发事件累计计数 (沿用 653 §2.3 模板)

| 刀 | 累计触发次数 | 累计 e2e 验证次数 | 备注 |
|---|---|---|---|
| 638-650 | 0 (n/a) | 0 (n/a) | BLOCKED_NO_POOL 分支不存在 |
| 651 | 0 | 0 | 分支代码首次落地; 但未触发 (双样本 REACHABLE) |
| 652 | 0 | 1 | 652 §0.14 强制 e2e 验证完成; 5 个守门 PASSED; 分支代码可达; 双样本均 REACHABLE (未触发 BLOCKED) |
| 653 | 2 (真网首次双触发) | 1 (本次双样本 BLOCKED → BLOCKED_NO_POOL 路径首次实测命中, 留痕完整 + retry_of lineage 全行) | 653 §0.14 复试 BLOCKED_NO_POOL 真网首次双触发; 8 守门 PASSED (含 retry_of 守门 + 双触发守门); shandong SSL handshake failure 0/0 + hubei 412×2 |
| **654** | **2** (真网首试省首触发双例) | **1** (本次双首试省 BLOCKED → BLOCKED_NO_POOL 路径首次实测命中 [首试省], 留痕完整 + retry_of=N/A lineage 全行) | **654 §0.14 首试省首触发 BLOCKED_NO_POOL 双例**; 8 守门 PASSED (沿用 653 模板); gansu 412×2 + qinghai Connection reset by peer ×2 |

---

## 3. M4.17 v11 spike 边界（vs 654 tasking 规划）

### 3.1 654 tasking 规划 vs 实测对比

**654 tasking 规划**：

- 沿用 653 fetch/seed 模式: 2 新样本 (≤12 total) — 西北四连收官: XINJIANG/NEIMENGGU (652) + SHAANXI (651 邻接) + GANSU/QINGHAI (654)
  - GANSU 首选: `https://www.gansu.gov.cn/zwgk/`; fallback #1 `https://www.gansu.gov.cn/` (省府根)
  - QINGHAI 首选: `https://www.qinghai.gov.cn/zwgk/`; fallback #1 `https://www.qinghai.gov.cn/` (省府根)
  - 双样本两级 fallback 全失败 → **BLOCKED_NO_POOL 留痕**, 不跨省代换 (per 653 §0.14 红线 14 增补沿用)
  - 三态均合法: 双 REACHABLE → 16 INSERT + 2 NEW SHA; 混合 → 按省实报; 双 BLOCKED → 0 INSERT + 三重留痕
  - lineage 全行 `retry_of=N/A` (双省无前史首试)
- = 双 REACHABLE: **16 INSERT ROWS planned** (12 政策表 + 2 source_registry + 2 source_document)
- = 任一 BLOCKED: **0 INSERT ROWS per BLOCKED 省份** (INSERT 数按实报并说明)
- ≤12 HTTP total (2 cells × 1-2 HTTP each = 2-4 actual)
- chain_id='real_654_m4_17_policy_detail_v11' (末段 `_v11`, ≠ 653 `_v10`)
- UUID prefix m 段 ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段
- 0 NEW SHA (无 REACHABLE) 或 2 NEW SHA (双 REACHABLE)
- 递补池 (SUBSTITUTE_POOL) [EXHAUSTED] 沿用 653 耗尽态

**654 实测反发现**：

- **真网首试省首触发 BLOCKED_NO_POOL 双例** (双首试省均两级 fallback 全失败):
  - gansu /zwgk/ + / 均 412 (412×2) — 与 649 HUBEI 412×2 史同型, 但 654 retry_of=N/A (无前史首试省, lineage 不引用 649)
  - qinghai /zwgk/ + / 均 Connection reset by peer (0/0) — **新失败形式 (失败形式库第二例首见)** (curl recv failure: Connection reset by peer, 全链第二例首见失败形式, 继 653 shandong SSL handshake failure 后)
- 双首试省均 verdict=BLOCKED_NO_POOL, substitute_used=false, blocked_reason 非空
- retry_of=N/A lineage 全行: gansu ← N/A (无前史首试); qinghai ← N/A (无前史首试)
- **0 INSERT ROWS** (per 654 §1.654-A.1 "任一 BLOCKED → 该省 0 INSERT"; 双 BLOCKED = 0 INSERT total)
- **0 NEW SHA** (无 REACHABLE → 无 SHA); distinct_shas=[]
- **递补池 [EXHAUSTED] 触发**: 双首试省均 BLOCKED; substitute_used_count=0; blocked_no_pool_count=2
- **BLOCKED_NO_POOL 分支代码 e2e 实测命中** (8 个守门 PASSED; per 654 §0.14 沿用 653 §0.14 强制验证; 含 retry_of=N/A 守门 + 双触发守门)
- spike 边界 **实测 0 INSERT ROWS** = **规划 0 INSERT ROWS (双 BLOCKED 口径) = 0 调整**
- **HTTP 实测 4/12 = 33% usage** (vs 653 4/12 = 33% usage; vs 652 3/12 = 25% usage; vs 651 4/12 = 33% usage)

### 3.2 西北五省区叙事收官表 (per 654 tasking §1.654-A.3)

| 西北省 | 落定刀 | URL 主域 | 试点方式 | 实际 verdict | retry_of | 实际省 |
|---|---|---|---|---|---|---|
| **XINJIANG** (新疆) | 652 (M4.15 v9) | www.xinjiang.gov.cn | 首选 /zwgk/ 200 REACHABLE | REACHABLE (fallback #1) | — | XINJIANG |
| **NEI MENGGU** (内蒙古) | 652 (M4.15 v9) | www.nmg.gov.cn | 首选 /zwgk/ 200 REACHABLE | REACHABLE (首选) | — | NEI MENGGU |
| **SHAANXI** (陕西) — 邻接 | 651 (M4.14 v8) | www.shaanxi.gov.cn | 首选 /zwgk/ 404 → fallback #1 / 200 REACHABLE | REACHABLE (fallback #1) | — | SHAANXI |
| **GANSU** (甘肃) | **654 (M4.17 v11)** | www.gansu.gov.cn | 首选 /zwgk/ 412 → fallback #1 / 412 | **BLOCKED_NO_POOL** | **N/A** (无前史) | NULL |
| **QINGHAI** (青海) | **654 (M4.17 v11)** | www.qinghai.gov.cn | 首选 /zwgk/ 0 (Connection reset) → fallback #1 / 0 (Connection reset) | **BLOCKED_NO_POOL** | **N/A** (无前史) | NULL |

**西北五省区叙事收官**: XINJIANG/NEI MENGGU (652 双 REACHABLE) + SHAANXI (651 REACHABLE 邻接) + GANSU/QINGHAI (654 双首试省首触发 BLOCKED)。三 REACHABLE 落 evidence + 两 BLOCKED 留痕 (e2e 完全体沿用 653 模板, 真网首试省首触发双例)。

**注**: SHAANXI 是 651 M4.14 v8 已落定 REACHABLE (fallback #1); XINJIANG/NEI MENGGU 是 652 M4.15 v9 双 REACHABLE; GANSU/QINGHAI 是 654 M4.17 v11 双首试省 BLOCKED。西北五省区 = 651+652+654 三刀收官。

### 3.3 spike 边界明细 (0 INSERT ROWS total per BLOCKED 口径)

**0 INSERT ROWS** (双首试省均 BLOCKED_NO_POOL; seed SQL 仅头部 documentation; lineage / chain_id / retry_of=N/A 全部在 evidence + docs/78 + receipt)

| 表 | ROWS | 备注 |
|---|---|---|
| source_registry | 0 | BLOCKED cell 占位在 evidence; 不写 INSERT |
| source_document | 0 | 同上 |
| policy_document | 0 | 同上 |
| policy_target | 0 | 同上 |
| policy_measure | 0 | 同上 |
| government_commitment | 0 | 同上 |
| commitment_progress | 0 | 同上 |
| project_event | 0 | 同上 |

**总计**: **0 INSERT ROWS** (per 654 §1.654-A.1 BLOCKED 口径; 与 651/652 REACHABLE 16 INSERT ROWS 形成对照)

### 3.4 真实样本 (0 NEW SHA per BLOCKED 口径)

| 序号 | 试点省 | slot | URL | SHA | file_size | 654 seed 用 | 备注 |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | **0 NEW SHA** (双首试省均 BLOCKED, 无 REACHABLE → 无 SHA) |

**0 SHA** (vs 653 0 NEW SHA [双 BLOCKED]; vs 652 2 NEW SHA `21c8211b/da1d4104` ≠ 651 2 NEW SHA `9d0ad78a/f58a3384`)

---

## 4. lineage 真实化 sentinel + chain_id 区分 + 真实 SHA 区分表

### 4.1 17 真实化刀 lineage 沿用 (per docs/33 §3.2)

| 刀 | chain_id | is_demo | 试点省 | UUID prefix | retry_of |
|---|---|---|---|---|---|
| 641 | `real_641_heilongjiang` | false | heilongjiang | real prefix | — |
| 642 | `real_642_m4_5_renmian` | false | henan/guangdong/guizhou | b 段 (b1-b6) | — |
| 643 | `real_643_m4_6_govreport` | false | hlj/henan/yunnan | c 段 (c41-c41) | — |
| 644 | `real_644_m4_7_policy_detail` | false | hlj/henan/yunnan | c 段 (c41-c93) | — |
| 645 | `real_645_m4_8_policy_detail_v2` | false | hlj/henan-zfgb/henan-zwgk/yunnan | d 段 (d21-d94) | — |
| 646 | `real_646_m4_9_policy_detail_v3` | false | fujian + guangdong | e 段 (e02-e62) | — |
| 647 | `real_647_m4_10_policy_detail_v4` | false | zhejiang + jiangxi (substitute) | f 段 (f02-f62) | shandong 4 连 BLOCKED 史 (供 653 retry) |
| 648 | `real_648_m4_11_policy_detail_v5` | false | hunan + anhui | g 段 (g02-g62) | — |
| 649 | `real_649_m4_12_policy_detail_v6` | false | hubei (→liaoning substitute) + jilin | h 段 (h02-h62) | hubei 412×2 史 (供 653 retry) |
| 650 | `real_650_m4_13_policy_detail_v7` | false | guizhou + jiangsu (双 REACHABLE, 无 substitute) | i 段 (i02-i62) | — |
| 651 | `real_651_m4_14_policy_detail_v8` | false | shaanxi + sichuan (双 fallback #1 REACHABLE, 递补池 [EXHAUSTED]) | j 段 (j02-j62) | — |
| 652 | `real_652_m4_15_policy_detail_v9` | false | xinjiang + nei_menggu (双 REACHABLE, BLOCKED_NO_POOL 分支代码 e2e 可达) | k 段 (k02-k62) | — |
| 653 | `real_653_m4_16_policy_detail_v10` | false (per evidence metadata; 无 INSERT) | shandong + hubei (双 BLOCKED_NO_POOL 真网首次双触发, retry_of 全行) | l 段 (l02-l62) | shandong ← 647; hubei ← 649 |
| **654** | **`real_654_m4_17_policy_detail_v11`** | **false** (per evidence metadata; 无 INSERT) | **gansu + qinghai (双首试省首触发 BLOCKED_NO_POOL, retry_of=N/A 双首试省无前史)** | **m 段 (m02-m62)** | **gansu ← N/A; qinghai ← N/A** |

### 4.2 真实 SHA 区分表（0 NEW SHA + 29 既有）

| 序号 | 刀 | 试点省 | URL | SHA (前 16) | 备注 |
|---|---|---|---|---|---|
| 1-29 | (沿用 638-652) | (略) | (略) | (略) | (见 docs/71/72/73/74/75/76) |
| — | 653 | shandong + hubei | (双 BLOCKED_NO_POOL) | (0 NEW SHA) | 653 双样本均 BLOCKED; 真网首次双触发; 0 SHA |
| — | **654** | **gansu + qinghai** | **(双首试省首触发 BLOCKED)** | **(0 NEW SHA)** | **654 双首试省均 BLOCKED; 真网首试省首触发双例; 0 SHA** |

**29 SHA 累计不变** (vs 652 后 +2 NEW = 31 总 SHA, 653/654 双样本均 BLOCKED → 0 NEW SHA → 总 SHA 不变 = 31)

### 4.3 UUID prefix 严格递增

```
demo → real → b → c → d → e → f (647) → g (648) → h (649) → i (650) → j (651) → k (652) → l (653) → m (654)
638-640 demo + real  →  641 real  →  642 b1-b6  →  643 c1-c2  →  644 c1-c2  →  645 d21-d94  →  646 e02-e62  →  647 f02-f62  →  648 g02-g62  →  649 h02-h62  →  650 i02-i62  →  651 j02-j62  →  652 k02-k62  →  653 l02-l62  →  654 m02-m62
```

**654 m 段** (`m0eebc99` / `m1eebc99` / `m2eebc99` / `m3eebc99` / `m4eebc99` / `m5eebc99` / `m6eebc99`) **≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段 ≠ 643 c 段** ✓

### 4.4 递补池状态更新 (沿用 653 [EXHAUSTED] substitute 状态)

Per 649 §4.4 + 650 增量 + 651 收官 + 652 沿用 + 653 沿用 + **654 沿用 [EXHAUSTED]** substitute 状态:

| 池成员 | 状态 (649 后) | 状态 (650 后) | 状态 (651 后) | 状态 (652 后) | 状态 (653 后) | 状态 (654 后) | 备注 |
|---|---|---|---|---|---|---|---|
| **liaoning** | ✓ 649 激活 | ✓ 649 激活（已 consumed） | ✓ 649 激活（已 consumed） | ✓ 649 激活（已 consumed） | ✓ 649 激活（已 consumed） | ✓ 649 激活（已 consumed） | hubei 412+412 → ln /zwgk/ 404 → ln / 200 REACHABLE |
| **shaanxi** | 备而未触发 | 备而未触发 (优先级 1) | ✓ **651 转正首选** (consumed) | ✓ 651 转正首选（已 consumed） | ✓ 651 转正首选（已 consumed） | ✓ 651 转正首选（已 consumed） | shaanxi /zwgk/ 404 → / 200 (87956 bytes) |
| **sichuan** | 备而未触发 | 备而未触发 (优先级 2) | ✓ **651 转正首选** (consumed) | ✓ 651 转正首选（已 consumed） | ✓ 651 转正首选（已 consumed） | ✓ 651 转正首选（已 consumed） | sichuan /zwgk/ 403 WAF → / 200 (100536 bytes) |
| guizhou | 备而未触发 | ✓ **650 直接 REACHABLE** (chain_index=0) | ✓ 650 直接 REACHABLE (chain_index=0) | ✓ 650 直接 REACHABLE (chain_index=0) | ✓ 650 直接 REACHABLE (chain_index=0) | ✓ 650 直接 REACHABLE (chain_index=0) | guizhou /zwgk/ 200 |
| jiangsu | 备而未触发 | ✓ **650 fallback REACHABLE** (chain_index=1) | ✓ 650 fallback REACHABLE (chain_index=1) | ✓ 650 fallback REACHABLE (chain_index=1) | ✓ 650 fallback REACHABLE (chain_index=1) | ✓ 650 fallback REACHABLE (chain_index=1) | jiangsu /zwgk/ 404 → / 200 |

**递补池正式耗尽 [EXHAUSTED]**: 5 个原始池成员 (649 候选) 全部落定 (liaoning 激活 + guizhou/jiangsu 升格 + shaanxi/sichuan 转正消耗); 池清空; **红线 14 生效**; 此后任一样本槽两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换。

**654 双首试省均 BLOCKED 留痕** (per 654 §0.14 真网首试省首触发双例): gansu + qinghai retry_of=N/A 全行; 0 INSERT ROWS; actual_province=NULL; 不跨省代换 ([EXHAUSTED] 池不可代换)。

**已用省全集** (按 actual_province 口径, 仍 18 省): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL / GUIZHOU / JIANGSU / SHAANXI / SICHUAN / XINJIANG / NEI MENGGU (17 个非 retry 历史 REACHABLE 集, 加上 649 替代 LIAONING, 共 18)
**649 增量**: HUBEI (substitute 槽名 consumed) / JILIN / LIAONING (跨省 substitute 实际抓取)
**650 增量**: GUIZHOU / JIANGSU (双直接 REACHABLE)
**651 增量**: SHAANXI / SICHUAN (双 fallback #1 REACHABLE)
**652 增量**: XINJIANG (fallback #1 REACHABLE) / NEI MENGGU (首选 REACHABLE)
**653 增量**: 0 (双样本均 BLOCKED; 已用省不变 18; shandong/hubei 留 BLOCKED_NO_POOL 痕迹, actual_province=NULL)
**654 增量**: 0 (双首试省均 BLOCKED; 已用省不变 18; gansu/qinghai 留 BLOCKED_NO_POOL 痕迹, actual_province=NULL)
**654 双首试**: gansu + qinghai → 双首试省均 BLOCKED (gansu 412×2 + qinghai Connection reset by peer ×2); retry_of=N/A 全行 (双首试省无前史); HTTP 4/12 (33% usage); 0 INSERT ROWS

### 4.5 654-A.4 evidence 落地（附属产物指针）

- ✓ `evidence_pack/m4_17_policy_detail_real_v11_20260902.json` (主 evidence; `summary.methodology` 含附属产物指针 + 654 §0.14 沿用 653 §0.14 复试援引 + retry_of=N/A 注解)
- ✓ `docs/reports/m4_17_policy_detail_real_v11_20260902.md` (附属 report; 主 evidence methodology 引用)
- ✓ 主 evidence `methodology` 字段: "Per 654 §0.14: 首试省 BLOCKED_NO_POOL 留痕 e2e 验证 (沿用 653 §0.14 模板, docs/77 §5.2 + 654 §0.14 复试). 递补池 [EXHAUSTED] 沿用 653. 本次双样本结果: REACHABLE×0 / BLOCKED_NO_POOL×2 (真网首试省首触发双例)."
- ✓ 主 evidence `summary.substitute_pool_status = "EXHAUSTED"` (显式登记)
- ✓ 主 evidence `summary.blocked_no_pool_count = 2` (本次真网首试省首触发双例)
- ✓ 主 evidence `summary.fetch_status = "ALL_BLOCKED_NO_POOL"` (双首试省均 BLOCKED)
- ✓ 主 evidence `summary.retry_of_annotation` 含 gansu + qinghai 双首试省 retry_of=N/A 注解
- ✓ 主 evidence `cells[0]` gansu: verdict=BLOCKED_NO_POOL + blocked_reason + retry_of=N/A 字段
- ✓ 主 evidence `cells[1]` qinghai: verdict=BLOCKED_NO_POOL + blocked_reason + retry_of=N/A 字段

---

## 5. 后续 655+ BLOCKED 留痕口径 + 失败形式库 (沿用 654 §0.14 e2e 验证机制 + 654 首试省首触发经验)

### 5.1 后续候选 scope

- **scope A (后续 655+ 推荐)**: 沿用 654 模式, 但**递补池 [EXHAUSTED]**, 任一样本槽两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换 (per 红线 14 增补沿用 653 §0.14); 654 §0.14 e2e 验证机制 (4 实现位置 + 8 个守门含 retry_of=N/A + 双触发) 作为后续 BLOCKED 触发时的守门标准; **retry_of 字段全行生效** (任一具有前史 BLOCKED 的省份 retry_of 必填; 任一首试省 retry_of=N/A)
- **scope B**: O1 B路 live-candidate 启用 (per 646-A.2 data.stats.gov.cn PENDING_CANDIDATE → 等用户裁定启用)
- **scope C**: Gate 1 启动 (M2 Gate 后才合法, 当前阻塞; 沿用 646-654 §5)
- **scope D**: docs/45/50 spike 文档清空收口 (沿用 M6 收口模式)
- **scope E**: 5W1H 分析 + 沿用 638-654 模式扩展 (spec 推演)

### 5.2 BLOCKED_NO_POOL 留痕口径 (沿用 654 §0.14 验证机制 + 654 首试省首触发经验)

- 触发条件: 任一样本槽两级 fallback 全失败 (e.g., /zwgk/ + / 均非 200/真内容/有锚点)
- 落点 (4 实现位置):
  1. fetch 脚本: `verdict="BLOCKED_NO_POOL"` + `blocked_reason` 字段
  2. seed SQL: 跳过该样本 (BLOCKED 留痕不写 INSERT, 但保留 0 INSERT ROWS + 头部 documentation 记录 BLOCKED 实测)
  3. 主 evidence: `summary.blocked_no_pool_count += 1` + cell 留 blocked_reason + retry_of 字段 (若 applicable — 首试省 N/A; 有前史省填具体刀号)
  4. docs/77+ §2 BLOCKED 留痕 e2e 验证登记表 (沿用 653/654 模板)
- 双样本均 BLOCKED → 0 INSERT ROWS (per 653 §1.653-A.1 + 654 §1.654-A.1 BLOCKED 口径)

### 5.3 失败形式库 (新增 654)

**全链失败形式累计**:

| # | 刀 | 失败形式 | 样本 | http_code | 描述 |
|---|---|---|---|---|---|
| 1 | 647 | 域名错配 + 403 | shandong | 403 | 域名解析指向非政府站; 4 连 BLOCKED (双 fallback × 2) |
| 2 | 649 | 412 Precondition Failed | hubei | 412 | 服务器拒绝请求条件; 槽被代换 actual=LIAONING |
| 3 | 653 | **SSL handshake failure** (LibreSSL/3.3.6 error:1404B410) | shandong | 0 (SSL 失败) | **首见失败形式**: SSL/TLS 握手失败, curl 无法建立加密连接 |
| 4 | 654 | **Connection reset by peer** (curl recv failure) | qinghai | 0 (recv failure) | **第二例首见失败形式**: 远程服务器主动重置连接; curl `Recv failure: Connection reset by peer` |
| 5 | 654 | 412 Precondition Failed (复发) | gansu | 412 | 同 649 hubei 412×2 史, 但 654 retry_of=N/A (首试省) |

**失败形式库登记 (新)**:
- 654 新增 1 例首见失败形式 (qinghai "Connection reset by peer"); 复用 1 例旧形式 (gansu 412×2 = 649 hubei 同型)
- 全链首见失败形式累计 = 2 例 (653 shandong SSL handshake failure + 654 qinghai Connection reset by peer)
- 后续 655+ 若再发现新失败形式, 沿用本表登记 (per docs/77 §5.2 BLOCKED 留痕口径 + 654 §5.3 失败形式库)

### 5.4 当前未落地（红线守护）

- **Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M4.13 / M4.14 / M4.15 / M4.16 / M4.17 / M5 / M5.1 / M5.2 / M5.3 / M6** — 22 个里程碑不宣布 PASS (vs 653 时 21 个; 654 增量 = M4.17)
- O1 仍 OPEN (B路 live-candidate 仅登记, 不切换/启用)
- dbt mart flip: 60 行 demo 中仅 1 行 (nanjing + CONDITION) 真实化 pilot, O1 全量未启动
- 4 fixture 锁值永不动 (nbs = e30ee811 / nbs_live = 9232efdb / sz = 937255a5 / hb = 9056001c)
- 不动 registry.csv / mart 既有 638-653 行
- 不写 cegr.* 生产表
- chain_id 区分: 654 '_v11' ≠ 653 '_v10' ≠ 652 '_v9' ≠ 651 '_v8' ≠ 650 '_v7' ≠ 649 '_v6' ≠ 648 '_v5' ≠ 647 '_v4' ≠ 646 '_v3' ≠ 645 '_v2' ≠ 644 '_policy_detail' ≠ 643 '_govreport' ≠ 642 '_renmian' ≠ 641 '_heilongjiang'
- UUID m 段 (m02-m62) ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段
- 递补池 [EXHAUSTED]: 后续两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换
- 654-A.0 规范 v3 终极条款: status 行禁含任何具体 SHA (per 653 审计 P4-2 处置)

---

## 6. 下一步 + 不宣称 PASS

**654 完成**:

- 654-A.0 653 审计 P4×2 处置 + 规范 v3 落地: §META 五字段原子更新 (rev/status/last_delivery/last_receipt/tasking 状态行与 cc_head 同 commit) + status 行禁含任何具体 SHA (终极条款) + 沿用 amend-first 规则; commit 9b54dbd (rev93)
- M4.17 政策详情 v11 西北双省 (2 首试省 (gansu + qinghai 第 21/22 样本) → **真网首试省首触发 BLOCKED_NO_POOL 双例**; chain_id='real_654_m4_17_policy_detail_v11'; UUID m 段; ≤12 HTTP total actual=4 (33% usage); gansu 412×2 + qinghai Connection reset by peer ×2 — 失败形式库第二例首见)
- retry_of=N/A lineage 全行: gansu ← N/A (无前史); qinghai ← N/A (无前史)
- **0 INSERT ROWS** (双首试省均 BLOCKED 留痕; per 654 §1.654-A.1 BLOCKED 口径)
- **首试省首触发 BLOCKED_NO_POOL 双例** (per 654 §0.14 沿用 653 §0.14 红线 14): 8 守门 PASSED (含 retry_of=N/A 守门 + 双触发守门)
- **递补池 [EXHAUSTED] 沿用 653 §0.14**: 5 候选全部 consumed; 红线 14 生效; 本次双首试省均 BLOCKED 真网首试省首触发, 池不可代换, 留痕不代换
- 已用省全集不变: 18 省 (双首试省 BLOCKED → 0 增量); gansu/qinghai 留 BLOCKED_NO_POOL 痕迹, actual_province=NULL
- evidence_pack × 1 + docs/reports × 1 + docs/78 §1-§6 + docs/77 既有正文零改动 (行内 append tailnote 仅限 P4 typo) 全部落地
- **≥200 pytest green** (M4.17 新 ≥8 + 653 回归 192 + 期望 ≥200; ≥196 底限 +2%)
- backfill 完整性三齐 (per 651 审计 P4 + 652 审计 P4-A.0 规范 v2 + 653 审计 P4×2 + 654-A.0 规范 v3 + 654 任务书 §C)

**不宣布** Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M4.13 / M4.14 / M4.15 / M4.16 / M4.17 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS (沿用红线)。

**O1 仍 OPEN** — B路 live-candidate 仅登记, 不切换/启用; 等用户/架构师裁定。

---

— End 78 — M4.17 v11 西北双省 spike 审查 20260902 —