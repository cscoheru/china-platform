# 392 — 深圳城页链到公开提取轨 · CC 回执

- 编号：`392-stage0-cc-shenzhen-city-link-public-extract-receipt-20260826`
- 任务书：`391-stage2-shenzhen-city-link-public-extract-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`<待回填>`
- 日期：2026-08-26

---

## §NOW 对照

| 391 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `frontend/app/cities/` 深圳相关页（`CityPage` / mart / slug=`shenzhen` 路径）增显式链接：`/public-extracts#track-sz`（文案标明 REGISTRY_SAMPLE demo，非 O1） | ✅ `CityPage.tsx` + `CityPageMart.tsx` 各新增条件分支（`city.slug === 'shenzhen'` / `mart.cityId === 'shenzhen'`）→ `<section data-testid="city-page-public-extract-link">` / `<section data-testid="city-page-mart-public-extract-link">`；h3「公开提取 — 深圳轨（per tasking 391）」+ 正文 `深圳统计公报散文段落表（sz.gov.cn MUNICIPAL_BULLETIN，71 行 {section, paragraph}）已落在 /public-extracts#track-sz` + `样本来自 registry 锚定的本地 spike，REGISTRY_SAMPLE demo，SSL 暂缓未做过 live 探测，非 O1 收口（per 回执 368/371/383）`；底部「mock 观察卡与公报散文轨互不覆盖 — mock 数据是城市观察卡演示，公报散文轨是公开源结构化提取演示；两者皆 demo，非 O1」守门 | diff + 自检 |
| (2) 首页或七维无关处可不改 | ✅ 未动 `frontend/app/page.tsx` 首页 / 七维 (`seven-dim`)；仅 `CityPage.tsx` + `CityPageMart.tsx` 增条件分支 | 自检 |
| (3) ≥1 pytest 或 smoke 针 | ✅ 3 pytest case + smoke §13 门（8 针）：<br>• `test_city_page_has_shenzhen_public_extract_link` — CityPage.tsx 含 `slug==='shenzhen'` 条件 + `/public-extracts#track-sz` 链 + `REGISTRY_SAMPLE` 标注 + 非 O1 守门；<br>• `test_city_page_mart_has_shenzhen_public_extract_link` — CityPageMart.tsx 同 4 针；<br>• `test_other_cities_do_not_render_link_unconditionally` — 链出现位置必须晚于最后一个 shenzhen 条件分支 (防止无条件链接污染其它城页)；<br>• `frontend/smoke-check.py §13` — CityPage.tsx + CityPageMart.tsx 各 4 针 (条件 + 链 + REGISTRY_SAMPLE + 非 O1) | 自检 + pytest + smoke |
| (4) 回执 `392`（`-cc-` 名） | ✅ 本文件名 | — |

## 证据

```
$ python3 -m pytest tests/test_shenzhen_city_link_public_extract.py \
                    tests/test_public_extract_frontend_fixture.py \
                    tests/test_auto_ingest_public_source_s52.py -q
113 passed in 2.13s                      # 3 + 24 + 86 = 113 全绿

$ python3 frontend/smoke-check.py
✅ CityPage.tsx: shenzhen 条件分支 → /public-extracts#track-sz 链 + REGISTRY_SAMPLE demo 标注 + 非 O1 守门
✅ CityPageMart.tsx: shenzhen 条件分支 → /public-extracts#track-sz 链 + REGISTRY_SAMPLE demo 标注 + 非 O1 守门
=== … smoke: PASS ===

$ (cd frontend && npm run build 2>&1 | grep -E '(public-extracts|Compiled|Generating)')
 ✓ Compiled successfully
 ✓ Generating static pages (22/22)
├ ○ /public-extracts                     160 B          87.2 kB
                                           # static prerender (○) ✓

$ python3 scripts/_knife66_manifest_bump.py
ADD: tests/test_shenzhen_city_link_public_extract.py (…)
ADD: scripts/_knife66_manifest_bump.py (…)
ADD: reviews/.../392-…-receipt-20260826.md (…)
UPDATE artifact_count: 700 → 703
INVARIANT: sum(role_count)=703 == artifact_count=703 == len(artifacts)=703
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `frontend/app/components/CityPage.tsx` | MODIFIED（+ 条件分支 shenzhen → `<section data-testid="city-page-public-extract-link">` 含 `/public-extracts#track-sz` 链 + REGISTRY_SAMPLE demo + 非 O1 守门） | 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例） |
| `frontend/app/components/CityPageMart.tsx` | MODIFIED（+ 条件分支 mart.cityId==='shenzhen' → `<section data-testid="city-page-mart-public-extract-link">` 同上） | 已入 manifest（SKIP） |
| `frontend/smoke-check.py` | MODIFIED（+ §13 门，CityPage + CityPageMart 各 4 针 = 8 针） | 已入 manifest（SKIP） |
| `tests/test_shenzhen_city_link_public_extract.py` | NEW（3 cases） | `schema_negative_test` |
| `scripts/_knife66_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../392-stage0-cc-shenzhen-city-link-public-extract-receipt-20260826.md` | NEW（本文件） | `documentation` |

## Pack 不变量

`_knife66_manifest_bump.py`：NEW_ARTIFACTS +3（1 新测文件 + bump + receipt）→ **700 → 703**；`sum(role_count) == artifact_count == len(artifacts) == 703`（CityPage.tsx / CityPageMart.tsx / smoke-check.py 皆 SHA REFRESH / 测 / 文档修订 不增计数；前置 knife 65 已落 4 public JSON 拷贝入 pack 694 → 700）。

## 红线自查

- ❌ 未谎称深圳城页数据 = 公报 extract（链旁显式「mock 观察卡与公报散文轨互不覆盖」+「样本来自 registry 锚定的本地 spike，REGISTRY_SAMPLE demo，非 O1 收口」+「两者皆 demo，非 O1」三处守门）
- ❌ 未改 fixture 字节（4 fixture 未动）
- ❌ 未无条件链接（条件分支严格 shenzhen slug/cityId 命中才渲染；pytest `test_other_cities_do_not_render_link_unconditionally` 锁定链必须出现在条件之后）
- ❌ 未覆盖/删减既有 10 城 mock 列表（per Cursor 锁定）
- ❌ 未跑任何 live 探测 / 未改 registry `enabled` 列 / 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json`
- ❌ 未 Gate/O1 PASS 宣告；未 --force；未索要 PAT
- ✅ 链接带 demo/REGISTRY_SAMPLE 提示（链旁 + 标题 + 守门三处明示）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`

## 下一步

`git push origin HEAD && git push github HEAD` → `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 393）。