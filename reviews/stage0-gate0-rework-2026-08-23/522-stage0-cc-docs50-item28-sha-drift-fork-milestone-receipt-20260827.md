# 522 — docs/50 §4.4 第 28 项 SHA drift 分叉里程碑行补登 · CC 回执

- 编号：`522-stage0-cc-docs50-item28-sha-drift-fork-milestone-receipt-20260827`
- 任务书：`522-stage2-docs50-item28-sha-drift-fork-milestone-tasking-20260827`
- 作者：CC（heartbeat 84）
- cc_head：`c5b97ee`（双推：origin f12cfc7..c5b97ee，github f12cfc7..c5b97ee；backfill 单独 commit）
- 日期：2026-08-27

---

## §NOW 对照

| 522 tasking §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/50` §4.4 里程碑表新增 **第 28 项行**：`docs/53` §5 第 28 项 SHA drift 候选轨处置分叉（per `520`；`a7e4029d…` ≠ `dea13b8a…`；等用户裁定；**O1 仍 OPEN**） | ✅ 第 28 项行已落（第 27 项行后、「预览 URL」段前；回执列 `520`；行内引实测 SHA 全值对 + 分叉 (a) 更新 registry 哈希 /(b) 改稳定归档 URL 二选一 + 「用户裁定后另起独立刀任务执行」+「只登记不替用户选」+ intro ⚠ 收据链尾保持 `→ 512` 原样未动——本刀任务书不含链尾续接；第 21–27 项行既有正文原样未动；本刀纯文档零运行零网络零代码） | grep（本文件证据段） |
| (2) `docs/45` 刷新四处 | ✅ (a) 文首 queue_rev 269 刷新行（k520 行下紧邻插入，「knife 76…126 锁链延续」）；(b) §1 第 28 项行补登段；(c) §6.2 真 SHA 投递入口行尾注 append（+「第 28 项行 SHA drift 分叉里程碑已补登（per \`522\`；回执列 \`520\`）」）；(d) §7 pack invariant 链头 834 → 836（knife 520 demote 链完整） | grep |
| (3) 可选 `docs/53` §5 第 28 项一句「docs/50 里程碑行补登 per `522`」 | ✅ 已落：「本第 28 项已同步作为 \`docs/50\` §4.4 里程碑表「docs/53 §5 第 28 项 SHA drift 候选轨处置分叉登记」行补登（per 回执 \`522\`）。」（第 28 项 blockquote 既有正文原样未动） | grep |
| (4) 非 O1/Gate PASS / 不删 OPEN / 不改 registry / 不替用户选分叉 | ✅ 「O1 仍 OPEN」计数不减反增或保持（docs/45 行计数 50→52、出现计 74→77；docs/50 ×8→×9——第 28 项行自带一条；docs/53 ×8 保持）；无任何 PASS 宣告；drift ≠ 收口多处写明；registry.csv expected 哈希 `dea13b8a4ff116ca…` 磁盘在位（grep =1，零改动）；(a)/(b) 二选一均留用户 | grep |
| (5) 回执 **`522`**（`-cc-`） | ✅ 本文件名 | — |

## 证据

```
$ grep -cF 六锚点
  docs/45:queue_rev 269（per `522-…tasking`）               = 1   （文首刷新行）
  docs/45:§1 「分叉里程碑行补登（per `522`）**：」             = 1
  docs/45:§6.2 append「第 28 项行 SHA drift 分叉里程碑已补登（per `522`；回执列 `520`）」= 1
  docs/45:§7 「836 == 836 == 836」                          = 1
  docs/50:「第 28 项 SHA drift 候选轨处置分叉登记**（O1 B 路 SHA drift 分叉登记里程碑；per 回执 `520` 落地…」= 1
  docs/53:「本第 28 项已同步作为 … 行补登（per 回执 `522`）。」 = 1

$ grep -cF 'dea13b8a4ff116ca91403b189cdd60705545b28200f9023c3d56e6db03f3939d' source_registry/registry.csv
  1   （expected 哈希在位 → registry 零改动磁盘实证）

$ grep -c/-o "O1 仍 OPEN" 计数核验
  docs/45 行计数 52（由 50 增至 52）、出现计 77（由 74 增至 77）—— 不减反增
  docs/50 行计 9、出现计 9（由 ×8 增至 ×9）—— 不减反增
  docs/53 行计 ×8、出现计 ×9 —— 保持

$ python3 -c 残留转义检查 chr(92)+chr(96)
  docs/45 = 0、docs/50 = 0、docs/53 = 0

$ shasum -a 256 frontend/lib/public_extract_{nbs,nbs_live_candidate,sz,hubei}.json | cut -c1-8
  e30ee811 9232efdb 937255a5 9056001c   （disk == HEAD == 锁值，未动 fixture 字节）

$ python3 scripts/_knife522_manifest_bump.py
ADD: scripts/_knife522_manifest_bump.py (3643 bytes, sha=faed6b04)
ADD: reviews/.../522-stage0-cc-docs50-item28-sha-drift-fork-milestone-receipt-20260827.md (7946 bytes, sha=0ecf420e)
UPDATE artifact_count: 834 → 836
INVARIANT: sum(role_count)=836 == artifact_count=836 == len(artifacts)=836
OK manifest updated; added 2 artifacts
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | MODIFIED（§4.4 里程碑表 +1 行第 28 项行；intro 收据链与既有行正文原样）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 第 28 项 blockquote 尾部 +1 句可选附注；第 21–27 项既有正文原样）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 +1 刷新行 queue_rev 269 + §1 +1 段 + §6.2 行尾注 + §7 链头更新）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife522_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../522-stage0-cc-docs50-item28-sha-drift-fork-milestone-receipt-20260827.md` | NEW（本文件）| `documentation` |

注：本刀 docs/52 零触碰（任务书范围不含）；source_registry/registry.csv 零触碰。

## Pack 不变量

`_knife522_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **834 → 836**；`sum(role_count) == artifact_count == len(artifacts) == 836`（docs/45/docs/50/docs/53 已入 manifest，SHA REFRESH 不增计数；本刀纯文档零运行零网络零代码；前置 knife 520 回执 `520` 已落 832 → 834；knife 518 `518` 已落 830 → 832；knife 516 `516` 已落 828 → 830；knife 514 `514` 已落 826 → 828；knife 512 `512` 已落 824 → 826；knife 510 `510` 已落 822 → 824；knife 508 `508` 已落 820 → 822；knife 506 `506` 已落 818 → 820；knife 504 `504` 已落 816 → 818；knife 502 `502` 已落 814 → 816；knife 500 `500` 已落 812 → 814；knife 498 `498` 已落 810 → 812；knife 496 `496` 已落 808 → 810；knife 494 `494` 已落 806 → 808；knife 492 `492` 已落 804 → 806；knife 490 `490` 已落 802 → 804；knife 488 `488` 已落 800 → 802；knife 486 `486` 已落 798 → 800；knife 484 `484` 已落 796 → 798；knife 482 `482` 已落 794 → 796；knife 480 `480` 已落 792 → 794；knife 105 `478` 已落 790 → 792；knife 104 `476` 已落 788 → 790；knife 103 `474` 已落 786 → 788；knife 102 `472` 已落 784 → 786）。

## 红线自查

- ❌ 未改代码 / 未运行任何 connector（本刀纯文档零运行零网络）/ 未实跑 `--live` / 未启用 Hubei live / 未做 Docker
- ❌ 未改 registry：`enabled` 与 `file_hash_sha256` 零改动——expected 哈希磁盘 grep 实证 =1；SHA drift 处置权完整保留用户（不替用户选分叉；两选项均待用户裁定后另起独立刀任务）
- ❌ 未删减 OPEN（docs/45 行计数 50→52、docs/50 ×8→×9、docs/53 ×8 保持，均不减反增或保持）
- ❌ 未 Gate/O1 PASS 宣告 / CANDIDATE_AUTO（`is_demo=true`）非真数据、drift ≠ 收口已在 docs/45 三处、docs/50 第 28 项行与本回执写明
- ❌ 未暗示必须用户投喂 / 未换服务器 / intro ⚠ 收据链尾 `→ 512` 原样未动（任务书不含链尾续接）
- ❌ 未动 docs/50 第 21–27 项行既有正文 / 未动 docs/53 第 21–27 项既有正文（第 28 项仅追加可选附注句 per (3)）/ 未动 docs/52（本刀零触碰）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ❌ 未动 fixture 字节（`shasum -a 256` 前 8 位实测 disk == HEAD == 锁值：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）
- ⚠ 无自引入瑕疵需披露（bump 生成器首轮 stale-token 清单漏列 docstring 自引用 `_knife520`（本文件）锚点致断言中止，补齐重跑通过——生成器脚本级插曲，未落任何 commit，产物本身无瑕）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `bash scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `522`）。
