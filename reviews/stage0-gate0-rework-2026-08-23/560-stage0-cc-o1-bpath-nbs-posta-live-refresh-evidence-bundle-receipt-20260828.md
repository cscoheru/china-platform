# 560 — 合刀：post-(a) live refresh 实跑 + docs/53 第 33 项 + docs/45 四处 · CC 回执

- 编号：`560-stage0-cc-o1-bpath-nbs-posta-live-refresh-evidence-bundle-receipt-20260828`
- 任务书：`560-stage2-o1-bpath-nbs-posta-live-refresh-evidence-bundle-tasking-20260828`（gate queue_rev 308；合刀：一把任务书多步、一个回执）
- 前置：`559` PASS（audit 559；558 闭环完成）
- 作者：CC（heartbeat 84）
- cc_head：`3ec4ec8`（双推 origin/github 432d66f..3ec4ec8；cc_head backfill 单独 commit 再双推）
- 日期：2026-08-28

---

## §NOW 对照

| 560 tasking §NOW / gate 308 NOW | 交付 | 证据 |
|---|---|---|
| (A) post-(a) `--live` refresh 实跑（有网络；写 lineage；期望 hash 匹配 registry `a7e4029d…`） | ✅ **exit 0**；download 180165 字节 sha256 = `a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb` **== registry 期望值（hash 匹配实测，post-(a) 裁定值验证成立）**；archived + extract 6 表行 + lineage 写入任务书指定路径 | 本文件证据段（命令 + stdout 原样粘贴） |
| (B) docs/53 §5 新增第 33 项 blockquote（post-(a) live refresh 证据；非 O1 收口） | ✅ 第 33 项已插第 32 项后：命令 + exit 0 + deeplink + 字节 + 全 SHA + hash 匹配实测 + lineage `O1_AUTO_INTAKED` + `is_demo=false` 首个非 demo 实测入库；红线句「hash 匹配 ≠ O1 收口——O1 收口须用户/Cursor 裁定，本刀不宣布」 | grep（本文件证据段） |
| (C) docs/45 文首/§1/§6.2/§7 四处同步 | ✅ 文首 queue_rev 308 刷新行（「knife 76…145 锁链延续」）+ §1 实跑证据句 + §6.2 行尾注 append + §7 链头 874 == 874 == 874（knife 558 demote 链完整） | grep（本文件证据段） |
| (D) 回执粘贴命令 + exit code + 关键 stdout + lineage 路径 | ✅ 本文件证据段原样粘贴命令 + stdout + `EXIT_CODE=0` + lineage 路径与实测字段（`intake_status=O1_AUTO_INTAKED`、`is_demo=false`、全 SHA） | 本文件证据段 |
| (E) 回执 **仅 `560`**（`-cc-`） | ✅ 合刀单槽单回执：`_knife560` bump + 本回执（仅此一个回执号）→ 872 → 874；本文件名含 `-cc-` | bump 输出（本文件证据段） |
| (6) **必须双推** → POLL | ✅ 双推 origin + github（范围见 backfill）；backfill cc_head 单独 commit 再双推 | push 输出（会话记录） |

## 证据

### 实跑命令 + exit code + 关键 stdout（原样粘贴，per tasking D）

```
$ python3 scripts/auto_ingest_public_source.py --live --pilot-domain=stats.gov.cn --pilot-category=NATIONAL_BULLETIN --confirm-live=reviews/stage0-gate0-rework-2026-08-23/20260828T-nbs-national-bulletin-posta-live-refresh-lineage.jsonl
OK pilot matched: stats.gov.cn / NATIONAL_BULLETIN
   primary_url: https://www.stats.gov.cn/sj/zxfb/
   auth_note: 公开；无需授权
   expected SHA: a7e4029df707918a…
OK deeplink discovered: https://www.stats.gov.cn/sj/zxfb/202608/t20260827_1965129.html
OK downloaded 180165 bytes; sha256=a7e4029df707918a…
OK archived: /Users/kjonekong/projects/china platform/data/public_archives/2026-08/stats.gov.cn/zxfb
OK extract: 6 table row(s)
OK observation written: reviews/stage0-gate0-rework-2026-08-23/20260828T-nbs-national-bulletin-posta-live-refresh-lineage.jsonl
EXIT_CODE=0
```

### lineage 实测字段（per tasking D；mart 真 SHA 入仓语义实测如实写明）

```
$ python3 -c (lineage JSONL 解析)
  path          = reviews/stage0-gate0-rework-2026-08-23/20260828T-nbs-national-bulletin-posta-live-refresh-lineage.jsonl
  intake_status = O1_AUTO_INTAKED
  is_demo       = false   （首个非 demo 实测入库）
  source_file_sha256 = a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb（== registry `a7e4029d…`/180165）
  房规：lineage JSONL 落盘 reviews/ 未跟踪、不入 manifest（同 `510` live-candidate lineage 先例）
```

### 文档锚点 + 计数

```
$ grep -cF 八锚点
  docs/53:「第 33 项（此条）· O1 B 路 NATIONAL_BULLETIN post-(a) live refresh 实跑证据」= 1
  docs/53:「a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb」= 3（第 33 项新增 1 + 既有第 30 项段 2，无删减）
  docs/45 文首:「queue_rev 308（per `560-stage2-o1-bpath-nbs-posta-live-refresh-evidence-bundle-tasking-20260828`）」= 1
  docs/45 文首:「knife 76…145 锁链延续」                                  = 1
  docs/45 §1:「**post-(a) live refresh 实跑证据 + docs/53 §5 第 33 项（per `560`）**」= 1
  docs/45 §6.2:「post-(a) live refresh 实跑证据已落 docs/53 §5 第 33 项（per `560`」= 1
  docs/45 §7:「874 == 874 == 874」                                        = 1
  docs/45 §7 demote:「knife 558 = 合刀 A+B+C 同 commit、单槽单回执」          = 1
  docs/45:stale「872 == 872 == 872」                                      = 0  （已由 §7 链头更新承接）

$ grep -c/-o "O1 仍 OPEN" 计数核验（非减）
  docs/45 行计数 91（由 89 增至 91）、出现计 136（由 132 增至 136）
  docs/53 行计数 13（由 12 增至 13）、出现计 15（由 14 增至 15）

$ python3 -c 残留转义检查 chr(92)+chr(96)
  docs/45 = 0、docs/53 = 0

$ shasum -a 256 frontend/lib/public_extract_{nbs,nbs_live_candidate,sz,hubei}.json | cut -c1-8
  e30ee811 9232efdb 937255a5 9056001c   （disk == 锁值，4 fixture 字节未动）

$ python3 scripts/_knife560_manifest_bump.py
ADD: scripts/_knife560_manifest_bump.py (3940 bytes, sha=496f8a64)
ADD: reviews/stage0-gate0-rework-2026-08-23/560-stage0-cc-o1-bpath-nbs-posta-live-refresh-evidence-bundle-receipt-20260828.md (10417 bytes, sha=b3b0c8bc)
UPDATE artifact_count: 872 → 874
INVARIANT: sum(role_count)=874 == artifact_count=874 == len(artifacts)=874
OK manifest updated; added 2 artifacts
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 新增第 33 项 blockquote；第 21–32 项既有 blockquote 正文原样未动）| 已入 manifest（SHA REFRESH 不增计数）|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 queue_rev 308 刷新行 + §1 实跑证据句 + §6.2 行尾注 + §7 链头更新；§3 弧 21–32 段保持原样）| 已入 manifest（SHA REFRESH 不增计数）|
| `scripts/_knife560_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../560-stage0-cc-o1-bpath-nbs-posta-live-refresh-evidence-bundle-receipt-20260828.md` | NEW（本文件；**唯一回执**）| `documentation` |
| `reviews/.../20260828T-nbs-national-bulletin-posta-live-refresh-lineage.jsonl` | 运行产物（tasking A 指定路径）| **未跟踪、不入 manifest**（房规同 `510`；路径 + 实测字段已录入本回执证据段）|
| `data/public_archives/2026-08/stats.gov.cn/zxfb` | 运行产物（archive）| **未跟踪、不入 manifest**（房规同 `510`）|

注：本刀 registry.csv 零触碰（任务书「不做改 registry」）；未启用 Hubei live；未绕过 AUTH（源站公开无需授权 auth_note）；docs/50 零触碰（intro ⚠ 收据链尾 `→ 556` 原样、里程碑表 21–32 行正文原样未动）。

## Pack 不变量

`_knife560_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **872 → 874**；`sum(role_count) == artifact_count == len(artifacts) == 874`（docs/45/docs/53 已入 manifest，SHA REFRESH 不增计数；lineage/archive 运行产物未跟踪不入 manifest；前置 knife 558 回执 `558` 已落 870 → 872；knife 556 `556` 已落 868 → 870；knife 554 `554` 已落 866 → 868；knife 552 `552` 已落 864 → 866；knife 550 `550` 已落 862 → 864；knife 548 `548` 已落 860 → 862；knife 546 `546` 已落 858 → 860；knife 544 `544` 已落 856 → 858；knife 542 `542` 已落 854 → 856；knife 540 `540` 已落 852 → 854；knife 538 `538` 已落 850 → 852；knife 536 `536` 已落 848 → 850；knife 534 `534` 已落 846 → 848；knife 532 `532` 已落 844 → 846；knife 530 `530` 已落 842 → 844；knife 528 `528` 已落 840 → 842；knife 526 `526` 已落 838 → 840；knife 524 `524` 已落 836 → 838；knife 522 `522` 已落 834 → 836；knife 520 `520` 已落 832 → 834；knife 518 `518` 已落 830 → 832；knife 516 `516` 已落 828 → 830；knife 514 `514` 已落 826 → 828；knife 512 `512` 已落 824 → 826；knife 510 `510` 已落 822 → 824；knife 508 `508` 已落 820 → 822；knife 506 `506` 已落 818 → 820；knife 504 `504` 已落 816 → 818；knife 502 `502` 已落 814 → 816；knife 500 `500` 已落 812 → 814；knife 498 `498` 已落 810 → 812；knife 496 `496` 已落 808 → 810；knife 494 `494` 已落 806 → 808；knife 492 `492` 已落 804 → 806；knife 490 `490` 已落 802 → 804；knife 488 `488` 已落 800 → 802；knife 486 `486` 已落 798 → 800；knife 484 `484` 已落 796 → 798；knife 105 `478` 已落 790 → 792；knife 104 `476` 已落 788 → 790；knife 103 `474` 已落 786 → 788；knife 102 `472` 已落 784 → 786）。

## 红线自查

- ❌ **未做 Gate/O1 PASS 宣告：hash 匹配 ≠ O1 收口——实测 hash 匹配（download sha256 == registry `a7e4029d…`/180165，lineage `is_demo=false`）已如实写明，但 O1 收口须用户/Cursor 裁定，本刀不宣布；O1 仍 OPEN**（docs/53 第 33 项 + docs/45 四处 + 本回执写明）
- ❌ 未改 registry（本刀零触碰；任务书「不做改 registry」）；未启用 Hubei live
- ❌ 未绕过 AUTH（源站公开无需授权 `auth_note: 公开；无需授权`；未遇 AUTH 阻停；无静默失败）
- ❌ 未删减 OPEN（docs/45 89→91 行 / 132→136 处；docs/53 12→13 行 / 14→15 处，均不减）
- ❌ 未动 4 frontend fixture 字节（实测锁值一致：e30ee811 / 9232efdb / 937255a5 / 9056001c）；docs/50 零触碰
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ❌ 未谎称已跑通（实跑 exit 0 原样粘贴，含完整命令 + stdout + lineage 实测字段）；未交两个回执号（合刀单槽单回执，回执仅 `560` 一个）
- ⚠ 红线重申：**合刀仍单槽单回执；hash 匹配 ≠ O1 收口（mart 真 SHA 入仓语义实测已写明：lineage `is_demo=false` + `O1_AUTO_INTAKED` + 全 SHA == registry）；遇 AUTH 阻停报告不绕过**（per tasking 红线段）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执/任务书号 + 简短语）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `bash scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `560`）。
