# 508 — docs/50 §4.4 第 25 项 live-candidate 里程碑行补登 · CC 回执

- 编号：`508-stage0-cc-docs50-item25-live-candidate-milestone-receipt-20260827`
- 任务书：`508-stage2-docs50-item25-o1-bpath-live-candidate-milestone-tasking-20260827`
- 作者：CC（heartbeat 84）
- cc_head：`2ae574f`（双推：origin 085de29..2ae574f，github 085de29..2ae574f；backfill 单独 commit）
- 日期：2026-08-27

---

## §NOW 对照

| 508 tasking §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/50` §4.4 里程碑表新增 **第 25 项行**：`docs/53` §5 第 25 项 O1 B 路 live-candidate 下一轴登记（per `506`；`--live --confirm-live`；只登记未运行；**O1 仍 OPEN**） | ✅ 第 25 项行已落（「docs/53 §5 第 24 项 O1 B 路 21–23 弧收口」行后、「预览 URL」段前；回执列 `506`；intro ⚠ 收据链尾保持 `→ 502` 原样未动——本刀任务书不含链尾续接；第 21–24 项行既有正文原样未动） | grep（本文件证据段） |
| (2) `docs/45` 刷新四处 | ✅ (a) 文首 queue_rev 255 刷新行（:56，锁链「与 knife 76…119 锁值完全一致」）；(b) §1 一句（:136「docs/50 §4.4 里程碑表第 25 项行 O1 B 路 live-candidate 下轴里程碑补登（per \`508\`）」段）；(c) §6.2 真 SHA 投递入口行尾注（+「docs/50 §4.4 里程碑表第 25 项行 live-candidate 下轴里程碑已补登（per \`508\`；回执列 \`506\`）」）；(d) §7 pack invariant 链头 820 → 822（:384，knife 506→504 demote 链完整） | grep |
| (3) 可选 `docs/53` §5 第 25 项一句「docs/50 里程碑行补登 per `508`」 | ✅ 已落：「本第 25 项已同步作为 \`docs/50\` §4.4 里程碑表「docs/53 §5 第 25 项 O1 B 路 live-candidate 下一探测轴登记」行补登（per 回执 \`508\`）。」（第 16–24 项既有正文原样未动） | grep |
| (4) 非 O1/Gate PASS / 不删 OPEN / `is_demo=true` 不得谎称真 SHA 收口 | ✅ 「O1 仍 OPEN」计数不减反增（docs/45 行计数 36→38、出现计 52→55；docs/50 ×5→×6——第 25 项行自带一条；docs/53 出现计 ×6 保持）；无任何 PASS 宣告；本刀零运行零网络副作用 | grep |
| (5) 回执 **`508`**（`-cc-`） | ✅ 本文件名 | — |

## 瑕疵修复披露（本刀顺手修复自引入缺陷）

k506 文首刷新行写入时混入 **2 处 shell 转义符残留**（「per \\\`506\\\`」误含字面反斜杠，Edit 参数转义混入所致，已在先前 commit 中、语义零变化、纯标点级瑕疵）。本刀以 `sed 's/\\\`/\`/g'` 就地修复归零（grep 复验 =0）。该残留位于 CC 本弧自写文本内，不涉及 Cursor 所有文档或既有第三方正文。

## 证据

```
$ grep -n 四锚点 docs/45…md
  docs/45:56    （文首 queue_rev 255 刷新行）
  docs/45:136   （§1 一句）
  docs/45:267   （§6.2 真 SHA 投递入口行尾注）
  docs/45:384   （§7 pack invariant 链头 820 → 822）

$ grep -n '第 25 项 O1 B 路 live-candidate 下一探测轴登记**' docs/50…md
  docs/50:209   （§4.4 里程碑表第 25 项行已落，预览 URL 段前）

$ grep -n '行补登（per 回执 `508`）' docs/53…md
  docs/53:162   （可选附注句已落）

$ grep -c/-o "O1 仍 OPEN" 计数核验
  docs/45 行计数 38（由 36 增至 38）、出现计 55（由 52 增至 55）—— 不减反增
  docs/50 行计 6、出现计 6（由 ×5 增至 ×6）—— 不减反增
  docs/53 行计 ×5、出现计 ×6 —— 保持

$ shasum -a 256 frontend/lib/public_extract_{nbs,nbs_live_candidate,sz,hubei}.json | cut -c1-8
  e30ee811 9232efdb 937255a5 9056001c   （disk == HEAD == 锁值，未动 fixture 字节）

$ python3 scripts/_knife508_manifest_bump.py
ADD: scripts/_knife508_manifest_bump.py (3445 bytes, sha=3c41a714)
ADD: reviews/.../508-stage0-cc-docs50-item25-live-candidate-milestone-receipt-20260827.md (7117 bytes, sha=d895686a)
UPDATE artifact_count: 820 → 822
INVARIANT: sum(role_count)=822 == artifact_count=822 == len(artifacts)=822
OK manifest updated; added 2 artifacts
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | MODIFIED（§4.4 里程碑表 +1 行第 25 项行；intro 收据链与既有行正文原样）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 第 25 项 blockquote 尾部 +1 句可选附注；第 16–24 项既有正文原样）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 +1 刷新行 queue_rev 255 + §1 +1 段 + §6.2 行尾注 + §7 链头更新 + 2 处自引入转义瑕疵就地修复）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife508_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../508-stage0-cc-docs50-item25-live-candidate-milestone-receipt-20260827.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife508_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **820 → 822**；`sum(role_count) == artifact_count == len(artifacts) == 822`（docs/45/docs/50/docs/53 已入 manifest，SHA REFRESH 不增计数；本刀纯文档零代码零运行；前置 knife 506 回执 `506` 已落 818 → 820；knife 504 `504` 已落 816 → 818；knife 502 `502` 已落 814 → 816；knife 500 `500` 已落 812 → 814；knife 498 `498` 已落 810 → 812；knife 496 `496` 已落 808 → 810；knife 494 `494` 已落 806 → 808；knife 492 `492` 已落 804 → 806；knife 490 `490` 已落 802 → 804；knife 488 `488` 已落 800 → 802；knife 486 `486` 已落 798 → 800；knife 484 `484` 已落 796 → 798；knife 482 `482` 已落 794 → 796；knife 480 `480` 已落 792 → 794；knife 105 `478` 已落 790 → 792；knife 104 `476` 已落 788 → 790；knife 103 `474` 已落 786 → 788；knife 102 `472` 已落 784 → 786）。

## 红线自查

- ❌ 未改代码 / 未实装爬取代码 / 未运行任何 connector（本刀纯文档零运行）/ 未实跑 `--live` / 未启用 Hubei live / 未做 Docker / 未改 registry `enabled`
- ❌ 未删减 OPEN（docs/45 行计数 36→38、docs/50 ×5→×6、docs/53 ×6 保持，均不减反增或保持）
- ❌ 未 Gate/O1 PASS 宣告 / `is_demo=true` 未谎称真 SHA 收口
- ❌ 未暗示必须用户投喂 / 未换服务器 / intro ⚠ 收据链尾 `→ 502` 原样未动（任务书不含链尾续接）
- ❌ 未动 docs/50 第 21–24 项行既有正文 / 未动 docs/53 第 16–24 项既有正文（第 25 项仅追加可选附注句 per (3)）/ 未动 docs/52（本刀零触碰）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ❌ 未动 fixture 字节（`shasum -a 256` 前 8 位实测 disk == HEAD == 锁值：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）
- ⚠ 本刀修复 2 处 CC 自引入的转义瑕疵（见披露节；语义零变化，仅标点级）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `bash scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `508`）。
