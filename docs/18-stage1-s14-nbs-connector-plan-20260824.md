# Stage 1 — S1.4 NBS-MONTHLY 连接器规划（CC 起草）

> 文件编号：`docs/18-stage1-s14-nbs-connector-plan-20260824.md`
> 起草方：**CC**（覆盖 Cursor 越界 `921f431` 草稿；per `reviews/37-stage0-cursor-architect-only-rule-20260824.md` §1）
> 起草日期：2026-08-24
> 依据：`docs/08` §2.1 S1.4；`reviews/33-stage1-s14-nbs-planning-20260824.md`；`spikes/01-national-yearbook/`
> 范围：**单期试点**（1 期 HTML `sample.html` 入库链端到端跑通）；**不**批量 2020–2025；**不**真 HTTP（除 `--live-url` 显式开关）

---

## §0. TL;DR

| 项 | 决策 |
|---|---|
| 基线 spike | `spikes/01-national-yearbook/`（HTML 月度 zxfb 表 + `extract_01_national_yearbook.py`） |
| 试点输入 | `spikes/01-national-yearbook/sample.html`（SHA-256 `dea13b8a4ff116ca91403b189cdd60705545b28200f9023c3d56e6db03f3939d`） |
| 试点入库 | 1 期；≥1 observation |
| 生产路径 | `backend/src/china_platform/connectors/nbs_monthly.py` |
| 持久化 | `ingestion_run` + `source_document`（必要时 + `source_location`） + `observation`（FK 解析失败时 status=PARTIAL） |
| 真 HTTP | **不实现**；仅 `--live-url` 单 URL 显式开关（per Cursor 36 §1） |
| 验证 | `docs/10` §2.1–2.6 → `tests/test_nbs_monthly_connector.py` ≥3 用例（hash / obs 数 / ingestion_run 状态） |
| 禁止 | 批量 2020–2025；skip-as-PASS；降 OCR 门槛；HTTP 默认开 |

---

## §1. 目录与模块

```
backend/src/china_platform/
├── __init__.py
└── connectors/
    ├── __init__.py
    └── nbs_monthly.py        # NbsMonthlyConnector

tests/
└── test_nbs_monthly_connector.py   # ≥3 用例
```

**不**创建 `ingest/runner.py`（S1.8 才上最小 ingest 调度；本连接器自带 ingestion_run 写入）。

---

## §2. 类与责任

```python
class NbsMonthlyConnector:
    """Stage 1 / S1.4 — NBS 月度统计公报 HTML 表连接器。

    复用 `spikes/01-national-yearbook/extract_01_national_yearbook.py` 的解析逻辑
    （避免代码分裂；通过 import 而不是 copy-paste）。

    默认输入：repo 内 sample.html（sha-256 与 `source_registry` 中 stats.gov.cn
    `NATIONAL_BULLETIN` 行的 `local_sample_path` 一致）。
    """

    DEFAULT_SAMPLE = REPO_ROOT / "spikes" / "01-national-yearbook" / "sample.html"
    DEFAULT_REGISTRY_DOMAIN = "stats.gov.cn"
    DEFAULT_REGISTRY_CATEGORY = "NATIONAL_BULLETIN"

    def compute_sha256(self, file_path: Path) -> str: ...

    def extract(self, file_path: Path) -> dict:
        """返回 {'sha256', 'observations': [...], 'metadata': {...}}。
        纯文件操作，无 DB 副作用。"""

    def ingest(
        self,
        file_path: Path,
        conn: psycopg2.extensions.connection,
        triggered_by: str = "test_nbs_monthly_connector",
    ) -> dict:
        """DB 入库：
        1) 解析 source_registry 行（按 domain + category）
        2) INSERT ingestion_run (status='RUNNING')
        3) compute sha256, INSERT source_document (source_registry_id, sha256,
           title/publisher/file_size_bytes, source_level='S0',
           verification_status='UNVERIFIED' — 由 S0+UNVERIFIED CHECK 触发 FAILED，
           所以这里走 VERIFIED；spike 01 是已 platform-verified 历史样本)
        4) extract() → observations
        5) 尝试 INSERT observations（FK 解析失败时 → 记录 error_log + status=PARTIAL）
        6) UPDATE ingestion_run SET status='SUCCESS' / 'PARTIAL' / 'FAILED',
           finished_at=NOW(), records_extracted / records_inserted
        7) 返回 {'ingestion_run_id', 'status', 'records_extracted',
                  'records_inserted', 'error_log'}
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
| `ingestion_run` | `source_registry_id` | stats.gov.cn NATIONAL_BULLETIN 行（import_registry_csv 已入） |
| | `started_at` | NOW() |
| | `status` | 'RUNNING' 入口；末尾按上述切换 |
| | `records_extracted` | len(observations) from extract() |
| | `records_inserted` | 实际 INSERT 成功数 |
| | `error_log` | NULL 或 FIRST error 摘要（<500 字符） |
| | `triggered_by` | 'test_nbs_monthly_connector' 或 CLI 名 |
| `source_document` | `source_registry_id` | 同上 |
| | `source_level` | 'S0'（NBS 直发） |
| | `verification_status` | 'VERIFIED'（spike 01 历史已核验样本；规避 I-05 §9.1 CHECK） |
| | `title` / `publisher` / `url` | 从 CSV `organization` + 已知 sample URL 推导 |
| | `file_hash_sha256` | extract() 返回值 |
| | `file_size_bytes` | file_path.stat().st_size |
| | `language` | 'zh' |

`source_document` 一旦入库不可 DELETE（per `source_document_no_delete` 触发器）；
测试用 SAVEPOINT 回滚确保不污染。

---

## §4. docs/10 §2.1–2.6 映射（连接器侧）

| 测试 | 连接器责任 | 试点验证方式 |
|---|---|---|
| 2.1 单位 / 数量级 | 保留 spike `_parse_value` 单位推断 | `extract()['observations'][i]['unit']` ∈ {'%', ...} |
| 2.2 合计行 | 单期试点不展开；留 Stage 1 dbt | N/A（不写 sum row） |
| 2.3 同比反算 | extract 仅 raw + parsed；YoY 计算留 Stage 3 | `extract()['observations'][i]` 含 `raw_value` 与 `value` |
| 2.4 跨来源 | 仅 NBS；跨源 Stage 3 | 单源 connector |
| 2.5 时间序列 | 单期；多期留 Stage 1 dbt | N=1 期 |
| 2.6 修订 | metadata `revision_note` 占位 | extract 输出不含 revision（试点 PRELIMINARY） |

**S1.4 试点退出**：1 期 HTML → extract + ingest → ingestion_run.status='SUCCESS'/'PARTIAL' + 至少 1 observation 入库 OR 失败状态有 error_log。

---

## §5. 失败 / 重试

| 失败类型 | 处理 |
|---|---|
| 文件缺失 | `pytest.fail`（mandatory；不允许 skip） |
| 网络（`--live-url`） | 当前 S1.4 不实现；out of scope（per Cursor 36 §1） |
| 解析 | `ingestion_run.status='FAILED'` + `error_log`；不部分 commit |
| FK 解析（observation） | 单条失败 → 累计 → `status='PARTIAL'`；不影响已成功行 |
| 通用 schema 违例 | CheckViolation → `status='FAILED'` + 完整 psycopg2 错误摘要 |

---

## §6. 红线

- ❌ 不批量 2020–2025
- ❌ 不改 `gate_thresholds.json`
- ❌ 不 HTTP 默认开
- ❌ 不宣布 Gate 1 PASS
- ❌ 不降 OCR 门槛
- ❌ 不 skip-as-PASS（缺失样本 → `pytest.fail`）
- ❌ 不复用 1909 / 陕西作为代表性（保持 research-only）

---

## §7. 下一刀

Cursor 36 §NOW step 4：
- `tests/test_nbs_monthly_connector.py` ≥3 用例
- pytest 全集 + pack → commit 双推 → `reviews/38-stage0-cc-s14-receipt-*.md`

— End S1.4 plan (CC) —