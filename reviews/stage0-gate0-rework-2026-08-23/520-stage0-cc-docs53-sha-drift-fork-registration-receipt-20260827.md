# 520 — docs/53 §5 第 28 项 SHA drift 候选轨处置分叉登记 · CC 回执

- 编号：`520-stage0-cc-docs53-sha-drift-fork-registration-receipt-20260827`
- 任务书：`520-stage2-docs53-sha-drift-candidate-disposition-fork-tasking-20260827`
- 作者：CC（heartbeat 84）
- cc_head：`PENDING_HEAD_SHA`（双推 origin/github 后由 backfill 单独 commit 回填）
- 日期：2026-08-27

---

## §NOW 对照

| 520 tasking §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/53` §5 新增 **第 28 项（此条）** blockquote：登记 `510` live-probe SHA drift 候选轨处置分叉（实测 `a7e4029d…` ≠ expected `dea13b8a…`；选项 (a) 更新 registry `file_hash_sha256` (b) 改稳定归档 URL；**本刀只登记、不改 registry**；**等用户裁定**） | ✅ 第 28 项 blockquote 已落（第 27 项段后、「冒烟：」段前）：实测 SHA 全值 + 分叉 (a)/(b) 二选一 + 「两选项均须用户裁定后另起独立刀任务执行，connector 不自动改 registry」+「不替用户选分叉」；registry `enabled` 与哈希本刀均未改；第 21–27 项既有正文原样未动 | grep（本文件证据段）+ registry.csv grep |
| (2) `docs/45` 刷新四处 | ✅ (a) 文首 queue_rev 267 刷新行（k518 行下紧邻插入，「knife 76…125 锁链延续」）；(b) §1 第 28 项分叉登记段；(c) §6.2 真 SHA 投递入口行尾注 append（+「分叉已登记（per \`520\`…等用户裁定后另刀）」）；(d) §7 pack invariant 链头 832 → 834（knife 518→516 demote 链完整） | grep |
| (3) 非 O1/Gate PASS / 不删 OPEN / 不改 registry / 不替用户选分叉 | ✅ 「O1 仍 OPEN」计数不减反增或保持（docs/45 行计数 48→50、出现计 71→74；docs/50 ×8 保持；docs/53 行计 7→8、出现计 8→9）；无任何 PASS 宣告；drift ≠ 收口多处写明；registry.csv expected 哈希 `dea13b8a4ff116ca…` 磁盘在位（grep =1，零改动）；(a)/(b) 二选一均留用户 | grep + `grep -cF 'dea13b8a4ff116ca…' source_registry/registry.csv = 1` |
| (4) 回执 **`520`**（`-cc-`） | ✅ 本文件名 | — |

## 证据

```
$ grep -cF 五锚点
  docs/45:queue_rev 267（per `520-…tasking`）                    = 1   （文首刷新行）
  docs/45:§1 「处置分叉登记（per `520`）**：」                     = 1
  docs/45:§6.2 append「已登记（per `520`；(a) 更新 registry 哈希 / …另刀）」= 1
  docs/45:§7 「834 == 834 == 834」                              = 1
  docs/53:「第 28 项（此条）· …（per `520` cc 回执；queue_rev 267 落地）」  = 1

$ grep -cF 'dea13b8a4ff116ca91403b189cdd60705545b28200f9023c3d56e6db03f3939d' source_registry/registry.csv
  1   （expected 哈希在位 → registry 零改动磁盘实证）

$ grep -c/-o "O1 仍 OPEN" 计数核验
  docs/45 行计数 50（由 48 增至 50）、出现计 74（由 71 增至 74）—— 不减反增
  docs/50 行计 ×8、出现计 ×8 —— 保持
  docs/53 行计 8（由 7 增至 8）、出现计 9（由 8 增至 9）—— 不减反增

$ python3 -c 残留转义检查 chr(92)+chr(96)
  docs/45 = 0、docs/50 = 0、docs/53 = 0

$ shasum -a 256 frontend/lib/public_extract_{nbs,nbs_live_candidate,sz,hubei}.json | cut -c1-8
  e30ee811 9232efdb 937255a5 9056001c   （disk == HEAD == 锁值，未动 fixture 字节）

$ python3 scripts/_knife520_manifest_bump.py
ADD: scripts/_knife520_manifest_bump.py (3475 bytes, sha=f21fb385)
ADD: reviews/.../520-stage0-cc-docs53-sha-drift-fork-registration-receipt-20260827.md (7232 bytes, sha=d7467c94)
UPDATE artifact_count: 832 → 834
INVARIANT: sum(role_count)=834 == artifact_count=834 == len(artifacts)=834
OK manifest updated; added 2 artifacts
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 第 27 项后新增第 28 项 blockquote 一处；第 21–27 项既有正文原样未动）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 +1 刷新行 queue_rev 267 + §1 +1 段 + §6.2 行尾注 + §7 链头更新）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife520_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../520-stage0-cc-docs53-sha-drift-fork-registration-receipt-20260827.md` | NEW（本文件）| `documentation` |

注：本刀 docs/50 与 docs/52 零触碰（任务书范围不含）；source_registry/registry.csv 零触碰。

## Pack 不变量

`_knife520_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **832 → 834**；`sum(role_count) == artifact_count == len(artifacts) == 834`（docs/45/docs/53 已入 manifest，SHA REFRESH 不增计数；本刀纯文档零运行零网络零代码；前置 knife 518 回执 `518` 已落 830 → 832；knife 516 `516` 已落 828 → 830；knife 514 `514` 已落 826 → 828；knife 512 `512` 已落 824 → 826；knife 510 `510` 已落 822 → 824；knife 508 `508` 已落 820 → 822；knife 506 `506` 已落 818 → 820；knife 504 `504` 已落 816 → 818；knife 502 `502` 已落 814 → 816；knife 500 `500` 已落 812 → 814；knife 498 `498` 已落 810 → 812；knife 496 `496` 已落 808 → 810；knife 494 `494` 已落 806 → 808；knife 492 `492` 已落 804 → 806；knife 490 `490` 已落 802 → 804；knife 488 `488` 已落 800 → 802；knife 486 `486` 已落 798 → 800；knife 484 `484` 已落 796 → 798；knife 482 `482` 已落 794 → 796；knife 480 `480` 已落 792 → 794；knife 105 `478` 已落 790 → 792；knife 104 `476` 已落 788 → 790；knife 103 `474` 已落 786 → 788；knife 102 `472` 已落 784 → 786）。

## 红线自查

- ❌ 未改代码 / 未运行任何 connector（本刀纯文档零运行零网络）/ 未实跑 `--live` / 未启用 Hubei live / 未做 Docker
- ❌ 未改 registry：`enabled` 与 `file_hash_sha256` 零改动——expected 哈希磁盘 grep 实证 =1；(a)/(b) 二选一处置权完整保留用户（不替用户选分叉；两选项均待用户裁定后另起独立刀任务）
- ❌ 未删减 OPEN（docs/45 行计数 48→50、docs/53 行 7→8 出现计 8→9、docs/50 ×8 保持，均不减反增或保持）
- ❌ 未 Gate/O1 PASS 宣告 / CANDIDATE_AUTO（`is_demo=true`）非真数据、drift ≠ 收口已在 docs/45 三处与 docs/53 第 28 项写明
- ❌ 未暗示必须用户投喂 / 未换服务器 / intro 收据链与里程碑表本刀均不在任务书范围（未触碰）
- ❌ 未动 docs/53 第 21–27 项既有正文（仅新增第 28 项）/ 未动 docs/50 与 docs/52
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ❌ 未动 fixture 字节（`shasum -a 256` 前 8 位实测 disk == HEAD == 锁值：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）
- ⚠ 无自引入瑕疵需披露（bump 生成器首轮 stale-token 清单误将新前置行合法区间 `(830 → 832)` 列为陈旧 token 致断言中止，修正清单后重跑通过——生成器脚本级插曲，未落任何 commit，产物本身无瑕）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `bash scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `520`）。
