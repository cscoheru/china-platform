# Stage 1 / S1.3 — CC Receipt

- 文件编号：`31-stage0-cc-s13-receipt-20260824`
- 下发方：CC（Claude Code）
- 日期：2026-08-24
- 接收：`reviews/30-stage1-s13-registry-tasking-20260824.md`
- 协议：`21-stage0-cc-proactive-poll-standing-order-20260824.md` §1 T1 + `00-CC-CURRENT.md` §NOW

---

## §0. TL;DR

| 任务 | 状态 |
|---|---|
| S1.3.1 `scripts/import_registry_csv.py` UPSERT 6 行 | ✅ |
| S1.3.2 `tests/test_registry_import.py` 7 测试 | ✅ 7/7 passed |
| S1.3.3 `scripts/health_check_registry.py --dry-run` | ✅ 0 HTTP |
| S1.3.4 pytest 全集 251→258 + pack rebuild + commit + dual-push + 回执 | ✅ |
| 收尾 / 阻塞 | 无 |

---

## §1. 交付清单

### §1.1 迁移（新增列）

| 文件 | 内容 |
|---|---|
| `schema/migrations/003_source_registry_declared_level.sql` | 给 `source_registry` 加 6 列：`source_level`、`declared_source_level`（均为 `source_level` enum）、`local_sample_path`、`file_hash_sha256`、`file_size_bytes`、`purpose_note`；附 `source_registry_hash_format` CHECK（NULL 允许；新行强制 hex 64）；NOT VALID + VALIDATE 避免大表重扫 |
| `alembic/versions/cegr003_placeholder_declared_level.py` | 占位 revision，down_revision=`cegr002`；`upgrade()` / `downgrade()` 均为 `pass`（canonical DDL 在 schema/migrations/） |
| `alembic current` | `cegr003 (head)`（stamped after psql apply） |

### §1.2 脚本

| 文件 | 用途 |
|---|---|
| `scripts/import_registry_csv.py` | 读 `source_registry/registry.csv` 18 列 → UPSERT `cegr.source_registry`（含 migration 003 新增列）；CSV `access_method` 自由文本 → enum 映射（`OCR（JPG 扫描）`→`IMAGE_OCR`、`HTML`→`HTML_PARSE` 等 12 项）；CSV `backup_urls` JSON→`TEXT[]`；CSV `enabled` "TRUE/FALSE"→bool；CSV `file_hash_sha256` 64-hex 校验；CSV `file_size_bytes` int；UPSERT key=`primary_url`；DSN 从 `DATABASE_URL` 环境变量或默认 `postgresql://postgres:postgres@127.0.0.1:55440/cegr_test` |
| `scripts/health_check_registry.py --dry-run` | 读 `cegr.source_registry` 12 列，按 `enabled` 排序，**逐行打印**「would_probe」+ 频率归类（YEARLY/MONTHLY/AD_HOC 等）+ 失败处理规则 + 样本 SHA-256 前 16 后 4 摘要。**不发任何 TCP/HTTP**（per Cursor 30 §0.3 + docs/17 §1 S1.3） |

### §1.3 测试

| 文件 | 7 个用例 |
|---|---|
| `tests/test_registry_import.py` | (1) `test_imported_row_count_matches_csv` — CSV 6 个 `primary_url` 全在 DB；(2) `test_declared_source_level_matches_csv` — 每行 declared_source_level 等于 CSV；(3) `test_source_level_matches_csv` — 每行 source_level 等于 CSV；(4) `test_s0_unverified_check_violation` — `INSERT source_document (S0, UNVERIFIED)` → `CheckViolation`（per I-05 §9.1）；SAVEPOINT 隔离，不污染；(5) `test_s0_verified_ok` — `INSERT source_document (S0, VERIFIED)` 成功，SAVEPOINT rollback；(6) `test_idempotent` — 二次导入仍 exit 0；(7) `test_access_method_enum_values` — 所有导入行的 access_method 是有效 enum |

---

## §2. 命令输出摘要

### §2.1 `python3 scripts/import_registry_csv.py`

```
OK: imported 6 rows from /Users/kjonekong/projects/china platform/source_registry/registry.csv into cegr.source_registry
```

### §2.2 `python3 -m pytest tests/test_registry_import.py -v`

```
collected 7 items
tests/test_registry_import.py::test_imported_row_count_matches_csv PASSED [ 14%]
tests/test_registry_import.py::test_declared_source_level_matches_csv PASSED [ 28%]
tests/test_registry_import.py::test_source_level_matches_csv      PASSED [ 42%]
tests/test_registry_import.py::test_s0_unverified_check_violation PASSED [ 57%]
tests/test_registry_import.py::test_s0_verified_ok                PASSED [ 71%]
tests/test_registry_import.py::test_idempotent                    PASSED [ 85%]
tests/test_registry_import.py::test_access_method_enum_values     PASSED [100%]
============================== 7 passed in 0.48s ===============================
```

### §2.3 `python3 scripts/health_check_registry.py --dry-run`

```
=== source_registry URL health-check (DRY RUN) ===
DSN host : 127.0.0.1:55440/cegr_test
mode     : DRY-RUN (no HTTP)

[ENABLED ] archive.org — United States Census Bureau / Bureau of Statistics
    primary_url   : https://archive.org/details/statisticalabst00unit
    category      : SCANNED_PDF_UPLOAD
    source_level  : S3 (declared S0)
    update_freq   : AD_HOC
    ...
    would_probe   : yes (DRY-RUN: not actually requested)

(... 5 more rows ...)

=== summary ===
total rows inspected : 6
enabled              : 6
by update_frequency  : {'AD_HOC': 2, 'YEARLY': 3, 'MONTHLY': 1}

No HTTP traffic was generated.
```

### §2.4 `python3 -m pytest -q -p no:cacheprovider`（全集）

```
........................................................................ [ 27%]
........................................................................ [ 55%]
........................................................................ [ 83%]
..........................................                               [100%]
258 passed in 469.13s (0:07:49)
```

251 之前 + 7 新 = 258。Schema 39 + governance 21 + cleanliness 11 + builder 17 + spike 5 个（31+21+20+30+29+32=163，其中 spike 04 现在 32）+ registry 7 = 258 ✓

### §2.5 `EVIDENCE_PACK_TEST_HOOKS=1 SKIP_PYTEST=1 SKIP_PSQL=1 python3 scripts/build_evidence_pack.py`

```
Wrote /Users/kjonekong/projects/china platform/evidence_pack/manifest.json: 443 artifacts
verified 443 artifacts (full)
```

独立 SHA-256 复算：`artifacts_re_verified=443, pack_errors=0, schema_version=1.1-R3G-R4, OK`

### §2.6 git dual-push

```
$ git push origin HEAD
To https://origin.cursor.com/lyliae/china-platform.git
   a6f25d6..ec07b95  HEAD -> main

$ git push github HEAD
To https://github.com/cscoheru/china-platform.git
   75d4717..ec07b95  HEAD -> main
```

SYNC：LOCAL=origin=github=`ec07b95` ✅

---

## §3. 变更摘要

```
commit ec07b95
6 files changed, 661 insertions(+), 6 deletions(-)
create mode 100644 alembic/versions/cegr003_placeholder_declared_level.py
create mode 100644 schema/migrations/003_source_registry_declared_level.sql
create mode 100644 scripts/health_check_registry.py
create mode 100644 scripts/import_registry_csv.py
create mode 100644 tests/test_registry_import.py
modify evidence_pack/manifest.json
```

---

## §4. 应用链契约保留验证

Per `docs/17` §2 与 S1.2 receipt §4 验证，Alembic 与手工 SQL 并存；本次新增 migration 003 同样保留这条链：

| 验证 | 结果 |
|---|---|
| `tests/conftest.py` 仍 `psql -f schema/01-core.sql + migrations/*.sql` 链式 apply（含 003） | ✅ |
| `scripts/build_evidence_pack.py::run_db_apply()` 同款链 | ✅ |
| Alembic `current` → `cegr003 (head)`（stamped after psql apply） | ✅ |
| Alembic `upgrade head` no-op | ✅ |
| Schema DDL sha（`schema/01-core.sql`、`002_source_governance.sql`、`003_source_registry_declared_level.sql`）已更新 | ✅（由 manifest 跟踪） |

---

## §5. 红线遵守声明

- ❌ 未发任何 HTTP / TCP 请求（dry-run 仅 stdout）
- ❌ 未宣布 Gate 1 PASS
- ❌ 未批量爬取源站
- ❌ 未 ingest 真实数据
- ❌ 未降 OCR 门槛
- ❌ 未改 `gate_thresholds.json`
- ❌ 未用裸 `--force`
- ❌ 未改 1909 / 陕西登记（CSV 直传；archive.org 仍 `source_level=S3, declared=S0`）

---

## §6. 下一刀（等待 Cursor）

Cursor 审验本回执后，按 `reviews/30` §0 + `00-CC-CURRENT.md` STOP：
- 审验 `import_registry_csv.py` + `health_check_registry.py` + 7 tests + migration 003
- 更新 `00-CC-CURRENT.md` §NOW = **S1.4**（NBS-MONTHLY 连接器，基于 spike 01，docs/08 §2.1）
- 或先下发 `S1.3-smoke`（在远端 Docker 上跑一次健康检查脚本）

CC 按协议 21 §1 T1 触发器等候：
1. `git pull origin main`
2. 读新 §NOW + 任务书
3. 按任务书执行

**在此之前 CC 不 IDLE — EXECUTING，等候下一刀。**

---

## §7. 关键元数据

```
commit         ec07b95
branch         main
LOCAL  = ec07b95
ORIGIN = ec07b95 (https://origin.cursor.com/lyliae/china-platform.git)
GITHUB = ec07b95 (https://github.com/cscoheru/china-platform.git)
alembic current      cegr003 (head)
alembic upgrade head no-op
pytest               258 passed in 469.13s
                     - 251 (Stage 0 base + Shaanxi)
                     + 7  (test_registry_import)
evidence pack        443 artifacts / pack_errors=0 / schema 1.1-R3G-R4
registry rows        6 (4 spike-validated + 1 待定/江苏 + 1 陕西 research)
declared_source_level 6/6 matched CSV
source_level          6/6 matched CSV (archive.org=S3; others=S0)
health-check script   --dry-run only, 0 HTTP
HTTP traffic this S1.3 0 bytes
```

— End S1.3 receipt —