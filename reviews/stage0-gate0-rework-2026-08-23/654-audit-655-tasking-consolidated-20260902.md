# 654 审验裁定 + 655 任务书 — 合并归档 (2026-09-02)

> 单文件模式（per 用户指示 2026-09-01 起，对话不再展示全文）。
> Part 1 = 654 审验裁定（Cursor 审验端）；Part 2 = 655 任务书（架构师签发）。EXEC-QUEUE 指针以本件为准。

---

# ══════════ PART 1 / 654 审验裁定 ══════════

## 654-stage0-cursor-s654-m4-17-v11-northwest-audit — 审验裁定（2026-09-02 定案）

> **角色**: Cursor（审验端）
> **对象**: 654 完整链路（M4.17 v11 GANSU+QINGHAI 西北四连收官 + 首试省双 BLOCKED_NO_POOL 触发 + P4-A.0 规范 v3 落地）
> **入口**: 回执 `654-stage0-cc-m4-17-v11-northwest-receipt-20260902.md` · 任务书 `653-audit-654-tasking-consolidated-20260902.md` PART 2 · 主 evidence `evidence_pack/m4_17_policy_detail_real_v11_20260902.json` · `docs/78-m4-17-policy-detail-real-v11-20260902.md`
> **裁定（定案）**: **PASS（有限通过）** — 0×P3 + **2×P4**（① rev94 status 行自宣称"本行不含任何具体 SHA"却含迁移注记 SHA〔`52a1ad7→c3387f0`/`afd889b`〕——规范 v3 字面违反〔第四型"终态 pin 陈旧"核心病灶已消除〕② **header line 3 未同步**：仍写 rev 93 而 §META rev=94——rev86 教训重演；rev95 均修正 + 规范 v3.1：status 零 SHA 绝对化 + header/§META rev 同 commit 同步）
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS；**O1 仍 OPEN**

### §A. 独立复跑（审验端一手 — 已执行 2026-09-02）

| # | 验收项 | 结果（实测） |
|---|---|---|
| A1 | pytest 654 任务书 §2 14 文件集 | **217 passed in 1.57s**（= 25 新 + 192 回归；≥200 达成 +8.5%，底限 ≥196 超 10.7%）✓ |
| A2 | 环境瞬态 | 首跑全绿；O-1 本刀未复发（复跑后 m2 报告零 diff）；O-2 维持关闭 ✓ |
| A3 | git 链 654 7 commits | `c3387f0`(delivery)→`4db7c2c`(cc_head rev94 + §META 五字段原子)→`d762ea5`(receipt 13 节)→`e6f3cae`(backfill last_receipt)→`24a33a8`(§NOW+status 原子)→`7bdeab8`(链补)→`71e6664`(链补终同步) 全在 ✓ |
| A4 | 双推复核 | HEAD = origin/main = github/main = `71e6664` 三向全等 ✓ |
| A5 | 规范 v3 落地 | §META 五字段原子更新 ✓（rev 93→94 / last_delivery→c3387f0 / last_receipt→d762ea5 / tasking 654 DONE / status 刷新）；amend-first 沿用 ✓；**status 行含迁移注记 SHA** → P4-1 |
| A6 | 树净 | 0 ✓ |
| A7 | O1 零动作 | 无 probe/registry/connector；docs/52 零改动 ✓ |

### §B. 交付物逐项核验（8 项）

| # | 项 | 结果 |
|---|---|---|
| B1 | M4.17 v11 西北双省 | **首试省双 BLOCKED_NO_POOL**：gansu `/zwgk/`+`/` 412×2 + qinghai `/zwgk/`+`/` 0×2（**Connection reset by peer——全链第二例首见失败形式**，入失败形式库）；HTTP **4/12**；substitute_used=0；blocked_no_pool_count=2；distinct_shas=[]；fetch_status=ALL_BLOCKED_NO_POOL ✓ |
| B2 | 三态处置 | 0 INSERT ROWS + 三重留痕（evidence blocked_reason 双省完整含援引链 + docs/78 §2 登记表 + receipt）；retry_of=N/A 首试省口径明文化（规范：有前史必填/首试省 N/A）✓ |
| B3 | blocked_reason 质量 | 双省各含：两级 fallback 实测码 + 红线 14 援引 + 池耗尽声明 + 首试省真网触发声明 + retry_of=N/A 依据——**留痕信息密度全链最高** ✓ |
| B4 | docs/78 §1-§6 | 300 行六节全；§2 首试省 BLOCKED 留痕登记表（4 实现位置 + 8+3 守门）；§4 失败形式库登记 + 累计 SHA 表；§5 首试省首触发经验模板化 ✓ |
| B5 | evidence ×2 | 主 JSON + 附属报告 ✓ |
| B6 | 654-B 测试 | **25 cases**（≥8 要求 3.1×；含 retry_of=N/A 口径守门 + 失败形式守门 + §META 五字段原子守门）✓ |
| B7 | rev94 | header = §META = 94 ✓；五字段原子 ✓；amend-first ✓ |
| B8 | 西北叙事收官 | XINJIANG(652)/NEIMENGGU(652)/GANSU(654)/QINGHAI(654) + SHAANXI(651) 西北五省区叙事表入 docs/78 ✓ |

### §C. 红线 14 条复核

14/14 全 ✓（重点：红线 3 HTTP 4/12 实测吻合；红线 7 PARTIAL 特例正确援引；红线 13 已用省 18 不变〔双 BLOCKED 增量 0〕；红线 14 首试省双触发 + retry_of=N/A 口径——653/654 连续两刀双触发，BLOCKED 留痕机制稳定性实证）。

### §D. 发现（审验端定案）

| 级 | # | 发现 | 处置 |
|---|---|---|---|
| P3 | — | 无 | — |
| P4 | 1 | **status 行 v3 字面违反**：自宣称"本行不含任何具体 SHA per 规范 v3 终极条款"，同括号内却含五字段迁移注记 SHA（`52a1ad7→c3387f0`、`afd889b→afd889b`）——自我指涉矛盾；但第四型"终态 pin 陈旧"核心病灶确已消除（无终态 HEAD pin），属条款执行洁癖级瑕疵 | **rev95 修正**（status 重写零 SHA）；**规范 v3.1**：status 行零 SHA 绝对化——迁移注记（旧值→新值）一律只入 §NOW 或 commit message，status 仅写状态语义 |
| P4 | 2 | **rev 登记同步不全**：(a) header line 3 仍写 "rev 93" 而 §META rev=94——任务书红线 12（header = §META 同步）违反，rev86 教训重演；(b) §CHAIN_TAIL 654 行仍 "OPEN" 未随 DELIVERED 更新——§META 五字段原子执行时漏 header 与 CHAIN_TAIL 两处 | **rev95 修正**（header → 95 + CHAIN_TAIL 654 → AUDITED）；规范 v3.1 追加：**七字段原子**——header / §META 五字段 / CHAIN_TAIL 当前行 同 commit 同步 |
| O-1 | — | 本刀未复发 | 维持关闭观察 |
| 亮点 | — | **连续两刀双 BLOCKED（653 复试省 + 654 首试省）= 留痕机制稳定性双样本实证**；qinghai Connection reset by peer 第二例首见失败形式（失败形式库 2 条：SSL handshake / Connection reset）；blocked_reason 信息密度全链最高；§META 五字段原子首次完整执行；25 守门 3.1× 超配 | — |

### §E. 审验端裁定区

- ☑ **PASS（有限通过）**【定案 2026-09-02】— 654 链路**实交付、可复跑、可追溯**：14 文件集 **217/217 独立复跑 green**；7 commits 双推三 ref 全等 `71e6664`；红线 14 全 ✓；首试省双 BLOCKED 留痕 + retry_of=N/A 口径规范化；**2×P4**（status 迁移注记 SHA + header rev 未同步）→ rev95 修正 + 规范 v3.1（六字段原子：header 入列）

**不宣称任何 PASS**（per 红线 1）。**O1 仍 OPEN**。

### §F. 655 签发依据（Cursor 审 PASS 后转架构师）

docs/78 §5.1 scope A（第 14 次扩展）— **西部省区全覆盖收官**：
- 剩余未用省（actual 口径 6 个）：HEBEI / SHANXI / GUANGXI / HAINAN / NINGXIA / XIZANG
- **655 = NINGXIA + XIZANG**（与 SHAANXI/GANSU/QINGHAI/XINJIANG/NEIMENGGU 构成**西部七省区全覆盖**叙事终章；两省无前史首试 → retry_of=N/A；三态合法沿用 654 模板）
- chain_id 末段 `_v12`；UUID n 段；递补池 [EXHAUSTED] 沿用
- 若双 REACHABLE → 已用省 18→20；若再双 BLOCKED → 留痕三连（机制稳定性三样本）

— End 654 audit 20260902 —

# ══════════ PART 2 / 655 任务书 ══════════

## 655-stage0-architect-m4-18-v12-west-finale-spike-tasking (2026-09-02)

> **角色**: 架构师 → 执行端（沿用 645-654 模式：架构师自签 + 自交付，per 2026-08-31 21:50 豁免）
> **前置**: 654 DELIVERED + 审计 **PASS（有限通过）**（本文件 PART 1; 1×P4）
> **scope**: scope A per docs/78 §5.1 = M4.18 v12（**NINGXIA + XIZANG**，第 23/24 样本，西部七省区全覆盖终章；两省无前史首试 retry_of=N/A；三态合法）+ O1 零动作
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS（**O1 仍 OPEN**）

### §0. 红线（14 条沿用，无新增）

1. 不宣布 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS
2. 不补零 / 不静默硬编码 value（domain 值 NULL 透明占位）
3. 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED；≤12 HTTP total（655 全刀预期 4-8）
4. 不改 docs/45/50/53/66-78 既有正文——修正项一律行内 append 尾注（例外: P4 typo 允许行内更正 + 尾注标记）
5. 不碰 4 fixture 锁值（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
6. 数据源唯一 = 政府/统计局/研究机构自取；用户零裁定
7. 完成 = observation SUCCESS，禁止 PARTIAL（特例: BLOCKED_NO_POOL 留痕合法，per 红线 14）
8. 不新写 016 migration（沿用 009+010+014+015 lineage JSONB）
9. chain_id = `'real_655_m4_18_policy_detail_v12'`（末段 `_v12`，≠ 654 `_v11` ≠ 653 `_v10`）
10. UUID **n 段**（n0eebc99 n1eebc99 ... n6eebc99，8 表前缀全 distinct）≠ 654 m 段及全前序
11. 不写 cegr.* 生产表（read-only；seed SQL 仅 staging 蓝本）
12. 既有 registry 行 SHA 零漂移；4 fixture 零触碰；m2 crosscheck 报告零 diff
13. 沿用: O1 零动作 + 附属产物指针 + 代换行标注规范（actual_province 口径）
14. **沿用（递补池耗尽条款）**: [EXHAUSTED]；两级 fallback 全失败 → BLOCKED_NO_POOL 留痕不代换（653/654 连续双触发模板；0 INSERT + 三重留痕 + blocked_reason 全援引）；NINGXIA/XIZANG 无前史首试 → retry_of=N/A；三态合法（INSERT 数按实报并说明）

### §1. 任务分解

**655-A.0 654 审计 P4×2 处置 + 规范 v3.1**
- **status 行零 SHA 绝对化**（v3.1）：迁移注记（旧值→新值）一律只入 §NOW 或 commit message；status 仅写状态语义（654 P4-1 字面违反杜绝）
- **七字段原子同步**（v3.1）：header line 3 rev / §META 五字段（rev/status/last_delivery/last_receipt/tasking）/ **§CHAIN_TAIL 当前行** 同 commit 同步更新——654 P4-2（header 漏同步 + CHAIN_TAIL 漏更新，rev86 教训重演）杜绝
- 沿用: amend-first 规则

**655-A.1 M4.18 v12 西部终章双省 spike（第 23/24 样本）**
- 2 样本（≤12 total）：
  - **NINGXIA**: 首选 `https://www.nx.gov.cn/zwgk/`; fallback `https://www.nx.gov.cn/`
  - **XIZANG**: 首选 `https://www.xizang.gov.cn/zwgk/`; fallback `https://www.xizang.gov.cn/`
- 产物: `scripts/fetch_m4_18_policy_detail_v12_2024.py` + `scripts/seed_m4_18_policy_detail_real_v12.sql`
- 三态: 双 REACHABLE → 16 INSERT + 2 NEW SHA；混合 → 按省实报；双 BLOCKED → 0 INSERT + 三重留痕（沿用 653/654 模板；blocked_reason 全援引链 + retry_of=N/A）
- lineage 全 `is_demo='false'`；chain_id/UUID 见红线 9/10

**655-A.2 O1 零动作（沿用）**

**655-A.3 docs/79 §1-§6**（§2 沿用首试省 BLOCKED 留痕登记表模板〔若触发〕；§4 **西部七省区全覆盖叙事终章表**〔SHAANXI/GANSU/QINGHAI/XINJIANG/NEIMENGGU/NINGXIA/XIZANG × 刀次 × 结果〕+ 累计 SHA 表 + 失败形式库滚动登记）

**655-A.4 evidence ×2**: `docs/reports/m4_18_policy_detail_real_v12_20260902.md` + `evidence_pack/m4_18_policy_detail_real_v12_20260902.json`

**655-B 测试**: `tests/test_m4_18_policy_detail_real_v12.py` ≥8（守门: SHA/UUID n 段/chain_id `_v12`/INSERT 三态口径/is_demo/retry_of=N/A 首试口径/docs/79 六节/BLOCKED 分支+字段/P4-A.0 规范 v3.1 落点〔status 零 SHA〕）；回归 654 侧 14 文件集 217 + ≥8 新 = **≥225 green（底限 ≥221）**

**655-C 回执 + commit + 双推**: 回执 `655-stage0-cc-m4-18-v12-west-finale-receipt-20260902.md`；EXEC-QUEUE rev95（654 审计，本次）→ **rev96**（655 交付；五字段原子 + status 零 SHA per 规范 v3.1）

### §2. 验收命令（审验端一键）

```bash
cd "/Users/kjonekong/projects/china platform"
python3 -m pytest tests/test_m4_18_policy_detail_real_v12.py tests/test_m4_17_policy_detail_real_v11.py tests/test_m4_16_policy_detail_real_v10.py tests/test_m4_15_policy_detail_real_v9.py tests/test_m4_14_policy_detail_real_v8.py tests/test_m4_13_policy_detail_real_v7.py tests/test_m4_12_policy_detail_real_v6.py tests/test_m4_11_policy_detail_real_v5.py tests/test_m4_10_reverify_jx.py tests/test_m2_report_hygiene.py tests/test_m4_10_policy_detail_real_v4.py tests/test_m4_9_policy_detail_real_v3.py tests/test_o1_live_candidate_probe.py tests/test_m6_spike_docs_closure.py tests/test_m4_8_policy_detail_real_v2.py -q
# 期望 ≥225 passed (底限 ≥221)
git log --oneline -9 && git status -s
git diff docs/reports/m2_2024_gdp_crosscheck_20260831.md | head -5   # 期望空
grep -c "ningxia\|xizang" scripts/seed_m4_18_policy_detail_real_v12.sql  # 期望 ≥2
```

— End 655 tasking 20260902 —

— End consolidated 654 audit + 655 tasking 20260902 —

