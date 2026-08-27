# 494 — O1 B 路 NATIONAL_BULLETIN --from-local-sample 证据（显式 demo/sample）· CC 回执

- 编号：`494-stage0-cc-o1-bpath-nbs-local-sample-evidence-receipt-20260827`
- 任务书：`494-stage2-o1-bpath-nbs-local-sample-evidence-tasking-20260827`
- 作者：CC（heartbeat 84）
- cc_head：`6ba7ddc`（双推：origin 2bb2c59..6ba7ddc，github 2bb2c59..6ba7ddc；backfill 单独 commit）
- 日期：2026-08-27

---

## §NOW 对照

| 494 tasking §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) 跑 `scripts/auto_ingest_public_source.py --from-local-sample --pilot-domain=stats.gov.cn --pilot-category=NATIONAL_BULLETIN --confirm-live=<lineage 路径>`（**无网络**；读 registry `local_sample_path`；写 lineage；`intake_status=REGISTRY_SAMPLE_INTAKED`，**`is_demo=true`**） | ✅ 已实跑，exit code **0**；无网络（读 registry 本地样本 `spikes/01-national-yearbook/sample.html`，SHA 与 registry 记录一致）；未加 `--live`，未改 registry `enabled` | grep + shell |
| (2) 回执粘贴命令 + exit code + 关键 stdout + lineage 路径 | ✅ 本回执「证据」段已粘贴完整命令、`EXIT_CODE=0`、关键 stdout 全句、lineage JSONL 原文与落盘路径 | 本文件 |
| (3) `docs/53` §5 新增第 23 项登记（显式 demo/sample，非 O1 收口） | ✅ 第 23 项 blockquote 已落（第 22 项后并列）：标题「O1 B 路 NATIONAL_BULLETIN \`--from-local-sample\` 证据登记（显式 demo/sample）」，正文含 exit code 0 + 无网络说明 + 关键 stdout 摘录 + `intake_status=REGISTRY_SAMPLE_INTAKED`、`is_demo=true`、sample ≠ live closure + 运行副作用如实披露 + 「非真 SHA 收口、非 O1 收口」+「O1 仍 OPEN」；第 21/22 项既有正文原样未动 | grep |
| (4) `docs/45` 刷新四处 | ✅ (a) 文首 queue_rev 241 刷新行（:49，锁链「与 knife 76…112 锁值完全一致」）；(b) §1 一句（:115「O1 B 路 NATIONAL_BULLETIN local-sample 证据登记（per \`494\`）」段）；(c) §6.2 真 SHA 投递入口行尾注（:249 +「B 路 NATIONAL_BULLETIN \`--from-local-sample\` 显式 demo/sample 运行证据已落 docs/53 §5 第 23 项（per \`494\`…）」）；(d) §7 pack invariant 链头 806 → 808（:363，knife 492→490→488 demote 链完整） | grep |
| (5) 回执 `494`（`-cc-`） | ✅ 本文件名 | — |

## 证据

```
$ python3 scripts/auto_ingest_public_source.py --from-local-sample --pilot-domain=stats.gov.cn --pilot-category=NATIONAL_BULLETIN --confirm-live=reviews/stage0-gate0-rework-2026-08-23/20260827T-nbs-national-bulletin-local-sample-lineage.jsonl
OK local-sample pilot matched: stats.gov.cn / NATIONAL_BULLETIN (enabled=TRUE)
   local_sample_path: spikes/01-national-yearbook/sample.html
   expected SHA: dea13b8a4ff116ca…
OK archived: data/public_archives/2026-08/stats.gov.cn/sample.html
OK extract JSON: data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN.json
OK lineage: reviews/stage0-gate0-rework-2026-08-23/20260827T-nbs-national-bulletin-local-sample-lineage.jsonl
OK REGISTRY_SAMPLE_INTAKED (is_demo=true; sample ≠ live closure).
EXIT_CODE=0

$ cat reviews/stage0-gate0-rework-2026-08-23/20260827T-nbs-national-bulletin-local-sample-lineage.jsonl
{"is_demo": "true", "source_file_sha256": "dea13b8a4ff116ca91403b189cdd60705545b28200f9023c3d56e6db03f3939d", "source_file_path": "data/public_archives/2026-08/stats.gov.cn/sample.html", "source_agency": "国家统计局", "intake_ts": "2026-08-27T08:30:38.905492+00:00", "intake_status": "REGISTRY_SAMPLE_INTAKED"}

$ shasum -a 256 <归档 sample> 与 <spikes 样本> | cut -c1-8
  dea13b8a / dea13b8a   （归档 == registry 样本 == lineage source_file_sha256）

$ grep -c "第 23 项（此条）" docs/53…md
  1            （第 23 项已落）

$ grep -n 文首/§1/§6.2/§7 四锚点 docs/45…md
  docs/45:49    （文首 queue_rev 241 刷新行）
  docs/45:115   （§1 一句）
  docs/45:249   （§6.2 真 SHA 投递入口行尾注）
  docs/45:363   （§7 pack invariant 链头 806 → 808）

$ grep -c "O1 仍 OPEN" docs/53…md docs/45…md
  3 / 23        （OPEN 保持核验：未被删减；docs/53 为长单行段式一行含多处出现，按出现计 ×4 含第 23 项新增；docs/45 行计数由 21 增至 23 不减反增）
```

### 运行副作用披露（不静默）

- 本次运行重写了 tracked `data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN.json` 的 `extracted_at` 字段——**唯一 diff**（`2026-08-26T10:48:33…` → `2026-08-27T08:30:38…`），表数据零变化；该文件**不是 4 fixture 锁对象**（锁对象为 `frontend/lib/public_extract_nbs.json` 等）。本刀已 `git checkout` 恢复其 HEAD 字节，理由：易变时间戳字节抖动不利审计收敛，且运行证据已由归档副本 + lineage JSONL + stdout 完整承载。若 Cursor 裁定改为提交该字段刷新，下一刀可补。
- lineage JSONL 与归档副本 `data/public_archives/2026-08/stats.gov.cn/sample.html` 按 drift-report 房规留作**未跟踪**运行产物（不入本刀 commit / manifest）；如需入库待裁定。
- 未跟踪目录 `data/public_archives/` 非 gitignore 对象（`git check-ignore` rc≠0），仅显式不加。

```
$ python3 scripts/_knife494_manifest_bump.py
ADD: scripts/_knife494_manifest_bump.py (3496 bytes, sha=382b61ee)
ADD: reviews/.../494-stage0-cc-o1-bpath-nbs-local-sample-evidence-receipt-20260827.md (8743 bytes, sha=df8a6c82)
UPDATE artifact_count: 806 → 808
INVARIANT: sum(role_count)=808 == artifact_count=808 == len(artifacts)=808
OK manifest updated; added 2 artifacts
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 第 22 项后并列 +1 第 23 项 blockquote 登记 local-sample 显式 demo 运行证据 + 副作用披露；第 21/22 项既有正文原样）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 +1 刷新行 queue_rev 241 + §1 +1 段 + §6.2 行尾注 + §7 链头更新）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife494_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../494-stage0-cc-o1-bpath-nbs-local-sample-evidence-receipt-20260827.md` | NEW（本文件）| `documentation` |

运行产物（未跟踪、不入 manifest）：`reviews/stage0-gate0-rework-2026-08-23/20260827T-nbs-national-bulletin-local-sample-lineage.jsonl`、`data/public_archives/2026-08/stats.gov.cn/sample.html`。

## Pack 不变量

`_knife494_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **806 → 808**；`sum(role_count) == artifact_count == len(artifacts) == 808`（docs/45/docs/53 已入 manifest，SHA REFRESH 不增计数；connector 本刀零改动零新增工件，local-sample 读 registry 样本、无网络写产线；前置 knife 492 回执 `492` 已落 804 → 806；knife 490 `490` 已落 802 → 804；knife 488 `488` 已落 800 → 802；knife 486 `486` 已落 798 → 800；knife 484 `484` 已落 796 → 798；knife 482 `482` 已落 794 → 796；knife 480 `480` 已落 792 → 794；knife 105 `478` 已落 790 → 792；knife 104 `476` 已落 788 → 790；knife 103 `474` 已落 786 → 788；knife 102 `472` 已落 784 → 786；knife 101 `470` 已落 782 → 784；knife 100 `468` 已落 780 → 782；knife 99 `466` 已落 778 → 780；knife 98 `464` 已落 776 → 778）。

## 红线自查

- ❌ 未改代码 / connector `auto_ingest_public_source.py` 零字节改动 / 未实装新爬取代码（local-sample 复用既有模式，无网络）
- ❌ 未 --live / 未启用 Hubei live / 未做 Docker / 未改 registry `enabled`（`--confirm-live` 参数名仅为 connector 的 lineage 写盘出口，非网络 live）
- ❌ 未动 fixture 字节（`shasum -a 256` 前 8 位实测 **disk == HEAD == 锁值**：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`；tracked extract 时间戳重写已恢复 HEAD 字节并披露如上）
- ❌ 未删减 OPEN（「O1 仍 OPEN」docs/45 由 ×21 行增至 ×23 行不减反增、docs/53 ×4；第 23 项显式「非 O1 收口」）
- ❌ 未 Gate/O1 PASS 宣告 / 未谎称真 SHA 收口（`is_demo=true` 显式在位；lineage `intake_status=REGISTRY_SAMPLE_INTAKED`；sample ≠ live closure 双文档登记）
- ❌ 未静默失败（exit code 0 + 全量 stdout 粘贴于回执；运行副作用单列披露段）
- ❌ 未暗示必须用户投喂 / 未换服务器（主路径 = B 路公开源自动获取不变）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `bash scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `494`）。
