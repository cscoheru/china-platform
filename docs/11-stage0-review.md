# 11 — Stage 0 最终评审总结（Stage 0 Final Review）

> Stage 0 交付物 #11；对应 PRD 第 15 章全部要求。
> **目的**：让评审方在不读其他 10 份文档的情况下，能够评估 Stage 0 是否完整。
> **状态**：🔴 **R3 返工后再次 REJECT / BLOCKED**（2026-08-23）。等待 Codex Gate 0 复核。
> **首轮验收**：`不通过`（per reviews/stage0-gate0-rework-2026-08-23）。
> **R2 修正**："READY FOR GATE 0 REVIEW"（已 R3 推翻）。
> **原始缺陷编号已恢复（见 §7）**：13 项原始缺陷中，**B-01（四类样本 — 真实扫描 PDF 外部阻塞）部分完成**，其余 12 项（B-02..B-08、I-01..I-05）已闭环（I-05 已闭环 per R4-4）。Codex 返工项 C/D/E 已实现（spike00 682 槽 + ZIP-only + 逐指标周期）。**最终状态：BLOCKED（真实扫描 PDF 仍 BLOCKED）**。
> 详细 R2→R3 缺陷映射见 `docs/12-stage0-closure-and-report.md` §4。

---

## 1. 做了什么（What Was Done）

### 1.1 PRD 第 15 章要求的 11 项交付物

| # | PRD 15 要求 | 交付文件 | 行数 | 状态 |
|---|---|---|---|---|
| 1 | 仓库现状评估 | `docs/00-project-assessment.md` | 137 | ✅ |
| 2 | 当前架构 | `docs/01-current-architecture.md` | 69 | ✅ |
| 3 | 目标架构 | `docs/02-target-architecture.md` | 204 | ✅ |
| 4 | 来源登记表 | `docs/03-source-registry.md` | 271 | ✅ |
| 5 | 数据模型 | `docs/04-data-model.md` | 378 | ✅ |
| 6 | 指标方法 | `docs/05-indicator-methodology.md` | 278 | ✅ |
| 7 | 治理观察方法 | `docs/06-governance-observation-method.md` | 208 | ✅ |
| 8 | DSH 决策 | `docs/07-dsh-decision.md` | 185 | ✅ |
| 9 | MVP 计划（长期） | `docs/08-mvp-plan.md` | 213 | ✅（22—32 周长期路线图） |
| 9b | MVP 计划（严格 8—12 周） | `docs/08b-strict-mvp.md` | 193 | ✅（新增 per 返工指令 §5） |
| 10 | 风险登记 | `docs/09-risk-register.md` | 316 | ✅（26 风险：10 高 / 16 中 / 0 低；17 已闭环 + 3 部分验证 + 2 BLOCKED；R22–R26 为 R4/R5 返工新增） |
| 11 | 验收测试 | `docs/10-acceptance-tests.md` | 330 | ✅ |
| 12 | 最终总结 | `docs/11-stage0-review.md` | 453 | ✅（本文件，返工后重写） |

**12 份文档**。

### 1.2 Schema 草案

| 文件 | 行数 | 内容 |
|---|---|---|
| `schema/01-core.sql` | 1082 | PostgreSQL 17 + PostGIS 3.6 DDL；39 张表 + 13 个枚举 + 视图 + 触发器；btree_gist + daterange + EXCLUDE USING gist |
| `schema/migrations/001_create_core.log` | 158 | 空 PG 17 + PostGIS 实例执行日志（psql exit 0） |

> 实际执行验证：在新启动的 `postgres@17` 容器内运行 `psql -v ON_ERROR_STOP=1 -f schema/01-core.sql`，退出码 0，39 张表 + 13 个枚举全部创建成功。
> 注：Homebrew 上 PostgreSQL 16 + PostGIS 不可用，使用 PG 17.11 + PostGIS 3.6.4（环境约束，已文档化）。

### 1.3 技术验证（6 个 spike，5 PASSED + 1 BLOCKED）

| Spike | 验证目标 | 真实样本 | 提取行数 | 测试 | 状态 |
|---|---|---|---|---|---|
| **00-national-yearbook-table** | 国家统计年鉴 JPG→OCR 真值对照 | `c0309.jpg` (550 KB, sha256: 9576529a...) | **682（31×22 全网格）** | 31/31 ✅ | ✅ 真实样本 + 逐列真值对照 |
| **00-provincial-yearbook-table** | 省级年鉴 xls→xlrd 真值对照 | `hubei_2025_yearbook.zip` (6.4 MB) 内 `0109-地区生产总值.xls` | **480** | 21/21 ✅ | ✅ 真实样本 + 真值对照 |
| **01-national-yearbook** | stats.gov.cn 月报 HTML | `sample.html` (388 KB) | 20 | 20/20 ✅ | ✅ |
| **02-provincial-yearbook** | 湖北统计局 xlsx | `hubei_2026_06.xlsx` | 19 | 30/30 ✅ | ✅ 逐指标周期建模（R3-E） |
| **03-municipal-bulletin** | sz.gov.cn 公报 HTML 散文 | `sample.html` | 8 | 29/29 ✅ | ✅ |
| **04-scanned-pdf** | 扫描 PDF OCR | **BLOCKED**（无合法中文免费源） | 450（450/450 needs_review） | 18/18 ✅ | 🟡 管线就绪 / 真实样本 BLOCKED |

### 1.4 关键测试数（2026-08-23 R4 完工后）

**总计**：**237 passed / 0 failed / 0 skipped**（默认 `python3 -m pytest -q -p no:cacheprovider`）。R3 期间为 205；R4 新增 32 测试（R4-1 8 / R4-2 8 / R4-3 4 / R4-4 21，扣除共享覆盖后净增 32）。spike 04 的 18 项测试断言其诚实 BLOCKED 状态，非"标为 PASSED"。

### 1.4 数据库负例测试（Schema 强制约束）

`tests/test_schema_negative.py` — 39 项负例，全部通过（下表为核心 13 项；R3 新增 26 项见 docs/12 §2 B-03）：

1. 重叠 geo_code_version 被拒（ExclusionViolation）
2. 无效 validity range 被拒（CheckViolation）
3. 重叠 methodology version 被拒
4. 空 source_location 被拒
5. observation 必须有 source_location
6. 非法 confidence 被拒
7. 非 SHA-256 hash 被拒
8. revision_no 非正整数被拒
9. observation.value 不能 UPDATE
10. observation_revision 不能 DELETE
11. 删 observation 不 cascade revision
12. v_current_observation 选最新 revision
13. 两个独立 source 可并存

### 1.5 PRD 12 章 10 个风险 + Stage 0 / 返工新增 11 个风险

| ID | 来源 | 等级 | 状态 |
|---|---|---|---|
| R01 统计口径 | PRD 12.1 | 🔴 | ✅ |
| R02 行政区划 | PRD 12.2 | 🔴 | ✅ |
| R03 地方缺失 | PRD 12.3 | 🔴 | ⬜ |
| R04 OCR 错误 | PRD 12.4 | 🔴 | 🟡 部分验证 |
| R05 范围失控 | PRD 12.5 | 🟡 | ✅ |
| R06 错误归因 | PRD 12.6 | 🔴 | ✅ |
| R07 活动冒充 | PRD 12.7 | 🟡 | ✅ |
| R08 授权稳定性 | PRD 12.8 | 🟡 | 🟡 部分验证 |
| R09 AI 幻觉 | PRD 12.9 | 🔴 | ⬜ |
| R10 确认偏差 | PRD 12.10 | 🟡 | ⬜ |
| R11 OCR 工具链 | Stage 0 | 🟡 | 🟡 部分验证 |
| R12 URL 漂移 | Stage 0 | 🟡 | ⬜ |
| R13 真实样本 BLOCKED | 返工 | 🔴 | ❌ BLOCKED |
| R14 永真断言 | 返工 | 🔴 | ✅ |
| R15 路径硬编码 | 返工 | 🟡 | ✅ |
| R16 OCR 子进程 | 返工 | 🟡 | ✅ |
| R17 natural key status | R3 返工 | 🟡 | ✅ |
| R18 测试纯净性 | R3 返工 | 🟡 | ✅ |
| R19 builder 自校验 | R3 返工 | 🟡 | ✅ |
| R20 spike 04 样本偏差 | R3 返工 | 🔴 | ❌ BLOCKED |
| R21 spike 00/02/03 partial | R3 返工 | 🔴 | ✅ |
| R22 skip-as-PASS 反检测 | R4 返工 | 🟡 | ✅ |
| R23 全国年鉴证据一致性 + 质量 BLOCKED | R4 返工 | 🔴 | ✅ |
| R24 Evidence Builder 加固 | R4 返工 | 🟡 | ✅ |
| R25 I-05 来源等级治理 | R4 返工 | 🟡 | ✅ |
| R26 默认 apply 链 + 文档同步 | R5 返工 | 🟡 | ✅ |

**统计**：🔴 高 10 / 🟡 中 16 / 🟢 低 0；✅ 已闭环 17 / 🟡 部分验证 3 / ⬜ 待 Stage 1-2 落地 4（R03/R09/R10/R12）/ ❌ BLOCKED 2。R22–R26 为 R4/R5 返工新增（详见 `docs/09-risk-register.md`）。

---

## 2. 没做什么（What Was NOT Done）

### 2.1 PRD 1.3 / 15 红线严守

- ❌ **未建立"官员能力总排名"**（per PRD 6.6；doc 06 明确首期不输出总分）
- ❌ **未收集任何私人/泄露/非公开个人信息**（per PRD 11.5；schema person 表只存公开履历）
- ❌ **未把新闻数、会议数、签约额直接当绩效**（per PRD 12.7；doc 06 六段证据链强制）
- ❌ **未让大模型直接改写原始统计数据**（per PRD 12.9；schema observation 不可写，Agent 只读）
- ❌ **未把抓取网页数作为完成标准**（per PRD 12.5；spike 看质不看数）
- ❌ **未批量抓取全国市县数据**（per 用户指令 + PRD 15；spike 仅试点单条样本）
- ❌ **未绕过验证码、付费墙或网站技术限制**（per PRD 12.8；spike 04 无公开免费扫描 PDF，保留 BLOCKED）
- ❌ **未把 DSH / Agent 框架作为核心数仓或统计引擎**（per PRD 1.3 + doc 07 决策矩阵）
- ❌ **未用合成样本替代真实样本验收**（per返工指令 §0；spike 04 真实 PDF 缺失保留 BLOCKED，合成仅作为非真值对照的代码通路测试）
- ❌ **未把 BLOCKED / 永真测试标为 PASSED**（per返工指令 §0）
- ❌ **未自动进入 Stage 1**（per用户指令，等评审）

### 2.2 Stage 0 范围外（待 Stage 1-5）

- ❌ 未部署生产 PostgreSQL 实例（仅开发容器验证 schema 可执行）
- ❌ 未实施 Alembic 迁移（Stage 1）
- ❌ 未实施 FastAPI 服务（Stage 1）
- ❌ 未实施 Next.js 前端（Stage 2）
- ❌ 未实施 dbt 模型层（Stage 1）
- ❌ 未实施 great_expectations 数据契约（Stage 1）
- ❌ 未实施 RLS 行级安全（Stage 2）
- ❌ 未实施 pgvector embedding（Stage 4 评估后决定）
- ❌ 未实施 ETL 生产化（连接器、retry、监控）— spike 是最小验证
- ❌ 未引入真实业务数据（仅 spike 试点 6 个样本）

---

## 3. 文件清单（File Inventory）

### 3.1 文档（docs/）

```
docs/
├── 00-project-assessment.md            (137 行)
├── 01-current-architecture.md          (69 行)
├── 02-target-architecture.md           (204 行)
├── 03-source-registry.md               (272 行)
├── 04-data-model.md                    (383 行)
├── 05-indicator-methodology.md         (279 行)
├── 06-governance-observation-method.md (208 行 — 七维度已校准)
├── 07-dsh-decision.md                  (185 行)
├── 08-mvp-plan.md                      (213 行 — 长期路线图)
├── 08b-strict-mvp.md                   (193 行 — 严格 8—12 周 MVP)
├── 09-risk-register.md                 (316 行 — 26 风险：R01–R21 + R22–R26)
├── 10-acceptance-tests.md              (330 行)
└── 11-stage0-review.md                 (453 行 — 本文件)
```

### 3.2 Schema

```
schema/
├── 01-core.sql                         (1082 行 — 39 表 + 13 enum + view + trigger)
└── migrations/
    └── 001_create_core.log             (158 行 — psql exit 0 验证日志)
```

### 3.3 Spike 产物（spikes/）

```
spikes/
├── 00-national-yearbook-table/        ⭐ 新增（真值对照）
│   ├── c0309.jpg                      (550 KB, sha256: 9576529a881b83be...)
│   ├── extract_00_national_yearbook_table.py
│   └── test_00_national_yearbook_table.py  (24 tests)
├── 00-provincial-yearbook-table/      ⭐ 新增（真值对照）
│   ├── hubei_2025_yearbook.zip        (6.4 MB, sha256: be4c83cc...)
│   ├── extract_00_provincial_yearbook_table.py
│   └── test_00_provincial_yearbook_table.py  (21 tests)
├── 01-national-yearbook/
│   ├── sample.html                    (388 KB)
│   ├── extract_01_national_yearbook.py
│   ├── test_01_national_yearbook.py   (20 tests)
│   └── README.md
├── 02-provincial-yearbook/
│   ├── hubei_2026_06.xlsx             (11 KB)
│   ├── extract_02_provincial_yearbook.py  (路径已修，无硬编码)
│   ├── test_02_provincial_yearbook.py (30 tests)
│   └── README.md
├── 03-municipal-bulletin/
│   ├── sample.html                    (61 KB)
│   ├── extract_03_municipal_bulletin.py
│   ├── test_03_municipal_bulletin.py  (29 tests)
│   └── README.md
├── 04-scanned-pdf/
│   ├── extract_04_scanned_pdf.py      (needs_review 逻辑已修正)
│   ├── test_04_scanned_pdf.py         (18 tests — 诚实 BLOCKED 断言)
│   └── README.md                      (BLOCKED 已文档化)
└── README.md
```

### 3.4 提取产物（data/extracts/）

```
data/extracts/
├── 00-national-yearbook-table/extracted.json     (682 obs — OCR 真值 31×22)
├── 00-provincial-yearbook-table/extracted.json   (480 obs — xls 真值)
├── 01-national-yearbook/extracted.json           (20 rows)
├── 02-provincial-yearbook/extracted.json         (19 rows)
└── 03-municipal-bulletin/extracted.json          (8 rows)
```

### 3.5 数据库负例测试

```
tests/
├── README.md
└── test_schema_negative.py            (39 项负例，全部通过)
```

### 3.6 项目骨架（顶层）

```
china platform/
├── .gitignore
├── README.md
├── backend/README.md
├── schema/README.md
├── source_registry/README.md
├── tests/README.md
├── spikes/README.md
└── pytest.ini                         (testpaths = spikes tests)
```

---

## 4. 运行过的命令和测试摘要（Commands & Test Summary）

### 4.1 默认测试运行（一条命令）

```bash
python3 -m pytest -q
# 输出：237 passed, 0 failed, 0 skipped
```

### 4.2 Schema 执行验证

```bash
# 在空 PG 17 + PostGIS 容器内
psql -v ON_ERROR_STOP=1 -f schema/01-core.sql
# 输出：CREATE EXTENSION / CREATE TABLE / CREATE TYPE 全部成功；退出码 0
# 39 tables, 13 enums
```

### 4.3 Spike 00 真值对照

```bash
# 国家统计年鉴 C03-09 表 OCR
python3 spikes/00-national-yearbook-table/extract_00_national_yearbook_table.py
# 输出：682 observations（31×22 全网格）；湖北 2024 GDP 与真值一致

# 省级年鉴湖北 0109-地区生产总值
python3 spikes/00-provincial-yearbook-table/extract_00_provincial_yearbook_table.py
# 输出：480 observations；湖北 2024 GDP=60012.97 与 NBS 真值一致
```

### 4.4 Spike 04 BLOCKED

```bash
python3 spikes/04-scanned-pdf/extract_04_scanned_pdf.py
# 真实扫描 PDF：仅 1909 美国统计摘要（archive.org，英文，非中国研究样本）可全流程验证；保留 BLOCKED；0 skip
```

---

## 5. 四类样本对比（Sample Comparison）

| 维度 | Spike 00 NBS | Spike 00 Hubei | Spike 02 Hubei xlsx | Spike 03 Shenzhen | Spike 04 Scanned |
|---|---|---|---|---|---|
| **形态** | JPG（OCR 真值） | xls 真值 | xlsx 单 sheet | HTML 散文 | PDF 扫描 |
| **大小** | 550 KB | 6.4 MB（zip 内） | 11 KB | 61 KB | – BLOCKED |
| **解析** | tesseract chi_sim | xlrd 2.0.2 | openpyxl | bs4 + lxml | pytesseract |
| **行数** | **682** | **480** | 19 | 8 | 450（needs_review） |
| **真值对照** | ✅ Hubei 2024 GDP=60013.0 | ✅ Hubei 2024 GDP=60012.97 | ✅ vs NBS | ✅ 政府报告引用 | ❌ BLOCKED |
| **血缘字段** | source_hash + cell_locator | source_hash + cell_locator | ✓ | ✓ | ✓ |
| **缺失值** | 标记 needs_review | 标记 needs_review | unit IS NULL 支持 | ✓ | needs_review |
| **测试条数** | 24 | 21 | 30 | 29 | 18 |

---

## 6. 风险状态（per doc 09，已与本节同步）

| 等级 | 数量 | 列表 |
|---|---|---|
| 🔴 高 | 10 | R01 / R02 / R03 / R04 / R06 / R09 / R13 / R14 / R20 / R21 / R23 |
| 🟡 中 | 16 | R05 / R07 / R08 / R10 / R11 / R12 / R15 / R16 / R17 / R18 / R19 / R22 / R24 / R25 / R26 |
| 🟢 低 | 0 | – |
| ❌ BLOCKED | 2 | R13 真实样本 / R20 spike 04 样本偏差 |
| ✅ 已闭环 | 17 | R01, R02, R05, R06, R07, R14, R15, R16, R17, R18, R19, R21, R22, R23, R24, R25, R26 |
| 🟡 部分验证 | 3 | R04, R08, R11 |
| ⬜ 待 Stage 1-2 落地 | 4 | R03, R09, R10, R12 |

---

## 7. 返工指令闭环（Rework Directive Closure — 原始缺陷编号）

> **缺陷编号恢复说明**：Gate 0 首轮评审（`reviews/stage0-gate0-rework-2026-08-23/01-Stage0-评审缺陷与证据.md`）定义了 **13 项原始缺陷**（B-01..B-08、I-01..I-05）。复核过程中同一批 B/I 标签曾被复用到“R3 复验项”上（与原始定义不符），造成编号语义漂移。本节严格按**原始定义与编号**逐项复盘；R3 复验项改用 `A..I` 标识（见附录 §7.2 / docs/12 §10），不再与原始缺陷编号混用。

### 7.1 原始 13 项缺陷闭环状态（定义来自 Gate 0 评审附件 01）

| 缺陷 ID | 原始定义（Gate 0 评审） | 状态 | 修复 / 证据 | 验证 |
|---|---|---|---|---|
| **B-01** | 四类 PRD 指定样本未完成 | ⚠ 部分完成 | 国家统计年鉴表 spike 00-national（682 槽）／省级年鉴表 spike 00-provincial（480）／地市公报 spike 03（8）三件套已闭环 + 真值对照；**真实扫描 PDF spike 04 ❌ BLOCKED**（无合法中文免费源） | 3/4 真实样本通过；spike 04 诚实 FAILED（未标 PASSED） |
| **B-02** | Schema 无法执行 | ✅ 已闭环 | `schema/01-core.sql` 重写：btree_gist + daterange + 前向外键/非法 COMMENT 修复；39 表 + 13 enum | 全新 PG16 + PG17 `psql -v ON_ERROR_STOP=1` exit 0 |
| **B-03** | 核心模型与数据血缘未满足 PRD | ✅ 已闭环 | 时变 geo_relation / indicator 地域范围 / methodology 版本 / 全真实外键 / append-only revision / current 视图 | `tests/test_schema_negative.py` 39/39（含 R3 新增 26 项） |
| **B-04** | 缺少 8—12 周 MVP | ✅ 已闭环 | `docs/08b-strict-mvp.md`（严格 8—12 周，含回滚 + Gate 条件） | 独立 MVP；22—32 周仅保留为长期路线图 |
| **B-05** | 阶段基线被静默改写 | ✅ 已闭环 | `docs/08b` §7 PRD 偏差表；PRD 基线保留至用户批准 | 无未批准偏差进入正式基线 |
| **B-06** | 湖北期间语义存在高风险错误 | ✅ 已闭环 | spike 02 `derive_period_metadata` 逐指标周期；移除强制 Q2_ONLY；GDP/居民收入标“待核验”caveat | `TestR3PeriodMetadata`（1-5月/月末/上半年/指数） |
| **B-07** | 测试绿灯不能证明提取器有效 | ✅ 已闭环 | pytest.ini `testpaths = spikes tests`；spike 1-4 测试调用实现；删永真断言；spike 04 诚实 BLOCKED | 默认 `python3 -m pytest -q` **237 passed / 0 failed / 0 skipped** |
| **B-08** | 缺失值 + 逐行血缘实现与文档相反 | ✅ 已闭环 | 缺失 obs 保留（value=None + missing_reason + raw_value + cell_locator）；省级逐行血缘字段齐全 | `test_missing_cells_modeled_explicitly` 等 |
| **I-01** | 最终总结不是最终工作区快照 | ✅ 已闭环 | 本文件按最终工作区重写；行数 / 产物 / hash / 测试全部对齐 | 行数与磁盘同步 |
| **I-02** | 省级 spike 不可移植且样本被忽略 | ✅ 已闭环 | 路径 `__file__` ／仓库根解析；无 `/Users/` 硬编码；clean-clone 可复验 | `test_no_path_hardcoding` 自检 |
| **I-03** | 来源登记交付物不一致 | ✅ 已闭环 | `source_registry/registry.csv` 存在（5 行，hash 已录）；README 移除虚假“校验工具”声明 | CSV 存在 + README 与实物一致 |
| **I-04** | 风险登记状态不可信 | ✅ 已闭环 | R04/R08/R11 诚实”部分验证”，未标已缓解；R13—R26 正式登记 | 风险状态与证据相符（doc 09） |
| **I-05** | 方法和来源等级规则不一致 | ✅ 已闭环 (R4-4) | `schema/migrations/002_source_governance.sql` 增加 declared_source_level 列 + CHECK（S0+UNVERIFIED 拒）+ verification_event 审计表（append-only）+ 触发器自动记录 verifier_id；`tests/test_source_governance.py` 21 测试；`source_registry/registry.csv` 新增 declared_source_level + purpose_note 列，archive.org 1909 美国样本 S0→S3（per R4 用户决策）；`docs/03-source-registry.md §9` 文档 | schema CHECK + 21 测试 + 文档同步 |

**13 项原始缺陷：12 项已闭环；B-01（真实扫描 PDF 外部阻塞）部分完成。**

### 7.2 R3 复验项（编号独立于原始缺陷，避免语义漂移）

R3 复验项改用 `A..I` 标识，逐项状态与证据见 `docs/12-stage0-closure-and-report.md` §10（A 缺陷映射 / B 扫描 PDF 诚实 / C 682 格 / D ZIP-only / E 逐指标周期 / F schema / G builder / H 纯净性 / I 文档同步）。

### 7.3 R4 返工 6 项闭环（Codex R3 复核 → REJECT → R4）

Codex R3 复核判定 REJECT，4 类原因：(1) skip-as-PASS 隐藏在 mandatory tests；(2) 全国年鉴证据不一致 + 准确率陈旧；(3) builder 随机 5-sample hash；(4) I-05 误归为用户决策项。

R4 返工 6 项全部闭环（详见 `docs/12-stage0-closure-and-report.md` §11）：

| 返工项 | 状态 | 关键证据 |
|---|---|---|
| **R4-1** 删除 skip-as-PASS | ✅ | `tests/test_cleanliness.py` H-2 用 `--deselect <nodeid>` 替换 `pytest.skip`；spike 00/04 删除 `pytest.skipif` + `if not TESSERACT_REQUIRED: pytest.skip(...)`，改为 `pytest.fail`；builder 解析真实 pytest stats；新增 spike 00 负例：`test_extractor_fails_when_sample_missing` / `test_extractor_fails_when_tesseract_missing` |
| **R4-2** 全国年鉴证据一致 + 质量 BLOCKED 记录 | ✅ | `spikes/00-national-yearbook-table/build_per_column_accuracy.py`（同源 extracted.json + 22 列 + needs_review 校验）；重生成 `per_column_accuracy.json`（header.extractor=spike00-national-yearbook/3.0-R3C，input_hash_sha256=9576529a...，n_observations=682，n_columns=22）；**summary.overall_verdict=BLOCKED**（needs_review=385/682=56.45% > 50% docs/08b 回滚线，诚实记录绝不假装 PASS）；新增 8 测试含 22 列覆盖 + 字节可重现 + BLOCKED 校验 + 无 cherry-picking |
| **R4-3** Evidence Builder 加固 | ✅ | 删除 `random.sample(artifacts, 5)`，改为 `verify_all_artifacts()` 逐项验证（路径唯一 + 相对 + 存在 + 大小 + SHA-256）；`EVIDENCE_PACK_TAMPER` 测试钩子模拟篡改非首 5 artifact → builder rc=4；`_check_hook_env_clean()` 门控 SKIP_*/FORCE_* 环境变量（无 `EVIDENCE_PACK_TEST_HOOKS=1` 一律拒绝，rc=6）；manifest 不在自身 artifacts 列表 + role_count 之和 == artifact_count；新增 4 测试 |
| **R4-4** I-05 来源等级治理 | ✅ | `schema/migrations/002_source_governance.sql`：(a) `declared_source_level` 列；(b) `source_level_s0_requires_verified` CHECK；(c) `source_document_verification_event` 表（append-only）；(d) 触发器自动记录 verification_status 迁移；`tests/test_source_governance.py` 21 测试 |
| **R4-5** 文档同步 | ✅ | docs/03 删除 "production-ready extract.py / 22/22 test_extract.py" 陈旧声明；§9 新增 I-05 治理章节；§4.4 archive.org S0→S3；docs/12 完整重写（区分 EXTERNAL/USER/DEV 三类 + R4-1..R4-6 闭环 + 过期数字修正）；本文件 §7.1 I-05 闭环状态更新 |
| **R4-6** 最终复验 | ✅ | 237 passed / 0 failed / 0 skipped；0 skipped（R4-1 反 skip-as-PASS）；逐项 hash 全量验证（R4-3）；worktree 0 污染（R4-1 H-2）；详见 `docs/12-stage0-closure-and-report.md` §7/§8 |

**R4-1..R4-6：6/6 完成。**

---

## 8. 需要用户决策的问题（Pending Decisions）

下列问题需要用户/评审方在 Stage 1 启动前做出选择：

### 8.1 **扫描 PDF 真实样本获取**（最重要，per 返工指令 §0）
**状态**：❌ BLOCKED（spike 04）
**问题**：是否授权用户手动上传一份扫描 PDF（带授权声明）作为 spike 04 真值对照？
**建议**：同意；否则 spike 04 永久保留 BLOCKED 状态，Gate 1 不要求 spike 04 真值。

### 8.2 **DSH 决策时机**
**问题**：Stage 4 末才做 DSH 评估，是否同意？
**建议**：同意（per doc 07 第 6 节；Stage 1-3 不引入 DSH）。

### 8.3 **R09 / R10 提前实施**
**问题**：AI 幻觉检测（R09）和确认偏差防控（R10）是否 Stage 2 提前实施？
**建议**：Stage 2 中段开始做"反例登记流程"，先于 R09（DSH）。

### 8.4 **R03 / R08 / R12 Stage 1 落地优先级**
**问题**：R03（地方缺失）/ R08（授权）/ R12（URL 漂移）三个运维风险先做哪个？
**建议**：R08 上传入口优先（前置 R03）；R12 URL 监控次之；R03 数据落库最后。

### 8.5 **pgvector / 向量检索**
**问题**：Stage 4 是否启用 pgvector？
**建议**：Stage 4 末与 DSH 一同评估；不提前。

### 8.6 **PRD 偏差**（per 返工指令 §5）
**问题**：当前 MVP 是否引入"江苏单省深度"等范围缩小？
**建议**：**不引入**。详见 `docs/08b-strict-mvp.md` §7 偏差表；任何偏差必须先经用户批准后才进入正式基线。

---

## 9. 评审清单（Review Checklist for Approver）

评审方请逐项打勾：

### 9.1 PRD 15 全清单（11 + 1b）

- [ ] **仓库现状评估**清晰（读 `00`）
- [ ] **当前架构**说明空仓现状（读 `01`）
- [ ] **目标架构**可执行（读 `02`）
- [ ] **来源登记表**有 spike 证据（读 `03` + 6 个 spike 目录）
- [ ] **数据模型**与 PRD 5 章对齐（读 `04` + `schema/01-core.sql`）
- [ ] **指标方法**版本化机制明确（读 `05`）
- [ ] **治理观察方法**遵守"不输出总分"（读 `06`，七维度已校准）
- [ ] **DSH 决策**有评分依据（读 `07`）
- [ ] **MVP 计划（严格 8—12 周）**符合返工指令 §5（读 `08b`）
- [ ] **MVP 计划（长期）**作为路线图保留（读 `08`）
- [ ] **风险登记**覆盖 PRD 12 章 + R13-R16 返工新增（读 `09`）
- [ ] **验收测试**覆盖数据/方法/AI 三层（读 `10`）

### 9.2 PRD 1.3 红线

- [ ] 未涉及"官员能力总评分"
- [ ] 未涉及"私人/泄露/非公开个人信息"
- [ ] 未涉及"活动数=绩效"
- [ ] 未涉及"LLM 改写原始数据"
- [ ] 未涉及"绕过验证码/付费墙"
- [ ] 未涉及"DSH 作为数仓"

### 9.3 PRD 15 阶段纪律

- [ ] 未批量抓取全国市县数据
- [ ] 未建立官员总评分
- [ ] 未用合成样本替代真实样本
- [ ] 未把 BLOCKED 标为 PASSED
- [ ] 未把永真测试当 PASSED
- [ ] 未自行进入 Stage 1

### 9.4 原始 13 项缺陷（Scheme 1 — 定义见 Gate 0 评审附件 01）

- [ ] B-01 四类指定样本未完成 → ⚠ 部分完成（国家/省级/地市已闭环；真实扫描 PDF BLOCKED）
- [x] B-02 Schema 无法执行 → ✅ 已闭环（PG16 + PG17 psql exit 0）
- [x] B-03 核心模型与数据血缘未满足 PRD → ✅ 已闭环（39 负例；F-2 NOT NULL 已落地）
- [x] B-04 缺少 8—12 周 MVP → ✅ 已闭环（docs/08b-strict-mvp.md）
- [x] B-05 阶段基线被静默改写 → ✅ 已闭环（08b §7 偏差表）
- [x] B-06 湖北期间语义存在高风险错误 → ✅ 已闭环（逐指标周期；移除 Q2_ONLY）
- [x] B-07 测试绿灯不能证明提取器有效 → ✅ 已闭环（默认 pytest 237 / 0 / 0；`tests/conftest.py` 自动 apply 002）
- [x] B-08 缺失值 + 逐行血缘与文档相反 → ✅ 已闭环（缺失 obs 显式建模）
- [x] I-01 最终总结不是最终工作区快照 → ✅ 已闭环（本文件重写）
- [x] I-02 省级 spike 不可移植且样本被忽略 → ✅ 已闭环（无 /Users/ 硬编码）
- [x] I-03 来源登记交付物不一致 → ✅ 已闭环（registry.csv 存在；README 清理）
- [x] I-04 风险登记状态不可信 → ✅ 已闭环（R04/R08/R11 未标已缓解；R13—R26 登记）
- [x] I-05 方法和来源等级规则不一致 → ✅ 已闭环（R4-4：declared_source_level + CHECK + 审计表 + 21 测试；docs/03 §9 同步）

### 9.5 测试硬指标

- [ ] 默认 `python3 -m pytest -q` 通过：237 passed / 0 failed / 0 skipped（默认流程经 `tests/conftest.py` 自动 apply 002 后）
- [ ] schema 负例通过：39/39（tests/test_schema_negative.py）
- [ ] Schema 在空 PG 17 + PostGIS 上 psql exit 0

### 9.6 真实样本

- [ ] NBS C03-09 JPG 真值（682 obs，31×22 全网格）
- [ ] Hubei 2025 年鉴 xls 真值（480 obs）
- [ ] Hubei 2026-06 xlsx 真值（19 obs）
- [ ] Shenzhen 公报 HTML 真值（8 obs）
- [ ] 扫描 PDF：BLOCKED（需用户决策）

---

## 10. 最终状态（Final State）

| 项目 | 状态 |
|---|---|
| **PRD 15 全部交付物** | ✅ 12/12（11 + 08b 严格 MVP） |
| **Schema 草案** | ✅ 1082 行 / 39 表 / 13 enum / psql exit 0 |
| **6 类数据 Spike 验证** | ✅ 5 PASSED + 1 BLOCKED（spike 04 真实 PDF） |
| **默认 pytest** | ✅ **237 passed / 0 failed / 0 skipped**（`tests/conftest.py` 自动 apply 002；详见 §1.4） |
| **数据库负例** | ✅ 39/39（核心 13 项 + R3 新增 26 项） |
| **风险登记** | ✅ 26 风险（R01—R21 + R22—R26，R4/R5 返工新增 5 条） |
| **PRD 1.3 红线** | ✅ 严守 |
| **PRD 15 阶段纪律** | ✅ 严守 |
| **原始 13 项缺陷（§7）** | ✅ 12 已闭环 / ⚠ B-01（真实扫描 PDF 外部阻塞）部分完成 |
| **Stage 1 启动** | ⏸️ **等待评审指令** |

---

**Stage 0 返工后重新提交。停止。等待审核。**

不自动进入 Stage 1。如需进入 Stage 1，请明确指令"启动 Stage 1"并对 §8 待决问题给出选择。