# 652 审验裁定 + 653 任务书 — 合并归档 (2026-09-02)

> 单文件模式（per 用户指示 2026-09-01 起，对话不再展示全文）。
> Part 1 = 652 审验裁定（Cursor 审验端）；Part 2 = 653 任务书（架构师签发）。EXEC-QUEUE 指针以本件为准。

---

# ══════════ PART 1 / 652 审验裁定 ══════════

## 652-stage0-cursor-s652-m4-15-v9-blocked-e2e-audit — 审验裁定（2026-09-02 定案）

> **角色**: Cursor（审验端）
> **对象**: 652 完整链路（M4.15 v9 xinjiang/nei_menggu + BLOCKED_NO_POOL e2e 验证 + 651 审计 P4×2 规范固化）
> **入口**: 回执 `652-stage0-cc-m4-15-v9-blocked-spike-receipt-20260902.md` · 任务书 `651-audit-652-tasking-consolidated-20260902.md` PART 2 · 主 evidence `evidence_pack/m4_15_policy_detail_real_v9_20260902.json` · 附属报告 `docs/reports/m4_15_policy_detail_real_v9_20260902.md` · 架构师审查 `docs/76-m4-15-policy-detail-real-v9-20260902.md`
> **裁定（定案）**: **PASS（有限通过）** — 0×P3 + **1×P4**（rev90 status 行 pin 中间 SHA `04721b7` 为"终态 HEAD"且"待 §C-5 双推复核"陈旧未收口——第三型自指陈旧复发，与执行端自身 P4-1 固化规则冲突；§NOW 已正确收口，实质无损 → rev91 修正 + 653-A.0 规范 v2）
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS；**O1 仍 OPEN**

### §A. 独立复跑（审验端一手 — 已执行 2026-09-02）

| # | 验收项 | 结果（实测） |
|---|---|---|
| A1 | pytest 652 任务书 §2 12 文件集 | **171 passed in 1.71s**（= 27 新 + 144 回归；≥152 达成 +12%，底限 ≥145 超 18%）✓ |
| A2 | 环境瞬态 | 任务书集合首跑即全绿；O-2（幽灵并发）未复发维持关闭；O-1（m2 复跑污染）本刀**未复发**（复跑后 m2 报告零 diff）✓ |
| A3 | git 链 652 7 commits | `c58d91d`(A.0)→`04721b7`(delivery)→`6bb6817`(cc_head rev90)→`d98cba0`(receipt)→`c093abf`(backfill)→`0a3d284`(§NOW 刷新)→`5537aff`(链补) 全在 ✓ |
| A4 | 双推复核 | HEAD = origin/main = github/main = `5537aff` 三向全等 ✓（回执"STOP R90 · 5537aff · 27/27"信号与实测一致）|
| A5 | backfill 三齐 + P4-2 amend-first | cc_head 链 append `04721b7`/`6bb6817`/`d98cba0`/`c093abf` 全部 git log 实测在史 ✓；**amend-first 规则首次正确执行**（"TBD-self-SHA → c093abf 替换"——预写占位后 amend 再回填，无孤儿）✓；last_receipt = `d98cba0` ✓ |
| A6 | 树净 | 0 ✓ |
| A7 | 4 fixture 锁值 | registry.csv 零触碰（4 SHA 均 0 漂移；守门由 171 green 测试集承担）✓ |

### §B. 交付物逐项核验（8 项）

| # | 项 | 结果 |
|---|---|---|
| B1 | A.0 P4×2 规范固化落点 | `docs/75:283-288` +6 行 append-only（0 删，红线 4 合规）；`651 receipt` +6 行 append-only（0 删）✓；P4-2"amend 先完成再写链文本"规则明文化 ✓ |
| B2 | M4.15 v9 真实化 | 16 INSERT ROWS（12 政策 + 2 registry + 2 document）；chain_id `real_652_m4_15_policy_detail_v9`（`_v9` ≠ 全前序）；UUID **k 段** 8 表前缀全 distinct；2 NEW SHA `21c8211b`（xinjiang 403 WAF→`/` 200, 108,841B）+ `da1d4104`（nei_menggu `/zwgk/` 200 直命中, 137,602B）distinct ≠ 638-651 全部 ✓；HTTP **3/12**（并列全链最优）；substitute=0；is_demo 全 'false'；lineage 全 red_line_14_status='EXHAUSTED' ✓ |
| B3 | BLOCKED_NO_POOL e2e 验证 | 4 实现位置全到位（fetch 分支 ×14 命中 + blocked_reason / seed 17 处 EXHAUSTED / evidence summary 字段 + methodology 援引 / docs/76 §2 登记表）；5 守门 PASSED（branch_present + count_zero_but_field_present + red_line_14 ×3）；**两态结论 = REACHABLE×2**（任务书明文"任一 REACHABLE 也属合法，不强求 BLOCKED"）✓；注：真网 BLOCKED 路径至今零触发 → 653 复试再攻（见 §F）|
| B4 | O1 零动作 | 无 probe / 无 registry / 无 connector 触碰；docs/52 零改动 ✓ |
| B5 | docs/76 §1-§6 | 286 行六节全（§2 BLOCKED 留痕 e2e 验证登记表 + §5.2 留痕口径 4 落点模板 + §5.3 红线守护 20 里程碑不宣称）✓ |
| B6 | evidence ×2 | 主 JSON（uuid_prefixes 8 表 + cells 逐 attempt + methodology 含 652 §0.14/651 §0.14/648 P3-1 援引）+ 附属报告 ✓ |
| B7 | 652-B 测试 | **27 cases**（≥8 要求 3.4×；守门覆盖：2 SHA distinct / k 段 8 前缀 / chain_id 7 代区分 / 16 INSERT / is_demo / blocked 分支+字段双守门 / docs/76 六节+登记表 / P4×2 尾注落地守门 / red_line_14 ×3 / 不宣称 PASS）✓ |
| B8 | rev90 | header = §META = 90 ✓；§NOW 收口完整（三 commit 入链 + last_receipt 更新 + amend-first 执行记录）；**status 行未随 §NOW 同步收口** → P4-1 |

### §C. 红线 14 条复核

14/14 全 ✓（重点：红线 3 HTTP 3/12 实测吻合 fetch_log 3 请求〔xinjiang 403+200 / nei_menggu 200〕；红线 4 docs/75+receipt 仅 append 尾注 0 删；红线 13 全 16 INSERT actual_province 直用零 substitute；红线 14 EXHAUSTED 沿用 + e2e 验证机制模板化固化——为后续真触发备好守门标准）。

### §D. 发现（审验端定案）

| 级 | # | 发现 | 处置 |
|---|---|---|---|
| P3 | — | 无 | — |
| P4 | 1 | **status 行第三型自指陈旧复发**：rev90 §CURRENT status 写"三 ref 全等终态 `HEAD=04721b7`"——实际终态 `5537aff`（写入时已至少落后 2 commits）；且"待 §C-5 双推复核"在 0a3d284 复核通过后未清除；**与执行端本刀自己固化的 P4-1 规则（docs/75:283"中间 SHA 一律不入 status 文本"）直接冲突**。§NOW 已正确收口，实质无损 | **rev91 修正**（本审计）；653-A.0 规范 v2：status 收口与 §NOW 同 commit 原子完成，"待复核"字样复核后必须清除 |
| O-1 | — | m2 复跑污染本刀未复发（复跑后零 diff） | 维持关闭；tmpdir 加固仍开放不 gating |
| 亮点 | — | **amend-first 规则首次零失误执行**（TBD→c093abf，无孤儿 SHA）；171 green 超底限 18%；HTTP 3/12 并列全链最优；BLOCKED e2e 验证机制模板化（4 位置+5 守门）沉淀为 docs/76 §5.2 可复用标准；nei_menggu 首选直命中证明 v9 fallback_chain 设计有效 | — |

### §E. 审验端裁定区

- ☑ **PASS（有限通过）**【定案 2026-09-02】— 652 链路**实交付、可复跑、可追溯**：12 文件集 **171/171 独立复跑 green**；7 commits 双推三 ref 全等 `5537aff`；backfill 三齐 + amend-first 首次正确执行；红线 14 条全 ✓；BLOCKED_NO_POOL e2e 两态合法落 REACHABLE×2 + 验证机制模板化；**1×P4**（status 行陈旧）→ rev91 修正 + 653-A.0 规范 v2

**不宣称任何 PASS**（per 红线 1）。**O1 仍 OPEN**。

### §F. 653 签发依据（Cursor 审 PASS 后转架构师）

docs/76 §5.1 scope A（第 12 次扩展）— **双 BLOCKED 史省复试**：
- 真网 BLOCKED_NO_POOL 路径至今零触发（652 选 xinjiang/nei_menggu 预期高 BLOCK 但双 REACHABLE）；**最大概率触发器 = 复试 647 shandong（4 连 BLOCKED 史：域名错配+403）+ 649 hubei（412×2 史，槽被代换 actual=LN）**
- 两态均收官价值高：若真触发 → **首次真网 BLOCKED_NO_POOL 留痕**（红线 14 e2e 完全体）；若 REACHABLE → SHANDONG/HUBEI 以 actual 口径入集（消除 647/649 槽名遗留歧义，已用省 18→20）
- chain_id 末段 `_v10`；UUID l 段；递补池 [EXHAUSTED] 沿用

— End 652 audit 20260902 —

# ══════════ PART 2 / 653 任务书 ══════════

## 653-stage0-architect-m4-16-v10-retry-spike-tasking (2026-09-02)

> **角色**: 架构师 → 执行端（沿用 645-652 模式：架构师自签 + 自交付，per 2026-08-31 21:50 豁免）
> **前置**: 652 DELIVERED + 审计 **PASS（有限通过）**（本文件 PART 1; 1×P4）
> **scope**: scope A per docs/76 §5.1 = M4.16 v10（**shandong + hubei 双复试**，第 19/20 样本；647 shandong 4 连 BLOCKED 史 + 649 hubei 槽被代换史；**真网 BLOCKED_NO_POOL 首触发最佳概率**；两态合法）+ O1 零动作
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS（**O1 仍 OPEN**）

### §0. 红线（14 条沿用，无新增）

1. 不宣布 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS
2. 不补零 / 不静默硬编码 value（domain 值 NULL 透明占位）
3. 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED；≤12 HTTP total（653 全刀预期 4-8）
4. 不改 docs/45/50/53/66-76 既有正文——修正项一律行内 append 尾注（例外: P4 typo 允许行内更正 + 尾注标记）
5. 不碰 4 fixture 锁值（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
6. 数据源唯一 = 政府/统计局/研究机构自取；用户零裁定
7. 完成 = observation SUCCESS，禁止 PARTIAL（**特例**: BLOCKED_NO_POOL 留痕是合法"未完成"态，per 红线 14）
8. 不新写 016 migration（沿用 009+010+014+015 lineage JSONB）
9. chain_id = `'real_653_m4_16_policy_detail_v10'`（末段 `_v10`，≠ 652 `_v9` ≠ 651 `_v8`）
10. UUID **l 段**（l0eebc99 l1eebc99 ... l6eebc99，8 表前缀全 distinct）≠ 652 k 段及全前序
11. 不写 cegr.* 生产表（read-only；seed SQL 仅 staging 蓝本）
12. 既有 registry 行 SHA 零漂移；4 fixture 零触碰；m2 crosscheck 报告零 diff
13. 沿用: O1 零动作 + 附属产物指针 + 代换行标注规范（registry province/name = actual_province）
14. **沿用（递补池耗尽条款）**: [EXHAUSTED]；**653 复试若两级 fallback 全失败 → 真网首次 BLOCKED_NO_POOL 留痕**（不跨省代换；seed 该省 0 INSERT + cell 占位 + blocked_reason；若 REACHABLE → 正常 16 INSERT）；两态均需 lineage 标注 `retry_of`（shandong ← 647 BLOCKED×4；hubei ← 649 substituted actual=LIAONING）

### §1. 任务分解

**653-A.0 652 审计 P4-1 处置 + 规范 v2**
- status 收口与 §NOW 刷新**同 commit 原子完成**；"待复核/待 §C-x"字样在复核通过后**必须清除**；status 文本如需引 HEAD 一律 `git log -1` 实测终态（或不写 SHA 仅写"三 ref 全等"）
- 沿用 652-A.0 P4-2 amend-first 规则（先 amend 后写链文本）

**653-A.1 M4.16 v10 双复试 spike（第 19/20 样本）**
- 2 样本（≤12 total）：
  - **SHANDONG（复试）**: 首选 `https://www.shandong.gov.cn/zwgk/`; fallback `https://www.shandong.gov.cn/`
  - **HUBEI（复试）**: 首选 `https://www.hubei.gov.cn/zwgk/`; fallback `https://www.hubei.gov.cn/`
- 产物: `scripts/fetch_m4_16_policy_detail_v10_2024.py` + `scripts/seed_m4_16_policy_detail_real_v10.sql`
- 两态: 双 REACHABLE → 2×8 = 16 INSERT + 2 NEW SHA distinct；任一 BLOCKED → 该省 0 INSERT + evidence BLOCKED cell（verdict=BLOCKED_NO_POOL + blocked_reason）+ 另一省正常落（INSERT 数按实报并说明）
- lineage 全 `is_demo='false'`；全行加 `retry_of` 字段；chain_id/UUID 见红线 9/10

**653-A.2 O1 零动作（沿用）**

**653-A.3 docs/77 §1-§6**（§2 复试 redemption / BLOCKED 留痕登记表——沿用 docs/76 §5.2 模板；§4 chain_id 区分 16 真实化刀 + UUID 严格递增至 l 段 + 累计 SHA 表）

**653-A.4 evidence ×2**: `docs/reports/m4_16_policy_detail_real_v10_20260902.md` + `evidence_pack/m4_16_policy_detail_real_v10_20260902.json`（methodology 含 653 §0.14 复试援引 + retry_of 说明）

**653-B 测试**: `tests/test_m4_16_policy_detail_real_v10.py` ≥8（守门: SHA/UUID/chain_id/INSERT 两态口径/is_demo/retry_of 落地/docs/77 六节/BLOCKED 分支+字段/P4-A.0 规范 v2 落点）；回归 652 侧 12 文件集 171 + ≥8 新 = **≥179 green（底限 ≥175）**

**653-C 回执 + commit + 双推**: 回执 `653-stage0-cc-m4-16-v10-retry-spike-receipt-20260902.md`；EXEC-QUEUE rev91（652 审计，本次）→ **rev92**（653 交付；三齐 + header 同步 + **A.0 规范 v2 原子收口**）

### §2. 验收命令（审验端一键）

```bash
cd "/Users/kjonekong/projects/china platform"
python3 -m pytest tests/test_m4_16_policy_detail_real_v10.py tests/test_m4_15_policy_detail_real_v9.py tests/test_m4_14_policy_detail_real_v8.py tests/test_m4_13_policy_detail_real_v7.py tests/test_m4_12_policy_detail_real_v6.py tests/test_m4_11_policy_detail_real_v5.py tests/test_m4_10_reverify_jx.py tests/test_m2_report_hygiene.py tests/test_m4_10_policy_detail_real_v4.py tests/test_m4_9_policy_detail_real_v3.py tests/test_o1_live_candidate_probe.py tests/test_m6_spike_docs_closure.py tests/test_m4_8_policy_detail_real_v2.py -q
# 期望 ≥179 passed (底限 ≥175)
git log --oneline -8 && git status -s
git diff docs/reports/m2_2024_gdp_crosscheck_20260831.md | head -5   # 期望空
grep -c "retry_of" scripts/seed_m4_16_policy_detail_real_v10.sql      # 期望 ≥2
```

— End 653 tasking 20260902 —

— End consolidated 652 audit + 653 tasking 20260902 —

