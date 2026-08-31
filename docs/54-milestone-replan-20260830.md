# 54 — 里程碑重排（2026-08-30）

> 依据：PRD v0.1 第 13/14/16 章；`docs/00-project-assessment.md`；`docs/01-current-architecture.md`；`docs/02-target-architecture.md`；`docs/08-mvp-plan.md`；`docs/08b-strict-mvp.md`；2026-08-30 对照审计。
> 地位：**现行里程碑**（用户 2026-08-30 裁定 U1–U5 全部按建议批准）。覆盖 `docs/08` 剩余 Stage 排序与 `docs/08b` 周历；`docs/08` / `08b` 保留为历史基线。
> **不宣布 Gate / O1 PASS。**
> HEAD 快照：`9efac2d` · evidence pack 1004 · 江苏 HTML 样本链 11/15（不作为本计划进度口径）。

---

## 0. 为什么要重排

三份 Stage 0 文档把项目定义成「空仓库、自底向上建七层」；PRD 把首期可用版本定义成「国家—31 省—试点城市可查询闭环」。过去两周实际走的是 **Stage 2 lite 页面 + 统计局首页 SHA-lock**，进度数字（11/15、pack 1004、刀 600+）放大了完成度，但 **L2 observation 生产入库与 L5 真 series 仍未接通**。

这直接违反：

- PRD 1.3 / `docs/00` 红线 5：**不以抓取网页数作为完成标准**
- `docs/02` §8：Stage 1 重点是 **L1 + L2 + L5**，不是 L7 演示壳
- `docs/08b`：唯一研究问题是 **2024 年 31 省 GDP 与官方口径一致率**，不是首页快照链
- PRD 16.1：**Gate 2 = 采集质量**（原表、解析值、单位、脚注、OCR），不是 5 省 10 城页面

`docs/01` 仍写「空仓库」；`docs/00` §5 仍写「6 个顶层目录」。两者都已过时，M0 必须刷新，不能继续当现状图。

---

## 1. 文档冲突（必须先对齐口径）

| 来源 | Stage 1 | Stage 2 | 「Gate 2」含义 | Next.js |
|---|---|---|---|---|
| **PRD 13 / 16** | 国家+31 省数据底座 3–4 周 | 试点省/市监测 4–6 周 | **采集质量** | 产品页（7.x），不绑定 Stage 号 |
| **docs/02** | L1 原始归档 + L2 标准化 + L5 API | 调度/监测 + 试点地市；L0–L4 齐 | 未用 Gate 2 这个名字 | **Stage 3+ / 决策表写 Stage 4+** |
| **docs/08** | 连接器 + Gate 1「可查询」 | **治理观察 UI**；Gate 2 = 5 省 10 城页 | 被改写成产品演示 | Stage 2 主交付 |
| **docs/08b** | 8–12 周只做一个 GDP 研究问题 | 不自动进入 | Gate 1 = W8 数据验收 | 仅 `/research/q1-2024-gdp` |
| **实际（2026-08-30）** | 连接器骨架；ingest 允许 PARTIAL（FK 未解析） | lite 页已交；真数据未接 | 评审包草稿，未 PASS | 10 路由 + 公网 mock 预览 |

**本计划选定：** 阶段定义以 **PRD 第 13 章** 为准；分层建设以 **docs/02** 为准；近端验收问题以 **docs/08b** 为准；`docs/08` 的「Gate 2 七条页面」降级为 **产品壳评审（Product Shell Review）**，不再叫 Gate 2。

PRD Gate 编号恢复为：

| Gate | PRD 16.1 | 进入条件（本计划） | 现状 |
|---|---|---|---|
| 0 | 范围与架构 | Stage 0 文档 + 四类 spike | 历史 CLOSED（2026-08-24） |
| 1 | 数据模型 | 地域版本可用、指标口径不自动合并、来源/修订完整；至少 1 条 observation 一跳回 SHA **且 SHA=文件字节** | OPEN |
| 2 | 采集质量 | 抽查原表 vs 解析值、单位、脚注；OCR 按来源单报或显式 BLOCKED | OPEN（HTML 首页 ≠ 原表） |
| 3 | 分析方法 | 比较组、模型假设、缺失值、因果措辞；docs/10 §3.2–3.4 从 xfail 实做 | 未开始 |
| 4 | 官员与政策 | 不把活动当结果；任期只展示重合 | schema/demo only |
| 5 | AI / Agent | 来源覆盖、只读权限、幻觉；DSH 非前置 | 未开始 |
| 6 | 产品与发布 | 性能、更新失败告警、回滚、可理解性 | 预览存在，非发布 |

---

## 2. 当前架构（刷新 docs/01 用）

对照 `docs/02` 七层，**不是空仓库**：

| 层 | 目标（docs/02） | 现状 | 缺口 |
|---|---|---|---|
| L0 | source_registry 路由 | registry **17 数据行**；4 类 spike + 11 份统计局首页 HTML | 首页登记 ≠ 可解析统计表 URL |
| L1 | MinIO/OSS，raw+sha256 不可变 | `data/seed_archives/*.html` + spikes 样本；无对象存储 | 无 WORM；registry SHA `a7e4029d` 与 `sample.html` 字节 `dea13b8a` 不一致 |
| L2 | Postgres+PostGIS；observation 真值 | `schema/01-core.sql` + migrations 001–014；docker-compose 仅 **db** | NBS 连接器明确 **No HTTP**、observation **FK deferred → PARTIAL**；无 2001–今年度序列 |
| L3 | Polars/DuckDB + model_spec | dbt **18** SQL；mart 1 行真 SHA pilot，其余 demo | 无派生指标生产跑批 |
| L4 | pgvector | 无 | 正确延后 |
| L5 | FastAPI 只读 + source/vintage | `/api/indicator/{id}/series` 等已交，测在 `cegr_test` | 前端默认 `NEXT_PUBLIC_USE_MOCK=true`，不读真 series |
| L6 | 只读 Agent | 无 | 正确延后 |
| L7 | Next.js 工作台 | 5 省页 + 10 城 SSG + 四轨 `/public-extracts` + 公网预览 | 演示壳；与 L5 未接 |
| 横切 | Prefect、Grafana、CI | pytest 53 文件；`ge-check.yml`；无 Prefect/MinIO | 调度文件 `00-EXEC-QUEUE.md` ~472 KB 不可扫读 |

已完成且**应保留**：四层信息模型、禁词守门、SHA mismatch 闸、`is_demo` 分离、六段链/七维卡 UI、公开源限速与禁绕过验证码。

已完成但**不再作为里程碑进度**：江苏/湖南统计局首页 SHA-lock、四轨 deeplink/CSV/overview 页面镀铬、刀链计数、pack artifact 数。

---

## 3. 近端北极星（唯一）

沿用 `docs/08b` §1.2，允许按咨询场景缩到可执行切片：

> **先回答：2024 年（必要时再回补 2001 起）国家 + 31 省 GDP（及三次产业增加值，能拿到则做）是否与官方公布值在声明口径下一致？每条 observation 必须一跳回到 source_document，且 `file_hash_sha256` 等于归档文件字节。**

咨询常用的「江苏近 5 年 GDP」是 **同一管线的第二条查询**，不得另开首页爬取项目。

达不到则 Gate 1 / PRD 14.1 **不得**宣布通过。

---

## 4. 停止 / 保留 / 启动

**停止（立即）**

- 以「江苏样本 n/15」或省统计局**首页** HTML 为 O1/Stage 进度（含规划中的 626 广东首页刀，除非用户明示只要源发现归档）。
- 继续给 `/public-extracts` 加入口、筛选、CSV、deeplink。
- 把 docs/45「Gate 2 七条」当成 PRD Gate 2。
- 为全绿 pytest 放宽 SHA 闸或把 live SHA 铺到无对应字节的行。

**保留**

- 现有 11 份 HTML 归档：降级为 **L0 源发现线索**，写入 registry `purpose_note`，不计入覆盖率。
- Next.js 省/城壳、六段链、七维卡、禁词、INFERENCE 标签。
- FastAPI 只读边界、dbt 模型形状、migrations、`is_demo`。
- OCR：真实中文扫描未闭环前保持 **BLOCKED-DEFERRED**，禁止合成 PDF 冒充 Gate 2。

**启动（M0 起）**

- 生产路径：L0 表 URL → L1 按字节归档 → L2 observation（FK 解析成功，禁止以 PARTIAL 为完成）→ L5 series → L7 **一页**关 mock。
- 进度 KPI：`observation` 行数（非 demo）、`geo×indicator×year` 覆盖率 + `missing_reason`、抽样 vs 原表一致率；**禁止** HTML 文件数。

---

## 5. 里程碑（自 2026-08-30 起）

总日历：**约 12 周到首个可用数据闭环（M2 末）**；试点监测 M3 再 4 周；人物政策 M4 与分析 Agent M5 不预支。对齐 PRD「8–12 周首个可用版本」= **M0–M2**，不是 M0–M5。

### M0 — 冻结与口径复位（3–5 个工作日）

**对应**：刷新过时的 docs/00 §5、docs/01；过程治理。不进功能大实现。

| ID | 任务 | 完成条件 |
|---|---|---|
| M0.1 | 用户裁定：626 首页刀停 / 仅源归档 / 改接 observation | 书面裁定进本文件 §8 |
| M0.2 | 重写 `docs/01-current-architecture.md` 为上表现状 | 与仓库 `rg --files` 一致 |
| M0.3 | 修补 NATIONAL_BULLETIN：registry SHA = 归档文件字节，或拆成 live 候选行 + sample 行 | 连接器测试与 registry 同一 SHA |
| M0.4 | EXEC-QUEUE 压成 §CURRENT 一行 + 链尾 ≤5 刀 | 主文件 < 30 KB 或拆归档 |
| M0.5 | 进度看板改为覆盖率，不再报 11/15 | 任务书模板改 KPI |

退出：用户确认北极星与试点省名单（§8）。**不叫 Gate。**

### M1 — 第一条可查询序列（2 周）≈ PRD 阶段 1 切片 / docs/02 L1–L2–L5 / 08b W4 缩微

> **任务拆分（2026-08-31）：`docs/55-m1-first-series-task-breakdown-20260831.md`**（T0–T7；2026-08-31 全勾 T0–T7）。指定表 = 湖北 `hubei_2026_06.xlsx` GDP 行。
> **执行回执：629 (`reviews/stage0-gate0-rework-2026-08-23/629-stage0-cc-m1-cd-t4-t7-receipt-20260831.md`)** — M1-c+d（T4+T5+T6+T7）一份回执集中摄影；非 Gate / O1 / M1 PASS。

| ID | 任务 | 完成条件 |
|---|---|---|
| M1.1 | NBS（或省级年鉴）**一张官方表**入库：raw 字节、source_document、observation 全部 SUCCESS（非 PARTIAL） | pytest：SHA(file)==registry；observation≥1；一跳回源 |
| M1.2 | 指标定义 + geo_entity 种子足够支撑该表（含单位、口径、统计期≠发布日） | 同名不同口径不合并 |
| M1.3 | `GET /api/indicator/{id}/series` 返回上表真值 + source_id + vintage | 不依赖 mock |
| M1.4 | 前端 **一个** 页面（建议全国或江苏）`USE_MOCK=false` 渲染该 series，图表可点回证据 | 公网预览若仍 mock 须标明「非 M1 验收面」 |

退出候选：**Gate 1 有限通过**（数据模型 + 单表闭环）。仍须用户裁定，不得自动 PASS。

### M2 — 国家 + 31 省 GDP 年度覆盖（3–4 周）≈ PRD 阶段 1 主体 / 08b 研究问题 / PRD 14.1 切片

> **任务拆分（2026-08-31）：`docs/56-m2-gdp-coverage-task-breakdown-20260831.md`。** 首刀 **631 = M2-a**（geo + inventory）。  
> **前置：** 用户 2026-08-31 裁定 **M1 有限通过**（≠ Gate 1 PASS）。

| ID | 任务 | 完成条件 |
|---|---|---|
| M2.1 | 2024 年 31 省 GDP 入库；缺省写 `missing_reason`，不补零 | 覆盖率报告可生成 |
| M2.2 | 能拿到则三次产业增加值；拿不到则登记缺口 | 不假装齐 |
| M2.3 | 跨源核对（国家发布 vs 省年鉴/公报）：差异规则按 08b（&lt;0.5% 一致，否则 QUARANTINED） | 31 行核对表 |
| M2.4 | 回补 2001 年起核心年度 **仅 GDP 族**，目标覆盖率向 95% 逼近 | 达不到则列不可得项，不降门槛装 PASS |
| M2.5 | `/research/q1-2024-gdp`（或等价页）回答 08b 问题 + 一跳回源 + caveat | 公开访问无 500 |

退出候选：**PRD 14.1 数据切片** + 产品最小页。OCR 仍可 BLOCKED。这是「首个可用版本」的数据含义。

### M3 — 试点监测（4 周）≈ PRD 阶段 2 / docs/02 Stage 2（调度+试点地市）

前置：M2 退出或用户书面接受「先 1 省深挖」。

| ID | 任务 | 完成条件 |
|---|---|---|
| M3.1 | 试点：默认 **江苏深挖** + 已有 UI 的广东/浙江/山东/四川中选 2 省；每省 2–4 城 **公报或年鉴表 → observation** | 不是首页 HTML |
| M3.2 | L1 对象存储（MinIO 本地，与 docs/02 一致）或等价 WORM 目录规范 | 覆盖不改字节 |
| M3.3 | 发布日历 + ingest_run 失败可见（Grafana 或文档化 cron + 日志；Prefect 可本里程碑引入） | 更新失败有告警（PRD 14.2） |
| M3.4 | 既有城页接 L5/mart **真行**；mock 仅测试夹具 | CityPage 默认非 mock |
| M3.5 | 采集抽查：每源 ≥3 行原表对照 | **这才是 PRD Gate 2** |

人物/政策 demo 表保持 is_demo，不在 M3 假装 S2.1-full 完成。

### M4 — 官员 / 政策 / 项目 / 承诺（6–8 周）≈ PRD 阶段 3 / docs/02 Stage 3

仅在 M3 Gate 2 有限通过后排期。公开任免与任期、政府工作报告、预算与项目状态；时间线只展示重合。UI 七维卡必须标 INFERENCE/JUDGMENT。禁止总分。docs/08 旧 Gate 2 七条里页面项可在此对照「产品壳+真数据」复核，名称仍不叫 Gate 2。

### M5 — 治理观察方法 + Agent 评估（6–10 周）≈ PRD 阶段 4 / docs/02 Stage 4

同类匹配、条件化相对表现、docs/10 §3.2–3.4 实做（现 xfail）。DSH 仅 sidecar 评估（doc 07），不进 ETL。全国地级/区县扩展仍是 PRD 阶段 5，**不设一次性完成日**。

---

## 6. 依赖与回滚

```
M0 口径复位
 └─ M1 单表 L1→L2→L5→L7
      └─ M2 31 省 GDP 族 + 08b 页面
           └─ M3 试点城 observation + PRD Gate 2
                ├─ M4 人物/政策/项目
                └─ M5 方法 + Agent（可与 M4 部分并行，但不得早于 M2）
```

| 触发 | 动作 |
|---|---|
| M1 仍只能 PARTIAL / SHA 双真相 | 停 M2；修 FK 与 registry；不扩源 |
| 2024 年 31 省 GDP 可得省 &lt; 20 且无 missing_reason | M2 不得退出 |
| OCR 无真实中文扫描 | 保持 BLOCKED；不挡 M1–M2 非 OCR 路径 |
| 范围再次滑向「再锁一个首页」 | R05；回到 M0.5 KPI |
| 任何官员总分 / LLM 改 observation.value | 立即回滚该提交 |

---

## 7. 与旧计划的关系

| 旧项 | 新归属 |
|---|---|
| docs/08 S1.4–S1.7「连接器存在即完成」 | 作废；完成 = observation SUCCESS + 可查询 |
| docs/08 Gate 2 七条 | **Product Shell Review**，挂在 M3 末对照，不叫 Gate 2 |
| docs/08 S2.7–S2.10 lite UI | 已提前交付；M1–M3 只接数据，不再镀铬 |
| 江苏样本 11/15 | M0 起不作为里程碑；可作 L0 线索清单附录 |
| docs/45 / docs/50 Gate 2 草稿 | 冻结；M3 末按 PRD 16.1 重开采集质量包 |
| docs/02「Next.js Stage 4+ 才引入」 | 已发生偏差（Stage 2 lite 已引入）；**承认偏差**，后续 L7 只消费 L5 |
| docs/08b W3「文档冻结 00–11」 | 失败（45–53 + 刀链）；M0 起治理文档只追加本系列与 CURRENT 一行 |
| Grafana / Prefect | 从「Stage 1 必做」挪到 **M3**（与 docs/02 Stage 2 一致） |
| paddle OCR 生产化 | 不进 M1–M2 关键路径 |

---

## 8. 用户裁定（2026-08-30 全部按建议批准）

| # | 问题 | 裁定 |
|---|---|---|
| U1 | 是否停止 626 及后续「省统计局首页 SHA-lock」刀？ | **停止作为里程碑**；已落档 HTML 留作 L0 线索。626 tasking **CANCELLED**，不得执行。 |
| U2 | 近端唯一研究问题是否即为 08b（2024 年 31 省 GDP 一致率）？ | **是**。江苏近 5 年 GDP 为 M2 的第二条查询，同一管线。 |
| U3 | 试点省 | **江苏深挖 + 广东 + 浙江**。河南/辽宁按数据可得性后补。山东/四川前端页保留，M3 不优先扩城。 |
| U4 | 商业年鉴库 | **M1–M2 不买**；M2 末再评。 |
| U5 | 本文件升为现行里程碑？ | **是**。覆盖 `docs/08` 剩余排序。 |

本裁定**不构成**任何 Gate / O1 PASS。

### M0 落地记录（同日）

| ID | 状态 | 说明 |
|---|---|---|
| M0.1 | 已做 | 626 CANCELLED；队列 KPI 改为覆盖率 |
| M0.2 | 已做 | `docs/01-current-architecture.md` 按现网七层重写 |
| M0.3 | 部分 | **不改** `registry.csv` 前 11 行（刀链 SHA 锁）。双真相写入 docs/01 与本表：live `a7e4029d` / 180165 ≠ `sample.html` 字节 `dea13b8a`。CSV 拆行放到 **M1.1** |
| M0.4 | 已做 | 旧队列归档为 `00-EXEC-QUEUE.archive-rev46-20260830.md`；现行队列压成 §CURRENT |
| M0.5 | 已做 | 进度口径见下；禁止再报 11/15 为 Stage 进度 |

**进度 KPI（唯一）：** `cegr.observation` 非 demo 行数；`geo × indicator × year` 覆盖率（缺省必须有 `missing_reason`）；抽样 vs 原表一致率。禁止用 HTML 文件数、刀号、pack artifact 数当作完成标准。
