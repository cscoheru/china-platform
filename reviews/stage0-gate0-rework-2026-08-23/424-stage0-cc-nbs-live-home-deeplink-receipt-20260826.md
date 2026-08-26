# 424 — 首页 NBS live 候选轨 deeplink · CC 回执

- 编号：`424-stage0-cc-nbs-live-home-deeplink-receipt-20260826`
- 任务书：`424-stage2-nbs-live-home-deeplink-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`1ced2bd`
- 日期：2026-08-26

---

## §NOW 对照

| 424 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) 首页 `frontend/app/page.tsx` 公开提取表新增一行「公开提取 NBS live 候选轨（candidate demo）」→ `/public-extracts#track-nbs-live`；镜像 NBS sample `#track-nbs-sample` 行 + 湖北 `#track-hb` 行；文案标明 LIVE_CANDIDATE / drift 候选 / 非 O1 收口 | ✅ `frontend/app/page.tsx` 公开提取表在 NBS sample 行后新增 1 行：`<td>公开提取 NBS live 候选轨（candidate demo）</td>` + `<a href="/public-extracts#track-nbs-live" data-testid="home-public-extracts-nbs-live">/public-extracts#track-nbs-live</a>` + 描述列「stats.gov.cn / NATIONAL_BULLETIN 60 行（WORM `zxfb` LIVE_CANDIDATE 提取；drift 候选；per 回执 `359` / `362`）」 + 标签列「LIVE_CANDIDATE · drift 候选 · 非 O1 收口」；不引入 next/link 保留 build ○ Static；不分支 `params.*` | diff |
| (2) ≥1 smoke 或 pytest | ✅ smoke §12b'' 4 针（href `#track-nbs-live` + testId `home-public-extracts-nbs-live` + LIVE_CANDIDATE / drift 候选 / 非 O1 收口 标注 + 综合 PASS 行）+ pytest `tests/test_nbs_live_home_deeplink_public_extract.py` 3 cases（home 页含 NBS live deeplink 行 + 省/城页不污染 + 4 fixture SHA 锁）；pytest `3 passed in 0.73s`；smoke 全绿（§12b' + §12b'' 新增行 + 既有 §12f/§12h/§13c 全部保留） | pytest log + smoke log |
| (3) 不改 fixture 字节 | ✅ 4 fixture byte SHA 锁在 pytest 内显式列出（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`；共享 knife 76 锁值，fixture 字节保持不变）| pytest `test_no_fixture_byte_modified` PASSED |
| (4) 回执 `424`（`-cc-`）| ✅ 本文件名 | — |

## 证据

```
$ python3 -m pytest tests/test_nbs_live_home_deeplink_public_extract.py -v
tests/test_nbs_live_home_deeplink_public_extract.py::test_home_page_has_nbs_live_deeplink PASSED [ 33%]
tests/test_nbs_live_home_deeplink_public_extract.py::test_no_nbs_live_deeplink_pollutes_province_or_city_pages PASSED [ 66%]
tests/test_nbs_live_home_deeplink_public_extract.py::test_no_fixture_byte_modified PASSED [100%]
============================== 3 passed in 0.73s ===============================

$ python3 frontend/smoke-check.py
...
✅ app/page.tsx links /public-extracts#track-nbs-live deeplink
✅ app/page.tsx testId=home-public-extracts-nbs-live
✅ app/page.tsx NBS live deeplink row: LIVE_CANDIDATE / drift 候选 / 非 O1 收口
...
=== S2.0.1 + S2.7-a + S2.7-a2 + S2.7-b-lite + S2.7-b-full-lite mart-shape + home nav smoke: PASS ===

$ grep -n "NBS live 候选轨\|track-nbs-live\|home-public-extracts-nbs-live" frontend/app/page.tsx
  175:            <td style={cellStyle}>公开提取 NBS live 候选轨（candidate demo）</td>
  178:                href="/public-extracts#track-nbs-live"
  179:                data-testid="home-public-extracts-nbs-live"
  181:                /public-extracts#track-nbs-live

$ python3 scripts/_knife78_manifest_bump.py
ADD: tests/test_nbs_live_home_deeplink_public_extract.py (5210 bytes, sha=73f90a1f)
ADD: scripts/_knife78_manifest_bump.py (3770 bytes, sha=66a15d82)
ADD: reviews/.../424-stage0-cc-nbs-live-home-deeplink-receipt-20260826.md (...)
UPDATE artifact_count: 734 → 737
INVARIANT: sum(role_count)=737 == artifact_count=737 == len(artifacts)=737
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `frontend/app/page.tsx` | MODIFIED（+1 行 NBS live 候选轨 deeplink）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `frontend/smoke-check.py` | MODIFIED（§12b'' 4 针 + 综合 PASS 行）| 已入 manifest（SKIP）|
| `tests/test_nbs_live_home_deeplink_public_extract.py` | NEW（3 cases）| `schema_negative_test` |
| `scripts/_knife78_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../424-stage0-cc-nbs-live-home-deeplink-receipt-20260826.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife78_manifest_bump.py`：NEW_ARTIFACTS +3（pytest + bump + receipt）→ **734 → 737**；`sum(role_count) == artifact_count == len(artifacts) == 737`（`frontend/app/page.tsx` / `frontend/smoke-check.py` 皆已入 manifest，SHA REFRESH 不增计数；前置 knife 76+77 已落 729 → 734）。

## 红线自查

- ❌ 未删减 OPEN（§3/§5.5/§6 OPEN 清单原样；仅增不改）
- ❌ 未 Gate/O1 PASS 宣告（首页三处「仍不宣布 Gate 2 PASS」+ 文案明示「非 O1 收口」+ LIVE_CANDIDATE drift 候选语义）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ❌ 未引入 next/link（保留 build ○ Static 22/22 特征）
- ❌ 未分支 `params.*`（静态段保持零分支）
- ❌ 未改 4 fixture 字节（pytest `test_no_fixture_byte_modified` 字节级 SHA 前 8 锁 + fixture byte SHA 与 knife 76 锁值完全一致）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ 镜像 NBS sample 行 + 湖北轨行结构（首页表内一致形态）
- ✅ docs/45 + docs/53 登记留给后续刀（per tasking 424 §SCHEMA 「本刀做」只列 page.tsx + smoke/pytest + receipt；不扩 docs）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `424`）。
