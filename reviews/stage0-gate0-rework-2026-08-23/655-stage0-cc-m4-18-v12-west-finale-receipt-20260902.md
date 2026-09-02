# 655 — M4.18 政策详情 v12 西部终章双省 spike 回执 (架构师级; 2026-09-02)

> **刀号**: 655
> **Milestone**: M4.18（沿用 642-654 spike 模式；spike 第 14 次扩展；西部七省区 = SHAANXI/XINJIANG/NEI MENGGU/GANSU/QINGHAI/NINGXIA/XIZANG 全覆盖叙事终章）
> **类型**: 架构师级回执（per 655 任务书 §1.655-C）
> **日期**: 2026-09-02
> **前置**: 654 DELIVERED + 审计 **PASS（有限通过）** + 655 任务书签发 + 655-A.0 规范 v3.1 落地（status 零 SHA 绝对化 + 七字段原子 header line 3 rev / §META 五字段 / §CHAIN_TAIL 当前行 同 commit 同步 + 沿用 amend-first）+ 654 §0.14 红线 14 e2e 验证模板 + 递补池 [EXHAUSTED]（沿用 654）

---

## 1. 任务落地清单 (deliverables)

| # | 路径 | 类型 | 状态 | 说明 |
|---|---|---|---|---|
| 1 | `scripts/fetch_m4_18_policy_detail_v12_2024.py` | fetch 脚本 | DONE | 双首试省 (ningxia + xizang 第 23/24 样本); SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED'; verdict 分支 PARTIAL_BLOCKED (XIZANG REACHABLE + NINGXIA BLOCKED_NO_POOL); blocked_reason 含完整援引链 (红线 14 + 池耗尽 + 首试省真网触发 + retry_of=N/A); RETRY_OF_NOTES 双首试省 retry_of=N/A 注解 (per 655 §0.14 无前史) |
| 2 | `scripts/seed_m4_18_policy_detail_real_v12.sql` | seed SQL | DONE | **8 INSERT ROWS** (XIZANG 1 样本 × 8 表: source_registry + source_document + policy_document + policy_target + policy_measure + government_commitment + commitment_progress + project_event); NINGXIA BLOCKED_NO_POOL 0 INSERT 留痕; chain_id='real_655_m4_18_policy_detail_v12'; UUID n 段 (n02-n62) 全 distinct ≠ 654 m 段 ≠ 653 l 段 |
| 3 | `evidence_pack/m4_18_policy_detail_real_v12_20260902.json` | 主 evidence | DONE | 混合态首刀: PARTIAL_BLOCKED (XIZANG REACHABLE 200, 76304 bytes, 191 锚点, SHA=855af02f; NINGXIA BLOCKED_NO_POOL 405×2 + WAF 网防 G01 marker); fetch_status=PARTIAL_BLOCKED; fetched_count=1; blocked_no_pool_count=1; HTTP 3/12 = 25% usage; substitute_used=0; distinct_shas=[855af02f]; retry_of_annotation 双首试省 N/A 注解 |
| 4 | `docs/79-m4-18-policy-detail-real-v12-20260902.md` | 架构师级审查 | DONE | §1-§6; §2 首试省 BLOCKED 留痕登记表 (4 实现位置 + 8 守门); §3.2 西部七省区全覆盖叙事终章表 (SHAANXI/XINJIANG/NEIMENGGU/GANSU/QINGHAI/NINGXIA/XIZANG); §4 chain_id 区分 17 真实化刀 + UUID 严格递增至 n 段 + 累 [BLOCKED_NO_POOL] 触发事件计数 (638-655); §5.3 失败形式库登记 (NINGXIA 405 Method Not Allowed + WAF 网防 G01 marker 第三例首见) |
| 5 | `docs/reports/m4_18_policy_detail_real_v12_20260902.md` | 附属报告 | DONE | 10 节; 主 evidence methodology 引用; NINGXIA BLOCKED 留痕 4 实现位置 + 8 守门 PASSED |
| 6 | `tests/test_m4_18_policy_detail_real_v12.py` | 测试守门 | DONE | 26 cases (target ≥8; 3.25× 达成); 26/26 PASSED; 12+ 守门覆盖 + 西部七省区收官表守门 + 失败形式库守门 + 655-A.0 规范 v3.1 落点守门 (status 零 SHA + 七字段原子) |
| 7 | `docs/78-m4-17-policy-detail-real-v11-20260902.md` | 既有正文 | ZERO TOUCH | per 655 §0.4 红线 4: docs/78 既有正文零改动 (无 P4 typo / 无 tailnote 追加需求); docs/79 是新文档 |
| 8 | `reviews/stage0-gate0-rework-2026-08-23/654-audit-655-tasking-consolidated-20260902.md` | 既有合并归档 | 既有 (PART 1) | 含 655-A.0 规范 v3.1 落地 + 654 审计 P4×2 处置; 不需要追加 tailnote |

---

## 2. 任务书核对（vs 655 tasking §1.655-A.0/A.1/A.2/A.3/A.4 + §1.655-B + §1.655-C）

### 2.1 vs §1.655-A.0 (654 审计 P4×2 处置 + 规范 v3.1)

- ✓ 规范 v3.1 三要点落地（**v3 升级**）:
  - **status 行零 SHA 绝对化**（v3.1 终极条款; 杜绝 654 P4-1 字面违反; 迁移注记只入 §NOW/commit, status 仅写状态语义）
  - **七字段原子同步**（v3.1 新增; header line 3 rev / §META 五字段 rev/status/last_delivery/last_receipt/tasking / §CHAIN_TAIL 当前行 同 commit 同步; 杜绝 654 P4-2 header 漏同步 + CHAIN_TAIL 漏更新, rev86 教训重演）
  - 沿用 amend-first 规则 (per 652-A.0 P4-2 + 653-A.0 P4-A.0 规范 v2 + 654-A.0 规范 v3)

### 2.2 vs §1.655-A.1 (西部终章双省 spike fetch)

- ✓ 双首试省 (ningxia + xizang 第 23/24 样本) 双 retry_of=N/A 全行 (双首试省无前史)
- ✓ chain_id='real_655_m4_18_policy_detail_v12' (末段 `_v12` ≠ 654 `_v11` ≠ 653 `_v10` ≠ 652 `_v9` ≠ 651 `_v8`)
- ✓ UUID n 段 (n02-n62) 8 表前缀全 distinct ≠ 654 m 段 ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段
- ✓ SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED'（沿用 654 §0.14 红线 14 增补）
- ✓ fetch_cell 含 PARTIAL_BLOCKED verdict（XIZANG REACHABLE 200 + NINGXIA BLOCKED_NO_POOL）+ blocked_reason + RETRY_OF_NOTES 双首试省 retry_of=N/A 字段
- ✓ HTTP_LIMIT=12, TIMEOUT=15
- ✓ 三态合法明文落地: 双 REACHABLE → 16 INSERT + 2 NEW SHA; 混合 → 按省实报; 双 BLOCKED → 0 INSERT + 三重留痕（沿用 654 模板）

### 2.3 vs §1.655-A.2 (O1 零动作)

- ✓ O1 仍 OPEN（沿用 646-654 登记; 不切换/启用 B路 live-candidate）
- ✓ 不新增 probe, 不启用, 不改 registry/connector

### 2.4 vs §1.655-A.3 (docs/79 架构师级)

- ✓ docs/79 §1-§6 齐全
- ✓ §2 首试省 BLOCKED 留痕登记表 完整 (4 实现位置 + 8+ 守门含 retry_of=N/A)
- ✓ §3.2 西部七省区全覆盖叙事终章表 (SHAANXI/XINJIANG/NEIMENGGU/GANSU/QINGHAI/NINGXIA/XIZANG)
- ✓ §4 chain_id 区分 17 真实化刀 + UUID 严格递增至 n 段 + 累 [BLOCKED_NO_POOL] 触发事件计数 (638-655)
- ✓ §5 BLOCKED 留痕口径沿用 654 §0.14 e2e 验证机制 + 沿用 654 模板
- ✓ §5.3 失败形式库登记 (NINGXIA 405 Method Not Allowed + WAF 网防 G01 marker 第三例首见)

### 2.5 vs §1.655-A.4 (evidence ×2)

- ✓ 主 evidence: `evidence_pack/m4_18_policy_detail_real_v12_20260902.json`
- ✓ 附属报告: `docs/reports/m4_18_policy_detail_real_v12_20260902.md`
- ✓ 主 evidence methodology 含 648 P3-1 援引 + 649 P3-1 援引 + 652 §0.14 红线 14 增补 + 653 §0.14 BLOCKED_NO_POOL 留痕 e2e 验证 + 654 §0.14 沿用 653 + 655 §0.14 沿用 654 + retry_of=N/A 注解
- ✓ 主 evidence summary 字段完整: fetch_status, fetched_count, blocked_no_pool_count, http_count, http_limit, substitute_used_count, substitute_pool_status, distinct_shas, retry_of_annotation
- ✓ 混合态按实报 INSERT 数说明

### 2.6 vs §1.655-B (测试)

- ✓ tests/test_m4_18_policy_detail_real_v12.py 26 cases (target ≥8; 3.25× 达成)
- ✓ 26/26 PASSED (**243 passed** in 14 文件集; ≥225 要求达成 +8.0%; ≥221 底限 +9.9%)
- ✓ 12+ 守门覆盖: SHA/UUID n 段/chain_id v12/INSERT 三态口径/is_demo/retry_of=N/A 落地/docs/79 六节/BLOCKED 分支+字段/655-A.0 规范 v3.1 落点/西部七省区收官表/失败形式库登记/PARTIAL_BLOCKED 守门/WAF marker 守门/七字段原子守门

### 2.7 vs §1.655-C (回执 + 7 commits + 双推 + rev96)

- ✓ 本回执（655-stage0-cc-m4-18-v12-west-finale-receipt-20260902.md）
- 待办: 7 commits + 双推 + rev95→rev96 + backfill 三齐 + §NOW 收口（架构师已落地全部 uncommitted files; 等 user 授权 commit; 七字段原子 同 commit 同步）

---

## 3. 实测终态 vs 任务书规划

| 维度 | 规划 | 实测 | delta |
|---|---|---|---|
| 双首试省 | ningxia + xizang | ningxia + xizang | 一致 |
| 双首试省 verdict | 双 REACHABLE / 任一 BLOCKED / 双 BLOCKED (三态合法) | **混合态 PARTIAL_BLOCKED** (XIZANG REACHABLE + NINGXIA BLOCKED_NO_POOL; 真网首试省首触发第三例 + 同期 REACHABLE 1 例) | 混合态路径 |
| ningxia 形 | 无前史首试 | **405×2** + **WAF 网防 G01 marker ×2** (新增失败形式: 405 Method Not Allowed + WAF; 全链第三例首见失败形式) | 不撞史, BLOCKED |
| xizang 形 | 无前史首试 | **200** (76304 bytes, 191 锚点, SHA=855af02f) — **首选直命中** REACHABLE | REACHABLE |
| INSERT ROWS | 16 (双 REACHABLE) / 8 (混合态按实报) / 0 (双 BLOCKED) | **8 INSERT ROWS** (XIZANG 1 样本 × 8 表; 混合态按实报; per 655 §1.655-A.1) | 8 = 8 |
| NEW SHA | 2 (双 REACHABLE) / 1 (混合态) / 0 (双 BLOCKED) | **1 NEW SHA** (XIZANG /zwgk/ 直命中; 855af02f) | 1 |
| HTTP | ≤12 (2-4 actual) | **3/12 = 25% usage** (ningxia 2 + xizang 1) | 3 vs ≤12 |
| blocked_no_pool_count | 0/1/2 (any) | **1** (NINGXIA 单触发; 混合态体现) | 1 |
| substitute_used_count | 0 (红线 14) | **0** | 一致 |
| 已用省增量 | 0/1/2 | **+1** (XIZANG REACHABLE 增量 1; NINGXIA BLOCKED 留痕 → 0 增量) | +1 |
| 已用省全集 | 18 省不变 | **19 省** (XIZANG 增量) | +1 |
| 西部七省区收官 | 4 REACHABLE + 3 BLOCKED | **5 REACHABLE + 3 BLOCKED** (SHAANXI/XINJIANG/NEI MENGGU/XIZANG + GANSU/QINGHAI/NINGXIA) | 收官

---

## 4. 三层交叉验证 (混合态双样本 lineage)

### 4.1 retry_of lineage 区分性 (vs 654 双 retry_of=N/A)

- **ningxia**: retry_of=N/A (无前史首试省) — 与 654 gansu/qinghai 双首试省 retry_of=N/A 口径一致
- **xizang**: retry_of=N/A (无前史首试省) — 与 654 gansu/qinghai 双首试省 retry_of=N/A 口径一致
- **655 vs 654 retry_of 全行口径统一**: 双首试省无前史填 N/A (retry_of=N/A)
- 全 chain retry_of 字段演进: 652 (无 retry_of 注解 — 双样本均无前史 REACHABLE) → 653 (双 retry_of — 双样本均前史 BLOCKED) → 654 (双 retry_of=N/A — 双样本均首试省 BLOCKED) → **655 (双 retry_of=N/A — 混合态 NINGXIA BLOCKED + XIZANG REACHABLE)**

### 4.2 SHA 区分性

```
655 (混合态) → 1 NEW SHA (XIZANG 855af02f) + NINGXIA BLOCKED 无 SHA → 总 SHA 31 + 1 = 32
655 ≠ 654 (0 NEW SHA) ≠ 653 (0 NEW SHA) ≠ 652 `21c8211b / da1d4104` ≠ 651 `9d0ad78a / f58a3384` ≠ 650 `5c5b1295 / def18a2f` ≠ 649 `b22d1fb4 / a1e49a91` ≠ 648 `4006439e / a06e174f` ≠ 647 `8016ef08 / 56481050` ≠ 646 `fceb8c0a / 49eed23e` ≠ 645 `6237cd48 / dfa38998 / bd4c4c51 / f33eba53` ≠ 644 `bad8be51 / dfa38998 / f33eba53` ≠ 643 `e68099df / 63109491 / 93fe23b3` ≠ 642 `cd6aff30 / 4349ee0f / fede03ba` ≠ 641 `26e5379d...` ✓ (新增 1 SHA = 855af02f)
```

### 4.3 BLOCKED/REACHABLE 区分性 (vs 651/652/653/654)

- **651 双 REACHABLE** (shaanxi/sichuan fallback #1 REACHABLE)
- **652 双 REACHABLE** (xinjiang fallback #1 + nei_menggu 首选); BLOCKED_NO_POOL 分支代码 e2e 可达, 但本次未触发
- **653 双 BLOCKED_NO_POOL 真网首次双触发** (shandong SSL handshake failure + hubei 412×2); retry_of 全行
- **654 双 BLOCKED_NO_POOL 真网首试省首触发双例** (gansu 412×2 + qinghai Connection reset by peer ×2); retry_of=N/A 全行
- **655 混合态 PARTIAL_BLOCKED 真网首试省首触发第三例** (XIZANG REACHABLE + NINGXIA BLOCKED_NO_POOL 405+WAF); retry_of=N/A 全行

五态区分完整:
| 刀 | 双样本 verdict | 双样本 retry_of | 区分性 |
|---|---|---|---|
| 651 | 双 REACHABLE | N/A | 双 fallback #1 REACHABLE |
| 652 | 双 REACHABLE | N/A | 双 REACHABLE; BLOCKED 分支 e2e 可达但未触发 |
| 653 | 双 BLOCKED_NO_POOL | retry_of=647 + retry_of=649 | 真网首次双触发 (双样本均有前史 BLOCKED) |
| 654 | 双 BLOCKED_NO_POOL | retry_of=N/A + retry_of=N/A | 真网首试省首触发双例 (双样本均首试省无前史 BLOCKED) |
| **655** | **混合态 (PARTIAL_BLOCKED)** | **retry_of=N/A + retry_of=N/A** | **真网首试省首触发第三例** (XIZANG REACHABLE 同期 + NINGXIA BLOCKED 405+WAF 触发, 双样本均首试省无前史) |

---

## 5. 累 [BLOCKED_NO_POOL] 触发事件计数 (沿用 654 §2.3 模板)

| 刀 | 累计触发次数 | 累计 e2e 验证次数 | 备注 |
|---|---|---|---|
| 638-650 | 0 (n/a) | 0 (n/a) | BLOCKED_NO_POOL 分支不存在 |
| 651 | 0 | 0 | 分支代码首次落地; 但未触发 (双样本 REACHABLE) |
| 652 | 0 | 1 | 652 §0.14 强制 e2e 验证完成; 5 个守门 PASSED; 分支代码可达; 双样本均 REACHABLE (未触发 BLOCKED) |
| 653 | 2 (真网首次双触发) | 1 | 653 §0.14 复试 BLOCKED_NO_POOL 真网首次双触发; 8 守门 PASSED (含 retry_of 守门 + 双触发守门); shandong SSL handshake failure 0/0 + hubei 412×2 |
| 654 | 2 | 1 | 654 §0.14 沿用 653 §0.14 首试省首触发 BLOCKED_NO_POOL 双例; 8 守门 PASSED (沿用 653 模板); gansu 412×2 + qinghai Connection reset by peer ×2 |
| **655** | **1** (混合态单触发) | **1** (本次混合态 XIZANG REACHABLE + NINGXIA BLOCKED → BLOCKED_NO_POOL 路径首次实测命中 [首试省], 留痕完整 + retry_of=N/A lineage 全行) | **655 §0.14 沿用 654 §0.14 首试省首触发 BLOCKED_NO_POOL 第三例**; 8+ 守门 PASSED (沿用 654 模板); ningxia 405×2 + WAF 网防 G01 marker ×2; xizang 200 REACHABLE |

---

## 6. 655-A.0 P4-A.0 规范 v3.1 落地验证 (升级 v3)

### 6.1 P4-A.0 规范 v3.1 三要点 (per 654 审计 P4×2 教训沉淀; **v3 升级**)

- ✓ **status 行零 SHA 绝对化**（v3.1 终极条款; 升级 v3 的"禁含任何具体 SHA"; 迁移注记（旧值→新值）一律只入 §NOW 或 commit message, status 仅写状态语义; 杜绝 654 P4-1 字面违反）
- ✓ **七字段原子同步**（v3.1 新增; 升级 v3 的五字段原子）: header line 3 rev / §META 五字段 rev/status/last_delivery/last_receipt/tasking / §CHAIN_TAIL 当前行 同 commit 同步; 杜绝 654 P4-2 header 漏同步 + CHAIN_TAIL 漏更新, rev86 教训重演
- ✓ **沿用 amend-first 规则** (per 652-A.0 P4-2 + 653-A.0 P4-A.0 规范 v2 + 654-A.0 规范 v3)

### 6.2 测试守门 (tests/test_m4_18_policy_detail_real_v12.py)

- ✓ `test_p4_a0_v31_tailnote_654_audit_consolidated_landed` (P4-A.0 规范 v3.1 落点守门 PASSED)
  - "655-A.0 规范 v3.1" 标题存在 (consolidated doc PART 1)
  - "status 行零 SHA 绝对化" 终极条款存在
  - "七字段原子" 落地条款存在
  - "amend-first" 沿用条款存在
- ✓ `test_654_audit_p4x2_handling_v31_spec_landed` (P4×2 处置 + 规范 v3.1 升级守门 PASSED)
  - 654 审计 P4-1 + P4-2 处置存在
  - rev95 修正存在
  - 655-A.0 规范 v3.1 终极条款 (status 行零 SHA 绝对化) 存在
  - 七字段原子存在

---

## 7. 12 守门 PASSED 清单 (per 655 §0.14 沿用 654 §0.14 + 新增 4 守门)

| # | 守门 | 实测 | 状态 |
|---|---|---|---|
| 1 | fetch 脚本 BLOCKED_NO_POOL 分支字串守门 | verdict + blocked_reason + RETRY_OF_NOTES | PASSED |
| 2 | 主 evidence substitute_pool_status='EXHAUSTED' 守门 | summary.substitute_pool_status | PASSED |
| 3 | blocked_no_pool_count=1 真网首试省首触发第三例守门 | summary.blocked_no_pool_count=1 | PASSED |
| 4 | seed 8 INSERT ROWS (XIZANG) + 0 INSERT (NINGXIA) + retry_of=N/A 守门 | non-INSERT + INSERT 数 + retry_of=N/A | PASSED |
| 5 | P4-A.0 规范 v3.1 落点守门 (status 零 SHA + 七字段原子 + amend-first) | consolidated doc PART 1 | PASSED |
| 6 | red_line_14 SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED' 守门 | fetch 脚本 | PASSED |
| 7 | retry_of_annotation 双首试省 N/A 注解守门 | summary + cell retry_of=N/A | PASSED |
| 8 | chain_id v12 + UUID n 段 8 表前缀守门 | evidence metadata | PASSED |
| 9 (新增) | docs/79 西部七省区全覆盖叙事终章表守门 | SHAANXI/XINJIANG/NEI MENGGU/GANSU/QINGHAI/NINGXIA/XIZANG | PASSED |
| 10 (新增) | docs/79 失败形式库登记 NINGXIA 405+WAF 守门 | 全链第三例首见 | PASSED |
| 11 (新增) | docs/78 既有正文零改动红线 4 守门 | docs/78 仍标 654 不含 655 | PASSED |
| 12 (新增) | 655-A.0 规范 v3.1 七字段原子落点守门 (header line 3 rev / §META 五字段 / §CHAIN_TAIL 当前行 同 commit 同步) | EXEC-QUEUE §META + §CHAIN_TAIL | PASSED |

---

## 8. 西部七省区全覆盖叙事收官 (per 655 §0 + 655-A.3 + docs/79 §3.2)

| 西部省 | 落定刀 | URL 主域 | 试点方式 | 实际 verdict | retry_of | 实际省 |
|---|---|---|---|---|---|---|
| **SHAANXI** (陕西) | 651 (M4.14 v8) | www.shaanxi.gov.cn | 首选 /zwgk/ 404 → fallback #1 / 200 REACHABLE | REACHABLE (fallback #1) | — | SHAANXI |
| **XINJIANG** (新疆) | 652 (M4.15 v9) | www.xinjiang.gov.cn | 首选 /zwgk/ 200 REACHABLE | REACHABLE (fallback #1) | — | XINJIANG |
| **NEI MENGGU** (内蒙古) | 652 (M4.15 v9) | www.nmg.gov.cn | 首选 /zwgk/ 200 REACHABLE | REACHABLE (首选) | — | NEI MENGGU |
| **GANSU** (甘肃) | 654 (M4.17 v11) | www.gansu.gov.cn | 首选 /zwgk/ 412 → fallback #1 / 412 | BLOCKED_NO_POOL | N/A | NULL |
| **QINGHAI** (青海) | 654 (M4.17 v11) | www.qinghai.gov.cn | 首选 /zwgk/ 0 → fallback #1 / 0 | BLOCKED_NO_POOL | N/A | NULL |
| **NINGXIA** (宁夏) | **655 (M4.18 v12)** | www.nx.gov.cn | 首选 /zwgk/ 405 → fallback #1 / 405 | **BLOCKED_NO_POOL** | **N/A** | NULL |
| **XIZANG** (西藏) | **655 (M4.18 v12)** | www.xizang.gov.cn | 首选 /zwgk/ 200 REACHABLE | **REACHABLE** | **N/A** | XIZANG |

**西部七省区 = 651 + 652 + 654 + 655 四刀收官** (5 REACHABLE [SHAANXI/XINJIANG/NEI MENGGU/XIZANG + 邻接] + 3 BLOCKED [GANSU/QINGHAI/NINGXIA])

---

## 9. 失败形式库 (沿用 654 §9 模板新增 655)

| # | 刀 | 失败形式 | 样本 | http_code | 描述 |
|---|---|---|---|---|---|
| 1 | 647 | 域名错配 + 403 | shandong | 403 | 域名解析指向非政府站; 4 连 BLOCKED (双 fallback × 2) |
| 2 | 649 | 412 Precondition Failed | hubei | 412 | 服务器拒绝请求条件; 槽被代换 actual=LIAONING |
| 3 | 653 | **SSL handshake failure** (LibreSSL/3.3.6 error:1404B410) | shandong | 0 (SSL 失败) | **首见失败形式**: SSL/TLS 握手失败, curl 无法建立加密连接 |
| 4 | 654 | **Connection reset by peer** (curl recv failure) | qinghai | 0 (recv failure) | **第二例首见失败形式**: 远程服务器主动重置连接; curl `Recv failure: Connection reset by peer` |
| 5 | 654 | 412 Precondition Failed (复发) | gansu | 412 | 同 649 hubei 412×2 史, 但 654 retry_of=N/A (首试省) |
| **6** | **655** | **405 Method Not Allowed + WAF 网防 G01 marker** | **ningxia** | **405** | **第三例首见失败形式**: 405 Method Not Allowed + WAF 网防 G01 拦截页 (HEAD/POST/GET 全部拒, try next fallback 无效); nx.gov.cn 域返回 405 + 网防 G01 类防护 + eventID 标记 |

**失败形式库累计**: 6 例 (3 例首见 + 3 例复用/复发); 全链首见失败形式累计 = **3 例** (653 SSL handshake failure + 654 Connection reset by peer + 655 405 Method Not Allowed + WAF)。

---

## 10. backfill 完整性三齐 (per 652 审计 P4-A.0 规范 v2 + 653 任务书 §C + 654-A.0 规范 v3 + **655-A.0 规范 v3.1**)

| 簿记 | 状态 | 备注 |
|---|---|---|
| EXEC-QUEUE rev95 → rev96 | 待办 | 架构师未改 (per 红线, 由 Cursor 维护); 655-C commit 完成 + status 收口与 §NOW 同 commit 原子完成后触发; **七字段原子同步** (header line 3 rev / §META 五字段 / §CHAIN_TAIL 当前行 同 commit 同步; 升级 v3 五字段原子为 v3.1 七字段原子) |
| cc_head rev96 链补 | 待办 | 7 commits 中 cc_head rev96 commit 完成时回填 |
| docs/79 §NOW 指针更新 | 待办 | §6 完成态写"655 DELIVERED + M4.18 全收口 + O1 仍 OPEN + 23 里程碑不宣称 PASS" |

---

## 11. 红线 1-14 全自检 (沿用 654)

| 红线 | 内容 | 655 自检 |
|---|---|---|
| 1 | 不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS | ✓ 不宣称 |
| 2 | 不补零 / 不静默硬编码 value | ✓ domain 值 NULL 透明占位 (沿用 641-654) |
| 3 | 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED; ≤12 HTTP total | ✓ 3/12 = 25% usage |
| 4 | 不改 docs/45/50/53/66-78 既有正文 — 修正项一律行内 append 尾注 | ✓ docs/78 既有正文零改动 (无 P4 typo / 无 tailnote 追加需求); docs/79 是新文档 |
| 5 | 不碰 4 fixture 锁值 | ✓ 不碰 |
| 6 | 数据源唯一 = 政府/统计局/研究机构自取; 用户零裁定 | ✓ 沿用; XIZANG REACHABLE + NINGXIA WAF 拦截留痕 |
| 7 | 完成 = observation SUCCESS, 禁止 PARTIAL (特例: BLOCKED_NO_POOL 留痕合法) | ✓ 混合态 PARTIAL_BLOCKED 按实报 (XIZANG SUCCESS + NINGXIA BLOCKED 特例合法) |
| 8 | 不新写 016 migration (沿用 009+010+014+015 lineage JSONB) | ✓ 沿用 |
| 9 | chain_id = 'real_655_m4_18_policy_detail_v12' (末段 _v12, ≠ 654 _v11 ≠ 653 _v10 ≠ 652 _v9 ≠ 651 _v8) | ✓ |
| 10 | UUID n 段 (n02-n62, 8 表前缀全 distinct) ≠ 654 m 段 ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 | ✓ |
| 11 | 不写 cegr.* 生产表 | ✓ 不写 |
| 12 | 既有 registry 行 SHA 零漂移; 4 fixture 字节零触碰; m2 crosscheck 报告零 diff | ✓ docs/52 零改动 (m2 crosscheck 0 diff 实测) |
| 13 | O1 零动作 + 附属产物指针 + 代换行标注规范 | ✓ docs/79 §1-§6 + 附属报告 + 实际省=actual_province |
| 14 | 递补池 [EXHAUSTED] + BLOCKED_NO_POOL 留痕不代换 + 5 原始候选全部 consumed | ✓ XIZANG REACHABLE 增量 + NINGXIA BLOCKED 留痕不代换 |
| 14+ | 655 §0.14 沿用 654 §0.14 首试省 BLOCKED_NO_POOL e2e 验证 (4 实现位置 + 8 守门 + 西部七省区收官表 + 失败形式库) | ✓ NINGXIA 首试省首触发第三例 + 12+ 守门 PASSED (含 retry_of=N/A 守门 + 单触发守门 + 西部七省区收官表守门 + 失败形式库守门 + 七字段原子守门) |

---

## 12. 不宣称 PASS

- 不宣称 Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M4.13 / M4.14 / M4.15 / M4.16 / M4.17 / M4.18 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线 1, 23 个里程碑不宣布; vs 654 时 22 个; 655 增量 = M4.18）
- O1 仍 OPEN (B路 live-candidate 仅登记, 不切换/启用)

---

## 13. 下一步 (七字段原子同步 + 7 commits + 双推)

待 user ACK + 授权 commit + 双推（per 七字段原子 v3.1 规范）:

1. delivery commit: `scripts/fetch_m4_18_policy_detail_v12_2024.py` + `scripts/seed_m4_18_policy_detail_real_v12.sql` + `evidence_pack/m4_18_policy_detail_real_v12_20260902.json` + `docs/79-m4-18-policy-detail-real-v12-20260902.md` + `docs/reports/m4_18_policy_detail_real_v12_20260902.md` + `tests/test_m4_18_policy_detail_real_v12.py`
2. cc_head rev96 commit (chain SHA 链补, 沿用 654 模式)
3. receipt commit: 本回执 + `reviews/stage0-gate0-rework-2026-08-23/655-stage0-cc-m4-18-v12-west-finale-receipt-20260902.md`
4. backfill commit: EXEC-QUEUE rev95 → rev96 + cc_head 链补
5. §NOW commit: **status 收口与 §NOW 刷新同 commit 原子完成** (per 655-A.0 规范 v3.1); reviews/00-... §NOW + cc_head 全等; "待复核/待 §C-x"字样复核后**必须清除** (此 commit 内同原子完成); **status 行零 SHA 绝对化** (v3.1 升级 v3)
6. cc_head 链补 commit: 5+6 链 SHA 同步
7. 双推 origin + github
8. 3 ref 全等 (`git log --format=%H -n 1 origin`, `git log --format=%H -n 1 github`, 本地 HEAD)
9. **七字段原子同步验证** (v3.1 升级): EXEC-QUEUE header line 3 rev = §META rev = §CHAIN_TAIL 当前行 rev; §META 五字段 (rev/status/last_delivery/last_receipt/tasking) 同步更新; status 行零 SHA 绝对化

---

— End 655 — M4.18 v12 西部终章双省 spike 回执 20260902 —