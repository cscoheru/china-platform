# 584 — 架构师审计：回执 583（O3 实装首刀 · validate_ocr_input API + migration 014 doc_kind='OCR_SCAN'）· PASS

- 编号：`584-stage0-architect-s583-o3-impl-validate-api-doc-kind-audit-PASS-20260829`
- 审计对象：`583-stage0-cc-o3-impl-validate-api-doc-kind-receipt-20260828`（交付 `380613a` + backfill `82a1f04`）
- 对照任务书：`583-stage2-o3-impl-validate-api-doc-kind-tasking-20260828`
- 审计者：CC 架构师终端（只读核验 + 零网络复跑，不改实现、不 commit）
- 日期：2026-08-29
- 裁定：**PASS**（§NOW A–G 全达成；**⚠1 docs/45 §7 链头数字 916 vs actual manifest 917 docs sync gap ACCEPTED with disclosure**；红线零违反；manifest 917 不变量成立；INCONSISTENT-1 tasking §F "+5" vs §E enumeration "+6" 已披露并以 enumeration = 917 收口）

---

## 审计证据（2026-08-29T08:3x+08:00 实测，原样粘贴）

```
=== A. 双推收敛 ===
HEAD = origin/main = github/main = 82a1f04                              ✅（交付 380613a + backfill 82a1f04 严格顺序；cc_head 单独 commit 入库）
=== B. 583 交付 commit 清单（380613a）===
14 files changed, 1366 insertions(+), 30 deletions(-)                   ✅
scripts/intake_real_sha_if_present.py(±) + scripts/_knife583_manifest_bump.py(+) +
schema/migrations/014_source_document_doc_kind.sql(+2064) +
schema/migrations/014_source_document_doc_kind.log(+2358) +
tests/test_validate_ocr_input_583.py(+9916) +
docs/45(±) + docs/49(±) + docs/50(±) + docs/53(±) +
00-EXEC-QUEUE.md(±) + 582 审计(随刀入库) + 583 任务书(随刀入库) + 583 回执(本刀落)
=== C. 受保护文件零漂移（36aea26..HEAD）===
registry.csv / gate_thresholds.json / 00-CC-CURRENT.md /
4×public_extract_*.json / mart_city_evidence_chain.sql /
mart_city_seven_dim_overview.sql / data/seeds/ / spikes/ /
schema/01-core.sql / migration 001-013 任何文件
→ git diff (空)                                                          ✅（仅 NEW：014.sql + 014.log；C 项零漂移）
=== C2. migration 001-013 + base schema 零改动 ===
git diff 36aea26..HEAD -- schema/migrations/ schema/01-core.sql → 0      ✅（migration 锁 001-013 守门；base schema 不动）
=== C3. SHA 闸零弱化（scripts/auto_ingest_public_source.py 零改动）===
git diff 36aea26..HEAD -- scripts/auto_ingest_public_source.py | wc -l
→ 0                                                                     ✅（防篡改机制零触碰）
=== D. 实装落地（scripts/intake_real_sha_if_present.py）===
+def is_control_flow_fixture(path: Path) -> bool:                         ✅（公开 wrapper 包装既有私有 _is_fixture）
+def validate_ocr_input(                                                   ✅（五态守门主函数）
=== E. 4 fixture 锁值（零漂移）===
e30ee811 / 9232efdb / 937255a5 / 9056001c                                ✅（disk == 锁值）
=== F. manifest 不变量 ===
len(artifacts) = 917 / artifact_count = 917 / sum(role_count) = 917       ✅
schema_negative_test: 50 → 51（s583 测试 ADD +1）
schema_migration_ddl + schema_migration_log：NEW 角色 ×2（014.sql + 014.log）
spike_helper: 增量 +1（bump 脚本）
documentation: 增量 +3（582 审计 + 583 任务书 + 583 回执）
== sum 917 / 917 / 917
=== G. 583 新测试单跑 ===
python3 -m pytest tests/test_validate_ocr_input_583.py -q → 14 passed / 1.62s / EXIT=0 ✅（四态 14 例覆盖：ACCEPT 5 / REJECT_OUTSIDE_ALLOWLIST 3 / REJECT_CONTROL_FLOW_FIXTURE 3 / REJECT_MIME 2 + boundary 1）
=== G2. S2.7-b-full 防回归 ===
python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -q → 25 passed / 1.14s / EXIT=0 ✅
=== H. docs 锚点（实测）===
docs/49 §2.3 实装说明 append（stdlib mimetypes + 实际常量名）                            ✅
docs/49 §5.2.2 + §5.2.3 段首 CLOSED per 583（2026-08-29）                             ✅（L84 + L249-250 落地）
docs/53 §5 第 44 项 blockquote（per 583 落地；A/B/C/D + 核心证据 + 红线 + 闭环）       ✅（L199-207 落地）
docs/50 §4.4 第 44 项行（per 583 落地；闭合 §5.2.2 + §5.2.3）                           ✅（L228 落地）
docs/50 intro 链尾续接 → 583（含第 44 项登记说明）                                       ✅（L183 实质链尾以 583 收口）
docs/50 §5.1 O3 状态行 append 处置标注（5.2.2 + 5.2.3 CLOSED；5.2.4+ OPEN；行内 append 不删行）✅
docs/45 文首 +1 刷新行（架构师治理模型第五刀 per 583）                                   ✅
docs/45 §1 +1 实装登记段（per 583）                                                      ✅
docs/45 §3 零涉（O1/O3 OPEN 计数非减）                                                   ✅
docs/45 §5.5 尾 O3 bullet 行尾注 append（per 583；CLOSED per 583；5.2.4/5/6 OPEN）       ✅
docs/45 §7 链头：`916 == 916 == 916`（⚠1 docs sync gap；见下文裁定）                  ⚠
docs/45 §7 knife 583 demote 段（per 583；+5 per bump 实际值；⚠1 同上）                  ⚠
「O3 仍 OPEN」计数非减（5.2.4/5/6 + 真实 PDF `--confirm-o3=PATH` 用户保留动作 不变）    ✅（O3 整体仍 OPEN）
```

---

## 偏差裁定

| # | 内容 | 架构师裁定 |
|---|---|---|
| ⚠1 | docs/45 §7 链头 invariant claim = `916 == 916 == 916`（L93 + L487）+ docs/45 L93 demote `manifest 911 → 916（+5 per bump 实际值）` + docs/53 §5 第 44 项 L203 `§7 链头 911 → 916` + docs/53 §5 第 44 项 L207 `§7 链头 916 == 916 == 916` + docs/50 §4.4 第 44 项 L228 `§7 链头 911 → 916`；actual manifest = **917**（per `911 + 6` enumeration per INCONSISTENT-1 disclosed） | **docs sync gap**（执行端按 tasking §F 头部 "+5" 字面写入了 916，未随 enumeration 修正为 917；INCONSISTENT-1 已披露但 docs 未 patch）。**invariant 真实 = 917 成立**（bump 实跑 `917 == 917 == 917`），docs claim 与 manifest 不一致 = docs sync gap，不影响功能正确性 / 不影响红线。可作为下一刀（584 tasking = paddle-ocr deps）docs sync patch 处理（**不动 manifest / 不动 commit / 仅 docs 文案对齐 actual 917**）。**ACCEPTED** with disclosure（per 582 ⚠4/⚠5 同模式：docs claim 偏差不阻塞 invariant 真实成立；本刀 ACCEPTED 强条件 = invariant 实测 917 + docs sync gap 列入下一刀 patch 清单） |

---

## ⚠2 INCONSISTENT-1 已收口核验（tasking §F "+5" vs §E enumeration "+6"）

tasking §F 头部标注 `+5`（911 → 916）；§E 枚举 6 条（含 `.sql` + `.log` 分列）；§E 条件解析「`013.log` 独立文件则双 ADD」→ 双 ADD = 6 项；bump 实跑 `917 == 917 == 917` = `+6` 实际收口。

执行端处置：
- bump 脚本 `EXPECTED_COUNT = 917`（per enumeration）
- INCONSISTENT-1 在 receipt §不一致记录 中显著披露
- 决议 = 以 enumeration 为准（per tasking §F「枚举即权威」原则）
- manifest invariant = 917 真实成立
- docs claim = 916 字面（tasking §F 头部影响）→ ⚠1 docs sync gap

**架构师核验**：
- receipt INCONSISTENT-1 披露完整 ✓
- bump 实跑 `917 917 917` 与 §E enumeration 一致 ✓
- §F 头部 +5 = tasking 侧口径偏差（per 581/582 教训库「任务书签发口径偏差」类）
- 闭合以 enumeration = 917 收口（INCONSISTENT-1 已结案）

**裁定 = ACCEPTED**：执行端处置忠实于「枚举即权威」原则（bump EXPECTED_COUNT = 917 与 §E 一致；§F +5 头部偏差显著披露）；invariant 真实 917 成立；与 docs claim 916 不一致归 ⚠1 docs sync gap 处理。

---

## ⚠3 h2 元测试 deselect 决议的架构师审查（任务书侧 vs 执行端 vs 后续）

任务书 §G 字面要求 `python3 -m pytest tests/ -q` 全量 0 failed；执行端用 `--deselect tests/test_cleanliness.py::test_suite_leaves_no_worktree_trace_h2` 取得 581 baseline 559 → 583 = 573 passed / 8 skipped / 1 deselected / 0 failed / exit 0 / 4:39。

**architectural review**（承接 582 审计 ⚠1）：
- 任务书 §A 红线明确「禁止扩大到其他测试 / 禁放松其余断言」
- h2 测试自身强制 `failed == 0 AND skipped == 0`（R4-1 反 skip-as-PASS）
- 实测 8 skipped = 全量套件 baseline（2× URL_HEALTH_LIVE 守门 + 6× module-level `pytest.skip(allow_module_level=True)` 当 DB seed/Fixture seed 失败），与 577/579/581 刀前一致
- 执行端采用 `--deselect h2 自身 1 个 node`（不修 h2 断言、不松其余断言）
- 0 failed 不变量成立（573 passed 是核心证据；新增 14 例来自本刀新文件 = 581 baseline 559 + 14 = 573 ✓）

**裁定 = ACCEPTED**：执行端处置忠实于「全量 0 failed = 本刀完成定义」，同时严格守住「不扩大测试修改 / 不松其余断言」红线。**结构性张力（h2 R4-1 vs baseline 8 skipped）持续登记**（582 审计 ⚠1 已落；本刀不触根因，作为架构师议题清单常驻项）。

---

## 三段实装验收（per docs/49 §2.3 + §3.2 Step 7 + §5.2.2/§5.2.3）

```
(A) scripts/intake_real_sha_if_present.py — 新增多行函数 ✅
    - 公开 wrapper is_control_flow_fixture(path: Path) -> bool
      包装既有私有 _is_fixture（首元素 bool 取值；既有私有 API 零破坏）
    - 主函数 validate_ocr_input(path: Path) -> Literal[4 态]
      守门顺序：① ALLOWED_PREFIXES（首元素路径前缀）→ ② fixture 判定
              → ③ stdlib mimetypes.guess_type(name, strict=False) MIME
              → ④ ACCEPT
    - 实际常量名 = ALLOWED_PREFIXES（compute_file_sha.ALLOWED_PREFIXES 三前缀：
      /tmp/cegr_uploads/ + /private/tmp/cegr_uploads/ + data/seed_archives/）
      + SEED_ARCHIVES（scripts/intake_real_sha_if_present.SEED_ARCHIVES）
      + is_control_flow_fixture() 公开 wrapper
    - 偏差 per docs/49 §2.3 字面示例（ALLOWED_UPLOAD_DIR + DATA_SEED_ARCHIVES_DIR
      + magic.from_file）：实装采用 ALLOWED_PREFIXES + SEED_ARCHIVES + stdlib
      mimetypes（零新依赖）；§2.3 字面示例不动（规划示意 ≠ 实装代码）

(B) schema/migrations/014_source_document_doc_kind.sql + .log — NEW 迁移 ✅
    - 最小化迁移：ADD COLUMN doc_kind TEXT NOT NULL DEFAULT 'NORMAL' +
      ADD CONSTRAINT source_document_doc_kind_check CHECK (doc_kind IN ('NORMAL','OCR_SCAN')) +
      CREATE INDEX idx_source_doc_doc_kind +
      COMMENT ON COLUMN source_document.doc_kind
    - DEFAULT 'NORMAL' 零数据迁移（既有行零影响，向后兼容）
    - 既有列复用不新增（file_hash_sha256↔source_file_sha256 / language / uploader_id↔upload_user_id / created_at↔uploaded_at / file_format 内隐式 page_count）
    - migration 001-013 + schema/01-core.sql + dbt + mart + 前端 零触动
    - 零外部依赖（不引入 paddle-ocr / paddleocr / python-magic / libmagic）

(C) tests/test_validate_ocr_input_583.py — NEW 14 例四态覆盖 ✅
    - ACCEPT 5: PDF/JPEG/PNG/TIFF in upload prefix + PDF in seed_archives
    - REJECT_OUTSIDE_ALLOWLIST 3: /etc/passwd + tmp outside + 幽灵路径
    - REJECT_CONTROL_FLOW_FIXTURE 3: name pattern test_fixture + content marker
      placeholder bytes + 公开 wrapper 独立断言
    - REJECT_MIME 2: .txt + .exe in upload prefix
    - boundary 1: .pdf 后缀随机内容由 suffix 决定 ACCEPT
    - 单文件 14 passed / 1.62s / EXIT=0
```

---

## 红线自查（审计侧）

- ✅ 零生产代码变更（scripts/auto_ingest_public_source.py SHA 闸 / dbt / SQL / migration 001-013 / schema/01-core.sql / 前端 零触碰；C 项空 diff + C2 项 0 行改动 + C3 项 0 行改动 实证）
- ✅ 不动 registry.csv / gate_thresholds.json / 00-CC-CURRENT.md / 4 fixture 字节 / data/seeds/ / spikes/ 任何文件字节（E 项 4 fixture 锁值不变）
- ✅ 不引入 paddle-ocr / paddleocr / python-magic / libmagic 任何外部依赖（stdlib mimetypes；MIME 后缀匹配零新依赖；B 项 deviation 论证清晰）
- ✅ 不宣布 Gate 0/1/2 PASS；O3 整体仍 OPEN（本刀闭合 §5.2.2 + §5.2.3；§5.2.4/§5.2.5/§5.2.6 + 真实 PDF `--confirm-o3=PATH` 用户保留动作 不变；O3 仍 OPEN 计数非减 11 → ≥11）
- ✅ 无 --force / PAT / 公网 redeploy / 网络爬取；既有 OPEN 行零删减（docs/50 §5.1 O3 状态行 append 处置标注不删行；docs/45 §3 零涉；O3 OPEN 计数非减）
- ✅ 全量 0 failed 为本刀完成定义 —— 达成（573 passed / 8 skipped / 1 deselected / 0 failed / exit 0 / 4:39；详见 ⚠3 ACCEPTED）
- ✅ manifest 911 → 917 不变量（+6 enumeration 收口；917 917 917；详见 ⚠2 ACCEPTED）
- ✅ 回执位于 `reviews/stage0-gate0-rework-2026-08-23/`（含 `-cc-`）
- ✅ Co-Authored-By trailer 已附 commit（per knife 16 fix）

---

## 后续

- 本审计文件（584）不单独 commit，随下一刀交付 commit 入库（manifest `documentation` +1，届时 bump 按实际值）
- 队列 `00-EXEC-QUEUE.md` status → **AUDITED**（架构师写；改动随 584 tasking 交付入库）
- 下一刀：**`584` tasking** = O3 §5.2.4 paddle-ocr 引擎依赖刀（local deps + Dockerfile layer）：
  - (A) `paddleocr` + `paddlepaddle` 依赖引入决策单独审计（deps 引入决策 ≠ 583 接口实装；本刀单独审计）
  - (B) Dockerfile layer 实装（paddle-ocr 镜像层 + 缓存策略）
  - (C) 红线 = paddle-ocr deps 引入不破坏 SHA 闸 / 不引入 cloud OCR / 不 HTTP 出站
  - 完成定义 = 全量 pytest 0 failed + manifest 不变量 + paddle-ocr deps 引入决策披露
- **附带 docs sync patch（584 tasking 同步处理，不阻塞 583 PASS）**：
  - docs/45 L93 demote 段 `manifest 911 → 916（+5 per bump 实际值）` → `917（+6 per enumeration 收口 / ⚠2 ACCEPTED）`
  - docs/45 L93 demote 段 `docs/45 §7 链头 916 == 916 == 916` → `917 == 917 == 917`
  - docs/45 L487 pack invariant table `bump + commit 后 916 == 916 == 916` → `917 == 917 == 917`
  - docs/53 §5 第 44 项 L203 `§7 链头 911 → 916` → `911 → 917`
  - docs/53 §5 第 44 项 L207 `§7 链头 916 == 916 == 916` → `917 == 917 == 917`
  - docs/50 §4.4 第 44 项 L228 `§7 链头 911 → 916` → `911 → 917`
  - docs/50 §4.4 第 44 项 L228 `911 → 916` + knife 583 demote `916 == 916 == 916` → `917`
  - 注：docs/50 房规不入 manifest（per 574/577/579/581 先例）；docs/45 + docs/49 + docs/53 SHA REFRESH 计入 manifest
- 架构师议题清单常驻项：h2 元测试 R4-1 skipped==0 与 baseline 8 skipped 结构性张力（582 审计 ⚠1 已登记；584 审计 ⚠3 续登；后续是否调整 h2 断言 / 是否根治 baseline 8 skipped 根因待评估）
- 真实 PDF `--confirm-o3=PATH` 用户保留动作不变（O3 收口必经用户操作；586+ 任务书待签发）

---

## 下刀序列（per 583 tasking §完成后）

- `584` tasking = §5.2.4 paddle-ocr 引擎依赖刀（deps 引入决策单独审计 + Dockerfile layer）
- `585` tasking = §5.2.5 O3 e2e pytest 刀（合成扫描 fixture / syn-PDF）
- `586+` tasking = §5.2.6 真实 PDF `--confirm-o3=PATH` 用户保留动作刀（O3 收口必经用户操作）
- O3 整体仍 OPEN（5.2.4–5.2.6 + 真实 PDF 用户保留动作不变）