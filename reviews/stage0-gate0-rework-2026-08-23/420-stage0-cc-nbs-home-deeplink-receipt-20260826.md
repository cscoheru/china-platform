# 420 — 首页 NBS sample 轨显式 deeplink · CC 回执

- 编号：`420-stage0-cc-nbs-home-deeplink-receipt-20260826`
- 任务书：`420-stage2-nbs-home-deeplink-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`TBD-pre-push`
- 日期：2026-08-26

---

## §NOW 对照

| 420 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) 首页 `frontend/app/page.tsx` 公开提取表：为 NBS sample 轨加显式链 `/public-extracts#track-nbs-sample`（镜像湖北 `#track-hb` 行；文案标明 REGISTRY_SAMPLE / demo / 非 O1；可改现有「四轨 demo」行 href 或新增一行）| ✅ 首页「横向视角入口」表内「公开提取样本（四轨 demo）」行 → **「公开提取 NBS sample 轨（demo）」** 行；href 从 `/public-extracts` → `/public-extracts#track-nbs-sample`；新增 `data-testid="home-public-extracts-nbs-sample"`；描述保留 `stats.gov.cn / NATIONAL_BULLETIN 63 行（registry 本地样本 --from-local-sample 结构化提取；per 回执 350）`；数据模式标 `REGISTRY_SAMPLE · demo · 非 live O1`；结构镜像湖北「公开提取湖北轨（xlsx demo）」行 | diff |
| (2) ≥1 smoke 或 pytest 针 | ✅ **smoke §12b'**（4 针：href + testId + REGISTRY_SAMPLE/demo/非 live O1）+ **pytest 3 cases**（de 行/无省城页污染/4 fixture SHA 不变） | smoke PASS；pytest `3 passed in 0.72s` |
| (3) 不改 fixture 字节 | ✅ 4 fixture SHA 前 8 锁（byte SHA, 非 registry SHA）— pytest `test_no_fixture_byte_modified` PASS；current SHA：`public_extract_nbs.json=e30ee811` / `nbs_live_candidate=9232efdb` / `sz=937255a5` / `hubei=9056001c` | pytest 守门 |
| (4) 回执 `420`（`-cc-`）| ✅ 本文件名 | — |

## 证据

```
$ python3 -m pytest tests/test_nbs_home_deeplink_public_extract.py -v
tests/test_nbs_home_deeplink_public_extract.py::test_home_page_has_nbs_sample_deeplink PASSED [ 33%]
tests/test_nbs_home_deeplink_public_extract.py::test_no_nbs_deeplink_pollutes_province_or_city_pages PASSED [ 66%]
tests/test_nbs_home_deeplink_public_extract.py::test_no_fixture_byte_modified PASSED [100%]
============================== 3 passed in 0.72s ===============================

$ python3 frontend/smoke-check.py | grep "12b\|NBS sample"
✅ app/page.tsx testId=home-public-extracts-nbs-sample
✅ app/page.tsx NBS sample deeplink row: REGISTRY_SAMPLE / demo / 非 O1
... smoke: PASS

$ python3 scripts/_knife76_manifest_bump.py
ADD: tests/test_nbs_home_deeplink_public_extract.py (…)
ADD: scripts/_knife76_manifest_bump.py (…)
ADD: reviews/.../420-…-receipt-20260826.md (…)
UPDATE artifact_count: 729 → 732
INVARIANT: sum(role_count)=732 == artifact_count=732 == len(artifacts)=732
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `frontend/app/page.tsx` | MODIFIED（公开提取表内 NBS sample 行：title 「公开提取样本（四轨 demo）」→「公开提取 NBS sample 轨（demo）」+ href `/public-extracts` → `/public-extracts#track-nbs-sample` + 新 testId `home-public-extracts-nbs-sample` + 数据模式 `REGISTRY_SAMPLE · demo · 非 live O1`）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `frontend/smoke-check.py` | MODIFIED（§12b 后新增 §12b' 守门 4 针：href + testId + REGISTRY_SAMPLE / demo / 非 live O1）| 已入 manifest（SKIP）|
| `tests/test_nbs_home_deeplink_public_extract.py` | NEW（3 pytest cases：de 行内容 / 省城页无污染 / 4 fixture byte SHA 不变）| `schema_negative_test` |
| `scripts/_knife76_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../420-stage0-cc-nbs-home-deeplink-receipt-20260826.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife76_manifest_bump.py`：NEW_ARTIFACTS +3（pytest + bump + receipt）→ **729 → 732**；`sum(role_count) == artifact_count == len(artifacts) == 732`（`page.tsx` / `smoke-check.py` 皆已入 manifest，SHA REFRESH 不增计数；前置 knife 75 已落 727 → 729）。

## 守门覆盖（per 420 §SCHEMA + §红线）

| 守门 | 落地 |
|---|---|
| §12b' smoke 4 针（href + testId + REGISTRY_SAMPLE + demo + 非 live O1）| ✅ `frontend/smoke-check.py` §12b' 5 行检查（4 标 + 1 综合）|
| pytest 3 cases（de 行 + 省城页无污染 + fixture SHA 不变）| ✅ `tests/test_nbs_home_deeplink_public_extract.py` 3 cases PASS |
| 镜像湖北 `#track-hb` 行结构 | ✅ 行标题「公开提取 NBS sample 轨（demo）」结构镜像「公开提取湖北轨（xlsx demo）」 |
| 4 fixture SHA 不变 | ✅ pytest `test_no_fixture_byte_modified` 锁定 4 fixture byte SHA 前 8 字符 |
| 不污染 /provinces/* 5 省页 | ✅ pytest `test_no_nbs_deeplink_pollutes_province_or_city_pages` 守门 |
| 不污染 10 城 CityPage/CityPageMart | ✅ 同上 pytest 守门（`/provinces/*` 5 + `CityPage` + `CityPageMart`）|
| 不动 build ○ Static 特征 | ✅ 仅 href 改 + 加 testId；无 `params.*` 分支；无 `next/link` 引入 |

## 红线自查

- ❌ 未 Gate/O1 PASS 宣告（page.tsx 数据模式列显式 `非 live O1`；smoke §12b' 守门包含 `非 live O1` 文案；pytest 守门包含 `非 live O1`）
- ❌ 未 live 探测 / 未 O1 收口 / 未改 fixture 字节（pytest 4 fixture byte SHA 前 8 守门 PASS）
- ❌ 未删减 OPEN 清单（首页原有 Indicator inventory / 5 省 / 10 地市 / 七维 / peer-compare / 湖北轨 / 其它链接全数保留）
- ❌ 未改深圳/湖北既有链（仅改 NBS sample 行；湖北行原样保留 `#track-hb`；深圳仅 `CityPage.tsx` `#track-sz` 不动）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ❌ 未 `next/link` 引入（保留 build ○ Static 22/22）
- ❌ 未 `params.*` 分支（保持纯 `<a href>` 锚链）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ smoke + pytest 双守门；smoke §12b' + pytest 3 cases 全 PASS

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `420`）。