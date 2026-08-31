# 595-stage0-architect-s594-blocker-relief-dockerfile-deps-tasking-20260829

> **任务书状态**: PENDING
> **签发者**: CC 架构师终端
> **签发日期**: 2026-08-29
> **前置**: `595-stage0-architect-s594-eval-584-deps-reack-trigger-audit-PASS-20260829`（PASS；本任务书审计依据）+ 594 PASS（594 audit 落）+ 593 PASS（594 audit 落）+ 592 PASS + 591 PASS（592 audit 落）+ 590 PASS + 589 PASS + 588 PASS + 587 PASS + 585 PASS + 583 PASS + 584 BLOCKED-DEFERRED per Path C（594 评估实际 = BLOCKER 5 → 1；P1 ✅ PASS via Python 3.11 / P2 ❌ FAIL 唯一 BLOCKER / P3 🟡 PARTIAL → auto-accept / P4 🟡 PARTIAL → auto-accept；零 paddlepaddle 实际安装 + 零 docker daemon 启动 + docs/52 字节不动 + docs/X K=0 minimization）
> **本质**: 架构师治理模型第十五刀；**BLOCKER 解除刀（P2 Docker 安装 + P3 Dockerfile 起草 + P4 paddlepaddle==2.6.2 manifest 写入）**（per 594 audit §L 推荐 #3 + 594 tasking §10 推荐 #1 + 594 receipt §10 + 594 receipt §6.1 P2 解除条件 + 594 receipt §6.1 P3 解除条件 + 594 receipt §6.1 P4 解除条件 + 594 receipt §9.3 候选 #3 + 593 tasking §7 + 592 audit §L.3）；584 BLOCKER 矩阵 5 → 1 收口后唯一保留 P2 ❌ FAIL（docker / podman / containerd / nerdctl 全部 not found）= 595 BLOCKER 解除刀（Docker 安装路径裁定 + Dockerfile 起草 + paddlepaddle==2.6.2 manifest 写入；一次闭环）；584 重 ACK 准备就绪路径 = 595 落地 → 584 重 ACK 任务书签发；**档 2 user 批准（2026-08-28 夜起生效）** = 同步执行 `scripts/executor_orient.sh` 创建 + `scripts/exec_wake.sh` enhancement（sound + title flash）；docs-only 评估零代码零 SQL（594 已落）+ 本刀实际 BLOCKER 解除（不 zero-code；Docker 安装 + Dockerfile 起草 + manifest 写入 = 实际环境变更；非 docs-only 刀）
> **核心动作**: (A) P2 BLOCKER 解除 = 架构师裁定 Docker 安装路径（推荐 **Colima**：Homebrew `brew install colima && colima start`；macOS 原生 + Docker CLI 兼容 + 启动 daemon；备选 OrbStack `brew install orbstack`；DOCKER 安装 + daemon 启动 + 验证 `docker info` PASS） + (B) P3 BLOCKER 解除 = Dockerfile 起草（per docs/52 B 路 spec；不修改 docs/52 字节；路径 = `./Dockerfile`；base image = `python:3.11-slim`；声明 `paddlepaddle==2.6.2`；COPY + RUN pip install + ENTRYPOINT 设计；非 production-critical，仅 Dockerfile 存在性 + 内容合规） + (C) P4 BLOCKER 解除 = paddlepaddle==2.6.2 manifest 写入（per 2026-08-29 治理铁律 auto-accept；路径 = 新建 `./requirements.txt` 或 `requirements-paddle.txt`；按 docs/48 §4 守门写 1 行 `paddlepaddle==2.6.2`；**主 deps manifest = `requirements-dbt.txt`（dbt 7 行 deps）不动**，新建独立文件避免污染 dbt env） + (D) 档 2 spec = 同步执行 (a) `scripts/executor_orient.sh` 创建（architect 起草 spec 已存在未提交；executor 审阅后 commit + manifest bump）+ (b) `scripts/exec_wake.sh` enhancement（sound + title flash；保持 macOS 通知 + tmux send-keys fallback）+ (E) manifest bump K → 934+K（K = Dockerfile + Dockerfile + manifest + executor_orient.sh + exec_wake.sh + 595 receipt + 可选 bump 脚本；enumeration 即权威 per 583 §F）+ 红线 100% 兑现（不动 001-014 migration 文件 / 不动 01-core.sql / 不动 4 fixture 锁值 / 不动 S0 原始 PDF 字节 / 不动 source_registry/registry.csv / 不动 gate_thresholds.json / 不爬网 / 不写 dbt/mart/前端 / 不宣布 Gate 0/1/2 PASS）

---

## §0. 本刀做/本刀不做

### 0.1 本刀做（按 §1 + §2 + §3 + §4 + §5 + §6 + §7 顺序执行）

| 项 | 落地 |
|---|---|
| (A) **P2 BLOCKER 解除 = Docker 安装路径裁定** | §1 安装 Colima（`brew install colima`）+ 启动 daemon（`colima start`）+ 验证 `docker info` + `docker ps` + `docker run hello-world` 退出码 0；备选 OrbStack（`brew install orbstack`）；不安装 Docker Desktop for Mac（per 594 §2.4 备选路径 a 优先 Colima 更轻量）|
| (B) **P3 BLOCKER 解除 = Dockerfile 起草** | §2 创建 `./Dockerfile`（per docs/52 B 路 spec；不修改 docs/52 字节）+ base image = `python:3.11-slim` + 声明 `paddlepaddle==2.6.2`（per 594 §1.4 备选版本 2.6.2 是 2.x 最后版本）+ COPY 项目代码 + RUN pip install -r requirements-paddle.txt + ENTRYPOINT 设计（无 critical production 依赖；仅 spec 合规） |
| (C) **P4 BLOCKER 解除 = paddlepaddle==2.6.2 manifest 写入** | §3 创建 `./requirements-paddle.txt`（独立文件，不污染 `requirements-dbt.txt`）+ 内容 = `paddlepaddle==2.6.2` 1 行（per 594 §1.4 主路径；与 Python 3.11 兼容；与 .venv-dbt 一致）+ 注释头（说明 paddle-ocr MOCK 路径不依赖此文件实际安装 / 仅 spec 合规） |
| (D) **档 2 spec = executor_orient.sh + exec_wake.sh** | §4 (a) `scripts/executor_orient.sh` 创建（architect 起草 spec 已存在未提交；executor 审阅后调整 + commit + manifest bump）+ (b) `scripts/exec_wake.sh` enhancement（sound + title flash；保持 macOS 通知 + tmux send-keys fallback；不动 exec_wake.sh 既有逻辑） |
| (E) **manifest bump K → 934+K** | §5 K = Dockerfile + Dockerfile + manifest + executor_orient.sh + exec_wake.sh + 595 receipt + 可选 bump 脚本；enumeration 即权威 per 583 §F；INVARIANT 934+K == 934+K == 934+K ✓ |

### 0.2 本刀不做（执行端零擅自做）

| 禁止 | 守门 |
|---|---|
| ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 整体保持 CLOSED 候选 per 588 PASS + 590 PASS 双重声明；595 不二次宣告 |
| ❌ 重新宣告 O1 整体收口 | ✅ O1 整体保持 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律 |
| ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注（per 591 docs/50 row 117） |
| ❌ 引入 `--confirm-*` 字面（实跑）| ✅ 2026-08-29 治理铁律；零用户动作；supersede 标注明文「零 `--confirm-*` 字面」 |
| ❌ 实际安装 paddlepaddle 到 system site-packages | ✅ 仅写 manifest spec；不动 .venv-dbt / 任何现有 venv；不 pip install paddlepaddle 到真实 env（per 594 §0.2 红线延续） |
| ❌ 修改 `requirements-dbt.txt`（dbt env）| ✅ 红线 / 零 dbt env 污染 |
| ❌ 修改 001-014 migration 文件 | ✅ 红线 / 零生产 schema 变更 |
| ❌ 修改 01-core.sql | ✅ 红线 / 零核心 schema 变更 |
| ❌ 修改 4 fixture 锁值 | ✅ data/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ SHA 零漂移（`f34b2e57…` 1007943 bytes） |
| ❌ 修改 source_registry/registry.csv | ✅ 7 行未改 |
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 修改 docs/52 内容 | ✅ 仅 grep 命中计数参考；不动 docs/52 任何字节 |
| ❌ 修改 docs/45 / docs/49 / docs/50 / docs/53 既有 supersede 标注 | ✅ 595 仅在 (A)(B)(C)(D) 落地；docs/X supersede 仅在 589 / 591 / 593 三层 + K=0 minimization per 594；不动 docs/X 任何字节 |
| ❌ 删除命中行原文 | ✅ 红线 / 既有 OPEN 行零删减 |
| ❌ 启动 584 re-ACK 实际跑 paddle-ocr deps | ✅ 仅 BLOCKER 解除；584 re-ACK 任务书签发另刀（per 595 audit §L 推荐 #3 + 594 receipt §10 推荐） |
| ❌ 爬网 / 写 dbt/mart/前端 | ✅ 红线 / 零域外触碰 |
| ❌ 宣布 Gate 0/1/2 PASS / O1 PASS / O3 PASS | ✅ 红线 / 仅 BLOCKER 解除 |
| ❌ 引入 cloud OCR / GPU runtime | ✅ per 594 §0.2 红线延续 |
| ❌ 引入 Docker Desktop for Mac | ✅ 路径 a (Colima) 优先；非生产 critical |

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

# Step 2: 启动 Colima + Docker daemon（首次启动可能需要 2-5 分钟下载 Linux VM）
colima start --cpu 2 --memory 4 --disk 20

# Step 3: 验证 docker daemon 可达
docker info 2>&1 | head -20
# 预期: Server Version / Storage Driver / Name 显示 colima 信息

# Step 4: 验证 docker ps
docker ps 2>&1
# 预期: CONTAINER ID 列空但有表头（无容器在跑）

# Step 5: hello-world 验证
docker run --rm hello-world
# 预期: "Hello from Docker!" 输出 + exit 0
```

### 1.3 验证清单

| 项 | 预期 | 验证命令 |
|---|---|---|
| docker CLI | exit 0 + version 显示 | `docker --version` |
| docker daemon | reachable + Server info | `docker info` |
| docker ps | exit 0 + 表头 | `docker ps` |
| docker run hello-world | "Hello from Docker!" + exit 0 | `docker run --rm hello-world` |
| colima status | "colima is running" | `colima status` |
| docker socket | /var/run/docker.sock 存在 | `ls -la ~/.colima/default/docker.sock` |

### 1.4 P2 BLOCKER 状态落地

```yaml
P2 BLOCKER 状态（after 595）:
  - docker CLI 安装: ✅ YES (via Colima)
  - docker daemon 可达: ✅ YES (colima daemon running)
  - docker socket 可访问: ✅ YES (~/.colima/default/docker.sock)
  - Colima runtime: ✅ running (2 CPU + 4 GB RAM + 20 GB disk)
  - hello-world 验证: ✅ PASS
  - P2 BLOCKER 整体: ✅ PASS (唯一保留 BLOCKER 解除)
```

---

## §2. (B) P3 BLOCKER 解除 = Dockerfile 起草

### 2.1 Dockerfile spec（per docs/52 B 路 spec；不修改 docs/52 字节）

```dockerfile
# Dockerfile - paddle-ocr / paddlepaddle runtime
# per 595 tasking §2 + docs/52 B 路 spec + 594 §1.4 备选 paddlepaddle==2.6.2
# 用途: paddle-ocr deps 引入运行时环境；非 production-critical；仅 spec 合规

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy paddle deps manifest
COPY requirements-paddle.txt /app/requirements-paddle.txt

# Install paddlepaddle (per 594 §1.4 主路径 paddlepaddle==2.6.2; 与 Python 3.11 兼容)
RUN pip install --no-cache-dir -r /app/requirements-paddle.txt

# Copy project source (保留以备扩展；当前非 production-critical)
COPY . /app/

# Default entrypoint
ENTRYPOINT ["python"]
CMD ["--version"]
```

### 2.2 创建路径

```
./Dockerfile
```

### 2.3 验证清单

| 项 | 预期 | 验证命令 |
|---|---|---|
| 文件存在 | ✅ | `ls -la Dockerfile` |
| base image | python:3.11-slim | `grep 'FROM python:3.11-slim' Dockerfile` |
| paddlepaddle 声明 | paddlepaddle==2.6.2 | `grep 'paddlepaddle==2.6.2' Dockerfile`（间接通过 requirements-paddle.txt） |
| COPY requirements-paddle.txt | ✅ | `grep 'COPY requirements-paddle.txt' Dockerfile` |
| 不含 cloud OCR / GPU | ✅ | `grep -v 'cloud\|gpu' Dockerfile`（无匹配） |

### 2.4 P3 BLOCKER 状态落地

```yaml
P3 BLOCKER 状态（after 595）:
  - 项目 Dockerfile 存在: ✅ YES (./Dockerfile)
  - Dockerfile base image: ✅ python:3.11-slim (per 594 §1.4 Python 3.11 路径)
  - Dockerfile paddlepaddle 声明: ✅ paddlepaddle==2.6.2 (per 594 §1.4 备选主路径)
  - docs/52 Dockerfile 标注: 0 occurrences (594 已 grep; 595 不修改 docs/52 字节)
  - P3 BLOCKER 整体: ✅ PASS (auto-accept 决策已落地)
```

---

## §3. (C) P4 BLOCKER 解除 = paddlepaddle==2.6.2 manifest 写入

### 3.1 manifest 文件 spec

**路径**: `./requirements-paddle.txt`（独立文件，不污染 `requirements-dbt.txt` dbt env）

```yaml
# requirements-paddle.txt - paddle-ocr / paddlepaddle runtime deps
# per 595 tasking §3 + docs/49 §5.2.1 paddle-ocr 引擎选型 (用户 2026-08-28 裁定)
# + 594 §1.4 paddlepaddle==2.6.2 (2.x 系列最后版本; 与 Python 3.11 兼容; 与 .venv-dbt 一致)
# 用途: Dockerfile pip install -r 使用; 实际 venv 不依赖此文件 (paddle-ocr MOCK only 路径)
# 注释: paddlepaddle==2.6.2 是 2.x 系列最后版本 (2.5.2/2.6.0/2.6.1/2.7.0 已下架; 3.0.0 - 3.3.1 跨大版本)

paddlepaddle==2.6.2
```

### 3.2 创建路径

```
./requirements-paddle.txt
```

### 3.3 验证清单

| 项 | 预期 | 验证命令 |
|---|---|---|
| 文件存在 | ✅ | `ls -la requirements-paddle.txt` |
| paddlepaddle 声明 | paddlepaddle==2.6.2 | `grep 'paddlepaddle==2.6.2' requirements-paddle.txt` |
| 注释头完整 | ✅ | `head -5 requirements-paddle.txt` |
| `requirements-dbt.txt` 未改 | 7 行不变 | `wc -l requirements-dbt.txt` = 8（1 注释 + 7 dbt deps）|

### 3.4 P4 BLOCKER 状态落地

```yaml
P4 BLOCKER 状态（after 595）:
  - paddlepaddle 声明状态: ✅ paddlepaddle==2.6.2 (in requirements-paddle.txt)
  - 主 deps manifest 状态: ✅ 不变 (requirements-dbt.txt 7 行 dbt deps 不污染)
  - paddle-ocr deps 引入路径: ✅ spec 落地 (实际 install 由 Dockerfile 决定; 595 不实际 install)
  - P4 BLOCKER 整体: ✅ PASS (auto-accept 决策已落地)
```

---

## §4. (D) 档 2 spec = executor_orient.sh + exec_wake.sh enhancement

### 4.1 (a) scripts/executor_orient.sh 创建

**路径**: `scripts/executor_orient.sh`

**架构师起草 spec（已存在未提交）**: architect 在本次会话前期已起草 `scripts/executor_orient.sh` 作为 spec（untracked file）。**执行端审阅 + 调整 + commit**。

**审阅要点**:
- ✅ Pull (ff-only) → 解析 §CURRENT → 显示当前刀号 / status / 红线条数 → 提示下一步
- ✅ 不 commit / 不 push / 不改 00-CC-CURRENT.md（只读）
- ✅ Bash UTF-8 lexer 修复（architect 已修：`）` → ASCII `)` 在 echo 行；详见 §4.1.1）
- ✅ 头部标识：`# executor_orient.sh — 执行端启动时一行自检`

**审阅 + 调整 + commit 后验证**:
```bash
bash scripts/executor_orient.sh
# 预期: ORIENT 头部 + KNIFE / STATUS / TASKING / RED / AUDITS 显示 + 提示下一步
```

**manifest 影响**: NEW spike_helper role +1（enumeration 即权威 per 583 §F）

### 4.1.1 ⚠️ architect 起草 spec 的 UTF-8 mojibake 修复说明

**问题**: 原始 spec 在 echo 行使用 `）`（UTF-8: `ef bc 89`）紧接 `$LATEST_AUDIT_NAME` 变量后；bash lexer 将 `）` 的字节 `e/f/b/c/8/9` 视为变量名扩展字符，导致变量扩展为空 + 字节剥离。

**修复**: 将 echo 行的 `）` 替换为 ASCII `)`：

```bash
# 原始 spec（有 bug）
echo "  RED     $RED_LINES 项红线（per $LATEST_AUDIT_NAME）"

# 修复后（architect 已修）
echo "  RED     $RED_LINES red lines (per $LATEST_AUDIT_NAME)"
```

**executor 验证**:
```bash
bash scripts/executor_orient.sh 2>&1 | grep 'RED'
# 预期: RED     25 red lines (per 595-stage0-architect-s594-eval-584-deps-reack-trigger-audit-PASS-20260829.md)
```

**注**: 595 receipt 实际验证此修复正确性。

### 4.2 (b) scripts/exec_wake.sh enhancement（sound + title flash）

**路径**: `scripts/exec_wake.sh`（既有；增强）

**增强 spec**:
- 保留既有 macOS 通知（`osascript -e 'display notification ...'`）+ tmux send-keys fallback
- 新增 sound alert（`afplay /System/Library/Sounds/Glass.aiff` 或 `Ping.aiff`；可配置）
- 新增 Terminal/iTerm2 title flash（通过 escape sequence；macOS Terminal.app + iTerm2 兼容）
- 不破坏既有行为（向后兼容）
- 不改 exec_wake.sh 的 §wake 调用接口

**executor 实施步骤**:
```bash
# Step 1: 阅读现有 exec_wake.sh
cat scripts/exec_wake.sh

# Step 2: 增强 sound + title flash（保持既有逻辑）
# - 在 notify 之后添加 afplay 调用（可选 sound 配置）
# - 在 tmux send-keys 之前添加 ANSI title escape sequence

# Step 3: 验证
bash scripts/exec_wake.sh
# 预期: macOS 通知 + Glass.aiff sound + Terminal title flash "🔔 EXEC-PULSE: 595 PENDING"
```

**manifest 影响**: NEW spike_helper role +1（如分类变更；如未变更则 0 bump；enumeration 即权威）

### 4.3 档 2 验收清单

| 项 | 验证 |
|---|---|
| `scripts/executor_orient.sh` 存在 + 可执行 + 输出正确 | ✅ |
| `scripts/executor_orient.sh` 不 commit 自身（仅 spec 输出）| ✅ |
| `scripts/executor_orient.sh` 不改 00-CC-CURRENT.md | ✅ |
| `scripts/exec_wake.sh` 既有行为保留 | ✅ |
| `scripts/exec_wake.sh` 新增 sound + title flash | ✅ |
| manifest bump 反映 NEW scripts（如有）| ✅ |

---

## §5. (E) manifest bump K → 934+K

### 5.1 K 枚举（enumeration 即权威 per 583 §F）

| K 项 | 文件 | role | 大小预估 |
|---|---|---|---|
| K1 | `./Dockerfile` | spike_helper | ~600 bytes |
| K2 | `./requirements-paddle.txt` | spike_helper | ~300 bytes |
| K3 | `scripts/executor_orient.sh` | spike_helper | ~2.5 KB |
| K4 | `scripts/exec_wake.sh`（增强）| spike_helper（如分类不变=0；如变更=+1）| +500 bytes |
| K5 | `reviews/.../595-...-receipt.md` | documentation | ~30 KB |
| K6 | `scripts/_knife595_manifest_bump.py`（可选）| spike_helper（如未复用上 bump 脚本）| ~7 KB |
| **K 合计** | **K = 5（无 K6 时）或 K = 6（含 K6）**| | |

**manifest 末态**: 934 + K（K = 5 或 6；enumeration 即权威）

**INVARIANT**: 934+K == 934+K == 934+K ✓

### 5.2 提交规范

```bash
# Step 1: bump script（如 K6）开发 + dry-run
python3 scripts/_knife595_manifest_bump.py --dry-run
python3 scripts/_knife595_manifest_bump.py

# Step 2: 单 commit feat(595)
git add Dockerfile requirements-paddle.txt scripts/executor_orient.sh scripts/exec_wake.sh scripts/_knife595_manifest_bump.py reviews/.../595-...-receipt.md evidence_pack/manifest.json reviews/.../00-EXEC-QUEUE.md
git commit -m "feat(595): BLOCKER 解除刀 (P2 Docker 安装 + P3 Dockerfile 起草 + P4 paddlepaddle==2.6.2 manifest 写入) + 档 2 (executor_orient.sh + exec_wake.sh enhancement) + manifest bump K → 934+K"

# Step 3: 双推
git push origin HEAD
git push github HEAD

# Step 4: cc_head backfill (separate commit, per 593 + 591 + 589 + 594 平行模式)
# 在 receipt §双推 + §0 manifest 末态表述中填回 feat commit SHA + 物理 manifest 末态
git add reviews/.../595-...-receipt.md
git commit -m "chore(595): cc_head backfill — populate §CURRENT commit SHA + receipt §双推 + cc_head metadata"
git push origin HEAD
git push github HEAD

# Step 5: 通知架构师 + 跑 exec_wake.sh
bash scripts/exec_wake.sh
```

---

## §6. 红线自检（执行端落实）

| # | 红线 | 状态 |
|---|---|---|
| 1 | ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS | ✅ 595 仅 BLOCKER 解除；O3 保持 CLOSED 候选 per 588 + 590 双重声明；O1 保持 WAITING_FILE per docs/47 + 用户披露 + 2026-08-29 治理铁律 |
| 2 | ❌ 2020-2025 batch work | ✅ 零批量 |
| 3 | ❌ HTTP source crawl | ✅ 零爬网（Colima docker daemon 仅本地 Linux VM） |
| 4 | ❌ OCR threshold lowering | ✅ 零阈值调整 |
| 5 | ❌ 1909-as-China | ✅ 零历史边界触碰 |
| 6 | ❌ --force | ✅ git push 走普通路径 |
| 7 | ❌ PAT request | ✅ 零 PAT |
| 8 | ❌ gate_thresholds.json edit | ✅ 3709 bytes / mtime Aug 23 不变 |
| 9 | ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 状态保持 CLOSED 候选 |
| 10 | ❌ 重新宣告 O1 整体收口 | ✅ O1 状态保持 WAITING_FILE |
| 11 | ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注 |
| 12 | ❌ 引入 --confirm-* 字面（实跑）| ✅ 2026-08-29 治理铁律；零用户动作；零 `--confirm-*` 字面 |
| 13 | ❌ 实际安装 paddlepaddle 到 system site-packages | ✅ 仅写 manifest spec；不动现有 venv；不 pip install paddlepaddle 到真实 env |
| 14 | ❌ 修改 requirements-dbt.txt（dbt env）| ✅ 红线 / 零 dbt env 污染 |
| 15 | ❌ 修改 001-014 migration 文件 | ✅ 零触碰 |
| 16 | ❌ 修改 01-core.sql | ✅ 零触碰 |
| 17 | ❌ 修改 scripts/（除 K3/K4 NEW/enhanced）| ✅ scripts/intake_real_sha_if_present.py / auto_ingest_public_source.py 零触碰 |
| 18 | ❌ 修改 4 fixture 锁值 | ✅ data/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门 |
| 19 | ❌ 修改 S0 原始 PDF 字节 | ✅ 零触碰 |
| 20 | ❌ 修改 source_registry/registry.csv | ✅ 7 行未改 |
| 21 | ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 3709 bytes 不变 |
| 22 | ❌ 修改 docs/52 内容 | ✅ 仅 grep 命中计数参考；不动 docs/52 字节 |
| 23 | ❌ 修改 docs/45 / docs/49 / docs/50 / docs/53 既有 supersede | ✅ 595 仅在 (A)(B)(C)(D) 落地；docs/X 零修改 |
| 24 | ❌ 删除命中行原文 | ✅ 既有 OPEN 行零删减 |
| 25 | ❌ 启动 584 re-ACK 实际跑 paddle-ocr deps | ✅ 仅 BLOCKER 解除；584 re-ACK 任务书签发另刀 |
| 26 | ❌ 爬网 / 写 dbt/mart/前端 | ✅ 零域外触碰 |
| 27 | ❌ 引入 cloud OCR / GPU runtime | ✅ per 594 §0.2 红线延续 |
| 28 | ❌ 引入 Docker Desktop for Mac | ✅ 路径 b Colima 优先 |
| 29 | ✅ INVARIANT 934+K == 934+K == 934+K | ✅ enumeration 即权威 |
| 30 | ✅ 零用户动作 / 零 `--confirm-*` 字面（实跑）| ✅ per 2026-08-29 治理铁律 |
| 31 | ✅ B 路（公开源自动获取）保持主路径 | ✅ docs/52 B 路 11 + 主路径 8 标注完整 |
| 32 | ✅ O1 整体仍 WAITING_FILE | ✅ O1 状态保持 |
| 33 | ✅ O3 整体仍 CLOSED 候选 | ✅ O3 状态保持 |

✅ **PASS 预期** — 33 项红线 100% 兑现，零触碰，零违规。

---

## §7. 任务-回执映射（executor 落地后回报）

执行端 595 回执必须包含：

- 任务-交付映射（按 §0.1 (A)(B)(C)(D)(E) 顺序）
- 命令输出（P2 §1.2 docker info / docker run hello-world；P3 §2.3 Dockerfile 验证；P4 §3.3 manifest 验证；§4.3 档 2 验收）
- 改动路径（5-6 文件：Dockerfile + requirements-paddle.txt + scripts/executor_orient.sh + scripts/exec_wake.sh + reviews/.../595-...-receipt.md + evidence_pack/manifest.json + reviews/.../00-EXEC-QUEUE.md）
- manifest delta（934 → 934+K；K enumeration 5 或 6）
- INVARIANT 验证（934+K == 934+K == 934+K）
- 双推 + cc_head（origin → github 顺序执行；cc_head separate commit per 593 + 591 + 589 + 594 平行模式）
- 红线自检（33 项）
- 零网络复跑（如有 pytest）

---

## §8. 下次心跳预期

- knife 595 落地后（P2 Docker 安装 + P3 Dockerfile 起草 + P4 manifest 写入 + 档 2 executor_orient.sh + exec_wake.sh enhancement + commit + 双推 + 回执签发）：
  - 架构师审计 `596-stage0-architect-s595-blocker-relief-dockerfile-deps-audit-…md`（PASS/FAIL）
  - 若 PASS：584 BLOCKER 矩阵 5 → 0 全闭环 + 档 2 spec 落地 + 596 tasking 签发（584 re-ACK 准备就绪刀 / O1 §5.2.x 真实 SHA-locked 江苏样本刀 / 其它治理推进刀）
  - 若 FAIL：`596-correction` 回合（修 Colima 安装路径 / 修 Dockerfile 起草 / 修 manifest 写入 / 修 executor_orient.sh spec / 修 exec_wake.sh enhancement / 修 manifest bump arithmetic / re-commit）

---

## §9. 关联文件清单

- 任务书：`reviews/stage0-gate0-rework-2026-08-23/595-stage0-architect-s594-blocker-relief-dockerfile-deps-tasking-20260829.md`（本文件）
- 审计依据：`reviews/stage0-gate0-rework-2026-08-23/595-stage0-architect-s594-eval-584-deps-reack-trigger-audit-PASS-20260829.md`（PASS）
- 上一刀回执：`reviews/stage0-gate0-rework-2026-08-23/594-stage0-cc-eval-584-deps-reack-trigger-tasking-20260829-receipt.md`（DELIVERED → AUDITED per 595 PASS）
- 上一刀审计：`reviews/stage0-gate0-rework-2026-08-23/594-stage0-architect-s593-eval-584-deps-reack-trigger-tasking-20260829.md`（tasking 594 = eval刀 tasking 文件）
- 上一刀审计（593 → 594 audit）：`reviews/stage0-gate0-rework-2026-08-23/594-stage0-architect-s593-docs-sync-full-sweep-audit-PASS-20260829.md`（PASS）
- 关联任务书：`reviews/stage0-gate0-rework-2026-08-23/594-stage0-architect-s593-eval-584-deps-reack-trigger-tasking-20260829.md`（594 = docs-only 评估刀）
- 关联任务书：`reviews/stage0-gate0-rework-2026-08-23/584-stage0-architect-s583-o3-impl-paddle-ocr-deps-tasking-20260829.md`（584 BLOCKED-DEFERRED per Path C；594 评估已重 BLOCKER 5 → 1）
- 关联回执：`reviews/stage0-gate0-rework-2026-08-23/594-stage0-cc-eval-584-deps-reack-trigger-tasking-20260829-receipt.md`（DELIVERED → AUDITED per 595 PASS）
- docs/52：`docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md`（B 路 11 + Dockerfile 0 + paddle-ocr 0 + 主路径 8；595 仅 grep 命中计数参考，不修改 docs/52 字节）
- Dockerfile：`./Dockerfile`（NEW K1 spike_helper）
- paddle manifest：`./requirements-paddle.txt`（NEW K2 spike_helper）
- executor_orient：`scripts/executor_orient.sh`（NEW K3 spike_helper；architect 起草 spec 已存在未提交）
- exec_wake：`scripts/exec_wake.sh`（K4 增强 spike_helper；保留既有 macOS 通知 + tmux fallback）
- bump 脚本：`scripts/_knife595_manifest_bump.py`（可选 K6 spike_helper；复用 K 模式）
- 595 receipt：`reviews/stage0-gate0-rework-2026-08-23/595-stage0-cc-blocker-relief-dockerfile-deps-tasking-20260829-receipt.md`（K5 documentation）

---

— End of `595-stage0-architect-s594-blocker-relief-dockerfile-deps-tasking-20260829.md` —

> ⚠ **本任务书不宣布 Gate 0/1/2 / O1 PASS / O3 PASS**（per 595 §红线 + docs/34 §1 + O3 整体保持 CLOSED 候选 per 588 PASS + 590 PASS 双重声明 + O1 整体保持 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律）。
> ⚠ **本任务书非 docs-only 评估刀**（per 594 §0.2 + 595 §0.2；实际环境变更：Docker 安装 + Dockerfile 起草 + manifest 写入 + 档 2 scripts 落地）。
> ⚠ **O3 整体仍 CLOSED 候选**（per 588 PASS + 590 PASS 双重声明；595 不二次宣告 O3 状态）。
> ⚠ **O1 整体仍 WAITING_FILE**（per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 595 BLOCKER 解除刀落地后另刀下发）。
> ⚠ **584 BLOCKER 数量 5 → 0 落地目标**（595 落地后：P2 ✅ PASS via Colima + P3 ✅ PASS via Dockerfile 起草 + P4 ✅ PASS via requirements-paddle.txt 写入 = 全闭环；584 重 ACK 准备就绪路径 = 596 tasking 签发）。
> ⚠ **档 2 spec（2026-08-28 夜 user 批准）**：architect cron self-wake（架构师自检 cron）+ executor_orient.sh 创建 + exec_wake.sh enhancement（sound + title flash）= 同步执行；architect 起草 spec 已存在未提交（untracked file）；executor 审阅 + commit + manifest bump。
> ⚠ **B 路（公开源自动获取）保持主路径**（per docs/52 B 路 11 + 主路径 8 标注完整）。
> ⚠ **docs/52 字节不动**（595 仅 grep 命中计数参考；不动 docs/52 任何字节）。
> ⚠ **零 paddlepaddle 实际安装到 system site-packages**（per 594 §0.2 红线延续；仅 manifest spec；Dockerfile 内部 install 由 docker daemon 决定；不动现有 venv）。
> ⚠ **零 docker daemon 启动 systemctl 操作**（per 594 §0.2 红线延续；Colima 启动 = `colima start` 用户态；不操作 launchctl / systemctl）。
> ⚠ **零 Dockerfile / requirements.txt 实际写入 requirements-dbt.txt**（独立文件 requirements-paddle.txt；不污染 dbt env）。
> ⚠ **零 584 re-ACK 实际启动**（per 595 §0.2 红线；仅 BLOCKER 解除；584 re-ACK 任务书签发另刀）。
> ⚠ **零 docs/X 任何字节修改**（595 仅在 (A)(B)(C)(D) 落地；docs/45 / docs/49 / docs/50 / docs/52 / docs/53 全部零修改）。
> ⚠ **594 audit 文件随 595 commit 入库**（per 591 tasking「审计文件不单独 commit，随下一刀入库」+ 594 audit 不单独 commit）。
> ⚠ **589 row 119 + 591 row 117 + 593 全 docs + 594 BLOCKER 评估 + 595 BLOCKER 解除 五层 supersede / 评估 / 解除 链**（per 589 + 591 + 593 + 594 教训模式 + 594 audit §L 推荐 #3）。
> ⚠ **INVARIANT: 934+K == 934+K == 934+K ✓**（per enumeration wins per 583 §F；K = 5 或 6）。
