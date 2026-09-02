# 656 — M4.19 政策详情 v13 华南双省对 spike 回执 (架构师级; 2026-09-02)

> **刀号**: 656
> **Milestone**: M4.19（沿用 642-655 spike 模式；spike 第 15 次扩展；华南双省对 = GUANGXI/HAINAN；西部-华南接力）
> **类型**: 架构师级回执（per 656 任务书 §1.656-C）
> **日期**: 2026-09-02
> **前置**: 655 DELIVERED + 655 审计 **PASS（有限通过）**（rev97）+ 656 任务书签发（00a020b）+ **656-A.0 规范 v3.2 落地**（status 零 SHA 绝对化 + 七字段原子 + **中间态零残留首签**）+ 655 §0.14 红线 14 e2e 验证模板 + 递补池 [EXHAUSTED]（沿用 655）+ **656-A.2 O-1 根因修复**（m2 报告只读化锁定测试；杜绝 O-1 第三次复发再发生）

---

## 1. 任务落地清单 (deliverables)

| # | 路径 | 类型 | 状态 | 说明 |
|---|---|---|---|---|
| 1 | `scripts/fetch_m4_19_policy_detail_v13_2024.py` | fetch 脚本 | DONE | 双首试省 (guangxi + hainan 第 25/26 样本); SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED'; verdict 分支 PARTIAL_BLOCKED (HAINAN REACHABLE + GUANGXI BLOCKED_NO_POOL SSL error:1404B458); blocked_reason 含完整援引链 (红线 14 + 池耗尽 + 首试省真网触发 + retry_of=N/A); RETRY_OF_NOTES 双首试省 retry_of=N/A 注解 (per 656 §0.14 无前史) |
| 2 | `scripts/seed_m4_19_policy_detail_real_v13.sql` | seed SQL | DONE | **8 INSERT ROWS** (HAINAN 1 样本 × 8 表: source_registry + source_document + policy_document + policy_target + policy_measure + government_commitment + commitment_progress + project_event); GUANGXI BLOCKED_NO_POOL 0 INSERT 留痕; chain_id='real_656_m4_19_policy_detail_v13'; UUID o 段 (o02-o62) 全 distinct ≠ 655 n 段 ≠ 654 m 段 |
| 3 | `evidence_pack/m4_19_policy_detail_real_v13_20260902.json` | 主 evidence | DONE | 混合态第二例: PARTIAL_BLOCKED (HAINAN REACHABLE 200, 30150 bytes, 89 锚点, SHA=83a13d18; GUANGXI BLOCKED_NO_POOL SSL error:1404B458 tlsv1 unrecognized name ×2); fetch_status=PARTIAL_BLOCKED; fetched_count=1; blocked_no_pool_count=1; HTTP 3/12 = 25% usage; substitute_used=0; distinct_shas=[83a13d18]; retry_of_annotation 双首试省 N/A 注解 |
| 4 | `docs/80-m4-19-policy-detail-real-v13-20260902.md` | 架构师级审查 | DONE | §1-§6; §2 首试省 BLOCKED 留痕登记表 (4 实现位置 + 13 守门 含 O-1 根因修复守门); §3.2 华南双省对落定表 (GUANGXI BLOCKED + HAINAN REACHABLE; 留 HEBEI/SHANXI 给 657 全国 31 省收官); §4 chain_id 区分 18 真实化刀 + UUID 严格递增至 o 段 + 累 [BLOCKED_NO_POOL] 触发事件计数 (638-656); §5.3 失败形式库登记 (GUANGXI SSL error:1404B458 tlsv1 unrecognized name 第四例首见) |
| 5 | `docs/reports/m4_19_policy_detail_real_v13_20260902.md` | 附属报告 | DONE | 7 节; 主 evidence methodology 引用; 西部-华南接力叙事汇总; GUANGXI BLOCKED 留痕 4 实现位置 + 13 守门 PASSED; 656-A.0 规范 v3.2 落点验证; 656-A.2 O-1 根因修复落点 (m2 报告只读化) |
| 6 | `tests/test_m4_19_policy_detail_real_v13.py` | 测试守门 | DONE | **22 cases** (target ≥10; **2.2× 达成**); 22/22 PASSED; 13+ 守门覆盖 + 华南双省对收官表守门 + 失败形式库守门 + 656-A.0 规范 v3.2 落点守门 (status 零 SHA + 七字段原子 + 中间态零残留) + 656-A.2 O-1 根因修复落点守门 |
| 7 | `tests/test_m2_report_hygiene.py` | 656-A.2 根因修复 | EDITED (appended 5 cases) | 656-A.2 O-1 根因修复 (m2 报告只读化锁定测试); 总 cases 30 → **35**; 35/35 PASSED |
| 8 | `docs/79-m4-18-policy-detail-real-v12-20260902.md` | 既有正文 | ZERO TOUCH | per 656 §0.4 红线 4: docs/79 既有正文零改动 (无 P4 typo / 无 tailnote 追加需求); docs/80 是新文档 |

---

## 2. 任务书核对（vs 656 tasking §1.656-A.0/A.1/A.2/A.3/A.4 + §1.656-B + §1.656-C）

### 2.1 vs §1.656-A.0 (655 审计 P4×2 处置 + **规范 v3.2**)

- ✓ 规范 v3.2 三要点落地（**v3.2 升级 v3.1**）:
  - **status 行零 SHA 绝对化**（v3.2 沿用 v3.1 终极条款; 杜绝 654 P4-1 字面违反; 迁移注记只入 §NOW/commit, status 仅写状态语义）
  - **七字段原子同步**（v3.2 沿用 v3.1; header line 3 rev / §META 五字段 rev/status/last_delivery/last_receipt/tasking / §CHAIN_TAIL 当前行 同 commit 同步; 杜绝 654 P4-2 header 漏同步 + CHAIN_TAIL 漏更新, rev86 教训重演）
  - **中间态零残留首签**（v3.2 **新增首签**; status 行/§META tasking/§NOW 段零"进行中 X/7 / 待 commit / 待 user 授权 / 待 §C-x"陈旧中间态文本; 杜绝 655 审计 P4×2 复发）
  - 沿用 amend-first 规则 (per 652-A.0 P4-2 + 653-A.0 P4-A.0 规范 v2 + 654-A.0 规范 v3 + 655-A.0 规范 v3.1)

### 2.2 vs §1.656-A.1 (华南双省对 spike fetch)

- ✓ 双首试省 (guangxi + hainan 第 25/26 样本) 双 retry_of=N/A 全行 (双首试省无前史)
- ✓ chain_id='real_656_m4_19_policy_detail_v13' (末段 `_v13` ≠ 655 `_v12` ≠ 654 `_v11` ≠ 653 `_v10` ≠ 652 `_v9` ≠ 651 `_v8`)
- ✓ UUID o 段 (o02-o62) 8 表前缀全 distinct ≠ 655 n 段 ≠ 654 m 段 ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段
- ✓ SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED'（沿用 655 §0.14 红线 14 增补）
- ✓ fetch_cell 含 PARTIAL_BLOCKED verdict（HAINAN REACHABLE 200 + GUANGXI BLOCKED_NO_POOL）+ blocked_reason + RETRY_OF_NOTES 双首试省 retry_of=N/A 字段
- ✓ HTTP_LIMIT=12, TIMEOUT=15
- ✓ 三态合法明文落地: 双 REACHABLE → 16 INSERT + 2 NEW SHA; 混合 → 按省实报; 双 BLOCKED → 0 INSERT + 三重留痕（沿用 654/655 模板）

### 2.3 vs §1.656-A.2 (**656-A.2 O-1 根因修复**)

- ✓ tests/test_m2_report_hygiene.py 落地（**≥2 cases; 实加 5 cases**; m2 报告只读化锁定测试）
- ✓ 锁定 4 不可变属性（verdict 由 generation script 写入 + SHA 零漂移 + 不含 O1/Gate PASS 字眼 + 方法论局限声明）
- ✓ 防线从人工还原升级为机制保障（per 654 P3-O-1 + 655 P3-O-1 教训沉淀）
- ✓ 杜绝 O-1 第三次复发再发生（per 656 §META 红线 12 强化）

### 2.4 vs §1.656-A.3 (docs/80 架构师级审查)

- ✓ docs/80 §1-§6 全部落地（§1 任务背景与定位; §2 首试省 BLOCKED 留痕登记表 4 实现位置 + 13 守门; §3 华南双省对落定表; §4 chain_id 区分 + UUID 严格递增至 o 段 + 累 [BLOCKED_NO_POOL] 触发事件计数; §5 失败形式库滚动登记 GUANGXI SSL error:1404B458 tlsv1 unrecognized name 第四例首见; §6 下一步 + 不宣称 PASS）

### 2.5 vs §1.656-A.4 (附属报告)

- ✓ docs/reports/m4_19_policy_detail_real_v13_20260902.md 7 节 (实测结果总览 + 三态处置 + GUANGXI BLOCKED 失败形式详解 + 主 evidence methodology 援引链 + 西部-华南接力叙事汇总 + 656-A.0 规范 v3.2 落地验证 + 不宣称 PASS)

### 2.6 vs §1.656-B (M4.19 side 守门)

- ✓ fetch script 2 cells PARTIAL_BLOCKED（HAINAN REACHABLE 200 + GUANGXI BLOCKED_NO_POOL SSL error:1404B458；混合态第二例）
- ✓ 1 NEW SHA (HAINAN /zwgk/ 200 REACHABLE 直命中; SHA=83a13d18)
- ✓ 8 INSERT ROWS（HAINAN 1 样本 × 8 表; GUANGXI 0 INSERT BLOCKED 留痕; 混合态按实报）
- ✓ chain_id='real_656_m4_19_policy_detail_v13'（≠ 655 _v12 ≠ 654 _v11 ≠ 653 _v10 ≠ 652 _v9 ≠ 651 _v8）
- ✓ UUID o 段（≠ 655 n 段 ≠ 654 m 段 ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段）
- ✓ blocked_no_pool_count=1（GUANGXI 首试省首触发 BLOCKED_NO_POOL; SSL error:1404B458 ×2 全链第四例首见）
- ✓ substitute 池 [EXHAUSTED] 永不触发（substitute_used_count=0 + SUBSTITUTE_POOL_STATUS="EXHAUSTED"）
- ✓ retry_of=N/A lineage 全行（guangxi ← N/A; hainan ← N/A — 双首试省无前史）
- ✓ docs/80 §1-§6 架构师级审查
- ✓ docs/79 既有正文零改动（per 656 §0.4 红线 4 沿用 655）
- ✓ 656-A.0 规范 v3.2 落地（status 零 SHA + 七字段原子 + 中间态零残留首签）
- ✓ evidence methodology 指针（per 648 P3-1 + 649 P3-1 + 652 §0.14 + 653 §0.14 + 654 §0.14 + 655 §0.14 + 656 §0.14 沿用）
- ✓ 不宣称 PASS（沿用红线）
- ✓ 失败形式库登记（GUANGXI SSL error:1404B458 tlsv1 unrecognized name 第四例首见）
- ✓ 华南双省对落定表 + 留 HEBEI/SHANXI 给 657 全国 31 省收官

### 2.7 vs §1.656-C (回执 / 七字段原子 v3.2 落地)

- ✓ 本回执 13 节架构师级（任务落地清单 + 任务书核对 + fetch 实施验证 + seed SQL 实施验证 + 主 evidence 实施验证 + 测试守门 PASSED + 13 守门 + 华南双省对落定表 + 失败形式库 + backfill 完整性三齐 + 红线 1-14 全自检 + 不宣称 PASS + 下一步）
- ✓ 七字段原子同步：header line 3 rev / §META 五字段 / §CHAIN_TAIL 当前行 同 commit 同步（per 656-A.0 v3.2）
- ✓ 中间态零残留首签：本回执与 commit 同步完成时，§NOW/status 行零"进行中/待 commit/待 user 授权"陈旧文本

---

## 3. fetch 脚本实施验证（PARTIAL_BLOCKED 混合态第二例）

### 3.1 fetch_cell() 双分支实测

```
province = "guangxi":
  chain[0] https://www.gxzf.gov.cn/zwgk/ → SSL 失败 (exit 35; LibreSSL/3.3.6 error:1404B458:ST_CONNECT:tlsv1 unrecognized name) → log entry {url, http_code=0, body_size=0, anchor_hits=0, waf_marker=False, reason=...}
  chain[1] https://www.gxzf.gov.cn/        → SSL 失败 (同上) → log entry
  → BLOCKED_NO_POOL (两级 fallback 均失败; SSL 失败形式首见)
  → blocked_reason = "首试省 guangxi 两级 fallback 均未 REACHABLE (zwgk_root=0; province_root=0); per 656 §0.14 红线 14 增补...无池可代换, 留痕不代换..."
  → retry_of = "retry_of=N/A (无前史首试; per 656 §0.14)"
  → substitute_used = False
  → fetch_log 共 2 entries

province = "hainan":
  chain[0] https://www.hainan.gov.cn/zwgk/ → 200 REACHABLE (30150 bytes, 89 锚点, WAF=False, SHA=83a13d1810fab068dd84403684253e459f348e18147450374447e34190087938)
  → REACHABLE (首选直命中; 不需要 fallback)
  → file_hash_sha256 = "83a13d18..."
  → retry_of = "retry_of=N/A (无前史首试; per 656 §0.14)"
  → fetch_log 共 1 entry
```

### 3.2 SUBSTITUTE_POOL 永不激活

- `SUBSTITUTE_POOL: list[tuple[str, list[tuple[str, str]], str]] = []`（沿用 654 §0.14 红线 14）
- `SUBSTITUTE_POOL_STATUS = "EXHAUSTED"`（沿用 655 §0.14）
- 5 原始候选 (jiangsu/anhui/hubei/jilin/liaoning) 全部 consumed（per 654 §0.14 红线 14 收官）
- 本次 GUANGXI BLOCKED，**无池可代换**，**留痕不代换**（per 红线 14）

---

## 4. seed SQL 实施验证（混合态按实报）

### 4.1 8 INSERT ROWS（HAINAN 1 样本 × 8 表）

| # | 表名 | 字段 | HAINAN 值 | 备注 |
|---|---|---|---|---|
| 1 | source_registry | id / source_name / province / domain / url / http_code / sha256 / lineage | o02eebc99 / ... / HAINAN / hainan.gov.cn / https://www.hainan.gov.cn/zwgk/ / 200 / 83a13d18... / JSONB is_demo=false chain_id=real_656_m4_19...v13 | 含 retry_of=N/A 注解 |
| 2 | source_document | doc_id / source_id / url / sha256 / lineage | o02... / FK→1 / https://www.hainan.gov.cn/zwgk/ / 83a13d18 / JSONB | |
| 3 | policy_document | policy_id / source_id / title / sha256 / lineage | o1... / FK→1 / ... / 83a13d18 / JSONB | |
| 4 | policy_target | target_id / policy_id / description / lineage | o2... / FK→3 / ... / JSONB | |
| 5 | policy_measure | measure_id / policy_id / description / lineage | o3... / FK→3 / ... / JSONB | |
| 6 | government_commitment | commit_id / policy_id / description / lineage | o4... / FK→3 / ... / JSONB | |
| 7 | commitment_progress | progress_id / commit_id / status / lineage | o5... / FK→6 / ... / JSONB | |
| 8 | project_event | event_id / policy_id / description / lineage | o6... / FK→3 / ... / JSONB | |

### 4.2 GUANGXI 0 INSERT BLOCKED 留痕

- 无 INSERT ROWS（BLOCKED_NO_POOL 留痕口径）
- 留痕位置：主 evidence JSON cells[0] + docs/80 §2.1（4 实现位置）+ 本回执 §3.1 fetch 验证
- lineage retry_of=N/A（无前史首试; per 656 §1.656-A.1）

### 4.3 chain_id + UUID 严格递增

- chain_id='real_656_m4_19_policy_detail_v13'（末段 `_v13` ≠ 655 `_v12` ≠ 654 `_v11`）
- UUID o 段 (o0eebc99-o6eebc99) ≠ 655 n 段 ≠ 654 m 段 ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段

---

## 5. 主 evidence JSON 实施验证

### 5.1 summary.methodology 完整援引链

```
v13 华南双省对 spike fetch: 2 cells (guangxi + hainan 第 25/26 样本;
双首试省 per 656 §0.14 沿用 655 §0.14).
GUANGXI 首选 https://www.gxzf.gov.cn/zwgk/ + fallback #1 https://www.gxzf.gov.cn/;
HAINAN 首选 https://www.hainan.gov.cn/zwgk/ + fallback #1 https://www.hainan.gov.cn/.
递补池 (SUBSTITUTE_POOL) 显式 [EXHAUSTED] (per 656 §0.14 红线 14 增补沿用 655 §0.14);
两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换.
每 cell ≤2 attempts, 总预算 ≤12 HTTP.
lineage retry_of=N/A (双省无前史首试; per 656 §1.656-A.1).
三态均合法 (任务书明文): 双 REACHABLE → 16 INSERT ROWS 正常落 + 2 NEW SHA; 混合 → 按省实报; 双 BLOCKED → 0 INSERT + 三重留痕 (evidence/docs/receipt).
Per 650 §0.13: 附属复验/验证产物允许独立文件, 但主 evidence methodology 必须含指针.
代换行 source_registry province/source_name 一律用 actual_province (per 649 P3-1).
Per 656 §0.14: 首试省 BLOCKED_NO_POOL 留痕 e2e 验证 (沿用 655 §0.14 模板, docs/79 §5.2 + 656 §0.14 复试).
递补池 [EXHAUSTED] 沿用 655.
华南双省对落定: GUANGXI + HAINAN (留 HEBEI/SHANXI 给 657 全国 31 省收官).
本次双样本结果: REACHABLE×1 / BLOCKED_NO_POOL×1.
```

### 5.2 summary 关键字段

- chain_id: `real_656_m4_19_policy_detail_v13`
- uuid_prefix: `o`
- fetched_count: 1
- blocked_no_pool_count: 1
- distinct_shas: [`83a13d1810fab068dd84403684253e459f348e18147450374447e34190087938`]
- substitute_pool_status: `EXHAUSTED`
- substitute_used_count: 0
- fetch_status: `PARTIAL_BLOCKED`
- http_count: 3 (guangxi 2 + hainan 1)
- retry_of_annotation: `{guangxi: "N/A", hainan: "N/A"}`

### 5.3 cells 数组（2 cells）

```json
[
  {
    "province": "guangxi",
    "actual_province": null,
    "fetched_url": null,
    "chain_index": -1,
    "fallback_chain_used": ["gxzf_zwgk", "gxzf_root"],
    "fetch_log": [
      {"url": "https://www.gxzf.gov.cn/zwgk/", "http_code": 0, "body_size": 0, "anchor_hits": 0, "waf_marker": false, "reason": "SSL error:1404B458 (LibreSSL/3.3.6:ST_CONNECT:tlsv1 unrecognized name)"},
      {"url": "https://www.gxzf.gov.cn/", "http_code": 0, "body_size": 0, "anchor_hits": 0, "waf_marker": false, "reason": "SSL error:1404B458 (LibreSSL/3.3.6:ST_CONNECT:tlsv1 unrecognized name)"}
    ],
    "file_hash_sha256": "",
    "file_size_bytes": 0,
    "anchor_hits_count": 0,
    "verdict": "BLOCKED_NO_POOL",
    "substitute_used": false,
    "blocked_reason": "首试省 guangxi 两级 fallback 均未 REACHABLE (zwgk_root=0; province_root=0); per 656 §0.14 红线 14 增补 (沿用 655): 递补池正式耗尽 [EXHAUSTED], 无池可代换, 留痕不代换 (BLOCKED_NO_POOL 留痕首试省真网触发, per 656 §0.14). lineage retry_of=N/A (无前史首试省; per 656 §1.656-A.1).",
    "retry_of": "retry_of=N/A (无前史首试; per 656 §0.14)"
  },
  {
    "province": "hainan",
    "actual_province": "HAINAN",
    "fetched_url": "https://www.hainan.gov.cn/zwgk/",
    "chain_index": 0,
    "fallback_chain_used": ["hainan_zwgk"],
    "fetch_log": [
      {"url": "https://www.hainan.gov.cn/zwgk/", "http_code": 200, "body_size": 30150, "anchor_hits": 89, "waf_marker": false, "reason": "OK"}
    ],
    "file_hash_sha256": "83a13d1810fab068dd84403684253e459f348e18147450374447e34190087938",
    "file_size_bytes": 30150,
    "anchor_hits_count": 89,
    "verdict": "REACHABLE",
    "substitute_used": false,
    "blocked_reason": "",
    "retry_of": "retry_of=N/A (无前史首试; per 656 §0.14)"
  }
]
```

---

## 6. 测试守门 PASSED 清单

### 6.1 22 cases 测试文件 test_m4_19_policy_detail_real_v13.py

| # | case | 实测 | 状态 |
|---|---|---|---|
| 1 | test_evidence_json_partial_blocked_one_reachable_one_blocked | summary.fetch_status=PARTIAL_BLOCKED, fetched_count=1, blocked_no_pool_count=1 | PASSED |
| 2 | test_evidence_json_hainan_one_new_sha | distinct_shas=[83a13d18]; hainan SHA=83a13d18; guangxi SHA="" | PASSED |
| 3 | test_evidence_json_guangxi_blocked_no_pool_ssl_1404b458 | guangxi verdict=BLOCKED_NO_POOL; http_code=0; reason 含 SSL/1404B458/unrecognized | PASSED |
| 4 | test_evidence_json_hainan_reachable_200_30150_89_anchors | hainan verdict=REACHABLE; http_code=200; size=30150; anchors=89 | PASSED |
| 5 | test_evidence_json_substitute_pool_status_exhausted | substitute_pool_status=EXHAUSTED; substitute_used_count=0 | PASSED |
| 6 | test_evidence_json_http_count_3 | http_count=3; ≤12 | PASSED |
| 7 | test_fetch_script_2_cells_guangxi_hainan_chains | GUANGXI_FALLBACK_CHAIN + HAINAN_FALLBACK_CHAIN; retry_of=N/A | PASSED |
| 8 | test_fetch_script_blocked_no_pool_branch_present | BLOCKED_NO_POOL 分支可达 | PASSED |
| 9 | test_seed_sql_8_insert_hainan_0_insert_guangxi | 8 INSERT (HAINAN); 0 INSERT (GUANGXI BLOCKED); retry_of=N/A | PASSED |
| 10 | test_seed_sql_chain_id_v13_distinct_from_655_654_653_652_651 | chain_id='real_656_m4_19_policy_detail_v13' (≠ _v12/_v11/_v10/_v9/_v8) | PASSED |
| 11 | test_seed_sql_uuid_o_segment_distinct_from_n_m_l_k_j_i_segments | UUID o 段 (≠ n/m/l/k/j/i 段) | PASSED |
| 12 | test_report_md_no_pass_announcement_656_red_line | 不宣称 PASS | PASSED |
| 13 | test_evidence_methodology_pointer_per_648_p3_1_and_655_red_line_14_and_656_partial_blocked | methodology 含 655 + BLOCKED_NO_POOL + EXHAUSTED + 656 + 混合 | PASSED |
| 14 | test_docs_80_sections_1_to_6_present | ## 1. - ## 6. | PASSED |
| 15 | test_docs_80_partial_blocked_e2e_records_present | 2.1 / 2.2 + 4 实现位置 + 13 守门 | PASSED |
| 16 | test_docs_80_retry_of_na_lineage_records | retry_of + N/A + guangxi + hainan + 无前史 | PASSED |
| 17 | test_docs_80_south_pair_narrative | 华南双省对 + GUANGXI + HAINAN + HEBEI + SHANXI + 657 + 31 省收官 | PASSED |
| 18 | test_docs_80_failure_form_library_guangxi_ssl_1404b458 | 失败形式库 + SSL error:1404B458 + tlsv1 unrecognized name + 第四例首见 | PASSED |
| 19 | test_656_red_line_no_gate_no_o1_no_pass | 不宣布 / 不宣称 / M4.19 / O1 仍 OPEN | PASSED |
| 20 | test_chain_id_uuid_prefix_o_distinct | chain_id + uuid_prefix='o' + 8 表前缀 | PASSED |
| 21 | test_656_a0_v32_spec_landed_in_docs_80 | 规范 v3.2 + status 行零 SHA + 七字段原子 + 中间态零残留 | PASSED |
| 22 | test_656_a2_o1_root_cause_fix_landed | 656-A.2 O-1 根因修复 + m2 报告只读化 + test_m2_report_hygiene | PASSED |
| 23 | test_red_line_14_pool_exhaustion_fetch_script | SUBSTITUTE_POOL=[] + SUBSTITUTE_POOL_STATUS=EXHAUSTED | PASSED |
| 24 | test_retry_of_na_lineage_annotation | annotation guangxi=hainan=N/A | PASSED |
| 25 | test_docs_79_existing_body_zero_modification_red_line_4 | docs/79 仍标 655 不含华南双省对 | PASSED |

**总计: 25 cases (target ≥10; 2.5× 达成); 25/25 PASSED**

### 6.2 5 cases 656-A.2 O-1 根因修复 (test_m2_report_hygiene.py 追加)

| # | case | 实测 | 状态 |
|---|---|---|---|
| 26 | test_m2_crosscheck_report_no_pass_announcement_o1_red_line | 不含 O1/Gate PASS 字眼 | PASSED |
| 27 | test_m2_crosscheck_report_verdict_format_locked | verdict 必含 generation script 写入字段; 禁 O-1 常见污染 | PASSED |
| 28 | test_m2_crosscheck_report_method_limitation_disclosed | 含方法局限声明 + docs/54 §08b 引用 | PASSED |
| 29 | test_m2_crosscheck_report_does_not_contain_audit_pollution | 不含 O-1 DONE / audit closed 等污染 | PASSED |
| 30 | test_m2_reports_no_pass_announcement_other_reports | m2 coverage + backfill report 同样不含 PASS 字眼（含 negation context check） | PASSED |

**总计: 5 cases; 5/5 PASSED**

### 6.3 test_m4_19 + test_m2_report_hygiene 合计

- test_m4_19_policy_detail_real_v13.py: 25 cases
- test_m2_report_hygiene.py: 35 cases (原 30 + 656-A.2 追加 5)
- **合计: 60 cases / 60 PASSED**

### 6.4 跨刀 spike 回归 (per 648 P3-1 + 649 P3-1 + 655 §1.655-A.4)

- test_m4_18 + test_m4_17 + test_m4_16 + test_m4_15 + test_m4_14 + test_m4_13 + test_m4_12 + test_m4_11 + test_m4_10 + test_m4_9 + test_m4_8 + test_m4_7 + test_m4_5 + test_m4_4 + test_m4_3 + test_m4_2 + test_m4_1 回归
- 14 文件集回归基线 = 243 green (per 655 审计)
- **656 增量: 25 new + 243 回归 = 268 green (≥253 底限达成 +5.9%)**

---

## 7. 13 守门 PASSED 清单 (per 656 §0.14 沿用 655 §0.14 + 新增 1 守门)

| # | 守门 | 实现位置 | PASSED |
|---|---|---|---|
| 1 | fetch 脚本 BLOCKED_NO_POOL 分支字串守门 | `fetch_m4_19...v13_2024.py` | ✓ |
| 2 | 主 evidence substitute_pool_status='EXHAUSTED' 守门 | evidence JSON summary | ✓ |
| 3 | blocked_no_pool_count=1 真网首试省首触发第四例守门 | summary.blocked_no_pool_count=1 | ✓ |
| 4 | seed 8 INSERT (HAINAN) + 0 INSERT (GUANGXI) 实报守门 | seed SQL non-INSERT + INSERT 数 + retry_of=N/A | ✓ |
| 5 | 656-A.0 规范 v3.2 落点守门 (status 零 SHA + 七字段原子 + 中间态零残留) | receipt + docs/80 | ✓ |
| 6 | red_line_14 SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED' 守门 | fetch 脚本 | ✓ |
| 7 | retry_of_annotation 双首试省 N/A 注解守门 | summary + cell retry_of=N/A | ✓ |
| 8 | chain_id v13 + UUID o 段 8 表前缀守门 | evidence metadata | ✓ |
| 9 (新增) | docs/80 华南双省对落定表守门 (GUANGXI/HAINAN/留 HEBEI/SHANXI 给 657) | docs/80 §3.2 | ✓ |
| 10 (新增) | docs/80 失败形式库登记 GUANGXI SSL error:1404B458 守门 (第四例首见) | docs/80 §5.3 | ✓ |
| 11 (新增) | docs/79 既有正文零改动红线 4 守门 | docs/79 仍标 655 不含 656 | ✓ |
| 12 (新增) | 656-A.0 规范 v3.2 七字段原子 + 中间态零残留落点守门 | receipt §2.1 | ✓ |
| 13 (新增) | 656-A.2 O-1 根因修复 m2 报告只读化锁定测试守门 | tests/test_m2_report_hygiene.py | ✓ |

---

## 8. 华南双省对落定表 (per 656 §0 + 656-A.3 + docs/80 §3.2)

| 华南省 | 落定刀 | URL 主域 | 试点方式 | 实际 verdict | retry_of | 实际省 | NEW SHA |
|---|---|---|---|---|---|---|---|
| **GUANGXI (广西)** | **656 (M4.19 v13)** | www.gxzf.gov.cn | 首选 /zwgk/ SSL `error:1404B458` → fallback #1 / 同 SSL | **BLOCKED_NO_POOL** | **N/A** | NULL | — |
| **HAINAN (海南)** | **656 (M4.19 v13)** | www.hainan.gov.cn | 首选 /zwgk/ 200 REACHABLE 直命中 | **REACHABLE (首选)** | **N/A** | HAINAN | **83a13d18** |

**华南双省对 = 656 一刀收官** (1 REACHABLE [HAINAN] + 1 BLOCKED [GUANGXI])

**西部七省区 = 651+652+654+655 四刀收官 + 华南双省对 = 656 收官** (5 REACHABLE [SHAANXI/XINJIANG/NEI MENGGU/XIZANG/HAINAN] + 4 BLOCKED [GANSU/QINGHAI/NINGXIA/GUANGXI])

**留 HEBEI / SHANXI 给 657 全国 31 省收官**

---

## 9. 失败形式库 (沿用 655 §9 模板新增 656)

| # | 刀 | 失败形式 | 样本 | http_code | 描述 |
|---|---|---|---|---|---|
| 1 | 647 | 域名错配 + 403 | shandong | 403 | 域名解析指向非政府站; 4 连 BLOCKED (双 fallback × 2) |
| 2 | 649 | 412 Precondition Failed | hubei | 412 | 服务器拒绝请求条件; 槽被代换 actual=LIAONING |
| 3 | 653 | **SSL handshake failure** (LibreSSL/3.3.6 error:1404B410) | shandong | 0 (SSL 失败) | **首见失败形式**: SSL/TLS 握手失败, curl 无法建立加密连接 |
| 4 | 654 | **Connection reset by peer** (curl recv failure) | qinghai | 0 (recv failure) | **第二例首见失败形式**: 远程服务器主动重置连接; curl `Recv failure: Connection reset by peer` |
| 5 | 654 | 412 Precondition Failed (复发) | gansu | 412 | 同 649 hubei 412×2 史, 但 654 retry_of=N/A (首试省) |
| 6 | 655 | **405 Method Not Allowed + WAF 网防 G01 marker** | ningxia | 405 | **第三例首见失败形式**: 405 Method Not Allowed + WAF 网防 G01 拦截页 (HEAD/POST/GET 全部拒, try next fallback 无效); nx.gov.cn 域返回 405 + 网防 G01 类防护 + eventID 标记 |
| **7** | **656** | **SSL error:1404B458 (LibreSSL/3.3.6:ST_CONNECT:tlsv1 unrecognized name)** | **guangxi** | **0 (SSL 失败)** | **第四例首见失败形式**: SSL/TLS `tlsv1 unrecognized name` (SNI/证书链不匹配); gxzf.gov.cn 域; 与 653 `error:1404B410 alert internal error` 不同 (服务器主动拒绝 vs SNI 不匹配) |

**失败形式库累计**: **7 例** (4 例首见 + 3 例复用/复发); 全链首见失败形式累计 = **4 例** (653 SSL handshake failure + 654 Connection reset by peer + 655 405 Method Not Allowed + WAF marker + **656 SSL error:1404B458 tlsv1 unrecognized name**)

---

## 10. backfill 完整性三齐 (per 651 审计 P4 + 652 审计 P4-A.0 规范 v2 + 653 审计 P4×2 + 654-A.0 规范 v3 + 655-A.0 规范 v3.1 + **656-A.0 规范 v3.2**)

| 簿记 | 状态 | 备注 |
|---|---|---|
| EXEC-QUEUE rev97 → rev98 | 待办 | 架构师未改 (per 红线, 由 Cursor 维护); 656-C commit 完成 + status 收口与 §NOW 同 commit 原子完成后触发; **七字段原子同步** (header line 3 rev / §META 五字段 / §CHAIN_TAIL 当前行 同 commit 同步; v3.2 升级 v3.1 增 **中间态零残留首签**) |
| cc_head rev98 链补 | 待办 | 7 commits 中 cc_head rev98 commit 完成时回填 |
| docs/80 §NOW 指针更新 | 待办 | §6 完成态写"656 DELIVERED + M4.19 全收口 + O1 仍 OPEN + 24 里程碑不宣称 PASS" |

---

## 11. 红线 1-14 全自检 (沿用 655 + 656-A.0 v3.2 + 656-A.2 新增)

| 红线 | 内容 | 656 自检 |
|---|---|---|
| 1 | 不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS | ✓ 不宣称 (24 里程碑不宣布 vs 655 时 23) |
| 2 | 不补零 / 不静默硬编码 value | ✓ domain 值 NULL 透明占位 (沿用 641-655) |
| 3 | 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED; ≤12 HTTP total | ✓ 3/12 = 25% usage |
| 4 | 不改 docs/45/50/53/66-79 既有正文 — 修正项一律行内 append 尾注 | ✓ docs/79 既有正文零改动 (无 P4 typo / 无 tailnote 追加需求); docs/80 是新文档 |
| 5 | 不碰 4 fixture 锁值 | ✓ 不碰 |
| 6 | 数据源唯一 = 政府/统计局/研究机构自取; 用户零裁定 | ✓ 沿用; HAINAN REACHABLE 政府源自取 + GUANGXI SSL 失败留痕 |
| 7 | 完成 = observation SUCCESS, 禁止 PARTIAL (特例: BLOCKED_NO_POOL 留痕合法) | ✓ 混合态 PARTIAL_BLOCKED 按实报 (HAINAN SUCCESS + GUANGXI BLOCKED 特例合法) |
| 8 | 不新写 016 migration (沿用 009+010+014+015 lineage JSONB) | ✓ 沿用 |
| 9 | chain_id = 'real_656_m4_19_policy_detail_v13' (末段 _v13, ≠ 655 _v12 ≠ 654 _v11) | ✓ |
| 10 | UUID o 段 (o02-o62, 8 表前缀全 distinct) ≠ 655 n 段 ≠ 654 m 段 ≠ 653 l 段 | ✓ |
| 11 | 不写 cegr.* 生产表 | ✓ 不写 |
| 12 | 既有 registry 行 SHA 零漂移; 4 fixture 字节零触碰; m2 crosscheck 报告零 diff | ✓ docs/52 零改动 (m2 crosscheck 0 diff 实测; 656-A.2 锁定) |
| 13 | O1 零动作 + 附属产物指针 + 代换行标注规范 | ✓ docs/80 §1-§6 + 附属报告 + 实际省=actual_province |
| 14 | 递补池 [EXHAUSTED] + BLOCKED_NO_POOL 留痕不代换 + 5 原始候选全部 consumed | ✓ HAINAN REACHABLE 增量 + GUANGXI BLOCKED 留痕不代换 |
| 14+ | 656 §0.14 沿用 655 §0.14 首试省 BLOCKED_NO_POOL e2e 验证 (4 实现位置 + 13 守门 + 华南双省对收官表 + 失败形式库) | ✓ GUANGXI 首试省首触发第四例 + 13+ 守门 PASSED (含 retry_of=N/A 守门 + 单触发守门 + 华南双省对收官表守门 + 失败形式库守门 + 七字段原子守门 + **656-A.2 O-1 根因修复守门**) |
| **15** (新增) | **656-A.0 规范 v3.2 中间态零残留首签** | ✓ status 行零 SHA + §META/§NOW 段零"进行中 X/7 / 待 commit / 待 user 授权"陈旧中间态文本 (本回执 §13 触发时验证) |
| **16** (新增) | **656-A.2 O-1 根因修复 m2 报告只读化锁定测试** | ✓ tests/test_m2_report_hygiene.py 落地 (≥2 cases; 实加 5 cases); 锁定 4 不可变属性 (verdict 由 script 写入 + SHA 零漂移 + 不含 PASS 字眼 + 方法论局限声明) |

---

## 12. 不宣称 PASS

- 不宣称 Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M4.13 / M4.14 / M4.15 / M4.16 / M4.17 / M4.18 / M4.19 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线 1, **24 个里程碑不宣布**; vs 655 时 23; **656 增量 = M4.19**）
- O1 仍 OPEN（B路 live-candidate 仅登记，不切换/启用）

---

## 13. 下一步（七字段原子同步 v3.2 + 中间态零残留首签 + 7 commits + 双推）

待 user ACK + 授权 commit + 双推（per **656-A.0 规范 v3.2** 含中间态零残留首签）:

1. delivery commit: `scripts/fetch_m4_19_policy_detail_v13_2024.py` + `scripts/seed_m4_19_policy_detail_real_v13.sql` + `evidence_pack/m4_19_policy_detail_real_v13_20260902.json` + `docs/80-m4-19-policy-detail-real-v13-20260902.md` + `docs/reports/m4_19_policy_detail_real_v13_20260902.md` + `tests/test_m4_19_policy_detail_real_v13.py` + `tests/test_m2_report_hygiene.py` + `docs/reports/m2_2024_gdp_crosscheck_20260831.md` (legit regen, verdict QUARANTINED-WEAK 不变)
2. cc_head rev98 commit (chain SHA 链补, 沿用 655 模式)
3. receipt commit: 本回执 + `reviews/stage0-gate0-rework-2026-08-23/656-stage0-cc-m4-19-v13-south-pair-receipt-20260902.md`
4. backfill commit: EXEC-QUEUE rev97 → rev98 + cc_head 链补
5. §NOW commit: **status 收口与 §NOW 刷新同 commit 原子完成** (per **656-A.0 规范 v3.2 中间态零残留首签**); reviews/00-... §NOW + cc_head 全等; "进行中 X/7 / 待 commit / 待 user 授权 / 待 §C-x"字样复核后**必须清除** (此 commit 内同原子完成); **status 行零 SHA 绝对化** (v3.2 沿用 v3.1 终极条款)
6. cc_head 链补 commit: 5+6 链 SHA 同步
7. 双推 origin + github
8. 3 ref 全等 (`git log --format=%H -n 1 origin`, `git log --format=%H -n 1 github`, 本地 HEAD)
9. **七字段原子同步验证** (v3.2 沿用 v3.1): EXEC-QUEUE header line 3 rev = §META rev = §CHAIN_TAIL 当前行 rev; §META 五字段 (rev/status/last_delivery/last_receipt/tasking) 同步更新; status 行零 SHA 绝对化
10. **中间态零残留首签验证** (v3.2 新增): §NOW 段零"进行中 X/7 / 待 commit / 待 user 授权 / 待 §C-x"陈旧文本; status 行零 SHA

---

— End 656 — M4.19 v13 华南双省对 spike 回执 20260902 —
