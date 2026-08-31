# 585 — 任务书：O3 §5.2.5 e2e pytest 刀（syn-PDF 合成 fixture + paddle-ocr MOCK + docs sync patch 五处 916 → 917 deferred from 584）

- 编号：`585-stage2-o3-impl-e2e-pytest-tasking-20260829`
- 前置：`585-stage0-architect-s584-o3-impl-paddle-ocr-deps-audit-BLOCKED-20260829`（584 BLOCKED disposition ACCEPTED + Path C 决议）
- 规划蓝图：`docs/49-stage2-o3-ocr-prod-path-plan-20260826.md` §5.2.5（O3 e2e pytest）+ §5.2.6（真实 PDF `--confirm-o3=PATH` 用户保留动作）
- 引擎裁定（per `579`）：**paddle-ocr**（用户 2026-08-28；§5.2.1 已关闭）
- paddle-ocr deps 引入（584 BLOCKED-DEFERRED）= 本刀不依赖 deps 落地 = paddle-ocr MOCK only（与 584 解耦）
- 下发：CC 架构师终端 → 执行端（经 `00-EXEC-QUEUE.md`，PENDING → ACK → DELIVERED）
- 日期：2026-08-29
- 验证深度：**e2e pytest 链路全 mock 守门 + docs sync patch 五处 916 → 917 落点验证**（零真实 paddle-ocr API / 零真实 PDF / 零真实 DB 写入）

---

## §NOW

**背景（per docs/49 §5.2.5 e2e pytest）**：O3 实装链 §5.2.5 闭合 = 合成扫描 fixture（syn-PDF）实跑守门，验证完整链路 `syn-PDF → validate_ocr_input → doc_kind='OCR_SCAN' → paddle-ocr MOCK → source_document 写入 MOCK → assert 链路正确性`。§5.2.4 paddle-ocr deps 引入 584 BLOCKED-DEFERRED = 本刀不依赖 deps 落地；e2e 测试全部走 mock 路径（per docs/49 §5.2.5 设计意图 + memory `china-platform-583-o3-impl.md` 585 tasking 设计前提）。§5.2.6 真实 PDF `--confirm-o3=PATH` 用户保留动作走后续刀，本刀不触。

**架构师本刀关键决策**：
1. **paddle-ocr MOCK only**：本刀 = `paddleocr.PaddleOCR().ocr()` mock 返回 canned text（不触真实 paddle-ocr API / 不下载模型 / 不依赖 paddle-ocr deps 落地）。584 BLOCKED 不阻塞本刀（mock 路径完全解耦）。
2. **syn-PDF 合成 fixture**：本刀 = synthesized PDF bytes（最小合法 PDF header + EOF marker + controlled content marker）作为测试输入；**不写真实 PDF / 不写 --confirm-o3=PATH 真实文件处理**。
3. **source_document 写入 MOCK**：e2e 测试用 in-memory capture（dict / sqlite :memory: / unittest.mock）模拟 source_document 行写入 + lineage JSONB 断言；**不触真实数据库**。
4. **§584 audit ⚠1 docs sync patch 五处 916 → 917 deferred**（per `585-stage0-architect-s584-...-BLOCKED-20260829` 后续段）：docs/45 L93 + L487 + docs/53 L203 + L207 + docs/50 L228 五处 docs 数字 916 → 917 修正。**docs sync 不动 manifest / 不动 commit SHA**（SHA REFRESH 类）。
5. **5.2.4 BLOCKED-DEFERRED 文档化**：docs/49 §5.2.4 段首标「**BLOCKED-DEFERRED per 584（2026-08-29）· Path C**」（非 CLOSED；非 OPEN；env 就绪后 retry）。

---

### (A) syn-PDF 合成 fixture（**tests/fixtures/_syn_pdf_585.py** NEW · NOT-IN manifest → SKIP per 先例）

**fixture 用途**：585 e2e 测试最小合法 PDF 输入。

**实现要点**（执行端落地）：
- 最小合法 PDF 字节序列（PDF header `%PDF-1.4` + 1 个 page object + xref table + trailer + `%%EOF`）
- controlled content marker = 「`__SYN_PDF_585_E2E__`」字符串（嵌入 PDF body 便于 mock paddle-ocr 解析验证）
- file size 控制在 < 4 KB（避免 CI / sandbox 大文件处理开销）
- 路径：`tests/fixtures/_syn_pdf_585.py`（module 提供 `make_syn_pdf_bytes() -> bytes` helper）
- fixture 文件不入 manifest（per 574/577/579/581/583 fixture 先例）
- 既有 4 fixture 字节不动（e30ee811 / 9232efdb / 937255a5 / 9056001c 锁值保持）

**零触碰核对**：
- ❌ 不写真实 PDF fixture（`--confirm-o3=PATH` 真实 PDF 用户保留动作 = §5.2.6）
- ❌ 不修改既有 4 fixture 字节
- ❌ 不引入 PyPDF2 / pypdf / pdfplumber 等 PDF 解析库（syn-PDF 仅生成字节序列供 mock paddle-ocr 解析）

---

### (B) `tests/test_o3_e2e_585.py` — NEW e2e 测试文件（**NOT-IN manifest → ADD +1 · role=test_e2e**）

**测试覆盖（7+ 例）**：
1. **syn-PDF 字节构造验证**：`make_syn_pdf_bytes()` 返回合法 PDF 头部 + controlled content marker
2. **validate_ocr_input ACCEPT**：syn-PDF bytes 写入临时 ALLOWED_PREFIX 路径 → validate_ocr_input → ACCEPT
3. **validate_ocr_input REJECT_OUTSIDE_ALLOWLIST**：syn-PDF bytes 写入非 allowlist 路径 → REJECT_OUTSIDE_ALLOWLIST
4. **doc_kind 守门**：syn-PDF bytes 经 validate_ocr_input ACCEPT 后 → e2e pipeline 设置 doc_kind='OCR_SCAN' → assert 链路
5. **paddle-ocr MOCK 调用**：mock `paddleocr.PaddleOCR().ocr()` 返回 canned text → e2e pipeline 调用 → assert mocked method called with correct args
6. **source_document 写入 MOCK**：e2e pipeline 触发 source_document 写入 → mock writer 捕获 row dict + lineage JSONB → assert schema 合规（uploader_id / file_hash_sha256 / doc_kind / created_at / lineage 等字段）
7. **lineage JSONB 结构断言**：mock 捕获的 lineage JSONB 含 `engine='paddle-ocr'` + `confidence` + `page_count` + `extracted_text` 字段（per docs/49 §3.2 Step 7 spec）
8. **零真实 paddle-ocr API 调用断言**：mock 验证 `paddleocr.PaddleOCR` 真实实例未被创建（`paddleocr.PaddleOCR.__init__` mock assert_called）
9. **§584 audit ⚠1 docs sync 落点验证**：执行端实测 docs/45 + docs/53 + docs/50 五处 916 → 917 修正落地（grep 计数）

**fixture 规范**：
- 不依赖 paddle-ocr deps 落地（mock only）
- 不写真实 OCR 模型 / 不写真实 PDF fixture / 不触真实数据库
- 不修改既有任何 fixture（4 fixture 锁值不变 + 不引入新 fixture file（除 `_syn_pdf_585.py` helper module））
- 使用 `tmp_path` + monkeypatch + unittest.mock 标准 pytest fixture

**imports**：
- `from scripts.intake_real_sha_if_present import validate_ocr_input, is_control_flow_fixture`
- `from unittest.mock import MagicMock, patch`
- `import pytest` + `pytest.MonkeyPatch`
- **零 paddleocr / paddlepaddle import**（mock only；584 deps 不落地不阻塞）

---

### (C) docs 同步（**docs/45 + docs/49 + docs/50 + docs/53 四件同步；含 §584 audit ⚠1 docs sync patch 五处**）

- **docs/49 §5.2.4 状态翻转**：段首标「**BLOCKED-DEFERRED per 584（2026-08-29）· Path C**」（非 CLOSED；env 就绪后 retry；584 tasking 文件保留）
- **docs/49 §5.2.5 状态翻转**：段首标「**CLOSED per 585（2026-08-29）**」（e2e pytest 守门落地；paddle-ocr MOCK）
- **docs/49 §5.2.6 状态保持**：仍 OPEN（真实 PDF `--confirm-o3=PATH` 用户保留动作 = 586+ tasking）
- **docs/53 §5 新增第 45 项**（per 583 末项第 44 项后）：
  - blockquote 内容 = 585 实装登记（syn-PDF 合成 fixture + e2e pytest + paddle-ocr MOCK + docs sync patch 五处 916 → 917 deferred from 584）
  - 闭合范围明示 = 5.2.5（e2e pytest 守门）；保持 OPEN = 5.2.4（BLOCKED-DEFERRED per env）+ 5.2.6 + O3 收口
- **docs/45 五处**（落点族 per `580` ⚠2 裁定 + 含 §584 audit ⚠1 docs sync patch）：
  - 文首 +1 刷新行（架构师治理模型第七刀 per 585）
  - §1 +1 段（O3 §5.2.5 e2e pytest 刀登记 + paddle-ocr MOCK 决策披露）
  - §5.5 尾 O3 bullet 行尾注 append（per `585`；5.2.5 CLOSED；5.2.4 BLOCKED-DEFERRED + 5.2.6 OPEN）
  - §7 链头 `921 == 921 == 921`（per bump 实际值）+ knife 585 demote
  - §7 链头 ⚠1 docs sync patch：**L93 demote 段 `916 == 916 == 916` → `917 == 917 == 917`** + `manifest 911 → 916（+5 per bump 实际值）` → `917（+6 per enumeration 收口）` + **L487 pack invariant table `916 == 916 == 916` → `917 == 917 == 917`**（per §584 audit ⚠1 ACCEPTED with disclosure，docs sync patch 五处 916 → 917 deferred from 584 → 入本刀闭合）
  - §3 零涉（无裁定变更；O3 整体仍 OPEN）
- **docs/50**：
  - §4.4 +1 第 45 项行
  - intro 链尾 `→ 583 → 584` 续接 `→ 585`
  - §5.1 O3 状态行 append 处置标注（O3 5.2.5 CLOSED per 585；5.2.4 BLOCKED-DEFERRED per 584；5.2.6 OPEN；行内 append 不删行）
  - §4.4 第 44 项行 ⚠1 docs sync patch：**L228 `§7 链头 911 → 916` → `911 → 917`**
  - §4.4 第 45 项行新增：`§7 链头 917 → 921` + knife 585 demote + paddle-ocr MOCK 决策

**「O3 仍 OPEN」计数非减**（5.2.4 BLOCKED-DEFERRED + 5.2.6 仍 OPEN + 真实 PDF 用户保留动作 不变 = O3 整体仍 OPEN；5.2.5 = 585 tasking CLOSED）

---

### (D) manifest bump（**+4** 含 docs sync patch SHA REFRESH）

`scripts/_knife585_manifest_bump.py`：NEW **+4**（枚举即权威，每项实测 NOT-IN）：
- bump 脚本本身（`spike_helper`）
- `585` 回执（`documentation`）
- `584` 审计文件（`documentation`，只读随刀入库；584 BLOCKED disposition ACCEPTED）
- `tests/test_o3_e2e_585.py`（`test_e2e`，NEW；与 `schema_negative_test` 并列新角色）
- `schema/migrations/015_*`（**0 件，本刀零 schema 改动**；migration 014 doc_kind 583 落够用；不增 schema_migration_ddl / schema_migration_log 角色）
→ **917 → 921**；断言 `sum(role_count) == artifact_count == len(artifacts) == 921`

**REFRESH**：
- `scripts/intake_real_sha_if_present.py`（SHA 不变 = 未改）
- `scripts/auto_ingest_public_source.py`（SHA 不变 = 未改）
- `docs/45 + docs/49 + docs/50 + docs/53`（**全部 SHA REFRESH 不增计数**；含 §584 audit ⚠1 docs sync patch 五处 916 → 917 落点 + 5.2.5 / 5.2.4 状态翻转）
- `00-EXEC-QUEUE.md`（SHA REFRESH 不增计数）

**SKIP**：
- `docs/50` 房规未入 manifest（per 574/577/579/581/583/584 先例）；**docs sync patch 落地但不入 manifest**
- `tests/fixtures/_syn_pdf_585.py` fixture 不入 manifest（per fixture 先例）
- `schema/01-core.sql` 不动（base schema 锁）
- `00-CC-CURRENT.md` 不动（Cursor 冻结）
- `registry.csv` / `gate_thresholds.json` 不动（红线）

**任务书按先例不计数**（574/577/579/581/583/584 任务书均不入 manifest；585 任务书同）

---

### (E) 零网络核验（命令 + 输出原样粘贴进回执）

```bash
python3 -m pytest tests/ -q                                          # 全量：预期 0 failed（≈580+ passed / 8 skipped / 1 deselected / +585 新增 7+ 例测试；~5 分钟含 e2e mock 链路开销）
python3 -m pytest tests/test_o3_e2e_585.py -q                        # 新文件单独实跑（7+ 例 PASS）
python3 -m pytest tests/test_validate_ocr_input_583.py -q             # 583 测试文件防回归（14 例 PASS）
python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -q          # 25 passed（零改动防回归）
python3 frontend/smoke-check.py                                      # PASS / exit 0
shasum -a 256 frontend/lib/public_extract_{nbs,nbs_live_candidate,sz,hubei}.json | cut -c1-8
                                                                    # e30ee811 9232efdb 937255a5 9056001c
grep -c "O3 仍 OPEN" docs/45-*.md                                   # ≥11（非减；5.2.4 BLOCKED-DEFERRED + 5.2.6 仍 OPEN）
grep -c "第 45 项（此条）" docs/53-*.md                              # 1
grep -c "917 == 917 == 917" docs/45-*.md                            # ≥3（per §584 audit ⚠1 patch 闭合；§7 链头 + L93 demote + L487 pack table）
grep -c "916 == 916 == 916" docs/45-*.md                            # 0（stale 916 已清 ✅；§584 audit ⚠1 闭合）
grep -c "917 == 917 == 917" docs/53-*.md                            # ≥2（per §584 audit ⚠1 patch 闭合；第 44 项 blockquote L203 + L207）
grep -c "916 == 916 == 916" docs/53-*.md                            # 0
grep -c "917" docs/50-*.md | grep "第 44 项"                         # ≥1（per §584 audit ⚠1 patch 闭合；第 44 项行 §7 链头 `911 → 917`）
grep -c "BLOCKED-DEFERRED per 584" docs/49-*.md                     # 1（§5.2.4 状态翻转）
grep -c "CLOSED per 585" docs/49-*.md                               # ≥1（§5.2.5 状态翻转）
python3 -c "import json;m=json.load(open('evidence_pack/manifest.json'));print(len(m['artifacts']),m['artifact_count'],sum(m['role_count'].values()))"
                                                                    # 921 921 921
python3 -c "from unittest.mock import MagicMock; m = MagicMock(); print('paddleocr mock OK:', m.__class__.__name__)"
                                                                    # paddleocr mock OK: MagicMock
python3 -c "from tests.fixtures._syn_pdf_585 import make_syn_pdf_bytes; b = make_syn_pdf_bytes(); assert b.startswith(b'%PDF-'); assert b.endswith(b'%%EOF'); print('syn-PDF OK:', len(b), 'bytes')"
                                                                    # syn-PDF OK: ~2000 bytes
```

**重要**：本刀全量 pytest 不需要 paddlepaddle / paddleocr / Docker（mock only + 不依赖 deps 落地）；584 BLOCKED env 约束不传染至 585。

---

### (F) 回执 + 交付 commit

- 回执：`reviews/stage0-gate0-rework-2026-08-23/585-stage0-cc-o3-impl-e2e-pytest-tasking-20260829-receipt.md`（含 `-cc-`；单槽单回执，仅 `585`）
- 交付 commit 含：
  - `tests/test_o3_e2e_585.py`（NEW）
  - `tests/fixtures/_syn_pdf_585.py`（NEW；fixture helper module）
  - `scripts/_knife585_manifest_bump.py`（NEW）
  - docs/49 + docs/50 + docs/53 + docs/45（MODIFIED，含 §584 audit ⚠1 docs sync patch 五处 916 → 917 + 5.2.4 BLOCKED-DEFERRED 翻转 + 5.2.5 CLOSED 翻转）
  - `584` 审计文件（NEW，只读随刀入库；584 BLOCKED disposition ACCEPTED）
  - `585` 任务书（NEW，只读随刀入库）
  - `585` 回执（NEW）
  - `00-EXEC-QUEUE.md`（ACK 填行 + status→PENDING（585）+ note 回执号）
- cc_head backfill 单独 commit（勿 amend）；`git push origin HEAD` → `git push github HEAD` 严格顺序

---

## 红线（零豁免）

- ❌ **paddle-ocr MOCK only** — 不触真实 `paddleocr.PaddleOCR().ocr()` API；不下载 paddleocr 模型；不引入 paddle-ocr deps（584 BLOCKED；mock 路径与 deps 落地解耦）
- ❌ **syn-PDF 合成 fixture only** — 不写真实 PDF；不引入 PyPDF2 / pypdf / pdfplumber 等 PDF 解析库；不触 `--confirm-o3=PATH` 真实 PDF 用户保留动作（§5.2.6）
- ❌ **source_document 写入 MOCK only** — 不触真实数据库；mock writer 捕获 row dict 即可；不引入 SQLAlchemy / psycopg 等 DB 驱动
- ❌ 不引入 cloud OCR（百度云 / 腾讯云 / 阿里云 OCR API / HTTP OCR 服务 一律禁止）
- ❌ 不引入 GPU runtime（CUDA / cuDNN / nvidia-docker 等）
- ❌ 不修改 migration 001-014 任何文件（migration 014 doc_kind 583 落够用；本刀零 schema 改动）
- ❌ 不修改 `schema/01-core.sql`（base schema 锁）
- ❌ 不修改 `scripts/auto_ingest_public_source.py` / `scripts/intake_real_sha_if_present.py` 既有函数（**仅 mock + e2e 测试新增**）
- ❌ 不修改 4 fixture 字节 / data/seeds/ / spikes/ 任何文件
- ❌ 不爬网 / 不 cloud OCR / 不 HTTP 出站（仅 grep / pytest / mock）
- ❌ 不写 dbt / mart / 前端任何文件
- ❌ 不宣布 Gate 0/1/2 PASS；不宣布 O3 收口；O3 整体仍 OPEN（5.2.4 BLOCKED-DEFERRED + 5.2.6 仍 OPEN + 真实 PDF 用户保留动作不变）
- ❌ 无 --force / PAT / 公网 redeploy；既有 OPEN 行零删减（docs/50 §5.1 O3 行 append 处置标注不删行）
- ✅ 全量 0 failed 为本刀完成定义；manifest 917 → 921 不变量（+4 枚举即权威；含 §584 audit ⚠1 docs sync patch 五处 SHA REFRESH）；回执位于 `reviews/stage0-gate0-rework-2026-08-23/`

---

## 完成后

双推完成即停，回报 cc_head；架构师出 `586` 号位审计；随后签发 **`586+` = §5.2.6 真实 PDF `--confirm-o3=PATH` 用户保留动作刀**（O3 收口必经用户操作；per 579 + 581 + 583 + 584 + 585 任务书红线）。**§584 audit ⚠1 docs sync patch 落地验证**：执行端在 receipt §零网络核验 实测 docs/45 / docs/53 / docs/50 五处 916 → 917 修正（patch deferred from 584 → 入 585 闭合）；patch 不动 manifest / 不动 commit SHA；docs sync 与 manifest invariant 真实 917（per 583 bump）/ 921（per 585 bump）一致。**584 BLOCKED-DEFERRED retry 触发条件**：用户裁定 + env 就绪（Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定）。

---

## 附：§584 audit ⚠1 docs sync patch 详单（执行端 patch 范围；deferred from 584 → closure in 585）

| # | 文件 | 行号 | 旧值 | 新值 |
|---|---|---|---|---|
| 1 | `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | L93 (583 demote 段) | `manifest 911 → 916（+5 per bump 实际值：bump + 回执 + 582 审计 + 2 个 migration 文件 + 测试文件 ADD）` | `manifest 911 → 917（+6 per enumeration 收口：bump + 回执 + 582 审计 + 2 个 migration 文件 + 测试文件 ADD；per §584 audit ⚠2 INCONSISTENT-1 enumeration wins）` |
| 2 | `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | L93 (583 demote 段) | `docs/45 §7 链头 916 == 916 == 916` | `docs/45 §7 链头 917 == 917 == 917` |
| 3 | `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | L487 (pack invariant table) | `bump + commit 后 916 == 916 == 916` | `bump + commit 后 917 == 917 == 917` |
| 4 | `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | L203 (第 44 项 blockquote (D) bullet) | `§7 链头 `911 → 916` + knife 583 demote` | `§7 链头 `911 → 917` + knife 583 demote` |
| 5 | `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | L207 (第 44 项 blockquote 闭环行) | `§7 链头 `916 == 916 == 916` + knife 583 demote` | `§7 链头 `917 == 917 == 917` + knife 583 demote` |
| 6 | `docs/50-stage2-gate2-review-packet-draft-20260826.md` | L228 (§4.4 第 44 项行 (D) bullet) | `§7 链头 `911 → 916` + knife 583 demote` | `§7 链头 `911 → 917` + knife 583 demote` |

**patch 不动 manifest / 不动 commit SHA**；docs/45 + docs/49 + docs/53 SHA REFRESH 计入 manifest（per 574/577/579/581/583 先例）；docs/50 房规不入 manifest → 显式 SKIP 不增计数。**§584 audit ⚠1 docs sync gap 闭合** = docs claim 与 manifest invariant 真实 917（per 583 bump）/ 921（per 585 bump）一致。

---

## 附 2：584 BLOCKED-DEFERRED 重 ACK 触发条件（用户裁定参考）

584 paddle-ocr deps 引入任务在以下全部就绪时可重 ACK：
1. **Python 3.12 可用**（paddlepaddle 官方 wheel 截止；3.13+ 暂无 wheel 公开记录）
2. **Docker daemon 就绪**（Docker Desktop 安装 / colima / lima / 远端 Docker host 任一）
3. **项目主 deps manifest 决策已定**（创 NEW `requirements.txt`？改 `requirements-dbt.txt` 为主？设 NEW `pyproject.toml`？）
4. **用户裁定 paddle-ocr deps 引入时机**（可结合 §5.2.6 真实 PDF 用户保留动作一并处理）

任一条件不满足 = 584 仍 BLOCKED-DEFERRED。
