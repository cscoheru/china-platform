# 356 — JS-shell 启发式收紧 + NBS live · CC 回执

- 编号：`356-stage0-cc-js-shell-nbs-live-receipt-20260826`
- 任务书：`355-stage2-js-shell-heuristic-nbs-live-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`<BACKFILL>`
- 日期：2026-08-26

---

## §NOW 对照

| 355 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) 仅小体积+脚本才判壳；大页放行 | ✅ `is_js_only_shell` 重写：`len(blob) < threshold` **且**（`<script` 或 `window.location`/`location.replace`）→ 壳；`len ≥ threshold` 一律 False。旧代码 `has_redirect → True` 无条件分支即 NBS 误判根因（388KB 索引页内嵌 redirect 片段被 rc=7） | `scripts/auto_ingest_public_source.py` |
| (2) 大页无 deeplink 且无 `<table>` → 另报「空内容」 | ✅ 新增 `is_empty_content_page()`；main() 0-deeplink 分支二分 phenomenon：空内容（大+无表）vs JS 渲染疑似（原有文本） | 同上 |
| (3) ≥4 pytest | ✅ **+5 case**（列表见下）；连跑 84 passed | `tests/test_auto_ingest_public_source_s52.py` |
| (4) 一次 NBS `--live`，成功/失败如实 | ✅ **过了壳门**（收紧生效的直接证据）：deeplink 发现 `202608/t20260821_1965093.html` → 435,469 bytes `sha=0b85212f…` → SHA drift（对 registry `dea13b8a…`）→ rc=4 drift 诚实处理 | 下文 §NBS live |
| (5) 回执 `356`（`-cc-` 名） | ✅ 本文件名 | — |

## 新增测试 5 case

1. `test_is_js_only_shell_false_for_large_page_with_redirect` — NBS 误判正主回归：大页 + `<script>` + `window.location` → False
2. `test_is_js_only_shell_small_redirect_without_script_tag_blocked` — 小体积 + 纯 redirect 标记（无 script 标签）仍拦
3. `test_is_js_only_shell_hubei_71b_still_blocked` — §SCHEMA (3) 指名回归：71B Hubei 壳仍拦（红线「小壳仍拦」「禁止把 71B 壳放行」）
4. `test_is_empty_content_page_classification` — 大无表 True / 大有表 False / 小无表 False
5. `test_main_reports_empty_content_not_js_shell` — in-process main()（monkeypatch `download` + `REVIEWS_DIR`→tmp）：大无表 0-deeplink → rc=7 + 报告含「空内容」且不含「JS-only shell」

```
$ python3 -m pytest tests/test_auto_ingest_public_source_s52.py \
    tests/test_public_extract_frontend_fixture.py -q
84 passed in 2.03s          # 79 + 5

$ git status --porcelain data/   # 测试后
（空）                            # 352 契约延续

$ python3 frontend/smoke-check.py
=== ... smoke: PASS ===
```

## NBS live 实录（一次，§SCHEMA 4）

```
$ python3 scripts/auto_ingest_public_source.py \
    --pilot-domain=stats.gov.cn --pilot-category=NATIONAL_BULLETIN \
    --live --confirm-live=/tmp/nbs_live_355.jsonl
OK pilot matched: stats.gov.cn / NATIONAL_BULLETIN
   primary_url: https://www.stats.gov.cn/sj/zxfb/
OK deeplink discovered: https://www.stats.gov.cn/sj/zxfb/202608/t20260821_1965093.html
OK downloaded 435469 bytes; sha256=0b85212f70055c38…
⚠ SHA drift; archived drifted bytes: data/public_archives/2026-08/stats.gov.cn/zxfb
⚠ drift report written: reviews/.../20260826T111011Z-stage2-public-source-sha-drift-stats.gov.cn-NATIONAL_BULLETIN.md
⚠ CANDIDATE_AUTO lineage emitted; rc=4
```

- **收紧前此路径 rc=7**（JS 壳误判）；收紧后直达 deeplink→下载→SHA——启发式修复的直接端到端证据。
- rc=4 = drift 已处理（WORM 归档 + drift 报告 + `CANDIDATE_AUTO`/`is_demo=true` lineage），**非 O1 收口**（knife 333 契约：drift 不自动改 registry，等用户裁定）。
- 落盘：归档 `data/public_archives/2026-08/stats.gov.cn/zxfb`（435,469 B，进 git 不入 pack——manifest 先例只收 `spikes/*/sample.html`，不收 WORM 归档）；drift 报告进 git；lineage 在 `/tmp`（caller 指定 confirm-live 路径，惯例副产物）。`data/public_extracts/` 零触碰（已提交 63 行 extract 原样）。

## registry pin 未做（如实报告 + 理由）

341 裁定「稳定直链 → 算 SHA → 可写 registry」。本次 deeplink `t20260821_1965093.html` 形式上属「单篇固定 HTML」，**但未 pin**，留给 Cursor/用户裁定，理由：

1. registry `file_hash_sha256` 若改为 `0b85212f…`，knife 52 的 fixture 锚定测试（`fixture.source_sha256 == registry.file_hash_sha256 == dea13b8a…`）与 `/public-extracts` 页 provenance 立即失锚——需配套重生成 extract + fixture + 前端内容 + 相关测试，是独立一刀的工作量；
2. `local_sample_path=spikes/01-national-yearbook/sample.html`（388,238 B = 索引页样本）与新 SHA 不匹配，pin 需同时换样本，否则 local-sample 路径 rc=8；
3. 本刀红线为缩刀（§SCHEMA「本刀不做」未授权 registry 改写）。

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `scripts/auto_ingest_public_source.py` | MODIFIED（收紧 + 空内容分类 + 分支文本） | 已入 manifest（SKIP） |
| `tests/test_auto_ingest_public_source_s52.py` | MODIFIED + 新增 5 case | 已入 manifest（SKIP） |
| `data/public_archives/2026-08/stats.gov.cn/zxfb` | NEW（NBS live drifted bytes WORM 归档；进 git 不入 pack） | — |
| `reviews/.../20260826T111011Z-stage2-public-source-sha-drift-stats.gov.cn-NATIONAL_BULLETIN.md` | NEW（drift 报告；进 git） | — |
| `scripts/_knife54_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../356-stage0-cc-js-shell-nbs-live-receipt-20260826.md` | NEW（本文件） | `documentation` |

## Pack 不变量

`_knife54_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **665 → 667**；`sum(role_count) == artifact_count == len(artifacts) == 667`。

## 红线自查

- ❌ 未执行页面 JS；未切 headless；未绕 AUTH
- ✅ 小壳仍拦（71B Hubei + 小 redirect 无 script 两 case 锁定）
- ❌ 未把 71B 壳放行；未伪造 O1（rc=4 如实，未宣称收口）
- ❌ 未宣布 Gate/O1 PASS；未动 `00-CC-CURRENT.md` / `gate_thresholds.json` / registry；未 --force；未索要 PAT
- ✅ 回执文件名含 `-cc-`；未在 chat 复述 Cursor 长文

## 下一步

`./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 357）。
