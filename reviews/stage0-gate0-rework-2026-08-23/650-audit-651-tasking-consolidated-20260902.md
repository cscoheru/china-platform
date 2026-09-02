# 650 审验裁定 + 651 任务书 — 合并归档 (2026-09-02)

> 单文件模式（per 用户指示 2026-09-01 起，对话不再展示全文）。
> Part 1 = 650 审验裁定；Part 2 = 651 任务书。EXEC-QUEUE 指针以本件为准。

---

# ══════════ PART 1 / 650 审验裁定 ══════════

## 650-stage0-cursor-s650-m4-13-v7-audit — 审验报告 PASS（有限通过）(2026-09-02)

> **角色**: Cursor（审验端） · **对象**: 650 完整链路（M4.13 v7 + 649 P3-1 蓝图更正 + 规范固化）
> **入口**: 回执 `650-stage0-cc-m4-13-v7-substitute-labeling-receipt-20260901.md` + 任务书（合并视图 `649-audit-650-tasking-consolidated-20260901.md`）
> **裁定**: **PASS（有限通过）** — 0×P3 + 2×P4（docs/74 措辞两处），转 651 处置
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS；**O1 仍 OPEN**

### §A. 独立复跑（审验端一手）

| # | 验收项 | 结果 |
|---|---|---|
| A1 | pytest 10 文件（650 新 20 + 649 侧 98） | **118/118 green**（3.08s；≥106 达成）。注: 首跑 1 failed（`test_m2_report_hygiene::test_crosscheck_script_idempotent_under_tmp`）→ 隔离重跑 **passed** → 全套复跑 **118 passed**、树净——定位为审计端被 TUI 阻塞期间排队的幽灵 pytest 进程并发竞态 /tmp 所致瞬态，**非交付缺陷**（观察 O-1） |
| A2 | git 链 650: `fce3153`(delivery) → `188b4ed`(rev86) → `a762bae`(receipt) → `f6cb180`(backfill) | 4 commits ✓ |
| A3 | 双推: HEAD = origin/main = github/main = `f6cb180` | ✓ |
| A4 | backfill 三齐 | cc_head 入链（fce3153/188b4ed/a762bae）✓ + last_receipt SHA `a762bae` ✓ + §NOW 刷新 ✓（f6cb180 自身按惯例由 rev87 入链=本次完成）|
| A5 | 树净（复跑后） | 0 ✓ |

### §B. 交付物逐项核验（8 files / +1677 −10；删除全部为 seed_m4_12 行内更正换行）

| # | 项 | 核验 | 结果 |
|---|---|---|---|
| B1 | A.0 P3-1 蓝图更正 | h02 `province='LIAONING'` + source_name 辽宁口径；8 处更正（h02 province/name + h04/h11/h41/h51/h61 描述 + h41/h61 geo FK lookup）；尾注块 365-380；**VALUES 级 'HUBEI' 残留 = 0**（grep 2 命中均在注释尾注块=更正登记本身，合规） | ✓ |
| B2 | A.0 docs/73 §6.1 | "### 6.1 649 审计裁定登记" +10 行 **0 删**（五要素齐） | ✓ |
| B3 | A.1 M4.13 v7 | 16 INSERT（12 政策 + 2 registry + 2 document，10 语句）；chain_id `real_650_m4_13_policy_detail_v7`；UUID **i 段**（8 表前缀 i0-i6eebc99 全 distinct）；guizhou `/zwgk/` 200 直接 REACHABLE（170166B，SHA `5c5b1295`）；jiangsu `/zwgk/` 404→`/` 200（82985B，SHA `def18a2f`）；2 NEW SHA distinct ≠ 638-649；substitute_used_count=0；HTTP **3/12**（25%，全链最低）；is_demo 全 `'false'`；lineage original/actual 双记 | ✓ |
| B4 | A.2 O1 零动作 | delivery 8 文件清单核验：无 probe/registry/connector/docs/52 触碰 | ✓ |
| B5 | A.3 docs/74 §1-§6 | 266 行全（§2 代换登记专节 + §4.4 池状态表 + §5.1 scope 候选） | ✓ |
| B6 | A.4 evidence ×2 | json 129 行（uuid_prefixes 8 表 + http_count=3 + distinct_shas + cells 逐 attempt）+ docs/reports 185 行（更正前后对照） | ✓ |
| B7 | B 测试 | **20 cases**（≥8 要求 2.5×；含 **3 个 P3-1 更正守门**） | ✓ 亮点 |
| B8 | C rev86 | header = §META = 86 ✓（649 P4-1 教训修复生效）；status/§NOW 现行无自指陈旧 ✓ | ✓ |

### §C. 红线 13 条复核

1-13 全部遵守（HTTP 3/12 ✓ / docs/72 零触碰 ✓ / docs/73 仅 append ✓ / 4 fixture 零触碰 ✓ / chain_id `_v7` ✓ / i≠h≠g≠f≠e≠d≠c ✓ / m2 报告零 diff ✓ / O1 零动作 ✓ / 递补池按序未触发 ✓ / 代换行标注规范——本刀无代换、原生样本 actual=original ✓ / 附属产物指针 ✓）。

### §D. 发现（全部非阻塞）

| 级 | # | 发现 | 处置 |
|---|---|---|---|
| P4 | 1 | docs/74 §2.1 "递补池按序 **sha anxi** → sichuan"（省名空格 typo） | 651-A.0 行内更正 + 尾注 |
| P4 | 2 | docs/74 §4.4 "649 增量: HUBEI/JILIN/LIAONING" 与上行 "已用省全集（按 actual_province 口径，无 HUBEI）" 并置——槽名混入 actual 口径增量列表，措辞歧义 | 651-A.0 尾注澄清（hubei 槽 consumed；actual=LIAONING） |
| 观察 | O-1 | m2 idempotent 测试对并发 /tmp 竞态敏感（审计端幽灵进程致首跑 1 fail；隔离+全套复跑双绿，非交付缺陷） | 651 可选加固（tmpdir isolation），不 gating |
| 亮点 | — | HTTP 3/12=25% 全链最低；20 新测试超要求 2.5×；P3-1 八处更正 + 3 例守门测试把规范固化为可执行断言 | — |

### §E. 结论

650 链路**实交付、可复跑、可追溯**：118/118 独立复跑 green；4 commits 双推；P3-1 蓝图更正八处全落且 VALUES 级零残留；红线 13 代换行标注规范首次落地即合规；HTTP 预算全链最优。裁定 **PASS（有限通过）**，2×P4 转 651。**不宣称任何 PASS；O1 仍 OPEN。**

### §F. 651 签发依据

docs/74 §5.1 scope A（第 10 次扩展）：651 = M4.14 v8 **shaanxi + sichuan**（递补池仅剩二省转正为首选；本刀后**递补池耗尽**，固化耗尽条款）+ P4×2 更正。已用省全集（actual 口径）：HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX/HUN/AH/LN/JL/GUIZHOU/JIANGSU；651 增量 SHAANXI/SICHUAN 后 = 16 省。

— End 650 audit 20260902 —

---

# ══════════ PART 2 / 651 任务书 ══════════

## 651-stage0-architect-m4-14-v8-pool-depletion-tasking (2026-09-02)

> **角色**: 架构师 → 执行端（沿用 645-650 模式：架构师自签 + 自交付，per 2026-08-31 21:50 豁免）
> **前置**: 650 DELIVERED + 审计 **PASS（有限通过）**（本文件 PART 1）
> **scope**: scope A per docs/74 §5.1 = M4.14 v8（shaanxi + sichuan 第 15/16 样本）+ 递补池耗尽条款固化 + 650 审计 P4×2 更正；**O1 零动作**
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS（**O1 仍 OPEN**）

### §0. 红线（14 条 = 13 沿用 + 1 增补；docs/74 入保护清单）

1. 不宣布 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS
2. 不补零 / 不静默硬编码 value（domain 值 NULL 透明占位，沿用 641-650）
3. 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED；≤12 HTTP total（651 全刀预期 2-10）
4. 不改 docs/45/50/53/66/67/68/69/70/71/72/73/**74** 既有正文——修正项一律行内 append 尾注（**例外**: P4 typo "sha anxi" 允许行内更正 + 尾注标记，per 蓝图更正先例）
5. 不碰 4 fixture 锁值（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
6. 数据源唯一 = 政府/统计局/研究机构自取；用户零裁定；执行端不可提任何用户裁定事项
7. 完成 = observation SUCCESS，禁止 PARTIAL
8. 不新写 016 migration（沿用 009+010+014+015 lineage JSONB）
9. chain_id = `'real_651_m4_14_policy_detail_v8'`（末段 `_v8`，≠ 650 `_v7` ≠ 649 `_v6`）
10. UUID **j 段**（j0/j1-j6`eebc99`，8 表前缀全 distinct）≠ 650 i 段 / 649 h 段 / 648 g 段 / 647 f 段 / 646 e 段 / 645 d 段 / 644 c 段
11. 不写 cegr.* 生产表（read-only；seed SQL 仅 staging 蓝本）
12. 既有 registry 行 SHA 零漂移；4 fixture 字节零触碰；m2 crosscheck 报告零 diff
13. 沿用: O1 零动作 + 附属产物指针 + 代换行标注规范（registry province/name = actual_province）
14. **增补（递补池耗尽条款）**: 651 后递补池（shaanxi/sichuan 转正消耗）**正式耗尽**；此后任何样本槽两级 fallback 均失败 → **BLOCKED 留痕，不再跨省代换**（evidence 记 blocked_reason + docs 登记；无池可递补）

### §1. 任务分解

**651-A.0 650 审计 P4×2 更正**
- docs/74 §2.1（及 §4.4 同类处）"sha anxi" → "shaanxi" 行内更正 + 尾注 `per 650 审计 P4-1`
- docs/74 §4.4 "649 增量" 行 append 尾注：`hubei 为槽名（consumed），actual_province=liaoning per 红线 13；per 650 审计 P4-2`

**651-A.1 M4.14 v8 真实化 spike（第 15/16 样本；递补池收官）**
- 2 新样本（≤12 total）:
  - shaanxi 首选 `https://www.shaanxi.gov.cn/zwgk/`；fallback #1 `https://www.shaanxi.gov.cn/`
  - sichuan 首选 `https://www.sc.gov.cn/zwgk/`；fallback #1 `https://www.sc.gov.cn/`
  - 两级均 BLOCKED → **无池可递补 → BLOCKED 留痕**（红线 14 首次执行；不代换）
- 产物: `scripts/fetch_m4_14_policy_detail_v8_2024.py` + `scripts/seed_m4_14_policy_detail_real_v8.sql`（2 样本 × 8 表 = 16 INSERT；语句数自报）
- lineage 全 `is_demo='false'`；chain_id 见红线 9；UUID j 段；2 真实 SHA distinct（≠ 638-650 全部）

**651-A.2 O1 零动作（沿用）**

**651-A.3 docs/75 §1-§6**（§2 含**递补池生命周期收官登记**：激活 1 次〔649 liaoning〕/ 备而未触发〔650/651〕/ 651 后耗尽 + 红线 14 生效）

**651-A.4 evidence ×2**: `docs/reports/m4_14_policy_detail_real_v8_20260902.md` + `evidence_pack/m4_14_policy_detail_real_v8_20260902.json`（沿用 650 cell 结构）

**651-B 测试**: `tests/test_m4_14_policy_detail_real_v8.py` ≥8（守门: 2 SHA distinct ≠ 638-650 / j 段 ≠ i·h·g·f·e·d·c / chain_id `_v8` / 16 INSERT / is_demo='false' / docs/75 六节 / A.0 更正守门〔docs/74 无 "sha anxi" 残留 + P4-2 尾注在〕/ **递补池耗尽守门**〔fetch 脚本含 BLOCKED 不代换分支〕）；回归 650 侧 118 = **≥126 green**

**651-C 回执 + commit + 双推**: 回执 `651-stage0-cc-m4-14-v8-pool-depletion-receipt-20260902.md`；EXEC-QUEUE rev87 → rev88（三齐 + header 同步沿用）

### §2. 验收命令（审验端一键）

```bash
cd "/Users/kjonekong/projects/china platform"
python3 -m pytest tests/test_m4_14_policy_detail_real_v8.py tests/test_m4_13_policy_detail_real_v7.py tests/test_m4_12_policy_detail_real_v6.py tests/test_m4_11_policy_detail_real_v5.py tests/test_m4_10_reverify_jx.py tests/test_m2_report_hygiene.py tests/test_m4_10_policy_detail_real_v4.py tests/test_m4_9_policy_detail_real_v3.py tests/test_o1_live_candidate_probe.py tests/test_m6_spike_docs_closure.py tests/test_m4_8_policy_detail_real_v2.py -q
# 期望 ≥126 passed
git log --oneline -5 && git status -s
grep -c "sha anxi" docs/74-m4-13-policy-detail-real-v7-20260901.md   # 期望 0
```

— End 651 tasking 20260902 —

— End consolidated 650 audit + 651 tasking 20260902 —
