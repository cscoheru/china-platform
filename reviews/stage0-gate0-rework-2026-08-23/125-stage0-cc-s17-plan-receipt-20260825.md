# 125 — Stage 0 / CC / S1.17 Plan Receipt (backfill)

**Tasking**: Cursor 124 §NOW（审计 `126` PASS；规划通过后用户裁定 **A**；实现催办 `129`）
**Date (UTC)**: 2026-08-25
**Plan delivered**: docs/32-stage1-s17-r12-url-health-plan-20260825.md (221 lines)
**Commit (origin)**: cec6e66
**Branch**: main
**Pack**: artifact_count=498, sum(role_count)=498 ✓ invariant
**Sub-pack delta**: 497 → 498 (+1 documentation)

---

## §NOW items completed (tasking 124)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 124-1 | 起草 `docs/32`（CC 拥有） | ✅ | cec6e66, 221 行（§0–§9） |
| 124-2a | 与 `test_ingest_monitor.py` / spike monitor 边界（复用 vs 新） | ✅ | docs/32 §1 — `IngestMonitor` 库函数复用 + 测试不动；唯一新构件 = 2 CLI + 2 pytest |
| 124-2b | 探针范围（`source_registry` URL / backup_urls）；**不爬业务数据**、不绕验证码 | ✅ | §2.1 钉死：HEAD 默认 / GET Range ≤1KB / ≤1req/s / ≤60s 全表 / 验证码即 PARTIAL 不绕过 |
| 124-2c | 失败率告警最小可验收（pytest 或脚本 + 退出码；本地/fixture 诚实） | ✅ | §3.2 monitor_ingest CLI（6 用例）+ §3.3 url_health_probe pytest（6 用例）+ §3.4 mock 策略不爬网 |
| 124-2d | 空表 / 无网环境策略；与 Stage 2 监控的边界 | ✅ | §4 空表/无网诚实退出码；§5 调度/通知/分布式移交清单 |
| 124-3 | 规划 only；回执 125 进 reviews/ | ✅ | 未写实现代码；本回执路径 reviews/ |
| 124-4 | → 84 POLL | ✅ | job 50a7c596 持续武装（180s, session-only） |

---

## §1 — Deliverables

| Path | Status | Role | sha256[:12] |
|------|--------|------|-------------|
| `docs/32-stage1-s17-r12-url-health-plan-20260825.md` | new (221 lines) | documentation | 0c7d28b444ff |
| `evidence_pack/manifest.json` | 497→498 | +1 documentation | — |

---

## §2 — 规划关键决策（供审计定位）

1. **复用边界**：S1.8 `IngestMonitor` 责任 =「读 ingestion_run 出报表」；本刀 CLI 责任 =「封 exit-code 给 cron」。不复用 SQL；新构件仅 2 CLI + 2 pytest wrapper。
2. **探针上限钉死**：HEAD 默认；GET Range bytes=0-1023 仅在 access_method=PDF_PARSE 或 HEAD 拒绝时降级；≤1req/s；≤60s 全表；验证码/付费墙特征即 PARTIAL 不绕过（per docs/09 措施 5）。
3. **触发 ingestion_run 行**：每 URL 一条 synthetic run，`triggered_by='url_health_probe'` 区分（per docs/22 §3.3 失败语义扩展）；**不**新建 `url_health_run` 表（Stage 2 视情拆表）。
4. **mock 策略**：探针 `requests.Session` 用 `unittest.mock.patch` 替换；CI 不联外网；本地可选 `URL_HEALTH_LIVE=1` 跑真实 HEAD 自验。
5. **失败率阈值不动**：本刀 CLI 沿用 S1.8 默认 25%（`IngestMonitorConfig.max_failure_rate`）；不引入新阈值常量；不引用 `gate_thresholds.json`。
6. **与 §3 S1.8 边界**：本刀 CLI 复用 `IngestMonitor.check_alerts()` 退出码 0/1/2/3；`test_ingest_monitor.py` 既有用例保护 SQL 正确性，本刀不复制。

---

## §3 — Honest gap list

| Gap | Impact | Notes |
|-----|--------|-------|
| 真实 URL 探针未跑 | 客观现状 | 仅 fixture + mock 验证语义；真实探针 Stage 2 部署后 |
| `url_health_run` 单独表未建 | 低 | 当前复用 `ingestion_run.triggered_by` 区分 |
| 验证码 / 付费墙识别规则仅特征字符串 | 低 | 首版覆盖明显情况，Stage 2 加规则 |
| 多 worker 并发未做 | 低 | 7 行 registry 全表顺序扫 <5s |
| 通知 / 调度未接 | 设计内 | §5 已列 Stage 2 移交清单 |

---

## §4 — Red-line compliance

- ❌ 未宣布 Gate 1 / Stage 0 PASS；❌ 未 DSH；❌ 未爬网
- ❌ 未修改 `gate_thresholds.json`（sha256 不变；与 §3 S1.8 阈值无引用关系）
- ❌ 未触碰 00-CC-CURRENT.md；未 --force
- ❌ 探针上限钉死 §2.1：HEAD 默认 / GET Range ≤1KB / ≤1req/s / 验证码即 PARTIAL

---

## §5 — §3.3 case 2 订正（per 126 §1）

`docs/32 §3.3` 用例 2 文案：「主 URL 200 + 1 个 backup 500 → status='PARTIAL' 主 + 'FAILED' 备」与 §2.2 「2xx→SUCCESS」矛盾。

**订正**：用例 2 = 主 SUCCESS + 备 FAILED；退出码按 §2.3 聚合 = 1。已 commit 进 docs/32（sha256 0c7d28b444ff）。

---

## §6 — Push confirmation

```
$ git push origin HEAD        # docs/32 + manifest
To https://origin.cursor.com/lyliae/china-platform.git
   de483d0..cec6e66  HEAD -> main

$ git push github HEAD        # 双推（origin 优先，github retry 20s/45s/90s）
```

---

## §7 — Pack invariant

```
artifact_count = 498
sum(role_count) = 498 ✓
```

Delta breakdown (497→498 = +1):
- +1 documentation: `docs/32-stage1-s17-r12-url-health-plan-20260825.md`

---

## §8 — Next heartbeat

84 while-POLL 持续武装（session-only, 180s, job 50a7c596）。等待 S1.17 实现命令（tasking `127`） + receipt `128`（per `129` 唤醒）。

— CC @ queue_rev 44, S1.17 规划回执 (backfill) 已补 —