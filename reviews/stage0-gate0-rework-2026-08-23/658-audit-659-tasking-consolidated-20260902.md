# 658 审计 + 659 任务书 合并件（knife 658 AUDIT / knife 659 TASKING, 2026-09-02）

> **刀号**: 658（PART 1 审计）/ 659（PART 2 任务书）
> **角色**: Cursor 审验端（架构师审计 + 签发）
> **日期**: 2026-09-02
> **前置**: 658 DELIVERED+C（rev102; 6 commits `89f5c52→42a3b82` 三 ref 全等; v3.4 五字段对链自检首签）
> **本件模式**: 单文件（PART 1 审计 + PART 2 任务书）

---

# PART 1 — 658 审计（M2 批量 23 省 × 5 指标真实入库 + P3-1 修正〔部分〕）

## §0. 裁定（定案）

**PASS（有限通过）** — **1×P3**（P3-2 = P3-1 未竟: docs/82 §1.2 重写补齐 31 行/删虚构/终态句 ✓, **但刀号映射未按任务书 §1.658-A.2 明示的链实证更正**——rows 12-19 仍写 651=辽/吉/黔、652=江苏、654=陕/川+甘/青（同刀 4 省自相矛盾）; 链实证: **651=SHAANXI/SICHUAN〔d13b3229〕、652=XINJIANG/NEI_MENGGU〔04721b7〕、LN=649 跨省 substitute〔936640d: "hubei/jilin + substitute 池首次激活(liaoning)"〕、653=SHANDONG/HUBEI 复试、654=GANSU/QINGHAI**; §3 失败形式归属列（653=辽/吉/黔 等）与 docs/80 §5.1（653=shandong / 654=qinghai）冲突; inline 注记"核刀号: 审计基线同"为循环自证）+ 0×P4 + 2×N → **659-B 终修**。

**批量入库验证 ✓**: 23 省 REACHABLE × 5 指标 = **115 observation INSERT** + registry lineage 三重（hongheiku_tjgb/XX省统计局/U6）全行; HTTP **23/32**; 3 整省 BLOCKED 留痕（LN/HAINAN/GUIZHOU = `NOT_FOUND_IN_2024_INDEX`——hongheiku 2024 索引缺文, 缺省禁补零合规, per 任务书预案口径〔26 目标 − 3 缺文 = 23〕）; **国家锚**: 28 省观察加总 vs NBS = **−5.336%**（阈值 ±5.5% PASS, 差值=3 缺文省体量）+ 31 省估计 = **−0.8144%**（±2-3% PASS 估计口径）; **自洽 28/28 = 0.0000%**（一+二+三产=GDP 全等）; **M2.3 跨源覆盖 28/31 = 90.3%**（只读评估, 不宣称 M2 PASS）。

## §A. 审计复现矩阵（独立复跑, 2026-09-02 本机）

| # | 项 | 结果 | 判 |
|---|---|---|---|
| A1 | pytest 19 文件集 run1 | **330 passed in 2.01s**（19 新 u6_batch + 311 回归; ≥326 达成 +1.2%, 底限 ≥316 超 4.4%） | ✓ |
| A2 | 同集 run2 | **330 passed in 1.74s**（两遍同数） | ✓ |
| A3 | m2 零 diff×2 | run1=0 / run2=0 / 树净 | ✓ |
| A4 | fetch evidence | 23 REACHABLE cells + blocked_provinces 3 条带 reason+note; http_count=23/32; category-first（禁 /tag/ 遵守） | ✓ |
| A5 | anchor evidence | national_anchor −5.336%（28 省）/ −0.8144%（31 省估计）; self_consistency 23+5=28/28 = 0.0000%; ruling=U6 入链 | ✓ |
| A6 | seed SQL | 210 `INSERT INTO` 语句（multi-row VALUES = 报告 232 ROWS 口径; observation 115 = 23×5 ✓; tests 守门过） | ✓ |
| A7 | git 链 + rev102 | 6 commits `89f5c52→42a3b82` 三 ref 全等; §META 五字段全对（last_delivery=`89f5c52` **v3.4 修正保持** + last_receipt=`2840c1b` + last_amend=`1f98c5d` 新字段合规） | ✓ |
| A8 | P3-1 修正核验 | 31 行 ✓ / NINGXIA 更正 655 B ✓ / TIBET 去重 ✓ / 虚构"剩 9 省"删除 ✓ / 终态句 25R+4B+2M2 ✓ / **rows 12-19 刀号未按链实证更正 ✗（→ P3-2）** | 半 |
| A9 | 交付面 | 10 文件全在（fetch/seed×2 生成器/evidence ×2/docs 83/report/tests 19 cases/receipt 13 节） | ✓ |

## §P. 问题清单

| 级 | 数 | 内容 | 处置 |
|---|---|---|---|
| P3 | 1 | **P3-2（P3-1 未竟）**: §1.2 rows 12-19 刀号映射仍错 + §3 归属列错（详见 §0）; 任务书 §1.658-A.2 明示的链实证映射（651=陕/川, 652=新/蒙, LN=649 substitute, 653=SD/HB, 654=GS/QH）未落实; inline"核刀号: 审计基线同"= 循环自证非链实证 | **659-B 终修**: rows 12-19 + §3 归属列按链 SHA 实证逐一更正（行内注记〔659-B P3-2 终修〕） |
| N-1 | 注记 | 26 目标 → 23 入库（3 省 hongheiku 索引缺文整省 BLOCKED）——任务书预案明文口径, 红线 1/14 合规, 非问题; 3 省进入"数据暂缺"状态待 659 UI 呈现 | 659 处理 |
| N-2 | 注记 | 报告"232 INSERT ROWS" vs grep 210 语句 = multi-row VALUES 语法差异; observation 115 行口径一致; tests 守门过 | 无需修正 |

## §RED. 红线复核（658）

1 不补零 ✓（3 省整省 BLOCKED 留痕 missing_reason）/ 2 不静默硬编码 ✓ / 3 不爬网 ✓（HTTP 23/32 限速）/ 4 不改既有 docs ✓（docs/82 行内更正 per 先例; docs/81 零改动）/ 5 SHA ✓（23+5=28 转载字节全锁; fixture 4 锁值未碰）/ 6 数据源 ✓（U6 裁定 + 金丝雀 5/5 守门过）/ 7 lineage ✓（三重标注全行）/ 8 本地 ✓ / 9 三重留痕 ✓ / 10 回执 13 节 ✓ / 11 spike 蓝本不入库 ✓（本刀是 observation 数据表合法入库, 非 spike 蓝本）/ 12 m2 零 diff ✓✓ / 13 不自动宣布 ✓ / 14 BLOCKED 留痕 ✓（NOT_FOUND_IN_2024_INDEX 3 省）+ U6 §5 五条 ✓。

## §VERDICT

- ☑ **PASS（有限通过）**【定案 2026-09-02】— **页面真实化数据层完成**: 28 省 2024 GDP 真数据在库（5 官方 + 23 hongheiku 金丝雀锚定）+ 国家锚/自洽双 PASS + 330/330 两遍 + v3.4 五字段首验保持; 1×P3（刀号映射未竟）→ 659-B 终修。
- **659 = mart flip + 前端切源**（页面 GDP 真实化收官刀）。

---

# PART 2 — 659 任务书（mart flip + 前端切源 = 页面 GDP 真实化收官刀）

## §1.659 主体: mart flip（省级 GDP 真数据 mart 重建）

- **源**: observation 表 28 省 2024 真数据（5 官方〔京/沪/鲁/鄂/川〕+ 23 hongheiku〔658 入库, lineage 三重全行〕）
- **产物**: `dbt/models/marts/` 新增 **`mart_province_gdp_2024.sql`**（28 省行: province_code/name + gdp_total + gdp_growth + primary/secondary/tertiary + source/origin/ruling 三重 lineage 列）+ **3 省 DATA_MISSING 行**（LN/HAINAN/GUIZHOU: `status='DATA_MISSING'`, `missing_reason='hongheiku 2024 索引缺文 NOT_FOUND_IN_2024_INDEX'`, 指标列 NULL **禁补零**）; dbt build 跑通 + 行数守门 31（28 数据 + 3 缺失）
- **禁止**: 3 缺失省任何 0/插值/静默默认值

## §1.659-A: 前端切源（demo → 真数据默认）

- `frontend/lib/api.ts`: `USE_MOCK` 逻辑翻转——`process.env.NEXT_PUBLIC_USE_MOCK === "true"` 才 mock（**默认 false 真数据**; env 开关保留为回退通道; 注释同步更新）
- `frontend/app/page.tsx`: 省 GDP 区块渲染改走真数据 API + mart（去 `MOCK_PROVINCE_LIST` 默认渲染; **mock 模块文件保留不删**——S1.18 历史资产 + 回退）; 3 缺失省显示「数据暂缺（公报源缺文）」状态而非 0/空白
- `frontend/app/layout.tsx`: demo 横幅文案更新（"S1.18 DEMO observations" → "28 省 2024 真实数据（官方 5 + 转载锚定 23; 3 省源缺文）+ lineage 可溯"）
- `frontend/smoke-check.py`: 断言更新（默认真数据 + USE_MOCK 开关语义翻转后仍可显式开 mock）
- API 层 `/api/indicator`（或既有端点）接 mart 数据; `cache: "no-store"` 沿用

## §1.659-B: P3-2 终修（docs/82 §1.2 rows 12-19 + §3 归属列）

按**链 SHA 实证**逐一更正（行内注记〔659-B P3-2 终修〕）:
- **651** = SHAANXI/SICHUAN（commit `d13b3229` "M4.14 v8 shaanxi/sichuan 第 15/16 样本"）→ rows 16-17 刀号 654→**651**; rows 12-14（LN/JL/GZ）改判: **LN = 649 跨省 substitute**（`936640d` "hubei/jilin + substitute 池首次激活(liaoning)"）、**JL = 649**、**GUIZHOU = 按链实证定位**（grep 链 commit 定刀号, 勿沿用 651）
- **652** = XINJIANG/NEI_MENGGU（`04721b7`）→ rows 18-19 刀号 655→**652**; row 15 JIANGSU 按链实证重定位
- **653** = SHANDONG/HUBEI 双复试（retry ← 647/649）→ §3 失败形式 #1 归属 653=**shandong**（对齐 docs/80 §5.1）
- **654** = GANSU/QINGHAI → §3 #2 归属 654=**qinghai**（对齐 docs/80 §5.1; 删"654=SHAANXI/SICHUAN"矛盾）
- **655** = NINGXIA(B)/XIZANG(R) → §3 #3 归属 655=**ningxia**
- 每处更正注链 SHA 短前缀为证; 禁循环自证（"审计基线同"类注记删除）

## §1.659-C. 测试

- `tests/test_mart_province_gdp_real.py` 新 ≥12（mart 31 行 = 28 数据 + 3 DATA_MISSING / 缺失省指标 NULL 非 0 / lineage 三重列 / dbt build / api 默认真数据〔USE_MOCK 语义翻转〕/ page 无 MOCK_PROVINCE_LIST 默认渲染 / smoke-check 断言 / P3-2 终修守门〔651=陕/川 + LN=649 substitute + §3 对齐 docs/80〕）
- `test_frontend_mart_demo_parity_s296.py` 更新为 **real-parity 28 省**（mock parity 保留为显式开关 case）
- 19 文件集 330 回归 + ≥12 = **≥342 green（底限 ≥336）**; m2 零 diff×2 沿用; 审计按 20 文件集

## §1.659-D. 产物与链

- dbt mart 模型 + 前端 4 文件（api/page/layout/smoke-check）+ tests + **`docs/84-mart-flip-frontend-real-20260902.md`** + `docs/reports/mart_flip_frontend_20260902.md` + evidence（mart 行数/缺失省/UI 状态截图级 JSON 佐证）+ receipt 13 节
- 七字段原子 rev102→rev103→（交付时 rev104）; v3.4 沿用; amend-first 沿用; 双推三 ref 全等

## §1.659-E. 红线

红线 1-14 + U6 §5 沿用; **3 缺失省 UI/层禁补零**（"数据暂缺"状态）; mock 链文件保留; **24 里程碑不宣布**（本刀完成 ≠ M2/M6 PASS）; O1 仍 OPEN 零动作; fixture 4 锁值 + 既有 registry 行 SHA 零漂移; docs/81 零改动。

---

— End 658 审计 + 659 任务书 20260902 —

