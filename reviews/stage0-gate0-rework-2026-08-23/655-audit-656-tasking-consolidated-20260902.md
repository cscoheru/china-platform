# 655 审验裁定 + 656 任务书 — 合并归档 (2026-09-02)

> 单文件模式（per 用户指示 2026-09-01 起，对话不再展示全文）。
> Part 1 = 655 审验裁定（Cursor 审验端）；Part 2 = 656 任务书（架构师签发）。EXEC-QUEUE 指针以本件为准。

---

# ══════════ PART 1 / 655 审验裁定 ══════════

## 655-stage0-cursor-s655-m4-18-v12-west-finale-audit — 审验裁定（2026-09-02 定案）

> **角色**: Cursor（审验端）
> **对象**: 655 完整链路（M4.18 v12 NINGXIA+XIZANG 西部七省区全覆盖终章 + **首次混合态 PARTIAL_BLOCKED** + 规范 v3.1 七字段原子落地）
> **入口**: 回执 `655-stage0-cc-m4-18-v12-west-finale-receipt-20260902.md` · 任务书 `654-audit-655-tasking-consolidated-20260902.md` PART 2 · 主 evidence `evidence_pack/m4_18_policy_detail_real_v12_20260902.json` · `docs/79-m4-18-policy-detail-real-v12-20260902.md`
> **裁定（定案）**: **PASS（有限通过）** — 0×P3 + **2×P4**（① §META tasking 行 + §NOW 段残留"进行中 4/7 / 待 commit / 双推待 user 授权"陈旧中间态文本〔commit 5 写入后 6/7 落地未刷新——653 P4-2 第三型同类〕② **O-1 第三次复发**：审验端复跑 15 文件集后 m2 报告被自动改写〔语义漂移 5/37→5/34、13.5%→14.7% 分母变化〕→ 已按 653 规则"第三次复发即还原"**还原 ✓**；656-A.2 增设根因修复任务）
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS；**O1 仍 OPEN**

### §A. 独立复跑（审验端一手 — 已执行 2026-09-02）

| # | 验收项 | 结果（实测） |
|---|---|---|
| A1 | pytest 655 任务书 §2 15 文件集 | **243 passed in 1.77s**（= 26 新 + 217 回归；≥225 达成 +8%，底限 ≥221 超 9.9%）✓ |
| A2 | 环境瞬态 | **O-1 第三次复发**：复跑后 m2 报告被改写（分母 5/37→5/34 语义漂移非纯时间戳）→ **已还原**（git checkout，树净 0 复核 ✓）per 653 规则；O-2 维持关闭 |
| A3 | git 链 655 7 commits | `86314f9`(delivery)→`07ba595`(cc_head rev96)→`3b1e44f`(receipt 13 节)→`b5fd9c7`(backfill last_receipt)→`77a37c3`(§NOW+七字段原子; amend-first: pre-amend `e12128f` 已替换)→`47ddb6d`(链补)→`c99d443`(链补终同步) 全在 ✓ |
| A4 | 双推复核 | HEAD = origin/main = github/main = `c99d443` 三向全等 ✓ |
| A5 | 规范 v3.1 七字段原子 | **首次完整落地 ✓**：header line 3 rev96 ✓ / §META 五字段 ✓ / §CHAIN_TAIL 655 OPEN→DELIVERED ✓；**status 行零 SHA ✓**（v3.1 终极条款达成，654 P4-1 病灶消除实证）；amend-first ✓（pre-amend `e12128f` NOT_IN_HISTORY 模式沿用）；**例外**: tasking 行含"进行中 4/7…待 commit…待 user 授权"陈旧文本 → P4-1 |
| A6 | 树净 | 交付态 0 ✓（audit 侧 O-1 复发已还原） |
| A7 | O1 零动作 | 无 probe/registry/connector；docs/52 零改动 ✓ |

### §B. 交付物逐项核验（8 项）

| # | 项 | 结果 |
|---|---|---|
| B1 | M4.18 v12 西部终章双省 | **首次混合态 PARTIAL_BLOCKED**：NINGXIA `/zwgk/`+`/` **405×2（405+WAF 网防 G01 marker——全链第三例首见失败形式，入失败形式库）**→ BLOCKED_NO_POOL；XIZANG `/zwgk/`+`/` **200×2 直命中 REACHABLE**，NEW SHA `855af02fd8ee…f82a`（64 位完整）；HTTP **3/12（=25%，全链历史最低并列）**；substitute_used=0 ✓ |
| B2 | 三态处置 | 8 INSERT ROWS（xizang 1 样本 × 8 表）+ ningxia BLOCKED 三重留痕（evidence blocked_reason 完整援引链 + docs/79 §2 登记表 + receipt）；retry_of=N/A 首试口径（ningxia 无前史 BLOCKED 留痕 / xizang 首试直命中）✓ |
| B3 | blocked_reason 质量 | ningxia 完整：两级 fallback 实测码 405/405 + WAF G01 marker + 红线 14 援引 + 池耗尽声明 + retry_of=N/A 依据 ✓ |
| B4 | docs/79 §1-§6 | 六节全；§3 **西部七省区全覆盖叙事终章表**（SHAANXI/XINJIANG/NEIMENGGU/XIZANG REACHABLE + GANSU/QINGHAI/NINGXIA BLOCKED = 4R+3B 全登记）；§5 失败形式库滚动（累计 3 条：SSL handshake / Connection reset / 405+WAF）✓ |
| B5 | evidence ×2 | 主 JSON + 附属报告 ✓ |
| B6 | 655-B 测试 | **26 cases**（≥8 要求 3.3×；含混合态三态口径 + n 段 UUID + retry_of=N/A + 七字段原子守门）✓ |
| B7 | rev96 | header = §META = 96 ✓（v3.1 七字段原子首执） |
| B8 | 西部叙事收官 | 七省区 × 刀次 × 结果终章表入 docs/79 §3 ✓；已用省（REACHABLE actual 口径）18→**19**（+xizang） |

### §C. 红线 14 条复核

14/14 全 ✓（重点：红线 3 HTTP 3/12 实测吻合〔历史最低并列〕；红线 7 PARTIAL 特例正确援引〔混合态 8 INSERT 实报〕；红线 13 已用省 18→19〔xizang REACHABLE 增量 +1；ningxia BLOCKED 不计 actual 口径〕；红线 14 混合态分支首触发——**三态机制 e2e 完全体收口：651/652 双 REACHABLE + 653/654 双 BLOCKED + 655 混合态，五刀全覆盖三态空间**）。

### §D. 发现（审验端定案）

| 级 | # | 发现 | 处置 |
|---|---|---|---|
| P3 | — | 无 | — |
| P4 | 1 | **§META tasking 行 + §NOW 段陈旧中间态文本**：tasking 行写"7 commits 进行中 4/7 … commit 5/6/7 待 commit；双推 origin + github 待 user 授权"——commit 5/6/7 已全部落地且双推完成（三 ref 全等 `c99d443`），文本未收口（commit 5 写入后 6/7 落地未回刷）；§NOW 段同类残留"4 commits 已落…commit 5 落地"——653 P4-2 第三型（"待 §C-x"陈旧）同类复发 | **rev97 修正**（tasking/§NOW 重写为终态语义）；**规范 v3.2**：交付终态时 §META/§NOW 范围内**中间态文本零残留**（"进行中 x/7 / 待 commit / 待授权 / 待 §C-x"字样在 DELIVERED+C 终态必须清零，迁移注记只入 commit message） |
| P4 | 2 | **O-1 第三次复发（语义级）**：审验端复跑 15 文件集后 `docs/reports/m2_2024_gdp_crosscheck_20260831.md` 被自动改写——非时间戳漂移而是**分母语义漂移**（5/37→5/34、13.5%→14.7%、threshold 0.0676→0.0735），根因 = `test_m2_report_hygiene` 重跑时按当前 DB/registry 状态重算覆盖率并回写报告 | **已按 653 规则还原**（git checkout，树净复核 0）✓；**656-A.2 根因修复任务**：hygiene 测试只读化（断言不改写已提交报告；分母来源钉死或写入 tmp 对照），修复后红线 12"m2 零 diff"由机制保障而非人工还原 |
| O-1 | — | 复发已处置 | 656-A.2 转根因修复后关闭观察 |
| 亮点 | — | **混合态 PARTIAL_BLOCKED 首触发 = 三态机制 e2e 完全体收口**（651/652 双 R + 653/654 双 B + 655 混合）；405+WAF G01 第三例首见失败形式；xizang 200×2 直命中 + 完整 64 位 NEW SHA；七字段原子首次完整落地（status 零 SHA 病灶消除实证）；HTTP 3/12 历史最低并列；26 守门 3.3× 超配；amend-first 零失误 | — |

### §E. 审验端裁定区

- ☑ **PASS（有限通过）**【定案 2026-09-02】— 655 链路**实交付、可复跑、可追溯**：15 文件集 **243/243 独立复跑 green**；7 commits 双推三 ref 全等 `c99d443`；红线 14 全 ✓；混合态首触发 + 西部七省区全覆盖终章；**2×P4**（tasking/§NOW 中间态残留 + O-1 第三次复发已还原）→ rev97 修正 + 规范 v3.2 + 656-A.2 根因任务

**不宣称任何 PASS**（per 红线 1）。**O1 仍 OPEN**。

### §F. 656 签发依据（Cursor 审 PASS 后转架构师）

docs/79 §6 后续候选 + 654/655 审计 §F 滚动 — **华南双省对**：
- 剩余未试省（4 个）：HEBEI / SHANXI / GUANGXI / HAINAN
- **656 = GUANGXI + HAINAN**（华南双省对；两省无前史首试 → retry_of=N/A；三态合法沿用 653/654/655 全模板；657 留 HEBEI+SHANXI 华北收官 → 全国 31 省 spike 全集终章）
- chain_id 末段 `_v13`；UUID **o 段**；递补池 [EXHAUSTED] 沿用
- **656-A.2 新增**: O-1 根因修复（hygiene 只读化）——655 P4-2 处置

— End 655 audit 20260902 —

# ══════════ PART 2 / 656 任务书 ══════════

## 656-stage0-architect-m4-19-v13-south-spike-tasking (2026-09-02)

> **角色**: 架构师 → 执行端（沿用 645-655 模式：架构师自签 + 自交付，per 2026-08-31 21:50 豁免）
> **前置**: 655 DELIVERED + 审计 **PASS（有限通过）**（本文件 PART 1; 2×P4）
> **scope**: scope A per docs/79 §6 = M4.19 v13（**GUANGXI + HAINAN**，第 25/26 样本，华南双省对；两省无前史首试 retry_of=N/A；三态合法）+ **O-1 根因修复** + O1 零动作
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS（**O1 仍 OPEN**）

### §0. 红线（14 条沿用，无新增）

1. 不宣布 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS
2. 不补零 / 不静默硬编码 value（domain 值 NULL 透明占位）
3. 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED；≤12 HTTP total（656 全刀预期 4-8）
4. 不改 docs/45/50/53/66-79 既有正文——修正项一律行内 append 尾注（例外: P4 typo 允许行内更正 + 尾注标记）
5. 不碰 4 fixture 锁值（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
6. 数据源唯一 = 政府/统计局/研究机构自取；用户零裁定
7. 完成 = observation SUCCESS，禁止 PARTIAL（特例: BLOCKED_NO_POOL 留痕合法，per 红线 14）
8. 不新写 016 migration（沿用 009+010+014+015 lineage JSONB）
9. chain_id = `'real_656_m4_19_policy_detail_v13'`（末段 `_v13`，≠ 655 `_v12` ≠ 654 `_v11`）
10. UUID **o 段**（o0eebc99 o1eebc99 ... o6eebc99，8 表前缀全 distinct）≠ 655 n 段及全前序
11. 不写 cegr.* 生产表（read-only；seed SQL 仅 staging 蓝本）
12. 既有 registry 行 SHA 零漂移；4 fixture 零触碰；m2 crosscheck 报告零 diff（**656-A.2 修复后由机制保障**）
13. 沿用: O1 零动作 + 附属产物指针 + 代换行标注规范（actual_province 口径）
14. **沿用（递补池耗尽条款）**: [EXHAUSTED]；两级 fallback 全失败 → BLOCKED_NO_POOL 留痕不代换（653/654/655 三态全模板）；GUANGXI/HAINAN 无前史首试 → retry_of=N/A；三态合法（INSERT 数按实报并说明；混合态 per 655 模板）

### §1. 任务分解

**656-A.0 655 审计 P4×2 处置 + 规范 v3.2**
- **中间态文本零残留**（v3.2）：交付终态（DELIVERED+C）时 §CURRENT/§META **活动状态行**范围内"进行中 x/7 / 待 commit / 待 user 授权 / 待 §C-x"字样必须清零——迁移注记只入 commit message（655 P4-1 杜绝；审计裁定区/§ACK 对发现的**历史性引用除外**）
- 沿用: v3.1 七字段原子（header/§META 五字段/CHAIN_TAIL 同 commit）+ status 零 SHA + amend-first

**656-A.1 M4.19 v13 华南双省 spike（第 25/26 样本）**
- 2 样本（≤12 total）：
  - **GUANGXI**: 首选 `https://www.gxzf.gov.cn/zwgk/`; fallback `https://www.gxzf.gov.cn/`
  - **HAINAN**: 首选 `https://www.hainan.gov.cn/zwgk/`; fallback `https://www.hainan.gov.cn/`
- 产物: `scripts/fetch_m4_19_policy_detail_v13_2024.py` + `scripts/seed_m4_19_policy_detail_real_v13.sql`
- 三态: 双 REACHABLE → 16 INSERT + 2 NEW SHA；混合 → 按省实报（per 655 模板）；双 BLOCKED → 0 INSERT + 三重留痕（per 653/654 模板）
- lineage 全 `is_demo='false'`；chain_id/UUID 见红线 9/10

**656-A.2 O-1 根因修复（新设——655 P4-2 处置）**
- 对象: `tests/test_m2_report_hygiene.py`（复跑自动改写 `docs/reports/m2_2024_gdp_crosscheck_20260831.md`，语义漂移 5/37→5/34）
- 目标: **hygiene 测试只读化**——断言计算与报告对照但不回写已提交报告（分母来源钉死或写 tmp 对照）；修复后"15 文件集连跑两遍 → m2 报告零 diff"由机制保障
- 守门: 新增 ≥2 测试（修复前后行为锁定）；修复说明入 docs/80 §5（尾注式，不改既有正文）
- 红线 12 升级: 零 diff 从"人工还原"转为"机制保障"

**656-A.3 O1 零动作（沿用）**

**656-A.4 docs/80 §1-§6**（§2 沿用 BLOCKED 留痕登记表模板〔若触发〕；§4 失败形式库滚动〔已 3 条〕+ 华南叙事; §5 含 656-A.2 O-1 修复说明尾注）

**656-A.5 evidence ×2**: `docs/reports/m4_19_policy_detail_real_v13_20260902.md` + `evidence_pack/m4_19_policy_detail_real_v13_20260902.json`

**656-B 测试**: `tests/test_m4_19_policy_detail_real_v13.py` ≥8（守门: SHA/UUID o 段/chain_id `_v13`/INSERT 三态口径/is_demo/retry_of=N/A 首试口径/docs/80 六节/BLOCKED 分支+字段/规范 v3.2 落点〔中间态零残留〕）+ 656-A.2 修复锁定 ≥2；回归 15 文件集 243 + ≥10 = **≥253 green（底限 ≥249）**

**656-C 回执 + commit + 双推**: 回执 `656-stage0-cc-m4-19-v13-south-receipt-20260902.md`；EXEC-QUEUE rev97（655 审计，本次）→ **rev98**（656 交付；七字段原子 + v3.2 中间态零残留）

### §2. 验收命令（审验端一键）

```bash
cd "/Users/kjonekong/projects/china platform"
python3 -m pytest tests/test_m4_19_policy_detail_real_v13.py tests/test_m4_18_policy_detail_real_v12.py tests/test_m4_17_policy_detail_real_v11.py tests/test_m4_16_policy_detail_real_v10.py tests/test_m4_15_policy_detail_real_v9.py tests/test_m4_14_policy_detail_real_v8.py tests/test_m4_13_policy_detail_real_v7.py tests/test_m4_12_policy_detail_real_v6.py tests/test_m4_11_policy_detail_real_v5.py tests/test_m4_10_reverify_jx.py tests/test_m2_report_hygiene.py tests/test_m4_10_policy_detail_real_v4.py tests/test_m4_9_policy_detail_real_v3.py tests/test_o1_live_candidate_probe.py tests/test_m6_spike_docs_closure.py tests/test_m4_8_policy_detail_real_v2.py -q
# 期望 ≥253 passed (底限 ≥249); **连跑两遍**
git diff docs/reports/m2_2024_gdp_crosscheck_20260831.md | head -5   # 期望空 ×2 遍（O-1 修复机制保障）
git log --oneline -9 && git status -s
grep -c "guangxi\|hainan" scripts/seed_m4_19_policy_detail_real_v13.sql  # 期望 ≥2（若 REACHABLE）
grep -n "进行中\|待 commit\|待 user" reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md | grep -v '^.*§ACK\|65[0-9] 审计' | wc -l   # 期望 0（v3.2; §CURRENT/§META 活动态零残留——§ACK/裁定区历史引用除外）
```

— End 656 tasking 20260902 —

— End consolidated 655 audit + 656 tasking 20260902 —

