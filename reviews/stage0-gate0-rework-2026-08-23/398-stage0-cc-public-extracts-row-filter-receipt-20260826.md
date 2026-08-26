# 398 — /public-extracts 四轨轻量行筛选 · CC 回执

- 编号：`398-stage0-cc-public-extracts-row-filter-receipt-20260826`
- 任务书：`397-stage2-public-extracts-row-filter-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`13501f8`
- 日期：2026-08-26

---

## §NOW 对照

| 397 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) 各数据表上方（或一览条下）增轻量行筛选：单输入框，按单元格文本包含匹配过滤当前可见表；**优先每轨独立 input** | ✅ 四个数据表（NBS sample 提取表 / NBS live 候选提取表 / 深圳散文段落表 / 湖北月报统计表）**各自独立** input（`TrackFilterInput` 受控组件，`testId="track-filter-{nbs-sample,nbs-live,sz,hb}"` 渲染为 `data-testid`）；过滤 = `filterRows` 单元格文本包含匹配（`toLowerCase().includes`，大小写不敏感，空查询=全量）；每轨独立 `useState`，互不影响；匹配计数行「匹配 X / Y 行」+ 空匹配占位行「无匹配行 — 客户端筛选 demo 数据, 非权威库检索; 清空输入恢复全量」 | diff + build |
| (2) 纯客户端，不改 fixture 字节 | ✅ 页面加 `"use client"`（仍 ○ Static prerender，22/22 生成）；`fetch(` 零出现（pytest 锁定）；4 个 lib fixture 与 public 下载拷贝字节未动（§12g 字节一致门仍绿）；tbody 消费 `filtered*Rows` 视图数组，不改数据/SHA/列序 | smoke §12g + pytest |
| (3) ≥2 pytest/smoke 针（input 在位 + 过滤逻辑或 data-testid） | ✅ **3 pytest case + smoke §12h 门（11 针）**：<br>• `test_track_filter_inputs_present_per_track` — 4 个 `testId="track-filter-…"` prop + `data-testid={props.testId}` 渲染 + 4 个受控 `value={…Filter}` 绑定 + 匹配计数行；<br>• `test_track_filter_logic_contains_match_client_side` — `"use client"` + `filterRows(` + `.toLowerCase().includes(` + 4 个 `filtered*.length === 0` 空匹配分支 + 4 个 `filtered*.map(` tbody 消费 + 4 个 fixture import 原样 + `fetch(` 不出现；<br>• `test_track_filter_disclaimer_and_empty_state` — 非权威库检索 + 视图过滤 + 无匹配行占位 + demo/candidate 标注仍在 + `O1_AUTO_INTAKED` 不出现；<br>• smoke §12h — use client / useState / data-testid 渲染 / 4 testId / toLowerCase().includes / 匹配计数 / 非权威库检索 / 无匹配行 | pytest + smoke |
| (4) 回执 `398`（`-cc-`） | ✅ 本文件名 | — |

## 证据

```
$ python3 -m pytest tests/test_public_extract_frontend_fixture.py \
                    tests/test_shenzhen_city_link_public_extract.py \
                    tests/test_hubei_home_link_public_extract.py \
                    tests/test_auto_ingest_public_source_s52.py -q
118 passed in 2.35s                      # 27 + 3 + 2 + 86 = 118 全绿
                                          # (fixture 文件 24 → 27: +3 行筛选 case)

$ python3 frontend/smoke-check.py
✅ public-extracts/page.tsx: 四轨行筛选 input (testid ×4) + 客户端包含匹配 + 非权威库检索守门
✅ public-extracts/page.tsx: 下载 JSON 列 + 4 download 链 (… §12g 字节一致门仍绿)
=== … smoke: PASS ===

$ cd frontend && npm run build
✓ Compiled successfully
✓ Generating static pages (22/22)
├ ○ /public-extracts    15.8 kB   103 kB   # 仍 ○ Static (use client 不破静态)

$ python3 scripts/_knife68_manifest_bump.py
ADD: scripts/_knife68_manifest_bump.py (…)
ADD: reviews/.../398-…-receipt-20260826.md (…)
UPDATE artifact_count: 706 → 708
INVARIANT: sum(role_count)=708 == artifact_count=708 == len(artifacts)=708
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `frontend/app/public-extracts/page.tsx` | MODIFIED（`"use client"` + 4 `useState` + `filterRows` + `TrackFilterInput` + 4 数据表筛选 input + 4 tbody 改消费 filtered 数组 + 空匹配占位行） | 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例） |
| `frontend/smoke-check.py` | MODIFIED（+ §12h 门，11 针） | 已入 manifest（SKIP） |
| `tests/test_public_extract_frontend_fixture.py` | MODIFIED（+3 cases: 24 → 27） | 已入 manifest（SKIP） |
| `scripts/_knife68_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../398-stage0-cc-public-extracts-row-filter-receipt-20260826.md` | NEW（本文件） | `documentation` |

## Pack 不变量

`_knife68_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **706 → 708**；`sum(role_count) == artifact_count == len(artifacts) == 708`（page.tsx / smoke-check.py / 测试文件皆已入 manifest，SHA REFRESH 不增计数；前置 knife 67 已落 703 → 706）。

## 红线自查

- ❌ 未改 4 个 lib fixture / 4 个 public 下载 JSON 字节（§12g 字节一致门 + pytest byte-identical case 仍绿）
- ❌ 未改 SHA / 列序 / 行数（过滤仅为视图层，tbody 消费 filtered 数组）
- ❌ 未谎称筛选结果=权威库（筛选行显式「非权威库检索」「视图过滤」「不改数据 / SHA」，pytest + smoke 双锁定）
- ❌ 未破坏 demo 标注（REGISTRY_SAMPLE / LIVE_CANDIDATE 标注在表外不受筛选影响；空匹配行重复守门）
- ❌ 未引入新源 / 运行时抓取（`fetch(` 不出现，pytest 锁定）/ 未用重型表格库（纯受控 input + filter）
- ❌ 未跑 live 探测 / 未动 registry `enabled` / 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json`
- ❌ 未 Gate/O1 PASS 宣告；未 --force；未索要 PAT；未碰 params.*（静态路由不变，build ○ 证实）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 399）。
