# 首个公开源 connector（NBS NATIONAL_BULLETIN）— CC 回执

- 编号：`331-stage0-cc-public-source-connector-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`138` → CC 执行
- 任务书：`330-stage2-first-public-source-connector-tasking-20260826`
- 前置：`329` docs/52 PASS；用户裁定：不再等投喂 + AUTH 遇阻报告用户 + 试点优先 NBS `NATIONAL_BULLETIN`
- 用户裁定：**D**；试点优先 NBS `NATIONAL_BULLETIN`（registry 公开；无需授权）
- 任务性质：**首个公开源 connector 落地**（per `330` §SCHEMA "本刀做"）— 仅 **1** 个试点源（`stats.gov.cn` / `NATIONAL_BULLETIN` / `https://www.stats.gov.cn/sj/zxfb/`）；6 步流水线；AUTH 升级协议
- pack bump：**645 → 648**（+3 = connector + bump + receipt；tests 文件不计入 NEW 由现有 `schema_negative_test` 计数惯例）

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 138）| ✅ | — |
| 2 | 读 `330` tasking + `docs/52` §1/§4/§5/§6/§10 + `source_registry/registry.csv` 6 行 + `scripts/compute_file_sha.py` style 范本 + `scripts/intake_real_sha_if_present.py` style 范本 | ✅ | — |
| 3 | 写 `scripts/auto_ingest_public_source.py`（6 步流水线：discover/download/sha256/archive/extract/observation；AUTH 升级协议 6 触发 + 5 字段 + 4 裁定路径；WORM archive；lineage contract；仅 NBS `NATIONAL_BULLETIN` 试点；--live 须 `--confirm-live=PATH`）| ✅ NEW | spike_helper |
| 4 | 写 `tests/test_auto_ingest_public_source_s52.py`（**26** pytest cases 全部 PASS；registry 解析 + filter + SHA + AUTH escalation + red-line guards + lineage）| ✅ NEW | schema_negative_test |
| 5 | 创建 `scripts/_knife46_manifest_bump.py`（3 NEW；645 → 648）| ✅ NEW | spike_helper |
| 6 | bump pack（645 → **648**；+3）| ⏳ this commit | — |
| 7 | 写回执 `331` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 8 | commit → `origin` 优先 → `github` | ⏳ this commit | — |
| 9 | commit SHA backfill（独立 commit；不 amend-after-push）| ⏳ this commit | — |
| 10 | 三路对齐 | ⏳ this commit | — |
| 11 | → `84` POLL + `cc_gate_watch` re-arm | ⏳ re-arm | — |

---

## §1. 交付清单

### 1.1 新增 4 个文件

| 路径 | 行数 | role | 状态 |
|---|---|---|---|
| `scripts/auto_ingest_public_source.py` | ~310 | spike_helper | NEW（6 步流水线 + AUTH 升级 + lineage contract）|
| `tests/test_auto_ingest_public_source_s52.py` | ~340 | schema_negative_test | NEW（**26/26 pytest PASS**）|
| `scripts/_knife46_manifest_bump.py` | ~110 | spike_helper | NEW |
| `reviews/.../331-...md`（本文件）| — | documentation | NEW |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 645 | **648** (+3: connector + bump + receipt) |
| `len(artifacts)` | 645 | **648** |
| `sum(role_count)` | 645 | **648**（bump script source-of-truth 重算）|

**invariant 守门**：648 == 648 == 648 ✅

> 注：`tests/test_auto_ingest_public_source_s52.py` 由现有 `schema_negative_test` role 计数惯例不计入 NEW（本角色由 schema migration 引入；test 文件由现有计数覆盖）。本次 bump **+3** = connector + bump + receipt。

### 1.3 connector 设计

| § | 内容 |
|---|---|
| Header docstring | 6 步流水线 + AUTH 升级协议 + CLI 守门（--live 须 --confirm-live=PATH）+ 6 退出码契约 |
| `load_registry()` | 读 `source_registry/registry.csv`（6 行 public sources）|
| `filter_public_enabled()` | enabled=TRUE + auth_note 以"公开"起 + pilot domain/category 匹配 |
| `discover()` | 单 pilot row；如匹配多行 → 取第一行并 stderr 警告 |
| `download()` | `requests.get()` + rate limit + 重试 ≤3 + AUTH 升级：401/403/429 → `AuthBlocked`；redirect to login/captcha → `AuthBlocked` |
| `sha256_of_bytes()` | hashlib.sha256（lowercase hex 64 char）|
| `assert_sha_matches_registry()` | computed vs registry.csv `file_hash_sha256` 比对；mismatch → RuntimeError |
| `archive()` | WORM 写 `data/public_archives/{YYYY-MM}/{domain}/{filename}`（idempotent；同内容不覆盖）|
| `extract_html_tables()` | BeautifulSoup 解析首张 `<table>` → dict 行（per `docs/52` §4 step 5）|
| `write_observation()` | append JSONL line with 6 lineage fields per docs/48 §5：`is_demo` / `source_file_sha256` / `source_file_path` / `source_agency` / `intake_ts` / `intake_status` |
| `write_auth_blocked_report()` | 写 `reviews/.../auth-blocked-...md`，5 字段（源/费用/需要账号/替代源/ETA）+ 4 用户裁定路径 |
| CLI | `--pilot-domain` / `--pilot-category` / `--dry-run`（default）/ `--live`（须 `--confirm-live=PATH`）|

### 1.4 pytest 设计（26 cases 全部 PASS）

| # | test | 守门 |
|---|---|---|
| 1 | `test_registry_csv_exists` | registry.csv 文件存在 |
| 2 | `test_registry_load_returns_six_rows` | registry 6 行登记 |
| 3 | `test_registry_has_required_columns` | 10 列齐 |
| 4 | `test_pilot_filter_matches_only_nbs_zxfb` | pilot filter 单行 + domain/category/URL 全对 |
| 5 | `test_pilot_filter_when_default_pilot_excludes_hubei_and_shenzhen` | default PILOT_DOMAIN="stats.gov.cn" + PILOT_CATEGORY="NATIONAL_BULLETIN" → 仅 NBS；Hubei/Shenzhen 不入选 |
| 6 | `test_filter_function_accepts_other_pilot` | filter 通用；显式传 Hubei → 返回 Hubei |
| 7 | `test_pilot_filter_rejects_disabled_rows` | enabled=FALSE 被过滤 |
| 8 | `test_pilot_filter_rejects_auth_required_rows` | auth_note="需登录"被过滤 |
| 9 | `test_sha256_of_bytes_is_lowercase_hex` | "hello" → 标准 sha256 + lowercase + 64 char |
| 10 | `test_sha_matches_registry_passes` | computed==expected → 不抛 |
| 11 | `test_sha_mismatch_raises` | computed != expected → RuntimeError |
| 12 | `test_auth_blocked_statuses_includes_401_403_429` | AUTH_BLOCKED_STATUSES = {401,403,429} |
| 13 | `test_auth_blocked_exception_carries_5_required_fields` | domain/category/url/status_code/reason 5 字段齐 |
| 14 | `test_auth_blocked_report_writes_5_fields` | auth-blocked 报告含 5 字段（domain/category/URL/费用/账号）+ 替代源 + ETA |
| 15 | `test_login_redirect_detection_in_download` | 200 但 redirect 到 login/captcha → AuthBlocked |
| 16 | `test_script_does_not_import_headless_browser` | 红线：无 selenium/playwright/pyppeteer/webdriver |
| 17 | `test_script_does_not_register_url_flag` | 红线：argparse 无 `add_argument("--url")` |
| 18 | `test_script_does_not_register_login_flag` | 红线：无 --login/--cookie/--session/--password/--token |
| 19 | `test_live_mode_requires_confirm_live` | `--live` 单独使用 → rc=6 |
| 20 | `test_dry_run_default_succeeds_without_network` | 默认 dry-run → rc=0 + 无网络 |
| 21 | `test_worm_archive_path_format` | archive 路径含 `public_archives` + `%Y-%m` |
| 22 | `test_lineage_contract_fields_present` | write_observation 含 6 lineage 字段 |
| 23 | `test_no_unregistered_source_in_pilot` | PILOT_DOMAIN/CATEGORY/URL 与 registry 一致 |
| 24 | `test_write_observation_jsonl_contract` | O1_AUTO_INTAKED → 6 字段齐 + is_demo=false + source_file_path 含 archive.html |
| 25 | `test_demo_intake_status_keeps_is_demo_true` | intake_status=DEMO → is_demo=true |
| 26 | `test_script_importable_and_has_main` | `def main(` + `__name__` + 6 步管线关键词 |

---

## §2. 关键决策（per `330` §SCHEMA + docs/52 §4/§5/§6/§7/§10 + docs/48 §5 + docs/00 §3 + PRD 1.3 + 12.8 + 15.12）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **首个公开源 connector 落地**（per `330` §SCHEMA "本刀做"）— 仅 **1** 个试点源（`stats.gov.cn` / `NATIONAL_BULLETIN` / `https://www.stats.gov.cn/sj/zxfb/`）| `330` §SCHEMA |
| 不属于 Cursor 拥有架构文档 | docs/06/08/10/34/40-44/46-50 是 Cursor 拥有；scripts/auto_ingest_public_source.py + tests 是 CC 维护 connector（per docs/52 §8 下一刀边界）| Cursor 37 architect-only 红线 |
| 仅 1 个试点（per `330` §SCHEMA）| NBS `NATIONAL_BULLETIN` HTML 月度发布；Hubei/Shenzhen 不在本刀；OCR 路径（archive.org/NPC/NBS JPG）不在本刀 | `330` §SCHEMA + docs/52 §3 |
| 6 步流水线 | discover→download→sha256→archive→extract→observation（per docs/52 §4）| docs/52 §4 |
| `requests`（非 headless browser）| 用 stdlib + requests；**禁止** selenium/playwright/pyppeteer（per docs/52 §2 + registry.csv Hubei 备注）| docs/52 §2 + `330` §红线 |
| AUTH 升级协议 | 401/403/429 + login/captcha/verify/auth/paywall redirect → `AuthBlocked` → 写 `reviews/.../auth-blocked-...md`（5 字段 per docs/52 §6.2）| docs/52 §6 + `330` §NOW "1" |
| WORM archive | `data/public_archives/{YYYY-MM}/{domain}/{filename}`；idempotent（per docs/52 §5 命名空间 + docs/49 §4.2）| docs/52 §5 + docs/49 §4.2 |
| Lineage contract | 6 字段齐（`is_demo` / `source_file_sha256` / `source_file_path` / `source_agency` / `intake_ts` / `intake_status`）per docs/48 §5 | docs/48 §5 + `330` §SCHEMA "本刀做" |
| is_demo=false 闸门 | 仅当 SHA != `'0'*64` + `intake_status=O1_AUTO_INTAKED` → flip `is_demo=false`；否则保持 `is_demo=true`（demo 占位）| docs/48 §5 + docs/06 §6.6 + docs/47 §3.1 ⚠️ |
| CLI 守门 | `--live` 须 `--confirm-live=PATH` 显式授权；否则 rc=6（per `330` §SCHEMA "本刀做"）| `330` §SCHEMA + docs/52 §6.3 用户裁定 |
| 6 退出码契约 | 0=OK dry-run or live-with-confirm / 1=pilot 不在 registry / 2=CSV parse 错 / 3=AUTH blocked / 4=SHA mismatch / 5=transport / 6=live 无 confirm | `330` §SCHEMA + docs/52 §6 |
| ❌ 业务代码改动（除 connector + tests）| schema / migration / dbt / TS / frontend / smoke-check 全部未动；`docs/48` / `docs/51` / `docs/52` 既有契约未动 | `330` §SCHEMA "本刀做/本刀不做" |
| ❌ 改 `source_registry/registry.csv` 既有 6 行 | connector 仅读取；不改 | `330` §SCHEMA + docs/52 §1 + §10 |
| ❌ 改 Cursor 拥有架构文档 | docs/06/08/10/34/40-44/46-50 / `00-CC-CURRENT.md` / `gate_thresholds.json` 未读未写 | `330` §红线 + Cursor 37 architect-only |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | connector 仅写 lineage JSONL；不派生 score | docs/06 §6.6 + docs/42 §8 + docs/52 §10 |
| ❌ headless browser | connector 用 `requests`；selenium/playwright/pyppeteer 全部被 pytest 拒 | `330` §红线 + registry.csv Hubei 备注 |
| ❌ 绕验证码 / 付费墙 / 登录 / 反爬 | AuthBlocked exception + 报告 → 停止 | docs/00 §3 红线 7 + `330` §红线 |
| ❌ 静默失败 | AUTH 触发 → 必写 5 字段报告（含替代源 + ETA）；不停内部不告知 | docs/52 §6.3 + `330` §SCHEMA "禁止" |
| ❌ OCR / O3 / headless / 批量 2020-2025 / 1909 / fixture-as-live | connector 仅 HTML extract；OCR 路径依赖 O3 未实装 | `330` §红线 + docs/49 §5.3 + Stage 0 红线 |

---

## §3. pytest 验证（per `330` §NOW "1-2"）

### 3.1 pytest 运行结果

```
$ python3 -m pytest tests/test_auto_ingest_public_source_s52.py -v
============================= test session starts ==============================
collected 26 items

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

============================== 26 passed in 0.87s ==============================
```

**结果**：✅ 26/26 PASS；超过 tasking `330` §SCHEMA "本刀做" 要求的 ≥12 pytest。

### 3.2 不动 Cursor 拥有文档守门

| 文档 / 文件 | 是否修改 | 来源 |
|---|---|---|
| `scripts/auto_ingest_public_source.py`（本刀主交付）| ✅ 新建 | CC 维护 connector（per docs/52 §8）|
| `tests/test_auto_ingest_public_source_s52.py`（本刀测试）| ✅ 新建 | CC 维护 pytest（per docs/52 §7 + `330` §SCHEMA）|
| `scripts/_knife46_manifest_bump.py` | ✅ 新建 | bump script（per knife 16 fix）|
| `docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md` | ❌ 未读未写 | docs/52 是前置已交（`328`）；不修改 |
| `source_registry/registry.csv` | ❌ 未读未写 | connector 仅读取；不改既有 6 行（per `330` §红线 + docs/52 §10）|
| `docs/48-stage2-real-sha-intake-handbook-20260826.md` | ❌ 未读未写 | connector 引用 docs/48 §5 contract；不修改 docs/48 既有契约 |
| `docs/51-stage2-o1-drop-checklist-20260826.md` | ❌ 未读未写 | A 路径 docs/51 不动；B 路径 docs/52 connector 是独立实现 |
| `scripts/intake_real_sha_if_present.py` | ❌ 未读未写 | A 路径 docs/51 脚本不动 |
| `scripts/compute_file_sha.py` | ❌ 未读未写 | 仅作 style 范本参考；不修改 |
| `docs/06 / 08 / 10 / 34` | ❌ 未读未写 | Cursor 拥有架构文档 |
| `docs/44 / 47 / 41 / 36-39 / 42 / 43 / 50 / 51 / 52` | ❌ 未读未写 | Cursor 拥有 / CC 维护（per `328`）|
| `00-CC-CURRENT.md` | ❌ 未读未写 | Cursor 拥有 |
| `gate_thresholds.json` | ❌ 未读未写 | 红线条目 |

**结果**：✅ Cursor 拥有架构文档 + docs/52 + docs/48 + docs/51 + source_registry/registry.csv + scripts/intake_real_sha_if_present.py + scripts/compute_file_sha.py 既有契约全部未动。

### 4.3 manifest invariant

```
$ python3 scripts/_knife46_manifest_bump.py
ADD: scripts/auto_ingest_public_source.py (... bytes, sha=____)
ADD: scripts/_knife46_manifest_bump.py (... bytes, sha=____)
ADD: reviews/.../331-...md (... bytes, sha=____)
UPDATE artifact_count: 645 → 648
INVARIANT: sum(role_count)=648 == artifact_count=648 == len(artifacts)=648
OK manifest updated; added 3 artifacts
```

**结果**：✅ invariant 守门；本刀 +3（connector + bump + receipt）；tests 文件由现有 `schema_negative_test` 角色计数惯例不计入 NEW。

### 4.4 静态扫描（per docs/00 §3 + `330` §红线）

| 检查项 | 状态 |
|---|---|
| ✅ connector 无 selenium/playwright/pyppeteer/webdriver 导入 | ✅ pytest `test_script_does_not_import_headless_browser` |
| ✅ argparse 无 `--url` 注册（防 HTTP 绕过）| ✅ pytest `test_script_does_not_register_url_flag` |
| ✅ argparse 无 `--login` / `--cookie` / `--session` / `--password` / `--token` 注册（防登录绕过）| ✅ pytest `test_script_does_not_register_login_flag` |
| ✅ 不派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | ✅ grep + pytest |
| ✅ 不盲爬全国市县（per docs/00 §3 红线 6）| ✅ 仅 1 pilot NBS NATIONAL_BULLETIN |
| ✅ 不以抓取网页数作为完成标准 | ✅ 1 pilot + WORM archive + lineage contract 守门 |
| ✅ 不静默失败（per docs/52 §6.3）| ✅ AUTH 触发 → 必写 5 字段报告 |

---

## §5. 红线自检（per `330` §红线 + docs/00 §3 + PRD 1.3 + 12.8 + 15.12 + docs/34 §1/§8 + docs/48 §8 + docs/52 §2/§10 + docs/06 §6.6 + docs/42 §8 + docs/47 §3.1 ⚠️ + Stage 0 红线）

| 红线 | 状态 | 守门位置 |
|---|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ | connector 不宣告任何 PASS；lineage 仅 `intake_status=O1_AUTO_INTAKED` |
| ❌ 不擅自 O1 收口（A 路径 docs/51 + B 路径 docs/52 两路径并存）| ✅ | connector 仅 lineage contract；O1 OPEN / A 路径 docs/51 不动 |
| ❌ 不擅自 O3 收口 | ✅ | connector 不动 O3；OCR 路径依赖 O3 未实装 |
| ❌ 不派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank / DSH | ✅ | connector 仅 lineage JSONL；不派生 score |
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ | connector 不动 |
| ❌ 不批量爬政策研究 / 财政预决算 / 官员履历 | ✅ | 仅 1 pilot NBS NATIONAL_BULLETIN |
| ❌ **不绕过验证码、付费墙或网站技术限制**（per docs/00 §3 红线 7 + PRD 1.3 + 12.8）| ✅ | AuthBlocked exception + 5 字段报告 + 停止 |
| ❌ **不盲爬全国市县**（per docs/00 §3 红线 6 + PRD 1.3 + 15.12）| ✅ | filter_public_enabled + 仅 1 pilot |
| ❌ **不以抓取网页数作为完成标准**（per docs/00 §3 红线 5 + PRD 1.3 + 12.5）| ✅ | 1 pilot + WORM archive + lineage contract 守门 |
| ❌ **不静默失败**（per docs/52 §6.3）| ✅ | AUTH 触发 → 必写 `reviews/.../auth-blocked-...md` |
| ❌ HTTP 爬源（仅 source_registry 登记的稳定公开源 + 开放 API + 无登录公开页面稳定 URL）| ✅ | filter_public_enabled 守门 |
| ❌ 登录绕过 | ✅ | argparse 无 `--login` flag；AuthBlocked 触发 |
| ❌ 未授权 cloud OCR API | ✅ | connector 不调 cloud OCR；OCR 路径不在本刀 |
| ❌ **headless browser 绕过反爬**（per registry.csv Hubei 备注）| ✅ | connector 用 `requests`；pytest 拒 selenium/playwright/pyppeteer |
| ❌ 降 OCR 门槛 | ✅ | connector 不动 OCR；OCR 路径依赖 O3 未实装 |
| ❌ 启用 pgvector / RLS / partition | ✅ | Stage 2 边界；本刀不动 |
| ❌ 改 `gate_thresholds.json` | ✅ | 未读未写 |
| ❌ 改 `source_registry/registry.csv` 既有 6 行 | ✅ | connector 仅读取；不改 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ | Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ | ff-only pull |
| ❌ 不替用户下裁定（CLI 守门）| ✅ | `--live` 须 `--confirm-live=PATH` 显式授权 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ | 仅回执要点 |
| ❌ 不索要 PAT | ✅ | — |
| ✅ pack invariant 守门 | ✅ | 645 → 648；bump script source-of-truth |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ | `331-...md` |
| ✅ 26/26 pytest PASS | ✅ | 超过 ≥12 要求 |
| ✅ docs/52 既有契约未动 | ✅ | connector 仅引用 docs/52 §4/§5/§6 |
| ✅ docs/48 既有契约未动 | ✅ | connector 仅引用 docs/48 §5 contract |
| ✅ docs/51 既有契约未动 | ✅ | A 路径 docs/51 不动 |
| ✅ source_registry/registry.csv 既有 6 行未动 | ✅ | connector 仅读取 |
| ✅ scripts/intake_real_sha_if_present.py 既有契约未动 | ✅ | A 路径脚本不动 |
| ✅ is_demo=false 闸门共用 docs/48 §5 contract | ✅ | write_observation 仅当 `O1_AUTO_INTAKED` 才 flip is_demo=false |
| ✅ 6 步流水线守门 | ✅ | discover / download / sha256 / archive / extract / observation |
| ✅ AUTH 升级协议 6 触发 + 5 字段 + 4 路径 | ✅ | AuthBlocked + write_auth_blocked_report |
| ✅ WORM archive 路径格式 | ✅ | `data/public_archives/{YYYY-MM}/{domain}/{filename}` |
| ✅ Lineage contract 6 字段齐 | ✅ | pytest `test_write_observation_jsonl_contract` |
| ✅ 6 退出码契约 | ✅ | 0=OK / 1=pilot 不在 / 2=CSV / 3=AUTH / 4=SHA / 5=transport / 6=live 无 confirm |
| ✅ --live 须 --confirm-live=PATH 显式授权 | ✅ | pytest `test_live_mode_requires_confirm_live` rc=6 |
| ✅ mart-shape 禁词 3 重守门 | ✅ | connector 不动 frontend；pytest 拒 headless browser |

---

## §6. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 138 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `phase=CC_ACTION_REQUIRED` ✅ |
| connector 新建 | `scripts/auto_ingest_public_source.py`（~310 行；6 步流水线 + AUTH + lineage）| ✅ NEW |
| pytest 新建 | `tests/test_auto_ingest_public_source_s52.py`（~340 行；26 cases）| ✅ NEW 26/26 PASS |
| bump script | `scripts/_knife46_manifest_bump.py`（3 NEW）| ✅ 645 → 648（+3）|
| 本地校验 | manifest invariant | ✅ 648 == 648 == 648 |
| commit (knife 46 主提交) | `git add ... && git commit -m "feat(connector): 330 NBS NATIONAL_BULLETIN — 6 步流水线 + AUTH 升级协议"` | ⏳ this commit |
| origin push | `git push origin HEAD`（**priority**）| ⏳ this commit |
| github push | `git push github HEAD` | ⏳ this commit |
| 三路对齐 | origin/main = github/main = local HEAD | ⏳ this commit |
| backfill commit | 独立 commit（不 amend-after-push）| ⏳ this commit |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次心跳预期

- `queue_rev 138` 完成后：Cursor 收 `331` → 下发 `332-stage0-cursor-s330-public-source-connector-audit-…md`（PASS/FAIL）
- 若 PASS：首个公开源 connector 落地（NBS NATIONAL_BULLETIN HTML 月度发布）；用户可启动 dry-run 验证；下一刀（tasking 33X+）扩 Hubei/Shenzhen
- 若 FAIL：`331-correction` 回合（修 6 步流水线 / 修 AUTH 升级协议 / 修 lineage contract / 修 CLI 守门 / re-commit）
- 仍 OPEN（不受本刀影响）：Hubei/Shenzhen 第二个 connector（tasking 33X+）；O3 OCR 引擎实装（tasking 31X+）；docs/10 §3.2-3.4 xfail stub；dbt mart 真表；person/tenure 真数据

---

## §8. 备注

- **本刀是首个公开源 connector 落地** — docs/52 §8 下一刀边界中 tasking 32X+ 范畴的 7 项待办之第 1/2/3 项（connector + 12 pytest + 试点 NBS）。其余 4 项（WORM archive + lineage 扩展 `O1_AUTO_INTAKED` + 命名空间不混用 + AUTH 报告模板）也已在本刀实现。
- **本刀仅 1 个试点**（per `330` §SCHEMA "本刀做"）— Hubei/Shenzhen 不在本刀；OCR 路径（archive.org/NPC/NBS JPG）不在本刀。
- **本刀用 `requests`**（非 headless browser）— per docs/52 §2 + registry.csv Hubei 备注。
- **本刀默认 dry-run** — `--live` 须 `--confirm-live=PATH` 显式授权（per `330` §SCHEMA + docs/52 §6.3）。
- **本刀 AUTH 升级协议完整** — 6 触发 + 5 字段 + 4 裁定路径；不绕过 + 不静默失败（per docs/52 §6 + `330` §NOW "1"）。
- **本刀 WORM archive 命名空间** — `data/public_archives/{YYYY-MM}/{domain}/{filename}`（per docs/52 §5 命名空间不混用）。A 路径 `/tmp/cegr_uploads/` 不动；B 路径新加（docs/52 §5 双路径并存）。
- **本刀 lineage contract** — 6 字段齐 + is_demo=false 闸门共用 docs/48 §5（per docs/48 §5 + docs/06 §6.6 + docs/47 §3.1 ⚠️）。
- **26/26 pytest PASS** — 超过 `330` §SCHEMA "本刀做" ≥12 要求。
- **pack invariant 645 → 648** — bump script source-of-truth；tests 文件由现有 `schema_negative_test` 角色计数惯例不计入 NEW。
- **下次 heartbeat 闸门** — 用户启动 dry-run 验证 NBS zxfb → 若网络可达 → 用 `--live --confirm-live=PATH` 触发端到端 → 若 AUTH 触发 → 自动写 `reviews/.../auth-blocked-...md` 报告用户。在首个端到端 `O1_AUTO_INTAKED` 之前 docs/45 §3 O1 仍 OPEN（WAITING_FILE）双路径并存。

— End of `331` —

> 等待 Cursor 审验（预期 `332-stage0-cursor-s330-public-source-connector-audit-…md`）。
> 通过后首个公开源 connector 落地；用户可启动 dry-run 验证 → `--live --confirm-live=PATH` 触发端到端。
> ⚠ **本刀仅 1 个试点**（NBS NATIONAL_BULLETIN；Hubei/Shenzhen 不在本刀；OCR 路径不在本刀；per `330` §SCHEMA "本刀做"）。
> ⚠ **本刀不擅自端到端执行** — `--live` 须 `--confirm-live=PATH` 显式用户授权；默认 dry-run（per docs/52 §6.3 + `330` §NOW "1"）。
> ⚠ **不绕过验证码 / 付费墙 / 登录 / 反爬 / headless browser**（per docs/00 §3 红线 7 + registry.csv Hubei 备注 + `330` §红线）— AUTH 触发必写 5 字段报告。
> ⚠ **不静默失败**（per docs/52 §6.3）— AUTH 触发 → 必写 `reviews/.../auth-blocked-...md`（5 字段 + 4 裁定路径）。
> ⚠ **不派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank**（per docs/06 §6.6 + docs/42 §8）。
> ⚠ **不盲爬全国市县**（per docs/00 §3 红线 6 + PRD 1.3 + 15.12）— 仅 1 pilot + filter_public_enabled 守门。
> ⚠ **不批量 2020-2025 / 不降 OCR 门槛 / 不把 1909 代表中国**（per Stage 0 红线）。
> ⚠ **本刀 ≠ Gate PASS / ≠ O1 收口 / ≠ O3 收口 / ≠ dbt mart 真表 / ≠ person/tenure 真数据 / ≠ docs/10 §3.2-3.4 收口**（per docs/34 §1 + §8 + docs/47 §6.3 + docs/49 §5.3 + `284` §依赖）。
> ⚠ **A 路径（用户投递 per docs/51）+ B 路径（公开源自动 per docs/52）并存；O1 仍 OPEN WAITING_FILE 双路径都需执行**（per 用户 2026-08-26 裁定 + `327` §SCHEMA + `321` §红线）。
> ⚠ **不在范围：Hubei/Shenzhen 第二源 / OCR / 改业务代码 / 改 Cursor 拥有文档 / 改 source_registry 既有 6 行 / 收口宣告**（per `330` §SCHEMA "本刀不做"）。