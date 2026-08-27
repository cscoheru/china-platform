# 510 — O1 B 路 NBS live-candidate 探测证据登记 · CC 回执

- 编号：`510-stage0-cc-o1-bpath-nbs-live-probe-evidence-receipt-20260827`
- 任务书：`510-stage2-o1-bpath-nbs-live-candidate-probe-evidence-tasking-20260827`
- 作者：CC（heartbeat 84）
- cc_head：`87dd859`（双推：origin 5977499..87dd859，github 5977499..87dd859；backfill 单独 commit）
- 日期：2026-08-27

---

## §NOW 对照

| 510 tasking §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) 跑 `scripts/auto_ingest_public_source.py --live --pilot-domain=stats.gov.cn --pilot-category=NATIONAL_BULLETIN --confirm-live=reviews/stage0-gate0-rework-2026-08-23/20260827T-nbs-national-bulletin-live-candidate-lineage.jsonl`（**有网络**；写 lineage；遇 AUTH/TECH 阻停如实报告） | ✅ 已按字实跑，exit code **0**：pilot matched → deeplink `t20260827_1965129.html` → download 180165 bytes sha256 `a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb` ≠ registry expected `dea13b8a4ff116ca…` → SHA drift 非静默处理（CANDIDATE_AUTO，见 (3) 与证据段）。无 AUTH/CAPTCHA 阻停（公开直连成功）；未绕任何技术限制 | 本文件命令+stdout 段 |
| (2) 回执粘贴命令 + exit code + 关键 stdout + lineage 路径 | ✅ 见「探测运行记录」节逐行粘贴 | 本文件 |
| (3) `docs/53` §5 新增 **第 26 项**登记（live-candidate 探测证据，非 O1 收口） | ✅ 第 26 项 blockquote 已落（:164）：完整命令、exit、下载字节与 SHA、drift 处理、lineage 字段；**如实披露两点**——WORM 幂等未覆盖（本刀实测字节未持久化至既有归档路径）+ 自动 drift 报告「已写入」模板句与磁盘实测不符（以磁盘为准）；第 21–25 项既有正文原样 | grep |
| (4) `docs/45` 刷新四处 | ✅ (a) 文首 queue_rev 257 刷新行；(b) §1 第 26 项段；(c) §6.2 真 SHA 投递入口行尾注 append；(d) §7 pack invariant 链头 822 → 824（knife 508→506 demote 链完整） | grep |
| (5) 回执 **`510`**（`-cc-`） | ✅ 本文件名 | — |

## 探测运行记录（tasking (2) 粘贴）

```
$ python3 scripts/auto_ingest_public_source.py --live \
    --pilot-domain=stats.gov.cn \
    --pilot-category=NATIONAL_BULLETIN \
    --confirm-live=reviews/stage0-gate0-rework-2026-08-23/20260827T-nbs-national-bulletin-live-candidate-lineage.jsonl

⚠ drift report written: …/reviews/stage0-gate0-rework-2026-08-23/20260827T122022Z-stage2-public-source-sha-drift-stats.gov.cn-NATIONAL_BULLETIN.md
⚠ CANDIDATE_AUTO lineage emitted; rc=4 means drift handled, NOT O1 收口。等用户裁定。
OK pilot matched: stats.gov.cn / NATIONAL_BULLETIN
   primary_url: https://www.stats.gov.cn/sj/zxfb/
   auth_note: 公开；无需授权
   expected SHA: dea13b8a4ff116ca…
OK deeplink discovered: https://www.stats.gov.cn/sj/zxfb/202608/t20260827_1965129.html
OK downloaded 180165 bytes; sha256=a7e4029df707918a…
⚠ SHA drift; archived drifted bytes: …/data/public_archives/2026-08/stats.gov.cn/zxfb
EXIT_CODE=0
```

lineage JSONL（落盘于任务书指定路径；房规保持未跟踪、不入 manifest）：

```json
{"is_demo": "true", "source_file_sha256": "a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb", "source_file_path": "data/public_archives/2026-08/stats.gov.cn/zxfb", "source_agency": "国家统计局", "intake_ts": "2026-08-27T12:20:22.498551+00:00", "intake_status": "CANDIDATE_AUTO"}
```

## ⚠ 如实披露（非静默失败）

1. **WORM 幂等未覆盖**：archive() 目标路径 `data/public_archives/2026-08/stats.gov.cn/zxfb` 已存在（tracked clean，sha256 前 8 位 `0b85212f`，mtime 早于本刀），脚本对已存在路径按幂等语义直接返回——**本刀实测下载的 180165 字节（sha256 `a7e4029d…`）未持久化到磁盘**，运行输出的「archived drifted bytes」消息指向的是该既有文件而非本刀字节；lineage 的 `source_file_path` 同样指向该既有路径。
2. **自动 drift 报告措辞差异**：工具生成的 drift 报告含「WORM 归档实测字节：已写入」模板句，与上述磁盘事实不符。drift 报告原件未改动（保留工具原样输出作证物），以磁盘实测为准；模板修正属代码变更、超出本刀 docs-only+指定 connector 实跑范围，留后续用户裁定/Cursor 裁定。
3. 候选轨处置等用户裁定二选一：(a) 更新 registry.csv `file_hash_sha256` 为实测值（认定源站换版）；(b) 改用稳定归档 URL。connector 不自动改 registry。

## 证据

```
$ grep -n 四锚点 docs/45…md
  文首 queue_rev 257 刷新行（:57）
  §1 「探测实跑证据登记（per `510`）」段（:138）
  §6.2 行尾注 append（「已登记 docs/53 §5 第 26 项（per `510`…」）
  §7 pack invariant 链头 822 → 824（:386）

$ grep -n '第 26 项（此条）' docs/53…md
  docs/53:164   （§5 第 26 项 blockquote 已落）

$ grep -c/-o "O1 仍 OPEN" 计数核验
  docs/45 行计数 40（由 38 增至 40）、出现计 58（由 55 增至 58）—— 不减反增
  docs/50 行计 6、出现计 6 —— 保持
  docs/53 行计 6（由 5 增至 6）、出现计 7（由 6 增至 7）—— 不减反增

$ git status --porcelain | grep -v '^??'
  仅 M docs/45 + M docs/53（两件运行产物均为 untracked 房规产物；
  既有 reviews D-anomaly 照旧未触碰）
  tracked fixture/extract/archive 字节零变化

$ shasum -a 256 frontend/lib/public_extract_{nbs,nbs_live_candidate,sz,hubei}.json | cut -c1-8
  e30ee811 9232efdb 937255a5 9056001c   （disk == HEAD == 锁值，未动 fixture 字节）

$ python3 scripts/_knife510_manifest_bump.py
ADD: scripts/_knife510_manifest_bump.py (3482 bytes, sha=c5f615b8)
ADD: reviews/.../510-stage0-cc-o1-bpath-nbs-live-probe-evidence-receipt-20260827.md (9143 bytes, sha=b7b85ec7)
UPDATE artifact_count: 822 → 824
INVARIANT: sum(role_count)=824 == artifact_count=824 == len(artifacts)=824
OK manifest updated; added 2 artifacts
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 新增第 26 项 blockquote 一处；第 21–25 项既有正文原样）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 +1 刷新行 queue_rev 257 + §1 +1 段 + §6.2 行尾注 + §7 链头更新）| 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例）|
| `scripts/_knife510_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../510-stage0-cc-o1-bpath-nbs-live-probe-evidence-receipt-20260827.md` | NEW（本文件）| `documentation` |
| `reviews/.../20260827T-nbs-national-bulletin-live-candidate-lineage.jsonl` | NEW 运行产物 | 未跟踪，不入 manifest（k494 lineage JSONL 房规先例）|
| `reviews/.../20260827T122022Z-stage2-public-source-sha-drift-stats.gov.cn-NATIONAL_BULLETIN.md` | NEW 运行产物 | 未跟踪，不入 manifest（drift-report 房规先例）|

## Pack 不变量

`_knife510_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **822 → 824**；`sum(role_count) == artifact_count == len(artifacts) == 824`（docs/45/docs/53 已入 manifest，SHA REFRESH 不增计数；两件探测运行产物未跟踪不入 manifest；前置 knife 508 回执 `508` 已落 820 → 822；knife 506 `506` 已落 818 → 820；knife 504 `504` 已落 816 → 818；knife 502 `502` 已落 814 → 816；knife 500 `500` 已落 812 → 814；knife 498 `498` 已落 810 → 812；knife 496 `496` 已落 808 → 810；knife 494 `494` 已落 806 → 808；knife 492 `492` 已落 804 → 806；knife 490 `490` 已落 802 → 804；knife 488 `488` 已落 800 → 802；knife 486 `486` 已落 798 → 800；knife 484 `484` 已落 796 → 798；knife 482 `482` 已落 794 → 796；knife 480 `480` 已落 792 → 794；knife 105 `478` 已落 790 → 792；knife 104 `476` 已落 788 → 790；knife 103 `474` 已落 786 → 788；knife 102 `472` 已落 784 → 786）。

## 红线自查

- ❌ 未改代码（唯一 `--live` 实跑 = tasking 显式授权的既定 connector 命令，零参数偏移）/ 未启用 Hubei live / 未做 Docker / **registry `enabled` 与 `file_hash_sha256` 均未改**
- ❌ 未删减 OPEN（docs/45 行计数 38→40、docs/50 6 保持、docs/53 行 5→6 出现计 6→7 均不减反增或保持）
- ❌ 未 Gate/O1 PASS 宣告 / `is_demo=true`（CANDIDATE_AUTO）未谎称真 SHA 收口 / drift ≠ 收口已三处写明
- ❌ 未暗示必须用户投喂 / 未换服务器 / 无 headless、未绕验证码/付费墙/登录/技术限制（公开直连成功即止）
- ❌ 未动 docs/53 第 21–25 项既有正文 / 未动 docs/52/docs/50（本刀零触碰）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ❌ 未动 fixture 字节（四锁 disk == HEAD == 锁值实测通过；tracked 树仅两 docs MODIFIED）
- ⚠ 两处非静默披露已写入回执与 docs/53 第 26 项（WORM 幂等未覆盖 + 自动报告模板句差异）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执号 + 简短语）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `bash scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `510`）。
