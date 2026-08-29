# 00-EXEC-QUEUE — 架构师 ↔ 执行端 交接队列（新治理模型 · 唯一状态源）

> Cursor 已退役；本文件取代 `00-CC-CURRENT.md` 的调度职能（后者冻结于 rev 320，勿读勿写）。
> 唤醒链路：架构师写本文件 + 跑 `scripts/exec_wake.sh`（macOS 通知）→ 执行端 session 内 EXEC-PULSE 自检（或用户粘贴一句"跟单"）。
> 本文件为治理工具，随 `577` 交付 commit 入库（manifest `documentation`）；此后每刀 bump SHA REFRESH（不增计数）。

## §META

- rev: 4
- updated: 2026-08-29
- architect: CC 架构师终端（本仓库唯一任务书/审计签发方；不写实现、不 commit）
- executor: CC 执行终端（本仓库目录内运行；按任务书执行、自验、回执、commit、双推）
- ruling: 用户（O1 / O3 / Gate 2 / 抽查）；**常设授权（2026-08-28 夜起生效）：需用户裁定项一律按架构师推荐自动执行**；例外 = 必须用户亲自操作项（注册/登录/付费/UI 人工验收/提供真实文件如 O3 的 `--confirm-o3=PATH` PDF）；仓库常备红线不因授权失效（不宣布 Gate PASS、不 --force、不公网 redeploy 等仍按红线）

## §CURRENT

- tasking: `reviews/stage0-gate0-rework-2026-08-23/584-stage2-paddle-ocr-deps-tasking-20260829.md`
- status: **DELIVERED（BLOCKED）**   <!-- PENDING → ACK → DELIVERED → AUDITED；只改本行 -->
- issued: 2026-08-29
- note: **O3 §5.2.4 paddle-ocr 引擎依赖刀**（per docs/49 §5.2.4；引擎 paddle-ocr per `579` 裁定 / §5.2.1 已关闭）= (A) `paddleocr` + `paddlepaddle` 依赖引入（`requirements.txt` 或 `pyproject.toml` deps append；deps 引入决策单独披露 = 版本 / 镜像层体积 / 系统库依赖 / license / 离线 wheel / build 时间成本 / 与 stdlib `mimetypes` 协同）+ (B) Dockerfile paddle-ocr 独立 layer（既有 `FROM` / `RUN pip install <既有 deps>` 零触动；paddle-ocr deps 单独 `RUN pip install paddleocr paddlepaddle` 段 + 单独 `COPY` cache key；`docker build` exit 0 + 镜像体积实测 + layer 分段验证）+ (C) `tests/test_paddle_ocr_deps_584.py` NEW 7+ 例覆盖（import / version / CPU-only / 离线能力 / 零 cloud OCR client / §584 audit ⚠1 docs sync 落点）+ (D) **§584 audit ⚠1 docs sync patch**（docs/45 L93 + L487 + docs/53 L203 + L207 + docs/50 L228 五处 `916` → `917` 修正；docs sync 不动 manifest / 不动 commit SHA）；**完成定义** = 全量 pytest 0 failed + Dockerfile build exit 0 + paddle-ocr deps 引入决策披露 + manifest 923 不变量 + §584 audit ⚠1 docs sync patch 落点验证；**§5.2.5 e2e pytest + §5.2.6 真实 PDF 用户保留动作 仍 OPEN**；**前置 584 审计 PASS**（583 修复刀交付 validate_ocr_input API + migration 014 doc_kind；manifest 917 不变量成立；⚠1 docs sync gap 入本刀 patch 闭合）；**584 = DELIVERED BLOCKED** = 执行端勘察发现 4 BLOCKER：(BLOCKER-1) `pip index versions paddlepaddle` = ERROR No matching distribution（Python 3.14 无 wheel）= deps 安装不可验证；(BLOCKER-2) 项目无 Dockerfile（零 baseline = layer 增量前提不成立）+ 无 requirements.txt / pyproject.toml 主 manifest（仅 requirements-dbt.txt）= deps append 路径需指定；(BLOCKER-3) Docker daemon 不可用 = `docker build` exit 0 验证不可执行；(BLOCKER-4) §E manifest 923 invariant 在 BLOCKED 下不可达（deps + Dockerfile + test = +3 文件不可落地）。回执 `584-stage0-cc-paddle-ocr-deps-tasking-20260829-receipt.md` 已落（含 4 BLOCKER 详单 + 架构师修订路径 A/B/C 建议）；manifest 917 不变量保持（无 bump）；待架构师按 A/B/C 修订任务书后重 ACK 重跑。**红线 100% 兑现**（不强行 partial 执行 / 不引入 cloud OCR / 不引入 GPU runtime / 不写真实 OCR pipeline / 不写真实 PDF fixture / 不修改 001-014 / 不修改 01-core.sql / 不修改 scripts/ / 不修改 4 fixture / 不爬网 / 不写 dbt/mart/前端 / 不宣布 Gate PASS / 既有 OPEN 行零删减）。

## §DELIVERED（584 BLOCKED）

- 2026-08-29 / CC-exec（Claude Code 执行终端，584 BLOCKED 交付） / 回执 `584-stage0-cc-paddle-ocr-deps-tasking-20260829-receipt.md`（4 BLOCKER：Python 3.14 无 paddlepaddle wheel + 项目零 baseline Dockerfile/requirements.txt + Docker daemon 不可用 + manifest 923 invariant 不可达；架构师修订路径 A/B/C 已附） → 待架构师修订任务书

## §AUDITED（584 PASS）

- 2026-08-29 / CC-arch（架构师审计终端） / 583 receipt PASS（`584-stage0-architect-s583-o3-impl-validate-api-doc-kind-audit-PASS-20260829`；A–H 证据段全达成 + ⚠1 docs/45 §7 链头 916 vs actual 917 docs sync gap ACCEPTED with disclosure [不动 commit / 不动 manifest / 仅 docs 文案对齐 actual 917 — 入下刀 patch] + ⚠2 INCONSISTENT-1 enumeration 收口 917 ACCEPTED + ⚠3 h2 deselect 续登 ACCEPTED；manifest 917 不变量成立；红线零违反）→ 584 tasking 签发（O3 §5.2.4 paddle-ocr 引擎依赖刀）

## §AUDITED（582 PASS）

- 2026-08-29T00:0x+08:00 / CC-arch（架构师审计终端） / 581 receipt PASS（`582-stage0-architect-s581-inherited-fix-audit-PASS-20260828`；9 证据段 A–I + ⚠4/⚠5 ACCEPTED with disclosure + ⚠6 四刀零 ⚠ 计数偏差复发；manifest 911 不变量成立；红线零违反）→ 583 签发（O3 实装首刀）

## §ACK

- 2026-08-29 / CC-exec（Claude Code 执行终端，跟单触发 / 跟单 584） / 开始执行 → 交付回执号待回填
- 2026-08-29T00:0x+08:00 / CC-exec（Claude Code 执行终端，跟单触发） / 开始执行 → 交付回执号待回填
- 2026-08-28T22:46+08:00 / CC-exec（Claude Code 执行终端，579 同 session） / 开始执行 → 交付 `fd483d1` + backfill `36aea26` → `582` 审计 PASS

## §ACK（579 刀存档）

- 2026-08-28T22:25+08:00 / CC-exec（Claude Code 执行终端，577 同 session） / 开始执行 → 交付 `6524155` + `81188dc` → `580` 审计 PASS

## §ACK（577 刀存档）

- 2026-08-28T21:30+08:00 / CC-exec（Claude Code 执行终端，574 同 session） / 开始执行 → 交付 `c8e2b9a` + `7c9668e` → `578` 审计 PASS

## §STATE 规则

| status | 含义 | 谁写 |
|---|---|---|
| PENDING | 任务书已签发，待执行端认领 | 架构师 |
| ACK | 执行端已认领开工 | 执行端（+§ACK 一行） |
| DELIVERED | 回执落盘 + 双推完成，待审计 | 执行端（回执号写进 note） |
| AUDITED | 架构师审计出档（PASS/FAIL 写 note） | 架构师 |
