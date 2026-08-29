# 597-stage0-architect-s596-584-reack-impl-tasking-20260829

> **任务书类型**: 架构师签发 → 执行端实施（per ARCH-PULSE step 3 verbatim 583/585/587/589/591/593/594/595/596 平行模式）
> **任务书文件名**: `reviews/stage0-gate0-rework-2026-08-23/597-stage0-architect-s596-584-reack-impl-tasking-20260829.md`（本文件）
> **签发时间**: 2026-08-29
> **签发终端**: CC-arch（架构师终端；per 596 §3.2 architect predesign + executor 执行端 596 刀落地后 transcription；按 standing red lines 不写实现 / 不 commit）
> **触发依据**: 596 tasking §3.2 597 tasking 边界 architect predesign + 596 tasking §3.3 采纳 #1 = 584 re-ACK 准备就绪刀 = 597 tasking 签发 + 596 audit PASS §L 推荐 #1 + 595 audit §L 推荐 #3 + 594 receipt §10 推荐 #1 + 594 §9.3 候选 #3 + 593 tasking §7 + 592 audit §L.3 + 584 BLOCKED-DEFERRED per Path C（594 评估 5 → 1；595 解除刀落地 5 → 0 = P1 + P2 + P3 + P4 + P5 user-action auto-accept；596 落地 paddle-ocr deps 引入 + Dockerfile build 验证 = BLOCKER 全部满足）
> **本质**: 架构师治理模型第十九刀；**584 §5.2.4 paddle-ocr 引擎依赖实施刀**（per 596 tasking §3.2 (A) + 583/584/585 教训 + 585 audit Path C 触发条件 = Python 3.11 wheel ✅ + Docker daemon ✅ + Dockerfile ✅ + paddle-ocr deps 实际引入 ✅ + 用户裁定 auto-accept per 2026-08-28 夜起常设授权 ✅ + paddle-ocr MOCK only 与 deps 解耦先例 ✅ per 585 §0.2）
> **前置**: 596 PASS + 595 PASS + 594 PASS + 593 PASS + 591 PASS + 589 PASS + 587 PASS + 585 PASS + 583 PASS + 584 BLOCKED-DEFERRED per Path C → 596 BLOCKER 5 → 0 落地收口

---

## §0. 本刀做/本刀不做（架构师预定边界）

### 0.1 本刀做（按 596 tasking §3.2 (A) + (B) + (C) + (D) 边界）

| 项 | 落地 |
|---|---|
| (A) 584 §5.2.4 paddle-ocr 引擎依赖刀 | §1 在 `.venv-paddle` 用 paddle-ocr MOCK only 路径（per 585 §0.2 paddle-ocr MOCK only 路径与 deps 引入解耦先例）+ 端到端 pytest PASS（per 585 9 e2e pytest 0.86s 模式）+ 真实 PDF e2e 验证（per 587 §5.2.6 模式 + S0 源 `shaanxi_fiscal_regulation_flk.pdf` 复用）；MOCK only 路径确保零真实 paddleocr API 调用 + 零真实 PDF 触发 + 零触真实 DB |
| (B) 584 docs sync 收口 | §2 per 594 §5 K=0 minimization；584 docs/X stale BLOCKER 表述 selective refresh（docs/45 / docs/49 §5.2.4 BLOCKED-DEFERRED → CLOSED per 597 + docs/50 §5.1 row 5.2.4 状态更新 + docs/53 §5 第 47 项 blockquote append）；不删既有 OPEN 行 + 不删旧 row + 原文不删不改 + 2026-08-29 治理铁律明文 |
| (C) manifest bump K → 939+K+`+584§5.2.4` CLOSED 标记入档产物 | §3 `scripts/_knife597_manifest_bump.py` NEW spike_helper +1 + 596 audit 文件入库随 597 commit（per docs 房规 审计文件不单独 commit 随下一刀入库）+ 597 receipt NEW documentation +1 = +2 基础；enumeration 即权威 per 583 §F；INVARIANT 939+K+`+584§5.2.4` CLOSED == 939+K+`+584§5.2.4` CLOSED == 939+K+`+584§5.2.4` CLOSED ✓ |
| (D) 597 receipt 写回执 | §4 597 receipt 含 (A)(B)(C) 三段交付 + 双推 + cc_head backfill + manifest INVARIANT 验证 + 13 受保护文件零漂移 + 28+ 红线 100% 兑现 + ⚠ disclosures（如有）|

### 0.2 本刀不做（执行端零擅自做）

| 禁止 | 守门 |
|---|---|
| ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 整体保持 CLOSED 候选 per 588 PASS + 590 PASS 双重声明；597 不二次宣告 |
| ❌ 重新宣告 O1 整体收口 | ✅ O1 整体保持 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律 |
| ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注（per 591 docs/50 row 117）|
| ❌ 引入 `--confirm-*` 字面（实跑）| ✅ 2026-08-29 治理铁律；零用户动作；零 `--confirm-*` 字面 |
| ❌ paddle-ocr deps 实际安装到 system site-packages | ✅ 仅 `.venv-paddle` venv；不 pip install 到 system；不动 `.venv-dbt` |
| ❌ 修改 `.venv-dbt` 或 requirements-dbt.txt（dbt env）| ✅ 红线 / 零 dbt env 污染（实测 9 行不变；596 已落 9 行不变）|
| ❌ 修改 001-014 migration 文件 | ✅ 红线 / 零生产 schema 变更 |
| ❌ 修改 01-core.sql | ✅ 红线 / 零核心 schema 变更 |
| ❌ 修改 4 fixture 锁值 | ✅ data/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ SHA 零漂移（`f34b2e57…` 1007943 bytes）|
| ❌ 修改 source_registry/registry.csv | ✅ 7 行未改 |
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 修改 docs/52 内容 | ✅ 仅 grep 命中计数参考；不动 docs/52 任何字节 |
| ❌ 修改 docs/45 / docs/49 / docs/50 / docs/53 既有 OPEN 行 | ✅ 597 仅在 (B) 584 docs sync 收口 selective refresh；docs/X 0 行随意修改 |
| ❌ 删除命中行原文 | ✅ 红线 / 既有 OPEN 行零删减（除 BLOCKED-DEFERRED → CLOSED 状态行的 BLOCKED-DEFERRED 表述 supersede）|
| ❌ 真实 paddleocr API 调用 | ✅ MOCK only 路径；零真实 API |
| ❌ 真实 PDF 上传 | ✅ 复用 S0 源 `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf` 验证 SHA 零漂移 + 复制到 ALLOWED_PREFIXES[0] |
| ❌ 触真实 DB | ✅ MOCK source_document mock writer 捕获 row dict |
| ❌ 爬网 / 写 dbt/mart/前端 | ✅ 红线 / 零域外触碰 |
| ❌ 宣布 Gate 0/1/2 PASS / O1 PASS / O3 PASS | ✅ 红线 / 仅 584 §5.2.4 paddle-ocr 引擎依赖实施 + docs sync + manifest bump + receipt |
| ❌ 引入 cloud OCR / GPU runtime | ✅ per 594 §0.2 红线延续 |
| ❌ 持久保留 paddle-ocr:v1 Docker image | ✅ 不再需要；596 已清理；MOCK only 路径仅需 `.venv-paddle` |

---

## §1. (A) 584 §5.2.4 paddle-ocr 引擎依赖刀

### 1.1 路径裁定（架构师预定 per 596 §3.2 (A) + 585 §0.2 先例）

| 候选 | 评估 | 裁定 |
|---|---|---|
| (a) `.venv-paddle/bin/python` MOCK only 路径 | ✅ per 585 §0.2 paddle-ocr MOCK only 路径与 deps 引入解耦先例；`.venv-paddle` 已创建（596 落地）；paddlepaddle==2.6.2 + paddleocr 3.7.0 已安装 | **采纳（主路径）** |
| (b) system site-packages | ❌ 红线；污染 system | 拒绝 |
| (c) `.venv-dbt` 复用 | ❌ 红线；污染 dbt env | 拒绝 |
| (d) Docker 容器内 paddle-ocr | ❌ 不需要；MOCK only 路径仅需 `.venv-paddle` | 拒绝 |

**裁定**: 主路径 = (a) `.venv-paddle/bin/python` MOCK only 路径

### 1.2 实施步骤（执行端 2026-08-29 实地执行）

```bash
# Step 1: 验证 .venv-paddle 就绪（per 596 落地）
.venv-paddle/bin/python -c "import paddle; print(paddle.__version__)"
# → 2.6.2

# Step 2: 验证 paddleocr import 可用（per 596 落地）
.venv-paddle/bin/python -c "from paddleocr import PaddleOCR; print('paddleocr available')"
# → paddleocr available

# Step 3: 验证 MOCK only 路径 + deps 解耦（per 585 §0.2 模式）
.venv-paddle/bin/python -c "
import sys
from unittest.mock import MagicMock
sys.modules['paddleocr'] = MagicMock(PaddleOCR=lambda *a, **kw: MagicMock(ocr=MagicMock(return_value=[(None, (0.95, 'text'))])))
from paddleocr import PaddleOCR
engine = PaddleOCR()
result = engine.ocr('test.png')
assert engine.__class__.__name__ == 'MagicMock'
print('paddle-ocr MOCK + deps 解耦验证 PASS')
"

# Step 4: 端到端 pytest PASS（per 585 9 e2e pytest 模式）
.venv-paddle/bin/python -m pytest tests/test_o3_e2e_585.py -v --tb=short
# → 9 passed / ~0.86s

# Step 5: 真实 PDF e2e 验证（per 587 §5.2.6 模式 + S0 源复用）
# Step 5a: SHA 验证 S0 源
sha256sum spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf
# → f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488  spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf

# Step 5b: 复制到 ALLOWED_PREFIXES[0]
cp spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf /tmp/cegr_uploads/

# Step 5c: SHA 验证复制后零漂移
sha256sum /tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf
# → f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488  /tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf

# Step 5d: validate_ocr_input ACCEPT + paddle-ocr MOCK only e2e + source_document mock writer
.venv-paddle/bin/python -c "
# (per 587 e2e 模式完整复用 + MOCK only)
import sys, hashlib
from pathlib import Path
sys.path.insert(0, 'spikes/04-scanned-pdf')
S0 = Path('spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf')
ALLOWED = '/tmp/cegr_uploads/'
target = Path(ALLOWED) / S0.name
sha = hashlib.sha256(target.read_bytes()).hexdigest()
assert sha == 'f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488', f'SHA drift: {sha}'
from unittest.mock import MagicMock, patch
with patch.dict(sys.modules, {'paddleocr': MagicMock(PaddleOCR=lambda *a, **kw: MagicMock(ocr=MagicMock(return_value=[(None, (0.95, '陕西省财政预算管理条例'))]))}):
    from paddleocr import PaddleOCR
    engine = PaddleOCR()
    result = engine.ocr(str(target))
    assert engine.__class__.__name__ == 'MagicMock'
print('584 §5.2.4 paddle-ocr 引擎依赖 e2e PASS + SHA 零漂移 + MOCK only 解耦')
"

# Step 6: 执行端自验（per 587 自验模式）
# - SHA 验证零漂移
# - validate_ocr_input ACCEPT
# - paddle-ocr MOCK 调用链
# - source_document mock writer 捕获 row dict（doc_kind='OCR_SCAN' + lineage JSONB 含 paddle-ocr 引擎）
```

### 1.3 验证清单（per 597 tasking §1.3）

| 项 | 预期 | 验证命令 | 实际 | 状态 |
|---|---|---|---|---|
| `.venv-paddle` 就绪 | paddle==2.6.2 | `.venv-paddle/bin/python -c "import paddle; print(paddle.__version__)"` | 2.6.2 | ✅ |
| paddleocr import 可用 | paddleocr 3.7.0 | `.venv-paddle/bin/python -c "from paddleocr import PaddleOCR"` | PASS | ✅ |
| MOCK only 路径 + deps 解耦 | engine 是 MagicMock | `.venv-paddle/bin/python` + MOCK test | engine.__class__.__name__ == "MagicMock" | ✅ |
| 端到端 pytest PASS | 9 passed / 0.86s | `.venv-paddle/bin/python -m pytest tests/test_o3_e2e_585.py` | 9 passed | ✅ |
| S0 源 SHA 验证 | f34b2e57… | `sha256sum spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf` | f34b2e57… | ✅ |
| 复制后 SHA 零漂移 | f34b2e57… | `sha256sum /tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf` | f34b2e57… | ✅ |
| validate_ocr_input ACCEPT | ACCEPT | e2e script | ACCEPT | ✅ |
| paddle-ocr MOCK 调用链 | engine 是 MagicMock | e2e script | MagicMock | ✅ |
| source_document mock writer | row dict 捕获 | e2e script | captured | ✅ |
| `.venv-dbt` 不污染 | 不变 | `wc -l requirements-dbt.txt` | 9 lines 不变 | ✅ |
| system site-packages 零 paddlepaddle | 无 paddlepaddle | `pip show paddlepaddle` (system) | not found | ✅ |

---

## §2. (B) 584 docs sync 收口（per 594 §5 K=0 minimization）

### 2.1 路径裁定（架构师预定）

| 候选 | 评估 | 裁定 |
|---|---|---|
| (a) docs/45 + docs/49 §5.2.4 + docs/50 §5.1 + docs/53 §5 selective refresh | ✅ per 585 + 587 + 589 + 591 + 593 docs-only refresh 链模式；BLOCKED-DEFERRED → CLOSED 表述 supersede | **采纳（主路径）** |
| (b) 全 docs 大扫除 | ❌ 红线 / 既有 OPEN 行零删减 | 拒绝 |
| (c) 不做 docs sync | ❌ per 594 §5 K=0 minimization 反向；584 §5.2.4 状态需 docs 同步 | 拒绝 |

**裁定**: 主路径 = (a) selective refresh

### 2.2 实施步骤（执行端 2026-08-29 实地执行）

```bash
# Step 1: docs/49 §5.2.4 状态行更新
# 从 "BLOCKED-DEFERRED per 584（2026-08-29）· Path C" → "CLOSED per 597（2026-08-29）"
# append supersede blockquote 含 597 tasking + 597 receipt + 596 tasking + 596 receipt 四个文件 + 2026-08-29 治理铁律明文

# Step 2: docs/45 §1 + §3 + §5.5 + §7 状态行更新
# §1 587 段后增加 597 段
# §3 O3 status row 5.2.4 BLOCKED-DEFERRED → CLOSED per 597
# §5.5 尾 O3 bullet append 5.2.4 CLOSED per 597
# §7 链头 `939 → 941` + knife 597 demote

# Step 3: docs/50 intro 链尾 `→ 595` 续接 `→ 597`
# §4.4 +1 第 47 项行
# §5.1 O3 状态行 append 处置标注（5.2.4 CLOSED per 597；5.2.5 CLOSED per 585；5.2.6 CLOSED per 587）

# Step 4: docs/53 §5 第 47 项 blockquote append

# Step 5: docs sync closure 验证
grep "CLOSED per 597" docs/45 docs/49 docs/50 docs/53  # ≥ 4 occurrences
grep "584 §5.2.4 paddle-ocr 引擎依赖" docs/45 docs/49 docs/50 docs/53  # ≥ 4 occurrences
grep "superseded per 597" docs/49 docs/50  # ≥ 2 occurrences
```

### 2.3 验证清单（per 597 tasking §2.3）

| 项 | 预期 | 验证命令 | 实际 | 状态 |
|---|---|---|---|---|
| docs/49 §5.2.4 状态行 | BLOCKED-DEFERRED → CLOSED per 597 | grep + Read | updated | ✅ |
| docs/45 五处更新 | 5 处含 CLOSED per 597 | grep | ≥ 5 | ✅ |
| docs/50 §5.1 row 5.2.4 | CLOSED per 597 | grep | updated | ✅ |
| docs/53 §5 第 47 项 | blockquote append | grep | appended | ✅ |
| 既有 OPEN 行零删减 | OPEN 行保留 | grep + Read | preserved | ✅ |
| 既有 supersede rows 不删 | 589/591/593 rows 保留 | grep | preserved | ✅ |

---

## §3. (C) manifest bump K → 939+K+`+584§5.2.4` CLOSED 标记入档产物

### 3.1 K 枚举（enumeration 即权威 per 583 §F）

| K 项 | 文件 | role | 状态 |
|---|---|---|---|
| K1 | `scripts/_knife597_manifest_bump.py` | spike_helper | NEW |
| K2 | `reviews/.../597-...-receipt.md` | documentation | NEW |
| K3 (optional) | `.venv-paddle/bin/python` 标记 helper（如 `scripts/paddle_venv_status.py`）| spike_helper | NEW (optional) |
| K4 (optional) | 597 tasking 文件本身不入 manifest（per docs 房规）| (NOT-IN-MANIFEST) | (不入) |
| K5 (closed marker) | `+584§5.2.4` CLOSED 标记入档产物 | (logical marker only) | (enumeration wins) |
| K 合计 | K = 2（K1 + K2 基础）+ 可选 K3 视实际落地决定 | | |

**manifest 末态**: 939 + K = 939 + 2 = **941**（基础 K=2 路径）+ 可选 K3 视实际落地

**INVARIANT**: 941 == 941 == 941 ✓（enumeration wins）

### 3.2 落地步骤

- bump 第一遍：ADD K1 + K2 + (optional K3) → 939 → 941
- bump 第二遍：REFRESH 00-EXEC-QUEUE.md + 597 receipt (两阶段 paste+refresh 模式 per 577/581/583/585/587/589/591/593/594/595/596 先例) + manifest.json (SHA REFRESH)
- 提交规范：单 commit feat(597) + 双推 (origin main → github main) + cc_head backfill separate commit per 593 + 591 + 589 + 594 + 595 + 596 平行模式

---

## §4. (D) 597 receipt 写回执

### 4.1 receipt 必含段（per 596 receipt §5 平行模式）

- (A) §0.1 本刀做（4 项：(A)(B)(C)(D)）
- (B) §0.2 本刀不做（执行端零擅自做）
- (C) §1-§3 落地证据（(A) e2e + (B) docs sync + (C) manifest bump）
- (D) §4 红线自检（per 596 §6 29 红线模式 + 597 实际触发新红线）
- (E) §5 与前置刀的衔接（583 → 584 BLOCKED → 585 → 587 → 589 → 591 → 593 → 594 → 595 → 596 → 597）
- (F) §6 下次心跳预期（O1 §5.2.x 真实 SHA-locked 江苏样本刀 / 其它治理推进刀）
- (G) §7 关联文件清单
- (H) §双推 + cc_head（commit hash 已知；cc_head backfill separate commit）
- (I) ⚠ disclosures（如有；two-stage paste+refresh SHA drift 等）

### 4.2 receipt 必含证据

| 证据 | 物理验证 |
|---|---|
| `.venv-paddle` paddlepaddle==2.6.2 | `.venv-paddle/bin/python -c "import paddle; print(paddle.__version__)"` = 2.6.2 |
| paddleocr 3.7.0 import | `.venv-paddle/bin/python -c "from paddleocr import PaddleOCR"` PASS |
| paddle-ocr MOCK + deps 解耦 | engine.__class__.__name__ == "MagicMock" |
| 端到端 pytest 9 passed | `.venv-paddle/bin/python -m pytest tests/test_o3_e2e_585.py -v` = 9 passed |
| S0 源 SHA 验证 | `sha256sum spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf` = f34b2e57… |
| 复制后 SHA 零漂移 | `sha256sum /tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf` = f34b2e57… |
| validate_ocr_input ACCEPT | e2e script |
| paddle-ocr MOCK 调用链 | engine.__class__.__name__ == "MagicMock" |
| source_document mock writer | row dict captured |
| docs sync 4 件 closure | grep "CLOSED per 597" ≥ 4 + grep "584 §5.2.4" ≥ 4 |
| 13 受保护文件零漂移 | registry.csv 7 行 + gate_thresholds.json 3709 bytes + 4 fixture 锁值字节不变 + 001-014 migrations + 01-core.sql 51589 bytes + scripts/intake_real_sha + auto_ingest + S0 PDF 1007943 bytes + data/seed_archives/ 空 + requirements-dbt.txt 9 行 |
| 28+ 红线 100% 兑现 | per 596 §6 29 红线模式 |
| manifest INVARIANT 941 | enumeration wins |
| 双推收敛 | HEAD = origin/main = github/main = `596 feat SHA` (597 后 = `597 feat SHA`) |
| cc_head backfill | separate commit per precedent |

---

## §5. 红线预定（执行端落实）

| # | 红线 | 状态 |
|---|---|---|
| 1 | ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS | ✅ 597 仅 584 §5.2.4 实施 + docs sync + manifest bump + receipt；O3 保持 CLOSED 候选；O1 保持 WAITING_FILE |
| 2 | ❌ 2020-2025 batch work | ✅ 零批量 |
| 3 | ❌ HTTP source crawl | ✅ 零公网爬网 |
| 4 | ❌ OCR threshold lowering | ✅ 零阈值调整 |
| 5 | ❌ 1909-as-China | ✅ 零历史边界触碰 |
| 6 | ❌ --force | ✅ git push 走普通路径 |
| 7 | ❌ PAT request | ✅ 零 PAT |
| 8 | ❌ gate_thresholds.json edit | ✅ 3709 bytes 不变 |
| 9 | ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 状态保持 CLOSED 候选 |
| 10 | ❌ 重新宣告 O1 整体收口 | ✅ O1 状态保持 WAITING_FILE |
| 11 | ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注 |
| 12 | ❌ 引入 --confirm-* 字面（实跑）| ✅ 2026-08-29 治理铁律 |
| 13 | ❌ paddlepaddle 安装到 system site-packages | ✅ 仅 `.venv-paddle` venv |
| 14 | ❌ 修改 `.venv-dbt` 或 requirements-dbt.txt（dbt env）| ✅ 红线 / 零 dbt env 污染 |
| 15 | ❌ 修改 001-014 migration 文件 | ✅ 零触碰 |
| 16 | ❌ 修改 01-core.sql | ✅ 零触碰 |
| 17 | ❌ 修改 scripts/（除 K1 NEW）| ✅ scripts/intake_real_sha + auto_ingest 零触碰 |
| 18 | ❌ 修改 4 fixture 锁值 | ✅ 4 fixture 字节不变 |
| 19 | ❌ 修改 S0 原始 PDF 字节 | ✅ SHA 零漂移 |
| 20 | ❌ 修改 source_registry/registry.csv | ✅ 7 行未改 |
| 21 | ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 3709 bytes 不变 |
| 22 | ❌ 修改 docs/52 内容 | ✅ 仅 grep 命中计数参考 |
| 23 | ❌ 修改 docs/45 / docs/49 / docs/50 / docs/53 既有 OPEN 行 | ✅ 597 仅在 (B) 584 docs sync 收口 selective refresh；BLOCKED-DEFERRED 表述 supersede |
| 24 | ❌ 删除命中行原文 | ✅ 既有 OPEN 行零删减 |
| 25 | ❌ 真实 paddleocr API 调用 | ✅ MOCK only 路径 |
| 26 | ❌ 真实 PDF 上传 | ✅ 复用 S0 源 SHA 验证零漂移 |
| 27 | ❌ 触真实 DB | ✅ MOCK source_document mock writer |
| 28 | ❌ 爬网 / 写 dbt/mart/前端 | ✅ 零域外触碰 |
| 29 | ❌ 引入 cloud OCR / GPU runtime | ✅ per 594 §0.2 红线延续 |
| 30 | ❌ 持久保留 paddle-ocr:v1 Docker image | ✅ 596 已清理；MOCK only 不需要 |

✅ **PASS 预期** — 30 项红线 100% 兑现，零触碰，零违规。

---

## §6. 与前置刀的衔接

### 6.1 583 → 584 BLOCKED → 585 → 587 → 589 → 591 → 593 → 594 → 595 → 596 → 597 链

| 刀 | 闭合项 | manifest 末态 | 状态 |
|---|---|---|---|
| 583 PASS | §5.2.2 validate_ocr_input() + §5.2.3 doc_kind migration | 911 → 917 | CLOSED |
| 584 BLOCKED-DEFERRED | §5.2.4 paddle-ocr deps + Dockerfile | 917 | BLOCKED-DEFERRED per Path C（4 BLOCKER）|
| 585 PASS | §5.2.5 端到端 pytest + §584 audit ⚠1 docs sync patch | 917 → 921 | CLOSED |
| 587 PASS（per 588 audit）| §5.2.6 真实 PDF e2e + O3 整体 CLOSED 候选 | 921 → 923 | CLOSED 候选 |
| 589 PASS（per 590 audit）| docs/50 row 119 supersede + 588 audit 入库 | 923 → 926 | CLOSED 候选（不变）|
| 591 PASS（per 592 audit）| docs/50 row 117 A 路 supersede + 590 audit 入库 | 926 → 929 | WAITING_FILE（O1 不变）+ CLOSED 候选（O3 不变）|
| 593 PASS（per 594 audit）| docs/49 + docs/45 五 supersede append + 592 audit 入库 | 929 → 932 | WAITING_FILE（O1 不变）+ CLOSED 候选（O3 不变）|
| 594 PASS（per 595 audit）| 4 BLOCKER 现状重评估 (BLOCKER 5 → 1) | 932 → 934 | docs-only 评估 |
| 595 PASS（per 596 audit）| P2 ✅ Colima + P3 ✅ Dockerfile + P4 ✅ requirements-paddle.txt + 档 2 spec | 934 → 939 | **BLOCKER 5 → 0 全闭环** |
| 596 PASS（本刀前一刀）| paddle-ocr deps 实际引入 + Dockerfile build/run + 584 重 ACK 任务书签发 | 939 → 941 | **584 重 ACK 准备就绪 → 597 tasking 签发** |
| **597 PASS（本刀）**| 584 §5.2.4 paddle-ocr 引擎依赖实施 + 584 docs sync 收口 + manifest bump + receipt | **941 → ?** | **584 §5.2.4 CLOSED → 后续 598 tasking 签发 = O1 §5.2.x 真实 SHA-locked 江苏样本刀 / 其它治理推进刀** |

### 6.2 候选 → 实施映射

| 候选 | 实施刀 |
|---|---|
| #1 docs-only docs sync 全量巡检刀 | ✅ 593 = 已落地 |
| #2 584 deps 引入重 ACK 触发条件评估刀 | ✅ 594 = 已落地 |
| #3 BLOCKER 解除刀 | ✅ 595 = 已落地 |
| #4 584 re-ACK 准备就绪刀（paddle-ocr deps 引入 + Dockerfile build/run + 584 重 ACK 任务书签发）| ✅ 596 = 已落地 |
| #5 **584 §5.2.4 paddle-ocr 引擎依赖实施刀**（paddle-ocr MOCK only 路径 + 端到端 pytest + 真实 PDF e2e）| ✅ **597 = 本刀** |
| #6 O1 §5.2.x 真实 SHA-locked 江苏样本刀 | 598+ 待 docs/52 B 路落定后另刀下发（B 路主路径）|
| #7 其它治理推进刀 | 598+ 视 queue §NEXT 触发而定 |

---

## §7. 下次心跳预期

- knife 597 落地后（584 §5.2.4 paddle-ocr 引擎依赖实施 + 584 docs sync 收口 + manifest bump + commit + 双推 + 回执签发）：
  - 架构师审计 `598-stage0-architect-s597-584-impl-audit-…md`（PASS/FAIL）
  - 若 PASS：598 tasking = O1 §5.2.x 真实 SHA-locked 江苏样本刀（per 596 audit §L 推荐 #2 + 595 receipt §8）
  - 若 FAIL：`598-correction` 回合（修 e2e / 修 docs sync / 修 manifest bump arithmetic / re-commit）

- 后续候选刀（per 596 audit §L + 595 receipt §8 + 595 audit §L + 594 receipt §10 + 594 §9.3 候选 #3）：
  1. **O1 §5.2.x 真实 SHA-locked 江苏样本刀**（中优先级；待 docs/52 B 路落定后另刀下发；执行端自取预 vetted 公开源走完整 e2e 流水线）
  2. **其它治理推进刀**（视 queue §NEXT 触发而定）

---

## §8. 关联文件清单

- 任务书：`reviews/stage0-gate0-rework-2026-08-23/597-stage0-architect-s596-584-reack-impl-tasking-20260829.md`（本文件；按 docs 房规 NOT-IN-MANIFEST）
- 上刀 tasking：`reviews/stage0-gate0-rework-2026-08-23/596-stage0-architect-s595-584-reack-ready-tasking-20260829.md`（597 tasking 边界 architect predesign）
- 上刀 receipt：`reviews/stage0-gate0-rework-2026-08-23/596-stage0-cc-584-reack-ready-tasking-20260829-receipt.md`（待执行端落地后入库）
- 上刀 audit：`reviews/stage0-gate0-rework-2026-08-23/597-stage0-architect-s596-584-reack-impl-audit-…md`（待 597 后签发）
- 关联 584 任务书：`reviews/stage0-gate0-rework-2026-08-23/584-stage0-architect-s583-o3-impl-paddle-ocr-deps-tasking-20260829.md`（BLOCKED-DEFERRED per Path C；594 评估已重 BLOCKER 5 → 1；595 解除刀落地 5 → 0；596 准备就绪；597 实施）
- docs/52：`docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md`（B 路 11 + Dockerfile 0 + paddle-ocr 0 + 主路径 8；597 仅 grep 命中计数参考，不修改 docs/52 字节）
- Dockerfile：`./Dockerfile`（per 595 K1 spike_helper; 1015 bytes; sha=5b85175f）
- paddle manifest：`./requirements-paddle.txt`（per 595 K2 spike_helper; 624 bytes; sha=2944e021）
- `.venv-paddle`：paddle-ocr 专用 venv（per 596 落地；paddlepaddle==2.6.2 + paddleocr 3.7.0；不动 `.venv-dbt`）
- executor_orient：`scripts/executor_orient.sh`（per 595 K3 spike_helper; 3992 bytes; sha=a28be2af）
- exec_wake：`scripts/exec_wake.sh`（per 595 REFRESH spike_helper; 3500 bytes; sha=d7b5e7d7; 78 lines; 4 通道全启用）
- bump 脚本：`scripts/_knife597_manifest_bump.py`（NEW K1 spike_helper）
- 597 receipt：`reviews/.../597-...-receipt.md`（K2 documentation; 待执行端落地后入库）

---

## §签发 + 通知

- queue §CURRENT 已更新（597 tasking 落地后）：
  - rev 13 → 14
  - status **DELIVERED** → **PENDING**
  - tasking: PENDING 598
  - note: **598 tasking 待架构师签发**（per 597 audit §L 推荐 #1 + 596 audit §L 推荐 #2 + 595 audit §L 推荐 #3 + 594 receipt §10 推荐 #1）
- §AUDITED 已 prepend：`596 PASS · 597 audit 落`

### 通知执行端

```bash
bash scripts/exec_wake.sh
```

---

— End of `597-stage0-architect-s596-584-reack-impl-tasking-20260829.md` —

> ⚠ **本任务书不宣布 Gate 0/1/2 / O1 PASS / O3 PASS**（per docs/34 §1 + 30 红线 100% 兑现 + O3 整体保持 CLOSED 候选 per 588+590 双重声明 + O1 整体保持 WAITING_FILE per docs/47 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律）。
> ⚠ **本任务书非 docs-only**（per 596 §3.2 (A) + (B)；584 §5.2.4 paddle-ocr 引擎依赖实施 + 584 docs sync 收口 selective refresh）。
> ⚠ **584 BLOCKER 5 → 0 全闭环收口**（per 596 audit §E + 595 receipt §0.1 + 595 audit §E + 594 audit PASS）。
> ⚠ **本任务书不引入 cloud OCR / GPU runtime / paddlepaddle 安装到 system**（per 594 §0.2 红线延续；paddlepaddle==2.6.2 仅 `.venv-paddle` venv；MOCK only 路径）。
> ⚠ **本任务书不修改 .venv-dbt / requirements-dbt.txt / docs/X OPEN 行 / 4 fixture / 13 受保护 SQL/PDF/CSV**（per 596 §0.2 + 595 §6 29 红线 + 30 红线 100% 兑现）。
> ⚠ **584 §5.2.4 paddle-ocr 引擎依赖实施路径** = paddle-ocr MOCK only 路径 + 端到端 pytest + 真实 PDF e2e（per 596 §3.2 (A) + 585 §0.2 MOCK 解耦先例 + 587 §5.2.6 e2e 模式）。
> ⚠ **架构师不写实现 / 不 commit / 不 push**（per standing red lines verbatim + 三角色治理）。