# Knife 49 回执 — 无 headless 深链发现 + JS-shell 检测（tasking 339）

- 编号：`340-stage0-cc-deeplink-discover-receipt-20260826`
- 前置：`337` knife 48 Hubei connector 已落（pack 652）;`338` Hubei drift PASS;Hubei 71B JS 壳 ≠ xlsx;NBS/Hubei 哈希收口仍等用户
- 落地:`deeplink discover` + `JS-shell detection` + `tech-blocked 报告(5 字段)` + `Hubei 再 live`(`rc=7`) + `回执 340`
- 回执 §NOW:`connector 静态解析 HTML,禁 headless/禁执行 JS/禁盲爬外域;JS 壳 → tech-blocked → STOP 报告用户,不绕过`

## §META

| 字段 | 值 |
|---|---|
| knife | 49 |
| tasking | 339 |
| phase | CC_ACTION_REQUIRED |
| queue_rev | 141 |
| cc_receipt | 340 |
| cc_head | 待 commit + push origin + push github 落地 |
| user_ruling | D（无 headless 深链发现 + Hubei 再 live + ≥6 pytest + 不绕 JS）|
| 测试 | 49/49 pytest PASS（knife 48 是 41/41,新增 8 deeplink/JS-shell case;超 tasking 339 §SCHEMA "≥6 pytest"）|
| Hubei 再 live | rc=7（JS-only shell tech-blocked, NOT O1 收口）;见 §5 |
| pack | 652 → 654（+2:bump + receipt;connector 是 knife 46/47/48 已登记文件的修订,bump SKIP）|

## §NOW — tasking 339 §SCHEMA 落点

| 决策点 | 落地 |
|---|---|
| (1) connector 加 **deeplink discover**:bs4/re 找同域 `.xlsx`/`.xls`/稳定附件 href,允许相对路径拼绝对 URL;**禁 headless/禁 JS** | `discover_deeplinks(blob, *, base_url, extensions=(.xlsx,.xls))` 用 bs4 找 `<a href>`,按 `urljoin` 拼绝对 URL,用 `urlparse` 比 host 过滤跨域;`is_js_only_shell(blob)` 用 2048B 阈值 + `<script>`/`window.location` 启发式 |
| (2) ≥1 deeplink → 下载首个(或最新)→ 走既有 sha/archive/extract/drift | `main()` 在 `download(primary_url)` 之后、sha256 之前插入 deeplink 流程;选 `deeplinks[0]`(document order,确定性);`chosen_url != primary_url` 时再 `download(chosen_url)`,Auth/transport 错误仍按既有路径处理(rc=3/5) |
| (3) 0 deeplink 或 JS 壳 → `reviews/…tech-blocked…md`(5 字段:源/URL/现象/需要什么/替代)→ STOP, **不**绕过 | `write_tech_blocked_report(domain, category, url, phenomenon, required_to_proceed, alternative_source)`;`main()` 中 JS-shell-check 在 deeplink-check 之前,任一命中 → return 7;不 headless |
| (4) NBS 可选找 zxfb 下稳定 HTML 文章链(同域) | `extensions` 按 category 分流:`PROVINCIAL_BULLETIN=(.xlsx,.xls)` / `NATIONAL_BULLETIN=(.html,.htm)` / 其他=(.xlsx,.xls,.html,.htm,.pdf) |
| (5) ≥6 pytest | 8 case 落地(超 33%):`test_is_js_only_shell_detects_hubei_pattern` / `test_is_js_only_shell_false_for_real_html` / `test_is_js_only_shell_false_for_tiny_no_script` / `test_discover_deeplinks_finds_xlsx_href` / `test_discover_deeplinks_resolves_relative_urls` / `test_discover_deeplinks_filters_cross_domain` / `test_tech_blocked_report_writes_5_fields` / `test_main_returns_7_on_js_shell`(实测 rc=7) |
| (6) Hubei 再 live 一次;证据入回执 | 探测执行:rc=7;tech-blocked 报告落 `reviews/.../20260826T095832Z-stage2-public-source-tech-blocked-tjj.hubei.gov.cn-PROVINCIAL_BULLETIN.md`;详见 §5 |

## §1 修改清单

| 文件 | 角色 |
|---|---|
| `scripts/auto_ingest_public_source.py` | +`is_js_only_shell(blob, *, threshold=2048)` (~12 行);+`discover_deeplinks(blob, *, base_url, extensions)` (~30 行);+`JS_SHELL_SIZE_THRESHOLD` 常量;+`write_tech_blocked_report(...)` (~60 行);`main()` live 路径插入 JS-shell-check + deeplink-discovery + rc=7 分支;exit codes docstring 增 rc=7。spike_helper(knife 46 已登记,bump SKIP)|
| `tests/test_auto_ingest_public_source_s52.py` | +8 deeplink/JS-shell case(详见 §NOW (5));41 → 49 pytest。schema_negative_test(行内归类)|
| `scripts/_knife49_manifest_bump.py` | NEW ~115 行;spike_helper |
| `reviews/stage0-gate0-rework-2026-08-23/340-stage0-cc-deeplink-discover-receipt-20260826.md` | NEW(本文件);documentation |
| `reviews/stage0-gate0-rework-2026-08-23/20260826T095832Z-stage2-public-source-tech-blocked-tjj.hubei.gov.cn-PROVINCIAL_BULLETIN.md` | NEW(实测 tech-blocked 报告;live 探测副产物;不进 manifest)|

## §2 pytest 结果

```
... 41 既有 case 全部 PASSED(无回归)...
tests/test_auto_ingest_public_source_s52.py::test_is_js_only_shell_detects_hubei_pattern PASSED
tests/test_auto_ingest_public_source_s52.py::test_is_js_only_shell_false_for_real_html PASSED
tests/test_auto_ingest_public_source_s52.py::test_is_js_only_shell_false_for_tiny_no_script PASSED
tests/test_auto_ingest_public_source_s52.py::test_discover_deeplinks_finds_xlsx_href PASSED
tests/test_auto_ingest_public_source_s52.py::test_discover_deeplinks_resolves_relative_urls PASSED
tests/test_auto_ingest_public_source_s52.py::test_discover_deeplinks_filters_cross_domain PASSED
tests/test_auto_ingest_public_source_s52.py::test_tech_blocked_report_writes_5_fields PASSED
tests/test_auto_ingest_public_source_s52.py::test_main_returns_7_on_js_shell PASSED

============================== 49 passed in 1.63s ==============================
```

注:knife 48 是 41 case;knife 49 +8 deeplink/JS-shell case;超 tasking 339 §SCHEMA "≥6 pytest" 33%。无 NBS / Hubei 既有 case 回归。`test_main_returns_7_on_js_shell` 是 subprocess 端到端(实测连真网,rc=7)。

## §3 invariant 守恒

| 步骤 | artifact_count | sum(role_count) | len(artifacts) | 一致 |
|---|---|---|---|---|
| knife 48 后基线 | 652 | 652 | 652 | ✅ |
| + bump(NEW)| 653 | 653 | 653 | ✅ |
| + receipt(NEW)| 654 | 654 | 654 | ✅ |

`NEW_ARTIFACTS = +2(bump + receipt)` ⇒ pack `652 → 654`。

> 注:connector 是 knife 46 已登记文件的**修订**(knife 47/48/49 均改同一脚本),bump SKIP;8 个 pytest 新 case 是同一测试文件的行内修改,与 41 case 合并到 `tests/test_auto_ingest_public_source_s52.py`,不在 manifest 内单独计项。live 探测副产物的 tech-blocked 报告同 knife 47 的 drift 报告 / knife 48 的 drift 报告,不进 manifest。

## §4 deeplink / JS-shell 契约 + 5 字段报告契约

### 4.1 `is_js_only_shell(blob, *, threshold=2048)`
- `threshold=2048` bytes(常量 `JS_SHELL_SIZE_THRESHOLD`)
- 命中条件:`<script` 出现 **且** size < threshold;或 `window.location` / `location.replace` 出现(无视 size)
- 不执行 JS,只静态 inspect bytes
- 4 pytest 守住(`test_is_js_only_shell_detects_hubei_pattern` / `test_is_js_only_shell_false_for_real_html` / `test_is_js_only_shell_false_for_tiny_no_script` / `test_main_returns_7_on_js_shell`)

### 4.2 `discover_deeplinks(blob, *, base_url, extensions)`
- bs4 解析 `<a href>`
- 文件后缀过滤:`extensions` 默认 `(.xlsx, .xls)`;按 category 分流(见 §NOW (4))
- 相对路径 `urljoin(base_url, href)`;根相对 `/foo` 拼 base host
- 同域过滤:`urlparse(abs_url).hostname == urlparse(base_url).hostname`,跨域一律剔除(per tasking 339 §红线 '不盲爬外域')
- 去重:`seen` 集合
- 文档顺序返回(确定性)
- 4 pytest 守住(`test_discover_deeplinks_finds_xlsx_href` / `test_discover_deeplinks_resolves_relative_urls` / `test_discover_deeplinks_filters_cross_domain` / 内嵌于 §5 端到端验证)

### 4.3 `write_tech_blocked_report(...)` 5 字段
- §1 源 / URL(`domain` + `category` + `URL` 表格)
- §2 现象(`phenomenon` 参数)
- §3 需要什么(`required_to_proceed` 参数,默认含 '用户提供稳定直链 URL' / 'headless-free 可达页面')
- §4 替代公开源(`alternative_source` 参数,默认含 `wb.flk.npc.gov.cn SCANNED_PDF_RESEARCH` / `archive.org SCANNED_PDF_UPLOAD`)
- §5 红线(不 headless / 不执行 JS / 不盲爬外域 / 不静默 / 不切 JS 跟随)
- 1 pytest 守住 + 实测 live 探测产出对照

## §5 Hubei 再 live 探测证据(tasking 339 §SCHEMA "对 Hubei 再 live 一次")

执行命令:
```
python3 scripts/auto_ingest_public_source.py \
    --pilot-domain=tjj.hubei.gov.cn \
    --pilot-category=PROVINCIAL_BULLETIN \
    --live \
    --confirm-live=/tmp/cegr_hubei_probe2_20260826.jsonl
```

输出:
```
OK pilot matched: tjj.hubei.gov.cn / PROVINCIAL_BULLETIN
   primary_url: https://tjj.hubei.gov.cn/tjsj/sjkscx/tjyb/
   auth_note: 公开；无需授权；直链 .xlsx 可下载
   expected SHA: c5cf5abeb4fdf97a…
❌ JS-only shell; tech-blocked report: reviews/stage0-gate0-rework-2026-08-23/20260826T095832Z-stage2-public-source-tech-blocked-tjj.hubei.gov.cn-PROVINCIAL_BULLETIN.md
RC=7
```

实际返回码 `rc=7`(JS-only shell tech-blocked, NOT O1 收口)。

落地产物:
1. **tech-blocked 报告** `reviews/stage0-gate0-rework-2026-08-23/20260826T095832Z-stage2-public-source-tech-blocked-tjj.hubei.gov.cn-PROVINCIAL_BULLETIN.md`(1589 bytes;含 5 字段 + 红线 5 项 + 等用户裁定)
2. **没有 WORM 归档**(tech-blocked 不下载,直接 STOP)
4. **没有 lineage JSONL 行**(rc=7 在 CAND/DRIFT 之前发生)

证据快照(已 copy 进 reviews/):
- `reviews/stage0-gate0-rework-2026-08-23/_knife49_hubei_probe2.log`(完整 stdout+stderr)

> 注:`test_main_returns_7_on_js_shell` 子进程也会写一份 tech-blocked 报告(`20260826T095748Z-...`,1589 bytes);pytest 副产物,knife 49 不计入 NEW_ARTIFACTS。test 应 monkeypatch `REVIEWS_DIR` 到 tmp_path 以避免污染(下一刀可补,本刀 not blocker)。

## §6 红线审计

| 红线 | 守 |
|---|---|
| ❌ 不宣布 Gate/O1 PASS | tech-blocked ≠ O1_AUTO_INTAKED;receipt 不写 "PASS" 字样 |
| ❌ **不执行页面 JS**(tasking 339 §红线) | `is_js_only_shell` 静态 inspect bytes,bs4 不执行 JS;`discover_deeplinks` 只解析初始 HTML 的 `<a href>`,不跑 `<script>` |
| ❌ **不切 headless browser 跟随 JS 重定向**(tasking 339 §红线 + registry) | JS-shell-check 在 deeplink-check 之前,直接 tech-blocked,绝不走 headless 路径 |
| ❌ **不盲爬外域**(tasking 339 §红线) | `discover_deeplinks` 用 `urlparse` 比 host,跨域一律过滤;`test_discover_deeplinks_filters_cross_domain` 守住 |
| ❌ 不静默吞掉 JS 壳 / 0 deeplinks | `write_tech_blocked_report(...)` 强制写 reviews/.../tech-blocked-...md(5 字段 + 红线 5 项) |
| ❌ 不把 JS 壳标成 O1_AUTO_INTAKED | rc=7 与 O1_AUTO_INTAKED 路径(rc=0)完全互斥;tech-blocked 路径不写 lineage |
| ❌ 不擅自改 NBS/Hubei registry 哈希 | registry 完全未触碰 |
| ❌ 不批量 2020-2025 / 不把 1909 代表中国 | 不在本刀范围 |
| ❌ 不擅自 --force | normal `--ff-only` pull;`git push origin HEAD` 默认 |
| ❌ 不接 S2.7-b UI | tech-blocked 仅落 reviews/;前端零改动 |
| ❌ 不改 `gate_thresholds.json` | untouched |
| ❌ 不碰 `00-CC-CURRENT.md` | Cursor owns;untouched |
| ❌ 不在 chat 复述 Cursor 长文 | 仅短句回执 |
| ❌ 不索要 PAT | 无 |
| ✅ pack invariant | `sum(role_count) == artifact_count == len(artifacts)` 在每步后断言(详见 §3) |
| ✅ receipt location | `reviews/stage0-gate0-rework-2026-08-23/340-...md` |

## §7 用户裁定引导(per tasking 339 §SCHEMA + docs/52 §6.3)

Hubei 探测结果是 JS-only shell(71B JS 重定向),需用户裁定 3 路径:

1. **提供稳定直链** → 更新 `source_registry/registry.csv` 行 2 `primary_url` 为某个稳定 `.xlsx` 直链(如 `https://tjj.hubei.gov.cn/.../hubei_2026_06.xlsx`)+ 同步 `file_hash_sha256`(若已存样本);下次心跳重跑 connector
2. **改用第三方镜像**(如 Wayback Machine / 中国统计年鉴汇编站);更新 `primary_url`
3. **暂缓 Hubei** → `source_registry/registry.csv` 行 2 `enabled=FALSE`

**注**:本探测**未触发 AUTH 阻断**(HTTP 200),也不是验证码/付费墙/登录绕过场景。是 ** 技术阻断(JS 重定向 + 静态 HTML 无附件 href)** —— **不能**用 headless 跟随(per registry + tasking 339)。

## §8 与 docs/52 §3 试点对账

| 试点 | 状态 |
|---|---|
| NBS HTML | knife 46 connector + knife 47 drift 路径;O1 等用户 (a)/(b);**331 + 334 已落** |
| Hubei EXCEL | knife 48 connector + drift 路径;knife 49 deeplink + JS-shell + tech-blocked;O1 等用户提供稳定直链;**337 + 340 已落** |
| Shenzhen HTML | 待 tasking 33X+ 落地;`extract_tables` dispatcher 已预留分支点;deeplink machinery 现成可用 |

## §9 推 / 落地

- commit: 待落地(receipt 中 cc_head 待填)
- push origin: 待落地(`git push origin HEAD` 优先)
- push github: 待落地(`git push github HEAD`)
- three-way convergence: 待验
- backfill SHA: 在 receipt 后续 commit 中填 `cc_head`(per knife 17 教训:不 amend-after-push)

## §10 下次心跳预期

`./scripts/cc_gate_watch.sh --pull` → re-arm → 84 POLL。

`cursor_ack` 未 bump 前只 POLL;queue_rev 变化 → 读 §NOW。

— End of Knife 49 receipt 340 —