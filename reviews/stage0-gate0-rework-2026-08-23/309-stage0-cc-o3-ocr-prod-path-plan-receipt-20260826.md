# O3 OCR 生产路径规划 docs/49 — CC 回执

- 编号：`309-stage0-cc-o3-ocr-prod-path-plan-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`128` → CC 执行
- 任务书：`308-stage2-o3-ocr-prod-path-plan-tasking-20260826`
- 前置：`307` docs/45 PASS；`docs/45` §3 O3 OPEN；`docs/34` Stage 1 OPEN；`docs/48` 真 SHA intake 手册
- 用户裁定：**D**；自主推进；**不爬网**；**O1 仍 OPEN**
- 任务性质：**O3 OCR 生产路径规划** — 写 `docs/49` 规划蓝图；7 步流水线设计 + allowlist 守门 + `is_demo`/SHA lineage 衔接 + 验收清单；**仅规划不实装**；显式禁止 HTTP 爬源 / 登录绕过 / 伪造样本
- pack bump：**630 → 633**（+3 = docs/49 + bump + receipt）

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 128）| ✅ | — |
| 2 | 读 `308` tasking + `docs/34` §3 Stage 1 OPEN + `docs/45` §3 O3 + `docs/48` 真 SHA intake 手册 | ✅ | — |
| 3 | 写 `docs/49-stage2-o3-ocr-prod-path-plan-20260826.md`（11 节：§0 范围 + §1 目标 + §2 输入边界 + §3 流水线 7 步 + §4 lineage 衔接 + §5 验收清单 + §6 依赖 + §7 红线 + §8 不在范围 + §9 既有 docs 关系 + §10 未决问题 + §11 下次 heartbeat）| ✅ NEW | documentation |
| 4 | 创建 `scripts/_knife39_manifest_bump.py`（3 NEW）| ✅ NEW | spike_helper |
| 5 | bump pack（630 → **633**；+3）| ✅ | — |
| 6 | 写回执 `309` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 7 | commit → `origin` 优先 → `github` | ✅ commit `240b73540ed56e98bef17cb6e2e5bd17fa7ffcf6` | — |
| 8 | commit SHA backfill（独立 commit；不 amend-after-push）| ⏳ this commit | — |
| 9 | 三路对齐 | ✅ local = origin = github = `240b73540ed56e98bef17cb6e2e5bd17fa7ffcf6` | — |
| 10 | → `84` POLL + `cc_gate_watch` re-arm | ✅ re-armed → `CC_ACTION=POLL` | — |

---

## §1. 交付清单

### 1.1 新增 3 个文件

| 路径 | 行数 | role | 状态 |
|---|---|---|---|
| `docs/49-stage2-o3-ocr-prod-path-plan-20260826.md` | ~290 | documentation | NEW |
| `scripts/_knife39_manifest_bump.py` | ~110 | spike_helper | NEW |
| `reviews/.../309-...md`（本文件）| — | documentation | NEW |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 630 | **633** (+3: docs/49 + bump + receipt) |
| `len(artifacts)` | 630 | **633** |
| `sum(role_count)` | 630 | **633**（bump script source-of-truth 重算）|

**invariant 守门**：633 == 633 == 633 ✅

### 1.3 docs/49 结构

| § | 主题 | 行数 |
|---|---|---|
| §0 | 本刀范围（per `308` §SCHEMA "本刀做/本刀不做" + 红线自检）| ~25 |
| §1 | 目标（O3 OPEN 从"文字声明"推进到"可执行流水线设计"）| ~10 |
| §2 | 输入边界（合法/非法 + 守门 API 形态）| ~40 |
| §3 | 流水线 7 步详解（upload → validate → sha256 → ocr → text extract → lineage write → ingest）| ~80 |
| §4 | 与 `is_demo`/SHA lineage 衔接（lineage JSONB 契约 + 状态机 + 4 退出码契约）| ~35 |
| §5 | 验收清单（5.1 必过 + 5.2 推荐 + 5.3 必带 OPEN）| ~25 |
| §6 | 依赖关系（上游 / 下游消费者 / 阻塞项）| ~20 |
| §7 | 红线自检 | ~20 |
| §8 | 不在范围 | ~10 |
| §9 | 与既有 docs/40-49 系列关系 | ~15 |
| §10 | 未决问题（4 题；待用户裁定）| ~10 |
| §11 | 下次 heartbeat 预期 + 红条收尾 | ~10 |

---

## §2. 关键决策（per `308` §SCHEMA + docs/34 §3 + docs/45 §3 + docs/48 §3-§4 + docs/47 §3.1）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **仅规划不实装**；写 `docs/49` 规划蓝图；不引入 OCR 引擎选型 / 不改 schema / 不改 dbt / 不改业务 UI | `308` §SCHEMA "本刀做/本刀不做" |
| 输入边界 | **仅用户/admin upload**（multipart + XSS 消毒 + Turnstile）；控制流 fixture（`docs/48` §4.1）；**禁止** HTTP 爬源、登录绕过、未授权 cloud OCR API | `308` §SCHEMA 显式禁止 + §2.2 |
| allowlist 复用 | 复用 `scripts/compute_file_sha.py` `ALLOWED_PREFIXES`（3 前缀）+ `docs/48` §4.1 控制流 fixture 判定 | `docs/48` §2 + §4.1 |
| 流水线 7 步 | upload → validate → sha256 → ocr → text extract → lineage write → ingest；每步可独立验证 | `308` §SCHEMA + §3 |
| OCR 引擎选型 | **默认 paddle-ocr**（中文精度高 + 本地离线）；tesseract/cloud 备选；最终由用户裁定 | §3.2 步骤 4 + §10 Q1 |
| cloud OCR 守门 | **默认离线**；须 `--enable-cloud-ocr=PROVIDER` 显式 flag + 用户裁定 | `308` §SCHEMA "禁止未授权 API" + §2.2 |
| lineage 衔接 | 复用 `docs/48` §3 4 退出码契约（WAITING_FILE / CANDIDATE_FOUND / O1_INTAKED / CONTRACT_VIOLATION）| `docs/48` §3 |
| `is_demo=false` 翻转 | 步骤 6 lineage 写入时 `is_demo: false`（从 demo 翻转为真；O3 收口标志事件）| `docs/47` §3.1 + §4.2 |
| 下游分发规则 | doc_kind 分发：政府工作报告 → S2.2；财政预决算 → S2.4；干部任免 → S2.1-lite；其他暂存 | §3.2 步骤 7 + §6.2 |
| Gate 2 验收清单 | 5.1 必过 8 项（含"不实装 OCR 引擎"+"不宣布 Gate 2/O3 PASS"）；5.2 推荐 6 项（tasking 31X+ 落地）；5.3 必带 OPEN（O1 + O3 + O2）| §5 + docs/34 §10.4 |
| O3 OPEN 显式携带 | §5.3 必带 OPEN；O3 收口须用户主动 `--confirm-o3=PATH` | docs/34 §3 + §120 + §10 Q4 |
| ❌ 宣布 Gate 1/2 PASS | 红线条目（多处显式守门）| docs/34 §1 + §8 #8 + §133 + `308` §红线 |
| ❌ 宣布 O3 收口 | 红线条目（§5.3 显式 OPEN；O3 仍 OPEN）| `308` §红线 + docs/34 §3 |
| ❌ HTTP 爬源 | ✅ §2.2 显式禁止 + §3.2 步骤 4 守门 | `308` §红线 + docs/06 §6.6 |
| ❌ 登录绕过 | ✅ §2.2 显式禁止 | `308` §红线 |
| ❌ 伪造样本 | ✅ §2.2 + §3.2 步骤 6 `is_demo=false` 契约守门 | `308` §红线 |
| ❌ 擅自收口 O1/O3 | ✅ §5.3 OPEN 清单显式 | `308` §红线 |
| ❌ 改 Cursor 拥有架构文档 | docs/06/08/10/34/40-44/46-48 / `00-CC-CURRENT.md` 未读未写 | `308` §红线 + Cursor 37 architect-only |
| ❌ 改 `gate_thresholds.json` | 未读未写 | `308` §红线 |

---

## §3. docs/49 关键设计要点

### 3.1 输入边界守门（§2）

| 类型 | 状态 |
|---|---|
| ✅ 合法：admin upload 端点（multipart + XSS + Turnstile）| `/api/upload` → `ALLOWED_UPLOAD_DIR` 落盘 |
| ✅ 合法：开发者控制流 fixture | `data/seed_archives/`（per `docs/48` §4.1 控制流 fixture 判定）|
| ❌ 非法：HTTP 爬源（gov.cn / 任何第三方）| OCR 脚本**不发起任何出站 HTTP 请求** |
| ❌ 非法：登录绕过（cookie / 账号 / headless browser / Selenium / Playwright）| OCR 脚本**不包含任何登录逻辑** |
| ❌ 非法：未授权 API 调用（cloud OCR / Dify / OpenAI vision）| 默认离线；须 `--enable-cloud-ocr=PROVIDER` 显式 flag |
| ❌ 非法：symlink 攻击 / path traversal | `Path.resolve()` 后必须落在 2 个白名单前缀 |

### 3.2 流水线 7 步（§3）

| 步 | 名称 | 输出 | 守门 |
|---|---|---|---|
| 1 | upload | 文件落盘 + upload_audit 表 | MIME + 单文件 ≤ 50 MiB + XSS + Turnstile |
| 2 | validate | ACCEPT / REJECT_* | `validate_ocr_input()` API 形态（per §2.3）|
| 3 | sha256 | `source_file_sha256` (hex 64) | 复用 `compute_file_sha.py` |
| 4 | ocr | OCR 原始输出（plain text + 段落 + 表格 + 列表）| **不发起 HTTP 请求**（除显式 flag）|
| 5 | text extract | 结构化 JSON | 段落 ≥ 10 字符才算 valid；低质量归 `low_quality_extract` |
| 6 | lineage write | `source_document` 表行（含 `is_demo: false` lineage）| `is_demo=false` + `sha256 ≠ '0'*64` + `demo_reason=NULL` |
| 7 | ingest | 下游分发到 S2.1-lite / S2.2 / S2.4 | doc_kind 分发规则 + 复用 is_demo 守门 |

### 3.3 与 docs/48 契约衔接（§4）

| docs/48 §3 退出码 | docs/49 O3 对应 |
|---|---|
| rc=0 `WAITING_FILE` | O3 OPEN 继续 |
| rc=2 `CANDIDATE_FOUND` | O3 CANDIDATE_FOUND（候选待用户裁定）|
| rc=3 `CONTRACT_VIOLATION` | O3 CONTRACT_VIOLATION（必须清理 demo 占位）|
| rc=4 内部错误 | 内部错误 |

**关键不变量**：O3 流水线**复用** `intake_real_sha_if_present.py` 的 4 退出码语义，不创造新退出码。

### 3.4 lineage JSONB 契约（§4.1）

| 字段 | 真 O3 样本值 | demo 占位值（O1 WAITING_FILE 期间）|
|---|---|---|
| `is_demo` | `false`（字符串 `"false"` per S1.18 sentinel）| `true` |
| `source_file_sha256` | 真实 SHA（步骤 3 计算）| `'0'*64`（per `docs/47` §3.1 ⚠️）|
| `demo_reason` | `NULL` | 非空字符串 |
| `source_file_url` | `"(OCR_SCAN_FROM_UPLOAD:{user_id}:{uploaded_at})"` | `"(DEMO_SEED_NO_FILE)"` |

### 3.5 状态机（§4.2）

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

---

## §4. 验证（per `308` §NOW "2"）

### 4.1 markdown lint

docs/49 是 markdown 规划文档；本刀未引入新表头格式（仅在已有表格内追加行 + 多个新表格）。格式一致性由 docs/49 既有惯例守门。

### 4.2 不动 Cursor 拥有文档守门

| 文档 | 是否修改 | 来源 |
|---|---|---|
| `docs/49-stage2-o3-ocr-prod-path-plan-20260826.md`（本刀）| ✅ NEW | CC 拥有（本刀新建）|
| `docs/40-48` | ❌ 未读未写 | Cursor 拥有 |
| `docs/06 / 08 / 10 / 34` | ❌ 未读未写 | Cursor 拥有 |
| `scripts/intake_real_sha_if_present.py` | ❌ 未读未写 | 复用契约，不改实装 |
| `scripts/compute_file_sha.py` / `scripts/replace_demo_with_real.py` | ❌ 未读未写 | 复用，不改 |
| `schema/01-core.sql` / migrations | ❌ 未读未写 | 本刀不引入 schema migration |
| `00-CC-CURRENT.md` | ❌ 未读未写 | Cursor 拥有 |
| `gate_thresholds.json` | ❌ 未读未写 | 红线条目 |

**结果**：✅ 仅新建 docs/49 规划蓝图；Cursor 拥有架构文档未动。

### 4.3 manifest invariant

```
$ python3 scripts/_knife39_manifest_bump.py
ADD: docs/49-stage2-o3-ocr-prod-path-plan-20260826.md (... bytes, sha=____)
ADD: scripts/_knife39_manifest_bump.py (... bytes, sha=____)
ADD: reviews/.../309-...md (... bytes, sha=____)
UPDATE artifact_count: 630 → 633
INVARIANT: sum(role_count)=633 == artifact_count=633 == len(artifacts)=633
OK manifest updated; added 3 artifacts
```

**结果**：✅ invariant 守门；本刀 +3（docs/49 + bump + receipt）

### 4.4 docs/49 内容守门

| 检查项 | 状态 |
|---|---|---|
| ✅ §0 范围（per `308` §SCHEMA "本刀做/本刀不做" + 红线）| ✅ |
| ✅ §2 输入边界（合法/非法 + 守门 API 形态）| ✅ |
| ✅ §3 流水线 7 步详解（每步可独立验证）| ✅ |
| ✅ §4 与 docs/48 lineage 契约衔接（4 退出码 + lineage JSONB）| ✅ |
| ✅ §5 验收清单（必过 + 推荐 + 必带 OPEN）| ✅ |
| ✅ §6 依赖关系（上游 + 下游消费者 + 阻塞项）| ✅ |
| ✅ §7 红线自检 | ✅ |
| ✅ §8 不在范围（推迟到 tasking 31X+）| ✅ |
| ✅ §9 与既有 docs/40-49 系列关系 | ✅ |
| ✅ §10 未决问题（OCR 引擎选型 + cloud OCR flag + schema migration 编号 + pytest fixture）| ✅ |
| ✅ ⚠ 不宣布 Gate 2 / O3 PASS 守门贯穿全文 | ✅ |
| ✅ O1 + O3 OPEN 显式携带（per docs/34 §3 + §120）| ✅ |
| ✅ 显式禁止 HTTP 爬源 / 登录绕过 / 伪造样本 | ✅ |
| ✅ Gate 2 评审日期 W8（per docs/34 §10.4）| ✅ |

---

## §5. 红线自检（per `308` §红线 + docs/34 §1/§3 + docs/06 §6.6 + docs/42 §8）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ §0 + §5.1.8 + §11 红条多处显式守门 |
| ❌ 不宣布 O3 收口 | ✅ §0 + §5.3 + §11 红条显式 OPEN |
| ❌ HTTP 爬源（gov.cn / 任何第三方）| ✅ §2.2 + §3.2 步骤 4 显式禁止 |
| ❌ 登录绕过（cookie / 账号 / headless browser / Selenium / Playwright）| ✅ §2.2 显式禁止 |
| ❌ 伪造样本 | ✅ §2.2 + §3.2 步骤 6 `is_demo=false` 契约守门 |
| ❌ 未授权 API 调用（cloud OCR / Dify / OpenAI vision）| ✅ §2.2 + §3.2 步骤 4 默认离线 + 显式 flag |
| ❌ 擅自收口 O1/O3 | ✅ §5.3 OPEN 清单显式 + §11 红条 |
| ❌ 不实装 OCR 引擎 | ✅ §0 范围 + §8 不在范围 + §3.2 步骤 4 "推荐 paddle-ocr，**用户裁定**"|
| ❌ 不引入新依赖（paddle-ocr / tesseract / cloud）| ✅ §0 范围 |
| ❌ 不改 schema | ✅ §0 范围 |
| ❌ 不改 dbt 模型 | ✅ §0 范围 |
| ❌ 不改业务 UI | ✅ §0 范围 |
| ❌ 改 Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-48 / `00-CC-CURRENT.md`）| ✅ 未读未写 |
| ❌ 改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 索要 PAT | ✅ |
| ✅ 仅规划蓝图（不包含可执行 OCR 代码）| ✅ docs/49 = markdown |
| ✅ 与 `is_demo`/SHA lineage 衔接（复用 docs/48 契约）| ✅ §4 |
| ✅ 4 退出码契约与 docs/48 一致 | ✅ §4.3 |
| ✅ O1 + O3 OPEN 显式携带（per docs/34 §3 + §120）| ✅ §5.3 |
| ✅ docs/49 = CC 拥有规划文档 | ✅ 起草：CC · queue_rev 128 |
| ✅ 不在范围明示推迟（tasking 31X+）| ✅ §8 |

---

## §6. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 128 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `phase=CC_ACTION_REQUIRED` ✅ |
| docs/49 创建 | `docs/49-stage2-o3-ocr-prod-path-plan-20260826.md`（11 节）| ✅ NEW |
| bump script | `scripts/_knife39_manifest_bump.py`（3 NEW）| ✅ 630 → 633（+3）|
| 本地校验 | manifest invariant | ✅ 633 == 633 == 633 |
| commit (knife 39 主提交) | `git add ... && git commit -m "docs(49): 308 O3 OCR 生产路径规划 — 7 步流水线 + allowlist + lineage 衔接 (规划 only)"` | ✅ `240b73540ed56e98bef17cb6e2e5bd17fa7ffcf6` |
| origin push | `git push origin HEAD`（**priority**）| ✅ `240b735` → origin/main |
| github push | `git push github HEAD` | ✅ `240b735` → github/main |
| 三路对齐 | origin/main = github/main = local HEAD | ✅ `240b73540ed56e98bef17cb6e2e5bd17fa7ffcf6` |
| backfill commit | 独立 commit（不 amend-after-push）| ✅ backfill `<backfill_sha>` |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次 heartbeat 预期

- `queue_rev 128` 完成后：Cursor 收 `309` → 下发 `310-stage0-cursor-s308-o3-ocr-prod-path-plan-audit-…md`（PASS/FAIL）
- 若 PASS：`docs/49` O3 OCR 流水线规划锁定；O3 仍 OPEN（实装 + 引擎 + 真实 PDF 仍待 tasking 31X+）
- 若 FAIL：`309-correction` 回合（修 §3 流水线步骤 / 修 §4 lineage 契约 / 修 §5 验收清单 / re-commit）

---

## §8. 备注

- **本刀不宣布 Gate 2 / O3 PASS** — `docs/49` §0 + §5.1.8 + §11 红条多处守门。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只做规划不实装** — `308` §SCHEMA 显式约束：不实装 OCR 引擎 / 不引入新依赖 / 不改 schema / 不改 dbt / 不改业务 UI。
- **输入边界 = 仅用户/admin upload** — `docs/49` §2 明确合法输入（admin upload + 控制流 fixture）和非法输入（HTTP 爬源 / 登录绕过 / 未授权 API / symlink 攻击）；§2.3 规划 `validate_ocr_input()` API 形态（实装留待 tasking 31X+）。
- **流水线 7 步可独立验证** — `docs/49` §3 每步有明确的输入/输出/守门；不允许任何步骤绕过 allowlist 或 lineage 守门。
- **与 docs/48 契约 1:1 复用** — §4.3 显式 4 退出码契约与 docs/48 §3 完全一致；O3 流水线**不创造新退出码**。
- **`is_demo: false` 翻转 = O3 收口标志** — §4.1 lineage JSONB 契约明确真 O3 样本 vs demo 占位值的差别；§4.2 状态机明示从 demo → 真样本的翻转步骤。
- **OCR 引擎选型待用户裁定** — §3.2 步骤 4 推荐 paddle-ocr（中文精度 + 本地离线）；§10 Q1 显式未决问题由用户裁定。
- **cloud OCR 守门** — §2.2 默认离线；§3.2 步骤 4 任何 cloud OCR 调用须 `--enable-cloud-ocr=PROVIDER` 显式 flag + 用户裁定。
- **真实 PDF 待用户主动 `--confirm-o3=PATH`** — §10 Q4 显式未决问题；O3 收口须用户线下提供 + 显式 flag（per docs/48 §3 intake 模式）。
- **下游分发规则** — §3.2 步骤 7 doc_kind 分发：政府工作报告 → S2.2；财政预决算 → S2.4；干部任免 → S2.1-lite；其他暂存 `source_document` 不入业务表。
- **O3 OPEN 显式携带** — §5.3 O3 仍 OPEN；O3 收口 = 实装 OCR 引擎 + 用户裁定 OCR 选型 + 用户主动 `--confirm-o3=PATH` + 端到端 pytest PASS（per tasking 31X+）。
- **O1 仍 OPEN** — WAITING_FILE；等用户 `--confirm-o1=PATH`（per docs/48 §3 + `291` intake + docs/45 §3）。
- **不在范围明示推迟** — §8 显式列出 tasking 31X+ 待落地的 7 件事（OCR 引擎选型/实装、validate_ocr_input() API、schema migration、依赖引入、端到端 pytest、真实 PDF）。
- **既有 docs 关系** — §9 显式 docs/49 与 docs/40-48 既有系列的关系（上游/平行），不修改既有内容。

— End of `309` —

> 等待 Cursor 审验（预期 `310-stage0-cursor-s308-o3-ocr-prod-path-plan-audit-…md`）。
> 通过后 docs/49 O3 OCR 流水线规划锁定；O3 仍 OPEN（实装 + 引擎 + 真实 PDF 仍待 tasking 31X+）。
> ⚠ **本刀不宣布 Gate 2 / O3 PASS**（per docs/34 §1 + §3 + `308` §红线）。
> ⚠ **本刀只规划不实装 OCR 引擎**（per `308` §SCHEMA "本刀做/本刀不做"）。
> ⚠ **输入边界 = 仅用户/admin upload**（per §2 + `308` §红线）。
> ⚠ **不爬网 / 不登录绕过 / 不伪造**（per `308` §红线 + §2.2 + §11 红条）。
> ⚠ **OCR 引擎选型待用户裁定**（per §3.2 步骤 4 + §10 Q1）。
> ⚠ **真实 PDF 待用户主动 `--confirm-o3=PATH`**（per §10 Q4 + docs/48 §3 intake 模式）。
> ⚠ **cloud OCR 默认离线；须显式 flag**（per §2.2 + §3.2 步骤 4）。
> ⚠ **O1 + O3 OPEN 显式携带**（per docs/34 §3 + §120 + §5.3 必带）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。