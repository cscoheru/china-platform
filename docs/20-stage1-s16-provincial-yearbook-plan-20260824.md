# Stage 1 — S1.6 PROVINCIAL-YEARBOOK 连接器规划（CC 起草）

> 文件编号：`docs/20-stage1-s16-provincial-yearbook-plan-20260824.md`
> 起草方：**CC**（per Cursor 47 §NOW；Cursor **不写** 本文件正文）
> 起草日期：2026-08-24
> 依据：`docs/08` §2.1 S1.6；`reviews/46-stage0-cursor-s15-impl-audit-20260824.md` §1；`reviews/47-stage1-s16-provincial-planning-tasking-20260824.md`
> 范围：**单样本试点**（spike 02 `hubei_2026_06.xlsx` 1 期 xlsx 入库链端到端跑通）；**不**批量「3 省 × 5 年」；**不**真 HTTP

---

## §0. TL;DR

| 项 | 决策 |
|---|---|
| 基线 spike | `spikes/02-provincial-yearbook/`（湖北省统计局 H1 2026 主要经济指标 xlsx） |
| 试点输入 | `spikes/02-provincial-yearbook/hubei_2026_06.xlsx`（11,261 bytes，SHA-256 `c5cf5abeb4fdf97af52567f0640470d631bc9ac329dcc98f14e5d40bf6a5cac7`） |
| 容器格式 | xlsx 单文件（非 ZIP 容器；spike 02 docstring §「注」明确） |
| 试点入库 | 1 期；≥1 observation（spike 02 实测 21 数据行） |
| 生产路径 | `backend/src/china_platform/connectors/provincial_yearbook.py` |
| 持久化 | `ingestion_run` + `source_document` + `observation`（FK 解析失败时 status=PARTIAL）+ 每行 `lineage` JSONB 子结构（per R3-E） |
| 解析思路 | `openpyxl.load_workbook(data_only=True)` 读 active sheet → title 行（row 1） + col_headers（row 2） + data rows（row 3+，4 列：indicator_zh / unit / value / growth_rate_yoy_pct） → `_lookup_map` + `derive_period_metadata` 生成 canonical indicator + period 元数据 + per-row lineage |
| per-indicator period metadata（B-06） | 显式建模 `period_start` / `period_end` / `period_label` / `period_type` / `caveat` / `quarterly_data_verified`（per R3-E）；不允许漂移为单一「CUMULATIVE_HALF_YEAR」 |
| indicator_canonical（避免 OCR 别名） | 中文指标 → 蛇形英文（`INDICATOR_CANONICAL_MAP`）；**中文不进 DB**，仅作 lineage / caveat 字段 |
| lineage 链（R3-E） | 每 observation 含 `lineage.{chain_id, source_file_sha256, source_file_url, extractor_version}`；上游追溯：统计局源 URL → 抓取 → SHA-256 锁定 → extractor v2.0 → 逐行 |
| 真 HTTP | **不实现**；仅 `--live-url` 单 URL 显式开关（per Cursor 47 §NOW） |
| 验证 | `docs/10` §2.1–2.5 + per-indicator period metadata (B-06) → `tests/test_provincial_yearbook_connector.py` ≥3 用例（hash / obs 数 / ingest_run 状态 / period metadata 完整性） |
| 禁止 | 批量「3 省 × 5 年」；skip-as-PASS；降 OCR 门槛；HTTP 默认开 |

---

## §1. 目录与模块

```
backend/src/china_platform/
├── __init__.py
└── connectors/
    ├── __init__.py
    ├── nbs_monthly.py                   # S1.4 已交付
    ├── sz_municipal_bulletin.py         # S1.5 已交付
    └── provincial_yearbook.py           # S1.6 新增（ProvincialYearbookConnector）

tests/
└── test_provincial_yearbook_connector.py   # ≥4 用例（hash / obs / ingest / period metadata）
```

**不**创建 `ingest/runner.py`（S1.8 才上最小 ingest 调度；本连接器自带 ingestion_run 写入）。

**复用**：
- `source_registry` 行（`tjj.hubei.gov.cn` / `PROVINCIAL_BULLETIN`）由 S1.3 导入；sample xlsx SHA-256 与 CSV `file_hash_sha256` 列一致
- `spikes/02-provincial-yearbook/extract_02_provincial_yearbook.py` 的 `compute_sha256(filepath)`、`extract_rows(ws)`、`derive_period_metadata(indicator_zh)`、`build_lineage_chain(sha)`、`INDICATOR_CANONICAL_MAP`、`COMPARISON_BASIS_MAP`、`PERIOD_METADATA_MAP`（**不**复制粘贴；通过 import 复用）

**不**复用：spike 02 的 `main()` + `--verify-determinism` 路径（属于 spike standalone CLI；连接器只 reuse library 函数）。spike 02 的 `verify_determinism` 测试 **保留在 spike 02 目录**（per Stage 0 测试纪律），**不**迁移到 `tests/test_provincial_yearbook_connector.py`。

---

## §2. 类与责任

```python
class ProvincialYearbookConnector:
    """Stage 1 / S1.6 — 省级统计年鉴 xlsx 连接器。

    复用 `spikes/02-provincial-yearbook/extract_02_provincial_yearbook.py` 的
    解析逻辑（避免代码分裂；通过 import 而不是 copy-paste）。

    默认输入：repo 内 `spikes/02-provincial-yearbook/hubei_2026_06.xlsx`
    （SHA-256 与 `source_registry` 中 tjj.hubei.gov.cn / PROVINCIAL_BULLETIN 行
    的 `local_sample_path` 一致）。

    强制约束（per R3-E / B-06）：
      * per-indicator period metadata 显式建模，不漂移为单一 CUMULATIVE_HALF_YEAR
      * indicator_canonical 中文 → 蛇形英文；中文别名仅作 lineage / caveat 字段
      * 每行 observation 携带 lineage.{chain_id, source_file_sha256, source_file_url, extractor_version}
      * deterministic rebuild：同一 SHA-256 输入必产 byte-identical JSON 序列
    """

    DEFAULT_SAMPLE = REPO_ROOT / "spikes" / "02-provincial-yearbook" / "hubei_2026_06.xlsx"
    DEFAULT_REGISTRY_DOMAIN = "tjj.hubei.gov.cn"
    DEFAULT_REGISTRY_CATEGORY = "PROVINCIAL_BULLETIN"
    DEFAULT_SAMPLE_TITLE = "湖北省2026年1-6月主要经济指标"
    DEFAULT_SAMPLE_PUBLISHER = "湖北省统计局"
    DEFAULT_SAMPLE_URL = (
        "https://tjj.hubei.gov.cn/tjsj/sjkscx/tjyb/2026yb/202608/"
        "P020260804600767306528.xlsx"
    )
    DEFAULT_PROVINCE_ZH = "湖北"
    DEFAULT_PROVINCE_PINYIN = "Hubei"
    DEFAULT_PROVINCE_CODE_GB2260 = "42"
    DEFAULT_EXTRACTOR_VERSION = "2.0"  # spike 02 R3-E lineage 版本

    def compute_sha256(self, file_path: Path) -> str:
        """文件 SHA-256 hex digest（复用 spike 02 `compute_sha256`）。"""

    def extract(self, file_path: Path) -> dict:
        """返回 {'sha256', 'observations': [...], 'metadata': {...}, 'lineage': {...}}。

        每条 observation 必含（R3-E / B-06）：
          - row_index, indicator_zh, indicator_canonical, unit, value, value_type
          - comparison_basis (per-row: CUMULATIVE_YOY / PERIOD_END_YOY / INDEX_YOY / CUMULATIVE_5MONTH)
          - period_start, period_end, period_label, period_type
          - caveat, quarterly_data_verified
          - growth_rate_yoy_pct, growth_rate_is_yoy, growth_rate_unit
          - missing_reason, needs_review, needs_review_reasons
          - lineage.{chain_id, source_file_sha256, source_file_url, extractor_version}

        纯文件操作，无 DB 副作用。
        """

    def ingest(
        self,
        file_path: Path,
        conn: psycopg2.extensions.connection,
        triggered_by: str = "test_provincial_yearbook_connector",
    ) -> dict:
        """DB 入库（与 S1.4/S1.5 镜像）：
        1) 解析 source_registry 行（按 domain='tjj.hubei.gov.cn' + category='PROVINCIAL_BULLETIN'）
        2) INSERT ingestion_run (status='RUNNING')
        3) compute sha256, INSERT source_document (source_registry_id, sha256,
           title/publisher/file_size_bytes, source_level='S0',
           verification_status='VERIFIED' — spike 02 历史已核验样本,
           规避 I-05 §9.1 source_level_s0_requires_verified CHECK)
        4) extract() → observations（含 lineage + period metadata）
        5) 尝试 INSERT observations（FK 解析失败时 → 记录 error_log + status=PARTIAL）
        6) UPDATE ingestion_run SET status='SUCCESS' / 'PARTIAL' / 'FAILED',
           finished_at=NOW(), records_extracted / records_inserted
        7) 返回 {'ingestion_run_id', 'status', 'records_extracted',
                  'records_inserted', 'error_log', 'source_document_id'}
        """
```

---

## §3. ingest_run 钩挂链路

```
RUNNING
  ├── extract / sha256 / source_document INSERT 成功
  │   ├── observations INSERT 全成功    → status='SUCCESS'  + records_inserted=N
  │   ├── 部分 FK 解析失败              → status='PARTIAL'  + error_log
  │   └── source_document INSERT 失败  → status='FAILED'   + error_log
  └── ingest 入口异常（FileNotFound 等） → status='FAILED' + error_log
```

| 表 | 字段 | 值 |
|---|---|---|
| `ingestion_run` | `source_registry_id` | tjj.hubei.gov.cn PROVINCIAL_BULLETIN 行（S1.3 import_registry_csv 已入） |
| | `started_at` | NOW() |
| | `status` | 'RUNNING' 入口；末尾按上述切换 |
| | `records_extracted` | len(observations) from extract() |
| | `records_inserted` | 实际 INSERT 成功数 |
| | `error_log` | NULL 或 FIRST error 摘要（<500 字符） |
| | `triggered_by` | 'test_provincial_yearbook_connector' 或 CLI 名 |
| `source_document` | `source_registry_id` | 同上 |
| | `source_level` | 'S0'（湖北统计局直发） |
| | `verification_status` | 'VERIFIED'（spike 02 历史已核验样本；规避 I-05 §9.1 CHECK） |
| | `title` / `publisher` / `url` | 从 CSV `organization` + 已知 sample URL 推导 |
| | `file_hash_sha256` | extract() 返回值 |
| | `file_size_bytes` | file_path.stat().st_size |
| | `language` | 'zh' |
| | `extraction_method` | 'EXCEL_PARSE' |

`source_document` 一旦入库不可 DELETE（per `source_document_no_delete` 触发器）；
测试用 SAVEPOINT 回滚确保不污染（同 S1.4/S1.5 测试纪律）。

**S1.6 特殊字段映射**（per observation）：

| connector 字段 | DB 列（建议；最终 schema 由 S1.6 impl 决定） | 来源 |
|---|---|---|
| `indicator_canonical` | `observation.indicator_id` (FK → indicator_definition.canonical) | INDICATOR_CANONICAL_MAP |
| `value` | `observation.value` | xlsx column 3 |
| `unit` | `observation.unit` | xlsx column 2 |
| `comparison_basis` | `observation.comparison_basis` | COMPARISON_BASIS_MAP per-row |
| `period_start` / `period_end` | `observation.period_start` / `period_end`（**新增 S1.6 schema 候选**） | derive_period_metadata |
| `period_label` | `observation.period_label`（**新增 S1.6 schema 候选**） | derive_period_metadata |
| `period_type` | `observation.period_type`（**新增 S1.6 schema 候选**） | derive_period_metadata |
| `caveat` | `observation.caveat_text` | derive_period_metadata (R3-E) |
| `lineage` JSON | `observation.lineage`（**新增 S1.6 schema 候选**） | build_lineage_chain per-row |

> **schema 候选字段**（`period_*` / `lineage` JSONB）若 S1.6 时机 schema 未就绪，**impl 阶段需先走 migration 004** 添加列；不允许在测试 fixture 中临时建表（违反 `docs/19 §6` schema-only-via-migration 红线）。本规划不预设 migration 细节，留给 `tasks/49-stage1-s16-impl-tasking-20260824.md` 决定。

---

## §4. docs/10 §2.1–2.5 映射（连接器侧）

| 测试 | 连接器责任 | 试点验证方式 |
|---|---|---|
| 2.1 单位 / 数量级 | 保留 spike 02 column B unit | `extract()['observations'][i]['unit']` ∈ {'亿元', '%', '万千瓦时', ...}（spike 02 实测单位集）|
| 2.2 合计行 | 单期试点不展开；spike 02 含 #子项 sub-item convention | N/A（不写 sum row）|
| 2.3 同比反算 | extract 含 `growth_rate_yoy_pct` 与 `value`；YoY 计算留 Stage 3 | `extract()['observations'][i]` 含 `value` + `growth_rate_yoy_pct` + `growth_rate_is_yoy=True` |
| 2.4 跨来源 | 仅湖北统计局；跨源 Stage 3 | 单源 connector |
| 2.5 时间序列 | 单期；多期留 Stage 1 dbt | N=1 期 |
| 2.6 修订（不映射）| metadata `revision_note` 占位 | extract 输出不含 revision（试点 PRELIMINARY） |
| **B-06 per-indicator period metadata** | **显式建模**，不漂移为单一 `CUMULATIVE_HALF_YEAR` | `extract()['observations'][i]` 含 `period_start` / `period_end` / `period_label` / `period_type` / `caveat` / `quarterly_data_verified`；至少 1 行 `quarterly_data_verified=False`（GDP/居民收入 待核验）|

**S1.6 试点退出**：1 期 xlsx → extract + ingest → ingestion_run.status='SUCCESS'/'PARTIAL' + 至少 1 observation 入库 OR 失败状态有 error_log + B-06 period metadata 完整 + lineage chain_id 存在。

---

## §5. 失败 / 重试

| 失败类型 | 处理 |
|---|---|
| 文件缺失 | `pytest.fail`（mandatory；不允许 skip） |
| openpyxl 缺失 | `RuntimeError`（连接器不自动 install；per spike 02 docstring §「ERROR: openpyxl not installed」）|
| 网络（`--live-url`） | 当前 S1.6 不实现；out of scope（per Cursor 47 §NOW） |
| 解析（openpyxl load 失败 / 0 obs） | `ingestion_run.status='FAILED'` + `error_log`；不部分 commit |
| FK 解析（observation） | 单条失败 → 累计 → `status='PARTIAL'`；不影响已成功行 |
| 通用 schema 违例 | CheckViolation → `status='FAILED'` + 完整 psycopg2 错误摘要 |
| indicator_canonical 缺失 | spike 02 fallback 为 `unknown__{hash}`；connector **不丢弃**该行，但 `needs_review=True`；DB 写入时该行仍尝试 INSERT（除非 FK 失败触发 PARTIAL）|

---

## §6. 红线

- ❌ 不批量「3 省 × 5 年」（per Cursor 47 §NOW）；省级年鉴多省回溯由 Stage 1 dbt 接管
- ❌ 不改 `gate_thresholds.json`
- ❌ 不 HTTP 默认开
- ❌ 不宣布 Gate 1 PASS
- ❌ 不降 OCR 门槛（spike 04 OCR 仍 BLOCKED；本连接器走 EXCEL_PARSE）
- ❌ 不 skip-as-PASS（缺失样本 → `pytest.fail`）
- ❌ 不复用 1909 / 陕西作为代表性（保持 research-only）
- ❌ 不漂移为单一 `CUMULATIVE_HALF_YEAR`（R3-E / B-06 per-indicator 显式建模强制）
- ❌ 不让中文 indicator_zh 进 DB（仅 lineage / caveat 字段保留）
- ❌ 不在测试 fixture 中临时建表（schema-only-via-migration 红线，per `docs/19 §6`）

---

## §7. 下一刀

Cursor 47 §NOW + `00-CC-CURRENT.md` 阶段任务：
1. Cursor 审验本 `docs/20` 规划
2. 通过后下发 `49-stage0-cursor-s16-impl-tasking-*.md`（含 schema 候选字段决策：是否先走 migration 004 添加 `period_*` / `lineage` 列）
3. CC 实现：
   - 若需 migration 004 → `schema/migrations/004_observation_period_lineage.sql` + `alembic/versions/cegr004_placeholder_*.py` + `pytest tests/test_cleanliness.py` 等 schema regression 通过
   - `backend/src/china_platform/connectors/provincial_yearbook.py`
   - `tests/test_provincial_yearbook_connector.py` ≥4 用例（hash / obs / ingest / period metadata）
4. pytest 全集 + pack rebuild + commit + dual-push + `reviews/49-stage0-cc-s16-impl-receipt-*.md`

— End S1.6 plan (CC) —
