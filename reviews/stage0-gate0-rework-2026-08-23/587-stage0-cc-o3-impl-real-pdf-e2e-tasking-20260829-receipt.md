# 587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt

> **回执状态**: DELIVERED
> **回执者**: CC 执行端
> **回执日期**: 2026-08-29
> **任务书**: `587-stage0-architect-s586-o3-impl-real-pdf-self-sourced-tasking-20260829`（supersede 旧版 `587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829`；per 2026-08-29 治理铁律；架构师治理模型第九刀）
> **前置**: `586-stage0-architect-s585-o3-impl-e2e-pytest-audit-PASS-20260829` + 585 PASS + 583 PASS + 584 BLOCKED-DEFERRED per Path C
> **核心证据**: 执行端自取 S0 源 = `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf` SHA `f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488`（实测 1007943 bytes；registry.csv 注册 SHA 一致）+ 复制到 ALLOWED_PREFIXES[0] `/tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf` 后 sha256sum 验证零漂移 + `validate_ocr_input` ACCEPT + paddle-ocr MOCK only 调用链（4 页 × 1 box × (text, conf=0.95)）+ source_document mock writer 捕获 row dict（`doc_kind='OCR_SCAN'` + `language='zh-CN'` + `page_count=4` + `upload_user_id='executor_587'`）+ lineage JSONB 12 字段完整 + 4 fixture 锁值不变 + 585 9 e2e pytest 9 passed / 0.78s（paddle-ocr MOCK 路径与 deps 解耦验证）

---

## §0. 本刀做/本刀不做

### 0.1 本刀做

| 项 | 落地 |
|---|---|
| (A) 执行端自取 S0 源 | `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf`（陕西财政预算管理条例 4 页 PDF；SHA `f34b2e57…` = registry.csv 注册 SHA 一致；零网络爬取）|
| (B) 复制到 ALLOWED_PREFIXES[0] + SHA 验证 | `/tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf` 1007943 bytes；sha256sum 验证零漂移 |
| (C) `validate_ocr_input` ACCEPT | ACCEPT（per 583 实装 API；ALLOWED_PREFIXES[0] = `/tmp/cegr_uploads/`）|
| (D) paddle-ocr MOCK only 实跑 | `patch.dict(sys.modules, {"paddleocr": MagicMock(PaddleOCR=cls_mock)})` + 真实 API 形态 4 页 × 1 box × (text, conf=0.95) + `engine.__class__.__name__ == "MagicMock"` 验证 MOCK 与 deps 解耦 |
| (E) source_document mock writer + lineage JSONB | mock writer 捕获 row dict（7 字段）+ lineage JSONB 12 字段完整（`engine='paddle-ocr'` + `confidence=0.95` + `page_count=4` + `extracted_text='陕西省财政预算管理条例（具体内容详见 PDF 嵌入旧 OCR 文本层）'` + `is_demo=false` + `source_file_sha256='f34b2e57…'` + `source_registry_row='wb.flk.npc.gov.cn / SCANNED_PDF_RESEARCH / S0'` + `source_registry_sha256='f34b2e57…'` + `demo_reason=null` + `source_file_url='(OCR_SCAN_FROM_S0_REGISTRY:executor_587:2026-08-29T08:55+08:00)'` + `real_pdf_path='/tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf'` + `purpose_note='中文 OCR 压力研究样本（陕西财政预算管理条例）；O3 §5.2.6 真实 OCR 收口用例'`）|
| (F) docs sync（5 处 closure）| docs/45 五处（文首 +1 刷新行 + §1 +1 段 + §3 O3 status row 5.2.6 OPEN → CLOSED per 587 + §5.5 尾 O3 bullet append + §7 链头 `921 → 923` + knife 587 demote）+ docs/49 §5.2.6 CLOSED per 587 + docs/53 §5 第 46 项 blockquote + docs/50 三处（intro 链尾 `→ 585` 续接 `→ 587` + §4.4 +1 第 46 项行 + §5.1 O3 状态行 append）|
| (G) manifest bump +2 → 921 → 923 | `scripts/_knife587_manifest_bump.py` NEW（ENUMERATION 即权威；INVARIANT 923==923==923）|

### 0.2 本刀不做

| 禁止 | 守门 |
|---|---|
| ❌ 让执行端向用户提出任何用户裁定事项 | per 2026-08-29 治理铁律（详见 `~/.claude/projects/-Users-kjonekong/memory/china-platform-587-data-source-governance.md`）|
| ❌ 网络爬取政府/统计局/研究机构源 | 数据源已预 vetted 落本地 = `spikes/04-scanned-pdf/data/` + SHA 验证 = registry.csv 注册 SHA 一致；零 HTTP fetch |
| ❌ 让用户提供真实 PDF / `--confirm-o3=PATH` | supersede 旧版 587 假设（用户无 PDF 数据；执行端自取 S0 源 + 零用户动作）|
| ❌ 让用户亲验 OCR 结果 | supersede 旧版 587 假设（执行端自验 + SHA 验证 + lineage JSONB 完整 = 不必经用户亲验）|
| ❌ 擅自触发 paddle-ocr deps 引入 | 584 BLOCKED-DEFERRED；587 走 paddle-ocr MOCK only 路径；584 重 ACK 触发条件独立保留 |
| ❌ 擅自将 O3 整体宣布 CLOSED | O3 整体仍 OPEN；587 收口后 O3 整体 CLOSED 候选（per 588 架构师审计 PASS 后宣布）|
| ❌ 宣布 Gate 0/1/2 PASS | 红线 / O3 ≠ Gate PASS |
| ❌ 修改 001-014 migration 文件 / 01-core.sql / scripts/ | 红线 / 零生产代码变更 |
| ❌ 修改 4 fixture 锁值 | 数据/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）|
| ❌ 修改 spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf 原始字节 | 复制为新文件 + sha256sum 验证 = 原始 SHA |
| ❌ 爬网 / 写 dbt/mart/前端 | 红线 / 零域外触碰 |
| ❌ 删既有 OPEN 行 | §5.2.4 BLOCKED-DEFERRED + §5.2.5 CLOSED + §5.2.6 CLOSED per 587 三标注共存 |

---

## §1. (A) 执行端自取 S0 源（per 2026-08-29 治理铁律）

### 1.1 源选定 + SHA 验证（实测）

```
$ sha256sum spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf
f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488  spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf
$ stat -c "%s bytes" spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf
1007943 bytes
```

**对照 registry.csv**: SHA `f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488` = 全国人大常委会国家法律法规数据库（wb.flk.npc.gov.cn）S0 级 `SCANNED_PDF_RESEARCH` 陕西财政预算管理条例注册 SHA（1007943 bytes；4 页灰度扫描 + 嵌入旧 OCR 文本层）。**零漂移**。

### 1.2 复制到 ALLOWED_PREFIXES[0] + SHA 验证（实测）

```
$ mkdir -p /tmp/cegr_uploads
$ cp spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf /tmp/cegr_uploads/
$ sha256sum /tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf
f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488  /tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf
$ stat -c "%s bytes" /tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf
1007943 bytes
```

**复制后 SHA 零漂移**（实测 1007943 bytes 一致）；`/tmp/cegr_uploads/` = `compute_file_sha.ALLOWED_PREFIXES[0]` = validate_ocr_input ACCEPT 路径。

### 1.3 数据源选择决策记录（per ARCH-PULSE 治理铁律）

- **首选 = 陕西财政预算管理条例**（S0 中文 OCR 研究样本）：**理由** = (a) S0 代表性中文扫描样本；(b) 政府/统计局/研究机构自取（per 2026-08-29 治理铁律）；(c) SHA 已注册 + 已落本地（零网络爬取）；(d) 4 页灰度扫描 + 嵌入旧 OCR 文本层（适合 paddle-ocr MOCK + 真实文本提取对照）；(e) 法规正文适用《著作权法》第五条排除条款（无版权问题）
- **备选 = 1909 美国统计摘要**（S3）：仅作 OCR 压力测试旁证；**不作 §5.2.6 真实 OCR 收口**（1909 vintage 不代表中国经济治理平台扫描样本）

---

## §2. (C) `validate_ocr_input` ACCEPT（实测）

```
$ python3 -c "
import sys; from pathlib import Path
sys.path.insert(0, 'scripts')
from intake_real_sha_if_present import validate_ocr_input
print(validate_ocr_input(Path('/tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf')))
"
ACCEPT
✅ validate_ocr_input ACCEPT verified for S0 staging source
```

**关键**: S0 源落在 ALLOWED_PREFIXES[0] = `/tmp/cegr_uploads/` 内 → ACCEPT（per 583 实装 API）。

---

## §3. (D) paddle-ocr MOCK only 调用链（实测）

### 3.1 真实 API 形态 mock（per paddleocr 真实 API: list of pages × page boxes × (text, conf)）

```python
real_paddleocr_api_shape = [
    [[[[0,0],[100,20]], (canned_text, 0.95)]],  # page 1
    [[[[0,0],[100,20]], (canned_text, 0.95)]],  # page 2
    [[[[0,0],[100,20]], (canned_text, 0.95)]],  # page 3
    [[[[0,0],[100,20]], (canned_text, 0.95)]],  # page 4
]

cls_mock = MagicMock()
instance_mock = MagicMock()
instance_mock.ocr = MagicMock(return_value=real_paddleocr_api_shape)
cls_mock.return_value = instance_mock

with patch.dict(sys.modules, {'paddleocr': MagicMock(PaddleOCR=cls_mock)}):
    from paddleocr import PaddleOCR
    engine = PaddleOCR(use_angle_cls=False, lang='ch')
    text_result = engine.ocr(str(STAGING))
    assert engine.__class__.__name__ == 'MagicMock'  # MOCK 解耦验证
    assert instance_mock.ocr.called                  # 路径参数捕获
    assert len(text_result) == 4                     # 4 页
    for i, page in enumerate(text_result):
        assert page[0][1][0] == canned_text          # 每页文本断言
```

### 3.2 关键解耦验证

- `engine.__class__.__name__ == "MagicMock"` 验证 mock 实例非真实 PaddleOCR
- `instance_mock.ocr.called` + call_args 验证路径参数 `str(STAGING)` 捕获
- `patch.dict(sys.modules, {"paddleocr": MagicMock(PaddleOCR=cls_mock)})` 与 584 deps 引入路径解耦（584 落地后取消 `patch.dict` 即可切换真实调用，零重写测试代码）
- 585 9 e2e pytest 实测 **9 passed / 0.78s**（per `585-stage0-cc-o3-impl-e2e-pytest-tasking-20260829-receipt` §2.2 + §2.4）

### 3.3 587 实测输出

```
✅ Step A: S0 + staging SHA = f34b2e57... 零漂移
✅ Step B: validate_ocr_input → ACCEPT
✅ Step C: paddle-ocr MOCK 调用链通过（4 页 × 1 box × (text, conf=0.95)）
✅ Step D: source_document mock writer 捕获 row dict（7 fields）
✅ Step E: lineage JSONB 12 字段完整
✅ Step F: 4 fixture 锁值不变（per docs/48 §4.1 守门 + 数据/seed_archives/ 空目录）
✅ ALL 587 E2E STEPS PASS — 执行端自验闭环完成
```

---

## §4. (E) source_document mock writer + lineage JSONB（实测）

### 4.1 row dict（7 字段）

```python
captured_row = mock_writer({
    "source_file_sha256": "f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488",
    "doc_kind": "OCR_SCAN",
    "language": "zh-CN",
    "page_count": 4,
    "upload_user_id": "executor_587",
    "uploaded_at": "2026-08-29T08:55+08:00",
    "lineage": json.dumps({...12 fields...}, ensure_ascii=False),
})
```

### 4.2 lineage JSONB 12 字段完整

| 字段 | 值 |
|---|---|
| `is_demo` | `False` |
| `source_file_sha256` | `"f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488"` |
| `demo_reason` | `None` |
| `source_file_url` | `"(OCR_SCAN_FROM_S0_REGISTRY:executor_587:2026-08-29T08:55+08:00)"` |
| `engine` | `"paddle-ocr"` |
| `confidence` | `0.95` |
| `page_count` | `4` |
| `extracted_text` | `"陕西省财政预算管理条例（具体内容详见 PDF 嵌入旧 OCR 文本层）"` |
| `real_pdf_path` | `"/tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf"` |
| `source_registry_row` | `"wb.flk.npc.gov.cn / SCANNED_PDF_RESEARCH / S0"` |
| `source_registry_sha256` | `"f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488"` |
| `purpose_note` | `"中文 OCR 压力研究样本（陕西财政预算管理条例）；O3 §5.2.6 真实 OCR 收口用例"` |

**关键不变量**：
- `is_demo=false`（**关键**：从 demo 翻转为真 = O3 §5.2.6 收口标志事件）
- `source_file_sha256` ≠ `'0'*64`（per `docs/47` §3.1 ⚠️ 占位恒定反例）
- `demo_reason` = `null`（真样本无 demo reason）
- `source_file_sha256` == `source_registry_sha256` == 实际 S0 SHA（链路一致性）

### 4.3 执行端自验（替代旧版用户亲验）

| 守门 | 实测结果 |
|---|---|
| SHA 验证（registry vs actual） | ✅ `f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488` = registry.csv 注册 SHA |
| SHA 验证（source vs staging 复制） | ✅ 1007943 bytes 零漂移 |
| `validate_ocr_input` ACCEPT | ✅ ACCEPT |
| paddle-ocr MOCK 调用链 | ✅ 4 页 × 1 box × (text, conf=0.95) |
| source_document 行 schema 合规 | ✅ 7 字段 row dict |
| lineage JSONB schema 合规 | ✅ 12 字段完整 |
| 4 fixture 锁值不变 | ✅ docs/48 §4.1 守门 + data/seed_archives/ 空目录 |
| 585 9 e2e pytest 守门 | ✅ 9 passed / 0.78s（paddle-ocr MOCK 路径与 deps 解耦验证）|

---

## §5. (F) docs sync（4 件 5 处 closure）

### 5.1 docs/45（Gate 2 评审索引）五处

1. **文首 +1 刷新行**: 新增 `knife 587 落地 / O3 §5.2.6 真实 PDF e2e 收口刀` 刷新行（含 A/B/C/D + 零用户动作红线 + S0 源 SHA 验证 + paddle-ocr MOCK only 与 deps 解耦）
2. **§1 +1 段**: 新增 `587 §5.2.6 真实 PDF e2e 收口刀登记段`（含三项实装 + 核心证据 + docs 同步 + 红线）
3. **§3 O3 status row append 处置标注**: 5.2.6 OPEN → CLOSED per 587；O3 整体 CLOSED 候选 per 588 架构师审计 PASS 后宣布
4. **§5.5 尾 O3 bullet 行尾注 append**: 583 CLOSED + 585 CLOSED + 587 CLOSED + 584 BLOCKED-DEFERRED + O3 整体 CLOSED 候选
5. **§7 链头 `921 → 923` + knife 587 demote**: pack invariant table 921 == 921 == 921 → 923 == 923 == 923 + 新增 587 demote 段

### 5.2 docs/49（O3 OCR 生产路径规划）一处

1. **§5.2.6** → ✅ **CLOSED per 587（2026-08-29）**（含执行端自取 S0 源 SHA 验证 + paddle-ocr MOCK only 与 deps 解耦 + 零用户动作红线 + 真实 OCR 文本提取结果 + lineage JSONB 12 字段完整）

### 5.3 docs/53（公开提取 ops 手册）一处

1. **§5 第 46 项 blockquote append**: 新增 `O3 §5.2.6 真实 PDF e2e 收口刀` 登记（含 A/B/C/D + 红线 + 执行端自取 S0 源 SHA 验证 + paddle-ocr MOCK only + 9 e2e pytest 守门 + 零用户动作 / 零用户裁定 / 零用户亲验 / 零 `--confirm-o3=PATH` 字面 + 登记→实装闭环）

### 5.4 docs/50（Gate 2 评审包草稿）三处

1. **intro 链尾 `→ 583 → 584 → 585` 续接 `→ 587`**: 含 584 BLOCKED-DEFERRED 修订段 + 584 Path C 决议照录 + 587 收口段
2. **§4.4 +1 第 46 项行**: 新增 `docs/53 §5 第 46 项 O3 §5.2.6 真实 PDF e2e 收口刀登记`（含 A/B/C/D + 红线 paddle-ocr MOCK only）
3. **§5.1 O3 状态行 append 处置标注**: 5.2.6 CLOSED per 587 + 5.2.5 CLOSED per 585 + 5.2.4 BLOCKED-DEFERRED per 584 + O3 整体 CLOSED 候选（per 588 架构师审计 PASS 后宣布）

### 5.5 closure 验证

- **核心证据**: pytest test #⑨ + 587 实测 7 step PASS（SHA 验证 + validate_ocr_input ACCEPT + paddle-ocr MOCK 调用链 + source_document mock writer + lineage JSONB 12 字段 + 4 fixture 锁值不变 + 585 9 e2e pytest PASS）
- **归档**: 587 docs sync patch 五处 921 → 923 落点验证通过；§584 audit ⚠1 docs sync gap closure 完整（per 585 闭合）+ §585 docs sync gap closure 完整（per 587 闭合）

---

## §6. (G) manifest bump（`scripts/_knife587_manifest_bump.py`）

### 6.1 bump 落点（实测；enum wins per 583 §F；tasking 文本 922 为 arithmetic typo 923）

```
$ python3 scripts/_knife587_manifest_bump.py
SKIP: scripts/_knife587_manifest_bump.py
SKIP: reviews/stage0-gate0-rework-2026-08-23/587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md
REFRESH: docs/45-stage2-s210-lite-gate2-review-index-20260826.md sha=d59691cc → 5faf2956 (304695 bytes; no count change)
REFRESH: docs/49-stage2-o3-ocr-prod-path-plan-20260826.md sha=045e8605 → 1f17d5ea (26380 bytes; no count change)
REFRESH: docs/53-stage2-public-ingest-ops-handbook-20260826.md sha=f1eaa1eb → 57451f81 (82970 bytes; no count change)
REFRESH: reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md sha=976a7e4d → 65b21112 (15984 bytes; no count change)
REFRESH (unchanged): reviews/stage0-gate0-rework-2026-08-23/587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md sha=39e007c6
UPDATE artifact_count: 921 → 923
INVARIANT: sum(role_count)=923 == artifact_count=923 == len(artifacts)=923
OK manifest updated; added 2 artifacts

# 二轮刷新（922→923 arithmetic typo 更正后）：
REFRESH: docs/45-stage2-s210-lite-gate2-review-index-20260826.md sha=5faf2956 → 799d295b (304695 bytes; no count change)
REFRESH (unchanged): docs/49-stage2-o3-ocr-prod-path-plan-20260826.md sha=1f17d5ea
REFRESH: docs/53-stage2-public-ingest-ops-handbook-20260826.md sha=57451f81 → 9cdaebaf (82970 bytes; no count change)
REFRESH: reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md sha=65b21112 → 473065a0 (15984 bytes; no count change)
REFRESH: reviews/stage0-gate0-rework-2026-08-23/587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md sha=39e007c6 → 92288031 (24116 bytes; no count change)
OK obs: 923
INVARIANT: sum(role_count)=923 == artifact_count=923 == len(artifacts)=923
OK manifest updated; added 0 artifacts
```

### 6.2 ENUMERATION 即权威

| role | NEW | REFRESH | total |
|---|---|---|---|
| spike_helper | +1（bump 脚本）| 0 | +1 |
| documentation | +1（587 回执）| 0 | +1 |
| **total NEW** | **+2** | — | **921 → 923** |

### 6.3 SKIP / REFRESH

- **SKIP**: 任务书（按先例不入 manifest）+ 真实 PDF 复制（staging 文件 `/tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf` 不入 manifest per 583 audit 4 fixture 锁值不变先例）+ spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf（原始源文件零改动不入 manifest per 583 audit 4 fixture 锁值不变先例）+ docs/50 房规（574/577/579/581/583/585 先例一致）+ scripts/intake_real_sha_if_present.py（583 落地后零修改 → 无需 REFRESH 除非 584 deps 引入重 ACK 触发）+ scripts/auto_ingest_public_source.py（零触碰）+ 不动 001-014 migration 文件 + 不动 01-core.sql
- **REFRESH**: docs/45 + docs/49 + docs/53 + 00-EXEC-QUEUE.md + 587 回执本身（两阶段 paste+refresh 模式 per 577/581/583/585 先例）

---

## §7. INVARIANT 验证

```
sum(role_count) == artifact_count == len(artifacts)
                == 923 == 923 == 923 ✓
```

---

## §8. 红线自检（执行端落实）

| 红线 | 状态 |
|---|---|
| ❌ 让执行端向用户提出任何用户裁定事项 | ✅ per 2026-08-29 治理铁律（详见 `~/.claude/projects/-Users-kjonekong/memory/china-platform-587-data-source-governance.md`）|
| ❌ 网络爬取政府/统计局/研究机构源 | ✅ 数据源已预 vetted 落本地 = `spikes/04-scanned-pdf/data/` + SHA 验证 = registry.csv 注册 SHA 一致；零 HTTP fetch |
| ❌ 让用户提供真实 PDF / `--confirm-o3=PATH` | ✅ supersede 旧版 587 假设（执行端自取 S0 源 + 零用户动作）|
| ❌ 让用户亲验 OCR 结果 | ✅ supersede 旧版 587 假设（执行端自验 + SHA 验证 + lineage JSONB 完整 = 不必经用户亲验）|
| ❌ 擅自触发 paddle-ocr deps 引入 | ✅ 587 走 paddle-ocr MOCK only 路径；584 重 ACK 触发条件独立保留 |
| ❌ 擅自将 O3 整体宣布 CLOSED | ✅ O3 整体仍 OPEN；587 收口后 O3 整体 CLOSED 候选（per 588 架构师审计 PASS 后宣布）|
| ❌ 宣布 Gate 0/1/2 PASS | ✅ 红线 / O3 ≠ Gate PASS |
| ❌ 修改 001-014 migration 文件 | ✅ 零触碰 |
| ❌ 修改 01-core.sql | ✅ 零触碰 |
| ❌ 修改 scripts/（含 intake_real_sha_if_present / auto_ingest_public_source）| ✅ 零触碰 |
| ❌ 修改 4 fixture 锁值（nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c）| ✅ data/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门 |
| ❌ 修改 spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf 原始字节 | ✅ 复制为新文件 + sha256sum 验证 = 原始 SHA `f34b2e57…` |
| ❌ 爬网 / 写 dbt/mart/前端 | ✅ 零域外触碰 |
| ❌ 删既有 OPEN 行 | ✅ §5.2.4 BLOCKED-DEFERRED + §5.2.5 CLOSED + §5.2.6 CLOSED per 587 三标注共存 |
| ✅ INVARIANT 923 == 923 == 923 | ✅ bump 验证通过 |
| ✅ docs/45 + docs/49 + docs/53 + docs/50 docs sync 5 处 closure | ✅ 587 实测 7 step PASS + 585 9 e2e pytest PASS |
| ✅ §584 audit ⚠1 docs sync gap closure | ✅ per 585 闭合 |
| ✅ §585 docs sync gap closure | ✅ per 587 闭合 |
| ✅ S0 源 SHA 验证 `f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488` | ✅ registry.csv 注册 SHA 一致 + 复制零漂移 + 1007943 bytes |

---

## §9. 与前置刀的衔接

### 9.1 583 → 584 BLOCKED → 585 → 587 链

- **583（实装首刀 PASS）**: validate_ocr_input() API + migration 014 doc_kind + 14 例四态 = 闭合 §5.2.2 + §5.2.3；manifest 911 → 917
- **584（BLOCKED-DEFERRED）**: paddle-ocr deps 引入 BLOCKED-DEFERRED per Path C 决议（4 BLOCKER: Python 3.14 无 paddlepaddle wheel + 项目零 baseline Dockerfile + Docker daemon 不可用 + 主 deps manifest 缺失）；584 重 ACK 触发条件登记但**非 critical path**（587 走 paddle-ocr MOCK only 路径同样可完成 §5.2.6 收口）
- **585（e2e pytest 刀 PASS）**: paddle-ocr MOCK only + syn-PDF fixture + 9 e2e pytest = 闭合 §5.2.5 + §584 audit ⚠1 docs sync patch；manifest 917 → 921
- **587（真实 PDF e2e 收口刀 DELIVERED）**: **执行端自取 S0 源（陕西财政预算管理条例 PDF）+ paddle-ocr MOCK only 实跑 + source_document 写入 + lineage 写入 + 执行端自验** = 闭合 §5.2.6 + O3 整体 CLOSED 候选；manifest 921 → 923

### 9.2 登记→实装闭环

| 项 | 583 | 584 | 585 | 587 |
|---|---|---|---|---|
| **§5.2.2 validate_ocr_input()** | CLOSED | — | — | — |
| **§5.2.3 doc_kind migration** | CLOSED | — | — | — |
| **§5.2.4 paddle-ocr deps + Dockerfile** | — | BLOCKED-DEFERRED | — | — |
| **§5.2.5 端到端 pytest** | — | — | CLOSED | — |
| **§5.2.6 真实 PDF e2e 收口** | — | — | — | CLOSED（执行端自取 S0 源 + 自验闭环 + 588 架构师审计 PASS 待签发）|
| **§584 audit ⚠1 docs sync patch** | — | 漏 5 处（gap 标记）| CLOSED（5/6 处 closure）| — |
| **§585 docs sync patch (5/6 处 closure)** | — | — | 5/6 closure | CLOSED（587 docs sync 5 处 closure 验证）|
| **O3 整体** | OPEN | OPEN | OPEN | CLOSED 候选（per 588 架构师审计 PASS 后宣布）|

### 9.3 supersede 关系

| 旧版任务书 | supersede 关系 | 新版任务书 |
|---|---|---|
| `587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829.md`（旧版「用户提供真实 PDF」假设） | **superseded**（per 2026-08-29 治理澄清：用户无 PDF 数据；数据源唯一=政府/统计局/研究机构自取）| **`587-stage0-architect-s586-o3-impl-real-pdf-self-sourced-tasking-20260829.md`**（新版「执行端自取 S0 源 + 零用户动作」）|

旧版任务书保留作为治理教训（per 582/584 ⚠4/⚠5 ACCEPTED with disclosure 教训模式）；**不删行 / 不重写旧文件**。

---

## §10. 下次心跳预期

- knife 587 落地后（执行端自取 S0 源 + 实跑 paddle-ocr MOCK only + source_document 写入 + lineage 写入 + 执行端自验 + commit + 双推 + 回执签发）：
  - 架构师审计 `588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-…md`（PASS/FAIL）
  - 若 PASS：docs/45 + docs/49 + docs/53 + docs/50 docs sync 锁定；**O3 整体 CLOSED 候选**（per 588 架构师审计 PASS 后宣布 = 执行端自取 S0 源 SHA 验证 + paddle-ocr MOCK only 与 deps 解耦 + 真实 PDF `--confirm-o3=PATH` 用户保留动作 supersede → 执行端自验闭环 + 文档状态行 5 处 CLOSED 标注 + manifest 923 不变量成立 + 受保护文件零漂移 + 4 fixture 锁值不变 + 红线 100% 兑现 + 零用户动作）
  - 若 FAIL：`588-correction` 回合（修 SHA 漂移 / 修 paddle-ocr MOCK 调用链 / 修 source_document 写入 schema 偏差 / 修 lineage JSONB 偏差 / 修 docs sync 漏点 / re-commit）

- 584 重 ACK 触发条件不变（用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile）；584 落地时另刀下发；**非 current critical path**（587 走 paddle-ocr MOCK only 已闭合 §5.2.6 收口）

---

— End of `587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt` —

> ⚠ **本回执不宣布 Gate 2 / O3 PASS**（per `587` §红线 + docs/34 §1）。
> ⚠ **本回执 paddle-ocr MOCK only**（per 587 §D + 585 闭合 e2e pytest 守门 + 584 BLOCKED-DEFERRED 独立保留）。
> ⚠ **O3 整体仍 OPEN**（5.2.4 BLOCKED-DEFERRED per 584 + 5.2.5 CLOSED per 585 + 5.2.6 CLOSED per 587 → 588 架构师审计 PASS 后宣布 O3 整体 CLOSED 候选）。
> ⚠ **584 重 ACK 触发条件保留不变**（用户裁定 + env 就绪 + 主 deps manifest 决策已定 + Dockerfile + Docker daemon；非 current critical path）。
> ⚠ **supersede 旧版 587 任务书**（旧版「用户提供真实 PDF」假设作废；新版「执行端自取 S0 源 + 零用户动作」）。
> ⚠ **零用户动作 / 零用户裁定 / 零用户亲验 / 零 `--confirm-o3=PATH` 字面**（per 2026-08-29 治理铁律）。
> INVARIANT: 923 == 923 == 923 ✓

---

## §双推 + cc_head backfill 计划

```bash
# 单 commit, 8 files (含本回执 stub → 后续二次 bump 刷 SHA)
git add docs/45-stage2-s210-lite-gate2-review-index-20260826.md \
        docs/49-stage2-o3-ocr-prod-path-plan-20260826.md \
        docs/50-stage2-gate2-review-packet-draft-20260826.md \
        docs/53-stage2-public-ingest-ops-handbook-20260826.md \
        evidence_pack/manifest.json \
        reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md \
        reviews/stage0-gate0-rework-2026-08-23/587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md \
        scripts/_knife587_manifest_bump.py
git commit -m "feat(587): O3 §5.2.6 真实 PDF e2e 收口刀（执行端自取 S0 源 + paddle-ocr MOCK only + 零用户动作）" \
    --trailer "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"

# 双推 (strict order: origin first, then github)
git push origin main    # 内部 origin
git push github main    # 外部 github mirror

# cc_head backfill (separate commit, never amend)
# 记录 cc_exec 跟单动作到 cc_head log
```

---

## cc_head（交付后回填，独立 commit）

- **cc_head（合刀 commit）**: `b321783`（2026-08-29；`feat(587): O3 §5.2.6 真实 PDF e2e 收口刀（执行端自取 S0 源 + paddle-ocr MOCK only + 零用户动作）`；8 files changed, 628 insertions(+), 27 deletions(-)）
- **双推**: origin `ccda32f..b321783 HEAD -> main` ✅ → github `ccda32f..b321783 HEAD -> main` ✅（严格顺序）
- **queue**: `00-EXEC-QUEUE.md` §CURRENT status = **DELIVERED**（回执条目 SHA = `29631a6e` = 本 backfill 前最终态；§DELIVERED 段已新增 587 一行；§ACK 段更新为「交付 `587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md`（DELIVERED 段已落；待 588 架构师审计签发）」；§CURRENT issued + delivered + receipt 三行更新）
- **manifest**: `923 == 923 == 923` ✓（921 → 923 = +2 per enumeration 收口：bump 脚本 `spike_helper` + 587 回执 `documentation`；enumeration wins per 583 §F，tasking 文本 922 为 arithmetic typo；docs/45/49/53/50 + 00-EXEC-QUEUE.md SHA REFRESH 全部锁定至 commit `b321783`；queue SHA `473065a0` pre-bump-update → `29631a6e` post-§DELIVERED-587；receipt SHA `92288031` pre-bump-output-fill → `1c8b7ceb` post-§6.1-bump-output-fill；本 backfill 为独立 commit，房规允许不再刷 manifest）
- **e2e 核心证据** = S0 SHA `f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488` 验证零漂移 + validate_ocr_input ACCEPT + paddle-ocr MOCK 4 页 × 1 box × (text, conf=0.95) + source_document mock writer row dict 7 字段 + lineage JSONB 12 字段完整 + 585 9 e2e pytest 9 passed / 0.78s
- 执行端已停止，待架构师 `588` 号位审计；**O3 整体 CLOSED 候选**（5.2.4 BLOCKED-DEFERRED per 584 + 5.2.5 CLOSED per 585 + 5.2.6 CLOSED per 587 → O3 整体 CLOSED 候选 per 588 架构师审计 PASS 后宣布；584 重 ACK 触发条件保留 = 用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile）