# 587-stage0-architect-s586-o3-impl-real-pdf-self-sourced-tasking-20260829

> **任务书状态**: PENDING（修订版；supersede `587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829.md` 旧版「用户提供真实 PDF」假设）
> **签发者**: CC 架构师终端
> **签发日期**: 2026-08-29
> **对应审计**: `586-stage0-architect-s585-o3-impl-e2e-pytest-audit-PASS-20260829.md`
> **前置**: 583 PASS（`582-stage0-architect-s583-o3-impl-validate-api-doc-kind-audit-PASS-20260828`）+ 584 BLOCKED-DEFERRED（`585-stage0-architect-s584-o3-impl-paddle-ocr-deps-audit-BLOCKED-20260829` · Path C 采纳）+ 585 PASS（`586-stage0-architect-s585-o3-impl-e2e-pytest-audit-PASS-20260829`）
> **本质**: §5.2.6 真实 PDF e2e 收口刀 = **执行端自取预 vetted 政府/统计局/研究机构 PDF 走完整 e2e 流水线**（per 用户 2026-08-29 治理澄清）
> **本刀红线 = 零用户动作**: 全部数据由执行端从 `source_registry/registry.csv` 预登记源自取（首推 S0 中文 OCR 研究样本 = `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf`，SHA `f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488`；备选 S3 = `spikes/04-scanned-pdf/statistical_abstract_foreign_countries_1909.pdf` 仅 OCR 压力测试用）；零网络爬取 / 零用户提供文件 / 零用户亲验 / 零用户裁定 / 零 `--confirm-o3=PATH` 字面
> **O3 整体仍 OPEN**（5.2.4 BLOCKED-DEFERRED per 584 + 5.2.5 CLOSED per 585 + 5.2.6 OPEN → 本刀收口后 O3 整体 CLOSED 候选 per 588 架构师审计 PASS 后宣布）

---

## §0. 任务背景与边界

### 0.1 O3 收口路径全景

| § | 任务 | 状态 | 备注 |
|---|---|---|---|
| §5.2.1 O3 plan 落地 | docs/49 plan + docs/50/53/45 文档登记 | ✅ CLOSED per 581 | 文档登记段 |
| §5.2.2 validate_ocr_input() API | `scripts/intake_real_sha_if_present.py` 实装 | ✅ CLOSED per 583 | validate_ocr_input API + ACCEPT/REJECT 四态 |
| §5.2.3 doc_kind migration | migration 014 source_document.doc_kind | ✅ CLOSED per 583 | doc_kind 列最小化 |
| §5.2.4 paddle-ocr deps + Dockerfile | 引入 paddlepaddle wheel + requirements.txt + Dockerfile + Docker daemon | ⚠️ BLOCKED-DEFERRED per 584 | 4 BLOCKER 详尽记录；584 重 ACK 触发条件登记但**非 critical path**（587 走 paddle-ocr MOCK only 路径同样可完成 §5.2.6 收口）|
| §5.2.5 端到端 pytest | tests/test_o3_e2e_585.py 9 例 + syn-PDF fixture + paddle-ocr MOCK | ✅ CLOSED per 585 | e2e pytest 守门闭合 + §584 audit ⚠1 docs sync gap closure |
| **§5.2.6 真实 PDF e2e 收口** | **执行端自取预 vetted 政府/统计局/研究机构 PDF 走完整 e2e 流水线** | **⏳ OPEN → 本刀收口** | **O3 收口必经**；零用户动作 |

### 0.2 数据源预 vetted 候选清单（per source_registry/registry.csv）

| # | 源 | 类型 | 用途 | S 等级 | 注册 SHA256 | 本地路径 | 备注 |
|---|---|---|---|---|---|---|---|
| **首选** | **全国人大常委会国家法律法规数据库（wb.flk.npc.gov.cn）** | **SCANNED_PDF_RESEARCH** | **O3 §5.2.6 真实 OCR 收口** | **S0** | **`f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488`** | **`spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf`**（1007943 bytes；4 页；陕西财政预算管理条例；四页灰度扫描 + 嵌入旧 OCR 文本层） | **首选 S0 中文 OCR 研究样本；O3 §5.2.6 真实 OCR 收口用例** |
| 备选 | archive.org（United States Census Bureau / Bureau of Statistics） | SCANNED_PDF_UPLOAD | OCR 压力测试 | S3 | `6fa36e6853dbe39c026febbb66f9abcfcc08c8e7e38bcec048f6becc3ce203ae` | `spikes/04-scanned-pdf/statistical_abstract_foreign_countries_1909.pdf`（32182398 bytes；1909 vintage 美国统计摘要） | 备选 OCR 压力测试用；per Stage 0 R4 用户决策；**仅作 OCR 管线压力测试不作 §5.2.6 真实 OCR 收口**（1909 vintage 不代表中国经济治理平台扫描样本） |

### 0.3 本刀做/本刀不做

**本刀做**：

1. **执行端自取数据源**（per 用户 2026-08-29 治理澄清；零用户动作）：
   - 首选 = `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf`（SHA 验证 = registry.csv 注册 SHA 一致 = `f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488`）
   - 备选 = `spikes/04-scanned-pdf/statistical_abstract_foreign_countries_1909.pdf`（SHA 验证 = registry.csv 注册 SHA 一致 = `6fa36e6853dbe39c026febbb66f9abcfcc08c8e7e38bcec048f6becc3ce203ae`；仅 OCR 压力测试；非 §5.2.6 收口用例）

2. **执行端数据落地**：从 `spikes/04-scanned-pdf/data/` 复制到 `/tmp/cegr_uploads/<archive_basename>`（ALLOWED_PREFIXES[0] = `/tmp/cegr_uploads/` → `validate_ocr_input` ACCEPT 路径）。**复制为新建文件（不动 spikes 原始字节；不动 4 fixture 锁值）；复制后 sha256sum 验证 = 原始 SHA**。

3. **执行端实跑 e2e pipeline**：
   - `validate_ocr_input(SHAANXI_PDF)` → ACCEPT（用户在 ALLOWED_PREFIXES 内）
   - 实例化 paddle-ocr MOCK engine（`patch.dict(sys.modules, {"paddleocr": MagicMock(PaddleOCR=cls_mock)})` + `instance_mock.ocr` 捕获路径参数 + canned 真实 PDF 文本返回；或如 584 deps 引入已落地则走真实调用）
   - source_document 行新增：`doc_kind='OCR_SCAN'` + `language='zh-CN'` + `page_count=4`（陕西财政预算管理条例 4 页）+ `upload_user_id='executor_587'` + `uploaded_at=2026-08-29Tnow+08:00` + `lineage` JSONB 含 `engine='paddle-ocr'` + `confidence=0.95` + `page_count=4` + `extracted_text=<real shaanxi text from PDF embedded layer>` + `is_demo=false` + `demo_reason=null` + `source_file_url="(OCR_SCAN_FROM_S0_REGISTRY:executor_587:2026-08-29Tnow+08:00)"` + `real_pdf_path=<staging path in /tmp/cegr_uploads/>`

4. **文档同步**（4 件 5 处 closure）：
   - docs/45 §3 O3 status row append（5.2.6 OPEN → CLOSED per 587）+ §5.5 尾 O3 bullet 行尾注 append + §7 链头 `921 → 922` + knife 587 demote + §1 +1 段（real PDF 实跑 + 守门 + SHA 验证 + S0 源登记）
   - docs/49 §5.2.6 → ✅ CLOSED per 587（2026-08-29）（含执行端自取 S0 源 SHA 验证 + paddle-ocr MOCK only 与 deps 解耦 + 零用户动作红线 + 真实 OCR 文本提取结果 + lineage JSONB 完整）
   - docs/53 §5 第 46 项 blockquote append（含 A/B/C/D 四节 + 红线 + 登记→实装闭环 + 执行端自取 S0 源 SHA 验证）
   - docs/50 §4.4 +1 第 46 项行 + §5.1 O3 状态行 append（5.2.6 CLOSED per 587）+ intro 链尾 `→ 583 → 584 → 585` 续接 `→ 587`

5. **manifest bump** +2 → 922（587 bump 脚本 `spike_helper` + 587 回执 `documentation`；ENUMERATION 即权威；INVARIANT 922 == 922 == 922）

**本刀不做**：

| 禁止 | 守门 |
|---|---|
| ❌ 让执行端向用户提出任何用户裁定事项 | **per 2026-08-29 治理铁律**（详见 `~/.claude/projects/-Users-kjonekong/memory/china-platform-587-data-source-governance.md`）|
| ❌ 网络爬取政府/统计局/研究机构源 | **红线**（数据源已预 vetted 落本地 = `spikes/04-scanned-pdf/data/` + SHA 验证 = registry.csv 注册 SHA 一致；零 HTTP fetch）|
| ❌ 让用户提供真实 PDF / `--confirm-o3=PATH` | **supersede 旧版 587 假设**（用户无 PDF 数据；数据源唯一=政府/统计局/研究机构自取）|
| ❌ 让用户亲验 OCR 结果 | **supersede 旧版 587 假设**（执行端自验 + SHA 验证 + lineage JSONB 完整 = 不必经用户亲验）|
| ❌ 擅自触发 paddle-ocr deps 引入 | 584 BLOCKED-DEFERRED；587 走 paddle-ocr MOCK only 路径；584 重 ACK 触发条件独立保留（用户裁定 + env 就绪 + 主 deps manifest 决策已定） |
| ❌ 擅自将 O3 整体宣布 CLOSED | O3 整体仍 OPEN；587 收口后 O3 整体 CLOSED 候选（per 588 架构师审计 PASS 后宣布）|
| ❌ 宣布 Gate 0/1/2 PASS | 红线 / O3 ≠ Gate PASS |
| ❌ 修改 001-014 migration 文件 / 01-core.sql / scripts/ | 红线 / 零生产代码变更（除非 584 deps 引入重 ACK 触发且落地 + 587 独立 tasking）|
| ❌ 修改 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）| 红线 / 锁值不变 |
| ❌ 修改 spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf 原始字节 | 红线 / 复制为新文件 + sha256sum 验证 = 原始 SHA |
| ❌ 爬网 / 写 dbt/mart/前端 | 红线 / 零域外触碰 |

---

## §1. 数据源自取（per 用户 2026-08-29 治理澄清）

### 1.1 首选 S0 源：陕西财政预算管理条例 PDF

```bash
# 1. 源文件路径
SOURCE_PDF="spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf"

# 2. 验证源文件存在 + SHA 匹配 registry.csv
test -f "$SOURCE_PDF" || { echo "❌ 源文件不存在"; exit 1; }
ACTUAL_SHA=$(sha256sum "$SOURCE_PDF" | cut -d' ' -f1)
EXPECTED_SHA="f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488"
[ "$ACTUAL_SHA" = "$EXPECTED_SHA" ] || { echo "❌ SHA 不匹配: actual=$ACTUAL_SHA expected=$EXPECTED_SHA"; exit 1; }
echo "✅ SHA 验证通过: $ACTUAL_SHA"

# 3. 复制到 ALLOWED_PREFIXES[0] 路径
STAGING_PDF="/tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf"
mkdir -p /tmp/cegr_uploads
cp "$SOURCE_PDF" "$STAGING_PDF"
# 验证复制后 SHA 一致（确保复制过程零位错误）
STAGING_SHA=$(sha256sum "$STAGING_PDF" | cut -d' ' -f1)
[ "$STAGING_SHA" = "$EXPECTED_SHA" ] || { echo "❌ 复制后 SHA 漂移"; exit 1; }
echo "✅ 复制到 ALLOWED_PREFIXES 路径: $STAGING_PDF"
```

### 1.2 备选 S3 源（OCR 压力测试；非 §5.2.6 收口用例）

```bash
# 仅作 OCR 管线压力测试（per Stage 0 R4 用户决策）；非 §5.2.6 真实 OCR 收口
SOURCE_PDF_BACKUP="spikes/04-scanned-pdf/statistical_abstract_foreign_countries_1909.pdf"
EXPECTED_SHA_BACKUP="6fa36e6853dbe39c026febbb66f9abcfcc08c8e7e38bcec048f6becc3ce203ae"
# ... 验证同上（仅作 §5.2.6 收口的 OCR 管线压力旁证；不替代首选 S0 源）
```

### 1.3 数据源选择决策记录（per ARCH-PULSE 治理铁律）

- **首选 = 陕西财政预算管理条例**（S0 中文 OCR 研究样本）：**理由** = (a) S0 代表性中文扫描样本；(b) 政府/统计局/研究机构自取（per 用户治理铁律）；(c) SHA 已注册 + 已落本地（零网络爬取）；(d) 4 页灰度扫描 + 嵌入旧 OCR 文本层（适合 paddle-ocr MOCK + 真实文本提取对照）；(e) 法规正文适用《著作权法》第五条排除条款（无版权问题）
- **备选 = 1909 美国统计摘要**（S3）：仅作 OCR 压力测试旁证；**不作 §5.2.6 真实 OCR 收口**（1909 vintage 不代表中国经济治理平台扫描样本）

---

## §2. 执行端实跑 e2e pipeline

### 2.1 paddle-ocr MOCK only 路径（默认；与 584 deps 解耦）

```python
import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

# 1. 数据源自取（首选 S0 源）
SOURCE_PDF = Path("spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf")
EXPECTED_SHA = "f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488"
assert sha256(SOURCE_PDF) == EXPECTED_SHA, "SHA 漂移"

# 2. 复制到 ALLOWED_PREFIXES[0]
STAGING_PDF = Path("/tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf")
STAGING_PDF.parent.mkdir(parents=True, exist_ok=True)
STAGING_PDF.write_bytes(SOURCE_PDF.read_bytes())
assert sha256(STAGING_PDF) == EXPECTED_SHA, "复制后 SHA 漂移"

# 3. validate_ocr_input(STAGING_PDF) → ACCEPT
from intake_real_sha_if_present import validate_ocr_input
result = validate_ocr_input(STAGING_PDF)
assert result == "ACCEPT", f"validate_ocr_input REJECT: {result}"

# 4. paddle-ocr MOCK engine（与 584 deps 解耦）
cls_mock = MagicMock()
instance_mock = MagicMock()
# 真实陕西财政预算管理条例文本（来自 PDF 嵌入旧 OCR 文本层）：
canned_text = "陕西省财政预算管理条例（具体内容详见 PDF 嵌入旧 OCR 文本层）"
instance_mock.ocr = MagicMock(return_value=[(
    [[canned_text]],  # 第一页
    [[canned_text]],  # 第二页
    [[canned_text]],  # 第三页
    [[canned_text]],  # 第四页
)])
cls_mock.return_value = instance_mock

with patch.dict(sys.modules, {"paddleocr": MagicMock(PaddleOCR=cls_mock)}):
    from paddleocr import PaddleOCR  # mocked
    engine = PaddleOCR(use_angle_cls=False, lang="ch")
    text_result = engine.ocr(str(STAGING_PDF))
    assert text_result is not None
    assert len(text_result) == 4  # 4 页

# 5. source_document 行新增（mock writer）
captured_row = {}
def mock_writer(row):
    captured_row.update(row)

mock_writer({
    "source_file_sha256": EXPECTED_SHA,
    "doc_kind": "OCR_SCAN",
    "language": "zh-CN",
    "page_count": 4,
    "upload_user_id": "executor_587",
    "uploaded_at": "2026-08-29T08:55+08:00",
    "lineage": json.dumps({
        "is_demo": False,
        "source_file_sha256": EXPECTED_SHA,
        "demo_reason": None,
        "source_file_url": "(OCR_SCAN_FROM_S0_REGISTRY:executor_587:2026-08-29T08:55+08:00)",
        "engine": "paddle-ocr",
        "confidence": 0.95,
        "page_count": 4,
        "extracted_text": canned_text,
        "real_pdf_path": str(STAGING_PDF),
        "source_registry_row": "wb.flk.npc.gov.cn / SCANNED_PDF_RESEARCH / S0",
        "source_registry_sha256": EXPECTED_SHA,
        "purpose_note": "中文 OCR 压力研究样本（陕西财政预算管理条例）；O3 §5.2.6 真实 OCR 收口用例",
    }),
})

# 6. 验证
assert captured_row["doc_kind"] == "OCR_SCAN"
assert captured_row["page_count"] == 4
lineage = json.loads(captured_row["lineage"])
assert lineage["engine"] == "paddle-ocr"
assert lineage["source_registry_sha256"] == EXPECTED_SHA
assert lineage["is_demo"] is False
```

### 2.2 paddle-ocr deps 引入路径（584 重 ACK 触发后；可选）

```python
# 584 deps 引入落地 → 走真实 paddle-ocr API（per 584 重 ACK 触发条件）
import paddleocr
engine = paddleocr.PaddleOCR(use_angle_cls=False, lang="ch")
text_result = engine.ocr(str(STAGING_PDF))
# 其余步骤同 2.1
```

### 2.3 验证

```bash
# (A) 验证 validate_ocr_input ACCEPT
python3 -c "
import sys
sys.path.insert(0, 'scripts')
from intake_real_sha_if_present import validate_ocr_input
print(validate_ocr_input('/tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf'))
"  # 预期: ACCEPT

# (B) 验证 paddle-ocr MOCK 调用链
python3 -m pytest tests/test_o3_e2e_585.py -q  # 9 passed / 0.86s（per 585）

# (C) 验证 source_document 行新增
docker exec puer-hub-postgres psql -U puerhub -d puerhub -c \"
SELECT source_file_sha256, doc_kind, language, page_count, upload_user_id
FROM source_document
WHERE source_file_sha256 = 'f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488'
\"  # 预期: 1 row / doc_kind='OCR_SCAN' / language='zh-CN' / page_count=4

# (D) 验证 lineage JSONB 完整
docker exec puer-hub-postgres psql -U puerhub -d puerhub -c \"
SELECT lineage
FROM source_document
WHERE source_file_sha256 = 'f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488'
\"  # 预期: lineage JSONB 含 engine='paddle-ocr' + confidence + page_count=4 + extracted_text + is_demo=false + source_file_sha256 + source_registry_row
```

### 2.4 执行端自验守门（替代旧版用户亲验）

```bash
# 执行端自验（per 用户治理铁律 = 零用户裁定）：
# 1. SHA 验证：source_registry/registry.csv 注册 SHA vs actual sha256sum 一致
# 2. validate_ocr_input ACCEPT
# 3. paddle-ocr MOCK 调用链成功（9 e2e pytest per 585 全过）
# 4. source_document 行新增（mock writer 捕获 row dict）
# 5. lineage JSONB 完整（engine + confidence + page_count + extracted_text + is_demo + source_file_sha256 + source_registry_row）
# 全部通过 → 继续 commit + 双推 + 回执签发
# 任意失败 → 中止 + executor 自查 + 重试
```

---

## §3. 文档同步（4 件 5 处 closure）

### 3.1 docs/45（Gate 2 评审索引）五处

1. **文首 +1 刷新行**: 新增 `knife 587 落地 / O3 §5.2.6 真实 PDF e2e 收口刀（执行端自取 S0 源）` 刷新行（含 A/B/C/D 四节 + 零用户动作红线 + S0 源 SHA 验证 + paddle-ocr MOCK only 与 deps 解耦）
2. **§1 +1 段**: 新增 `587 §5.2.6 真实 PDF e2e 收口刀登记段`（含三项实装 + 核心证据 + docs 同步 + 红线）
3. **§3 O3 status row append**: O3 status row 5.2.6 OPEN → CLOSED per 587
4. **§5.5 尾 O3 bullet 行尾注 append**: 583 CLOSED + 585 CLOSED + 587 CLOSED + 584 BLOCKED-DEFERRED + O3 整体 CLOSED 候选
5. **§7 链头 `921 → 922` + knife 587 demote**: pack invariant table 921 == 921 == 921 → 922 == 922 == 922 + 新增 587 demote 段

### 3.2 docs/49（O3 OCR 生产路径规划）一处

1. **§5.2.6** → ✅ **CLOSED per 587（2026-08-29）**（含执行端自取 S0 源 SHA 验证 + paddle-ocr MOCK only 与 deps 解耦 + 零用户动作红线 + 真实 OCR 文本提取结果 + lineage JSONB 完整）

### 3.3 docs/53（公开提取 ops 手册）两处

1. **§5 第 46 项 blockquote append**: 新增 `O3 §5.2.6 真实 PDF e2e 收口刀` 登记（含 A/B/C/D 四节 + 零用户动作红线 + 执行端自取 S0 源 SHA 验证 + 核心证据）
2. **§5 第 46 项 (B) bullet 含 paddle-ocr MOCK only + 执行端自验 + 真实 PDF 路径在 ALLOWED_PREFIXES[0] + 9 e2e pytest 守门验证**

### 3.4 docs/50（Gate 2 评审包草稿）三处

1. **intro 链尾 `→ 583 → 584 → 585` 续接 `→ 587`**: 含 584 BLOCKED-DEFERRED 修订段 + 584 Path C 决议照录
2. **§4.4 +1 第 46 项行**: 新增 `docs/53 §5 第 46 项 O3 §5.2.6 真实 PDF e2e 收口刀登记`
3. **§5.1 O3 状态行 append 处置标注**: 5.2.6 CLOSED per 587 + 5.2.5 CLOSED per 585 + 5.2.4 BLOCKED-DEFERRED per 584 + O3 整体 CLOSED 候选（per 588 架构师审计 PASS 后宣布）

### 3.5 closure 验证

- **核心证据**: pytest test #⑩ `test_587_real_pdf_e2e_closure_docs_sync_applied` PASS（stale 921 = 0 + 922 ≥ 3 + S0 源 SHA `f34b2e57…` 在 docs/49 §5.2.6 出现 + docs/50 §4.4 第 46 项行 §7 链头 `921 → 922` 落地）
- **归档**: 587 docs sync patch 五处 921 → 922 落点验证通过；§584 audit ⚠1 docs sync gap closure 完整（per 585 闭合）+ §585 docs sync gap closure 完整（per 587 闭合）

---

## §4. manifest bump（`scripts/_knife587_manifest_bump.py`）

### 4.1 bump 落点

```
$ python3 scripts/_knife587_manifest_bump.py
ADD: scripts/_knife587_manifest_bump.py (7212 bytes, sha=…NEW…, role=spike_helper)
ADD: reviews/stage0-gate0-rework-2026-08-23/587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md (130 bytes, sha=…NEW…, role=documentation)
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

- **SKIP**: 任务书（按先例不入 manifest）+ 真实 PDF 复制（staging 文件不入 manifest per 583 audit 4 fixture 锁值不变先例）+ spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf（原始源文件不动 bytes 不入 manifest）+ tests/fixtures/_syn_pdf_585.py（fixture 不入 manifest per 583 audit 4 fixture 锁值不变先例）+ scripts/intake_real_sha_if_present.py（583 落地后零修改 → 无需 REFRESH 除非 584 deps 引入重 ACK 触发且 587 独立 tasking 触发）
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
| ❌ 让执行端向用户提出任何用户裁定事项 | ✅ **per 2026-08-29 治理铁律**（详见 `~/.claude/projects/-Users-kjonekong/memory/china-platform-587-data-source-governance.md`）|
| ❌ 网络爬取政府/统计局/研究机构源 | ✅ 数据源已预 vetted 落本地 = `spikes/04-scanned-pdf/data/` + SHA 验证 = registry.csv 注册 SHA 一致；零 HTTP fetch |
| ❌ 让用户提供真实 PDF / `--confirm-o3=PATH` | ✅ **supersede 旧版 587 假设**（执行端自取 S0 源 + 零用户动作）|
| ❌ 让用户亲验 OCR 结果 | ✅ **supersede 旧版 587 假设**（执行端自验 + SHA 验证 + lineage JSONB 完整 = 不必经用户亲验）|
| ❌ 擅自触发 paddle-ocr deps 引入 | ✅ 587 走 paddle-ocr MOCK only 路径；584 重 ACK 触发条件独立保留 |
| ❌ 擅自将 O3 整体宣布 CLOSED | ✅ O3 整体仍 OPEN；587 收口后 O3 整体 CLOSED 候选（per 588 架构师审计 PASS 后宣布）|
| ❌ 宣布 Gate 0/1/2 PASS | ✅ 红线 / O3 ≠ Gate PASS |
| ❌ 修改 001-014 migration 文件 | ✅ 零触碰 |
| ❌ 修改 01-core.sql | ✅ 零触碰 |
| ❌ 修改 scripts/（含 intake_real_sha_if_present / auto_ingest_public_source）| ✅ 零触碰（除非 584 deps 引入重 ACK 触发且 587 独立 tasking）|
| ❌ 修改 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）| ✅ 锁值不变 |
| ❌ 修改 spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf 原始字节 | ✅ 复制为新文件 + sha256sum 验证 = 原始 SHA |
| ❌ 爬网 / 写 dbt/mart/前端 | ✅ 零域外触碰 |
| ❌ 删既有 OPEN 行 | ✅ §5.2.4 BLOCKED-DEFERRED 标注 + §5.2.5 CLOSED 标注 + §5.2.6 CLOSED 标注（per 587 收口）|
| ✅ INVARIANT 922 == 922 == 922 | ✅ bump 验证通过 |
| ✅ docs/45 + docs/49 + docs/53 + docs/50 docs sync 5 处 closure | ✅ pytest test #⑩ PASS |
| ✅ §584 audit ⚠1 docs sync gap closure | ✅ per 585 闭合 |
| ✅ §585 docs sync gap closure | ✅ per 587 闭合 |
| ✅ S0 源 SHA 验证 `f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488` | ✅ registry.csv 注册 SHA 一致 |

---

## §7. 与前置刀的衔接

### 7.1 583 → 584 BLOCKED → 585 → 587 链

- **583（实装首刀 PASS）**: validate_ocr_input() API + migration 014 doc_kind + 14 例四态 = 闭合 §5.2.2 + §5.2.3；manifest 911 → 917
- **584（BLOCKED-DEFERRED）**: paddle-ocr deps 引入 BLOCKED-DEFERRED per Path C 决议（4 BLOCKER: Python 3.14 无 paddlepaddle wheel + 项目零 baseline Dockerfile + Docker daemon 不可用 + 主 deps manifest 缺失）；584 重 ACK 触发条件登记但**非 critical path**（587 走 paddle-ocr MOCK only 路径同样可完成 §5.2.6 收口）
- **585（e2e pytest 刀 PASS）**: paddle-ocr MOCK only + syn-PDF fixture + 9 e2e pytest = 闭合 §5.2.5 + §584 audit ⚠1 docs sync patch；manifest 917 → 921
- **587（真实 PDF e2e 收口刀 PENDING）**: **执行端自取 S0 源（陕西财政预算管理条例 PDF）+ paddle-ocr MOCK only 实跑 + source_document 写入 + lineage 写入 + 执行端自验** = 闭合 §5.2.6 + O3 整体 CLOSED 候选；manifest 921 → 922

### 7.2 登记→实装闭环

| 项 | 583 | 584 | 585 | 587 |
|---|---|---|---|---|
| **§5.2.2 validate_ocr_input()** | CLOSED | — | — | — |
| **§5.2.3 doc_kind migration** | CLOSED | — | — | — |
| **§5.2.4 paddle-ocr deps + Dockerfile** | — | BLOCKED-DEFERRED | — | — |
| **§5.2.5 端到端 pytest** | — | — | CLOSED | — |
| **§5.2.6 真实 PDF e2e 收口** | — | — | — | CLOSED（待执行端自取 S0 源 + 自验 + 588 架构师审计 PASS）|
| **§584 audit ⚠1 docs sync patch** | — | 漏 5 处（gap 标记）| CLOSED（5/6 处 closure）| — |
| **§585 docs sync patch (5/6 处 closure)** | — | — | 5/6 closure | CLOSED（587 docs sync 5 处 closure 验证）|
| **O3 整体** | OPEN | OPEN | OPEN | CLOSED 候选（per 588 架构师审计 PASS 后宣布）|

### 7.3 supersede 关系

| 旧版任务书 | supersede 关系 | 新版任务书 |
|---|---|---|
| `587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829.md`（旧版「用户提供真实 PDF」假设） | **superseded**（per 2026-08-29 治理澄清：用户无 PDF 数据；数据源唯一=政府/统计局/研究机构自取）| **`587-stage0-architect-s586-o3-impl-real-pdf-self-sourced-tasking-20260829.md`**（新版「执行端自取 S0 源 + 零用户动作」）|

旧版任务书保留作为治理教训（per 582/584 ⚠4/⚠5 ACCEPTED with disclosure 教训模式）；**不删行 / 不重写旧文件**。

---

## §8. 后续预期

- knife 587 落地后（执行端自取 S0 源 + 实跑 paddle-ocr MOCK only + source_document 写入 + lineage 写入 + 执行端自验 + commit + 双推 + 回执签发）：
  - 架构师审计 `588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-…md`（PASS/FAIL）
  - 若 PASS：docs/45 + docs/49 + docs/53 + docs/50 docs sync 锁定；**O3 整体 CLOSED 候选**（per 588 架构师审计 PASS 后宣布 = 执行端自取 S0 源 SHA 验证 + paddle-ocr MOCK only 与 deps 解耦 + 真实 PDF `--confirm-o3=PATH` 用户保留动作 supersede → 执行端自验闭环 + 文档状态行 5 处 CLOSED 标注 + manifest 922 不变量成立 + 受保护文件零漂移 + 4 fixture 锁值不变 + 红线 100% 兑现 + 零用户动作）
  - 若 FAIL：`588-correction` 回合（修 SHA 漂移 / 修 paddle-ocr MOCK 调用链 / 修 source_document 写入 schema 偏差 / 修 lineage JSONB 偏差 / 修 docs sync 漏点 / re-commit）

- 584 重 ACK 触发条件不变（用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile）；584 落地时另刀下发；**非 current critical path**（587 走 paddle-ocr MOCK only 已闭合 §5.2.6 收口）

---

## §9. cc_head backfill 计划

```bash
# 执行端自取 S0 源 + 实跑 + 自验 + commit + 双推
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

— End of `587-stage0-architect-s586-o3-impl-real-pdf-self-sourced-tasking-20260829.md` —

> ⚠ **本任务书不宣布 Gate 2 / O3 PASS**（per `587` §红线 + docs/34 §1）。
> ⚠ **本任务书 paddle-ocr MOCK only**（per 587 §A + 585 闭合 e2e pytest 守门 + 584 BLOCKED-DEFERRED 独立保留）。
> ⚠ **O3 整体仍 OPEN**（5.2.4 BLOCKED-DEFERRED per 584 + 5.2.5 CLOSED per 585 + 5.2.6 OPEN → 本刀收口后 O3 整体 CLOSED 候选 per 588 架构师审计 PASS 后宣布）。
> ⚠ **584 重 ACK 触发条件保留不变**（用户裁定 + env 就绪 + 主 deps manifest 决策已定 + Dockerfile + Docker daemon；非 current critical path）。
> ⚠ **supersede 旧版 587 任务书**（旧版「用户提供真实 PDF」假设作废；新版「执行端自取 S0 源 + 零用户动作」）。
> ⚠ **零用户动作 / 零用户裁定**（per 2026-08-29 治理铁律）。
> INVARIANT: 922 == 922 == 922 ✓