# 651 审验裁定 + 652 任务书 — 合并归档 (2026-09-02)

> 单文件模式（per 用户指示 2026-09-01 起，对话不再展示全文）。
> Part 1 = 651 审验裁定（Cursor 审验端）；Part 2 = 652 任务书（架构师签发）。EXEC-QUEUE 指针以本件为准。

---

# ══════════ PART 1 / 651 审验裁定 ══════════

## 651-stage0-cursor-s651-m4-14-v8-pool-depletion-audit — 审验指令 (2026-09-02)

> **角色**: Cursor（审验端）
> **对象**: 651 完整链路（M4.14 v8 shaanxi/sichuan + 递补池 [EXHAUSTED] 收官 + 红线 14 增补 + 650 审计 P4×2 更正）
> **入口**:
> - 回执 `reviews/stage0-gate0-rework-2026-08-23/651-stage0-cc-m4-14-v8-pool-depletion-receipt-20260902.md`
> - 任务书 `reviews/stage0-gate0-rework-2026-08-23/650-audit-651-tasking-consolidated-20260902.md`（合并件 PART 2）
> - 主 evidence `evidence_pack/m4_14_policy_detail_real_v8_20260902.json`
> - 附属报告 `docs/reports/m4_14_policy_detail_real_v8_20260902.md`
> - 架构师审查 `docs/75-m4-14-policy-detail-real-v8-20260902.md`
> **裁定（定案）**: **PASS（有限通过）** — 0×P3 + **2×P4**（① rev88 status 行 pin 中间 SHA；② cc_head 错录 amend 孤儿 SHA ea64640，应为 eb6b012——rev89 已修正）+ 2×观察（O-1 复发即还原 = 预测命中；O-2 本刀任务书集合未复发）；650 P4×2 全部行内更正 + 尾注落地；红线 14 增补 4 实现位置全部到位
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS；**O1 仍 OPEN**

### §A. 独立复跑（审验端一手 — 已执行 2026-09-02）

| # | 验收项 | 结果（实测） |
|---|---|---|
| A1 | pytest 651 新测试 + 650 侧回归（任务书 §2 11 文件集） | **144 passed in 1.65s**（= 26 新 + 118 回归；≥126 达成 +14%）。注: 回执/§META "137 回归 = 163" 为执行端全套口径（M4.1→M4.14），审验端全套复跑受本机环境截断（15% 处 timeout），以任务书集合 144 为权威 ✓ |
| A2 | 隔离复跑 | 任务书集合首跑即全绿（无 650 式幽灵并发干扰——O-2 未复发）✓ |
| A3 | git 链 651 6 commits | `d13b322`→`8ea2af4`→`fadb015`→`eb6b012`→`70b277e`→`8ae20de` 全在 ✓ |
| A4 | 双推复核 | HEAD = origin/main = github/main = `8ae20de` 三向全等 ✓ |
| A5 | backfill 三齐 | cc_head 链入 5 SHAs（d13b3229/8ea2af4/fadb015/**eb6b012**〔原错录 ea64640 孤儿 → P4-2，rev89 修正〕/70b277e；8ae20de 自身按惯例由 rev89 入链=本次完成）+ last_receipt = `fadb015` ✓ + §NOW 刷新 ✓ |
| A6 | 树净 | 0（仅本合并件 untracked = 预期产物）✓ |
| A7 | 复跑后污染核查 | m2 crosscheck 报告复跑后现 4+/4- churn → **O-1 预测命中**，`git checkout --` 即还原，树净 ✓（非交付缺陷）|

### §B. 交付物逐项核验（10 files / 重点 8 项）

| # | 项 | 核验重点 | 结果 |
|---|---|---|---|
| B1 | A.0 P4×2 行内更正 + 尾注 | docs/74 第 42 行 "shaanxi" 正确连写 + 尾注 "per 650 审计 P4-1 行内更正 / 2026-09-02"; 第 79 行 (§2.4) 槽名/actual 口径尾注 "per 650 审计 P4-2 口径尾注 / 2026-09-02" 含 "HUBEI 为槽名 (consumed); actual_province = LIAONING"; 第 214 行 (§4.4) 同口径尾注; `grep -c "sha anxi" docs/74-...md` = **0** | ✓ |
| B2 | A.1 M4.14 v8 真实化 | 16 INSERT (12 政策 + 2 registry + 2 document); chain_id `real_651_m4_14_policy_detail_v8` (末段 `_v8` ≠ 650 `_v7` ≠ 649 `_v6` ≠ 648 `_v5`); UUID **j 段** 8 表前缀 (j0eebc99 j1eebc99 ... j6eebc99) 全 distinct ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段; shaanxi /zwgk/ 404 → / 200 REACHABLE (87956 bytes, SHA `9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5`); sichuan /zwgk/ 403 WAF → / 200 REACHABLE (100536 bytes, SHA `f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29346ad5`); **2 NEW SHA distinct ≠ 638-650 全部**; `substitute_used_count=0`; `blocked_no_pool_count=0`; HTTP **4/12** (33%); is_demo 全 `'false'`; lineage original/actual 双记; lineage `red_line_14_status='EXHAUSTED'` 16 行显式登记; `substitute_pool_note` 显式登记 | ✓ |
| B3 | A.1 fetch 脚本 BLOCKED_NO_POOL 分支 | `SUBSTITUTE_POOL: list = []` (空; 5 原始候选全部 consumed); `SUBSTITUTE_POOL_STATUS = "EXHAUSTED"`; `fetch_cell()` 含 `verdict: "BLOCKED_NO_POOL"` + `blocked_reason` 字段 (本次未触发, 因双样本 fallback #1 REACHABLE); `summary.substitute_pool_status = "EXHAUSTED"` 写入主 evidence | ✓ |
| B4 | A.2 O1 零动作 | delivery 文件清单核验: 无 probe / 无 registry 触碰 / 无 connector 触碰 / docs/52 零改动 | ✓ |
| B5 | A.3 docs/75 §1-§6 | 286 行全 (§1 M4.14 v8 落地终态 + §2 substitute 跨省代换登记 + **递补池生命周期收官 4 阶段**〔649 激活/650 备而未触发/651 转正/651 后 EXHAUSTED〕 + §3 spike 边界 16 INSERT 明细 + §4 lineage 真实化 sentinel + chain_id 区分 14 真实化刀 + 27 SHA 累计 + UUID 严格递增 + §5 后续 652+ BLOCKED 留痕口径 5 候选 scope + §6 下一步 + 不宣称 PASS 19 里程碑) | ✓ |
| B6 | A.4 evidence ×2 | json 主 evidence (uuid_prefixes 8 表 + http_count=4 + distinct_shas + cells 逐 attempt + methodology 含 651 §0.14 援引 + BLOCKED_NO_POOL 留痕不代换条款 + 649 P3-1 援引) + docs/reports 附属产物 9 节齐全 (任务背景 / 样本复盘 / 三层交叉验证 / HTTP 预算 / SHA 区分表 + lineage 落地 / 递补池耗尽登记 / 651 §0.14 红线 14 增补登记 / 附属产物指针 / 验收 checklist) | ✓ |
| B7 | B 测试 | **26 cases** (≥8 要求 3.25×; 含 **5 个 P3-1/P4-1/P4-2/红线 14/docs/75 §1-§6 守门**) — 重点守门: `test_evidence_json_real_fetched_2_samples` + `test_evidence_json_substitute_pool_status_exhausted` + `test_fetch_script_blocked_no_pool_branch_present` + `test_seed_sql_red_line_14_status_exhausted` + `test_p4_1_docs_74_no_sha_anxi_residue` + `test_p4_2_docs_74_slot_actual_province_koujings` + `test_red_line_14_pool_exhaustion_*` (3 项) + `test_docs_75_sections_1_to_6_present` + `test_docs_75_pool_depletion_records` | ✓ |
| B8 | C rev88 | header = §META = 88 ✓; status = "651 DELIVERED + 651-C 完成 (receipt 入链 + backfill 三齐 + rev88 header 同步 + 双推 origin=github=eb6b012)"; cc_head 链含 6 个新 SHA (d13b3229/8ea2af4/fadb015/eb6b012/70b277e/8ae20de); last_receipt = `fadb015`; §NOW 已刷新 (HTTP 4/12 + 163 green + 后续 scope A-E) | ✓ |

### §C. 红线 14 条复核 (13 沿用 + **1 增补**红线 14 增补 4 实现位置全部到位)

| # | 红线 | 复核重点 | 结果 |
|---|---|---|---|
| 1 | 不宣布 Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS | docs/75 §6 + 651 receipt §RED_LINE_AUDIT 19 个里程碑不宣布 | ✓ |
| 2 | 不补零 / 不静默硬编码 value | domain 值 NULL 透明占位 (沿用 641-650); lineage 字段无伪造 | ✓ |
| 3 | 不爬网 / 不镀铬四轨 / ≤12 HTTP total | HTTP 实测 4/12 = 33% usage (vs 650 3/12 = 25%; vs 649 6/12 = 50%); 双样本 × 2 HTTP each | ✓ |
| 4 | 不把目录页标 FETCHED | 仅 fallback 链 (zwgk → /) 落入 seed; 目录页未标 FETCHED | ✓ |
| 5 | 不改 docs/45/50/53/66/67/68/69/70/71/72/73 既有正文 | 仅 docs/74 行内 append 尾注 (per 650 审计 P4×2); 其余 docs 零触碰 | ✓ |
| 6 | scripts/ 蓝图 SQL 的 P3-1 更正不属 docs 正文 | 651 无 P3-1 新增; 沿用 650 蓝图更正 | ✓ |
| 7 | 不碰 4 fixture 锁值 (nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c) | 0 触碰; grep SHA 全 distinct | ✓ |
| 8 | 数据源唯一 = 政府/统计局/研究机构自取; 用户零裁定 | shaanxi/sichuan 政府门户; 用户零裁定 (执行端自签自交付 per 2026-08-31 21:50 豁免) | ✓ |
| 9 | 完成 = observation SUCCESS, 禁止 PARTIAL | fetch_status = REAL_FETCHED; fetched_count = 2; verdict = REACHABLE ×2 | ✓ |
| 10 | 不新写 016 migration | 沿用 009+010+014+015 lineage JSONB; 0 新 migration | ✓ |
| 11 | chain_id = `real_651_m4_14_policy_detail_v8` (末段 _v8) | ≠ 650 _v7 ≠ 649 _v6 ≠ 648 _v5 ≠ 647 _v4 | ✓ |
| 12 | UUID j 段 (j02-j62) ≠ 650 i 段 ≠ 649 h 段 | 8 表前缀 j0/j1/j2/j3/j4/j5/j6eebc99 全 distinct | ✓ |
| 13 | 不写 cegr.* 生产表 | seed SQL 仅 staging 蓝本; 0 production 写入 | ✓ |
| **14 增补** | **递补池耗尽条款 (2026-09-02 立)**: 5 候选全部 consumed; 此后 BLOCKED 留痕不代换 | **4 实现位置全部到位**: (a) `scripts/fetch_m4_14_policy_detail_v8_2024.py` SUBSTITUTE_POOL=[] + STATUS='EXHAUSTED' + BLOCKED_NO_POOL verdict 分支 + blocked_reason 字段; (b) `scripts/seed_m4_14_policy_detail_real_v8.sql` lineage JSONB 全 red_line_14_status='EXHAUSTED' + substitute_pool_note; (c) `evidence_pack/m4_14_policy_detail_real_v8_20260902.json` summary.substitute_pool_status='EXHAUSTED' + methodology 含 BLOCKED_NO_POOL 援引; (d) `docs/75-m4-14-policy-detail-real-v8-20260902.md` §2.2 生命周期收官 4 阶段 + §2.3 池成员最终状态表 + §4.4 收官表 + §5 BLOCKED 留痕口径 | ✓ |

### §D. 发现（重点 — 审计端裁定区）

| 级 | # | 重点发现（审验端定案） | 处置 |
|---|---|---|---|
| P3 | — | 无 | — |
| P4 | 1 | **rev88 §CURRENT status 行 pin 中间 SHA**："双推 origin=github=eb6b012"——其后 2 个收口 commit（70b277e §NOW 刷新 / 8ae20de 链补）使终态 HEAD=8ae20de，status 行 SHA pin 陈旧（同类: 649 P4 自指陈旧模式的轻量复发；§NOW 本身已被 70b277e 刷新，实质无损） | 652-C 规范：status/§NOW 措辞**不 pin 中间 SHA**，以"三 ref 全等 + 最终 HEAD"表述（652-A.0 登记） |
| P4 | 2 | **cc_head 链错录孤儿 SHA**：651 receipt-backfill 记为 `ea64640`——git 考古实证其为 amend 前孤儿（与真实 `eb6b012` 同信息相差 9 秒，10:01:03 vs 10:01:12；`ea64640 NOT_IN_HISTORY`，任何分支/remote 均不含） | **rev89 已修正**（cc_head 行 ea64640 → eb6b012 + 尾注）；教训固化入 652-C：入链 SHA 一律取自 `git log` 实测非记忆 |
| O-1 | — | **预测命中**: 审验端复跑后 m2 crosscheck 报告 4+/4- churn → checkout 还原树净（650 O-1 登记的持续观察第二次出现；加固建议仍开放: crosscheck 测试 tmpdir isolation） | 652 可选加固，不 gating |
| O-2 | — | 650 幽灵并发 flake 本刀未复发（任务书集合首跑全绿 144） | 关闭观察（若复发再登记） |
| 亮点 | — | 递补池 [EXHAUSTED] 收官 4 实现位置一钓到位且**先建分支后实战**（BLOCKED_NO_POOL 分支先于触发存在 = 防御性正确）；26 新测试含 5 类守门；HTTP 4/12；docs/75 §2 生命周期 4 阶段登记完整 | — |

### §E. 审验端裁定区

- ☐ **PASS** — （未选）
- ☑ **PASS（有限通过）**【定案 2026-09-02】— 651 链路**实交付、可复跑、可追溯**：任务书集合 **144/144 独立复跑 green**（≥126 达成；全套 163 为执行端口径，审验端环境截断不阻断）；6 commits 双推三 ref 全等 `8ae20de`；backfill 三齐；红线 14 条 + 增补 4 实现位置全到位；650 P4×2 更正落地（"sha anxi"=0）；**2×P4**（status 中间 SHA pin + cc_head 孤儿 SHA 错录〔rev89 已修正〕）→ 652-A.0 规范处置
- ☐ **FAIL** — （未选）

**不宣称任何 PASS** (per 红线 1)。**O1 仍 OPEN**。

### §F. 652 签发依据 (Cursor 审 PASS 后转架构师)

docs/75 §5.1 scope A (第 11 次扩展) — **沿用 651 模式 + BLOCKED 留痕 spike**：
- 红线 14 增补 4 实现位置已全部到位 (BLOCKED_NO_POOL 分支 + lineage JSONB red_line_14_status + 主 evidence substitute_pool_status + docs/75 §5 BLOCKED 留痕口径), 但 651 实际未触发 BLOCKED (双样本 fallback #1 REACHABLE)
- 652 scope = **M4.15 v9 spike 第 17/18 样本 + 强制触发 BLOCKED_NO_POOL 留痕** — 选 edge case 候选省 (XINJIANG + NEI MENGGU, 高 BLOCK 概率 验证红线 14 增补 e2e 可执行性)
- 已用省全集 (actual 口径, 16 省): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL / GUIZHOU / JIANGSU / SHAANXI / SICHUAN; 652 增量后 = 17/18 省 (若双样本均 REACHABLE)
- chain_id 末段 `_v9` (≠ 651 `_v8`); UUID k 段 (k02-k62) ≠ 651 j 段

— End 651 audit instruction 20260902 —

---

# ══════════ PART 2 / 652 任务书 ══════════

## 652-stage0-architect-m4-15-v9-blocked-spike-tasking (2026-09-02)

> **角色**: 架构师 → 执行端（沿用 645-651 模式：架构师自签 + 自交付，per 2026-08-31 21:50 豁免）
> **前置**: 651 DELIVERED + 审计 **PASS（有限通过）**（本文件 PART 1）; 递补池 [EXHAUSTED] + 红线 14 增补
> **scope**: scope A per docs/75 §5.1 = M4.15 v9（XINJIANG + NEI MENGGU 第 17/18 样本，edge case 高 BLOCK 概率，强制触发红线 14 增补 e2e BLOCKED_NO_POOL 留痕验证）+ O1 零动作
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS（**O1 仍 OPEN**）

### §0. 红线（14 条沿用，无新增 — docs/75 §1 §2 §4 已全部落地 4 实现位置）

1. 不宣布 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS
2. 不补零 / 不静默硬编码 value（domain 值 NULL 透明占位，沿用 641-651）
3. 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED；≤12 HTTP total（652 全刀预期 4-8）
4. 不改 docs/45/50/53/66/67/68/69/70/71/72/73/74/75 既有正文——修正项一律行内 append 尾注（例外: P4 typo 允许行内更正 + 尾注标记）
5. 不碰 4 fixture 锁值（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
6. 数据源唯一 = 政府/统计局/研究机构自取；用户零裁定；执行端不可提任何用户裁定事项
7. 完成 = observation SUCCESS，禁止 PARTIAL（**特例**: BLOCKED_NO_POOL 留痕是合法的"未完成"状态, per 红线 14; 落 `verdict=BLOCKED_NO_POOL` + `blocked_reason` 字段）
8. 不新写 016 migration（沿用 009+010+014+015 lineage JSONB）
9. chain_id = `'real_652_m4_15_policy_detail_v9'`（末段 `_v9`，≠ 651 `_v8` ≠ 650 `_v7`）
10. UUID **k 段**（k0eebc99 k1eebc99 ... k6eebc99，8 表前缀全 distinct）≠ 651 j 段 / 650 i 段 / 649 h 段 / 648 g 段 / 647 f 段 / 646 e 段 / 645 d 段 / 644 c 段
11. 不写 cegr.* 生产表（read-only；seed SQL 仅 staging 蓝本）
12. 既有 registry 行 SHA 零漂移；4 fixture 字节零触碰；m2 crosscheck 报告零 diff
13. 沿用: O1 零动作 + 附属产物指针 + 代换行标注规范（registry province/name = actual_province）
14. **沿用（递补池耗尽条款，2026-09-02 立; 651 §0.14 已固化）**: 5 候选全部 consumed [EXHAUSTED]; **652 强制验证 BLOCKED_NO_POOL 留痕 e2e**（XINJIANG + NEI MENGGU 双样本若两级 fallback 全失败 → BLOCKED 留痕, 不跨省代换; 若任一 REACHABLE 则 REACHABLE 落 evidence; 两种路径均需 e2e 验证）

### §1. 任务分解

**652-A.0 651 审计 P4×2 处置 + 规范固化**
- 652-C 写 EXEC-QUEUE rev90 时：status/§NOW 措辞**不 pin 中间 SHA**——以"三 ref 全等（HEAD=origin=github）+ 最终 HEAD SHA"表述（per 651 审计 P4-1；649 P4 同类教训终固化）
- **P4-2 教训固化**: cc_head/回执入链 SHA 一律取自 `git log --oneline` 实测输出（禁记忆/预写）；commit --amend 后必须复核 EXEC-QUEUE 已录 SHA 在历史中存在（per 651 审计 P4-2：ea64640 amend 孤儿错录，真实 eb6b012）
- O-1（m2 crosscheck 复跑污染）可选加固仍开放：crosscheck 测试 tmpdir isolation（不 gating；若实施在 652-B 加 1 守门）

**652-A.1 M4.15 v9 真实化 spike（第 17/18 样本；BLOCKED 留痕 e2e 验证）**
- 2 新样本（≤12 total）：
  - **XINJIANG (新疆)**: 首选 `https://www.xinjiang.gov.cn/zwgk/`; fallback #1 `https://www.xinjiang.gov.cn/`
  - **NEI MENGGU (内蒙古)**: 首选 `https://www.nmg.gov.cn/zwgk/`; fallback #1 `https://www.nmg.gov.cn/`
  - **目标**: 双样本两级 fallback 全失败 → 触发 BLOCKED_NO_POOL 留痕, 验证红线 14 增补 e2e 可执行性; 若任一 REACHABLE 也属合法 (REACHABLE 落 evidence, 不强求 BLOCKED)
- 产物: `scripts/fetch_m4_15_policy_detail_v9_2024.py` + `scripts/seed_m4_15_policy_detail_real_v9.sql`（2 样本 × 8 表 = 16 INSERT；语句数自报）
- lineage 全 `is_demo='false'`；chain_id 见红线 9；UUID k 段；2 真实 SHA distinct（≠ 638-651 全部）
- **BLOCKED_NO_POOL 留痕实现** (沿用 651 fetch_cell):
  - `SUBSTITUTE_POOL = []` (沿用 651 耗尽态)
  - `SUBSTITUTE_POOL_STATUS = "EXHAUSTED"`
  - 若双样本两级 fallback 全失败 → `verdict = "BLOCKED_NO_POOL"` + `blocked_reason = "递补池已耗尽 [EXHAUSTED]; 两级 fallback 全失败; 不跨省代换"` + `summary.blocked_no_pool_count += 1`
  - 若任一 REACHABLE → REACHABLE 正常落 evidence (不强求 BLOCKED)

**652-A.2 O1 零动作（沿用）**

**652-A.3 docs/76 §1-§6**（§2 含**BLOCKED 留痕 e2e 验证登记表**；§4 含 chain_id 区分 15 真实化刀 + UUID 严格递增 + 累 [BLOCKED_NO_POOL] 触发事件计数）

**652-A.4 evidence ×2**: `docs/reports/m4_15_policy_detail_real_v9_20260902.md` + `evidence_pack/m4_15_policy_detail_real_v9_20260902.json`
- 主 evidence methodology 含 "Per 652 §0.14: BLOCKED_NO_POOL 留痕 e2e 验证. 递补池 [EXHAUSTED] 沿用 651. 本次双样本结果: REACHABLE×n / BLOCKED_NO_POOL×(2-n)."

**652-B 测试**: `tests/test_m4_15_policy_detail_real_v9.py` ≥8（守门: 2 SHA distinct ≠ 638-651 / k 段 ≠ j·i·h·g·f·e·d·c / chain_id `_v9` / 16 INSERT（两态: 若一省 BLOCKED_NO_POOL 则该省 0 INSERT + evidence BLOCKED cell, INSERT 数按实报并说明）/ is_demo='false' / docs/76 六节 / **BLOCKED 留痕 e2e 守门**〔fetch 脚本含 BLOCKED_NO_POOL 分支 + evidence 记 blocked_reason + 不跨省代换〕/ **沿用 651 红线 14 增补守门**）; 回归 651 侧 12 文件集 144 + ≥8 新 = **≥152 green**（底限 ≥145）

**652-C 回执 + commit + 双推**: 回执 `652-stage0-cc-m4-15-v9-blocked-spike-receipt-20260902.md`；EXEC-QUEUE rev89（651 审计，本次）→ **rev90**（652 交付；三齐 + header 同步 + **A.0 status 措辞规范**沿用）

### §2. 验收命令（审验端一键）

```bash
cd "/Users/kjonekong/projects/china platform"
python3 -m pytest tests/test_m4_15_policy_detail_real_v9.py tests/test_m4_14_policy_detail_real_v8.py tests/test_m4_13_policy_detail_real_v7.py tests/test_m4_12_policy_detail_real_v6.py tests/test_m4_11_policy_detail_real_v5.py tests/test_m4_10_reverify_jx.py tests/test_m2_report_hygiene.py tests/test_m4_10_policy_detail_real_v4.py tests/test_m4_9_policy_detail_real_v3.py tests/test_o1_live_candidate_probe.py tests/test_m6_spike_docs_closure.py tests/test_m4_8_policy_detail_real_v2.py -q
# 期望 ≥152 passed (底限 ≥145)
git log --oneline -8 && git status -s
# 重点核查 m2 报告零 diff:
git diff docs/reports/m2_2024_gdp_crosscheck_20260831.md | head -5
# 重点核查 4 fixture 零触碰:
for sha in e30ee811 9232efdb 937255a5 9056001c; do
  echo "fixture SHA $sha: $(grep -c "$sha" source_registry/registry.csv || echo 0)"
done
```

— End 652 tasking 20260902 —

— End consolidated 651 audit + 652 tasking 20260902 —
