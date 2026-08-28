# 579 — 合刀：O3 决策备忘 + 全量 4 failed 继承登记 · CC 回执

- 编号：`579-stage0-cc-o3-memo-inherited-failures-docs-bundle-receipt-20260828`
- 任务书：`579-stage2-o3-memo-inherited-failures-docs-bundle-tasking-20260828`（架构师治理模型第三刀，经 `00-EXEC-QUEUE.md` 签发：PENDING → ACK → DELIVERED；`00-CC-CURRENT.md` 维持冻结勿读勿写；前置 `578` 审计 PASS；合刀 A–G 同 commit、单槽单回执；**docs-only 零网络零代码零 SQL 零 pytest 变更**）
- 前置：`578-stage0-architect-s577-o1-close-s21full-audit-PASS-20260828`（577 审计 PASS；本审计文件随本刀交付 commit 入库、只读未改）；**用户裁定 2026-08-28：O3 OCR 引擎选项 A = paddle-ocr**（架构师于任务书签发后在 §A-4 补注，`00-EXEC-QUEUE.md` note 同步「照录入档」）
- 作者：CC（执行端 Claude Code 终端）
- cc_head：见文末「下一步」（双推后回填）
- 日期：2026-08-28

---

## ⚠ 两处任务书内文与签发后补注不一致的处理（显著披露）

1. **裁定态取代（WAITING_RULING → 已裁定照录）**：任务书 §C/§D 字面写「第 41 项 O3 决策备忘 · WAITING_RULING」，但架构师签发后在 §A-4 补注：**用户 2026-08-28 已裁定选项 A = paddle-ocr**，并明文「docs/45 §3 O3 行尾注同步写明『引擎已裁定 paddle-ocr』」；`00-EXEC-QUEUE.md` §CURRENT note 亦同步「引擎已裁定…照录入档」。处置：docs/53 §5 第 41 项按 §A-4 **照录裁定值、选项全文与裁定日期**（非 WAITING_RULING 字面）；docs/45 §3 行尾注 / §5.5 尾 bullet / 文首刷新行 / §1 段、docs/50 §4.4 第 41 项行 / §5.1 O3 行 / intro 链尾均写明「引擎已裁定 paddle-ocr（2026-08-28）」。**裁定 ≠ O3 收口 ≠ Gate 2 PASS**：仅关闭依赖链 5.2.1（引擎选型），5.2.2–5.2.6 实装链 OPEN，真实 PDF `--confirm-o3=PATH` 为用户保留动作——**O3 仍 OPEN** 全文一致。
2. **§D「§6.2 行尾注」实际落点（沿先例）**：任务书 §D 第三处写「§6.2 行尾注 append（per `579`）」。实测 570/572/574/577 各刀的「§6.2 行尾注」均落在 **§5.5 尾部 O1 bullet**（docs/45 现第 364 行，`578` 审计以「（合刀 per `577`」= 1 锚点接受该落点），并非 §6.2 节本体（§6.2 = S2.7-b-full-lite 接驳路径节，与 O3 无关）。本刀行尾注对称落在紧邻的 **O3 bullet（第 368 行）**，内容 per `579`；docs/45 §6.2 节本体零改动。锚点核验：「per `579`：」于该 bullet = 1。
3. **§E 计数核对（枚举即权威，无偏差）**：任务书 §E 标注 NEW +3（bump 脚本 + `578` 审计文件 + `579` 回执）→ 904 → 907；实测 3 个路径全部不在 manifest（NONE）→ **+3 = 907 无偏差**（577 刀 §F「+14→903」标注错误未复发）。

## §NOW 对照

| 579 tasking §NOW | 交付 | 证据 |
|---|---|---|
| (A) docs/53 §5 第 41 项 O3 决策备忘登记 | ✅ blockquote 插第 40 项后：三选项全文（paddle-ocr 推荐 / tesseract / cloud OCR 默认禁止须 `--enable-cloud-ocr=PROVIDER` 显式 flag + 用户裁定）+ 用户 2026-08-28 裁定 A = paddle-ocr 照录（签发后补注，见 ⚠1）+ 实装依赖链 5.2.1（✅ 裁定关闭）→ 5.2.6（`--confirm-o3=PATH` 非爬源，5.2.2–5.2.6 OPEN）+ 收口标志事件（`is_demo='false'` 翻转：lineage SHA ≠ `'0'*64` + `demo_reason=NULL` + `source_file_url="(OCR_SCAN_FROM_UPLOAD:…)"`）+ 裁定 ≠ O3 收口 ≠ Gate 2 PASS（O3 仍 OPEN；决策就绪登记非收口）| grep（证据段）|
| (B) docs/53 §5 第 42 项 4 failed 继承登记 | ✅ blockquote 插第 41 项后：事实（4 failed / 556 passed / 8 skipped；`578` git 实证全部先于 577 存在于 HEAD `d95d21e`）+ 归因三条（① sample.html 磁盘 SHA dea13b8a… ≠ registry a7e4029d…（`538` 裁定值），spike 样例与权威源文件本非同一对象，registry.csv 红线不可动；② `test_cleanliness` data/ 目录白名单四目录皆历史遗留；③ h2 嵌套复跑 rc=1 内含①②）+ 处置方向（只登记不修码：provenance 口径仅对 `public_extracts/` 强制 / spike 样例免责标注 / data/ 白名单房规化，留后续刀按红线路径裁定）+ 登记 ≠ 修复（存量既有不新增阻塞；Gate 2 OPEN 必带照录）| grep（证据段）|
| (C) docs/50 同步 | ✅ §4.4 +2 行（第 41 项裁定照录里程碑行 + 第 42 项继承登记行）+ intro 收据链 `→ 574 → 577` 续接 `→ 579`（链尾以 `579` 收口）+ §5.1 OPEN 必带清单：O3 行照录「决策备忘已交 + 引擎已裁定 paddle-ocr（2026-08-28 照录），实装仍 OPEN」+ 新增「继承 4 failed」行（已登记 · Gate 2 评审包照录 · 后续刀裁定修法）| grep（证据段）|
| (D) docs/45 同步（五处） | ✅ 文首 +1 第三刀刷新行；§1 +1 段（O3 决策备忘 + 继承登记，含裁定照录与实装链 OPEN）；§3 O3 行尾注（引擎已裁定 paddle-ocr，仅关闭 5.2.1，实装待后续刀 5.2.2–5.2.6）；§6.2 行尾注 → 落点 §5.5 尾 O3 bullet（见 ⚠2，沿 574/577 先例落点族）；§7 链头 `907 == 907 == 907`（+3 枚举）+ knife 577 demote（保留 889→904 历史与 `578` 审计 PASS 注记）；「O1 仍 OPEN」「O3 仍 OPEN」计数非减（166 / 5→9）| grep（证据段）|
| (E) manifest bump | ✅ `scripts/_knife579_manifest_bump.py`：NEW **+3** → **904 → 907**（枚举即权威实测无偏差，见 ⚠3）；REFRESH docs/45 / docs/53 / `00-EXEC-QUEUE.md`（自 577 起已在 manifest，本刀 ACK/DELIVERED 改动 = SHA REFRESH 不增计数）；docs/50 房规 SKIP；回执二次执行 REFRESH 至最终态；断言 `sum(role_count) == artifact_count == len(artifacts) == 907` | bump 输出（证据段）|
| (F) 零网络核验 | ✅ 全部命令 + 输出原样粘贴（证据段）：计数器 O1=166（≥166）/ O3=9（基线 5 非减）；第 41/42 项（此条）=1/=1；907 链头 =1、stale 904 =0；s27bf 25 passed exit 0（零改动防回归）；smoke PASS exit 0；4 fixture 锁值不变；manifest 907 907 907 | 证据段 |
| (G) 回执 + 交付 commit | ✅ 本文件名含 `-cc-`；合刀单槽单回执仅 `579`；交付 commit 含 docs/53、docs/50、docs/45、bump 脚本、`578` 审计文件（只读）、本任务书（只读）、本回执、`00-EXEC-QUEUE.md`（ACK 填行 + status→DELIVERED）| git（会话记录）|

## 证据（命令 + 输出原样粘贴）

```
$ grep -o "O1 仍 OPEN" docs/45-*.md | wc -l        → 166   （≥166，非减 ✅；基线亦 166，本刀零删除）
$ grep -o "O3 仍 OPEN" docs/45-*.md | wc -l        → 9     （基线实测 5 → 9，非减且增长 ✅）
$ grep -c "第 41 项（此条）" docs/53-*.md            → 1     （edit 前 = 0）
$ grep -c "第 42 项（此条）" docs/53-*.md            → 1     （edit 前 = 0）
$ grep -c "907 == 907 == 907" docs/45-*.md          → 1     （stale「904 == 904 == 904」= 0 ✅）
$ grep -c "904 == 904 == 904" docs/45-*.md          → 0

$ python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -q
.........................                                            [100%]
25 passed in 0.83s                                                  EXIT=0
  （零改动防回归：本刀未触碰任何测试文件；git diff 实证仅 docs/53/50/45 + 回执/bump/队列）

$ python3 frontend/smoke-check.py
=== S2.0.1 + S2.7-a + S2.7-a2 + S2.7-b-lite + S2.7-b-full-lite mart-shape + home nav (S2.7-a + S2.7-b + S2.8-lite + S2.9-lite, per tasking 280) smoke: PASS ===
                                                                   EXIT=0

$ shasum -a 256 frontend/lib/public_extract_{nbs,nbs_live_candidate,sz,hubei}.json | cut -c1-8
e30ee811 / 9232efdb / 937255a5 / 9056001c   （disk == 锁值，4 fixture 字节未动）

$ python3 -c "import json;m=json.load(open('evidence_pack/manifest.json'));print(len(m['artifacts']),m['artifact_count'],sum(m['role_count'].values()))"
（bump 前）904 904 904 →（bump 后）907 907 907
```

### 文档锚点 + 计数

```
docs/53:「第 41 项（此条）· O3 决策备忘登记」                                       = 1
docs/53:「第 42 项（此条）· 全量套件 4 failed 继承问题登记」                          = 1
docs/53:「paddle-ocr」出现（三选项 (i) + 裁定照录）                                     = 2
docs/50 §4.4:「docs/53 §5 第 41 项 O3 决策备忘登记」（里程碑行）                      = 1
docs/50 §4.4:「docs/53 §5 第 42 项 全量 4 failed 继承登记」（里程碑行）               = 1
docs/50 intro:「→ `574` → `577` → `579`」                                            = 1
docs/50 intro:「链尾以 `579` 收口」                                                   = 1
docs/50 §5.1:「继承 4 failed」新行 = 1；「引擎用户已裁定」= 2（§5.1 O3 行 + intro 链段）
docs/45 文首:「架构师治理模型第三刀（per `579-…tasking`」                             = 1
docs/45 §1:「O3 决策备忘 + 继承 4 failed 登记（per `579`」                            = 1
docs/45 §3 O3 行:「引擎已裁定 **paddle-ocr**（用户 2026-08-28；仅关闭 5.2.1）」        = 1
docs/45 §5.5 尾 O3 bullet:「O3 决策备忘已交（per `579`：」                            = 1
docs/45 §7:「907 == 907 == 907」                                                     = 1
docs/45 stale「904 == 904 == 904」                                                   = 0  （已由 §7 链头更新承接）
「O1 仍 OPEN」计数：docs/45 = 166（非减 ✅）；「O3 仍 OPEN」docs/45 = 5 → 9（非减 ✅）
00-EXEC-QUEUE.md（ACK 填行 + status→DELIVERED）在位待入库
```

```
$ python3 scripts/_knife579_manifest_bump.py（首跑）
ADD: scripts/_knife579_manifest_bump.py (6242 bytes, sha=5e57ed04)
ADD: reviews/stage0-gate0-rework-2026-08-23/578-stage0-architect-s577-o1-close-s21full-audit-PASS-20260828.md (6646 bytes, sha=a2059fd1)
ADD: reviews/stage0-gate0-rework-2026-08-23/579-stage0-cc-o3-memo-inherited-failures-docs-bundle-receipt-20260828.md (15205 bytes, sha=e5f1e86a)
REFRESH: docs/45-stage2-s210-lite-gate2-review-index-20260826.md sha=50076666 → a115106d (269940 bytes; no count change)
NOT-IN-MANIFEST (房规 skip, no count change): docs/50-stage2-gate2-review-packet-draft-20260826.md
REFRESH: docs/53-stage2-public-ingest-ops-handbook-20260826.md sha=0aee13d8 → 9becf2c4 (64995 bytes; no count change)
REFRESH: reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md sha=8777745c → bcb0c4ec (2633 bytes; no count change)
REFRESH (unchanged): reviews/stage0-gate0-rework-2026-08-23/579-stage0-cc-o3-memo-inherited-failures-docs-bundle-receipt-20260828.md sha=e5f1e86a
UPDATE artifact_count: 904 → 907
INVARIANT: sum(role_count)=907 == artifact_count=907 == len(artifacts)=907
OK manifest updated; added 3 artifacts
  （首跑 ADD 时回执为粘贴前状态 e5f1e86a；下方末次执行将本回执条目 REFRESH 至最终字节）

$ python3 scripts/_knife579_manifest_bump.py（末次：回执粘贴首跑输出后运行）
（+3 条目已在位 → SKIP；REFRESH 本回执 SHA → 本文件最终字节；docs/45/53/queue REFRESH；
 INVARIANT 907 == 907 == 907 —— manifest 中本回执条目 SHA 即本文件最终态；此后本文件不再
 变更（cc_head backfill 为独立 commit，房规允许））
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 新增第 41 项 O3 决策备忘 + 第 42 项 4 failed 继承登记 blockquote；第 21–40 项既有正文原样未动）| 已入 manifest（SHA REFRESH 不增计数）|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | MODIFIED（§4.4 +2 行 + intro 链尾续接 `→ 579` + §5.1 O3 行照录 + 新增继承 4 failed 行）| **房规未入 manifest**（镜像 574/577 先例；显式 SKIP 不增计数）|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 +1 刷新行 + §1 +1 段 + §3 O3 行尾注 + §5.5 尾 O3 bullet 行尾注（⚠2 落点披露）+ §7 链头 907 + knife 577 demote）| 已入 manifest（SHA REFRESH 不增计数）|
| `scripts/_knife579_manifest_bump.py` | NEW（本刀 bump 脚本：ADD +3 + REFRESH + 907 断言）| `spike_helper` |
| `reviews/.../578-stage0-architect-s577-o1-close-s21full-audit-PASS-20260828.md` | NEW（架构师资产，**只读随刀入库、内容零改动**）| `documentation` |
| `reviews/.../579-stage2-o3-memo-inherited-failures-docs-bundle-tasking-20260828.md` | NEW（架构师任务书，含签发后 §A-4 裁定补注，**只读随刀入库**）| 未入 manifest（任务书按先例不计数；574/577 先例一致）|
| `reviews/.../579-stage0-cc-o3-memo-inherited-failures-docs-bundle-receipt-20260828.md` | NEW（本文件）| `documentation` |
| `reviews/.../00-EXEC-QUEUE.md` | MODIFIED（§ACK 新增 579 认领行 + §CURRENT status→DELIVERED + note 回执号；架构师签发后补注 §META 常设授权 + §CURRENT note 引擎裁定随本刀状态一并入库）| 已入 manifest（SHA REFRESH 不增计数，自 577 起在册）|
| `evidence_pack/manifest.json` | MODIFIED（bump 产物：ADD +3 → 907；REFRESH docs/45 + docs/53 + queue + 本回执最终态）| manifest 本体 |

注：本刀 **docs-only**——零代码 / 零 SQL / 零 schema / 零 pytest 变更 / 零 dbt 实跑（s27bf + smoke 为零改动防回归核验，非变更）；registry.csv / gate_thresholds.json / `00-CC-CURRENT.md`（勿读勿写）/ 4 fixture 字节 / 既有测试与 mart SQL / migration 001–013 零触碰；4 failed 只登记不修码；未跟踪运行产物维持不入 manifest 房规。

## Pack 不变量

`_knife579_manifest_bump.py`：NEW_ARTIFACTS **+3** → **904 → 907**（§E 枚举即权威，3 项实测均不在 manifest，无偏差——577 §F 计数标注错误未复发）；断言 `sum(role_count) == artifact_count == len(artifacts) == 907`（脚本内强制 + §F 实测 `907 907 907`）；docs/45 / docs/53 / `00-EXEC-QUEUE.md` SHA REFRESH 不增计数；docs/50 房规未入 manifest → 显式 SKIP；任务书按先例不入 manifest；本回执条目 SHA 经 bump 二次执行 REFRESH 至粘贴输出后的最终态。前置链条：knife 577 已落 889 → 904；knife 574 已落 886 → 889（此前链条见 577 回执 §Pack 不变量，原样承接不再复述）。

## 红线自查

- ❌ 本刀 docs-only：零代码 / 零 SQL / 零 schema / 零 pytest 变更 / 零 dbt 实跑（git diff 实证仅 docs/53/50/45 + 回执/bump 脚本/队列/任务书/审计文件）
- ❌ 不宣布 Gate 0/1/2 PASS：**O3 决策备忘 ≠ O3 收口 ≠ Gate 2 PASS**；引擎裁定（paddle-ocr）仅关闭 5.2.1，5.2.2–5.2.6 实装链 OPEN，真实 PDF `--confirm-o3=PATH` 为用户保留动作；**O3 仍 OPEN** 全文一致；未替用户扩大裁定范围（照录 §A-4 补注值）
- ❌ 未动 registry.csv / gate_thresholds.json / `00-CC-CURRENT.md`（勿读勿写）/ 4 fixture 字节（实测锁值 e30ee811 / 9232efdb / 937255a5 / 9056001c）/ 既有测试与 mart SQL / migration 001–013
- ❌ 4 failed **只登记不修码**（处置方向登记于 docs/53 第 42 项，修法留后续刀按红线路径裁定）
- ❌ 无 --force / PAT / 公网 redeploy / 网络爬取；既有 OPEN 行零删减（O1 = 166 非减；O3 = 5 → 9 增长）
- ❌ 未谎称收口、未静默失败：裁定态取代（⚠1）与行尾注落点（⚠2）显著披露于文首
- ✅ manifest 904 → 907 不变量（+3 枚举即权威，逐项核对防 ⚠ 复发，实测无偏差）；回执位于 `reviews/stage0-gate0-rework-2026-08-23/`；文件名含 `-cc-`；合刀单槽单回执仅 `579`
- ✅ 不复述架构师长文（仅引用任务书/审计号 + 简短语）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推、严格顺序** per tasking）→ 回填 cc_head（单独 commit，勿 amend，再双推）→ queue status → DELIVERED（已随本刀 commit）→ **停止并回报 cc_head**。架构师将出 `580` 号位审计。O3 引擎裁定已照录（paddle-ocr）；实装刀（`58X`）与 `--confirm-o3=PATH` 真实 PDF 待架构师签发/用户提供。

## cc_head（交付后回填，独立 commit）

- （待回填）
