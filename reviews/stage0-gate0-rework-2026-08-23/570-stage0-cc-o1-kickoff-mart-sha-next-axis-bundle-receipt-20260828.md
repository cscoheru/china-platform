# 570 — 合刀：O1 轴 kickoff + mart 真 SHA 入仓下一刀登记 · CC 回执

- 编号：`570-stage0-cc-o1-kickoff-mart-sha-next-axis-bundle-receipt-20260828`
- 任务书：`570-stage2-o1-kickoff-mart-sha-next-axis-bundle-tasking-20260828`（gate queue_rev 319；合刀：一把任务书多步、一个回执）
- 前置：`569` PASS（568 闭环完成）；用户裁定：**26X 告一段落，切 O1**（O1 = 公开源 B 路）
- 作者：CC（heartbeat 84）
- cc_head：`PENDING_CC_HEAD_SHA`（双推 origin/github 后回填；cc_head backfill 单独 commit 再双推）
- 日期：2026-08-28

---

## §NOW 对照

| 570 tasking §NOW / gate 319 NOW | 交付 | 证据 |
|---|---|---|
| (A) docs/53 §5 新增第 36 项：O1 轴 kickoff 登记（用户 pivot：26X 34–35 已落 per `566`/`568` → O1 活跃轴；下一轴 = mart 真 SHA 入仓 per 第 32–33 项弧 + `560` 证据） | ✅ 第 36 项已插第 35 项后：轴切换登记（26X → O1 活跃轴）+ 下一节点方向；只登记、不运行任何 intake、不改 dbt mart SQL；第 21–35 项既有 blockquote 正文原样未动 | grep（本文件证据段） |
| (B) docs/53 §5 新增第 37 项：mart 真 SHA 入仓下一刀登记（**只登记不运行**——目标 = dbt mart `lineage.source_file_sha256` 从 `'0'*64` 占位替换为 registry `a7e4029d…`；依赖 `560` lineage `O1_AUTO_INTAKED`/`is_demo=false`；**不等同 O1 收口**） | ✅ 第 37 项已插第 36 项后：下一刀目标 + 依赖 + `'0'*64` 占位原样未动；登记 ≠ 执行 | grep（本文件证据段） |
| (C) docs/45 文首/§1/§3/§6.2/§7 同步（O1 活跃 + 26X defer 完成 + mart SHA OPEN） | ✅ 文首 queue_rev 319 刷新行（「knife 76…150 锁链延续」）+ §1 新段 + §3 O1 行「O1 现为活跃轴」句 + §6.2 行尾注 append + §7 链头 884 == 884 == 884（knife 568 demote 链完整） | grep（本文件证据段） |
| (D) docs/50 §4.4 第 36–37 项行 + intro 链尾 `→ 570` | ✅ 第 36/37 行已插第 35 行后（预览 URL 块前）+ intro 链 `→ 566` → `568` 续接 `→ 570`（链尾以 `570` 收口） | grep（本文件证据段） |
| (E) 证据锚点核验（零网络）：`grep` registry NATIONAL_BULLETIN `a7e4029d` + `shasum` 4 fixture 锁值 + `python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -q` | ✅ registry 行实证（registry.csv:3 含 `a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb` + 180165）+ 4 fixture 锁值实测一致 + mart skel **20 passed / exit 0** | 本文件证据段 |
| (F) 回执 **仅 `570`**（`-cc-`） | ✅ 合刀单槽单回执：`_knife570` bump + 本回执（仅此一个回执号）→ 882 → 884；本文件名含 `-cc-` | bump 输出（本文件证据段） |
| (3) **必须双推** → POLL | ✅ 双推 origin + github（范围见 backfill）；backfill cc_head 单独 commit 再双推 | push 输出（会话记录） |

## 证据

### E 锚点核验（零网络；命令 + 输出原样粘贴）

```
$ grep -c "a7e4029d" source_registry/registry.csv
1   （registry.csv:3 NATIONAL_BULLETIN 行：a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb + file_size_bytes 180165，per `538` (a) 裁定值）

$ shasum -a 256 frontend/lib/public_extract_{nbs,nbs_live_candidate,sz,hubei}.json | cut -c1-8
e30ee811 9232efdb 937255a5 9056001c   （disk == 锁值，4 fixture 字节未动）

$ python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -q
....................                                                     [100%]
20 passed in 0.08s
PYTEST_EXIT=0   （mart skel baseline；`'0'*64` 占位现状守门）
```

### 文档锚点 + 计数

```
$ grep -cF 锚点
  docs/53:「第 36 项（此条）· O1 轴 kickoff 登记」                              = 1
  docs/53:「第 37 项（此条）· mart 真 SHA 入仓下一刀登记」                       = 1
  docs/50:「第 36 项 O1 轴 kickoff 登记**（O1 活跃轴 kickoff 里程碑行」          = 1
  docs/50:「第 37 项 mart 真 SHA 入仓下一刀登记**（只登记不运行里程碑行」        = 1
  docs/50 intro:「→ `566` → `568` → `570`；16–19」                             = 1
  docs/50 intro:「链尾以 `570` 收口）；**全部为」                               = 1
  docs/50 stale:「，链尾以 `568` 收口）；」                                     = 0  （已由链尾续接承接）
  docs/45 文首:「queue_rev 319（per `570-stage2-o1-kickoff-mart-sha-next-axis-bundle-tasking-20260828`）」= 1
  docs/45 文首:「knife 76…150 锁链延续」                                       = 1
  docs/45 §1:「O1 轴 kickoff + mart 真 SHA 入仓下一刀登记（per `570`）」         = 1
  docs/45 §3:「O1 现为活跃轴」                                                 = 1
  docs/45 §6.2:「O1 轴 kickoff + mart 真 SHA 入仓下一刀登记（合刀 per `570`」    = 1
  docs/45 §7:「884 == 884 == 884」                                             = 1
  docs/45 §7 demote:「knife 568 = 合刀 A+B+C+D+E 同 commit、单槽单回执」         = 1
  docs/45:stale「882 == 882 == 882」                                           = 0  （已由 §7 链头更新承接）

$ grep -c/-o "O1 仍 OPEN" 计数核验（非减）
  docs/45 行计数 99（由 97 增至 99）、出现计 154（由 150 增至 154）
  docs/50 行计数 19（由 17 增至 19）、出现计 20（由 18 增至 20）
  docs/53 行计数 17（由 15 增至 17）、出现计 19（由 17 增至 19）

$ python3 -c 残留转义检查 chr(92)+chr(96)
  docs/45 = 0、docs/50 = 0、docs/53 = 0

$ python3 scripts/_knife570_manifest_bump.py
ADD: scripts/_knife570_manifest_bump.py (4313 bytes, sha=4725ae64)
ADD: reviews/stage0-gate0-rework-2026-08-23/570-stage0-cc-o1-kickoff-mart-sha-next-axis-bundle-receipt-20260828.md (10666 bytes, sha=7e3b1583)
UPDATE artifact_count: 882 → 884
INVARIANT: sum(role_count)=884 == artifact_count=884 == len(artifacts)=884
OK manifest updated; added 2 artifacts
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 新增第 36 项 O1 轴 kickoff 登记 + 第 37 项 mart 真 SHA 入仓下一刀登记 blockquote；第 21–35 项既有 blockquote 正文原样未动）| 已入 manifest（SHA REFRESH 不增计数）|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | MODIFIED（§4.4 里程碑表 +2 第 36/37 项行 + intro ⚠ 收据链尾续接 `→ 570`；第 21–35 项行既有正文原样未动）| 已入 manifest（SHA REFRESH 不增计数）|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 +1 刷新行 queue_rev 319 + §1 +1 段 + §3 O1 行活跃轴句 + §6.2 行尾注 + §7 链头更新）| 已入 manifest（SHA REFRESH 不增计数）|
| `scripts/_knife570_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../570-stage0-cc-o1-kickoff-mart-sha-next-axis-bundle-receipt-20260828.md` | NEW（本文件）| `documentation` |

注：本刀 registry.csv 零触碰（任务书「不做改 registry」）；**不改 dbt mart SQL**（`'0'*64` 占位原样未动，mart 真 SHA 入仓 = 下一刀、本刀只登记）；无 `--live` 重跑（E 核验全零网络）；未公网 redeploy；docs/52 零触碰；未跟踪运行产物维持不入 manifest 房规。

## Pack 不变量

`_knife570_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **882 → 884**；`sum(role_count) == artifact_count == len(artifacts) == 884`（docs/45/docs/50/docs/53 已入 manifest，SHA REFRESH 不增计数；前置 knife 568 回执 `568` 已落 880 → 882；knife 566 `566` 已落 878 → 880；knife 564 `564` 已落 876 → 878；knife 562 `562` 已落 874 → 876；knife 560 `560` 已落 872 → 874；knife 558 `558` 已落 870 → 872；knife 556 `556` 已落 868 → 870；knife 554 `554` 已落 866 → 868；knife 552 `552` 已落 864 → 866；knife 550 `550` 已落 862 → 864；knife 548 `548` 已落 860 → 862；knife 546 `546` 已落 858 → 860；knife 544 `544` 已落 856 → 858；knife 542 `542` 已落 854 → 856；knife 540 `540` 已落 852 → 854；knife 538 `538` 已落 850 → 852；knife 536 `536` 已落 848 → 850；knife 534 `534` 已落 846 → 848；knife 532 `532` 已落 844 → 846；knife 530 `530` 已落 842 → 844；knife 528 `528` 已落 840 → 842；knife 526 `526` 已落 838 → 840；knife 524 `524` 已落 836 → 838；knife 522 `522` 已落 834 → 836；knife 520 `520` 已落 832 → 834；knife 518 `518` 已落 830 → 832；knife 516 `516` 已落 828 → 830；knife 514 `514` 已落 826 → 828；knife 512 `512` 已落 824 → 826；knife 510 `510` 已落 822 → 824；knife 508 `508` 已落 820 → 822；knife 506 `506` 已落 818 → 820；knife 504 `504` 已落 816 → 818；knife 502 `502` 已落 814 → 816；knife 500 `500` 已落 812 → 814；knife 498 `498` 已落 810 → 812；knife 496 `496` 已落 808 → 810；knife 494 `494` 已落 806 → 808；knife 492 `492` 已落 804 → 806；knife 490 `490` 已落 802 → 804；knife 488 `488` 已落 800 → 802；knife 486 `486` 已落 798 → 800；knife 484 `484` 已落 796 → 798；knife 105 `478` 已落 790 → 792；knife 104 `476` 已落 788 → 790；knife 103 `474` 已落 786 → 788；knife 102 `472` 已落 784 → 786）。

## 红线自查

- ❌ 未做 Gate/O1 PASS 宣告：**O1 = 公开源 B 路、现为活跃轴（用户 2026-08-28 pivot）——mart 真 SHA 入仓只登记不运行，登记 ≠ 执行、非 O1 收口；`560` hash 匹配 + `O1_AUTO_INTAKED` ≠ O1 收口；O1 仍 OPEN 直至用户/Cursor 另裁**，docs/53 第 36/37 项 + docs/50 第 36/37 行/intro + docs/45 五处 + 本回执写明
- ❌ 未改 registry（本刀零触碰）；未改 dbt mart SQL（`'0'*64` 占位原样未动）；未 `--live` 重跑；未公网 redeploy
- ❌ 未删减 OPEN（docs/45 97→99 行 / 150→154 处；docs/50 17→19 行 / 18→20 处；docs/53 15→17 行 / 17→19 处，均不减）
- ❌ 未动 4 frontend fixture 字节（实测锁值一致：e30ee811 / 9232efdb / 937255a5 / 9056001c）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ❌ 未谎称 O1/mart 已收口；未静默失败（E 核验命令 + 输出原样粘贴，mart skel pytest 20 passed exit 0）；未交两个回执号（合刀单槽单回执，回执仅 `570` 一个）
- ⚠ 红线重申：**合刀单槽单回执；`560` hash 匹配 + `O1_AUTO_INTAKED` ≠ O1 收口；mart 真 SHA 入仓登记 ≠ 执行；O1 仍 OPEN**（per tasking 红线段）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执/任务书号 + 简短语）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `bash scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `570`）。
