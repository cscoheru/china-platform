# 585-stage0-architect-s584-o3-impl-paddle-ocr-deps-audit-BLOCKED-20260829

> **审计状态**: BLOCKED · Path C 采纳
> **审计者**: 架构师（CC 架构师终端）
> **审计日期**: 2026-08-29
> **审计对象**: knife 584 paddle-ocr deps 引入刀
> **前置**: knife 583 实装首刀 PASS（per `583-stage0-cc-o3-impl-validate-api-doc-kind-receipt-20260828`）
> **任务书**: `585-stage2-o3-impl-e2e-pytest-tasking-20260829`（架构师治理模型第七刀）
> **后续**: knife 585 e2e pytest 刀 paddle-ocr MOCK only 与 deps 解耦（per `585-stage0-cc-o3-impl-e2e-pytest-tasking-20260829-receipt`）

---

## §0. 审计结论（BLOCKED-DEFERRED · Path C）

**架构师裁决**: paddle-ocr deps 引入走后续刀（584 重 ACK 触发条件 = 用户裁定 + env 就绪 + 主 deps manifest 决策已定）；585 e2e pytest 刀 paddle-ocr MOCK only 与 deps 引入解耦。

**理由**: 584 触发环境实测发现 4 个 BLOCKER，paddlepaddle wheel 与 Python 3.14 不兼容是硬阻塞；不建议硬塞 Dockerfile layer / patch paddlepaddle 包内代码 / 切换 OCR 引擎走 tesseract/cloud（per 579 用户裁定 paddle-ocr 不可变更）；paddle-ocr deps 引入走后续刀。

---

## §1. 4 个 BLOCKER（584 env 实测发现）

### 1.1 BLOCKER 1: Python 3.14 无 paddlepaddle wheel

- **现象**: paddlepaddle 官方 wheel 仅发布到 Python 3.12，pip install paddlepaddle 在 Python 3.14 报 `Could not find a version that satisfies the requirement paddlepaddle`
- **影响**: 584 实装 paddle-ocr deps 引入必失败
- **解锁条件**: 等 paddlepaddle 官方 wheel 支持 3.14 / 降级 Python 到 3.12 / 切换 OCR 引擎（用户裁定）

### 1.2 BLOCKER 2: 项目零 baseline Dockerfile

- **现象**: 项目根目录无 Dockerfile，无镜像构建入口
- **影响**: paddle-ocr deps 引入需要镜像化隔离 Python 环境，缺 Dockerfile 无法走容器化路径
- **解锁条件**: 项目添加 baseline Dockerfile（可借鉴 puer-hub baseline Dockerfile）

### 1.3 BLOCKER 3: Docker daemon 不可用

- **现象**: 当前开发环境 `docker info` 报 daemon 不可用（per env 实测）
- **影响**: 即便有 Dockerfile 也无法 `docker build` / `docker run`
- **解锁条件**: env 启动 Docker daemon / 切换到可构建镜像的开发环境

### 1.4 BLOCKER 4: 主 deps manifest 缺失

- **现象**: 项目无 `requirements.txt` / `pyproject.toml` / `Pipfile` 等主 deps manifest
- **影响**: paddle-ocr deps 引入无统一声明位置；散落到各脚本零散 `pip install` 调用不可追踪
- **解锁条件**: 项目添加主 deps manifest 并约定 paddle-ocr deps 录入位置

---

## §2. Path C 决策详述

### 2.1 三选项对比

| 选项 | 内容 | 阻塞 | 建议 |
|---|---|---|---|
| **Path A** | 硬塞 Dockerfile + patch paddlepaddle 包内代码 + 降级 Python 3.12 | 高（破坏性变更 + paddlepaddle 包内代码 patch 不可持续） | ❌ 不建议 |
| **Path B** | 切换 OCR 引擎走 tesseract / cloud | 高（579 用户裁定 paddle-ocr 不可变更；tesseract 中文精度低；cloud 默认禁止） | ❌ 不建议 |
| **Path C** | paddle-ocr deps 引入走后续刀 + 585 e2e pytest 刀 paddle-ocr MOCK only 与 deps 解耦 | 无（584 暂缓 + 585 走 MOCK only 闭环 §5.2.5 e2e pytest） | ✅ **采纳** |

### 2.2 Path C 落地要点

- **584 暂缓**: 584 不实装 paddle-ocr deps 引入；584 任务书保留作为后续刀 plan 文档；584 重 ACK 触发条件登记于 §584 audit
- **585 e2e pytest 走 paddle-ocr MOCK only**: 585 任务书 §红线 paddle-ocr MOCK only / 零真实 PDF / 零触真实 DB / 零引入 cloud OCR / 零引入 GPU runtime
- **deps 引入解耦**: MOCK 路径与 deps 引入完全解耦，584 paddle-ocr deps 落地后无需重写 585 测试（仅 `patch.dict(sys.modules, ...)` 取消即可切换真实调用）

---

## §3. §584 audit ⚠1 docs sync gap 决议

### 3.1 gap 内容

584 落地时 docs sync patch 五处 916 → 917 未完成（per 583 落地后 manifest 917 + 584 落地后 docs sync 漏掉）：
1. `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` L93 demote 段 2 处
2. `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` L487 pack invariant table
3. `docs/53-stage2-public-ingest-ops-handbook-20260826.md` L203 第 44 项 blockquote D
4. `docs/53-stage2-public-ingest-ops-handbook-20260826.md` L207 第 44 项 blockquote 闭环
5. `docs/50-stage2-gate2-review-packet-draft-20260826.md` L228 §4.4 第 44 项行 D

### 3.2 决议

§584 audit ⚠1 docs sync patch deferred to 585 — 585 tasking §C 明确承担 docs/45 + docs/53 + docs/50 五处 docs sync 落点验证（test #⑨ §584 audit docs sync patch applied 验证 stale 916 = 0）。

### 3.3 closure 验证

- **执行**: knife 585 §D docs sync = docs/49 §5.2.4 BLOCKED-DEFERRED 标注 + §5.2.5 CLOSED 标注 + docs/53 §5 第 45 项 blockquote + docs/50 §4.4 +1 第 45 项行 + intro 链尾续接 + §5.1 O3 状态行 append 处置标注 + 本文件五处（文首 + §1 + §3 + §5.5 + §7）
- **核心证据**: pytest test #⑨ PASS（stale 916 = 0 + 917 ≥ 3）
- **归档**: 本审计文件（585-stage0-architect-s584-o3-impl-paddle-ocr-deps-audit-BLOCKED-20260829.md）作为 585 bump +4 中 +1 documentation 角色入库

---

## §4. 584 重 ACK 触发条件登记

584 重 ACK 触发条件（per 架构师 Path C 决议）：
1. **用户裁定**: 用户对 paddle-ocr deps 引入路径的明确裁定（继续 paddle-ocr / 切换 tesseract / 切换 cloud）
2. **env 就绪**: Python 3.14 有 paddlepaddle wheel（或 Python 降级到 3.12）
3. **主 deps manifest 决策已定**: 项目添加 requirements.txt / pyproject.toml 并约定 paddle-ocr deps 录入位置
4. **Dockerfile + Docker daemon**: 项目添加 baseline Dockerfile + env Docker daemon 可用

**保留事项**: 584 任务书按先例不入 manifest（per 583 audit `583-stage0-architect-s582-o3-impl-validate-api-doc-kind-audit-PASS-20260828`）；584 重 ACK 触发时另刀下发。

---

## §5. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate PASS | ✅ §0 + §2 多处显式守门 |
| ❌ 不删既有 OPEN 行 | ✅ §584 audit 决议 5.2.4 BLOCKED-DEFERRED + 5.2.6 OPEN 显式 |
| ❌ 不擅自收口 O3 | ✅ §3 显式 O3 整体仍 OPEN |
| ❌ 不引入未裁定的 OCR 引擎切换 | ✅ §2.1 Path B 不采纳 |
| ❌ 不擅自硬塞 Python 降级 / Dockerfile patch | ✅ §2.1 Path A 不采纳 |
| ✅ docs sync gap closure deferred to 585 | ✅ §3 + 585 test #⑨ 验证 |

---

— End of `585-stage0-architect-s584-o3-impl-paddle-ocr-deps-audit-BLOCKED-20260829` —

> ⚠ **本审计文件不宣布 O3 收口 / Gate PASS**。
> ⚠ **584 重 ACK 触发条件保留不变**（用户裁定 + env 就绪 + 主 deps manifest 决策已定）。
> ⚠ **O3 整体仍 OPEN**（5.2.4 BLOCKED-DEFERRED + 5.2.6 OPEN + 真实 PDF `--confirm-o3=PATH` 用户保留动作不变）。
> ⚠ **paddle-ocr MOCK only 与 deps 解耦**（585 e2e pytest 闭合 §5.2.5；deps 引入走后续刀）。