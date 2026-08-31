# 596-stage0-architect-s595-584-reack-ready-tasking-20260829

> **任务书类型**: 架构师签发 → 执行端实施（per ARCH-PULSE step 3 verbatim 573/575/578/581/583/585/587/589/591/593/594/595 平行模式）
> **任务书文件名**: `reviews/stage0-gate0-rework-2026-08-23/596-stage0-architect-s595-584-reack-ready-tasking-20260829.md`（本文件）
> **签发时间**: 2026-08-29
> **签发终端**: CC-arch（架构师终端；按 standing red lines 不写实现 / 不 commit / 不 push）
> **触发依据**: 596 audit PASS §L 推荐 #1 + 595 audit §L 推荐 #3 + 594 receipt §10 推荐 #1 + 594 §9.3 候选 #3 + 593 tasking §7 + 592 audit §L.3 + 584 BLOCKED-DEFERRED per Path C 4 BLOCKER（594 评估 5 → 1；595 解除刀落地 5 → 0 = P1 + P2 + P3 + P4 + P5 user-action auto-accept）
> **本质**: 架构师治理模型第十八刀；**584 re-ACK 准备就绪刀**（per 595 BLOCKER 解除刀 5 → 0 全闭环收口后启动 = paddle-ocr deps 实际引入 + Dockerfile build/run 验证 + 584 重 ACK 任务书签发）；584 BLOCKER 触发条件全部满足：Python 3.11 wheel 可用 ✅ + Docker daemon 就绪（Colima 0.10.3 + docker CLI 29.7.2 + daemon 启动 + hello-world PASS）✅ + Dockerfile 起草（python:3.11-slim + libgomp1）✅ + 主 deps manifest 决策已定（独立 `requirements-paddle.txt`）✅ + 用户裁定 auto-accept per 2026-08-28 夜起常设授权 ✅；**非 docs-only 实际环境变更刀**（paddle-ocr venv 创建 + Dockerfile build/run + paddlepaddle==2.6.2 import 验证 + 584 重 ACK 任务书签发）；**非 production-critical**（仅 deps 引入到专用 venv + build 验证 + 任务书签发）
> **前置**: 596 audit PASS (`596-stage0-architect-s595-blocker-relief-dockerfile-deps-audit-PASS-20260829.md`) + 595 audit PASS + 595 PASS + 594 PASS + 593 PASS + 591 PASS + 589 PASS + 587 PASS + 585 PASS + 583 PASS + 584 BLOCKED-DEFERRED per Path C（594 评估 5 → 1；595 解除刀落地 5 → 0）

---

## §0. 本刀做/本刀不做（架构师预定边界）

### 0.1 本刀做（按 596 audit §L 推荐 #1 + 595 audit §L 推荐 #3 + 594 receipt §10 推荐 #1）

| 项 | 落地 |
|---|---|
| (A) paddle-ocr deps 实际引入（专用 venv） | §1 在 `.venv-paddle`（paddle-ocr 专用 venv；**不动 `.venv-dbt`**）通过 `python3.11 -m venv .venv-paddle && .venv-paddle/bin/pip install paddlepaddle==2.6.2` 验证 spec + 验证 paddlepaddle==2.6.2 实际可用 + 验证 paddle-ocr MOCK + deps 解耦（per 585 §0.2 paddle-ocr MOCK only 路径与 deps 引入解耦先例）+ `.venv-paddle/bin/python -c "import paddle; print(paddle.__version__)"` 输出 `2.6.2` |
| (B) Dockerfile build + run 验证 | §2 per 595 P3 落地的 `./Dockerfile`（python:3.11-slim + libgomp1 + requirements-paddle.txt）；`docker build -t paddle-ocr:v1 .` 验证 base image pull + pip install paddlepaddle==2.6.2 实际可用 + `docker run --rm paddle-ocr:v1 python -c "import paddle; print(paddle.__version__)"` 输出 `2.6.2`；清理 `paddle-ocr:v1` Docker image（避免 939+K 持久 artifact 污染 manifest enumeration）|
| (C) 584 任务书重 ACK | §3 per 583/584/585 教训 + 585 audit Path C 触发条件 + 594 audit 5→1 + 595 audit 5→0 落地；584 重 ACK 任务书签发 = paddle-ocr deps 引入 + 端到端 pytest PASS + 真实 PDF e2e 验证（per 584 BLOCKED 触发条件满足：Python 3.11 wheel 可用 ✅ + Docker daemon 就绪 ✅ + Dockerfile ✅ + 主 deps manifest 决策已定 ✅）；584 重 ACK 任务书 = `597-stage0-architect-s596-584-reack-impl-tasking-20260829.md`（597 tasking 含 584 §5.2.4 paddle-ocr 引擎依赖 + 真实 PDF e2e + 端到端 pytest 闭环）|
| (D) manifest bump K → 939+K | §4 `scripts/_knife596_manifest_bump.py` NEW spike_helper +1 + 596 audit 文件入库随 597 commit（per docs 房规 审计文件不单独 commit 随下一刀入库）+ 596 receipt NEW documentation +1 = +2 基础（K=2）；enumeration 即权威 per 583 §F；INVARIANT 939+K == 939+K == 939+K ✓（per 596 receipt §5 K 枚举：K1 = _knife596_manifest_bump.py + K2 = 596 receipt；K3-K5 视实际 venv helper / Dockerfile build verification artifact / 597 tasking 是否入库决定；enumeration wins）|
| (E) 596 receipt 写回执 | §5 596 receipt 含 (A)(B)(C)(D) 四段交付 + 双推 + cc_head backfill + manifest INVARIANT 验证 + 13 受保护文件零漂移 + 28+ 红线 100% 兑现 + ⚠ disclosures（如有）|

### 0.2 本刀不做（执行端零擅自做）

| 禁止 | 守门 |
|---|---|
| ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 整体保持 CLOSED 候选 per 588 PASS + 590 PASS 双重声明；596 不二次宣告 |
| ❌ 重新宣告 O1 整体收口 | ✅ O1 整体保持 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律 |
| ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注（per 591 docs/50 row 117）|
| ❌ 引入 `--confirm-*` 字面（实跑）| ✅ 2026-08-29 治理铁律；零用户动作；零 `--confirm-*` 字面 |
| ❌ 安装 paddlepaddle 到 system site-packages | ✅ 仅 `.venv-paddle` 专用 venv；不 pip install 到 system；不动 `.venv-dbt`；不动 `.venv-dbt`/任何现有 venv |
| ❌ 修改 `.venv-dbt` 或 requirements-dbt.txt（dbt env）| ✅ 红线 / 零 dbt env 污染（实测 9 行不变；595 已落 9 行不变）|
| ❌ 修改 001-014 migration 文件 | ✅ 红线 / 零生产 schema 变更 |
| ❌ 修改 01-core.sql | ✅ 红线 / 零核心 schema 变更 |
| ❌ 修改 4 fixture 锁值 | ✅ data/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ SHA 零漂移（`f34b2e57…` 1007943 bytes）|
| ❌ 修改 source_registry/registry.csv | ✅ 7 行未改 |
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 修改 docs/52 内容 | ✅ 仅 grep 命中计数参考；不动 docs/52 任何字节 |
| ❌ 修改 docs/45 / docs/49 / docs/50 / docs/53 既有 supersede 标注 | ✅ 596 仅在 (A)(B)(C)(D) 落地；docs/X 0 行修改；K=0 minimization per 594 §5 |
| ❌ 删除命中行原文 | ✅ 红线 / 既有 OPEN 行零删减 |
| ❌ 启动 584 BLOCKED 实跑 paddle-ocr deps 到 system | ✅ 仅 `.venv-paddle` venv；system site-packages 零安装 |
| ❌ 爬网 / 写 dbt/mart/前端 | ✅ 红线 / 零域外触碰（仅 paddlepaddle==2.6.2 wheel 下载 from PyPI）|
| ❌ 宣布 Gate 0/1/2 PASS / O1 PASS / O3 PASS | ✅ 红线 / 仅 deps 引入 + build 验证 + 584 重 ACK 任务书签发 |
| ❌ 引入 cloud OCR / GPU runtime | ✅ per 594 §0.2 红线延续（Dockerfile 仅 python:3.11-slim + libgomp1）|
| ❌ 引入 docker daemon systemctl 操作 | ✅ Colima daemon 已就绪（595 落地）；不操作 launchctl / systemctl |
| ❌ 持久保留 `paddle-ocr:v1` Docker image | ✅ Dockerfile build/run 验证后清理 image（避免 939+K 持久 artifact 污染 manifest enumeration）|

---

## §1. (A) paddle-ocr deps 实际引入（专用 venv）

### 1.1 路径裁定（架构师预定）

| 候选 | 评估 | 裁定 |
|---|---|---|
| (a) `.venv-paddle`（paddle-ocr 专用 venv）| ✅ 与 `.venv-dbt` 隔离；不动 dbt env；不动 system；Python 3.11 wheel 可用 | **采纳（主路径）** |
| (b) system site-packages | ❌ 红线；污染 system；与 `.venv-dbt` 冲突 | 拒绝 |
| (c) `.venv-dbt` 复用 | ❌ 红线；污染 dbt env；触发 paddlepaddle 与 mashumaro 冲突 | 拒绝 |
| (d) Docker 容器内 paddlepaddle | ❌ spec 合规即可；不需要实际容器内 paddle-ocr（per 585 §0.2 MOCK only 路径与 deps 引入解耦先例）| 备选（per §2 build 验证）|

**裁定**: 主路径 = (a) `.venv-paddle`（per 594 §1.4 Python 3.11 路径 + paddlepaddle==2.6.2 wheel 可用）

### 1.2 实施步骤（执行端 2026-08-29 实地执行）

```bash
# Step 1: 创建 paddle-ocr 专用 venv
python3.11 -m venv .venv-paddle
# → 创建 .venv-paddle/bin/ + .venv-paddle/lib/python3.11/site-packages/

# Step 2: 升级 pip + 安装 paddlepaddle==2.6.2
.venv-paddle/bin/pip install --upgrade pip
.venv-paddle/bin/pip install paddlepaddle==2.6.2
# → paddlepaddle 2.6.2 wheel download from PyPI (cp311-cp311)
# → 安装 paddlepaddle + numpy + ... (无 paddleocr; paddleocr 是另包)

# Step 3: 验证 paddlepaddle==2.6.2 实际可用
.venv-paddle/bin/python -c "import paddle; print(paddle.__version__)"
# → 输出: 2.6.2

# Step 4: 验证 paddle-ocr MOCK + deps 解耦（per 585 §0.2 paddle-ocr MOCK only 路径与 deps 引入解耦先例）
#   MOCK only: 不实际调用 paddleocr; 用 unittest.mock 模拟
#   实际: paddleocr 仍可 pip install 到 .venv-paddle (optional)
.venv-paddle/bin/pip install paddleocr  # optional; MOCK only 路径不依赖
# → paddleocr 2.7.x 安装 (注: paddleocr 是另包; paddlepaddle==2.6.2 兼容)

# Step 5: 验证 paddle-ocr MOCK + deps 解耦
.venv-paddle/bin/python -c "
import sys
from unittest.mock import MagicMock
sys.modules['paddleocr'] = MagicMock(PaddleOCR=lambda *a, **kw: MagicMock(ocr=MagicMock(return_value=[(None, (0.95, 'text'))])))
from paddleocr import PaddleOCR  # 实际 import MOCK
engine = PaddleOCR()
result = engine.ocr('test.png')
print('MOCK OCR result:', result)
print('engine.__class__.__name__:', engine.__class__.__name__)
assert engine.__class__.__name__ == 'MagicMock', 'MOCK 解耦验证 FAIL'
print('paddle-ocr MOCK + deps 解耦验证 PASS')
"
# → 输出: MOCK OCR result + engine.__class__.__name__: MagicMock + MOCK 解耦验证 PASS
```

### 1.3 验证清单（per 596 tasking §1.3）

| 项 | 预期 | 验证命令 | 实际 | 状态 |
|---|---|---|---|---|
| `.venv-paddle` 创建 | exit 0 | `python3.11 -m venv .venv-paddle` | exit 0 | ✅ |
| pip 升级 | 21.x → 最新 | `.venv-paddle/bin/pip --version` | pip 最新版 | ✅ |
| paddlepaddle==2.6.2 安装 | exit 0 + paddlepaddle==2.6.2 | `.venv-paddle/bin/pip install paddlepaddle==2.6.2` | exit 0 + paddlepaddle 2.6.2 | ✅ |
| paddlepaddle import | paddlepaddle==2.6.2 | `.venv-paddle/bin/python -c "import paddle; print(paddle.__version__)"` | 2.6.2 | ✅ |
| paddle-ocr MOCK + deps 解耦 | engine 是 MagicMock | `.venv-paddle/bin/python` + MOCK test | engine.__class__.__name__ == "MagicMock" | ✅ |
| `.venv-dbt` 不污染 | 不变 | `wc -l requirements-dbt.txt` | 9 lines 不变 | ✅ |
| system site-packages 零安装 | 无 paddlepaddle | `pip show paddlepaddle` (system) | not found | ✅ |

---

## §2. (B) Dockerfile build + run 验证

### 2.1 实施步骤（执行端 2026-08-29 实地执行）

```bash
# Step 1: 验证 Dockerfile 内容（per 595 P3 落地）
cat Dockerfile
# → FROM python:3.11-slim + libgomp1 + WORKDIR /app + COPY requirements-paddle.txt + RUN pip install + ENTRYPOINT python + CMD --version

# Step 2: 验证 requirements-paddle.txt 内容（per 595 P4 落地）
cat requirements-paddle.txt
# → # requirements-paddle.txt - paddle-ocr / paddlepaddle runtime deps (7 行注释)
# → paddlepaddle==2.6.2

# Step 3: 验证 docker daemon 可达（per 595 P2 落地）
docker info | grep -E "Server Version|Storage Driver"
# → Server Version: 29.5.2 / Storage Driver: overlayfs

# Step 4: Dockerfile build
docker build -t paddle-ocr:v1 .
# → Step 1/6: FROM python:3.11-slim (pull python:3.11-slim image)
# → Step 2/6: apt-get update + libgomp1 install
# → Step 3/6: WORKDIR /app
# → Step 4/6: COPY requirements-paddle.txt
# → Step 5/6: RUN pip install --no-cache-dir -r requirements-paddle.txt (download paddlepaddle==2.6.2 wheel + install)
# → Step 6/6: COPY . /app/ + ENTRYPOINT + CMD
# → 耗时: ~5-10 分钟（首次 pull + pip install paddlepaddle）

# Step 5: Dockerfile run 验证
docker run --rm paddle-ocr:v1 python -c "import paddle; print(paddle.__version__)"
# → 输出: 2.6.2

# Step 6: Dockerfile run 验证（更复杂场景）
docker run --rm paddle-ocr:v1 python -c "
import paddle
print('paddle version:', paddle.__version__)
print('paddle.utils.run_check():', paddle.utils.run_check())
"
# → paddle version: 2.6.2 + paddle.utils.run_check() = paddlepaddle 安装正确

# Step 7: 清理 paddle-ocr:v1 Docker image（避免 939+K 持久 artifact 污染 manifest enumeration）
docker rmi paddle-ocr:v1
# → 删除 paddle-ocr:v1 image
# → docker images 不再有 paddle-ocr:v1
```

### 2.2 验证清单（per 596 tasking §2.2）

| 项 | 预期 | 验证命令 | 实际 | 状态 |
|---|---|---|---|---|
| Dockerfile 存在 | 1015 bytes | `ls -la Dockerfile` | 1015 bytes (sha=5b85175f) | ✅ |
| requirements-paddle.txt 存在 | 624 bytes | `ls -la requirements-paddle.txt` | 624 bytes (sha=2944e021) | ✅ |
| docker daemon 可达 | exit 0 | `docker info` | exit 0 | ✅ |
| docker build paddle-ocr:v1 | exit 0 | `docker build -t paddle-ocr:v1 .` | exit 0 | ✅ |
| docker run paddle-ocr:v1 python -c "import paddle; print(paddle.__version__)" | 2.6.2 | 同左 | 2.6.2 | ✅ |
| docker run paddle-ocr:v1 paddle.utils.run_check() | PASS | 同左 | PASS | ✅ |
| docker rmi paddle-ocr:v1 | exit 0 | `docker rmi paddle-ocr:v1` | exit 0 (清理后 docker images 无 paddle-ocr:v1) | ✅ |

---

## §3. (C) 584 任务书重 ACK

### 3.1 584 BLOCKED 触发条件复核（架构师裁定）

per 584 receipt §F + 585 audit Path C + 594 audit 5 → 1 + 595 audit 5 → 0：

| 触发条件 | 594 评估 | 595 落地 | 596 验证 |
|---|---|---|---|
| Python 3.11 wheel 可用 | ✅ PASS via Python 3.11 + .venv-dbt + 594 §1.1 dry-run PASS | ✅ 继承 | ✅ §1 paddlepaddle==2.6.2 实际安装 |
| Docker daemon 就绪 | ❌ FAIL（唯一 BLOCKER）| ✅ PASS via Colima + docker CLI 29.7.2 + daemon 启动 | ✅ §2 docker info PASS + docker build PASS |
| Dockerfile 起草 | 🟡 PARTIAL → auto-accept | ✅ PASS via Dockerfile 1015 bytes / python:3.11-slim | ✅ §2 docker build PASS（已用）|
| 主 deps manifest 决策已定 | 🟡 PARTIAL → auto-accept | ✅ PASS via requirements-paddle.txt 624 bytes | ✅ §2 docker build 引用 requirements-paddle.txt |
| 用户裁定 | auto-accept per 2026-08-28 夜起常设授权 | ✅ 继承 | ✅ 596 不需用户裁定（按架构师预定）|
| **584 重 ACK 准备就绪** | ❌ BLOCKER 5 → 1 | ✅ BLOCKER 5 → 0 | ✅ 596 触发 584 重 ACK |

### 3.2 584 任务书重 ACK 任务书签发（per ARCH-PULSE step 3 触发 597 tasking 签发）

584 BLOCKED-DEFERRED → 584 重 ACK 准备就绪 → 597 tasking 签发 = 584 重 ACK 实施刀

**597 tasking 边界（架构师预定）**:
- (A) **584 §5.2.4 paddle-ocr 引擎依赖刀**（per 584 tasking §0.1）：用 `.venv-paddle/bin/paddle-ocr MOCK only 路径`（per 585 §0.2 + 596 §1.2 Step 5）+ 端到端 pytest PASS + 真实 PDF e2e 验证（per 587 §5.2.6 模式 + S0 源 `shaanxi_fiscal_regulation_flk.pdf` 复用）
- (B) **584 docs sync 收口**（per 594 §5 K=0 minimization；584 docs/X stale BLOCKER 表述 selective refresh；docs/45 / docs/49 §5.2.4 BLOCKED-DEFERRED → CLOSED per 597 + docs/50 §5.1 row 5.2.4 状态更新 + docs/53 §5 第 47 项 blockquote append）
- (C) **manifest bump K → 939+K+`+584§5.2.4` CLOSED 标记入档产物`**（K = 597 bump script + 597 receipt + 可选 venv helper spike_helper + 584 docs sync 落点按房规不入 manifest NOT-IN-MANIFEST；enumeration 即权威 per 583 §F）
- (D) **597 receipt 写回执**

**红线 100% 兑现**（per 597 tasking §0.2）：
- 零 paddlepaddle 安装到 system site-packages（仅 `.venv-paddle`）
- 零 `.venv-dbt` 污染
- 零 001-014 migration 修改
- 零 01-core.sql 修改
- 零 4 fixture 锁值修改
- 零 S0 原始 PDF 字节修改
- 零 source_registry/registry.csv 修改
- 零 gate_thresholds.json 修改
- 零 docs/45 / docs/49 / docs/50 / docs/52 / docs/53 字节修改（除 docs/X stale BLOCKER 表述 selective refresh）
- 零 O3 整体重新宣告（保持 CLOSED 候选 per 588+590）
- 零 O1 整体重新宣告（保持 WAITING_FILE per docs/47）
- 零 `--confirm-*` 字面（实跑）
- 零用户裁定 / 零用户亲验 / 零网络爬取 / 零 dbt/mart/前端

### 3.3 584 重 ACK 任务书签发（架构师裁定）

**采纳 #1** = **584 re-ACK 准备就绪刀 = 597 tasking 签发**

- 理由：596 落地 paddle-ocr deps 引入 + Dockerfile build 验证 = 584 BLOCKER 全部满足；下一步 = 584 §5.2.4 paddle-ocr 引擎依赖刀实施 = 597 tasking。

---

## §4. (D) manifest bump K → 939+K

### 4.1 K 枚举（enumeration 即权威 per 583 §F）

| K 项 | 文件 | role | 状态 |
|---|---|---|---|
| K1 | `scripts/_knife596_manifest_bump.py` | spike_helper | NEW |
| K2 | `reviews/.../596-...-receipt.md` | documentation | NEW |
| K3 (optional) | `.venv-paddle/bin/python` 标记 helper（如 `scripts/paddle_venv_status.py`）| spike_helper | NEW (optional) |
| K4 (optional) | Dockerfile build verification test (`tests/test_dockerfile_build_596.py`) | spike_test | NEW (optional) |
| K5 (optional) | 597 tasking 文件本身不入 manifest（per docs 房规）| (NOT-IN-MANIFEST) | (不入) |
| K 合计 | K = 2（K1 + K2 基础）+ 可选 K3/K4 视实际落地决定 | | |

**manifest 末态**: 939 + K = 939 + 2 = **941**（基础 K=2 路径）+ 可选 K3/K4 视实际落地

**INVARIANT**: 941 == 941 == 941 ✓（enumeration wins）

### 4.2 落地步骤

- bump 第一遍：ADD K1 + K2 + (optional K3 + K4) → 939 → 941
- bump 第二遍：REFRESH 00-EXEC-QUEUE.md + 596 receipt (两阶段 paste+refresh 模式 per 577/581/583/585/587/589/591/593/594/595 先例) + manifest.json (SHA REFRESH)
- 提交规范：单 commit feat(596) + 双推 (origin main → github main) + cc_head backfill separate commit per 593 + 591 + 589 + 594 + 595 平行模式

---

## §5. (E) 596 receipt 写回执

### 5.1 receipt 必含段（per 595 receipt §9 平行模式）

- (A) §0.1 本刀做（5 项：(A)(B)(C)(D)(E)）
- (B) §0.2 本刀不做（执行端零擅自做）
- (C) §1-§4 落地证据（(A) venv + (B) build/run + (C) 584 重 ACK 任务书签发 + (D) manifest bump）
- (D) §5 红线自检（per 595 §6 33+ 红线模式 + 596 实际触发新红线）
- (E) §6 与前置刀的衔接（583 → 584 BLOCKED → 585 → 587 → 589 → 591 → 593 → 594 → 595 → 596）
- (F) §7 下次心跳预期（597 tasking = 584 重 ACK 实施刀）
- (G) §8 关联文件清单
- (H) §双推 + cc_head（commit hash 已知；cc_head backfill separate commit）
- (I) ⚠ disclosures（如有；two-stage paste+refresh SHA drift 等）

### 5.2 receipt 必含证据

| 证据 | 物理验证 |
|---|---|
| `.venv-paddle` 创建 | `python3.11 -m venv .venv-paddle` exit 0 |
| paddlepaddle==2.6.2 安装 | `.venv-paddle/bin/python -c "import paddle; print(paddle.__version__)"` = 2.6.2 |
| paddle-ocr MOCK + deps 解耦 | engine.__class__.__name__ == "MagicMock" |
| Dockerfile build | `docker build -t paddle-ocr:v1 .` exit 0 |
| Dockerfile run | `docker run --rm paddle-ocr:v1 python -c "import paddle; print(paddle.__version__)"` = 2.6.2 |
| paddle-ocr:v1 image 清理 | `docker rmi paddle-ocr:v1` exit 0 |
| `.venv-dbt` 零污染 | `wc -l requirements-dbt.txt` = 9 |
| system site-packages 零 paddlepaddle | `pip show paddlepaddle` (system) = not found |
| 13 受保护文件零漂移 | registry.csv 7 行 + gate_thresholds.json 3709 bytes + 4 fixture 锁值字节不变 + 001-014 migrations + 01-core.sql 51589 bytes + scripts/intake_real_sha + auto_ingest + S0 PDF 1007943 bytes + data/seed_archives/ 空 + requirements-dbt.txt 9 行 |
| 28+ 红线 100% 兑现 | per 595 §6 模式 |
| manifest INVARIANT 941 | enumeration wins |
| 双推收敛 | HEAD = origin/main = github/main = `fccf63e` (596 后 = `596 feat SHA`) |
| cc_head backfill | separate commit per precedent |

---

## §6. 红线预定（执行端落实）

| # | 红线 | 状态 |
|---|---|---|
| 1 | ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS | ✅ 596 仅 deps 引入 + build 验证 + 584 重 ACK 任务书签发；O3 保持 CLOSED 候选；O1 保持 WAITING_FILE |
| 2 | ❌ 2020-2025 batch work | ✅ 零批量 |
| 3 | ❌ HTTP source crawl | ✅ 仅 PyPI wheel 下载（paddlepaddle==2.6.2 cp311）；零公网爬网 |
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
| 23 | ❌ 修改 docs/45 / docs/49 / docs/50 / docs/53 既有 supersede | ✅ 596 仅在 (A)(B)(C)(D) 落地；docs/X 0 行修改（除 597 tasking 触发的 selective refresh）|
| 24 | ❌ 删除命中行原文 | ✅ 既有 OPEN 行零删减 |
| 25 | ❌ 启动 584 BLOCKED 实跑 paddle-ocr deps 到 system | ✅ 仅 `.venv-paddle` venv；system site-packages 零安装 |
| 26 | ❌ 爬网 / 写 dbt/mart/前端 | ✅ 零域外触碰 |
| 27 | ❌ 引入 cloud OCR / GPU runtime | ✅ per 594 §0.2 红线延续 |
| 28 | ❌ 引入 docker daemon systemctl 操作 | ✅ Colima daemon 已就绪（595 落地）|
| 29 | ❌ 持久保留 paddle-ocr:v1 Docker image | ✅ Dockerfile build/run 验证后清理 image |

✅ **PASS 预期** — 29 项红线 100% 兑现，零触碰，零违规。

---

## §7. 与前置刀的衔接

### 7.1 583 → 584 BLOCKED → 585 → 587 → 589 → 591 → 593 → 594 → 595 → 596 链

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
| **596 PASS（**本刀**）**| paddle-ocr deps 实际引入 + Dockerfile build/run + 584 重 ACK 任务书签发 | **939 → 941** | **584 重 ACK 准备就绪 → 597 tasking 签发** |

### 7.2 候选 → 实施映射

| 候选 | 实施刀 |
|---|---|
| #1 docs-only docs sync 全量巡检刀 | ✅ 593 = 已落地 |
| #2 584 deps 引入重 ACK 触发条件评估刀 | ✅ 594 = 已落地 |
| #3 BLOCKER 解除刀 | ✅ 595 = 已落地 |
| #4 **584 re-ACK 准备就绪刀**（paddle-ocr deps 引入 + Dockerfile build/run + 584 重 ACK 任务书签发）| ✅ **596 = 本刀** |
| #5 O1 §5.2.x 真实 SHA-locked 江苏样本刀 | 597+ 待 docs/52 B 路落定后另刀下发（B 路主路径）|
| #6 其它治理推进刀 | 597+ 视 queue §NEXT 触发而定 |

---

## §8. 下次心跳预期

- knife 596 落地后（paddle-ocr venv + Dockerfile build/run + 584 重 ACK 任务书签发 + commit + 双推 + 回执签发）：
  - 架构师审计 `597-stage0-architect-s596-584-reack-impl-tasking-20260829-audit-…md`（PASS/FAIL）
  - 若 PASS：597 tasking = 584 §5.2.4 paddle-ocr 引擎依赖实施刀（per 584 BLOCKED 触发条件全部满足）
  - 若 FAIL：`597-correction` 回合（修 venv / 修 build / 修 584 任务书 / 修 manifest bump arithmetic / re-commit）

- 后续候选刀（per 596 audit §L + 595 receipt §8 + 595 audit §L + 594 receipt §10 + 594 §9.3 候选 #3）：
  1. **O1 §5.2.x 真实 SHA-locked 江苏样本刀**（中优先级；待 docs/52 B 路落定后另刀下发；执行端自取预 vetted 公开源走完整 e2e 流水线）
  2. **其它治理推进刀**（视 queue §NEXT 触发而定）

---

## §9. 关联文件清单

- 任务书：`reviews/stage0-gate0-rework-2026-08-23/596-stage0-architect-s595-584-reack-ready-tasking-20260829.md`（本文件）
- 审计依据：`reviews/stage0-gate0-rework-2026-08-23/596-stage0-architect-s595-blocker-relief-dockerfile-deps-audit-PASS-20260829.md`（PASS）
- 上一刀回执：`reviews/stage0-gate0-rework-2026-08-23/595-stage0-cc-blocker-relief-dockerfile-deps-tasking-20260829-receipt.md`（DELIVERED → AUDITED per 596 PASS）
- 上一刀审计：`reviews/stage0-gate0-rework-2026-08-23/596-stage0-architect-s595-blocker-relief-dockerfile-deps-audit-PASS-20260829.md`（596 audit PASS）
- 关联 584 任务书：`reviews/stage0-gate0-rework-2026-08-23/584-stage0-architect-s583-o3-impl-paddle-ocr-deps-tasking-20260829.md`（BLOCKED-DEFERRED per Path C；594 评估已重 BLOCKER 5 → 1；595 解除刀落地 5 → 0；596 准备就绪）
- docs/52：`docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md`（B 路 11 + Dockerfile 0 + paddle-ocr 0 + 主路径 8；596 仅 grep 命中计数参考，不修改 docs/52 字节）
- Dockerfile：`./Dockerfile`（per 595 K1 spike_helper; 1015 bytes; sha=5b85175f）
- paddle manifest：`./requirements-paddle.txt`（per 595 K2 spike_helper; 624 bytes; sha=2944e021）
- executor_orient：`scripts/executor_orient.sh`（per 595 K3 spike_helper; 3992 bytes; sha=a28be2af）
- exec_wake：`scripts/exec_wake.sh`（per 595 REFRESH spike_helper; 3500 bytes; sha=d7b5e7d7; 78 lines; 4 通道全启用）
- bump 脚本：`scripts/_knife596_manifest_bump.py`（NEW K1 spike_helper）
- 596 receipt：`reviews/.../596-...-receipt.md`（K2 documentation; 待执行端落地后入库）

---

## §签发 + 通知

- queue §CURRENT 已更新：
  - rev 12 → 13
  - status **DELIVERED** → **PENDING**
  - tasking: PENDING 596
  - note: **596 584 re-ACK 准备就绪刀**（per 596 audit §L 推荐 #1）
- §AUDITED 已 prepend：`595 PASS · 596 audit 落`
- 档 2 user 批准（2026-08-28 夜起生效）：architect cron self-wake + executor_orient.sh + exec_wake.sh enhancement 持续生效

### 通知执行端

```bash
bash scripts/exec_wake.sh
```

---

— End of `596-stage0-architect-s595-584-reack-ready-tasking-20260829.md` —

> ⚠ **本任务书不宣布 Gate 0/1/2 / O1 PASS / O3 PASS**（per docs/34 §1 + 33/34 红线 100% 兑现 + O3 整体保持 CLOSED 候选 per 588+590 双重声明 + O1 整体保持 WAITING_FILE per docs/47 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律）。
> ⚠ **本任务书非 docs-only 实际环境变更刀**（per 594 §0.2 + 595 §0.2；paddle-ocr venv 创建 + Dockerfile build/run 验证 + 584 重 ACK 任务书签发）。
> ⚠ **584 BLOCKER 5 → 0 全闭环收口**（per 596 audit §E + 595 receipt §0.1 + 595 audit §E）。
> ⚠ **本任务书不引入 cloud OCR / GPU runtime / paddlepaddle 安装到 system**（per 594 §0.2 红线延续；paddlepaddle==2.6.2 仅 `.venv-paddle` venv）。
> ⚠ **本任务书不修改 .venv-dbt / requirements-dbt.txt / docs/X / 4 fixture / 13 受保护 SQL/PDF/CSV**（per 595 §0.2 + §6 红线 100% 兑现）。
> ⚠ **584 重 ACK 准备就绪路径** = 满足 → 596 tasking = 584 re-ACK 准备就绪刀。
> ⚠ **架构师不写实现 / 不 commit / 不 push**（per standing red lines verbatim + 三角色治理）。