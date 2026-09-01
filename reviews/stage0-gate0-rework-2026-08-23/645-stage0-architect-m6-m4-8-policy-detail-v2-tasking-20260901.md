# 645 — M6 spike 文档收口 + M4.8 政策详情扩展（架构师 tasking · scope A）

> **刀号**: 645  
> **类型**: 架构师 tasking（沿用 644 模式 · 架构师本终端即签即自交付）  
> **Milestone**: M6 + M4.8（双刀并行）  
> **日期**: 2026-09-01  
> **依据**:
> - `docs/67-m4-7-policy-detail-real-20260901.md` (644 M4.7 政策详情真实化)
> - `docs/66-m5-waf-third-pass-20260901.md` (644 M5 WAF 第三次收口)
> - `reviews/stage0-gate0-rework-2026-08-23/644-stage0-architect-m5-3-m4-7-parallel-tasking-20260901.md` §5 (645 推荐 scope A)
> - 用户 ACK：「收644，下发645 A」（2026-09-01）
> **前置**: 644 DELIVERED (4 commits `aac8225`/`a66215b`/`899bd41`/`9b9bf20` 双推完成)  
> **架构师综合**: M6 = M4.x spike 系列文档收口（docs/66/67/68/69 四文档作为 M4.x/M5 spike 完整审计链） + M4.8 = 政策详情 v2 扩展（沿用 644 模式 + 纳入 644 留作扩展的 henan `bd4c4c51...` (zwgk root) 作为第 4 样本）。  
> **不宣布** Gate / O1 / M2 / M4 / M4.7 / M4.8 / M5 / M6 PASS。

---

## 1. 645 scope 总览（沿用 644 双刀并行模式）

| 子刀 | 类型 | 范围 | 交付物 | 状态 |
|---|---|---|---|---|
| **645-A.1** | M6 spike 文档收口 | docs/66/67 + 645 docs/68 (M6 master) + 645 docs/69 (M4.8) + docs/45 §3 + docs/50 §4.4 + docs/53 §5 跨文档互链收口 | docs/68-m6-spike-docs-closure-20260901.md (M6 master) + 4 处互链补登 | OPEN |
| **645-A.2** | M4.8 政策详情 v2 真实化 | 沿用 644 3 试点省 × 1 detail each × 6 政策表 = 18 INSERT + 纳入 644 留作 henan `bd4c4c51...` (zwgk root) 作为第 4 样本 = **24 INSERT planned**；chain_id='real_645_m4_8_policy_detail_v2' (≠ 644 chain_id)；UUID prefix d 段 ≠ 644 c 段 | `scripts/fetch_m4_8_policy_detail_v2_2024.py` + `evidence_pack/m4_8_policy_detail_real_v2_20260901.json` + `docs/reports/m4_8_policy_detail_real_v2_20260901.md` | OPEN |
| **645-A.3** | M4.8 seed SQL | 24 INSERT 真实化 sentinel (lineage.is_demo='false') + chain_id='real_645_m4_8_policy_detail_v2' + UUID prefix d 段 ≠ 644 c 段 + hlj/henan/yunnan geo_entity_id SELECT 子查询 | `scripts/seed_m4_8_policy_detail_real_v2.sql` | OPEN |
| **645-A.4** | docs/68 (M6) + docs/69 (M4.8) §1-§6 双文档架构师级审查 | 六段（终态 / spike 边界 / 真实化 demo SQL 结构 / lineage sentinel / 下一步 / 不宣称 PASS） | docs/68 + docs/69 | OPEN |
| **645-A.5** | 2 reports + 2 evidence JSONs | `docs/reports/m6_spike_docs_closure_20260901.md` (M6 文档收口报告) + `evidence_pack/m6_spike_docs_closure_20260901.json` (M6 证据) + `docs/reports/m4_8_policy_detail_real_v2_20260901.md` (M4.8 fetch 报告) + `evidence_pack/m4_8_policy_detail_real_v2_20260901.json` (M4.8 evidence) | 4 文件 | OPEN |
| **645-A.6** | EXEC-QUEUE rev74 → rev75 | rev74 「644 DELIVERED · 等用户 ACK → 645 待定」→ rev75 「645 tasking OPEN (645-A → 645-B → 645-C 顺序执行)」 | `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` | OPEN |
| **645-B** | 测试 | ≥ 12 用例（≥ 6 M6 + ≥ 6 M4.8）= 12 cases | `tests/test_m6_spike_docs_closure.py` + `tests/test_m4_8_policy_detail_real_v2.py` | OPEN |
| **645-C** | 回执 + commit + 双推 | `645-stage0-cc-m6-m4-8-parallel-receipt-20260901.md` §PHOTO-1..6 + 4 commits + 双推 (origin→github SSH fallback) | receipt + delivery + cc_head + receipt-backfill 4 commits | OPEN |

---

## 2. 645-A.1 M6 spike 文档收口详细设计

### 2.1 M6 scope 定义（架构师裁定）

**M6 = M4.x + M5 spike 文档系列收口**，不是新功能 spike，而是已有 spike 文档（644/643/642/641）的跨文档互链 + 主从收口。具体为：

1. **docs/68 = M6 master 文档**（NEW）— 总览 M4.x (4.1-4.8) + M5 (5.1-5.3) 全 spike 链：
   - §1 落地终态（按刀号表）
   - §2 spike 边界（每刀的 ≤ HTTP / cells / INSERT）
   - §3 lineage JSONB `is_demo='false'` 真实化 sentinel 沿用链
   - §4 chain_id 区分（`real_641_heilongjiang` → `real_645_m4_8_policy_detail_v2`）
   - §5 真实 SHA 区分（不撞 638-644 demo/real SHA）
   - §6 646 下一步 + 不宣称 PASS

2. **docs/66/67 → docs/68 互链尾注**：
   - docs/66 §6 末「→ 645 docs/68」尾注（沿用 644 docs/66 → docs/68 链尾）
   - docs/67 §6 末「→ 645 docs/68」尾注

3. **docs/45 §3 O1/O3 OPEN 段 + §6.2 S2.7-b 接驳路径段**：
   - 不动既有 OPEN 段（O1 仍 OPEN，O3 仍 OPEN）
   - 仅在 §6.2 表末 + 1 行「M4.x/M5 spike 文档收口（M6 master = docs/68）」

4. **docs/50 §4.4 里程碑表末 + 1 行「M6 spike 文档收口」**：
   - 交付列指向 docs/68 §1
   - 回执列 `645`
   - 守门列 docs/45+53 同步登记

5. **docs/53 §5 末 + 1 项「M6 spike 文档收口」**：
   - 同 docs/45 §3 互链
   - chain 链接 docs/45 §3 + docs/50 §4.4

### 2.2 M6 不动红线（沿用 644）

- ❌ 不宣布 Gate / O1 / O3 / M2 / M4 / M4.5 / M4.6 / M4.7 / M4.8 / M5 / M6 PASS
- ❌ 不补零 / 不静默硬编码 value / 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED
- ❌ 不改 docs/45/50 正文既有 OPEN 段（O1/O3 OPEN 段）
- ❌ 不碰 4 fixture 锁值
- ❌ docs/68 不写新功能（仅文档收口）
- ❌ docs/69 M4.8 = 真实化 spike 二次（非新功能）
- ❌ 不引入 `next/link` / 不分支 `params.*`（与 644 无关但保留 build ○ Static）

### 2.3 docs/68 草稿大纲

```markdown
# 68 — M4.x + M5 spike 文档系列收口（M6 master · 架构师级审查）

> 刀号: 645
> 类型: M6 master 文档（spike 文档收口，非新功能 spike）
> 前置: 638/639/640/641/642/643/644 全部 DELIVERED
> 不宣布 Gate / O1 / O3 / M2 / M4 / M5 / M6 PASS。

## 1. M4.x + M5 spike 链落地终态（8 刀）
| 刀 | milestone | docs | 状态 |
| 638 | M4.1 | docs/58 | DELIVERED |
| 639 | M4.2 | docs/59 | DELIVERED |
| 640 | M4.3 | docs/60 | DELIVERED |
| 641 | M4.4 | docs/61 | DELIVERED |
| 642 | M4.5 + M5 | docs/62 + docs/63 | DELIVERED |
| 643 | M4.6 + M5.2 | docs/64 + docs/65 | DELIVERED |
| 644 | M4.7 + M5.3 | docs/66 + docs/67 | DELIVERED |
| 645 | M4.8 + M6 (master) | docs/68 + docs/69 | OPEN |

## 2. spike 边界统一表
| 刀 | ≤ HTTP | cells | INSERT | chain_id | UUID prefix |
| 638 | ≤10 | 23 | n/a (probe only) | n/a | n/a |
| 639 | ≤10 | 23 | 5 demo | demo_639 | demo prefix |
| 640 | ≤10 | 6 | 18 demo | demo_640 | demo prefix |
| 641 | ≤4 | 1 | 6 real | real_641_heilongjiang | real prefix |
| 642 | ≤10 + ≤10 | 10 + 6 | 18 real | real_642_m4_5_renmian | b 段 |
| 643 | ≤10 + ≤12 | 10 + 9 | 24 real | real_643_m4_6_govreport | b 段 |
| 644 | ≤10 + ≤12 | 10 + 5 | 18 real | real_644_m4_7_policy_detail | c 段 |
| 645 | ≤12 + ≤12 | 6 + 8 | 24 real | real_645_m4_8_policy_detail_v2 | d 段 |

## 3. lineage JSONB is_demo='false' 真实化 sentinel 沿用
(sentinel 沿用 009 + 010 + 014 + 015 migrations)

## 4. chain_id 区分裁定（避免 SHA collision）
(7 chain_ids 全部 distinct)

## 5. 真实 SHA 区分表（不撞 638-644 demo/real SHA）
(沿用 641-644 SHA + 645 4 新 SHA)

## 6. 646 下一步 + 不宣称 PASS
(沿用 644 docs/67 §5 五 scope 候选 + M4.9 选项)
```

---

## 3. 645-A.2 M4.8 政策详情 v2 扩展详细设计

### 3.1 M4.8 scope（沿用 644 模式 + 1 新样本）

**沿用 644 3 试点省 × 1 detail each × 6 政策表 = 18 INSERT**：
- heilongjiang: `bad8be51...` (c107884 list) → 644 已 fetch，可复用（沿用 URL 重新 fetch 验证 idempotent + 落新 SHA 副本）
- henan: `dfa38998...` (zfgb list) → 644 已 fetch
- yunnan: `f33eba53...` (zfgzbg) → 644 已 fetch

**新增 644 留作扩展的 henan `bd4c4c51...` (zwgk root) 作为 M4.8 第 4 样本**：
- henan zwgk root 是 644 留作 v2 扩展的源，645 正式 fetch + seed
- 645 fetch henan `https://www.henan.gov.cn/zwgk/` → SHA `bd4c4c51...`

**M4.8 样本总览**（4 样本，比 644 多 1）：
| 序号 | 试点省 | URL | SHA (前 16) | file_size | 645 seed 用 |
| 1 | heilongjiang | `/hlj/c107884/list.shtml` | `bad8be51...` | varies | ✓ |
| 2 | henan | `/zwgk/zfgb/` | `dfa38998...` | 8,959 | ✓ |
| 3 | henan (NEW) | `/zwgk/` | `bd4c4c51...` (NEW 真实 fetch) | varies | ✓ |
| 4 | yunnan | `/zwgk/zfxxgk/zfgzbg/` | `f33eba53...` | 94,310 | ✓ |

### 3.2 M4.8 INSERT 规划（24 INSERT = 644 模式 × 4 样本）

| 表 | 行数 | lineage.is_demo | UUID prefix | 区别 vs 644 |
|---|---|---|---|---|
| source_registry | 4 (新 chain_id 包含 4 source URLs) | `'false'` | d0eebc99-...d21/d22/d23/d24 | 644 = 0 行（沿用 643）|
| source_document | 4 | `'false'` | d0eebc99-...d31/d32/d33/d34 | 644 = 0 行 |
| policy_document | 4 | `'false'` | d1eebc99-...d41/d42/d43/d44 | 644 = d1eebc99-...c41/c42/c43 (3 行) |
| policy_target | 4 | `'false'` | d2eebc99-...d51/d52/d53/d54 | 644 = ...c51/c52/c53 |
| policy_measure | 4 | `'false'` | d3eebc99-...d61/d62/d63/d64 | 644 = ...c61/c62/c63 |
| government_commitment | 4 | `'false'` | d4eebc99-...d71/d72/d73/d74 | 644 = ...c71/c72/c73 |
| commitment_progress | 4 | `'false'` | d5eebc99-...d81/d82/d83/d84 | 644 = ...c81/c82/c83 |
| project_event | 4 | `'false'` | d6eebc99-...d91/d92/d93/d94 | 644 = ...c91/c92/c93 |

**总计**：4 × 6 = **24 INSERT planned**（vs 644 实测 18 INSERT；M4.8 多 1 样本 henan zwgk root；UUID d 段 ≠ 644 c 段）

### 3.3 chain_id 区分

- 644 chain_id: `real_644_m4_7_policy_detail`
- **645 chain_id: `real_645_m4_8_policy_detail_v2`**（v2 标记 = 第 4 样本纳入）

### 3.4 红线（沿用 644 + 645-specific）

- ❌ 645 fetch http_count ≤ 12（沿用 644 红线）
- ❌ 645 UUID prefix d 段 ≠ 644 c 段（防 UUID collision）
- ❌ 645 chain_id ≠ 644 chain_id
- ❌ 645 4 新 SHA ≠ 644 3 SHA + ≠ 643/642/641/640/639 demo/real SHA
- ❌ 645 不重新 fetch 644 已 fetch 的 3 样本（仅复验 idempotent + 落 SHA 副本 + 纳入第 4 样本 henan zwgk root）
- ❌ 645 不删表 / 不 DROP COLUMN / 不 DELETE FROM 真实数据

---

## 4. 645-A.4 docs/68 + docs/69 §1-§6 双文档结构（沿用 644 模板）

docs/68 §1-§6（同 2.3 草稿大纲）  
docs/69 §1-§6（M4.8 spike 二次，结构同 docs/67）：
- §1 M4.8 落地终态
- §2 M4.8 spike 边界（vs 644 tasking 规划）
- §3 真实化 demo SQL 结构
- §4 lineage 真实化 sentinel
- §5 646 下一步
- §6 下一步 + 不宣称 PASS

---

## 5. 645-A.5 报告 + 证据（沿用 644 模板）

- `docs/reports/m6_spike_docs_closure_20260901.md`（M6 文档收口报告）
- `evidence_pack/m6_spike_docs_closure_20260901.json`（M6 证据：互链节点列表）
- `docs/reports/m4_8_policy_detail_real_v2_20260901.md`（M4.8 fetch 报告）
- `evidence_pack/m4_8_policy_detail_real_v2_20260901.json`（M4.8 evidence）

---

## 6. 645-A.6 EXEC-QUEUE rev74 → rev75

| rev | status | 一句话 |
|---|---|---|
| 74 | 644 DELIVERED · 等用户 ACK → 645 待定 | (current) |
| 75 | **645 tasking OPEN (M6 + M4.8 双刀并行 spike)** | (target) |

cc_head chain 不动（645 tasking 暂不入链；DELIVERED 时入链 645 tasking → 645 delivery → 645 cc_head → 645 receipt）

---

## 7. 645-B 测试 ≥ 12 用例

### 7.1 `tests/test_m6_spike_docs_closure.py`（≥ 6 用例）

1. `test_docs_68_exists_and_has_six_sections` — docs/68 §1-§6 架构师级审查
2. `test_docs_68_no_pass_announcement` — docs/68 不宣称 PASS
3. `test_docs_68_links_to_66_67_via_tail_note` — docs/68 §6 末「→ docs/66 / → docs/67」尾注
4. `test_docs_45_section_6_2_appends_m6_row` — docs/45 §6.2 末 +1 行「M6 spike 文档收口」
5. `test_docs_50_section_4_4_appends_m6_row` — docs/50 §4.4 末 +1 行「M6 spike 文档收口」
6. `test_docs_53_section_5_appends_m6_item` — docs/53 §5 末 +1 项「M6 spike 文档收口」

### 7.2 `tests/test_m4_8_policy_detail_real_v2.py`（≥ 6 用例）

1. `test_m4_8_fetch_report_exists_and_has_top_verdict` — fetch 报告 + REAL_FETCHED
2. `test_m4_8_evidence_json_parses_and_http_count` — evidence + http_count ≤ 12
3. `test_seed_m4_8_sql_exists_and_has_real_data` — 24 INSERT (6 表 × 4 行 UUID 计数)
4. `test_seed_m4_8_sql_lineage_is_demo_false_isolation` — 6 表 × 4 行 lineage.is_demo='false'
5. `test_seed_m4_8_sql_real_sha_distinct_from_prior_shas` — 4 新 SHA ≠ 644/643/642/641/640/639
6. `test_seed_m4_8_sql_uuid_d_segment_distinct_from_644_c_segment` — UUID d 段 ≠ 644 c 段
7. `test_docs_69_has_six_sections` — docs/69 §1-§6
8. `test_docs_69_no_pass_announcement` — docs/69 不宣称 PASS
9. `test_seed_m4_8_sql_chain_id_v2_distinct_from_644_chain_id` — chain_id='real_645_m4_8_policy_detail_v2' ≠ 'real_644_m4_7_policy_detail'

---

## 8. 645-C 回执 + commit + 双推（沿用 644 4 commits 模式）

### 8.1 4 commits 序列

1. **delivery commit** (TBD-1) — `feat(645): M6 spike 文档收口 + M4.8 政策详情 v2 真实化并行 (24 INSERT, 4 样本; UUID d 段 ≠ 644 c 段)`
2. **cc_head backfill commit** (TBD-2) — `chore(645): EXEC-QUEUE rev75 cc_head backfill — append 645 delivery`
3. **receipt commit** (TBD-3) — `docs(645): 645-stage0-cc-m6-m4-8-parallel-receipt-20260901.md §PHOTO-1..6`
4. **receipt-backfill commit** (TBD-4) — `chore(645): EXEC-QUEUE rev75 cc_head backfill — append 645 receipt`

### 8.2 双推顺序

```bash
git push origin HEAD       # 1st push
git push github HEAD       # 2nd push (SSH fallback HTTPS 443 阻塞)
```

每个 commit 单独 push（沿用 644 模式）。

---

## 9. 红线（沿用 644 + 645-specific）

- ❌ 不宣布 Gate / O1 / O3 / M2 / M4 / M4.5 / M4.6 / M4.7 / M4.8 / M5 / M6 PASS
- ❌ 不补零 / 不静默硬编码 value / 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED
- ❌ 不改 docs/45/50/66/67 正文既有 OPEN 段
- ❌ 不碰 4 fixture 锁值
- ❌ 645 fetch http_count ≤ 12（沿用 644 红线）
- ❌ 645 4 新 SHA ≠ 644/643/642/641/640/639 demo/real SHA
- ❌ 645 UUID prefix d 段 ≠ 644 c 段
- ❌ 645 chain_id 'real_645_m4_8_policy_detail_v2' ≠ 644 'real_644_m4_7_policy_detail'
- ❌ 不重新 fetch 644 已 fetch 的 3 样本（仅复验 idempotent + 落 SHA 副本 + 纳入第 4 样本 henan zwgk root）
- ❌ 不删表 / 不 DROP COLUMN / 不 DELETE FROM 真实数据
- ❌ 数据源治理铁律（2026-08-29）：数据源唯一=政府/统计局/研究机构自取；用户零裁定（除注册/登录/付费/UI 人工验收）
- ❌ 双推门门: commit + push origin → push github 必须顺序
- ❌ 不主动 commit/push（已被用户豁免 2026-08-31 21:50）

---

## 10. 架构师推荐 646 下一步（沿用 644 docs/67 §5 五 scope 候选）

- **scope A（推荐）**：646 = M6 收口（如 O1 主路径 docs/52 B 路 live-candidate 探测）+ M4.9 政策详情 v3 扩展
- **scope B**：646 = Gate 1 启动（架构师启动 Gate 1 而非继续 spike）— M2 Gate 后才合法
- **scope C**：646 = O3 OCR 真实化（沿用 583 O3 spike；2026-08 已完成 spike + audit + 自取政府源）
- **scope D**：646 = docs/45/50 spike 文档清空收口（沿用 M6 收口模式）
- **scope E**：646 = M4.9 试点省扩展（沿用 644 模式 + 加 fujian / guangdong 第 5/6 样本）

---

**沿用 644 模式**：架构师本终端自签 + 自交付（执行端模式继续）。

— End 645 tasking —
