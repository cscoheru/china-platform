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
