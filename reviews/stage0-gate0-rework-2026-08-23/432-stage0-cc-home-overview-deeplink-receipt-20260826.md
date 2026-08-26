# 432 — 首页四轨一览 overview 显式 deeplink · CC 回执

- 编号：`432-stage0-cc-home-overview-deeplink-receipt-20260826`
- 任务书：`432-stage2-home-overview-deeplink-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`624f02a`（backfill commit `TBD`，后续单独 commit 回填；前序 commit `624f02a` = knife 82 主落地）
- 日期：2026-08-26

---

## §NOW 对照

| 432 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) 首页 `frontend/app/page.tsx` 公开提取表：新增一行「公开提取四轨一览（overview）」→ `/public-extracts#overview`（镜像 NBS/湖北 deeplink 行；文案标明 demo / 非 O1）| ✅ `frontend/app/page.tsx` 公开提取表内湖北行后新增「公开提取四轨一览（overview strip）」行；href `/public-extracts#overview`；新增 `data-testid="home-public-extracts-overview"`；描述列「stats.gov.cn / sz.gov.cn / tjj.hubei.gov.cn 7 列 × 4 行 overview（轨 / domain / category / 行数 / SHA 前 8 / demo\|candidate 标注 / 分节锚点；数据只读自既有 4 fixture，不重算；per 回执 `383`；smoke §12f 门）」；数据模式标 `OVERVIEW · 四轨 demo · 非 O1`；结构镜像 knife 76 tasking 420 NBS sample 行 + knife 78 tasking 424 NBS live 行 + knife 67 tasking 394 湖北 `#track-hb` 行；纯 `<a href>` 锚链未引入 `next/link`（保留 build ○ Static 22/22）；不分支 `params.*`（AGENTS.md 静态路由红线）| diff |
| (2) ≥1 smoke 或 pytest | ✅ `frontend/smoke-check.py` §12b''' 4 针（href + testId + OVERVIEW / 四轨 demo / 非 O1 + 综合 PASS）+ `tests/test_overview_home_deeplink_public_extract.py` 3 pytest cases（de 行内容 / 5 省 + 10 城 CityPage/CityPageMart 无 `#overview` 污染 / 4 fixture byte SHA 前 8 锁不漂：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`；与 knife 76/78/80/81 锁值完全一致，fixture 字节保持不变）；`pytest` `9 passed in 0.68s`（3 新 + 6 prior home deeplink regression）；smoke §12b''' PASS | diff + pytest 9 passed + smoke §12b''' 4 针 ✅ |
| (3) 不改 fixture 字节 | ✅ 4 fixture 字节锁 `nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c` 与 knife 76/78/80/81 完全一致；pytest `test_no_fixture_byte_modified` 锁前缀不漂 | pytest + diff |
| (4) 回执 `432`（`-cc-`）| ✅ 本文件名 | — |

## 证据

```
$ grep -n "公开提取四轨一览\|/public-extracts#overview\|home-public-extracts-overview" frontend/app/page.tsx | head -10
  208:| <td style={cellStyle}>公开提取四轨一览（overview strip）</td>
  212:| href="/public-extracts#overview"
  213:| data-testid="home-public-extracts-overview"
  215:| /public-extracts#overview

$ python3 frontend/smoke-check.py 2>&1 | grep -E "overview deeplink|OVERVIEW|home-public-extracts-overview"
  ✅ app/page.tsx links /public-extracts#overview deeplink
  ✅ app/page.tsx testId=home-public-extracts-overview
  ✅ app/page.tsx overview deeplink row: OVERVIEW / 四轨 demo / 非 O1

$ python3 -m pytest tests/test_overview_home_deeplink_public_extract.py -v
  tests/test_overview_home_deeplink_public_extract.py::test_home_page_has_overview_deeplink PASSED
  tests/test_overview_home_deeplink_public_extract.py::test_no_overview_deeplink_pollutes_province_or_city_pages PASSED
  tests/test_overview_home_deeplink_public_extract.py::test_no_fixture_byte_modified PASSED
  ============================== 3 passed in 0.75s ===============================

$ python3 -m pytest tests/test_nbs_home_deeplink_public_extract.py tests/test_nbs_live_home_deeplink_public_extract.py tests/test_overview_home_deeplink_public_extract.py -v
  ============================== 9 passed in 0.68s ===============================
  （3 new + 6 prior home deeplink regression — no cross-contamination）

$ python3 scripts/_knife82_manifest_bump.py
ADD: tests/test_overview_home_deeplink_public_extract.py (…)
ADD: scripts/_knife82_manifest_bump.py (…)
ADD: reviews/.../432-…-receipt-20260826.md (…)
UPDATE artifact_count: 743 → 746
INVARIANT: sum(role_count)=746 == artifact_count=746 == len(artifacts)=746
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `frontend/app/page.tsx` | MODIFIED（公开提取表 湖北行后新增「公开提取四轨一览」行）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `frontend/smoke-check.py` | MODIFIED（§12b''' 4 针：href + testId + OVERVIEW / 四轨 demo / 非 O1 + 综合 PASS）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `tests/test_overview_home_deeplink_public_extract.py` | NEW | `schema_negative_test` |
| `scripts/_knife82_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../432-stage0-cc-home-overview-deeplink-receipt-20260826.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife82_manifest_bump.py`：NEW_ARTIFACTS +3（pytest + bump + receipt）→ **743 → 746**；`sum(role_count) == artifact_count == len(artifacts) == 746`（page.tsx + smoke 已入 manifest，SHA REFRESH 不增计数；前置 knife 81 docs/45/docs/53/docs/50 互链已落 741 → 743；前置 knife 80 docs/50 §4.4 +2 行已落 739 → 741；前置 knife 78 + knife 79 已落 734 → 737 → 739）。

## overview deeplink 互链对账

| deeplink 行 | href | testId | 数据模式 | smoke 门 | pytest | 4 fixture SHA 锁 |
|---|---|---|---|---|---|---|
| **公开提取四轨一览（overview strip）**（行 208）| `/public-extracts#overview` | `home-public-extracts-overview` | `OVERVIEW · 四轨 demo · 非 O1` | §12b''' 4 针 ✅ | 3 cases PASSED | `nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`（与 knife 76/78/80/81 完全一致，fixture 字节保持不变）|

## 红线自查

- ❌ 未宣布 Gate/O1 PASS（数据模式标 `OVERVIEW · 四轨 demo · 非 O1`；与 knife 76/78 NBS 行 `REGISTRY_SAMPLE · demo · 非 live O1` / `LIVE_CANDIDATE · drift 候选 · 非 O1 收口` 守门一致；smoke §12f 门保留 overview strip 守门 13 针）
- ❌ 未改代码契约（page.tsx 仅新增一行，结构镜像 knife 76/78/67 行模板；不改 4 fixture 字节）
- ❌ 未引入 `next/link`（纯 `<a href>` 锚链保留 build ○ Static 22/22 公共 chunk 87 kB）
- ❌ 未分支 `params.*`（AGENTS.md 静态路由红线，pytest `test_no_overview_deeplink_pollutes_province_or_city_pages` 锁定 5 省 + 10 城 CityPage/CityPageMart 不出现 `#overview` 链）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ 4 fixture byte SHA 前 8 锁在 receipt 中显式列出（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与 knife 76 + knife 78 + knife 80 + knife 81 完全一致，fixture 字节保持不变）
- ✅ 9 pytest cases passed (3 new + 6 prior home deeplink regression — no cross-contamination)
- ✅ smoke §12b''' 4 针 PASS + 全 smoke PASS（保留所有原 §12a-§12e / §12f / §12g / §12h / §12i / §13a-§13c 门）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `432`）。