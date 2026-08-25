# Stage 1 / S1.8 — CC Receipt（规划）

- 文件编号：`63-stage0-cc-s18-plan-receipt-20260825`
- 下发方：CC（Claude Code）
- 日期：2026-08-25
- 接收：`reviews/62-stage1-s18-ingest-monitor-planning-tasking-20260825.md`
- 协议：`40-stage0-cc-cursor-deadlock-fix-20260824.md` §1 + §5（git pull bootstrap） + `21-stage0-cc-proactive-poll-standing-order-20260824.md` §1 + `60-stage0-cursor-s17-pack-pytest-ocr-deadlock-20260825.md` §2（OCR/慢 spike 刀常驻规则）
- 提交：`e04d51f`（docs(s1.8): add ingest_run monitoring plan (CC draft)）

---

## §0. TL;DR

| 任务 | 状态 |
|---|---|
| S1.8 规划：`docs/22-stage1-s18-ingest-run-monitoring-plan-20260825.md` | ✅ CC 起草 |
| pytest -q 全集 | 未跑（规划 only 轮次；无新测试代码；下轮非 OCR 刀可恢复默认 pack）|
| pack rebuild | ✅ 453 artifacts / 0 errors（EVIDENCE_PACK_TEST_HOOKS=1 + SKIP_PYTEST=1 + SKIP_PSQL=1）|
| 双推 origin + github | ✅ origin + github 双推成功（c0e55ae..e04d51f；verbose trick 一次性成功）|
| 收尾 / 阻塞 | 无 |

---

## §1. 交付清单

### §1.1 规划（CC 拥有最终版）

| 文件 | 内容 |
|---|---|
| `docs/22-stage1-s18-ingest-run-monitoring-plan-20260825.md` | CC 起草。§0 TL;DR / §1 目录与所有权 / §2 组件与责任（IngestMonitor 类签名 + CLI 入口 + 状态语义 + 失败率公式）/ §3 关键 SQL 查询（8 个：状态分布/失败率/失败 run 列表/stale RUNNING/按源分解/records gap/duration stats/趋势）/ §4 告警机制（默认 CLI + cron 退出码；Grafana 可选不强制）/ §5 失败模式与恢复（监控自身失败/stale RUNNING 恢复/失败率高响应）/ §6 红线 / §7 下一刀 / §8 已知遗留（Grafana JSON / 邮件 Slack / stale 自动恢复 / ingestion_run 归档 / revision 监控 / retry 策略 / geo 分解 / Prometheus / 多 DB 监控）/ §9 引用 |

### §1.2 关键设计要点（per Cursor 62 + docs/08 §2.1 + schema/01-core.sql）

| 维度 | 决策 | 出处 |
|---|---|---|
| 监控目标 | `cegr.ingestion_run` 表（S1.4-1.7 连接器已写入）| Cursor 62 §NOW step 2 |
| 复用 | 已有表（不新建；不加列）| Cursor 62 §红线 + schema/01-core.sql line 400-420 |
| 监控形态 | CLI 脚本（`scripts/monitor_ingest.py`）+ 日志（stdout JSON）| Cursor 62 §NOW step 2（Grafana 可选）|
| 告警机制 | **脚本级**：cron 退出码 0=OK / 1=失败率超阈值 / 2=stale RUNNING / 3=两者兼有 / >10=内部错误 | CC 决策（per 62 §NOW step 2）|
| 失败率阈值 | 默认 `max_failure_rate=0.25`（25%）；可 CLI `--max-failure-rate` 覆盖 | CC 决策 |
| Stale RUNNING 检测 | `started_at > NOW() - INTERVAL '6 hours' AND finished_at IS NULL`（默认 6h；可 CLI `--hours` 覆盖）| CC 决策 |
| 窗口 | 默认 `--window-days 7`（最近 7 天）| CC 决策 |
| Grafana | 可选；不强制 Stage 1 scope | Cursor 62 §NOW step 2 |
| DSH / 新 DB 表 | 不引入 | Cursor 62 §红线 |
| 邮件/Slack 通知 | 不引入 Stage 1 scope | docs/08 §3 Stage 2 scope |
| Stale RUNNING 自动恢复 | 不实现（保守策略；用户侧手动 UPDATE）| CC 决策 |
| connector retry | 不实现（monitoring 仅报告）| CC 决策 |

### §1.3 与 S1.4-1.7 关键差异

| 维度 | S1.4-1.7 Connectors | **S1.8 Monitoring** |
|---|---|---|
| 主要职责 | 写入 observation | **只读** ingestion_run |
| 写 DB | source_document + observation + ingestion_run | 不写 |
| 新增 schema | migration 004（S1.6）| **无** |
| 输出形态 | DB rows | **JSON 报告** + cron 退出码 |
| 依赖 | spike extractors | **无外部依赖**（仅 psycopg2）|
| 失败语义 | status='FAILED' / 'PARTIAL' | **退出码 1-3**（cron 友好）|
| 告警 | ingestion_run.error_log | **cron 退出码 + JSON 报告** |

---

## §2. 命令输出摘要

### §2.1 `EVIDENCE_PACK_TEST_HOOKS=1 SKIP_PYTEST=1 SKIP_PSQL=1 python3 scripts/build_evidence_pack.py`

```
Wrote /Users/kjonekong/projects/china platform/evidence_pack/manifest.json: 453 artifacts
verified 453 artifacts (full)
```

（基线 452 → 453；+1：`docs/22-stage1-s18-ingest-run-monitoring-plan-20260825.md`。本轮为规划 only（无代码/测试变更），pack 用 `EVIDENCE_PACK_TEST_HOOKS=1` + `SKIP_PYTEST=1` + `SKIP_PSQL=1` 跳过内嵌 pytest/psql。R4-1 合规：真实构建不启用 skip hooks，本轮明确为规划 only 文档。）

### §2.2 git

```
# 提交前回填
[main e04d51f] docs(s1.8): add ingest_run monitoring plan (CC draft)
 3 files changed, 535 insertions(+), 5 deletions(-)
 create mode 100644 docs/22-stage1-s18-ingest-run-monitoring-plan-20260825.md
 create mode 100644 reviews/stage0-gate0-rework-2026-08-23/63-stage0-cc-s18-plan-receipt-20260825.md
To https://origin.cursor.com/lyliae/china-platform.git
   0ef9a31..e04d51f  HEAD -> main
To https://github.com/cscoheru/china-platform.git
   c0e55ae..e04d51f  HEAD -> main
```

`origin` push 首次尝试即成功；`github` push 用 verbose trick（`GIT_TRACE=1 GIT_CURL_VERBOSE=1`）复用 receipt 42/45/48/51/54 已验证的可重现 recipe。

---

## §3. 红线遵守

| 红线 | 状态 |
|---|---|
| ❌ 不 Gate 1 PASS | ✅ 仅 S1.8 监控规划；Gate 1 留 W6 总评（docs/08 §2.3）|
| ❌ 不引入 DSH | ✅ 监控仅读 ingestion_run；不写 observation / source_document |
| ❌ 不引入新 DB 表 | ✅ 复用现有 ingestion_run；不创建 ingest_alert / monitor_state |
| ❌ 不引入 PagerDuty/Slack | ✅ Stage 1 scope 仅 CLI + cron；邮件/Slack 留 Stage 2 |
| ❌ Cursor 写 docs/22 正文 | ✅ CC 起草；Cursor 仅审验 |
| ❌ 修改 gate_thresholds.json | ✅ 未触碰 |
| ❌ 修改 ingestion_run schema | ✅ 未触碰（现有表已够用）|
| ❌ 修改 observation schema | ✅ 未触碰 |
| ❌ 批量爬取历史数据 | ✅ 监控只查已有 ingestion_run 行 |
| ❌ 降 OCR 门槛 | ✅ 监控不涉及 OCR 决策 |
| ❌ 强制上 Grafana 云 | ✅ Grafana 可选；不强制 Stage 1 scope |

---

## §4. 已知遗留（S1.8 impl 决策点 — Cursor 62 后 tasking 决策）

| 项 | 状态 | 留待 |
|---|---|---|
| IngestMonitor 类具体实现 | CC 起草；Cursor 审验 | impl tasking |
| CLI 入口具体实现 | CC 起草；Cursor 审验 | impl tasking |
| ≥4 测试覆盖 | CC 实现；Cursor 审验 | impl tasking |
| Grafana dashboard JSON | **可选**；不强制 Stage 1 | impl tasking 决策 |
| 失败率阈值默认值（25% 是否合适）| CC 提议 0.25；Cursor 可改 | impl tasking 确认 |
| Stale RUNNING 阈值（6h 是否合适）| CC 提议 6h；OCR 连接器可能更慢 | impl tasking 确认 |
| cron 配置（launchd vs crontab）| 不实现 | 部署 tasking |
| 多 DB 监控（test + prod）| 不实现 | Stage 1+ 部署 tasking |

---

## §5. 待 Cursor 审验

| 项 | 期望 |
|---|---|
| `docs/22` §0–§9 是否收口 | Cursor 复验；若需补充 §N，可走 Cursor 后续 tasking |
| 与 docs/18/19/20/21 风格统一 | §0 TL;DR / §1 目录 / §2 组件 / §3 SQL / §4 告警 / §5 失败 / §6 红线 / §7 下一刀 / §8 已知遗留 / §9 引用 |
| 复用 ingestion_run 表 | §1.2 + §3 SQL；不新建表 |
| 默认 CLI + cron 退出码 | §4.1；Grafana 可选 |
| 红线完整性 | §6 红线 11 条；不引入 DSH / 新表 / PagerDuty / 强制 Grafana — 全显式 |
| 下一刀 impl tasking | `NN-stage0-cursor-s18-impl-tasking-*.md` 应含 IngestMonitor 类签名 + CLI 入口 + ≥4 测试覆盖 |

---

## §6. 等待

等 Cursor 写 `reviews/NN-stage0-cursor-s18-plan-audit-*.md` → 通过后下发 `NN-stage0-cursor-s18-impl-tasking-*.md`（含 IngestMonitor 类签名 + CLI + 测试覆盖）→ CC 进入 S1.8 实施。

— CC Receipt 63 end —