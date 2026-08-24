# Stage 0 Gate 0 — 陕西中文扫描 PDF 集成与 U-4 验收报告

> 文档日期：2026-08-24
>
> 编写角色：CC（Claude Code）
>
> 状态：**实现与专项验证完成；等待最终全量测试、evidence pack 独立复算、Cursor 终态复验及用户 U-4 裁定**
>
> 范围：Stage 0 Gate 0 陕西 OCR research-track；不修改 PRD、`reviews/` 或 `gate_thresholds.json`。

---

## §0. TL;DR

| 维度 | 终态事实 |
|---|---|
| 官方样本 | 全国人大常委会国家法律法规数据库《陕西省财政预算管理条例》四页真实扫描 PDF 已集成 |
| 来源验证 | 本地 PDF magic、size、SHA-256、扫描结构、嵌入文本层及 macOS 官方下载来源元数据均已验证；CC 未伪造 HTTP 200 |
| OCR 方法 | 300 DPI、Tesseract `chi_sim` PSM 6、TSV 坐标；图像 OCR 不读取嵌入文本层 |
| U-2 对照 | PDF 嵌入旧 OCR 文本层；有噪声，不是人工校对真值 |
| 评测结果 | Han 93.93%；all non-whitespace 90.05%；needs_review 1/4=25%；numeric N/A |
| 门槛结论 | `MEETS_UNCHANGED_APPLICABLE_THRESHOLDS`；门槛数值未降低，N/A 不计 PASS |
| Gate 影响 | per U-3：`none_per_U3_non_gating_research_sample` |
| 自动判定 | CC **不宣布 Stage 0 PASS**；等待 Cursor 终态复验和用户 U-4 |
| 禁止动作 | 未 commit、未 push、未发布、未进入 Stage 1 |

---

## §1. 用户裁定与结论边界

| 裁定 | 已执行口径 |
|---|---|
| P-1 | OCR 门槛保持 numeric ≥80%、char ≥90%、needs_review ≤30% |
| P-2 | 1909 美国样本不作为中国平台代表性样本 |
| U-1 | 陕西法规扫描件作为中文 OCR 压力样本，不冒充原 B-01 统计表代表性 |
| U-2 | 接受嵌入文本层作对照，不要求人工全表标注；必须披露参考噪声 |
| U-3 | spike 04 完整移出 Stage 0 验收，保留为非门控研究轨 |
| U-4 | 最终 eval 与 Cursor 复验后由用户裁定；CC 无权自动给 Stage 0 PASS |
| U-5 | `reviews/` 不纳入 evidence pack，且本轮不改历史审核原文 |

陕西样本通过来源、管线和适用研究阈值验证；numeric 对非表格法规为 N/A 且不计 PASS。per U-3，该研究结果不改变 Gate verdict。

---

## §2. C-1～C-4 验证

### C-1 — 文件、来源与完整性

| Field | Verified value |
|---|---|
| Title | 陕西省财政预算管理条例 |
| Official institution | 全国人大常委会国家法律法规数据库 |
| Official URL | `https://wb.flk.npc.gov.cn/dfxfg/PDF/d31411b562fc4226a7465f1c875afe67.pdf` |
| Local file | `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf` |
| Magic | `%PDF-1.4` |
| Size | 1,007,943 bytes |
| Pages | 4 |
| SHA-256 | `f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488` |

macOS `kMDItemWhereFroms` 记录上述官方直链，Chrome quarantine metadata 存在。用户通过该直链下载后上传文件；CC 验证了本地来源链和文件字节，但本机 TLS 探针未成功，故 `provenance.json` 诚实记录：

```json
"http_status_observed_by_cc": null
```

这不伪装成 CC 独立观测到 HTTP 200，也没有使用 `curl --insecure`。

### C-2 — 真实扫描结构

- Creator：Canon SC1011
- Producer：MP Navigator EX
- 页面尺寸：453.24 × 600.84 pt
- 每页一张 1259 × 1669 grayscale JPEG 图像
- 图像元数据：200 × 200 DPI
- 非合成 PDF、非 HTML 打印版

### C-3 — 中文字符规模与 U-2 对照

- 嵌入文本层 SHA-256：`cec93b67f8da16ecdd97b7e08ab2baf23995f2e61530afff3f1d6295dfdfc0bf`
- Han characters：3,230（满足候选预审的 ≥3,000 字要求）
- Pages：4
- Reference artifact：`spikes/04-scanned-pdf/truth_shaanxi_flk.json`

### C-4 — Provenance 与许可边界

`spikes/04-scanned-pdf/provenance.json` 已记录官方 URL、机构、文件 hashes、扫描元数据、嵌入层 hashes、U-1/U-2/U-3、数值指标 N/A 和 Stage 0 effect。

许可依据限定为《中华人民共和国著作权法》第五条第一项对法律、法规及国家机关官方文件正文的排除。该依据**不扩张**为对法规数据库界面、扫描版式、门户其他资产的 blanket public-domain assertion；样本用途限定为内部 OCR 研究和可复现证据。

---

## §3. OCR 与布局评测实现

### 3.1 独立数据流

1. `build_truth_shaanxi_flk.py` 用 `pdftotext -bbox` 构建 U-2 接受的参考层，并锁定 PDF 和文本 hash。
2. `extract_04_shaanxi_text.py` 将扫描页以 300 DPI 渲染后运行 Tesseract 5.5.3，语言 `chi_sim`、PSM 6、TSV 输出。
3. OCR 提取器只读渲染图像，明确记录 `embedded_text_layer_used=false`，并锁定 `chi_sim.traineddata` SHA-256 `a5fcb6f0...1e1f730`。
4. `ocr_text_layout.py` 以每页可见 word bbox 边界裁去两端各 5% 后的中点作为自适应栏间线，避免内容偏置扫描页被物理中线误分栏。
5. 跨栏间线 word 继续按 bbox 中心归栏，但每页显式记录 divider、crossing count 和 policy，不再静默处理。
6. left/right 两区分别按 Y 中心聚类行、行内按 X 排序；`evaluate_04_shaanxi_text.py` 在各物理区域独立计算 NFKC 归一化后的 Levenshtein distance，再汇总 edits 与 denominator。

旧固定物理中线会在 page 1/page 3 把右栏开头拼入左栏；自适应分栏已消除该串接。该设计不采用字符袋比较，也不按已识别字符身份对齐 reference/OCR，避免掩盖真实插入、删除与替换。

### 3.2 Reference noise

嵌入文本层是旧 OCR，不是人工校对真值；其错误没有被静默修正。例如：

| U-2 reference | New image OCR |
|---|---|
| `预箅` | `预算` |
| `人会` | `大会` |
| `收攴` | `收支` |
| `本行畋区域` | `本行政区域` |

因此下节分数是“与 U-2 接受参考层的一致率”，不是对人工真值的准确率估计。新 OCR 在正确纠正旧参考错误时仍可能被扣分。

---

## §4. 评测结果

来源：`data/extracts/04-scanned-pdf/shaanxi_text_eval_report.json`

| Page | Han agreement | All non-whitespace | Needs review |
|---:|---:|---:|---|
| 1 | 89.40% | 83.45% | yes |
| 2 | 97.62% | 94.70% | no |
| 3 | 92.13% | 88.49% | no |
| 4 | 95.69% | 92.25% | no |
| **Overall** | **93.93%** | **90.05%** | **1/4 = 25%** |

门槛核对：

| Metric | Threshold | Result | Status |
|---|---:|---:|---|
| Han character agreement | ≥90% | 93.93% | met |
| Needs-review pages | ≤30% | 25% | met |
| Numeric-cell accuracy | ≥80% | `null` / non-tabular | N/A，**不计 PASS** |

陕西 `needs_review` 是“页面 Han 一致率低于 90%”的 research-page triage 定义，不冒充 legacy 数值表 confidence/null/raw-parse 信号。`gate_thresholds.json` 的数值没有修改；machine report 用 `threshold_values_unchanged=true` 和独立的 `needs_review_definition/scope` 明确区分。

Machine verdict：

```text
research_track_result=MEETS_UNCHANGED_APPLICABLE_THRESHOLDS
stage0_effect=none_per_U3_non_gating_research_sample
stage0_verdict=not_determined_by_this_report_user_U4_required
```

---

## §5. 文件清单

### 新增实现与样本

- `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf`
- `spikes/04-scanned-pdf/ocr_text_layout.py`
- `spikes/04-scanned-pdf/build_truth_shaanxi_flk.py`
- `spikes/04-scanned-pdf/extract_04_shaanxi_text.py`
- `spikes/04-scanned-pdf/evaluate_04_shaanxi_text.py`
- `spikes/04-scanned-pdf/test_04_shaanxi_text.py`
- `spikes/04-scanned-pdf/truth_shaanxi_flk.json`
- `data/extracts/04-scanned-pdf/shaanxi_text_ocr.json`
- `data/extracts/04-scanned-pdf/shaanxi_text_eval_report.json`

### 更新的当前态与证据契约

- `spikes/04-scanned-pdf/provenance.json`
- `spikes/04-scanned-pdf/README.md`
- `source_registry/registry.csv`
- `scripts/build_evidence_pack.py`
- `docs/03-source-registry.md`
- `docs/11-stage0-review.md`
- `docs/12-stage0-closure-and-report.md`
- `docs/13-r4-final-verification.md`
- 本文件

Builder 已增加 `spikes/**/*.py`，确保共同依赖 `ocr_text_layout.py` 进入 pack 并归类为 `spike_helper`。

### 明确未修改

- PRD
- `reviews/` 既有审核原文
- `spikes/04-scanned-pdf/gate_thresholds.json`
- legacy 1909 truth/extractor/evaluator/tests

---

## §6. 验证记录

### 6.1 已完成专项验证

| Suite | Result |
|---|---|
| Shaanxi research-track | **14 passed** |
| Legacy 1909 scanned-PDF track | **18 passed** |
| Spike 04 combined | **32 passed** |

新增 14 tests 覆盖：PDF magic/size/hash、官方来源与诚实 HTTP 状态、许可边界、truth 字节可重现、U-2 hash/字符数、参考噪声、自适应分栏回归、显式 crossing policy、image-only OCR、`chi_sim.traineddata` hash、OCR 两次字节一致、truth/OCR/eval 与 committed 产物 freshness 对账、缺 PDF/工具/input 非零失败，以及 tmp 输出不改写正式产物。

### 6.2 最终全集与 evidence pack

本表记录真实复跑结果；若后续审查触发代码变更，必须再次复跑并覆盖本表。

| Verification | Final evidence |
|---|---|
| Full pytest | **251 passed / 0 failed / 0 skipped in 450.57s** |
| Worktree hash before/after | `9b874a09...784a8e` (pre-manifest-update, 561 files) → `6e43c318...3deaf46` (post-manifest-update, 561 files)；**差异仅 `evidence_pack/manifest.json`**（即本次 rebuild 的预期产物）；排除 `.git`/cache/bytecode |
| Evidence Builder real rebuild | **440 artifacts**；role_count sum=440；schema_version=1.1-R3G-R4；陕西 `research_non_gating_extracted_artifact` × 1 + `research_non_gating_eval_report` × 1；`reviews/`=0；exit 0 |
| Independent pack validation | **artifacts_reverified=440; pack_errors=0**（size、SHA-256、relative/unique paths、role_count 之和、manifest 自排除、`/Users/`/`/home/`/`/tmp/` 禁止前缀全部 0 错） |
| Static checks | **PY_COMPILE_OK=7/7**（spike04 5 files + builder + evidence test）；**JSON_OK=4/4**（provenance/truth/OCR/eval）；**git diff --check exit=0**；**source_registry/registry.csv=7 行 18 列**（含 1 表头 + 6 数据行） |
| Review | **BLOCKED_BY_TOOLING**：3 次 `feature-dev:code-reviewer` 子代理全部因 `API error: Stream error: error decoding response body` 提前终止；codex review `--uncommitted` exit=0 但输出仅含 rmcp HTTP 502 / AuthRequired / TLS handshake EOF transport errors + SKILL.md preamble，**无任何实际 review findings**；`/review` skill 因当前位于默认分支 `main` 自动停止；CC 不冒充已 cleared |
| DevEx probes | **完成**：3 个 CLI 均有说明/默认路径；缺输入与不可写输出统一 rc=2 + `FATAL`，无 traceback；README 提供 prerequisites 与全临时输出流水线 |

第一次全量复跑同样得到 251 passed，但外壳误用 zsh 只读变量 `status`，导致 after-hash 未执行；该次不计零污染证据。上表仅采用随后完整执行成功的 before/test/after 链。

> **Review 工具链诚实记录（BLOCKED_BY_TOOLING）**：本应在代码变更 ≥ 5 文件后自动跑 `/review`，但本次实测三次子代理全部失败（`feature-dev:code-reviewer` × 3 → "Agent terminated early due to an API error: Stream error: error decoding response body"），回退到 `codex review --uncommitted` 也只回传 rmcp HTTP 502 / AuthRequired / TLS handshake EOF transport errors 而无实际审查条目。因此 `/review` 状态为 **未通过、未绕过、未冒充 cleared**。可用替代证据：静态检查（PY_COMPILE 7/7、JSON 4/4、git diff --check 0）、special tests（spike04 32 passed 含 14 陕西新增）、worktree pollution proof、real evidence pack rebuild + 独立复算 0 错。**Cursor 终态复验**应优先弥补这一缺口，并对上述替代证据逐项独立复算后再给出 U-4 建议。

### 6.3 Cursor 可执行复验 runbook

```bash
# A. Prerequisites and pinned OCR model
command -v pdftotext pdfinfo pdftoppm tesseract
tesseract --version
tesseract --list-langs | grep '^chi_sim$'
# expected chi_sim.traineddata SHA-256:
# a5fcb6f0db1e1d6d8522f39db4e848f05984669172e584e8d76b6b3141e1f730

# B. Non-mutating Shaanxi rebuild
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
python3 spikes/04-scanned-pdf/build_truth_shaanxi_flk.py --out "$tmp/truth.json"
python3 spikes/04-scanned-pdf/extract_04_shaanxi_text.py --out "$tmp/extracted.json"
python3 spikes/04-scanned-pdf/evaluate_04_shaanxi_text.py \
  --truth "$tmp/truth.json" --extracted "$tmp/extracted.json" \
  --out "$tmp/report.json"

# C. Tests
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider \
  spikes/04-scanned-pdf/test_04_shaanxi_text.py \
  spikes/04-scanned-pdf/test_04_scanned_pdf.py
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider

# D. Real builder to isolated output; no SKIP/FORCE hooks
EVIDENCE_PACK_DIR="$tmp/pack" python3 scripts/build_evidence_pack.py

# E. Independent pack validation
python3 - "$tmp/pack/manifest.json" <<'PY'
import hashlib, json, sys
from pathlib import Path
repo = Path.cwd()
manifest = json.loads(Path(sys.argv[1]).read_text())
errors = []
paths = [item["path"] for item in manifest["artifacts"]]
for item in manifest["artifacts"]:
    path = Path(item["path"])
    disk = repo / path
    if path.is_absolute() or any(prefix in item["path"] for prefix in ("/Users/", "/home/", "/tmp/")):
        errors.append((item["path"], "forbidden_path"))
    elif not disk.is_file():
        errors.append((item["path"], "missing"))
    elif disk.stat().st_size != item["size_bytes"]:
        errors.append((item["path"], "size"))
    elif hashlib.sha256(disk.read_bytes()).hexdigest() != item["sha256"]:
        errors.append((item["path"], "sha256"))
if len(paths) != len(set(paths)):
    errors.append(("manifest", "duplicate_paths"))
if "evidence_pack/manifest.json" in paths:
    errors.append(("manifest", "self_included"))
if sum(manifest["role_count"].values()) != manifest["artifact_count"]:
    errors.append(("manifest", "role_count"))
if any(path.startswith("reviews/") for path in paths):
    errors.append(("manifest", "reviews_included"))
print(f"artifacts_reverified={len(paths)} pack_errors={len(errors)}")
print(errors)
raise SystemExit(bool(errors))
PY
```

正式 pack 完成后，本节和 `docs/13 §10` 必须同步真实结果；若验证失败，必须原样报告。

---

## §7. Cursor 终态复验清单

Cursor 复验建议按以下顺序：

1. 本文件 §1～§4：确认政策边界、C-1～C-4、评测和 U-3/U-4 口径。
2. `spikes/04-scanned-pdf/provenance.json`：核对来源、hash、`http_status_observed_by_cc=null` 与许可范围。
3. `spikes/04-scanned-pdf/truth_shaanxi_flk.json` 与两个 `data/extracts/.../shaanxi_*` 产物：核对参考和报告。
4. `ocr_text_layout.py`、truth/extract/evaluate 三脚本及 `test_04_shaanxi_text.py`：核对 image-only、双栏区域算法、确定性与失败路径。
5. `scripts/build_evidence_pack.py` 与最终 `evidence_pack/manifest.json`：确认 helper 已入包且独立复算零错误。本次真实 rebuild 已得 **440 artifacts**、**pack_errors=0**、schema_version=`1.1-R3G-R4`、陕西 2 个 `research_non_gating_*` role、`reviews/`=0；详见 §6.2。
6. `docs/03`、`docs/11`、`docs/12`、`docs/13`：确认当前态一致，历史审核记录未倒改。
7. 确认 PRD、`reviews/`、`gate_thresholds.json` 未修改。

Cursor 应独立报告：测试真实状态、最终 artifact_count、`pack_errors`、发现的任何不一致，以及是否建议用户作 U-4 裁定。Cursor 复验不替代用户 U-4。

---

## §8. U-4 用户验收点

完成 Cursor 终态复验后，用户只需裁定：

> 在 U-1/U-2/U-3 已锁定、门槛不降、陕西研究轨满足适用研究阈值但 numeric N/A 不计 PASS 且不参与 Gate、全部工程验证和 evidence pack 独立复验结果透明的前提下，Stage 0 Gate 0 的最终状态是什么？

CC 不预填该答案，也不会从陕西 research-track 适用阈值达标推导 Stage 0 PASS。

---

## §9. 操作红线与仓库状态

- 未批量爬取，未绕过验证码、登录、付费墙或 TLS 验证。
- 未使用商业数据源或付费 OCR。
- 未用合成 PDF/HTML 打印版冒充真实扫描件。
- 未降低 OCR 门槛，未把 N/A、skipped、BLOCKED 或字段断言计为 PASS。
- 未把 1909 美国样本描述为中国代表性样本。
- 未修改 PRD 或 `reviews/`。
- **未 commit、未 push、未部署、未进入 Stage 1。**

---

— End of Shaanxi integration and U-4 acceptance report —
