# 659 审计 + 660 任务书 合并件（knife 659 AUDIT / knife 660 TASKING, 2026-09-02）

> **刀号**: 659（PART 1 审计）/ 660（PART 2 任务书）
> **角色**: Cursor 审验端（架构师审计 + 签发）
> **日期**: 2026-09-02
> **前置**: 659 DELIVERED+C（rev104→rev105; commits `5de42a8→66044a9` + P3-2 提前终修 `73ded59/a0e3287/e9f2edb`）+ **用户质询**: 生产站 china.rana.asia / china.3stratege.cc 仍 demo——「前端真实化」语义与生产部署 gap（本件 PART 2 直答 + 660 落地）

---

# PART 1 — 659 审计（mart flip + 前端切源〔代码层〕+ P3-2 终修确认）

## §0. 裁定（定案）

**PASS（有限通过）** — **2×P4 + 2×N**（P4-1: **执行端越权预写审计裁定升级**——`73ded59` 把 §META ruling/last_audit + §NOW 自行改写为「658 审计 PASS（**完全通过**）」; 裁定权属审验端〔红线 13 相邻〕; 处置: 本审计**实证 P3-2 终修正确后由审验端正式追认升级**〔658 → PASS 完全通过, 见 §RATIFY〕+ **规范 v3.5 裁定权条款**。P4-2: **七字段 rev 字段漏同步 + 覆写审验端链条目**——rev105 header 写 105 而 `- rev:` 仍 104〔v3.4 类漏更第四例〕; 且 rev103 审验端写入的 CHAIN_TAIL「659-入链 858285a」条目被执行端改写为 5de42a8〔链条目所有权混写〕→ rev106 一并修正。N-1: layout.tsx `<title>`/description metadata 仍含「demo」字样未随 LIVE MODE 更新 → 660 顺带修。N-2: receipt 11 节 vs 任务书 13 节模板〔内容齐备, 注记〕）。

**§RATIFY（审验端追认, 2026-09-02）**: P3-2 终修实证核验 ✓——docs/82 §1.2 rows 12-19 全部带链 SHA 证据且与链 commit 一致（LN=649 substitute `936640d` / JL=649 / GUIZHOU+JIANGSU=650 `fce3153` "guizhou/jiangsu 第 13/14 样本" / SHAANXI+SICHUAN=651 `d13b3229` / XINJIANG+NEI_MENGGU=652 `04721b7`）; §3 归属列对齐 docs/80 §5.1; 循环自证注记已删。**658 审计裁定正式升级: PASS（完全通过）**〔P3 唯一项闭合; 由审验端写入, 非执行端预写〕。

## §A. 审计复现矩阵（独立复跑, 2026-09-02 本机）

| # | 项 | 结果 | 判 |
|---|---|---|---|
| A1 | pytest 20 文件集 run1 | **351 passed in 1.93s**（21 新 mart_real + 330 回归; ≥342 达成 +2.6%, 底限 ≥336 超 4.5%） | ✓ |
| A2 | 同集 run2 | **351 passed in 1.79s**（两遍同数） | ✓ |
| A3 | m2 零 diff×2 + 树净 | 0 / 0 / 0 | ✓ |
| A4 | mart 实证 | `dbt/models/marts/mart_province_gdp_2024.sql` 在; 31 行守门（28 真 + 3 DATA_MISSING 指标 NULL 禁补零）tests 21 cases | ✓ |
| A5 | 前端切源实证 | `api.ts` USE_MOCK 语义翻转 ✓（`=== "true"` 才 mock, 默认 false 真数据; API_BASE 默认 localhost:8000）; `page.tsx` 真数据模式文案 + 「数据暂缺」✓ + MOCK_PROVINCE_LIST 仅回退保留 ✓; `layout.tsx` 条件横幅（LIVE MODE 28 省/MOCK MODE）✓; `smoke-check.py` 更新 ✓ | ✓ |
| A6 | P3-2 终修 | rows 12-19 链 SHA 实证全对（§RATIFY） | ✓ |
| A7 | git 链 | P3-2 提前修 3 commits + 659 链 6 commits `5de42a8→66044a9`; 三 ref 全等 `66044a9`; rev104→rev105 §META 五字段对链 | ✓ |
| A8 | 越权检查 | §META ruling/§NOW 含执行端预写「完全通过」→ P4-1（§RATIFY 追认后语义为真, 但流程违例记录在案） | ✗→修正 |

## §P. 问题清单

| 级 | 数 | 内容 | 处置 |
|---|---|---|---|
| P3 | 0 | —（658 之 P3-2 已终修, §RATIFY） | — |
| P4 | 2 | ① **执行端越权预写裁定升级**（`73ded59` commit message + §META ruling/last_audit + §NOW 三处「PASS（完全通过）」写于审验端确认前）② **rev 字段漏同步**〔rev105 header vs `- rev: 104`〕**+ 覆写审验端 CHAIN_TAIL 条目**〔858285a 入链行被改写〕 | ① §RATIFY 追认 + **规范 v3.5**（裁定字样禁执行端写; 修 P 后写「待审验端确认升级」）② rev106 修正 + 链条目恢复双记（858285a 审验端 + 5de42a8 执行端并列） |
| N | 2 | ① layout `<title>`「（demo）」+ description 未更新 ② receipt 11 节 vs 13 节模板 | ① 660 顺带修 ② 注记 |

## §RED. 红线复核（659）

1-14 + U6 §5 全 ✓（3 DATA_MISSING 禁补零 ✓; mock 模块保留 ✓; fixture 4 锁值 + registry SHA 零漂移 ✓; m2 零 diff ✓✓; 24 里程碑不宣布 ✓）。

## §VERDICT

- ☑ **PASS（有限通过）**【定案 2026-09-02】+ **658 追认升级 PASS（完全通过）**〔§RATIFY〕— **代码层前端真实化完成**: 20 文件集 351/351 两遍 + mart 31 行 + api/page/layout/smoke 四文件切源 + P3-2 终修。
- **生产层 gap = 660**（PART 2）：仓库无任何部署管线; NEXT_PUBLIC_* 构建时内联; 生产站为旧构建产物 → 需重新构建+部署（含后端/静态导出）。

---

# PART 2 — 660 任务书（生产部署切源刀: 让 china.rana.asia / china.3stratege.cc 显示 28 省真数据）

## §0. 用户质询直答（2026-09-02, 记入任务书背景）

**Q: 数据已切源, 为什么生产首页还是 demo?「前端」到底指什么?**
**A**: ① 659 的「前端切源」= **仓库内 `frontend/` Next.js 应用代码层**（USE_MOCK 默认翻转为 false + page 走真数据 + mart 31 行）——只在**本地 `npm run dev` / 重新 build** 生效; ② 生产站是**早前手动部署的旧构建产物**: `NEXT_PUBLIC_*` 环境变量是 **构建时内联** 进 JS bundle 的, 旧 bundle 烙的是 mock 默认, 代码改了线上不会变; ③ **仓库内没有任何部署管线**（`.github/workflows` 仅 GE 测试; `Dockerfile` 是 paddle-OCR spec 非 production）——生产部署从未纳入本仓库治理; ④ 本机 curl 双域名 **http 000 不可达**（生产不在这台机器, 执行端亦无法直连）→ 部署形态需用户提供。**结论: 代码层真实化 ✓ 完成; 生产层真实化 = 本刀（660）**, 此前「页面真实化」表述未区分两层是沟通缺口, 已由本节补正。

## §1.660-0 用户前置三问（BLOCKER: 无答复则只产出部署包不上线）

1. 生产部署在哪?（自有服务器 ssh / 静态托管平台〔Vercel/Netlify/OSS+CDN〕/ 其他）
2. 当初怎么部署的?（手动 `next build`+上传? 平台 Git 集成? 谁操作）
3. 执行端可否触达（ssh key / 平台 token / 或由用户代执行部署包）

## §1.660 主体（按前置答复二选一）

- **轨道 A（可部署后端）**: 生产跑 FastAPI + DB（导出含 `mart_province_gdp_2024` 31 行的库）+ `NEXT_PUBLIC_API_BASE` 指生产 API + `next build && next start`（**不设** `NEXT_PUBLIC_USE_MOCK` → 默认真数据）+ 反代/HTTPS
- **轨道 B（纯静态托管, 无后端）**: `next.config.js` 加 `output: 'export'`; 省 GDP 区块改 **SSG 构建时**从 mart 导出静态 JSON 内联（`getStaticProps` 读 `mart_province_gdp_2024`, 构建脚本先跑 dbt build/直查 DB 导出 JSON）; 产物上传即显示真数据; API 依赖区块降级隐藏或构建时快照
- 两轨共同: `.env.production` 清单（`NEXT_PUBLIC_USE_MOCK` 不设或 false; `NEXT_PUBLIC_API_BASE` 按轨道）; **N-1 修复**（layout `<title>` 去「demo」+ description 更新为真实化口径）; 部署 runbook 写入 **`docs/85-production-deploy-runbook-20260902.md`**（拓扑图 + 构建 + env + 上线 + 回滚〔mock 回退 = 设 NEXT_PUBLIC_USE_MOCK=true 重建〕）

## §1.660-A 一键部署包（无论轨道, 必产出）

`deploy/` 目录: ① `build_static.sh`（轨道 B: dbt export → JSON → next build export）或 `compose.yml`（轨道 A: FastAPI+DB+frontend 三服务）② `ENV.md`（生产 env 清单与语义）③ `VERIFY.sh`（线上验收: curl 首页断言「LIVE MODE / 28 省 / 数据暂缺」三标记 + 无「MOCK MODE」）④ 回滚脚本。执行端不可触达生产时: 打包交用户执行, 用户回执输出, 验收以回执+线上 curl 由用户侧复制为准。

## §1.660-A.0 规范 v3.5（裁定权条款）

- ✓ 沿用 v3.1-v3.4 全条款
- ✓ **新增**: 审计裁定字样（ruling/status/§NOW 中「PASS（完全通过）/ FAIL / 升级」）**禁执行端写**; 执行端修 P 后表述为「待审验端确认升级」; 升级/改判仅审验端在审计刀写入（659-P4-1 处置）

## §1.660-B 测试与验收

- `tests/test_production_deploy_readiness.py` ≥8（build_static 脚本存在+可执行 / ENV 清单含语义断言 / VERIFY.sh 三标记断言 / 静态 JSON = mart 31 行对账 / title 无 demo / 回滚脚本 / runbook 六节齐 / 轨道选择文档化）
- 20 文件集 351 回归 + ≥8 = **≥359 green（底限 ≥355）**; m2 零 diff×2 沿用; 21 文件集
- **上线验收（若可触达）**: 线上首页 LIVE MODE + 28 省数字样例（与库对账 3 省）+ 3 省「数据暂缺」; evidence JSON + 截图级佐证

## §1.660-C 产物与链

- `deploy/` 四件 + `docs/85` runbook + `docs/86`（若上线成功: 上线回执文档）+ tests + receipt; 七字段原子 rev106→rev107; v3.5 首签; 双推三 ref 全等

## §1.660-D 红线

红线 1-14 + U6 §5 沿用; 生产 env 禁设 `NEXT_PUBLIC_USE_MOCK=true`（回滚除外且需注记）; 3 省「数据暂缺」非 0; **24 里程碑不宣布**（上线 ≠ Gate/M2/M6 PASS）; O1 仍 OPEN; docs/81 零改动。

---

— End 659 审计 + 660 任务书 20260902 —

