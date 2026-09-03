# 661 审计 + 662 任务书 合并件（knife 661 AUDIT / knife 662 TASKING, 2026-09-03）

> **角色**: Cursor 审验端。**前置**: 661 DELIVERED+DBL-PUSHED（9 commits `445b855→901832e`; docs/87 + P1 一刀切: 5 指标 tab + 国家锚 + 溯源 popover + 31 省动态路由 + peer-compare 真数据化）; **用户亲眼确认生产站 28 省 GDP/增速/一二三产可见 = F1 redeploy 用户侧回执成立**。

---

# PART 1 — 661 审计（PRD 对齐重排 + P1 产品化一刀切）

## §0. 裁定（定案）

**PASS（有限通过）** — 1×P4 + 2×N（P4-1: **last_delivery 链尾未含 post-receipt P1 修复** `901832e`（type-only import webpack fix; §META rev109 写于 `415542c` 时点, 之后修复未回写 last_delivery〔v3.4 对链精神; 660 同类前科〕→ rev110 修正为 `901832e`。N-1: docs/87 §7.2 标题引「至少 8 维度」vs PRD 原文 15 项子能力（正文表格按 15 项计, 仅标题口径偏差）。N-2: **F2 公网 12 项验收未闭环**（redeploy 后的正式验收留 #832-F2; 用户肉眼回执可代 F1 但 F2 仍需脚本化实证 → 662 承接））。

## §A. 审计复现矩阵（2026-09-03 本机）

| # | 项 | 结果 | 判 |
|---|---|---|---|
| A1 | 治理集 23 文件（22 旧 + s661 新 13 cases） | **377 passed in 3.05s**（≥374 达成; 底限 ≥370 超 1.9%） | ✓ |
| A2 | m2 零 diff + 树净 | 0 / 0 | ✓ |
| A3 | docs/87 质量 | §7.1-7.7 逐项对照 + 现状小结（6/8/…子项 live|demo|无）+ §2 在库未上页盘点 8 行 + §3 三期路线（P1 locked 引 user_ruling_661; P2/P3 待裁定且**执行端禁开**）+ §5 本刀对应 + §6 深水区红线; 81 表行 | ✓ |
| A4 | P1 切片实证 | 首页 5 指标 tab ✓（**用户回执: 生产站可见 GDP/增速/一二三产**）; NATIONAL 锚行 ✓; 溯源 popover（source_url + source_hash_prefix; lineage_source/origin 已入 JSON/类型未全露出→662）; 31 省动态路由（5 静态页删除→[slug]）✓; peer-compare 真数据优先 + mock 仅回退带 DEMO 标 ✓（红线合规） | ✓ |
| A5 | docs/54 呈现层里程碑行 | 已补 ✓ | ✓ |
| A6 | §META rev109 | 五字段同步 ✓（last_delivery/last_receipt 均更新; 较 660 改善）; **但链尾停 760363e 未含修复 901832e** | ✗→P4-1 |
| A7 | git 链 | 9 commits; 三 ref 全等 `901832e`; tsbuildinfo 入 gitignore ✓ | ✓ |

## §VERDICT

- ☑ **PASS（有限通过）**【定案 2026-09-03】— **P1 按 docs/87 §3.1 一刀切完成**: PRD §7.1/7.2/7.3 三段从 1 live 升 3 live; 生产站已可见（用户回执）。
- 遗留: F2 脚本化验收 + 血缘 3 字段全露 + demo 壳标注 + 指标定义页 → **662 P1 收尾刀**。

---

# PART 2 — 662 任务书（P1 收尾刀: 库中数据全量呈现闭环 + 公网验收脚本化）

## §0. 用户指令直答

用户确认生产站已见 28 省 GDP/增速/一二三产（= 661 P1 生效）, 并指令「这只是地基极小一部分, **尽快将现有数据按 PRD 要求呈现**」。662 = 把**库中已有但页面未露出/未标注**的部分全部收口——不新采数据（P2 待裁定）, 不碰深水区（P3 禁开）。

## §1.662 主体（六件, 全前端 + 静态导出扩展）

1. **血缘全量露出**（PRD §3.3）: 溯源 popover 补 `lineage_source`/`lineage_origin`（JSON 已有字段）; 31 省详情页 + 首页全表可溯
2. **指标定义页** `/indicators`（PRD §5.2 + §3.2 来源等级）: 5 指标定义/单位/口径/**来源等级分布**（OFFICIAL_INTAKED 5 省 vs HONGHEIKU_TRANSLOAD 23 vs DATA_MISSING 3）+ 国家锚口径; 数据从 mart/observation 元数据导出（禁手写）
3. **数据完整度面板**（PRD §7.2「数据完整度和不确定性」切片）: 31 省 × 5 指标覆盖矩阵 + 3 省缺失公示 + lineage_ruling 分布统计; 首页与详情页入口
4. **31 省 × 5 指标组合视图**: 省详情页 5 指标卡齐（若 661 已齐则验核+测试固化）; 首页排序切换（按任一指标, 禁全国实时排名红线仅禁「排名榜单」呈现——排序交互需带口径提示, 参 docs/05 §8.3）
5. **demo 壳显式标注**: `seven-dim`/`research/m1-series`/`research/q1-2024-gdp`/`public-extracts` 各页顶部 DEMO/MOCK 横幅（同 layout 模式; **禁静默假数据**）; 导航分组 LIVE / DEMO
6. **F2 公网验收脚本化**: `deploy/static-export/verify-live.sh`——curl 生产域名断言 ≥12 项（LIVE MODE 标/5 指标 tab/国家锚行/31 行/3 暂缺/溯源三字段/无 MOCK MODE/指标定义页/覆盖矩阵/DEMO 横幅×4/省份详情可路由/compare 真数据）; 产出 evidence JSON 入链; **需 #832 SSH 或用户代跑**, 输出回执即 F2 闭环

## §1.662-B 测试与验收

- `tests/test_p1_completion_s662.py` ≥14（血缘 5 字段全露/指标定义 5 条+来源等级三分布/覆盖矩阵 155 格=31×5+3 缺公示/排序交互口径提示/4 demo 页横幅断言/verify-live.sh 12 项断言/静态导出可构建/mart JSON 未回归）+ smoke §18
- 治理集 24 文件 **≥391 green（底限 ≥385）**; m2 零 diff×2; redeploy 沿用 deploy.sh; F2 evidence 回执

## §1.662-C 产物与链

指标定义 JSON + 覆盖矩阵数据导出 + page 扩展 + verify-live.sh + tests + receipt; 七字段原子 rev110→rev111（**last_delivery 含 post-receipt 修复链尾**〔P4-1 教训〕）; 双推三 ref。

## §1.662-D 红线

红线 1-14 + v3.5 + user_ruling_661 沿用; **全部数据只准库/mart 导出**; demo 壳只准标注不准真数据冒充也不准删; 排序禁榜单化（docs/05 §8.3）; **P2/P3 不得开**（需 user_ruling）; 24 里程碑不宣布; O1 OPEN; docs/81 零改动。

---

— End 661 审计 + 662 任务书 20260903 —
