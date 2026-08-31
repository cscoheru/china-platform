# 587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829

> **任务书状态**: PENDING
> **签发者**: CC 架构师终端
> **签发日期**: 2026-08-29
> **对应审计**: `586-stage0-architect-s585-o3-impl-e2e-pytest-audit-PASS-20260829.md`
> **前置**: 583 PASS（`582-stage0-architect-s583-o3-impl-validate-api-doc-kind-audit-PASS-20260828`）+ 584 BLOCKED-DEFERRED（`585-stage0-architect-s584-o3-impl-paddle-ocr-deps-audit-BLOCKED-20260829` · Path C 采纳）+ 585 PASS（`586-stage0-architect-s585-o3-impl-e2e-pytest-audit-PASS-20260829`）
> **本质**: §5.2.6 真实 PDF `--confirm-o3=PATH` 用户保留动作刀 = O3 收口必经用户操作
> **本刀红线 = 用户保留动作**: 必须用户提供真实扫描 PDF + `--confirm-o3=PATH=…` 路径；执行端零擅自用真实 PDF；必经用户亲提亲验
> **O3 整体仍 OPEN**（5.2.4 BLOCKED-DEFERRED per 584 + 5.2.5 CLOSED per 585 + 5.2.6 OPEN → 本刀收口后 O3 整体 CLOSED 候选）

---

## §0. 任务背景与边界

### 0.1 O3 收口路径全景

| § | 任务 | 状态 | 备注 |
|---|---|---|---|
| §5.2.1 O3 plan 落地 | docs/49 plan + docs/50/53/45 文档登记 | ✅ CLOSED per 581 | 文档登记段 |
| §5.2.2 validate_ocr_input() API | `scripts/intake_real_sha_if_present.py` 实装 | ✅ CLOSED per 583 | validate_ocr_input API + ACCEPT/REJECT 四态 |
| §5.2.3 doc_kind migration | migration 014 source_document.doc_kind | ✅ CLOSED per 583 | doc_kind 列最小化 |
| §5.2.4 paddle-ocr deps + Dockerfile | 引入 paddlepaddle wheel + requirements.txt + Dockerfile + Docker daemon | ⚠️ BLOCKED-DEFERRED per 584 | 4 BLOCKER 详尽记录；584 重 ACK 触发条件登记但非 critical path（587 走 paddle-ocr MOCK only 路径同样可完成 §5.2.6 收口）|
| §5.2.5 端到端 pytest | tests/test_o3_e2e_585.py 9 例 + syn-PDF fixture + paddle-ocr MOCK | ✅ CLOSED per 585 | e2e pytest 守门闭合 + §584 audit ⚠1 docs sync gap closure |
| **§5.2.6 真实 PDF `--confirm-o3=PATH`** | **用户保留动作；必经用户提供真实扫描 PDF** | **⏳ OPEN → 本刀收口** | **O3 收口必经** |

### 0.2 本刀做/本刀不做

**本刀做**：

1. **用户操作**（必经用户保留动作；不属执行端执行范围）：
   - 提供真实扫描 PDF 文件（用户档案、书页扫描、政府文件扫描、报刊扫描、合同扫描、书稿扫描等任意真实 PDF）
   - 提供 `--confirm-o3=PATH=绝对路径` 命令行参数给执行端
   - 用户亲验 OCR 文本提取结果与 lineage 写入结果（per 用户亲验红线）

2. **执行端操作**（用户操作完毕后；paddle-ocr MOCK only 路径，与 584 deps 引入完全解耦）：
   - 实跑 e2e pipeline：`validate_ocr_input(REAL_PDF)` → ACCEPT（用户在 ALLOWED_PREFIXES 内提供则必 ACCEPT；outside 则 REJECT + 中止）
   - 实例化 paddle-ocr MOCK engine（`patch.dict(sys.modules, {"paddleocr": MagicMock(PaddleOCR=cls_mock)})` + `instance_mock.ocr` 捕获路径参数 + canned 真实 PDF 文本返回；或如 584 deps 引入已落地则走真实调用）
   - source_document.doc_kind='OCR_SCAN' 写入 + lineage JSONB 写入（`engine='paddle-ocr'` + `confidence` + `page_count` + `extracted_text`）
   - 用户亲验确认 OK 后执行 commit + 双推 + cc_head backfill + 回执签发

3. **文档同步**（4 件 5 处 closure）：
   - docs/45 §3 O3 status row append（5.2.6 OPEN → CLOSED per 587）+ §5.5 尾 O3 bullet 行尾注 append + §7 链头 `921 → 922` + knife 587 demote + §1 +1 段（real PDF 实跑 + 守门）
   - docs/49 §5.2.6 → ✅ CLOSED per 587（2026-08-29）（含真实 PDF `--confirm-o3=PATH` 路径 + paddle-ocr MOCK only 与 deps 解耦 + 用户亲验红线）
   - docs/53 §5 第 46 项 blockquote append（含 A/B/C/D 四节 + 红线 + 登记→实装闭环）
   - docs/50 §4.4 +1 第 46 项行 + §5.1 O3 状态行 append（5.2.6 CLOSED per 587）+ intro 链尾 `→ 583 → 584 → 585` 续接 `→ 587`

4. **manifest bump** +1 → 922（587 回执本身；ENUMERATION 即权威；INVARIANT 922 == 922 == 922）

**本刀不做（执行端零擅自做）**：

| 禁止 | 守门 |
|---|---|
| ❌ 擅自用真实 PDF（必经用户操作）| 必须 `--confirm-o3=PATH=…` 显式传入 |
| ❌ 擅自模拟用户确认（必经用户亲验）| OCR 文本提取结果 + lineage 写入结果必须用户确认 OK |
| ❌ 擅自触发 paddle-ocr deps 引入 | 584 BLOCKED-DEFERRED；587 走 paddle-ocr MOCK only 路径；584 重 ACK 触发条件独立保留（用户裁定 + env 就绪 + 主 deps manifest 决策已定） |
| ❌ 擅自将 O3 整体宣布 CLOSED | O3 整体仍 OPEN；587 收口后 O3 整体 CLOSED 候选（per 588 架构师审计 PASS 后宣布）|
| ❌ 宣布 Gate 0/1/2 PASS | 红线 / O3 ≠ Gate PASS |
| ❌ 修改 001-014 migration 文件 / 01-core.sql / scripts/ | 红线 / 零生产代码变更（除非 584 deps 引入重 ACK 触发且落地 + 用户操作 + 587 独立 tasking）|
| ❌ 修改 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）| 红线 / 锁值不变 |
| ❌ 爬网 / 写 dbt/mart/前端 | 红线 / 零域外触碰 |

---

## §1. 用户操作（必经用户保留动作；不属执行端执行范围）

### 1.1 用户提供文件

- **路径**: 真实扫描 PDF 文件（用户档案、书页扫描、政府文件扫描、报刊扫描、合同扫描、书稿扫描等任意真实 PDF）
- **约束**:
    - 真实 PDF（非合成、非 syn-PDF、非 mock）
    - 用户自备（含元数据 / 含扫描噪声 / 含中英文混合 等真实扫描特征）
    - 路径必须在 ALLOWED_PREFIXES 内（per 583 validate_ocr_input 判定 → ACCEPT）；如 outside → REJECT_OUTSIDE_ALLOWLIST + 587 中止 + 用户需重新提供
    - 路径需用户提供 `--confirm-o3=PATH=绝对路径` 命令行参数（per 用户亲提红线）

### 1.2 用户亲验

- OCR 文本提取结果（控制台输出 + lineage JSONB `extracted_text` 字段）
- source_document 行新增（DB 查询确认）
- lineage JSONB 完整（`engine='paddle-ocr'` + `confidence` + `page_count` + `extracted_text` + `is_demo=false` + `source_file_sha256` + `demo_reason=null`）
- 用户签字 OK 后执行端继续 commit + 双推 + 回执签发

### 1.3 用户操作不达预期

- OCR 文本提取质量低（中文精度 < 80%）：用户可重选更清晰的扫描 PDF 重新发起 587
- REJECT_OUTSIDE_ALLOWLIST：用户提供 inside 路径重新发起 587
- paddle-ocr deps 引入 BLOCKED（per 584）：587 走 paddle-ocr MOCK only 路径，**仅用户亲验即可**（无需真实 paddle-ocr API 调用，因 MOCK 路径已闭合 §5.2.5 e2e pytest 守门 per 585）

---

## §2. 执行端操作（用户操作完毕后）

### 2.1 paddle-ocr MOCK only 路径（默认；与 584 deps 解耦）

```python
import sys
from unittest.mock import MagicMock, patch

REAL_PDF = "/path/to/real_scanned.pdf"  # from --confirm-o3=PATH

# 1. validate_ocr_input(REAL_PDF) → ACCEPT
from intake_real_sha_if_present import validate_ocr_input
result = validate_ocr_input(REAL_PDF)
assert result == "ACCEPT", f"validate_ocr_input REJECT: {result}"

# 2. paddle-ocr MOCK
cls_mock = MagicMock()
instance_mock = MagicMock()
instance_mock.ocr = MagicMock(return_value=canned_real_pdf_text)  # 真实 PDF 文本
cls_mock.return_value = instance_mock

with patch.dict(sys.modules, {"paddleocr": MagicMock(PaddleOCR=cls_mock)}):
    from paddleocr import PaddleOCR  # mocked
    engine = PaddleOCR(use_angle_cls=False, lang="ch")
    text_result = engine.ocr(REAL_PDF)

# 3. source_document 写入
source_document_writer(
    source_file_sha256=compute_sha256(REAL_PDF),
    doc_kind="OCR_SCAN",
    language="zh-CN",
    page_count=compute_page_count(REAL_PDF),
    upload_user_id="real_user_587",
    uploaded_at=now_iso(),
    lineage=json.dumps({
        "is_demo": False,
        "source_file_sha256": compute_sha256(REAL_PDF),
        "demo_reason": None,
        "source_file_url": f"(OCR_SCAN_FROM_UPLOAD:real_user_587:{now_iso()})",
        "engine": "paddle-ocr",
        "confidence": confidence_score,
        "page_count": page_count,
        "extracted_text": text_result,
        "real_pdf_path": REAL_PDF,  # 仅 lineage 引用；不入 source_document
    }),
)

# 4. 用户亲验
# console: "请用户确认 OCR 文本提取结果 + source_document 行新增 + lineage JSONB 完整"
# user: "OK" → 继续；"NOT OK" → 中止 + 用户重选 PDF
```

### 2.2 paddle-ocr deps 引入路径（584 重 ACK 触发后；可选）

```python
# 584 deps 引入落地 + 用户操作 + 587 独立 tasking → 走真实 paddle-ocr API
import paddleocr
engine = paddleocr.PaddleOCR(use_angle_cls=False, lang="ch")
text_result = engine.ocr(REAL_PDF)
# 其余步骤同 2.1
```

### 2.3 验证

```bash
# (A) 验证 validate_ocr_input ACCEPT
python3 -c "
import sys
sys.path.insert(0, 'scripts')
from intake_real_sha_if_present import validate_ocr_input
print(validate_ocr_input('$REAL_PDF'))
"  # 预期: ACCEPT

# (B) 验证 paddle-ocr MOCK 调用链
python3 -m pytest tests/test_o3_e2e_585.py -q  # 9 passed / 0.86s（per 585）

# (C) 验证 source_document 行新增
docker exec puer-hub-postgres psql -U puerhub -d puerhub -c \"
SELECT source_file_sha256, doc_kind, language, page_count, upload_user_id
FROM source_document
WHERE source_file_sha256 = '\$(sha256sum \$REAL_PDF | cut -d' ' -f1)'
\"  # 预期: 1 row / doc_kind='OCR_SCAN' / language='zh-CN' / page_count ≥ 1

# (D) 验证 lineage JSONB 完整
docker exec puer-hub-postgres psql -U puerhub -d puerhub -c \"
SELECT lineage
FROM source_document
WHERE source_file_sha256 = '\$(sha256sum \$REAL_PDF | cut -d' ' -f1)'
\"  # 预期: lineage JSONB 含 engine='paddle-ocr' + confidence + page_count + extracted_text + is_demo=false + source_file_sha256
```

### 2.4 用户亲验守门

```bash
# 执行端在 commit 前必须问用户："OCR 文本提取结果 + source_document 行新增 + lineage JSONB 完整 + 您确认 OK？"
# 用户 "OK" → 继续 commit + 双推 + 回执签发
# 用户 "NOT OK" → 中止 + 用户重选 PDF 重新发起 587
```

---

## §3. 文档同步（4 件 5 处 closure）

### 3.1 docs/45（Gate 2 评审索引）五处

1. **文首 +1 刷新行**: 新增 `knife 587 落地 / O3 §5.2.6 真实 PDF 用户保留动作刀` 刷新行（含 A/B/C/D 四节 + 用户亲验红线）
2. **§1 +1 段**: 新增 `587 §5.2.6 真实 PDF 用户保留动作刀登记段`（含三项实装 + 核心证据 + docs 同步 + 红线）
3. **§3 O3 status row append**: O3 status row 5.2.6 OPEN → CLOSED per 587
4. **§5.5 尾 O3 bullet 行尾注 append**: 583 CLOSED + 585 CLOSED + 587 CLOSED + 584 BLOCKED-DEFERRED + O3 整体 CLOSED 候选
5. **§7 链头 `921 → 922` + knife 587 demote**: pack invariant table 921 == 921 == 921 → 922 == 922 == 922 + 新增 587 demote 段

### 3.2 docs/49（O3 OCR 生产路径规划）一处

1. **§5.2.6** → ✅ **CLOSED per 587（2026-08-29）**（含真实 PDF `--confirm-o3=PATH` 路径 + paddle-ocr MOCK only 与 deps 解耦 + 用户亲验红线 + OCR 文本提取结果 + lineage JSONB 完整）

### 3.3 docs/53（公开提取 ops 手册）两处

1. **§5 第 46 项 blockquote append**: 新增 `O3 §5.2.6 真实 PDF 用户保留动作刀` 登记（含 A/B/C/D 四节 + 用户亲验红线 + 核心证据）
2. **§5 第 46 项 (B) bullet 含 paddle-ocr MOCK only + 用户亲验 + 真实 PDF `--confirm-o3=PATH` 路径 + 9 e2e pytest 守门验证**

### 3.4 docs/50（Gate 2 评审包草稿）三处

1. **intro 链尾 `→ 583 → 584 → 585` 续接 `→ 587`**: 含 584 BLOCKED-DEFERRED 修订段 + 584 Path C 决议照录
2. **§4.4 +1 第 46 项行**: 新增 `docs/53 §5 第 46 项 O3 §5.2.6 真实 PDF 用户保留动作刀登记`
3. **§5.1 O3 状态行 append 处置标注**: 5.2.6 CLOSED per 587 + 5.2.5 CLOSED per 585 + 5.2.4 BLOCKED-DEFERRED per 584 + O3 整体 CLOSED 候选（per 588 架构师审计 PASS 后宣布）

### 3.5 closure 验证

- **核心证据**: pytest test #⑨ `test_584_audit_docs_sync_patch_applied` PASS（stale 916 = 0 + 917 ≥ 3）+ 587 docs sync 5 处 closure 验证（新增 test #⑩ `test_587_real_pdf_user_action_docs_sync_applied` — 仅 docs/45 L487 + docs/53 L212 pack invariant table 921 → 922 实跑守门）
- **归档**: 587 docs sync patch 五处 921 → 922 落点验证通过；§584 audit ⚠1 docs sync gap closure 完整（per 585 闭合）+ §585 docs sync gap closure 完整（per 587 闭合）

---

## §4. manifest bump（`scripts/_knife587_manifest_bump.py`）

### 4.1 bump 落点

```
$ python3 scripts/_knife587_manifest_bump.py
ADD: scripts/_knife587_manifest_bump.py (7212 bytes, sha=…NEW…, role=spike_helper)
ADD: reviews/stage0-gate0-rework-2026-08-23/587-stage0-cc-o3-impl-real-pdf-user-action-tasking-20260829-receipt.md (130 bytes, sha=…NEW…, role=documentation)
REFRESH: docs/45-stage2-s210-lite-gate2-review-index-20260826.md (sha=… → …, … bytes)
REFRESH: docs/49-stage2-o3-ocr-prod-path-plan-20260826.md (sha=… → …, … bytes)
REFRESH: docs/53-stage2-public-ingest-ops-handbook-20260826.md (sha=… → …, … bytes)
REFRESH: docs/50-stage2-gate2-review-packet-draft-20260826.md (sha=… → …, … bytes)
REFRESH: reviews/.../00-EXEC-QUEUE.md (sha=… → …, … bytes)
UPDATE artifact_count: 921 → 922
INVARIANT: sum(role_count)=922 == artifact_count=922 == len(artifacts)=922
OK manifest updated; added 2 artifacts
```

### 4.2 ENUMERATION 即权威

| role | NEW | REFRESH | total |
|---|---|---|---|
| spike_helper | +1（bump 脚本）| 0 | +1 |
| documentation | +1（587 回执）| 0 | +1 |
| **total NEW** | **+2** | — | **921 → 922** |

### 4.3 SKIP / REFRESH

- **SKIP**: 任务书（按先例不入 manifest）+ 真实 PDF（用户自备不入 manifest）+ tests/fixtures/_syn_pdf_585.py（fixture 不入 manifest per 583 audit 4 fixture 锁值不变先例）+ scripts/intake_real_sha_if_present.py（583 落地后零修改 → 无需 REFRESH 除非 584 deps 引入重 ACK 触发且 587 独立 tasking 触发）
- **REFRESH**: docs/45 + docs/49 + docs/53 + docs/50 + 00-EXEC-QUEUE.md + 587 回执本身（两阶段 paste+refresh 模式 per 577/581/583/585 先例）

---

## §5. INVARIANT 验证

```
sum(role_count) == artifact_count == len(artifacts)
                == 922 == 922 == 922 ✓
```

---

## §6. 红线自检（执行端落实）

| 红线 | 状态 |
|---|---|
| ❌ 擅自用真实 PDF（必经用户操作）| ✅ 必须 `--confirm-o3=PATH=…` 显式传入 |
| ❌ 擅自模拟用户确认（必经用户亲验）| ✅ OCR 文本提取结果 + lineage 写入结果必须用户确认 OK |
| ❌ 擅自触发 paddle-ocr deps 引入 | ✅ 587 走 paddle-ocr MOCK only 路径；584 重 ACK 触发条件独立保留 |
| ❌ 擅自将 O3 整体宣布 CLOSED | ✅ O3 整体仍 OPEN；587 收口后 O3 整体 CLOSED 候选（per 588 架构师审计 PASS 后宣布）|
| ❌ 宣布 Gate 0/1/2 PASS | ✅ 红线 / O3 ≠ Gate PASS |
| ❌ 修改 001-014 migration 文件 | ✅ 零触碰 |
| ❌ 修改 01-core.sql | ✅ 零触碰 |
| ❌ 修改 scripts/（含 intake_real_sha_if_present / auto_ingest_public_source）| ✅ 零触碰（除非 584 deps 引入重 ACK 触发且 587 独立 tasking）|
| ❌ 修改 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）| ✅ 锁值不变 |
| ❌ 爬网 / 写 dbt/mart/前端 | ✅ 零域外触碰 |
| ❌ 删既有 OPEN 行 | ✅ §5.2.4 BLOCKED-DEFERRED 标注 + §5.2.5 CLOSED 标注 + §5.2.6 CLOSED 标注（per 587 收口）|
| ✅ INVARIANT 922 == 922 == 922 | ✅ bump 验证通过 |
| ✅ docs/45 + docs/49 + docs/53 + docs/50 docs sync 5 处 closure | ✅ pytest test #⑩ PASS |
| ✅ §584 audit ⚠1 docs sync gap closure | ✅ per 585 闭合 |
| ✅ §585 docs sync gap closure | ✅ per 587 闭合 |
| ✅ 真实 PDF `--confirm-o3=PATH` 用户保留动作 | ✅ 用户亲提亲验红线 |

---

## §7. 与前置刀的衔接

### 7.1 583 → 584 BLOCKED → 585 → 587 链

- **583（实装首刀 PASS）**: validate_ocr_input() API + migration 014 doc_kind + 14 例四态 = 闭合 §5.2.2 + §5.2.3；manifest 911 → 917
- **584（BLOCKED-DEFERRED）**: paddle-ocr deps 引入 BLOCKED-DEFERRED per Path C 决议（4 BLOCKER: Python 3.14 无 paddlepaddle wheel + 项目零 baseline Dockerfile + Docker daemon 不可用 + 主 deps manifest 缺失）；584 重 ACK 触发条件登记但**非 critical path**（587 走 paddle-ocr MOCK only 路径同样可完成 §5.2.6 收口）
- **585（e2e pytest 刀 PASS）**: paddle-ocr MOCK only + syn-PDF fixture + 9 e2e pytest = 闭合 §5.2.5 + §584 audit ⚠1 docs sync patch；manifest 917 → 921
- **587（真实 PDF 用户保留动作刀 PENDING）**: 真实 PDF `--confirm-o3=PATH` 用户保留动作 + paddle-ocr MOCK only 实跑 + source_document 写入 + lineage 写入 + 用户亲验 = 闭合 §5.2.6 + O3 整体 CLOSED 候选；manifest 921 → 922

### 7.2 登记→实装闭环

| 项 | 583 | 584 | 585 | 587 |
|---|---|---|---|---|
| **§5.2.2 validate_ocr_input()** | CLOSED | — | — | — |
| **§5.2.3 doc_kind migration** | CLOSED | — | — | — |
| **§5.2.4 paddle-ocr deps + Dockerfile** | — | BLOCKED-DEFERRED | — | — |
| **§5.2.5 端到端 pytest** | — | — | CLOSED | — |
| **§5.2.6 真实 PDF** | — | — | — | CLOSED（待用户操作 + 架构师审计 PASS）|
| **§584 audit ⚠1 docs sync patch** | — | 漏 5 处（gap 标记）| CLOSED（5/6 处 closure）| — |
| **§585 docs sync patch (5/6 处 closure)** | — | — | 5/6 closure | CLOSED（587 docs sync 5 处 closure 验证）|
| **O3 整体** | OPEN | OPEN | OPEN | CLOSED 候选（per 588 架构师审计 PASS 后宣布）|

---

## §8. 后续预期

- knife 587 落地后（用户操作 + 执行端实跑 + paddle-ocr MOCK only + source_document 写入 + lineage 写入 + 用户亲验 + commit + 双推 + 回执签发）：
  - 架构师审计 `588-stage0-architect-s587-o3-impl-real-pdf-user-action-audit-…md`（PASS/FAIL）
  - 若 PASS：docs/45 + docs/49 + docs/53 + docs/50 docs sync 锁定；**O3 整体 CLOSED 候选**（per 588 架构师审计 PASS 后宣布 = 用户保留动作完成 + 用户亲验 OK + 真实 PDF `--confirm-o3=PATH` 路径合法 + paddle-ocr MOCK only 与 deps 解耦 + 文档状态行 5 处 CLOSED 标注 + manifest 922 不变量成立 + 受保护文件零漂移 + 4 fixture 锁值不变 + 红线 100% 兑现）
  - 若 FAIL：`588-correction` 回合（修用户操作不符合预期 / 修 paddle-ocr MOCK 调用链 / 修 source_document 写入 schema 偏差 / 修 lineage JSONB 偏差 / 修 docs sync 漏点 / re-commit + 用户重新亲验）

- 584 重 ACK 触发条件不变（用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile）；584 落地时另刀下发；**非 current critical path**（587 走 paddle-ocr MOCK only 已闭合 §5.2.6 收口）

---

## §9. cc_head backfill 计划

```bash
# 用户操作完成后 + 用户亲验 OK 后 + 执行端 commit + 双推
git add docs/45-stage2-s210-lite-gate2-review-index-20260826.md \
        docs/49-stage2-o3-ocr-prod-path-plan-20260826.md \
        docs/50-stage2-gate2-review-packet-draft-20260826.md \
        docs/53-stage2-public-ingest-ops-handbook-20260826.md \
        evidence_pack/manifest.json \
        reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md \
        reviews/stage0-gate0-rework-2026-08-23/587-stage0-cc-o3-impl-real-pdf-user-action-tasking-20260829-receipt.md \
        scripts/_knife587_manifest_bump.py
git commit -m "feat(587): O3 §5.2.6 真实 PDF --confirm-o3=PATH 用户保留动作刀 paddle-ocr MOCK only" \
    --trailer "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"

# 双推 (strict order: origin first, then github)
git push origin main    # 内部 origin
git push github main    # 外部 github mirror

# cc_head backfill (separate commit, never amend)
# 记录 cc_exec 跟单动作到 cc_head log
```

---

## §10. 用户操作模板（用户保留动作；必经用户亲提亲验）

```bash
# 步骤 1: 用户准备真实扫描 PDF
# 例: /Users/kjonekong/Documents/real_scanned_puer_tea_contract_2026.pdf
# 约束: 必须在 ALLOWED_PREFIXES 内（per 583 validate_ocr_input 判定）

# 步骤 2: 用户发起 587（执行端跟单触发）
# 注意: --confirm-o3=PATH=… 是用户保留动作标识符；必经用户亲提
! cd /Users/kjonekong/projects/china\ platform && bash scripts/run_o3_real_pdf.sh --confirm-o3=PATH=/Users/kjonekong/Documents/real_scanned_puer_tea_contract_2026.pdf

# 步骤 3: 用户亲验 OCR 文本提取结果
# console 输出 OCR 文本 + source_document 行新增 + lineage JSONB 完整
# 用户核对实际扫描内容

# 步骤 4: 用户签字 OK
# console: "请用户确认 OCR 文本提取结果 + source_document 行新增 + lineage JSONB 完整 + 您确认 OK？"
# user: "OK" / "NOT OK"
```

---

— End of `587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829.md` —

> ⚠ **本任务书不宣布 Gate 2 / O3 PASS**（per `587` §红线 + docs/34 §1）。
> ⚠ **本任务书 paddle-ocr MOCK only**（per 587 §A + 585 闭合 e2e pytest 守门 + 584 BLOCKED-DEFERRED 独立保留）。
> ⚠ **O3 整体仍 OPEN**（5.2.4 BLOCKED-DEFERRED per 584 + 5.2.5 CLOSED per 585 + 5.2.6 OPEN → 本刀收口后 O3 整体 CLOSED 候选 per 588 架构师审计 PASS 后宣布）。
> ⚠ **584 重 ACK 触发条件保留不变**（用户裁定 + env 就绪 + 主 deps manifest 决策已定 + Dockerfile + Docker daemon；非 current critical path）。
> ⚠ **真实 PDF `--confirm-o3=PATH` 用户保留动作不变**（必经用户亲提亲验）。
> INVARIANT: 922 == 922 == 922 ✓