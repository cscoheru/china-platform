# 584 — Stage 0 / CC receipt: paddle-ocr 引擎依赖刀 = **BLOCKED by 环境约束**

> 起草：CC（执行端）· 2026-08-29 · 跟单触发「584已发」
> 前置：`584-stage0-architect-s583-o3-impl-validate-api-doc-kind-audit-PASS-20260829`（583 审计 PASS）
> 任务书：`584-stage2-paddle-ocr-deps-tasking-20260829`
> 性质：**BLOCKED by 环境约束**（见 §ENV-BLOCKERS；不强行 partial 执行）

---

## §ENV-BLOCKERS（硬约束 — 必须 架构师修订任务书方可继续）

### BLOCKER-1: paddlepaddle 无 Python 3.14 wheel（hard env）

| 项 | 实测 |
|---|---|
| Python version | 3.14.3 |
| `pip3 index versions paddleocr` | ✅ 3.7.0 / 3.6.0 / ... / 2.7.0.3 / ...（多版本可用）|
| `pip3 index versions paddlepaddle` | ❌ **ERROR: No matching distribution found for paddlepaddle** |

**影响**：584 §A paddlepaddle deps append → `pip install paddlepaddle` 失败（Python 3.14 wheel 缺失；paddlepaddle 最新支持通常到 Python 3.12）。

**决议**：本沙箱**无法安装** paddlepaddle = 无法满足 §A 红线前提 + §F 验证命令 `python3 -c "import paddlepaddle; print(...)"` 必 fail。

### BLOCKER-2: 项目无 Dockerfile（zero baseline）

| 项 | 实测 |
|---|---|
| `find . -name 'Dockerfile*' -maxdepth 4` | **No matches**（排除 node_modules / .venv）|
| `find . -name 'requirements.txt' -maxdepth 4` | **仅 `requirements-dbt.txt`**（dbt 专用；非项目主 deps）|
| `find . -name 'pyproject.toml' -maxdepth 4` | **No matches** |
| `find . -name 'setup.py' -maxdepth 4` | **No matches** |

**影响**：584 §B 「Dockerfile paddle-ocr 独立 layer」**前提不成立**（无 base image 可叠加 layer；"独立 layer" 必须有既有 FROM 基线）。
红线条文：「不修改既有 FROM / RUN apt-get / RUN pip install <既有 deps> 段」隐含既有 image；zero baseline = 不能"layer 增量"，只能 NEW FROM scratch（deviates 任务书字面）。

**决议**：584 §B 在 zero-baseline 项目需重写为「NEW Dockerfile FROM scratch + paddle-ocr 段」；任务书未授权此路径。

### BLOCKER-3: Docker daemon 不可用（env）

| 项 | 实测 |
|---|---|
| `which docker` | ❌ docker not found |
| `docker build` / `docker history` | ❌ 命令不可用 |

**影响**：584 §B 镜像 build 验证（`docker build -t <project-app>:test-584 .`）**无法执行** = 「完成定义」中"Dockerfile build exit 0"硬指标无法满足。

**决议**：镜像 build 验证需独立 Docker 主机；本沙箱**无 Docker daemon**。

### BLOCKER-4: requirements.txt / pyproject.toml 主 manifest 缺失

| 项 | 实测 |
|---|---|
| `ls requirements.txt pyproject.toml` | ❌ No such file |

**影响**：584 §A 「`requirements.txt` 或 `pyproject.toml` — deps append」前提不成立（无 deps manifest 可 append；只有 dbt 子集 `requirements-dbt.txt`，非项目主 deps manifest）。

**决议**：584 §A 需先决定 deps manifest 路径（创 NEW requirements.txt？改 `requirements-dbt.txt`？设 NEW pyproject.toml？）；任务书未指定新建 vs append。

---

## §决议（per executor protocol 「不强行 partial 执行」）

584 **BLOCKED** — 不写入 paddle-ocr deps / 不创建 Dockerfile / 不创建 584 test file / 不跑 584 pytest（避免 §E manifest 923 invariant 偏差 + 红线 100% 兑现前提破缺）。

**已落地（最小执行证据）**：
- §CURRENT status PENDING → ACK（认领 + 立即勘察 env）
- §CURRENT note append env constraints（架构师可见）
- 本 receipt 落地（文档化 BLOCKER 1–4 + 决议）

**未落地（待 架构师修订任务书后执行）**：
- ❌ `requirements.txt` / `pyproject.toml` paddle-ocr deps append（BLOCKER-1 + BLOCKER-4）
- ❌ `Dockerfile` paddle-ocr 独立 layer（BLOCKER-2 + BLOCKER-3）
- ❌ `tests/test_paddle_ocr_deps_584.py` 7+ 例测试（BLOCKER-1 import 不可验证）
- ❌ manifest bump（deps / Dockerfile / test = +3 文件不可落地 = bump 不能达 +6 invariant；partial +3 = 920 偏差任务书）
- ❌ 双推（无 commit 内容）
- ❌ cc_head（无 commit）

**docs sync patch（§D）**：docs/45 L93 + L487 + docs/53 L203 + L207 + docs/50 L228 五处 916 → 917 修正 **未执行**（任务书 §D 与 BLOCKED 决议互斥；docs/45 / docs/53 / docs/50 属 ARCHITECT'S tasking-scope，本 receipt 视 docs sync 为任务书修订后的重新执行项）。

---

## §架构师修订路径建议（per executor → 架构师回执）

### 选项 A：环境就绪后 retry 584（推荐）

1. 架构师确认执行端升级 Python 至 3.12（paddlepaddle wheel 兼容上限）+ 安装 Docker Desktop（macOS native）
2. 任务书修订：明确 deps manifest 主文件路径（如 NEW `requirements.txt` vs `requirements-dbt.txt` 改主）
3. 任务书修订：明确 Dockerfile 路径（NEW vs append to infra/Dockerfile）
4. 执行端按修订后任务书重 ACK 重跑

### 选项 B：拆分 584 为 3 个 sub-knife

1. **584a**: deps-only knife（requirements.txt NEW + paddle-ocr deps；零 Dockerfile；零 import 验证 = dry-run `pip install --dry-run`）
2. **584b**: Dockerfile-only knife（infra/Dockerfile NEW；零 docker build 验证 = docker daemon 升级后补）
3. **584c**: tests-only knife（test_paddle_ocr_deps_584.py NEW；imports 在 deps 落 + Docker daemon 升级后实跑）

### 选项 C：暂缓 584，优先 §5.2.5 / §5.2.6

1. 584 暂缓（环境就绪后再开）
2. 优先 585 = §5.2.5 e2e pytest 刀（合成扫描 fixture / syn-PDF 守门；与 paddle-ocr deps 解耦）
3. 586+ = §5.2.6 真实 PDF `--confirm-o3=PATH` 用户保留动作刀

---

## §红线 100% 兑现（per 584 §红线）

- ✅ **不强行 partial 执行**：4 BLOCKER 全部报告，不写 paddle-ocr deps / Dockerfile / 584 test（避免 invariant 偏差 + 红线前提破缺）
- ✅ **不引入 cloud OCR**（paddle-ocr = local-only；BLOCKED 前未触）
- ✅ **不引入 GPU runtime**（未触）
- ✅ **不写真实 OCR pipeline 集成**（未触；584 仅 deps + import 验证，BLOCKED 后未实跑）
- ✅ **不写真实 PDF fixture 处理**（未触）
- ✅ **不修改 migration 001-014**（未触；migration 014 doc_kind 583 落）
- ✅ **不修改 schema/01-core.sql**（未触）
- ✅ **不修改 scripts/auto_ingest_public_source.py / intake_real_sha_if_present.py**（未触）
- ✅ **不修改 4 fixture 字节 / data/seeds/ / spikes/**（未触）
- ✅ **不爬网 / 不 cloud OCR / 不 HTTP 出站**（仅 `pip index versions` = PyPI metadata 查询，非 OCR / non-paddle-ocr 模型下载）
- ✅ **不写 dbt / mart / 前端任何文件**（未触）
- ✅ **不宣布 Gate 0/1/2 PASS**（未触）
- ✅ **不 --force / PAT / 公网 redeploy**（未触）
- ✅ **既有 OPEN 行零删减**（未触）

---

## §next heartbeat 预期

- 架构师收本回执 + 4 BLOCKER 详单 → 修订任务书（A/B/C 任一）
- 修订后执行端 ACK 修订版重跑
- 若选 C：584 暂缓 → 585 e2e pytest 刀 优先签发

---

## §交付证据

- **status**: §CURRENT **ACK → DELIVERED（BLOCKED）** — 交付本 receipt 即可，不双推（无 commit 内容）
- **cc_head**: NONE（无 commit）
- **回执文件**: `reviews/stage0-gate0-rework-2026-08-23/584-stage0-cc-paddle-ocr-deps-tasking-20260829-receipt.md`（本文件）
- **manifest 不动**: 917 = 917 = 917 不变量保持（无 bump）

---

— End of `584-stage0-cc-paddle-ocr-deps-tasking-20260829-receipt.md` (BLOCKED) —
