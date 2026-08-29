# 583 — 任务书：O3 实装首刀（validate_ocr_input API + doc_kind='OCR_SCAN' migration 014）

- 编号：`583-stage2-o3-impl-validate-api-doc-kind-tasking-20260828`
- 前置：`582-stage0-architect-s581-inherited-fix-audit-PASS-20260828`（581 审计 PASS；581 修复刀恢复全量 0 failed + manifest 911）
- 规划蓝图：`docs/49-stage2-o3-ocr-prod-path-plan-20260826.md` §2.3（API 形态）+ §3.2 Step 7（source_document 输出）+ §5.2.2 + §5.2.3（实装位置）
- 引擎裁定（per `579`）：**paddle-ocr**（用户 2026-08-28；§5.2.1 已关闭；5.2.4–5.2.6 OPEN）
- 下发：CC 架构师终端 → 执行端（经 `00-EXEC-QUEUE.md`，PENDING → ACK → DELIVERED）
- 日期：2026-08-29
- 验证深度：**零网络 · 接口实装 + schema 迁移刀**（migration 014 NEW；接口函数实装于既有脚本；零外部依赖新增；全量 pytest 为本刀核心证据）

---

## §NOW

**背景（per docs/49 §2.3 API 形态 + §5.2.2/§5.2.3 实装位置）**：O3 实装链 5.2.2 + 5.2.3 闭合 → API + migration 落地。引擎依赖（paddle-ocr）走 §5.2.4 单独刀（5.2.4 = local deps + Dockerfile layer），避免本刀同时引入外部依赖导致回滚粒度过粗；真实 PDF 走 §5.2.6（用户 `--confirm-o3=PATH` 保留动作，本刀不触）。

**架构师本刀关键决策（基于实际代码库调研）**：
1. **API 常量名映射**：docs/49 §2.3 形态示例用 `ALLOWED_UPLOAD_DIR` + `DATA_SEED_ARCHIVES_DIR` + `is_control_flow_fixture`；实际 `scripts/intake_real_sha_if_present.py` 现有导出 = `ALLOWED_PREFIXES`（line 59，来自 `compute_file_sha.ALLOWED_PREFIXES`）+ `SEED_ARCHIVES`（line 56）+ `_is_fixture`（line 79，私有）。**本刀实装采用实际导出名**（`ALLOWED_PREFIXES` + `SEED_ARCHIVES`），并在 intake_real_sha_if_present.py 中**新增公开 wrapper** `is_control_flow_fixture(path) -> bool` 包装私有 `_is_fixture`（取首元素 bool），避免打破既有私有 API。**docs/49 §2.3 示例为规划示意，与实装以代码为准**——任务书侧口径偏差，记入 docs/49 修订议题（不阻塞 583）。
2. **MIME 检测零新依赖**：docs/49 §2.3 示例用 `magic.from_file()`（python-magic + libmagic 系统库）。**本刀实装采用 stdlib `mimetypes` 模块**（按后缀判断，零新依赖；PDF/image MIME 后缀覆盖完整 = docs/49 §2.1 合法 MIME 集全覆盖）。**§5.2.4 后续刀**如需 content sniffing 精度提升，可切到 python-magic（独立 deps 决策）。本刀完成定义不依赖 magic lib。
3. **migration 014 最小化**：docs/49 §3.2 Step 7 输出 spec 含 `source_file_sha256 / doc_kind / language / page_count / upload_user_id / uploaded_at / lineage`。**核对 source_document 现有列**（schema/01-core.sql L312–334）：`file_hash_sha256 / language / file_format / uploader_id (=upload_user_id 语义映射) / created_at (=uploaded_at 语义映射)` 已存在。**migration 014 仅新增 `doc_kind TEXT NOT NULL DEFAULT 'NORMAL'`** + CHECK 约束（合法值 = `'NORMAL' | 'OCR_SCAN'`）+ 单列索引；**不新增 `upload_user_id` / `uploaded_at` / `lineage`**（已存在语义映射列，避免列冗余）。**page_count 已在 `file_format` 内隐式表达**（PDF 页数将来走 OCR 工具元数据提取，非 schema 强制列）。

---

### (A) `scripts/intake_real_sha_if_present.py` — 新增 `validate_ocr_input()` API + `is_control_flow_fixture()` 公开 wrapper（已入 manifest → REFRESH）

**实装位置**：`scripts/intake_real_sha_if_present.py`（既有脚本，新增多行函数，不新建脚本）

**新增 1 — 公开 wrapper（包装既有私有 `_is_fixture`）**：
- 在 `_is_fixture` 函数附近（line 79 后）新增公开函数：
  ```python
  def is_control_flow_fixture(path: Path) -> bool:
      """per docs/48 §4.1；公开 wrapper 包装私有 _is_fixture。"""
      ok, _reason = _is_fixture(path)
      return ok
  ```
- docstring 写明：用于 O3 validate_ocr_input 调用 + docs/49 §2.3 / docs/48 §4.1 判定

**新增 2 — `validate_ocr_input()` 主函数**：
- 函数签名严格按 docs/49 §2.3：
  ```python
  def validate_ocr_input(path: Path) -> Literal["ACCEPT", "REJECT_OUTSIDE_ALLOWLIST", "REJECT_CONTROL_FLOW_FIXTURE", "REJECT_MIME"]:
      """per docs/49 §2.3；五态守门：路径 allowlist → fixture 判定 → MIME 白名单。"""
  ```
- 守门顺序（per docs/49 §2.3 字面）：
  1. `resolved = path.resolve()`；若 `resolved.is_relative_to(ALLOWED_UPLOAD_DIR)` 或 `resolved.is_relative_to(SEED_ARCHIVES)`（即实际 `ALLOWED_PREFIXES` 任一前缀）→ pass；否则 return `"REJECT_OUTSIDE_ALLOWLIST"`
  2. `is_control_flow_fixture(resolved)` → True 则 return `"REJECT_CONTROL_FLOW_FIXTURE"`
  3. `mimetypes.guess_type(resolved.name, strict=False)[0]` 命中 `application/pdf` / `image/tiff` / `image/jpeg` / `image/png` 任一 → pass；否则 return `"REJECT_MIME"`
  4. 全 pass → return `"ACCEPT"`
- `ALLOWED_UPLOAD_DIR` 常量映射：实际 `ALLOWED_PREFIXES` 列表（`compute_file_sha.ALLOWED_PREFIXES`），取首元素作为 primary `ALLOWED_UPLOAD_DIR` 常量（如有 `ALLOWED_UPLOAD_DIR = ALLOWED_PREFIXES[0]`）；`DATA_SEED_ARCHIVES_DIR` 映射为既有 `SEED_ARCHIVES` 常量
- import 增量：`from typing import Literal`（如既有 typing import 已含则跳过）；`import mimetypes`（stdlib）
- docstring 写明：本函数纯路径 + MIME 判定，**不触发 SHA 计算、不读文件内容**（IO 最小化；SHA 计算走既有 `compute_file_sha.py` 入口）

**变更边界**：
- 本文件其他函数零改动（`_is_candidate_window` / `_compute_sha_via_cli` / `_scan_allowlist` / `_build_lineage` / `_assert_contract` / `main` 零触碰）
- 既有 import 零改动
- 既有常量（`MIN_CANDIDATE_SIZE_BYTES` / `CONTROL_FLOW_MTIME_WINDOW_S` / `CANDIDATE_MTIME_WINDOW_S` / `FIXTURE_NAME_PATTERNS` / `FIXTURE_CONTENT_MARKERS` / `ZERO_SHA` / `SHA_PATTERN`）零改动

---

### (B) `schema/migrations/014_source_document_doc_kind.sql` — NEW 迁移 + 对应 `.log` 旁车（**NOT-IN manifest → ADD +2**）

**新增文件 1**：`schema/migrations/014_source_document_doc_kind.sql`

**最小化迁移内容**（单 column 增量 + CHECK + index）：

```sql
-- Migration 014 — O3 OCR 生产路径：source_document.doc_kind 列
--
-- Per docs/49 §3.2 Step 7 output spec + §5.2.3 (实装位置) + 583 任务书 §B。
-- 前置：582 审计 PASS；581 修复刀完成。
-- 性质：流程刀落地（最小）；单列增量 + CHECK + index；零数据迁移（DEFAULT 'NORMAL'）。
--
-- 闭合 docs/49 §5.2.3；O3 引擎依赖（paddle-ocr / 5.2.4 / 5.2.5 / 5.2.6）后续刀。
--
-- 列选择 deviation 论证：
--   docs/49 §3.2 Step 7 列 spec = {source_file_sha256, doc_kind, language, page_count,
--                                    upload_user_id, uploaded_at, lineage}
--   source_document 既有列（schema/01-core.sql L312–334）已含：
--     file_hash_sha256 ↔ source_file_sha256 ✓（既有，零新增）
--     language ✓（既有，DEFAULT 'zh'）
--     uploader_id (TEXT) ↔ upload_user_id 语义映射 ✓（既有，零新增）
--     created_at (TIMESTAMPTZ) ↔ uploaded_at 语义映射 ✓（既有，零新增）
--     file_format (TEXT) 内隐式表达 page_count（OCR 工具元数据提取，非 schema 列）
--   → migration 014 **仅新增 doc_kind 列**；其余语义映射走既有列，避免列冗余。
--
-- 评分/排名/总分字段 (score/rating/rank/total_score/confidence_score/credibility_score)
-- 红线: 一律不引入.
--
-- 线 lineage JSONB（如需）：迁移本期不新增；如 O3 流水线后续需独立 lineage 列（区别
--   source_document.file_hash_sha256 上游链），后续刀 §5.2.7+ 单独议。

BEGIN;

ALTER TABLE source_document
    ADD COLUMN doc_kind TEXT NOT NULL DEFAULT 'NORMAL';

ALTER TABLE source_document
    ADD CONSTRAINT source_document_doc_kind_check
        CHECK (doc_kind IN ('NORMAL', 'OCR_SCAN'));

CREATE INDEX idx_source_doc_doc_kind ON source_document (doc_kind);

COMMENT ON COLUMN source_document.doc_kind IS
    '来源文档类型：NORMAL = 普通文件上传（默认值，向后兼容既有行）；OCR_SCAN = 扫描件 OCR 录入（per docs/49 §3.2 Step 7 + 583 任务书 §B）';

COMMIT;
```

**新增文件 2**：`schema/migrations/014_source_document_doc_kind.log`（旁车，按 001-013 范式）
- 内容按 013 `.log` 范式：执行环境 + dry-run 语法核验（如环境无 psql 则仅写 schema 静态核验）+ 时间戳 + commit 指针占位

**红线**：
- ❌ 不修改 migration 001-013 任何文件（仅新增 014 + .log 旁车）
- ❌ 不修改 schema/01-core.sql（既定 base schema）
- ❌ 不修改 dbt / mart / 前端任何文件
- ❌ 不引入 paddle-ocr / paddleocr 任何依赖（本刀零新依赖）

---

### (C) `tests/test_validate_ocr_input_583.py` — NEW 测试文件（**NOT-IN manifest → ADD +1**）

**新增文件**：`tests/test_validate_ocr_input_583.py`

**测试覆盖（四态）**：

1. **ACCEPT 路径**：
   - 用 `tmp_path` 构造位于 `ALLOWED_PREFIXES[0]` 下（即 `/tmp/...` 或 `/private/tmp/...`）的 PDF 文件（magic bytes `%PDF-1.4\n` 起手）；`validate_ocr_input(p)` → `"ACCEPT"` ✓
   - 用 `tmp_path` 构造位于 `SEED_ARCHIVES` 下的合法 PDF（fixture 文件实测 bytes 提供）；`validate_ocr_input(p)` → `"ACCEPT"` ✓
   - 同上：JPEG/PNG/TIFF 后缀对应 MIME 命中 → `"ACCEPT"`

2. **REJECT_OUTSIDE_ALLOWLIST 路径**：
   - 构造路径 = `Path("/etc/passwd")`（不可能在 ALLOWED_PREFIXES）；`validate_ocr_input(p)` → `"REJECT_OUTSIDE_ALLOWLIST"` ✓
   - 构造路径 = `tmp_path` 但不在 ALLOWED_UPLOAD_DIR 下（如显式 `Path("/tmp/non_prefix/test.pdf")` 不在 `compute_file_sha.ALLOWED_PREFIXES` 任一前缀下）；如无法构造则用 mock `ALLOWED_PREFIXES` 临时收紧测试

3. **REJECT_CONTROL_FLOW_FIXTURE 路径**：
   - 复用既有 `spikes/01-national-yearbook/sample.html` 或自造 fixture 文件（首 32 bytes 含 docs/48 §4.1 标记，如首 32 bytes 含 `NOT a forged` 或 `placeholder bytes`）；`validate_ocr_input(p)` → `"REJECT_CONTROL_FLOW_FIXTURE"` ✓

4. **REJECT_MIME 路径**：
   - 构造 PDF 后缀但内容非 PDF（如 `.pdf` 文件内容 = `random bytes` 不以 `%PDF-` 起手且 mimetypes 按后缀仍判为 application/pdf → pass 后缀但本路径不触发）
   - 正确触发：构造后缀 = `.txt` 或 `.exe`，位于 ALLOWED_UPLOAD_DIR 下；`validate_ocr_input(p)` → `"REJECT_MIME"` ✓
   - 边界：构造后缀 `.pdf` 但文件实际不存在 → 行为定义为 REJECT_OUTSIDE_ALLOWLIST（path.resolve() 后落 ALLOWED_UPLOAD_DIR 失败）

**fixture 规范**：
- 不在 spike 路径下新建文件（spike 既有零修改）；用 `tmp_path` + `write_bytes()` 自造测试输入
- 不依赖网络 / 不写磁盘到 spike 目录
- 不修改既有任何 fixture（4 fixture 锁值不变 e30ee811 9232efdb 937255a5 905600c1）

**imports**：
- `from scripts.intake_real_sha_if_present import validate_ocr_input, is_control_flow_fixture, ALLOWED_PREFIXES, SEED_ARCHIVES`
- `from pathlib import Path`
- `import tempfile, pytest`

---

### (D) docs 登记（**docs/49 + docs/53 + docs/45 + docs/50 四件同步**）

- **docs/49 §2.3 实装说明**：在 §2.3 示例下方 append 一行「实装 per 583 任务书 §A：采用 stdlib mimetypes（零新依赖）；常量名 = ALLOWED_PREFIXES + SEED_ARCHIVES + is_control_flow_fixture 公开 wrapper；不引入 python-magic（§5.2.4 议）」；**§2.3 字面示例不动**（规划示意 ≠ 实装代码）
- **docs/49 §5.2.2/5.2.3 状态翻转**：在 §5.2.2 / §5.2.3 段首标注「**CLOSED per 583（YYYY-MM-DD）**」；§5.2.4/5.2.5/5.2.6 保持 OPEN
- **docs/53 §5 新增第 44 项**（per 581 末项第 43 项后）：
  - blockquote 内容 = 583 实装登记（API + migration 014 + 四态单测 + docs 同步）
  - 闭合范围明示 = 5.2.2 + 5.2.3；保持 OPEN = 5.2.4–5.2.6 + O3 收口
- **docs/45 五处**（落点族 per `580` ⚠2 裁定）：
  - 文首 +1 刷新行（架构师治理模型第五刀）
  - §1 +1 段（O3 实装首刀登记）
  - §5.5 尾 O3 bullet 行尾注 append（per `583`）
  - §7 链头 `916 == 916 == 916`（per bump 实际值）+ knife 583 demote
  - §3 零涉（无裁定变更）
- **docs/50**：
  - §4.4 +1 第 44 项行
  - intro 链尾 `→ 581` 续接 `→ 583`
  - §5.1 O3 状态行 append 处置标注（O3 5.2.2+5.2.3 CLOSED；5.2.4+ OPEN）

**「O3 仍 OPEN」计数非减**（5.2.4+ 仍 OPEN = O3 整体仍 OPEN）

---

### (E) manifest bump（**+5**）

`scripts/_knife583_manifest_bump.py`：NEW **+5**（枚举即权威，每项实测 NOT-IN）：
- bump 脚本本身（`spike_helper`）
- `583` 回执（`documentation`）
- `582` 审计文件（`documentation`，只读随刀入库）
- `schema/migrations/014_source_document_doc_kind.sql`（`schema_migration`，NEW 角色）
- `schema/migrations/014_source_document_doc_kind.log`（`schema_migration_log`，NEW 角色；或并入 sql 单条 ADD 如 013.log 范式 — 复核 013.log 独立文件则双 ADD）
- `tests/test_validate_ocr_input_583.py`（`schema_negative_test`）
→ **911 → 916**；断言 `sum(role_count) == artifact_count == len(artifacts) == 916`

**REFRESH**：`scripts/intake_real_sha_if_present.py` + docs/45 + docs/49 + docs/50 + docs/53 + `00-EXEC-QUEUE.md`（SHA REFRESH 不增计数）

**SKIP**：docs/50 房规未入 manifest（574/577/579/581 先例一致）；任务书按先例不计数

---

### (F) 零网络核验（命令 + 输出原样粘贴进回执；**(1) 全量为本刀核心证据**）

```bash
python3 -m pytest tests/ -q                                          # 全量：预期 0 failed（≈561+ passed / 8 skipped，+583 新增 4 态测试；~13 分钟）
python3 -m pytest tests/test_validate_ocr_input_583.py -q            # 新文件单独实跑（4 态 PASS）
python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -q          # 25 passed（零改动防回归）
python3 frontend/smoke-check.py                                      # PASS / exit 0
shasum -a 256 frontend/lib/public_extract_{nbs,nbs_live_candidate,sz,hubei}.json | cut -c1-8
                                                                    # e30ee811 9232efdb 937255a5 905600c1
grep -c "O3 仍 OPEN" docs/45-*.md                                   # ≥11（非减）
grep -c "第 44 项（此条）" docs/53-*.md                              # 1
grep -c "916 == 916 == 916" docs/45-*.md                            # 1（stale 911 = 0）
python3 -c "import json;m=json.load(open('evidence_pack/manifest.json'));print(len(m['artifacts']),m['artifact_count'],sum(m['role_count'].values()))"
                                                                    # 916 916 916
ls schema/migrations/014*                                            # 2 文件（sql + log）
psql --version 2>/dev/null || echo "psql not available - migration 014 语法静态核验 per docs/46 / migration 013 范式（迁移脚本含 BEGIN/COMMIT + ALTER TABLE + CHECK + CREATE INDEX + COMMENT 标准结构，syntax check 由执行端人工 review 即可）"
```

---

### (G) 回执 + 交付 commit

- 回执：`reviews/stage0-gate0-rework-2026-08-23/583-stage0-cc-o3-impl-validate-api-doc-kind-receipt-20260828.md`（含 `-cc-`；单槽单回执，仅 `583`）
- 交付 commit 含：
  - `scripts/intake_real_sha_if_present.py`（MODIFIED）
  - `schema/migrations/014_source_document_doc_kind.sql`（NEW）
  - `schema/migrations/014_source_document_doc_kind.log`（NEW）
  - `tests/test_validate_ocr_input_583.py`（NEW）
  - docs/49 + docs/50 + docs/53 + docs/45（MODIFIED）
  - bump 脚本（NEW）
  - `582` 审计文件（NEW，只读随刀入库）
  - `583` 任务书（NEW，只读随刀入库）
  - `583` 回执（NEW）
  - `00-EXEC-QUEUE.md`（ACK 填行 + status→DELIVERED）
- cc_head backfill 单独 commit（勿 amend）；`git push origin HEAD` → `git push github HEAD` 严格顺序

---

## 红线（零豁免）

- ❌ 零生产代码变更（仅 `scripts/intake_real_sha_if_present.py` 新增多行 API + wrapper；**`scripts/auto_ingest_public_source.py` 零触碰**；SHA 闸零弱化）
- ❌ 不修改 migration 001-013 任何文件（**仅新增 014 + .log 旁车**）；不修改 schema/01-core.sql（base schema 零改动）
- ❌ 不引入 paddle-ocr / paddleocr / python-magic / libmagic 任何外部依赖（**零新依赖**；MIME 检测走 stdlib mimetypes）
- ❌ 不写 dbt / mart / 前端任何文件
- ❌ 不爬网 / 不 cloud OCR / 不 HTTP 出站（`scripts/compute_file_sha.py` `ALLOWED_PREFIXES` 不含 `http(s)://`）
- ❌ 不修改 4 fixture 字节 / data/seeds/ / spikes/ 任何文件
- ❌ 不宣布 Gate 0/1/2 PASS；不宣布 O3 收口；O3 整体仍 OPEN（5.2.4–5.2.6 + 真实 PDF 用户保留动作不变）
- ❌ 无 --force / PAT / 公网 redeploy；既有 OPEN 行零删减（docs/50 §5.1 O3 行 append 处置标注不删行）
- ✅ 全量 0 failed 为本刀完成定义；manifest 911 → 916 不变量（+5 枚举即权威）；回执位于 `reviews/stage0-gate0-rework-2026-08-23/`

---

## 完成后

双推完成即停，回报 cc_head；架构师出 `584` 号位审计；随后签发 **`584` = §5.2.4 O3 引擎依赖刀**（local deps + Dockerfile layer for paddle-ocr；deps 引入决策单独审计）、`**585` = §5.2.5 O3 e2e pytest 刀**（合成扫描 fixture）、`**586+` = §5.2.6 真实 PDF `--confirm-o3=PATH` 用户保留动作刀**（O3 收口必经用户操作）。
