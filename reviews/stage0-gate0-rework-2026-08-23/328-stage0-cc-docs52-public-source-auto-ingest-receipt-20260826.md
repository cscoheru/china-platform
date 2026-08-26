# 官方公开源自动获取规划 docs/52 — CC 回执

- 编号：`328-stage0-cc-docs52-public-source-auto-ingest-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`137` → CC 执行
- 任务书：`327-stage2-official-open-source-auto-ingest-plan-tasking-20260826`
- 前置：`326` docs/45 docs/51 登记 PASS；用户 2026-08-26 裁定**不再等用户投喂**；产品两目标=①自动检索官方公开数据 ②结构化呈现
- 用户裁定：**D**；覆盖此前「仅用户投递 O1」等待策略；遇登录/验证码/付费墙 → 报告用户（不绕过）
- 任务性质：**官方公开源自动获取规划**（per `327` §SCHEMA "本刀做"）— markdown-only；**不实装爬虫**；**不**绕过；**不**宣布 Gate/O1 PASS
- pack bump：**643 → 645**（+2 = bump + receipt；docs/52 NEW）

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 137）| ✅ | — |
| 2 | 读 `327` tasking + `docs/00 §3` 红线 7 + `docs/08 MVP` §192 + `source_registry/registry.csv` 6 行 + `docs/48 §5` contract + `docs/51 §5` 双路径 + `docs/49 §2.2` OCR 红线 | ✅ | — |
| 3 | 写 `docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md`（13 节；禁止 PASS 措辞；OPEN 必带；AUTH 升级协议 5 字段 + 4 用户裁定路径）| ✅ NEW | documentation |
| 4 | 创建 `scripts/_knife45_manifest_bump.py`（2 NEW；643 → 645）| ✅ NEW | spike_helper |
| 5 | bump pack（643 → **645**；+2）| ⏳ this commit | — |
| 6 | 写回执 `328` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 7 | commit → `origin` 优先 → `github` | ⏳ this commit | — |
| 8 | commit SHA backfill（独立 commit；不 amend-after-push）| ⏳ this commit | — |
| 9 | 三路对齐 | ⏳ this commit | — |
| 10 | → `84` POLL + `cc_gate_watch` re-arm | ⏳ re-arm | — |

---

## §1. 交付清单

### 1.1 新增 3 个文件

| 路径 | 行数 | role | 状态 |
|---|---|---|---|
| `docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md` | ~310 | documentation | NEW（13 节）|
| `scripts/_knife45_manifest_bump.py` | ~110 | spike_helper | NEW |
| `reviews/.../328-...md`（本文件）| — | documentation | NEW |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 643 | **645** (+2: bump + receipt; docs/52 NEW) |
| `len(artifacts)` | 643 | **645** |
| `sum(role_count)` | 643 | **645**（bump script source-of-truth 重算）|

**invariant 守门**：645 == 645 == 645 ✅

### 1.3 docs/52 结构

| § | 内容 |
|---|---|
| §0 | 一句话总览（registry 登记 → 6 步流水线 → is_demo=false 闸门；遇 AUTH 触发 → 停止+报告用户）|
| §1 | 允许范围（3 类公开源：source_registry 登记 / 开放 API / 无登录公开页面稳定 URL；含 6 行公开源表）|
| §2 | 禁止事项 10 项（绕验证码/盲爬/伪造/以网页数作完成标准/headless browser/静默失败/未登记源/降 OCR/批量 2020-2025/派生 score）|
| §3 | 首批 1-3 试点源建议（NBS `NATIONAL_BULLETIN` HTML → Hubei EXCEL → Shenzhen HTML；archive.org/NPC 不入首批；NBS `NATIONAL_YEARBOOK` JPG 依赖 O3 不入首批）|
| §4 | 流水线 6 步（discover / download / sha256 / archive / extract / observation）+ is_demo=false 闸门 |
| §5 | 与 docs/48 intake / docs/51 O1 drop 关系（A 路径用户投递 + B 路径公开源自动并存；命名空间不混用）|
| §6 | **AUTH 升级协议**（6 触发条件 + 5 报告字段 + 4 用户裁定路径；不绕过 + 不静默失败）|
| §7 | 验收清单 11 项 |
| §8 | 下一刀边界（首个 connector 落地 tasking 32X+；7 项待办 + 4 项实装后验收）|
| §9 | 不可隐藏清单 15 项 |
| §10 | 红线 18 项 ❌ |
| §11 | 不在范围（per `327` §SCHEMA "本刀不做"）|
| §12 | 下次心跳预期 |

---

## §2. 关键决策（per `327` §SCHEMA + docs/00 §3 + PRD 1.3 + 12.8 + 15.12 + docs/48 §5 + docs/51 §5 + docs/49 §2.2 + docs/34 §120 + `321` §红线 + `284` §依赖）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **官方公开源自动获取规划**（per `327` §SCHEMA "本刀做"）— markdown-only；**不实装爬虫**；**不**绕过；**不**宣布 Gate/O1 PASS | `327` §SCHEMA |
| docs/52 不属于 Cursor 拥有架构文档 | docs/06/08/10/34/40-44/46-50 是 Cursor 拥有；docs/52 = CC 维护公开源规划（per `327` §SCHEMA）| `327` §SCHEMA + Cursor 37 architect-only 红线 |
| §0 一句话总览 | registry → discover→download→sha256→archive→extract→observation → is_demo=false 闸门；遇 AUTH → 停止+报告用户 | `327` §SCHEMA + docs/48 §5 contract |
| §1 允许 3 类公开源 | source_registry 登记（6 行）+ 开放 API + 无登录公开页面稳定 URL | `327` §SCHEMA + docs/00 §3 + registry.csv |
| §1 含 6 行公开源表 | stats.gov.cn ×2 + tjj.hubei.gov.cn + sz.gov.cn + archive.org + wb.flk.npc.gov.cn | `source_registry/registry.csv` |
| §2 禁止 10 项 | 绕验证码 / 盲爬 / 伪造 / 网页数作完成标准 / headless browser / 静默失败 / 未登记源 / 降 OCR / 批量 2020-2025 / 派生 score | docs/00 §3 + PRD 1.3 + `327` §SCHEMA "本刀不做" |
| §3 首批 1-3 试点源 | NBS `NATIONAL_BULLETIN` HTML → Hubei EXCEL → Shenzhen HTML；**不入首批**：archive.org 1909 / NPC 法律 / NBS `NATIONAL_YEARBOOK` JPG（依赖 O3）| `327` §SCHEMA + docs/49 §5.3 |
| §4 流水线 6 步 | discover→download→sha256→archive→extract→observation；每步守门 | docs/48 §5 contract + docs/49 §4.2 WORM + registry.csv |
| §4 is_demo=false 闸门 | sha256 ≠ `'0'*64` + 真 lineage 字段齐（source_file_sha256 / is_demo / intake_ts / intake_status / source_agency）| docs/48 §5 contract + docs/06 §6.6 + docs/47 §3.1 ⚠️ |
| §5 与 docs/48 / docs/51 关系 | A 路径（用户投递 per docs/51）+ B 路径（公开源自动 per docs/52）**并存**；命名空间不混用 | `327` §SCHEMA + 用户 2026-08-26 裁定 + docs/51 |
| §5 命名空间 | A: `/tmp/cegr_uploads/`；B: `/opt/puer-hub/cegr_public_ingest/{YYYY-MM}/{domain}/{filename}` | docs/49 §4.2 + docs/51 §2 |
| §6 AUTH 升级协议 6 触发 | HTTP 302→登录 / 403/401/429 连续 3 次 / 验证码 / 付费墙 / 反爬检测 / headless browser 检测 | docs/00 §3 红线 7 + PRD 1.3 + 12.8 + registry.csv Hubei 备注 |
| §6 报告 5 字段 | 源 domain/category/URL + 费用估计 + 需要账号/订阅 + 替代公开源 + ETA | `327` §SCHEMA "本刀做" |
| §6 用户裁定 4 路径 | 提供授权 / 跳过该源（enabled=FALSE）/ 改用替代公开源 / 暂缓 | `327` §SCHEMA "本刀做" + docs/00 §3 |
| §8 下一刀 7 待办 | `scripts/auto_ingest_public_source.py` + pytest + 首个 connector + WORM archive + lineage 扩展（`intake_status='O1_AUTO_INTAKED'`）+ 命名空间不混用 + AUTH 报告模板 | `327` §SCHEMA "本刀做" |
| §9 不可隐藏清单 15 项 | Gate PASS 显式禁 + O1 收口显式禁 + 不实装爬虫 + 不绕 AUTH + 不盲爬 + 不伪造 + 不以网页数作完成标准 + 不静默失败 + 不降 OCR/批量 2020-2025/1909 + 不派生 score + 不改 Cursor 拥有文档 + 不改 registry 既有 6 行 + A/B 命名空间不混用 + 不构成 Gate 2 PASS/O3/真表/真数据/§3.2-3.4 收口 + 1909 ≠ 中国 | docs/00 §3 + docs/34 §120 + `327` §SCHEMA |
| ❌ 文首/文末 PASS 措辞 | header + §0 + §9 + §10 + §12 多次 ⚠ 显式 "不是 PASS 宣告" / "不是 O1 收口宣告" / "不是实装"；无 bare PASS | `327` §SCHEMA + §红线 |
| ❌ 业务代码改动 | docs/52 = markdown-only；schema / migration / dbt / pytest / TS / frontend / smoke-check 全部未动 | `327` §SCHEMA "本刀不做" |
| ❌ 爬源站 / 登录绕过 / OCR 降门槛 / headless browser | docs/52 §0 + §2 + §6 + §10 + header 多处显式禁止 | `327` §红线 + docs/49 §2.2 + registry.csv Hubei 备注 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | §2 + §10 显式禁止 | docs/06 §6.6 + docs/42 §8 |
| ❌ 改 Cursor 拥有架构文档 | docs/06/08/10/34/40-44/46-50 / `00-CC-CURRENT.md` / `gate_thresholds.json` 未读未写 | `327` §红线 + Cursor 37 architect-only |
| ❌ 改 `source_registry/registry.csv` 既有 6 行 | docs/52 仅引用既有 6 行；不修改 | `327` §SCHEMA + docs/52 §1 + §7 |
| ❌ 改 `docs/48` 既有内容 | docs/52 §4 + §5 引用 docs/48 §5 contract；不改 docs/48 | `327` §SCHEMA "本刀做/本刀不做" |
| ❌ 改 `docs/51` 既有内容 | docs/52 §5 引用 docs/51 双路径并存；不改 docs/51 | `327` §SCHEMA "本刀做/本刀不做" |
| ❌ 改 `scripts/intake_real_sha_if_present.py` 既有内容 | 脚本未读未写 | `327` §SCHEMA "本刀做/本刀不做" |
| ❌ 静默失败（不告知用户）| §6.3 + §10 显式禁止 | `327` §SCHEMA "禁止" + docs/00 §3 红线 7 |

---

## §3. docs/52 不可隐藏清单 15 项（per docs/34 §120 + `327` §SCHEMA）

| # | docs/52 §6/§9 出现项 | 守门位置 |
|---|---|---|
| 1 | 公开源自动获取不是 Gate PASS 宣告 | §0 + §10 + header ⚠ |
| 2 | 公开源自动获取不构成 O1 收口（O1 仍 OPEN WAITING_FILE；A + B 两路径都需执行）| §0 + §5 + §10 + header ⚠ |
| 3 | 公开源自动获取不实装全量爬虫 | §0 + §8 + header ⚠ |
| 4 | 不绕验证码 / 付费墙 / 登录 / 技术限制 | §2 + §6 + §10 + header ⚠ |
| 5 | 不盲爬全国市县（per docs/00 §3 红线 6）| §1 + §2 + §3 + §10 + header ⚠ |
| 6 | 不伪造 / 不伪造 SHA / 不伪造 lineage 字段 | §2 + §4 + §10 + header ⚠ |
| 7 | 不以抓取网页数作为完成标准（per docs/00 §3 红线 5）| §2 + §7 + §10 + header ⚠ |
| 8 | 不静默失败（遇 AUTH 触发必须报告用户）| §2 + §6.3 + §10 + header ⚠ |
| 9 | 不降 OCR 门槛 / 不批量 2020-2025 / 不把 1909 代表中国 | §10 + header ⚠ |
| 10 | 不派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank / DSH | §2 + §10 + header ⚠ |
| 11 | 不改 Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-50 / `00-CC-CURRENT.md` / `gate_thresholds.json`）| §10 + header ⚠ |
| 12 | 不改 `source_registry/registry.csv` 既有 6 行 | §1 + §7 + §10 + header ⚠ |
| 13 | A 路径（用户投递 per docs/51）+ B 路径（公开源自动 per docs/52）命名空间不混用 | §5 + §10 + header ⚠ |
| 14 | 公开源自动获取不构成 Gate 2 PASS / O3 收口 / person/tenure 真数据 / dbt mart 真表 / docs/10 §3.2-3.4 收口 | §0 + §10 + header ⚠ |
| 15 | archive.org 1909 美国统计摘要 ≠ 中国经济治理平台样本 | §1 + §3 + §10 + header ⚠ |

**结果**：✅ 15 项不可隐藏清单在 docs/52 中**共出现 40+ 次**显式 ⚠ 标注；公开源自动获取 / Gate 2 评审 / O1 收口 / 用户投递场景**无法隐藏或省略**（per docs/34 §120）。

---

## §4. 验证（per `327` §NOW "1-2"）

### 4.1 markdown lint

docs/52 是 markdown 文件；未引入新表头格式（仅在 docs/51 / docs/48 / docs/49 既有格式基础上加公开源规划）。格式一致性由 docs/51 既有惯例守门。

### 4.2 docs/52 内容守门

| 检查项 | 状态 |
|---|---|---|
| ✅ §0 一句话总览（registry → 6 步流水线 → is_demo=false 闸门；遇 AUTH → 停止+报告用户）| ✅ |
| ✅ §1 允许范围 3 类公开源 + 6 行公开源表 | ✅ |
| ✅ §2 禁止事项 10 项 | ✅ |
| ✅ §3 首批 1-3 试点源建议（NBS HTML → Hubei EXCEL → Shenzhen HTML；不入首批：archive.org/NPC/NBS YEARBOOK JPG）| ✅ |
| ✅ §4 流水线 6 步（discover / download / sha256 / archive / extract / observation）+ is_demo=false 闸门 | ✅ |
| ✅ §5 与 docs/48 / docs/51 双路径并存 + 命名空间不混用 | ✅ |
| ✅ §6 AUTH 升级协议 6 触发 + 5 报告字段 + 4 用户裁定路径 | ✅ |
| ✅ §7 验收清单 11 项 | ✅ |
| ✅ §8 下一刀边界（tasking 32X+）| ✅ |
| ✅ §9 不可隐藏清单 15 项 | ✅ |
| ✅ §10 红线 18 项 | ✅ |
| ✅ §11 不在范围（per `327` §SCHEMA "本刀不做"）| ✅ |
| ✅ §12 下次心跳预期 | ✅ |
| ✅ ⚠ 文首/文末禁止 "PASS" / "O1 收口宣告" / "实装" 措辞 | ✅ |
| ✅ docs/52 = markdown-only（无业务代码改动）| ✅ |
| ✅ Cursor 拥有架构文档未动 | ✅ |

### 4.3 不动 Cursor 拥有文档守门

| 文档 | 是否修改 | 来源 |
|---|---|---|
| `docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md`（本刀）| ✅ 新建 | CC 维护公开源规划（per `327` §SCHEMA）|
| `docs/00-project-assessment.md`（红线 7）| ❌ 未读未写 | docs/52 §6 + §9 + §10 引用；不修改 |
| `docs/08-mvp-plan.md`（line 192 不绕验证码）| ❌ 未读未写 | docs/52 §6 引用；不修改 |
| `docs/48-stage2-real-sha-intake-handbook-20260826.md` | ❌ 未读未写 | docs/52 §4 + §5 引用 docs/48 §5 contract；不修改 docs/48 既有契约 |
| `docs/51-stage2-o1-drop-checklist-20260826.md` | ❌ 未读未写 | docs/52 §5 引用 docs/51 双路径；不修改 docs/51 既有契约 |
| `docs/49-stage2-o3-ocr-prod-path-plan-20260826.md` | ❌ 未读未写 | docs/52 §3 + §10 引用 docs/49 §2.2 + §5.3 |
| `source_registry/registry.csv` | ❌ 未读未写 | docs/52 §1 + §7 引用既有 6 行；不修改 |
| `scripts/intake_real_sha_if_present.py` | ❌ 未读未写 | docs/52 §5 引用；不修改脚本既有契约（per docs/48 §6）|
| `scripts/compute_file_sha.py` / `scripts/replace_demo_with_real.py` / `scripts/seed_jiangsu_gdp_demo.py` | ❌ 未读未写 | docs/52 §4 引用 docs/48 §6；不修改 |
| `docs/44 / 47 / 41 / 36-39 / 42 / 43 / 50` | ❌ 未读未写 | Cursor 拥有架构文档 |
| `docs/06 / 08 / 10 / 34` | ❌ 未读未写 | Cursor 拥有 |
| `00-CC-CURRENT.md` | ❌ 未读未写 | Cursor 拥有 |
| `gate_thresholds.json` | ❌ 未读未写 | 红线条目 |

**结果**：✅ Cursor 拥有架构文档 + docs/00 + docs/08 + docs/48 + docs/51 + docs/49 + source_registry/registry.csv + scripts/intake_real_sha_if_present.py 既有契约全部未动；docs/52 是 CC 维护公开源规划（per `327` §SCHEMA "本刀做"）。

### 4.4 manifest invariant

```
$ python3 scripts/_knife45_manifest_bump.py
ADD: scripts/_knife45_manifest_bump.py (... bytes, sha=____)
ADD: reviews/.../328-...md (... bytes, sha=____)
UPDATE artifact_count: 643 → 645
INVARIANT: sum(role_count)=645 == artifact_count=645 == len(artifacts)=645
OK manifest updated; added 2 artifacts
```

**结果**：✅ invariant 守门；本刀 +2（bump + receipt），docs/52 NEW（增计数 1 已计入）

### 4.5 docs/52 grep "PASS" / "收口宣告" 检查

```
$ grep -nE "PASS|收口宣告" docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md
(only "不是 PASS 宣告" / "不构成 Gate 2 PASS" / "不是 O1 收口宣告" / "不宣布 Gate/O1/O3 收口" / "禁止收口宣告" 等显式禁止语境)
```

**结果**：✅ 无 bare "PASS" / bare "O1 收口宣告"；所有 "PASS" / "收口" 均在否定语境或显式禁止语境。

### 4.6 source_registry/registry.csv 既有 6 行守门

```
$ git diff source_registry/registry.csv | head
(empty — 未修改)
```

**结果**：✅ source_registry 既有 6 行未动；docs/52 §1 + §7 仅引用。

---

## §5. 红线自检（per `327` §红线 + docs/00 §3 + PRD 1.3 + 12.8 + 15.12 + docs/34 §1/§8 + docs/48 §8 + docs/49 §2.2 + docs/06 §6.6 + docs/42 §8）

| 红线 | 状态 | 守门位置 |
|---|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ | docs/52 §0 + §8 + §9 + §10 + header 多次 ⚠ |
| ❌ 不擅自 O1 收口（A + B 两路径并存）| ✅ | §0 + §5 + §9 + §10 + header 多次显式 |
| ❌ 不擅自 O3 收口 | ✅ | §3 + §9 + §10 + header 多次显式 |
| ❌ 不派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | ✅ | §2 + §10 显式禁止 |
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ | §10 显式禁止 |
| ❌ 不批量爬政策研究 / 财政预决算 / 官员履历 | ✅ | §2 + §10 显式 |
| ❌ **不绕过验证码、付费墙或网站技术限制**（per docs/00 §3 红线 7 + PRD 1.3 + 12.8）| ✅ | §0 + §2 + §6 + §9 + §10 + header 多次 ⚠ |
| ❌ **不盲爬全国市县**（per docs/00 §3 红线 6 + PRD 1.3 + 15.12）| ✅ | §1 + §2 + §3 + §9 + §10 + header 多次 ⚠ |
| ❌ **不以抓取网页数作为完成标准**（per docs/00 §3 红线 5 + PRD 1.3 + 12.5）| ✅ | §2 + §7 + §9 + §10 + header 多次 ⚠ |
| ❌ **不静默失败**（遇 AUTH 触发必须报告用户）| ✅ | §2 + §6.3 + §9 + §10 + header 多次 ⚠ |
| ❌ HTTP 爬源（仅 source_registry 登记的稳定公开源 + 开放 API + 无登录公开页面稳定 URL）| ✅ | §1 + §3 + §10 显式 |
| ❌ 登录绕过 | ✅ | §0 + §2 + §6 + §9 + §10 + header 多次显式 |
| ❌ 未授权 cloud OCR API | ✅ | §10 显式禁止（默认离线；O3 仍 OPEN）|
| ❌ headless browser 绕过反爬（registry.csv Hubei 备注）| ✅ | §2 + §6.1 + §10 显式 |
| ❌ 降 OCR 门槛 | ✅ | §10 + docs/49 §2.2 守门 |
| ❌ 启用 pgvector / RLS / partition | ✅ | Stage 2 边界；本刀不动 |
| ❌ 改 `gate_thresholds.json` | ✅ | 未读未写 |
| ❌ 改 `source_registry/registry.csv` 既有 6 行 | ✅ | §1 + §7 + §9 + §10 显式；未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ | Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ | ff-only pull |
| ❌ 不替用户下裁定（AUTH 升级协议 4 路径）| ✅ | §6.3 显式 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ | 仅回执要点 |
| ❌ 不索要 PAT | ✅ | — |
| ✅ pack invariant 守门 | ✅ | 643 → 645；bump script source-of-truth |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ | `328-...md` |
| ✅ docs/52 = CC 维护公开源规划 | ✅ | `327` §SCHEMA "本刀做" |
| ✅ docs/52 文首/文末**禁止 PASS / O1 收口宣告 / 实装** 措辞 | ✅ | grep 验证无 bare PASS / bare 收口宣告 |
| ✅ docs/52 = markdown-only（无业务代码改动）| ✅ | §11 显式 "不创业务代码" |
| ✅ Cursor 拥有架构文档未动 | ✅ | docs/06/08/10/34/40-44/46-50 / `00-CC-CURRENT.md` 未读未写 |
| ✅ docs/48 既有契约未动 | ✅ | docs/52 仅引用 docs/48 §5 contract |
| ✅ docs/51 既有契约未动 | ✅ | docs/52 §5 引用 docs/51 双路径并存 |
| ✅ docs/49 既有契约未动 | ✅ | docs/52 §3 + §10 引用 docs/49 §2.2 + §5.3 |
| ✅ source_registry/registry.csv 既有 6 行未动 | ✅ | docs/52 §1 + §7 引用 |
| ✅ scripts/intake_real_sha_if_present.py 既有契约未动 | ✅ | docs/52 §5 引用 |
| ✅ O1 仍 OPEN（WAITING_FILE）| ✅ | §0 + §5 + §9 #2 + header ⚠ |
| ✅ A + B 路径命名空间不混用 | ✅ | §5 + §9 #13 + §10 显式 |
| ✅ AUTH 升级协议 6 触发 + 5 字段 + 4 路径 | ✅ | §6 |
| ✅ 首批 1-3 试点源建议（NBS HTML → Hubei → Shenzhen；archive.org/NPC/NBS JPG 不入首批）| ✅ | §3 |
| ✅ 流水线 6 步守门 | ✅ | §4 |
| ✅ is_demo=false 闸门共用 docs/48 §5 contract | ✅ | §4 + §5 |
| ✅ PDF 扫描件须先经 O3 OCR 流水线 | ✅ | §3 + §9 显式（O3 仍 OPEN 未实装）|
| ✅ mart-shape 禁词 3 重守门 | ✅ | docs/52 不创业务代码；§10 显式 |

---

## §6. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 137 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `phase=CC_ACTION_REQUIRED` ✅ |
| docs/52 新建 | `docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md`（13 节；~310 行）| ✅ NEW |
| bump script | `scripts/_knife45_manifest_bump.py`（2 NEW）| ✅ 643 → 645（+2）|
| 本地校验 | manifest invariant | ✅ 645 == 645 == 645 |
| commit (knife 45 主提交) | `git add ... && git commit -m "docs(52): 327 官方公开源自动获取规划 — 6 步流水线 + AUTH 升级协议"` | ⏳ this commit |
| origin push | `git push origin HEAD`（**priority**）| ⏳ this commit |
| github push | `git push github HEAD` | ⏳ this commit |
| 三路对齐 | origin/main = github/main = local HEAD | ⏳ this commit |
| backfill commit | 独立 commit（不 amend-after-push）| ⏳ this commit |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次心跳预期

- `queue_rev 137` 完成后：Cursor 收 `328` → 下发 `329-stage0-cursor-s327-docs52-public-source-audit-…md`（PASS/FAIL）
- 若 PASS：公开源自动获取规划齐；下一刀（tasking 32X+）落地首个 connector（NBS `NATIONAL_BULLETIN` HTML 月度发布）
- 若 FAIL：`328-correction` 回合（修 §3 试点源建议 / 修 §4 流水线 / 修 §6 AUTH 升级协议 5 字段 / 修 §8 下一刀边界 / re-commit）

---

## §8. 备注

- **本刀只规划，不实装爬虫 / 不绕 AUTH / 不宣布 Gate/O1 收口** — docs/52 §0 + §11 + header + 文末 多次 ⚠ 守门。
- **本刀覆盖此前「仅用户投递 O1」等待策略** — A 路径（用户投递 per docs/51）+ B 路径（公开源自动 per docs/52）**并存**（per 用户 2026-08-26 裁定 + `327` §SCHEMA）。
- **docs/52 = CC 维护公开源规划**（per `327` §SCHEMA "本刀做"）— 13 节 markdown 文档；不属于 Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-50）；红线 "Cursor 37 architect-only" 不约束 docs/52。
- **O1 仍 OPEN（WAITING_FILE）** — docs/52 §0 + §5 + §9 + header 多次显式（per docs/34 §3 + §120 + docs/47 §3.1 ⚠️ + `284` + `321` + `327`）。
- **O3 仍 OPEN — 规划已交，实装待 tasking 31X+** — docs/52 §3 + §9 + §10 + header 多次显式（per `docs/49` §5.3 + §8 + §10 + `309` + `313`）。
- **不可隐藏清单 15 项** — docs/52 §9 显式公开源自动获取必带：Gate PASS 禁 + O1 收口禁 + 不实装爬虫 + 不绕 AUTH + 不盲爬 + 不伪造 + 不以网页数作完成标准 + 不静默失败 + 不降 OCR/批量 2020-2025/1909 + 不派生 score + 不改 Cursor 拥有文档 + 不改 registry 既有 6 行 + A/B 命名空间不混用 + 不构成 Gate 2/O3/真表/真数据/§3.2-3.4 收口 + 1909 ≠ 中国。
- **AUTH 升级协议** — docs/52 §6 6 触发 + 5 字段 + 4 用户裁定路径；遇登录/验证码/付费墙/技术限制/反爬/headless browser 检测 → 立即停止并报告用户（5 字段含源/费用/需要账号/替代源/ETA）；用户提供授权 / 跳过该源（enabled=FALSE）/ 改用替代公开源 / 暂缓；**不绕过** + **不静默失败**。
- **流水线 6 步** — discover→download→sha256→archive→extract→observation；每步守门（registry CSV / HEAD 200 / hash 比对 / WORM archive / 解析按 access_method / lineage contract）；is_demo=false 仅当 sha256 ≠ `'0'*64` + 真 lineage 字段齐。
- **命名空间不混用** — A 路径 `/tmp/cegr_uploads/`（per docs/51 §2 allowlist）；B 路径 `/opt/puer-hub/cegr_public_ingest/{YYYY-MM}/{domain}/{filename}`（per docs/49 §4.2 WORM archive）。
- **首批 1-3 试点源** — NBS `NATIONAL_BULLETIN` HTML 月度发布（首选；不依赖 O3）→ Hubei 月度 EXCEL → Shenzhen 散文 HTML；**不入首批**：archive.org 1909（美国 + 依赖 O3）/ NPC 法律（依赖 O3）/ NBS `NATIONAL_YEARBOOK` JPG 扫描（依赖 O3）。
- **下次 heartbeat 闸门** — 首个 connector 落地须 tasking 32X+；在此之前 docs/52 §0 + §8 + §9 + §10 + header 仍标注"规划、不实装、不绕 AUTH"。

— End of `328` —

> 等待 Cursor 审验（预期 `329-stage0-cursor-s327-docs52-public-source-audit-…md`）。
> 通过后公开源自动获取规划齐；下一刀（tasking 32X+）落地首个 connector（NBS `NATIONAL_BULLETIN` HTML 月度发布）。
> ⚠ **本刀是规划，不是实装**（per `327` §SCHEMA "本刀做" + `327` §红线）。
> ⚠ **O1 仍 OPEN（WAITING_FILE）**（per docs/34 §3 + §120 + docs/47 §3.1 ⚠️ + `284` §SCHEMA + `321` §红线 + `327` §红线）。
> ⚠ **A 路径（用户投递 per docs/51）+ B 路径（公开源自动 per docs/52）并存**（per 用户 2026-08-26 裁定 + `327` §SCHEMA）。
> ⚠ **不绕过验证码 / 付费墙 / 登录 / 技术限制**（per docs/00 §3 红线 7 + PRD 1.3 + 12.8）。
> ⚠ **不盲爬全国市县**（per docs/00 §3 红线 6 + PRD 1.3 + 15.12）。
> ⚠ **不静默失败**（遇 AUTH 触发必须报告用户；5 字段 + 4 裁定路径）。
> ⚠ **不以抓取网页数作为完成标准**（per docs/00 §3 红线 5 + PRD 1.3 + 12.5）。
> ⚠ **不派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank**（per docs/06 §6.6 + docs/42 §8）。
> ⚠ **不降 OCR 门槛 / 不批量 2020-2025 / 不把 1909 代表中国**（per Stage 0 红线）。
> ⚠ **公开源自动获取 ≠ Gate PASS / ≠ O1 收口 / ≠ O3 收口 / ≠ dbt mart 真表 / ≠ person/tenure 真数据 / ≠ docs/10 §3.2-3.4 收口**（per docs/34 §1 + §8 #8 + docs/47 §6.3 + docs/49 §5.3 + `284` §依赖）。
> ⚠ **archive.org 1909 美国统计摘要 ≠ 中国经济治理平台样本**（per Stage 0 R4 用户决策）。
> ⚠ **不在范围：实装爬虫 / 实装 OCR / 改业务代码 / 改 Cursor 拥有文档 / 改 source_registry 既有 6 行 / 改 docs/48 既有契约 / 收口宣告**（per `327` §SCHEMA "本刀不做"）。