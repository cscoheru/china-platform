# 428 — docs/50 §4.4 补登首页 deeplink 里程碑 · CC 回执

- 编号：`428-stage0-cc-docs50-home-deeplinks-milestone-receipt-20260826`
- 任务书：`428-stage2-docs50-home-deeplinks-milestone-refresh-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`10f26cf`
- 日期：2026-08-26

---

## §NOW 对照

| 428 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/50` §4.4 里程碑表补 2 行：首页 NBS sample `#track-nbs-sample`（回执 `420`）+ 首页 NBS live `#track-nbs-live`（回执 `424`）；链 `docs/45`/`53` | ✅ `docs/50-stage2-gate2-review-packet-draft-20260826.md` §4.4 里程碑表末尾（docs/45+53 同步登记行后）新增 2 行：<br>(a) **首页 NBS sample 轨显式 deeplink**（per 回执 `420` + cc_head backfill `bee7950`）：`frontend/app/page.tsx` 公开提取表内「公开提取样本（四轨 demo）」行 → 「公开提取 NBS sample 轨（demo）」行；href `/public-extracts` → `/public-extracts#track-nbs-sample` + `data-testid="home-public-extracts-nbs-sample"` + 数据模式 `REGISTRY_SAMPLE · demo · 非 live O1`；结构镜像湖北 `#track-hb` 行（per knife 67 tasking 394）；纯 `<a href>` 锚链未引入 `next/link`（保留 build ○ Static 22/22）；不分支 `params.*`（AGENTS.md 静态路由红线）；链 docs/45 §1 + §6.2 + §7 + docs/53 §5；smoke §12b' 4 针（href + testId + REGISTRY_SAMPLE / demo / 非 live O1）+ pytest 3 cases `tests/test_nbs_home_deeplink_public_extract.py` + 4 fixture byte SHA 前 8 锁不漂：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`<br>(b) **首页 NBS live 候选轨显式 deeplink**（per 回执 `424` + cc_head backfill `29467c4`）：`frontend/app/page.tsx` NBS sample 行后新增「公开提取 NBS live 候选轨（candidate demo）」行；href `/public-extracts#track-nbs-live` + `data-testid="home-public-extracts-nbs-live"`；描述列「stats.gov.cn / NATIONAL_BULLETIN 60 行（WORM `zxfb` LIVE_CANDIDATE 提取；drift 候选；per 回执 `359` / `362`）」；数据模式标 `LIVE_CANDIDATE · drift 候选 · 非 O1 收口`；与 NBS sample 行同表内并列（镜像 knife 76 NBS sample 行 + knife 67 湖北 `#track-hb` 行模板）；不引入 `next/link`；不分支 `params.*`；链 docs/45 §1 + §6.2 + §7 + docs/53 §5；smoke §12b'' 4 针 + pytest 3 cases `tests/test_nbs_live_home_deeplink_public_extract.py` + 4 fixture byte SHA 锁与 knife 76 完全一致 | diff |
| (2) 非 O1/Gate PASS | ✅ 2 行末尾均标注「**drift 候选非 O1 收口**」+ 「**非 O1/Gate PASS**」；与 §4.4 文首 ⚠ 守门一致（四轨皆 demo/candidate 演示）；5 条 ⚠「预览路径不构成 O1 / Gate 2 收口」原样保留 | diff |
| (3) 回执 `428`（`-cc-`）| ✅ 本文件名 | — |

## 证据

```
$ grep -n "首页 NBS sample 轨显式 deeplink\|首页 NBS live 候选轨显式 deeplink\|420\|424" docs/50-stage2-gate2-review-packet-draft-20260826.md | head -20
  196:| **首页 NBS sample 轨显式 deeplink**（首页表内显式锚链演示）| ... | `420` + `bee7950` | ...
  197:| **首页 NBS live 候选轨显式 deeplink**（首页表内显式锚链演示，drift 候选非 O1 收口）| ... | `424` + `29467c4` | ...

$ python3 scripts/_knife80_manifest_bump.py
ADD: scripts/_knife80_manifest_bump.py (…)
ADD: reviews/.../428-…-receipt-20260826.md (…)
UPDATE artifact_count: 739 → 741
INVARIANT: sum(role_count)=741 == artifact_count=741 == len(artifacts)=741
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | MODIFIED（§4.4 里程碑表 +2 行；末尾 docs/45+53 同步登记行后）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife80_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../428-stage0-cc-docs50-home-deeplinks-milestone-receipt-20260826.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife80_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **739 → 741**；`sum(role_count) == artifact_count == len(artifacts) == 741`（docs/50 已入 manifest，SHA REFRESH 不增计数；前置 knife 78 + knife 79 已落 734 → 737 → 739）。

## docs/50 §4.4 互链对账

| docs/50 §4.4 新增行 | 内容 | 指向 knife |
|---|---|---|
| **首页 NBS sample 轨显式 deeplink**（行 196）| href `/public-extracts#track-nbs-sample` + testId + REGISTRY_SAMPLE demo + smoke §12b' 4 针 + pytest 3 cases + 4 fixture SHA 锁 | ✅ 链 knife 76 tasking 420 + docs/45 §1 + §6.2 + §7 + docs/53 §5 |
| **首页 NBS live 候选轨显式 deeplink**（行 197）| href `/public-extracts#track-nbs-live` + testId + LIVE_CANDIDATE drift 候选 + smoke §12b'' 4 针 + pytest 3 cases + 4 fixture SHA 锁与 knife 76 一致 | ✅ 链 knife 78 tasking 424 + docs/45 §1 + §6.2 + §7 + docs/53 §5 |

## 红线自查

- ❌ 未改代码（docs only per §NOW；knife 76 + knife 78 page.tsx 改动已在 `420`/`424` 闭环）
- ❌ 未删减 OPEN（§5.1/§5.4 OPEN 清单原样；5 条 ⚠「预览路径不构成 O1 / Gate 2 收口」原样保留；仅增不改）
- ❌ 未 Gate/O1 PASS 宣告（2 行末尾均显式「非 O1/Gate PASS」+ 「drift 候选非 O1 收口」+ §4.4 文首 ⚠ 守门保留）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ docs/45 + docs/53 已分别在 knife 77 (回执 422) + knife 79 (回执 426) 登记；本刀 docs/50 §4.4 链接两侧双向对账
- ✅ 4 fixture byte SHA 前 8 锁在 receipt 中显式列出（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与 knife 76 + knife 78 完全一致，fixture 字节保持不变）
- ✅ docs/50 §4.4 链 docs/45 §1 + §6.2 + §7 + docs/53 §5（双向，docs/45 §7 pack invariant 链亦指向 docs/50 §4.4）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `428`）。
