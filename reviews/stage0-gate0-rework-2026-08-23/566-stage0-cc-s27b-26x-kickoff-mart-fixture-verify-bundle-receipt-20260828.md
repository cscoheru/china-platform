# 566 — 合刀：26X 轴 kickoff 登记 + mart-shape 预览路径实跑证据 · CC 回执

- 编号：`566-stage0-cc-s27b-26x-kickoff-mart-fixture-verify-bundle-receipt-20260828`
- 任务书：`566-stage2-s27b-full-26x-kickoff-mart-fixture-verify-bundle-tasking-20260828`（gate queue_rev 315；合刀：一把任务书多步、一个回执）
- 前置：`565` PASS（audit 565；564 闭环完成）；用户分叉裁定：**先 26X → 保持 C（合刀）→ 再 O1**
- 作者：CC（heartbeat 84）
- cc_head：`6205081`（双推 origin/github ad4625b..6205081；cc_head backfill 单独 commit 再双推）
- 日期：2026-08-28

---

## §NOW 对照

| 566 tasking §NOW / gate 315 NOW | 交付 | 证据 |
|---|---|---|
| (A) docs/53 §5 新增第 34 项：26X 轴 kickoff 登记（用户分叉 = 先 26X·合刀·再 O1；S2.7-b-full 去 demo 预览路径 = `NEXT_PUBLIC_USE_MART_FIXTURE=1` 看 mart-shape 管道；真 mart 真 SHA / person 真数据仍 OPEN → O1 后另刀） | ✅ 第 34 项已插第 33 项后：「26X 轴 kickoff 登记（用户分叉 = 先 26X·合刀·再 O1；本条为登记节点，非 O1 收口）」；第 21–33 项既有 blockquote 正文原样未动 | grep（本文件证据段） |
| (B) docs/45 文首/§1/§6.2/§7 四处同步（26X 为活跃轴 + O1 defer 序列） | ✅ 文首 queue_rev 315 刷新行（「knife 76…148 锁链延续」）+ §1 新段 + §6.2 行尾注 append + §7 链头 880 == 880 == 880（knife 564 demote 链完整） | grep（本文件证据段） |
| (C) docs/50 §4.4 里程碑行补登第 34 项 + intro ⚠ 收据链尾续接（链尾以本刀里程碑收口） | ✅ 第 34 项行已插第 33 项行后、预览 URL 段前；intro 链尾 `→ 562` 续接 `→ 566`（链尾以 `566` 收口）；里程碑表 21–33 行正文原样未动 | grep（本文件证据段） |
| (D) 实跑 mart-shape 预览路径守门：pytest `test_mart_city_types_s27bf.py` + `test_frontend_mart_demo_parity_s296.py` + `frontend/smoke-check.py`（§10a–§10e 须 PASS） | ✅ **30 passed / exit 0** + **smoke PASS / exit 0**（§10a–§10e mart-shape 门全 PASS）；命令 + exit code + 关键 stdout 本文件证据段原样粘贴 | 本文件证据段 |
| (E) 回执 **仅 `566`**（`-cc-`） | ✅ 合刀单槽单回执：`_knife566` bump + 本回执（仅此一个回执号）→ 878 → 880；本文件名含 `-cc-` | bump 输出（本文件证据段） |
| (3) **必须双推** → POLL | ✅ 双推 origin + github（范围见 backfill）；backfill cc_head 单独 commit 再双推 | push 输出（会话记录） |

## 证据

### 实跑命令 + exit code + 关键 stdout（原样粘贴，per tasking D）

```
$ python3 -m pytest tests/test_mart_city_types_s27bf.py tests/test_frontend_mart_demo_parity_s296.py -q
..............................                                           [100%]
30 passed in 0.26s
PYTEST_EXIT=0

$ python3 frontend/smoke-check.py
✅ mart_city_types.ts: SHA256 placeholder = '0'.repeat(64)                （§10a）
✅ mart_city_demo.ts references CITY_SLUG_LIST                             （§10b）
✅ mart_city_demo.ts reuses MART_LINEAGE_PLACEHOLDER_SHA (= '0'*64)        （§10b）
✅ mart_city_demo.ts covers 10 cities (via_import=True, literal_hits=0/10) （§10b）
✅ CityPageMart.tsx reuses EvidenceChain + SevenDimGrid + PeerCompareCard  （§10d）
✅ [slug]/page.tsx declares NEXT_PUBLIC_USE_MART_FIXTURE feature-flag      （§10e）
✅ [slug]/page.tsx defaults to getMockCity (mock path 保留)                 （§10e）
✅ [slug]/page.tsx opt-in mart-shape path (getMartCityDemo)                （§10e）
✅ [slug]/page.tsx imports CityPageMart                                    （§10e）
（10c 禁词守门：app/page.tsx 无 score/rating/rank/total_score/confidence_score/peer_rank 禁词，全部 ✅）
=== S2.0.1 + S2.7-a + S2.7-a2 + S2.7-b-lite + S2.7-b-full-lite mart-shape + home nav (S2.7-a + S2.7-b + S2.8-lite + S2.9-lite, per tasking 280) smoke: PASS ===
SMOKE_EXIT=0
```

### 文档锚点 + 计数

```
$ grep -cF 锚点
  docs/53:「第 34 项（此条）· 26X 轴 kickoff 登记」                          = 1
  docs/50:「第 34 项 26X 轴 kickoff 登记**（26X 活跃轴里程碑行；per 回执 `566` 落地」= 1
  docs/50 intro:「→ `510` → `512` → `548` → `556` → `562` → `566`；16–19」  = 1
  docs/50 intro:「链尾以 `566` 收口）；」                                    = 1
  docs/50 stale:「，链尾以 `562` 收口）；」                                  = 0  （已由链尾续接承接）
  docs/45 文首:「queue_rev 315（per `566-stage2-s27b-full-26x-kickoff-mart-fixture-verify-bundle-tasking-20260828`）」= 1
  docs/45 文首:「knife 76…148 锁链延续」                                    = 1
  docs/45 §1:「**26X 轴 kickoff + mart-shape 预览路径实跑证据（per `566`）**」= 1
  docs/45 §6.2:「26X 轴 kickoff + mart-shape 预览路径实跑证据（合刀 per `566`」= 1
  docs/45 §7:「880 == 880 == 880」                                          = 1
  docs/45 §7 demote:「knife 564 = 合刀 A+B+C 同 commit、单槽单回执」          = 1
  docs/45:stale「878 == 878 == 878」                                        = 0  （已由 §7 链头更新承接）

$ grep -c/-o "O1 仍 OPEN" 计数核验（非减）
  docs/45 行计数 96（由 95 增至 96）、出现计 147（由 144 增至 147）
  docs/50 行计数 16（由 15 增至 16）、出现计 17（由 16 增至 17）
  docs/53 行计数 14（由 13 增至 14）、出现计 16（由 15 增至 16）

$ python3 -c 残留转义检查 chr(92)+chr(96)
  docs/45 = 0、docs/50 = 0、docs/53 = 0

$ shasum -a 256 frontend/lib/public_extract_{nbs,nbs_live_candidate,sz,hubei}.json | cut -c1-8
  e30ee811 9232efdb 937255a5 9056001c   （disk == 锁值，4 fixture 字节未动）

$ python3 scripts/_knife566_manifest_bump.py
ADD: scripts/_knife566_manifest_bump.py (4175 bytes, sha=6875bcd2)
ADD: reviews/stage0-gate0-rework-2026-08-23/566-stage0-cc-s27b-26x-kickoff-mart-fixture-verify-bundle-receipt-20260828.md (10686 bytes, sha=cb59f9dc)
UPDATE artifact_count: 878 → 880
INVARIANT: sum(role_count)=880 == artifact_count=880 == len(artifacts)=880
OK manifest updated; added 2 artifacts
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 新增第 34 项 26X kickoff 登记 blockquote；第 21–33 项既有 blockquote 正文原样未动）| 已入 manifest（SHA REFRESH 不增计数）|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | MODIFIED（§4.4 里程碑表 +1 第 34 项行 + intro ⚠ 收据链尾续接 `→ 566`；第 21–33 项行既有正文原样未动）| 已入 manifest（SHA REFRESH 不增计数）|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 +1 刷新行 queue_rev 315 + §1 +1 段 + §6.2 行尾注 + §7 链头更新）| 已入 manifest（SHA REFRESH 不增计数）|
| `scripts/_knife566_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../566-stage0-cc-s27b-26x-kickoff-mart-fixture-verify-bundle-receipt-20260828.md` | NEW（本文件）| `documentation` |

注：本刀 registry.csv 零触碰（任务书「不做改 registry」）；未 mart 真 SHA 入仓、未 person/tenure 真数据替换、未 `NEXT_PUBLIC_USE_MOCK=false` 公网 redeploy；D 实跑 = 本地 pytest + smoke-check（零网络写副作用）；docs/52 零触碰；未跟踪运行产物维持不入 manifest 房规。

## Pack 不变量

`_knife566_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **878 → 880**；`sum(role_count) == artifact_count == len(artifacts) == 880`（docs/45/docs/50/docs/53 已入 manifest，SHA REFRESH 不增计数；前置 knife 564 回执 `564` 已落 876 → 878；knife 562 `562` 已落 874 → 876；knife 560 `560` 已落 872 → 874；knife 558 `558` 已落 870 → 872；knife 556 `556` 已落 868 → 870；knife 554 `554` 已落 866 → 868；knife 552 `552` 已落 864 → 866；knife 550 `550` 已落 862 → 864；knife 548 `548` 已落 860 → 862；knife 546 `546` 已落 858 → 860；knife 544 `544` 已落 856 → 858；knife 542 `542` 已落 854 → 856；knife 540 `540` 已落 852 → 854；knife 538 `538` 已落 850 → 852；knife 536 `536` 已落 848 → 850；knife 534 `534` 已落 846 → 848；knife 532 `532` 已落 844 → 846；knife 530 `530` 已落 842 → 844；knife 528 `528` 已落 840 → 842；knife 526 `526` 已落 838 → 840；knife 524 `524` 已落 836 → 838；knife 522 `522` 已落 834 → 836；knife 520 `520` 已落 832 → 834；knife 518 `518` 已落 830 → 832；knife 516 `516` 已落 828 → 830；knife 514 `514` 已落 826 → 828；knife 512 `512` 已落 824 → 826；knife 510 `510` 已落 822 → 824；knife 508 `508` 已落 820 → 822；knife 506 `506` 已落 818 → 820；knife 504 `504` 已落 816 → 818；knife 502 `502` 已落 814 → 816；knife 500 `500` 已落 812 → 814；knife 498 `498` 已落 810 → 812；knife 496 `496` 已落 808 → 810；knife 494 `494` 已落 806 → 808；knife 492 `492` 已落 804 → 806；knife 490 `490` 已落 802 → 804；knife 488 `488` 已落 800 → 802；knife 486 `486` 已落 798 → 800；knife 484 `484` 已落 796 → 798；knife 105 `478` 已落 790 → 792；knife 104 `476` 已落 788 → 790；knife 103 `474` 已落 786 → 788；knife 102 `472` 已落 784 → 786）。

## 红线自查

- ❌ 未做 Gate/O1 PASS 宣告：**`NEXT_PUBLIC_USE_MART_FIXTURE=1` 预览 = demo mart-shape 管道——非 O1 收口，O1 收口须用户/Cursor 裁定，O1 仍 OPEN（defer 至 26X 后用户序列）**，docs/53 第 34 项 + docs/50 第 34 项行/intro + docs/45 四处 + 本回执写明
- ❌ 未改 registry（本刀零触碰）；未 mart 真 SHA 入仓；未 person/tenure 真数据替换；未 `NEXT_PUBLIC_USE_MOCK=false` 公网 redeploy
- ❌ 未删减 OPEN（docs/45 95→96 行 / 144→147 处；docs/50 15→16 行 / 16→17 处；docs/53 13→14 行 / 15→16 处，均不减）
- ❌ 未动 4 frontend fixture 字节（实测锁值一致：e30ee811 / 9232efdb / 937255a5 / 9056001c）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ❌ 未谎称 mart/O1 已收口；未静默失败（D 实跑 exit 0 原样粘贴）；未交两个回执号（合刀单槽单回执，回执仅 `566` 一个）
- ⚠ 红线重申：**合刀单槽单回执；MART_FIXTURE 预览 = demo mart-shape 管道（非 O1 收口）；O1 defer 至 26X 后用户序列**（per tasking 红线段）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执/任务书号 + 简短语）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `bash scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `566`）。
