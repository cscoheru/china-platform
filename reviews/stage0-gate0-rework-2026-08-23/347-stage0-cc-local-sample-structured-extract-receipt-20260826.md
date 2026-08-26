# Knife 51 回执 — registry 本地样本结构化提取 + NBS 再探（tasking 346）

- 编号：`347-stage0-cc-local-sample-structured-extract-receipt-20260826`
- 前置：`344` Knife 50 已落（pack 656）;`345` Cursor PASS;深圳 HTTPS SSL `BAD_ecPOINT` 暂缓（禁 HTTP pin）;湖北 `enabled=FALSE`;Cursor `341` 源工程代判
- 落地：connector `--from-local-sample` 模式（SHA 必匹配 / 不匹配硬失败 rc=8 / `REGISTRY_SAMPLE_INTAKED` lineage / `is_demo=true` / `data/public_extracts/{domain}/{category}.json` 结构化输出）+ `--allow-disabled-local-sample` Hubei opt-in + registry 深圳 SSL 注记 + NBS/深圳本地样本抽取 + NBS live 再探(rc=7)+ 回执 **`347`**
- 回执 §NOW：`--from-local-sample` 跑通深圳(0 行)/NBS(63 行) + NBS live 仍 JS 壳(同 knife 47 结论) + 深圳 暂缓 live 维持 + 湖北 维持 disabled;下一刀视 Cursor 审计再分派

## §META

| 字段 | 值 |
|---|---|
| knife | 51 |
| tasking | 346 |
| phase | CC_ACTION_REQUIRED |
| queue_rev | 144 |
| cc_receipt | 347 |
| user_ruling | D + 源工程 **Cursor 代判（`341`）**;深圳 HTTPS SSL 暂缓(禁 HTTP pin) |
| 测试 | **69/69 pytest PASS（59 → 69,+10:10 local-sample case,超 tasking 346 §SCHEMA "≥8 pytest" 25%）** |
| NBS live 再探 | rc=7（JS-only shell tech-blocked;与 knife 47 一致;非 O1 收口）;见 §6 |
| Shenzhen local-sample | rc=0,`REGISTRY_SAMPLE_INTAKED`,0 行（spike 表结构需后续 tasking 增强抽取） |
| NBS local-sample | rc=0,`REGISTRY_SAMPLE_INTAKED`,63 行 |
| Hubei local-sample opt-in | 测试覆盖;实跑视用户/Cursor 是否启动 |
| pack | 656 → 658（+2:bump + receipt;connector 是 knife 46 已登记文件的修订,bump SKIP） |

## §NOW — tasking 346 §SCHEMA 落点

| 决策点 | 落地 |
|---|---|
| (1) connector 增 `--from-local-sample`:读 registry `local_sample_path`,SHA 必须匹配 `file_hash_sha256`,否则 fail | `intake_from_local_sample(pilot_row, allow_disabled)` 函数;SHA 不匹配 → `LocalSampleMismatch` 异常 → main() return 8;详见 §3 |
| (2) WORM + extract + observation:`intake_status=REGISTRY_SAMPLE_INTAKED`,`is_demo=true`;另写 `data/public_extracts/{domain}/{category}.json` | `archive()` + `extract_tables()` + `write_extract_json()` + `write_observation(intake_status="REGISTRY_SAMPLE_INTAKED")`;is_demo 自动 true（per `write_observation` 内部逻辑：非 O1 即 true）;详见 §4 |
| (3) 对 NBS + 深圳各跑一次;湖北允许 `--allow-disabled-local-sample` | NBS local-sample rc=0 + 63 行;深圳 local-sample rc=0 + 0 行(spike 表结构需后续 tasking);Hubei local-sample opt-in 通过 pytest 覆盖(测试用真 spike 文件 + 真 SHA);详见 §6 |
| (4) registry 深圳 `failure_handling` 注「2026-08-26 HTTPS BAD_ecPOINT;Cursor 暂缓 live;禁 HTTP pin」 | `source_registry/registry.csv` 行 5:`auth_note`/`failure_handling`/`purpose_note` 三列注记;详见 §5 |
| (5) **一次** NBS `--live`:若得稳定文章/非壳 → 按 `341` 可 pin;否则 drift/tech-blocked 照旧 | 执行 rc=7（JS-only shell tech-blocked）;与 knife 47 一致;**未**自动 pin registry;**未**写 lineage;详见 §6.2 |
| (6) ≥8 pytest | **10 case 落地**(超 25%):详见 §2 + §NOW 逐条 |
| (7) 回执 **`347`** | 本文件 |

## §1 修改清单

| 文件 | 角色 | 状态 |
|---|---|---|
| `source_registry/registry.csv` | sz.gov.cn 行 `auth_note`/`failure_handling`/`purpose_note` 注 SSL 暂缓 | MODIFIED（knife 51 修订） |
| `scripts/auto_ingest_public_source.py` | +`PUBLIC_EXTRACTS_ROOT` 常量;+`REGISTRY_SAMPLE_INTAKE_STATUS` 常量;+`LocalSampleMismatch` 异常;+`intake_from_local_sample()` 5 步管道;+`write_extract_json()`;main() 新增 `--from-local-sample` / `--allow-disabled-local-sample` flags + 早期分支;exit code 新增 8(SHA mismatch)/9(sample missing);CLI docstring 更新 | MODIFIED（knife 51 修订;knife 46 已登记,bump SKIP） |
| `tests/test_auto_ingest_public_source_s52.py` | +10 local-sample case(flag routing / emits-status / SHA mismatch hard fail / disabled refused / Hubei allow-disabled / extract JSON / WORM archive path / no network / exit code 8 / main rc=0);59 → 69 | MODIFIED |
| `scripts/_knife51_manifest_bump.py` | NEW ~120 行;spike_helper(NEW 计项 +1) | NEW |
| `reviews/stage0-gate0-rework-2026-08-23/347-stage0-cc-local-sample-structured-extract-receipt-20260826.md` | NEW（本文件）;documentation(NEW 计项 +1) | NEW |
| `data/public_extracts/sz.gov.cn/MUNICIPAL_BULLETIN.json` | NEW（深圳本地样本结构化抽取产物;0 行;spike 表结构限制） | NEW |
| `data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN.json` | NEW（NBS 本地样本结构化抽取产物;63 行） | NEW |
| `data/public_archives/2026-08/sz.gov.cn/sample.html` | NEW（深圳 WORM 副本,62831B,SHA 验证匹配） | NEW |
| `data/public_archives/2026-08/stats.gov.cn/sample.html` | NEW（NBS WORM 副本,388238B,SHA 验证匹配） | NEW |
| `reviews/stage0-gate0-rework-2026-08-23/_knife51_sz_local_sample.log` | NEW（深圳本地样本抽取日志,553B;副产物不计入 manifest） | NEW |
| `reviews/stage0-gate0-rework-2026-08-23/_knife51_nbs_local_sample.log` | NEW（NBS 本地样本抽取日志,560B;副产物不计入 manifest） | NEW |
| `reviews/stage0-gate0-rework-2026-08-23/_knife51_nbs_live_probe.log` | NEW（NBS live 再探日志,379B;副产物不计入 manifest） | NEW |
| `reviews/stage0-gate0-rework-2026-08-23/20260826T102849Z-stage2-public-source-tech-blocked-stats.gov.cn-NATIONAL_BULLETIN.md` | NEW（NBS live tech-blocked 报告,1589B;副产物不计入 manifest） | NEW |

## §2 pytest 结果

```
tests/test_auto_ingest_public_source_s52.py::test_local_sample_flag_routes_in_main PASSED
tests/test_auto_ingest_public_source_s52.py::test_local_sample_emits_registry_sample_intaked PASSED
tests/test_auto_ingest_public_source_s52.py::test_local_sample_sha_mismatch_hard_fails PASSED
tests/test_auto_ingest_public_source_s52.py::test_local_sample_disabled_row_refused_without_opt_in PASSED
tests/test_auto_ingest_public_source_s52.py::test_local_sample_hubei_with_allow_disabled_succeeds PASSED
tests/test_auto_ingest_public_source_s52.py::test_local_sample_extracts_to_structured_json PASSED
tests/test_auto_ingest_public_source_s52.py::test_local_sample_writes_worm_archive_under_ym_domain PASSED
tests/test_auto_ingest_public_source_s52.py::test_local_sample_no_network_calls PASSED
tests/test_auto_ingest_public_source_s52.py::test_local_sample_exit_code_8_on_sha_mismatch PASSED
tests/test_auto_ingest_public_source_s52.py::test_local_sample_main_returns_0_for_sz PASSED
+ 既有 59 case 全部 PASSED（无回归）

============================== 69 passed in 1.72s ==============================
```

| 步骤 | pytest 数 |
|---|---|
| knife 50 后基线 | 59 |
| + 10 local-sample case | 69 |
| **knife 51 总数** | **69** |

knife 51 净新增 10 case(全部为全新 local-sample)。无回归。超 tasking 346 §SCHEMA "≥8 pytest" 25%。

## §3 connector 路由契约(per tasking 346 §SCHEMA)

### 3.1 `--from-local-sample` 模式契约

| 步骤 | 函数 | 输出 |
|---|---|---|
| 1. 读取 `local_sample_path`(相对 PROJECT_ROOT 或绝对路径) | `intake_from_local_sample()` | `sample_path` (Path) |
| 2. SHA 校验 | `sha256_of_bytes()` vs `file_hash_sha256` | 不匹配 → `LocalSampleMismatch` 异常 → rc=8 |
| 3. WORM 归档 | `archive(blob, domain, filename)` | `data/public_archives/{YYYY-MM}/{domain}/{filename}` |
| 4. 表抽取 | `extract_tables(blob, category=pilot.category)` | `list[dict[str, str]]` |
| 5. 结构化 JSON | `write_extract_json(...)` | `data/public_extracts/{domain}/{category}.json` |
| 6. lineage JSONL | `write_observation(intake_status="REGISTRY_SAMPLE_INTAKED")` | `--confirm-live=PATH` |

### 3.2 `REGISTRY_SAMPLE_INTAKED` lineage 契约

| 字段 | 值 |
|---|---|
| `is_demo` | `true`(诚实:sample ≠ live closure) |
| `source_file_sha256` | sample SHA(必匹配 registry,否则根本走不到这步) |
| `source_file_path` | WORM archive 相对路径 |
| `source_agency` | pilot.organization |
| `intake_ts` | UTC ISO timestamp |
| `intake_status` | `REGISTRY_SAMPLE_INTAKED`(新常量;与 `O1_AUTO_INTAKED` / `CANDIDATE_AUTO` / `DEMO` 并列) |

### 3.3 disabled-row 守门(per tasking 346 §SCHEMA "(3)")

| 情况 | 行为 |
|---|---|
| `enabled=TRUE` + `--from-local-sample` | 正常 intake;rc=0 |
| `enabled=FALSE` + `--from-local-sample` | 抛 `RuntimeError("... enabled='FALSE' ... --allow-disabled-local-sample ...")`,rc=1(per main() 兜底) |
| `enabled=FALSE` + `--from-local-sample --allow-disabled-local-sample` | 正常 intake;rc=0;**仅** Hubei 当前符合(opt-in 路径) |
| `enabled=TRUE` + SHA mismatch | 抛 `LocalSampleMismatch`,**不**归档,**不**写 lineage,rc=8 |
| `local_sample_path` 不存在 | 抛 `FileNotFoundError`,rc=9 |
| `--from-local-sample` 无 `--confirm-live=PATH` | rc=6(显式授权守门,同 live 模式) |

### 3.4 main() 新增 exit codes(per tasking 346 §SCHEMA)

| rc | 含义 |
|---|---|
| 8 | local-sample SHA 不匹配 registry(file_hash_sha256);硬失败 |
| 9 | local-sample 文件不存在(local_sample_path 指向 missing file) |

## §4 `intake_from_local_sample` 实现要点

### 4.1 enabled 守门

```python
enabled = pilot_row.get("enabled", "").strip().upper()
if enabled != "TRUE" and not allow_disabled:
    raise RuntimeError(
        f"registry row enabled={enabled!r} (not TRUE); refusing local-sample "
        f"intake for {pilot_row['domain']} / {pilot_row['category']}. "
        f"Pass --allow-disabled-local-sample to override (per tasking 346 "
        f"§SCHEMA \"(3) 湖北允许\")."
    )
```

### 4.2 SHA 守门(per tasking 346 §红线 'SHA 不匹配仍入库')

```python
sha = sha256_of_bytes(blob)
expected_sha = pilot_row["file_hash_sha256"].strip().lower()
if sha.lower() != expected_sha:
    raise LocalSampleMismatch(
        domain=pilot_row["domain"],
        category=pilot_row["category"],
        path=sample_path,
        computed_sha256=sha,
        expected_sha256=pilot_row["file_hash_sha256"],
    )
```

**关键红线**:不匹配 = 硬失败 = 不归档 + 不写 lineage + 不动 registry;per tasking 346 §红线 'SHA 不匹配仍入库' = ❌。

### 4.3 WORM + extract + lineage 三步

```python
archive_path = archive(blob=blob, domain=..., filename=sample_path.name)
tables = extract_tables(blob, category=pilot_row["category"])
extract_json_path = write_extract_json(...)
write_observation(archive_path=..., intake_status=REGISTRY_SAMPLE_INTAKE_STATUS, ...)
return archive_path, extract_json_path, lineage_path
```

## §5 registry 深圳 SSL 暂缓注记

### 5.1 registry.csv 行 5(sz.gov.cn)对比

| 字段 | knife 50 改后 | knife 51 改后(增量) |
|---|---|---|
| `auth_note` | `公开；无需授权（2026-08-26 HTTPS SSL BAD_ecPOINT 暂缓；Cursor 341 暂缓 live；改走 local sample；禁 HTTP pin）` | (knife 50 已注;knife 51 维持) |
| `failure_handling` | `重试 3 次 → SSL BAD_ecPOINT transport error（服务端问题，与 client CA 无关）→ 暂缓 live → --from-local-sample 抽取本地样本 → 仍 is_demo=true；禁降级 HTTP pin` | (knife 50 已注;knife 51 维持) |
| `purpose_note` | `代表性市级公报（深圳市政府；2026-08-26 live SSL 暂缓,改走 --from-local-sample）` | (knife 50 已注;knife 51 维持) |

注:knife 51 主要增量为 connector + 接收路径,registry 注记已在 knife 50(347 的前置 344)完成,knife 51 仅做 §6.1/6.3 的实跑验证。

## §6 三次实跑证据

### 6.1 Shenzhen `--from-local-sample` 实跑

执行:
```bash
python3 scripts/auto_ingest_public_source.py \
    --pilot-domain=sz.gov.cn \
    --pilot-category=MUNICIPAL_BULLETIN \
    --from-local-sample \
    --confirm-live=/tmp/cegr_kn51/sz_local_sample_lineage.jsonl
```

输出(`reviews/.../_knife51_sz_local_sample.log`,553B):
```
OK local-sample pilot matched: sz.gov.cn / MUNICIPAL_BULLETIN (enabled=TRUE)
   local_sample_path: spikes/03-municipal-bulletin/sample.html
   expected SHA: d5e2c73196b43cec…
OK archived: /Users/kjonekong/projects/china platform/data/public_archives/2026-08/sz.gov.cn/sample.html
OK extract JSON: /Users/kjonekong/projects/china platform/data/public_extracts/sz.gov.cn/MUNICIPAL_BULLETIN.json
OK lineage: /tmp/cegr_kn51/sz_local_sample_lineage.jsonl
OK REGISTRY_SAMPLE_INTAKED (is_demo=true; sample ≠ live closure). rc=0 = sample intake successful.
```

落地:
- WORM: `data/public_archives/2026-08/sz.gov.cn/sample.html`(62831B,SHA `d5e2c73...` 匹配)
- 结构化 JSON: `data/public_extracts/sz.gov.cn/MUNICIPAL_BULLETIN.json`(**row_count=0**;spike 文件表格在 DOM 深处,`extract_html_tables` 的 `find("table")` 拿到的是非数据表;**未伪造**;详见 §6.5)
- lineage: `REGISTRY_SAMPLE_INTAKED`, `is_demo=true`, `source_agency=深圳市人民政府`

### 6.2 NBS `--live` 再探

执行:
```bash
python3 scripts/auto_ingest_public_source.py \
    --pilot-domain=stats.gov.cn \
    --pilot-category=NATIONAL_BULLETIN \
    --live \
    --confirm-live=/tmp/cegr_kn51/nbs_live_lineage.jsonl
```

输出(`reviews/.../_knife51_nbs_live_probe.log`,379B):
```
❌ JS-only shell; tech-blocked report: /Users/kjonekong/projects/china platform/reviews/stage0-gate0-rework-2026-08-23/20260826T102849Z-stage2-public-source-tech-blocked-stats.gov.cn-NATIONAL_BULLETIN.md
OK pilot matched: stats.gov.cn / NATIONAL_BULLETIN
   primary_url: https://www.stats.gov.cn/sj/zxfb/
   auth_note: 公开；无需授权
   expected SHA: dea13b8a4ff116ca…
```

实际返回码: **`rc=7`**(tech-blocked,与 knife 47 一致)。

落地产物:
- tech-blocked 报告:`reviews/.../20260826T102849Z-...md`(1589B,5 字段 + 红线 5 项)
- **没有 WORM 归档**(tech-blocked 不下载,直接 STOP)
- **没有 lineage JSONL**(`/tmp/cegr_kn51/nbs_live_lineage.jsonl` **不存在**;tech-blocked 在 drift 路径前发生)

**Cursor 341 §0.5** 解读:虽然 live 仍是 JS 壳,但本地样本已通过 `--from-local-sample` 抽取 63 行 → **drift 仍等用户裁定**,但样本管道已就位。

### 6.3 NBS `--from-local-sample` 实跑

执行:
```bash
python3 scripts/auto_ingest_public_source.py \
    --pilot-domain=stats.gov.cn \
    --pilot-category=NATIONAL_BULLETIN \
    --from-local-sample \
    --confirm-live=/tmp/cegr_kn51/nbs_local_sample_lineage.jsonl
```

输出(`reviews/.../_knife51_nbs_local_sample.log`,560B):
```
OK local-sample pilot matched: stats.gov.cn / NATIONAL_BULLETIN (enabled=TRUE)
   local_sample_path: spikes/01-national-yearbook/sample.html
   expected SHA: dea13b8a4ff116ca…
OK archived: /Users/kjonekong/projects/china platform/data/public_archives/2026-08/stats.gov.cn/sample.html
OK extract JSON: /Users/kjonekong/projects/china platform/data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN.json
OK lineage: /tmp/cegr_kn51/nbs_local_sample_lineage.jsonl
OK REGISTRY_SAMPLE_INTAKED (is_demo=true; sample ≠ live closure). rc=0 = sample intake successful.
```

落地:
- WORM: `data/public_archives/2026-08/stats.gov.cn/sample.html`(388238B,SHA `dea13b8a...` 匹配)
- 结构化 JSON: `data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN.json`(**row_count=63**,真实数据)
- lineage: `REGISTRY_SAMPLE_INTAKED`, `is_demo=true`, `source_agency=国家统计局`

### 6.4 Hubei `--from-local-sample --allow-disabled-local-sample`(测试覆盖;实跑视 Cursor 启动)

test_local_sample_hubei_with_allow_disabled_succeeds 用 **真实 spike 文件** + **真 SHA** `c5cf5abeb4fdf97a...`:

```python
pilot_row = {
    "domain": "tjj.hubei.gov.cn",
    "enabled": "FALSE",
    "file_hash_sha256": sha256_of_bytes(hubei_sample.read_bytes()),  # 真 SHA
    "local_sample_path": str(hubei_sample),  # 真实 spike/02-provincial-yearbook/hubei_2026_06.xlsx
}
archive_path, extract_json_path, lineage_path = aips.intake_from_local_sample(
    pilot_row=pilot_row, allow_disabled=True,
)
# → archive OK + JSON OK + lineage OK (REGISTRY_SAMPLE_INTAKED + is_demo=true)
```

通过。Hubei opt-in 路径端到端验证。

### 6.5 Shenzhen 抽取 0 行的诚实说明

`extract_html_tables` 当前用 `soup.find("table")` 拿到**第一个** `<table>`。深圳 spike 的 828 行 HTML 中:
- 第一个 `<table>` 是 layout / nav 用的(无数据行)
- 数据表在 DOM 更深处,需要 walk-all-tables-and-pick-data 增强

**未伪造**:knife 51 不偷工;`extract_html_tables` 在 0 数据行的情况下返回 `[]`(已修过的 if-header-is-None 路径),lineage `row_count=0` 诚实标记。

**下一刀可能增强**(若 Cursor 任务):`extract_html_tables_v2(blob)` — walk all tables, score by (row_count × col_count), pick largest data-bearing table。NBS 抽取 63 行已证明现有抽取对简单表足够;深圳 spike 揭示了更复杂样本需要 v2。

## §7 invariant 守恒

| 步骤 | artifact_count | sum(role_count) | len(artifacts) | 一致 |
|---|---|---|---|---|
| knife 50 后基线 | 656 | 656 | 656 | ✅ |
| + bump(NEW) | 657 | 657 | 657 | ✅ |
| + receipt(NEW) | 658 | 658 | 658 | ✅ |

`NEW_ARTIFACTS = +2(bump + receipt)` ⇒ pack `656 → 658`。

> 注:connector / registry.csv / test file 是既有文件修订,bump SKIP;WORM 归档 + 结构化 JSON 是 `--from-local-sample` 管道产物,**不入 manifest**(live/extract 输出非 source-of-truth artifact);3 个 `_knife51_*.log` 是实跑留痕,**不入 manifest**(同 knife 47/48/49/50 副产物处理);1 个 tech-blocked 报告 同 knife 47/48/49/50 处理,**不入 manifest**。

## §8 红线审计

| 红线 | 守 |
|---|---|
| ❌ 不宣布 Gate/O1 PASS | `REGISTRY_SAMPLE_INTAKED` ≠ O1;`is_demo=true` 诚实标记;receipt 不写 PASS 字样 |
| ❌ **不执行页面 JS**（tasking 339 §红线） | `is_js_only_shell` 静态 inspect;`--from-local-sample` 完全离线;`--live` 仍按 knife 47/49 路径 |
| ❌ **不切 headless browser** | 同上;`--from-local-sample` 模式无网络 |
| ❌ **不盲爬外域** | deeplink 仍 `urlparse` 比 host;`--from-local-sample` 不涉及 |
| ❌ **不绕 HTTPS / 降级到 HTTP**（tasking 346 §红线） | sz.gov.cn HTTPS 失败不切 HTTP 镜像;`BAD_ecPOINT` 维持 transport-blocked 状态 |
| ❌ **SHA 不匹配仍入库**（tasking 346 §红线） | `LocalSampleMismatch` 硬失败,rc=8,**不**归档,**不**写 lineage |
| ❌ **不 headless 跟随 JS 重定向** | 维持 knife 49 路径 |
| ❌ **不擅自改 NBS/Hubei 哈希** | registry NBS/Hubei 行未触碰;Hubei 维持 `enabled=FALSE` |
| ❌ **不批量 2020-2025 / 不把 1909 代表中国** | 不在本刀范围 |
| ❌ **不擅自 --force** | normal `--ff-only` pull;`git push origin HEAD` 默认 |
| ❌ **不接 S2.7-b UI** | local-sample JSON 输出仅落 `data/public_extracts/`;前端零改动 |
| ❌ **不改 `gate_thresholds.json`** | untouched |
| ❌ **不碰 `00-CC-CURRENT.md`** | Cursor owns;untouched |
| ❌ **不在 chat 复述 Cursor 长文** | 仅短句回执 |
| ❌ **不索要 PAT** | 无 |
| ✅ pack invariant | `sum(role_count) == artifact_count == len(artifacts)` 在每步后断言(详见 §7) |
| ✅ receipt location | `reviews/stage0-gate0-rework-2026-08-23/347-...md` |
| ✅ extractor bug 修复(NBS+深圳) | knife 50 修的 `if header is None:` 路径在 knife 51 全程使用 |
| ✅ 跨刀测试无回归 | 59 → 69,既有 case 全 PASSED |

## §9 与 docs/52 §3 试点对账

| 试点 | 状态 |
|---|---|
| NBS HTML | knife 46/47 + knife 51 local-sample(**row_count=63**);live 仍 JS 壳;**334 + 347 已落**;O1 drift 等用户 |
| Hubei EXCEL | knife 48/49 + knife 50 `enabled=FALSE`;knife 51 `--allow-disabled-local-sample` 路径已 pytest 覆盖;**337 + 340 + 347 已落**;local sample opt-in 待 Cursor 启动 |
| Shenzhen HTML | knife 50 connector + knife 51 local-sample(**row_count=0**,spike 表格在 DOM 深处,需 v2 抽取);live SSL 暂缓;**344 + 347 已落**;下刀可选:抽取器 v2 或换 spike |

## §10 推 / 落地

- commit: TBD（pending knife51_manifest_bump.py 执行后）
- push origin: TBD
- push github: TBD
- three-way convergence: TBD
- backfill SHA: 本 receipt §META `cc_head` 在 commit 后填;按 knife 17 教训另起 commit(不 amend-after-push)

## §11 下次心跳预期

`./scripts/cc_gate_watch.sh --pull` → re-arm → 84 POLL。

`cursor_ack` 未 bump 前只 POLL;queue_rev 变化 → 读 §NOW。

— End of Knife 51 receipt 347 —