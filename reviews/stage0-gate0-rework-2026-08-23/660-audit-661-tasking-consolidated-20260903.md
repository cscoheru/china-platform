# 660 审计 + 661 任务书 合并件（knife 660 AUDIT / knife 661 TASKING, 2026-09-03）

> **角色**: Cursor 审验端。**前置**: 660 DELIVERED+DEPLOYED+DBL-PUSHED（7 commits `3875989→3b10dbd`; newvps 静态导出上线; **用户亲眼确认 28 省真数据 = 用户侧回执成立**; 本机 curl 双域名仍 000 不可达〔网络路径〕）。**背景**: 用户质询「660 刀下来才一个 28 省表格, 与 PRD 设计初衷相差十万八千里」→ 本件 PART 2 直答 + 661 = PRD 对齐重排刀。

---

# PART 1 — 660 审计（Track B 静态导出公网上线）

## §0. 裁定（定案）

**PASS（有限通过）** — 1×P4 + 3×N（P4-1: **§META rev107 五字段对链漏更第 5 例**——last_delivery/last_receipt 仍指 659 的 `5de42a8`/`dc09cea` 未随 660 交付更新〔v3.4 条款为此而立, 657 前科〕**+ cc_head 行重复两行**〔rev107 编辑事故〕→ rev108 修正。N-1: 测试文件名偏离（`test_mart_static_export_s660.py` vs 任务书 `test_production_deploy_readiness.py`; 12 cases 内容覆盖等价, 复跑实证）。N-2: `docs/86` 上线回执文档未独立建（并入 receipt; 任务书 §1.660-C 要求）。N-3: receipt 写 `china.3strategy.cc` vs 用户域名 `3stratege.cc` 拼写不一致〔需用户确认实际域名〕）。

## §A. 审计复现矩阵（2026-09-03 本机）

| # | 项 | 结果 | 判 |
|---|---|---|---|
| A1 | 治理集 22 文件（21 旧 + s660 新） | **364 passed in 2.20s**（351+12+1; ≥359 达成） | ✓ |
| A2 | m2 零 diff + 树净 | 0 / 0 | ✓ |
| A3 | deploy 四件 | `deploy/static-export/{export-mart-data.py, deploy.sh, precheck.sh, README.md}` 齐; export --strict 8 条红线自检; deploy.sh 7 exit codes | ✓ |
| A4 | mart JSON | `frontend/data/mart_province_gdp_2024.json` 31 行（28 真 + 3 缺） | ✓ |
| A5 | Track B 接线 | `lib/mart-static.ts` + `api.ts` Track B 分支 + `page.tsx` mart section; **线上 = 用户亲眼确认 28 省表**〔用户侧回执 per 任务书 §1.660-A fallback〕 | ✓ |
| A6 | P1 修复 | `3b10dbd` fmtNum/fmtPct 字符串数值 coerce（上线后发现即修, 处置合规） | ✓ |
| A7 | 文档 | docs/85 runbook 388 行 9 节 ✓; smoke §16 七子守门 ✓; 自审件 350 行 7 节已入链（`a9030de`）✓ | ✓ |
| A8 | git 链 | 7 commits `3875989→3b10dbd`; 三 ref 全等 `3b10dbd` | ✓ |
| A9 | §META 检查 | rev107 ruling/status 合规引用 659 裁定; **last_delivery/last_receipt 漏更 + cc_head 重复** | ✗→P4-1 |

## §VERDICT

- ☑ **PASS（有限通过）**【定案 2026-09-03】— **生产站首次显示真实数据**（用户确认）; 部署包/回执/测试/修复链完整。
- **生产真实化 = DONE（本刀范围）**; 但 660 范围仅「上线已有数据」——PRD 产品功能欠账 = 661 起（PART 2）。

---

# PART 2 — 661 任务书（PRD 对齐重排刀: docs/87 产品差距对照 + 首个产品化切片）

## §0. 用户质询直答（记入任务书）

**Q: 660 刀下来才一个 28 省表格, 与 PRD 初衷差十万八千里?**
**A**: 属实。PRD §7 定义七大产品功能（全国总览/地区画像 15 项/地区比较/历史脉络/监测预警/官员政策项目页/研究工作台）, §5 数据模型五块（指标观测+**人物任期**+**政策承诺项目**+研究推断）, 时间范围 WTO 以来 25 年, 层级国家-省-市-县。当前生产 = **1 个指标 × 1 年 × 省级 × 1 张表**。三层原因: ① 659+ 刀几乎全部花在 PRD §3 证据规则（血缘/不可变/红线）的治理地基——必要但零产品产出; ② MVP 被越切越窄（docs/54 首期定义「国家-31省-试点城市闭环」, 实际只做省级 GDP 角落; 国家锚在库未上页, M3 城市 U6 放宽, O1 时序仍 OPEN）; ③ 呈现层从未规划（660 前无部署管线）。**修正路径 = 本刀: PRD §7 逐项对照现状×数据就绪度×刀次路线, 重排主计划, 交用户裁定优先级。**

## §1.661-A.0 规范

v3.5 沿用 + 强调: §META 五字段对链**交付时必须同步 last_delivery/last_receipt**（P4-1 第 5 例, 勿再犯）; 裁定字样禁执行端写。

## §1.661 主体（两段, 均必做）

1. **docs/87-prd-product-gap-replan-20260903.md**（PRD 对齐重排, 架构师级）:
   - PRD §7.1-7.7 逐项 × 现状（live/demo 壳/无）× **数据就绪度**（已在库/部分/零）× 依赖（前端 only / 需新数据刀 / 需 PRD 深水区模型）× 建议刀次
   - 已在库未上页的盘点: 115 observation（23 省×5 指标: GDP/增速/人均等——以库实查为准）+ 国家锚 + 5 省静态详情页 + seven-dim/peer-compare/public-extracts demo 壳
   - 三期路线提案: **P1 产品化〔纯前端, 数据已在库: 多指标切换+国家锚+31 省动态详情+溯源 UI（来源链接+SHA+刀次, 血缘字段库中已有）〕** / P2 数据扩展〔多年度时序回填+M3 试点城市〕/ P3 PRD 深水区〔§5.3 人物任期+§5.4 政策承诺+§6 治理效能观察六段证据链; PRD 自估 9-18 个月级〕
   - **产出必须交用户裁定优先级**（用户 §BLOCKED 权）; docs/54 主计划补呈现层里程碑行（引用 docs/87）
2. **首个产品化切片（P1 之一, 与重排同刀落地）**: 首页表**多指标切换**（5 指标 tab/下拉, 数据从 mart-static 扩展导出 JSON; 缺失省保持「数据暂缺」）+ **国家锚行**（全国 2024 GDP 锚值置顶, 标 OFFICIAL）+ 每行**溯源链接**（点开显示 source_url + source_hash_prefix + lineage_ruling; PRD §3.3 血缘首次上页面）。

## §1.661-B 测试与验收

- `tests/test_prd_gap_replan_s661.py` ≥10（docs/87 七节齐 + §7.1-7.7 逐项有行 + 现状标注与实际 live 一致 + 三期路线含依赖列 + docs/54 引用行存在 + 多指标 JSON 5 指标×31 行 + 国家锚行 + 溯源字段三件套 + 缺失省守门 + 静态导出可构建）+ smoke §17
- 治理集 23 文件 **≥374 green（底限 ≥370）**; m2 零 diff×2; 上线 redeploy 沿用 660 deploy.sh + 用户侧回执

## §1.661-C 产物与链

docs/87 + docs/54 修订行 + 多指标 JSON + page.tsx 扩展 + tests + receipt; 七字段原子 rev108→rev109（**last_delivery/last_receipt 同步更新**）; 双推三 ref。

## §1.661-D 红线

红线 1-14 + U6 §5 + v3.5 沿用; 多指标数据**只准来自库/mart 导出**（禁手填）; 缺失省禁补零; 溯源 UI 只显示库中真实血缘字段（禁编造 source）; 24 里程碑不宣布; O1 仍 OPEN; docs/81 零改动; **docs/87 路线为提案, 优先级由用户裁定, 执行端不得自行开 P3 深水区刀**。

---

— End 660 审计 + 661 任务书 20260903 —
