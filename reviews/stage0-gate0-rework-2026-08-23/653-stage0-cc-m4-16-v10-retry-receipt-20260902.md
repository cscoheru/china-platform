# 653 — M4.16 政策详情 v10 双复试 spike 回执 (架构师级; 2026-09-02)

> **刀号**: 653
> **Milestone**: M4.16（沿用 642-652 spike 模式；spike 第 12 次扩展）
> **类型**: 架构师级回执（per 653 任务书 §1.653-C）
> **日期**: 2026-09-02
> **前置**: 652 DELIVERED + 审计 **PASS（有限通过）**（PART 1）+ 653 任务书签发 + 653-A.0 P4-A.0 规范 v2 落地（commit af7a95c; docs/76 §6.1 + 652 receipt §RED_LINE_AUDIT.1 tailnote）+ 652 §0.14 红线 14 e2e 验证模板 + 递补池 [EXHAUSTED]（沿用 652）

---

## 1. 任务落地清单 (deliverables)

| # | 路径 | 类型 | 状态 | 说明 |
|---|---|---|---|---|
| 1 | `scripts/fetch_m4_16_policy_detail_v10_2024.py` | fetch 脚本 | DONE | 双样本 (shandong + hubei 第 19/20 样本); SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED'; verdict 分支 BLOCKED_NO_POOL + blocked_reason + RETRY_OF_NOTES 双样本 retry_of 注解 |
| 2 | `scripts/seed_m4_16_policy_detail_real_v10.sql` | seed SQL | DONE | **0 INSERT ROWS** (双样本均 BLOCKED 留痕; lineage / chain_id / retry_of 信息保留在 evidence + docs/77 + receipt) |
| 3 | `evidence_pack/m4_16_policy_detail_real_v10_20260902.json` | 主 evidence | DONE | 真网首次双触发 BLOCKED_NO_POOL; blocked_no_pool_count=2; fetch_status=ALL_BLOCKED_NO_POOL; HTTP 4/12 = 33% usage; substitute_used=0; distinct_shas=[]; retry_of_annotation 双样本注解 |
| 4 | `docs/77-m4-16-policy-detail-real-v10-20260902.md` | 架构师级审查 | DONE | §1-§6; §2 复试 BLOCKED 留痕登记表 (4 实现位置 + 8 守门); §4 chain_id 区分 16 真实化刀 + UUID 严格递增至 l 段 + 累 [BLOCKED_NO_POOL] 触发事件计数 |
| 5 | `docs/reports/m4_16_policy_detail_real_v10_20260902.md` | 附属报告 | DONE | 9 节; 主 evidence methodology 引用 |
| 6 | `tests/test_m4_16_policy_detail_real_v10.py` | 测试守门 | DONE | 21 cases (target ≥8); 21/21 PASSED |
| 7 | `docs/76-m4-15-policy-detail-real-v9-20260902.md` | tailnote 落地 | DONE (commit af7a95c) | §6.1 653-A.0 P4-A.0 规范 v2 落地 (status 收口与 §NOW 同 commit 原子完成 + "待复核/待 §C-x"字样复核后必须清除 + 沿用 P4-2 amend-first 规则) |
| 8 | `reviews/stage0-gate0-rework-2026-08-23/652-stage0-cc-m4-15-v9-blocked-spike-receipt-20260902.md` | tailnote 落地 | DONE (commit af7a95c) | §RED_LINE_AUDIT.1 653-A.0 P4-A.0 规范 v2 落地 |

---

## 2. 任务书核对（vs 653 tasking §1.653-A.0/A.1/A.2/A.3/A.4 + §1.653-B + §1.653-C）

### 2.1 vs §1.653-A.0 (P4-A.0 规范 v2)

- ✓ docs/76 §6.1 tailnote 落地（status 收口与 §NOW 同 commit 原子完成）
- ✓ 652 receipt §RED_LINE_AUDIT.1 tailnote 落地
- ✓ commit af7a95c 已落地（commit hash: af7a95c; HEAD = af7a95c 本地）

### 2.2 vs §1.653-A.1 (双复试 spike fetch)

- ✓ 双样本 (shandong + hubei 第 19/20 样本) 双 retry_of 全行 (shandong ← 647 BLOCKED×4; hubei ← 649 substituted actual=LIAONING)
- ✓ chain_id='real_653_m4_16_policy_detail_v10' (末段 `_v10` ≠ 652 `_v9` ≠ 651 `_v8`)
- ✓ UUID l 段 (l02-l62) 8 表前缀全 distinct ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段
- ✓ SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED'（沿用 652 §0.14 红线 14 增补）
- ✓ fetch_cell 含 BLOCKED_NO_POOL verdict + blocked_reason + RETRY_OF_NOTES 双样本 retry_of 字段
- ✓ HTTP_LIMIT=12, TIMEOUT=15

### 2.3 vs §1.653-A.2 (O1 零动作)

- ✓ O1 仍 OPEN（沿用 646-652 登记; 不切换/启用 B路 live-candidate）
- ✓ 不新增 probe, 不启用, 不改 registry/connector

### 2.4 vs §1.653-A.3 (docs/77 架构师级)

- ✓ docs/77 §1-§6 齐全
- ✓ §2 复试 BLOCKED 留痕登记表 完整 (4 实现位置 + 8 守门含 retry_of)
- ✓ §4 chain_id 区分 16 真实化刀 + UUID 严格递增至 l 段 + 累 [BLOCKED_NO_POOL] 触发事件计数 (638-653)
- ✓ §5 BLOCKED 留痕口径沿用 653 §0.14 e2e 验证机制 + 复试模板

### 2.5 vs §1.653-A.4 (evidence ×2)

- ✓ 主 evidence: `evidence_pack/m4_16_policy_detail_real_v10_20260902.json`
- ✓ 附属报告: `docs/reports/m4_16_policy_detail_real_v10_20260902.md`
- ✓ 主 evidence methodology 含 648 P3-1 援引 + 649 P3-1 援引 + 652 §0.14 红线 14 增补 + 653 §0.14 强制 BLOCKED_NO_POOL 留痕 e2e 验证 复试 + retry_of 注解
- ✓ 主 evidence summary 字段完整: fetch_status, fetched_count, blocked_no_pool_count, http_count, http_limit, substitute_used_count, substitute_pool_status, distinct_shas, retry_of_annotation

### 2.6 vs §1.653-B (测试)

- ✓ tests/test_m4_16_policy_detail_real_v10.py 21 cases (target ≥8)
- ✓ 21/21 PASSED (≥179 not strictly applicable; ≥175 底限 +2.3% achieved)
- ✓ 8 守门覆盖: SHA/UUID l 段/chain_id v10/INSERT 两态口径/is_demo/retry_of 落地/docs/77 六节/BLOCKED 分支+字段/P4-A.0 规范 v2 落点

### 2.7 vs §1.653-C (回执 + 6 commits + 双推 + rev92)

- ✓ 本回执（653-stage0-cc-m4-16-v10-retry-receipt-20260902.md）
- 待办: 6 commits + 双推 + rev91→rev92 + backfill 三齐（架构师已落地全部 uncommitted files; 等 user 授权 commit）

---

## 3. 实测终态 vs 任务书规划

| 维度 | 规划 | 实测 | delta |
|---|---|---|---|
| 双样本 | shandong + hubei | shandong + hubei | 一致 |
| 双样本 verdict | 双 REACHABLE / 任一 BLOCKED / 双 BLOCKED (三态合法) | **双 BLOCKED_NO_POOL** (真网首次双触发) | 双 BLOCKED 路径 |
| shandong 形 | (域名错配+403) 4 连 BLOCKED 史 (per 647) | **SSL handshake failure 0/0** (新 BLOCKED 形式, 此前所有刀未见) | 不撞史, 但仍 BLOCKED |
| hubei 形 | 412×2 史 (per 649, 槽被代换 actual=LIAONING) | **412×2** (同史) | 同史, 留痕不代换 |
| INSERT ROWS | 16 (双 REACHABLE) 或 0 (双 BLOCKED) | **0 INSERT ROWS** (双 BLOCKED 口径; per 653 §1.653-A.1) | 0 = 0 |
| NEW SHA | 2 (双 REACHABLE) 或 0 (双 BLOCKED) | **0 NEW SHA** (双 BLOCKED) | 0 = 0 |
| HTTP | ≤12 (2-4 actual) | **4/12 = 33% usage** | 4 vs ≤12 |
| blocked_no_pool_count | 0/1/2 (any) | **2** (双样本均 BLOCKED 真网首触发) | 2 |
| substitute_used_count | 0 (红线 14) | **0** | 一致 |
| 已用省增量 | 0/1/2 | **0** (双 BLOCKED → actual_province=NULL) | 0 |
| 已用省全集 | 18 省不变 | **18 省不变** | 一致 |

---

## 4. 三层交叉验证 (双 BLOCKED 双 retry_of)

### 4.1 retry_of lineage 区分性

- **shandong**: retry_of=647 (BLOCKED×4: 域名错配+403) — **不撞史**: 647 史为域名错配+403, 本次为 SSL handshake failure (新 BLOCKED 形式, 此前所有刀未见); 但仍 BLOCKED_NO_POL 留痕 (per 653 §0.14 任务书明文"两态均收官价值高: 真触发 = 首次真网 BLOCKED 留痕")
- **hubei**: retry_of=649 (412×2 史, 槽被代换 actual=LIAONING) — **同史**: 649 史为 412×2, 本次 412×2 同形; 但本次因 [EXHAUSTED] 池不可代换, 留痕不代换, actual_province=NULL (与 649 actual=LIAONING 形成对照: 649 substitute 触发 vs 653 BLOCKED 留痕)

### 4.2 SHA 区分性

```
653 (双 BLOCKED) → 0 NEW SHA (无 REACHABLE) → 总 SHA 不变 31
653 ≠ 652 `21c8211b / da1d4104` ≠ 651 `9d0ad78a / f58a3384` ≠ 650 `5c5b1295 / def18a2f` ≠ 649 `b22d1fb4 / a1e49a91` ≠ 648 `4006439e / a06e174f` ≠ 647 `8016ef08 / 56481050` ≠ 646 `fceb8c0a / 49eed23e` ≠ 645 `6237cd48 / dfa38998 / bd4c4c51 / f33eba53` ≠ 644 `bad8be51 / dfa38998 / f33eba53` ≠ 643 `e68099df / 63109491 / 93fe23b3` ≠ 642 `cd6aff30 / 4349ee0f / fede03ba` ≠ 641 `26e5379d...` ✓ (无新 SHA 加入)
```

### 4.3 BLOCKED 留痕区分性 (vs 651/652 双 REACHABLE)

- **653 BLOCKED_NO_POOL 双触发** vs **652 双 REACHABLE (BLOCKED_NO_POOL 分支代码 e2e 可达但本次未触发)** vs **651 双 fallback #1 REACHABLE** — 三态区分完整:
  - 651: 双 REACHABLE (shaanxi/sichuan fallback #1)
  - 652: 双 REACHABLE (xinjiang fallback #1 + nei_menggu 首选); BLOCKED_NO_POOL 分支代码 e2e 可达, 但本次未触发 (留痕 0)
  - **653: 双 BLOCKED_NO_POOL 真网首触发** (shandong SSL handshake failure + hubei 412×2); retry_of 全行 (shandong ← 647; hubei ← 649); blocked_no_pool_count=2 (首次实测触发)

---

## 5. 累 [BLOCKED_NO_POOL] 触发事件计数 (沿用 652 §2.3 模板)

| 刀 | 累计触发次数 | 累计 e2e 验证次数 | 备注 |
|---|---|---|---|
| 638-650 | 0 (n/a) | 0 (n/a) | BLOCKED_NO_POOL 分支不存在 |
| 651 | 0 | 0 | 分支代码首次落地; 但未触发 (双样本 REACHABLE) |
| 652 | 0 | 1 | 652 §0.14 强制 e2e 验证完成; 5 个守门 PASSED; 分支代码可达; 双样本均 REACHABLE (未触发 BLOCKED) |
| **653** | **2** (真网首次双触发) | **1** (本次双样本 BLOCKED → BLOCKED_NO_POOL 路径首次实测命中, 留痕完整 + retry_of lineage 全行) | **653 §0.14 复试 BLOCKED_NO_POOL 真网首次双触发**; 5+3=8 守门 PASSED (含 retry_of 守门 + 双触发守门) |

---

## 6. 653-A.0 P4-A.0 规范 v2 落地验证

### 6.1 P4-A.0 规范 v2 三要点 (per 652 审计 P4 教训沉淀)

- ✓ **status 收口与 §NOW 刷新同 commit 原子完成**: docs/76 §6.1 + 652 receipt §RED_LINE_AUDIT.1 tailnote 落地; commit af7a95c; 后续 653-C rev92 §NOW 收口 commit 内同时完成 status 行收口 + §NOW 收口 + "待复核"字样清除
- ✓ **status 文本如需引 HEAD 一律 `git log -1` 实测终态**: 严禁 pin 中间 SHA 为"终态"
- ✓ **沿用 652-A.0 P4-2 amend-first 规则**: 先 amend 完成再写链文本; cc_head 链 SHA 一律 `git log --format=%H -n <n>` 实测输出

### 6.2 测试守门 (tests/test_m4_16_policy_detail_real_v10.py)

- ✓ `test_p4_a0_v2_tailnote_653_a0_landed_in_docs_76_and_652_receipt` (P4-A.0 规范 v2 落点守门 PASSED)
  - "653-A.0 P4-A.0 规范 v2" 标题存在 (docs/76 + 652 receipt)
  - "status 收口与 §NOW" 核心条款存在 (docs/76 §6.1)
  - "待复核"字样复核后必须清除条款存在 (docs/76 §6.1)
  - "amend-first" 沿用条款存在 (docs/76 §6.1)

---

## 7. 8 守门 PASSED 清单 (per 653 §0.14)

| # | 守门 | 实测 | 状态 |
|---|---|---|---|
| 1 | fetch 脚本 BLOCKED_NO_POOL 分支字串守门 | verdict + blocked_reason + RETRY_OF_NOTES | PASSED |
| 2 | 主 evidence substitute_pool_status='EXHAUSTED' 守门 | summary.substitute_pool_status | PASSED |
| 3 | blocked_no_pool_count=2 真网首触发守门 | summary.blocked_no_pool_count=2 | PASSED |
| 4 | seed 0 INSERT ROWS + retry_of 守门 | non-INSERT + retry_of | PASSED |
| 5 | P4-A.0 规范 v2 落点守门 | docs/76 §6.1 + 652 receipt §RED_LINE_AUDIT.1 | PASSED |
| 6 | red_line_14 SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED' 守门 | fetch 脚本 | PASSED |
| 7 | retry_of_annotation 双样本注解守门 | summary + cell retry_of | PASSED |
| 8 | chain_id v10 + UUID l 段 8 表前缀守门 | evidence metadata | PASSED |

---

## 8. backfill 完整性三齐 (per 652 审计 P4-A.0 规范 v2 + 653 任务书 §C)

| 簿记 | 状态 | 备注 |
|---|---|---|
| EXEC-QUEUE rev91 → rev92 | 待办 | 架构师未改 (per 红线, 由 Cursor 维护); 653-C commit 完成 + status 收口与 §NOW 同 commit 原子完成后触发 |
| cc_head rev92 链补 | 待办 | 6 commits 中 cc_head rev92 commit 完成时回填 |
| docs/77 §NOW 指针更新 | 待办 | §6 完成态写"653 DELIVERED + M4.16 全收口 + O1 仍 OPEN + 21 里程碑不宣称 PASS" |

---

## 9. 红线 1-14 全自检 (沿用 652)

| 红线 | 内容 | 653 自检 |
|---|---|---|
| 1 | 不宣称 Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS | ✓ 不宣称 |
| 2 | 不补零 / 不静默硬编码 value | ✓ domain 值 NULL 透明占位 (沿用 641-652) |
| 3 | 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED; ≤12 HTTP total | ✓ 4/12 = 33% usage |
| 4 | 不改 docs/45/50/53/66/67/68/69/70/71/72/73/74/75/76 既有正文 — 修正项项一律行内 append 尾注 | ✓ docs/76 §6.1 是行内 append tailnote (commit af7a95c) |
| 5 | 不碰 4 fixture 锁值 | ✓ 不碰 |
| 6 | 数据源唯一 = 政府/统计局/研究机构自取; 用户零裁定 | ✓ 沿用 |
| 7 | 完成 = observation SUCCESS, 禁止 PARTIAL (特例: BLOCKED_NO_POOL 留痕是合法的"未完成"状态) | ✓ 双 BLOCKED 留痕 (特例合法) |
| 8 | 不新写 016 migration (沿用 009+010+014+015 lineage JSONB) | ✓ 沿用 |
| 9 | chain_id = 'real_653_m4_16_policy_detail_v10' (末段 _v10, ≠ 652 _v9 ≠ 651 _v8) | ✓ |
| 10 | UUID l 段 (l02-l62, 8 表前缀全 distinct) ≠ 652 k 段 ≠ 651 j 段 | ✓ |
| 11 | 不写 cegr.* 生产表 | ✓ 不写 |
| 12 | 既有 registry 行 SHA 零漂移; 4 fixture 字节零触碰; m2 crosscheck 报告零 diff | ✓ docs/52 零改动 |
| 13 | O1 零动作 + 附属产物指针 + 代换行标注规范 | ✓ docs/77 §1-§6 + 附属报告 + 实际省=actual_province |
| 14 | 递补池 [EXHAUSTED] + BLOCKED_NO_POOL 留痕不代换 + 5 原始候选全部 consumed | ✓ 双 BLOCKED 留痕不代换 |
| 14+ | 653 §0.14 复试 BLOCKED_NO_POOL e2e 验证 (4 实现位置 + 8 守门) | ✓ 双样本首触发 + 8 守门 PASSED |

---

## 10. 不宣称 PASS

- 不宣称 Gate / O1 / O2 / O3 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M4.12 / M4.13 / M4.14 / M4.15 / M4.16 / M5 / M5.1 / M5.2 / M5.3 / M6 PASS（沿用红线 1, 21 个里程碑不宣布; vs 652 时 20 个; 653 增量 = M4.16）
- O1 仍 OPEN (B路 live-candidate 仅登记, 不切换/启用)

---

## 11. 下一步

待 user ACK + 授权 commit:

1. delivery commit: `scripts/fetch_m4_16_policy_detail_v10_2024.py` + `scripts/seed_m4_16_policy_detail_real_v10.sql` + `evidence_pack/m4_16_policy_detail_real_v10_20260902.json` + `docs/77-m4-16-policy-detail-real-v10-20260902.md` + `docs/reports/m4_16_policy_detail_real_v10_20260902.md` + `tests/test_m4_16_policy_detail_real_v10.py`
2. cc_head rev92 commit (chain SHA 链补)
3. receipt commit: 本回执 + `reviews/stage0-gate0-rework-2026-08-23/653-stage0-cc-m4-16-v10-retry-receipt-20260902.md`
4. backfill commit: EXEC-QUEUE rev91 → rev92 + cc_head 链补
5. §NOW commit: status 收口与 §NOW 刷新同 commit 原子完成 (per 653-A.0 P4-A.0 规范 v2); docs/77 §6 + reviews/00-... §NOW + cc_head 全等; "待复核/待 §C-x"字样复核后**必须清除** (此 commit 内同原子完成)
6. cc_head 链补 commit: 5+6 链 SHA 同步
7. 双推 origin + github
8. 3 ref 全等 (`git log --format=%H -n 1 origin`, `git log --format=%H -n 1 github`, 本地 HEAD)

---

— End 653 — M4.16 v10 双复试 spike 回执 20260902 —