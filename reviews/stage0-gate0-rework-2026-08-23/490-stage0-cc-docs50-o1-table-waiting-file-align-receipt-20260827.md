# 490 — docs/50 §3.3/§5.1 O1 表行 WAITING_FILE 语义对齐 · CC 回执

- 编号：`490-stage0-cc-docs50-o1-table-waiting-file-align-receipt-20260827`
- 任务书：`490-stage2-docs50-o1-table-waiting-file-align-tasking-20260827`
- 作者：CC（heartbeat 84）
- cc_head：`<backfill>`（双推后单独 commit 回填）
- 日期：2026-08-27

---

## §NOW 对照

| 490 tasking §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/50` §3.3 表行（:118）+ §5.1 表行（:242）刷新 | ✅ 两表行已刷（`484`/`486`/`488` 校准延续）：(a) §3.3 O1 行——状态列 **WAITING_FILE 保留**为 intake 出口码 / mart 真 SHA 未入仓技术状态语义、非「等用户投喂才可继续」；收口前置列改为「**主路径 = docs/52 B 路**（公开源自动获取，试点轴 `NATIONAL_BULLETIN` per \`480\`/\`482\`）；A 路 = 用户线下渠道 + `--confirm-o1=PATH`（仅限 A 路出口）+ intake 4 退出码契约，仍可用但非唯一」；(b) §5.1 O1 行——状态列同语义，收口前置列「主路径 = docs/52 B 路（试点轴 \`NATIONAL_BULLETIN\`）；A 路 `--confirm-o1=PATH` + intake 4 退出码契约仍可用但非唯一」 | grep |
| (2) 可选文末/清单三句对齐（约 277/413/461） | ✅ 三处已落：(a) §5.4 不可隐藏清单 O1 项尾注「WAITING_FILE = intake 出口码 / 真 SHA 未入仓语义，非『等用户投喂』per \`490\` 对齐」；(b) Gate 2 必带清单第 1 项尾注「WAITING_FILE = intake 出口码 / mart 真 SHA 未入仓技术状态语义（per \`490\` 对齐）」；(c) 文末 ⚠ 行「WAITING_FILE = intake 出口码 / 真 SHA 未入仓技术状态语义，非『等用户投喂』，per \`484\`/\`486\`/\`488\`/\`490\` 对齐」；§4.4 里程碑表原样未动 | grep |
| (3) `docs/45` 刷新四处 | ✅ (a) 文首 queue_rev 237 刷新行（:47）；(b) §1 一句（:109「docs/50 §3.3/§5.1 O1 表行 WAITING_FILE 语义对齐（per \`490\`）」段）；(c) §6.2 真 SHA 投递入口行尾注（:243 +「docs/50 §3.3/§5.1 O1 表行同源语义已对齐（per \`490\`）」）；(d) §7 pack invariant 链头 802 → 804（:357，knife 488→486→484 demote 链完整） | grep |
| (4) 非 O1/Gate PASS / 不删 OPEN / 不暗示必须用户投喂 | ✅ 「O1 仍 OPEN」计数不减（docs/45 由 ×18 增至 ×19 行计数）；两表行均保留 WAITING_FILE 标记 + 「不擅自宣布收口」语义；「不谎称 O1 已收口」「不暗示必须用户投喂」在文首刷新行 + §1 句显式在位；A 路明确「仍可用但非唯一」，`--confirm-o1=PATH` 标注仅限 A 路出口 | diff |
| (5) 回执 `490`（`-cc-`） | ✅ 本文件名 | — |

## 证据

```
$ grep -n "主路径 = docs/52 B 路（公开源自动获取，试点轴\|主路径 = docs/52 B 路（试点轴" docs/50…md
  docs/50:118   （§3.3 O1 表行）
  docs/50:242   （§5.1 O1 表行）

$ grep -c "per \`490\`" docs/50…md
  3            （可选三句已落：§5.4 清单 + 必带清单第 1 项 [+ 文末 ⚠ 行 per 490 对齐]）

$ grep -n "queue_rev 237（per \`490\|docs/50 §3.3/§5.1 O1 表行同源语义已对齐（per \`490\`\|804 == 804 == 804" docs/45…md
  docs/45:47   （文首 queue_rev 237 刷新行）
  docs/45:109  （§1 一句）
  docs/45:243  （§6.2 真 SHA 投递入口行尾注）
  docs/45:357  （§7 pack invariant 链头 802 → 804）

$ grep -c "O1 仍 OPEN" docs/50…md docs/45…md
  2 / 19        （OPEN 保持核验：未被删改、docs/45 行计数由 18 增至 19）

$ python3 scripts/_knife490_manifest_bump.py
ADD: scripts/_knife490_manifest_bump.py (…)
ADD: reviews/.../490-…-receipt-20260827.md (…)
UPDATE artifact_count: 802 → 804
INVARIANT: sum(role_count)=804 == artifact_count=804 == len(artifacts)=804
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | MODIFIED（§3.3 O1 表行 + §5.1 O1 表行刷新 + 可选三句（§5.4 / 必带清单第 1 项 / 文末 ⚠）；§4.4 里程碑表与其余既有正文原样）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 +1 刷新行 + §1 +1 段 + §6.2 行尾注 + §7 链头更新）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife490_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../490-stage0-cc-docs50-o1-table-waiting-file-align-receipt-20260827.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife490_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **802 → 804**；`sum(role_count) == artifact_count == len(artifacts) == 804`（docs/45/docs/50 已入 manifest，SHA REFRESH 不增计数；前置 knife 488 回执 `488` 已落 800 → 802；knife 486 `486` 已落 798 → 800；knife 484 `484` 已落 796 → 798；knife 482 `482` 已落 794 → 796；knife 480 `480` 已落 792 → 794；knife 105 `478` 已落 790 → 792；knife 104 `476` 已落 788 → 790；knife 103 `474` 已落 786 → 788；knife 102 `472` 已落 784 → 786；knife 101 `470` 已落 782 → 784；knife 100 `468` 已落 780 → 782；knife 99 `466` 已落 778 → 780；knife 98 `464` 已落 776 → 778）。

## 红线自查

- ❌ 未改代码 / 未实装爬取代码 / 未启用 Hubei live / 未做 Docker（docs only per §NOW）
- ❌ 未删减 OPEN（「O1 仍 OPEN」计数不减、docs/45 ×19 不减反增；WAITING_FILE 标记在两表行原位保留并转为新语义说明）
- ❌ 未 Gate/O1 PASS 宣告 / 未谎称 O1 已收口
- ❌ 未暗示必须用户投喂（A 路「仍可用但非唯一」、`--confirm-o1=PATH` 仅限 A 路出口）
- ❌ 未动 §4.4 里程碑表既有正文 / 未换服务器
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ 4 fixture byte SHA 前 8 锁显式列出（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀完全一致，未动 fixture 字节）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `bash scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `490`）。
