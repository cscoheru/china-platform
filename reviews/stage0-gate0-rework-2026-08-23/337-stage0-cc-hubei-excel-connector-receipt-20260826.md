# Knife 48 回执 — 湖北 EXCEL 公开源 connector（tasking 336）

- 编号：`337-stage0-cc-hubei-excel-connector-receipt-20260826`
- 前置：`334` knife 47 已落（pack 650）;`335` NBS drift PASS;NBS 正式 `O1_AUTO_INTAKED` 等用户 (a)/(b);本刀并行推进第二试点
- 落地:`Hubei EXCEL pilot` + `extract_xlsx_tables` + `dispatcher` + `10 pytest` + `一次 live 探测 (drift)` + `回执 337`
- 回执 §NOW:`Hubei 公开源接入 + drift 候选路径复用;不 headless;不绕过 ERR_CONNECTION_RESET`

## §META

| 字段 | 值 |
|---|---|
| knife | 48 |
| tasking | 336 |
| phase | CC_ACTION_REQUIRED |
| queue_rev | 140 |
| cc_receipt | 337 |
| cc_head | `4d9e28f`（已 commit + push origin + push github + three-way converged）|
| user_ruling | D（Hubei pilot + 复用 AUTH + drift + 不 headless + ≥8 pytest + 一次 live 探测）|
| 测试 | 41/41 pytest PASS（knife 47 是 31/31,新增 10 Hubei case;超 tasking 336 §SCHEMA "≥8 pytest"）|
| live 探测 | rc=4（drift handled, NOT O1 收口）;见 §5 |
| pack | 650 → 652（+2:bump + receipt;connector 是 knife 46/47 已登记文件的修订,bump SKIP）|

## §NOW — tasking 336 §SCHEMA 落点

| 决策点 | 落地 |
|---|---|
| (1) 扩展 connector 支持 pilot=tjj.hubei.gov.cn / PROVINCIAL_BULLETIN:discover→download→sha256→archive→extract(xlsx)→observation | `extract_xlsx_tables(blob)` 用 openpyxl（read_only=True, data_only=True）取第一个 sheet,首行作 header,其余行作 dict;`extract_tables(blob, category=...)` 按 category 分流:NATIONAL→HTML / PROVINCIAL→XLSX / 未知→ValueError;`main()` 把原 `extract_html_tables(blob)` 调用改为 `extract_tables(blob, category=pilot["category"])` |
| (2) **禁止 headless**（registry 注明）;curl/requests 直链 | `download()` 仍是 `requests.get` + `User-Agent`;全局 `test_script_does_not_import_headless_browser` 守住（selenium/playwright/pyppeteer/webdriver 禁词）;registry.csv Hubei 行原文 `禁止 headless browser,被 ERR_CONNECTION_RESET 拒绝` 由 `test_hubei_red_line_no_headless_browser` 守住 |
| (3) 复用 AUTH + SHA drift（CANDIDATE_AUTO）路径 | knife 47 的 `AuthBlocked` + `write_auth_blocked_report` + `ShaDrift` + `write_sha_drift_report` 完全保留;`main()` 中 sha_matched 分流对 Hubei 与 NBS 等价生效 |
| (4) dry-run 默认;一次 `--live` 探测证据入回执 | 探测执行:rc=4;落 WORM 71B（实测字节）+ 1 份 sha-drift report + `CANDIDATE_AUTO` lineage(`is_demo=true`)。详见 §5 |
| (5) ≥8 pytest | 10 case 落地,超 25%:`test_hubei_pilot_filter_matches_tjj_hubei` / `test_hubei_dry_run_succeeds_without_network` / `test_hubei_live_requires_confirm_live` / `test_extract_xlsx_tables_returns_rows` / `test_extract_xlsx_tables_handles_empty_sheet` / `test_extract_dispatcher_routes_by_category` / `test_hubei_worm_archive_path_format` / `test_hubei_red_line_no_headless_browser` / `test_hubei_red_line_drift_path_is_reused` / `test_hubei_drift_intake_status_is_candidate_auto` |
| (6) 回执 `337` | 本文件 |

## §1 修改清单

| 文件 | 角色 |
|---|---|
| `scripts/auto_ingest_public_source.py` | +`extract_xlsx_tables(blob)` (~30 行);+`extract_tables(blob, category=...)` dispatcher;`main()` live 路径 `extract_html_tables` → `extract_tables(..., category=)`;docstring 增 "two pilots (HTML + XLSX)" + headless 标注。spike_helper（knife 46 已登记,bump SKIP）|
| `tests/test_auto_ingest_public_source_s52.py` | +10 Hubei case（详见 §NOW (5)）;31 → 41 pytest。schema_negative_test（行内归类）|
| `scripts/_knife48_manifest_bump.py` | NEW ~110 行;spike_helper |
| `reviews/stage0-gate0-rework-2026-08-23/337-stage0-cc-hubei-excel-connector-receipt-20260826.md` | NEW（本文件）;documentation |
| `reviews/stage0-gate0-rework-2026-08-23/20260826T094554Z-stage2-public-source-sha-drift-tjj.hubei.gov.cn-PROVINCIAL_BULLETIN.md` | NEW（live 探测产物;1 份 drift 报告;非 receipt 主体,但作为 evidence 链入 §5）;不计入 NEW_ARTIFACTS（live 探测副产物,与 knife 47 的 drift 报告同性质）|

## §2 pytest 结果

```
... 31 NBS+drift case 全部 PASSED（无回归）...
tests/test_auto_ingest_public_source_s52.py::test_hubei_pilot_filter_matches_tjj_hubei PASSED
tests/test_auto_ingest_public_source_s52.py::test_hubei_dry_run_succeeds_without_network PASSED
tests/test_auto_ingest_public_source_s52.py::test_hubei_live_requires_confirm_live PASSED
tests/test_auto_ingest_public_source_s52.py::test_extract_xlsx_tables_returns_rows PASSED
tests/test_auto_ingest_public_source_s52.py::test_extract_xlsx_tables_handles_empty_sheet PASSED
tests/test_auto_ingest_public_source_s52.py::test_extract_dispatcher_routes_by_category PASSED
tests/test_auto_ingest_public_source_s52.py::test_hubei_worm_archive_path_format PASSED
tests/test_auto_ingest_public_source_s52.py::test_hubei_red_line_no_headless_browser PASSED
tests/test_auto_ingest_public_source_s52.py::test_hubei_red_line_drift_path_is_reused PASSED
tests/test_auto_ingest_public_source_s52.py::test_hubei_drift_intake_status_is_candidate_auto PASSED

============================== 41 passed in 1.31s ==============================
```

注:knife 47 是 31 case;knife 48 +10 Hubei case;超 tasking 336 §SCHEMA "≥8 pytest" 25%。无 NBS 回归。

## §3 invariant 守恒

| 步骤 | artifact_count | sum(role_count) | len(artifacts) | 一致 |
|---|---|---|---|---|
| knife 47 后基线 | 650 | 650 | 650 | ✅ |
| + bump（NEW）| 651 | 651 | 651 | ✅ |
| + receipt（NEW）| 652 | 652 | 652 | ✅ |

`NEW_ARTIFACTS = +2（bump + receipt）` ⇒ pack `650 → 652`。

> 注:connector 是 knife 46 已登记文件的**修订**(knife 47+48 均改同一脚本),bump SKIP;10 个 pytest 新 case 是同一测试文件的行内修改(与 31 case 合并到 `tests/test_auto_ingest_public_source_s52.py`),不在 manifest 内单独计项。live 探测副产物的 drift 报告同 knife 47,不进 manifest。

## §4 dispatcher 契约 + 抽取契约

per tasking 336 §SCHEMA + docs/52 §4 6 步流水线,extractor 必须按 category 分流,且未知 category 必须显式 fail-fast:

| category | extractor | 依赖 |
|---|---|---|
| `NATIONAL_BULLETIN` | `extract_html_tables` (BeautifulSoup) | beautifulsoup4 |
| `PROVINCIAL_BULLETIN` | `extract_xlsx_tables` (openpyxl) | openpyxl |
| 其他 | `ValueError("unknown category ...")` | — |

3 条 pytest 守住:`test_extract_dispatcher_routes_by_category` (含 unknown 抛 ValueError) + `test_extract_xlsx_tables_returns_rows` + `test_extract_xlsx_tables_handles_empty_sheet`。

`extract_xlsx_tables` 行为契约:
- 第一个 sheet
- 首行非空 cell 作 header
- 后续非空行 → `{header: value}` dict,value 用 `str(v)` 转换
- 全空行 skip
- 空 workbook → `[]`(不崩、不伪造)

## §5 live 探测证据（tasking 336 §SCHEMA "一次"）

执行命令:
```
python3 scripts/auto_ingest_public_source.py \
    --pilot-domain=tjj.hubei.gov.cn \
    --pilot-category=PROVINCIAL_BULLETIN \
    --live \
    --confirm-live=/tmp/cegr_hubei_probe_20260826.jsonl
```

输出:
```
OK pilot matched: tjj.hubei.gov.cn / PROVINCIAL_BULLETIN
   primary_url: https://tjj.hubei.gov.cn/tjsj/sjkscx/tjyb/
   auth_note: 公开；无需授权；直链 .xlsx 可下载
   expected SHA: c5cf5abeb4fdf97a…
OK downloaded 71 bytes; sha256=65b5156901042419…
⚠ SHA drift; archived drifted bytes: data/public_archives/2026-08/tjj.hubei.gov.cn/tjyb
⚠ drift report written: reviews/stage0-gate0-rework-2026-08-23/20260826T094554Z-stage2-public-source-sha-drift-tjj.hubei.gov.cn-PROVINCIAL_BULLETIN.md
⚠ CANDIDATE_AUTO lineage emitted; rc=4 means drift handled, NOT O1 收口。等用户裁定。
RC=4
```

实际返回码 `rc=4`(drift handled, NOT O1 收口)。

WORM 字节内容(前 200 chars):
```html
<script language="javascript">
window.location = "./2026yb/";
</script>
```

**洞察**:Hubei 索引页返回的是一个 **71 字节 JS 重定向**(让浏览器跳到 `./2026yb/`),而非真实 .xlsx;这是省级统计局常见的 anti-bot 防护 —`registry.csv` 注:`"禁止 headless browser,被 ERR_CONNECTION_RESET 拒绝"`。connector 正确识别为 drift(71B ≠11261B),不伪造、不绕过 JS 重定向、不切 headless。

落地的 3 个产物:
1. **WORM 归档** `data/public_archives/2026-08/tjj.hubei.gov.cn/tjyb`(71 bytes,SHA-256 `65b5156901042419a2065d0250e767317bc8facb04a56b231dec215a4cff78b4`)
2. **drift 报告** `reviews/stage0-gate0-rework-2026-08-23/20260826T094554Z-stage2-public-source-sha-drift-tjj.hubei.gov.cn-PROVINCIAL_BULLETIN.md`(含 5 字段 + WORM 路径 + 红线 4 项)
3. **lineage JSONL** `/tmp/cegr_hubei_probe_20260826.jsonl`:
   ```json
   {"is_demo": "true", "source_file_sha256": "65b5156901042419a2065d0250e767317bc8facb04a56b231dec215a4cff78b4", "source_file_path": "data/public_archives/2026-08/tjj.hubei.gov.cn/tjyb", "source_agency": "湖北省统计局", "intake_ts": "2026-08-26T09:45:54.424449+00:00", "intake_status": "CANDIDATE_AUTO"}
   ```

证据快照(已 copy 进 reviews/):
- `reviews/stage0-gate0-rework-2026-08-23/_knife48_hubei_probe.log`(完整 stdout+stderr)
- `reviews/stage0-gate0-rework-2026-08-23/_knife48_hubei_probe_lineage.jsonl`(lineage 行)

## §6 红线审计

| 红线 | 守 |
|---|---|
| ❌ 不宣布 Gate/O1 PASS | Hubei drift ≠ O1_AUTO_INTAKED;is_demo=true;receipt 不写 "PASS" 字样 |
| ❌ 不擅自改 NBS registry 哈希(NBS 等用户) | NBS registry 完全未触碰;live 探测后 `read_bytes()` 不变 |
| ❌ 不自动改 registry.csv | `test_sha_drift_does_not_auto_update_registry` + Hubei 等价(同源码)守住;实际探测前后 registry.csv `read_bytes()` 不变 |
| ❌ 不把 drift 标成 O1_AUTO_INTAKED | `main()` 显式分流 sha_matched→O1_AUTO_INTAKED / else→CANDIDATE_AUTO;两路径互斥 |
| ❌ 不静默吞掉 drift | `write_sha_drift_report(...)` 强制写 reviews/.../sha-drift-...md(5 字段 + WORM 路径 + 红线 4 项) |
| ❌ **不 headless / 不绕过反爬**(tasking 336 §红线 + registry) | `test_script_does_not_import_headless_browser` 守住(全局);`test_hubei_red_line_no_headless_browser` 守住(registry 原文 `禁止 headless browser,被 ERR_CONNECTION_RESET 拒绝`)。live 探测收到 71B JS 重定向,**不**切 headless 跟随 |
| ❌ 不批量 2020-2025 / 不把 1909 代表中国 | 不在本刀范围 |
| ❌ 不擅自 --force | normal `--ff-only` pull;`git push origin HEAD` 默认 |
| ❌ 不接 S2.7-b UI | drift 仅落 lineage JSONL + WORM + reviews/;前端零改动 |
| ❌ 不改 `gate_thresholds.json` | untouched |
| ❌ 不碰 `00-CC-CURRENT.md` | Cursor owns;untouched |
| ❌ 不在 chat 复述 Cursor 长文 | 仅短句回执 |
| ❌ 不索要 PAT | 无 |
| ✅ pack invariant | `sum(role_count) == artifact_count == len(artifacts)` 在每步后断言(详见 §3) |
| ✅ receipt location | `reviews/stage0-gate0-rework-2026-08-23/337-...md` |

## §7 用户裁定引导（per tasking 336 §SCHEMA + docs/52 §6.3）

Hubei 探测结果是 71B JS 重定向,需用户裁定:

1. **提供稳定直链** → 更新 `source_registry/registry.csv` 行 2 `primary_url` 为某个稳定 `.xlsx` 直链(如 `https://tjj.hubei.gov.cn/.../hubei_2026_06.xlsx`)+ 同步 `file_hash_sha256`(若已存样本);下次心跳重跑 connector
2. **改用第三方镜像**(如 Wayback Machine / 中国统计年鉴汇编站);更新 `primary_url`
3. **跳过 Hubei** → `source_registry/registry.csv` 行 2 `enabled=FALSE`
5. **暂缓** → 保持 `enabled=TRUE` + `CANDIDATE_AUTO` 在 lineage 中保留供后续审计;不进入 O1 收口

**注**:本探测**未触发 AUTH 阻断**(HTTP 200),drift 是源站 anti-bot(JS 重定向)而非验证码/付费墙/登录绕过场景。registry 的"禁止 headless browser"明确告知:**不能**用 headless 跟随 JS 重定向 — 等用户给稳定直链或暂缓。

## §8 与 docs/52 §3 第二试点建议对账

docs/52 §3 首批 1-3 试点源建议:NBS HTML → **Hubei EXCEL** → Shenzhen HTML。

| 试点 | 状态 |
|---|---|
| NBS HTML | knife 46 connector + knife 47 drift 路径;O1 等用户 (a)/(b);**331 + 334 已落** |
| Hubei EXCEL | knife 48(本刀) connector + drift 路径;O1 等用户 (a)/(b);**337 已落** |
| Shenzhen HTML | 待 tasking 33X+ 落地(下一刀候选)|

`extract_tables` dispatcher 已为 Shenzhen HTML(`MUNICIPAL_BULLETIN`)预留分支点;只需加 `extract_html_tables` 调用 + registry 新行 + pytest 即可。

## §9 推 / 落地

- commit: `4d9e28f` (`feat(connector): 336 Hubei EXCEL pilot + extract_tables dispatcher`)
- push origin: ✅ `4d9e28f` (`5505627..4d9e28f HEAD -> main`)
- push github: ✅ `4d9e28f` (`5505627..4d9e28f HEAD -> main`)
- three-way convergence: ✅ `local = origin = github = 4d9e28f179712320533cbb2f9d508230cf2b2890`
- backfill SHA: 本 receipt `cc_head` 字段已更新;若需补 commit 则按 knife 17 教训另起（不 amend-after-push）

## §10 下次心跳预期

`./scripts/cc_gate_watch.sh --pull` → re-arm → 84 POLL。

`cursor_ack` 未 bump 前只 POLL;queue_rev 变化 → 读 §NOW。

— End of Knife 48 receipt 337 —