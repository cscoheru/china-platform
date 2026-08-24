# Stage 1 — S1.5 SZ-MUNICIPAL-BULLETIN 连接器规划（CC 起草）

> 文件编号：`docs/19-stage1-s15-shenzhen-bulletin-plan-20260824.md`
> 起草方：**CC**（per Cursor 41 §NOW；Cursor **不写** 本文件正文）
> 起草日期：2026-08-24
> 依据：`docs/08` §2.1 S1.5；`reviews/39-stage0-cursor-s14-audit-20260824.md` §1；`reviews/41-stage1-s15-shenzhen-planning-tasking-20260824.md`
> 范围：**单样本试点**（spike 03 `sample.html` 1 期 HTML 入库链端到端跑通）；**不**批量 2020–2024；**不**真 HTTP（除 `--live-url` 显式开关）

---

## §0. TL;DR

| 项 | 决策 |
|---|---|
| 基线 spike | `spikes/03-municipal-bulletin/`（散文式 HTML 月度公报 + `extract_03_municipal_bulletin.py`） |
| 试点输入 | `spikes/03-municipal-bulletin/sample.html`（SHA-256 `d5e2c73196b43cecc8efa20e174d30bf78c382e21a1cda956f0637aeb9022d29`，size 62831） |
| 试点入库 | 1 期；≥1 observation（spike 03 实测 8 行；散文正则成功率高） |
| 生产路径 | `backend/src/china_platform/connectors/sz_municipal_bulletin.py` |
| 持久化 | `ingestion_run` + `source_document`（必要时 + `source_location`） + `observation`（FK 解析失败时 status=PARTIAL） |
| 解析思路 | `beautifulsoup` 解析 `<div class="news_cont_d_wrap">` 文章体 → 按 section（一、综合 / 二、农业 / ...）分段落 → 按 indicator family 正则提取值+单位 |
| 真 HTTP | **不实现**；仅 `--live-url` 单 URL 显式开关（per Cursor 41 §NOW；同 S1.4 纪律） |
| 验证 | `docs/10` §2.1–2.5 → `tests/test_sz_municipal_bulletin_connector.py` ≥3 用例（hash / obs 数 / ingest_run 状态） |
| 禁止 | 批量 2020–2024；skip-as-PASS；降 OCR 门槛；HTTP 默认开 |

---

## §1. 目录与模块

```
backend/src/china_platform/
├── __init__.py
└── connectors/
    ├── __init__.py
    ├── nbs_monthly.py                   # S1.4 已交付
    └── sz_municipal_bulletin.py         # S1.5 新增（SzMunicipalBulletinConnector）

tests/
└── test_sz_municipal_bulletin_connector.py   # ≥3 用例
```

**不**创建 `ingest/runner.py`（S1.8 才上最小 ingest 调度；本连接器自带 ingestion_run 写入）。

**复用**：
- `source_registry` 行（`sz.gov.cn` / `MUNICIPAL_BULLETIN`）由 S1.3 导入；sample.html SHA-256 与 CSV `file_hash_sha256` 列一致
- `spikes/03-municipal-bulletin/extract_03_municipal_bulletin.py` 的 `extract_statistics(html_bytes)`、`compute_sha256(bytes)`（**不**复制粘贴；通过 import 复用，逻辑单点真相）

---

## §2. 类与责任

```python
class SzMunicipalBulletinConnector:
    """Stage 1 / S1.5 — 深圳市政府统计公报连接器。

    复用 `spikes/03-municipal-bulletin/extract_03_municipal_bulletin.py` 的
    解析逻辑（避免代码分裂；通过 import 而不是 copy-paste）。

    默认输入：repo 内 `spikes/03-municipal-bulletin/sample.html`
    （SHA-256 与 `source_registry` 中 sz.gov.cn / MUNICIPAL_BULLETIN 行的
    `local_sample_path` 一致）。
    """

    DEFAULT_SAMPLE = REPO_ROOT / "spikes" / "03-municipal-bulletin" / "sample.html"
    DEFAULT_REGISTRY_DOMAIN = "sz.gov.cn"
    DEFAULT_REGISTRY_CATEGORY = "MUNICIPAL_BULLETIN"
    DEFAULT_SAMPLE_TITLE = "深圳市2024年国民经济和社会发展统计公报"
    DEFAULT_SAMPLE_PUBLISHER = "深圳市人民政府"
    DEFAULT_SAMPLE_URL = (
        "https://www.sz.gov.cn/zfgb/2025/gb1374/content/post_12212437.html"
    )

    def compute_sha256(self, file_path: Path) -> str:
        """文件 SHA-256 hex digest（复用 spike 03 `compute_sha256(bytes)`）。"""

    def extract(self, file_path: Path) -> dict:
        """返回 {'sha256', 'observations': [...], 'metadata': {...}}。
        纯文件操作，无 DB 副作用。每条 observation 含：
          - indicator, period, value, unit
          - comparison_basis (当年价格 / 可比价格 / None)
          - context_quote (散文原句前 200 字符，用于人工追溯)
          - source_url, locator (section 标题如 '一、综合')
          - extraction_method, confidence
        """

    def ingest(
        self,
        file_path: Path,
        conn: psycopg2.extensions.connection,
        triggered_by: str = "test_sz_municipal_bulletin_connector",
    ) -> dict:
        """DB 入库（与 S1.4 NbsMonthlyConnector 镜像）：
        1) 解析 source_registry 行（按 domain='sz.gov.cn' + category='MUNICIPAL_BULLETIN'）
        2) INSERT ingestion_run (status='RUNNING')
        3) compute sha256, INSERT source_document (source_registry_id, sha256,
           title/publisher/file_size_bytes, source_level='S0',
           verification_status='VERIFIED' — spike 03 是已 platform-verified 历史样本,
           规避 I-05 §9.1 source_level_s0_requires_verified CHECK)
        4) extract() → observations
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
| `ingestion_run` | `source_registry_id` | sz.gov.cn MUNICIPAL_BULLETIN 行（S1.3 import_registry_csv 已入） |
| | `started_at` | NOW() |
| | `status` | 'RUNNING' 入口；末尾按上述切换 |
| | `records_extracted` | len(observations) from extract() |
| | `records_inserted` | 实际 INSERT 成功数 |
| | `error_log` | NULL 或 FIRST error 摘要（<500 字符） |
| | `triggered_by` | 'test_sz_municipal_bulletin_connector' 或 CLI 名 |
| `source_document` | `source_registry_id` | 同上 |
| | `source_level` | 'S0'（深圳市政府直发） |
| | `verification_status` | 'VERIFIED'（spike 03 历史已核验样本；规避 I-05 §9.1 CHECK） |
| | `title` / `publisher` / `url` | 从 CSV `organization` + 已知 sample URL 推导 |
| | `file_hash_sha256` | extract() 返回值 |
| | `file_size_bytes` | file_path.stat().st_size |
| | `language` | 'zh' |
| | `extraction_method` | 'HTML_PARSE' |

`source_document` 一旦入库不可 DELETE（per `source_document_no_delete` 触发器）；
测试用 SAVEPOINT 回滚确保不污染（同 S1.4 测试纪律）。

---

## §4. docs/10 §2.1–2.5 映射（连接器侧）

| 测试 | 连接器责任 | 试点验证方式 |
|---|---|---|
| 2.1 单位 / 数量级 | 保留 spike 03 `parse_value_unit` 单位推断；spike 03 实测单位 ∈ {'亿元', '%', '万人', '元'} | `extract()['observations'][i]['unit']` ∈ 该集合 |
| 2.2 合计行 | 单期试点不展开；留 Stage 1 dbt | N/A（不写 sum row） |
| 2.3 同比反算 | extract 仅 raw + parsed；YoY 计算留 Stage 3 | `extract()['observations'][i]` 含 `value` 与 `comparison_basis`；spike 03 已抓 GDP growth 与 GDP 总值两条，可手工反算 |
| 2.4 跨来源 | 仅深圳公报；跨源 Stage 3 | 单源 connector |
| 2.5 时间序列 | 单期；多期留 Stage 1 dbt | N=1 期 |
| 2.6 修订（不映射）| metadata `revision_note` 占位 | extract 输出不含 revision（试点 PRELIMINARY） |

**S1.5 试点退出**：1 期 HTML → extract + ingest → ingestion_run.status='SUCCESS'/'PARTIAL' + 至少 1 observation 入库 OR 失败状态有 error_log。

**S1.5 与 S1.4 关键差异（连接器侧）**：

| 维度 | S1.4 NbsMonthlyConnector | S1.5 SzMunicipalBulletinConnector |
|---|---|---|
| 解析目标 | HTML `<table>` 结构化表格 | HTML `<div class="news_cont_d_wrap">` 散文段落 |
| 解析方法 | regex on rows + cell | beautifulsoup + section-aware regex on prose |
| 提取指标数 | ≥1（spike 01 实测） | 8（spike 03 实测：GDP/人口/固投/零售/进出口/人均/财政/固投增速） |
| locator 字段 | `table[1] — ...` | section 标题（"一、综合" / "五、国内贸易" / ...） |
| 持久化层 | ingestion_run + source_document + observation | 同 S1.4（同一 schema） |
| 真 HTTP | 不实现 | 同 S1.4 |

---

## §5. 失败 / 重试

| 失败类型 | 处理 |
|---|---|
| 文件缺失 | `pytest.fail`（mandatory；不允许 skip） |
| 网络（`--live-url`） | 当前 S1.5 不实现；out of scope（per Cursor 41 §NOW；同 S1.4 纪律） |
| 解析（BeautifulSoup 失败 / 0 obs） | `ingestion_run.status='FAILED'` + `error_log`；不部分 commit |
| FK 解析（observation） | 单条失败 → 累计 → `status='PARTIAL'`；不影响已成功行 |
| 通用 schema 违例 | CheckViolation → `status='FAILED'` + 完整 psycopg2 错误摘要 |

**与 S1.4 差异**：spike 03 的 `extract_statistics` 在 sample.html 上稳定返回 8 行；但若散文版式变更（其他城市公报 / 其他年份），可能 0 obs。**0 obs 不自动 FAIL**：若 `extract()` 返回空列表，status 仍为 SUCCESS（因为 extract 自身没崩；no rows found 是诚实报告），但 `records_inserted=0`。

---

## §6. 红线

- ❌ 不批量 2020–2024（市级公报 5 年回溯由 Stage 1 dbt 接管，非本连接器责任）
- ❌ 不改 `gate_thresholds.json`
- ❌ 不 HTTP 默认开
- ❌ 不宣布 Gate 1 PASS
- ❌ 不降 OCR 门槛（spike 04 OCR 仍 BLOCKED；本连接器不走 OCR 路径）
- ❌ 不 skip-as-PASS（缺失样本 → `pytest.fail`）
- ❌ 不复用 1909 / 陕西作为代表性（保持 research-only）
- ❌ 不复用 spike 03 `fetch_bulletin()` 走网络（spike 03 内置 httpx fallback 仅 spike 内 standalone 用；连接器强制只读 repo 内 sample.html）

---

## §7. 下一刀

Cursor 41 §NOW + `00-CC-CURRENT.md` 阶段任务：
1. Cursor 审验本 `docs/19` 规划
2. 通过后下发 `42-stage0-cursor-s15-impl-tasking-*.md`
3. CC 实现：`backend/src/china_platform/connectors/sz_municipal_bulletin.py` + `tests/test_sz_municipal_bulletin_connector.py` ≥3 用例
4. pytest 全集 + pack rebuild + commit + dual-push + `reviews/42-stage0-cc-s15-impl-receipt-*.md`

— End S1.5 plan (CC) —
