# 648-stage0-cursor-s648-m4-11-v5-audit — 审验报告 PASS（有限通过）(knife 648 audit, 2026-09-01)

> **角色**: Cursor（审验端） · **对象**: 648 完整链路（M4.11 v5 + jiangxi 复验 + m2 卫生收口）
> **入口**: 回执 `648-stage0-cc-m4-11-v5-quality-hygiene-receipt-20260901.md` + 任务书 `648-stage0-architect-m4-11-v5-quality-hygiene-tasking-20260901.md`
> **裁定**: **PASS（有限通过）** — 2×P3（reverify 拆独立文件致验收命令字面失败；EXEC-QUEUE 回填缺失三处）+ 3×P4，转 649 处置/登记
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS；**O1 仍 OPEN**

---

## §A. 独立复跑（审验端一手）

| # | 验收项（任务书 §2） | 结果 |
|---|---|---|
| A1 | `pytest` 6 文件（M4.11 16 + M4.10 14 + M4.9 10 + O1 6 + M6 10 + M4.8 12） | **68 passed in 1.76s** ✓（≥60 达成） |
| A1b | 补跑交付内另 2 文件（reverify 8 + hygiene 5） | **13 passed in 1.42s** ✓（合计 81 全 green；回执称 80，P4-3 口径差） |
| A2 | git 链 648：`69a8f91` → `033cbdc`(rev81) → `7560b0f`(receipt) → `cf24840`(backfill) | 4 commits ✓，树净 ✓ |
| A3 | 双推：HEAD = origin/main = github/main = `cf24840` | ✓（双 remote reflog 逐 commit 铁证） |
| A4 | `grep -c reverify evidence_pack/m4_11_…json` 期望 ≥1 | **0 —— 命令字面失败** → 见 P3-1（实质在独立文件 `m4_10_reverify_jx_20260901.json`，改查该文件 ≥1 ✓） |
| A5 | 树净（含 m2 报告零 diff） | ✓ 且**跑过生成测试后仍净**（卫生收口实证） |

## §B. 交付物逐项核验（任务书 §1 对照）

| # | 项 | 核验 | 结果 |
|---|---|---|---|
| B1 | A.0 jiangxi 复验 | re-fetch 200；**new_sha == original_sha（sha_match=true，零 drift）**；锚点 72 命中（江西/jiangxi）、body 44306 字符、waf_marker_present=true（title="403" 判定为真实内容页的真实标题）；verdict **CONTENT_CONFIRMED** | ✓（647 P3-1 收口） |
| B2 | A.0 登记落点 | docs/71 **§7 append**（line 240）+ End 行移位重加（就地扩展，P4-4）；reverify evidence 独立文件 + 8 守门测试 | ✓（拆分偏差见 P3-1） |
| B3 | A.1 fetch hunan | `/zwgk/` 404 → 省府根 200（chain fallback_1）；SHA `4006439e…` 113702B | ✓ |
| B4 | A.1 fetch anhui | `/zwgk/` http_code=0（curl 错误，evidence reason 留痕）→ 省府根 200；SHA `a06e174f…` 128409B | ✓ |
| B5 | A.1 未触发代换 | 两省 fallback 命中，预授权池未启用 ✓；已用省约束遵守（HUN/AH ∉ 已用集） | ✓ |
| B6 | HTTP 预算 | M4.11 = 4 + reverify = 1 → **全刀 5/12** ✓ | ✓ |
| B7 | seed SQL | 10 语句 / 16 行；chain_id `real_648_m4_11_policy_detail_v5`（×20 处）；**g 段** 分布 g0×12/g1×6/g2×4/g3×2/g4×4/g5×2/g6×2，f·e·d·c 段 **0 命中**；is_demo='false'（守门测试 green） | ✓ |
| B8 | A.2 卫生收口 | `scripts/crosscheck_m2_2024_gdp.py` 最小改：argparse `--output/-o`（默认路径不变，测试走 tmp）；3 行删除均在脚本内（非 docs 正文）；`test_m2_report_hygiene` 5 例 + 实证"跑完生成测试树仍净" | ✓（647 P3-3 收口） |
| B9 | A.3 docs/72 | §1-§6 全（§2 = jiangxi 复验专节）；文件名短后缀（P4-1） | ✓ |
| B10 | A.4 evidence ×2 | m4_11 report+json + reverify json（B1） | ✓ |
| B11 | B 测试 | M4.11 **16 新**（≥8）+ reverify 8 + hygiene 5 = 29 新；回归全 green（A1/A1b） | ✓ |
| B12 | C | rev81 字段基本齐；**last_receipt 未回填 SHA**（仍标"待 §C-3 commit"，P4-2）；§ACK ×3；回执 §COMMIT_PLAN 与 4 commits 一致 | ⚠（P4-2） |

## §C. 红线 13 条复核

1-12 全部遵守（≤12 HTTP=5 ✓ / docs 既有正文仅 append——docs/71 End 行就地扩展见 P4-4 / 4 fixture 零触碰 ✓ / chain_id `_v5` ✓ / g≠f≠e≠d≠c ✓ / m2 报告在交付 diff 与运行后均零改动 ✓）；13（O1 零动作 + substitute 未越池）✓。

## §D. 发现（全部非阻塞）

| 级 | # | 发现 | 处置 |
|---|---|---|---|
| **P3** | 1 | **reverify 产物拆独立文件**：任务书 §1-A.0 要求"并入 648-A.4 evidence（fetch_log phase=jiangxi_reverify）"、§2 验收命令 `grep reverify m4_11.json` 字面失败（=0）；实质完备（独立 json + docs/71 §7 + 8 测试），但验收口径与交付结构失配 | 649-A.0 口径统一：附属复验产物允许独立文件，但**主 evidence summary.methodology 必须含指针**（文件名 + verdict）；649 任务书验收命令按新口径写 |
| P4 | 1 | docs/72 文件名缺 `-quality-hygiene` 后缀（任务书指定名）——链接已按实际名落，不改名 | 登记 |
| **P3** | 2 | **EXEC-QUEUE 回填缺失三处**：cc_head 链缺口（`033cbdc`/`7560b0f`/`cf24840` 未入链）+ last_receipt 无 SHA（仍"待 §C-3 commit"）+ §NOW 陈旧（仍写"CC 执行 648"）；且 `cf24840` commit message 称"cc_head chain + 7560b0f + last_receipt 更新"但 diff 仅触碰回执文件（message 与内容不符） | rev82 由审验端全面修复；649-C 验收增加"backfill 完整性"检查（cc_head 入链 + last_receipt SHA + §NOW 刷新三齐） |
| P4 | 3 | 回执 80/80 vs 实测 68+13=81（off-by-one 口径差） | 免修 |
| P4 | 4 | docs/71 End 行就地扩展（+648-A.0 字样）而非纯 append——沿用 646/647 前例，git 可溯 | 接受 |

## §E. 结论

648 三合一**全数落地**：jiangxi "403" **CONTENT_CONFIRMED**（SHA 零 drift + 72 锚点，647 P3-1 闭环）；M4.11 v5 hunan/anhui 16 INSERT（g 段 + `_v5` + 2 NEW SHA，HTTP 5/12）；m2 卫生收口实证有效（生成测试跑后 tracked 零 diff）。81 例全 green；4 commits 双推铁证。裁定 **PASS（有限通过）**，P3/P4 转 649。**不宣称任何 PASS；O1 仍 OPEN。**

## §F. 649 签发依据

docs/72 §5.1 scope A（第 7 次扩展，激活预授权池）：649 = M4.12 v6 **hubei + jilin**（池内取 2，剩余 liaoning/shaanxi/sichuan/guizhou/jiangsu 递补）+ A.0 口径统一（P3-1）+ rev82 修复（P4-2 审验端已做）。已用省全集：HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX/HUN/AH。

— End 648 audit 20260901 —
