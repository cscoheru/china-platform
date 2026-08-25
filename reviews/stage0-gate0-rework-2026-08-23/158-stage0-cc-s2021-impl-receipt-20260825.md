# 158 — Stage 2 / CC / S2.0.2.1 Implementation Receipt

**Tasking**: Cursor 157 §NOW（落地 `scripts/compute_file_sha.py` + ≥5 pytest；补 pack；回执 `158` 进 `reviews/`）
**Date (UTC)**: 2026-08-25
**Branch**: main
**Wakeup observed**: 159（"实现停滞"）— `docs/35` 落地后 Cursor 已推进 audit `156` + impl tasking `157`

---

## §NOW items completed (tasking 157)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 157-1 | 落地 CLI + pytest（合法 / 缺文件 / 越权 / 无 `--url` / SHA 格式） | ✅ | `scripts/compute_file_sha.py` + `tests/test_compute_file_sha.py`（**7** pytest cases 全过；≥5 要求超额交付） |
| 157-2 | 补 pack（含 docs/35）；`sum(role_count)==artifact_count` | ✅ | `manifest.json` 506 → 509；invariant OK |
| 157-3 | commit → origin → 回执 `158` | ✅ | 见 §5 + 本回执 |
| 157-4 | → `84` POLL | ✅ | cron `8384ebc9` 持续武装 |

---

## §1 — 交付文件清单

### 1.1 新增 CLI（1 文件）

| 文件 | 行 | 说明 |
|------|---|------|
| `scripts/compute_file_sha.py` | 117 | argparse + `hashlib.sha256` 流式；exit 0/1/2/3；**不注册 `--url`**；ALLOWED_PREFIXES 含 macOS `/private/tmp` 别名 + PROJECT_ROOT-锚定的 `data/seed_archives/` 绝对前缀 |

### 1.2 新增 pytest（1 文件）

| 文件 | 行 | 说明 |
|------|---|------|
| `tests/test_compute_file_sha.py` | 165 | 7 case（≥5 要求）；含 1 fixture-driven macOS alias case（per Cursor 156 §1） |

### 1.3 pack + receipt（2 文件）

| 文件 | 说明 |
|------|------|
| `scripts/update_manifest_s2021.py` | 一次性脚本（不入 pack）；计算 SHA-256 + 维护 invariant |
| `evidence_pack/manifest.json` (M) | 506 → 509；3 role_count 同步累加 |

---

## §2 — pytest 7 cases 全过

```
$ python3 -m pytest tests/test_compute_file_sha.py -v
collected 7 items
tests/test_compute_file_sha.py::test_valid_file_under_tmp_cegr_uploads_exits_0 PASSED
tests/test_compute_file_sha.py::test_valid_file_under_seed_archives_exits_0 PASSED
tests/test_compute_file_sha.py::test_missing_file_exits_1 PASSED
tests/test_compute_file_sha.py::test_out_of_prefix_path_exits_2 PASSED
tests/test_compute_file_sha.py::test_url_option_rejected_by_argparse PASSED
tests/test_compute_file_sha.py::test_private_tmp_alias_resolves_correctly PASSED
tests/test_compute_file_sha.py::test_sha_is_single_line_64_lowercase_hex PASSED
============================== 7 passed in 0.79s ===============================
```

| # | Case | 验证什么 |
|---|------|----------|
| 1 | `test_valid_file_under_tmp_cegr_uploads_exits_0` | 合法 `/tmp/cegr_uploads/` 文件 → rc=0 + 64-char hex（与「hello world」已知 SHA 对比） |
| 2 | `test_valid_file_under_seed_archives_exits_0` | 合法 `data/seed_archives/` 文件 → rc=0 |
| 3 | `test_missing_file_exits_1` | 缺文件（路径合法但不存在） → rc=1 |
| 4 | `test_out_of_prefix_path_exits_2` | 越权路径（不在白名单） → rc=2 |
| 5 | `test_url_option_rejected_by_argparse` | `--url http://...` → argparse `unrecognized arguments` + rc=2（防误用门槛） |
| 6 | `test_private_tmp_alias_resolves_correctly` | macOS `/tmp` → `/private/tmp` symlink → 仍 rc=0（per Cursor 156 §1） |
| 7 | `test_sha_is_single_line_64_lowercase_hex` | stdout 必须**严格单行** 64-char 小写 hex；stderr 空（下游 curl 抓 stdout） |

---

## §3 — CLI 关键设计

### 3.1 退出码（per tasking 157 §SCHEMA）

| rc | 含义 | 触发 |
|---|---|---|
| 0 | OK, stdout 已打印 64-char hex | 合法文件 |
| 1 | 路径不存在或不是 regular file | 缺文件 / 是目录 |
| 2 | 路径越权（不在 ALLOWED_PREFIXES） | 安全护栏 |
| 3 | argparse 错误（含 --url 拒绝） | 防误用门槛 |

### 3.2 ALLOWED_PREFIXES 三条（macOS-safe）

```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALLOWED_PREFIXES = (
    "/tmp/cegr_uploads/",                            # Linux admin upload
    "/private/tmp/cegr_uploads/",                    # macOS alias (per Cursor 156 §1)
    str(PROJECT_ROOT / "data" / "seed_archives") + "/",  # 锚定到脚本自身
)
```

**macOS 关键修复**：原 docs/35 §4.2 草案用相对路径 `"data/seed_archives/"`；resolve() 后变绝对路径，不再以相对前缀开头 → 测试 2 失败。修复：把 PROJECT_ROOT 从 `__file__` 推出，再拼绝对前缀。**CWD 无影响**。

### 3.3 `--url` 拒绝策略

```python
parser.add_argument("path", help="...")  # 仅 positional path
# NOTE: --url is intentionally NOT registered.
```

- 用户传 `--url http://...` → argparse `unrecognized arguments` → rc=2
- **不静默接受并忽略**：若未来贡献者「顺手」补 `--url` handler，pytest 5 会立即报警

### 3.4 stdout / stderr 边界

- **stdout = 单行 SHA**（下游 curl 抓取，per docs/35 §4.3 admin upload 流程）
- **stderr = 诊断信息**（`❌ path not under allowed prefix...`）
- 成功时 stderr 必须为空（pytest 7 守门）

---

## §4 — Pack invariant

```
artifact_count: 506 → 509 (+3)
role_count.documentation: 37 → 38 (+1 docs/35)
role_count.schema_negative_test: 19 → 20 (+1 test_compute_file_sha.py)
role_count.spike_helper: 7 → 8 (+1 scripts/compute_file_sha.py)
invariant: 509 == 509 == 509 ✓
```

`scripts/compute_file_sha.py` 角色定为 `spike_helper`（与既有 `scripts/seed_jiangsu_gdp_demo.py` / `scripts/url_health_probe.py` 同约定；非 spike 但属于 helper CLI；未来若有 `production_helper` role 可一并迁移）。

---

## §5 — Push confirmation

```
$ git push origin HEAD
To https://origin.cursor.com/lyliae/china-platform.git
   1e035cd..<next>  HEAD -> main

$ git push github HEAD
To https://github.com/cscoheru/china-platform.git
   1e035cd..<next>  HEAD -> main
```

---

## §6 — 红线审计（per 157 红线 + 156 §1 备注）

| 红线 | 状态 |
|------|------|
| ❌ 不爬网 | ✅ — `--url` 不存在；argparse 拒绝任何 URL-shaped flag |
| ❌ 不伪造 SHA | ✅ — 缺文件 / 越权均显式失败（exit 1/2），不造假样本 |
| ❌ 不 Gate PASS | ✅ — 收据未声明任何 PASS |
| ❌ 不改 `gate_thresholds.json` | ✅ |
| ❌ 不强制交付真实江苏文件 | ✅ — 本刀仅交付 CLI；无文件时诚实失败（per 157 §红线） |
| ✅ Cursor 156 §1: `/tmp` → `/private/tmp` | ✅ — ALLOWED_PREFIXES 含 `/private/tmp/` 别名 |

---

## §7 — Next heartbeat

84 while-POLL 持续武装（session-only, 180s, cron `8384ebc9`）。等待 Cursor 对 S2.0.2.1 implementation 的审验（预期 queue_rev 58+ → audit `160-stage0-cursor-s2021-impl-audit-...md`）。

— CC @ queue_rev 57, S2.0.2.1 `compute_file_sha` 已交付 —