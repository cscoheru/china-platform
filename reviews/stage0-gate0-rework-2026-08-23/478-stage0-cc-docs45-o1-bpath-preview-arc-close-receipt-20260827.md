# 478 — docs/45 preview 弧 16–20 收口 + O1 主路径指针（docs/52 B 路） · CC 回执

- 编号：`478-stage0-cc-docs45-o1-bpath-preview-arc-close-receipt-20260827`
- 任务书：`478-stage2-docs45-o1-bpath-preview-arc-close-tasking-20260827`
- 作者：CC（heartbeat 84）
- cc_head：`ac33440`（双推：origin 826af50..ac33440，github 826af50..ac33440；backfill 单独 commit）
- 日期：2026-08-27

---

## §NOW 对照

| 478 tasking §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `docs/45` 刷新四处：登记 preview 弧 16–20 文档链完整收口（per `472`/`474`/`476`；docs/50 intro 链尾 `474`）+ **O1 主路径指针 = docs/52 公开源 B 路**（docs/51 用户投递仍可用但非唯一；仍 OPEN） | ✅ 文首 queue_rev 225 刷新行（:41）+ §1 登记段（:91：六节点弧逐项收口核验 + O1 B 路指针 discover→download→sha256→archive→extract + docs/51 非唯一 + **O1 仍 OPEN** 不宣布收口）+ §6.2 行（:309）+ §7 链头 790 → 792（:337，knife 104→103→102 demote 链完整） | grep |
| (2) 可选 `docs/52` §0/§1 一句互链 preview 弧收口 + 下一试点轴 = `NATIONAL_BULLETIN`（stats.gov.cn HTML） | ✅ §0（行 21 blockquote 尾续句）：preview 弧文档链完整收口（16–20 项 per `472`/`474`/`476`；docs/50 intro 收据链尾 `474`）+ 下一试点轴维持 `NATIONAL_BULLETIN` | grep |
| (3) 非 O1/Gate PASS | ✅ 两文档均显式「非 O1/Gate PASS」「不改代码」「不实装 crawler」「不启用 Hubei live」「不等用户投喂文件」「不动 16–20 既有正文」「仍不宣布 Gate 2 PASS」；「O1 仍 OPEN」语义保持（docs/52 ×4 处、docs/45 本刀段 ×明示），未删减 OPEN | diff |
| (4) 回执 `478`（`-cc-`） | ✅ 本文件名 | — |

## 证据

```
$ grep -n "queue_rev 225（per \`478\|preview 弧 16–20 文档链完整收口\|792 == 792 == 792" docs/45-…md
  docs/45:41    （文首 queue_rev 225 刷新行）
  docs/45:91    （§1 preview 弧收口 + O1 B 路主路径登记段）
  docs/45:309   （§6.2 行）
  docs/45:337   （§7 pack invariant 链头 790 → 792）

$ grep -c "preview 公网预览互链弧文档链已完整收口（第 16–20 项，per \`472\`/\`474\`/\`476\`" docs/52-…md
  1              （可选互链已落：docs/52 §0 blockquote 尾句）

$ grep -c "O1 仍 OPEN" docs/45-…md docs/52-…md
  docs/45:6  docs/52:4   （OPEN 保持核验：未被删改）

$ python3 scripts/_knife105_manifest_bump.py
ADD: scripts/_knife105_manifest_bump.py (…)
ADD: reviews/.../478-…-receipt-20260827.md (…)
UPDATE artifact_count: 790 → 792
INVARIANT: sum(role_count)=792 == artifact_count=792 == len(artifacts)=792
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 +1 刷新行 + §1 +1 段（preview 弧收口 + O1 B 路指针）+ §6.2 +1 行 + §7 链头更新）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md` | MODIFIED（§0 blockquote 尾 +1 句互链，可选句已做；正文原样）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife105_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../478-stage0-cc-docs45-o1-bpath-preview-arc-close-receipt-20260827.md` | NEW（本文件）| `documentation` |

## Pack 不变量

`_knife105_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **790 → 792**；`sum(role_count) == artifact_count == len(artifacts) == 792`（docs/45/docs/52 已入 manifest，SHA REFRESH 不增计数；前置 knife 104 回执 `476` 已落 788 → 790；knife 103 `474` 已落 786 → 788；knife 102 `472` 已落 784 → 786；knife 101 `470` 已落 782 → 784；knife 100 `468` 已落 780 → 782；knife 99 `466` 已落 778 → 780；knife 98 `464` 已落 776 → 778；knife 97 `462` 已落 774 → 776；knife 96 `460` 已落 772 → 774；knife 95 `458` 已落 770 → 772）。

## 红线自查

- ❌ 未改代码 / 未实装 crawler / 未启用 Hubei live（docs only per §NOW）
- ❌ 未动 16–20 项既有正文与里程碑表 16–20 行（本刀仅 docs/45 四处登记 + docs/52 尾注一句）
- ❌ 未删减 OPEN（「O1 仍 OPEN」在位；O1 指针只登记路径选择、不宣布收口）
- ❌ 未 Gate/O1 PASS 宣告
- ❌ 未做 Docker / 未换服务器
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）
- ✅ 4 fixture byte SHA 前 8 锁显式列出（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀完全一致，未动 fixture 字节）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `bash scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `478`）。
