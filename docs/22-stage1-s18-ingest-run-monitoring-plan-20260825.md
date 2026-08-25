# 22 — Stage 1 / S1.8 ingest_run 监控 + 失败告警 规划

> **规划 only**；CC 拥有最终版（per Cursor 37 §META architect-only rule）。
> 范围：**监控/告警设计**；不强制上 Grafana 云（per Cursor 62 §NOW 范围）；不引入 DSH（per 62 §红线）。

---

## §0. TL;DR

| 项 | 决策 |
|---|---|
| 范围 | 监控 S1.4-1.7 连接器写入的 `cegr.ingestion_run` 行；**不**批量爬取；**不**降 OCR 门槛 |
| 复用 | 已有 `ingestion_run` 表（`schema/01-core.sql` line 400-420；status/records_*/started_at/finished_at/error_log） |
| 监控形态 | **CLI 脚本** + **日志输出**（默认；cron 调用）；Grafana dashboard **可选**（不强制上云） |
| 告警机制 | **日志级**（stderr + JSON 报告）+ **cron 退出码**（非 0 = 失败率超阈值）；不引入 PagerDuty/Slack（Stage 1 scope） |
| 失败率阈值 | 默认 `max_failure_rate=0.25`（25%）；可 CLI 覆盖；超阈值 → 退出码 1 + 报告 |
| Stale RUNNING 检测 | `started_at > NOW() - INTERVAL '6 hours' AND finished_at IS NULL`（默认 6h） |
| 关键 SQL | 11 个查询（状态分布/失败率/失败列表/PARTIAL 列表/stale RUNNING/按源分解/records 提取/插入 gap/duration/趋势/趋势对比）|
| 红线 | 不 Gate 1 PASS；不引入 DSH；不引入新 DB 表；Cursor 不写 `docs/22` 正文；不修改 `gate_thresholds.json` |
| 下一刀 | Cursor 62 → `64-stage0-cursor-s18-plan-audit-*.md` → S1.8 实施 tasking（含 CLI 签名 + 测试覆盖） |

---

## §1. 目录与所有权

### §1.1 文件树（增量）

```
china-platform/
├── backend/src/china_platform/monitoring/
│   └── ingest_monitor.py                # NEW (CC owns)
├── scripts/
│   └── monitor_ingest.py                # NEW (CC owns; CLI entry)
├── tests/
│   └── test_ingest_monitor.py           # NEW (CC owns; ≥4)
├── docs/
│   └── 22-stage1-s18-ingest-run-monitoring-plan-20260825.md   # THIS FILE (CC owns)
└── reviews/
    └── 63-stage0-cc-s18-plan-receipt-20260825.md       # NEW (CC owns)
```

### §1.2 所有权（per Cursor 37 §META）

| 文件 / 决策 | CC | Cursor |
|---|---|---|
| `docs/22-stage1-s18-...-plan-20260825.md` 正文 | ✅ 起草 | ❌ 不改 |
| `backend/.../monitoring/ingest_monitor.py` | ✅ 实现 | ❌ |
| `scripts/monitor_ingest.py` CLI | ✅ 实现 | ❌ |
| `tests/test_ingest_monitor.py` | ✅ ≥4 | ❌ |
| 新增 DB 表 / migration | ❌ | ❌；复用现有 `ingestion_run` |
| `gate_thresholds.json` 修改 | ❌ 严禁 | 严禁 |
| Grafana 仪表盘 | ❌（可选，不强制上云）| 可选后续 tasking |

---

## §2. 组件与责任

### §2.1 IngestMonitor

```python
class IngestMonitor:
    """Stage 1 / S1.8 — ingest_run 监控器.

    查询 cegr.ingestion_run 表（S1.4-1.7 连接器已写入），报告：
      * 状态分布（SUCCESS/PARTIAL/FAILED/RUNNING）
      * 失败率（PARTIAL + FAILED / 总 runs）
      * Stale RUNNING（started_at > 6h 未 finished_at）
      * 按 source_registry 分解（domain + category）
      * records_extracted vs records_inserted gap
      * 运行时长统计（started_at vs finished_at）

    不引入新表；不引入 DSH；不写 observation 数据；不修改 source_document。
    """

    DEFAULT_DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"
    DEFAULT_MAX_FAILURE_RATE = 0.25  # 25% 失败率阈值（可 CLI 覆盖）
    DEFAULT_STALE_RUNNING_HOURS = 6  # stale RUNNING 检测窗口
    DEFAULT_WINDOW_DAYS = 7  # 默认看最近 7 天

    # methods
    def status_distribution(self, window_days: int = DEFAULT_WINDOW_DAYS) -> dict
    def failure_rate(self, window_days: int = DEFAULT_WINDOW_DAYS) -> float
    def failed_runs(self, limit: int = 100) -> list[dict]
    def partial_runs(self, limit: int = 100) -> list[dict]
    def stale_running(self, hours: int = DEFAULT_STALE_RUNNING_HOURS) -> list[dict]
    def per_source_breakdown(self, window_days: int = DEFAULT_WINDOW_DAYS) -> list[dict]
    def records_gap_analysis(self, window_days: int = DEFAULT_WINDOW_DAYS) -> list[dict]
    def duration_stats(self, window_days: int = DEFAULT_WINDOW_DAYS) -> dict
    def trend(self, days: int = 30) -> list[dict]
    def generate_report(self, window_days: int = DEFAULT_WINDOW_DAYS) -> dict
    def check_alerts(self, ...) -> tuple[bool, str]  # (ok, message)
```

### §2.2 CLI 入口（`scripts/monitor_ingest.py`）

```bash
# 基础报告（stdout JSON）
python3 scripts/monitor_ingest.py report

# 检查告警（退出码 0 = OK / 1 = 失败率超阈值 / 2 = 有 stale RUNNING）
python3 scripts/monitor_ingest.py check

# 列出失败 run（stdout table）
python3 scripts/monitor_ingest.py failed

# 列出 PARTIAL run
python3 scripts/monitor_ingest.py partial

# 列出 stale RUNNING
python3 scripts/monitor_ingest.py stale

# 按 source_registry 分解
python3 scripts/monitor_ingest.py per-source

# 趋势（30 天）
python3 scripts/monitor_ingest.py trend

# 自定义窗口
python3 scripts/monitor_ingest.py report --window-days 14
python3 scripts/monitor_ingest.py check --max-failure-rate 0.10
python3 scripts/monitor_ingest.py stale --hours 12
```

### §2.3 状态语义（ingestion_run.status）

| 状态 | 含义 | 触发条件 |
|---|---|---|
| `RUNNING` | 进行中 | connector `ingest()` 开始时 INSERT；`finished_at` IS NULL |
| `SUCCESS` | 成功 | `n_inserted == n_extracted` 或 `n_extracted == 0`（clean extract） |
| `PARTIAL` | 部分成功 | `0 < n_inserted < n_extracted`（部分 observation FK 失败） |
| `FAILED` | 失败 | `n_inserted == 0` 且 `n_extracted > 0`，或 extract 阶段异常 |

### §2.4 失败率公式

```
failure_rate = (count(PARTIAL) + count(FAILED)) / count(ALL)  -- within window_days

若 count(ALL) == 0：failure_rate = 0.0（无数据 = 无失败；诚实报告）
```

**超阈值退出**：`failure_rate > max_failure_rate` → 退出码 1 + stderr 报告

---

## §3. 关键 SQL 查询（CC 实现时使用）

### §3.1 状态分布

```sql
SELECT status, COUNT(*) AS run_count,
       SUM(records_extracted) AS total_extracted,
       SUM(records_inserted) AS total_inserted
FROM cegr.ingestion_run
WHERE started_at >= NOW() - INTERVAL '%s days'
GROUP BY status
ORDER BY run_count DESC;
```

### §3.2 失败率

```sql
SELECT
    (COUNT(*) FILTER (WHERE status IN ('PARTIAL', 'FAILED')))::float /
    NULLIF(COUNT(*), 0) AS failure_rate
FROM cegr.ingestion_run
WHERE started_at >= NOW() - INTERVAL '%s days';
```

### §3.3 失败 run 列表（含 source_registry + error_log）

```sql
SELECT ir.id, r.domain, r.category, ir.started_at, ir.finished_at,
       ir.records_extracted, ir.records_inserted,
       LEFT(ir.error_log, 200) AS error_preview
FROM cegr.ingestion_run ir
JOIN cegr.source_registry r ON ir.source_registry_id = r.id
WHERE ir.status IN ('FAILED', 'PARTIAL')
  AND ir.started_at >= NOW() - INTERVAL '%s days'
ORDER BY ir.started_at DESC
LIMIT %s;
```

### §3.4 Stale RUNNING 检测

```sql
SELECT ir.id, r.domain, r.category, ir.started_at,
       EXTRACT(EPOCH FROM (NOW() - ir.started_at))/3600 AS hours_running,
       ir.records_extracted, ir.triggered_by
FROM cegr.ingestion_run ir
JOIN cegr.source_registry r ON ir.source_registry_id = r.id
WHERE ir.status = 'RUNNING'
  AND ir.finished_at IS NULL
  AND ir.started_at < NOW() - INTERVAL '%s hours'
ORDER BY ir.started_at ASC;
```

### §3.5 按 source_registry 分解

```sql
SELECT r.domain, r.category,
       COUNT(*) AS total_runs,
       COUNT(*) FILTER (WHERE ir.status = 'SUCCESS') AS success_count,
       COUNT(*) FILTER (WHERE ir.status = 'PARTIAL') AS partial_count,
       COUNT(*) FILTER (WHERE ir.status = 'FAILED') AS failed_count,
       (COUNT(*) FILTER (WHERE ir.status IN ('PARTIAL','FAILED'))::float /
        NULLIF(COUNT(*), 0)) AS per_source_failure_rate,
       SUM(ir.records_extracted) AS total_extracted,
       SUM(ir.records_inserted) AS total_inserted
FROM cegr.ingestion_run ir
JOIN cegr.source_registry r ON ir.source_registry_id = r.id
WHERE ir.started_at >= NOW() - INTERVAL '%s days'
GROUP BY r.domain, r.category
ORDER BY total_runs DESC;
```

### §3.6 records 提取/插入 gap

```sql
SELECT ir.id, r.domain, r.category,
       ir.records_extracted, ir.records_inserted,
       (ir.records_extracted - COALESCE(ir.records_inserted, 0)) AS gap,
       CASE WHEN ir.records_extracted > 0
            THEN ROUND((ir.records_inserted::numeric / ir.records_extracted) * 100, 1)
            ELSE NULL END AS insertion_pct
FROM cegr.ingestion_run ir
JOIN cegr.source_registry r ON ir.source_registry_id = r.id
WHERE ir.records_extracted > 0
  AND (ir.records_inserted IS NULL OR ir.records_inserted < ir.records_extracted)
  AND ir.started_at >= NOW() - INTERVAL '%s days'
ORDER BY gap DESC
LIMIT 20;
```

### §3.7 运行时长统计

```sql
SELECT
    COUNT(*) AS run_count,
    AVG(EXTRACT(EPOCH FROM (finished_at - started_at))) AS avg_seconds,
    MIN(EXTRACT(EPOCH FROM (finished_at - started_at))) AS min_seconds,
    MAX(EXTRACT(EPOCH FROM (finished_at - started_at))) AS max_seconds,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (finished_at - started_at))) AS median_seconds,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (finished_at - started_at))) AS p95_seconds
FROM cegr.ingestion_run
WHERE finished_at IS NOT NULL
  AND started_at >= NOW() - INTERVAL '%s days';
```

### §3.8 趋势（每日成功率）

```sql
SELECT DATE(started_at) AS run_date,
       COUNT(*) AS daily_runs,
       COUNT(*) FILTER (WHERE status = 'SUCCESS') AS success,
       COUNT(*) FILTER (WHERE status IN ('PARTIAL','FAILED')) AS failed,
       (COUNT(*) FILTER (WHERE status IN ('PARTIAL','FAILED'))::float /
        NULLIF(COUNT(*), 0)) AS daily_failure_rate
FROM cegr.ingestion_run
WHERE started_at >= NOW() - INTERVAL '%s days'
GROUP BY DATE(started_at)
ORDER BY run_date ASC;
```

---

## §4. 告警机制

### §4.1 默认：脚本级告警（cron 友好）

```bash
# crontab 示例：每天 UTC 08:00（北京 16:00）检查
0 8 * * * cd /opt/china-platform && python3 scripts/monitor_ingest.py check >> /var/log/cegr-monitor.log 2>&1
```

**退出码语义**：
- `0` = OK（无告警）
- `1` = 失败率超阈值
- `2` = 有 stale RUNNING
- `3` = 两者兼有
- `>10` = 内部错误（DB 连接失败 / SQL 错误）

### §4.2 可选：Grafana dashboard（不强制上云）

若后续 Stage 1 tasking 批准 Grafana：
- **数据源**：PostgreSQL（`cegr` prod DB）
- **Panel 1**：状态分布 pie chart（最近 7 天）
- **Panel 2**：每日失败率折线图（30 天趋势）
- **Panel 3**：按 source_registry 分解的 bar chart
- **Panel 4**：stale RUNNING 计数（single stat）
- **Panel 5**：records gap 表格（top 20）

**不强制**：Stage 1 默认用 CLI + log；Grafana 留 tasking 决策。

### §4.3 可选：邮件/Slack 通知（不引入 Stage 1）

Stage 1 scope 仅 CLI + cron 退出码；邮件/Slack 通知留 Stage 2（per docs/08 §3 Stage 2 scope）。

---

## §5. 失败模式与恢复

### §5.1 监控自身失败

| 失败模式 | 症状 | 恢复 |
|---|---|---|
| DB 连接失败 | `psycopg2.OperationalError` + 退出码 >10 | 检查 `STAGE0_DSN` 环境变量 / DB 进程；重试 |
| SQL 语法错误 | `psycopg2.errors.SyntaxError` + 退出码 >10 | 检查 `schema/01-core.sql` ingestion_run schema 是否变更 |
| 空 ingestion_run 表 | `failure_rate = 0.0` + `stale_running = []` | 诚实报告；不假阳性 |
| cron 未跑 | 无日志输出 | 检查 crontab / launchd 配置 |

### §5.2 Stale RUNNING 恢复策略

**Stage 1 不自动恢复**（保守策略）：
- 监控脚本报告 stale RUNNING 列表
- 用户侧手动检查：connector 进程是否还在运行？
  - 是 → 等它完成（OCR 可能慢；默认 6h 阈值已留余量）
  - 否 → 手动 `UPDATE cegr.ingestion_run SET status='FAILED', finished_at=NOW() WHERE id='<stale_run_id>'`
- **不自动**改 DB（避免误判）

### §5.3 失败率高 → 用户侧响应

1. `python3 scripts/monitor_ingest.py failed` 查看失败 run 列表
2. 检查 `error_log` 列（每个 connector 在失败时写入具体错误信息）
3. 常见错误：
   - `FK violation` → S1.4-1.7 pilot 阶段正常（placeholder UUIDs）；S1.9+ 种子 reference data
   - `FileNotFoundError` → sample PDF/XLSX 缺失；检查 spike data 目录
   - `RuntimeError: tesseract missing` → spike 04 OCR 工具缺失；安装 `tesseract` + `tesseract-lang`
   - `psycopg2.errors.UniqueViolation` → source_document SHA-256 重复；检查 connector 是否被重复调用

---

## §6. 红线

| 红线 | 状态 |
|---|---|
| ❌ 不 Gate 1 PASS | 仅 S1.8 监控设计；Gate 1 留 W6 总评（docs/08 §2.3）|
| ❌ 不引入 DSH | 监控仅读 `ingestion_run`；不写 observation / source_document |
| ❌ 不引入新 DB 表 | 复用现有 `ingestion_run`；不创建 `ingest_alert` / `monitor_state` 等 |
| ❌ 不引入 PagerDuty/Slack | Stage 1 scope 仅 CLI + cron；邮件/Slack 留 Stage 2 |
| ❌ Cursor 写 `docs/22` / `ingest_monitor.py` / `scripts/monitor_ingest.py` 正文 | CC 起草；Cursor 仅审验 |
| ❌ 修改 `gate_thresholds.json` | 严禁（per B-3/B-6）|
| ❌ 不修改 `ingestion_run` schema | 现有表已够用；不加列 |
| ❌ 不修改 `observation` schema | 监控只读 |
| ❌ 不批量爬取历史数据 | 监控只查已有 ingestion_run 行 |
| ❌ 不降 OCR 门槛 | 监控不涉及 OCR 决策 |
| ❌ 强制上 Grafana 云 | Grafana 可选；不强制 Stage 1 scope |

---

## §7. 下一刀（Cursor 62 → 后续 tasking）

1. Cursor 审验 `docs/22` → `64-stage0-cursor-s18-plan-audit-*.md`
2. 通过后 → `65-stage1-s18-impl-tasking-*.md`（含 IngestMonitor 类签名 + CLI 入口 + ≥4 测试覆盖）
3. CC 实施 `ingest_monitor.py` + `monitor_ingest.py` + `test_ingest_monitor.py`
4. 可能扩展：Grafana dashboard JSON（若 tasking 批准）

---

## §8. 已知遗留（Cursor 62 后 tasking 决策候选）

| 项 | 状态 | 留待 |
|---|---|---|
| Grafana dashboard JSON | 可选；不强制 Stage 1 | 后续 tasking 决策 |
| 邮件/Slack 通知 | 不实现 | Stage 2（per docs/08 §3） |
| Stale RUNNING 自动恢复 | 不实现（保守策略；手动 UPDATE）| Stage 2 |
| ingestion_run 归档（>1 年旧数据）| 不实现 | Stage 2+ |
| observation_revision 监控 | 不实现（依赖 Stage 2 revision 表）| Stage 2 |
| connector retry 策略 | 不实现（monitoring 仅报告；不重试）| S1.9+ |
| 按 geo_entity 分解监控 | 不实现（observation 维度；Stage 1 仅 run 维度）| Stage 2 |
| Prometheus metrics endpoint | 不实现（Stage 1 仅 CLI + log）| Stage 2+ |
| 多 DB 监控（test + prod）| 不实现 | Stage 1+ 部署 tasking |

---

## §9. 引用

- `docs/08-mvp-plan.md` §2.1 任务清单：`S1.8 实施 ingest_run 监控 + 失败告警`
- `docs/21-stage1-s17-scanned-pdf-ocr-plan-20260825.md` §3.1：S1.7 connector 写入 `ingestion_run` 的流程
- `schema/01-core.sql` line 400-420：`ingestion_run` 表结构 + CHECK 约束 + 索引
- `reviews/61-stage0-cursor-s17-impl-audit-20260825.md`：S1.7 实施通过
- `reviews/62-stage1-s18-ingest-monitor-planning-tasking-20260825.md`：S1.8 规划任务书

— CC Plan 22 end —