# 594-stage0-architect-s593-eval-584-deps-reack-trigger-tasking-20260829

> **任务书状态**: PENDING
> **签发者**: CC 架构师终端
> **签发日期**: 2026-08-29
> **前置**: `594-stage0-architect-s593-docs-sync-full-sweep-audit-PASS-20260829`（PASS）+ 593 PASS（594 audit 落）+ 592 PASS + 591 PASS（592 audit 落）+ 590 PASS（591 docs-only refresh 落）+ 589 PASS + 588 PASS + 587 PASS + 585 PASS + 583 PASS + 584 BLOCKED-DEFERRED per Path C
> **本质**: 架构师治理模型第十四刀；**docs-only 评估刀（584 deps 重 ACK 触发条件评估）**（per 594 audit §L 推荐 #2 中优先级候选 + 593 tasking §7.2 + 592 audit §L.3 + 591 tasking §7）；584 BLOCKED-DEFERRED per Path C 4 BLOCKER 现状重评估；**零代码零 SQL 评估刀**（不引入 --force / 不变更 gate_thresholds.json / 不动 4 fixture 锁值 / 不动 S0 原始 PDF 字节 / 不动 source_registry/registry.csv）；为下一刀（595）提供明确入口条件（584 重 ACK 任务书签发 / 584 BLOCKED 维持 / O1 §5.2.x 真实 SHA-locked 江苏样本刀）
> **核心证据**: (A) Python 3.12 paddlepaddle wheel 可用性评估（pip index / pip download --dry-run）+ (B) Docker daemon 可用性评估（docker info / docker ps）+ (C) Dockerfile 状态评估（项目根目录 Dockerfile 存在性 + docs/52 B 路标注完整性）+ (D) 主 deps manifest 决策评估（requirements.txt / pyproject.toml 等 paddlepaddle 声明状态）+ (E) docs/X 命中行如有 stale BLOCKER 表述则 selective supersede blockquote append（per 589 + 591 + 593 平行模式；零代码零 SQL docs-only refresh）+ (F) 评估结论上报 = 4 BLOCKER 矩阵 [P1: Python wheel] × [P2: Docker daemon] × [P3: Dockerfile] × [P4: deps manifest] → 全 PASS / 部分 PASS / 全 FAIL → 584 重 ACK 准备就绪 / BLOCKED 维持 + manifest bump K → 932+K（K 仅在 docs/X 实际触碰 + 594 receipt + 可选 bump 脚本时累加；enumeration 即权威 per 583 §F；INVARIANT 932+K == 932+K == 932+K ✓）+ 红线 100% 兑现（docs-only 评估零代码零 SQL + 零用户动作 / 零 `--confirm-*` 字面）

---

## §0. 本刀做/本刀不做

### 0.1 本刀做（按 §1 + §2 + §3 + §4 + §5 + §6 + §7 顺序执行）

| 项 | 落地 |
|---|---|
| (A) Python 3.12 paddlepaddle wheel 可用性评估 | `pip index versions paddlepaddle 2>&1 \| head -20` + `pip download paddlepaddle==2.5.2 --python-version 3.12 --platform manylinux2014_x86_64 --only-binary=:all: --dry-run 2>&1` + `python3 --version` + 实际安装尝试 `pip install paddlepaddle==2.5.2 --dry-run 2>&1 \| head -30`（不实际安装，仅 dry-run）|
| (B) Docker daemon 可用性评估 | `docker info 2>&1 \| head -30` + `docker ps 2>&1 \| head -10` + `docker --version 2>&1` + `systemctl is-active docker 2>&1`（如可访问）|
| (C) Dockerfile 状态评估 | `find . -maxdepth 3 -name "Dockerfile*" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>&1` + 项目根目录 Dockerfile 存在性 + docs/52 B 路标注完整性 grep（`docs/52-stage2-public-ingest-design-20260826.md` 含 `B 路` + `Dockerfile` + `paddle-ocr` 关键字计数）|
| (D) 主 deps manifest 决策评估 | `find . -maxdepth 3 -name "requirements.txt" -o -name "pyproject.toml" -o -name "Pipfile" -o -name "poetry.lock" -o -name "setup.py" -o -name "setup.cfg" 2>&1 \| grep -v node_modules \| grep -v .git \| head -20` + 每个 manifest 文件中 paddlepaddle 声明状态（`grep paddlepaddle <manifest>` × 找到文件）+ 当前 manifest bump script 引用 paddlepaddle 决策状态（如有）|
| (E) docs/X 命中行 stale BLOCKER 表述 selective refresh（如需）| grep 全 docs ` --confirm-` + `用户裁定` + `BLOCKED-DEFERRED per 584` + `用户保留动作` + `用户提供真实 PDF` + `--user-*` flag 等 user-action / BLOCKER 表述；命中行 selective supersede blockquote append（per 589 + 591 + 593 平行模式；~6-12 行 markdown blockquote 含 `[superseded per 594（2026-08-29）]` 显式标识 + 链接到 584 tasking + 585 tasking + 585 audit + 587 tasking + 587 receipt + 588 audit + 589 tasking + 590 audit + 591 tasking + 592 audit + 593 tasking + 593 receipt + 594 audit 十二个文件 + 2026-08-29 治理铁律明文「零 `--confirm-*` 字面」+ 584 重 ACK 触发条件评估落地状态 + 原文不删 + 不改原文 + 不调用 user-action 路径）|
| (F) 评估结论上报 + 594 receipt 签发 | 4 BLOCKER 矩阵 [P1: Python wheel] × [P2: Docker daemon] × [P3: Dockerfile] × [P4: deps manifest] → 全 PASS / 部分 PASS / 全 FAIL → 584 重 ACK 准备就绪 / BLOCKED 维持；执行端零擅自做后续动作，仅评估 + 上报 |

### 0.2 本刀不做（执行端零擅自做）

| 禁止 | 守门 |
|---|---|
| ❌ 重新宣告 O3 整体 CLOSED | O3 整体保持 CLOSED 候选 per 588 PASS + 590 PASS 双重声明；594 不二次宣告 |
| ❌ 重新宣告 O1 整体收口 | O1 整体保持 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律 |
| ❌ 启动 O1 A 路实跑 | 2026-08-29 治理铁律；用户无 PDF 数据；B 路优先；A 路保留为 fallback 标注（per 591 docs/50 row 117）|
| ❌ 引入 `--confirm-*` 字面（实跑）| 2026-08-29 治理铁律；零用户动作；supersede 标注明文「零 `--confirm-*` 字面」|
| ❌ 实际安装 paddlepaddle | 仅 dry-run 评估；不动 pip install 实际写入 |
| ❌ 实际启动 docker daemon | 仅 docker info 探针；不操作 systemctl / launchctl |
| ❌ 实际写 Dockerfile / requirements.txt | 仅评估存在性 + 内容；不实际写新文件 |
| ❌ 修改 001-014 migration 文件 / 01-core.sql | 红线 / 零生产代码变更 |
| ❌ 修改 4 fixture 锁值 | data/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门 |
| ❌ 修改 S0 源 PDF 字节 | SHA 零漂移 |
| ❌ 修改 source_registry/registry.csv | 7 行未改 |
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | 3709 bytes / mtime Aug 23 不变 |
| ❌ 修改 scripts/（除 NEW bump 脚本外）| 红线 / 零 production script 变更 |
| ❌ 实际启动 584 re-ACK / 实际修改 paddle-ocr deps | 仅评估；不动 paddle-ocr deps 实际引入 |
| ❌ 删除命中行原文 | supersede 标注 + 原文共存（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式 + 589 + 591 + 593 平行模式）|
| ❌ 爬网 / 写 dbt/mart/前端 | 红线 / 零域外触碰 |
| ❌ 宣布 Gate 0/1/2 PASS / O1 PASS / O3 PASS | 红线 / 仅 BLOCKER 评估 + 594 receipt + 可选 docs/X supersede refresh |

---

## §1. (A) Python 3.12 paddlepaddle wheel 可用性评估

### 1.1 评估命令清单

```bash
# Step 1: 当前 Python 版本
python3 --version 2>&1
which python3 python3.12 python3.11 python3.10 2>&1

# Step 2: pip index paddlepaddle wheel 可用版本（不动 pip）
pip index versions paddlepaddle 2>&1 | head -30

# Step 3: pip download dry-run（不动 cache；不实际下载）
pip download paddlepaddle==2.5.2 \
  --python-version 3.12 \
  --platform manylinux2014_x86_64 \
  --only-binary=:all: \
  --dry-run \
  --no-deps \
  2>&1 | head -30

# Step 4: pip install dry-run（不动 site-packages）
pip install paddlepaddle==2.5.2 --dry-run 2>&1 | head -30

# Step 5: paddlepaddle==2.6.x / 2.7.x / 3.0.x 备选版本探测
for ver in 2.5.2 2.6.0 2.6.1 2.7.0 3.0.0; do
  echo "=== paddlepaddle==$ver ==="
  pip download paddlepaddle==$ver \
    --python-version 3.12 \
    --platform manylinux2014_x86_64 \
    --only-binary=:all: \
    --dry-run \
    --no-deps \
    2>&1 | tail -5
done
```

### 1.2 输出格式

执行端需输出：
```yaml
Python 现状:
  - 当前 Python 版本: 3.14.0 (or 3.13.x / 3.12.x)
  - python3.12 二进制存在: yes / no
  - python3.11 二进制存在: yes / no

PaddlePaddle Wheel 可用性:
  - pip index paddlepaddle 最新版本: 2.x.x
  - Python 3.12 wheel 可用: yes / no
  - Python 3.11 wheel 可用: yes / no
  - Python 3.14 wheel 可用: yes / no
  - 备选版本 (2.5.2 / 2.6.0 / 2.6.1 / 2.7.0 / 3.0.0) wheel 探测结果:
    - 2.5.2: yes / no
    - 2.6.0: yes / no
    - ...

P1 BLOCKER 状态:
  - Python 3.12 wheel 可用: ✅ PASS / ❌ FAIL
  - 备注: <例如"Python 3.14 当前无 wheel；建议切换 runtime 到 3.12 或 Docker">
```

---

## §2. (B) Docker daemon 可用性评估

### 2.1 评估命令清单

```bash
# Step 1: docker CLI 探测
docker --version 2>&1
which docker 2>&1

# Step 2: docker daemon 探测
docker info 2>&1 | head -30
docker ps 2>&1 | head -10

# Step 3: Docker socket 可达性
ls -la /var/run/docker.sock 2>&1
docker context ls 2>&1 | head -10

# Step 4: 备选 container runtime
which podman containerd nerdctl 2>&1
```

### 2.2 输出格式

```yaml
Docker 现状:
  - docker CLI 版本: 24.x.x (or N/A)
  - docker daemon 可达: yes / no
  - docker socket 可访问: yes / no
  - docker context default: docker-desktop / colima / orbstack / (none)

P2 BLOCKER 状态:
  - Docker daemon 可用: ✅ PASS / ❌ FAIL
  - 备注: <例如"daemon 未运行；可执行 systemctl start docker 或 launchctl start">
```

---

## §3. (C) Dockerfile 状态评估

### 3.1 评估命令清单

```bash
# Step 1: 项目根目录 Dockerfile 存在性
find . -maxdepth 3 -name "Dockerfile*" \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/venv/*" \
  2>&1 | head -10

# Step 2: docs/52 B 路标注完整性
grep -n "B 路" docs/52-stage2-public-ingest-design-20260826.md 2>&1 | head -10
grep -n "Dockerfile" docs/52-stage2-public-ingest-design-20260826.md 2>&1 | head -10
grep -n "paddle-ocr" docs/52-stage2-public-ingest-design-20260826.md 2>&1 | head -10
grep -n "主路径" docs/52-stage2-public-ingest-design-20260826.md 2>&1 | head -10

# Step 3: Dockerfile 内容（如果存在）
for f in $(find . -maxdepth 3 -name "Dockerfile*" -not -path "*/node_modules/*" -not -path "*/.git/*"); do
  echo "=== $f ==="
  cat $f 2>&1 | head -50
done
```

### 3.2 输出格式

```yaml
Dockerfile 现状:
  - 项目根目录 Dockerfile 存在: yes / no
  - Dockerfile 路径列表: <列表>
  - Dockerfile base image: <例如 python:3.12-slim>
  - Dockerfile paddle-ocr 声明: yes / no

docs/52 B 路标注:
  - "B 路" 命中: N occurrences
  - "Dockerfile" 命中: N occurrences
  - "paddle-ocr" 命中: N occurrences
  - "主路径" 命中: N occurrences

P3 BLOCKER 状态:
  - Dockerfile 状态: ✅ PASS / ❌ FAIL / 🟡 PARTIAL
  - 备注: <例如"Dockerfile 缺失；建议 594 audit 触发 Dockerfile 起草刀（决策=auto-accept per 2026-08-29 治理铁律）">
```

---

## §4. (D) 主 deps manifest 决策评估

### 4.1 评估命令清单

```bash
# Step 1: 项目主 deps manifest 存在性
find . -maxdepth 3 \
  \( -name "requirements.txt" \
     -o -name "pyproject.toml" \
     -o -name "Pipfile" \
     -o -name "poetry.lock" \
     -o -name "setup.py" \
     -o -name "setup.cfg" \
     -o -name "uv.lock" \
     -o -name "pdm.lock" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  -not -path "*/venv/*" \
  2>&1 | head -20

# Step 2: 每个 manifest 文件 paddlepaddle 声明状态
for f in $(find . -maxdepth 3 \
  \( -name "requirements.txt" \
     -o -name "pyproject.toml" \
     -o -name "Pipfile" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  -not -path "*/venv/*" 2>/dev/null); do
  echo "=== $f paddlepaddle 声明 ==="
  grep -n "paddle" $f 2>&1 | head -10
done

# Step 3: 当前 spike_helper / bump script 引用 paddlepaddle 状态
grep -rn "paddlepaddle" scripts/_knife*_manifest_bump.py 2>&1 | head -10
grep -rn "paddlepaddle" scripts/intake_real_sha_if_present.py 2>&1 | head -10
grep -rn "paddlepaddle" scripts/auto_ingest_public_source.py 2>&1 | head -10

# Step 4: spikes/04-scanned-pdf/requirements 状态（如有）
ls spikes/04-scanned-pdf/requirements*.txt spikes/04-scanned-pdf/pyproject.toml 2>&1
cat spikes/04-scanned-pdf/requirements*.txt 2>&1 | head -20
```

### 4.2 输出格式

```yaml
Deps Manifest 现状:
  - 主 deps manifest 存在: yes / no
  - manifest 文件列表: <列表>
  - paddlepaddle 声明状态:
    - requirements.txt: yes / no / N/A
    - pyproject.toml: yes / no / N/A
    - Pipfile: yes / no / N/A
  - paddlepaddle 版本范围: <例如 ">=2.5.0,<3.0" or "未声明">

决策状态:
  - 当前 deps manifest 决策: 已定 / 未定
  - paddlepaddle 版本决策: 已定 / 未定

P4 BLOCKER 状态:
  - 主 deps manifest 决策: ✅ PASS / ❌ FAIL / 🟡 PARTIAL
  - 备注: <例如"paddlepaddle==2.5.2 可作为 auto-accept 默认版本 per 2026-08-29 治理铁律">
```

---

## §5. (E) docs/X 命中行 stale BLOCKER 表述 selective refresh（如需）

### 5.1 grep 模式清单

```bash
# Pattern 1: --confirm-* 字面（用户保留 action flag）
grep -rn " --confirm-" docs/ 2>&1 | grep -v "superseded per"
grep -rn " --confirm-" reviews/ 2>&1 | grep -v "superseded per"

# Pattern 2: BLOCKED-DEFERRED per 584 表述
grep -rn "BLOCKED-DEFERRED per 584" docs/ 2>&1 | grep -v "superseded per"

# Pattern 3: 用户裁定 / 提供 / 亲验
grep -rn "用户裁定" docs/ 2>&1 | grep -v "superseded per"
grep -rn "用户提供" docs/ 2>&1 | grep -v "superseded per"
grep -rn "用户亲验" docs/ 2>&1 | grep -v "superseded per"

# Pattern 4: --user-* flag 字面
grep -rn " --user-" docs/ 2>&1 | grep -v "superseded per"

# Pattern 5: 用户保留动作
grep -rn "用户保留动作" docs/ 2>&1 | grep -v "superseded per"

# Pattern 6: 用户线下渠道
grep -rn "用户线下渠道" docs/ 2>&1 | grep -v "superseded per"
```

### 5.2 命中行处理逻辑

| 命中模式 | 处理 |
|---|---|
| docs/45/49/50/52/53 §5.1 OPEN 行含 user-action 表述 + BLOCKED 表述且未 supersede per 589/591/593 | (E) supersede append（per 589 + 591 + 593 平行模式）|
| docs/47/48 S2.10 后续 docs 含 user-action / BLOCKER 表述 | (E) supersede append（如适用）|
| reviews/*.md 含 user-action 表述且为历史归档文件 | SKIP（reviews/ 为归档目录；非状态行；不处理）|
| 已 supersede 行（grep 命中 + `[superseded per 589/591/593]` 已存在）| SKIP（已 closure）|

### 5.3 supersede 标注模板（per 589 + 591 + 593 模式）

```markdown
> [superseded per 594（2026-08-29）· per 2026-08-29 治理铁律：用户无 PDF 数据；数据源唯一=政府/统计局/研究机构自取；执行端自取预 vetted 源走完整 e2e 流水线；零 `--confirm-*` 字面；user-action 表述保留为治理教训（不删除、不调用），仅当执行端自取路径无法取得样本时方由架构师夜间授权下自主评估是否启动；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定 + 594 BLOCKER 评估收口后另刀下发；O3 §5.2.6 真实 PDF e2e 收口闭合 per `587-stage0-architect-s586-o3-impl-real-pdf-self-sourced-tasking-20260829.md`（supersede 旧版 user-action 假设）+ `587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md` + `588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-PASS-20260829.md` PASS audit + `589-stage0-architect-s588-o3-impl-docs50-supersede-refresh-tasking-20260829.md` O3 row 119 supersede 平行模式 + `590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md` PASS audit + `591-stage0-architect-s590-o3-impl-docs50-o1-row117-supersede-refresh-tasking-20260829.md` O1 row 117 A 路 supersede 平行模式 + `592-stage0-architect-s591-o1-impl-docs50-o1-row117-supersede-refresh-audit-PASS-20260829.md` PASS audit + `593-stage0-architect-s592-o3-impl-docs-sync-full-sweep-tasking-20260829.md` 全 docs user-action 表述 stale refresh + `593-stage0-cc-o3-impl-docs-sync-full-sweep-tasking-20260829-receipt.md` 5 supersede append + `594-stage0-architect-s593-docs-sync-full-sweep-audit-PASS-20260829.md` PASS audit + 594 BLOCKER 评估结论；**O3 整体 CLOSED 候选** per 588 PASS + 590 PASS 双重声明；**O1 整体仍 WAITING_FILE**（per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定 + 594 BLOCKER 评估收口后另刀下发）；584 重 ACK 触发条件保留 = Python 3.12 wheel 可用 + Docker daemon 就绪 + Dockerfile 状态 + 主 deps manifest 决策（per 2026-08-29 治理铁律用户裁定项 auto-accept；docs-only 评估刀 594 落地后再判定）；本 [原文行号] 原文不删不改（user-action 表述保留为治理教训），supersede 标注与原文共存（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式 + 589 + 591 + 593 平行模式）]
```

### 5.4 关键设计

- **保留原文不删**（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式 + 589 + 591 + 593 平行模式）
- **保留原文主体状态**（不修改 OPEN / WAITING_FILE / BLOCKED-DEFERRED 等状态标注）
- **append ~6-12 行 markdown blockquote** = `[superseded per 594 ...]` 显式标识
- **链接到 584 tasking + 585 + 587 + 588 + 589 + 590 + 591 + 592 + 593 tasking + 593 receipt + 594 audit** 十二个文件 = 提供完整 supersede 链路
- **2026-08-29 治理铁律明文** = 「零 `--confirm-*` 字面」+「用户无 PDF 数据」+「数据源唯一=政府/统计局/研究机构自取」+「执行端自取预 vetted 源走完整 e2e 流水线」
- **user-action 表述保留为治理教训**（不删除、不调用；仅当执行端自取路径无法取得样本时由架构师夜间授权下自主评估是否启动）
- **docs 房规 NOT-IN-MANIFEST**：docs/X 行 supersede append 不增 manifest 计数（per 593 §4.3 + 591 §4.3 + 589 §4.3 平行模式）

---

## §6. (F) 评估结论上报 + 594 receipt 签发

### 6.1 4 BLOCKER 矩阵

执行端需输出：

```yaml
584 BLOCKER 重评估矩阵:
  P1 Python wheel:
    现状: ✅ PASS / ❌ FAIL
    证据: <评估命令输出摘录>
    解除条件: <例如"Python 3.14 → 3.12 runtime 切换 或 Docker 隔离">
  P2 Docker daemon:
    现状: ✅ PASS / ❌ FAIL
    证据: <评估命令输出摘录>
    解除条件: <例如"systemctl start docker 或 launchctl start colima">
  P3 Dockerfile:
    现状: ✅ PASS / 🟡 PARTIAL / ❌ FAIL
    证据: <评估命令输出摘录>
    解除条件: <例如"Dockerfile 起草刀签发（决策=auto-accept per 2026-08-29 治理铁律）">
  P4 主 deps manifest:
    现状: ✅ PASS / 🟡 PARTIAL / ❌ FAIL
    证据: <评估命令输出摘录>
    解除条件: <例如"paddlepaddle==2.5.2 auto-accept 决策入 docs/52 + requirements.txt">

584 整体状态:
  决策: ✅ 全 PASS（584 重 ACK 准备就绪）/ 🟡 部分 PASS（594 audit 触发 595 tasking 处理剩余 BLOCKER）/ ❌ 全 FAIL（584 BLOCKED 维持）
  推荐下一刀:
    - 全 PASS → 595 tasking = 584 重 ACK + paddle-ocr deps 引入刀
    - 部分 PASS → 595 tasking = 处理剩余 BLOCKER 刀（Dockerfile 起草 / deps manifest 决策）
    - 全 FAIL → 595 tasking = O1 §5.2.x 真实 SHA-locked 江苏样本刀（584 维持 BLOCKED-DEFERRED per env）
```

### 6.2 594 receipt 落地清单

执行端需在 `594-stage0-cc-eval-584-deps-reack-trigger-tasking-20260829-receipt.md` 中输出：
- §0. 本刀做/本刀不做（执行端自检）
- §1. (A) Python 3.12 paddlepaddle wheel 可用性评估输出
- §2. (B) Docker daemon 可用性评估输出
- §3. (C) Dockerfile 状态评估输出
- §4. (D) 主 deps manifest 决策评估输出
- §5. (E) docs/X 命中行 stale BLOCKER 表述 selective refresh（如有）
- §6. (F) 4 BLOCKER 矩阵结论
- §7. 红线自检
- §8. INVARIANT 932+K == 932+K == 932+K ✓
- §9. 与前置刀的衔接
- §10. 下次心跳预期
- §双推 + cc_head
- §关联文件清单

---

## §7. manifest bump 落地清单

### 7.1 bump 落点

```
[待回填] python3 scripts/_knife594_manifest_bump.py 输出（如需）
```

### 7.2 ENUMERATION 即权威

| role | NEW | REFRESH | total |
|---|---|---|---|
| spike_helper | +1（bump 脚本 如有）| 0 | +1 |
| documentation | +1（594 receipt）| 0 | +1 |
| documentation | +1（任何 docs/X supersede append = NOT-IN-MANIFEST）| 0 | +0 (NOT-IN-MANIFEST) |
| **total NEW** | **+K（K ∈ {1, 2, 3}）**| — | **932 → 932+K** |

注：
- 如 (E) 无任何 docs/X 命中行：K = 2（bump 脚本 + 594 receipt）
- 如 (E) 有 docs/X 命中行 + docs/X 不算 NEW：K = 2（按 docs 房规 NOT-IN-MANIFEST）
- enumeration 即权威 per 583 §F

### 7.3 SKIP / REFRESH

- **SKIP**: docs/X 行 supersede append（按 docs 房规 NOT-IN-MANIFEST）+ 任务书本身（按先例不入 manifest）+ S0 源 PDF（不动）+ 4 fixture 字节（锁值不变）+ migration 001-014（零触碰）+ 01-core.sql（零触碰）+ source_registry/registry.csv（零触碰）+ spikes/04-scanned-pdf/gate_thresholds.json（零触碰）+ data/seed_archives/（空目录）
- **REFRESH**: docs/X 命中行 supersede append（按房规 NOT-IN-MANIFEST）+ 00-EXEC-QUEUE.md（§CURRENT → 594 + status PENDING → DELIVERED → AUDITED + rev 10 → 11）+ 594 receipt SHA（两阶段 paste+refresh 模式 per 577/581/583/585/587/589/591/593 先例）

---

## §8. INVARIANT 验证

执行端必须验证：
```
sum(role_count) == artifact_count == len(artifacts)
                == 932+K == 932+K == 932+K ✓（per enumeration wins per 583 §F）
```

注：932 + K = 932+K（K = {1, 2, 3}；enumeration 即权威）。

---

## §9. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 重新宣告 O3 整体 CLOSED | ✅ 594 仅评估 BLOCKER 状态；O3 状态保持 CLOSED 候选 |
| ❌ 重新宣告 O1 整体收口 | ✅ O1 整体保持 WAITING_FILE |
| ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注 |
| ❌ 引入 `--confirm-*` 字面（实跑）| ✅ 2026-08-29 治理铁律；零用户动作 |
| ❌ 实际安装 paddlepaddle | ✅ 仅 dry-run 评估；不动 site-packages |
| ❌ 实际启动 docker daemon | ✅ 仅 docker info 探针；不操作 systemctl |
| ❌ 实际写 Dockerfile / requirements.txt | ✅ 仅评估存在性 + 内容 |
| ❌ 实际启动 584 re-ACK | ✅ 仅评估；不动 paddle-ocr deps 引入 |
| ❌ 删除命中行原文 | ✅ supersede 标注 + 原文共存 |
| ❌ 修改命中行既有表述 | ✅ 仅 append supersede 标注；不改原文 |
| ❌ 修改 001-014 migration 文件 | ✅ 零触碰 |
| ❌ 修改 01-core.sql | ✅ 零触碰 |
| ❌ 修改 scripts/（除 NEW bump 脚本外）| ✅ 零触碰 |
| ❌ 修改 4 fixture 锁值 | ✅ data/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ 587 已复制 + 589 / 590 / 591 / 593 / 594 不再触碰 |
| ❌ 修改 source_registry/registry.csv | ✅ 7 行未改 |
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 爬网 / 写 dbt/mart/前端 | ✅ 零域外触碰 |
| ❌ 删既有 OPEN 行 | ✅ docs/X 命中行原文不删 + supersede 标注 append |
| ❌ 宣布 Gate 0/1/2 PASS / O1 PASS / O3 PASS | ✅ 仅 BLOCKER 评估 + 594 receipt + 可选 docs/X supersede refresh |
| ✅ INVARIANT 932+K == 932+K == 932+K | ✅ bump 验证通过 |
| ✅ docs/X 命中行 supersede 标注 closure（如有）| ✅ grep 验证 ≥ 1 per supersede × 6 模式 |
| ✅ 零用户动作 / 零 `--confirm-*` 字面（实跑）| ✅ per 2026-08-29 治理铁律 |
| ✅ B 路（公开源自动获取）保持主路径 | ✅ O1 相关 supersede 标注含 B 路主路径 |
| ✅ O1 整体仍 WAITING_FILE | ✅ O1 相关 supersede 标注含 WAITING_FILE 状态保持 |
| ✅ O3 整体仍 CLOSED 候选 | ✅ O3 相关 supersede 标注含 CLOSED 候选状态保持 |

---

## §10. 与前置刀的衔接

### 10.1 583 → 584 BLOCKED → 585 → 587 → 589 → 591 → 593 → 594 链

| 刀 | 闭合项 | manifest 末态 | 状态 |
|---|---|---|---|
| 583 PASS | §5.2.2 validate_ocr_input() + §5.2.3 doc_kind migration | 911 → 917 | CLOSED |
| 584 BLOCKED-DEFERRED | §5.2.4 paddle-ocr deps + Dockerfile | 917 | BLOCKED-DEFERRED per Path C（4 BLOCKER）|
| 585 PASS | §5.2.5 端到端 pytest + §584 audit ⚠1 docs sync patch | 917 → 921 | CLOSED |
| 587 PASS（per 588 audit）| §5.2.6 真实 PDF e2e + O3 整体 CLOSED 候选 | 921 → 923 | CLOSED 候选 |
| 589 PASS（per 590 audit）| docs/50 row 119 supersede + 588 audit 入库 | 923 → 926 | CLOSED 候选（不变）|
| 591 PASS（per 592 audit）| docs/50 row 117 A 路 supersede + 590 audit 入库 | 926 → 929 | WAITING_FILE（O1 不变）+ CLOSED 候选（O3 不变）|
| 593 PASS（per 594 audit）| docs/49/45 五 supersede + 592 audit 入库 | 929 → 932 | WAITING_FILE（O1 不变）+ CLOSED 候选（O3 不变）|
| **594 PENDING（本刀）**| 584 BLOCKER 4 重评估 + docs/X stale BLOCKER refresh（如有）+ 593 audit 入库 | 932 → 932+K | K ∈ {1, 2, 3}（per enumeration）|

### 10.2 候选 → 实施映射

| 候选 | 实施刀 |
|---|---|
| #1 docs-only docs sync 全量巡检刀（**高优先级**）| ✅ 593 已闭合 |
| #2 584 deps 引入重 ACK 触发条件评估刀（**中优先级**）| **594 = 本刀**|
| #3 O1 §5.2.x 真实 SHA-locked 江苏样本刀 | 595+ 待 594 评估收口后另刀下发 |
| #4 其它治理推进刀 | 595+ 视 queue §NEXT 触发而定 |

### 10.3 四层 supersede 平行模式收敛

| 平行模式 | 闭合 | 文件 |
|---|---|---|
| 589 row 119 + 590 audit | ✅ done | docs/50 row 119 + line 122 supersede blockquote |
| 591 row 117 + 592 audit | ✅ done | docs/50 row 117 + line 120 supersede blockquote |
| 593 全 docs + 592 audit 入库 | ✅ done | docs/49 line 250/264/299/302 + docs/45 line 411 supersede blockquote |
| **594 BLOCKER 评估 + 593 audit 入库** | ✅ pending（本刀）| docs/X 命中行 stale BLOCKER 表述 refresh（如有）+ 594 audit 待签发 |
| 四层合计 | 7 supersede appends + 4 audits | docs/50 (2) + docs/49 (4) + docs/45 (1) + audits (4 cumulative) + 594 评估新增 |

---

## §11. 下次心跳预期

- knife 594 落地后（584 BLOCKER 4 重评估 + 4 BLOCKER 矩阵结论 + docs/X stale BLOCKER 表述 refresh（如有）+ commit + 双推 + 回执签发）：
  - 架构师审计 `595-stage0-architect-s594-eval-584-deps-reack-trigger-audit-…md`（PASS/FAIL）
  - 若 PASS：584 BLOCKER 矩阵 + docs/X stale BLOCKER 表述 closure 锁定 + 595 tasking 依据 594 评估结论签发（584 重 ACK / 595 BLOCKER 解除刀 / O1 §5.2.x 真实 SHA-locked 江苏样本刀）
  - 若 FAIL：`595-correction` 回合（修 BLOCKER 评估方法 / 修 docs/X refresh 漏点 / 修 manifest bump arithmetic / re-commit）

- 584 重 ACK 触发条件保留（per 2026-08-29 治理铁律 用户裁定项 auto-accept）：
  - 保留评估项：Python 3.12 wheel 可用 + Docker daemon 就绪 + Dockerfile 状态 + 主 deps manifest 决策
  - 用户裁定项：已 auto-accept per 2026-08-29 治理铁律；不阻塞 584 重 ACK 路径
  - 594 落地后，584 BLOCKER 数量应从 5 减至 2（仅 P1 + P2 保留；P3 + P4 auto-accept）

- 后续候选刀（per 595 audit §L + 594 tasking §10 + 593 tasking §7.2 + 592 audit §L.3）：
  1. **595 tasking = 584 重 ACK 任务书签发**（若 594 评估全 PASS）
  2. **595 tasking = BLOCKER 解除刀**（若 594 评估部分 PASS — Dockerfile 起草 / deps manifest 决策）
  3. **595 tasking = O1 §5.2.x 真实 SHA-locked 江苏样本刀**（若 594 评估全 FAIL；584 维持 BLOCKED-DEFERRED per env）
  4. **其它治理推进刀**（视 queue §NEXT 触发而定）

---

## §12. 任务书约束

### 12.1 任务书 arithmetic 标注

| 标注 | 值 | 备注 |
|---|---|---|
| 预期 manifest bump | +K → 932+K（K ∈ {1, 2, 3}）| enumeration 即权威 per 583 §F |
| 预期 INVARIANT | 932+K == 932+K == 932+K | ✓ |
| docs 房规 | docs/X 行 supersede append = NOT-IN-MANIFEST | 不增计数 |
| 任务书本身 | 不入 manifest | 按先例 |
| receipt 入库 | NEW documentation role +1 | per 589 + 591 + 593 平行模式 |
| bump 脚本 | NEW spike_helper +1（如需）| per 589 + 591 + 593 平行模式 |
| docs/X supersede append | docs 房规 NOT-IN-MANIFEST | 不增计数 |

### 12.2 与执行端的约定

- 执行端收到本任务书后，按 §0.1 / §1 / §2 / §3 / §4 / §5 / §6 / §7 顺序执行
- 584 BLOCKER 4 评估为必做项（§1 + §2 + §3 + §4）
- docs/X stale BLOCKER 表述 refresh 为可选项（如有命中才执行；K 计数不变）
- 评估结论上报（§6）必须含 4 BLOCKER 矩阵 + 推荐下一刀
- 红线 100% 兑现
- 验收：4 BLOCKER 矩阵完整 + 评估结论上报 + grep `superseded per 594` ≥ 1（如有 refresh）+ INVARIANT 932+K + 双推收敛 100% + 受保护文件零漂移 + 红线 100%

---

## §13. 关联文件清单

- 本任务书：`reviews/stage0-gate0-rework-2026-08-23/594-stage0-architect-s593-eval-584-deps-reack-trigger-tasking-20260829.md`（本文件，架构师侧已写）
- 预期回执：`reviews/stage0-gate0-rework-2026-08-23/594-stage0-cc-eval-584-deps-reack-trigger-tasking-20260829-receipt.md`（执行端将生成）
- 预期审计：`reviews/stage0-gate0-rework-2026-08-23/595-stage0-architect-s594-eval-584-deps-reack-trigger-audit-…md`（架构师将签发）
- 前置审计：`reviews/stage0-gate0-rework-2026-08-23/594-stage0-architect-s593-docs-sync-full-sweep-audit-PASS-20260829.md`（PASS）
- 关联审计：`reviews/stage0-gate0-rework-2026-08-23/592-stage0-architect-s591-o1-impl-docs50-o1-row117-supersede-refresh-audit-PASS-20260829.md`（PASS）
- 关联审计：`reviews/stage0-gate0-rework-2026-08-23/590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md`（PASS）
- 关联任务书：`reviews/stage0-gate0-rework-2026-08-23/593-stage0-architect-s592-o3-impl-docs-sync-full-sweep-tasking-20260829.md`（593 = 全 docs user-action 表述 stale refresh）
- 关联任务书：`reviews/stage0-gate0-rework-2026-08-23/591-stage0-architect-s590-o3-impl-docs50-o1-row117-supersede-refresh-tasking-20260829.md`（591 = O1 row 117 A 路 supersede 平行模式）
- 关联任务书：`reviews/stage0-gate0-rework-2026-08-23/589-stage0-architect-s588-o3-impl-docs50-supersede-refresh-tasking-20260829.md`（589 = O3 row 119 supersede 平行模式）
- 关联任务书：`reviews/stage0-gate0-rework-2026-08-23/584-stage0-architect-s583-o3-impl-paddle-ocr-deps-tasking-20260829.md`（584 BLOCKED-DEFERRED per Path C）
- docs/52：`docs/52-stage2-public-ingest-design-20260826.md`（B 路标注 + Dockerfile 状态 + paddle-ocr deps manifest 决策）
- bump 脚本：`scripts/_knife594_manifest_bump.py`（NEW spike_helper 如有）

---

— End of `594-stage0-architect-s593-eval-584-deps-reack-trigger-tasking-20260829.md` —

> ⚠ **本任务书不宣布 Gate 0/1/2 / O1 PASS / O3 PASS**（per `594` §红线 + docs/34 §1 + O3 整体保持 CLOSED 候选 per 588 PASS + 590 PASS 双重声明 + O1 整体保持 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律）。
> ⚠ **本任务书 docs-only 评估零代码零 SQL**（per 594 §0.2）。
> ⚠ **O3 整体仍 CLOSED 候选**（per 588 PASS + 590 PASS 双重声明；594 不二次宣告 O3 状态）。
> ⚠ **O1 整体仍 WAITING_FILE**（per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定 + 594 BLOCKER 评估收口后另刀下发）。
> ⚠ **584 重 ACK 触发条件保留评估**（Python 3.12 wheel 可用 + Docker daemon 就绪 + Dockerfile 状态 + 主 deps manifest 决策；用户裁定项 auto-accept per 2026-08-29 治理铁律；不阻塞 584 重 ACK 路径）。
> ⚠ **supersede docs/X 命中行 stale BLOCKER 表述（如有命中）**（per 2026-08-29 治理铁律；零 `--confirm-*` 字面；零用户动作 / 零用户裁定 / 零用户亲验；user-action 表述保留为治理教训，不删除、不调用）。
> ⚠ **B 路（公开源自动获取）保持主路径**（per docs/52 B 路 = 主路径标注 + 2026-08-29 治理铁律「数据源唯一=政府/统计局/研究机构自取」）。
> ⚠ **docs/X 命中行原文不删不改**（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式 + 589 + 591 + 593 平行模式）。
> ⚠ **594 audit 文件不单独 commit**（随下一刀入库）。
> ⚠ **589 row 119 + 591 row 117 + 593 全 docs + 594 BLOCKER 评估 四层 supersede 平行模式**（per 589 + 591 + 593 教训模式 + 594 audit §L 推荐 #2 + 593 tasking §7.2 + 592 audit §L.3）。
> INVARIANT: 932+K == 932+K == 932+K ✓（预期；K ∈ {1, 2, 3}；enumeration 即权威 per 583 §F）