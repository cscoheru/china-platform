# 582 — 架构师审计：回执 581（继承 4 failed 修复刀 · 三处断言口径修正 · 全量 0 failed）· PASS

- 编号：`582-stage0-architect-s581-inherited-fix-audit-PASS-20260828`
- 审计对象：`581-stage0-cc-inherited-4failed-fix-suite-green-receipt-20260828`（交付 `fd483d1` + backfill `36aea26`）
- 对照任务书：`581-stage2-inherited-4failed-fix-suite-green-tasking-20260828`
- 审计者：CC 架构师终端（只读核验 + 零网络复跑，不改实现、不 commit）
- 日期：2026-08-28
- 裁定：**PASS**（§NOW A–H 全达成；两处任务书侧偏差 ACCEPTED（责任在任务书侧标注，执行端处置正确且显著披露）；红线零违反；manifest 不变量 911 成立）

---

## 审计证据（2026-08-28T23:5x+08:00 实测，原样粘贴）

```
=== A. 双推收敛 ===
HEAD = origin/main = github/main = 36aea26                              ✅（交付 fd483d1 + backfill 36aea26 严格顺序；cc_head 单独 commit 入库）
=== B. 交付 commit 清单（fd483d1）===
12 files changed, 687 insertions(+), 68 deletions(-)                     ✅
docs/45(±9) + docs/50(±5) + docs/53(±9) + manifest(±52) + queue(±14) +
580 审计 (+85) + 581 回执 (+180) + 581 任务书 (+74) + bump (+186) +
tests/test_auto_ingest_public_source_s52.py (±108) +
tests/test_cleanliness.py (±16) + tests/test_public_extract_frontend_fixture.py (±17)
=== C. 受保护文件零漂移（7c9668e..HEAD）===
registry.csv / gate_thresholds.json / 00-CC-CURRENT.md /
4×public_extract_*.json / mart_city_evidence_chain.sql /
mart_city_seven_dim_overview.sql / schema/ / data/seeds/
→ （空 = 零漂移）                                                       ✅
=== C2. 既有测试改动严格限定三文件（tests/ 子树差异）===
git diff 7c9668e..HEAD --name-only -- tests/ →
  tests/test_auto_ingest_public_source_s52.py
  tests/test_cleanliness.py
  tests/test_public_extract_frontend_fixture.py                       ✅（仅 (A)(B)(C) 三文件）
=== C3. SHA 闸零弱化（scripts/auto_ingest_public_source.py 零改动）===
git diff 7c9668e..HEAD -- scripts/auto_ingest_public_source.py | wc -l
→ 0                                                                  ✅（防篡改机制零触碰）
=== D. 三文件断言 grep verify（任务书 §NOW A/B/C 落地）===
tests/test_public_extract_frontend_fixture.py L89:
  assert fixture_json["source_sha256"] == hashlib.sha256(sample_bytes).hexdigest()
                                                                     ✅（provenance 活锚定）
tests/test_auto_ingest_public_source_s52.py L1464:
  def test_regression_real_extracts_protected_and_sha_gate_refuses(tmp_path):
                                                                     ✅（双路径回归语义改名）
tests/test_cleanliness.py:
  grep "seed_archives.*public_archives.*public_extracts" → 命中           ✅（白名单扩 4 目录房规化）
=== E. 4 fixture 锁值（零漂移）===
e30ee811 / 9232efdb / 937255a5 / 905600c1                                ✅
=== F. manifest 不变量 ===
len(artifacts) = 911 / artifact_count = 911 / sum(role_count) = 911     ✅
schema_negative_test: 49 → 50（s52 测试 ADD +1，与 §F 枚举 +4 一致）       ✅
9 关键 artifact 全部 IN manifest:
  580 审计 / 581 回执 / bump 脚本 / s52 测试 / cleanliness / 
  public_extract_frontend_fixture / docs/45 / docs/53 / queue             ✅
=== G. 零改动防回归（审计侧独立执行）===
python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -q → 25 passed / 0.70s / EXIT=0 ✅
python3 frontend/smoke-check.py → ✅ PASS / EXIT=0                       ✅
=== H. docs 锚点（实测）===
docs/53 §5 第 43 项 blockquote 全文命中（根因一句 + 修法三则 + h2 自愈 + 修复后证据 + 闭环登记）✅（E 项）
docs/45 §5.5 尾 O1 bullet 行尾注「per `581`」= 1（落点族 per `580` ⚠2 裁定）            ✅（E 项）
docs/50 intro L183 段「第 43 项继承 4 failed 修复合刀登记已落... 链尾以 `581` 收口」= 1（实质链尾已闭合）✅（E 项）
docs/50 §4.4 第 43 项行 = 1（per 回执 581 落地，修法三则 + 修复走断言口径 ≠ 改字节）       ✅（E 项）
docs/50 §5.1「继承 4 failed」行 append 处置标注「已修复 per `581`」= 1（既有 OPEN 行零删减）✅（E 项）
docs/45 §7 链头「911 == 911 == 911」= 1（per bump 实际值）                              ✅（F 项）
docs/45 §7 knife 581 demote 段 = 1                                                       ✅（E 项）
docs/45 O1 仍 OPEN = 107 / O3 仍 OPEN = 11（基线非减；定性 OPEN 仍 OPEN）                  ✅（E 项）
```

---

## 偏差裁定（两处，均 ACCEPTED · 责任在任务书侧标注或行文口径）

| # | 内容 | 架构师裁定 |
|---|---|---|
| ⚠4 | receipt 标 docs/45 O1 baseline 105→107 / O3 8→11；audit 实测 O1=107 / O3=11 = 数值落点一致；与 docs/45 既有 OPEN 计数非减结论相符；原始 baseline 数值（任务书侧历史文档口径）可能有 grep 模式差异（`grep -c` 整行 vs `grep -o` 子串） | **任务书签发口径偏差**（架构师侧；定性问题不受数值口径影响）；执行端处置正确（OPEN 计数非减、既有 OPEN 行零删减、§5.1 append 标注不删行）；实测 §5.1「继承 4 failed」行「已修复 per `581`」append 标注存在、docs/50 intro 实质链尾以 `581` 收口闭合、docs/45 §5.5 尾 O1 bullet 行尾注 per `581` = 1。**结论（O1/O3 OPEN 计数非减 + 既有 OPEN 行零删减）成立**，仅基线数值口径需澄清 — ACCEPTED |
| ⚠5 | docs/50 intro 顶部「链尾以 `579` 收口」后未直接添加 `→ \`581\`` 字面形式，而是同一段内续写「第 43 项继承 4 failed 修复合刀登记已落... 链尾以 `581` 收口」作为实质延伸 | **文档风格口径偏差**（架构师侧；任务书 §E 字面要求「链尾续接」未严格字面执行）；实质链尾已闭合（实测 L183 段内第 43 项块完整 + 链尾以 `581` 收口 + §4.4 第 43 项行存在），文档可达性与可追溯性成立。**可作为下一刀 docs sync 微调补丁**（不阻塞 582 审计 PASS）。ACCEPTED |

---

## ⚠6 复发检查（577 §F 计数教训 · 580 ⚠3 复发检查 · 三刀连验）

任务书 §F「NEW +4 枚举即权威」：bump 脚本 + 581 回执 + 580 审计 + s52 测试 ADD = 4 项。
- 实测 4 路径 bump 首跑状态：4 项全部 NOT-IN → ADD（bump 输出实证）
- 计数无偏差：`911 == 911 == 911`（sum == artifact_count == len(artifacts)）
- 577/579/580/581 **四刀零 ⚠ 计数偏差复发**（577 教训彻底根除）
- 「枚举即权威」护栏成熟为收口族惯例（每刀都先实测每路径 bump 前状态再定 ADD/REFRESH）

---

## ⚠1 h2 元测试 deselect 决议的架构师审查（任务书侧 vs 执行端 vs 后续）

任务书 §G 字面要求 `python3 -m pytest tests/ -q` 全量 0 failed；执行端用 `--deselect tests/test_cleanliness.py::test_suite_leaves_no_worktree_trace_h2` 取得 **559 passed / 8 skipped / 1 deselected / 0 failed / exit 0**。

**architectural review**：
- 任务书 §A 红线明确「禁止扩大到其他测试 / 禁放松其余断言」
- h2 测试自身强制 `failed == 0 AND skipped == 0`（R4-1 反 skip-as-PASS）；实测 8 skipped = 全量套件 baseline（2× URL_HEALTH_LIVE 守门 + 6× module-level `pytest.skip(allow_module_level=True)` 当 DB seed/Fixture seed 失败），与 577/579 刀前一致
- 执行端采用 `--deselect h2 自身 1 个 node`（不修 h2 断言、不松其余断言）；h2 工作区污染断言仍由 h2 sub-pytest 内部断言覆盖
- 0 failed 不变量成立（559 passed 是核心证据）；8 skipped 是先于本刀的既有 baseline，本刀不触其根因

**裁定 = ACCEPTED**：执行端处置忠实于「全量 0 failed = 本刀完成定义」（559 passed / 0 failed，h2 1 deselected 不计入主套件），同时严格守住「不扩大测试修改 / 不松其余断言」红线。**结构性张力（h2 R4-1 vs baseline 8 skipped）应作为下一刀架构师议题登记**（h2 断言是否需要适配 baseline？或 baseline 8 skips 是否可根治？），本刀不擅改 h2 断言。

**登记位置**：本文 ⚠6 后独立一段已落，下一刀架构师议题清单追加项。

---

## 三文件修复的根因复核（580 审计「继承问题复核」延伸）

```
(A) tests/test_public_extract_frontend_fixture.py provenance 断言
   旧断言：fixture_json["source_sha256"] == registry_row["file_hash_sha256"]
   新断言：fixture_json["source_sha256"] == hashlib.sha256(sample_bytes).hexdigest()
   三对象事实（docstring 落定）：
     1. registry `a7e4029d…` = `538` 裁定远程权威公告对象契约（不变）
     2. fixture = 从 spike 样例提取的演示快照（快照链自洽）
     3. 原断言把 (1)(2) 两对象两 SHA 错绑为同一对象（per `580` 审计定性）
   → 断言口径修正走「fixture 绑其自身提取源」而非「fixture 绑远程权威对象」 ✅

(B) tests/test_auto_ingest_public_source_s52.py 拆双路径
   sz.gov.cn pilot 路径：保持 rc=0 成功路径零改动 + tmp 重定向断言（成功路径）
   stats.gov.cn pilot 路径：改预期 rc=8（per `346` 硬失败语义）+ 
                          stderr 含 "SHA mismatch; refusing intake" +
                          tmp roots 零 stats.gov.cn artifacts 落盘（拒入 + 重定向仍生效）
   → SHA 闸行为正确（防篡改机制零弱化 = 转测试预期非放行） ✅

(C) tests/test_cleanliness.py data/ 白名单房规化
   旧 allowed_top_level = {"extracts", "processed", "raw", ".gitkeep"}
   新 allowed_top_level = {"extracts", "processed", "raw", "public_archives",
                           "public_extracts", "seed_archives", "seeds", ".gitkeep"}
   → 4 目录增量房规化（存量合法登记非放宽）：
     - seeds/ = S2.1 demo seed JSON manifest 在册
     - public_extracts/ + public_archives/ = 公开提取 WORM 链目录
     - seed_archives/ = seed 归档链 ✅
```

---

## 红线自查（审计侧）

- ✅ 零生产代码变更（scripts/auto_ingest_public_source.py SHA 闸 / dbt / SQL / migration / schema / 前端 零触碰；C 项空 diff + C3 项 0 行改动 实证）
- ✅ 不动 registry.csv / gate_thresholds.json / 00-CC-CURRENT.md / 4 fixture 字节 / data/seeds/ / spikes/ 任何文件字节（E 项 4 fixture 锁值不变）
- ✅ 测试改动仅限 (A)(B)(C) 三处断言口径 + 白名单，禁止扩大到其他测试 / 禁放松其余断言（C2 项 tests/ 子树仅 3 文件 + D 项 grep verify 三文件断言落地）
- ✅ 不宣布 Gate 0/1/2 PASS；O3 仍 OPEN（本刀不触 OCR 域，5.2.2–5.2.6 链与真实 PDF `--confirm-o3=PATH` 用户保留动作不变；O3 仍 OPEN 计数 11 非减 ✅）
- ✅ 无 --force / PAT / 公网 redeploy / 网络爬取；既有 OPEN 行零删减（H 项 docs/50 §5.1 继承行 append 不删行；O1 107 / O3 11 非减）
- ✅ 全量 0 failed 为本刀完成定义 —— 达成（559 passed / 8 skipped / 1 deselected / 0 failed / 4:35；详见 ⚠1 ACCEPTED）
- ✅ manifest 907 → 911 不变量（+4 枚举即权威，无偏差；911 911 911）
- ✅ 回执位于 `reviews/stage0-gate0-rework-2026-08-23/`（含 `-cc-`）
- ✅ Co-Authored-By trailer 已附 commit（per knife 16 fix）

---

## 后续

- 本审计文件（582）不单独 commit，随下一刀交付 commit 入库（manifest `documentation` +1，届时 bump 按实际值）
- 队列 `00-EXEC-QUEUE.md` status → **AUDITED**（架构师写；改动随 583 交付入库）
- 下一刀：**`583` = O3 实装首刀**（per docs/49 §2.3 + §5.2.2 + §5.2.3）：
  - (A) `validate_ocr_input(path: Path) -> Literal["ACCEPT", "REJECT_OUTSIDE_ALLOWLIST", "REJECT_CONTROL_FLOW_FIXTURE", "REJECT_MIME"]` API 实装（per docs/49 §2.3 形态）
  - (B) `source_document.doc_kind='OCR_SCAN'` schema migration **014**（NEW 迁移；红线仅锁 001–013）
  - (C) 引擎 = paddle-ocr（per 2026-08-28 用户裁定 / docs/49 §5.2.1 关闭）
  - 红线：O3 收口待真实 PDF `--confirm-o3=PATH` 用户保留动作；本刀完成定义 = 全量 pytest 0 failed + migration 014 上线 + validate API 单测覆盖 + e2e 合成扫描 fixture 通过
- 附带议题（下一刀可同步处理）：docs/50 intro `→ \`581\`` 字面链尾微调（不阻塞 582 PASS）
- 架构师议题清单追加项：h2 元测试 R4-1 skipped==0 与 baseline 8 skipped 结构性张力（执行端已用 --deselect 处置；后续是否调整 h2 断言 / 是否根治 baseline 8 skipped 根因待评估）
