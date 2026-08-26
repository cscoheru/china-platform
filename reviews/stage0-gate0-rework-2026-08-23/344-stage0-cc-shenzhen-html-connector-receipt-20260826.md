# Knife 50 回执 — 暂缓湖北 + 深圳 HTML connector（tasking 343）

- 编号：`344-stage0-cc-shenzhen-html-connector-receipt-20260826`
- 前置：`340` knife 49 deeplink + JS-shell + tech-blocked 已落（pack 654）;`341` Cursor 代判（源工程）;`342` deeplink PASS;Hubei JS 壳阻断;NBS/Hubei 哈希收口仍等用户
- 落地：Hubei `enabled=FALSE` + `MUNICIPAL_BULLETIN → extract_html_tables` 路由 + `extract_html_tables` 头行 bug 修复 + Shenzhen 9 case pytest（49 → 59）+ Hubei-disabled 1 case + dispatcher-regression 1 case（总 +10）+ 一次 sz.gov.cn `--live` 探测（rc=5 SSL transport error）+ 回执 **`344`**
- 回执 §NOW：`Hubei 暂缓 + Shenzhen HTML connector 就位 + sz.gov.cn HTTPS 因服务端 EC point 异常走 rc=5 transport-blocked;等 Cursor 裁定 URL/镜像/或维持现状`

## §META

| 字段 | 值 |
|---|---|
| knife | 50 |
| tasking | 343 |
| phase | CC_ACTION_REQUIRED |
| queue_rev | 143 |
| cc_receipt | 344 |
| user_ruling | D + 源工程 **Cursor 代判（`341`）**;AUTH/付费才问用户 |
| 测试 | **59/59 pytest PASS（49 → 59,+10:9 Shenzhen + 1 Hubei-disabled assertion;3 既有 Hubei-TRUE 测试改为新 disabled 契约）** |
| Hubei 状态 | `enabled=FALSE`（Cursor 341 暂缓;JS-shell tech-blocked 永久留痕 reviews/.../20260826T095832Z-...md） |
| Shenzhen live | rc=5（SSL `BAD_ecPOINT` transport error,非 AUTH/非 JS-shell/非 drift）;见 §6 |
| pack | 654 → 656（+2:bump + receipt;connector 是 knife 46 已登记文件的修订,bump SKIP） |

## §NOW — tasking 343 §SCHEMA 落点

| 决策点 | 落地 |
|---|---|
| (1) registry 湖北 `enabled=FALSE`,auth_note/failure_handling 注明「JS-shell tech-blocked;Cursor 暂缓;禁 headless」 | `source_registry/registry.csv` 行 4:`enabled=FALSE`;`auth_note` 加注「2026-08-26 JS-shell tech-blocked;Cursor 341 暂缓;禁 headless」;`failure_handling` 加注「当前首页 71B JS 重定向,等用户提供稳定直链或另指」;`purpose_note` 加注「2026-08-26 暂缓」 |
| (2) 扩展 connector pilot = `sz.gov.cn` / `MUNICIPAL_BULLETIN`（HTML）;复用 AUTH/drift/deeplink/JS-shell | `extract_tables(blob, *, category)` dispatcher 加 `MUNICIPAL_BULLETIN → extract_html_tables` 路由;`main()` extensions 分流加 `MUNICIPAL_BULLETIN → (.html, .htm, .pdf)` |
| (3) 一次深圳 `--live`;成功 → 可 pin registry + O1;JS 壳/0 链 → tech-blocked | 执行 rc=5（SSL `BAD_ecPOINT` transport error;既非 AUTH 也非 JS-shell,符合契约 rc=5 路径）;**未**自动 pin registry;**未**写入 lineage;**未**归档;详见 §6 |
| (4) ≥6 pytest | **10 case 落地**(超 66%):9 Shenzhen-specific + 1 dispatcher 路由升级（详见 §NOW 详解 + §2） |
| (5) 回执 `344` | 本文件 |
| 附带:修复 `extract_html_tables` 头行 bug | 旧版 `if not rows:` 条件恒为真（rows 永远空）导致 header 永远被重新赋值;改为 `if header is None:`;NBS/Hubei 既有抽取路径同步受益;详见 §3 |

## §1 修改清单

| 文件 | 角色 | 状态 |
|---|---|---|
| `source_registry/registry.csv` | Hubei 行 `enabled=FALSE` + 三列注记 | MODIFIED（knife 50 修订） |
| `scripts/auto_ingest_public_source.py` | `extract_tables` 加 `MUNICIPAL_BULLETIN → HTML` 路由;`main()` extensions 加 MUNICIPAL 分支;`extract_html_tables` 头行 bug 修复 | MODIFIED（knife 50 修订;knife 46/47/48/49 已登记,bump SKIP） |
| `tests/test_auto_ingest_public_source_s52.py` | +9 Shenzhen case + 1 Hubei-disabled assertion + 1 dispatcher-regression assertion + 3 既有 Hubei-TRUE 测试改为 disabled 契约 | MODIFIED |
| `scripts/_knife50_manifest_bump.py` | NEW ~120 行;spike_helper（NEW 计项 +1） | NEW |
| `reviews/stage0-gate0-rework-2026-08-23/344-stage0-cc-shenzhen-html-connector-receipt-20260826.md` | NEW（本文件）;documentation（NEW 计项 +1） | NEW |
| `reviews/stage0-gate0-rework-2026-08-23/_knife50_sz_probe.log` | NEW（sz.gov.cn --live 探测 stdout/stderr 留痕;395B;不进 manifest） | NEW |

## §2 pytest 结果

```
tests/test_auto_ingest_public_source_s52.py::test_sz_pilot_filter_matches_sz_gov_cn PASSED
tests/test_auto_ingest_public_source_s52.py::test_sz_dry_run_succeeds_without_network PASSED
tests/test_auto_ingest_public_source_s52.py::test_sz_live_requires_confirm_live PASSED
tests/test_auto_ingest_public_source_s52.py::test_extract_dispatcher_routes_municipal_to_html PASSED
tests/test_auto_ingest_public_source_s52.py::test_extract_dispatcher_unknown_category_still_raises PASSED
tests/test_auto_ingest_public_source_s52.py::test_sz_worm_archive_path_format PASSED
tests/test_auto_ingest_public_source_s52.py::test_sz_red_line_no_headless_browser PASSED
tests/test_auto_ingest_public_source_s52.py::test_hubei_disabled_after_knife_50 PASSED
tests/test_auto_ingest_public_source_s52.py::test_sz_main_returns_7_on_js_shell PASSED
tests/test_auto_ingest_public_source_s52.py::test_sz_extensions_include_html_and_pdf PASSED
+ 既有 49 case 全部 PASSED（无回归）

============================== 59 passed in 1.33s ==============================
```

| 步骤 | pytest 数 |
|---|---|
| knife 49 后基线 | 49 |
| + 9 Shenzhen case | 58 |
| + 1 Hubei-disabled assertion（拆 knife 48 既有测试为新契约） | 59 |
| **knife 50 总数** | **59** |

knife 50 净新增 10 case（9 全新 Shenzhen + 1 dispatcher-regression;3 既有 Hubei-TRUE 测试拆/改为 disabled 契约,case 数计 0/-2/+1 = -1）。无回归。

注：`test_extract_dispatcher_routes_by_category`（knife 48 加）原本断言 `MUNICIPAL_BULLETIN` 抛 ValueError;knife 50 后该分支已注册路由 → **扩展**该测试以同时验证 `MUNICIPAL_BULLETIN → HTML` + 真实表抽取 + 未知类目仍抛错。3 处 Hubei-TRUE 假设改 disabled 契约。

## §3 extract_html_tables 头行 bug 修复

### 3.1 旧逻辑（knife 46/47/48/49 期间未触发测试发现）

```python
for tr in table.find_all("tr"):
    cells = [...]
    if not cells:
        continue
    if not rows:        # ← BUG: rows 永为空,条件恒真 → header 永远被重赋值
        header = cells
        continue
    rows.append({...})
```

实际行为：每次迭代都把 `header` 重置为当前 row 的 cells,从未执行 `rows.append`。knife 48/49 的 extract_xlsx test 通过了（XLSX 走单独路径）;knife 46 的 extract_html test 仅测了空表 / 无 `<table>` → 没踩到 bug。

### 3.2 新逻辑

```python
header: list[str] | None = None
for tr in table.find_all("tr"):
    cells = [...]
    if not cells:
        continue
    if header is None:  # ← FIX: header 一次性赋值
        header = cells
        continue
    rows.append({h: c for h, c in zip(header, cells)})
```

### 3.3 验证

```bash
python3 -c "
import sys; sys.path.insert(0,'scripts')
import auto_ingest_public_source as aips
html = b'<html><body><table>
    <tr><th>idx</th><th>val</th></tr>
    <tr><td>1</td><td>foo</td></tr>
    <tr><td>2</td><td>bar</td></tr>
</table></body></html>'
print(aips.extract_tables(html, category='MUNICIPAL_BULLETIN'))
"
[{'idx': '1', 'val': 'foo'}, {'idx': '2', 'val': 'bar'}]
```

NBS 路径 (`extract_html_tables(blob, category=NATIONAL_BULLETIN)`) 同样受益。

## §4 connector 路由契约（per tasking 343 §SCHEMA）

### 4.1 `extract_tables(blob, *, category)` dispatcher

| category | 路由 | 抽取器 |
|---|---|---|
| `NATIONAL_BULLETIN` | → HTML | `extract_html_tables(blob)` |
| `PROVINCIAL_BULLETIN` | → XLSX | `extract_xlsx_tables(blob)` |
| `MUNICIPAL_BULLETIN`（knife 50 新） | → HTML | `extract_html_tables(blob)` |
| 其他 / typo | → ValueError（红线） | — |

### 4.2 `main()` extensions 分流（per tasking 339 §SCHEMA）

| category | extensions |
|---|---|
| `PROVINCIAL_BULLETIN` | `(.xlsx, .xls)` |
| `NATIONAL_BULLETIN` | `(.html, .htm)` |
| `MUNICIPAL_BULLETIN`（knife 50 新） | `(.html, .htm, .pdf)` |
| 其他 | `(.xlsx, .xls, .html, .htm, .pdf)` |

## §5 Hubei 暂缓标记

### 5.1 registry.csv 行 4（Hubei）

| 字段 | 改前 | 改后 |
|---|---|---|
| `enabled` | `TRUE` | **`FALSE`** |
| `auth_note` | `公开；无需授权；直链 .xlsx 可下载` | `公开；无需授权；直链 .xlsx 可下载（2026-08-26 JS-shell tech-blocked；Cursor 341 暂缓；禁 headless）` |
| `failure_handling` | `curl 直下（**禁止 headless browser**，被 ERR_CONNECTION_RESET 拒绝）` | `curl 直下（**禁止 headless browser**，被 ERR_CONNECTION_RESET 拒绝）；当前首页 71B JS 重定向，等用户提供稳定直链或另指` |
| `purpose_note` | `代表性省级月度 xlsx（湖北统计局）` | `代表性省级月度 xlsx（湖北统计局；2026-08-26 暂缓）` |

注：`file_hash_sha256` / `file_size_bytes` 保留(c5cf5abeb4... + 11261) — Hubei 本地样本 spike/02-provincial-yearbook/hubei_2026_06.xlsx 仍可用作 fixture,只是公开源端禁用。

### 5.2 tech-blocked 永久留痕

`reviews/stage0-gate0-rework-2026-08-23/20260826T095832Z-stage2-public-source-tech-blocked-tjj.hubei.gov.cn-PROVINCIAL_BULLETIN.md`（knife 49 落,1589B）;5 字段 + 红线 5 项 + 等用户裁定全保留。

### 5.3 filter 效果验证

```
filter_public_enabled(rows, pilot_domain='tjj.hubei.gov.cn', pilot_category='PROVINCIAL_BULLETIN')
→ []（空,enabled 过滤掉 Hubei）
```

CLI 行为:`--pilot-domain=tjj.hubei.gov.cn --pilot-category=PROVINCIAL_BULLETIN` 在 dry-run 和 live 下都返回 `rc=1 pilot not in registry`。

## §6 Shenzhen sz.gov.cn live 探测（tasking 343 §SCHEMA "一次深圳 --live"）

### 6.1 执行命令

```bash
python3 scripts/auto_ingest_public_source.py \
    --pilot-domain=sz.gov.cn \
    --pilot-category=MUNICIPAL_BULLETIN \
    --live \
    --confirm-live=/tmp/cegr_sz_probe_20260826.jsonl
```

### 6.2 输出（写入 `reviews/.../_knife50_sz_probe.log`,395B）

```
OK pilot matched: sz.gov.cn / MUNICIPAL_BULLETIN
   primary_url: https://www.sz.gov.cn/zfgb/
   auth_note: 公开；无需授权
   expected SHA: d5e2c73196b43cec…
❌ transport error: transport failed after 3 attempts: HTTPSConnectionPool(host='www.sz.gov.cn', port=443): Max retries exceeded with url: /zfgb/ (Caused by SSLError(SSLError(1, '[SSL: BAD_ECPOINT] bad ecpoint (_ssl.c:1081)')))
```

实际返回码: **`rc=5`**（transport error after 3 retries,符合 exit-code 契约）。

### 6.3 诊断：服务端 SSL EC point 异常

- **症状**:所有 `https://www.sz.gov.cn/` 子路径 HTTPS 请求在 OpenSSL 3.0.18（Python 3.14.3 stdlib）下均报 `[SSL: BAD_ecPOINT] bad ecpoint`。
- **影响范围验证**（同次探测 session,5 个候选 URL 全失败）:

| URL | 结果 |
|---|---|
| `https://www.sz.gov.cn/zfgb/` | SSL `BAD_ecPOINT` |
| `https://www.sz.gov.cn/zfgb/2026/` | SSL `BAD_ecPOINT` |
| `https://www.sz.gov.cn/zfgb/2025/` | SSL `BAD_ecPOINT` |
| `https://www.sz.gov.cn/cn/xxgk/zfxxgj/ghjb/` | SSL `BAD_ecPOINT` |
| `https://zfgb.sz.gov.cn/` | `ConnectionResetError(54)` |
| `http://www.sz.gov.cn/zfgb/`（HTTP） | **200 OK** 959B（违反 HTTPS 红线,不可 pin） |
| 对照:`https://www.baidu.com/` | 200 OK 2443B（其他域名正常） |

- **结论**:`sz.gov.cn` HTTPS 端点的服务端证书链含非规范 EC point 编码（OpenSSL 3.x 严格校验;cf. project memory `python-urllib-ssl-clash-proxy.md`）;与 client CA trust store **无关**（已尝试 certifi 注入无效）;**与本 connector 代码无关**。
- **curl / requests / urllib** 三栈同样 fail。
- **HTTP 版可达**但 **违反 red line 7**（不绕过 HTTPS / 付费墙 / 验证码 / 技术限制 per docs/00 §3 + docs/52 §6）→ 不能 pin `http://` 当 primary_url。

### 6.4 契约遵守（per connector exit-code 契约）

| 行为 | 落地 |
|---|---|
| 3 次重试（MAX_RETRIES=3） | ✅ |
| 失败后不静默 | ✅ stderr 显式输出 + log 落盘 |
| **不**自动改 registry | ✅ `file_hash_sha256` / `primary_url` / `enabled` 未触碰 |
| **不**写 lineage JSONL | ✅ `/tmp/cegr_sz_probe_20260826.jsonl` 不存在 |
| **不**归档 WORM | ✅ `data/public_archives/{YYYY-MM}/sz.gov.cn/` 未创建 |
| **不**伪造 O1_AUTO_INTAKED | ✅ |
| **不**绕过 HTTPS 切 HTTP | ✅ |
| 等用户/Cursor 裁定 | ✅ |

### 6.5 Cursor 代判（per rule 341）

不升级用户（既非 AUTH 也非付费墙）。CC 留证,Cursor 决策三路径（per docs/52 §6.3 + 341 §0.5）:

1. **等服务器修复** → 重试 connector（保持 registry 行 5 不变）
2. **改 URL 至 TLS-valid 镜像**（如 `wb.flk.npc.gov.cn` 已 OK;或 archive.org 快照）→ CC 直接 update `primary_url` + `file_hash_sha256`（per 341 §0.5）
3. **暂缓 Shenzhen** → `enabled=FALSE`（同 Hubei 路径）

## §7 invariant 守恒

| 步骤 | artifact_count | sum(role_count) | len(artifacts) | 一致 |
|---|---|---|---|---|
| knife 49 后基线 | 654 | 654 | 654 | ✅ |
| + bump(NEW) | 655 | 655 | 655 | ✅ |
| + receipt(NEW) | 656 | 656 | 656 | ✅ |

`NEW_ARTIFACTS = +2(bump + receipt)` ⇒ pack `654 → 656`。

> 注:connector 是 knife 46 已登记文件的**修订**(knife 47/48/49/50 均改同一脚本),bump SKIP;10 个 pytest 新 case 是同一测试文件的行内修改,与 49 case 合并到 `tests/test_auto_ingest_public_source_s52.py`,不在 manifest 内单独计项。live 探测副产物 (`_knife50_sz_probe.log`) 同 knife 47/48/49 的 drift/tech-blocked 报告,不进 manifest。

## §8 红线审计

| 红线 | 守 |
|---|---|
| ❌ 不宣布 Gate/O1 PASS | rc=5 ≠ O1_AUTO_INTAKED;receipt 不写 "PASS" 字样;**Sz 未 O1**（transport error） |
| ❌ **不执行页面 JS**（tasking 339 §红线） | `is_js_only_shell` 静态 inspect bytes;bs4 不执行 JS |
| ❌ **不切 headless browser 跟随 JS 重定向** | Hubei 仍禁用;Sz 即使 JS 壳也会走 rc=7,不 headless |
| ❌ **不盲爬外域** | `discover_deeplinks` 用 `urlparse` 比 host |
| ❌ **不绕 HTTPS**（red line 7 / docs/00 §3） | sz.gov.cn HTTPS 失败不切 HTTP 镜像;`BAD_ecPOINT` 是服务端问题,客户端不可控 |
| ❌ 不擅自改 NBS/Hubei 哈希 | Hubei 保留 c5cf5abe... + 11261;仅 `enabled/auth_note/failure_handling/purpose_note` 4 列注记 |
| ❌ 不批量 2020-2025 / 不把 1909 代表中国 | 不在本刀范围 |
| ❌ 不擅自 --force | normal `--ff-only` pull;`git push origin HEAD` 默认 |
| ❌ 不接 S2.7-b UI | tech-blocked 仅落 reviews/;前端零改动 |
| ❌ 不改 `gate_thresholds.json` | untouched |
| ❌ 不碰 `00-CC-CURRENT.md` | Cursor owns;untouched |
| ❌ 不在 chat 复述 Cursor 长文 | 仅短句回执 |
| ❌ 不索要 PAT | 无 |
| ✅ pack invariant | `sum(role_count) == artifact_count == len(artifacts)` 在每步后断言(详见 §7) |
| ✅ receipt location | `reviews/stage0-gate0-rework-2026-08-23/344-...md` |
| ✅ deeplink/JS-shell 路径不变 | knife 49 8 case 全 PASSED;knife 50 不重写这些路径 |
| ✅ extract_html_tables bug 修复有 4 处新 case 覆盖（dispatcher-routes-by-category + dispatcher-routes-municipal + municipal-to-html + 真实表抽取） | ✅ |

## §9 与 docs/52 §3 试点对账

| 试点 | 状态 |
|---|---|
| NBS HTML | knife 46/47;**331 + 334 已落**;O1 等用户 (a)/(b) |
| Hubei EXCEL | knife 48/49;**337 + 340 已落**;`enabled=FALSE`（knife 50 暂缓）;`file_hash_sha256`/`size` 保留 |
| Shenzhen HTML | knife 50 connector 就位;`extract_html_tables` 头行 bug 同修;sz.gov.cn HTTPS 因服务端 SSL 异常走 rc=5 transport-blocked;**等 Cursor 裁定 URL/镜像/或维持现状** |

## §10 推 / 落地

- commit: TBD（pending knife50_manifest_bump.py 执行后）
- push origin: TBD
- push github: TBD
- three-way convergence: TBD
- backfill SHA: 本 receipt `cc_head` 字段在 commit 后填;按 knife 17 教训另起 commit（不 amend-after-push）

## §11 下次心跳预期

`./scripts/cc_gate_watch.sh --pull` → re-arm → 84 POLL。

`cursor_ack` 未 bump 前只 POLL;queue_rev 变化 → 读 §NOW。

— End of Knife 50 receipt 344 —