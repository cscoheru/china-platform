# Stage 0 Gate 0 — Closure Matrix & Final Report (R3 + R4 rework)

> Generated 2026-08-23 per R3/R4 directives; updated 2026-08-24 for U-1/U-2/U-3 Shaanxi integration; **Gate 0 CLOSED 2026-08-24 per U-4=A（per `reviews/23-stage1-kickoff-20260824.md` §1）**。
>
> 关键修正 (R4 返工后)：
> - Codex R3 复核判定 **REJECT**，原因：A–I 9/9 "done" 隐藏了 skip-as-PASS、随机 5-sample hash、陈旧准确率快照、I-05 误归为用户决策项
> - R4 返工 6 项全部闭环，详见 **§11 R4 Rework Closure**
> - 当前测试基线：**251 passed / 0 failed / 0 skipped**（原 237 + 陕西 OCR research-track 14）
> - I-05 已落地为 schema + 审计表 + 测试 + doc（不再是"待用户决策"）
> - E-1 资源等待已结束：陕西官方四页扫描 PDF 已集成；per U-3，spike 04 仍为非门控研究项；P-1/P-2 不变，Stage 0 终态只由 Cursor 复验与用户 U-4 裁定
>
> 编号口径：§2 用原始 13 项缺陷（B-01..B-08、I-01..I-05）；§10 用 A..I 返工项；§11 用 R4-1..R4-6 返工项。三套编号互不混用。

## §1. Stage 0 Status（Gate 0 CLOSED 2026-08-24 per U-4=A）

| Field | Value |
|---|---|
| Gate | Gate 0 (Stage 0 verification) |
| Verdict | **CLOSED**（U-4=A；用户已授权启动 Stage 1；详见 `reviews/23` §1；**不等于** Stage 0 全 PASS 或统计表代表性样本齐备；spike 00 needs_review 56% / 1909 FAILED / 陕西 research-only 等质量债由 Stage 1 继续诚实记录） |
| Closure matrix (原始 13 项缺陷) | 12/13 closed；B-01 原统计表代表性缺口保留，按 U-3 移出 spike 04 门控 |
| Dev rework (R4-1..R4-6) | 6/6 closed |
| Pytest (total project) | **251 collected / 251 passed / 0 failed / 0 skipped**（spikes + tests 全集） |
| Pytest increment | +14 Shaanxi OCR tests；历史 R4 +32 基线不倒改 |
| Schema DDL SHA-256 | `09aa46f9f6713b17d7e7171799a769c600f4b6eb26f37631039ffb77b7e089ea` + `002_source_governance.sql` 增量 |
| DB engine (PG16 path) | PostgreSQL 16.15 + PostGIS 3.4.6（`schema/migrations/001_create_core.log`） |
| DB engine (PG17 path) | PostgreSQL 17.11 + PostGIS 3.6.4（builder 每次构建对 55440 DROP+apply） |
| Spike domains | 5 个 Stage 0 主轨保留原结论 + 1 个非门控 scanned-PDF 研究轨 |
| Mandatory-test policy | NO `pytest.skip`、no BLOCKED-as-PASS、no field-only PASS、no random-sample hash |

## §2. 13-item Closure Matrix（原始缺陷，Scheme-1 定义）

| ID | 原始缺陷（定义） | R4 verdict | 证据 |
|---|---|---|---|
| **B-01** | 四类 PRD 指定样本未完成 | ⚪ U-3 非门控 | 国家年鉴／省级／地市三类闭环；陕西法规真实扫描件已作 U-1 中文压力样本集成，但不冒充原统计表代表性；spike 04 不参与 Stage 0 Gate |
| **B-02** | Schema 无法执行 | ✅ | PG16 + PG17 `psql -v ON_ERROR_STOP=1` exit 0；migration 002 增量（I-05 治理） |
| **B-03** | 核心模型与数据血缘未满足 PRD | ✅ | `tests/test_schema_negative.py` 39 tests 全部通过 |
| **B-04** | 缺少 8—12 周 MVP | ✅ | `docs/08b-strict-mvp.md`（严格 8—12 周） |
| **B-05** | 阶段基线被静默改写 | ✅ | `docs/08b` §7 PRD 偏差表 |
| **B-06** | 湖北期间语义存在高风险错误 | ✅ | spike 02 per-indicator period metadata；schema `comparison_basis` 移除 `Q2_ONLY` |
| **B-07** | 测试绿灯不能证明提取器有效 | ✅ | 251/251 passed；spike 测试真实调用提取器；陕西 truth/extract/eval 全写 tmp、两次字节一致、缺依赖 fail；不把研究阈值失败写成 PASS |
| **B-08** | 缺失值 + 逐行血缘实现与文档相反 | ✅ | 缺格 obs 保留（value=None + missing_reason） |
| **I-01** | 最终总结不是最终工作区快照 | ✅ | 行数 / 产物 / hash / 测试数与磁盘一致（本文件按最终状态重写） |
| **I-02** | 省级 spike 不可移植且样本被忽略 | ✅ | `__file__` 解析仓库根；clean-clone 缺 ZIP fail |
| **I-03** | 来源登记交付物不一致 | ✅ | `source_registry/registry.csv`（6 条来源；新增陕西官方 URL/hash/size/非门控用途） |
| **I-04** | 风险登记状态不可信 | ✅ | R04/R08/R11 诚实"部分验证"；R13—R26 登记 |
| **I-05** | 方法和来源等级规则不一致 | ✅ | `schema/migrations/002_source_governance.sql` + `tests/test_source_governance.py`（21 测试）+ `docs/03 §9` + `registry.csv` archive.org S0→S3 |

**闭环口径：12/13 closed；B-01 原定义下仍不是统计表代表性样本，但 U-3 已将其完整移出 Stage 0 验收，不再形成外部 BLOCKED。**

## §3. Spike-by-Spike Status（6 个 spike）

### 3.1 Spike 00-national（国家年鉴 JPG 多列 OCR）— ✅ PASS
31×22 = 682 槽位完整网格 + 缺格显式建模 + right-edge 列边界映射。
**R4-2 新增**：`per_column_accuracy.json`（22 列 + needs_review=385/682=56.45%）+ 字节可重现测试；**overall_verdict=BLOCKED**（needs_review > 50% 触发 docs/08b 回滚线，诚实记录）。
**R4-1**：删除 `@pytest.mark.skipif(not PDF_REQUIRED)` 与 `if not TESSERACT_REQUIRED: pytest.skip(...)`，改为 `pytest.fail`；H-2 用 `--deselect` 而非 `pytest.skip` 防递归。

### 3.2 Spike 00-provincial（省级年鉴 ZIP）— ✅ PASS
tracked-ZIP-only + TemporaryDirectory + zip-slip 防护 + clean-clone fail。
R4-1：跳过路径移除，缺失样本 → fail（不 skip）。

### 3.3 Spike 02（湖北 2026 H1 月报）— ✅ PASS
per-indicator 周期元数据；锁定 `extracted_at`；30/30 tests。

### 3.4 Spike 03（地市统计公报）— ✅ PASS
29/29 tests。

### 3.5 Spike 01（国家年鉴表）— ✅ PASS
20/20 tests。

### 3.6 Spike 04（扫描 PDF OCR）— ⚪ **非 Stage 0 验收项（per U-3）**

**Legacy 数值表轨**保留 1909 美国 Statistical Abstract 的历史结果：numeric 0.0%、digit-char 3.7%、needs_review 450/450。它不代表中国，且未被新样本覆盖。

**陕西中文文本轨**已完成集成：

- 官方源：全国人大常委会国家法律法规数据库四页 PDF；SHA-256 `f34b2e57...71488`
- C-1：本地 `%PDF-1.4`、size/hash 通过；来源扩展属性指向官方 URL；CC 未亲见 HTTP 200，明确记为 `null` 而非伪造
- C-2：Canon SC1011 / MP Navigator EX + 每页 1259×1669 灰度 JPEG 图像层
- C-3：嵌入层 3,230 汉字（≥3,000）
- C-4：`provenance.json` 记录 source URL、法规数据库、著作权法第五条依据及不扩张的许可边界
- U-2 对照：嵌入旧 OCR 文本层；已披露其 `预箅`/`收攴`/`本行畋区域` 等参考噪声
- 评测：Han **93.93%**；all non-whitespace **90.05%**；needs_review **1/4=25%**；numeric `N/A` 且不计 PASS
- 结果：`MEETS_UNCHANGED_APPLICABLE_THRESHOLDS`
- 门控：`stage0_effect=none_per_U3_non_gating_research_sample`；不得据此宣布 Stage 0 PASS

## §4. R2 → R3 Mapping（保留作历史参考）

| R2 task | 原始缺陷 | 文件/测试 | 结果 |
|---|---|---|---|
| R2-1 DB 负例 | B-03 | `tests/test_schema_negative.py` | ✅ |
| R2-2 MVP/doc 一致 | B-04 | `docs/08b-strict-mvp.md` | ✅ |
| R2-3 registry CSV | I-03 | `source_registry/registry.csv` | ✅ |
| R2-4 machine manifest | I-05 部分 | `evidence_pack/manifest.json` + `scripts/build_evidence_pack.py` | ✅ |
| R2-5 evidence pack | I-05 | 同上 | ✅ |
| R2-6 closure matrix | – | 本文件 | ✅ |
| R2-7 final report | – | 本文件 | ✅ |
| R2-8 spike 04 honesty | B-01 | `spikes/04-scanned-pdf/README.md`、`gate_thresholds.json` | ✅ |
| R2-9 682 槽（C） | I-01 | `test_full_31x22_grid_exact` | ✅ |
| R2-10 ZIP-only（D） | B-06 | zip-slip + 0109 定位 | ✅ |
| R2-11 逐指标周期（E） | I-02 | `TestR3PeriodMetadata` | ✅ |

## §5. Outstanding Items — 三类分开

### 5.1 EXTERNAL BLOCKING

**无 E-1 文件获取阻塞。** 用户已从官方 URL 下载并上传陕西 PDF；来源、结构与 hashes 已验证。原“中文扫描 PDF 缺失”只保留在历史审核记录中。

### 5.2 USER POLICY（用户已决策，dev 不得变更）

| # | 决策 | 含义 |
|---|---|---|
| P-1 | 不下调当前 OCR 门槛 | numeric ≥80% / char ≥90% / needs_review ≤30% |
| P-2 | 不接受 1909 美国样本作为中国代表性 | legacy 轨仅作历史 OCR 压力回归 |
| U-1 | 陕西法规扫描件可作中文 OCR 压力样本 | 不要求满足原 B-01 统计表代表性 |
| U-2 | 接受嵌入文本层作对照 | 参考噪声必须披露，不静默人工纠正 |
| U-3 | spike 04 完整移出 Stage 0 验收 | research result 不改变 Gate verdict |
| U-4 | 待最终 eval + Cursor 复验后裁定 | CC 不自动宣布 Stage 0 PASS |

### 5.3 DEV REWORK

陕西 truth/extract/evaluate/test/provenance/source registry/docs 已完成；固定物理中线串栏缺陷已改为每页 robust content-bounds divider，跨线 word policy 显式记录；`chi_sim.traineddata` hash 和 truth/OCR/eval committed freshness 已进入测试。最终 evidence pack 重建、独立 hash 复算与 Cursor 复验记录见 `docs/16-e1-candidate-report-20260824.md`。

## §6. Risk Register 状态（详见 docs/09）

| Risk | 状态 |
|---|---|
| R3-R1 spike 04 样本偏差 | ⚪ 1909 仍不代表中国；陕西已集成但仅研究；per U-3 非 Gate blocker |
| R3-R2 source_registry_id 孤儿文档 | ✅ MITIGATED（F-2 NOT NULL + 39 测试） |
| R3-R3 manifest 自 hash | ✅ MITIGATED（G-2 + R4-3：manifest 不在自身 artifacts） |
| R3-R4 manifest 绝对路径 | ✅ MITIGATED（G-2：无 /Users/ /home/ /tmp/） |
| R3-R5 PG16/PG17 fixture 端口 | 🟢 文档化（`001_create_core.log` 双路径） |
| R3-R6 预解压 XLS 消费 | ✅ MITIGATED（D：tracked-ZIP-only） |
| R3-R7 Q2_ONLY 期间语义 | ✅ MITIGATED（E：per-indicator period metadata） |
| R3-R8 682 网格未实现 | ✅ MITIGATED（C：`test_full_31x22_grid_exact`） |
| R3-R9 测试污染契约缺失 | ✅ MITIGATED（H-2：worktree hash 前后一致） |
| R3-R10 builder 不自校验 | ✅ MITIGATED（G-2 + R4-3：逐项验证 + 篡改负例） |
| **R4-R1** skip-as-PASS | ✅ MITIGATED（R4-1：删除 skip + pytest.fail；见 `docs/09` R22） |
| **R4-R2** 全国年鉴证据不一致 | ✅ MITIGATED（R4-2：同源抽取 + 22 列覆盖 + 字节可重现；见 `docs/09` R23） |
| **R4-R3** builder 随机抽样 hash | ✅ MITIGATED（R4-3：全量逐项验证 + EVIDENCE_PACK_TAMPER 负例；见 `docs/09` R24） |
| **R4-R4** I-05 来源等级无治理 | ✅ MITIGATED（migration 002 + CHECK + 审计表 + 21 测试；见 `docs/09` R25） |

## §7. Fresh Test Execution Evidence（2026-08-24，陕西集成后）

| Metric | Value |
|---|---|
| Command | `python3 -m pytest -q -p no:cacheprovider`（spikes + tests 全集） |
| Collected / Passed / Failed / Skipped | **251 / 251 / 0 / 0** |
| `tests/test_schema_negative.py` | 39 passed（PG17 @55440） |
| `tests/test_evidence_builder.py` | 17 passed |
| `tests/test_cleanliness.py` | 11 passed（含 H-2 worktree hash） |
| `tests/test_source_governance.py` | 21 passed |
| `spikes/00-national-yearbook-table` | 31 passed |
| `spikes/04-scanned-pdf` | **32 passed**（18 legacy + 14 陕西；缺样本/工具 fail；tmp 输出不污染正式产物） |
| DSN | `host=127.0.0.1 port=55440 user=postgres dbname=cegr_test` |
| Engine | PostgreSQL 17.11 + PostGIS 3.6.4 |

## §8. Mandatory-test policy audit（R4 强化）

- `pytest.skip` 在全集内贡献 **0 个 skip**（251 passed / 0 skipped）
- BLOCKED-as-PASS：**0**（spike 04 诚实 BLOCKED；per_column_accuracy.json 总体 BLOCKED 记录）
- Field-only PASS：**0**（H-2 + R4-1 强制实跑）
- Random-sample hash：**0**（R4-3 全量逐项验证）
- 同义反复断言：**0**（R4-2 字节可重现 + extracted.json 与 per_column_accuracy.json 同源）

## §9. Clean-clone reproducibility instructions

```bash
# 1. PG17 listening on 55440:
brew services start postgresql@17
# 2. Create test DB:
createdb -h 127.0.0.1 -p 55440 -U postgres cegr_test
# 3. Apply DDL + migrations (from clean clone):
PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
  -v ON_ERROR_STOP=1 -f schema/01-core.sql
PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
  -v ON_ERROR_STOP=1 -f schema/migrations/002_source_governance.sql
# 4. Run full suite:
python3 -m pytest -q -p no:cacheprovider
# Expected: 251 passed, 0 failed, 0 skipped
# 5. Build evidence pack (drops + reapplies cegr schema):
python3 scripts/build_evidence_pack.py
# Expected: exit 0; evidence_pack/manifest.json (1.1-R3G-R4)
```

## §10. 返工项 A..I 闭环（独立于 §2 原始缺陷 + §11 R4 返工）

| Item | Status | Evidence |
|---|---|---|
| **A** 缺陷编号恢复 + R2 映射 | ✅ | §2 用原始 Scheme-1 定义；§4 R2→原始→文件→测试映射 |
| **B** spike 04 重置 FAILED/BLOCKED | ✅ | `spikes/04-scanned-pdf/README.md`、`gate_thresholds.json`、§3.6 真实数字 |
| **C** 31×22=682 全网格 | ✅ | `test_full_31x22_grid_exact`（n==682）+ 缺格显式建模 |
| **D** tracked-ZIP-only 输入 | ✅ | 默认输入 tracked ZIP；zip-slip ×2；`locate_0109_in_zip`；clean-clone fail |
| **E** 逐指标周期元数据 | ✅ | `TestR3PeriodMetadata`；`comparison_basis` 移除 `Q2_ONLY` |
| **F/F-2** Schema/DB + NOT NULL | ✅ | `source_registry_id UUID NOT NULL`；39 负例 |
| **G/G-2** Builder 加固 | ✅ | `scripts/build_evidence_pack.py`（R4-3 加固）；17 测试 |
| **H/H-2** 测试纯净性 | ✅ | `tests/test_cleanliness.py`；H-2 = worktree hash 前后一致 |
| **I** Doc sync (R3) | ✅ | docs/04/05/09/11/12 + README 与代码/测试数一致 |

**A..I：9/9 完成。**

## §11. R4 Rework Closure（Codex R3 复核 → R4 返工 6 项）

Codex R3 复核判定 **REJECT**，原因 4 类：(1) skip-as-PASS 隐藏在 mandatory tests；(2) 全国年鉴证据不一致 + 准确率陈旧；(3) builder 随机 5-sample hash；(4) I-05 误归为用户决策项。

R4 返工分 6 项（5 dev rework + 1 final re-verification）：

| Item | Status | Evidence |
|---|---|---|
| **R4-1** 删除 skip-as-PASS | ✅ | `tests/test_cleanliness.py` H-2 改用 `--deselect <nodeid>`（移除 `pytest.skip("内部子进程运行，避免递归")`），断言子进程 failed=0/skipped=0/passed=parent-1；spike 00/04 删除 `pytest.skipif` 与 `if not TESSERACT_REQUIRED: pytest.skip(...)`，改为 `pytest.fail`；新增 `test_extractor_fails_when_sample_missing`、`test_extractor_fails_when_tesseract_missing`；builder 解析真实 pytest stats（skipped>0 → rc=2）；builder 强制拒绝缺失样本/工具 |
| **R4-2** 全国年鉴证据一致性 + 质量 BLOCKED 记录 | ✅ | 新建 `spikes/00-national-yearbook-table/build_per_column_accuracy.py`（22 列 + 同源 extracted.json 输入 + needs_review 校验）；重生成 `data/extracts/00-national-yearbook-table/per_column_accuracy.json`（header.extractor=spike00-national-yearbook/3.0-R3C，input_hash_sha256=9576529a881b83be...，n_observations=682，n_columns=22）；**summary.overall_verdict=BLOCKED**（needs_review=385/682=56.45% > 50% docs/08b 回滚线），**绝不假装 PASS**；新增 8 测试含 22 列覆盖、字节可重现（同一 extracted.json 输入 → 脚本产出字节一致）、BLOCKED 校验、无 cherry-picking |
| **R4-3** Evidence Builder 加固 | ✅ | 删除 `random.sample(artifacts, 5)`，改为 `verify_all_artifacts()` 逐项验证（路径唯一 + 相对 + 存在 + 大小 + SHA-256）；`EVIDENCE_PACK_TAMPER=<artifact-path>` 测试钩子模拟篡改非首 5 个 artifact → builder rc=4；`_check_hook_env_clean()` 门控 SKIP_*/FORCE_* 环境变量（除 `EVIDENCE_PACK_TEST_HOOKS=1` 外一律拒绝，rc=6）；manifest 不在自身 artifacts 列表 + role_count 之和 == artifact_count；新增 4 测试 |
| **R4-4** I-05 来源等级治理 | ✅ | `schema/migrations/002_source_governance.sql`（已 apply + log）：(a) `source_document.declared_source_level` 新列；(b) `source_level_s0_requires_verified` CHECK 约束（S0 + UNVERIFIED/PENDING/REJECTED → CheckViolation）；(c) `source_document_verification_event` 表（append-only，UPDATE/DELETE 均被 trigger 拒）；(d) `source_document_log_verification()` 触发器：每次 verification_status UPDATE → 写事件（含 verifier_id via `SET LOCAL app.verifier_id` + declared/effective 前后级别）；`source_registry/registry.csv` 新增 `declared_source_level` + `purpose_note` 列，archive.org 行 source_level S0→S3（per 用户决策）；`tests/test_source_governance.py` 21 测试；`docs/03-source-registry.md` §9 文档同步 |
| **R4-5** 文档同步 | ✅ | `docs/03-source-registry.md`：删除"production-ready extract.py / 22/22 test_extract.py"陈旧声明；§9 新增 I-05 治理章节；§4.4 archive.org S0→S3；本文件 (docs/12) 完整重写：区分 EXTERNAL BLOCKING / USER POLICY / DEV REWORK 三类；§11 新增 R4 闭环；过期数字修正（205→237 / 13→17 / 39→47 → 已回正为 39） |
| **R4-6** 最终复验 | ✅ | 见 §7（237 passed / 0 failed / 0 skipped）/ §8（policy audit）/ §9（clean-clone instructions）/ §1（最终 verdict） |

**R4-1..R4-6：6/6 完成。**

## §12. Outstanding Items — 陕西集成后的终态边界

### 12.1 EXTERNAL BLOCKING
- **无 E-1 文件获取阻塞**：陕西官方 PDF 已由用户下载上传并完成本地来源、结构、hash 验证。

### 12.2 USER POLICY（dev 不得变更）
- **P-1**：不降低 OCR 门槛（numeric ≥80% / char ≥90% / needs_review ≤30%）。
- **P-2**：不接受 1909 美国样本代表中国治理平台。
- **U-1/U-2**：陕西仅作中文 OCR 压力样本；嵌入文本层作为有噪声对照。
- **U-3**：spike 04 非 Stage 0 验收项。
- **U-4**：**已裁定 A（2026-08-24）** — Gate 0 关闭；可继续；用户授权启动 Stage 1（per `reviews/23-stage1-kickoff-20260824.md`）。Stage 1 红线：不全国抓取；不官员评分；不 DSH；不降 OCR 门槛；1909 不代表中国。

### 12.3 DEV REWORK
- 陕西来源登记、provenance、truth、image-only OCR、布局评测、14 tests 与当前态文档已完成。
- 最终 pack 数量与独立 `pack_errors=0` 以 `docs/16-e1-candidate-report-20260824.md` 的终态记录为准。

**CC 结论边界：不自动宣布 Stage 0 PASS，不进入 Stage 1。**

— End of closure matrix —
