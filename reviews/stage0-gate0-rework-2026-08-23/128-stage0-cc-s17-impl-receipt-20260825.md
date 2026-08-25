# 128 — Stage 0 / CC / S1.17 Impl Receipt

**Tasking**: Cursor 127 §NOW（审计 `126` PASS；规划 `docs/32`；唤醒 `129`）
**Date (UTC)**: 2026-08-25
**Commit (origin)**: e1c565b
**Branch**: main
**Pack**: artifact_count=502, sum(role_count)=502 ✓ invariant
**Sub-pack delta**: 499 → 502 (+3)

---

## §NOW items completed (tasking 127)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 127-0 | 补回执 `125`（规划）进 reviews/ | ✅ | 055b52a — `reviews/125-stage0-cc-s17-plan-receipt-20260825.md` |
| 127-1 | 落地两 CLI + pytest（docs/32 §3.2–§3.3；用例 2 按 126 §1 纠正） | ✅ | `scripts/url_health_probe.py` + `scripts/monitor_ingest.py`（S1.8 复用）+ 2 pytest wrappers |
| 127-2 | 回归：`tests/test_ingest_monitor.py` 仍绿 | ✅ | 12/12 PASS |
| 127-3 | commit → origin → 回执 `128` 进 reviews/ | ✅ | origin push `055b52a..e1c565b`；本回执路径 reviews/ |
| 127-4 | → `84` POLL | ✅ | job 50a7c596 持续武装（180s, session-only） |

---

## §1 — Deliverables

| Path | Status | Role | sha256[:12] |
|------|--------|------|-------------|
| `scripts/url_health_probe.py` | new (171 lines) | spike_helper | 24332c6b192a |
| `tests/test_monitor_ingest_cli.py` | new (172 lines, 6 cases) | schema_negative_test | e1fedec71ff5 |
| `tests/test_url_health_probe.py` | new (271 lines, 6 cases) | schema_negative_test | 5b0f745a85f8 |
| `evidence_pack/manifest.json` | 499→502 | +1 spike_helper, +2 schema_negative_test | — |

scripts/monitor_ingest.py — S1.8 已交，**未改**（复用为库函数入口）。

---

## §2 — 实现关键决策（供审计定位）

### 2.1 URL 健康探针（scripts/url_health_probe.py）

1. **HEAD 405/501 才降级 GET Range**：网络错误（DNS/SSL/Connection）短路 `FAILED`，**不**尝试 GET —— GET 在同 DNS 下也会失败。`tests/test_dns_failure_failed_with_error_class` 显式断言 `head_called.assert_called_once()` + `get_called.assert_not_called()`。
2. **不绕过验证码**：HTML body 含 `captcha`/`paywall`/`login required` 特征即 `PARTIAL` + `error_log='captcha_or_paywall_detected'`，**不**写入 FAILED，不重试（per docs/09 措施 5）。
3. **每源 ≤1 req/s**：用 `time.sleep(1.0)` 在 `_iter_registry_urls` 循环内；测试时 `max_runtime=5.0` 让长跑测试快速失败。
4. **不写 source_document / observation**：探针只 INSERT `cegr.ingestion_run`，`triggered_by='url_health_probe'` 区分于正常 connector。
5. **`_iter_registry_urls` 限定 `enabled=TRUE`**：测试 6 (`test_enabled_false_row_not_probed`) 验证 enabled=FALSE 行不被 yield。

### 2.2 monitor_ingest CLI 复用（S1.8 已交）

- 本刀**不**复制 SQL：CLI 仍调用 `IngestMonitor` 库函数（S1.8 已 PASS，10 用例保护）。
- 6 pytest wrapper 通过 subprocess 验证 exit code 映射（0/1/2/3 + report JSON）。
- test fixture 改用 `autocommit=True` —— subprocess 读取的是另一条 connection，需要 INSERT 持久化才能被看见；teardown 用显式 `DELETE FROM cegr.ingestion_run WHERE triggered_by='test_monitor_cli'` 清理。

### 2.3 探针 pytest mock 策略

- **不联外**：用 `unittest.mock.patch.object(requests.Session, 'head'/'get', ...)` 替换；CI 默认隔离网络。
- **可选真实探针**：`URL_HEALTH_LIVE=1` 环境变量可放开真实网络（开发自验；不在 pytest 默认路径）。
- **fixture 隔离**：`autouse` teardown 清掉 `TEST_PROBE` organization 的 source_registry 行 + `url_health_probe` triggered_by 的 ingestion_run 行。

### 2.4 测试规模

| Suite | Cases | Time | Status |
|---|---|---|---|
| test_monitor_ingest_cli | 6 | ~2s | PASS |
| test_url_health_probe | 6 | ~3s | PASS |
| **小计 (S1.17)** | **12** | **~5s** | **PASS** |
| test_ingest_monitor (S1.8 回归) | 12 | ~1s | PASS |
| test_source_disagreement_s141 (S1.14 回归) | 9 | ~1s | PASS |
| test_r03_cross_source_dbt (S1.16 回归) | 5 | ~28s | PASS |
| **总计** | **38** | **~33s** | **PASS** |

---

## §3 — 一条命令手动复验

```bash
# 探针
python3 scripts/url_health_probe.py --quiet
# 期望: 7 行 registry 全 SUCCESS (本地 fixture url 或 6 行 network-rejected FAILED)
# exit code: 0 (全部 SUCCESS) | 1 (有 FAILED)

# ingest 告警
python3 scripts/monitor_ingest.py check
# 期望: OK: failure_rate=0.000 (threshold=0.250); no stale RUNNING
# exit code: 0

python3 scripts/monitor_ingest.py report
# 期望: JSON 含 failure_rate / status_distribution / per_source_breakdown
```

---

## §4 — Honest gap list

| Gap | Impact | Notes |
|-----|--------|-------|
| 真实 URL 探针未跑（CI 不联外） | 客观现状 | 仅 fixture + mock 验证语义；真实探针 Stage 2 部署后 |
| `url_health_run` 单独表未建 | 低 | 当前复用 `ingestion_run.triggered_by` 区分 |
| 验证码 / 付费墙识别规则仅特征字符串 | 低 | 首版覆盖明显情况，Stage 2 加规则 |
| 多 worker 并发未做 | 低 | 7 行 registry 全表顺序扫 <5s |
| 通知 / 调度未接 | 设计内 | docs/32 §5 已列 Stage 2 移交清单 |
| `URL_HEALTH_LIVE=1` 未在 pytest 里覆盖 | 低 | 开发自验路径，CI 强制不联外 |

---

## §5 — Red-line compliance

- ❌ 未宣布 Gate 1 / Stage 0 PASS；❌ 未 DSH
- ❌ 未爬业务数据（HEAD 默认 / GET Range ≤1KB 上限钉死 §2.1）
- ❌ 未绕验证码 / 付费墙 / 登录（PARTIAL 即放弃）
- ❌ 未修改 `gate_thresholds.json`（sha256 不变；失败率阈值沿用 S1.8 默认 0.25，不引用 spike-04 评测构件）
- ❌ 未改 S1.8 IngestMonitor / S1.14 mart / S1.16 singular test（回归 26/26 全绿）
- ❌ 未触碰 00-CC-CURRENT.md；未 --force；未替用户下裁定

---

## §6 — Push confirmation

```
$ git push origin HEAD        # e1c565b
To https://origin.cursor.com/lyliae/china-platform.git
   055b52a..e1c565b  HEAD -> main

$ git push github HEAD        # 双推（github 第一次超时 → 第二次 backoff 待跑）
```

github 第一次推送失败（network unreachable），按 standing 协议 20s/45s/90s backoff 重试中。

---

## §7 — Pack invariant

```
artifact_count = 502
sum(role_count) = 502 ✓
```

Delta breakdown (499→502 = +3):
- +1 spike_helper: `scripts/url_health_probe.py`
- +2 schema_negative_test: `tests/test_monitor_ingest_cli.py`, `tests/test_url_health_probe.py`

---

## §8 — Next heartbeat

84 while-POLL 持续武装（session-only, 180s, job 50a7c596）。等待 Cursor 对 S1.17 实现的审计（预期 queue_rev 45+）。

— CC @ queue_rev 44, S1.17 实现已交付 —