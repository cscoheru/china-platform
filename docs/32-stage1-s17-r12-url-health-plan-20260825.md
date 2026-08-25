# Stage 1 / S1.17 — R12 URL 健康探针 + ingest 失败率自动化 规划

- 编号：`docs/32-stage1-s17-r12-url-health-plan-20260825`
- 前置：S1.16 PASS（Cursor `123`）；用户裁定 **A**；`docs/27` §4.1 缺口 #5
- 范围：**规划 only**（实现另开；本文为 §NOW 交付物）

---

## §0. 背景与目标

**业务问题**：R12（`docs/09-risk-register.md`）= URL 漂移。`source_registry.primary_url` / `backup_urls` 在源站改版/下架后无人察觉，直到 `ingestion_run` 失败才被发现；失败率告警未自动化（spike 仅有手动 `ingest_monitor` 模块 + `tests/test_ingest_monitor.py`，无 CLI、无调度）。

**目标刀**：补两层自动化 ——

1. **URL 健康探针**（本刀主）：对 `source_registry` 每个 enabled 行的 `primary_url` 与 `backup_urls[]` 做轻量 HTTP HEAD/GET-元数据 探活；不抓业务数据、不绕验证码/付费墙。失败 → 写 `ingestion_run.status='FAILED'` 标记一条合成记录供后续监控消费（per docs/22 §3.3 失败语义）。
2. **ingest 失败率告警**（本刀次）：在 `ingest_monitor.py` 之上加 CLI 入口 `scripts/monitor_ingest.py`（per docs/22 §2.2 已规划但未实现），cron 退出码 0/1/2/3 与 `test_ingest_monitor.py` 一致；缺 .venv-dbt → 复用既有 `CEGR_DSN` 直接跑。

**目标边界**：本刀交付可重复运行、退出码可信的两条命令（`url_health` + `monitor_ingest check`），覆盖 `docs/26` §1.4 / `docs/27` §4.1 缺口 #5。**真实 cron 调度 + 通知（Slack/邮件）+ 分布式去重** —— Stage 2。

---

## §1. 与既有构件的边界

| 既有构件 | 责任 | 本刀动作 |
|---|---|---|
| `backend/.../monitoring/ingest_monitor.py` (S1.8) | 只读查询 `cegr.ingestion_run`；输出 status 分发/失败率/stale RUNNING | **复用为库函数**；不复制 SQL |
| `tests/test_ingest_monitor.py` (S1.8) | ingest_monitor 的 pytest 覆盖（10 用例） | **不动**；既有用例继续保护 SQL 正确性 |
| `dbt/tests/test_cross_source_consistency_threshold.sql` (S1.16) | R03 跨源冲突自动化 | **不动** |
| `tests/test_acceptance_e2e_s15.py` (S1.15) | §2.7/2.8/2.9 自动化 | **不动** |
| `source_registry.backup_urls` (schema/01-core.sql) | 多备选 URL 字段 | **复用为目标** |
| `source_registry.access_method` | `extraction_method` enum（API/HTTP/PDF_PARSE/CSV_PARSE/...） | 探针按 access_method 选 HEAD 或 GET-bytes-N |
| `source_registry.enabled` | 仅 enabled=TRUE 行被探针扫到 | **复用为过滤器** |
| `cegr.ingestion_run.status='FAILED'` | 现有 RUN 状态枚举 | **复用为合成失败标记**（triggered_by='url_health_probe' 区分） |

**唯一新增构件**（实现刀）：
- `scripts/url_health_probe.py`：CLI；扫 `source_registry`，HEAD 主 + 备选 URL，写 `ingestion_run`
- `scripts/monitor_ingest.py`：CLI；封装 `IngestMonitor.check_alerts` / `generate_report`（per docs/22 §2.2 接口）
- `tests/test_url_health_probe.py`：pytest 覆盖（探针行为 + 写库 + 退出码）
- `tests/test_monitor_ingest_cli.py`：pytest 覆盖（CLI 退出码与 `test_ingest_monitor` 一致）

**migration**：**无**。`ingestion_run` 表已支持 `triggered_by` 区分来源；`source_registry` 无需改字段。

---

## §2. URL 健康探针设计

### §2.1 探针范围（钉死上限）

| 范围项 | 上限 |
|---|---|
| **HTTP 方法** | 默认 `HEAD`；仅当 `access_method='PDF_PARSE'` 或目标服务器拒绝 HEAD 时降级 `GET` 并 `Range: bytes=0-1023`（≤1KB 元数据） |
| **目标** | `source_registry` 中 `enabled=TRUE` 的 `primary_url` + `backup_urls[]`；URL 长度 ≤2048 |
| **请求频率** | **每源 ≤1 req/s**（per docs/09 措施 2；与既有 connector 同节流）；并发 worker ≤4 |
| **超时** | connect 5s / read 10s / total 15s |
| **重试** | **1 次**指数退避（500ms 后）；不重试 |
| **总耗时上限** | **60s 全表**（registry 现 7 行；未来 200 行仍可控） |
| **UA** | 标识 `cegr-url-health/1.0 (+probe)` —— 便于源站管理员识别 |
| **验证码 / 付费墙 / 登录** | **触发即放弃 + 记 SKIPPED**（`error_log` 写 `'captcha_or_paywall_detected'`）；**不绕过** |
| **robots.txt** | 探针 **不解析 robots.txt** —— 健康检查与爬虫策略解耦（per docs/09 措施 5）；接入源站以 `/robots.txt` 屏蔽时可由人工改 `enabled=FALSE` |

### §2.2 探针语义（每 URL 一条 `ingestion_run`）

```sql
INSERT INTO cegr.ingestion_run (
  id, source_registry_id, started_at, finished_at, status,
  records_extracted, records_inserted, error_log, triggered_by
) VALUES (
  uuid_generate_v4(), <registry_id>, NOW(), NOW(), <status>,  -- finished_at = started_at for synthetic probe runs
  0, 0, <error_log or NULL>, 'url_health_probe'
);
```

| HTTP 结果 | ingestion_run.status | error_log |
|---|---|---|
| 2xx | `'SUCCESS'` | NULL |
| 3xx（HEAD→GET 跟随后 2xx） | `'SUCCESS'` | NULL |
| 4xx 客户端错 | `'FAILED'` | `'<code> <reason>'`（前 200 字符） |
| 5xx 服务器错 | `'FAILED'` | `'<code> <reason>'` |
| ConnectTimeout / ReadTimeout | `'FAILED'` | `'timeout: <kind>'` |
| DNS / SSL / ConnectionError | `'FAILED'` | `'<err_class>: <msg[:200]>'` |
| 验证码 / 付费墙特征（HTML 含 `captcha`/`paywall`/`login required`） | `'PARTIAL'` | `'captcha_or_paywall_detected'` |
| HEAD 不支持 + GET Range 仍失败 | `'FAILED'` | `'HEAD+GET_Range: <err>'` |

### §2.3 探针退出码

| 退出码 | 含义 |
|---|---|
| 0 | 全部 enabled 源 URL 探活通过；无 FAILED/PARTIAL |
| 1 | ≥1 URL FAILED 但无 PARTIAL |
| 2 | ≥1 URL PARTIAL（验证码/付费墙）但无 FAILED |
| 3 | FAILED + PARTIAL 同时存在 |

### §2.4 与失败率告警的耦合

`ingest_monitor.check_alerts()`（S1.8 既有用例已保护）现在消费 `ingestion_run` 表；当探针写入足够多 FAILED 行后，**自动**参与失败率计算 —— 本刀**不修改** ingest_monitor。

---

## §3. 失败率告警自动化最小可验收

### §3.1 一条命令可重复无网络跑：

```bash
python3 scripts/monitor_ingest.py check --max-failure-rate 0.25 --window-days 7
```

| 返回 | 含义 |
|---|---|
| exit 0 | OK；可入 cron |
| exit 1 | 失败率超阈值 |
| exit 2 | stale RUNNING 存在 |
| exit 3 | 失败率 + stale 都有 |

### §3.2 pytest wrapper（≥5 用例；缺环境 skip）

`tests/test_monitor_ingest_cli.py`：

| # | 用例 | 期望 |
|---|---|---|
| 1 | `--help` 退出码 0 | CLI 可执行 |
| 2 | 空表 → `check` 退出码 0 | 空表诚实（与 `test_ingest_monitor` 一致） |
| 3 | 4 行（1 SUCCESS + 3 FAILED）→ 退出码 1 | 失败率触发 |
| 4 | 1 RUNNING >6h + ≥1 SUCCESS → 退出码 2 | stale 触发 |
| 5 | 1 RUNNING >6h + 3 FAILED → 退出码 3 | 复合触发 |
| 6 | 注入 1 FAILED 后 `report` 输出 JSON 含 `failure_rate` 字段 | CLI 报表 |

### §3.3 pytest wrapper for URL 探针（≥5 用例）

`tests/test_url_health_probe.py`：

| # | 用例 | 期望 |
|---|---|---|
| 1 | 无源（registry 为空）→ 退出码 0 + 不写 ingestion_run | 空表诚实 |
| 2 | 主 URL 200 + 1 个 backup 500 → status='PARTIAL' 主 + 'FAILED' 备 | 200/500 分流 |
| 3 | 主 URL 4xx → 主 'FAILED' + 备未探（不级联） | 失败不传染 |
| 4 | 验证码特征 HTML → 'PARTIAL' | 不爬 + 放弃 |
| 5 | DNS 失败 → 'FAILED' + error_log 含 `'DNSError'` | 异常分类 |
| 6 | `enabled=FALSE` 行被跳过 | 启用过滤 |

**探针侧 mock 策略**：用 `unittest.mock.patch('requests.head')` 与 `requests.get` 返回 fixture；不跑真实网络（per 红线 §6）。

### §3.4 fixture 策略

- **不爬网**：探针内 `requests.Session` 用 mock 替换；测试 fixture 注入伪响应。
- **不写 ingestion_run** 既不污染：每个测试 `TRUNCATE cegr.ingestion_run`（`observation_no_delete` 不涉及 `ingestion_run`）。
- **source_registry fixture**：沿用 `test_ingest_monitor.py` 模块级 `imported_registry`（`source_registry/registry.csv` 导入）；URL 健康测试**额外**注入 `backup_urls` 与 `enabled` flag —— 不污染 CSV。
- **networkx 真实探针**：CI 不跑（per 红线 §6）；本地开发可选 `URL_HEALTH_LIVE=1` 跑真实 HEAD（开发机自验）。

---

## §4. 空表 / 无网环境策略

| 场景 | 行为 |
|---|---|
| `source_registry` 为空 | 探针退出码 0；不写 ingestion_run；stdout `OK: 0 sources probed` |
| `ingestion_run` 为空 | `monitor_ingest check` 退出码 0；空表诚实（与 S1.8 既有用例一致） |
| **探针在无网环境跑** | 网络异常 → 全部 URL 走 'FAILED'；退出码 1；**不**静默成功 |
| `monitor_ingest` 在无网环境跑 | **不依赖网络**（纯 DB 查询）；DB 可达即跑 |

---

## §5. 与 Stage 2 监控的边界

| 本刀交付 | Stage 2 移交 |
|---|---|
| CLI 可重复执行 + 退出码可信 | Cron 调度（`crontab` / k8s CronJob） |
| pytest wrapper 验证语义 | CI 集成（与 S1.16 dbt pytest 同 CI step） |
| `ingestion_run.triggered_by='url_health_probe'` 区分 | 通知（Slack webhook / 邮件 / PagerDuty） |
| 失败率 25% 阈值（沿用 S1.8 默认） | 阈值动态化（按源 trust_tier 调） |
| 单实例 / 全表顺序扫 | 分布式（多 worker + Redis 去重 + 指数退避） |
| **不**保存 `url_health_run` 单独表 | 持久化探针历史（便于回溯 URL 漂移时间） |

---

## §6. 红线（沿用 `docs/09` + Cursor 124）

- ❌ 不宣布 Gate 1 / Stage 0 PASS
- ❌ 不批量 2020-2025
- ❌ 不 HTTP 爬业务数据（仅 HEAD/GET-bytes-0-1023 元数据；上限 §2.1 钉死）
- ❌ 不绕验证码 / 付费墙 / 登录（触发即记 PARTIAL + 不再尝试）
- ❌ 不把 1909 代表中国 / 不把陕西标为门控
- ❌ 不擅自 --force / --force-with-lease
- ❌ 不替用户下裁定（阈值 / 调度频率 / 通知渠道）
- ❌ 不改 `gate_thresholds.json`（spike-04 评测构件，只读）
- ❌ Cursor 不写 `docs/32` 正文
- ❌ 不触碰 `00-CC-CURRENT.md`
- ❌ 不 commit 除非 §NOW 明确要求
- ❌ 不把心跳写到磁盘

---

## §7. 诚实缺口

| Gap | Impact | Notes |
|-----|--------|-------|
| 真实 URL 探针未跑（CI 不联外） | 客观现状 | 仅 fixture + mock 验证语义；首次真实探针在 Stage 2 部署后 |
| `url_health_run` 单独表未建 | 低 | 当前复用 `ingestion_run` 区分字段 `triggered_by`；Stage 2 视情拆表 |
| 验证码 / 付费墙识别规则仅特征字符串 | 低 | 真实业务可能更复杂；首版特征覆盖明显情况，Stage 2 加规则 |
| 多 worker 并发未做 | 低 | 7 行 registry 全表顺序扫 <5s；规模上来再分片 |
| 通知 / 调度未接 | 设计内 | §5 已列入 Stage 2 移交清单 |

---

## §8. 与 §2.4 / S1.16 的边界声明

- §2.4 跨源一致性阈值（**2%/5%**）属 mart + singular test 责任（S1.16 已交）—— **本刀不参与**。
- §3 失败率阈值（**25%** 默认）属 ingest_monitor（**S1.8** 已交）—— 本刀**复用为库函数**，不复制 SQL，不引入新阈值常量。
- `gate_thresholds.json`（spike-04 评测构件）—— 本刀不读、不写、不引用。

---

## §9. 后续刀（Stage 1 候选）

| 编号 | 主题 | 状态 |
|---|---|---|
| S1.18 | R12 实施（URL 探针 + CLI 告警）；本规划打基础 | 候选 |
| S1.19 | 跨源一致性 §2.7/2.8/2.9 端到端补缺（docs/27 §4.1 #3） | 候选 |
| S1.20 | 真实研究问题 demo 扩样 | 候选 |

**S1.18 不在本刀范围**；本文仅为规划 + 任务书 + 红线 + 边界声明。

— End —