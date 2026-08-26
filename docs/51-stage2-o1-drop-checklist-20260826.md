# 51 — O1 投递一页清单（给用户）

> ⚠ **本文不是 O1 收口宣告** — 只是给用户的**单页投递清单**（per `321` §SCHEMA "本刀做"）。
> ⚠ **O1 仍 OPEN（WAITING_FILE）** — 用户 2026-08-26 确认本机/仓库**未持有**江苏真实 SHA-locked 样本（per `284` §SCHEMA + `319`）。
> ⚠ **不伪造** — 禁止假造江苏政府文件 SHA / 拿 mock fixture 冒充真实样本 / 拿 cursor-demo 替代物冒充（per `321` §红线 + docs/06 §6.6）。
> ⚠ **不爬网** — 不 HTTP 抓政府站 / 不调用第三方 API / 不登录绕过（per `321` §红线 + docs/48 §2 + `docs/49` §2.2）。
> ⚠ **不擅自 O1 收口** — 收口须用户主动 `--confirm-o1=PATH`（per docs/48 §4.3 + `321` §红线）。

> 起草：CC · 2026-08-26 · queue_rev 133
> 前置：`320` docs/45 PASS；`docs/48` intake；用户裁定"**尽快真数据**"（per `320`/`321`）
> 用户裁定：**D**；O1 仍 OPEN；**不伪造 / 不爬网**
> 任务性质：**O1 投递一页清单**（per `321` §SCHEMA "本刀做"）— markdown-only；不接真数据；**不**宣称已收口
> 链到：`docs/48-stage2-real-sha-intake-handbook-20260826.md`（intake 操作手册）+ `scripts/intake_real_sha_if_present.py`

---

## §0. 一句话总览

把**您线下持有的江苏政府文件**（CSV / Excel / PDF 扫描件 / 政府工作报告等）复制到白名单路径 → 跑一次 `intake_real_sha_if_present.py` → 看到 `CANDIDATE_FOUND`（rc=2）后再用 `--confirm-o1=PATH` 显式确认 → 看到 `O1_INTAKED`（rc=0）才视为 O1 收口。

---

## §1. 投递前检查（pre-conditions）

| # | 项 | 必须 | 来源 |
|---|---|---|---|
| 1 | 您线下**合法持有**江苏政府文件（非爬网、非 OCR 绕过、非第三方 API 抓取）| ✅ | docs/48 §2 + `321` §红线 |
| 2 | 文件**≥ 1 KiB**（不是空文件、不是 1 行 stub）| ✅ | docs/48 §4.2 |
| 3 | 文件**不包含** `NOT a forged` / `placeholder bytes` 字面字符串（避免控制流 fixture 被误判）| ✅ | docs/48 §4.1 + §4.2 |
| 4 | 文件**mtime 在最近 90 天内**（防止过期缓存）| ⚠️ 推荐 | docs/48 §4.2 |
| 5 | 文件**不是**以 `fixture` / `test_fixture` / `test_` / `_test.` 命名 | ✅ | docs/48 §4.1 |

> ⚠ **如果您只有 PDF 扫描件**：当前 O1 intake 仅接受**数字可解析**文件（CSV / Excel / JSON）；**PDF 扫描件**须先经 O3 OCR 流水线（per `docs/49`，**O3 仍 OPEN，未实装**；tasking 31X+）→ 暂不能直接投递。本清单只覆盖 O1（数字可解析）路径。

---

## §2. 把文件放到白名单（3 个 allowlist 前缀之一）

| 白名单路径 | 用途 | 来源 |
|---|---|---|
| `/tmp/cegr_uploads/` | **首选**：管理员 upload 落盘目录 | `scripts/compute_file_sha.py` `ALLOWED_PREFIXES` |
| `/private/tmp/cegr_uploads/` | macOS `/tmp` → `/private/tmp` symlink 解析后等价路径 | 同上 |
| `data/seed_archives/` | ⚠️ **不推荐**（混入开发 fixture；除非您刻意要测试 fixture 分支）| docs/48 §2 |

**操作**（任选其一）：

```bash
# 方式 A：直接 cp（最简单）
cp /path/to/your/jiangsu_2022_gdp.csv /tmp/cegr_uploads/

# 方式 B：通过 admin upload 端点（推荐；保留上传审计 trail）
#   → 走 admin upload UI（per S1.13 已交）；落盘到 /tmp/cegr_uploads/
```

> ⚠ **其他路径（如 `/Users/yourname/Downloads/`）**不会被 intake 脚本接受；rc=2 + "path not in allowlist" 提示（per docs/48 §2 + `compute_file_sha.py` `ALLOWED_PREFIXES`）。

---

## §3. 单步 intake（探测模式）

```bash
# 探测模式（不收口；只报 status）
python3 scripts/intake_real_sha_if_present.py
```

**预期 4 种退出码**（per docs/48 §3 + §4.3）：

| rc | 含义 | 操作 |
|---|---|---|
| **0** | **WAITING_FILE**（白名单内**无合法 O1 样本**）| 路径 1：再次确认您文件确实落在白名单内；路径 2：检查文件命名（避免 fixture 命名）；路径 3：检查文件大小（≥ 1 KiB）|
| **2** | **CANDIDATE_FOUND**（已发现候选；**用户裁定闸门 OPEN**）| **进入 §4 显式确认**（不擅自收口；须您 `--confirm-o1=PATH`）|
| **3** | **CONTRACT_VIOLATION**（候选违反契约：SHA=全0 / is_demo 仍 true / lineage 字段缺失）| 联系 CC 排查；**不擅自修正**（避免掩盖 bug）|
| **4** | **内部错误**（subprocess / JSON 解析失败）| 联系 CC 排查 |

> ⚠ **rc=0 (WAITING_FILE) ≠ O1 收口** — 仅表示"白名单内无合法 O1 样本"；这是诚实路径（per docs/48 §3 + `321` §红线）。

---

## §4. 显式确认（仅在 rc=2 CANDIDATE_FOUND 后）

```bash
# 显式确认某候选 = O1（必须 PATH 参数；非交互）
python3 scripts/intake_real_sha_if_present.py --confirm-o1=/tmp/cegr_uploads/jiangsu_2022_gdp.csv
```

**预期**：

| rc | 含义 | 后续 |
|---|---|---|
| **0** | **O1_INTAKED**（O1 收口；lineage `source_file_sha256` ≠ `'0'*64` + `is_demo=false` + `intake_status='O1_INTAKED'`）| 进入 §5 验证预览；**O1 首次收口**（per docs/48 §4.3 + §5 contract 守门）|
| **2** | 路径不在白名单 / 候选不存在 | 检查 PATH 是否正确 |
| **3** | contract violation | 联系 CC 排查 |
| **4** | 内部错误 | 联系 CC 排查 |

> ⚠ **`--confirm-o1=PATH` 不可省略 PATH** — argparse 自动拒绝空值（per docs/48 §4.3 + §7 pytest 守门）。
> ⚠ **pytest 自动 `--confirm-o1` 是禁止的**（per docs/48 §7 红线）；必须**用户主动**显式 flag 才视为收口。

---

## §5. 收口后预览（O1 首次收口后能看到什么）

| 视图 | 路径 | 预期变化 |
|---|---|---|
| 5 省 lite 页面 | `localhost:3000/provinces/jiangsu` | "演示" 标识消失；lineage `source_file_sha256` 显示真实 SHA（≠ `'0'*64`）|
| 10 地市 lite 页面 | `localhost:3000/cities/nanjing` 等 | "演示" 标识消失；`buildMartRelatedPersons` 仍为 demo（person/tenure 真数据待 S2.1-lite PASS，per `303`）|
| CityPageMart 管道 | `NEXT_PUBLIC_USE_MART_FIXTURE=1` | evidence_chain + seven_dim_overview 行从 demo 翻转为真数据 |
| 预览路径 | `NEXT_PUBLIC_USE_MART_FIXTURE=1` | **O1 收口后**预览仍是 demo 演示管道（除非额外 wire 真数据迁移刀；S2.7-b-full 真数据迁移刀 tasking 26X+ OPEN）|

> ⚠ **O1 收口仅是 lineage 标志事件** — `lineage.source_file_sha256` ≠ `'0'*64` + `lineage.is_demo=false` + `lineage.intake_status='O1_INTAKED'`。**前端 UI 切换真数据须 S2.7-b-full 真数据迁移刀**（tasking 26X+ OPEN，per docs/47 §6.3 + `284` §依赖）。

---

## §6. 不可隐藏清单（per docs/34 §120 + `321` §红线）

| # | 项 | 状态 |
|---|---|---|
| 1 | O1 仍 OPEN（WAITING_FILE）直到用户主动 `--confirm-o1=PATH` | ✅ 必带 |
| 2 | **禁止** 拿 mock fixture 冒充真实样本 | ✅ 必带 |
| 3 | **禁止** 假造江苏政府文件 SHA | ✅ 必带 |
| 4 | **禁止** HTTP 爬源 / 登录绕过 / 第三方 API / 未授权 cloud OCR / symlink / 伪造 | ✅ 必带 |
| 5 | **禁止** `--confirm-o1` 由 pytest / 自动化脚本擅自触发；必须**用户主动** | ✅ 必带 |
| 6 | rc=0 (WAITING_FILE) **不等于** O1 收口 | ✅ 必带 |
| 7 | O1 收口**不构成** Gate 2 PASS（per docs/34 §1 + §8 #8）| ✅ 必带 |
| 8 | O1 收口**不构成** person/tenure 真数据迁移（仍 demo 占位，待 S2.1-lite PASS）| ✅ 必带 |
| 9 | O1 收口**不构成** O3 OCR 收口（per `docs/49` §5.3）| ✅ 必带 |
| 10 | O1 收口**不构成** dbt mart 真表（演示级 WHERE FALSE 骨架已交 `288`；真表待 S2.7-b-full）| ✅ 必带 |
| 11 | O1 收口**不构成** docs/10 §3.2-3.4 收口（xfail stub；Stage 3 收口）| ✅ 必带 |

---

## §7. 红线（per `321` §红线 + docs/34 §1/§8 + docs/48 §8 + docs/06 §6.6 + docs/49 §2.2）

- ❌ 不宣布 Gate 1 / Gate 2 PASS（per docs/34 §1 + §8 #8）
- ❌ 不伪造 SHA / 不伪造样本内容 / 不拿 mock fixture 冒充（per docs/06 §6.6 + docs/48 §8）
- ❌ 不爬网（HTTP / URL 选项不在 CLI 注册；argparse 自动拒绝）
- ❌ 不擅自 O1 CLOSED（除非用户用 `--confirm-o1=PATH` 显式确认）
- ❌ 不擅自把 fixture 收口为真 O1
- ❌ 不调用未授权 cloud OCR API（默认离线；须 `--enable-cloud-ocr=PROVIDER` 显式 flag + 用户裁定）
- ❌ 不登录绕过 / 不 symlink / 不 path traversal
- ❌ 不派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank / DSH / 实时数据
- ❌ 不改 `gate_thresholds.json`
- ❌ 不碰 `00-CC-CURRENT.md`（Cursor 拥有）
- ❌ 不擅自 `--force` / `--force-with-lease`
- ❌ 不在聊天复述 Cursor 长文 / 不索要 PAT

---

## §8. 不在范围（per `321` §SCHEMA "本刀不做" + docs/49 §8）

- ❌ 接收真数据（用户未投递前，本刀不接收；O1 仍 OPEN）
- ❌ 实装 OCR 引擎（O3 路径；per `docs/49` §5.3；tasking 31X+）
- ❌ 改业务代码（schema / migration / dbt / pytest / TS / frontend / smoke-check）
- ❌ 改 Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-50 / `00-CC-CURRENT.md` / `gate_thresholds.json`）
- ❌ 改 `docs/48` 既有内容（仅 docs/51 引用 docs/48 §2/§3/§4/§5；不改 docs/48 既有契约）
- ❌ Gate 1 / Gate 2 / O1 / O3 收口宣告

---

## §9. 下次心跳预期

- 用户投递真数据后：跑 `python3 scripts/intake_real_sha_if_present.py` → rc=2 (CANDIDATE_FOUND) → 用户 `--confirm-o1=PATH` → rc=0 (O1_INTAKED)
- `intake_real_sha_if_present.py` 自动写入 receipt-like log（per docs/48 §6）；下次 heartbeat 时 `cc_gate_watch.sh` 检测到 `intake_status='O1_INTAKED'` → Cursor 下发 `O1_intake_log_audit_…md` → docs/45 §3 O1 详细 flip `WAITING_FILE` → `O1_INTAKED`
- 仍 OPEN 项（O3 / docs/10 §3.2-3.4 / dbt mart 真表 / person/tenure 真数据）不受 O1 收口影响

---

— End of `docs/51` —

> ⚠ **本文不是 O1 收口宣告**（per `321` §SCHEMA "本刀做" + `321` §红线）。
> ⚠ **O1 仍 OPEN（WAITING_FILE）**（per docs/34 §3 + §120 + `284` §SCHEMA + `321` §红线）。
> ⚠ **不伪造**（per `321` §红线 + docs/06 §6.6）。
> ⚠ **不爬网**（per `321` §红线 + docs/48 §2 + docs/49 §2.2）。
> ⚠ **不擅自 O1 收口**（per docs/48 §4.3 + `321` §红线）。
> ⚠ **rc=0 (WAITING_FILE) ≠ O1 收口**（per docs/48 §3）。
> ⚠ **`--confirm-o1=PATH` 必须由用户主动显式触发**（per docs/48 §4.3 + §7）。
> ⚠ **O1 收口不构成 Gate 2 / O3 / dbt mart 真表 / person/tenure 真数据 收口**（per docs/34 §1 + §8 #8 + docs/47 §6.3 + docs/49 §5.3 + `284` §依赖）。
> ⚠ **PDF 扫描件须先经 O3 OCR 流水线**（per docs/49 §5.3 + §10 Q4；O3 仍 OPEN，未实装）。
> ⚠ **docs/51 = CC 维护投递清单**（per `321` §SCHEMA "本刀做"）；不属于 Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-50）。
> ⚠ **不在范围：实装 OCR / 改业务代码 / 改 Cursor 拥有文档 / 收口宣告**（per `321` §SCHEMA "本刀不做"）。