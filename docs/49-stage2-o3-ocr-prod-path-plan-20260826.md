# 49 — Stage 2 / O3 OCR 生产路径规划

> 起草：CC · 2026-08-26 · queue_rev 128
> 前置：`307` docs/45 PASS；`docs/45` §3 O3 OPEN；`docs/34` Stage 1 OPEN；`docs/48` 真 SHA intake 手册
> 用户裁定：**D**（缩刀）；自主推进；**不爬网**；**O1 仍 OPEN**
> 任务书：`308-stage2-o3-ocr-prod-path-plan-tasking-20260826`
> 性质：**只规划不实装**；本文件=规划蓝图，不引入 OCR 引擎选型、不改 schema、不改 dbt、不改业务 UI

---

## §0. 本刀范围（per `308` §SCHEMA "本刀做/本刀不做"）

| 类别 | 项 |
|---|---|
| **本刀做** | 写本文件 `docs/49`：O3 OCR 生产路径规划（输入=用户/admin 已上传 PDF 扫描件；流水线步骤；与 `is_demo`/SHA lineage 衔接；验收清单；**明确禁止** HTTP 爬源 / 登录绕过）|
| **本刀不做** | 实装 OCR 引擎；伪造样本；宣布 Gate/O1/O3 收口；改业务 UI；引入新依赖；改 schema；改 dbt 模型 |
| **本刀禁止** | ❌ Gate 1/2 PASS；❌ HTTP 爬源（gov.cn / 任何第三方）；❌ 登录绕过（cookie/账号/headless browser）；❌ 伪造样本；❌ 擅自收口 O3 |

**红线自检**（per `308` §红线 + docs/34 §1 + docs/42 §8 + docs/06 §6.6）：
- 本刀是**规划文档**（markdown），不包含任何可执行 OCR 代码或网络调用。
- 本刀不修改 `scripts/intake_real_sha_if_present.py`、`scripts/compute_file_sha.py`、`scripts/replace_demo_with_real.py` 或 `docs/48` 既有脚本/手册。
- 本刀不修改 Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-48）。
- 本刀不修改 `00-CC-CURRENT.md`（Cursor 拥有）。
- 本刀不修改 `gate_thresholds.json`。

---

## §1. 目标

把 **O3「OCR 生产路径」OPEN** 从「文字声明」推进到「可执行流水线设计」：
- 明确**输入边界**（仅接受用户/admin 已上传的 PDF 扫描件；**禁止**任何 HTTP 爬源、登录绕过）
- 明确**流水线步骤**（upload → checksum → OCR → text extraction → SHA lineage 写入 → S2.1-lite/S2.2/S2.4 ingestion）
- 明确**与 `is_demo`/SHA lineage 的衔接**（复用 `docs/48` 真 SHA intake 契约，不创造新机制）
- 给出 **Gate 2 评审验收清单**（不擅自宣布 PASS；仅列验证项）

> ⚠ **本刀不实装 OCR 引擎**；仅规划流水线步骤、依赖、边界、验收项。OCR 引擎选型（paddle-ocr / tesseract / cloud OCR）留待用户裁定。

---

## §2. 输入边界（per `308` §SCHEMA 显式禁止）

### 2.1 合法输入

| 输入类型 | 路径 | 触发方式 |
|---|---|---|
| **管理员 upload 端点**（`/api/upload`，已部署 + XSS 消毒 + Turnstile；per `puer-hub-security-hardening.md` 模板可复用）| 文件系统落盘 → `ALLOWED_UPLOAD_DIR` 路径 | admin 用户手动上传；multipart/form-data；单文件 ≤ 50 MiB；MIME 必须为 `application/pdf` 或扫描件 `image/tiff` / `image/jpeg` / `image/png` |
| **开发者控制流 fixture**（**仅控制流，非 O3 样本**）| `data/seed_archives/` | 仅在 `intake_real_sha_if_present.py` 4 退出状态测试用；不计入 O3 真实流水线 |

### 2.2 非法输入（**显式拒绝**）

| 禁止行为 | 守门位置 |
|---|---|
| ❌ **HTTP 爬源**（gov.cn / 任何第三方 PDF 来源）| 网络层：OCR 流水线脚本**不发起任何出站 HTTP 请求**；`scripts/compute_file_sha.py` `ALLOWED_PREFIXES` 不含 `http(s)://` |
| ❌ **登录绕过**（cookie / 账号 / headless browser / Selenium / Playwright）| OCR 流水线脚本**不包含任何登录逻辑**；不接受任何 `--auth-*` / `--cookie-*` flag |
| ❌ **未授权 API 调用**（第三方 OCR cloud API / Dify 集成 / OpenAI vision）| OCR 流水线脚本**默认离线**；任何 cloud OCR 调用须用户显式 `--enable-cloud-ocr=PROVIDER` flag（per `284` O1 显式 flag 模式）|
| ❌ **伪造样本**（mock PDF 冒充真实政府文件）| 同 `docs/48` §4.1 控制流 fixture 判定契约；首 32 字节含 `NOT a forged` / `placeholder bytes` → 控制流 fixture，不算 O3 真实样本 |
| ❌ **绕过 allowlist 路径**（symlink 攻击 / path traversal）| `Path.resolve()` 后必须落在 `ALLOWED_UPLOAD_DIR` + `data/seed_archives/` 2 个前缀 |

### 2.3 输入守门调用

```python
# OCR 流水线脚本必须复用 docs/48 §2 allowlist 守门
from scripts.intake_real_sha_if_present import (
    ALLOWED_UPLOAD_DIR,         # /tmp/cegr_uploads, /private/tmp/cegr_uploads
    DATA_SEED_ARCHIVES_DIR,     # data/seed_archives/
    is_control_flow_fixture,    # docs/48 §4.1 判定
    compute_file_sha256,        # scripts/compute_file_sha.py
)

def validate_ocr_input(path: Path) -> Literal["ACCEPT", "REJECT_OUTSIDE_ALLOWLIST", "REJECT_CONTROL_FLOW_FIXTURE", "REJECT_MIME"]:
    resolved = path.resolve()
    if not (resolved.is_relative_to(ALLOWED_UPLOAD_DIR) or resolved.is_relative_to(DATA_SEED_ARCHIVES_DIR)):
        return "REJECT_OUTSIDE_ALLOWLIST"
    if is_control_flow_fixture(resolved):  # docs/48 §4.1
        return "REJECT_CONTROL_FLOW_FIXTURE"
    mime = magic.from_file(resolved, mime=True)
    if mime not in ("application/pdf", "image/tiff", "image/jpeg", "image/png"):
        return "REJECT_MIME"
    return "ACCEPT"
```

> 注：本刀不实装 `validate_ocr_input()`；仅规划 API 形态。实装留待后续 knife（tasking 31X+）。

---

## §3. 流水线步骤（7 步；每步可独立验证）

### 3.1 总览

```
┌─────────────────────────────────────────────────────────────────────┐
│  O3 OCR 生产路径流水线（7 步；纯本地；无 HTTP 爬源）                  │
└─────────────────────────────────────────────────────────────────────┘

[1] upload          [2] validate          [3] sha256
  admin upload    →   allowlist + MIME  →   compute_file_sha
  端点 (multipart)   控制流 fixture 拒     (per docs/48 §3)

                    [4] ocr             [5] text extract
                  →   OCR 引擎（paddle-ocr →  段落/表格/列表
                      / tesseract / cloud）  重建（结构化 JSON）

                                          [6] lineage write
                                        →   source_document 表
                        (sha256, is_demo,  (per docs/47 §3.1 lineage)
                         demo_reason,
                         doc_kind=OCR_SCAN)

                                                      [7] ingest
                                                    →   S2.1-lite person/tenure
                                                        S2.2 policy_observation
                                                        S2.4 fiscal_observation
                                                        (下游表根据 doc_kind 分发)
```

### 3.2 步骤详解

#### 步骤 1 — upload（admin upload 端点）

| 项 | 详情 |
|---|---|
| **触发** | admin 用户手动上传（per `puer-hub-security-hardening.md` 模板：`/api/upload` multipart/form-data；XSS 消毒；Turnstile；单文件 ≤ 50 MiB；rate limit）|
| **输出** | 文件落盘到 `ALLOWED_UPLOAD_DIR`；返回 `{path, size_bytes, mime, sha256_placeholder}` |
| **守门** | MIME 必须为 `application/pdf` / `image/tiff` / `image/jpeg` / `image/png`；否则 415 Unsupported Media Type |
| **审计** | 写 `upload_audit` 表：`{user_id, path, size_bytes, mime, client_ip, uploaded_at}` |

#### 步骤 2 — validate（输入边界守门）

| 项 | 详情 |
|---|---|
| **触发** | 自动（在 OCR 流水线脚本入口）|
| **输出** | `ACCEPT` / `REJECT_OUTSIDE_ALLOWLIST` / `REJECT_CONTROL_FLOW_FIXTURE` / `REJECT_MIME` |
| **守门** | `validate_ocr_input(path)`（per §2.3 API 形态）|
| **拒绝行为** | 任一 REJECT → 写 `reject_audit` 表 + 返回 rc=2（与 `intake_real_sha_if_present.py` 一致）|

#### 步骤 3 — sha256（文件指纹）

| 项 | 详情 |
|---|---|
| **触发** | 步骤 2 ACCEPT 后 |
| **输出** | `sha256` (hex, 64 chars)；写 `source_document` 表 `source_file_sha256` 字段 |
| **守门** | 复用 `scripts/compute_file_sha.py` `compute_file_sha256(path)` |
| **禁词** | SHA 不可为 `'0'*64`（占位）；不可为 fixture SHA 名单中的任何值（per `docs/48` §4.1）|

#### 步骤 4 — ocr（OCR 引擎调用）

| 项 | 详情 |
|---|---|
| **触发** | 步骤 3 SHA 写入后 |
| **输出** | 原始 OCR 输出（plain text + 段落结构 + 表格 + 列表）|
| **OCR 引擎选项** | (i) paddle-ocr（开源，本地，CPU/GPU）；(ii) tesseract（开源，本地，CPU）；(iii) cloud OCR（百度/腾讯/Azure；**默认禁止**；须 `--enable-cloud-ocr=PROVIDER` 显式 flag + 用户裁定）|
| **推荐** | paddle-ocr（中文识别精度高；本地离线；无网络依赖）；最终选型由用户裁定 |
| **守门** | OCR 调用结果必须写入临时文件（`/tmp/cegr_ocr/<sha256>.txt`），不直接入 DB；下一步才解析 |
| **禁词守门** | OCR 脚本不发起任何 HTTP 请求（除 `--enable-cloud-ocr=PROVIDER` 显式 flag 之外）|

#### 步骤 5 — text extract（结构化文本提取）

| 项 | 详情 |
|---|---|
| **触发** | 步骤 4 OCR 输出后 |
| **输出** | 结构化 JSON：`{paragraphs: [...], tables: [[...]], lists: [[...]], page_count, language: "zh-CN"}` |
| **解析器** | 行级正则 + 段落重建（启发式）；表格用 `pdfplumber` / `camelot-py`（如 PDF 含可选中文本层）|
| **守门** | 段落长度 ≥ 10 字符才算 valid；否则归入 `low_quality_extract` 标记（不阻塞，但记入 `ocr_quality_audit`）|

#### 步骤 6 — lineage write（写入 `source_document` + `lineage`）

| 项 | 详情 |
|---|---|
| **触发** | 步骤 5 结构化提取后 |
| **输出** | `source_document` 表行：`{source_file_sha256, doc_kind='OCR_SCAN', language='zh-CN', page_count, upload_user_id, uploaded_at, lineage: {is_demo: false, source_file_sha256: ..., demo_reason: null}}` |
| **守门** | `is_demo=false`（**关键**：从 demo 翻转为真；这是 O3 收口的标志事件）|
| **守门** | `source_file_sha256` ≠ `'0'*64`（per `docs/47` §3.1 ⚠️ 占位恒定反例）|
| **守门** | `demo_reason` 必须为 NULL（真样本无 demo reason）|
| **依赖** | `source_document` 表已存在（per `schema/01-core.sql`）；如不存在由 schema migration 0XX 落地（**本刀不引入 migration**）|

#### 步骤 7 — ingest（下游分发到 S2.1-lite / S2.2 / S2.4）

| 项 | 详情 |
|---|---|
| **触发** | 步骤 6 lineage 写入后 |
| **输出** | 分发到下游表：S2.1-lite `person` / `tenure`（履历相关） / S2.2 `policy_observation`（政策文件）/ S2.4 `fiscal_observation`（财政文件）|
| **doc_kind 分发规则** | (i) 政府工作报告 → S2.2 policy_observation；(ii) 财政预决算 → S2.4 fiscal_observation；(iii) 干部任免通知 → S2.1-lite person/tenure；(iv) 其他 → 暂存 `source_document` 不入业务表 |
| **守门** | 每个下游表写入必须通过 §2 allowlist + `is_demo=false` lineage 守门 |
| **依赖** | 下游表 schema 必须已存在（S2.1-lite / S2.2 / S2.4 落地刀）|

---

## §4. 与 `is_demo`/SHA lineage 衔接（per docs/47 §3.1 + docs/48 §3-§4）

### 4.1 lineage JSONB 契约

| 字段 | 真 O3 样本值 | demo 占位值（O1 WAITING_FILE 期间）|
|---|---|---|
| `is_demo` | `false`（**字符串** `"false"` per S1.18 sentinel）| `true` |
| `source_file_sha256` | 真实 SHA（hex, 64 chars；步骤 3 计算）| `'0'*64`（per `docs/47` §3.1 ⚠️）|
| `demo_reason` | `NULL` | 非空字符串（解释为何 SHA 占位）|
| `source_file_url` | `"(OCR_SCAN_FROM_UPLOAD:{user_id}:{uploaded_at})"` | `"(DEMO_SEED_NO_FILE)"` |

### 4.2 状态机（O3 收口前 → 后）

```
              [O3 OPEN]
                  │
                  ▼
   is_demo=true + source_file_sha256='0'*64
   (S2.7-b-full-lite / S2.7-b-full demo-join 期间)
                  │
                  │  (步骤 6 写入：is_demo=false + 真实 SHA)
                  ▼
   is_demo=false + source_file_sha256=<real sha>
   (O3 收口；任一 admin 上传 1 个真实 PDF 后)
```

### 4.3 与 docs/48 §3 退出码衔接

| `intake_real_sha_if_present.py` 退出码 | O3 流水线对应 |
|---|---|
| rc=0 `WAITING_FILE`（白名单内无合法 O1 样本）| O3 同样 → **O3 OPEN 继续** |
| rc=2 `CANDIDATE_FOUND`（候选 + SHA 成功 + lineage 已写）| O3 同样 → **O3 CANDIDATE_FOUND**（候选待用户裁定「此即 O3」）|
| rc=3 `CONTRACT_VIOLATION`（候选但 SHA 全 0 / is_demo 未清除）| O3 同样 → **O3 CONTRACT_VIOLATION**（必须清理 demo 占位）|
| rc=4 内部错误 | O3 同样 → 内部错误 |

> **关键不变量**：O3 流水线**复用** `intake_real_sha_if_present.py` 的 4 退出码语义，不创造新退出码。

---

## §5. 验收清单（Gate 2 评审必带；不擅自宣布 PASS）

### 5.1 必过（per docs/34 §10.4 Gate 2 W8 评审）

| # | 验收项 | 当前状态 |
|---|---|---|
| 5.1.1 | O3 流水线 7 步设计文档（本文件 `docs/49`）| ✅ 本刀落地 |
| 5.1.2 | 输入边界明确（仅用户/admin upload；无 HTTP 爬源；无登录绕过）| ✅ §2 |
| 5.1.3 | 流水线步骤每步可独立验证（步骤 1-7）| ✅ §3 |
| 5.1.4 | `is_demo`/SHA lineage 衔接（复用 `docs/48` 契约；不创造新机制）| ✅ §4 |
| 5.1.5 | 显式禁词守门（HTTP / 登录绕过 / 伪造 / 未授权 cloud OCR）| ✅ §2.2 + §3.2 步骤 4 |
| 5.1.6 | 4 退出码契约与 docs/48 一致 | ✅ §4.3 |
| 5.1.7 | **不实装 OCR 引擎**（仅规划）| ✅ §0 范围 |
| 5.1.8 | **不宣布 Gate 2 / O3 PASS** | ✅ §0 + §5 多处显式守门 |

### 5.2 推荐（不阻塞 Gate 2；S2.0.1/S2.0.2 收口期补）

| # | 验收项 | 当前状态 |
|---|---|---|
| 5.2.1 | OCR 引擎选型（paddle-ocr / tesseract / cloud）| ⚠️ 用户裁定（per `308` §SCHEMA "本刀不做"）|
| 5.2.2 | `validate_ocr_input()` API 实装（per §2.3）| ⚠️ 后续 knife（tasking 31X+）|
| 5.2.3 | `source_document.doc_kind = 'OCR_SCAN'` schema migration | ⚠️ 后续 knife（tasking 31X+；本刀不引入 migration）|
| 5.2.4 | paddle-ocr 本地依赖 + Dockerfile layer | ⚠️ 后续 knife |
| 5.2.5 | 端到端 pytest（upload → OCR → SHA lineage → S2.2 ingestion）| ⚠️ 后续 knife |
| 5.2.6 | 至少 1 个真实 PDF（用户裁定提供；非爬源）| ⚠️ O3 收口须用户主动 `--confirm-o3=PATH` |

### 5.3 必带 OPEN（per docs/34 §3 + docs/45 §6）

| OPEN | 状态 | Gate 2 必带？ |
|---|---|---|
| **O3 OCR 生产路径** | ⚠️ **本刀仅规划**；**O3 仍 OPEN**（O3 实装 + 引擎 + 真实样本 = tasking 31X+）| ✅ **必带**（per docs/34 §3 + §120）|
| **O1 真实 SHA** | ⚠️ **O1 仍 OPEN**（WAITING_FILE；等用户 `--confirm-o1=PATH`）| ✅ **必带**（per docs/45 §3 O1）|
| **O2 cron / 通知 / 真实联外探针** | Stage 1 运维 OPEN | ⚠️ 演示级可过 |

---

## §6. 依赖关系

### 6.1 上游依赖（必须先满足）

| 依赖 | 来源 | 当前状态 |
|---|---|---|
| `docs/48` 真 SHA intake 手册 + `scripts/intake_real_sha_if_present.py` | `291` 已交 | ✅ |
| `scripts/compute_file_sha.py` `ALLOWED_PREFIXES` 守门 | S1.6 已交 | ✅ |
| `scripts/replace_demo_with_real.py` 真 SHA 替换 demo | S1.7 已交 | ✅ |
| `source_document` 表 schema（`schema/01-core.sql`）| S1.5 已交 | ✅ |
| `lineage` JSONB 字段契约（`docs/33` + `docs/47` §3.1）| `docs/47` 已交 | ✅ |
| S1.18 `is_demo` sentinel（`'true'` / `'false'` 字符串）| S1.18 已交 | ✅ |
| admin upload 端点 + XSS 消毒 + Turnstile（per `puer-hub-security-hardening.md` 模板可复用）| puer-hub 已交 | ✅（可复用模式；本项目未必直接复用，需适配）|

### 6.2 下游消费者（O3 收口后受益）

| 下游 | 来源 | 受益 |
|---|---|---|
| S2.1-lite `mart_person_tenure` | Cursor 174 OPEN | 干部任免 PDF OCR → `person` / `tenure` 表 |
| S2.2 `policy_observation` | docs/44 §2 | 政府工作报告 OCR → `policy_observation` 表 |
| S2.4 `fiscal_observation` | docs/44 §2 | 财政预决算 OCR → `fiscal_observation` 表 |
| S2.7-b-full 真数据迁移刀 | docs/47 §6.3 + `303` 路线图 | O3 真样本 → 替换 `303` demo 占位 `relatedPersons` |

### 6.3 阻塞项

| 阻塞 | 影响 | 解锁条件 |
|---|---|---|
| ❌ OCR 引擎未选型 | 步骤 4 无法实装 | 用户裁定（paddle-ocr / tesseract / cloud）|
| ❌ O1 真实 SHA 未提供 | O3 收口无锚点 | 用户主动 `--confirm-o1=PATH`（per `291` intake）|
| ❌ O3 真实 PDF 未提供 | O3 流水线无端到端验证 | 用户主动 `--confirm-o3=PATH` |
| ❌ S2.1-lite `mart_person_tenure` 未 PASS | 步骤 7 S2.1-lite 分发阻塞 | Cursor 174 S2.1 落地 |
| ❌ S2.2 / S2.4 schema 未 PASS | 步骤 7 S2.2/S2.4 分发阻塞 | 后续 knife 落地 |

---

## §7. 红线自检（per `308` §红线 + docs/34 §1/§3 + docs/06 §6.6 + docs/42 §8）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ §0 + §5.1.8 显式守门 |
| ❌ 不宣布 O3 收口 | ✅ §0 + §5.3 显式 OPEN |
| ❌ 不爬源（HTTP / gov.cn / 任何第三方）| ✅ §2.2 + §3.2 步骤 4 显式禁止 |
| ❌ 不登录绕过（cookie / 账号 / headless browser / Selenium / Playwright）| ✅ §2.2 显式禁止 |
| ❌ 不伪造样本 | ✅ §2.2 + §3.2 步骤 6 `is_demo=false` 契约守门 |
| ❌ 不擅自收口 O1/O3 | ✅ §5.3 OPEN 清单显式 |
| ❌ 不实装 OCR 引擎 | ✅ §0 范围 + §3.2 步骤 4 "推荐" 注明用户裁定 |
| ❌ 不引入新依赖（paddle-ocr / tesseract / cloud）| ✅ §0 范围 |
| ❌ 不改 schema | ✅ §0 范围 |
| ❌ 不改 dbt 模型 | ✅ §0 范围 |
| ❌ 不改业务 UI | ✅ §0 范围 |
| ❌ 不改 Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-48 / `00-CC-CURRENT.md`）| ✅ §0 范围 |
| ❌ 不改 `gate_thresholds.json` | ✅ §0 范围 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不索要 PAT | ✅ |
| ✅ 仅规划蓝图（不包含可执行 OCR 代码）| ✅ 本文件 = markdown |
| ✅ 与 `is_demo`/SHA lineage 衔接（复用 docs/48 契约）| ✅ §4 |
| ✅ 4 退出码契约与 docs/48 一致 | ✅ §4.3 |
| ✅ O3 OPEN 显式携带（per docs/34 §3 + §120）| ✅ §5.3 |

---

## §8. 不在范围（per `308` §SCHEMA "本刀不做"）

| 项 | 推迟到 |
|---|---|
| OCR 引擎选型 / 实装 / 调参 | 用户裁定 → tasking 31X+ |
| `validate_ocr_input()` API 实装 | tasking 31X+ |
| `source_document.doc_kind = 'OCR_SCAN'` schema migration | tasking 31X+ |
| paddle-ocr / tesseract 依赖引入 | tasking 31X+ |
| 端到端 pytest（upload → OCR → SHA lineage → ingestion）| tasking 31X+ |
| 真实江苏政府文件 PDF（O3 收口锚点）| 用户线下提供 + `--confirm-o3=PATH` |
| O3 流水线代码 / Docker / CI | tasking 31X+ |

---

## §9. 与既有 docs/40-49 系列的关系

| docs | 主题 | 与本文件关系 |
|---|---|---|
| `docs/40` | Stage 1 总览 | 上游 |
| `docs/41` | S2.6 反例 trigger 规划 | 平行 |
| `docs/42` | 字段白名单 + 禁词守门 | 上游（`is_demo`/`lineage` 字段白名单）|
| `docs/43` | S2.9 同类对比契约 | 平行 |
| `docs/44` | Stage 2 / Gate 2 整体规划 | 上游（§2 Gate 2 七条 + §3 docs/10 §3.1-3.5）|
| `docs/45` | Gate 2 评审索引 | 上游（§3 O3 OPEN 显式；§5.3 必带）|
| `docs/46` | S2.5 inference alignment 规划 | 平行 |
| `docs/47` | S2.7-b-full mart evidence 规划 | 上游（§3.1 lineage 字段契约）|
| `docs/48` | 真 SHA intake 手册 | 上游（§2 allowlist + §3 4 退出码 + §4 判定契约）|
| **`docs/49`** | **O3 OCR 生产路径规划（本文件）** | — |
| `docs/10` | 测试方法层 | 上游（§3.1-3.5 测试覆盖）|

> ⚠ 本文件不修改 `docs/40-48` 既有内容；仅作交叉引用。

---

## §10. 附：未决问题（待用户裁定）

| # | 问题 | 默认值 | 触发 |
|---|---|---|---|
| Q1 | OCR 引擎选型（paddle-ocr / tesseract / cloud）| 默认 paddle-ocr（中文精度高 + 本地离线）| 用户裁定 |
| Q2 | `--enable-cloud-ocr=PROVIDER` 显式 flag 是否启用（用于部分高精度场景）| 默认禁用（离线优先）| 用户裁定 |
| Q3 | `source_document.doc_kind = 'OCR_SCAN'` schema migration 编号（0XX）| 留空（待 0XX 编号）| 后续 knife |
| Q4 | 端到端 pytest fixture PDF（不伪造）| 用户手动提供 + `--confirm-o3=PATH` | 用户裁定 |

---

## §11. 下次 heartbeat 预期

- `queue_rev 128` 完成后：Cursor 收 `309` → 下发 `310-stage0-cursor-s308-o3-ocr-prod-path-plan-audit-…md`（PASS/FAIL）
- 若 PASS：`docs/49` OCR 流水线规划锁定；O3 仍 OPEN（实装 + 真实 PDF 仍待 tasking 31X+）
- 若 FAIL：`309-correction` 回合（修 §3 流水线步骤 / 修 §4 lineage 契约 / 修 §5 验收清单 / re-commit）

---

— End of `docs/49` —

> ⚠ **本文件不宣布 Gate 2 / O3 PASS**（per `308` §红线 + docs/34 §1）。
> ⚠ **本文件不实装 OCR 引擎**（per `308` §SCHEMA "本刀不做"）。
> ⚠ **本文件不爬网**（per `308` §红线 + §2.2）。
> ⚠ **本文件不登录绕过**（per `308` §红线 + §2.2）。
> ⚠ **本文件不伪造样本**（per `308` §红线 + §2.2 + §3.2 步骤 6）。
> ⚠ **O3 仍 OPEN**（per docs/34 §3 + §120 + §5.3 必带 OPEN 清单）。
> ⚠ **O1 仍 OPEN**（per docs/45 §3 O1；WAITING_FILE；等用户 `--confirm-o1=PATH`）。
> ⚠ **OCR 引擎选型待用户裁定**（per §3.2 步骤 4 + §10 Q1）。
> ⚠ **真实 PDF 待用户主动 `--confirm-o3=PATH`**（per §10 Q4 + docs/48 §3）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。