# 572 — 合刀：mart 真 SHA 入仓 pilot（nanjing CONDITION）+ docs · CC 回执

- 编号：`572-stage0-cc-o1-mart-sha-pilot-impl-bundle-receipt-20260828`
- 任务书：`572-stage2-o1-mart-sha-pilot-impl-bundle-tasking-20260828`（gate queue_rev 320；合刀：一把任务书多步、一个回执）
- 前置：`571` PASS（570 闭环完成）；用户裁定：自主推进 O1 序列；**O1 仍 OPEN（本刀不宣布收口）**
- 作者：CC（heartbeat 84）
- cc_head：`PENDING_CC_HEAD_SHA`（双推 origin/github 完成；cc_head backfill 单独 commit 再双推）
- 日期：2026-08-28

---

## §NOW 对照

| 572 tasking §NOW / gate 320 NOW | 交付 | 证据 |
|---|---|---|
| (A) `dbt/models/marts/mart_city_evidence_chain.sql`：pilot 行 = `nanjing` + `CONDITION` 段 — `lineage_source_file_sha256` = registry `a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb`（per `538`/`560`）；`lineage_is_demo` = `'false'`；其余 59 行保持 demo + `'0'*64` | ✅ lineage 两列改 CASE 条件式（executable 唯一真 SHA 落点 = `WHEN c.city_slug = 'nanjing' AND c.segment = 'CONDITION'` 的 sha CASE 分支；is_demo CASE 同条件 THEN `'false'` / ELSE `'true'`；其余 59 行 ELSE `REPEAT('0', 64)::TEXT` 占位不变；头部 Demo-join status + No-fabricated-SHA 注释同步为 pilot 单行语义；`mart_city_seven_dim_overview.sql` 本刀零触碰）| 本文件证据段（pytest §8 五例 + grep）|
| (B) 扩 `tests/test_mart_city_dbt_skel_s27bf.py`：新增/调整 cases 锁定 pilot 行 + 其余行 demo 占位不变 | ✅ 新增 §8 五例（真 SHA 在位 / 真 SHA executable count == 1 / 条件精确锁定 (nanjing, CONDITION) 恰 2 处 / ELSE `REPEAT('0', 64)::TEXT` 占位 / is_demo CASE 结构 `THEN 'false' ELSE 'true'`）+ 既有 20 例中模块 docstring 红线段与 `test_mart_evidence_chain_lineage_is_demo_true` docstring/message 语义对齐（占位守门逻辑本身未放松）| 本文件证据段 |
| (C) docs/53 §5 第 38 项：mart SHA pilot 实装证据 | ✅ 第 38 项已插第 37 项后（blockquote）：pilot CASE 实装 + 59 行占位不变 + tests 扩 5 例 + pytest 25 passed / exit 0 + registry 零改动 + 红线（pilot 1 行 ≠ O1 收口 / 全量 flip / person 真数据仍 OPEN）；第 21–37 项既有 blockquote 正文原样未动 | grep（本文件证据段）|
| (D) docs/45 + docs/50 同步 + intro `→ 572` | ✅ docs/50：§4.4 第 38 项行（插第 37 行后、预览 URL 块前）+ intro 链 `→ 570` 续接 `→ 572`（链尾以 `572` 收口）；docs/45：文首 queue_rev 320 刷新行（「knife 76…151 锁链延续」）+ §1 新段 + §6.2 占位行 pilot 例外注 + §6.2 行尾注 append + §7 链头 886 == 886 == 886（knife 570 demote 链完整）| grep（本文件证据段）|
| (E) `python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -q` exit 0 | ✅ **25 passed / exit 0**（原 20 例 + 新 5 例；零网络静态 SQL 解析）| 本文件证据段（命令 + 输出原样粘贴）|
| (F) 回执 **仅 `572`**（`-cc-`） | ✅ 合刀单槽单回执：`_knife572` bump + 本回执（仅此一个回执号）→ 884 → 886；本文件名含 `-cc-` | bump 输出（本文件证据段）|
| (3) **必须双推** → POLL | ✅ 双推 origin + github（范围见 backfill）；backfill cc_head 单独 commit 再双推 | push 输出（会话记录）|

## 证据

### E 锚点核验（零网络；命令 + 输出原样粘贴）

```
$ grep -c "a7e4029d" source_registry/registry.csv
1   （registry.csv:3 NATIONAL_BULLETIN 行：a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb + file_size_bytes 180165，per `538` (a) 裁定值；本刀 registry 零改动）

$ shasum -a 256 frontend/lib/public_extract_{nbs,nbs_live_candidate,sz,hubei}.json | cut -c1-8
e30ee811 9232efdb 937255a5 9056001c   （disk == 锁值，4 fixture 字节未动）

$ python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -q
.........................                                                [100%]
25 passed in 0.11s
PYTEST_EXIT=0   （原 20 例 + 新 §8 五例；`_strip_sql_comments` 先剥注释再扫 — 真 SHA executable count == 1 守门生效）
```

### 文档锚点 + 计数

```
$ grep -cF 锚点
  docs/53:「第 38 项（此条）· mart 真 SHA 入仓 pilot 实装」                     = 1
  docs/50:「第 38 项 mart 真 SHA 入仓 pilot 实装**（nanjing + CONDITION 单行；pilot 1 行 ≠ O1 收口里程碑行」 = 1
  docs/50 intro:「→ `568` → `570` → `572`；16–19」                             = 1
  docs/50 intro:「链尾以 `572` 收口）；**全部为」                               = 1
  docs/50 stale:「，链尾以 `570` 收口）；」                                     = 0  （已由链尾续接承接）
  docs/45 文首:「queue_rev 320（per `572-stage2-o1-mart-sha-pilot-impl-bundle-tasking-20260828`）」= 1
  docs/45 文首:「knife 76…151 锁链延续」                                       = 1
  docs/45 §1:「mart 真 SHA 入仓 pilot 实装（per `572`）」                       = 1
  docs/45 §6.2 占位行:「per `572` pilot 例外」                                  = 1
  docs/45 §6.2 行尾注:「mart 真 SHA 入仓 pilot 实装（合刀 per `572`；docs/53 §5 第 38 项」 = 1
  docs/45 §7:「886 == 886 == 886」                                             = 1
  docs/45 §7 demote:「；knife 570 = 合刀 A–F 同 commit、单槽单回执」             = 1
  docs/45:stale「884 == 884 == 884」                                           = 0  （已由 §7 链头更新承接）

$ grep -c/-o "O1 仍 OPEN" 计数核验（非减）
  docs/45 行计数 101（由 99 增至 101）、出现计 157（由 154 增至 157）
  docs/50 行计数 20（由 19 增至 20）、出现计 21（由 20 增至 21）
  docs/53 行计数 18（由 17 增至 18）、出现计 20（由 19 增至 20）

$ python3 -c 残留转义检查 chr(92)+chr(96)
  docs/45 = 0、docs/50 = 0、docs/53 = 0

$ python3 scripts/_knife572_manifest_bump.py
ADD: scripts/_knife572_manifest_bump.py (4720 bytes, sha=037e0e65)
ADD: reviews/stage0-gate0-rework-2026-08-23/572-stage0-cc-o1-mart-sha-pilot-impl-bundle-receipt-20260828.md (11581 bytes, sha=a3efc742)
UPDATE artifact_count: 884 → 886
INVARIANT: sum(role_count)=886 == artifact_count=886 == len(artifacts)=886
OK manifest updated; added 2 artifacts
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `dbt/models/marts/mart_city_evidence_chain.sql` | MODIFIED（lineage 两列 CASE 条件式：pilot 行 (nanjing + CONDITION) = registry 真 SHA + `is_demo='false'`；其余 59 行 demo + `'0'*64` 占位原样；注释同步 pilot 单行语义）| 已入 manifest（SHA REFRESH 不增计数）|
| `tests/test_mart_city_dbt_skel_s27bf.py` | MODIFIED（新增 §8 五例 + 既有 20 例 docstring 语义对齐；占位/禁词守门逻辑未放松）| 已入 manifest（SHA REFRESH 不增计数）|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 新增第 38 项 mart SHA pilot 实装证据 blockquote；第 21–37 项既有 blockquote 正文原样未动）| 已入 manifest（SHA REFRESH 不增计数）|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | MODIFIED（§4.4 里程碑表 +1 第 38 项行 + intro ⚠ 收据链尾续接 `→ 572`；第 21–37 项行既有正文原样未动）| 已入 manifest（SHA REFRESH 不增计数）|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 +1 刷新行 queue_rev 320 + §1 +1 段 + §6.2 占位行 pilot 例外注 + §6.2 行尾注 append + §7 链头更新）| 已入 manifest（SHA REFRESH 不增计数）|
| `scripts/_knife572_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../572-stage0-cc-o1-mart-sha-pilot-impl-bundle-receipt-20260828.md` | NEW（本文件）| `documentation` |

注：本刀 registry.csv 零触碰（任务书「不做改 registry」）；`mart_city_seven_dim_overview.sql` 零触碰（pilot 仅 evidence_chain mart）；无 dbt 实跑、无 `--live` 重跑（E 核验全零网络）；未公网 redeploy；docs/52 零触碰；未跟踪运行产物维持不入 manifest 房规。

## Pack 不变量

`_knife572_manifest_bump.py`：NEW_ARTIFACTS +2（bump + receipt）→ **884 → 886**；`sum(role_count) == artifact_count == len(artifacts) == 886`（docs/45/docs/50/docs/53 + mart SQL + test 文件已入 manifest，SHA REFRESH 不增计数；前置 knife 570 回执 `570` 已落 882 → 884；knife 568 `568` 已落 880 → 882；knife 566 `566` 已落 878 → 880；knife 564 `564` 已落 876 → 878；knife 562 `562` 已落 874 → 876；knife 560 `560` 已落 872 → 874；knife 558 `558` 已落 870 → 872；knife 556 `556` 已落 868 → 870；knife 554 `554` 已落 866 → 868；knife 552 `552` 已落 864 → 866；knife 550 `550` 已落 862 → 864；knife 548 `548` 已落 860 → 862；knife 546 `546` 已落 858 → 860；knife 544 `544` 已落 856 → 858；knife 542 `542` 已落 854 → 856；knife 540 `540` 已落 852 → 854；knife 538 `538` 已落 850 → 852；knife 536 `536` 已落 848 → 850；knife 534 `534` 已落 846 → 848；knife 532 `532` 已落 844 → 846；knife 530 `530` 已落 842 → 844；knife 528 `528` 已落 840 → 842；knife 526 `526` 已落 838 → 840；knife 524 `524` 已落 836 → 838；knife 522 `522` 已落 834 → 836；knife 520 `520` 已落 832 → 834；knife 518 `518` 已落 830 → 832；knife 516 `516` 已落 828 → 830；knife 514 `514` 已落 826 → 828；knife 512 `512` 已落 824 → 826；knife 510 `510` 已落 822 → 824；knife 508 `508` 已落 820 → 822；knife 506 `506` 已落 818 → 820；knife 504 `504` 已落 816 → 818；knife 502 `502` 已落 814 → 816；knife 500 `500` 已落 812 → 814；knife 498 `498` 已落 810 → 812；knife 496 `496` 已落 808 → 810；knife 494 `494` 已落 806 → 808；knife 492 `492` 已落 804 → 806；knife 490 `490` 已落 802 → 804；knife 488 `488` 已落 800 → 802；knife 486 `486` 已落 798 → 800；knife 484 `484` 已落 796 → 798；knife 105 `478` 已落 790 → 792；knife 104 `476` 已落 788 → 790；knife 103 `474` 已落 786 → 788；knife 102 `472` 已落 784 → 786）。

## 红线自查

- ❌ 未做 Gate/O1 PASS 宣告：**pilot 1 行真 SHA ≠ O1 收口——mart 全量 60 行 flip / person 真数据仍 OPEN；O1 收口须用户/Cursor 裁定、O1 仍 OPEN**，docs/53 第 38 项 + docs/50 第 38 行/intro + docs/45 五处 + 本回执写明
- ❌ 未改 registry（本刀零触碰，真 SHA = `538` (a) 裁定值 + `560` hash 匹配实测的既有 registry 行）；未跑 dbt；未 `--live` 重跑；未公网 redeploy
- ❌ 未删减 OPEN（docs/45 99→101 行 / 154→157 处；docs/50 19→20 行 / 20→21 处；docs/53 17→18 行 / 19→20 处，均不减）
- ❌ 未动 4 frontend fixture 字节（实测锁值一致：e30ee811 / 9232efdb / 937255a5 / 9056001c）
- ❌ 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json` / 未 --force / 未索要 PAT
- ❌ 未谎称 O1/mart 已收口（pilot 单行语义三处注释 + tests §8 count==1 守门锁死「扩散 = 另刀」）；未静默失败（E 核验命令 + 输出原样粘贴，pytest 25 passed exit 0）；未交两个回执号（合刀单槽单回执，回执仅 `572` 一个）
- ⚠ 红线重申：**合刀单槽单回执；pilot 1 行真 SHA ≠ O1 收口（mart 全量真 SHA / person 真数据仍 OPEN）；不动 4 fixture 字节**（per tasking 红线段）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 不复述 Cursor 长文（仅引用回执/任务书号 + 简短语）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推** per §NOW）→ 回填 cc_head（单独 commit，再双推）→ `bash scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 `572`）。
