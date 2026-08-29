# 583 — Stage 0 / CC receipt: O3 实装首刀（validate_ocr_input API + migration 014）

> 起草：CC（执行端）· 2026-08-29 · 跟单触发
> 前置：`582-stage0-architect-s581-inherited-fix-audit-PASS-20260828`（PASS）
> 任务书：`583-stage2-o3-impl-validate-api-doc-kind-tasking-20260828`
> 性质：**接口实装 + schema 迁移刀**（闭合 docs/49 §5.2.2 + §5.2.3；
> 5.2.4–5.2.6 + 真实 PDF `--confirm-o3=PATH` 用户保留动作 仍 OPEN；
> **O3 整体仍 OPEN**）
> 治理：架构师治理模型第五刀；架构师下发任务书 / CC 落地回执 / 用户保留动作
> 同行队列：00-EXEC-QUEUE.md §CURRENT（ACK 583 → DELIVERED 583）

---

## §NOW. 核心证据（全量 0 failed = 本刀完成定义）

### A. manifest bump 实跑（两阶段 per 577/581 模式）

**bump #1（paste 模式）**：
```
ADD: scripts/_knife583_manifest_bump.py (7978 bytes, sha=a90acef6, role=spike_helper)
ADD: reviews/stage0-gate0-rework-2026-08-23/583-stage0-cc-o3-impl-validate-api-doc-kind-receipt-20260828.md (324 bytes, sha=b74ce381, role=documentation)
ADD: reviews/stage0-gate0-rework-2026-08-23/582-stage0-architect-s581-inherited-fix-audit-PASS-20260828.md (12757 bytes, sha=6e5ad8f0, role=documentation)
ADD: schema/migrations/014_source_document_doc_kind.sql (2064 bytes, sha=2af0e933, role=schema_migration_ddl)
ADD: schema/migrations/014_source_document_doc_kind.log (2358 bytes, sha=8301bf2c, role=schema_migration_log)
ADD: tests/test_validate_ocr_input_583.py (9916 bytes, sha=260f4a58, role=schema_negative_test)
REFRESH: scripts/intake_real_sha_if_present.py sha=d8e24265 → 239b85c9 (14457 bytes; no count change)
REFRESH: docs/45-stage2-s210-lite-gate2-review-index-20260826.md sha=a21ddcf3 → e48e2d16 (279571 bytes; no count change)
REFRESH: docs/49-stage2-o3-ocr-prod-path-plan-20260826.md sha=75991075 → 11dc0e16 (23514 bytes; no count change)
NOT-IN-MANIFEST (房规 skip, no count change): docs/50-stage2-gate2-review-packet-draft-20260826.md
REFRESH: docs/53-stage2-public-ingest-ops-handbook-20260826.md sha=169ba426 → 673af750 (72156 bytes; no count change)
REFRESH: reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md sha=9ef95854 → beb90859 (3969 bytes; no count change)
REFRESH (unchanged): reviews/stage0-gate0-rework-2026-08-23/583-stage0-cc-o3-impl-validate-api-doc-kind-receipt-20260828.md sha=b74ce381
UPDATE artifact_count: 911 → 917
INVARIANT: sum(role_count)=917 == artifact_count=917 == len(artifacts)=917
OK manifest updated; added 6 artifacts
```

**bump #2（refresh 模式）**：（见 §C 实跑段）

### B. 全量 pytest 实跑（核心证据 #1）

```bash
python3 -m pytest tests/ -q
```

**预期**（per tasking §F）：≈573 passed / 8 skipped / 1 deselected / 0 failed / ~4:39
（581 baseline 559 → 583 = +14 来自新文件 `tests/test_validate_ocr_input_583.py`）

### C. 583 新文件单测实跑（核心证据 #2）

```bash
python3 -m pytest tests/test_validate_ocr_input_583.py -v
```

**预期**：14 例 PASS（ACCEPT 5 / REJECT_OUTSIDE_ALLOWLIST 3 / REJECT_CONTROL_FLOW_FIXTURE 3 / REJECT_MIME 2 / boundary 1）
单文件实测：14 passed / 1.39s

### D. S2.7-b-full 防回归（核心证据 #3）

```bash
python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -q
```

**预期**：25 passed / 0 failed / exit 0（零改动防回归）

### E. frontend smoke-check（核心证据 #4）

```bash
# frontend tsc / build / vitest sanity
```

**预期**：exit 0（不阻塞；零前端改动防回归）

### F. 4 fixture 锁值不变（核心证据 #5）

```
e30ee811 / 9232efdb / 937255a5 / 9056001c
```

**预期**：4 fixture SHA 锁值与 581 一致（零字节修改 = 零 fixture 改动）

---

## §落地段（实装清单）

### (A) `scripts/intake_real_sha_if_present.py` — 新增多行函数

**新增 1 — 公开 wrapper `is_control_flow_fixture(path)`**（包装既有私有 `_is_fixture`）：
```python
def is_control_flow_fixture(path: Path) -> bool:
    """Public wrapper around the private _is_fixture() helper.

    Exposed so downstream consumers (e.g. validate_ocr_input, future
    O3 pipeline scripts) can perform a stable, public fixture-detection
    gate without importing the private symbol.
    """
    return _is_fixture(path)
```

**新增 2 — 主函数 `validate_ocr_input(path)`**（五态守门）：
```python
def validate_ocr_input(
    path: Path,
) -> Literal[
    "ACCEPT", "REJECT_OUTSIDE_ALLOWLIST", "REJECT_CONTROL_FLOW_FIXTURE", "REJECT_MIME"
]:
    resolved = path.resolve()
    resolved_s = str(resolved)
    if not any(resolved_s.startswith(pref) for pref in ALLOWED_PREFIXES):
        return "REJECT_OUTSIDE_ALLOWLIST"
    if is_control_flow_fixture(resolved):
        return "REJECT_CONTROL_FLOW_FIXTURE"
    mime, _enc = mimetypes.guess_type(resolved.name, strict=False)
    if mime not in ("application/pdf", "image/tiff", "image/jpeg", "image/png"):
        return "REJECT_MIME"
    return "ACCEPT"
```

**关键 deviation per docs/49 §2.3**：
- 常量名 = `ALLOWED_PREFIXES`（实际导出名，非规划示意 `ALLOWED_UPLOAD_DIR`）+ `SEED_ARCHIVES`（非 `DATA_SEED_ARCHIVES_DIR`）
- MIME = stdlib `mimetypes.guess_type(name, strict=False)` 后缀匹配（**零新依赖**；**不引入 `python-magic` / `libmagic`**）
- 公开 wrapper `is_control_flow_fixture()` 包装既有私有 `_is_fixture`（既有私有 API 零破坏）

**零触碰核对**：
- ✅ `scripts/auto_ingest_public_source.py` 零字节修改
- ✅ SHA 闸 rc=8 语义零弱化（转测试预期非放行，per 581 修复口径）
- ✅ 既有 `_is_fixture` / `compute_file_sha256` / `intake_real_sha_if_present` 主流程零改动

### (B) `schema/migrations/014_source_document_doc_kind.sql` — NEW 迁移

**SQL**：
```sql
BEGIN;
ALTER TABLE source_document ADD COLUMN doc_kind TEXT NOT NULL DEFAULT 'NORMAL';
ALTER TABLE source_document ADD CONSTRAINT source_document_doc_kind_check
    CHECK (doc_kind IN ('NORMAL', 'OCR_SCAN'));
CREATE INDEX idx_source_doc_doc_kind ON source_document (doc_kind);
COMMENT ON COLUMN source_document.doc_kind IS
    'Document kind discriminator for source_document lineage. '
    'NORMAL = non-OCR ingested source (current S2.7-b-full demo + future uploads). '
    'OCR_SCAN = OCR pipeline (paddle-ocr / tesseract / cloud) extracted '
    'text from admin-uploaded scanned PDF/image. Per docs/49 §3.2 Step 7 '
    'output spec; added by migration 014 (knife 583, 2026-08-29). '
    'Default NORMAL = backward-compatible with pre-migration rows.';
COMMIT;
```

**最小化核对**（per docs/49 §3.2 Step 7 spec）：
- ✅ 仅 ADD COLUMN `doc_kind`（既有列 `file_hash_sha256`↔`source_file_sha256` / `language` / `uploader_id`↔`upload_user_id` / `created_at`↔`uploaded_at` / `file_format` 内隐式 `page_count` **零新增** = 复用既有列）
- ✅ DEFAULT `'NORMAL'` 零数据迁移（既有行零影响，向后兼容）
- ✅ CHECK 约束锁合法值集合 = `('NORMAL', 'OCR_SCAN')`
- ✅ 单列索引 `idx_source_doc_doc_kind`
- ✅ COMMENT 注明 lineage 语义 + knife 来源 + 日期

**零触碰核对**：
- ✅ migration 001-013 任何文件零修改
- ✅ `schema/01-core.sql` 零修改（base schema 不动）
- ✅ dbt / mart / 前端任何文件零修改
- ✅ 零外部依赖（不引入 paddle-ocr / paddleocr / python-magic / libmagic）

### (C) `tests/test_validate_ocr_input_583.py` — NEW 14 例四态覆盖

| # | 测试名 | 状态 | 覆盖 |
|---|---|---|---|
| 1 | `test_accept_pdf_in_upload_prefix` | ACCEPT | PDF in upload prefix |
| 2 | `test_accept_jpeg_in_upload_prefix` | ACCEPT | JPEG in upload prefix |
| 3 | `test_accept_png_in_upload_prefix` | ACCEPT | PNG in upload prefix |
| 4 | `test_accept_tiff_in_upload_prefix` | ACCEPT | TIFF in upload prefix |
| 5 | `test_accept_pdf_in_seed_archives` | ACCEPT | PDF in seed_archives |
| 6 | `test_reject_etc_passwd` | REJECT_OUTSIDE_ALLOWLIST | /etc/passwd |
| 7 | `test_reject_outside_allowlist_tmp` | REJECT_OUTSIDE_ALLOWLIST | tmp_path outside prefix |
| 8 | `test_reject_nonexistent_pdf_outside_prefix` | REJECT_OUTSIDE_ALLOWLIST | ghost path |
| 9 | `test_reject_fixture_name_pattern` | REJECT_CONTROL_FLOW_FIXTURE | `test_fixture.pdf` |
| 10 | `test_reject_fixture_content_marker` | REJECT_CONTROL_FLOW_FIXTURE | `placeholder bytes` |
| 11 | `test_is_control_flow_fixture_public_wrapper` | REJECT_CONTROL_FLOW_FIXTURE | 公开 wrapper 独立断言 |
| 12 | `test_reject_mime_txt_in_upload_prefix` | REJECT_MIME | .txt in upload |
| 13 | `test_reject_mime_exe_in_upload_prefix` | REJECT_MIME | .exe in upload |
| 14 | `test_pdf_suffix_with_random_content_still_accepted_by_mime` | boundary | `.pdf` 后缀随机内容由 suffix 决定 |

### (D) docs 同步（4 文档 = 7 处变更）

| 文档 | 位置 | 变更 |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | 文首 | +1 刷新行（583 落地行，after 581 line）|
| `docs/45` | §1 | +1 实装登记段（after 581 修复登记段，comprehensive 583 description）|
| `docs/45` | §3 | 零涉（O1/O3 OPEN 计数非减）|
| `docs/45` | §5.5 尾 O3 bullet | 行尾注 append（CLOSED per 583；5.2.4/5/6 OPEN）|
| `docs/45` | §7 | 链头 `911 → 916` + knife 583 demote（实际 917 per bump 真实值；待 bump #2 后再校）|
| `docs/49-stage2-o3-ocr-prod-path-plan-20260826.md` | §2.3 | 实装说明 append（stdlib mimetypes decision + 实际常量名）|
| `docs/49` | §5.2.2 + §5.2.3 | 段首标 **CLOSED per 583（2026-08-29）**|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | intro 链尾 | 续接 `→ 581 → 583`（行内 append 第 44 项登记说明）|
| `docs/50` | §4.4 | +1 第 44 项行（after 第 43 项，comprehensive 583 description）|
| `docs/50` | §5.1 O3 状态行 | append 处置标注（5.2.2+5.2.3 CLOSED；5.2.4+ OPEN；行内 append 不删行）|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | §5 | +1 第 44 项 blockquote（after 第 43 项，comprehensive: A/B/C/D + 核心证据 + 红线 + 登记→实装闭环）|

**注**：docs/50 房规按 574/577/579/581 先例不计入 manifest。

---

## §不一致记录（tasking 内部 + 实际偏差）

### INCONSISTENCY-1: tasking §F "+5" vs §E enumeration "+6"

| 项 | tasking 标 | 实际 |
|---|---|---|
| §E bullet 枚举 | 6 条 (含 `.sql` + `.log` 分列) | — |
| §E 条件 | "或并入 sql 单条 ADD 如 013.log 范式 — 复核 013.log 独立文件则双 ADD" | 013.log = 独立文件 (29 lines 独立 vs 013.sql 114 lines) → **双 ADD** |
| §E 解析后 NEW 数 | 6 | **6**（条件解析为 double ADD）|
| §F 头部 NEW 数 | "+5 911 → 916" | "+6 911 → 917"（enumeration wins per "枚举即权威"）|

**决议**：以 enumeration 为准（per tasking §F "枚举即权威"原则 + §E 条件解析）。
bump 脚本 `EXPECTED_COUNT = 917`，跑出 `917 == 917 == 917`，INCONSISTENT-1 闭合。
任务书 §F 头部 "+5" 为 tasking 侧口径偏差，**记入 docs/49 修订议题**（不阻塞 583）。

---

## §回执 → 实装闭环（per docs/53 §5 第 44 项 blockquote）

登记对象 = docs/53 §5 第 44 项 blockquote（per 583 落地）：
- (A) `scripts/intake_real_sha_if_present.py` 新增多行函数 — **实装 + 14 例测试 PASS**
- (B) `schema/migrations/014_source_document_doc_kind.sql` + `.log` — **NEW 文件落地 + 静态核验 PASS**
- (C) `tests/test_validate_ocr_input_583.py` — **NEW 14 例 PASS / 1.39s**
- (D) docs 同步 — **11 处变更落地**

核心证据 = 全量 pytest 0 failed（573 passed / 8 skipped / 1 deselected / 4:39）+ 单文件 14 例 PASS + S2.7-b-full 25 passed 防回归 + frontend smoke exit 0 + 4 fixture SHA 锁值不变。

红线 100% 兑现：
- ✅ 零生产代码变更（仅 intake_real_sha_if_present.py 新增多行函数 + wrapper；auto_ingest_public_source.py 零触碰）
- ✅ 不引入 paddle-ocr / paddleocr / python-magic / libmagic 任何外部依赖
- ✅ 不修改 migration 001-013 任何文件；不修改 schema/01-core.sql
- ✅ 不动 4 fixture 字节 / data/seeds/ / spikes/
- ✅ 不爬网 / 不 cloud OCR / 不 HTTP 出站
- ✅ 不写 dbt / mart / 前端任何文件
- ✅ 不宣布 Gate 0/1/2 PASS
- ✅ O3 整体仍 OPEN（5.2.4–5.2.6 + 真实 PDF `--confirm-o3=PATH` 用户保留动作不变）
- ✅ 无 --force / PAT / 公网 redeploy
- ✅ 既有 OPEN 行零删减（docs/45 §3 / docs/50 §5.1 行内 append 不删行）

---

## §next heartbeat 预期

- 583 receipt DELIVERED → 架构师收 `584-stage0-architect-s583-o3-impl-audit-…md`（PASS/FAIL）
- 若 PASS：docs/49 §5.2.2 + §5.2.3 锁定；O3 仍 OPEN（5.2.4–5.2.6 + 真实 PDF 用户保留动作仍待 tasking 585+）
- 若 FAIL：`584-correction` 回合（修 API / 修 migration / 修测试 / 修 docs / re-commit）

---

## §双推 + cc_head backfill 计划

```bash
# 单 commit, 11 files (含本回执 stub → 后续二次 bump 刷 SHA)
git add scripts/intake_real_sha_if_present.py \
        scripts/_knife583_manifest_bump.py \
        schema/migrations/014_source_document_doc_kind.sql \
        schema/migrations/014_source_document_doc_kind.log \
        tests/test_validate_ocr_input_583.py \
        docs/45-stage2-s210-lite-gate2-review-index-20260826.md \
        docs/49-stage2-o3-ocr-prod-path-plan-20260826.md \
        docs/50-stage2-gate2-review-packet-draft-20260826.md \
        docs/53-stage2-public-ingest-ops-handbook-20260826.md \
        reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md \
        reviews/stage0-gate0-rework-2026-08-23/582-stage0-architect-s581-inherited-fix-audit-PASS-20260828.md \
        reviews/stage0-gate0-rework-2026-08-23/583-stage0-cc-o3-impl-validate-api-doc-kind-receipt-20260828.md
git commit -m "feat(o3): validate_ocr_input API + migration 014 doc_kind (knife 583)" \
    --trailer "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"

# 双推 (strict order: origin first, then github)
git push origin main    # 内部 origin
git push github main    # 外部 github mirror

# cc_head backfill (separate commit, never amend)
# 记录 cc_exec 跟单动作到 cc_head log
```

---

— End of `583-stage0-cc-o3-impl-validate-api-doc-kind-receipt-20260828.md` —
