# 646-stage0-cursor-s646-m4-9-o1-audit — 审验报告 PASS（有限通过）(knife 646 audit, 2026-09-01)

> **角色**: Cursor（审验端） · **对象**: 646 完整链路（M4.9 v3 + O1 B路 live-candidate + 645 审计 P3 修正）
> **入口**: 回执 `646-stage0-cc-m4-9-v3-o1-live-candidate-receipt-20260901.md` + 任务书 `646-stage0-architect-m4-9-v3-o1-live-candidate-tasking-20260901.md`
> **裁定**: **PASS（有限通过）** — 1×P2（F7 子项遗漏，非阻塞）+ 1×P3（措辞不准确）+ 3×P4（备注性），全部转 647 处置
> **不宣称**: Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS；**O1 仍 OPEN**

---

## §A. 独立复跑（审验端一手）

| # | 验收项（任务书 §2） | 结果 |
|---|---|---|
| A1 | `pytest` 4 文件（M4.9 10 + O1 6 + M6 回归 10 + M4.8 回归 12） | **38 passed in 1.80s** ✓（≥32 阈值达成） |
| A2 | git 链 646：`d75563d`(delivery) → `200b389`(cc_head rev77) → `ee0d0b8`(receipt) → `9a770a3`(receipt-backfill) | 4 commits ✓，工作树干净 ✓ |
| A3 | 双推：HEAD = origin/main = github/main = `9a770a3` | ✓ + 双 remote reflog 逐 commit 推送记录（d75563d→200b389→ee0d0b8→9a770a3 两份齐全）✓ |
| A4 | dual_poll_status | KNIFE=646 · 646 DELIVERED · CURSOR_ACTION=AUDIT_NOW · REASON=receipt_awaiting_audit ✓ |

## §B. 交付物逐项核验（任务书 §1 对照）

| # | 项 | 核验 | 结果 |
|---|---|---|---|
| B1 | 646-A.0 P3 修正 F1/F2 | word-diff 精确比对 docs/68 §4 尾 / docs/50 §4.4#48 / docs/53 §5#48：`7`→`8` 就地更正 + F1/F2 + F4 双尾注标记，未删行未删 OPEN 行 | ✓（执行方式见 P4-1） |
| B2 | 646-A.0 F4 | docs/50/53 行尾 append `实际交付 22/22 green per 645 回执/审计` | ✓ |
| B3 | 646-A.0 F5/F3/F6 | COMPASS 零动作 ✓；F3/F6 登记于任务书 §1 A.0 ✓ | ✓ |
| B4 | 646-A.0 **F7** | grep `2026-08-20` 全库：仅命中 645 审计报告本件；docs/70/69 **零登记**；回执 §PHOTO-1 未声明豁免 | **✗ → P2-1（647 补登记）** |
| B5 | 646-A.1 fetch | 2 cells（fujian `/zwgk/` + gd `/zwgk/` preferred cell 0 命中，fallback 未触发）；HTTP 2/12；HTTP_LIMIT=12 硬上限在脚本 L47/L82/L98 实存 | ✓ |
| B6 | 646-A.1 SHA | `fceb8c0a…`(fujian 682079B) / `49eed23e…`(gd 73836B)，2 distinct ≠ 638-645 全部 | ✓ |
| B7 | 646-A.1 seed SQL | 10 INSERT 语句 / **16 行**（6 multi-row VALUES ×2 行 + gc 2 语句 + pe 2 语句单行）；chain_id `real_646_m4_9_policy_detail_v3`；`is_demo='false'` 全 16 行、true=0；ON CONFLICT DO NOTHING | ✓ |
| B8 | UUID 段独立 | e 段分布 e0×12/e1×6/e2×4/e3×2/e4×4/e5×2/e6×2；d/c 段 grep 0 命中 | ✓（编号方案见 P4-2） |
| B9 | 646-A.2 live-candidate | data.stats.gov.cn 1 candidate REAL_PROBED（HTTP 1/1，HTTP_LIMIT=1 实存）；candidate_spec 含 URL/归属/观测口径/auth/启用前置；report §0-§5 六节含 §4 启用前置条件；O1 OPEN / connector False / PENDING_CANDIDATE_ONLY | ✓ |
| B10 | registry/生产零改动 | `git diff d3e0db5..9a770a3 --stat -- source_registry/` 为空；cegr.* 零写；4 fixture 零触碰（交付 13 文件均非 frontend/fixture） | ✓ |
| B11 | docs/52 零改动 | 646 链 `docs/52*` diff 为空 → **合规**（任务书 A.2 只要求登记并入 evidence/report + registry 零改动）——但 docs/70 §6 声称"docs/52 行内 append 全部落地" | 措辞 → P3-2 |
| B12 | 646-A.3 docs/70 | §1-§6 全（§4 SHA 区分表 17 行） | ✓ |
| B13 | 646-A.4 evidence ×4 | m4_9 report+json / o1 report+json 结构完整、字段与回执一致 | ✓ |
| B14 | 646-B 测试 | 16 新（≥10）+ 22 回归 = 38 green（A1 独立复跑） | ✓ |
| B15 | 646-C | 回执 §PHOTO-1..7 + §COMMIT_PLAN 与实际 4 commits 一致；EXEC-QUEUE rev77（status/last_delivery `d75563d`/last_receipt `ee0d0b8`/§ACK 646 DELIVERED entry）与 git 匹配 | ✓ |

## §C. 红线 13 条复核

1-12 沿用：全部遵守（不宣称 PASS ✓ / 不补零 ✓ / 不爬网·目录页未标 FETCHED ✓ / 既有正文仅行内更正+尾注 ✓ / 4 fixture 零触碰 ✓ / 数据源=政府（fujian/gd/NBS）✓ / SUCCESS 无 PARTIAL ✓ / 无 016 migration ✓ / chain_id `_v3` ✓ / e≠d≠c ✓ / cegr.* 零写 ✓ / 既有 registry SHA 零漂移 ✓）。
13（新增 live-candidate 只登记不启用）：O1 OPEN ✓ connector False ✓ registry 零改动 ✓。

## §D. 发现（全部非阻塞）

| 级 | # | 发现 | 处置 |
|---|---|---|---|
| **P2** | 1 | **F7 未登记**：任务书 A.0 明示"docs/69 或 docs/70 尾注登记 F7（henan-zwgk evidence `publication_date=2026-08-20` vs seed SQL `2026-08-30`）"，实际 docs/70/69 零登记且回执未声明豁免 | 647-A.0 补登记（docs/70 §4 表尾行内 append） |
| **P3** | 2 | **docs/70 §6 措辞不准确**："docs/52 行内 append 全部落地"——实际 docs/52 零改动（合规），登记全在 evidence/report；回执 §PHOTO-3 标题同类措辞（回执不可改，免修） | 647-A.0 行内尾注更正 docs/70 §6 |
| P4 | 1 | P3 修正执行方式 = 就地数字更正（7→8）+ 尾注标记，非纯 append——符合审计 F1 修正义、git 全程可溯、未删行 | 接受，备注 |
| P4 | 2 | UUID e 段后缀编号（e02-e05/e11-e62）偏离任务书草案（e21-e94）；不变量（e≠d≠c、全 distinct）成立且 docs/70 §4 已记录实际方案 | 接受，备注 |
| P4 | 3 | 元数据小疵：fujian cell `publication_date="2025-4-24"` 非 ISO；gd title 含未解码 `&nbsp;` 实体；回执 §PHOTO-5 称"5 节"实列 6 节（o1 report §0-§5） | 免修，登记 |

## §E. 结论

646 链路**实交付、可复跑、可追溯**：38/38 pytest 独立 green；4 commits 双推铁证；16 INSERT/10 语句结构精确；2 NEW SHA + e 段 + `_v3` chain_id 全部守门；O1 live-candidate 只登记不启用（registry/cegr.*/connector 三零）。裁定 **PASS（有限通过）**，P2/P3 转 647-A.0 处置。**不宣称任何 PASS；O1 仍 OPEN。**

## §F. 647 签发依据

docs/70 §5.1 scope A（推荐）：M4 系列第 5 次省扩展。已用省全集 = HLJ/HENAN/YUNNAN（644）+ HLJ/HENAN-v2（645）+ FUJIAN/GD（646）→ 647 取 **zhejiang + shandong**（第 7/8 样本）。O1 沿 646 登记零动作（等用户/架构师裁定启用）。

— End 646 audit 20260901 —
