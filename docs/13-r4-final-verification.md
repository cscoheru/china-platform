# Stage 0 Gate 0 R4 — Final Verification Report (R4-6)

> Generated 2026-08-24 after R6 rebuild; extended 2026-08-24 for the Shaanxi OCR integration; **Gate 0 CLOSED 2026-08-24 per U-4=A（per `reviews/23-stage1-kickoff-20260824.md` §1）**。
> R6 historical baseline was 237 tests and 428 artifacts. The current integration baseline is
> 251 tests; the post-integration artifact count and independent hash result are recorded in §10
> after the final rebuild. Historical command outputs below are retained as dated evidence, not
> silently rewritten.

## §0. Final Verdict

**Gate 0 CLOSED（2026-08-24，per U-4=A）**。Stage 0 不等于全 PASS；spike 00 needs_review 56% / 1909 eval FAILED / 陕西 research-only 等质量债由 Stage 1 继续诚实记录。

- Stage 0 维持 BLOCKED（口径需待 docs/11/12/13 全部落地后由 Cursor 复验 + 用户最终确认）
- 历史 E-1（中文扫描 PDF 缺失）：**已不再作为 Stage 0 BLOCKED 根因**（per `docs/15` §4a U-3 用户裁定 + `reviews/09` §3 预审确认）；spike 04 转为非验收项（OCR 管线压力样本，研究追踪）
- User policy（dev 不得变更）：P-1（不降低 OCR 门槛）+ P-2（不接受 1909 美国样本代表中国）— 不变
- Dev rework: 6/6 + 9/9 + 5/5 闭环（R4-1..R4-6 + R5-A..R5-I + R6-A..R6-E；详见 §1.1 与 §8）

## §1. Worktree 0-Pollution Proof

| Metric | Value |
|---|---|
| WORKTREE_HASH_BEFORE (pre-test+pre-builder) | `2f082b0dea89fb098eea9c1b3d3ca3d375211639255e020be65f9e24b296383f` |
| WORKTREE_HASH_AFTER (post-test+post-builder) | `2f082b0dea89fb098eea9c1b3d3ca3d375211639255e020be65f9e24b296383f` |
| MATCH | ✅ True |
| Files hashed | 480（排除 __pycache__ / .git / .pytest_cache / .pyc / .pyo） |
| Hash algorithm | SHA-256 over (相对路径 \x00 字节内容 \x00) 串联 |

零污染：整套 pytest + builder 运行后磁盘真实字节与运行前一致。
(H-2 = `test_suite_leaves_no_worktree_trace_h2` 在子进程内已通过相同逻辑的二次确认)

### §1.1 R5-A 可复现性证据（Cursor §9 命令链独立复跑，2026-08-23）

> **目标**：证明默认 `python3 -m pytest -q` 不依赖人工手动 apply 002 也能通过；
> 默认流程若只 apply 01-core.sql，governance 测试必失败。

```bash
# Cursor §9.B：仅 apply 01-core → governance 应红（21 failed）
$ PGPASSWORD=postgres psql ... -c "DROP SCHEMA IF EXISTS cegr CASCADE"
$ PGPASSWORD=postgres psql ... -f schema/01-core.sql
$ STAGE0_SKIP_SCHEMA_APPLY=1 python3 -m pytest -q tests/test_source_governance.py
21 failed in 1.24s   # ✅ 期望：declared_source_level 列缺失

# Cursor §9.C：apply 002 → 60 passed（21 governance + 39 schema_negative）
$ PGPASSWORD=postgres psql ... -f schema/migrations/002_source_governance.sql
$ python3 -m pytest -q tests/test_source_governance.py tests/test_schema_negative.py
60 passed in 0.42s   # ✅

# Cursor §9.A：DROP 后**不手动 apply**，默认 pytest（含 conftest）自动 apply
$ PGPASSWORD=postgres psql ... -c "DROP SCHEMA IF EXISTS cegr CASCADE"
$ python3 -m pytest -q -p no:cacheprovider
237 passed in 342.06s   # ✅ conftest autouse session fixture 链式 apply 全部 SQL
```

**结论**：Cursor §9 三个步骤全部独立复跑成功。默认 pytest 不再依赖人工手动 apply 002；
schema apply 链已纳入 `tests/conftest.py`（autouse session fixture）+ builder `run_db_apply()`
（R5-A）。R4-5/R4-6 文档同步已闭环；R26 风险已闭环。

### §1.2 R5 + R6 修改摘要（便于下一轮复验方一眼可见）

> 本节是 §8 R5/R6 闭环表的精简索引。Cursor `04` §3.1/§3.2 指出的"7 文件哈希过期 + 文档残留错数"已在 R6-B/C 全部清零。完整证据见 §8。

| 维度 | R5 修改 | R6 修复 | 当前状态 |
|---|---|---|---|
| **apply 链** | conftest autouse + builder `run_db_apply()` 链式 apply | 全集 237 默认通过 | ✅ 已闭环 |
| **builder 收录** | R6: migration + conftest roles | R6 历史 pack 428；陕西集成新增 `spikes/**/*.py`，确保共同依赖 `ocr_text_layout.py` 不漏包；当前数见 §10 | ✅ 契约扩展 |
| **pack 与磁盘一致性** | schema_version=1.1-R3G-R4 + 002.sql | R6 历史 0 mismatch；陕西集成后重新验证见 §10 | ⏳ 以 §10 为终态 |
| **test composition** | R6 历史 237 = 31+21+20+30+29+18+11+17+39+21 | 陕西新增 14，使 spike04 18→32、总计 237→251 | ✅ 公式已同步 |
| **docs/03 章节** | §4.1-4.3 测试数 20/29/30；§4.4 0%/3.7%/100% BLOCKED；§9.5 澄清 CSV 无 verification_status | – | ✅ 已闭环 |
| **docs/09 风险** | 新增 R22-R26（R4/R5 返工） | – | ✅ 已闭环 |
| **eval_report 相对路径** | `_to_repo_relative()` 写入 eval_report.json | – | ✅ 已闭环 |
| **复跑证据** | Cursor `03` §9.B/C/A 三步 | 含 H-2 全集 237 passed in 362.71s（R6-A） | ✅ 已闭环 |

**复验方只需读 §1.1 + §1.2 + §8 即可判断 R5/R6 全部返工闭环，无需翻 03/04 全文。**

## §2. Historical R6 Full Pytest Run (237 baseline; superseded by §10)

```
$ EVIDENCE_PACK_DIR=/tmp/r46_evidence_pack PYTHONDONTWRITEBYTECODE=1 \
  python3 -m pytest -q -p no:cacheprovider --tb=line
237 passed in 356.81s (0:05:56)
```

| Suite | Tests | Status |
|---|---|---|
| spikes/00-national-yearbook-table | 31 | ✅ (R4-2 新增 8：22 列覆盖 + 字节可重现 + needs_review BLOCKED 校验 + 无 cherry-picking) |
| spikes/00-provincial-yearbook | 21 | ✅ |
| spikes/01-national-yearbook | 20 | ✅ |
| spikes/02-provincial-yearbook | 30 | ✅ |
| spikes/03-municipal-bulletin | 29 | ✅ |
| spikes/04-scanned-pdf | 18 | ✅ (R4-1 移除 skip，缺失样本/tesseract → fail) |
| tests/test_cleanliness.py | 11 | ✅ (含 H-2 子进程反递归) |
| tests/test_evidence_builder.py | 17 | ✅ (R4-3 新增 4：refuse_skip/refuse_force/verify_every/path_unique) |
| tests/test_schema_negative.py | 39 | ✅ (注：R3 期间曾记为 47 为 R3 误计；现以 `python3 -m pytest --collect-only -q` 实测 39 为准) |
| tests/test_source_governance.py | 21 | ✅ (R4-4 新增；含 S1-S4 parametrize) |
| **Total** | **237** | **✅ 237 passed / 0 failed / 0 skipped** |

## §3. PG DDL Apply (Fresh Empty DB)

```bash
PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
  -v ON_ERROR_STOP=1 -c "DROP SCHEMA IF EXISTS cegr CASCADE"
PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
  -v ON_ERROR_STOP=1 -f schema/01-core.sql
PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
  -v ON_ERROR_STOP=1 -f schema/migrations/002_source_governance.sql
```

Result: exit 0；39 表 + 13 enum + 1 增量表（source_document_verification_event）+
1 新列（declared_source_level）+ 1 CHECK 约束（source_level_s0_requires_verified）
+ 1 索引（idx_src_verify_event_doc）+ 3 触发器（log_verification, event_no_update, event_no_delete）。

所有 DB 负例（test_schema_negative.py 39 项 + test_source_governance.py 21 项）全部通过。

## §4. Historical R6 Builder Real Run (428 baseline; superseded by §10)

```bash
$ EVIDENCE_PACK_DIR=/tmp/r6_evidence_pack python3 scripts/build_evidence_pack.py
Wrote /tmp/r6_evidence_pack/manifest.json: 428 artifacts
verified 428 artifacts (full)
```

| Field | Value |
|---|---|
| Exit code | 0 |
| schema_version | `1.1-R3G-R4` |
| artifact_count | 428 |
| Manifest role_count 之和 == artifact_count | ✅ |
| Manifest 自身不在 artifacts 列表 | ✅ |
| Builder wrote to EVIDENCE_PACK_DIR (temp) | ✅ `/tmp/r6_evidence_pack/manifest.json` |
| 仓库 evidence_pack/manifest.json 同步覆盖 | ✅（R6 重建后与磁盘 0 mismatch） |

## §5. Historical R6 Independent Hash Re-Verification (superseded by §10)

```python
# 独立于 builder，重新读 manifest 并对每个 artifact 算 SHA-256
$ python3 -c "<see R4-6 script>"
artifacts_re_verified=428
errors=0
ALL ARTIFACTS INDEPENDENTLY RE-VERIFIED OK
```

逐项校验：
- ✅ 大小匹配（每个 artifact 的 size_bytes 与磁盘 stat 一致）
- ✅ SHA-256 匹配（每个 artifact 的 sha256 与磁盘实际哈希一致）
- ✅ 路径唯一（428 个 path 无重复）
- ✅ 相对路径（无 / 开头的路径）
- ✅ 禁止前缀（无 /Users/、/home/、/tmp/）
- ✅ manifest 不在自身列表
- ✅ role_count 之和 == artifact_count

## §6. Mandatory-Test Policy Audit (R4-1 invariants)

| Policy | Status |
|---|---|
| pytest.skip in mandatory tests | ✅ 0（spike 04/00 删除所有 skip；H-2 用 --deselect 替代） |
| Missing sample → fail | ✅（spike 00/04 用 pytest.fail 替代 pytest.skip） |
| Missing tesseract → fail | ✅（spike 00 用 pytest.fail；monkeypatch.setenv("PATH") 模拟） |
| Skipped count > 0 in real pytest → rc != 0 | ✅（builder 解析 stdout 统计 skipped > 0 → rc=2） |
| Force/skip hook without TEST_HOOKS=1 → refused | ✅（builder rc=6 + 不写 manifest） |
| Tampered artifact → builder rc != 0 | ✅（EVIDENCE_PACK_TAMPER 模拟非首 5 → rc=4） |
| Random 5-sample hash → removed | ✅（R4-3 verify_all_artifacts 全量逐项） |
| Wall-clock field in manifest | ✅ 不存在（generated_at_utc/wall_clock_now 缺位） |
| Absolute path in manifest | ✅ 不存在（无 /Users/、/home/、/tmp/） |
| Schema DDL applied to fresh empty PG | ✅（schema/01-core.sql + migration 002 全部 exit 0） |
| All DB negative tests pass | ✅（39 schema + 21 governance = 60 用例） |
| Worktree 0 pollution | ✅（HASH_BEFORE == HASH_AFTER） |

## §7. Schema SHA-256 (Post-R4-4)

| File | SHA-256 |
|---|---|
| `schema/01-core.sql` | `09aa46f9f6713b17d7e7171799a769c600f4b6eb26f37631039ffb77b7e089ea` |
| `schema/migrations/002_source_governance.sql` | `c41161a86fb68e882bc4925ebec758f2b2616d0f4914b023dc8c5a5ec85e168b` |
| `schema/migrations/002_source_governance.log` | `b36f6a45b6126ad70644d2bceb119d5ff05246fdcf3522bda0da8fcc081d34a2` |
| `schema/migrations/001_create_core.log` | `646c545f2b22dab610063202ae907791500c38988b411f154e4c6dc1b31d77cc` |

## §8. R4/R5/R6 Rework 闭环总结

### R4-1..R4-6（R4 返工 6 项）

| ID | Status | 关键证据 |
|---|---|---|
| R4-1 | ✅ | `tests/test_cleanliness.py` H-2 `--deselect`；spike 00/04 删除 skip；builder 解析 stats；新增 spike 00 负例 |
| R4-2 | ✅ | `build_per_column_accuracy.py` + 22 列覆盖；`per_column_accuracy.json` 重生成（682 obs / 22 cols / needs_review=56.45% / overall_verdict=BLOCKED）；8 新测试含字节可重现 |
| R4-3 | ✅ | 删除 random.sample(5)；`verify_all_artifacts()` 全量；`EVIDENCE_PACK_TAMPER` 负例；HOOK_ENV_VARS 门控；4 新测试 |
| R4-4 | ✅ | migration 002：declared_source_level 列 + S0 CHECK + verification_event 审计表 + 触发器；21 测试；registry.csv S0→S3 (archive.org) |
| R4-5 | ✅ | docs/03 删除陈旧声明；§9 I-05 章节；docs/11 §7.3 R4 闭环 + I-05 ✅；docs/12 完整重写（EXTERNAL/USER/DEV 三类）；docs/00/08b/10 修正文件名引用 |
| R4-6 | ✅ | 本文件 |

### R5-A..R5-I（R5 返工 9 项，对应 Cursor `03` §3 真问题）

| ID | Status | 关键证据 |
|---|---|---|
| R5-A | ✅ | `tests/conftest.py` autouse session fixture：DB 可达时 DROP+链式 apply 01-core + migrations/*.sql；builder `run_db_apply()` 同款链式 apply |
| R5-B | ✅ | builder glob 加 `schema/migrations/*.sql`；`classify()` 增 `schema_migration_ddl` 角色 |
| R5-C | ✅ | 仓库 `evidence_pack/manifest.json` 现 428 artifacts, schema_version=1.1-R3G-R4, 含 002.sql；Cursor `04` 指出的 7 文件哈希过期已在 R6-B 重建后清零 |
| R5-D | ✅ | collect 237 = 31+21+20+30+29+18+11+17+39+21（公式 + §2 表对齐）；R6-C 二次扫描清 24/47 残留 |
| R5-E | ✅ | docs/11 文首 / §1.3 / §1.4 / §9.4 / §9.5 / §10 全部 237 + I-05 已闭环；§1.5 风险表加 R22–R26 |
| R5-F | ✅ | docs/03 §4.1-4.3 测试数 20/29/30；§4.4 改 0% / 3.7% / 100% BLOCKED；§9.5 澄清 CSV 无 verification_status |
| R5-G | ✅ | docs/09 加 R22（skip-as-PASS）/ R23（证据一致性）/ R24（builder 加固）/ R25（I-05 治理）/ R26（默认 apply 链 + 文档同步）；docs/12 §6 指向 R22-R25 |
| R5-H | ✅ | `spikes/04-scanned-pdf/evaluate_04.py` `_to_repo_relative()`；`eval_report.json` truth_table + extracted_file 均为相对路径，无 /Users/ |
| R5-I | ✅ | Cursor `03` §9.B/C/A 三步全部独立复跑：仅 01-core → 21 failed；apply 002 → 60 passed；默认 pytest → 237 passed（conftest 自动 apply） |

### R6-A..R6-E（R6 返工 5 项，对应 Cursor `04` §3.1/§3.2 残留）

| ID | Status | 关键证据 |
|---|---|---|
| R6-A | ✅ | 全集 pytest 复跑：237 passed in 362.71s（含 H-2 子进程 worktree proof）；**P1 独立留档**：`/tmp/stage0-pytest-237.log`，237 passed in 349.77s（PG17 @55440；2026-08-24 commit f475717 后；由 Cursor `06` 独立读取校验） |
| R6-B | ✅ | 冻结文档后重建 `evidence_pack/manifest.json`：428 artifacts, schema_version=1.1-R3G-R4，独立逐项 SHA-256 重算 = **0 mismatch**（Cursor `04` §3.1 7 文件哈希过期已清零） |
| R6-C | ✅ | 残留错数清零：docs/13 §3/§6 47→39；docs/13 §4 425→428；docs/12 §7 24→31；docs/11 §1.3 24/24→31/31；docs/11 §1.1/§3.5/§10 21→26；docs/12 §2 I-04 R13-R21→R13-R26 |
| R6-D | ✅ | builder glob 加 `tests/conftest.py`；`classify()` 增 `test_conftest` 角色；conftest.py 入 pack（sha 91fe765d7711） |
| R6-E | ✅ | 本节补全 R4/R5/R6 修改摘要，便于下一轮复验方一眼看到 apply 链 + 相对路径 + 重建契约 |

**R4-1..R4-6 + R5-A..R5-I + R6-A..R6-E = 6+9+5 = 20 项 dev rework 全部闭环。**

## §9. Outstanding Items（陕西集成后）

### EXTERNAL BLOCKING
- **无 E-1 文件获取阻塞**：用户已通过全国人大法规库官方直链下载并上传陕西四页扫描 PDF；CC 已验证本地来源元数据、magic、结构、size 与 hashes。

### USER POLICY（dev 不得变更）
- **P-1**：不降低 OCR 门槛（numeric ≥80% / char ≥90% / needs_review ≤30%）
- **P-2**：不接受 1909 美国样本代表中国治理平台
- **U-1/U-2**：陕西是中文 OCR 压力样本；嵌入旧 OCR 文本层作有噪声对照
- **U-3**：spike 04 非 Stage 0 验收项
- **U-4**：等待 §10 证据经 Cursor 复验后由用户裁定

### DEV REWORK
- R4/R5/R6 历史 20 项闭环不变
- 陕西集成新增代码、14 tests、provenance/source registry/docs 与 pack 完整性修复；当前验证见 §10

**Stage 0 当前判定权**：CC 不自动宣布 PASS；等待 Cursor 复验 + 用户 U-4。不进入 Stage 1。

## §10. Shaanxi OCR Integration Verification（当前终态）

本节在最终全集 pytest、evidence pack rebuild 与独立 SHA-256 复算后填写；详细验收入口同时写入 `docs/16-e1-candidate-report-20260824.md`。

| Field | Result |
|---|---|
| Source PDF | `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf`; SHA-256 `f34b2e57...71488`; 4 pages |
| OCR evaluation | Han 93.93%; all non-whitespace 90.05%; needs_review 1/4=25%; numeric N/A |
| Research result | `MEETS_UNCHANGED_APPLICABLE_THRESHOLDS` |
| Stage 0 effect | `none_per_U3_non_gating_research_sample` |
| Full pytest | **251 passed / 0 failed / 0 skipped in 450.57s** |
| Test pollution proof | `9b874a09...784a8e` (pre-manifest-update) → `6e43c318...3deaf46` (post-manifest-update); 561 files; **差异仅 `evidence_pack/manifest.json`**（本次 rebuild 的预期产物） |
| Evidence pack | **440 artifacts**；role_count sum=440；schema_version=`1.1-R3G-R4`；陕西 `research_non_gating_extracted_artifact` × 1 + `research_non_gating_eval_report` × 1；`reviews/`=0 |
| Independent pack validation | **artifacts_reverified=440; pack_errors=0**（size/SHA-256/relative/unique paths/role_count/manifest 自排除/禁止前缀） |
| Static checks | PY_COMPILE_OK=7/7；JSON_OK=4/4；git diff --check exit=0；registry.csv 7 行 × 18 列 |
| Code review tooling | **BLOCKED_BY_TOOLING**：3 次 `feature-dev:code-reviewer` 子代理 API stream error；`codex review --uncommitted` 仅 transport errors 无 findings；详见 `docs/16 §6.2` |
| Verdict | **等待 Cursor 复验 + user U-4；CC 不自动给 PASS** |

— End of current verification report —
