# Knife 47 回执 — live 探测 + SHA 漂移候选（tasking 333）

- 编号：`334-stage0-cc-live-probe-sha-drift-receipt-20260826`
- 前置：`331` connector 已落（pack 645 → 648）;`333` tasking §SCHEMA 裁定 D
- 落地:`drift 候选路径` + `一次 NBS zxfb --live 探测` + `5 pytest` + `pack 648 → 651`
- 回执 §NOW:`drift ≠ 收口;WORM 归档实测字节;不自动改 registry;等用户裁定`

## §META

| 字段 | 值 |
|---|---|
| knife | 47 |
| tasking | 333 |
| phase | CC_ACTION_REQUIRED |
| queue_rev | 139 |
| cc_receipt | 334 |
| cc_head（预）| 待 commit + push origin + push github 落地 |
| user_ruling | D（drift 路径 + 一次 live 探测 + 5 pytest + 不自动改 registry）|
| 测试 | 31/31 pytest PASS（knife 46 是 26/26,新增 5 case）|
| live 探测 | rc=4（drift handled, NOT O1 收口）;见 §5 |
| pack | 648 → 650（+2:bump + receipt;connector 是 knife 46 的修订,bump SKIP）|

## §NOW — tasking 333 §SCHEMA 落点

| 决策点 | 落地 |
|---|---|
| (1) 扩展 connector:drift → `CANDIDATE_AUTO` + `is_demo=true` + WORM 归档实测字节 + 写 drift 报告（5 字段）| `scripts/auto_ingest_public_source.py` 加 `ShaDrift` 异常 + `write_sha_drift_report(...)` + `main()` live 分支按 SHA 是否匹配分流（matched→O1_AUTO_INTAKED / drift→CANDIDATE_AUTO + rc=4）。`assert_sha_matches_registry` 自身保持抛 RuntimeError（contract 仍响亮）；只有 `main()` 捕 |
| (2) SHA 匹配才 `O1_AUTO_INTAKED` + `is_demo=false` | `main()` live 路径显式判 `sha_matched`；只有 `True` 才走 `O1_AUTO_INTAKED` 写入 |
| (3) 一次 NBS zxfb `--live --confirm-live=…` 探测 | 探测执行;rc=4;AUTH 无阻断;落入 drift 路径。详见 §5 |
| (4) ≥4 pytest（drift 路径 / 仍拒 AUTH bypass）| 5 case 落地（`test_sha_drift_report_writes_5_fields` / `test_sha_drift_intake_status_is_candidate_auto` / `test_sha_drift_does_not_auto_update_registry` / `test_sha_drift_archive_still_written` / `test_sha_drift_red_line_no_registry_write`）;`test_sha_mismatch_raises` 保留（assert_sha_matches_registry 仍抛）|
| (5) 回执 `334` | 本文件 |

## §1 修改清单

| 文件 | 行数 / 字节 | 角色 |
|---|---|---|
| `scripts/auto_ingest_public_source.py` | 562 → ~620（+ShaDrift class + write_sha_drift_report + main drift 分支 + exit-code 4 注释更新 + write_observation docstring 增 CANDIDATE_AUTO）| spike_helper |
| `tests/test_auto_ingest_public_source_s52.py` | 388 → ~520（+5 drift case;含"不自动改 registry" + WORM 仍写 + CANDIDATE_AUTO + 5 字段报告 + 无 DictWriter）| schema_negative_test（行内归类）|
| `scripts/_knife47_manifest_bump.py` | NEW ~115 | spike_helper |
| `reviews/stage0-gate0-rework-2026-08-23/334-stage0-cc-live-probe-sha-drift-receipt-20260826.md` | NEW（本文件）| documentation |

## §2 pytest 结果

```
tests/test_auto_ingest_public_source_s52.py::test_registry_csv_exists PASSED
tests/test_auto_ingest_public_source_s52.py::test_registry_load_returns_six_rows PASSED
tests/test_auto_ingest_public_source_s52.py::test_registry_has_required_columns PASSED
tests/test_auto_ingest_public_source_s52.py::test_pilot_filter_matches_only_nbs_zxfb PASSED
tests/test_auto_ingest_public_source_s52.py::test_pilot_filter_when_default_pilot_excludes_hubei_and_shenzhen PASSED
tests/test_auto_ingest_public_source_s52.py::test_filter_function_accepts_other_pilot PASSED
tests/test_auto_ingest_public_source_s52.py::test_pilot_filter_rejects_disabled_rows PASSED
tests/test_auto_ingest_public_source_s52.py::test_pilot_filter_rejects_auth_required_rows PASSED
tests/test_auto_ingest_public_source_s52.py::test_sha256_of_bytes_is_lowercase_hex PASSED
tests/test_auto_ingest_public_source_s52.py::test_sha_matches_registry_passes PASSED
tests/test_auto_ingest_public_source_s52.py::test_sha_mismatch_raises PASSED
tests/test_auto_ingest_public_source_s52.py::test_sha_drift_report_writes_5_fields PASSED
tests/test_auto_ingest_public_source_s52.py::test_sha_drift_intake_status_is_candidate_auto PASSED
tests/test_auto_ingest_public_source_s52.py::test_sha_drift_does_not_auto_update_registry PASSED
tests/test_auto_ingest_public_source_s52.py::test_sha_drift_archive_still_written PASSED
tests/test_auto_ingest_public_source_s52.py::test_sha_drift_red_line_no_registry_write PASSED
tests/test_auto_ingest_public_source_s52.py::test_auth_blocked_statuses_includes_401_403_429 PASSED
tests/test_auto_ingest_public_source_s52.py::test_auth_blocked_exception_carries_5_required_fields PASSED
tests/test_auto_ingest_public_source_s52.py::test_auth_blocked_report_writes_5_fields PASSED
tests/test_auto_ingest_public_source_s52.py::test_login_redirect_detection_in_download PASSED
tests/test_auto_ingest_public_source_s52.py::test_script_does_not_import_headless_browser PASSED
tests/test_auto_ingest_public_source_s52.py::test_script_does_not_register_url_flag PASSED
tests/test_auto_ingest_public_source_s52.py::test_script_does_not_register_login_flag PASSED
tests/test_auto_ingest_public_source_s52.py::test_live_mode_requires_confirm_live PASSED
tests/test_auto_ingest_public_source_s52.py::test_dry_run_default_succeeds_without_network PASSED
tests/test_auto_ingest_public_source_s52.py::test_worm_archive_path_format PASSED
tests/test_auto_ingest_public_source_s52.py::test_lineage_contract_fields_present PASSED
tests/test_auto_ingest_public_source_s52.py::test_no_unregistered_source_in_pilot PASSED
tests/test_auto_ingest_public_source_s52.py::test_write_observation_jsonl_contract PASSED
tests/test_auto_ingest_public_source_s52.py::test_demo_intake_status_keeps_is_demo_true PASSED
tests/test_auto_ingest_public_source_s52.py::test_script_importable_and_has_main PASSED

============================== 31 passed in 0.86s ==============================
```

注：knife 46 是 26 case;knife 47 +5（5 drift case）;AUTH bypass 路径仍由 `test_login_redirect_detection_in_download` + `test_live_mode_requires_confirm_live` 守住。

## §3 invariant 守恒

| 步骤 | artifact_count | sum(role_count) | len(artifacts) | 一致 |
|---|---|---|---|---|
| knife 46 后基线 | 648 | 648 | 648 | ✅ |
| + bump（NEW）| 649 | 649 | 649 | ✅ |
| + receipt（NEW）| 650 | 650 | 650 | ✅ |

`NEW_ARTIFACTS = +2（bump + receipt）` ⇒ pack `648 → 650`。

> 注：connector（`scripts/auto_ingest_public_source.py`）是 knife 46 已登记文件的**修订**（非新文件），bump 时 SKIP;5 个 pytest 新 case 是同一测试文件的行内修改（与原 26 case 合并到 `tests/test_auto_ingest_public_source_s52.py`），不在 manifest 内单独计项。

## §4 drift 路径契约（5 字段 + 4 红线）

per tasking 333 §SCHEMA,drift 报告必须包含:
- **源**（domain + category + URL + WORM 路径）
- **URL**（同上）
- **computed SHA-256**（实测下载字节的 hex）
- **expected SHA-256**（registry.csv file_hash_sha256 的 hex）
- **建议**（用户裁定二选一:更新 registry 或改用稳定 URL）

red-line guards（4）:
- ❌ 不自动改 registry.csv file_hash_sha256
- ❌ 不把 drift 标成 O1_AUTO_INTAKED（drift ≠ 收口）
- ❌ 不静默吞掉 drift
- ❌ 不 headless / 不绕过反爬获取"应该匹配的"内容

5/5 pytest 守住（含 `test_sha_drift_red_line_no_registry_write` 源码静态扫 + `test_sha_drift_does_not_auto_update_registry` 运行时 `read_bytes` 不变）。

## §5 live 探测证据（tasking 333 §SCHEMA "做一次"）

执行命令:
```
python3 scripts/auto_ingest_public_source.py \
    --live --confirm-live=/tmp/cegr_live_probe_20260826.jsonl
```

输出:
```
OK pilot matched: stats.gov.cn / NATIONAL_BULLETIN
   primary_url: https://www.stats.gov.cn/sj/zxfb/
   auth_note: 公开；无需授权
   expected SHA: dea13b8a4ff116ca…
OK downloaded 73116 bytes; sha256=bb1a573af8ea5802…
⚠ SHA drift; archived drifted bytes: data/public_archives/2026-08/stats.gov.cn/zxfb
⚠ drift report written: reviews/stage0-gate0-rework-2026-08-23/20260826T093042Z-stage2-public-source-sha-drift-stats.gov.cn-NATIONAL_BULLETIN.md
⚠ CANDIDATE_AUTO lineage emitted; rc=4 means drift handled, NOT O1 收口。等用户裁定。
RC=4
```

实际返回码 `rc=4`（drift handled, NOT O1 收口）— 不再是硬 fail。

落地的 3 个产物:
1. **WORM 归档** `data/public_archives/2026-08/stats.gov.cn/zxfb`（73,116 bytes,SHA-256 `bb1a573af8ea5802c6d823bb108e54f8a76e7dde1059e70cb25930f66d70d768`）
2. **drift 报告** `reviews/stage0-gate0-rework-2026-08-23/20260826T093042Z-stage2-public-source-sha-drift-stats.gov.cn-NATIONAL_BULLETIN.md`（含 5 字段 + WORM 路径 + 红线 4 项）
3. **lineage JSONL** `/tmp/cegr_live_probe_20260826.jsonl`:
   ```json
   {"is_demo": "true", "source_file_sha256": "bb1a573af8ea5802c6d823bb108e54f8a76e7dde1059e70cb25930f66d70d768", "source_file_path": "data/public_archives/2026-08/stats.gov.cn/zxfb", "source_agency": "国家统计局", "intake_ts": "2026-08-26T09:30:42.694733+00:00", "intake_status": "CANDIDATE_AUTO"}
   ```

证据快照（已 copy 进 reviews/）:
- `reviews/stage0-gate0-rework-2026-08-23/_knife47_live_probe.log`（完整 stdout+stderr）
- `reviews/stage0-gate0-rework-2026-08-23/_knife47_live_probe_lineage.jsonl`（lineage 行）

## §6 红线审计

| 红线 | 守 |
|---|---|
| ❌ 不宣布 Gate/O1 PASS | drift ≠ O1_AUTO_INTAKED;is_demo=true;receipt 不写 "PASS" 字样 |
| ❌ 不自动改 registry.csv file_hash_sha256 | `test_sha_drift_does_not_auto_update_registry` 验证源码不含 DictWriter / 不 open REGISTRY_CSV;实际探测前后 registry.csv `read_bytes()` 不变 |
| ❌ 不把 drift 标成 O1_AUTO_INTAKED | `main()` 显式分流 sha_matched→O1_AUTO_INTAKED / else→CANDIDATE_AUTO;两路径互斥 |
| ❌ 不静默吞掉 drift | `write_sha_drift_report(...)` 强制写 reviews/.../sha-drift-...md（5 字段 + WORM 路径 + 红线 4 项） |
| ❌ 不 headless / 不绕过反爬 | `test_script_does_not_import_headless_browser` 守住;live 仅用 `requests.get` + `User-Agent` |
| ❌ 不批量 2020-2025 / 不把 1909 代表中国 | 不在本刀范围 |
| ❌ 不擅自 --force | normal `--ff-only` pull;`git push origin HEAD` 默认 |
| ❌ 不接 S2.7-b UI | drift 仅落 lineage JSONL + WORM + reviews/;前端零改动 |
| ❌ 不改 `gate_thresholds.json` | untouched |
| ❌ 不碰 `00-CC-CURRENT.md` | Cursor owns;untouched |
| ❌ 不在 chat 复述 Cursor 长文 | 仅短句回执 |
| ❌ 不索要 PAT | 无 |
| ✅ pack invariant | `sum(role_count) == artifact_count == len(artifacts)` 在每步后断言（详见 §3） |
| ✅ receipt location | `reviews/stage0-gate0-rework-2026-08-23/334-...md` |

## §7 用户裁定引导（per tasking 333 §SCHEMA + docs/52 §6.3）

用户对 `stats.gov.cn NATIONAL_BULLETIN` SHA drift 可裁 4 路径之一:

1. **采纳 computed SHA `bb1a573a…d768`** → 更新 `source_registry/registry.csv` 行 3 `file_hash_sha256` 为实测值（认定源站换版/换路径）;**本 connector 不会自动改**，必须用户手动
2. **改用稳定 URL** → 如 `archive.org` Wayback Machine 快照（如有）或 稳定 PDF/EXCEL 直链（若 NBS 提供）;更新 `primary_url` + `file_hash_sha256`
3. **跳过该源** → `source_registry/registry.csv` 行 3 `enabled=FALSE`
4. **暂缓** → 保持 `enabled=TRUE` + `CANDIDATE_AUTO` 在 lineage 中保留供后续审计;不进入 O1 收口

**注**:本次探测无 AUTH 阻断（HTTP 200）;drift 是源站变更导致（典型 NBS 月度发布版式漂移）;非验证码/付费墙/登录绕过场景。

## §8 推 / 落地

- commit: 待落地（receipt 中 cc_head 待填）
- push origin: 待落地（`git push origin HEAD` 优先）
- push github: 待落地（`git push github HEAD`）
- backfill SHA: 在 receipt 后续 commit 中填 `cc_head`（per knife 17 教训:不 amend-after-push）

## §9 下次心跳预期

`./scripts/cc_gate_watch.sh --pull` → re-arm → 84 POLL。

`cursor_ack` 未 bump 前只 POLL;queue_rev 变化 → 读 §NOW。

— End of Knife 47 receipt 334 —