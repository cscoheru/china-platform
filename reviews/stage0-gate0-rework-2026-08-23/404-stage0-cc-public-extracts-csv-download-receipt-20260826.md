# 404 — /public-extracts 四轨 CSV 静态下载 · CC 回执

- 编号：`404-stage0-cc-public-extracts-csv-download-receipt-20260826`
- 任务书：`403-stage2-public-extracts-csv-download-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`abc8606`
- 日期：2026-08-26

---

## §NOW 对照

| 403 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) 由既有 4 fixture **确定性**生成 CSV（列序=首行键序，不重命名）→ `frontend/public/public-extracts/{nbs,nbs-live-candidate,sz,hubei}.csv` | ✅ `scripts/gen_public_extracts_csv.py`（`render_csv_bytes` 纯函数：UTF-8 无 BOM / `\n` / QUOTE_MINIMAL；列序=首行键序，不重命名不重排，湖北未命名空列键原样保留；单元格 `row.get(key,"")` 与页面 `{row[key] ?? ""}` 同语义）；产物已 commit：nbs.csv 2444B（63 行）/ nbs-live-candidate.csv 2788B（60 行）/ sz.csv 19818B（71 行）/ hubei.csv 902B（21 行）；重跑 shasum 全等（21b97d4f… 等，字节确定性实测） | 脚本 + shasum |
| (2) overview 表「下载 JSON」旁增 CSV 链（或同列第二链） | ✅ 列头改「下载 JSON / CSV」（含原 §12g needle 子串不回归）；4 个下载格同格第二链 `⬇ {name}.csv`（href `/public-extracts/{name}.csv` + download attr）；页脚注 +「JSON / CSV 下载皆为 fixture 快照确定性导出 (demo/candidate), 非权威库」 | diff |
| (3) ≥2 pytest（CSV 行数=fixture 行数；表头一致）+ smoke 针 | ✅ **13 pytest case + smoke §12i 门（15 针）**：<br>• `test_csv_header_matches_fixture_first_row_keys` ×4（表头==首行键序）；<br>• `test_csv_row_count_and_field_count_match_fixture` ×4（数据行数==row_count==len(rows) + 每行字段数==表头）；<br>• `test_csv_bytes_match_deterministic_regeneration` ×4（committed CSV == 生成器重渲字节 — 确定性+可再生，禁手编辑偏离）；<br>• `test_page_links_csv_and_keeps_json_downloads`（4 CSV href+download / 4 JSON 链不回归 / 非权威库守门 / 无 `text/csv` 服务端动态导出）；<br>• smoke §12i — 4 CSV 在位非空 + 列头 + 4 href + 4 download attr + 非权威库守门 + JSON 4 链不回归 | pytest + smoke |
| (4) 回执 `404`（`-cc-`） | ✅ 本文件名 | — |

## 证据

```
$ python3 scripts/gen_public_extracts_csv.py
WROTE frontend/public/public-extracts/hubei.csv (902 bytes, 21 data rows + header)
WROTE frontend/public/public-extracts/nbs.csv (2444 bytes, 63 data rows + header)
WROTE frontend/public/public-extracts/nbs-live-candidate.csv (2788 bytes, 60 data rows + header)
WROTE frontend/public/public-extracts/sz.csv (19818 bytes, 71 data rows + header)
$ (重跑) shasum 全等 → 字节确定性实测

$ python3 -m pytest tests/test_public_extracts_csv_download.py \
                    tests/test_public_extract_frontend_fixture.py -q
40 passed in 0.73s                       # 13 新 CSV case + 27 fixture case 全绿

$ python3 frontend/smoke-check.py
✅ public-extracts/page.tsx: 下载 JSON / CSV 列 + 4 CSV download 链 + 非权威库守门 (JSON 链不回归)
=== … smoke: PASS ===

$ cd frontend && npm run build
✓ Compiled successfully
├ ○ /public-extracts    15.9 kB   103 kB   # 仍 ○ Static

$ python3 scripts/_knife70_manifest_bump.py
ADD: frontend/public/public-extracts/nbs.csv (…)
ADD: frontend/public/public-extracts/nbs-live-candidate.csv (…)
ADD: frontend/public/public-extracts/sz.csv (…)
ADD: frontend/public/public-extracts/hubei.csv (…)
ADD: scripts/gen_public_extracts_csv.py (…)
ADD: tests/test_public_extracts_csv_download.py (…)
ADD: scripts/_knife70_manifest_bump.py (…)
ADD: reviews/.../404-…-receipt-20260826.md (…)
UPDATE artifact_count: 710 → 718
INVARIANT: sum(role_count)=718 == artifact_count=718 == len(artifacts)=718
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `frontend/app/public-extracts/page.tsx` | MODIFIED（列头「下载 JSON / CSV」+ 4 同格 CSV 第二链 + 页脚非权威库注 + 头部注释 403 段） | 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例） |
| `frontend/smoke-check.py` | MODIFIED（+ §12i 门，15 针） | 已入 manifest（SKIP） |
| `frontend/public/public-extracts/{nbs,nbs-live-candidate,sz,hubei}.csv` | NEW ×4（确定性生成产物） | `data_contract_suite` |
| `scripts/gen_public_extracts_csv.py` | NEW（生成器，`render_csv_bytes` 纯函数可测） | `spike_helper` |
| `tests/test_public_extracts_csv_download.py` | NEW（13 cases） | `schema_negative_test` |
| `scripts/_knife70_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../404-stage0-cc-public-extracts-csv-download-receipt-20260826.md` | NEW（本文件） | `documentation` |

## Pack 不变量

`_knife70_manifest_bump.py`：NEW_ARTIFACTS +8（4 CSV + 生成器 + 测试 + bump + receipt）→ **710 → 718**；`sum(role_count) == artifact_count == len(artifacts) == 718`（page.tsx / smoke-check.py 皆 SHA REFRESH 不增计数；前置 knife 69 已落 708 → 710）。

## 红线自查

- ❌ 未改 4 个 fixture JSON 字节（§12g 字节一致门 + byte-identical pytest 仍绿）
- ❌ CSV 行数与 fixture 不一致的情况不存在（×4 pytest 锁定 21/63/60/71 行 + 字段数==表头）
- ❌ 未破坏 JSON 下载（4 JSON 链原样，smoke §12i + §12g + pytest 三重复检）
- ❌ 未谎称 CSV=权威库（页脚「fixture 快照确定性导出 (demo/candidate), 非权威库」+ pytest/smoke 锁定）
- ❌ 无服务端动态导出（静态 public 文件；页面无 `text/csv`；生成器为 scripts/ 工具）
- ❌ 未跑 live 探测 / 未动 registry / 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json`
- ❌ 未 Gate/O1 PASS 宣告；未 --force；未索要 PAT；未碰 params.*（build ○ 证实）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 405）。
