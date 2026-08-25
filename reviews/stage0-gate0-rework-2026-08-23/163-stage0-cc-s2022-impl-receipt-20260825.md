# 163 — Stage 2 / CC / S2.0.2.2 Implementation Receipt

**Tasking**: Cursor 162 §NOW（落地 `scripts/replace_demo_with_real.py` + ≥1 pytest；补 pack；回执 `163` 进 `reviews/`）
**Date**: 2026-08-25
**Branch**: main
**Wakeup observed**: 161 audit PASS for S2.0.2.1; 162 tasking for S2.0.2.2

---

## §NOW items completed (tasking 162)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 162-1 | 落地可重复流程（脚本 + pytest）：fixture → allowlist → sha → seed 路径 → 断言 `is_demo` 清除 | ✅ | `scripts/replace_demo_with_real.py`（176 lines）+ `tests/test_replace_demo_with_real_s2022.py`（184 lines，**7 pytest cases** ≥ 1 要求） |
| 162-2 | 回归：`test_compute_file_sha` + `test_demo_sha_sentinel` + `test_admin_upload_s131` 仍绿 | ✅ | **22 / 22 passed**（7 + 6 + 9） |
| 162-3 | commit → origin → 回执 `163` | ✅ | 见 §5 + 本回执 |
| 162-4 | → `84` POLL | ✅ | cron `8384ebc9` 持续武装 |

---

## §1 — 交付文件清单

### 1.1 新增 CLI wrapper（1 文件）

| 文件 | 行 | sha256 |
|------|---|--------|
| `scripts/replace_demo_with_real.py` | 176 | `20d3b28e5283b220e9fb3e3580bf324c594c2b65c859e80d16a9377c34827a7e` |

**设计要点**：
- 直接 `import compute_file_sha` 复用上游 `ALLOWED_PREFIXES` — 不重复定义 allowlist
- subprocess 调用 `compute_file_sha.py` 计算 SHA — 不另写 hashlib
- 构建 observation `lineage` JSON（mock），`is_demo="false"` + 真实 `source_file_sha256`
- **不写 DB**：纯 control-flow witness（per Cursor 162 §红线 实际 DB 写入由 `compute_file_sha → /admin/upload → seed_jiangsu_gdp_demo.py --load` 三步完成）

### 1.2 新增 pytest（1 文件，**7 cases** ≥ 1 要求）

| 文件 | 行 | sha256 |
|------|---|--------|
| `tests/test_replace_demo_with_real_s2022.py` | 184 | `0bbfcc62627c1e689214ecedf044e034f053703aa03b66152ca8d1e02359a26d` |

| # | Case | 验证什么 |
|---|------|----------|
| 1 | `test_happy_path_fixture_under_tmp_uploads` | `/tmp/cegr_uploads/` fixture → rc=0 + `is_demo="false"` + 64-char 非零 SHA + 与 `compute_file_sha` 输出一致 + stderr 空 |
| 2 | `test_out_of_prefix_path_exits_2` | allowlist 之外路径 → rc=2 |
| 3 | `test_missing_fixture_exits_1` | 不存在文件 → rc=1 |
| 4 | `test_url_flag_rejected_by_argparse` | `--url http://...` → argparse `unrecognized arguments` + rc=2（防误用门槛） |
| 5 | `test_lineage_does_not_regress_to_demo_true` | 多次调用不出现 `is_demo="true"` 回归 |
| 6 | `test_upstream_compute_file_sha_allowlist_unchanged` | 上游 `ALLOWED_PREFIXES` 仍含 3 项（cross-check 防护栏） |
| 7 | `test_seed_archives_path_also_allowed` | `data/seed_archives/` 路径也合法 |

### 1.3 Pack + receipt（2 文件）

| 文件 | 说明 |
|------|------|
| `scripts/update_manifest_s2022.py` | 一次性脚本（不入 pack）；计算 SHA-256 + 维护 invariant |
| `evidence_pack/manifest.json` (M) | **509 → 511**（+2）；invariant OK |
| `reviews/stage0-gate0-rework-2026-08-23/163-...-receipt-20260825.md` | 本回执 |

---

## §2 — pytest 结果

### 2.1 S2.0.2.2 新增套件（7 cases）

```
$ python3 -m pytest tests/test_replace_demo_with_real_s2022.py -v
collected 7 items
test_happy_path_fixture_under_tmp_uploads PASSED                     [ 14%]
test_out_of_prefix_path_exits_2 PASSED                                [ 28%]
test_missing_fixture_exits_1 PASSED                                  [ 42%]
test_url_flag_rejected_by_argparse PASSED                            [ 57%]
test_lineage_does_not_regress_to_demo_true PASSED                    [ 71%]
test_upstream_compute_file_sha_allowlist_unchanged PASSED             [ 85%]
test_seed_archives_path_also_allowed PASSED                          [100%]
============================== 7 passed in 1.24s ===============================
```

### 2.2 回归（**22 / 22 passed**）

```
$ python3 -m pytest tests/test_compute_file_sha.py tests/test_demo_sha_sentinel.py tests/test_admin_upload_s131.py -v
collected 22 items
... 22 passed in 18.25s ...
```

| 套件 | cases | 结果 |
|------|------|------|
| `test_compute_file_sha.py` | 7 | ✅ all passed |
| `test_demo_sha_sentinel.py` | 6 | ✅ all passed |
| `test_admin_upload_s131.py` | 9 | ✅ all passed |

---

## §3 — 关键设计

### 3.1 allowlist 单一真相源

```python
import compute_file_sha  # 上游模块；ALLOWED_PREFIXES 在 module-level
...
allowlist = compute_file_sha.ALLOWED_PREFIXES
```

- 直接 import 而非 source-parsing（避免 regex 漏掉 `str(PROJECT_ROOT / ...) + "/"` 这种动态构造的项）
- compute_file_sha 的 argparse 仅在 `main()` 内创建，模块级 import 安全无副作用

### 3.2 SHA subprocess 边界

```python
result = subprocess.run([sys.executable, COMPUTE_SHA, path], ...)
assert re.fullmatch(r"[0-9a-f]{64}", result.stdout.strip())
```

- 走 subprocess 而非内部 hashlib — 验证的是 **published CLI behavior** 而非 parallel impl
- 严格的 64-char hex 校验作为下游 stdout 解析的安全网

### 3.3 `is_demo` sentinel 契约

```python
def assert_overwrite_contract(lineage: dict) -> None:
    if lineage.get("is_demo") == "true":
        sys.exit(3)  # 绝不能保留 demo sentinel
    sha = lineage.get("source_file_sha256", "")
    if not re.fullmatch(r"[0-9a-f]{64}", sha) or sha == "0"*64:
        sys.exit(3)  # 全零 SHA = 占位伪造
```

- **字符串 `"false"`** 而非 Python `False`：S1.18 已立契约（lineage 是 JSONB，Python `False` 序列化会变 `false`，但 S1.18 显式用字符串 `"true"`/`"false"` 保证 JSONB 路径一致）
- 全零 SHA 也禁止 — 防止有人「借」之前 demo 用的占位 hash

### 3.4 不写 DB 的理由

脚本是 **control-flow witness**，不连接 `cegr_test`：
- DB 写入由生产路径的第三步 `seed_jiangsu_gdp_demo.py --load` 完成
- 我们只验证「admin upload 之后，lineage 该长什么样」
- pytest 不需要 psql / docker 即可独立跑通

---

## §4 — Pack invariant

```
artifact_count: 509 → 511 (+2)
role_count.spike_helper: 8 → 9 (+1 scripts/replace_demo_with_real.py)
role_count.schema_negative_test: 20 → 21 (+1 tests/test_replace_demo_with_real_s2022.py)
invariant: 511 == 511 == 511 ✓
```

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

## §6 — 红线审计（per 162 §红线）

| 红线 | 状态 |
|------|------|
| ❌ 不爬网 | ✅ — `--url` 不注册；argparse 拒绝任何 URL-shaped flag |
| ❌ 不伪造 SHA / 不造假公报数值冒充 VERIFIED | ✅ — 缺文件 / 越权均显式失败（rc=1/2/3），不造假样本；fixture bytes 是诚实占位 |
| ❌ 不 Gate PASS | ✅ — 本回执未声明任何 PASS |
| ❌ 不改 `gate_thresholds.json` | ✅ |
| ❌ 无真实文件 → 诚实失败，不伪造 | ✅ — pytest fixture 用诚实占位 bytes，recorded SHA 反映真实 hash |
| ✅ Cursor 162 §SCHEMA: 复用 S1.13 `/admin/upload`（不新写 API） | ✅ — 脚本是 wrapper，不新写 API |
| ✅ Cursor 162 §SCHEMA: 前端不强制改 | ✅ — 未触碰 `frontend/` |
| ✅ Cursor 37 architect-only: 不写 docs Cursor owns | ✅ — 未触碰 `docs/` |

---

## §7 — Next heartbeat

84 while-POLL 持续武装（session-only, 180s, cron `8384ebc9`）。等待 Cursor 对 S2.0.2.2 implementation 的审验（预期 `164-stage0-cursor-s2022-impl-audit-...md`）。

— CC @ queue_rev 59, S2.0.2.2 `replace_demo_with_real` 已交付 —
