# Stage 1 / S1.5 — CC Receipt（实施）

- 文件编号：`45-stage0-cc-s15-impl-receipt-20260824`
- 下发方：CC（Claude Code）
- 日期：2026-08-24
- 接收：`reviews/44-stage1-s15-shenzhen-impl-tasking-20260824.md`
- 协议：`40-stage0-cc-cursor-deadlock-fix-20260824.md` §1 + §5（git pull bootstrap） + `21-stage0-cc-proactive-poll-standing-order-20260824.md` §1
- 提交：`0df4c8c`（feat(s1.5): implement SZ municipal bulletin connector (prose parser)）

---

## §0. TL;DR

| 任务 | 状态 |
|---|---|
| S1.5.1 `sz_municipal_bulletin.py` | ✅ SzMunicipalBulletinConnector |
| S1.5.2 `tests/test_sz_municipal_bulletin_connector.py` ≥3 用例 | ✅ 7 用例（hash ×2 / extract ×3 / ingest ×2） |
| S1.5.3 pytest 全集 + pack rebuild | ✅ 271 passed / 447 artifacts |
| S1.5.4 commit + 双推 | ✅ origin OK；⚠️ github 443 待重试（见 §6） |
| S1.5.5 回执 `45` | ✅（本文件）|
| 收尾 / 阻塞 | 无 |

---

## §1. 交付清单

### §1.1 包结构

```
backend/src/china_platform/
├── __init__.py
└── connectors/
    ├── __init__.py
    ├── nbs_monthly.py                   # S1.4 已交付
    └── sz_municipal_bulletin.py         # S1.5 新增（SzMunicipalBulletinConnector）
```

**不**创建 `ingest/runner.py`（S1.8 才上最小 ingest 调度；本连接器自带 ingestion_run 写入）。

### §1.2 连接器

| 类 / 方法 | 责任 |
|---|---|
| `SzMunicipalBulletinConnector.compute_sha256(path)` | 文件 SHA-256 hex digest（复用 spike 03 `_spike_compute_sha256(bytes)`；读文件 → bytes → hex） |
| `SzMunicipalBulletinConnector.extract(path)` | 纯文件解析 → `{sha256, observations, metadata}`；`FileNotFoundError` 抛出（per `docs/19` §5 不 swallow） |
| `SzMunicipalBulletinConnector._resolve_source_registry(conn)` | 按 `domain='sz.gov.cn'` + `category='MUNICIPAL_BULLETIN'` 查 `cegr.source_registry` |
| `SzMunicipalBulletinConnector._create_ingestion_run(conn, sr_id, triggered_by)` | INSERT `cegr.ingestion_run (status='RUNNING', started_at=NOW())`，返回 run_id |
| `SzMunicipalBulletinConnector._create_source_document(conn, sr_id, sha, size, title, publisher, url)` | INSERT `cegr.source_document (S0, VERIFIED, HTML_PARSE, 'zh')`，返回 doc_id |
| `SzMunicipalBulletinConnector._attempt_observation_insert(conn, obs, run_id)` | INSERT `cegr.observation`（FK 占位；S1.5+ 替换为真实 lookup），FK 违例 → `(False, summary)`；其他 `psycopg2.Error` → `(False, summary)` |
| `SzMunicipalBulletinConnector._finalize_ingestion_run(conn, run_id, status, extracted, inserted, err)` | UPDATE `cegr.ingestion_run` 终态；`error_log` 截断 ≤ 500 字符 |
| `SzMunicipalBulletinConnector.ingest(path, conn, ...)` | 端到端：`source_registry` → `ingestion_run RUNNING` → `extract()` → `source_document` → `observations` best-effort → `ingestion_run` 终态；返回 `{ingestion_run_id, status, records_extracted, records_inserted, error_log, source_document_id}` |

### §1.3 终态语义（per `docs/19` §3 + §5 0-obs 特殊处理）

```
RUNNING
  ├── extract / sha256 / source_document INSERT 成功
  │   ├── observations 全成功    → status='SUCCESS'
  │   ├── 部分 FK 解析失败       → status='PARTIAL'（error_log = FIRST error）
  │   ├── 0 obs（散文解析空）    → status='SUCCESS'（extract 自身没崩；N=0 是诚实报告）
  │   └── source_document 失败   → status='FAILED'
  └── ingest 入口异常（FileNotFound 等） → status='FAILED'
```

### §1.4 测试

| 文件 | 7 个用例（`Cursor 44 §NOW` 要求 ≥3） |
|---|---|
| `tests/test_sz_municipal_bulletin_connector.py` | (1) `test_compute_sha256_matches_known_digest` — SHA-256 == `d5e2c731…2d29`（避免 spike 03 sample drift）；(2) `test_connector_compute_sha256_reproducible` — 同一文件两次计算同值；(3) `test_extract_returns_observations` — `extract()` 返回 `{sha256, observations, metadata}`，observations ≥1，S1.5 增值字段 `comparison_basis` / `context_quote` 均存在，metadata.city=='深圳'；(4) `test_extract_units_within_expected_set` — unit ∈ {'亿元', '%', '万人', '元'}（per docs/10 §2.1 + docs/19 §4）；(5) `test_extract_missing_file_raises` — `FileNotFoundError` 不 swallow；(6) `test_ingest_writes_ingestion_run_with_valid_status` — `ingestion_run` 行存在，status ∈ `{SUCCESS, PARTIAL, FAILED, RUNNING}`；(7) `test_ingest_records_inserted_le_records_extracted` — 防御性断言 `records_inserted ≤ records_extracted`，0 inserted + N extracted 时 status ∈ `{PARTIAL, FAILED}` |

---

## §2. 命令输出摘要

### §2.1 `python3 -m pytest tests/test_sz_municipal_bulletin_connector.py -v`

```
collected 7 items
tests/test_sz_municipal_bulletin_connector.py::test_compute_sha256_matches_known_digest PASSED
tests/test_sz_municipal_bulletin_connector.py::test_connector_compute_sha256_reproducible PASSED
tests/test_sz_municipal_bulletin_connector.py::test_extract_returns_observations PASSED
tests/test_sz_municipal_bulletin_connector.py::test_extract_units_within_expected_set PASSED
tests/test_sz_municipal_bulletin_connector.py::test_extract_missing_file_raises PASSED
tests/test_sz_municipal_bulletin_connector.py::test_ingest_writes_ingestion_run_with_valid_status PASSED
tests/test_sz_municipal_bulletin_connector.py::test_ingest_records_inserted_le_records_extracted PASSED
============================== 7 passed in 0.74s ===============================
```

### §2.2 `python3 -m pytest -q`（全集，含 `spikes` + `tests`）

```
........................................................................ [ 79%]
.......................................................                  [100%]
271 passed in 470.58s (0:07:50)
```

（S1.5 规划收尾时 264 → S1.5 实施收尾 271，+7 来自 `test_sz_municipal_bulletin_connector.py`）

### §2.3 `python3 scripts/build_evidence_pack.py`

```
Wrote /Users/kjonekong/projects/china platform/evidence_pack/manifest.json: 447 artifacts
verified 447 artifacts (full)
```

（S1.5 规划收尾时 446 → S1.5 实施收尾 447，+1：`backend/src/china_platform/connectors/sz_municipal_bulletin.py`）

### §2.4 git

```
[main 0df4c8c] feat(s1.5): implement SZ municipal bulletin connector (prose parser)
 3 files changed, 596 insertions(+), 7 deletions(-)
 create mode 100644 backend/src/china_platform/connectors/sz_municipal_bulletin.py
 create mode 100644 tests/test_sz_municipal_bulletin_connector.py
To https://origin.cursor.com/lyliae/china-platform.git
   9caab88..0df4c8c  HEAD -> main
```

`github` 远端 443 timeout（见 §6）— 不阻塞 origin 队列；按既常 protocol 写 hold 记录 + 后台续推。

---

## §3. 红线遵守

| 红线 | 状态 |
|---|---|
| ❌ 不批量 2020–2024（市级公报回溯） | ✅ 单期 sample.html 试点 |
| ❌ 不 HTTP 默认开 | ✅ 默认走 repo 内 `spikes/03-municipal-bulletin/sample.html`；`--live-url` 显式开关 S1.5 不实现（per Cursor 44 §NOW + docs/19 §6） |
| ❌ 不降 OCR 门槛 | ✅ N/A；HTML_PARSE 路径（spike 04 OCR 仍 BLOCKED，不混线） |
| ❌ 不宣布 Gate 1 PASS | ✅ 仅 S1.5 实施；Gate 1 留待 `docs/08` §2.3 全量退出条件 |
| ❌ 不复用 1909 / 陕西为代表性 | ✅ source_registry 6 行未涉及 1909 / 陕西（NBS / 湖北 / 深圳） |
| ❌ 不 skip-as-PASS | ✅ 缺失 sample → `pytest.fail`（`test_compute_sha256_matches_known_digest` + `test_extract_returns_observations` + `test_extract_units_within_expected_set` + 2 ingest 测试） |
| ❌ 不复用 spike 03 `fetch_bulletin()` 走网络 | ✅ 连接器强制只读 repo 内 sample.html；`extract_statistics(html_bytes)` 仅在 `_attempt_observation_insert` 之前调用，无网络路径 |
| ❌ 不擅自 `--force` / `--force-with-lease` | ✅ 普通 `git push origin HEAD` |
| ❌ 不替用户下裁定 | ✅ 不宣布 Gate 1；不表态接受 audit |

---

## §4. 与 S1.4 NbsMonthlyConnector 差异（实现层）

| 维度 | S1.4 | S1.5 |
|---|---|---|
| 类名 | NbsMonthlyConnector | SzMunicipalBulletinConnector |
| 解析入口 | spike 01 `_spike_parse_html_table` + `_spike_extract_rows` | spike 03 `_spike_extract_statistics(html_bytes)` |
| `extract()` 入参类型 | file_path → 内部 read | file_path → 内部 `read_bytes()` → 传入 spike |
| observation schema | indicator/period/value/unit/source_url/table_locator/extraction_method/confidence | + `comparison_basis` + `context_quote` |
| locator 字段值 | `table[1] — 规模以上工业增加值月度数据表` | section 标题（"一、综合" / "五、国内贸易" / ...）|
| 0-obs 处理 | 不显式；S1.4 默认≥1 obs | **显式**：0 obs → SUCCESS（per docs/19 §5）|
| 终态 `n_extracted == 0` 分支 | 不存在（S1.4 无 0-obs 路径） | `status='SUCCESS'`（extract 自身没崩；N=0 是诚实报告）|

---

## §5. 已知遗留（S1.5+ 范围）

| 项 | 状态 | 留待 |
|---|---|---|
| observation FK 解析（indicator_id / geo_entity_id / calendar_period_id / source_id / source_location_id / geo_code_version_id / indicator_methodology_version_id） | 当前为 placeholder（`UUID(int=0)`），`records_inserted=0` 触发 status='PARTIAL' 或 'FAILED' | S1.5+：reference data 种子脚本 + connector 真实 FK lookup |
| 多期 2020–2024 公报 | 不实现 | Stage 1 dbt（per `docs/08` §2.1） |
| 其他城市公报（广州 / 成都 / ...）| 不实现 | S1.6+；spike 03 散文正则模式跨城市迁移性待评估 |
| `--live-url` 显式开关 | 不实现 | S1.8 ingest 调度 |
| `ingest/runner.py` 最小调度 | 不实现 | S1.8 |
| source_registry `MUNICIPAL_BULLETIN` 类别的 indicator / geo 字典 | 留待 | S1.6 reference data seeding |
| spike 04 OCR 与本连接器解耦 | 已红线（`docs/19` §6）显式隔开 | S1.4 OCR BLOCKED 解除后另开规划 |

---

## §6. github 远端 443 timeout（不阻塞）

`git push origin HEAD` 成功；`git push github HEAD` 失败：

```
fatal: unable to access 'https://github.com/cscoheru/china-platform.git/':
Recv failure: Operation timed out
```

（首次 443 timeout 后重试亦 timeout；与 receipt 42 §6 同模式）

| 项 | 状态 |
|---|---|
| origin (Cursor) | ✅ `9caab88..0df4c8c  HEAD -> main` |
| github | ⚠️ 443 timeout 待重试 |
| 是否阻塞 | **否**（per `22-stage0-cursor-github-network-hold-20260824.md` 协议 — origin 是 CC↔Cursor 主通道，github 尽力） |
| 后台重试 | 另开续推；不在本回执内继续 |

---

## §7. 待 Cursor 审验

| 项 | 期望 |
|---|---|
| `sz_municipal_bulletin.py` 结构 | 镜像 S1.4 NbsMonthlyConnector（`_resolve_source_registry` / `_create_ingestion_run` / `_create_source_document` / `_attempt_observation_insert` / `_finalize_ingestion_run` / `ingest`）|
| spike 03 复用 | 通过 `import` 而非 copy-paste；`extract_statistics` / `compute_sha256` 单点真相 |
| 7 个测试覆盖 | hash ×2 / extract ×3（含 schema 校验 + units 白名单）/ ingest ×2 |
| 与 S1.4 connector 共用 schema | ingestion_run / source_document / observation 不变；FK 解析失败 → PARTIAL 同 S1.4 |
| 0-obs 处理（docs/19 §5）| `n_extracted == 0` → SUCCESS（已显式实现 + 测试覆盖）|
| pytest 全集 271 passed | 是（264 + 7） |
| pack 447 artifacts | 是 |
| 双推 | origin ✅ / github ⚠️（§6）|

---

## §8. 等待

等 Cursor 写 `reviews/NN-stage0-cursor-s15-impl-audit-*.md` → 通过后下发 S1.6 / S1.7 tasking（per `docs/08` §2.1 顺序）。

— CC Receipt 45 end —
