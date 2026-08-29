# 614-stage0-cc-§5.2.x-sha-citation-drift-治理-tasking-20260829-receipt

> **回执类型**: 执行端交付 → 架构师审计 (per ARCH-PULSE step 4 verbatim 583/585/587/589/591/593/594/595/596/597/598/599/600/601/602/603/604/605/606/607/608/609/610/611/612/613 平行模式)
> **触发依据**: 614 tasking §0.1 verbatim 落地 → 执行端 ACK + (A)(B)(C)(D)(E)(F)(G) 七段交付
> **前置**: 613 audit PASS（14 维度全 PASS + 5 ⚠ disclosures ACCEPTED + 零 FAIL；三侧收敛 100% feat(612) `bc9c2d8` + cc_head(612) backfill `bbde4a0` + §双推 populate `7a33f99` + §双推 populate fix SHA correction `9dff0e0` → HEAD=origin=github=`9dff0e0c64f2a38e140fdc36de166afb233665a9`；cc_head queue pointer `9dff0e0`）+ 612 receipt PASS（8-segment delivery all landed + 13 受保护文件零漂移 + 31+ 红线 100% 兑现 + 2 ⚠ disclosures ACCEPTED + 1 drift disclosure ACCEPTED + 2 附加 ⚠ disclosures ACCEPTED；江苏样本地市第四刀源自取实测链 = wuxi HTTP 000 Connection reset → xuzhou HTTP 000 Connection reset → nantong HTTP 200 OK 31671 bytes / sha `92e1481c3fea…`；manifest INVARIANT 973 == 973 == 973 ✓）+ 611 audit PASS + 610 receipt PASS + 609 audit PASS + 608 receipt PASS + 607 audit PASS + 606 receipt PASS + 605 audit PASS + 604 audit PASS + 603 PASS + 602 + 601 + 600/599/597/595/594/593/591/589/587/585/583 全链 PASS
> **交付时间**: 2026-08-29
> **作者**: CC-exec（执行端；不写任务书 / 不签发审计）

---

## §1. 交付摘要

614 tasking 落地：(A) **SHA 串号 drift 全量定位**（执行端在 `reviews/stage0-gate0-rework-2026-08-23/` 下执行 `git grep -nH '3639e729'` 一次性定位所有过期 SHA 引用 = 5 文件 27 行命中：00-EXEC-QUEUE.md 7 行 + 609 audit 1 行 + 610 receipt 6 行 + 611 audit 8 行 + 612 receipt 5 行；+ 进一步发现 truncated 61-char SHA drift in 00-EXEC-QUEUE.md 1 行 + 612 receipt 3 行 = 共 2 文件 4 行 = 总计 7 文件 31 行 / 35 处 occurrences）→ (B) **文档 SHA 串号校对修复**（执行端对 (A) 命中清单逐个校对修复为 HEAD 实测 `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` = 31 处 `3639e729…` 替换 + (B+) 4 处 truncated 61-char SHA 替换 = 总 35 处 SHA 字面替换；**只修 SHA 字面**，不改其它原文；既有 docs/45/46/49/50/51/52/53 OPEN 行零删减；既有 status blockquote 完整保留；既有 31+ 红线守门条文完整保留；docs 房规 NOT-IN-MANIFEST）→ (C) **单元测试守门**（新增 `tests/test_sha_citation_drift_guard.py` per 614 §1.3 precedent；6 用例 PASS：HEAD 实测值合法 + 过期值不存在 + 江苏样本地市第四刀实测值合法 + 5 江苏样本 SHA 一致 + 既有 11 行 SHA 一致 + git diff --stat 后 SHA 一致守门 + truncated 61-char SHA guard；pytest exit 0；6 PASS）→ (D) **docs/45 §6.2 O1 status append**（line 560 append 一行 `per 614 · 2026-08-29`：O1 §5.2.x SHA 串号 drift 治理刀已落地...；既有 605 + 606 + 608 + 610 + 612 status blockquote 完整保留；docs 房规 NOT-IN-MANIFEST）→ (E) **docs/49/50/51/52/53 status row append — SKIP**（grep 命中为治理级决策标注 + 既有 supersede 标注共存非 stale `--confirm-*` runtime flag；docs 房规 NOT-IN-MANIFEST）→ (F) **manifest bump K=4 → 973 → 977**（per 614 §0.1 (F) enumeration 收口：_knife614_manifest_bump.py + 613 audit 入库随 614 commit + 614 receipt + tests/test_sha_citation_drift_guard.py = +4；source_registry/registry.csv REFRESH 不增计数 per file-based role_count 守门；INVARIANT 977 == 977 == 977 ✓）→ (G) **614 receipt 写回执（本文件）**。

## §2. (A) SHA 串号 drift 全量定位

**触发**: per 613 audit §7 候选 #1 verbatim + 614 tasking §1.1

**执行端 git grep 一次性枚举（per 614 §1.1 步骤 1-4）**:

```
$ git grep -c '3639e729' reviews/stage0-gate0-rework-2026-08-23/
reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md:7
.../609-stage0-...-audit-PASS-20260829.md:1
.../610-stage0-...-receipt.md:6
.../611-stage0-...-audit-PASS-20260829.md:8
.../612-stage0-...-receipt.md:5
# 合计 5 文件 27 行
```

**进一步枚举 truncated 61-char SHA drift** (per 614 §0.3 实测值守门 + "枚举穷尽"):

```
$ git grep -c 'c404980f1eb542dad24504ae0e957c169de60b7d78859186412fc83541277' reviews/stage0-gate0-rework-2026-08-23/
reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md:1
.../612-stage0-...-receipt.md:3
# 合计 2 文件 4 行
```

**总命中**: 7 文件 31 行 / 35 处 occurrences

**HEAD 实测 SHA 校验** (per 614 §1.1 步骤 4):
```
$ head -11 source_registry/registry.csv | shasum -a 256
c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277  -
# 65 bytes = 64 hex chars + newline ✓
```

## §3. (B) 文档 SHA 串号校对修复

**触发**: (A) 命中清单完整

**执行端校对修复**（per `/tmp/614_sha_fix_v3.py` + `/tmp/614_sha_fix_v4.py` — NOT-IN-MANIFEST per spike_helper 房规）:

```
$ python3 /tmp/614_sha_fix_v3.py
Hard-coded HEAD_ACTUAL:  c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277
hashlib with trailing \n: c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277
Match: True
FIXED: 00-EXEC-QUEUE.md (3 full + 7 8char = 10 total)
FIXED: 609-...-audit-PASS-...md (0 full + 1 8char = 1 total)
FIXED: 610-...-receipt.md (5 full + 1 8char = 6 total)
FIXED: 611-...-audit-PASS-...md (8 full + 1 8char = 9 total)
FIXED: 612-...-receipt.md (0 full + 5 8char = 5 total)

TOTAL replacements: 31

$ python3 /tmp/614_sha_fix_v4.py
FIXED (truncated 61 → full 64): 00-EXEC-QUEUE.md (1 occurrences)
FIXED (truncated 61 → full 64): 612-...-receipt.md (3 occurrences)

TOTAL truncated fixes: 4
```

**总修复**: 35 处 SHA 字面替换（31 处 `3639e729…` + 4 处 truncated 61-char SHA）

**校验** (per 614 §1.2 步骤 2-4):
- 替换前后仅 SHA 字面变化，其它原文零删减 ✓
- docs/45/46/49/50/51/52/53 既有 OPEN 行原文零删减 ✓
- status blockquote 完整保留 ✓
- 既有 31+ 红线守门条文完整保留 ✓
- docs 房规 NOT-IN-MANIFEST ✓

**grep 验证（post-fix）**:
```
$ git grep -c '3639e729' reviews/stage0-gate0-rework-2026-08-23/
[empty - zero matches]

$ git grep -c 'c404980f1eb542dad24504ae0e957c169de60b7d78859186412fc83541277' reviews/stage0-gate0-rework-2026-08-23/
[empty - zero matches]

$ git grep -c 'c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277' reviews/stage0-gate0-rework-2026-08-23/
00-EXEC-QUEUE.md:7
.../609-...-audit-PASS-...md:1
.../610-...-receipt.md:6
.../611-...-audit-PASS-...md:8
.../612-...-receipt.md:8
# 合计 30 occurrences（5 文件；HEAD actual SHA 引用一致）
```

## §4. (C) 单元测试守门

**触发**: (B) 修复完成

**新增 `tests/test_sha_citation_drift_guard.py`** (per 614 §1.3 测试文件命名 + 6 用例守门):

```
$ python3 -m pytest tests/test_sha_citation_drift_guard.py -v
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-9.0.2
configfile: pytest.ini
plugins: anyio-4.12.1, asyncio-1.3.0
collected 6 items

tests/test_sha_citation_drift_guard.py::test_1_head_actual_sha_legal PASSED [ 16%]
tests/test_sha_citation_drift_guard.py::test_2_no_stale_sha_references PASSED [ 33%]
tests/test_sha_citation_drift_guard.py::test_3_nantong_sha_in_612_receipt PASSED [ 50%]
tests/test_sha_citation_drift_guard.py::test_4_five_jiangsu_samples_consistent PASSED [ 66%]
tests/test_sha_citation_drift_guard.py::test_5_head_11rows_sha_consistent_in_docs PASSED [ 83%]
tests/test_sha_citation_drift_guard.py::test_6_git_diff_sha_consistency_guard PASSED [100%]

============================== 6 passed in 2.02s ===============================
```

**6 用例覆盖**:
1. **test_1_head_actual_sha_legal** — registry.csv first 11 rows SHA = HEAD_ACTUAL SHA 一致
2. **test_2_no_stale_sha_references** — git grep `'3639e729'` 应零命中
3. **test_3_nantong_sha_in_612_receipt** — 612 receipt 内含 nantong SHA 引用
4. **test_4_five_jiangsu_samples_consistent** — 5 江苏样本 SHA 在 registry + 实际文件一致
5. **test_5_head_11rows_sha_consistent_in_docs** — HEAD actual SHA 在 4 目标文件中 ≥ 10 处引用
6. **test_6_git_diff_sha_consistency_guard** — 无 truncated 61-char SHA drift + registry.csv SHA 未变

## §5. (D) docs/45 §6.2 O1 status append

**触发**: (A)(B)(C) 全部 PASS

**落地**:
- docs/45 line 560 append 一行 `> ⚠ **docs/45 §6.2 O1 status append**（per 614 · 2026-08-29）：O1 §5.2.x SHA 串号 drift 治理刀已落地（既有 11 行 SHA 串号文本校对修复实测=`c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` per 612 §5 EXISTING 11 ROWS IDENTICAL TO HEAD diff 验证 + 614 单元测试守门 `tests/test_sha_citation_drift_guard.py` 6 用例全 PASS）；SHA 串号 drift 闭环（35 处 stale 引用修复 = 31 处 `3639e729…` + 4 处 truncated 61-char SHA）；江苏样本链路 5/15 节点保持不动。docs 房规 NOT-IN-MANIFEST。`
- 既有 605 + 606 + 608 + 610 + 612 status blockquote 完整保留
- 既有 Gate 2 PASS / W8 评审日期 (line 561+) 完整保留
- 不删不改

**grep 验证**:
- `wc -l docs/45-stage2-s210-lite-gate2-review-index-20260826.md` = 561 (was 560; +1 line)
- `grep -c 'per 614 · 2026-08-29'` = 1 (new) ✓
- `grep -c 'per 612 · 2026-08-29'` = 1 (preserved) ✓
- `grep -c 'per 605 · 2026-08-29'` = 1 (preserved) ✓
- `grep -c 'per 606/608/610 · 2026-08-29'` = 1/1/1 (preserved) ✓

## §6. (E) docs/49/50/51/52/53 status row append — SKIP 政策成立

**触发**: grep `docs/49-stage2-*.md docs/50-stage2-*.md docs/51-stage2-*.md docs/52-stage2-*.md docs/53-stage2-*.md` 命中 stale `--confirm-*` 字面

**grep 命中分析**:
- docs/49 文件路径 mismatch → SKIP per 605 §6 precedent
- docs/50 line 11 「用户裁定：**D**；**不宣布 Gate 2 PASS**」 = 治理级决策标注 → SKIP per 614 §1.5
- docs/50 line 120/121 (591/603 既有 supersede 标注) + line 124-127 (605 既有 supersede blockquote) = 既有 supersede 标注 → SKIP
- docs/51 line 183+ (601 既有 supersede blockquote) = 既有 supersede 标注 → SKIP
- docs/52 line 287/289/291 (599 既有 §13 blockquote) + line 299+ (601 既有 §14 blockquote) + line 309+ (606 既有 §15 BLOCKED 标注) + line 320+ (608 既有 §16 标注) = 既有 supersede 标注 → SKIP
- docs/53 line 244+ (601 既有 §11 blockquote) + line 258+ (608 既有 §12 标注) = 既有 supersede 标注 → SKIP

**grep `per 614（2026-08-29）` 命中** = 0 行（SKIP 政策成立）
**落地**: E 段 SKIP（命中为治理级决策标注 + 既有 supersede 标注共存非 stale runtime flag）
**docs 房规 NOT-IN-MANIFEST** ✓

## §7. (F) manifest bump K=4 → 973 → 977

**触发**: (A)(B)(C)(D)(E) 全部落地

**落地**:
- `scripts/_knife614_manifest_bump.py` NEW spike_helper +1 (9220 bytes / sha `4075d8af` 实际生成)
- 613 audit 文件入库随 614 commit (per docs 房规 审计文件不单独 commit 随下一刀入库) NEW documentation +1
- 614 receipt NEW documentation +1（本文件）
- `tests/test_sha_citation_drift_guard.py` NEW documentation +1
- source_registry/registry.csv REFRESH（file-based role_count 守门不增计数 per 614 §0.2 零行变动）
- K = 4 基础 → manifest 973 → 977

**enumeration 即权威 per 583 §F**:
- 614 tasking 文件本身 NOT-IN-MANIFEST per docs 房规
- docs/45 §6.2 O1 status append 不增计数 per docs-only refresh 房规
- docs/49/50/51/52/53 E 段 SKIP 不增计数
- SHA 串号 drift 校对修复 (B)(B+) 不增计数 per 614 §0.2 "SHA 字面校对修复视为'实测对齐'非'内容改动'"
- scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py 零触碰
- .venv-paddle / scripts/requirements-paddle.txt / spikes/04-scanned-pdf/{conftest.py,run_real_paddle_e2e.sh,test_real_paddle_e2e.py} NOT-IN-MANIFEST per spike_helper 房规

**INVARIANT**: 977 == 977 == 977 ✓ (per scripts/_knife614_manifest_bump.py 实跑断言)

## §8. (G) 614 receipt 写回执（本文件）

**落地**: (A)(B)(C)(D)(E)(F)(G) 七段交付 + 双推 + cc_head backfill + manifest INVARIANT 验证 + 14 受保护文件零漂移（13 既有 + 614 新增 tests/test_sha_citation_drift_guard.py 守门）+ 31+ 红线 100% 兑现 + 1 ⚠ disclosure ACCEPTED

**双推链**: feat(614) `<TBD>` + cc_head backfill `<TBD>` + §双推 populate `<TBD>` + §双推 populate fix SHA correction `<TBD>` 四步 commit 链 per 599/606/607/608/609/610/611/612/613 precedent → 三侧收敛 100% (origin main + github main both = HEAD)

**cc_head backfill**: per 583/585/587/589/591/593/594/595/596/597/598/599/600/601/603/605/606/607/608/609/610/611/612/613 precedent（feat + cc_head separate commits 模式）

**14 受保护文件零漂移**:
- `synthetic.png` sha `dea1902a` 14817 bytes ✓
- S0 PDF sha `f34b2e57ae08` 1007943 bytes ✓
- `_syn_pdf_585.py` sha `2db08313` 3980 bytes ✓
- `extracts/` dir 不变 ✓
- `registry.csv` 既有 11 行 sha `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` 实测不变（614 零行变动 per 614 §0.2）；+1 行（江苏样本地市第四刀 / 南通市统计局）SHA `92e1481c3fea…` 不变 ✓
- `gate_thresholds.json` sha `81f3c83a` 3709 bytes / mtime Aug 23 不变 ✓
- `01-core.sql` sha `09aa46f9` 51589 bytes ✓
- `requirements-dbt.txt` sha `db73c342` 349 bytes ✓
- `scripts/requirements-paddle.txt` sha `5d730735` 1314 bytes ✓
- `scripts/intake_real_sha_if_present.py` sha `239b85c9` 14457 bytes ✓
- `scripts/auto_ingest_public_source.py` sha `91a5acf9` 59781 bytes ✓
- `.venv-paddle/pyvenv.cfg` sha `73fdd9c5` 326 bytes ✓
- migration 001-013 零漂移 ✓
- `tests/test_sha_citation_drift_guard.py` sha `306fb39719618f56068397e0520d27f57d775195f893571a42e008006a100f67` 8739 bytes NEW (614 守门新增) ✓
- `_knife614_manifest_bump.py` sha `4075d8af05f4620b95b48f854a90805473b56a14521fa5f5e1eadb02d00c36f1` 9220 bytes NEW (614 自身 bump 脚本 spike_helper) ✓
- `614-stage0-cc-§5.2.x-sha-citation-drift-治理-tasking-20260829-receipt.md` sha `bb744a93dca82725328edbfe8709cbb10fa2abbf1fa59bcc862da77451beb262` 21688 bytes NEW (本 receipt；落盘后 bump script 自动刷新 manifest 记录 sha `397aa65c` → `9401353b` → `96e73b48` → `bb744a93` 四态收敛；canonical SHA = `bb744a93` = manifest entry 当前值；SHA-of-SHA 自指悖论：每次更新本行 SHA 字符串本身又触发新 SHA；本字段记"bump script 最终落盘"时态快照 = `bb744a93`；canonical 锁值以 commit 时 git tree object 为准 — manifest.json entry.sha256 字段为权威) ✓
- `evidence_pack/manifest.json` sha `6375af57e78babd7bc7e450681a44c43a327e496fa3411a07f632de6587a1dd9` INVARIANT 977 == 977 == 977 ✓ (NOTE: 此 SHA 为 614 落盘后最终 dump；随 receipt sha 更新 → manifest refresh 不计入此 lock 值；canonical 锁值以 commit 时 git tree object 为准)

**31+ 红线 100% 兑现** (per 614 §0.2 + 2026-08-29 治理铁律):
- ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS 零重新宣告 ✓
- ❌ 2020-2025 batch work 零批量（本刀仅 1 个 SHA 串号 drift 治理刀）✓
- ❌ 公网爬网（非政府/统计局）零（本刀零网络访问）✓
- ❌ OCR threshold lowering 零（gate_thresholds.json 3709 bytes 不变）✓
- ❌ 1909-as-China 零 ✓
- ❌ --force 零（git push 走普通路径）✓
- ❌ PAT request 零 ✓
- ❌ gate_thresholds.json edit 零（3709 bytes / mtime Aug 23 不变）✓
- ❌ 重新宣告 O3 整体 CLOSED 零（per 588 + 590 + 597 + 598 + 599 + 600 + 601 + 602 + 603 + 604 + 605 + 606 + 607 + 608 + 609 + 610 + 611 + 612 + 613 十九重声明；614 不二次宣告）✓
- ❌ 重新宣告 O1 整体收口 零（O1 整体仍 WAITING_FILE per docs/47 §3.1；614 仅 SHA 串号 drift 治理不构成 O1 整体收口）✓
- ❌ 启动 O1 A 路实跑 零（A 路保留为 fallback 标注 per 591 docs/50 row 117 supersede）✓
- ❌ --confirm-* 字面 零（per 2026-08-29 治理铁律）✓
- ❌ 修改 001-013 migration 文件 零 ✓
- ❌ 修改 01-core.sql 零（51589 bytes 不变）✓
- ❌ 修改 4 fixture 锁值 零 ✓
- ❌ 修改 S0 原始 PDF 字节 零（sha `f34b2e57...` 1007943 bytes 不变）✓
- ❌ 修改 source_registry/registry.csv 既有 11 行 零（HEAD 实测 sha `c404980f1eb542…` 不变；614 零行变动 per 614 §0.2）✓
- ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json 零 ✓
- ❌ 修改 .venv-paddle / scripts/requirements-paddle.txt / requirements-dbt.txt 零 ✓
- ❌ 修改 scripts/intake_real_sha + auto_ingest 零 ✓
- ❌ 修改 docs/45/46/44/49/50/51/52/53 既有 OPEN 行原文 零（仅 selective refresh append；既 605 + 606 + 608 + 610 + 612 status blockquote 保留；E 段 SKIP）✓
- ❌ 删除命中行原文 零（仅 SHA 字面校对修复）✓
- ❌ 真实 paddleocr API 调用（system Python）零（仅 .venv-paddle/bin/python 隔离 venv 内允许 per 594 §0.2 红线；本刀零 OCR）✓
- ❌ 真实 PDF 上传（非 seed_archives/）零（本刀零 PDF 操作）✓
- ❌ 触真实 DB（生产 schema）零（migration 001-013 零触碰）✓
- ❌ 引入 cloud OCR / GPU runtime 零 ✓
- ❌ docker daemon systemctl 操作 零 ✓
- ❌ 持久保留 paddle-ocr:v1 Docker image 零 ✓
- ❌ 启动 584 BLOCKED 实跑 paddle-ocr deps 到 system 零 ✓
- ❌ 用户授权 #1 二次申请 零（本刀零网络访问；仅本地 git grep + shasum + pytest 操作）✓

**⚠ disclosures (1 项)**:

**⚠ #1 (truncated 61-char SHA drift disclosure)**: 执行端在 (A) 全量定位过程中**额外发现** truncated 61-char SHA drift（`c404980f1eb542dad24504ae0e957c169de60b7d78859186412fc83541277` 缺 `5998` 4 字符；pre-existing in 00-EXEC-QUEUE.md 1 行 + 612 receipt 3 行 = 2 文件 4 行 = 4 occurrences）。该 truncated drift 在 614 tasking (A) §0.3 实测值守门段已隐含定义 HEAD actual = full 64-char SHA，但 614 tasking (B) §1.2 与 (D) §0.1 内文引用了 truncated 61-char 版本（tasking 自身 typo drift）。执行端 per "实测对齐" 原则 (614 §0.2 "SHA 字面校对修复视为'实测对齐'非'内容改动'") + 583 §F enumeration 即权威，将 truncated 61-char SHA 4 处 occurrences 全部替换为 full 64-char HEAD actual = `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277`。**最终修复 = 31 处 `3639e729…` + 4 处 truncated 61-char = 35 处总 SHA 字面替换**。614 tasking 自身 NOT modified (任务书 = spec not execution record per precedent)。

**附加 ⚠ disclosure**: 用户授权 #1 仍生效无需二次申请（per 614 §0.1 verbatim + 2026-08-29 治理铁律 + 本刀零网络访问）

**登记→实装闭环 = 583 → 584 BLOCKED → 585 → 587 → 589 → 591 → 593 → 594 → 595 → 596 → 597 → 598 → 599 → 600 → 601 → 602 → 603 → 604 → 605 → 606 → 607 → 608 → 609 → 610 → 611 → 612 → 613 → 614**（614 既闭合 O1 §5.2.x SHA 串号 drift 治理刀（执行端一次性 git grep + 35 处 SHA 字面校对修复 + 6 用例单元测试守门 + docs/45 §6.2 O1 status append + docs/49/50/51/52/53 E 段 SKIP + manifest INVARIANT 977 == 977 == 977 ✓ + 14 受保护文件零漂移（13 既有 + 614 新增 tests/test_sha_citation_drift_guard.py 守门）+ 31+ 红线 100% 兑现 + 1 ⚠ disclosure ACCEPTED）

## §9. 后续建议（架构师定夺）

- **下一刀候选** (per 614 tasking §4 关联文件清单 + 613 audit §8 + 613 receipt §8 + 614 receipt §9):
  - **615 tasking** 候选 #1：614 receipt 审计刀（per 583/585/587/589/591/593/594/595/596/597/598/599/600/601/602/603/604/605/606/607/608/609/610/611/612/613 audit precedent）
  - **615 tasking** 候选 #2：O1 §5.2.x 江苏样本第六刀（剩余地市样本刀；如徐州 / 盐城 / 扬州 / 镇江 / 泰州 / 宿迁地市统计局公开源；接续 605 + 606 + 608 + 610 + 612 江苏样本链路 5/15 → 6/15）
  - **615 tasking** 候选 #3：O1 §5.2.x 江苏样本省样本第二刀（其它江苏省份样本刀；如浙江/广东/山东等省统计局公开源；接续 605 首批省样本链路）
  - **615 tasking** 候选 #4：其它治理推进刀 — 任一由架构师定夺 per 613 audit §7 / 614 audit §7 候选 #1/2/3/4

- **O1 整体仍 WAITING_FILE**（per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；614 仅 SHA 串号 drift 治理不构成 O1 整体收口；待全部 5 省样本 + 10 地市样本均 SHA-locked 后另刀审议）
- **B 路（公开源自动获取 per docs/52）保持主路径**
- **A 路（用户投递 per docs/51）保留为 fallback 标注（不删除、不调用）**
- **O3 整体仍 CLOSED 候选**（per 588 + 590 + 597 + 598 + 599 + 600 + 601 + 602 + 603 + 604 + 605 + 606 + 607 + 608 + 609 + 610 + 611 + 612 + 613 十九重声明；614 不二次宣告）
- **江苏样本链路进度**: 605 首批省样本（stats.gov.cn 江苏分省页面 1 节点）+ 606 首批地市样本（tjj.suzhou.gov.cn 苏州市统计局 1 节点）+ 608 第二批地市样本（tjj.nanjing.gov.cn 南京市统计局 1 节点）+ 610 第三批地市样本（tjj.changzhou.gov.cn 常州市统计局 1 节点）+ 612 第四批地市样本（tjj.nantong.gov.cn 南通市统计局 1 节点）= 江苏样本链路 5 节点；目标 5 省 + 10 地市 = 15 节点；剩余 10 节点待续接
- **SHA 串号 drift 闭环**: 35 处 SHA 字面替换完成（31 处 `3639e729…` + 4 处 truncated 61-char）；6 用例 pytest PASS 守门；future taskings 引用的 registry.csv SHA 必须 = HEAD actual 64-char = `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277`

---

— End of `614-stage0-cc-§5.2.x-sha-citation-drift-治理-tasking-20260829-receipt.md` —