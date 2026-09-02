# 654 — M4.17 政策详情 v11 西北双省 spike 回执 (架构师级; 2026-09-02)

> **刀号**: 654
> **Milestone**: M4.17（沿用 642-653 spike 模式；spike 第 13 次扩展；西北五省区叙事收官）
> **类型**: 架构师级回执（per 654 任务书 §1.654-C）
> **日期**: 2026-09-02
> **前置**: 653 DELIVERED + 审计 **PASS（有限通过）** + 654 任务书签发 + 654-A.0 规范 v3 落地（commit 9b54dbd; rev93; §META 五字段原子更新 + status 行禁含任何具体 SHA 终极条款 + 沿用 amend-first）+ 653 §0.14 红线 14 e2e 验证模板 + 递补池 [EXHAUSTED]（沿用 653）

---

## 1. 任务落地清单 (deliverables)

| # | 路径 | 类型 | 状态 | 说明 |
|---|---|---|---|---|
| 1 | `scripts/fetch_m4_17_policy_detail_v11_2024.py` | fetch 脚本 | DONE | 双首试省 (gansu + qinghai 第 21/22 样本); SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED'; verdict 分支 BLOCKED_NO_POOL + blocked_reason + RETRY_OF_NOTES 双首试省 retry_of=N/A 注解 (per 654 §0.14 无前史) |
| 2 | `scripts/seed_m4_17_policy_detail_real_v11.sql` | seed SQL | DONE | **0 INSERT ROWS** (双首试省均 BLOCKED 留痕; lineage / chain_id / retry_of=N/A 信息保留在 evidence + docs/78 + receipt) |
| 3 | `evidence_pack/m4_17_policy_detail_real_v11_20260902.json` | 主 evidence | DONE | 真网首试省首触发双 BLOCKED_NO_POOL; blocked_no_pool_count=2; fetch_status=ALL_BLOCKED_NO_POOL; HTTP 4/12 = 33% usage; substitute_used=0; distinct_shas=[]; retry_of_annotation 双首试省 N/A 注解 |
| 4 | `docs/78-m4-17-policy-detail-real-v11-20260902.md` | 架构师级审查 | DONE | §1-§6; §2 首试省 BLOCKED 留痕登记表 (4 实现位置 + 8 守门); §3.2 西北五省区叙事收官表 (XINJIANG/NEIMENGGU/SHAANXI/GANSU/QINGHAI); §4 chain_id 区分 17 真实化刀 + UUID 严格递增至 m 段 + 累 [BLOCKED_NO_POOL] 触发事件计数 (638-654); §5.3 失败形式库登记 (qinghai Connection reset by peer 全链第二例首见) |
| 5 | `docs/reports/m4_17_policy_detail_real_v11_20260902.md` | 附属报告 | DONE | 9 节; 主 evidence methodology 引用 |
| 6 | `tests/test_m4_17_policy_detail_real_v11.py` | 测试守门 | DONE | 25 cases (target ≥8); 25/25 PASSED (≥8 要求 3.1× 达成; 8 守门覆盖 + 西北五省区收官表守门 + 失败形式库守门 + P4-A.0 规范 v3 落点守门) |
| 7 | `docs/77-m4-16-policy-detail-real-v10-20260902.md` | 既有正文 | ZERO TOUCH | per 654 §0.4 红线 4: docs/77 既有正文零改动 (无 P4 typo / 无 tailnote 追加需求) |
| 8 | `reviews/stage0-gate0-rework-2026-08-23/653-audit-654-tasking-consolidated-20260902.md` | 既有合并归档 | 既有 (PART 1) | 含 654-A.0 规范 v3 落地 + 653 审计 P4×2 处置; 不需要追加 tailnote |

---

## 2. 任务书核对（vs 654 tasking §1.654-A.0/A.1/A.2/A.3/A.4 + §1.654-B + §1.654-C）

### 2.1 vs §1.654-A.0 (653 审计 P4×2 处置 + 规范 v3)

- ✓ 规范 v3 三要点落地:
  - §META 五字段原子更新 (rev/status/last_delivery/last_receipt/tasking 状态行与 cc_head 同 commit)
  - status 行禁含任何具体 SHA 终极条款 (杜绝第四型 pin 陈旧; per 653 审计 P4-2)
  - 沿用 amend-first 规则 (per 652-A.0 P4-2 + 653-A.0 P4-A.0 规范 v2)
- ✓ commit 9b54dbd (rev93) 已落地 (含 653 审计 + 654 任务书 + §META 五字段原子更新)

### 2.2 vs §1.654-A.1 (西北双省 spike fetch)

- ✓ 双首试省 (gansu + qinghai 第 21/22 样本) 双 retry_of=N/A 全行 (双首试省无前史)
- ✓ chain_id='real_654_m4_17_policy_detail_v11' (末段 `_v11` ≠ 653 `_v10` ≠ 652 `_v9` ≠ 651 `_v8`)
- ✓ UUID m 段 (m02-m62) 8 表前缀全 distinct ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段
- ✓ SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED'（沿用 653 §0.14 红线 14 增补）
- ✓ fetch_cell 含 BLOCKED_NO_POOL verdict + blocked_reason + RETRY_OF_NOTES 双首试省 retry_of=N/A 字段
- ✓ HTTP_LIMIT=12, TIMEOUT=15

### 2.3 vs §1.654-A.2 (O1 零动作)

- ✓ O1 仍 OPEN（沿用 646-653 登记; 不切换/启用 B路 live-candidate）
- ✓ 不新增 probe, 不启用, 不改 registry/connector

### 2.4 vs §1.654-A.3 (docs/78 架构师级)

- ✓ docs/78 §1-§6 齐全
- ✓ §2 首试省 BLOCKED 留痕登记表 完整 (4 实现位置 + 8 守门含 retry_of=N/A)
- ✓ §3.2 西北五省区叙事收官表 (XINJIANG/NEIMENGGU/SHAANXI/GANSU/QINGHAI)
- ✓ §4 chain_id 区分 17 真实化刀 + UUID 严格递增至 m 段 + 累 [BLOCKED_NO_POOL] 触发事件计数 (638-654)
- ✓ §5 BLOCKED 留痕口径沿用 654 §0.14 e2e 验证机制 + 沿用 653 模板
- ✓ §5.3 失败形式库登记 (qinghai Connection reset by peer 全链第二例首见)

### 2.5 vs §1.654-A.4 (evidence ×2)

- ✓ 主 evidence: `evidence_pack/m4_17_policy_detail_real_v11_20260902.json`
- ✓ 附属报告: `docs/reports/m4_17_policy_detail_real_v11_20260902.md`
- ✓ 主 evidence methodology 含 648 P3-1 援引 + 649 P3-1 援引 + 652 §0.14 红线 14 增补 + 653 §0.14 BLOCKED_NO_POOL 留痕 e2e 验证 + 654 §0.14 沿用 653 + retry_of=N/A 注解
- ✓ 主 evidence summary 字段完整: fetch_status, fetched_count, blocked_no_pool_count, http_count, http_limit, substitute_used_count, substitute_pool_status, distinct_shas, retry_of_annotation

### 2.6 vs §1.654-B (测试)

- ✓ tests/test_m4_17_policy_detail_real_v11.py 25 cases (target ≥8; 3.1× 达成)
- ✓ 25/25 PASSED (≥200 not strictly applicable; ≥196 底限 +2% achieved; **217 passed** in 13 文件集)
- ✓ 8+ 守门覆盖: SHA/UUID m 段/chain_id v11/INSERT 三态口径/is_demo/retry_of=N/A 落地/docs/78 六节/BLOCKED 分支+字段/P4-A.0 规范 v3 落点/西北五省区收官表/失败形式库登记

### 2.7 vs §1.654-C (回执 + 7 commits + 双推 + rev94)

- ✓ 本回执（654-stage0-cc-m4-17-v11-northwest-receipt-20260902.md）
- 待办: 7 commits + 双推 + rev93→rev94 + backfill 三齐 + §NOW 收口（架构师已落地全部 uncommitted files; 等 user 授权 commit）

---

## 3. 实测终态 vs 任务书规划

| 维度 | 规划 | 实测 | delta |
|---|---|---|---|
| 双首试省 | gansu + qinghai | gansu + qinghai | 一致 |
| 双首试省 verdict | 双 REACHABLE / 任一 BLOCKED / 双 BLOCKED (三态合法) | **双 BLOCKED_NO_POOL** (真网首试省首触发双例) | 双 BLOCKED 路径 |
| gansu 形 | 无前史首试 | **412×2** (同 649 hubei 412×2 史, 但 retry_of=N/A 首试省不引用) | 不撞史引用, 但仍 BLOCKED |
| qinghai 形 | 无前史首试 | **Connection reset by peer ×2 (0/0)** (curl recv failure, 全链第二例首见失败形式) | 不撞史, 但仍 BLOCKED |
| INSERT ROWS | 16 (双 REACHABLE) 或 0 (双 BLOCKED) | **0 INSERT ROWS** (双 BLOCKED 口径; per 654 §1.654-A.1) | 0 = 0 |
| NEW SHA | 2 (双 REACHABLE) 或 0 (双 BLOCKED) | **0 NEW SHA** (双 BLOCKED) | 0 = 0 |
| HTTP | ≤12 (2-4 actual) | **4/12 = 33% usage** | 4 vs ≤12 |
| blocked_no_pool_count | 0/1/2 (any) | **2** (双首试省均 BLOCKED 真网首试省首触发) | 2 |
| substitute_used_count | 0 (红线 14) | **0** | 一致 |
| 已用省增量 | 0/1/2 | **0** (双 BLOCKED → actual_province=NULL) | 0 |
| 已用省全集 | 18 省不变 | **18 省不变** | 一致 |
| 西北五省区收官 | GANSU/QINGHAI BLOCKED + XINJIANG/NEIMENGGU/SHAANXI REACHABLE | 一致 (3 REACHABLE + 2 BLOCKED 双首试省首触发) | 收官 |

---

## 4. 三层交叉验证 (双 BLOCKED 双 retry_of=N/A)

### 4.1 retry_of lineage 区分性 (vs 653 双 retry_of)

- **gansu**: retry_of=N/A (无前史首试省) — 与 653 shandong retry_of=647 形成对照 (653 有前史, 654 无前史)
- **qinghai**: retry_of=N/A (无前史首试省) — 与 653 hubei retry_of=649 形成对照 (653 有前史, 654 无前史)
- **654 vs 653 retry_of 全行口径统一**: 有前史必填具体刀号 (retry_of=649); 无前史首试省填 N/A (retry_of=N/A)
- 全 chain retry_of 字段演进: 652 (无 retry_of 注解 — 双样本均无前史 REACHABLE) → 653 (双 retry_of — 双样本均前史 BLOCKED) → **654 (双 retry_of=N/A — 双样本均首试省 BLOCKED)**

### 4.2 SHA 区分性

```
654 (双 BLOCKED) → 0 NEW SHA (无 REACHABLE) → 总 SHA 不变 31
654 ≠ 653 (0 NEW SHA) ≠ 652 `21c8211b / da1d4104` ≠ 651 `9d0ad78a / f58a3384` ≠ 650 `5c5b1295 / def18a2f` ≠ 649 `b22d1fb4 / a1e49a91` ≠ 648 `4006439e / a06e174f` ≠ 647 `8016ef08 / 56481050` ≠ 646 `fceb8c0a / 49eed23e` ≠ 645 `6237cd48 / dfa38998 / bd4c4c51 / f33eba53` ≠ 644 `bad8be51 / dfa38998 / f33eba53` ≠ 643 `e68099df / 63109491 / 93fe23b3` ≠ 642 `cd6aff30 / 4349ee0f / fede03ba` ≠ 641 `26e5379d...` ✓ (无新 SHA 加入)
```

### 4.3 BLOCKED 留痕区分性 (vs 651/652/653)

- **651 双 REACHABLE** (shaanxi/sichuan fallback #1 REACHABLE)
- **652 双 REACHABLE** (xinjiang fallback #1 + nei_menggu 首选); BLOCKED_NO_POOL 分支代码 e2e 可达, 但本次未触发
- **653 双 BLOCKED_NO_POOL 真网首次双触发** (shandong SSL handshake failure + hubei 412×2); retry_of 全行
- **654 双 BLOCKED_NO_POOL 真网首试省首触发双例** (gansu 412×2 + qinghai Connection reset by peer ×2); retry_of=N/A 全行 (双首试省无前史)

四态区分完整:
| 刀 | 双样本 verdict | 双样本 retry_of | 区分性 |
|---|---|---|---|
| 651 | 双 REACHABLE | N/A | 双 fallback #1 REACHABLE |
| 652 | 双 REACHABLE | N/A | 双 REACHABLE; BLOCKED 分支 e2e 可达但未触发 |
| 653 | 双 BLOCKED_NO_POOL | retry_of=647 + retry_of=649 | 真网首次双触发 (双样本均有前史 BLOCKED) |
| **654** | **双 BLOCKED_NO_POOL** | **retry_of=N/A + retry_of=N/A** | **真网首试省首触发双例** (双样本均首试省无前史 BLOCKED) |

---

## 5. 累 [BLOCKED_NO_POOL] 触发事件计数 (沿用 653 §2.3 模板)

| 刀 | 累计触发次数 | 累计 e2e 验证次数 | 备注 |
|---|---|---|---|
| 638-650 | 0 (n/a) | 0 (n/a) | BLOCKED_NO_POOL 分支不存在 |
| 651 | 0 | 0 | 分支代码首次落地; 但未触发 (双样本 REACHABLE) |
| 652 | 0 | 1 | 652 §0.14 强制 e2e 验证完成; 5 个守门 PASSED; 分支代码可达; 双样本均 REACHABLE (未触发 BLOCKED) |
| 653 | 2 (真网首次双触发) | 1 (本次双样本 BLOCKED → BLOCKED_NO_POOL 路径首次实测命中, 留痕完整 + retry_of lineage 全行) | 653 §0.14 复试 BLOCKED_NO_POOL 真网首次双触发; 8 守门 PASSED (含 retry_of 守门 + 双触发守门); shandong SSL handshake failure 0/0 + hubei 412×2 |
| **654** | **2** (真网首试省首触发双例) | **1** (本次双首试省 BLOCKED → BLOCKED_NO_POOL 路径首次实测命中 [首试省], 留痕完整 + retry_of=N/A lineage 全行) | **654 §0.14 沿用 653 §0.14 首试省首触发 BLOCKED_NO_POOL 双例**; 8 守门 PASSED (沿用 653 模板); gansu 412×2 + qinghai Connection reset by peer ×2 |

---

## 6. 654-A.0 P4-A.0 规范 v3 落地验证

### 6.1 P4-A.0 规范 v3 三要点 (per 653 审计 P4×2 教训沉淀)

- ✓ **§META 五字段原子更新**: rev / status / last_delivery / last_receipt / tasking 状态行与 cc_head 链**同 commit**更新 (杜绝 653 P4-1 回填遗漏); commit 9b54dbd (rev93) 已落地
- ✓ **status 行禁含任何具体 SHA 终极条款**: 只写"三 ref 全等〔git log -1 实测〕" (杜绝第四型 pin 陈旧; per 653 审计 P4-2)
- ✓ **沿用 652-A.0 P4-2 amend-first 规则**: 先 amend 完成再写链文本; cc_head 链 SHA 一律 `git log --format=%H -n <n>` 实测输出

### 6.2 测试守门 (tests/test_m4_17_policy_detail_real_v11.py)

- ✓ `test_p4_a0_v3_tailnote_654_a0_landed_in_653_audit_doc` (P4-A.0 规范 v3 落点守门 PASSED)
  - "654-A.0 规范 v3" 标题存在 (consolidated doc PART 1)
  - "§META 五字段原子更新" 存在
  - "status 行禁含任何具体 SHA" 终极条款存在
  - "amend-first" 沿用条款存在
- ✓ `test_654_audit_consolidated_p4x2_handling_red_line` (P4×2 处置守门 PASSED)
  - 653 审计 P4-1 + P4-2 处置存在
  - rev93 修正存在
  - 654-A.0 规范 v3 终极条款 (status 行禁含任何具体 SHA) 存在

---

## 7. 8 守门 PASSED 清单 (per 654 §0.14 沿用 653 §0.14)

| # | 守门 | 实测 | 状态 |
|---|---|---|---|
| 1 | fetch 脚本 BLOCKED_NO_POOL 分支字串守门 | verdict + blocked_reason + RETRY_OF_NOTES | PASSED |
| 2 | 主 evidence substitute_pool_status='EXHAUSTED' 守门 | summary.substitute_pool_status | PASSED |
| 3 | blocked_no_pool_count=2 真网首试省首触发双例守门 | summary.blocked_no_pool_count=2 | PASSED |
| 4 | seed 0 INSERT ROWS + retry_of=N/A 守门 | non-INSERT + retry_of=N/A | PASSED |
| 5 | P4-A.0 规范 v3 落点守门 (含 status 禁 SHA + §META 五字段 + amend-first) | consolidated doc PART 1 | PASSED |
| 6 | red_line_14 SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED' 守门 | fetch 脚本 | PASSED |
| 7 | retry_of_annotation 双首试省 N/A 注解守门 | summary + cell retry_of=N/A | PASSED |
| 8 | chain_id v11 + UUID m 段 8 表前缀守门 | evidence metadata | PASSED |
| 9 (新增) | docs/78 西北五省区叙事收官表守门 | XINJIANG/NEIMENGGU/SHAANXI/GANSU/QINGHAI | PASSED |
| 10 (新增) | docs/78 失败形式库登记 qinghai Connection reset by peer 守门 | 全链第二例首见 | PASSED |
| 11 (新增) | docs/77 既有正文零改动红线 4 守门 | docs/77 仍标 653 不含 654 | PASSED |

---

## 8. 西北五省区叙事收官 (per 654 §0 + 654-A.3 + docs/78 §3.2)

| 西北省 | 落定刀 | URL 主域 | 试点方式 | 实际 verdict | retry_of | 实际省 |
|---|---|---|---|---|---|---|
| **XINJIANG** (新疆) | 652 (M4.15 v9) | www.xinjiang.gov.cn | 首选 /zwgk/ 200 REACHABLE | REACHABLE (fallback #1) | — | XINJIANG |
| **NEI MENGGU** (内蒙古) | 652 (M4.15 v9) | www.nmg.gov.cn | 首选 /zwgk/ 200 REACHABLE | REACHABLE (首选) | — | NEI MENGGU |
| **SHAANXI** (陕西) — 邻接 | 651 (M4.14 v8) | www.shaanxi.gov.cn | 首选 /zwgk/ 404 → fallback #1 / 200 REACHABLE | REACHABLE (fallback #1) | — | SHAANXI |
| **GANSU** (甘肃) | **654 (M4.17 v11)** | www.gansu.gov.cn | 首选 /zwgk/ 412 → fallback #1 / 412 | **BLOCKED_NO_POOL** | **N/A** (无前史) | NULL |
| **QINGHAI** (青海) | **654 (M4.17 v11)** | www.qinghai.gov.cn | 首选 /zwgk/ 0 (Connection reset) → fallback #1 / 0 (Connection reset) | **BLOCKED_NO_POOL** | **N/A** (无前史) | NULL |

**西北五省区叙事收官**: XINJIANG/NEI MENGGU (652 双 REACHABLE) + SHAANXI (651 REACHABLE 邻接) + GANSU/QINGHAI (654 双首试省首触发 BLOCKED)。三 REACHABLE 落 evidence + 两 BLOCKED 留痕 (e2e 完全体沿用 653 模板, 真网首试省首触发双例)。

**注**: SHAANXI 是 651 M4.14 v8 已落定 REACHABLE (fallback #1); XINJIANG/NEI MENGGU 是 652 M4.15 v9 双 REACHABLE; GANSU/QINGHAI 是 654 M4.17 v11 双首试省 BLOCKED。**西北五省区 = 651 + 652 + 654 三刀收官** (3 REACHABLE + 2 BLOCKED 双首试省首触发)。

---

## 9. 失败形式库 (沿用 653 §5.3 模板新增 654)

| # | 刀 | 失败形式 | 样本 | http_code | 描述 |
|---|---|---|---|---|---|
| 1 | 647 | 域名错配 + 403 | shandong | 403 | 域名解析指向非政府站; 4 连 BLOCKED (双 fallback × 2) |
| 2 | 649 | 412 Precondition Failed | hubei | 412 | 服务器拒绝请求条件; 槽被代换 actual=LIAONING |
| 3 | 653 | **SSL handshake failure** (LibreSSL/3.3.6 error:1404B410) | shandong | 0 (SSL 失败) | **首见失败形式**: SSL/TLS 握手失败, curl 无法建立加密连接 |
| 4 | **654** | **Connection reset by peer** (curl recv failure) | **qinghai** | **0 (recv failure)** | **第二例首见失败形式**: 远程服务器主动重置连接; curl `Recv failure: Connection reset by peer` |
| 5 | **654** | 412 Precondition Failed (复发) | **gansu** | **412** | 同 649 hubei 412×2 史, 但 654 retry_of=N/A (首试省) |

**失败形式库累计**: 5 例 (2 例首见 + 3 例复用/复发); 全链首见失败形式累计 = **2 例** (653 SSL handshake failure + 654 Connection reset by peer)。

---

## 10. backfill 完整性三齐 (per 652 审计 P4-A.0 规范 v2 + 653 任务书 §C + 654-A.0 规范 v3)

| 簿记 | 状态 | 备注 |
|---|---|---|
| EXEC-QUEUE rev93 → rev94 | 待办 | 架构师未改 (per 红线, 由 Cursor 维护); 654-C commit 完成 + status 收口与 §NOW 同 commit 原子完成后触发 |
| cc_head rev94 链补 | 待办 | 7 commits 中 cc_head rev94 commit 完成时回填 |
| docs/78 §NOW 指针更新 | 待办 | §6 完成态写"654 DELIVERED + M4.17 全收口 + O1 仍 OPEN + 22 里程碑不宣称 PASS" |

---

## 11. 红线 1-14 全自检 (沿用 653)

| 红线 | 内容 | 654 自检 |
|---|---|---|
| 1 | 不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS | ✓ 不宣称 |
| 2 | 不补零 / 不静默硬编码 value | ✓ domain 值 NULL 透明占位 (沿用 641-653) |
| 3 | 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED; ≤12 HTTP total | ✓ 4/12 = 33% usage |
| 4 | 不改 docs/45/50/53/66/67/68/69/70/71/72/73/74/75/76/77 既有正文 — 修正项一律行内 append 尾注 | ✓ docs/77 既有正文零改动 (无 P4 typo / 无 tailnote 追加需求); docs/78 是新文档 |
| 5 | 不碰 4 fixture 锁值 | ✓ 不碰 |
| 6 | 数据源唯一 = 政府/统计局/研究机构自取; 用户零裁定 | ✓ 沿用 |
| 7 | 完成 = observation SUCCESS, 禁止 PARTIAL (特例: BLOCKED_NO_POOL 留痕合法) | ✓ 双首试省 BLOCKED 留痕 (特例合法) |
| 8 | 不新写 016 migration (沿用 009+010+014+015 lineage JSONB) | ✓ 沿用 |
| 9 | chain_id = 'real_654_m4_17_policy_detail_v11' (末段 _v11, ≠ 653 _v10 ≠ 652 _v9 ≠ 651 _v8) | ✓ |
| 10 | UUID m 段 (m02-m62, 8 表前缀全 distinct) ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 | ✓ |
| 11 | 不写 cegr.* 生产表 | ✓ 不写 |
| 12 | 既有 registry 行 SHA 零漂移; 4 fixture 字节零触碰; m2 crosscheck 报告零 diff | ✓ docs/52 零改动 |
| 13 | O1 零动作 + 附属产物指针 + 代换行标注规范 | ✓ docs/78 §1-§6 + 附属报告 + 实际省=actual_province |
| 14 | 递补池 [EXHAUSTED] + BLOCKED_NO_POOL 留痕不代换 + 5 原始候选全部 consumed | ✓ 双首试省 BLOCKED 留痕不代换 |
| 14+ | 654 §0.14 沿用 653 §0.14 首试省 BLOCKED_NO_POOL e2e 验证 (4 实现位置 + 8 守门 + 西北五省区收官表 + 失败形式库) | ✓ 双首试省首触发 + 8+ 守门 PASSED (含 retry_of=N/A 守门 + 双触发守门 + 西北五省区收官表守门 + 失败形式库守门) |

---

## 12. 不宣称 PASS

- 不宣称 Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M4.13 / M4.14 / M4.15 / M4.16 / M4.17 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线 1, 22 个里程碑不宣布; vs 653 时 21 个; 654 增量 = M4.17）
- O1 仍 OPEN (B路 live-candidate 仅登记, 不切换/启用)

---

## 13. 下一步

待 user ACK + 授权 commit:

1. delivery commit: `scripts/fetch_m4_17_policy_detail_v11_2024.py` + `scripts/seed_m4_17_policy_detail_real_v11.sql` + `evidence_pack/m4_17_policy_detail_real_v11_20260902.json` + `docs/78-m4-17-policy-detail-real-v11-20260902.md` + `docs/reports/m4_17_policy_detail_real_v11_20260902.md` + `tests/test_m4_17_policy_detail_real_v11.py`
2. cc_head rev94 commit (chain SHA 链补)
3. receipt commit: 本回执 + `reviews/stage0-gate0-rework-2026-08-23/654-stage0-cc-m4-17-v11-northwest-receipt-20260902.md`
4. backfill commit: EXEC-QUEUE rev93 → rev94 + cc_head 链补
5. §NOW commit: **status 收口与 §NOW 刷新同 commit 原子完成** (per 654-A.0 规范 v3); docs/78 §6 + reviews/00-... §NOW + cc_head 全等; "待复核/待 §C-x"字样复核后**必须清除** (此 commit 内同原子完成); **status 行禁含任何具体 SHA**
6. cc_head 链补 commit: 5+6 链 SHA 同步
7. 双推 origin + github
8. 3 ref 全等 (`git log --format=%H -n 1 origin`, `git log --format=%H -n 1 github`, 本地 HEAD)

---

— End 654 — M4.17 v11 西北双省 spike 回执 20260902 —