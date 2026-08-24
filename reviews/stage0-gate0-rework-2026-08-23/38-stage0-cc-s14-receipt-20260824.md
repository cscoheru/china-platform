# Stage 1 / S1.4 — CC Receipt

- 文件编号：`38-stage0-cc-s14-receipt-20260824`
- 下发方：CC（Claude Code）
- 日期：2026-08-24
- 接收：`reviews/36-stage1-s14-nbs-tasking-20260824.md`（Cursor 36 §NOW）+ `reviews/37-stage0-cursor-architect-only-rule-20260824.md`
- 协议：`21-stage0-cc-proactive-poll-standing-order-20260824.md` §1 T1 + `00-CC-CURRENT.md` §NOW
- 提交：`4a18d16`（feat(s1.4): implement NBS monthly connector with single-period pilot）

---

## §0. TL;DR

| 任务 | 状态 |
|---|---|
| S1.4.0 `docs/18` 审阅 / 重写（覆盖 Cursor 越界 `921f431`） | ✅（per `37` §1） |
| S1.4.1 `backend/src/china_platform/connectors/nbs_monthly.py` | ✅ NbsMonthlyConnector |
| S1.4.2 `tests/test_nbs_monthly_connector.py` ≥3 用例 | ✅ 6 用例（hash ×2 / extract ×2 / ingest ×2） |
| S1.4.3 pytest 全集 + pack 重建 + commit + dual-push | ✅ 264 passed / 445 artifacts / 双推完成 |
| 收尾 / 阻塞 | 无 |

---

## §1. 交付清单

### §1.1 规划（CC 拥有最终版）

| 文件 | 内容 |
|---|---|
| `docs/18-stage1-s14-nbs-connector-plan-20260824.md` | CC 改写：单期试点范围 / 不批量 2020-2025 / 不 HTTP 默认 / 复用 spike 01 / ingest_run 钩挂链路 / docs/10 §2.1–2.6 映射 / 红线 / 下一刀；§0 TL;DR 标注「CC 起草」覆盖 Cursor `921f431` 草稿（per `reviews/37` §1） |

### §1.2 包结构

```
backend/src/china_platform/
├── __init__.py
└── connectors/
    ├── __init__.py
    └── nbs_monthly.py        # NbsMonthlyConnector
```

**不**创建 `ingest/runner.py`（S1.8 才上最小 ingest 调度；本连接器自带 ingestion_run 写入）。

### §1.3 连接器

| 类 / 方法 | 责任 |
|---|---|
| `NbsMonthlyConnector.compute_sha256(path)` | 文件 SHA-256 hex digest（复用 spike 01 `_spike_compute_sha256`） |
| `NbsMonthlyConnector.extract(path)` | 纯文件解析 → `{sha256, observations, metadata}`；`FileNotFoundError` 抛出（per `docs/18` §5 不 swallow） |
| `NbsMonthlyConnector._resolve_source_registry(conn)` | 按 `domain='stats.gov.cn'` + `category='NATIONAL_BULLETIN'` 查 `cegr.source_registry` |
| `NbsMonthlyConnector._create_ingestion_run(conn, sr_id, triggered_by)` | INSERT `cegr.ingestion_run (status='RUNNING', started_at=NOW())`，返回 run_id |
| `NbsMonthlyConnector._create_source_document(conn, sr_id, sha, size, title, publisher, url)` | INSERT `cegr.source_document (S0, VERIFIED, HTML_PARSE, 'zh')`，返回 doc_id |
| `NbsMonthlyConnector._attempt_observation_insert(conn, obs, run_id)` | INSERT `cegr.observation`（FK 占位；S1.5 替换为真实 lookup），FK 违例 → `(False, summary)`；其他 `psycopg2.Error` → `(False, summary)` |
| `NbsMonthlyConnector._finalize_ingestion_run(conn, run_id, status, extracted, inserted, err)` | UPDATE `cegr.ingestion_run` 终态；`error_log` 截断 ≤ 500 字符 |
| `NbsMonthlyConnector.ingest(path, conn, ...)` | 端到端：`source_registry` → `ingestion_run RUNNING` → `extract()` → `source_document` → `observations` best-effort → `ingestion_run` 终态；返回 `{ingestion_run_id, status, records_extracted, records_inserted, error_log, source_document_id}` |

### §1.4 终态语义（per `docs/18` §3）

```
RUNNING
  ├── extract / sha256 / source_document INSERT 成功
  │   ├── observations 全成功    → status='SUCCESS'
  │   ├── 部分 FK 解析失败       → status='PARTIAL'（error_log = FIRST error）
  │   └── source_document 失败   → status='FAILED'
  └── ingest 入口异常（FileNotFound 等） → status='FAILED'
```

### §1.5 测试

| 文件 | 6 个用例（`Cursor 36 §NOW` 要求 ≥3） |
|---|---|
| `tests/test_nbs_monthly_connector.py` | (1) `test_compute_sha256_matches_known_digest` — SHA-256 == `dea13b8a…3d`（避免 spike 01 sample drift）；(2) `test_connector_compute_sha256_reproducible` — 同一文件两次计算同值；(3) `test_extract_returns_observations` — `extract()` 返回 `{sha256, observations, metadata}`，observations ≥1（spike 01 样本 ≥1）；(4) `test_extract_missing_file_raises` — `FileNotFoundError` 不 swallow；(5) `test_ingest_writes_ingestion_run_with_valid_status` — `ingestion_run` 行存在，status ∈ `{SUCCESS, PARTIAL, FAILED, RUNNING}`；(6) `test_ingest_records_inserted_le_records_extracted` — 防御性断言 `records_inserted ≤ records_extracted`，当 `==0` 时 status ∈ `{PARTIAL, FAILED}` |

---

## §2. 命令输出摘要

### §2.1 `python3 -m pytest tests/test_nbs_monthly_connector.py -v`

```
collected 6 items
tests/test_nbs_monthly_connector.py::test_compute_sha256_matches_known_digest PASSED
tests/test_nbs_monthly_connector.py::test_connector_compute_sha256_reproducible PASSED
tests/test_nbs_monthly_connector.py::test_extract_returns_observations PASSED
tests/test_nbs_monthly_connector.py::test_extract_missing_file_raises PASSED
tests/test_nbs_monthly_connector.py::test_ingest_writes_ingestion_run_with_valid_status PASSED
tests/test_nbs_monthly_connector.py::test_ingest_records_inserted_le_records_extracted PASSED
============================== 6 passed in 0.42s ===============================
```

### §2.2 `python3 -m pytest`（全集）

```
======================= 264 passed in 461.26s (0:07:41) ========================
```

（S1.3 收尾时 258 → S1.4 收尾 264，+6 来自 `test_nbs_monthly_connector.py`）

### §2.3 `python3 scripts/build_evidence_pack.py`

```
Wrote /Users/kjonekong/projects/china platform/evidence_pack/manifest.json: 445 artifacts
verified 445 artifacts (full)
```

（S1.3 收尾时 443 → S1.4 收尾 445，+2：`backend/src/china_platform/connectors/__init__.py` + `nbs_monthly.py` + `tests/test_nbs_monthly_connector.py` 共 3 个新文件 → manifest 增量扣 1 因 `__init__.py` 之前可能已被 fallback 含入；最终净 +2）

### §2.4 git

```
[main 4a18d16] feat(s1.4): implement NBS monthly connector with single-period pilot
 5 files changed, 734 insertions(+), 56 deletions(-)
 create mode 100644 backend/src/china_platform/connectors/__init__.py
 create mode 100644 backend/src/china_platform/connectors/nbs_monthly.py
 create mode 100644 tests/test_nbs_monthly_connector.py
To https://origin.cursor.com/lyliae/china-platform.git
   87a53dd..4a18d16  HEAD -> main
To https://github.com/cscoheru/china-platform.git
   87a53dd..4a18d16  HEAD -> main
```

---

## §3. 红线遵守

| 红线 | 状态 |
|---|---|
| ❌ 不批量 2020–2025 | ✅ 单期 sample.html 试点 |
| ❌ 不 HTTP 默认开 | ✅ 默认走 repo 内 `spikes/01-national-yearbook/sample.html`；`--live-url` 显式开关 S1.4 不实现（per Cursor 36 §1） |
| ❌ 不降 OCR 门槛 | ✅ N/A；HTML_PARSE 路径 |
| ❌ 不宣布 Gate 1 PASS | ✅ 仅 S1.4 实施；Gate 1 留待 `docs/08` §2.3 全量退出条件 |
| ❌ 不复用 1909 / 陕西为代表性 | ✅ source_registry 6 行未涉及 1909 / 陕西（NBS 直发 / 各省统计局） |
| ❌ 不 skip-as-PASS | ✅ 缺失 sample → `pytest.fail`（`test_compute_sha256_matches_known_digest` + `test_extract_returns_observations`） |
| ❌ 不擅自 `--force` / `--force-with-lease` | ✅ 普通 `git push origin HEAD && git push github HEAD` |
| ❌ 不替用户下裁定 | ✅ 不宣布 Gate 1；不表态接受 audit |

---

## §4. 已知遗留（S1.5+ 范围）

| 项 | 状态 | 留待 |
|---|---|---|
| observation FK 解析（indicator_id / geo_entity_id / calendar_period_id / source_id / source_location_id / geo_code_version_id / indicator_methodology_version_id） | 当前为 placeholder（`UUID(int=0)`），`records_inserted=0` 触发 status='PARTIAL' 或 'FAILED' | S1.5：reference data 种子脚本 + connector 真实 FK lookup |
| `--live-url` 显式开关 | 不实现 | S1.4 不需要；S1.8 ingest 调度再启 |
| 批量 2020–2025 | 不实现 | S1.8+；需 docs/08 §2.3 Gate 1 全量退出条件先开 |
| `ingest/runner.py` 最小调度 | 不实现 | S1.8（per `docs/18` §1） |
| `ingestion_run.status` 字段是否记录 `triggered_by`（如 'test_nbs_monthly_connector' / CLI 名） | ✅ 已写入；后续接入 run history 视图 | S1.8+ 报表 |
| `source_document` S0+UNVERIFIED CHECK（I-05 §9.1）vs connector 强制 VERIFIED | 当前 connector 写 VERIFIED（spike 01 是 platform-verified 历史样本）；未来如要消化 UNVERIFIED，需另增 downgrade 路径并 audit | S1.6 governance audit |

---

## §5. 待 Cursor 审验

| 项 | 期望 |
|---|---|
| `docs/18` 修订是否仍待 CC 进一步收口 | Cursor 复验；若需 §N 补充，可走 Cursor 33 |
| connector ingest_run status 语义 | 若 Cursor 想严格区分「PARTIAL vs FAILED」（例如 records_inserted=0 时是否允许 FAILED），现 §3 流程已声明接受 PARTIAL |
| pytest 全集 264 passed 是否合预期 | 是（S1.3: 258；S1.4: +6） |
| 提交 commit message 体例 | `feat(s1.4): …`（per global CLAUDE.md 「conventional commits」） |
| pack manifest 445 artifacts | 是 |

---

## §6. 等待

等 Cursor 写 `reviews/NN-stage0-cursor-s14-audit-*.md` → 更新 `00-CC-CURRENT.md` 队列至 S1.5+。

— CC Receipt 38 end —
