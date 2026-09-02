# 653 审验裁定 + 654 任务书 — 合并归档 (2026-09-02)

> 单文件模式（per 用户指示 2026-09-01 起，对话不再展示全文）。
> Part 1 = 653 审验裁定（Cursor 审验端）；Part 2 = 654 任务书（架构师签发）。EXEC-QUEUE 指针以本件为准。

---

# ══════════ PART 1 / 653 审验裁定 ══════════

## 653-stage0-cursor-s653-m4-16-v10-retry-audit — 审验裁定（2026-09-02 定案）

> **角色**: Cursor（审验端）
> **对象**: 653 完整链路（M4.16 v10 shandong+hubei 双复试 + 真网首次双 BLOCKED_NO_POOL 触发 + P4-A.0 规范 v2）
> **入口**: 回执 `653-stage0-cc-m4-16-v10-retry-receipt-20260902.md` · 任务书 `652-audit-653-tasking-consolidated-20260902.md` PART 2 · 主 evidence `evidence_pack/m4_16_policy_detail_real_v10_20260902.json` · `docs/77-m4-16-policy-detail-real-v10-20260902.md`
> **裁定（定案）**: **PASS（有限通过）** — 0×P3 + **2×P4**（① §META `last_delivery`/`last_receipt`/tasking 状态行未随 rev92 回填至 653〔仍为 652 值 04721b7/d98cba0/OPEN〕② status 行 pin `52a1ad7`〔delivery〕为"终态 HEAD"且标注 "per git log -1" 与实际终态 `17c08aa` 不符——**第四型 SHA pin 陈旧复发**；规范 v2 亮点并存："待复核"字样已清除 ✓ + post/pre-amend SHA 透明 ✓ → rev93 修正 + 654-A.0 规范 v3：**status 禁含 SHA**）
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS；**O1 仍 OPEN**

### §A. 独立复跑（审验端一手 — 已执行 2026-09-02）

| # | 验收项 | 结果（实测） |
|---|---|---|
| A1 | pytest 653 任务书 §2 13 文件集 | **192 passed in 2.25s**（= 21 新 + 171 回归；≥179 达成 +7%，底限 ≥175 超 10%）✓ |
| A2 | 环境瞬态 | 首跑全绿；**O-1 第三次复发**（复跑后 m2 报告 churn → checkout 即还原树净，非交付缺陷，模式已固化）；O-2 维持关闭 ✓ |
| A3 | git 链 653 8 commits | `af7a95c`(A.0 v2)→`52a1ad7`(delivery)→`14eb055`(cc_head rev92)→`afd889b`(receipt)→`f74af31`(backfill)→`c5cdcaf`(§NOW+status 原子, post-amend of 217ad25)→`b287afe`(链补)→`17c08aa`(链补终同步) 全在 ✓ |
| A4 | 双推复核 | HEAD = origin/main = github/main = `17c08aa` 三向全等 ✓（执行端信号一致）|
| A5 | backfill | rev91→rev92 + afd889b 入链 ✓；post/pre-amend SHA 双记（217ad25→c5cdcaf）透明 ✓；**但 §META last_delivery/last_receipt/tasking 行未回填** → P4-1 |
| A6 | 树净 | 0（m2 churn 已还原）✓ |
| A7 | retry_of | seed 3 处 + fetch RETRY_OF_NOTES + evidence retry_of_annotation 双样本 ✓（任务书 "≥2" 达成）|

### §B. 交付物逐项核验（8 项）

| # | 项 | 结果 |
|---|---|---|
| B1 | A.0 规范 v2 | status 收口与 §NOW 同 commit（c5cdcaf）原子完成 ✓；"待复核/待 §C-x"清除 ✓；amend-first 双 SHA 透明 ✓；**status 含 SHA 引用且与终态不符** → P4-2 |
| B2 | M4.16 v10 双复试 | **真网首次双 BLOCKED_NO_POOL**：shandong `/zwgk/`+`/` 均 SSL handshake failure 0/0（**新失败形式**，全链首见）+ hubei `/zwgk/`+`/` 412×2（同 649 史）；HTTP **4/12**（33%）；substitute_used=0；blocked_no_pool_count=**2**；distinct_shas=[]；fetch_status=ALL_BLOCKED_NO_POOL ✓ |
| B3 | 三态处置 | 双 BLOCKED → **0 INSERT ROWS**（任务书"INSERT 数按实报并说明"口径；三态合法性论证入回执 §两态表）；seed 头部 documentation 完整（实测/史/红线 14/13 沿用/chain_id/UUID 全注）；lineage 信息三重留痕（evidence + docs/77 + receipt）✓ |
| B4 | O1 零动作 | 无 probe/registry/connector；docs/52 零改动 ✓ |
| B5 | docs/77 §1-§6 | 294 行六节全；§2 复试 BLOCKED 留痕登记表（4 实现位置 + **8 守门**含 retry_of）；§4 累计 [BLOCKED_NO_POOL] 触发事件计数（638-653）；§5.2 双触发经验模板化 ✓ |
| B6 | evidence ×2 | 主 JSON（ALL_BLOCKED_NO_POOL + cells 双 blocked_reason + retry_of_annotation + methodology 全援引）+ 附属报告 ✓ |
| B7 | 653-B 测试 | **21 cases**（≥8 要求 2.6×；守门：INSERT 两态口径/0 ROWS 合法/retry_of/BLOCKED 分支+字段/docs/77 六节+登记表/P4-A.0 v2 落点/红线 14 ×3/不宣称 PASS）✓ |
| B8 | rev92 | header = §META = 92 ✓；**§META 三行未回填** → P4-1 |

### §C. 红线 14 条复核

14/14 全 ✓（重点：红线 3 HTTP 4/12 与 fetch_log 吻合〔每省 2 请求〕；红线 7 PARTIAL 特例正确援引——BLOCKED_NO_POOL 留痕 = 合法"未完成"；红线 13 已用省 18 不变〔双 BLOCKED 增量 0 省, actual_province=NULL〕；红线 14 **真网双触发 = e2e 完全体达成**——4 实现位置 + 8 守门经受实战检验）。

### §D. 发现（审验端定案）

| 级 | # | 发现 | 处置 |
|---|---|---|---|
| P3 | — | 无 | — |
| P4 | 1 | **§META 回填不全**：rev92 后 `last_delivery` 仍 652 值 `04721b7`、`last_receipt` 仍 `d98cba0`、tasking 行仍 "653 OPEN"——f74af31 commit message 称 "backfill…afd889b (receipt) 入链" 但仅入 cc_head 链，未更新 §META 字段 | **rev93 修正**（本审计）；654-A.0 规范 v3：§META 五字段（rev/status/last_delivery/last_receipt/tasking 状态）与 cc_head 同 commit 原子更新 |
| P4 | 2 | **status 行第四型 SHA pin 陈旧**：写"三 ref 全等终态 HEAD=`52a1ad7` (per git log -1)"——52a1ad7 为 delivery commit，其后又有 6 commits（终态 `17c08aa`）；"per git log -1" 标注在任何时点均不成立；规范 v2 的"待复核清除+amend 透明"两点达成但 SHA 引用规则再度失守（第三次同类） | **rev93 修正 + 规范 v3 终极条款：status 行禁含任何具体 SHA**（只写"三 ref 全等〔git log -1 实测〕"） |
| O-1 | — | m2 复跑污染第三次复发（checkout 即还原，模式固化） | 维持观察；tmpdir 加固建议持续开放 |
| 亮点 | — | **真网首次双 BLOCKED_NO_POOL 触发 = 红线 14 e2e 完全体**（651 建池→652 验证机制→653 实战双触发，三刀闭环）；shandong SSL handshake failure 为全链首见失败形式（入失败形式库）；三态处置（0 INSERT + 三重留痕）示范级；retry_of lineage 全行落地；21 守门测试 | — |

### §E. 审验端裁定区

- ☑ **PASS（有限通过）**【定案 2026-09-02】— 653 链路**实交付、可复跑、可追溯**：13 文件集 **192/192 独立复跑 green**；8 commits 双推三 ref 全等 `17c08aa`；红线 14 全 ✓ 且 **BLOCKED_NO_POOL 真网双触发 e2e 完全体**；**2×P4**（§META 回填不全 + status SHA pin 陈旧）→ rev93 修正 + 654-A.0 规范 v3

**不宣称任何 PASS**（per 红线 1）。**O1 仍 OPEN**。

### §F. 654 签发依据（Cursor 审 PASS 后转架构师）

docs/77 §5.1 scope A（第 13 次扩展）— **西北四连收官**：
- BLOCKED e2e 已完全体（653 双触发），spike 链剩余价值 = 省覆盖扩展 + 失败形式库累积
- 剩余未用省（actual 口径 8 个）：HEBEI / SHANXI / GUANGXI / HAINAN / GANSU / QINGHAI / NINGXIA / XIZANG
- **654 = GANSU + QINGHAI**（与 652 XINJIANG/NEIMENGGU 构成西北五省区叙事收官；两省均无前史 → retry_of 不适用〔新省首试〕，若 BLOCKED → 纯 BLOCKED_NO_POOL 留痕）
- chain_id 末段 `_v11`；UUID m 段；递补池 [EXHAUSTED] 沿用

— End 653 audit 20260902 —

# ══════════ PART 2 / 654 任务书 ══════════

## 654-stage0-architect-m4-17-v11-northwest-spike-tasking (2026-09-02)

> **角色**: 架构师 → 执行端（沿用 645-653 模式：架构师自签 + 自交付，per 2026-08-31 21:50 豁免）
> **前置**: 653 DELIVERED + 审计 **PASS（有限通过）**（本文件 PART 1; 2×P4）
> **scope**: scope A per docs/77 §5.1 = M4.17 v11（**GANSU + QINGHAI**，第 21/22 样本，西北四连收官；两省无前史首试——若 BLOCKED 即纯 BLOCKED_NO_POOL 留痕〔retry_of 不适用〕；三态合法）+ O1 零动作
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4 / M4.x / M5 / M5.x / M6 PASS（**O1 仍 OPEN**）

### §0. 红线（14 条沿用，无新增）

1. 不宣布 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS
2. 不补零 / 不静默硬编码 value（domain 值 NULL 透明占位）
3. 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED；≤12 HTTP total（654 全刀预期 4-8）
4. 不改 docs/45/50/53/66-77 既有正文——修正项一律行内 append 尾注（例外: P4 typo 允许行内更正 + 尾注标记）
5. 不碰 4 fixture 锁值（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
6. 数据源唯一 = 政府/统计局/研究机构自取；用户零裁定
7. 完成 = observation SUCCESS，禁止 PARTIAL（特例: BLOCKED_NO_POOL 留痕合法，per 红线 14）
8. 不新写 016 migration（沿用 009+010+014+015 lineage JSONB）
9. chain_id = `'real_654_m4_17_policy_detail_v11'`（末段 `_v11`，≠ 653 `_v10` ≠ 652 `_v9`）
10. UUID **m 段**（m0eebc99 m1eebc99 ... m6eebc99，8 表前缀全 distinct）≠ 653 l 段及全前序
11. 不写 cegr.* 生产表（read-only；seed SQL 仅 staging 蓝本）
12. 既有 registry 行 SHA 零漂移；4 fixture 零触碰；m2 crosscheck 报告零 diff
13. 沿用: O1 零动作 + 附属产物指针 + 代换行标注规范（actual_province 口径）
14. **沿用（递补池耗尽条款）**: [EXHAUSTED]；两级 fallback 全失败 → BLOCKED_NO_POOL 留痕不代换（653 双触发模板沿用：0 INSERT + 三重留痕〔evidence/docs/receipt〕）；GANSU/QINGHAI 无前史 → retry_of 不适用（首试省）；三态合法（INSERT 数按实报并说明）

### §1. 任务分解

**654-A.0 653 审计 P4×2 处置 + 规范 v3**
- **§META 五字段原子更新**：rev / status / last_delivery / last_receipt / tasking 状态行与 cc_head 链**同 commit**更新（杜绝 653 P4-1 回填遗漏）
- **status 行禁含任何具体 SHA**（只写"三 ref 全等〔git log -1 实测〕"）——杜绝第四型 pin 陈旧（653 P4-2）
- 沿用 amend-first 规则（post/pre-amend SHA 双记透明）

**654-A.1 M4.17 v11 西北双省 spike（第 21/22 样本）**
- 2 样本（≤12 total）：
  - **GANSU**: 首选 `https://www.gansu.gov.cn/zwgk/`; fallback `https://www.gansu.gov.cn/`
  - **QINGHAI**: 首选 `https://www.qinghai.gov.cn/zwgk/`; fallback `https://www.qinghai.gov.cn/`
- 产物: `scripts/fetch_m4_17_policy_detail_v11_2024.py` + `scripts/seed_m4_17_policy_detail_real_v11.sql`
- 三态: 双 REACHABLE → 16 INSERT + 2 NEW SHA；混合 → 按省实报；双 BLOCKED → 0 INSERT + 三重留痕（沿用 653 模板）
- lineage 全 `is_demo='false'`；chain_id/UUID 见红线 9/10

**654-A.2 O1 零动作（沿用）**

**654-A.3 docs/78 §1-§6**（§2 沿用 BLOCKED 留痕登记表模板〔若触发〕+ 西北五省区叙事收官表〔XINJIANG/NEIMENGGU/GANSU/QINGHAI + SHAANXI 邻接〕；§4 累计 SHA 表 + 失败形式库登记〔含 653 SSL handshake failure〕）

**654-A.4 evidence ×2**: `docs/reports/m4_17_policy_detail_real_v11_20260902.md` + `evidence_pack/m4_17_policy_detail_real_v11_20260902.json`

**654-B 测试**: `tests/test_m4_17_policy_detail_real_v11.py` ≥8（守门: SHA/UUID m 段/chain_id `_v11`/INSERT 三态口径/is_demo/docs/78 六节/BLOCKED 分支+字段/P4-A.0 规范 v3 落点〔§META 五字段原子 + status 无 SHA〕）；回归 653 侧 13 文件集 192 + ≥8 新 = **≥200 green（底限 ≥196）**

**654-C 回执 + commit + 双推**: 回执 `654-stage0-cc-m4-17-v11-northwest-receipt-20260902.md`；EXEC-QUEUE rev93（653 审计，本次）→ **rev94**（654 交付；三齐 + header 同步 + **A.0 规范 v3 原子收口**）

### §2. 验收命令（审验端一键）

```bash
cd "/Users/kjonekong/projects/china platform"
python3 -m pytest tests/test_m4_17_policy_detail_real_v11.py tests/test_m4_16_policy_detail_real_v10.py tests/test_m4_15_policy_detail_real_v9.py tests/test_m4_14_policy_detail_real_v8.py tests/test_m4_13_policy_detail_real_v7.py tests/test_m4_12_policy_detail_real_v6.py tests/test_m4_11_policy_detail_real_v5.py tests/test_m4_10_reverify_jx.py tests/test_m2_report_hygiene.py tests/test_m4_10_policy_detail_real_v4.py tests/test_m4_9_policy_detail_real_v3.py tests/test_o1_live_candidate_probe.py tests/test_m6_spike_docs_closure.py tests/test_m4_8_policy_detail_real_v2.py -q
# 期望 ≥200 passed (底限 ≥196)
git log --oneline -9 && git status -s
git diff docs/reports/m2_2024_gdp_crosscheck_20260831.md | head -5   # 期望空
grep -c "gansu\\|qinghai" scripts/seed_m4_17_policy_detail_real_v11.sql  # 期望 ≥2
```

— End 654 tasking 20260902 —

— End consolidated 653 audit + 654 tasking 20260902 —

