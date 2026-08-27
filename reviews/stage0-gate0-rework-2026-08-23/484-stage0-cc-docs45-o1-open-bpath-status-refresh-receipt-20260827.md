# 484 — docs/45 §3 O1 OPEN 状态刷新（B 路主路径） · CC 回执

- 编号：`484-stage0-cc-docs45-o1-open-bpath-status-refresh-receipt-20260827`
- 任务书：`484-stage2-docs45-o1-open-bpath-status-refresh-tasking-20260827`
- 作者：CC（heartbeat 84）
- cc_head：待回填（见下）
- 日期：2026-08-27

---

## §NOW 对照

| 484 tasking §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/45` §3 O1 详细段 + §6.2 相关行刷新：明确 **O1 主路径 = docs/52 B 路**（试点轴 `NATIONAL_BULLETIN` per `480`/`482`）；`WAITING_FILE` 仅保留为 intake 出口码/mart 真 SHA 未入仓语义，**不再写成「等用户投喂才可继续」**；docs/51 用户投递仍可用但非唯一 | ✅ 三处刷新：(a) §3 O1 表行（:124：主路径 = B 路 + A 路非唯一 + WAITING_FILE 新语义）；(b) §3 收口路径 bullet（:143 整段刷新：B 路六步流水线产出真 SHA 入仓即满足 contract + A 路投递仍走线下原件/`--confirm-o1=PATH` 仅限 A 路出口 + 收口前 demo 恒占位）；(c) §6.2 相关行（:234：「**O1 仍 OPEN**——主路径 = docs/52 B 路…非『等用户投喂才可继续』」）；「O1 仍 OPEN」「不宣布收口」语义全程保持，未删 OPEN（docs/45 ×14 处计数不减反增）| grep |
| (2) 文首刷新行 + §1 一句 + §7 pack 链 | ✅ (a) 文首 queue_rev 231 刷新行（:44）；(b) §1 一句（:100 短段：新语义 + 主路径 + A 路非唯一 + **O1 仍 OPEN**）；(c) §7 pack invariant 链头 796 → 798（:348，knife 482→480→105 demote 链完整） | grep |
| (3) 可选 `docs/50` §5 OPEN 必带一句同步 | ✅ §5.1 表后一句已落（blockquote 刷新句：「上表 O1 行状态语义已随 docs/45 §3 同步刷新——WAITING_FILE 新语义…主路径 = B 路…A 路仍可用非唯一…O1 仍 OPEN——本清单不宣布任何收口」）；§5.1 表行正文原样未动 | grep |
| (4) 非 O1/Gate PASS / 不删 OPEN / 不暗示必须用户投喂 | ✅ 「O1 仍 OPEN」「不宣布收口」「不谎称 O1 已收口」在文首刷新行 + §3 表行/bullet + §6.2 + §1 句 + docs/50 §5 句全数在位；「等用户投喂才可继续」旧 gate 语义在 scoped 三处全部移除，历史日志区（queue_rev 125–229 刷新行 + 回执 `322` 登记段）原样保留 | diff |
| (5) 回执 `484`（`-cc-`） | ✅ 本文件名 | — |

## 证据

```
$ grep -n "O1 主路径 = docs/52 公开源自动获取 B 路\|收口路径（per \`484\` 状态刷新）\|真 SHA 投递入口…\*\*O1 仍 OPEN\*\*—" docs/45…md
  docs/45:124   （§3 O1 表行刷新）
  docs/45:143   （§3 收口路径 bullet 刷新）
  docs/45:234   （§6.2 相关行刷新）

$ grep -n "queue_rev 231（per \`484\|798 == 798 == 798\|O1 OPEN 状态刷新（B 路主路径；per \`484\`）" docs/45…md
  docs/45:44    （文首 queue_rev 231 刷新行）
  docs/45:100   （§1 一句）
  docs/45:348   （§7 pack invariant 链头 796 → 798）

$ grep -c "刷新（per \`484\` 可选一句）" docs/50…md
  1              （可选 docs/50 §5.1 表后同步句已落）

$ grep -c "O1 仍 OPEN" docs/45…md docs/50…md
  14 / 2          （OPEN 保持核验：未被删改、计数不减）

$ python3 scripts/_knife484_manifest_bump.py
ADD: scripts/_knife484_manifest_bump.py (…)
ADD: reviews/.../484-…-receipt-20260827.md (…)
UPDATE artifact_count: 796 → 798
INVARIANT: sum(role_count)=798 == artifact_count=798 == len(artifacts)=798
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（§3 表行 + 收口路径 bullet + §6.2 行三处语义刷新 + 文首 +1 刷新行 + §1 +1 句段 + §7 链头更新；历史日志区原样）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | MODIFIED（§5.1 表后 +1 句 blockquote 同步，可选句已做；§5.1 表行原样）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife484_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../484-stage0-cc-docs45-o1-open-bpath-status-refresh-receipt-20260827.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife484_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **796 → 798**；`sum(role_count) == artifact_count == len(artifacts) == 798`（docs/45/docs/50 已入 manifest，SHA REFRESH 不增计数；前置 knife 482 回执 `482` 已落 794 → 796；knife 480 `480` 已落 792 → 794；knife 105 `478` 已落 790 → 792；knife 104 `476` 已落 788 → 790；knife 103 `474` 已落 786 → 788；knife 102 `472` 已落 784 → 786；knife 101 `470` 已落 782 → 784；knife 100 `468` 已落 780 → 782；knife 99 `466` 已落 778 → 780；knife 98 `464` 已落 776 → 778；knife 97 `462` 已落 774 → 776）。

## 红线自查

- ❌ 未改代码 / 未实装爬取代码 / 未启用 Hubei live / 未做 Docker（docs only per §NOW）
- ❌ 未删减 OPEN（「O1 仍 OPEN」全数在位且计数不减；删除的仅是「等用户投喂才可继续」这一过时 gate 语义本身，per tasking 授权范围）
- ❌ 未 Gate/O1 PASS 宣告 / 未谎称 O1 已收口
- ❌ 未暗示必须用户投喂（A 路明确降为「仍可用但非唯一」，`--confirm-o1=PATH` 标注仅限 A 路出口）
- ❌ 未换服务器
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ 4 fixture byte SHA 前 8 锁显式列出（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀完全一致，未动 fixture 字节）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `bash scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `484`）。
