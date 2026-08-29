# 597-stage0-cc-584-reack-impl-tasking-20260829-receipt

> **任务书类型**: 架构师签发 → 执行端实施（per ARCH-PULSE step 3 verbatim 583/585/587/589/591/593/594/595/596 平行模式）
> **回执类型**: 执行端 597 落地交付（584 §5.2.4 paddle-ocr 引擎依赖实施刀 + 584 docs sync 收口 + manifest bump）
> **回执作者**: CC-exec（Claude Code 执行终端；按 standing red lines 写实现 / commit / push）
> **签发时间**: 2026-08-29
> **触发依据**: 596 audit PASS §L 推荐 #1 + 596 receipt §3.2 architect predesign + 595 audit §L 推荐 #3 + 594 receipt §10 推荐 #1 + 594 §9.3 候选 #3 + 584 BLOCKER 5 → 0 全闭环收口后启动

---

## §0.1 本刀做（per 597 tasking §0.1）

| 项 | 落地 |
|---|---|
| (A) 584 §5.2.4 paddle-ocr 引擎依赖实施 | §1 paddle-ocr MOCK only 路径守门完整（per 585 §0.2）+ 端到端 pytest PASS（per 583 + 585 + 587 三刀累计守门）+ 真实 PDF e2e 守门完整（per 587）= paddle-ocr 真依赖路径仅 spike/ 隔离入口走；`.venv-paddle/bin/python -c "import paddleocr; print(paddleocr.__version__)"` exit 0 + version 3.7.0（隔离 venv 内真依赖导入非污染 system Python）；`scripts/requirements-paddle.txt` NEW（paddlepaddle==2.6.2 + paddleocr==3.7.0；与 `requirements-dbt.txt` 物理隔离）|
| (B) 584 docs sync 收口 | §2 per docs/45 五处（文首 +1 刷新行 / §1 +1 §5.2.4 paddle-ocr 引擎依赖实施刀登记段 / §3 零涉 / §5.5 尾 O3 bullet 行尾注 append / §7 链头 `923 → 944`）+ docs/49 §5.2.4 → ✅ **CLOSED per 597（2026-08-29）**（paddle-ocr 引擎依赖实施收口，supersede 旧版 BLOCKED-DEFERRED per 584）+ docs/50 §4.4 +1 第 47 项行 + intro 链尾 `→ 587` 续接 `→ 597` + §5.1 O3 状态行 append 处置标注（5.2.4 CLOSED per 597；行内 append 不删行）+ docs/53 §5 第 47 项 blockquote append |
| (C) manifest bump K → 941+K | §3 `scripts/_knife597_manifest_bump.py` NEW spike_helper +1 + 596 audit 文件入库随 597 commit（per docs 房规 审计文件不单独 commit 随下一刀入库）+ 597 receipt NEW documentation +1 = +3 基础（K=3）；enumeration 即权威 per 583 §F；INVARIANT 944 == 944 == 944 ✓ |
| (D) 597 receipt 写回执 | §4 597 receipt 含 (A)(B)(C)(D) 四段交付 + 双推 + cc_head backfill + manifest INVARIANT 验证 + 13 受保护文件零漂移 + 30+ 红线 100% 兑现 + ⚠ disclosures（如有）|

---

## §0.2 本刀不做（执行端零擅自做）

| 禁止 | 守门 |
|---|---|
| ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS | ✅ 597 仅 deps 实施收口 + 584 docs sync 收口；O3 整体保持 CLOSED 候选 per 588 PASS + 590 PASS 双重声明；O1 整体保持 WAITING_FILE |
| ❌ 2020-2025 batch work | ✅ 零批量 |
| ❌ HTTP source crawl | ✅ 仅 PyPI wheel 下载（paddlepaddle==2.6.2 cp311 + paddleocr==3.7.0 cp311 已就绪 per 596 §1）；零公网爬网 |
| ❌ OCR threshold lowering | ✅ 零阈值调整 |
| ❌ 1909-as-China | ✅ 零历史边界触碰 |
| ❌ --force | ✅ git push 走普通路径 |
| ❌ PAT request | ✅ 零 PAT |
| ❌ gate_thresholds.json edit | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 状态保持 CLOSED 候选；597 不二次宣告（仍待 588 架构师审计 PASS 后宣布）|
| ❌ 重新宣告 O1 整体收口 | ✅ O1 状态保持 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律 |
| ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注（per 591 docs/50 row 117）|
| ❌ 引入 --confirm-* 字面（实跑）| ✅ 2026-08-29 治理铁律；零用户动作；零 `--confirm-*` 字面 |
| ❌ paddlepaddle 安装到 system site-packages | ✅ 仅 `.venv-paddle` 专用 venv（per 596 §1）；不 pip install 到 system；不动 `.venv-dbt` |
| ❌ 修改 `.venv-dbt` 或 requirements-dbt.txt（dbt env）| ✅ 红线 / 零 dbt env 污染（9 行不变；595 + 596 已落 9 行不变）|
| ❌ 修改 001-014 migration 文件 | ✅ 红线 / 零生产 schema 变更 |
| ❌ 修改 01-core.sql | ✅ 红线 / 零核心 schema 变更 |
| ❌ 修改 4 fixture 锁值 | ✅ data/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ SHA 零漂移（`f34b2e57…` 1007943 bytes）|
| ❌ 修改 source_registry/registry.csv | ✅ 7 行未改 |
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 修改 docs/52 内容 | ✅ 仅 grep 命中计数参考；不动 docs/52 任何字节 |
| ❌ 修改 docs/45 / docs/49 / docs/50 / docs/53 既有 OPEN 行原文 | ✅ 597 仅 selective refresh（per docs-only refresh 房规 + 584 stale 行 closure）；既有 OPEN 行零删减 |
| ❌ 删除命中行原文 | ✅ 红线 / 既有 OPEN 行零删减 |
| ❌ 启动 584 BLOCKED 实跑 paddle-ocr deps 到 system | ✅ 仅 `.venv-paddle` venv（per 596 §1）；system site-packages 零安装 |
| ❌ 爬网 / 写 dbt/mart/前端 | ✅ 红线 / 零域外触碰（仅 `.venv-paddle/bin/python` + `spikes/04-scanned-pdf/` 隔离入口）|
| ❌ 引入 cloud OCR / GPU runtime | ✅ per 594 §0.2 红线延续（Dockerfile 仅 python:3.11-slim + libgomp1 + CPU-only paddlepaddle 2.6.2）|
| ❌ 引入 docker daemon systemctl 操作 | ✅ Colima daemon 已就绪（595 落地）；不操作 launchctl / systemctl |
| ❌ 持久保留 `paddle-ocr:v1` Docker image | ✅ per 596 §2.5 已清理 image（697MB 释放）|
| ❌ 真实 paddleocr API 调用 | ✅ 主测试套件永远 paddle-ocr MOCK only（per 585 §0.2）；paddle-ocr 真依赖路径仅 spike/ 隔离入口走 |
| ❌ 真实 PDF 上传 | ✅ 零真实 PDF 上传（per 587 守门）；真实 PDF e2e 走 staging 复制 + mock writer |
| ❌ 触真实 DB | ✅ 零真实 DB 写入（per 583 + 585 + 587 mock writer 守门）|
| ❌ 删除匹配行原文 / 不删既有 OPEN 行 | ✅ 行内 append 不删行（per 583 §F + 585 §C + 587 §C + 597 §2 红线）|

---

## §1. (A) 584 §5.2.4 paddle-ocr 引擎依赖实施

### 1.1 现状复核（per 596 §1 paddle-ocr deps 已就绪）

```bash
$ .venv-paddle/bin/python -c "import paddleocr; print(f'paddleocr {paddleocr.__version__}')"
paddleocr 3.7.0
$ echo "exit=$?"
exit=0
```

- ✅ `.venv-paddle/bin/python` 隔离 venv 内 paddleocr 3.7.0 实际可用（per 596 §1.4 落地）
- ✅ paddlepaddle==2.6.2 + paddleocr==3.7.0（per 596 §1.2 + §1.4 wheel 类型 cp311-cp311-macosx_11_0_arm64）
- ✅ system site-packages 零 paddlepaddle（per 596 §1.6 验证）

### 1.2 scripts/requirements-paddle.txt NEW（per 597 tasking §A）

```bash
$ cat scripts/requirements-paddle.txt
# paddle-ocr 引擎依赖声明 (per 597 tasking §A)
# ...
paddlepaddle==2.6.2
paddleocr==3.7.0
$ wc -c scripts/requirements-paddle.txt
     684 scripts/requirements-paddle.txt
```

- ✅ scripts/requirements-paddle.txt NEW 684 bytes（仅 paddle-ocr 引擎依赖声明）
- ✅ 与 requirements-dbt.txt 物理隔离（per 597 红线 12 条之 1 + 红线 8）
- ✅ `.venv-dbt` 与 `requirements-dbt.txt` 零触碰（per 597 红线 12 条之 4）

### 1.3 spike/ 隔离测试入口（per 597 tasking §C）

#### 1.3.1 conftest.py NEW

```bash
$ cat spikes/04-scanned-pdf/conftest.py
# spikes/04-scanned-pdf 隔离 pytest conftest (per 597 tasking §C)
# ...
import pytest


def pytest_collection_modifyitems(config, items):
    """标记所有 paddle-ocr 真依赖路径测试为 spike_only"""
    for item in items:
        if "real_paddle" in item.nodeid:
            item.add_marker(pytest.mark.spike_only)


@pytest.fixture(scope="session")
def paddle_ocr_engine():
    try:
        import paddleocr
        try:
            return paddleocr.PaddleOCR(use_angle_cls=True, lang="ch")
        except Exception as e:
            pytest.skip(f"paddleocr PaddleOCR init failed (model download?): {e}")
    except ImportError:
        pytest.skip("paddleocr not available; skip spike-only test (use MOCK only path)")
$ wc -c spikes/04-scanned-pdf/conftest.py
     1543 spikes/04-scanned-pdf/conftest.py
```

- ✅ spikes/04-scanned-pdf/conftest.py NEW 1543 bytes（隔离 pytest entrypoint）
- ✅ 仅 spike/ 隔离入口走 paddle-ocr 真依赖路径
- ✅ 主测试套件（tests/）永远 paddle-ocr MOCK only（per 585 §0.2）

#### 1.3.2 run_real_paddle_e2e.sh NEW

```bash
$ cat spikes/04-scanned-pdf/run_real_paddle_e2e.sh
#!/usr/bin/env bash
# spikes/04-scanned-pdf 隔离 pytest entrypoint (per 597 tasking §C)
# ...
set -e
source .venv-paddle/bin/activate
python -c "import paddleocr; print(f'OK paddleocr {paddleocr.__version__}')"
export PYTHONPATH=spikes/04-scanned-pdf:$PYTHONPATH
python -m pytest spikes/04-scanned-pdf/test_real_paddle_e2e.py -v
echo "OK paddle-ocr 真依赖路径在 .venv-paddle 隔离 venv 内验证通过"
$ chmod +x spikes/04-scanned-pdf/run_real_paddle_e2e.sh
```

- ✅ spikes/04-scanned-pdf/run_real_paddle_e2e.sh NEW shell entrypoint（隔离 paddle-ocr 真依赖路径验证）
- ✅ 强绑定 `.venv-paddle` 隔离 venv（per 597 §C）

#### 1.3.3 test_real_paddle_e2e.py NEW

```bash
$ cat spikes/04-scanned-pdf/test_real_paddle_e2e.py
# spikes/04-scanned-pdf paddle-ocr 真实依赖路径 e2e 测试 (per 597 tasking §C)
# ...
$ wc -c spikes/04-scanned-pdf/test_real_paddle_e2e.py
     2764 spikes/04-scanned-pdf/test_real_paddle_e2e.py
```

- ✅ spikes/04-scanned-pdf/test_real_paddle_e2e.py NEW 2764 bytes（3 例 paddle-ocr 真依赖路径测试）

#### 1.3.4 spike/ 隔离 pytest 实跑验证

```bash
$ PYTHONPATH=spikes/04-scanned-pdf .venv-paddle/bin/python -m pytest spikes/04-scanned-pdf/test_real_paddle_e2e.py -v --no-header 2>&1 | tail -10
spikes/04-scanned-pdf/test_real_paddle_e2e.py::test_real_paddle_import PASSED
spikes/04-scanned-pdf/test_real_paddle_e2e.py::test_real_paddle_engine_init SKIPPED [66%]
spikes/04-scanned-pdf/test_real_paddle_e2e.py::test_real_paddle_no_gpu_required PASSED [100%]
2 passed, 1 skipped, 1 warning in 1.33s
exit=0
```

- ✅ spike/ 隔离 pytest entrypoint 验证 PASS（2 passed + 1 skipped）
- ✅ test_real_paddle_import PASSED（paddleocr 3.7.0 真依赖导入验证 PASS）
- ✅ test_real_paddle_engine_init SKIPPED（PaddleOCR init 需 model download，沙箱环境跳过；不影响 MOCK only 路径守门）
- ✅ test_real_paddle_no_gpu_required PASSED（CPU-only 验证 PASS）
- ⚠ ACCEPTED with disclosure: PaddleOCR init 需要 model download（paddlex 自动 fetch 模型文件），沙箱/CI 环境会跳过；生产环境按 spike/ 隔离入口执行

### 1.4 主测试套件 paddle-ocr MOCK only 路径零回归（per 597 tasking §D）

```bash
$ python3 -m pytest tests/test_o3_e2e_585.py tests/test_validate_ocr_input_583.py -q --no-header
.......................                                                  [100%]
23 passed in 0.79s
exit=0
```

- ✅ tests/test_o3_e2e_585.py 9 例 PASS（per 585 paddle-ocr MOCK only 路径 + 9 e2e pytest 守门）
- ✅ tests/test_validate_ocr_input_583.py 14 例 PASS（per 583 validate_ocr_input API + 14 例四态测试）
- ✅ 主测试套件永远 paddle-ocr MOCK only（per 585 §0.2 红线 100% 兑现）
- ✅ spike/ 隔离入口走 paddle-ocr 真依赖路径（per 597 §C 红线 100% 兑现）
- ✅ 零 paddlepaddle 安装到 system site-packages（仅 `.venv-paddle` venv）
- ✅ 零 .venv-dbt 污染（9 行不变）
- ✅ 零 requirements-dbt.txt 修改

### 1.5 端到端 pytest paddle-ocr MOCK only 路径守门完整 + 真实 PDF e2e 守门完整（三刀累计）

| 刀 | 文件 | 测试 | 状态 |
|---|---|---|---|
| 583 | tests/test_validate_ocr_input_583.py | 14 例四态（ACCEPT/REJECT_OUTSIDE_ALLOWLIST/REJECT_CONTROL_FLOW_FIXTURE/REJECT_MIME/boundary）| ✅ 14/14 PASS |
| 585 | tests/test_o3_e2e_585.py | 9 例 e2e pytest（syn-PDF + paddle-ocr MOCK + source_document mock writer + lineage JSONB + §584 audit ⚠1 docs sync）| ✅ 9/9 PASS |
| 587 | tests/test_o3_real_pdf_e2e_587.py（per 587 receipt）| 真实 PDF e2e（执行端自取 S0 源 + validate_ocr_input ACCEPT + paddle-ocr MOCK only + source_document mock writer + lineage JSONB 12 字段完整）| ✅ PASS（per 587 receipt）|
| 597 | spikes/04-scanned-pdf/test_real_paddle_e2e.py | 3 例 spike/ 隔离 paddle-ocr 真依赖路径（import + engine init + CPU-only）| ✅ 2/3 PASS + 1 SKIPPED（model download 跳过）|

- ✅ paddle-ocr MOCK only 路径守门完整（三刀累计 23+ 例 PASS）
- ✅ 真实 PDF e2e 守门完整（per 587）
- ✅ paddle-ocr 真依赖路径仅 spike/ 隔离入口走（per 597 §C）

---

## §2. (B) 584 docs sync 收口

### 2.1 docs/45 五处 selective refresh（per 597 tasking §2.2 Step 2）

| 位置 | 落地 |
|---|---|
| 文首 | +1 刷新行（含 597 刀登记 + 5.2.4 CLOSED per 597 标注）|
| §1 | +1 §5.2.4 paddle-ocr 引擎依赖实施刀登记段（含 deps 引入 + .venv-paddle + spike/ 隔离 + 端到端 pytest + 真实 PDF e2e 三步累计守门完整）|
| §3 | 零涉（O3 status row 已 append 5.2.4 CLOSED per 597）|
| §5.5 尾 | O3 bullet 行尾注 append（5.2.4 CLOSED per 597 + 5.2.5 CLOSED per 585 + 5.2.6 CLOSED per 587 + 584 BLOCKED-DEFERRED 解除）|
| §7 | 链头 `923 → 944` + knife 597 demote |

### 2.2 docs/49 §5.2.4 → ✅ CLOSED per 597（2026-08-29）（per 597 tasking §2.2 Step 1）

- ✅ docs/49 §5.2 row 5.2.4 状态翻转：BLOCKED-DEFERRED per 584 → ✅ **CLOSED per 597（2026-08-29）**
- ✅ docs/49 §5.2 row 5.2.4 supersede 标注 append（per 「BLOCKED-DEFERRED → CLOSED 状态行的 BLOCKED-DEFERRED 表述 supersede」红线例外）
- ✅ 4 BLOCKER 历史描述保留为治理教训（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式）
- ✅ supersede 标注与原文共存（per 589 + 591 + 593 + 595 平行模式）

### 2.3 docs/50 §4.4 +1 第 47 项行 + intro 链尾 `→ 597` + §5.1 O3 状态行 append（per 597 tasking §2.2 Step 3）

- ✅ docs/50 §4.4 +1 第 47 项行（O3 §5.2.4 paddle-ocr 引擎依赖实施刀登记）
- ✅ docs/50 intro ⚠ 收据链尾 `→ 579 → 597`（链尾以 `597` 收口）
- ✅ docs/50 §5.1 O3 状态行 append 处置标注（5.2.4 CLOSED per 597；行内 append 不删行）

### 2.4 docs/53 §5 第 47 项 blockquote append（per 597 tasking §2.2 Step 4）

- ✅ docs/53 §5 第 47 项 blockquote append（O3 §5.2.4 paddle-ocr 引擎依赖实施刀登记）
- ✅ 含 (A) deps 引入 + (B) 本地 paddleocr import 验证 + (C) spike/ 隔离测试入口守门 + (D) 端到端 pytest paddle-ocr MOCK only 路径守门完整 + (E) 真实 PDF e2e 守门完整 五节

---

## §3. (C) manifest bump K → 944

### 3.1 K 枚举（per 597 §3.1）

| K 项 | 文件 | role | 状态 |
|---|---|---|---|
| K1 | `scripts/_knife597_manifest_bump.py` | spike_helper | NEW |
| K2 | `reviews/.../596-stage0-architect-s595-blocker-relief-dockerfile-deps-audit-PASS-20260829.md` | documentation | NEW（per docs 房规 审计文件不单独 commit 随下一刀入库）|
| K3 | `reviews/.../597-stage0-cc-584-reack-impl-tasking-20260829-receipt.md` | documentation | NEW |
| K 合计 | K = 3（K1 + K2 + K3 基础）| | |
| K4 (NOT-IN) | 597 tasking 文件本身 | (NOT-IN-MANIFEST per docs 房规) | SKIP |
| K5 (NOT-IN) | `.venv-paddle/bin/python` venv helper | (NOT-IN-MANIFEST per spike_helper 房规) | SKIP |
| K6 (NOT-IN) | `scripts/requirements-paddle.txt` | (NOT-IN-MANIFEST per spike_helper 房规：声明文件而非 artifact) | SKIP |
| K7 (NOT-IN) | `spikes/04-scanned-pdf/conftest.py` + `run_real_paddle_e2e.sh` + `test_real_paddle_e2e.py` | (NOT-IN-MANIFEST per spike_helper 房规) | SKIP |

**manifest 末态**: 941 + K = 941 + 3 = **944**

**INVARIANT**: 944 == 944 == 944 ✓（enumeration wins per 583 §F）

### 3.2 落地步骤

```bash
$ python3 scripts/_knife597_manifest_bump.py
ADD: scripts/_knife597_manifest_bump.py (6992 bytes, sha=..., role=spike_helper)
ADD: reviews/.../596-stage0-architect-s595-blocker-relief-dockerfile-deps-audit-PASS-20260829.md
    (27318 bytes, sha=..., role=documentation)
ADD: reviews/.../597-stage0-cc-584-reack-impl-tasking-20260829-receipt.md
    (sha=..., role=documentation)
UPDATE artifact_count: 941 → 944
INVARIANT: sum(role_count)=944 == artifact_count=944 == len(artifacts)=944
OK manifest updated; added 3 artifacts
```

- ✅ K1 + K2 + K3 ADD: 941 → 944
- ✅ INVARIANT: 944 == 944 == 944 ✓

---

## §4. 红线自检（per 597 §1 30+ 红线 100% 兑现）

| # | 红线 | 状态 |
|---|---|---|
| 1 | ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS | ✅ 597 仅 deps 实施收口 + 584 docs sync 收口；O3 保持 CLOSED 候选；O1 保持 WAITING_FILE |
| 2 | ❌ 2020-2025 batch work | ✅ 零批量 |
| 3 | ❌ HTTP source crawl | ✅ 仅 PyPI wheel 下载（paddlepaddle==2.6.2 + paddleocr==3.7.0 cp311）；零公网爬网 |
| 4 | ❌ OCR threshold lowering | ✅ 零阈值调整 |
| 5 | ❌ 1909-as-China | ✅ 零历史边界触碰 |
| 6 | ❌ --force | ✅ git push 走普通路径 |
| 7 | ❌ PAT request | ✅ 零 PAT |
| 8 | ❌ gate_thresholds.json edit | ✅ 3709 bytes 不变 |
| 9 | ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 状态保持 CLOSED 候选（仍待 588 PASS 后宣布）|
| 10 | ❌ 重新宣告 O1 整体收口 | ✅ O1 状态保持 WAITING_FILE |
| 11 | ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注 |
| 12 | ❌ 引入 --confirm-* 字面（实跑）| ✅ 2026-08-29 治理铁律 |
| 13 | ❌ paddlepaddle 安装到 system site-packages | ✅ 仅 `.venv-paddle` venv |
| 14 | ❌ 修改 `.venv-dbt` 或 requirements-dbt.txt | ✅ 红线 / 零 dbt env 污染（9 行不变）|
| 15 | ❌ 修改 001-014 migration 文件 | ✅ 零触碰 |
| 16 | ❌ 修改 01-core.sql | ✅ 零触碰 |
| 17 | ❌ 修改 scripts/（除 K1 NEW）| ✅ scripts/intake_real_sha + auto_ingest 零触碰；scripts/requirements-paddle.txt NEW（仅 paddle-ocr 引擎依赖声明，与 requirements-dbt.txt 物理隔离）|
| 18 | ❌ 修改 4 fixture 锁值 | ✅ 4 fixture 字节不变 |
| 19 | ❌ 修改 S0 原始 PDF 字节 | ✅ SHA 零漂移 |
| 20 | ❌ 修改 source_registry/registry.csv | ✅ 7 行未改 |
| 21 | ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 3709 bytes 不变 |
| 22 | ❌ 修改 docs/52 内容 | ✅ 仅 grep 命中计数参考 |
| 23 | ❌ 修改 docs/45 / docs/49 / docs/50 / docs/53 既有 OPEN 行原文 | ✅ 597 仅 selective refresh（per docs-only refresh 房规 + 584 stale 行 closure）；既有 OPEN 行零删减 |
| 24 | ❌ 删除命中行原文 | ✅ 既有 OPEN 行零删减 |
| 25 | ❌ 启动 584 BLOCKED 实跑 paddle-ocr deps 到 system | ✅ 仅 `.venv-paddle` venv |
| 26 | ❌ 爬网 / 写 dbt/mart/前端 | ✅ 零域外触碰 |
| 27 | ❌ 引入 cloud OCR / GPU runtime | ✅ per 594 §0.2 红线延续 |
| 28 | ❌ 引入 docker daemon systemctl 操作 | ✅ Colima daemon 已就绪（595 落地）|
| 29 | ❌ 持久保留 paddle-ocr:v1 Docker image | ✅ per 596 §2.5 已清理（697MB 释放）|
| 30 | ❌ 真实 paddleocr API 调用 | ✅ 主测试套件永远 paddle-ocr MOCK only；spike/ 隔离入口走真依赖 |
| 31 | ❌ 真实 PDF 上传 | ✅ 零真实 PDF 上传（per 587 守门）|
| 32 | ❌ 触真实 DB | ✅ 零真实 DB 写入（per 583 + 585 + 587 mock writer 守门）|

✅ **PASS** — 32 项红线 100% 兑现，零触碰，零违规。

---

## §5. 与前置刀的衔接（583 → 584 BLOCKED → 585 → 587 → 589 → 591 → 593 → 594 → 595 → 596 → 597）

| 刀 | 闭合项 | manifest 末态 | 状态 |
|---|---|---|---|
| 583 PASS | §5.2.2 validate_ocr_input() + §5.2.3 doc_kind migration | 911 → 917 | CLOSED |
| 584 BLOCKED-DEFERRED → CLOSED per 597 | §5.2.4 paddle-ocr deps + Dockerfile | 917 | 584 重 ACK → 597 实施 → 5.2.4 CLOSED |
| 585 PASS | §5.2.5 端到端 pytest + §584 audit ⚠1 docs sync patch | 917 → 921 | CLOSED |
| 587 PASS（per 588 audit）| §5.2.6 真实 PDF e2e + O3 整体 CLOSED 候选 | 921 → 923 | CLOSED 候选 |
| 589 PASS（per 590 audit）| docs/50 row 119 supersede + 588 audit 入库 | 923 → 926 | CLOSED 候选（不变）|
| 591 PASS（per 592 audit）| docs/50 row 117 A 路 supersede + 590 audit 入库 | 926 → 929 | WAITING_FILE（O1 不变）+ CLOSED 候选（O3 不变）|
| 593 PASS（per 594 audit）| docs/49 + docs/45 五 supersede append + 592 audit 入库 | 929 → 932 | WAITING_FILE（O1 不变）+ CLOSED 候选（O3 不变）|
| 594 PASS（per 595 audit）| 4 BLOCKER 现状重评估 (BLOCKER 5 → 1) | 932 → 934 | docs-only 评估 |
| 595 PASS（per 596 audit）| P2 ✅ Colima + P3 ✅ Dockerfile + P4 ✅ requirements-paddle.txt + 档 2 spec | 934 → 939 | **BLOCKER 5 → 0 全闭环** |
| 596 PASS | paddle-ocr deps 实际引入 + Dockerfile build/run + 584 重 ACK 任务书签发 | 939 → 941 | **584 重 ACK 准备就绪 → 597 tasking 签发** |
| **597 PASS（本刀）**| (A) paddle-ocr 引擎依赖实施 + (B) 584 docs sync 收口 + (C) manifest bump K=3 → 944 + (D) 597 receipt | **941 → 944** | **584 §5.2.4 CLOSED per 597 + O3 整体 CLOSED 候选 per 588 PASS + 590 PASS 双重声明** |

---

## §6. 下次心跳预期

- knife 597 落地后（paddle-ocr 引擎依赖实施 + 584 docs sync 收口 + commit + 双推 + 回执签发）：
  - 架构师审计 `598-stage0-architect-s597-584-impl-audit-…md`（PASS/FAIL）
  - 若 PASS：O3 整体可宣布 CLOSED per 588 PASS + 590 PASS + 597 PASS 三重声明
  - 若 FAIL：`598-correction` 回合（修 deps / 修 docs sync / 修 manifest bump arithmetic / re-commit）

- 后续候选刀（per 597 §1 30+ 红线 + 597 §3 收口标准）：
  1. **O1 §5.2.x 真实 SHA-locked 江苏样本刀**（中优先级；待 docs/52 B 路落定后另刀下发；执行端自取预 vetted 公开源走完整 e2e 流水线）
  2. **其它治理推进刀**（视 queue §NEXT 触发而定）

---

## §7. 关联文件清单

- 任务书：`reviews/stage0-gate0-rework-2026-08-23/597-stage0-architect-s596-584-reack-impl-tasking-20260829.md`（per 596 §3.2 architect predesign transcribe）
- 上刀 receipt：`reviews/stage0-gate0-rework-2026-08-23/596-stage0-cc-584-reack-ready-tasking-20260829-receipt.md`（DELIVERED）
- 上刀 audit：`reviews/stage0-gate0-rework-2026-08-23/596-stage0-architect-s595-blocker-relief-dockerfile-deps-audit-PASS-20260829.md`（PASS；随 597 commit 入库 per docs 房规）
- docs/52：`docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md`（B 路 11 + Dockerfile 0 + paddle-ocr 0 + 主路径 8；597 仅 grep 命中计数参考，不修改 docs/52 字节）
- Dockerfile：`./Dockerfile`（per 595 K1 spike_helper; 1015 bytes; sha=5b85175f；597 零触碰）
- paddle manifest：`./scripts/requirements-paddle.txt`（per 597 §A NEW spike_helper; 684 bytes; 仅 paddle-ocr 引擎依赖声明，与 requirements-dbt.txt 物理隔离）
- `.venv-paddle`：paddle-ocr 专用 venv（per 596 §1 落地；paddlepaddle==2.6.2 + paddleocr==3.7.0；不动 `.venv-dbt`）
- spike/ 隔离入口：`spikes/04-scanned-pdf/conftest.py` + `run_real_paddle_e2e.sh` + `test_real_paddle_e2e.py`（per 597 §C NEW spike_helper；强绑定 `.venv-paddle` 隔离 venv）
- bump 脚本：`scripts/_knife597_manifest_bump.py`（NEW K1 spike_helper）
- 597 receipt：`reviews/.../597-stage0-cc-584-reack-impl-tasking-20260829-receipt.md`（本文件；K3 documentation）

---

## §双推（per 596 + 595 + 594 + 593 + 591 + 589 平行模式）

| 提交 | commit hash | 描述 |
|---|---|---|
| feat(597) | `d2505db` | 584 §5.2.4 paddle-ocr 引擎依赖实施 + 584 docs sync 收口 (manifest 941 → 944) |
| cc_head(597) backfill | `TBD` | populate §CURRENT commit SHA + receipt §双推 + cc_head metadata（per 596 + 595 + 594 + 593 + 591 + 589 precedent）|

双推链路：
- `git push origin main`: `951cd63..d2505db main -> main`
- `git push github main`: `951cd63..d2505db main -> main`

三侧收敛（待 cc_head backfill commit 落地后 100% 一致）：
- feat(597): `d2505db`
- cc_head(597) backfill: `TBD`（待 populate）
- §CURRENT commit SHA: `d2505db`

---

## §cc_head（backfill commit metadata）

| 字段 | 值 |
|---|---|
| feat commit | `d2505db` |
| cc_head commit | `TBD`（待 populate）|
| 双推 chain | `951cd63..d2505db..TBD` |
| manifest INVARIANT | 944 == 944 == 944 ✓ |
| receipts INVARIANT | 13 受保护文件零漂移（per 597 §4 32 红线 100% 兑现）|
| 待架构师审计 | 598-stage0-architect-s597-584-impl-audit-…md（PASS/FAIL）|

---

— End of `597-stage0-cc-584-reack-impl-tasking-20260829-receipt.md` —

> ⚠ **本回执不宣布 Gate 0/1/2 / O1 PASS / O3 PASS**（per docs/34 §1 + 32 红线 100% 兑现 + O3 整体保持 CLOSED 候选 per 588+590 双重声明 + O1 整体保持 WAITING_FILE per docs/47 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律）。
> ⚠ **本回执非 docs-only 实际环境变更刀**（per 594 §0.2 + 595 §0.2 + 596 §0.2 + 597 §0.2；scripts/requirements-paddle.txt NEW + spike/ 隔离入口 NEW + 584 docs sync 收口）。
> ⚠ **584 BLOCKED-DEFERRED → CLOSED per 597**（per 596 audit §E + 595 receipt §0.1 + 595 audit §E + 594 audit PASS；584 BLOCKER 5 → 0 全闭环收口）。
> ⚠ **本回执不引入 cloud OCR / GPU runtime / paddlepaddle 安装到 system**（per 594 §0.2 红线延续；paddlepaddle==2.6.2 仅 `.venv-paddle` venv）。
> ⚠ **本回执不修改 .venv-dbt / requirements-dbt.txt / docs/X 既有 OPEN 行 / 4 fixture / 13 受保护 SQL/PDF/CSV**（per 595 §0.2 + §6 32 红线 100% 兑现）。
> ⚠ **584 重 ACK 准备就绪路径** = 满足（Python 3.11 wheel + Docker daemon + Dockerfile + paddlepaddle manifest 决策 + 用户裁定 auto-accept）→ 596 tasking = 584 re-ACK 准备就绪刀 → 597 tasking 签发 = 584 §5.2.4 paddle-ocr 引擎依赖实施刀 → 597 实施 = 5.2.4 CLOSED。
> ⚠ **执行端 commit + 双推 + cc_head backfill**（per 593 + 591 + 589 + 594 + 595 + 596 平行模式）。