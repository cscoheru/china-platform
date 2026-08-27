# 52 — 官方公开源自动获取规划（AUTH 升级协议）

> ⚠ **本文是规划（per `327` §SCHEMA "本刀做"）** — 不实装全量爬虫；不绕验证码/付费墙/登录；不伪造；不盲爬全国市县。
> ⚠ **O1 仍 OPEN**（per docs/34 §3 + §120 + docs/47 §3.1 ⚠️ + `284`；状态语义对齐 per `484` + `486`）— 主路径 = 本规划 B 路（公开源自动获取六步流水线，试点轴 `NATIONAL_BULLETIN` per `480`/`482`）；`WAITING_FILE` 仅保留为 intake 出口码 / mart 真 SHA 未入仓的技术状态语义，**非「等用户投喂才可继续」**；docs/51 A 路（用户投递）仍可用但非唯一路径。
> ⚠ **不绕过验证码 / 付费墙 / 登录 / 技术限制**（per docs/00 红线 7 + PRD 1.3 + 12.8）— 遇阻**停止并报告用户**，**不静默失败**。
> ⚠ **不盲爬全国市县**（per docs/00 红线 6 + PRD 1.3 + 15.12）— 仅 `source_registry` 登记的稳定公开源 + 开放 API + 无登录公开页面稳定 URL。
> ⚠ **不把 1909 代表中国 / 不批量 2020-2025 / 不降 OCR 门槛**（per Stage 0 红线）。

> 起草：CC · 2026-08-26 · queue_rev 137
> 前置：`326` docs/45 docs/51 登记 PASS；用户 2026-08-26 裁定：**不再等用户投喂**；产品两目标=①自动检索官方公开数据 ②结构化呈现；PRD §9（来源登记 / 原始不可变 / 哈希）+ docs/00 §3 红线 7
> 用户裁定：**D**；覆盖此前「仅用户投递 O1」等待策略
> 任务性质：**官方公开源自动获取规划**（per `327` §SCHEMA "本刀做"）— markdown-only；不实装全量爬虫；不绕过；不宣布 Gate/O1 PASS
> 链到：`source_registry/registry.csv`（6 行 S0-S3 公开源）+ `docs/48-stage2-real-sha-intake-handbook-20260826.md`（intake 操作手册）+ `docs/51-stage2-o1-drop-checklist-20260826.md`（用户投递清单）+ `docs/00-project-assessment.md`（红线 7）
> 链到（续 · per `506`）：下一探测轴 = **live-candidate 探测**登记（connector 模式 `--live --confirm-live`，per docs/53 §5 第 25 项；该刀只登记未运行；遇 AUTH 阻停报告不绕过）

---

## §0. 一句话总览

按 `source_registry/registry.csv` 登记的**公开**下载包 / 开放 API / 无登录公开页面稳定 URL → 走 **`discover → download → sha256 → archive → extract → observation`** 流水线 → 仅当 SHA-256 入仓 + lineage 字段齐才允许 `is_demo=false`；**遇登录 / 验证码 / 付费墙 / 技术限制 → 停止并报告用户（不绕过）**，等用户裁定授权后再继续。

> **用户投递（per docs/51）仍可用**；本规划是 O1 自动获取路径补充，**用户投递不再是唯一路径**（per `327` §SCHEMA "本刀做" + 用户 2026-08-26 裁定）。preview 公网预览互链弧文档链已完整收口（第 16–20 项，per `472`/`474`/`476`；docs/50 §4.4 intro 收据链尾 `474`），下一试点轴维持 `NATIONAL_BULLETIN`（stats.gov.cn HTML）（per `478` 登记于 docs/45 文首刷新行 + §1 + §6.2 + §7）。docs/53 §5 第 21 项互链已落（per `480`）：O1 B 路下一试点轴 = `stats.gov.cn` / `NATIONAL_BULLETIN` HTML 月度发布已在 docs/53 §5 blockquote 登记（O1 仍 OPEN）。

---

## §1. 允许范围（3 类公开源）

| # | 类型 | 例 | 来源 |
|---|---|---|---|
| 1 | **source_registry 登记的公开下载包** | `source_registry/registry.csv` 中 `auth_note` 字段含"公开；无需登录/无需授权"且 `enabled=TRUE` 的源 | `source_registry/registry.csv`（当前 6 行 S0-S3）|
| 2 | **开放 API**（无 OAuth / 无 API Key）| 国家统计局 `data.stats.gov.cn` 公开 API（无需 token）| docs/00 §3 + 官方源开放 API 列表 |
| 3 | **无登录公开页面稳定 URL**（HTML/Excel/PDF 直链，不触发登录墙）| 湖北省统计局月度报告 .xlsx 直链（per registry.csv "curl 直下"）| registry.csv `auth_note="公开；无需授权；直链 .xlsx 可下载"` |

**当前 source_registry 6 行**（per `source_registry/registry.csv`）：

| domain | organization | category | auth | access_method |
|---|---|---|---|---|
| `stats.gov.cn` | 国家统计局 | `NATIONAL_YEARBOOK` | 公开；无需授权 | OCR（JPG 扫描）|
| `stats.gov.cn` | 国家统计局 | `NATIONAL_BULLETIN` | 公开；无需授权 | HTML |
| `tjj.hubei.gov.cn` | 湖北省统计局 | `PROVINCIAL_BULLETIN` | 公开；无需授权；直链 .xlsx | EXCEL |
| `sz.gov.cn` | 深圳市人民政府 | `MUNICIPAL_BULLETIN` | 公开；无需授权 | HTML |
| `archive.org` | United States Census Bureau | `SCANNED_PDF_UPLOAD` | 公开；public domain | OCR |
| `wb.flk.npc.gov.cn` | 全国人大常委会国家法律法规数据库 | `SCANNED_PDF_RESEARCH` | 公开；无需登录 | OCR（嵌入旧 OCR 层）|

> ⚠ **archive.org 美国统计摘要 1909** — 非代表性中文样本；仅作 OCR 压力测试（per Stage 0 R4 用户决策）；**不**代表中国经济治理平台（per docs/00 §3 + Stage 0 红线）。

---

## §2. 禁止事项（per docs/00 §3 + `327` §SCHEMA "本刀不做" + PRD 1.3 + 12.8 + 15.12）

| # | 禁止 | 来源 |
|---|---|---|
| 1 | ❌ **绕验证码 / 付费墙 / 登录 / 技术限制** | docs/00 §3 红线 7 + PRD 1.3 + 12.8 |
| 2 | ❌ **盲爬全国市县** | docs/00 §3 红线 6 + PRD 1.3 + 15.12 |
| 3 | ❌ **伪造样本 / 伪造 SHA-256 / 伪造 lineage 字段** | docs/00 §3 + docs/48 §8 + docs/06 §6.6 |
| 4 | ❌ **以抓取网页数作为完成标准** | docs/00 §3 红线 5 + PRD 1.3 + 12.5 |
| 5 | ❌ **headless browser 绕过反爬** | registry.csv Hubei 备注"**禁止 headless browser**，被 ERR_CONNECTION_RESET 拒绝" |
| 6 | ❌ **静默失败不告知用户**（遇授权源不报告） | `327` §SCHEMA "禁止" + AUTH 升级协议 |
| 7 | ❌ **未登记的源**（registry.csv `enabled=FALSE` 的源 / 未登记的新源） | docs/00 §3 + source_registry 主路径 |
| 8 | ❌ **降 OCR 门槛** | docs/00 §3 + docs/49 §2.2 |
| 9 | ❌ **批量 2020-2025** | Stage 0 红线 |
| 10 | ❌ **派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank** | docs/06 §6.6 + docs/42 §8 |

---

## §3. 首批 1-3 试点源建议（per `327` §SCHEMA "本刀做"）

按 `source_registry/registry.csv` 当前 6 行公开源 + 试点策略（**先 1 个最小可行源 → 验证流水线 → 再扩**），建议：

| 优先级 | domain | category | 试点理由 |
|---|---|---|---|
| 1 | `stats.gov.cn` | `NATIONAL_BULLETIN`（HTML 月度发布）| URL 格式稳定；HTML 可直接 `curl`；OCR 不需要；可端到端验证 discover→download→sha256→archive→extract→observation 流水线 |
| 2 | `tjj.hubei.gov.cn` | `PROVINCIAL_BULLETIN`（EXCEL 月度报告）| `.xlsx` 直链无需登录；不需要 headless browser；可验证 EXCEL extract 路径 |
| 3 | `sz.gov.cn` | `MUNICIPAL_BULLETIN`（HTML 散文 + 嵌入表格）| 散文 HTML + 嵌入表格（验证 extract 边界）；市级公开源 |

> ⚠ **`archive.org` / `wb.flk.npc.gov.cn`** — **不进入首批试点**（OCR 路径依赖 O3 引擎；O3 仍 OPEN，未实装；per docs/49 §5.3 + `309` + tasking 31X+）。待 O3 实装后再评估。
> ⚠ **`stats.gov.cn` `NATIONAL_YEARBOOK`** — JPG 扫描；同样依赖 O3 OCR 流水线；**不进入首批试点**。

---

## §4. 流水线（per `327` §SCHEMA "本刀做"）

```
discover → download → sha256 → archive → extract → observation
   ↓         ↓         ↓        ↓         ↓           ↓
 registry   HEAD 200  hash     WORM     csv/xlsx    lineage
 + LLM    + GET       file     archive  → observation  contract
 judge       <size>              store                 + is_demo=false
            + Content-Type                              闸门
```

| 步 | 动作 | 守门 | 出错处理 |
|---|---|---|---|
| **1. discover** | 读 `source_registry/registry.csv` → 筛选 `enabled=TRUE` + `auth_note` 含"公开" + 在试点清单内 | registry.csv 主路径；schema `source_registry` PK | registry 漏源 → 报告用户 + 暂不实装 |
| **2. download** | `curl -L` HEAD 200 + GET → 校验 `Content-Type` + `Content-Length` 与 registry.csv `file_hash_sha256` `file_size_bytes` 一致 | `requests`/`curl` 不触发 headless browser；rate limit（per-source）| 重试 3 次 → 报告用户（不绕过 ERR_CONNECTION_RESET）|
| **3. sha256** | 对下载文件计算 `sha256`；与 registry.csv `file_hash_sha256` 比对 | hashlib.sha256 | hash 不匹配 → 不入仓；报告用户（可能源站变更）|
| **4. archive** | 写入 WORM（write-once）archive（不可变；保留原始字节）| per docs/49 §4.2 不可变 + SHA 入 lineage | WORM 失败 → 停止流水线 |
| **5. extract** | 按 `access_method` 解析：HTML → 表格 / Excel → sheets / OCR（O3 仍 OPEN，未实装；PDF 跳过）| pandas / lxml / openpyxl（仅开源包；不调未授权 cloud OCR API）| extract 失败 → 报告用户 + 留源待修 |
| **6. observation** | 写入 `observation` 表 + lineage 字段齐：`is_demo=false` 仅当 hash ≠ `'0'*64` + `source_file_sha256` 真 SHA + `source_file_path` 真实路径 + `source_agency` 与 registry.csv `organization` 一致 + `intake_ts` ISO-8601 + `intake_status='O1_AUTO_INTAKED'` | docs/48 §5 contract 守门 | contract 违反 → 报告 CC + 不入仓 |

> ⚠ **`is_demo=false` 闸门**（per docs/48 §5 + docs/06 §6.6 + docs/47 §3.1 ⚠️）— 仅当 sha256 ≠ `'0'*64`（即非 `spikes/*/data/` 占位文件）+ 文件 mtime 90 天内 + 来源与 registry.csv 一致 → 才允许 flip `is_demo=false`。否则保持 `is_demo=true`（演示占位）。

---

## §5. 与 docs/48 intake / docs/51 O1 drop 关系（per `327` §SCHEMA "本刀做"）

| 路径 | 文档 | 触发方 | 现状 |
|---|---|---|---|
| **A. 用户投递**（per docs/51）| `docs/51-stage2-o1-drop-checklist-20260826.md` + `scripts/intake_real_sha_if_present.py` | 用户主动 `--confirm-o1=PATH` | ✅ 已交（回执 `322` + `325`）|
| **B. 公开源自动获取**（per docs/52）| 本文档 + 未来 `scripts/auto_ingest_public_source.py`（tasking 32X+ OPEN）| 流水线自动；registry.csv 主路径 | ⚠️ 规划已交（回执 `328`）；实装待 tasking 32X+ |

**两条路径都允许** — 用户投递仍可用，**不再是唯一路径**（per `327` §SCHEMA "本刀做" + 用户 2026-08-26 裁定）。

**is_demo=false 闸门共用**（per docs/48 §5）— 两条路径产出的 observation 行共用同一 contract 守门：`source_file_sha256` ≠ `'0'*64` + `is_demo=false` + `intake_status` ∈ {`'O1_INTAKED'`, `'O1_AUTO_INTAKED'`} + `source_agency` 与登记一致。

> ⚠ **A 路径与 B 路径的 source_file_path 命名空间**（per `327` §SCHEMA）— 建议：A 路径走 `/tmp/cegr_uploads/`（per docs/51 §2 allowlist）；B 路径走 `/opt/puer-hub/cegr_public_ingest/{YYYY-MM}/{domain}/{filename}`（per docs/49 §4.2 WORM archive）。两条路径**不混用**（避免 hash 冲突）。

---

## §6. AUTH 升级协议（per `327` §SCHEMA "本刀做" + 用户 2026-08-26 裁定 + docs/00 §3 红线 7）

> ⚠ **遇登录 / 验证码 / 付费墙 / 技术限制 → 立即停止并报告用户**（per docs/00 §3 红线 7 + PRD 1.3 + 12.8 + `327` §红线）。

### 6.1 触发条件

| 现象 | 触发 AUTH 升级 | 来源 |
|---|---|---|
| HTTP 302 → 登录页 | ✅ | docs/00 §3 红线 7 |
| HTTP 403 / 401 / 429（连续 3 次重试后）| ✅ | docs/00 §3 红线 7 |
| 验证码 / CAPTCHA 弹出 | ✅ | docs/00 §3 红线 7 + PRD 1.3 |
| 付费墙 / 订阅提示 | ✅ | docs/00 §3 红线 7 |
| 反爬检测（ERR_CONNECTION_RESET / TLS 异常 / Cloudflare 5s 盾）| ✅ | registry.csv Hubei 备注 + docs/00 §3 红线 7 |
| headless browser 检测 | ✅ | registry.csv Hubei 备注 |

### 6.2 报告内容（必须包含 5 字段）

| 字段 | 例 |
|---|---|
| **源 domain / category / URL** | `xxx.com` / `PROVINCIAL_BULLETIN` / `https://...` |
| **费用估计（若可知）** | "免费但需注册" / "￥299/年订阅" / "政府内部账号" |
| **需要什么账号/订阅** | "单位邮箱注册" / "支付宝订阅" / "省级统计局内部账号" |
| **可替代公开源（registry.csv 已有）** | "建议改用 `tjj.hubei.gov.cn` 已登记公开源" |
| **ETA（用户提供授权后）** | "用户提供账号后 ~30 分钟可继续" |

### 6.3 用户裁定路径

| 路径 | 处理 |
|---|---|
| **用户提供授权**（账号/订阅/凭证）| 升级 `source_registry/registry.csv` `auth_note` 字段；下次心跳流水线自动重试 |
| **用户裁定跳过该源** | 标记 `enabled=FALSE`；下次心跳流水线跳过；不静默失败 |
| **用户裁定改用替代公开源** | discover 阶段重路由到 `registry.csv` 替代项 |
| **用户裁定暂缓** | 源保持 `enabled=FALSE`；等下次用户裁定 |

> ⚠ **不绕过** — 即使用户提供账号/订阅，仍需 `source_registry/registry.csv` 显式 `enabled=TRUE` + `auth_note` 更新 + lineage 字段含 `source_agency` + `intake_ts`。**不**未经登记就调任何付费 API / 登录后端点。
> ⚠ **不静默失败** — 任何 AUTH 触发必须写入 `reviews/` 报告（如 `329-stage2-public-source-auth-blocked-report-…md`）；不可仅写日志而不通知用户。

---

## §7. 验收清单（per `327` §SCHEMA "本刀做"）

| # | 验收项 | 状态 |
|---|---|---|
| 1 | docs/52 已交（10+ 节；含 AUTH 升级协议）| ⏳ 回执 `328` 后 ✅ |
| 2 | source_registry/registry.csv 6 行登记未动 | ✅ docs/52 仅引用；不改 registry |
| 3 | 流水线 6 步守门（discover / download / sha256 / archive / extract / observation）| ⏳ 规划已交；实装待 tasking 32X+ |
| 4 | is_demo=false 闸门共用 docs/48 §5 contract | ✅ docs/52 §4 + §5 引用 |
| 5 | A 路径（用户投递 per docs/51）+ B 路径（公开源自动 per docs/52）并存 | ✅ docs/52 §5 双路径说明 |
| 6 | AUTH 升级协议（5 触发 + 5 报告字段 + 4 用户裁定路径）| ✅ docs/52 §6 |
| 7 | 不实装全量爬虫 | ✅ docs/52 §0 + §8 + header |
| 8 | 不绕验证码 / 付费墙 / 登录 | ✅ docs/52 §2 + §6 + §10 |
| 9 | 不盲爬全国市县（per docs/00 §3 红线 6）| ✅ docs/52 §2 + §1 + §3 |
| 10 | 不伪造 / 不静默失败 | ✅ docs/52 §2 + §6.3 |
| 11 | 与 docs/48 / docs/51 / docs/49 / docs/00 引用齐 | ✅ docs/52 全文 |

---

## §8. 下一刀边界（per `327` §SCHEMA "本刀做" + `327` §NOW）

> **首个 connector 落地**（tasking **32X+** OPEN）— 不在本刀范围。

### 8.1 下一刀待办（tasking 32X+ 范畴）

| # | 项 | 范围 |
|---|---|---|
| 1 | 写 `scripts/auto_ingest_public_source.py`（registry.csv 主路径 + 6 步流水线 + is_demo=false 闸门）| spike_helper |
| 2 | 写 `tests/test_auto_ingest_public_source_s52.py`（12+ pytest cases）| schema_negative_test |
| 3 | 首批 1-3 试点源（per docs/52 §3）首个 connector | NBS `NATIONAL_BULLETIN`（HTML 月度发布）|
| 4 | WORM archive 落 `data/public_archives/{YYYY-MM}/{domain}/{filename}`（per docs/49 §4.2）| documentation + schema |
| 5 | lineage 字段扩展：`intake_status='O1_AUTO_INTAKED'`（区别于 docs/51 `'O1_INTAKED'`）| schema_migration_ddl |
| 6 | A 路径 + B 路径命名空间不混用（per docs/52 §5）| schema_migration_ddl |
| 7 | AUTH 升级报告模板（`329-stage2-public-source-auth-blocked-report-…md`）| documentation |

### 8.2 实装后验收（首个 connector 落地后）

- `pytest tests/test_auto_ingest_public_source_s52.py` ≥ 12/12 PASS
- NBS `NATIONAL_BULLETIN` HTML 月度发布端到端 `discover → download → sha256 → archive → extract → observation` rc=0（O1_AUTO_INTAKED）
- lineage 字段齐（per docs/48 §5 contract）：`source_file_sha256` 真 SHA + `is_demo=false` + `intake_ts` + `intake_status` + `source_agency` 与 registry.csv `organization` 一致
- pack invariant（per docs/47 §6.3）

---

## §9. 不可隐藏清单（per docs/00 §3 + docs/34 §120 + `327` §SCHEMA "本刀不做"）

| # | 项 | 必带位置 |
|---|---|---|
| 1 | 公开源自动获取**不是 Gate PASS 宣告** | §0 + §10 + header ⚠ |
| 2 | 公开源自动获取**不构成 O1 收口**（**O1 仍 OPEN**；主路径 = 本规划 B 路，`WAITING_FILE` = intake 出口码 / mart 真 SHA 未入仓语义、非「等用户投喂才可继续」per `484`/`486`/`488`；A/B 两条路径都需执行）| §0 + §5 + §10 + header ⚠ |
| 3 | 公开源自动获取**不实装全量爬虫**（per `327` §SCHEMA "本刀不做"）| §0 + §8 + header ⚠ |
| 4 | **不绕验证码 / 付费墙 / 登录 / 技术限制** | §2 + §6 + §10 + header ⚠ |
| 5 | **不盲爬全国市县**（per docs/00 §3 红线 6）| §1 + §2 + §3 + §10 + header ⚠ |
| 6 | **不伪造 / 不伪造 SHA / 不伪造 lineage 字段** | §2 + §4 + §10 + header ⚠ |
| 7 | **不以抓取网页数作为完成标准**（per docs/00 §3 红线 5）| §2 + §7 + §10 + header ⚠ |
| 8 | **不静默失败**（遇 AUTH 触发必须报告用户）| §2 + §6.3 + §10 + header ⚠ |
| 9 | **不降 OCR 门槛 / 不批量 2020-2025 / 不把 1909 代表中国** | §10 + header ⚠ |
| 10 | **不派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank / DSH** | §2 + §10 + header ⚠ |
| 11 | **不改 Cursor 拥有架构文档**（docs/06/08/10/34/40-44/46-50 / `00-CC-CURRENT.md` / `gate_thresholds.json`）| §10 + header ⚠ |
| 12 | **不改 `source_registry/registry.csv` 既有 6 行**（per docs/52 §1 + §7）| §1 + §7 + §10 + header ⚠ |
| 13 | **A 路径（用户投递 per docs/51）+ B 路径（公开源自动 per docs/52）命名空间不混用** | §5 + §10 + header ⚠ |
| 14 | **公开源自动获取不构成 Gate 2 PASS / O3 收口 / person/tenure 真数据 / dbt mart 真表 / docs/10 §3.2-3.4 收口** | §0 + §10 + header ⚠ |
| 15 | **archive.org 1909 美国统计摘要 ≠ 中国经济治理平台样本** | §1 + §3 + §10 + header ⚠ |

---

## §10. 红线（per docs/00 §3 + PRD 1.3 + 12.8 + 15.12 + `327` §SCHEMA "本刀不做" + docs/34 §1/§8 + docs/49 §2.2 + docs/06 §6.6 + docs/42 §8）

- ❌ 不宣布 Gate 1 / Gate 2 PASS（per docs/34 §1 + §8 #8）
- ❌ 不擅自 O1 收口（A 路径 docs/51 + B 路径 docs/52 两条路径都需执行；**O1 仍 OPEN**——主路径 = B 路，`WAITING_FILE` = intake 出口码 / 真 SHA 未入仓技术状态、非「等用户投喂才可继续」per `488` 措辞清理）
- ❌ 不擅自 O3 收口（per `docs/49` §5.3；tasking 31X+ OPEN）
- ❌ 不派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank / DSH / 实时数据
- ❌ 不做"地区得分" / 不做"地区排名" / 不做官员能力总分（per docs/00 §3 红线 1 + PRD 1.3 + 6.6）
- ❌ 不批量爬政策研究 / 财政预决算 / 官员履历
- ❌ **不绕过验证码、付费墙或网站技术限制**（per docs/00 §3 红线 7 + PRD 1.3 + 12.8）
- ❌ **不盲爬全国市县**（per docs/00 §3 红线 6 + PRD 1.3 + 15.12）
- ❌ **不以抓取网页数作为完成标准**（per docs/00 §3 红线 5 + PRD 1.3 + 12.5）
- ❌ 不调用未授权 cloud OCR API（默认离线；须 `--enable-cloud-ocr=PROVIDER` 显式 flag + 用户裁定）
- ❌ 不登录绕过 / 不 symlink / 不 path traversal / 不伪造 SHA / 不伪造 lineage 字段
- ❌ 不降 OCR 门槛
- ❌ 启用 pgvector / RLS / partition（Stage 2 边界）
- ❌ 改 `gate_thresholds.json`
- ❌ 不碰 `00-CC-CURRENT.md`（Cursor 拥有）
- ❌ 不擅自 `--force` / `--force-with-lease`
- ❌ 不在聊天复述 Cursor 长文 / 不索要 PAT
- ❌ 不静默失败（遇 AUTH 触发必须报告用户；不绕过）
- ❌ 不改 `source_registry/registry.csv` 既有 6 行（docs/52 仅引用）

---

## §11. 不在范围（per `327` §SCHEMA "本刀不做" + docs/49 §3）

- ❌ 实装全量爬虫（仅规划 + 首批 1-3 试点源建议）
- ❌ 实装 OCR 引擎（O3 路径；per `docs/49` §5.3；tasking 31X+）
- ❌ 写 `scripts/auto_ingest_public_source.py`（首个 connector 落地待 tasking 32X+）
- ❌ 改业务代码（schema / migration / dbt / pytest / TS / frontend / smoke-check）
- ❌ 改 Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-50 / `00-CC-CURRENT.md` / `gate_thresholds.json`）
- ❌ 改 `source_registry/registry.csv` 既有 6 行（仅 docs/52 引用）
- ❌ 改 `docs/48` 既有内容（docs/52 引用 docs/48 §5 contract）
- ❌ 改 `docs/51` 既有内容（docs/52 §5 双路径并存说明）
- ❌ Gate 1 / Gate 2 / O1 / O3 收口宣告
- ❌ 不公告 user 投递 → 自动化路径切换（per `327` §SCHEMA "本刀做" + 用户裁定；A 路径 + B 路径并存）

---

## §12. 下次心跳预期

- `queue_rev 137` 完成后：Cursor 收 `328` → 下发 `329-stage0-cursor-s327-docs52-public-source-audit-…md`（PASS/FAIL）
- 若 PASS：公开源自动获取规划齐；下一刀（tasking 32X+）落地首个 connector（NBS `NATIONAL_BULLETIN` HTML 月度发布）
- 若 FAIL：`328-correction` 回合（修 §3 试点源建议 / 修 §4 流水线 / 修 §6 AUTH 升级协议 5 字段 / 修 §8 下一刀边界 / re-commit）
- 仍 OPEN（不受本刀影响）：O1 真实 SHA 收口（A 路径用户投递 + B 路径首个 connector 落地）；O3 OCR 引擎实装；docs/10 §3.2-3.4 xfail stub；dbt mart 真表；person/tenure 真数据

---

— End of `docs/52` —

> ⚠ **本文是规划，不是实装**（per `327` §SCHEMA "本刀做" + `327` §红线）。
> ⚠ **O1 仍 OPEN**（状态语义对齐 per `484`/`486`/`488`：`WAITING_FILE` 仅保留为 intake 出口码 / mart 真 SHA 未入仓的技术状态语义，非「等用户投喂才可继续」）— 主路径 = B 路径（公开源自动 per docs/52）；A 路径（用户投递 per docs/51）仍可用但非唯一，两路**并存**（per `327` §SCHEMA + 用户 2026-08-26 裁定）。
> ⚠ **不绕过验证码 / 付费墙 / 登录 / 技术限制**（per docs/00 §3 红线 7 + PRD 1.3 + 12.8）。
> ⚠ **不盲爬全国市县**（per docs/00 §3 红线 6 + PRD 1.3 + 15.12）。
> ⚠ **不静默失败**（遇 AUTH 触发必须报告用户；不绕过）。
> ⚠ **不伪造 / 不伪造 SHA / 不伪造 lineage 字段**（per docs/00 §3 + docs/48 §8 + docs/06 §6.6）。
> ⚠ **不以抓取网页数作为完成标准**（per docs/00 §3 红线 5 + PRD 1.3 + 12.5）。
> ⚠ **公开源自动获取 ≠ Gate PASS / ≠ O1 收口 / ≠ O3 收口 / ≠ dbt mart 真表 / ≠ person/tenure 真数据 / ≠ docs/10 §3.2-3.4 收口**。
> ⚠ **archive.org 1909 美国统计摘要 ≠ 中国经济治理平台样本**（per Stage 0 R4 用户决策）。
> ⚠ **不在范围：实装爬虫 / 实装 OCR / 改业务代码 / 改 Cursor 拥有文档 / 改 source_registry 既有 6 行 / 收口宣告**（per `327` §SCHEMA "本刀不做"）。