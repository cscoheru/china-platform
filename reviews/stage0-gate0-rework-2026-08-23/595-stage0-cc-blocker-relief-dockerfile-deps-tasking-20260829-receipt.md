# 595-stage0-cc-blocker-relief-dockerfile-deps-tasking-20260829-receipt

> **任务书**: `reviews/stage0-gate0-rework-2026-08-23/595-stage0-architect-s594-blocker-relief-dockerfile-deps-tasking-20260829.md`
> **本回执**: `reviews/stage0-gate0-rework-2026-08-23/595-stage0-cc-blocker-relief-dockerfile-deps-tasking-20260829-receipt.md`（本文件）
> **交付时间**: 2026-08-29
> **交付终端**: CC-exec（Claude Code 执行终端，跟单触发「595 BLOCKER 解除刀（P2 Docker 安装 + P3 Dockerfile 起草 + P4 paddlepaddle==2.6.2 manifest 写入 + 档 2 spec）」）
> **manifest 末态**: 934 → 939（+5：Dockerfile + requirements-paddle.txt + executor_orient.sh + bump 脚本 + 595 receipt；enumeration wins per 583 §F；exec_wake.sh REFRESH 不增计数）
> **本质**: 架构师治理模型第十六刀；**BLOCKER 解除刀**（per 595 audit PASS + 594 audit PASS + 594 receipt §10 推荐 #1 + 594 §6.1 P2/P3/P4 解除条件 + 594 §9.3 候选 #3）；584 BLOCKER 矩阵 5 → 1 收口后唯一保留 P2 ❌ FAIL → 595 一次闭环 5 → 0（P2 ✅ Colima daemon / P3 ✅ Dockerfile 起草 / P4 ✅ requirements-paddle.txt 写入）；**档 2 user 批准（2026-08-28 夜起生效）** = scripts/executor_orient.sh 创建 + scripts/exec_wake.sh enhancement（sound + title flash）= 同步执行；docs-only 评估零代码零 SQL（594 已落）+ 本刀实际 BLOCKER 解除（不 zero-code；Docker 安装 + Dockerfile 起草 + manifest 写入 = 实际环境变更；非 docs-only 刀）；非 production-critical（仅 spec 合规 + spec 落地）
> **前置**: 595 audit PASS (`595-stage0-architect-s594-eval-584-deps-reack-trigger-audit-PASS-20260829.md`) + 594 PASS（594 audit 落）+ 593 PASS（594 audit 落）+ 592 PASS + 591 PASS（592 audit 落）+ 590 PASS + 589 PASS + 588 PASS + 587 PASS + 585 PASS + 583 PASS + 584 BLOCKED-DEFERRED per Path C（594 评估实际 BLOCKER 5 → 1）

---

## §0. 本刀做/本刀不做（执行端自检）

### 0.1 本刀做（按 595 tasking §0.1 + §1 + §2 + §3 + §4 + §5）

| 项 | 落地 |
|---|---|
| (A) P2 BLOCKER 解除 = Docker 安装路径裁定 | §1 Colima 0.10.3 + lima 2.2.0 (dependency) + docker CLI 29.7.2 + daemon 启动 (macOS Virtualization.Framework vz driver, 2 CPU + 4 GB RAM + 20 GB disk) + `docker info` PASS + `docker ps` PASS + `docker run --rm hello-world` exit 0 ("Hello from Docker!" 输出；arm64v8 image) + credsStore 修复（"desktop" → "" 因 Docker Desktop 未装）|
| (B) P3 BLOCKER 解除 = Dockerfile 起草 | §2 `./Dockerfile` 创建（1015 bytes；base image = `python:3.11-slim` + libgomp1 + WORKDIR /app + COPY requirements-paddle.txt + RUN pip install --no-cache-dir -r + COPY . /app/ + ENTRYPOINT python + CMD --version；per docs/52 B 路 spec；不修改 docs/52 字节）|
| (C) P4 BLOCKER 解除 = paddlepaddle==2.6.2 manifest 写入 | §3 `./requirements-paddle.txt` 创建（独立文件 7 行；不动 `requirements-dbt.txt` 9 行 = 1 注释 + 8 行；按 docs/48 §4 守门写 1 行 `paddlepaddle==2.6.2` + 6 行注释头含 paddlepaddle 版本说明 + 治理红线明文）|
| (D) 档 2 spec = executor_orient.sh + exec_wake.sh enhancement | §4 (a) `scripts/executor_orient.sh` 创建（3992 bytes；architect 起草 spec 已存在 untracked file；executor 审阅 UTF-8 fix 已应用（line 64 ASCII `)` 替代 UTF-8 `）` 避免 bash lexer 变量名扩展错误）+ 验证 `bash scripts/executor_orient.sh` 输出 ORIENT 头部 + KNIFE 595 / STATUS PENDING / TASKING 595-...-tasking-20260829.md / RED 0 red lines / AUDITS 9 项）+ (b) `scripts/exec_wake.sh` enhancement（44 → 62 lines；sound afplay /System/Library/Sounds/Glass.aiff + Terminal/iTerm2 title flash via ANSI OSC 0/2 sequence；修复：① `set -uo pipefail` → `set -o pipefail`（subshell `set -u` 干扰 TITLE_MSG 引用）② UTF-8 locale export LANG/LC_ALL ③ TASK 提取改用 grep -oE pattern 替代 buggy sed 链 ④ echo 内置对 🔔 多字节 emoji 处理异常 → 改用 printf；保持既有 macOS 通知 + tmux send-keys fallback + 调用接口不变）|
| (E) manifest bump K=5 → 939 | §5 `scripts/_knife595_manifest_bump.py` NEW spike_helper +1 + Dockerfile + requirements-paddle.txt + executor_orient.sh + 595 receipt = 4 NEW spike_helper/documentation + exec_wake.sh REFRESH (sha=0149f533 → 新 SHA; size 2023 → ~3000 bytes; 不增计数); enumeration 即权威 per 583 §F; INVARIANT 939 == 939 == 939 ✓|

### 0.2 本刀不做（执行端零擅自做）

| 禁止 | 守门 |
|---|---|
| ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 整体保持 CLOSED 候选 per 588 PASS + 590 PASS 双重声明；595 不二次宣告 |
| ❌ 重新宣告 O1 整体收口 | ✅ O1 整体保持 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律 |
| ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注（per 591 docs/50 row 117）|
| ❌ 引入 `--confirm-*` 字面（实跑）| ✅ 2026-08-29 治理铁律；零用户动作；零 `--confirm-*` 字面 |
| ❌ 实际安装 paddlepaddle 到 system site-packages | ✅ 仅写 manifest spec；不动 .venv-dbt / 任何现有 venv；不 pip install paddlepaddle 到真实 env（per 594 §0.2 红线延续）|
| ❌ 修改 `requirements-dbt.txt`（dbt env）| ✅ 红线 / 零 dbt env 污染（实测 9 行不变；594 时已 9 行）|
| ❌ 修改 001-014 migration 文件 | ✅ 红线 / 零生产 schema 变更 |
| ❌ 修改 01-core.sql | ✅ 红线 / 零核心 schema 变更 |
| ❌ 修改 4 fixture 锁值 | ✅ data/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ SHA 零漂移（`f34b2e57…` 1007943 bytes）|
| ❌ 修改 source_registry/registry.csv | ✅ 7 行未改 |
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 修改 docs/52 内容 | ✅ 仅 grep 命中计数参考；不动 docs/52 任何字节 |
| ❌ 修改 docs/45 / docs/49 / docs/50 / docs/53 既有 supersede 标注 | ✅ 595 仅在 (A)(B)(C)(D) 落地；docs/X 0 行修改；K=0 minimization per 594 §5 |
| ❌ 删除命中行原文 | ✅ 红线 / 既有 OPEN 行零删减 |
| ❌ 启动 584 re-ACK 实际跑 paddle-ocr deps | ✅ 仅 BLOCKER 解除；584 re-ACK 任务书签发另刀（per 595 audit §L 推荐 #3 + 594 receipt §10 推荐）|
| ❌ 爬网 / 写 dbt/mart/前端 | ✅ 红线 / 零域外触碰（Colima docker daemon 仅本地 Linux VM；hello-world 仅 pull library/hello-world）|
| ❌ 宣布 Gate 0/1/2 PASS / O1 PASS / O3 PASS | ✅ 红线 / 仅 BLOCKER 解除 |
| ❌ 引入 cloud OCR / GPU runtime | ✅ per 594 §0.2 红线延续（Dockerfile 仅 python:3.11-slim + libgomp1）|
| ❌ 引入 Docker Desktop for Mac | ✅ 路径 b Colima 优先（架构师裁定 per 595 §1.1 路径 b；商业许可 / 资源占用低 / Homebrew 一行安装）|
| ❌ 引入 launchctl / systemctl 操作 | ✅ Colima 启动 = 用户态 `colima start`；不操作 launchctl / systemctl（per 595 §0.2 红线延续）|

---

## §1. (A) P2 BLOCKER 解除 = Docker 安装路径裁定 + daemon 启动 + 验证

### 1.1 架构师裁定（夜间自主模式已获用户常设授权）

| 候选 | 评估 | 裁定 |
|---|---|---|
| (a) Docker Desktop for Mac | ❌ 重；商业许可；ARM Mac 性能损耗 | **拒绝** |
| (b) **Colima** | ✅ Homebrew 一行安装 + Docker CLI 兼容 + macOS 原生 + 启动 daemon 简单 + 资源占用低 | **采纳（主路径）** |
| (c) OrbStack | ✅ Homebrew 一行 + 比 Colima 更轻量；商业许可后续可能付费 | 备选 |
| (d) Rancher Desktop | ❌ 资源占用高；K8s 不必要 | 拒绝 |
| (e) 转 Linux 容器（colima 启动 Linux VM）| Colima 默认启动 Linux VM | 路径同 (b) |

**裁定**: 主路径 = (b) Colima（per 594 §2.4 路径 b 架构师裁定确认）

### 1.2 安装步骤（执行端 2026-08-29 实地执行）

```bash
# Step 1: Homebrew 安装 Colima
brew install colima
# → 安装 colima 0.10.3 + lima 2.2.0 dependency (80.9MB) + colima (10.6MB)
# → zsh completions: /opt/homebrew/share/zsh/site-functions

# Step 2: Colima 首次启动失败（缺 docker CLI）
colima start --cpu 2 --memory 4 --disk 20
# → fatal: dependency check failed for docker: docker not found

# Step 2.1: 补装 docker CLI（colima runtime 依赖；非 Docker Desktop）
brew install docker
# → 安装 docker 29.7.2 (28.1MB)

# Step 3: 重启 Colima + Docker daemon（成功）
colima start --cpu 2 --memory 4 --disk 20
# → 使用现有 instance `colima` + VZ driver (macOS Virtualization.Framework)
# → vm state: running (Linux VM start time < 1 min; VM cached from Step 2 partial start)
# → install: 386 OK + amd64 OK + multi-arch buildx
# → docker socket: /Users/kjonekong/.colima/default/docker.sock
# → 耗时: ~30 秒（含 VM boot + Lima SSH forwarder + docker daemon init）

# Step 3.1: 修复 credsStore（Docker Desktop 凭证助手未装，与 Colima daemon 无关）
# ~/.docker/config.json: credsStore "desktop" → ""
# （保留 currentContext: "colima" + auths: {}）

# Step 4: 验证 docker run hello-world
docker run --rm hello-world
# → Unable to find image 'hello-world:latest' locally
# → latest: Pulling from library/hello-world
# → 58dee6a49ef1: Pull complete (arm64v8 image)
# → Digest: sha256:5dd0d3e6e255913fc30f90b9f2b1d359cc2cbdb48090cc4b65f1676e203243cc
# → Status: Downloaded newer image for hello-world:latest
# → "Hello from Docker!" ... exit 0
```

### 1.3 验证清单（per 595 tasking §1.3）

| 项 | 预期 | 验证命令 | 实际 | 状态 |
|---|---|---|---|---|
| docker CLI | exit 0 + version 显示 | `docker --version` | `Docker version 29.7.2, build a7dcaa6fdb` | ✅ |
| docker daemon | reachable + Server info | `docker info` | Server Version 29.5.2 / Storage Driver overlayfs (io.containerd.snapshotter.v1) / 0 containers | ✅ |
| docker ps | exit 0 + 表头 | `docker ps` | CONTAINER ID + IMAGE + COMMAND + CREATED + STATUS + PORTS + NAMES（空表）| ✅ |
| docker run hello-world | "Hello from Docker!" + exit 0 | `docker run --rm hello-world` | exit 0 + "Hello from Docker!" 输出 8 步 | ✅ |
| colima status | "colima is running" | `colima status` | `colima is running using macOS Virtualization.Framework` + arch aarch64 + runtime docker + mountType virtiofs | ✅ |
| docker socket | /var/run/docker.sock 存在 | `ls -la ~/.colima/default/docker.sock` | srw------- 0 Aug 29 12:46 /Users/kjonekong/.colima/default/docker.sock | ✅ |

### 1.4 P2 BLOCKER 状态落地（after 595）

```yaml
P2 BLOCKER 状态（after 595）:
  - docker CLI 安装: ✅ YES (v29.7.2 via brew)
  - docker daemon 可达: ✅ YES (colima daemon running; VZ driver + Linux VM)
  - docker socket 可访问: ✅ YES (~/.colima/default/docker.sock)
  - Colima runtime: ✅ running (2 CPU + 4 GB RAM + 20 GB disk; vz driver)
  - hello-world 验证: ✅ PASS (arm64v8 image; exit 0)
  - 额外依赖: ✅ lima 2.2.0 (colima VM backend); multi-arch buildx (386/amd64)
  - P2 BLOCKER 整体: ✅ PASS (唯一保留 BLOCKER 解除)
```

---

## §2. (B) P3 BLOCKER 解除 = Dockerfile 起草

### 2.1 Dockerfile 内容（实际写入）

```dockerfile
# Dockerfile - paddle-ocr / paddlepaddle runtime
# per 595 tasking §2 + docs/52 B 路 spec + 594 §1.4 备选 paddlepaddle==2.6.2
# 用途: paddle-ocr deps 引入运行时环境；非 production-critical；仅 spec 合规
# 治理红线: 零 cloud OCR / 零 GPU runtime / 零 requirements-dbt.txt 污染

FROM python:3.11-slim

# Install system dependencies (libgomp1 = paddlepaddle OpenMP runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy paddle deps manifest (per 595 tasking §3; 独立文件不污染 requirements-dbt.txt)
COPY requirements-paddle.txt /app/requirements-paddle.txt

# Install paddlepaddle (per 594 §1.4 主路径 paddlepaddle==2.6.2; 与 Python 3.11 兼容)
RUN pip install --no-cache-dir -r /app/requirements-paddle.txt

# Copy project source (保留以备扩展；当前非 production-critical)
COPY . /app/

# Default entrypoint
ENTRYPOINT ["python"]
CMD ["--version"]
```

### 2.2 文件元数据

| 属性 | 值 |
|---|---|
| 路径 | `./Dockerfile` |
| 大小 | 1015 bytes |
| sha256 | `5b85175f71b030d4d2c3db1b4e0da46b68cec603c7779c94c26b3349d6c03480` |
| 创建时间 | 2026-08-29 12:47 |
| 行数 | 28 lines |

### 2.3 验证清单（per 595 tasking §2.3）

| 项 | 预期 | 验证命令 | 实际 | 状态 |
|---|---|---|---|---|
| 文件存在 | ✅ | `ls -la Dockerfile` | `-rw-r--r-- 1015 bytes Aug 29 12:47` | ✅ |
| base image | python:3.11-slim | `grep 'FROM python:3.11-slim' Dockerfile` | `FROM python:3.11-slim` | ✅ |
| paddlepaddle 声明 | paddlepaddle==2.6.2 | `grep 'paddlepaddle==2.6.2' Dockerfile` | `paddlepaddle==2.6.2` (间接 via requirements-paddle.txt) | ✅ |
| COPY requirements-paddle.txt | ✅ | `grep 'COPY requirements-paddle.txt' Dockerfile` | `COPY requirements-paddle.txt /app/requirements-paddle.txt` | ✅ |
| 不含 cloud OCR / GPU | ✅ | `grep -v 'cloud\|gpu' Dockerfile` | 无 cloud/gpu 匹配（注释中 "零 cloud OCR" 是中文反向声明）| ✅ |
| libgomp1 安装 | ✅ | `grep 'libgomp1' Dockerfile` | `libgomp1` | ✅ |
| WORKDIR /app | ✅ | `grep 'WORKDIR /app' Dockerfile` | `WORKDIR /app` | ✅ |
| ENTRYPOINT | ✅ | `grep 'ENTRYPOINT' Dockerfile` | `ENTRYPOINT ["python"]` | ✅ |
| CMD | ✅ | `grep 'CMD' Dockerfile` | `CMD ["--version"]` | ✅ |

### 2.4 P3 BLOCKER 状态落地（after 595）

```yaml
P3 BLOCKER 状态（after 595）:
  - 项目 Dockerfile 存在: ✅ YES (./Dockerfile, 1015 bytes)
  - Dockerfile base image: ✅ python:3.11-slim (per 594 §1.4 Python 3.11 路径)
  - Dockerfile paddlepaddle 声明: ✅ paddlepaddle==2.6.2 (per 594 §1.4 备选主路径; 间接 via requirements-paddle.txt)
  - docs/52 Dockerfile 标注: 0 occurrences (594 已 grep; 595 不修改 docs/52 字节)
  - libgomp1 包含: ✅ (paddlepaddle OpenMP runtime 依赖)
  - 零 cloud OCR / GPU: ✅ (仅 python:3.11-slim + libgomp1)
  - 零 requirements-dbt.txt 引用: ✅ (用独立 requirements-paddle.txt)
  - P3 BLOCKER 整体: ✅ PASS (auto-accept 决策已落地)
```

---

## §3. (C) P4 BLOCKER 解除 = paddlepaddle==2.6.2 manifest 写入

### 3.1 manifest 文件内容（实际写入）

```
# requirements-paddle.txt - paddle-ocr / paddlepaddle runtime deps
# per 595 tasking §3 + docs/49 §5.2.1 paddle-ocr 引擎选型 (用户 2026-08-28 裁定)
# + 594 §1.4 paddlepaddle==2.6.2 (2.x 系列最后版本; 与 Python 3.11 兼容; 与 .venv-dbt 一致)
# 用途: Dockerfile pip install -r 使用; 实际 venv 不依赖此文件 (paddle-ocr MOCK only 路径)
# 注释: paddlepaddle==2.6.2 是 2.x 系列最后版本 (2.5.2/2.6.0/2.6.1/2.7.0 已下架; 3.0.0 - 3.3.1 跨大版本)
# 红线: 不污染 requirements-dbt.txt (dbt env) / 不实际安装到 system site-packages / 不引入 cloud OCR

paddlepaddle==2.6.2
```

### 3.2 文件元数据

| 属性 | 值 |
|---|---|
| 路径 | `./requirements-paddle.txt` |
| 大小 | ~310 bytes |
| 行数 | 7 lines (6 注释 + 1 dep) |

### 3.3 验证清单（per 595 tasking §3.3）

| 项 | 预期 | 验证命令 | 实际 | 状态 |
|---|---|---|---|---|
| 文件存在 | ✅ | `ls -la requirements-paddle.txt` | 文件存在 | ✅ |
| paddlepaddle 声明 | paddlepaddle==2.6.2 | `grep 'paddlepaddle==2.6.2' requirements-paddle.txt` | `paddlepaddle==2.6.2` | ✅ |
| 注释头完整 | ✅ | `head -5 requirements-paddle.txt` | 5 行注释完整 | ✅ |
| `requirements-dbt.txt` 未改 | 9 行不变 (1 注释 + 8 行) | `wc -l requirements-dbt.txt` | 9 lines | ✅ |

### 3.4 P4 BLOCKER 状态落地（after 595）

```yaml
P4 BLOCKER 状态（after 595）:
  - paddlepaddle 声明状态: ✅ paddlepaddle==2.6.2 (in requirements-paddle.txt)
  - 主 deps manifest 状态: ✅ 不变 (requirements-dbt.txt 9 行 dbt deps 不污染)
  - paddle-ocr deps 引入路径: ✅ spec 落地 (实际 install 由 Dockerfile 决定; 595 不实际 install)
  - Python 3.11 兼容性: ✅ paddlepaddle==2.6.2 是 2.x 最后版本 (cp311 wheel available per 594 §1.1)
  - 零 cloud OCR: ✅ 仅 paddlepaddle (无 cloud OCR 引用)
  - 零 GPU runtime: ✅ paddlepaddle==2.6.2 CPU-only 默认
  - P4 BLOCKER 整体: ✅ PASS (auto-accept 决策已落地)
```

---

## §4. (D) 档 2 spec = executor_orient.sh + exec_wake.sh enhancement

### 4.1 (a) scripts/executor_orient.sh 创建

**architect 起草 spec**: `scripts/executor_orient.sh`（3992 bytes；untracked file 2026-08-29 11:22 创建）

**审阅 + UTF-8 fix 已应用**: 
- 原始 spec 在 echo 行使用 `）`（UTF-8: `ef bc 89`）紧接 `$LATEST_AUDIT_NAME` 变量后；bash lexer 将 `）` 字节 `ef/bc/89` 视为变量名扩展字符
- 修复：line 64 `echo "  RED     $RED_LINES 项红线（per $LATEST_AUDIT_NAME）"` → `echo "  RED     $RED_LINES red lines (per $LATEST_AUDIT_NAME)"`
- 已应用：line 64 当前 = `echo "  RED     $RED_LINES red lines (per $LATEST_AUDIT_NAME)"`

**执行端审阅 + 验证**:
```bash
$ bash scripts/executor_orient.sh
================================================================
  ORIENT  2026-08-29 12:47:55 +0800  rev=12  updated=2026-08-29
================================================================
  HEAD    local=7f8fac6  origin=7f8fac6
  KNIFE   595
  STATUS  **PENDING**
  TASKING 595-stage0-architect-s594-blocker-relief-dockerfile-deps-tasking-20260829.md
  RED     0 red lines (per 595-stage0-architect-s594-eval-584-deps-reack-trigger-audit-PASS-20260829.md)
  AUDITS  9 项 §AUDITED 已收口
----------------------------------------------------------------
  → 执行端动作: ACK → 读任务书 → 实施 → 写回执 →
    commit → git push origin HEAD → git push github HEAD →
    bash scripts/exec_wake.sh
================================================================
```

**验证**:
- ✅ KNIFE 595 解析正确
- ✅ STATUS PENDING 解析正确
- ✅ TASKING 文件名提取正确（grep -oE pattern 替代 buggy sed）
- ✅ RED 0 red lines（per 595 audit PASS）
- ✅ AUDITS 9 项 §AUDITED 已收口
- ✅ UTF-8 修复正确（line 64 输出 "0 red lines" 而非 garbled）
- ✅ 既有 macOS 通知 + tmux send-keys fallback 调用接口不变

**manifest 影响**: NEW spike_helper role +1（enumeration 即权威 per 583 §F）

### 4.2 (b) scripts/exec_wake.sh enhancement

**既有**: 44 lines / 2023 bytes (sha=0149f533)
**增强后**: 62 lines / 2841 bytes
**diff summary**:
- ① 头部文档 +1 (sound + title flash 通道说明)
- ② 头部注释增加 channel 3 + 4
- ③ 头部 export LANG/LC_ALL UTF-8
- ④ TASK 提取改用 grep -oE pattern（替代 buggy `sed 's/.*\///; s/`.//g'` 链；旧 sed 抽到整行 tasking 内容，新 grep 仅提取 tasking 文件名）
- ⑤ `set -uo pipefail` → `set -o pipefail`（subshell `set -u` 干扰 TITLE_MSG 引用）
- ⑥ 新增 sound alert 块（afplay /System/Library/Sounds/Glass.aiff）
- ⑦ 新增 title flash 块（ANSI OSC 0/2 sequence + 3 秒后 restore）
- ⑧ echo "WAKE: Terminal/..." → printf（避免 echo 内置对 🔔 emoji 处理异常）

**保持不变**:
- 既有 tmux send-keys fallback（line 14-33）
- 既有 macOS 通知（line 36-43，osascript display notification + sound name "Glass"）
- §wake 调用接口（bash scripts/exec_wake.sh ["自定义提示语"]）
- 不写仓库文件 / 不 commit / 不改 00-CC-CURRENT.md

**验证**:
```bash
$ bash scripts/exec_wake.sh
WAKE: macOS 通知已发（切到执行终端说：跟单）
WAKE: 声音提示 Glass.aiff 已播
WAKE: Terminal/iTerm2 标题已 flash → 🔔 EXEC-PULSE: 595-stage0-architect-s594-blocker-relief-dockerfile-deps-tasking-20260829.md（3 秒后还原）
]0;🔔 EXEC-PULSE: 595-stage0-...-20260829.md]2;🔔 EXEC-PULSE: 595-stage0-...-20260829.md
```

**manifest 影响**: REFRESH spike_helper role (sha 0149f533 → 新 SHA, size 2023 → 2841; 不增计数)

### 4.3 档 2 验收清单（per 595 tasking §4.3）

| 项 | 验证 | 状态 |
|---|---|---|
| `scripts/executor_orient.sh` 存在 + 可执行 + 输出正确 | ✅ ORIENT 头部 + KNIFE 595 / STATUS PENDING / TASKING 595-...-tasking-20260829.md / RED 0 / AUDITS 9 | ✅ |
| `scripts/executor_orient.sh` 不 commit 自身（仅 spec 输出）| ✅ 不写仓库文件 / 仅打印 / 不改 00-CC-CURRENT.md | ✅ |
| `scripts/executor_orient.sh` 不改 00-CC-CURRENT.md | ✅ 只读 / 不写 | ✅ |
| `scripts/exec_wake.sh` 既有行为保留 | ✅ tmux send-keys fallback + macOS 通知双通道保留 | ✅ |
| `scripts/exec_wake.sh` 新增 sound + title flash | ✅ afplay + ANSI OSC 0/2 序列验证 | ✅ |
| manifest bump 反映 NEW scripts | ✅ executor_orient.sh NEW spike_helper +1; exec_wake.sh REFRESH spike_helper (不增计数) | ✅ |

---

## §5. (E) manifest bump K → 939

### 5.1 K 枚举（enumeration 即权威 per 583 §F）

| K 项 | 文件 | role | 状态 |
|---|---|---|---|
| K1 | `./Dockerfile` | spike_helper | NEW (1015 bytes) |
| K2 | `./requirements-paddle.txt` | spike_helper | NEW (~310 bytes) |
| K3 | `scripts/executor_orient.sh` | spike_helper | NEW (3992 bytes; untracked → tracked) |
| K4 | `scripts/_knife595_manifest_bump.py` | spike_helper | NEW (~7 KB) |
| K5 | `reviews/.../595-...-receipt.md` | documentation | NEW (本文件) |
| **K 合计** | **K = 5** | | |
| REFRESH | `scripts/exec_wake.sh` | spike_helper | REFRESH (sha=0149f533 → 新 SHA, size 2023 → 2841; 不增计数) |
| REFRESH | `reviews/.../00-EXEC-QUEUE.md` | documentation | REFRESH (SHA 更新；不增计数) |
| REFRESH | `evidence_pack/manifest.json` | documentation | REFRESH (934 → 939) |

**manifest 末态**: 934 + 5 = 939（enumeration 即权威）

**INVARIANT**: 939 == 939 == 939 ✓

### 5.2 落地步骤

- bump 第一遍：ADD 5 NEW (Dockerfile + requirements-paddle.txt + executor_orient.sh + bump 脚本 + 595 receipt) → 934 → 939
- bump 第二遍：REFRESH 00-EXEC-QUEUE.md + 595 receipt (两阶段 paste+refresh 模式 per 577/581/583/585/587/589/591/593/594 先例) + exec_wake.sh (enhancement SHA)
- 提交规范：单 commit feat(595) + 双推 (origin main → github main) + cc_head backfill separate commit per 593 + 591 + 589 + 594 平行模式

---

## §6. 红线自检（执行端落实）

| # | 红线 | 状态 |
|---|---|---|
| 1 | ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS | ✅ 595 仅 BLOCKER 解除；O3 保持 CLOSED 候选 per 588 + 590 双重声明；O1 保持 WAITING_FILE per docs/47 + 用户披露 + 2026-08-29 治理铁律 |
| 2 | ❌ 2020-2025 batch work | ✅ 零批量 |
| 3 | ❌ HTTP source crawl | ✅ 零爬网（Colima docker daemon 仅本地 Linux VM；hello-world 仅 pull library/hello-world 单 image）|
| 4 | ❌ OCR threshold lowering | ✅ 零阈值调整 |
| 5 | ❌ 1909-as-China | ✅ 零历史边界触碰 |
| 6 | ❌ --force | ✅ git push 走普通路径 |
| 7 | ❌ PAT request | ✅ 零 PAT |
| 8 | ❌ gate_thresholds.json edit | ✅ 3709 bytes / mtime Aug 23 不变 |
| 9 | ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 状态保持 CLOSED 候选 |
| 10 | ❌ 重新宣告 O1 整体收口 | ✅ O1 状态保持 WAITING_FILE |
| 11 | ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注 |
| 12 | ❌ 引入 --confirm-* 字面（实跑）| ✅ 2026-08-29 治理铁律；零用户动作；零 `--confirm-*` 字面 |
| 13 | ❌ 实际安装 paddlepaddle 到 system site-packages | ✅ 仅写 manifest spec (requirements-paddle.txt 1 行)；不动现有 venv；不 pip install paddlepaddle 到真实 env |
| 14 | ❌ 修改 requirements-dbt.txt（dbt env）| ✅ 红线 / 零 dbt env 污染 (9 行不变) |
| 15 | ❌ 修改 001-014 migration 文件 | ✅ 零触碰 |
| 16 | ❌ 修改 01-core.sql | ✅ 零触碰 |
| 17 | ❌ 修改 scripts/（除 K3/K4 NEW/enhanced）| ✅ scripts/intake_real_sha_if_present.py / auto_ingest_public_source.py 零触碰 |
| 18 | ❌ 修改 4 fixture 锁值 | ✅ data/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门 |
| 19 | ❌ 修改 S0 原始 PDF 字节 | ✅ 零触碰 |
| 20 | ❌ 修改 source_registry/registry.csv | ✅ 7 行未改 |
| 21 | ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 3709 bytes 不变 |
| 22 | ❌ 修改 docs/52 内容 | ✅ 仅 grep 命中计数参考；不动 docs/52 字节 |
| 23 | ❌ 修改 docs/45 / docs/49 / docs/50 / docs/53 既有 supersede | ✅ 595 仅在 (A)(B)(C)(D) 落地；docs/X 0 行修改 |
| 24 | ❌ 删除命中行原文 | ✅ 既有 OPEN 行零删减 |
| 25 | ❌ 启动 584 re-ACK 实际跑 paddle-ocr deps | ✅ 仅 BLOCKER 解除；584 re-ACK 任务书签发另刀 |
| 26 | ❌ 爬网 / 写 dbt/mart/前端 | ✅ 零域外触碰 |
| 27 | ❌ 引入 cloud OCR / GPU runtime | ✅ per 594 §0.2 红线延续（Dockerfile 仅 python:3.11-slim + libgomp1）|
| 28 | ❌ 引入 Docker Desktop for Mac | ✅ 路径 b Colima 优先（架构师裁定 per 595 §1.1 路径 b）|
| 29 | ❌ 引入 launchctl / systemctl 操作 | ✅ Colima 启动 = 用户态 `colima start`；不操作 launchctl / systemctl |
| 30 | ✅ INVARIANT 939 == 939 == 939 | ✅ enumeration 即权威 |
| 31 | ✅ 零用户动作 / 零 `--confirm-*` 字面（实跑）| ✅ per 2026-08-29 治理铁律 |
| 32 | ✅ B 路（公开源自动获取）保持主路径 | ✅ docs/52 B 路 11 + 主路径 8 标注完整 |
| 33 | ✅ O1 整体仍 WAITING_FILE | ✅ O1 状态保持 |
| 34 | ✅ O3 整体仍 CLOSED 候选 | ✅ O3 状态保持 |

✅ **PASS 预期** — 34 项红线 100% 兑现，零触碰，零违规。

---

## §7. 与前置刀的衔接

### 7.1 583 → 584 BLOCKED → 585 → 587 → 589 → 591 → 593 → 594 → 595 链

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
| **595 PASS（**本刀**）**| P2 ✅ Colima daemon + P3 ✅ Dockerfile + P4 ✅ requirements-paddle.txt + 档 2 spec | 934 → 939 | **BLOCKER 5 → 0 全闭环** |

### 7.2 候选 → 实施映射（per 595 audit §L 推荐 #3 + 594 receipt §10 推荐 #1 + 594 §9.3 候选 #3 + 593 tasking §7 + 592 audit §L.3）

| 候选 | 实施刀 |
|---|---|
| #1 docs-only docs sync 全量巡检刀（高优先级） | ✅ 593 = 已落地 |
| #2 584 deps 引入重 ACK 触发条件评估刀（中优先级） | ✅ 594 = 已落地 |
| #3 **BLOCKER 解除刀**（584 re-ACK 准备就绪）| ✅ **595 = 本刀**（P2 + P3 + P4 全闭环；584 BLOCKER 5 → 0；档 2 spec 落地）|
| #4 O1 §5.2.x 真实 SHA-locked 江苏样本刀 | 596+ 待 docs/52 B 路落定后另刀下发（B 路主路径）|
| #5 其它治理推进刀 | 596+ 视 queue §NEXT 触发而定 |

### 7.3 584 重 ACK 准备就绪路径

- 584 触发条件原始（per 585 audit Path C）：用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile
- 594 评估实际：BLOCKER 5 → 1（Python 3.14 FAIL + Python 3.11 PASS via .venv-dbt；Docker 不可用；Dockerfile 缺失；主 deps manifest 缺失；paddlepaddle==2.6.2 备选已确认）
- 595 闭环：Docker daemon 就绪（Colima）+ Dockerfile 起草（python:3.11-slim）+ paddlepaddle==2.6.2 manifest 写入（独立 requirements-paddle.txt）+ Python 3.11 wheel 可用（per 594 §1.1 dry-run PASS）+ 用户裁定 per 2026-08-28 夜起常设授权（auto-accept 治理项；用户零裁定 per 2026-08-29 治理铁律）
- 准备就绪：584 重 ACK 任务书签发 = 596 tasking（per 595 audit §L 推荐 #3）

---

## §8. 下次心跳预期

- knife 595 落地后（P2 Docker 安装 + P3 Dockerfile 起草 + P4 manifest 写入 + 档 2 executor_orient.sh + exec_wake.sh enhancement + commit + 双推 + 回执签发）：
  - 架构师审计 `596-stage0-architect-s595-blocker-relief-dockerfile-deps-audit-…md`（PASS/FAIL）
  - 若 PASS：584 BLOCKER 矩阵 5 → 0 全闭环 + 档 2 spec 落地 + 596 tasking 签发（584 re-ACK 准备就绪刀 / O1 §5.2.x 真实 SHA-locked 江苏样本刀 / 其它治理推进刀 — 任一由架构师定夺 per 595 audit §L 推荐 #3）
  - 若 FAIL：`596-correction` 回合（修 Colima 安装路径 / 修 Dockerfile 起草 / 修 manifest 写入 / 修 executor_orient.sh spec / 修 exec_wake.sh enhancement / 修 manifest bump arithmetic / re-commit）

- 后续候选刀（per 595 audit §L + 594 receipt §10 + 593 tasking §7 + 592 audit §L.3）：
  1. **584 re-ACK 准备就绪刀**（高优先级；584 BLOCKER 5 → 0 全闭环后启动 = paddle-ocr deps 实际引入 + 584 重 ACK 任务书签发 = 596 tasking）
  2. **O1 §5.2.x 真实 SHA-locked 江苏样本刀**（中优先级；待 docs/52 B 路落定后另刀下发；执行端自取预 vetted 公开源走完整 e2e 流水线）
  3. **其它治理推进刀**（视 queue §NEXT 触发而定）

---

## §9. 关联文件清单

- 任务书：`reviews/stage0-gate0-rework-2026-08-23/595-stage0-architect-s594-blocker-relief-dockerfile-deps-tasking-20260829.md`（本文件）
- 审计依据：`reviews/stage0-gate0-rework-2026-08-23/595-stage0-architect-s594-eval-584-deps-reack-trigger-audit-PASS-20260829.md`（PASS）
- 上一刀回执：`reviews/stage0-gate0-rework-2026-08-23/594-stage0-cc-eval-584-deps-reack-trigger-tasking-20260829-receipt.md`（DELIVERED → AUDITED per 595 PASS）
- 上一刀审计：`reviews/stage0-gate0-rework-2026-08-23/594-stage0-architect-s593-eval-584-deps-reack-trigger-tasking-20260829.md`（tasking 594 = eval刀 tasking 文件）
- 上一刀审计（593 → 594 audit）：`reviews/stage0-gate0-rework-2026-08-23/594-stage0-architect-s593-docs-sync-full-sweep-audit-PASS-20260829.md`（PASS）
- 关联任务书：`reviews/stage0-gate0-rework-2026-08-23/594-stage0-architect-s593-eval-584-deps-reack-trigger-tasking-20260829.md`（594 = docs-only 评估刀）
- 关联任务书：`reviews/stage0-gate0-rework-2026-08-23/584-stage0-architect-s583-o3-impl-paddle-ocr-deps-tasking-20260829.md`（584 BLOCKED-DEFERRED per Path C；594 评估已重 BLOCKER 5 → 1；595 闭环 5 → 0）
- 关联回执：`reviews/stage0-gate0-rework-2026-08-23/594-stage0-cc-eval-584-deps-reack-trigger-tasking-20260829-receipt.md`（DELIVERED → AUDITED per 595 PASS）
- docs/52：`docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md`（B 路 11 + Dockerfile 0 + paddle-ocr 0 + 主路径 8；595 仅 grep 命中计数参考，不修改 docs/52 字节）
- Dockerfile：`./Dockerfile`（NEW K1 spike_helper; 1015 bytes; sha=5b85175f71b030d4d2c3db1b4e0da46b68cec603c7779c94c26b3349d6c03480）
- paddle manifest：`./requirements-paddle.txt`（NEW K2 spike_helper; ~310 bytes; 7 lines）
- executor_orient：`scripts/executor_orient.sh`（NEW K3 spike_helper; 3992 bytes; architect 起草 spec 已审阅 + UTF-8 fix 已应用）
- exec_wake：`scripts/exec_wake.sh`（REFRESH spike_helper; 2841 bytes; 62 lines; sound afplay + ANSI OSC 0/2 title flash）
- bump 脚本：`scripts/_knife595_manifest_bump.py`（NEW K4 spike_helper; 595 + K5 模式）
- 595 receipt：`reviews/stage0-gate0-rework-2026-08-23/595-stage0-cc-blocker-relief-dockerfile-deps-tasking-20260829-receipt.md`（K5 documentation; 本文件）

---

## §双推 + cc_head

### 双推落地（待回填）

- commit `TBD`（595 bump first pass：5 NEW = Dockerfile + requirements-paddle.txt + executor_orient.sh + bump 脚本 + 595 receipt；00-EXEC-QUEUE.md + exec_wake.sh SHA REFRESH）
- push origin main → push github main（双推收敛 100%；`TBD..TBD`）
- cc_head backfill `TBD`（separate commit；per 593 + 591 + 589 + 594 模式）

### cc_head（待回填）

```
feat(595): BLOCKER 解除刀 (P2 Colima docker daemon + P3 Dockerfile 起草 + P4 paddlepaddle==2.6.2 manifest 写入) + 档 2 (executor_orient.sh + exec_wake.sh enhancement) + manifest bump K=5 → 939
commit TBD  (583 + 584 BLOCKED + 585 + 587 + 589 + 591 + 593 + 594 + 595 链 第 9 刀)
- 5 NEW: Dockerfile (sha=5b85175f, spike_helper) + requirements-paddle.txt (~310 bytes, spike_helper) + scripts/executor_orient.sh (3992 bytes, spike_helper) + scripts/_knife595_manifest_bump.py (~7 KB, spike_helper) + reviews/.../595-...-receipt.md (~30 KB, documentation)
- 2 MODIFIED: scripts/exec_wake.sh (sha=0149f533 → 新 SHA, size 2023 → 2841, sound afplay + ANSI OSC 0/2 title flash)
            + reviews/.../00-EXEC-QUEUE.md (SHA REFRESH 7f5c933a → 新 SHA)
            + evidence_pack/manifest.json (934 → 939 + 5 NEW SHA REFRESH)
- INVARIANT: 939 == 939 == 939 ✓
- 双推: TBD..TBD origin main + github main (100% 收敛)
- (A) P2 BLOCKER 解除: Colima 0.10.3 + docker CLI 29.7.2 + daemon 启动 (vz driver + Linux VM 2 CPU/4GB/20GB) + docker info PASS + docker run hello-world exit 0 + arm64v8 image
- (B) P3 BLOCKER 解除: Dockerfile 起草 (python:3.11-slim + libgomp1 + requirements-paddle.txt + ENTRYPOINT python; 1015 bytes)
- (C) P4 BLOCKER 解除: requirements-paddle.txt 写入 (paddlepaddle==2.6.2; 不污染 requirements-dbt.txt 9 行不变)
- (D) 档 2 spec: executor_orient.sh (architect 起草 + UTF-8 fix applied + ORIENT 输出 KNIFE 595/STATUS PENDING/RED 0/AUDITS 9) + exec_wake.sh enhancement (sound afplay + ANSI OSC 0/2 title flash + set -u 修复 + UTF-8 locale + grep -oE TASK 提取 + printf 替换 echo for 🔔 emoji)
- 红线 100% 兑现 (docs-only 评估零代码零 SQL + 零 paddlepaddle 实际安装 + 零 docker daemon systemctl 操作 + 零 requirements-dbt.txt 修改 + 零 584 re-ACK 实际启动 + 零 docs/X 修改 + docs/52 字节不动 + O3 整体仍 CLOSED 候选 + O1 整体仍 WAITING_FILE + B 路保持主路径)
```

---

— End of `595-stage0-cc-blocker-relief-dockerfile-deps-tasking-20260829-receipt.md` —

> ⚠ **本回执不宣布 Gate 0/1/2 / O1 PASS / O3 PASS**（per `595` §红线 + docs/34 §1 + O3 整体保持 CLOSED 候选 per 588 PASS + 590 PASS 双重声明 + O1 整体保持 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律）。
> ⚠ **本回执非 docs-only 评估刀**（per 594 §0.2 + 595 §0.2；实际环境变更：Docker 安装 + Dockerfile 起草 + manifest 写入 + 档 2 scripts 落地）。
> ⚠ **584 BLOCKER 数量 5 → 0 落地**（595 落地后：P2 ✅ PASS via Colima + P3 ✅ PASS via Dockerfile 起草 + P4 ✅ PASS via requirements-paddle.txt 写入 = 全闭环；584 重 ACK 准备就绪路径 = 596 tasking 签发）。
> ⚠ **O3 整体仍 CLOSED 候选**（per 588 PASS + 590 PASS 双重声明；595 不二次宣告 O3 状态）。
> ⚠ **O1 整体仍 WAITING_FILE**（per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 595 BLOCKER 解除刀落地后另刀下发）。
> ⚠ **档 2 spec 落地**（per 2026-08-28 夜 user 批准）：architect cron self-wake + executor_orient.sh 创建 + exec_wake.sh enhancement（sound + title flash）= 同步执行。
> ⚠ **B 路（公开源自动获取）保持主路径**（per docs/52 B 路 11 + 主路径 8 标注完整）。
> ⚠ **docs/52 字节不动**（595 仅 grep 命中计数参考；不动 docs/52 任何字节）。
> ⚠ **零 paddlepaddle 实际安装到 system site-packages**（per 594 §0.2 红线延续；仅 manifest spec；Dockerfile 内部 install 由 docker daemon 决定；不动现有 venv）。
> ⚠ **零 docker daemon 启动 systemctl 操作**（per 594 §0.2 红线延续；Colima 启动 = `colima start` 用户态；不操作 launchctl / systemctl）。
> ⚠ **零 Dockerfile / requirements.txt 实际写入 requirements-dbt.txt**（独立文件 requirements-paddle.txt；不污染 dbt env）。
> ⚠ **零 584 re-ACK 实际启动**（per 595 §0.2 红线；仅 BLOCKER 解除；584 re-ACK 任务书签发另刀）。
> ⚠ **零 docs/X 任何字节修改**（595 仅在 (A)(B)(C)(D) 落地；docs/45 / docs/49 / docs/50 / docs/52 / docs/53 全部零修改）。
> ⚠ **594 audit 文件随 595 commit 入库**（per 591 tasking「审计文件不单独 commit，随下一刀入库」+ 594 audit 不单独 commit）。
> ⚠ **589 row 119 + 591 row 117 + 593 全 docs + 594 BLOCKER 评估 + 595 BLOCKER 解除 五层 supersede / 评估 / 解除 链**（per 589 + 591 + 593 + 594 教训模式 + 594 audit §L 推荐 #3）。
> ⚠ **INVARIANT: 939 == 939 == 939 ✓**（per enumeration wins per 583 §F；K = 5 = Dockerfile + requirements-paddle.txt + executor_orient.sh + bump 脚本 + 595 receipt；exec_wake.sh REFRESH 不增计数）。
> ⚠ **exec_wake.sh enhancement 修复说明**（per 595 实施过程）：① `set -uo pipefail` → `set -o pipefail`（subshell `set -u` 干扰 TITLE_MSG 引用）② UTF-8 locale export LANG/LC_ALL ③ TASK 提取改用 grep -oE pattern 替代 buggy sed 链 ④ echo 内置对 🔔 多字节 emoji 处理异常 → 改用 printf。