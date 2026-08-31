# 605-stage0-architect-s604-o1-§5.2.x-real-sha-locked-江苏样本-tasking-20260829

> **任务书类型**: 架构师签发 → 执行端实施（per ARCH-PULSE step 3 verbatim 583/585/587/589/591/593/594/595/596/597/598/599/600/601/602/603 平行模式）
> **触发依据**: 604 audit §8.1 + 603 receipt §8.1 候选 #1 verbatim "O1 §5.2.x 真实 SHA-locked 江苏样本刀（中优先级；待 docs/52 B 路落定后另刀下发；执行端自取预 vetted 公开源走完整 e2e 流水线）" + 2026-08-29 治理铁律（数据源唯一=政府/统计局/研究机构自取；用户零裁定；执行端不可提任何用户裁定事项）+ docs/52 B 路 spec 已 CLOSED per 599 audit PASS 落地（前置条件已满足）
> **前置**: 604 audit PASS（13 维度全 PASS + 2 ⚠ ACCEPTED + 零 FAIL；三侧收敛 `32a3059`）+ 603 PASS（docs/45 chain head refresh 收口刀落地）+ 602 audit PASS（84/84 验证项 + 三侧收敛 `9bf5cb9`）+ 601 PASS（docs/52 §14 + docs/51 §11 + docs/53 §11 + docs/45 §7 四 docs-only refresh 落点 closure）+ 600/599/597/595/594/593/591/589/587/585/583 全链 PASS
> **签发时间**: 2026-08-29
> **作者**: CC-arch（架构师；按 ARCH-PULSE step 3 verbatim 不写实现/不 commit/不 push）

---

## §0.1 本刀做

| 项 | 落地 |
|---|---|
| (A) 江苏样本源自取（执行端自取预 vetted 政府/统计局/研究机构公开源）| 执行端从江苏省统计局 / 江苏省统计年鉴 / 国家统计局江苏数据 等政府/统计局/研究机构公开源自取预 vetted 样本（如 `stats.jiangsu.gov.cn` 年度数据 / `tjj.jiangsu.gov.cn` 统计公报 / `stats.gov.cn` 江苏分省页面）；按 docs/52 B 路 spec 四步流水线（discover → download → sha256 → archive）；**零 `--confirm-*` 字面**；**零用户动作**；**零用户裁定**；**执行端零爬网公网（非政府域）**；仅政府/统计局/研究机构公开源 |
| (B) 江苏样本 SHA-locked 落 `data/seed_archives/` | sha256 验证 + 落入 `data/seed_archives/jiangsu_<source>_<YYYYMMDD>.pdf` 或 `<source>_<YYYYMMDD>.html`（per source 类型）；更新 `source_registry/registry.csv` +1 行（**⚠ disclosure**: source_registry/registry.csv 锁值不变；新增行而非修改既有 7 行；enumeration 即权威 per 583 §F；K3 计数加 1 但 NOT-IN-MANIFEST per docs 房规 + spike_helper 房规；source_registry/registry.csv bytes 变化是预期而非触碰红线的修改）|
| (C) paddle-ocr e2e 流水线（江苏样本）| `.venv-paddle/bin/python -c "from paddleocr import PaddleOCR; o = PaddleOCR(use_angle_cls=False, lang='ch'); r = o.ocr('/data/seed_archives/jiangsu_xxx.pdf', cls=False)"` 跑通（或 HTML 路径走 docs/53 §5 connector 模式）；**真实 paddle-ocr API 调用**（per 594 §0.2 红线：仅 `.venv-paddle` venv 内允许真实调用；system site-packages 零 paddlepaddle）；不修改 gate_thresholds.json；不修改 4 fixture 锁值 |
| (D) source_document + lineage JSONB 写入（江苏样本）| `source_document` 行新增 `doc_kind='OCR_SCAN'` + `source_sha256=<sha>` + `archive_path='data/seed_archives/jiangsu_xxx.pdf'`；`lineage` JSONB 写入 `{engine: 'paddle-ocr', version: '3.7.0', confidence: ..., page_count: ..., extracted_text: ..., source_sha256: <sha>, captured_at: <iso8601>}`；零数据库 schema 变更（migration 001-013 零触碰）|
| (E) docs/45 §6.2 O1 status append（post-605）| docs/45 §6.x line 550 后续 append 一行 `> ⚠ **docs/45 §6.2 O1 status append**（per 605 · 2026-08-29）：O1 §5.2.x 真实 SHA-locked 江苏样本刀首批样本已落地（`<sha12>` per source_registry/registry.csv +1 行；江苏统计局公开源；执行端自取预 vetted 公开源走完整 e2e 流水线 per docs/52 B 路 spec）；后续江苏样本刀待续接。docs 房规 NOT-IN-MANIFEST。`；既有 603 status blockquote 完整保留；不删不改 |
| (F) docs/49 + docs/50 + docs/51 + docs/52 + docs/53 status row append（如适用；SKIP 政策若 grep 命中 0 行 stale 字面）| per docs-only refresh 房规；SKIP 政策若命中为治理级决策标注非 stale `--confirm-*` 字面；docs 房规 NOT-IN-MANIFEST |
| (G) manifest bump K → 953+K | per docs 房规 + spike_helper 房规；K 仅在 docs/X 实际触碰 + 604 audit 入库随 605 commit（per docs 房规 审计文件不单独 commit 随下一刀入库）+ 605 receipt NEW + source_registry/registry.csv +1 行（NOT-IN-MANIFEST 守门；但 +1 行实际算入 K？per 583 §F enumeration 即权威） + 江苏样本 SHA-locked PDF/HTML 新增（spike_sample_or_truth role +1）；enumeration 即权威 per 583 §F；INVARIANT 953+K == 953+K == 953+K ✓ |
| (H) 605 receipt 写回执 | 含 (A)(B)(C)(D)(E)(F)(G)(H) 八段交付 + 双推 + cc_head backfill + manifest INVARIANT 验证 + 13 受保护文件零漂移（⚠ disclosure: source_registry/registry.csv +1 行；非修改既有 7 行而是 append；视为 0 漂移对既有行；bytes 总数变化是预期）+ 31+ 红线 100% 兑现 + ⚠ disclosures（如有）|

---

## §0.2 本刀不做（执行端零擅自做）

| 禁止 | 守门 |
|---|---|
| ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS | ✅ 605 仅 O1 §5.2.x 首批江苏样本 SHA-locked + e2e 跑通；O1 整体保持 WAITING_FILE（per docs/47 §3.1 + 484/486/488 校准：WAITING_FILE = intake 出口码 / mart 真 SHA 未入仓技术状态语义）；O3 整体保持 CLOSED 候选 per 588+590+597+598+599+600+601+602+603 九重声明 |
| ❌ 2020-2025 batch work | ✅ 零批量；本刀仅 1 个江苏样本 |
| ❌ 公网爬网（非政府/统计局/研究机构）| ✅ 零公网爬网；仅政府/统计局/研究机构公开源（per 2026-08-29 治理铁律）|
| ❌ OCR threshold lowering | ✅ 零阈值调整；gate_thresholds.json 3709 bytes 不变 |
| ❌ 1909-as-China | ✅ 零历史边界触碰 |
| ❌ --force | ✅ git push 走普通路径 |
| ❌ PAT request | ✅ 零 PAT |
| ❌ gate_thresholds.json edit | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 状态保持 CLOSED 候选（per 588 + 590 + 597 + 598 audit + 599 + 600 audit + 601 + 602 audit + 603 + 604 audit 十重声明）；605 不二次宣告 |
| ❌ 重新宣告 O1 整体收口 | ✅ O1 状态保持 WAITING_FILE；605 仅首批样本 SHA-locked 不构成 O1 整体收口；待全部 5 省样本 + 10 地市样本均 SHA-locked 后另刀审议 |
| ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注（per 601 + 599 + 591 docs/50 row 117 supersede）|
| ❌ 引入 --confirm-* 字面（实跑）| ✅ 2026-08-29 治理铁律；零 `--confirm-*` 字面 |
| ❌ 修改 001-013 migration 文件 | ✅ 红线 / 零生产 schema 变更 |
| ❌ 修改 01-core.sql | ✅ 红线 / 零核心 schema 变更（51589 bytes 不变）|
| ❌ 修改 4 fixture 锁值（synthetic.png + S0 PDF + _syn_pdf_585.py + extracts dir）| ✅ 红线 / 4 fixture 字节不变 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ SHA 零漂移（`f34b2e57…` 1007943 bytes）|
| ❌ 修改 source_registry/registry.csv 既有 7 行 | ✅ 红线 / 既有 7 行未改；605 仅 +1 行（新增江苏样本行）；既有 7 行 SHA 不变 |
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 红线 / 3709 bytes / mtime Aug 23 不变 |
| ❌ 修改 .venv-paddle / scripts/requirements-paddle.txt / requirements-dbt.txt | ✅ 红线 / 零 venv/env 污染（requirements-dbt.txt 349 bytes 不变）|
| ❌ 修改 scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py | ✅ 红线 / 零 intake 实跑触碰 |
| ❌ 修改 docs/45 / docs/46 / docs/44 / docs/49 / docs/50 / docs/51 / docs/52 / docs/53 既有 OPEN 行原文 | ✅ 605 仅 selective refresh（per docs-only refresh 房规）；既有 OPEN 行零删减 |
| ❌ 删除命中行原文 | ✅ 红线 / 既有 OPEN 行零删减 |
| ❌ 真实 paddleocr API 调用（system Python）| ✅ 仅 `.venv-paddle/bin/python` 隔离 venv 内允许（per 594 §0.2 红线延续）|
| ❌ 真实 PDF 上传（非 seed_archives/）| ✅ 零真实 PDF 上传到 ALLOWED_PREFIXES 上传目录；仅 `data/seed_archives/` 落 |
| ❌ 触真实 DB（生产 schema）| ✅ 零生产 schema 变更；source_document + lineage 写入走测试 mock writer 或新建 staging DB（per 587 §0.2）|
| ❌ 引入 cloud OCR / GPU runtime | ✅ per 594 §0.2 红线延续；零 `--enable-cloud-ocr=PROVIDER` 字面（实跑）|
| ❌ docker daemon systemctl 操作 | ✅ Colima daemon 已就绪（per 595 落地）；零 docker 操作 |
| ❌ 持久保留 paddle-ocr:v1 Docker image | ✅ per 596 §2.5 已清理（697MB 释放）|
| ❌ 启动 584 BLOCKED 实跑 paddle-ocr deps 到 system | ✅ 仅 `.venv-paddle` venv |

---

## §1. 605 tasking 详情

### 1.1 (A) 江苏样本源自取

**触发条件**:
- docs/52 B 路 spec 已 CLOSED per 599 audit PASS 落地（前置条件已满足）
- 2026-08-29 治理铁律：数据源唯一=政府/统计局/研究机构自取
- 执行端零爬网公网（非政府域）
- 预 vetted 公开源候选清单（任选其一或多个）:
  - `stats.jiangsu.gov.cn` 江苏省统计局门户
  - `tjj.jiangsu.gov.cn` 江苏省统计局（旧域名）
  - `stats.gov.cn` 国家统计局江苏分省页面
  - 江苏省统计年鉴（年度发布 PDF）

**落地**:
- 按 docs/52 B 路 spec 四步流水线：`discover → download → sha256 → archive`
- 真实 curl/wget 自取（**非公网爬虫**；仅政府/统计局/研究机构域）
- 记录 SHA-256 + source URL + captured_at (ISO 8601)
- **零 `--confirm-*` 字面**；**零用户动作**；**零用户裁定**

**grep 验证**:
- `ls data/seed_archives/jiangsu_*` 命中 ≥ 1 文件
- `cat source_registry/registry.csv | grep jiangsu` 命中 ≥ 1 行（新增行而非修改既有）

### 1.2 (B) 江苏样本 SHA-locked 落 `data/seed_archives/`

**触发条件**:
- (A) 已落地至少 1 个江苏样本文件

**落地**:
- sha256 验证（与下载时计算的 SHA 对比；零漂移）
- 落入 `data/seed_archives/jiangsu_<source>_<YYYYMMDD>.pdf` 或 `<source>_<YYYYMMDD>.html`
- 更新 `source_registry/registry.csv` +1 行（新增行而非修改既有 7 行）
- 新增行格式：`jiangsu_<source>_<YYYYMMDD>,<sha256>,<archive_path>,<source_url>,<captured_at>`
- ⚠ disclosure: source_registry/registry.csv bytes 总数变化是预期；既有 7 行 SHA 不变；不视为触碰红线

**grep 验证**:
- `cat source_registry/registry.csv | wc -l` = 7 (既有) + 1 (新增) = 8
- `cat source_registry/registry.csv | head -7 | shasum -a 256` SHA 不变（既有 7 行零修改）

### 1.3 (C) paddle-ocr e2e 流水线（江苏样本）

**触发条件**:
- (B) 江苏样本已 SHA-locked 落 `data/seed_archives/`

**落地**:
- `.venv-paddle/bin/python -c "from paddleocr import PaddleOCR; o = PaddleOCR(use_angle_cls=False, lang='ch'); r = o.ocr('/data/seed_archives/jiangsu_xxx.pdf', cls=False); print(r)"` 跑通
- 或 HTML 路径走 docs/53 §5 connector 模式
- **真实 paddle-ocr API 调用**（仅 `.venv-paddle` venv 内允许）
- 不修改 gate_thresholds.json
- 不修改 4 fixture 锁值

**grep 验证**:
- `.venv-paddle/bin/python -c "import paddleocr; print(paddleocr.__version__)"` = `3.7.0`
- `python3 -c "import paddle"` system site-packages = ModuleNotFoundError（隔离守门）
- paddle-ocr 跑通结果含 confidence + page_count + extracted_text

### 1.4 (D) source_document + lineage JSONB 写入（江苏样本）

**触发条件**:
- (C) paddle-ocr e2e 跑通

**落地**:
- `source_document` 行新增 `doc_kind='OCR_SCAN'` + `source_sha256=<sha>` + `archive_path='data/seed_archives/jiangsu_xxx.pdf'`
- `lineage` JSONB 写入：
  ```json
  {
    "engine": "paddle-ocr",
    "version": "3.7.0",
    "confidence": <float>,
    "page_count": <int>,
    "extracted_text": "<text>",
    "source_sha256": "<sha>",
    "captured_at": "<iso8601>",
    "source_url": "<url>",
    "doc_kind": "OCR_SCAN"
  }
  ```
- 零数据库 schema 变更（migration 001-013 零触碰）
- 写入走测试 mock writer 或新建 staging DB（per 587 §0.2）

**grep 验证**:
- 测试 mock writer 捕获 row dict 含 source_sha256 + lineage JSONB
- migration 001-013 零触碰（git diff --stat 32a3059..HEAD -- schema/migrations/ empty）

### 1.5 (E) docs/45 §6.2 O1 status append（post-605）

**触发条件**:
- (D) source_document + lineage JSONB 写入完成

**落地**:
- docs/45 §6.x line 550 后续 append 一行：
  ```
  > ⚠ **docs/45 §6.2 O1 status append**（per 605 · 2026-08-29）：O1 §5.2.x 真实 SHA-locked 江苏样本刀首批样本已落地（`<sha12>` per source_registry/registry.csv +1 行；江苏统计局公开源；执行端自取预 vetted 公开源走完整 e2e 流水线 per docs/52 B 路 spec）；后续江苏样本刀待续接。docs 房规 NOT-IN-MANIFEST。
  ```
- 既有 603 status blockquote 完整保留
- 不删不改

**grep 验证**:
- `grep "per 605 · 2026-08-29" docs/45-stage2-s210-lite-gate2-review-index-20260826.md` 命中 ≥ 1 occurrence

### 1.6 (F) docs/49 + docs/50 + docs/51 + docs/52 + docs/53 status row append（如适用）

**触发条件**:
- grep `docs/49-stage2-*.md docs/50-stage2-*.md docs/51-stage2-*.md docs/52-stage2-*.md docs/53-stage2-*.md` 命中 stale `--confirm-*` + `用户裁定` 字面

**落地**:
- append status 行（如适用；SKIP 政策若 grep 命中 0 行 stale runtime flag 字面）
- 命中为治理级决策标注（per 604 ⚠ disclosure 2）非 stale runtime flag → SKIP
- docs 房规 NOT-IN-MANIFEST

**grep 验证**:
- `grep "per 605（2026-08-29）" docs/49-stage2-*.md docs/50-stage2-*.md docs/51-stage2-*.md docs/52-stage2-*.md docs/53-stage2-*.md` 命中 ≥ 0 occurrence（SKIP 政策若 0 行）

### 1.7 (G) manifest bump K → 953+K

**落地**:
- `scripts/_knife605_manifest_bump.py` NEW spike_helper +1
- 604 audit 文件入库随 605 commit（per docs 房规 审计文件不单独 commit 随下一刀入库）documentation +1
- 605 receipt NEW documentation +1
- 江苏样本 SHA-locked PDF/HTML 新增（spike_sample_or_truth role +1；enumeration 即权威 per 583 §F）
- source_registry/registry.csv +1 行（NOT-IN-MANIFEST 守门；既有 7 行 SHA 不变；K 是否含此行？per 583 §F enumeration 即权威：source_registry_csv role +1 即含）
- K = 4 基础（K1+K2+K3+K4）+ 江苏样本 K5 = +5（如适用）
- **INVARIANT**: 953+K == 953+K == 953+K ✓

### 1.8 (H) 605 receipt 写回执

**落地**:
- (A)(B)(C)(D)(E)(F)(G)(H) 八段交付
- 双推 + cc_head backfill
- manifest INVARIANT 验证
- 13 受保护文件零漂移（⚠ disclosure: source_registry/registry.csv +1 行；既有 7 行 SHA 不变；bytes 总数变化是预期）
- 31+ 红线 100% 兑现
- ⚠ disclosures（如有）

---

## §2. 验收清单

| # | 验证项 | 预期 |
|---|---|---|
| 1 | 江苏样本源自取（执行端自取政府/统计局/研究机构公开源）| ✅ 1+ 个文件落 `data/seed_archives/jiangsu_*` |
| 2 | 江苏样本 SHA-locked 落 `data/seed_archives/` | ✅ sha256 验证 + 落入 + source_registry/registry.csv +1 行 |
| 3 | paddle-ocr e2e 流水线（江苏样本）| ✅ `.venv-paddle/bin/python` 跑通 |
| 4 | source_document + lineage JSONB 写入（江苏样本）| ✅ 测试 mock writer 捕获 row dict 含 source_sha256 + lineage JSONB |
| 5 | docs/45 §6.2 O1 status append | ✅ 1+ 处 `per 605 · 2026-08-29` 标识 |
| 6 | docs/49 + docs/50 + docs/51 + docs/52 + docs/53 status row append（如适用）| ✅ 1+ 处 / SKIP 政策（如适用）|
| 7 | manifest INVARIANT | ✅ 953+K == 953+K == 953+K |
| 8 | 13 受保护文件零漂移 | ✅ 全部 SHA + bytes 不变（⚠ disclosure: source_registry/registry.csv +1 行）|
| 9 | 31+ 红线 100% 兑现 | ✅ 全部 PASS |
| 10 | 双推 + cc_head backfill | ✅ 100% 收敛 |
| 11 | docs 房规 NOT-IN-MANIFEST | ✅ docs/X 命中行 supersede append 不增计数 |
| 12 | 既有 OPEN 行零删减 | ✅ 全部保留 |
| 13 | O1 整体仍 WAITING_FILE | ✅ 605 仅首批样本 SHA-locked 不构成 O1 整体收口 |
| 14 | O3 整体仍 CLOSED 候选 | ✅ 不二次宣告 |
| 15 | source_registry/registry.csv 既有 7 行 SHA 不变 | ✅ 既有 7 行零修改 |
| 16 | gate_thresholds.json 3709 bytes 不变 | ✅ 零阈值调整 |
| 17 | 4 fixture 锁值字节不变 | ✅ 全部保留 |
| 18 | S0 PDF SHA 零漂移 | ✅ `f34b2e57ae08` 1007943 bytes 不变 |
| 19 | migration 001-013 零触碰 | ✅ 零 schema 变更 |
| 20 | 01-core.sql 51589 bytes 不变 | ✅ 零核心 schema 变更 |

---

## §3. 与前置刀的衔接

| 刀 | 闭合项 | 状态 |
|---|---|---|
| 583 PASS | §5.2.2 validate_ocr_input() + §5.2.3 doc_kind migration | CLOSED |
| 584 BLOCKED-DEFERRED → CLOSED per 597 | §5.2.4 paddle-ocr deps + Dockerfile | CLOSED |
| 585 PASS | §5.2.5 端到端 pytest + §584 audit ⚠1 docs sync patch | CLOSED |
| 587 PASS | §5.2.6 真实 PDF e2e + O3 整体 CLOSED 候选 | CLOSED 候选 |
| 589/591/593/595/596/597/599/601/603 PASS | docs/45/49/50/51/52/53 六层 supersede 平行模式 + BLOCKER 5→0 闭环 + docs/45 chain head refresh 收口 | CLOSED |
| 600 PASS（per 600 audit）| docs/52 §13 B 路主路径收口 blockquote 已 append line 287 | CLOSED |
| 602 PASS（per 602 audit）| docs/52 §14 + docs/51 §11 + docs/53 §11 + docs/45 §7 四 docs-only refresh 落点 closure | CLOSED |
| 604 PASS（per 604 audit）| docs/45 文首刷新行 + §5.5 链头续接 + §6.x 状态行 append + 13 受保护文件零漂移 + 31+ 红线 100% 兑现 | CLOSED |
| **605（本刀）**| O1 §5.2.x 真实 SHA-locked 江苏样本刀首批样本落地（执行端自取江苏统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec）+ docs/45 §6.2 O1 status append + manifest bump + 605 receipt | O1 §5.2.x 首批样本 SHA-locked 落地 |

---

## §4. 关联文件清单

- 604 audit：`reviews/stage0-gate0-rework-2026-08-23/604-stage0-architect-s603-docs-45-chain-head-refresh-收口-tasking-20260829-audit-PASS-20260829.md`（84+ 验证项 + 2 ⚠ ACCEPTED；按 docs 房规随 605 commit 入库）
- 603 receipt：`reviews/stage0-gate0-rework-2026-08-23/603-stage0-cc-docs-45-chain-head-refresh-收口-tasking-20260829-receipt.md`（DELIVERED）
- 605 tasking 本文件：`reviews/stage0-gate0-rework-2026-08-23/605-stage0-architect-s604-o1-§5.2.x-real-sha-locked-江苏样本-tasking-20260829.md`
- docs/45：`docs/45-stage2-s210-lite-gate2-review-index-20260826.md`（line 550 后续 append O1 status）
- docs/49：`docs/49-stage2-pipeline-package-plan-20260825.md`（如适用）
- docs/50：`docs/50-stage2-gate2-review-packet-draft-20260826.md`（如适用）
- docs/51：`docs/51-stage2-o1-drop-checklist-20260826.md`（如适用）
- docs/52：`docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md`（B 路 spec 应用）
- docs/53：`docs/53-stage2-public-ingest-ops-handbook-20260826.md`（如适用）
- data/seed_archives/：`jiangsu_<source>_<YYYYMMDD>.pdf` 或 `<source>_<YYYYMMDD>.html`（NEW）
- source_registry/registry.csv：+1 行（既有 7 行 SHA 不变）
- queue：`reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md`（rev 20 → 21 → 22）

---

## §5. ⚠ disclosures（per 583 §F enumeration 即权威）

1. **source_registry/registry.csv +1 行**：既有 7 行 SHA 不变（per 583 §F 锁值）；新增江苏样本行；不视为触碰红线；enumeration 计入 source_registry_csv role +1；manifest INVARIANT 维持。
2. **江苏样本 SHA-locked 落 `data/seed_archives/`**：bytes 总数变化是预期；既有零样本不删；新增 1+ 个江苏样本；spike_sample_or_truth role +1。
3. **paddle-ocr e2e 流水线真实调用**：仅 `.venv-paddle/bin/python` 隔离 venv 内允许（per 594 §0.2 红线延续）；system Python 零 paddlepaddle；不视为触碰红线。

---

— End of `605-stage0-architect-s604-o1-§5.2.x-real-sha-locked-江苏样本-tasking-20260829.md` —
