# Stage 0 Gate 0 — Cursor 独立复验（对照 R4-6）

- 复验日期：2026-08-23
- 复验方：Cursor（对照 Claude Code 提交的 R4 成果）
- 对照材料：
  - `docs/13-r4-final-verification.md`（R4-6 声称）
  - `docs/12-stage0-closure-and-report.md`（完整 closure）
  - `docs/03-source-registry.md` §9（I-05 治理）
  - `docs/11-stage0-review.md`
- 方法：把 `docs/13` 当**声称**，把磁盘文件 + 本机命令当**证据**；不改代码、不以叙事补齐缺口。
- 范围：Stage 0 Gate 0 / R4 返工闭环复验。不得据此进入 Stage 1。

---

## 0. 评审输出（per PRD 16.3）

| 项 | 判定 |
|---|---|
| 结论 | **有限通过（代码）+ 不通过（R4-5/R4-6 文档与入库证据包）**；Stage 0 **维持 BLOCKED** |
| Stage 0 Gate 0 | **BLOCKED**（同意 CC：中文扫描 PDF 缺失 + 不降 OCR 门槛 + 不接受 1909 美国样本代表中国） |
| R4-1…R4-4 代码实质 | **有限通过**（实现存在；默认库/builder 路径不保证 I-05 已 apply） |
| R4-5 / R4-6 文档与 evidence pack | **不通过** |
| 阻塞问题 | 见 §2 |
| 重要但非阻塞 | 见 §3 |
| 证据不足 | 见 §4 |
| 要求 CC 修改的精确任务 | 见 §7（仅当用户另行下达改代码/文档指令时执行） |
| 下一 Gate 进入条件 | 见 §8；**当前不得进入 Stage 1** |

---

## 1. 总评

同意 Claude Code 将 Stage 0 标为 **BLOCKED**，且阻塞原因应仅归为：

- **EXTERNAL**：无代表性中文扫描 PDF（B-01 / E-1 / spike 04）
- **USER POLICY**：不降低 OCR 门槛；不接受 1909 年美国统计摘要作为中国研究平台代表性样本

**不同意**将 R4-6 按字面验收为「237 passed 可复现、425 artifacts 已入库、分套计数正确、文档已同步」。

把「dev rework 6/6 闭环」降级为：**I-05 等代码在补跑 migration 002 后可用；交付叙事与入库证据包未达到独立复验标准。**

---

## 2. 阻塞问题（维持 Stage 0 BLOCKED）

### 2.1 E-1 / B-01 中文扫描 PDF 缺失

- 严重性：P0（Stage 0 外部阻塞，非本轮文档错误）
- 证据：
  - `data/extracts/04-scanned-pdf/eval_report.json`：`numeric_cell_accuracy_pct = 0.0`，`char_accuracy_pct = 3.7`，`needs_review_total = 450/450`
  - `spikes/04-scanned-pdf/gate_thresholds.json`：`gate_verdict` 为 BLOCKED；阈值 numeric ≥80% / char ≥90% / needs_review ≤30%
  - 唯一样本：archive.org 1909 美国 Statistical Abstract
- 关闭条件：用户提供代表性中文扫描 PDF，或书面批准改变样本/门槛政策。在此之前不得把 spike 04 标成产品 PASS。

### 2.2 用户政策 P-1 / P-2 / P-3

- 不降低 OCR 门槛。
- 不接受 1909 美国样本代表中国治理平台（仅可作 OCR 压力样本；`registry.csv` 已将 archive.org 有效等级标为 S3）。
- Stage 0 维持 BLOCKED 直至 E-1 解除。

以上三项复验方**同意维持**，不建议 CC 自行改门槛或把美国样本升为 S0。

---

## 3. 重要但非阻塞（宣布「R4 闭环」前应修；不解开 E-1）

下列问题**不能**用来推翻「Stage 0 因扫描 PDF 而 BLOCKED」，但足以判定 **R4-5/R4-6 不通过**。

### 3.1 测试分套计数错误（`docs/13` 表内自相矛盾）

独立命令：

```bash
python3 -m pytest --collect-only -q -p no:cacheprovider
```

结果：**237 tests collected**。

| 套件 | `docs/13` 声称 | 实际 collect |
|---|---|---|
| `spikes/00-national-yearbook-table` | 24 | **31** |
| `spikes/00-provincial-yearbook-table` | 21 | 21 |
| `spikes/01-national-yearbook` | 20 | 20 |
| `spikes/02-provincial-yearbook` | 30 | 30 |
| `spikes/03-municipal-bulletin` | 29 | 29 |
| `spikes/04-scanned-pdf` | 18 | 18 |
| `tests/test_cleanliness.py` | 11 | 11 |
| `tests/test_evidence_builder.py` | 17 | 17 |
| `tests/test_schema_negative.py` | **47** | **39** |
| `tests/test_source_governance.py` | 21 | 21 |
| **合计** | 各行相加 = **238**，正文写 237 | **237** |

`docs/12` 将 schema 负例写成 47（§2 B-03、§7），属 R4-5「39→47」写过头；磁盘上 `test_schema_negative.py` 为 39 个 `def test_`，复验实跑 **39 passed**。

### 3.2 「237 passed」在默认库上不可复现（I-05 apply 链断裂）

复验开始时 PostgreSQL 17.11 @ `127.0.0.1:55440` / `cegr_test`：

- `cegr`：**39 张基表**（与 `01-core.sql` 一致）
- **没有** `source_document.declared_source_level`
- **没有** `source_level_s0_requires_verified`
- **没有** `source_document_verification_event`

未 apply 002 时：`python3 -m pytest tests/test_source_governance.py` → **21 failed**（`UndefinedColumn: declared_source_level`）。

对同一库执行 `schema/migrations/002_source_governance.sql` 后 → **21 passed**。

结论：

- I-05 SQL/测试**本身成立**。
- pytest **不会**自动 apply 002。
- `scripts/build_evidence_pack.py` 的 `run_db_apply`：`DROP SCHEMA cegr CASCADE` 后只 apply `schema/01-core.sql`，真实 builder 跑完会**再次丢掉** I-05 对象。
- `docs/13` 把「历史一次跑分 237/0/0」写成当前可复现状态，不成立。

干净复验方法：先 `DROP SCHEMA cegr CASCADE`，只跑 `01-core.sql`，确认治理测试为红；再 apply 002，确认为绿。若库上已手动 apply 过 002，绿灯不能证明默认交付链完整。

### 3.3 入库 evidence pack 仍是 R3 快照

| 来源 | `schema_version` | artifact 数 | `002_source_governance.sql` |
|---|---|---|---|
| `docs/13` 声称 | `1.1-R3G-R4` | 425 | 作为 DDL 增量被强调 |
| 仓库 `evidence_pack/manifest.json` | **`1.1-R3G`** | **423** | **不在 artifacts** |
| SKIP 构建到临时目录（不覆盖仓库） | `1.1-R3G-R4` | **426**（含 `docs/13`） | **仍不在 pack**（builder 只收 `schema/*.sql` 与 `migrations/*.log`） |

契约抽查（入库 pack 与 SKIP 新构建）：manifest **没有** `/Users/`、`/home/`、`/tmp/`，也没有 `generated_at_utc` / `wall_clock_now`。路径相对、无自哈希、role 之和等于 count：SKIP 构建成立。

Builder 源码为 `schema_version = 1.1-R3G-R4`，且无 `random.sample`。**已提交 pack 不能当 R4 全量哈希证明。**

独立计算：`schema/01-core.sql` SHA-256 = `09aa46f9f6713b17d7e7171799a769c600f4b6eb26f37631039ffb77b7e089ea`（与 `docs/12` 一致）。`002_source_governance.sql` = `c41161a86fb68e882bc4925ebec758f2b2616d0f4914b023dc8c5a5ec85e168b`。`docs/13` §7 仍为占位「原 R3 hash 未变」。

### 3.4 R4-5 文档未同步（内部打架）

- `docs/11` 文首仍写 **I-05 部分完成**；§9.4 勾选 I-05「部分完成」；§9.5 / §10 仍写 pytest **205**、schema **39/39**。同文件 §7.1 / §7.3 写 I-05 已闭环、237。文首与附录清单未跟 R4。
- `docs/03` §4.1–4.3 测试数仍为 14/14、20/20、31/31（与 collect 20/30/29 不符）。
- `docs/03` §4.4 仍写「**5/15 页面通过即算 PASS / 当前 5/15**」。`gate_thresholds.json` 与 `eval_report.json` 为 numeric **0%** / char **3.7%** / needs_review **100%**，`gate_verdict=BLOCKED`。§9 与 registry 的 S0→S3 更新不能掩盖 §4.4 陈旧门控叙事。
- `docs/03` §9.5「中文登记保持 S0 + VERIFIED」：`source_registry/registry.csv` 无 `verification_status` 列（该字段属于 `source_document`）。
- `docs/12` §6 登记 R4-R1…R4-R4 为 MITIGATED；`docs/09-risk-register.md` **止于 R21**，未写入对应条目。

### 3.5 skip 政策过满

- spike 00/04 缺样本/缺 tesseract 已改为 `pytest.fail`（R4-1 主体成立）。
- `tests/test_cleanliness.py` 仍有 **3 处** `pytest.skip`（无 `data/`、git 不可用）。「mandatory tests 中 0 个 skip」在本仓库默认路径下碰巧不触发，但代码路径仍在。

### 3.6 抽取物绝对路径

`eval_report.json` 的 `truth_table` / `extracted_file` 为 `/Users/kjonekong/projects/china platform/...`。manifest 禁止绝对路径；评估报告未遵守同一契约。`evaluate_04.py` 用 `str(args.truth)` 写入，复跑会再生绝对路径。

---

## 4. 证据不足之处

- **全量 237 + H-2 worktree 哈希前后一致**：本次未重跑含 H-2 的整套（约 6 分钟且子进程再跑一遍）。只确认 collect=237，以及 schema 39 passed、governance 在 apply 002 后 21 passed。`docs/13` §1 的 `WORKTREE_HASH_*` 未独立重算。
- **真实 builder 全量**（无 SKIP，真跑 pytest + DROP+psql）：未作为本轮复验步骤执行；仅静态阅读 `run_db_apply` 确认未 apply 002。
- 上一轮复验曾对本地 `cegr_test` **手动 apply 002**。后续若未 `DROP SCHEMA`，治理测试绿灯**不能**当作「默认流程已修好」。

---

## 5. I-05 专章复验（`docs/03` §9 + 代码）

### 5.1 与 SQL/测试对齐的部分（成立）

- 两层等级：`declared_source_level`（声明）vs `source_level`（effective）
- CHECK：`source_level <> 'S0' OR verification_status = 'VERIFIED'`
- 审计表 `source_document_verification_event` append-only；UPDATE/DELETE 由 trigger 拒绝
- `verification_status` 变更写事件（含 `app.verifier_id` GUC）
- `tests/test_source_governance.py` collect **21**（含 S1–S4 参数化）
- `source_registry/registry.csv` 5 行：archive.org **S3** + `declared_source_level=S0` + purpose_note；中文四源 **S0**

### 5.2 不成立或未落地的部分

- 默认空库 / builder DROP+`01-core` 后，§9 描述的约束在数据库中**不存在**，直至手动 apply 002。
- `002.sql` 不进入 evidence pack。
- CSV 无法证明「VERIFIED」；平台核验状态未在登记表体现。

I-05 作为「方法与来源等级规则」：**设计与测试在 apply 后通过；交付链与文档清单未闭环。** 不宜再标成「待用户决策」，也不宜标成「生产库默认已治理」。

---

## 6. 对 R4-1…R4-6 的逐项复核

| ID | 代码 | 文档/证据包 | 说明 |
|---|---|---|---|
| R4-1 | 基本成立 | 过满 | skip 未从 cleanliness 环境分支删净 |
| R4-2 | 成立 | 成立 | `per_column_accuracy.json`：682 / 22 列 / needs_review 385（56.45%）/ `overall_verdict=BLOCKED` |
| R4-3 | 代码成立 | 入库 pack 未更新 | 声称 425 ≠ 仓库 423 ≠ SKIP 现构建 426 |
| R4-4 | **成立（apply 002 后）** | registry + §9 主体成立 | 默认 DB 无 002；`002.sql` 不进 pack |
| R4-5 | 部分 | **失败** | docs/11 清单、docs/03 §4、docs/09 未跟到 R4 |
| R4-6 | — | **失败** | 分套计数自相矛盾；§7 无哈希；把历史跑分写成当前可复现状态 |

R4-2 数字与磁盘一致，属诚实 BLOCKED 记录，予以认可。

---

## 7. 要求 CC 修改的精确任务（需用户另行下令改仓库）

本文件为**复验意见**。下列任务**不是**本文件作者已实施的补丁，仅在用户明确要求 CC 改代码/文档时执行：

1. 修正 `docs/11` / `docs/12` / `docs/13` 测试数：schema **39**、spike 00-national **31**、分套表加总必须等于 collect **237**。
2. pytest 与 builder 默认 apply `002_source_governance.sql`（或在 `01-core.sql` 后强制链式 apply）；禁止 DROP+只 core 后仍声称 I-05 已落地。
3. builder 收录 `schema/migrations/*.sql`；用真实 R4 构建替换或明确标注仓库内 R3 `evidence_pack/manifest.json`（`1.1-R3G` / 423）。
4. 删除 `docs/03` §4.4 的 5/15 PASS 叙事；同步 §4.1–4.3 测试数；澄清 CSV 无 VERIFIED 字段。
5. 修正 `docs/11` 文首与 §9.4 / §9.5 / §10（I-05 部分完成、205 passed）。
6. 将 R4 风险写入 `docs/09`，或从 `docs/12` 删除「已写入 09」的表述。
7. （可选）`eval_report.json` / `evaluate_04.py` 改为仓库相对路径；cleanliness 环境 skip 改为 fail。

**不要**降低 OCR 门槛，**不要**把 1909 美国样本标为代表性 S0，**不要**进入 Stage 1。

---

## 8. 下一 Gate 进入条件

进入 Stage 1 之前至少满足：

1. E-1 解除（中文扫描 PDF）或用户书面批准维持 BLOCKED 并缩小 Stage 0 验收范围（排除代表性 OCR 闭环）。
2. 独立复验：`DROP SCHEMA` → 只 `01-core` → 治理测试失败；再 apply 002 → 21 passed；builder 真实路径 apply 两者。
3. `pytest --collect-only` 与文档分套表一致且总和 237。
4. 入库 `evidence_pack/manifest.json` 的 `schema_version` 为 R4 口径，且含 `002_source_governance.sql`（或文档明确声明 pack 仅为 R3、不以 pack 证明 R4）。
5. `docs/11` 文首/附录与 §7 不再互相否定。

当前：**停止。等待审核。不得自行进入 Stage 1。**

---

## 9. 建议复验命令（供下一轮评审方复跑，不修改仓库）

```bash
# A. 清单
python3 -m pytest --collect-only -q -p no:cacheprovider

# B. I-05 默认链（会改测试库 schema，不改 git 工作区）
PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
  -v ON_ERROR_STOP=1 -c "DROP SCHEMA IF EXISTS cegr CASCADE"
PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
  -v ON_ERROR_STOP=1 -f schema/01-core.sql
python3 -m pytest -q -p no:cacheprovider tests/test_source_governance.py
# 预期：21 failed（缺列）

PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
  -v ON_ERROR_STOP=1 -f schema/migrations/002_source_governance.sql
python3 -m pytest -q -p no:cacheprovider tests/test_source_governance.py tests/test_schema_negative.py
# 预期：21 + 39 passed

# C. 证据包（写临时目录，勿覆盖仓库 evidence_pack/）
EVIDENCE_PACK_DIR=/tmp/r4_reverify EVIDENCE_PACK_TEST_HOOKS=1 SKIP_PYTEST=1 SKIP_PSQL=1 \
  python3 scripts/build_evidence_pack.py
```

对照：`evidence_pack/manifest.json` 是否仍为 `1.1-R3G` / 423。

---

## 10. 复验方决策建议（给用户）

1. 是否提供中文扫描 PDF（唯一能解开 E-1 的材料）。
2. 是否要求 CC 只修 §7 的文档与 apply 链后再交一轮，还是接受「代码有限通过 + 文档/pack 不合格」作为 R4 终态。
3. 测试库是否应在 clone 后自动 apply 002（建议：**要**）。

**下一步：不要进 Stage 1。**

---

## 11. 本文件未做的事

- 未修改业务代码、schema、测试或 `docs/00`–`docs/13`。
- 未覆盖仓库 `evidence_pack/manifest.json`。
- 未把 BLOCKED 改写成 PASS。
- 未重跑含 H-2 的全量 pytest。

— End of Cursor R4 re-review —
