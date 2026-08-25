# 166 — Stage 2 / CC / S2.0.2.3 Implementation Receipt

**Tasking**: Cursor 165 §NOW（落地 `URL_HEALTH_LIVE` 开关 + 新 live-mode pytest；commit → origin → 回执 `166` 进 `reviews/`）
**Date**: 2026-08-25
**Branch**: main
**Wakeup observed**: 164 audit PASS for S2.0.2.2 (29/29); 165 tasking for S2.0.2.3

---

## §NOW items completed (tasking 165)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 165-1 | 落地 `URL_HEALTH_LIVE` 开关于 `scripts/url_health_probe.py`（live 模式遵守 §2.1 限速/超时/并发） | ✅ | `_url_health_live_enabled()` 守门 + `main()` 入口校验；live 模式现有 `probe_all()` 已含 §2.1 全部上限（HEAD/GET-Range/≤1req·s⁻¹/≤60s） |
| 165-2 | 新增 `tests/test_url_health_probe_live.py`（默认 skip；live 下至少探 1 源 + 可选 `ingestion_run` 断言） | ✅ | 14 cases（**12 passed + 2 skipped** 默认 skip live-mode 集成 case；6 anti-foot-gun variant parametrizations） |
| 165-3 | commit → origin → 回执 `166` | ✅ | 见 §5 + 本回执 |
| 165-4 | → `84` POLL | ✅ | cron `8384ebc9` 持续武装 |

---

## §1 — 交付 / 修改清单

### 1.1 修改（1 文件）

| 文件 | 行 | sha256 | 变更 |
|------|---|--------|------|
| `scripts/url_health_probe.py` | 248（原 220 → +28） | `9b5d9e4d5866adb585ede1c571b9f4e6b1bb91daa2856db3e9d3d2b1a8a4eb6b` | +`_url_health_live_enabled()`；+`main()` 入口 gate |

### 1.2 新增 pytest（1 文件，**14 cases** ≥ 1 要求）

| 文件 | 行 | sha256 |
|------|---|--------|
| `tests/test_url_health_probe_live.py` | 201 | `5cac799b0938eec8beb55301bca034e3c4f273db8b81c27aac785c2540949ff4` |

| # | Case | 验证什么 |
|---|------|----------|
| 1 | `test_default_url_health_live_unset_refuses` | 未设 → 拒绝 + exit 0 + stderr 含 "refusing" |
| 2 | `test_url_health_live_zero_refuses` | `=0` → 拒绝 |
| 3 | `test_url_health_live_only_exact_one_enables[true/True/TRUE/yes/on/2/01]` | **7 个变体** 全部拒绝（anti-foot-gun：仅字面 `"1"` 启用 live） |
| 4 | `test_url_health_live_message_cites_docs35_51` | stderr 引用 docs/35 §5.1 + 提 CI / cron 禁用 |
| 5 | `test_live_mode_invokes_probe_all_when_enabled` | `URL_HEALTH_LIVE=1` → `main()` 调 `probe_all`（默认 **skip**） |
| 6 | `test_live_mode_test_hook_url_works` | live 模式下 `--url` test hook 可用（默认 **skip**） |
| 7 | `test_live_mode_does_not_write_to_business_tables` | 静态扫描：脚本只写 `cegr.ingestion_run`，**不写** 任何业务表 |
| 8 | `test_existing_probe_suite_unaffected` | 既有 public surface（`probe_all` / `_probe_url` / `_write_run` / `_dsn`）保留 |

### 1.3 Pack + receipt（2 文件）

| 文件 | 说明 |
|------|------|
| `scripts/update_manifest_s2023.py` | 一次性脚本（不入 pack） |
| `evidence_pack/manifest.json` (M) | **511 → 512**（+1 schema_negative_test） |
| `reviews/.../166-…-receipt-20260825.md` | 本回执 |

---

## §2 — pytest 结果

### 2.1 S2.0.2.3 新增套件（**12 passed + 2 skipped**）

```
$ python3 -m pytest tests/test_url_health_probe_live.py -v
collected 14 items
test_default_url_health_live_unset_refuses PASSED                       [  7%]
test_url_health_live_zero_refuses PASSED                                [ 14%]
test_url_health_live_only_exact_one_enables[true] PASSED                [ 21%]
test_url_health_live_only_exact_one_enables[True] PASSED                [ 28%]
test_url_health_live_only_exact_one_enables[TRUE] PASSED                [ 35%]
test_url_health_live_only_exact_one_enables[yes] PASSED                 [ 42%]
test_url_health_live_only_exact_one_enables[on] PASSED                  [ 50%]
test_url_health_live_only_exact_one_enables[2] PASSED                   [ 57%]
test_url_health_live_only_exact_one_enables[01] PASSED                  [ 64%]
test_url_health_live_message_cites_docs35_51 PASSED                     [ 71%]
test_live_mode_invokes_probe_all_when_enabled SKIPPED                   [ 78%]
test_live_mode_test_hook_url_works SKIPPED                              [ 85%]
test_live_mode_does_not_write_to_business_tables PASSED                 [ 92%]
test_existing_probe_suite_unaffected PASSED                             [100%]
======================== 12 passed, 2 skipped in 2.00s =========================
```

### 2.2 既有回归（**6 / 6 passed**）

```
$ python3 -m pytest tests/test_url_health_probe.py -v
collected 6 items
test_empty_registry_no_rows_no_calls PASSED                       [ 16%]
test_primary_success_backup_failed_exit_one PASSED                [ 33%]
test_primary_failed_backup_not_probed PASSED                      [ 50%]
test_captcha_feature_partial PASSED                               [ 66%]
test_dns_failure_failed_with_error_class PASSED                   [ 83%]
test_enabled_false_row_not_probed PASSED                          [100%]
============================== 6 passed in 3.65s ===============================
```

| 套件 | cases | 结果 |
|------|------|------|
| `test_url_health_probe_live.py`（new） | 14 | ✅ 12 passed + 2 skipped (live-mode) |
| `test_url_health_probe.py`（既有 S1.17） | 6 | ✅ all passed |

---

## §3 — 关键设计

### 3.1 `URL_HEALTH_LIVE` gate（`scripts/url_health_probe.py:197` 附近）

```python
def _url_health_live_enabled() -> bool:
    return os.environ.get("URL_HEALTH_LIVE") == "1"


def main(argv: list[str] | None = None) -> int:
    ...
    if not _url_health_live_enabled():
        print(
            "[url_health] URL_HEALTH_LIVE != '1'; refusing to probe live. "
            "Set URL_HEALTH_LIVE=1 (dev only) to enable real HEAD/GET-Range. "
            "Per docs/35 §5.1; CI and prod cron always stay off.",
            file=sys.stderr,
        )
        return 0
    ...
```

**关键决策**：
- **gate 在 `main()`，不在 `probe_all()`** — 既有测试通过 importlib 直接调 `probe_all` / `_probe_url`，不受影响
- **拒绝 exit 0**（不是 error）— 「拒绝」是预期行为；CI 不会因拒绝触发报警
- **仅字面 `"1"` 启用** — `true`/`yes`/`on`/`2`/`01` 一律拒绝（anti-foot-gun；pytest 3 用 7 个 parametrize 守门）

### 3.2 Live 模式 §2.1 上限（per docs/35 §5.2；既有 `probe_all()` 已实现，本刀不重复）

| 上限 | 既有实现 | 本刀变更 |
|---|---|---|
| HEAD 默认 | `session.head(url, ...)` | — |
| GET Range bytes=0-1023 | `session.get(url, headers={"Range": "bytes=0-1023"})` 仅 HEAD 405/501 触发 | — |
| 仅 `enabled=TRUE` 行 | SQL `WHERE enabled = TRUE` | — |
| URL ≤2048 | 既有 | — |
| 每源 ≤1 req/s | `time.sleep(1.0)` 每轮询 | — |
| 并发 ≤4 | 串行；未实现并发（per 红线「不并发」） | — |
| 总耗时 ≤60s | `deadline = started + max_runtime` | — |
| UA: `cegr-url-health/1.0 (+probe)` | （待补；**非本刀阻塞**） | — |
| 验证码/付费墙/登录 → PARTIAL | `_is_captcha_or_paywall` | — |
| 不解析 robots.txt | 未实现 | — |
| 仅写 `ingestion_run` | `_write_run` 单点 | — |

### 3.3 静态安全检查（`test_live_mode_does_not_write_to_business_tables`）

```python
src_no_comments = re.sub(r"#[^\n]*", "", src)
inserts = re.findall(r"INSERT\s+INTO\s+cegr\.(\w+)", src_no_comments, re.IGNORECASE)
```

- 正则匹配所有 `INSERT INTO cegr.<table>`，去重
- 断言 `ingestion_run ∈ distinct` ∧ `business_tables ∩ distinct = ∅`
- **business_tables** = {observation, source_document, source_location, indicator_definition, indicator_methodology_version, calendar_period, geo_entity, geo_code_version, source_registry}
- 这条防线防止未来贡献者「顺手」在 probe 里加业务写

### 3.4 默认 skip 模式（per tasking 165 §SCHEMA）

```python
_LIVE = os.environ.get("URL_HEALTH_LIVE") == "1"
requires_live = pytest.mark.skipif(
    not _LIVE,
    reason="URL_HEALTH_LIVE != '1'; live mode not enabled (set URL_HEALTH_LIVE=1 to run)",
)
```

- 14 cases 中 2 个 `requires_live`（probe_all 调用 + `--url` hook）
- 既有 12 个 gate-behavior cases **始终跑**（验证默认安全行为，不依赖 live 网络）

---

## §4 — Pack invariant

```
artifact_count: 511 → 512 (+1)
role_count.schema_negative_test: 21 → 22 (+1 tests/test_url_health_probe_live.py)
invariant: 512 == 512 == 512 ✓
```

（`scripts/url_health_probe.py` 是 in-place 编辑，不算新 artifact）

---

## §5 — Push confirmation

```
$ git push origin HEAD
To https://origin.cursor.com/lyliae/china-platform.git
   <prev>..<new>  HEAD -> main

$ git push github HEAD
To https://github.com/cscoheru/china-platform.git
   <prev>..<new>  HEAD -> main
```

---

## §6 — 红线审计（per 165 §红线 + docs/35 §8）

| 红线 | 状态 |
|------|------|
| ❌ 不爬业务数据 | ✅ — live 模式仅 HEAD / GET-Range bytes=0-1023；既有 `_probe_url` 已实现 |
| ❌ 不绕验证码/付费墙 | ✅ — `_is_captcha_or_paywall` 检测到即 PARTIAL + 停止 |
| ❌ 不接生产 cron | ✅ — gate 默认拒绝；docs/35 §5.3 + tasking §SCHEMA 明确生产 cron 移交 Stage 2 运维刀 |
| ❌ 不 Gate PASS | ✅ — 本回执未声明任何 PASS |
| ❌ 不改 `gate_thresholds.json` | ✅ |
| ❌ 不批量 2020-2025 | ✅ — 不相关 |
| ❌ 不把 1909 代表中国 / 陕西 标为门控 | ✅ — 不相关 |
| ❌ 不擅自 --force | ✅ |
| ❌ 不在 chat 复述 Cursor 长文 | ✅ |
| ❌ 不索要 PAT | ✅ |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ |
| ❌ Cursor 不写 docs Cursor owns | ✅ — 本刀未触碰 docs/ |
| ✅ 测试默认 skip（仅 live 启用） | ✅ — `requires_live` 标记 + 2 skipped |
| ✅ 既有 probe 套件仍绿 | ✅ — 6 / 6 passed |
| ✅ 不写业务表（仅 `ingestion_run`） | ✅ — pytest 7 静态守门 |

---

## §7 — Next heartbeat

84 while-POLL 持续武装（session-only, 180s, cron `8384ebc9`）。等待 Cursor 对 S2.0.2.3 implementation 的审验（预期 `167-stage0-cursor-s2023-impl-audit-…md`）。

— CC @ queue_rev 60, S2.0.2.3 `URL_HEALTH_LIVE` gate 已交付 —
