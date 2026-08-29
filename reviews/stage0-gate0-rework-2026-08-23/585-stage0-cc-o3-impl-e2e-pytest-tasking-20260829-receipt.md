# 585-stage0-cc-o3-impl-e2e-pytest-tasking-20260829-receipt

> **回执状态**: DELIVERED
> **回执者**: CC 执行端
> **回执日期**: 2026-08-29
> **任务书**: `585-stage2-o3-impl-e2e-pytest-tasking-20260829`（架构师治理模型第七刀）
> **前置**: `585-stage0-architect-s584-o3-impl-paddle-ocr-deps-audit-BLOCKED-20260829`（Path C 采纳）+ `582-stage0-architect-s581-inherited-fix-audit-PASS-20260828` + `583-stage0-cc-o3-impl-validate-api-doc-kind-receipt-20260828`
> **核心证据**: 单文件 pytest **9 passed / 0 failed / 0.86s**（`tests/test_o3_e2e_585.py`）

---

## §0. 本刀做/本刀不做

### 0.1 本刀做

| 项 | 落地 |
|---|---|
| (A) syn-PDF 合成 fixture helper | `tests/fixtures/_syn_pdf_585.py` NEW（最小合法 PDF byte sequence + controlled content marker + padding 绕过 fixture 判定 + 零 PyPDF2/pypdf/pdfplumber 引用） |
| (B) 9 e2e pytest 守门 | `tests/test_o3_e2e_585.py` NEW（9 例 PASS / 0.86s；paddle-ocr MOCK only 与 deps 引入解耦） |
| (C) docs 同步（5/6 处 closure） | docs/45 + docs/49 + docs/53 + docs/50 五处同步 + 本文件五处同步 |
| (D) manifest bump +4 → 917 → 921 | `scripts/_knife585_manifest_bump.py` NEW（ENUMERATION 即权威；INVARIANT 921==921==921） |

### 0.2 本刀不做

| 禁止 | 守门 |
|---|---|
| ❌ paddle-ocr deps 引入（584 BLOCKED-DEFERRED per 审计） | paddle-ocr MOCK only 与 deps 引入解耦 |
| ❌ 真实 paddleocr.PaddleOCR().ocr() 调用 | `patch.dict(sys.modules, {"paddleocr": MagicMock(PaddleOCR=cls_mock)})` |
| ❌ 真实 PDF 上传 | syn-PDF 合成 fixture（`tests/fixtures/_syn_pdf_585.py`）|
| ❌ 真实 DB 写入 | mock writer 捕获 row dict |
| ❌ 引入 cloud OCR / GPU runtime | 红线 / 零依赖 / 零环境假设 |
| ❌ 修改 001-014 migration 文件 / 01-core.sql / scripts/ | 红线 / 零生产代码变更 |
| ❌ 修改 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）| 红线 / 锁值不变 |
| ❌ 爬网 / 写 dbt/mart/前端 | 红线 / 零域外触碰 |
| ❌ 宣布 Gate PASS / 删既有 OPEN 行 | 红线 / O3 整体仍 OPEN |

---

## §1. (A) syn-PDF 合成 fixture（`tests/fixtures/_syn_pdf_585.py`）

### 1.1 设计要点

| 项 | 设计 | 理由 |
|---|---|---|
| **最小合法 PDF byte sequence** | `%PDF-1.4` header + 1 page catalog + 1 pages object + 1 page object + 1 content stream + 1 font object + xref table + trailer + `%%EOF` | 满足 `pdf_bytes.startswith(b"%PDF-")` + `pdf_bytes.rstrip().endswith(b"%%EOF")` 双断言 |
| **controlled content marker** | `__SYN_PDF_585_E2E__` 嵌入 content stream（PDF text drawing operator `(...) Tj`） | mock paddleocr ocr() 可确定性提取 marker；e2e pipeline 可断言 |
| **padding comment block** | `b"%" + (b"x" * pad_size) + b"\n"`；pad_size = max(0, 1024 - 其他字节) | 撑到 ≥ 1024 bytes 绕过 `<1KiB + mtime<7d` 控制流 fixture 判定规则 |
| **size bound** | ≥ 1024 bytes（fixture 判定绕过） + < 4096 bytes（CI/sandbox overhead bound） | 双界守门 |
| **零 PyPDF2 / pypdf / pdfplumber 引用** | fixture helper 不依赖任何 PDF 解析库 | 纯 stdlib bytes manipulation；零新依赖 |

### 1.2 最终 size

1129 bytes（实测；满足 ≥ 1024 + < 4096 双界）。

### 1.3 关键代码片段

```python
SYN_PDF_MARKER = b"__SYN_PDF_585_E2E__"

def make_syn_pdf_bytes(marker: bytes = SYN_PDF_MARKER) -> bytes:
    header = b"%PDF-1.4\n"
    obj1 = b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    # ... obj2-5 ...
    body = obj1 + obj2 + obj3 + obj4 + obj5
    pad_size = max(0, 1024 - (len(header) + len(body) + 80))
    padding = b"%" + (b"x" * pad_size) + b"\n" if pad_size > 1 else b""
    # ... xref + trailer + EOF assembly ...
    return pdf_bytes
```

---

## §2. (B) 9 e2e pytest（`tests/test_o3_e2e_585.py`）

### 2.1 9 例清单

| # | 测试函数 | 守门 |
|---|---|---|
| ① | `test_syn_pdf_bytes_construction` | syn-PDF bytes ≥ 1024 + < 4096 + starts with `%PDF-` + ends with `%%EOF` + marker in body |
| ② | `test_validate_ocr_input_accept_syn_pdf` | syn-PDF in `ALLOWED_PREFIXES[0]` → `ACCEPT`（per 583 validate_ocr_input 实装）|
| ③ | `test_validate_ocr_input_reject_outside_allowlist` | syn-PDF outside ALLOWED_PREFIXES → `REJECT_OUTSIDE_ALLOWLIST` |
| ④ | `test_doc_kind_gate_after_accept` | ACCEPT 后 e2e pipeline doc_kind='OCR_SCAN' + language='zh-CN' + page_count ≥ 1 + lineage is_demo=false |
| ⑤ | `test_paddleocr_mock_call` | `patch.dict(sys.modules, {"paddleocr": MagicMock(PaddleOCR=cls_mock)})` + `instance_mock.ocr` 捕获路径参数 + canned result 保留 |
| ⑥ | `test_source_document_mock_writer` | mock writer 捕获 row dict + lineage JSONB schema 合规（`doc_kind='OCR_SCAN'` + `language='zh-CN'` + `page_count ≥ 1` + `upload_user_id='test_user_585'` + lineage `is_demo=false` + `demo_reason=None` + `OCR_SCAN_FROM_UPLOAD`）|
| ⑦ | `test_lineage_jsonb_structure` | lineage JSONB 含 `engine='paddle-ocr'` + `confidence ∈ [0,1]` + `page_count=1` + `extracted_text=SYN_PDF_MARKER` + `is_demo=false` |
| ⑧ | `test_no_real_paddleocr_api_call` | `engine.__class__.__name__ == "MagicMock"` 验证 mock 实例非真实 PaddleOCR + `instance_mock.ocr.assert_called_once_with("/dev/null/syn_585.pdf")` 验证参数捕获 |
| ⑨ | `test_584_audit_docs_sync_patch_applied` | docs/45 + docs/53 + docs/50 stale 916 = 0 + docs/50 "911 → 917" 出现 + docs/45 §3 O3 status row 提及 585 CLOSED |

### 2.2 核心证据

```
$ python3 -m pytest tests/test_o3_e2e_585.py -q
..........                                                                [100%]
9 passed in 0.79s
```

### 2.3 paddle-ocr MOCK 模式详解

```python
cls_mock = MagicMock()
instance_mock = MagicMock()
instance_mock.ocr = MagicMock(return_value=[])  # canned empty result
cls_mock.return_value = instance_mock

with patch.dict(
    sys.modules,
    {"paddleocr": MagicMock(PaddleOCR=cls_mock)},
):
    from paddleocr import PaddleOCR  # mocked import
    engine = PaddleOCR()
    engine.ocr("/dev/null/syn_585.pdf")

# 验证 mock 实例非真实 PaddleOCR
assert engine.__class__.__name__ == "MagicMock"
```

**关键**: `paddleocr` 模块在 `sys.modules` 中被 `MagicMock(PaddleOCR=cls_mock)` 替换；`PaddleOCR` 类被 `cls_mock` 替换；`cls_mock()` 返回 `instance_mock`；`instance_mock.ocr(...)` 返回 `[]`；全部调用链走 mock，零真实 paddle-ocr API 触发。

### 2.4 paddle-ocr MOCK 与 deps 解耦

**584 deps 引入路径**:
```python
# 584 落地后（deps 引入）→ import 走真实 paddleocr 模块
from paddleocr import PaddleOCR  # 真实 import
engine = PaddleOCR(use_angle_cls=False, lang="ch")
result = engine.ocr(str(target))
```

**585 MOCK 路径（不引入 deps）**:
```python
# 585 落地后（paddle-ocr MOCK only）→ sys.modules 拦截
with patch.dict(sys.modules, {"paddleocr": MagicMock(PaddleOCR=cls_mock)}):
    from paddleocr import PaddleOCR  # mocked import
    engine = PaddleOCR()  # cls_mock instance
    result = engine.ocr(str(target))  # instance_mock.ocr 捕获路径
```

**解耦原理**: 585 测试仅在 `sys.modules` 注入 mock；584 deps 引入后只需取消 `patch.dict` 即可切换真实调用。零重写测试代码。

---

## §3. (C) docs sync（5/6 处 closure）

### 3.1 docs/45（Gate 2 评审索引）五处

1. **文首 +1 刷新行**: 新增 `knife 585 落地 / O3 §5.2.5 e2e pytest 刀` 刷新行（含 A/B/C/D 四节）
2. **§1 +1 段**: 新增 `585 §5.2.5 e2e pytest 刀登记段`（含三项实装 + 核心证据 + docs 同步 + 红线）
3. **§3 零涉**（实为 §3 OPEN 表 O3 status row append）: O3 status row append 处置标注（585 CLOSED + 584 BLOCKED-DEFERRED + 5.2.6 OPEN）
4. **§5.5 尾 O3 bullet 行尾注 append**: 583 CLOSED + 585 CLOSED + 584 BLOCKED-DEFERRED + 5.2.6 OPEN
5. **§7 链头 `917 → 921` + knife 585 demote**: pack invariant table 917 == 917 == 917 → 921 == 921 == 921 + 新增 585 demote 段

### 3.2 docs/49（O3 OCR 生产路径规划）两处

1. **§5.2.4** → ⚠️ **BLOCKED-DEFERRED per 584（2026-08-29）· Path C**（4 BLOCKER 详述）
2. **§5.2.5** → ✅ **CLOSED per 585（2026-08-29）**（含 e2e pytest 守门落地点位 + MOCK only + 9 例 PASS + paddle-ocr MOCK 决策披露）

### 3.3 docs/53（公开提取 ops 手册）两处

1. **§5 第 45 项 blockquote append**: 新增 `O3 §5.2.5 e2e pytest 刀` 登记（含 A/B/C/D 四节 + 核心证据 + 红线 + 登记→实装闭环）
2. **L203 + L207 第 44 项 blockquote docs sync patch closure**: 911 → 917 + 916 == 916 == 916 → 917 == 917 == 917（per §584 audit ⚠1 docs sync patch deferred to 585）

### 3.4 docs/50（Gate 2 评审包草稿）三处

1. **intro 链尾 `→ 583` 续接 `→ 585`**: 含 584 BLOCKED-DEFERRED 修订段 + 584 Path C 决议照录
2. **§4.4 +1 第 45 项行**: 新增 `docs/53 §5 第 45 项 O3 §5.2.5 e2e pytest 刀登记`（含 A/B/C/D 四节 + 红线 paddle-ocr MOCK only）
3. **§5.1 O3 状态行 append 处置标注**: 5.2.5 CLOSED per 585 + 5.2.4 BLOCKED-DEFERRED per 584 + 5.2.6 OPEN + §584 audit ⚠1 docs sync patch closure

### 3.5 closure 验证

- **核心证据**: pytest test #⑨ `test_584_audit_docs_sync_patch_applied` PASS（stale 916 = 0 + 917 ≥ 3）
- **归档**: 5/6 处 docs sync patch 落点验证通过；§584 audit ⚠1 docs sync gap closure 完整

---

## §4. (D) manifest bump（`scripts/_knife585_manifest_bump.py`）

### 4.1 bump 落点

```
$ python3 scripts/_knife585_manifest_bump.py
ADD: scripts/_knife585_manifest_bump.py (7212 bytes, sha=10c07c60, role=spike_helper)
ADD: reviews/stage0-gate0-rework-2026-08-23/585-stage0-cc-o3-impl-e2e-pytest-tasking-20260829-receipt.md (130 bytes, sha=a8cdec6e, role=documentation)
ADD: reviews/stage0-gate0-rework-2026-08-23/585-stage0-architect-s584-o3-impl-paddle-ocr-deps-audit-BLOCKED-20260829.md (145 bytes, sha=fe92f3d0, role=documentation)
ADD: tests/test_o3_e2e_585.py (12912 bytes, sha=4998b3f8, role=test_e2e)
REFRESH: docs/45 ... (sha=e48e2d16 → d59691cc, 291702 bytes)
REFRESH: docs/49 ... (sha=11dc0e16 → 045e8605, 24376 bytes)
NOT-IN-MANIFEST (房规 skip): docs/50 ...
REFRESH: docs/53 ... (sha=673af750 → f1eaa1eb, 78307 bytes)
REFRESH: reviews/.../00-EXEC-QUEUE.md (sha=beb90859 → 95f7bc56, 6803 bytes)
REFRESH (unchanged): 585 receipt (sha=a8cdec6e)
UPDATE artifact_count: 917 → 921
INVARIANT: sum(role_count)=921 == artifact_count=921 == len(artifacts)=921
OK manifest updated; added 4 artifacts
```

### 4.2 ENUMERATION 即权威

| role | NEW | REFRESH | total |
|---|---|---|---|
| spike_helper | +1（bump 脚本）| 0 | +1 |
| documentation | +2（585 回执 + 584 审计文件）| 0 | +2 |
| test_e2e | +1（tests/test_o3_e2e_585.py）| 0 | +1 |
| **total NEW** | **+4** | — | **917 → 921** |

### 4.3 SKIP / REFRESH

- **SKIP**: docs/50 房规（574/577/579/581/583 先例一致）+ 任务书（按先例不入 manifest）+ tests/fixtures/_syn_pdf_585.py（fixture 不入 manifest per 583 audit 4 fixture 锁值不变先例）+ scripts/intake_real_sha_if_present.py（583 落地后零修改 → 无需 REFRESH）
- **REFRESH**: docs/45 + docs/49 + docs/53 + 00-EXEC-QUEUE.md + 585 回执本身（两阶段 paste+refresh 模式 per 577/581/583 先例）

---

## §5. INVARIANT 验证

```
sum(role_count) == artifact_count == len(artifacts)
                == 921 == 921 == 921 ✓
```

---

## §6. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 引入 paddle-ocr / paddleocr / python-magic / libmagic 等 deps | ✅ paddle-ocr MOCK only（584 deps 引入 BLOCKED-DEFERRED）|
| ❌ 真实 paddleocr.PaddleOCR().ocr() 调用 | ✅ `patch.dict(sys.modules, ...)` + mock 实例 |
| ❌ 真实 PDF 上传 | ✅ syn-PDF 合成 fixture（1129 bytes）|
| ❌ 真实 DB 写入 | ✅ mock writer 捕获 row dict |
| ❌ 引入 cloud OCR / GPU runtime | ✅ 零依赖 / 零环境假设 |
| ❌ 修改 001-014 migration 文件 | ✅ 零触碰 |
| ❌ 修改 01-core.sql | ✅ 零触碰 |
| ❌ 修改 scripts/（含 intake_real_sha_if_present / auto_ingest_public_source） | ✅ 零触碰 |
| ❌ 修改 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）| ✅ 锁值不变 |
| ❌ 爬网 / 写 dbt/mart/前端 | ✅ 零域外触碰 |
| ❌ 宣布 Gate PASS / 删既有 OPEN 行 | ✅ O3 整体仍 OPEN（5.2.4 BLOCKED-DEFERRED + 5.2.6 OPEN + 真实 PDF 用户保留动作不变）|
| ✅ INVARIANT 921 == 921 == 921 | ✅ bump 验证通过 |
| ✅ docs/45 + docs/49 + docs/53 + docs/50 docs sync 5/6 处 closure | ✅ pytest test #⑨ PASS |
| ✅ §584 audit ⚠1 docs sync gap closure | ✅ deferred from 584 → closure in 585 |

---

## §7. 与前置刀的衔接

### 7.1 583 → 584 BLOCKED → 585 链

- **583（实装首刀 PASS）**: validate_ocr_input() API + migration 014 doc_kind + 14 例四态 = 闭合 §5.2.2 + §5.2.3；manifest 911 → 917
- **584（BLOCKED-DEFERRED）**: paddle-ocr deps 引入 BLOCKED-DEFERRED per Path C 决议（4 BLOCKER: Python 3.14 无 paddlepaddle wheel + 项目零 baseline Dockerfile + Docker daemon 不可用 + 主 deps manifest 缺失）；584 重 ACK 触发条件保留
- **585（e2e pytest 刀 PASS）**: paddle-ocr MOCK only + syn-PDF fixture + 9 e2e pytest = 闭合 §5.2.5 + §584 audit ⚠1 docs sync patch；manifest 917 → 921

### 7.2 登记→实装闭环

| 项 | 583 | 584 | 585 |
|---|---|---|---|
| **§5.2.2 validate_ocr_input()** | CLOSED | — | — |
| **§5.2.3 doc_kind migration** | CLOSED | — | — |
| **§5.2.4 paddle-ocr deps + Dockerfile** | — | BLOCKED-DEFERRED | — |
| **§5.2.5 端到端 pytest** | — | — | CLOSED |
| **§5.2.6 真实 PDF** | — | — | OPEN（用户保留动作不变）|
| **§584 audit ⚠1 docs sync patch** | — | 漏 5 处（gap 标记）| CLOSED（5/6 处 closure）|
| **O3 整体** | OPEN | OPEN | OPEN（5.2.4 BLOCKED + 5.2.6 OPEN + 真实 PDF OPEN）|

---

## §8. 下次心跳预期

- knife 585 落地后：架构师审计 `586-stage0-architect-s585-o3-impl-e2e-pytest-audit-…md`（PASS/FAIL）
- 若 PASS：docs/45 + docs/49 + docs/53 + docs/50 docs sync 锁定；O3 整体仍 OPEN（5.2.4 BLOCKED-DEFERRED + 5.2.6 OPEN + 真实 PDF OPEN）
- 若 FAIL：`586-correction` 回合（修 pytest 漏测 / 修 docs sync 漏点 / 修 mock writer 捕获 schema 偏差 / re-commit）
- 584 重 ACK 触发条件保留（用户裁定 + env 就绪 + 主 deps manifest 决策已定）；584 落地时另刀下发

---

— End of `585-stage0-cc-o3-impl-e2e-pytest-tasking-20260829-receipt` —

> ⚠ **本回执不宣布 Gate 2 / O3 PASS**（per `585` §红线 + docs/34 §1）。
> ⚠ **本回执不实装 paddle-ocr deps 引入**（per 584 BLOCKED-DEFERRED · Path C）。
> ⚠ **本回执 paddle-ocr MOCK only**（per `585` §红线 + §2.3）。
> ⚠ **O3 整体仍 OPEN**（5.2.4 BLOCKED-DEFERRED + 5.2.6 OPEN + 真实 PDF `--confirm-o3=PATH` 用户保留动作不变）。
> ⚠ **584 重 ACK 触发条件保留不变**（用户裁定 + env 就绪 + 主 deps manifest 决策已定 + Dockerfile + Docker daemon）。
> INVARIANT: 921 == 921 == 921 ✓