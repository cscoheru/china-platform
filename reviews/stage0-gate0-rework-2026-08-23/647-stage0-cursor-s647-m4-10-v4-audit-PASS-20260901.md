# 647-stage0-cursor-s647-m4-10-v4-audit — 审验报告 PASS（有限通过）(knife 647 audit, 2026-09-01)

> **角色**: Cursor（审验端） · **对象**: 647 完整链路（M4.10 v4 + 646 审计 P2/P3 修正 + O1 零动作）
> **入口**: 回执 `647-stage0-cc-m4-10-v4-f7-fixes-receipt-20260901.md` + 任务书 `647-stage0-architect-m4-10-v4-f7-p2-fixes-tasking-20260901.md`
> **裁定**: **PASS（有限通过）** — 2×P3（jiangxi 样本 title="403" 真实性待复验；跨省代换超任务书字面授权但合规）+ 3×P4，全部转 648 处置
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS；**O1 仍 OPEN**

---

## §A. 独立复跑（审验端一手）

| # | 验收项（任务书 §2） | 结果 |
|---|---|---|
| A1 | `pytest` 5 文件（M4.10 14 + M4.9 10 + O1 6 + M6 10 + M4.8 12） | **52 passed in 0.96s** ✓（≥48 阈值达成；回执口径 51 = 14+16+12+9 含 644 不含 M6，双绿） |
| A2 | git 链 647：`2db29d7`(delivery) → `c68f8e2`(rev79) → `cfcce7b`(receipt) → `4d01f33`(backfill) | 4 commits ✓；审后树净 ✓ |
| A3 | 双推：HEAD = origin/main = github/main = `4d01f33` | ✓ + 双 remote reflog 逐 commit 推送（4b0c70b→2db29d7→c68f8e2→cfcce7b→4d01f33 两份齐全）✓ |
| A4 | dual_poll_status | KNIFE=647 · 647 DELIVERED · CURSOR_ACTION=AUDIT_NOW ✓ |

## §B. 交付物逐项核验（任务书 §1 对照）

| # | 项 | 核验 | 结果 |
|---|---|---|---|
| B1 | 647-A.0 **P2-1 F7 补登记** | docs/70 §4.2 表尾 append（henan `2026-08-20` vs seed `2026-08-30`，SHA/字节一致，纯元数据；成因=抓取时刻 vs 撰写时刻） | ✓（守门测试 `test_docs_70_p2_1_f7_postscript_647_a0` green） |
| B2 | 647-A.0 **P3-2 措辞更正** | docs/70 §6 行内 append（docs/52 零改动=合规；落点=evidence/report） | ✓（`test_docs_70_p3_2_wording_correction_647_a0` green） |
| B3 | docs/70 append-only | delivery diff 恰 **+6 行 0 删**；`test_docs_70_no_destructive_edit_preserves_open_lines` green | ✓ |
| B4 | 647-A.1 fetch zhejiang | `/zwgk/` 403 WAF → fallback `/`（chain_index=1）200；SHA `8016ef08` 159382B | ✓ |
| B5 | 647-A.1 fetch shandong | 4 attempts 全 BLOCKED（HTTPS TLS sslv3 handshake_failure ×2 + HTTP 404 + HTTP timeout）→ fetch_log 逐条留痕 | ✓ |
| B6 | 647-A.1 **625 跨省代换** | jiangxi `/zwgk/` 200（48118B，SHA `56481050`）；evidence cells 含 `original_province`/`substitute_reason`；docs/71 §2.2 完整 fallback 矩阵；未用省约束遵守（JX ∉ HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ） | ✓ 合规（授权边界见 P3-2） |
| B7 | HTTP 预算 | http_count = **7/12**（zj 2 + sd 4 + jx 1；fetch_log 一条 attempt=6 marker 不计）；HTTP_LIMIT=12 脚本实存 | ✓ |
| B8 | seed SQL | 10 语句 / **16 行**；chain_id `real_647_m4_10_policy_detail_v4`；f 段分布 f0×12/f1×6/f2×4/f3×2/f4×4/f5×2/f6×2，e·d·c 段 **0 命中**；`is_demo='false'` 16 处、true=0 | ✓ |
| B9 | 647-A.2 O1 零动作 | 交付 7 文件无 probe 脚本、无 registry/connector/O1 evidence 触碰；`git diff` O1 相关零改动 | ✓ |
| B10 | 647-A.3 docs/71 | §1-§6 全（§2.2 代换注记 + §4 SHA 区分表） | ✓ |
| B11 | 647-A.4 evidence ×2 | m4_10 report（含 §3 HTTP 日志逐条 + 403 title 原样记录）+ json（fetch_log 8 条 + cells 2） | ✓ |
| B12 | 647-B 测试 | **14 新**（≥10）+ 回归 = 52 green（A1） | ✓ |
| B13 | 647-C | rev79（status/last_delivery `2db29d7`/last_receipt `cfcce7b`/§ACK×3/647 DELIVERED 行）；回执 §COMMIT_PLAN 与实际 4 commits 一致 | ✓ |

## §C. 红线 13 条复核

1-12 全部遵守（含 ≤12 HTTP=7 ✓ / 既有正文仅 append +6 ✓ / 4 fixture 零触碰 ✓ / chain_id `_v4` ✓ / f≠e≠d≠c ✓ / registry 零漂移 ✓）；13（O1 零动作）✓。**注**：红线 3"不把目录页标 FETCHED"——jiangxi 样本为 landing 直抓、SHA 真实、title 诚实记录，不在违规范畴（但见 P3-1）。

## §D. 发现（全部非阻塞）

| 级 | # | 发现 | 处置 |
|---|---|---|---|
| **P3** | 1 | **jiangxi 样本 title="403"**（evidence 原样保留，48118B）——疑似 WAF 挑战页或异常标题页，内容真实性未经二次验证；seed 标题字段为人工正名（"江西省人民政府 政务公开 landing"），与 raw title 存在美化落差 | 648-A.0 复验：1×HTTP re-fetch + SHA 对比 + 内容锚点（含"政务公开"）；一致=注记确认，不一致=按 docs/52 (a) drift 登记 + 评估换样 |
| **P3** | 2 | **跨省代换超出任务书字面授权**（任务书仅授权省内 fallback #1 省府根；无跨省条款）——但 625 先例（646 任务书 gd fallback #2=guizhou 跨省）+ 红线 7 禁 PARTIAL + 全程留痕 + 未用省约束遵守 → 接受为文档化偏差 | 648 任务书显式 substitute 条款（预授权代换池 + 即时登记义务），收口此类偏差 |
| **P3** | 3 | **m2 crosscheck 报告污染复发第 2 次**（执行端全量 pytest 重写 tracked `docs/reports/m2_2024_gdp_crosscheck_20260831.md`，5/31→5/34；审验端已 checkout 还原）——系统性 tech-debt | 648-A.2 卫生收口：生成型测试默认跳过或输出改 tmp 路径；禁止全量跑挂起套件（沿用 645 教训） |
| P4 | 1 | evidence summary methodology 字符串陈旧（仍写 "shandong /zwgk/"；fetch_log/cells 全量准确） | 免修，登记 |
| P4 | 2 | 回执 51/51 vs 任务书验收口径 52（用例集差异：回执含 644 回归不含 M6） | 免修，双绿备注 |
| P4 | 3 | 元数据口径：zj publication_date=抓取日 `2026-09-01`；jx `2025-07-16` | 免修，登记 |

## §E. 结论

647 链路**实交付、可复跑、可追溯**：52/52 独立 green；4 commits 双推铁证；16 INSERT/10 语句；f 段 + `_v4` + 2 NEW SHA（`8016ef08`/`56481050`）全守门；P2-1/P3-2 修正落地（append-only +6）；O1 零动作三零保持。shandong 4 连 BLOCKED 留痕完整，jiangxi 625 代换合规但触发样本质量与授权边界两项 P3。裁定 **PASS（有限通过）**，P3 转 648 处置。**不宣称任何 PASS；O1 仍 OPEN。**

## §F. 648 签发依据

docs/71 §5.1 scope A（第 6 次省扩展）+ 647 审计 §D：648 = **三合一**（A.0 jiangxi 复验 + A.1 M4.11 v5 扩展 hunan/anhui（显式 substitute 条款）+ A.2 m2 报告污染卫生收口）。已用省全集：HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX。

— End 647 audit 20260901 —
