# 649 审验裁定 + 650 任务书 — 合并归档 (2026-09-01)

> 本文件 = 单文件合并版（per 用户指示 2026-09-01：审验裁定与任务书写入一个文件，对话中不再展示；下同）。
> Part 1 = 649 审验裁定 PASS（有限通过）；Part 2 = 650 任务书。
> 规范文件仍为原文两件（EXEC-QUEUE last_audit/tasking 字段指向原文）；本件为合并视图与后续单文件模式起点。

---

# ══════════ PART 1 / 649 审验裁定 ══════════

# 649-stage0-cursor-s649-m4-12-v6-audit — 审验报告 PASS（有限通过）(knife 649 audit, 2026-09-01)

> **角色**: Cursor（审验端） · **对象**: 649 完整链路（M4.12 v6 + 递补池首次激活 + docs/72 §7 登记）
> **入口**: 回执 `649-stage0-cc-m4-12-v6-pool-activation-receipt-20260901.md` + 任务书 `649-stage0-architect-m4-12-v6-pool-activation-tasking-20260901.md`
> **裁定**: **PASS（有限通过）** — 1×P3（代换样本 registry 行 province/name 与 actual_province 错位）+ 3×P4（EXEC-QUEUE 陈旧三处），转 650 处置
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS；**O1 仍 OPEN**

---

## §A. 独立复跑（审验端一手）

| # | 验收项（任务书 §2） | 结果 |
|---|---|---|
| A1 | `pytest` 9 文件（M4.12 17 + 648 侧 81） | **98 passed in 1.51s** ✓（≥89 达成；与回执 98/98 一致） |
| A2 | git 链 649：`936640d` → `cd15adc`(rev83) → `0e91921`(receipt) → `6ddd5a2`(backfill) | 4 commits ✓，树净 ✓ |
| A3 | 双推：HEAD = origin/main = github/main = `6ddd5a2` | ✓ |
| A4 | backfill 三齐（per 648 审计 P3-2） | cc_head 入链（936640d/cd15adc/0e91921）✓ + last_receipt SHA `0e91921` ✓ + §NOW 刷新 ✓（陈旧残留见 P4） |
| A5 | `git status -s` | 0（含 m2 报告干净）✓ |

## §B. 交付物逐项核验（任务书 §1 对照）

| # | 项 | 核验 | 结果 |
|---|---|---|---|
| B1 | A.0 docs/72 §7 | +46 行 **0 删**（append-only）："648 审计 PASS（有限通过）尾注 + 修正项登记" | ✓ |
| B2 | A.1 fetch hubei | `/zwgk/` 412 + 省府根 412（各 ~3KB WAF 页、0 锚点——正确拒收）→ 两级 BLOCKED 留痕 | ✓ |
| B3 | A.1 递补池激活 | hubei 槽 → **liaoning**（`/zwgk/` 404〔393B，正确拒收〕→ 省府根 200，SHA `b22d1fb4` 148399B）——**递补池首次激活，序位合规**（liaoning = 递补池 #1） | ✓（标注错位见 P3-1） |
| B4 | A.1 fetch jilin | `/zwgk/` curl 0 → 省府根 200；SHA `a1e49a91` 69943B | ✓ |
| B5 | evidence 质量 | cell 含 `actual_province`/`fetched_url`/`fallback_chain_used` 四级链/逐 attempt 锚点与 WAF 标记——**代换留痕结构史上最全**（超 647） | ✓ 亮点 |
| B6 | HTTP 预算 | **6/12**（hubei 2 + ln 2 + jl 2）✓；substitute_used_count=1 | ✓ |
| B7 | seed SQL | 10 语句 / 16 行；chain_id `real_649_m4_12_policy_detail_v6`；**h 段** 分布 h0×12/h1×6/h2×4/h3×2/h4×4/h5×2/h6×2，g·f·e·d·c 段 **0 命中**；lineage 含 original/actual_province + substitute_used + is_demo='false' | ✓（B3 标注见 P3-1） |
| B8 | A.2 O1 零动作 | 交付 7 文件无 probe/registry/connector/O1 evidence 触碰 | ✓ |
| B9 | A.3 docs/73 | §1-§6 全（§2 = substitute 跨省代换登记专节） | ✓ |
| B10 | A.4 evidence ×2 | m4_12 report（170 行）+ json（193 行，含 distinct_shas 数组） | ✓ |
| B11 | B 测试 | **17 新**（≥8）+ 81 回归 = 98 green | ✓ |
| B12 | C | rev84 backfill 三齐实质完成；陈旧残留三处（P4）；§ACK 条目在 | ⚠（P4） |

## §C. 红线 13 条复核

1-12 全部遵守（≤12 HTTP=6 ✓ / docs/72 仅 append 46 行 0 删 ✓ / 4 fixture 零触碰 ✓ / chain_id `_v6` ✓ / h≠g≠f≠e≠d≠c ✓ / m2 报告零 diff ✓）；13（O1 零动作 + 递补池按序 liaoning ✓ + 指针条款无适用附属产物 ✓）。

## §D. 发现（全部非阻塞）

| 级 | # | 发现 | 处置 |
|---|---|---|---|
| **P3** | 1 | **代换样本 registry 行标注错位**：`seed_m4_12` h02 行 `province='HUBEI'` + `source_name="湖北省人民政府…"`，但 `source_url=https://www.ln.gov.cn/`（内容 = 辽宁省府根）——与 647 先例相悖（jiangxi 代换行标 JIANGXI）；语义上 ln.gov.cn 源标 HUBEI 会污染省级分组口径。lineage JSONB 内 `actual_province='liaoning'` 属实（蓝图级瑕疵，未写生产） | 650-A.0 蓝图行内更正（province→LIAONING + name→辽宁省人民政府〔hubei 槽递补〕+ 尾注标记）+ 规范固化入红线 13：**代换行 registry 标注一律用 actual_province** |
| P4 | 1 | rev84 顶部 header 仍写 **"rev 82"**（§META `rev: 84` 正确） | rev85 审验端顺手修 |
| P4 | 2 | status 行仍写 "待 649-C receipt + receipt-backfill 完成"（实际已完成） | 同上 |
| P4 | 3 | §NOW 措辞 "HEAD = 0e91921 parent + receipt-backfill pending" 自指陈旧 | 同上 |

## §E. 结论

649 链路**实交付、可复跑、可追溯**：98/98 独立 green；4 commits 双推；16 INSERT/10 语句；h 段 + `_v6` + 2 NEW SHA（`a1e49a91`/`b22d1fb4`）；**递补池首次激活合规**（hubei 412×2 → liaoning 序位 #1）；backfill 三齐实质达成；evidence 代换留痕结构为全链最佳。裁定 **PASS（有限通过）**，P3/P4 转 650。**不宣称任何 PASS；O1 仍 OPEN。**

## §F. 650 签发依据

docs/73 §5.1 scope A（第 9 次扩展）：650 = M4.13 v7 **guizhou + jiangsu**（递补池剩 shaanxi/sichuan）+ P3-1 蓝图更正与规范固化 + P4 三处（rev85 顺修）。已用省全集（槽位）：HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX/HUN/AH/**HUBEI(槽→LN 实)**/JL。

— End 649 audit 20260901 —

---

# ══════════ PART 2 / 650 任务书 ══════════

# 650-stage0-architect-m4-13-v7-substitute-labeling-tasking — 任务书 (knife 650, 2026-09-01)

> **角色**: 架构师 → 执行端（沿用 645-649 模式：架构师自签 + 自交付，per 2026-08-31 21:50 豁免）
> **前置**: 649 DELIVERED + 审计 **PASS（有限通过）**（`649-stage0-cursor-s649-m4-12-v6-audit-PASS-20260901.md`）
> **scope**: scope A per docs/73 §5.1 = M4.13 v7（guizhou + jiangsu 第 13/14 样本）+ 649 审计 P3-1 蓝图更正与规范固化；**O1 零动作**
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS（沿用红线；**O1 仍 OPEN**）

---

## §0. 红线（13 条，12 沿用 + 1 增补）

1. 不宣布 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS
2. 不补零 / 不静默硬编码 value（domain 值 NULL 透明占位，沿用 641-649）
3. 不爬网 / 不镀铬四轨 / 不把目录页标 FETCHED；≤12 HTTP total（650 全刀预期 2-10）
4. 不改 docs/45/50/53/66/67/68/69/70/71/72/73 既有正文 —— **修正项一律行内 append 尾注，不删行不删 OPEN 行**（End 行就地扩展沿用前例须可溯；**scripts/ 蓝图 SQL 的 P3-1 更正不属 docs 正文，允许行内更正 + 尾注标记**）
5. 不碰 4 fixture 锁值（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）
6. 数据源唯一 = 政府/统计局/研究机构自取；用户零裁定；执行端不可提任何用户裁定事项（2026-08-29 铁律）
7. 完成 = observation SUCCESS，禁止 PARTIAL
8. 不新写 016 migration（沿用 009+010+014+015 lineage JSONB）
9. chain_id = `'real_650_m4_13_policy_detail_v7'`（末段 `_v7`，≠ 649 `_v6` ≠ 648 `_v5`）
10. UUID **i 段**（i0/i1-i6`eebc99`，后缀编号自报并全 distinct）≠ 649 h 段 / 648 g 段 / 647 f 段 / 646 e 段 / 645 d 段 / 644 c 段
11. 不写 cegr.* 生产表（read-only；seed SQL 仅 staging 蓝本）
12. 既有 registry 行 SHA 零漂移；4 fixture 字节零触碰；m2 crosscheck 报告零 diff
13. **增补**: O1 零动作 + 递补池按序（shaanxi → sichuan；每候选 ≤4 attempts）+ 附属产物指针条款（沿用）+ **代换行标注规范：source_registry `province`/`source_name` 一律用 actual_province（URL 归属省），original_province 仅存 lineage JSONB**（per 649 审计 P3-1，固化 647 先例）

## §1. 任务分解

### 650-A.0 649 审计 P3-1 蓝图更正 + 规范固化

- `scripts/seed_m4_12_policy_detail_real_v6.sql` h02 行行内更正（允许，非 docs 正文）：`'CN', 'HUBEI'` → `'CN', 'LIAONING'`；`source_name` → `'辽宁省人民政府 政务公开 landing (hubei 槽 412×2 递补 per 649; per 650-A.0 P3-1 更正)'`；行尾 append 尾注标记 `-- per 649 审计 P3-1 / 650-A.0 行内更正 2026-09-01`
- 同文件其余引用该样本名称的 policy 表行若有 "湖北省"（湖北）字样同步更正 + 尾注
- docs/73 §6 行内 append 尾注登记 649 审计结果（PASS·有限通过 + P3-1 + P4×3 已修/登记）

### 650-A.1 M4.13 政策详情 v7 真实化 spike（第 13/14 样本）

- 沿用 649 fetch/seed 模式：**2 新样本**（≤12 total）
  - guizhou 首选: `https://www.guizhou.gov.cn/zwgk/`；fallback #1 `https://www.guizhou.gov.cn/`（省府根）
  - jiangsu 首选: `https://www.jiangsu.gov.cn/zwgk/`；fallback #1 `https://www.jiangsu.gov.cn/`（省府根）
  - 两级均 BLOCKED → 递补池按序 shaanxi → sichuan
  - 已用省全集（不得重复，按 actual_province 口径）: HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX/HUN/AH/**LN**/JL
- 产物: `scripts/fetch_m4_13_policy_detail_v7_2024.py` + `scripts/seed_m4_13_policy_detail_real_v7.sql`（2 样本 × 8 表 = **16 INSERT 行**；语句数自报；代换若触发按红线 13 标注 actual_province）
- lineage 全 `is_demo='false'`；chain_id 见红线 9；UUID i 段；真实 SHA 2 个 distinct（≠ 638-649 全部 SHA；drift 按 docs/52 (a) 注记）

### 650-A.2 O1 零动作（沿用）

### 650-A.3 架构师级审查文档

- `docs/74-m4-13-policy-detail-real-v7-20260901.md` §1-§6 + 650-A.0 更正说明

### 650-A.4 证据 2 文件

- `docs/reports/m4_13_policy_detail_real_v7_20260901.md` + `evidence_pack/m4_13_policy_detail_real_v7_20260901.json`（沿用 649 cell 结构：actual_province/fallback_chain_used/逐 attempt 锚点）

### 650-B 测试（≥8 用例，全套 green）

- `tests/test_m4_13_policy_detail_real_v7.py` ≥8（守门: 2 SHA distinct ≠ 638-649 / i 段 ≠ h·g·f·e·d·c / chain_id `_v7` / 16 INSERT / is_demo='false' / 不宣称 PASS / docs/74 六节 / **P3-1 更正守门：seed_m4_12 无 'HUBEI' 残留于代换行 + 存在 LIAONING 更正尾注**）
- 回归: 649 全量 98 例保持 green（总 ≥106）

### 650-C 回执 + commit + 双推

- 回执 `650-stage0-cc-m4-13-v7-substitute-labeling-receipt-20260901.md` §PHOTO-1..N
- EXEC-QUEUE rev85 → rev86（§CURRENT DELIVERED + §CHAIN_TAIL 650 OPEN→DELIVERED + §ACK entry）；**backfill 三齐 + rev header 行同步**（per 649 审计 P4 教训：顶部 `> **rev N**` 行必须与 §META 同步）
- 每 commit 双推: `git push origin HEAD && git push github HEAD`

## §2. 验收命令（审验端一键）

```bash
cd "/Users/kjonekong/projects/china platform"
python3 -m pytest tests/test_m4_13_policy_detail_real_v7.py tests/test_m4_12_policy_detail_real_v6.py tests/test_m4_11_policy_detail_real_v5.py tests/test_m4_10_reverify_jx.py tests/test_m2_report_hygiene.py tests/test_m4_10_policy_detail_real_v4.py tests/test_m4_9_policy_detail_real_v3.py tests/test_o1_live_candidate_probe.py tests/test_m6_spike_docs_closure.py tests/test_m4_8_policy_detail_real_v2.py -v
# 期望: 650 ≥8 + 649 侧 98 = ≥106 passed
git log --oneline -8 && git status -s   # 期望: 650 commits 双推, 无 pending diff
grep -n "LIAONING" scripts/seed_m4_12_policy_detail_real_v6.sql | head -2   # 期望: P3-1 更正命中 + 尾注标记
```

— End 650 tasking 20260901 —
