# 395 — 湖北观察页链到公开提取轨 · CC 回执

- 编号：`395-stage0-cc-hubei-home-link-public-extract-receipt-20260826`
- 任务书：`394-stage2-hubei-page-link-public-extract-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`<待回填>`
- 日期：2026-08-26

---

## §NOW 对照

| 394 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) 找到湖北相关前端页（省级 `/provinces/...` 或城页若有）；增显式链 `/public-extracts#track-hb`，文案标明 REGISTRY_SAMPLE / xlsx / live `enabled=FALSE` / 非 O1 | ✅ **事实核查走兜底**：`/provinces/` 仅 guangdong/jiangsu/shandong/sichuan/zhejiang（5 省无湖北）；`city_slug_map.ts` 10 城无湖北城市 → 按 §SCHEMA-2 缩刀兜底在首页加行：`frontend/app/page.tsx` 公开提取表格 + 一行「公开提取湖北轨（xlsx demo）」→ `/public-extracts#track-hb` 链 + `tjj.hubei.gov.cn / PROVINCIAL_BULLETIN 21 行 xlsx 月报统计（--from-local-sample --allow-disabled-local-sample 提取）` + `REGISTRY_SAMPLE · xlsx · demo · live enabled=FALSE 暂缓（非 live O1）` 四项提示 | diff + 自检 |
| (2) ≥1 pytest 或 smoke | ✅ 2 pytest case + smoke §13b 门（5 针）：<br>• `test_home_page_has_hubei_track_link_row` — 首页含「公开提取湖北轨」行 + `/public-extracts#track-hb` 链 + `PROVINCIAL_BULLETIN` + `enabled=FALSE` + `非 live O1` 五针；<br>• `test_no_hubei_link_pollutes_province_or_city_pages` — `/provinces/*` 5 省页与 CityPage/CityPageMart 不得出现 `#track-hb` 链（防无条件污染）；<br>• `frontend/smoke-check.py §13b` — 首页湖北轨行 + #track-hb 链 + PROVINCIAL_BULLETIN + enabled=FALSE + 非 live O1 五针 | 自检 + pytest + smoke |
| (3) 回执 `395`（`-cc-` 名） | ✅ 本文件名 | — |

## 证据

```
$ python3 -m pytest tests/test_hubei_home_link_public_extract.py \
                    tests/test_shenzhen_city_link_public_extract.py \
                    tests/test_public_extract_frontend_fixture.py \
                    tests/test_auto_ingest_public_source_s52.py -q
115 passed in 2.25s                      # 2 + 3 + 24 + 86 = 115 全绿

$ python3 frontend/smoke-check.py
✅ app/page.tsx: 公开提取湖北轨行 → /public-extracts#track-hb 链 + REGISTRY_SAMPLE xlsx demo + enabled=FALSE 暂缓 + 非 O1 守门
=== … smoke: PASS ===

$ python3 scripts/_knife67_manifest_bump.py
ADD: tests/test_hubei_home_link_public_extract.py (…)
ADD: scripts/_knife67_manifest_bump.py (…)
ADD: reviews/.../395-…-receipt-20260826.md (…)
UPDATE artifact_count: 703 → 706
INVARIANT: sum(role_count)=706 == artifact_count=706 == len(artifacts)=706
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `frontend/app/page.tsx` | MODIFIED（公开提取表格 + 一行「公开提取湖北轨（xlsx demo）」） | 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例） |
| `frontend/smoke-check.py` | MODIFIED（+ §13b 门，5 针） | 已入 manifest（SKIP） |
| `tests/test_hubei_home_link_public_extract.py` | NEW（2 cases） | `schema_negative_test` |
| `scripts/_knife67_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../395-stage0-cc-hubei-home-link-public-extract-receipt-20260826.md` | NEW（本文件） | `documentation` |

## Pack 不变量

`_knife67_manifest_bump.py`：NEW_ARTIFACTS +3（1 新测文件 + bump + receipt）→ **703 → 706**；`sum(role_count) == artifact_count == len(artifacts) == 706`（page.tsx / smoke-check.py 皆 SHA REFRESH 不增计数；前置 knife 66 已落 knife 66 新测文件入 pack 700 → 703）。

## 红线自查

- ❌ 未启用湖北 live（`enabled=FALSE` 显式标注在链接旁 + smoke §13b + pytest 针锁定）
- ❌ 未改 extract / fixture 字节（4 fixture 未动）
- ❌ 未无条件污染其它省/城页（pytest `test_no_hubei_link_pollutes_province_or_city_pages` 锁定 `/provinces/*` 与 CityPage/CityPageMart 无 #track-hb 链）
- ❌ 未谎称 live（四项提示 REGISTRY_SAMPLE / xlsx / enabled=FALSE 暂缓 / 非 live O1 全在链接行）
- ❌ 未跑任何 live 探测 / 未改 registry `enabled` 列 / 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json`
- ❌ 未 Gate/O1 PASS 宣告；未 --force；未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 396）。