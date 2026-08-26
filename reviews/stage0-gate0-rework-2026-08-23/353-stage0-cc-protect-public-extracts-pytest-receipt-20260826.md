# 353 — 禁止 pytest 覆写 public_extracts · CC 回执

- 编号：`353-stage0-cc-protect-public-extracts-pytest-receipt-20260826`
- 任务书：`352-stage2-protect-public-extracts-from-pytest-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`c33d3f4`
- 日期：2026-08-26

---

## §NOW 对照

| 352 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) connector CLI 增 `--extract-root=DIR` / `--archive-root=DIR`（默认仍仓库路径） | ✅ `main()` argparse 两 flag，解析后立即写入 `CEGR_ARCHIVE_ROOT`/`CEGR_EXTRACT_ROOT` env（早于任何写路径）；默认值不变 | `scripts/auto_ingest_public_source.py` |
| (2) **所有** pytest（含 subprocess）传临时 root 或设 env | ✅ `tmp_archive_root` fixture 升级为 `autouse=True`：`monkeypatch.setenv(CEGR_ARCHIVE_ROOT/CEGR_EXTRACT_ROOT → tmp)`。subprocess 子进程继承父 env → 一并覆盖；in-process 调 `get_*_root()` 同样命中 env | `tests/test_auto_ingest_public_source_s52.py` |
| (3) 回归测：跑相关 case 后 NBS extract `source_sha256`/`row_count` 不变 | ✅ `test_regression_real_extracts_not_clobbered_by_pytest`：快照真实 `NATIONAL_BULLETIN.json` bytes → subprocess 双 pilot `--from-local-sample`（显式 `--archive-root`/`--extract-root` tmp，走新 flag 路径）→ 断言真实文件 bytes 不变 + tmp 落盘 | 同上 |
| (4) 回执文件名匹配 `N-stage0-cc-…-receipt-…md` | ✅ 本文件名 `353-stage0-cc-protect-public-extracts-pytest-receipt-20260826.md` | — |
| (5) 回执编号 353 | ✅ | — |

## 根因与修法（两路覆写向量）

**向量 A（in-process，默认参数 import 期绑定）**：`write_extract_json(output_root: Path = PUBLIC_EXTRACTS_ROOT)` 的默认值在 import 时求值，`monkeypatch.setattr(aips, "PUBLIC_EXTRACTS_ROOT", …)` 改不动它 → `test_local_sample_emits_registry_sample_intaked`（example.test.cn）与 fake stats.gov.cn case 直接写真实 extracts（NBS 63→1 的来源）。

**向量 B（subprocess，patch 不跨进程）**：`test_local_sample_flag_routes_in_main` / `test_local_sample_main_returns_0_for_sz` spawn 新解释器，只继承 `os.environ`，不继承 module-attr patch → sz.gov.cn 真实 extract 被重写（`7f04237`/`95a8569` 两度恢复的就是这条）。

**修法（CALL-time 解析，env 优先）**：

```python
def get_extracts_root() -> Path:
    env = os.environ.get("CEGR_EXTRACT_ROOT")
    if env:
        return Path(env)
    return PUBLIC_EXTRACTS_ROOT   # module default, in-process 可 monkeypatch
```

`archive()` / `write_extract_json()` / `write_sha_drift_report()` 全部改走 resolver（`write_extract_json` 签名同时改为 `output_root: Path | None = None`，消灭 import 期绑定）。CLI flag 在 `main()` 里 funnel 进同一 env → 一条机制覆盖 in-process patch、env 继承、CLI 显式三场景。

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `scripts/auto_ingest_public_source.py` | MODIFIED（resolver ×2 + 三函数改道 + argparse ×2） | 已入 manifest（SKIP） |
| `tests/test_auto_ingest_public_source_s52.py` | MODIFIED（autouse setenv fixture + sz 路径测试改 setenv）+ **新增 3 case** | 已入 manifest（SKIP） |
| `scripts/_knife53_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../353-stage0-cc-protect-public-extracts-pytest-receipt-20260826.md` | NEW（本文件） | `documentation` |

新增测试 3 case：

1. `test_regression_real_extracts_not_clobbered_by_pytest` — §SCHEMA (3) 的正主回归：subprocess 双 pilot + 显式新 flag → 真实 NBS bytes 不变 + tmp 落盘 2 extract + tmp NBS row_count=63。
2. `test_root_override_env_directs_in_process_intake` — 向量 A 的回归：纯 env（无 flag）重定向 in-process intake，且 `data/public_extracts/example.test.cn/` 不落盘。
3. `test_root_override_cli_flags_equal_env` — §SCHEMA (1) 的 CLI 可用性：dry-run 带 flag rc=0。

## 测试证据

```
$ python3 -m pytest tests/test_auto_ingest_public_source_s52.py \
    tests/test_public_extract_frontend_fixture.py -q
79 passed in 2.00s          # 旧 76 + 新 3

$ git status --porcelain data/
（空）                        # 跑完测试后 data/ 零变动 ← 352 核心契约

$ python3 frontend/smoke-check.py
=== ... smoke: PASS ===      # 含 §12 public-extracts gate
```

（全量 `pytest tests/` 不跑：DB-backed 用例等待未启动的 Postgres 会挂起，本刀回归范围 = connector + fixture 两文件，与既往各刀证据范围一致。）

## data/ 污染清理（本刀顺手，untracked）

跑测期间确认了 5 处历史污染（全部 untracked、逐一验明为 fake 测试产物后删除）：

- `data/public_extracts/example.test.cn/`（extract 的 `source_sample_path` 指向 pytest tmp；`source_archive_path` 也指向 tmp —— 恰好是向量 A「archive 被重定向而 extract 泄漏」的化石证据）
- `data/public_extracts/tjj.hubei.gov.cn/`（同上）
- `data/public_archives/2026-08/stats.gov.cn/n.html`（SHA-mismatch 用例的 tampered 单元格表）
- `data/public_archives/2026-08/stats.gov.cn/zxfb`（fake 归档 bytes，文件名取自 URL 尾段）
- `data/public_archives/2026-08/tjj.hubei.gov.cn/tjyb`（同上）

清理时误删了同目录 tracked 的 `data/public_archives/2026-08/stats.gov.cn/sample.html`（真实 WORM 归档），已 `git checkout --` 恢复（388,238 bytes，`git status data/` 干净）。

## Pack 不变量

`_knife53_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **663 → 665**；`sum(role_count) == artifact_count == len(artifacts) == 665`（role_count 从 artifacts 重算，knife 16 法）。

## 红线自查

- ❌ 未宣布 Gate 1/2 / O1 PASS
- ❌ 未覆写已提交 extracts（`git status data/` 干净为证）
- ✅ 回执文件名含 `-cc-`
- ❌ 未改前端呈现 / 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 未在 chat 复述 Cursor 长文

## 下一步

`./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 354）。
