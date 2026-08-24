# 03 — 来源登记与连接器适配（Source Registry & Connector Spec）

> Stage 0 交付物 #03；对应 PRD 第 15 章第 3 项 + 第 9 章 + 第 12.8 节。
> 任何连接器实现前**必须先在此登记**（per PRD 9.1；防 R05 范围失控）。

## 1. 来源登记总表（`source_registry`）

来源登记表是所有抓取活动的"前置许可"。每条记录回答：
- **谁发的**：发布机构
- **在哪**：URL + 镜像
- **怎么拿**：访问方式 + 频率 + 反爬
- **什么周期**：覆盖时段 + 更新节奏
- **什么状态**：稳定性观察 + 失败处理
- **能不能用**：`enabled` 布尔 + 风险评估

## 2. 登记表 Schema（对应 `schema/01-core.sql` 中 `source_registry` 表）

| 列 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `domain` | TEXT | ✅ | 主域名（如 `stats.gov.cn`） |
| `organization` | TEXT | ✅ | 发布机构（如"国家统计局"） |
| `category` | TEXT | ✅ | 见下方类别枚举 |
| `primary_url` | TEXT | ✅ | 主入口 URL |
| `backup_urls` | TEXT[] | – | 备选入口（含 archive.org 快照） |
| `update_frequency` | TEXT | – | DAILY/MONTHLY/QUARTERLY/YEARLY/AD_HOC |
| `auth_note` | TEXT | – | 授权说明（公开/需授权/付费墙/…） |
| `access_method` | TEXT | – | API/HTML/EXCEL/PDF/OCR |
| `historical_coverage` | TEXT | – | 历史时段（如 "1995-2024"） |
| `stability_note` | TEXT | – | 稳定性观察（URL 漂移频率等） |
| `failure_handling` | TEXT | – | 失败处理策略 |
| `enabled` | BOOLEAN | ✅ | 启用开关 |

### 来源类别枚举（`category`）

| 值 | 说明 | 典型示例 |
|---|---|---|
| `NATIONAL_YEARBOOK` | 国家年度统计资料 | stats.gov.cn/sj/ndsj/ |
| `NATIONAL_BULLETIN` | 国家月度/季度发布 | stats.gov.cn/sj/zxfb/ |
| `PROVINCIAL_YEARBOOK` | 省级年度统计资料 | 各省统计局 |
| `PROVINCIAL_BULLETIN` | 省级月度/季度发布 | 各省统计局公报 |
| `MUNICIPAL_BULLETIN` | 地市级公报 | sz.gov.cn/zfgb/ |
| `MUNICIPAL_YEARBOOK` | 地市级年鉴 | 各市统计局 |
| `POLICY_CENTRAL` | 中央政策文件 | gov.cn/zhengce/ |
| `POLICY_LOCAL` | 地方政策文件 | 地方政府门户 |
| `BUDGET_CENTRAL` | 中央财政预算决算 | mof.gov.cn |
| `BUDGET_LOCAL` | 地方财政预算决算 | 各省财政厅 |
| `AUDIT_REPORT` | 审计报告 | audit.gov.cn |
| `PERSONNEL_ANNOUNCEMENT` | 人事任免公告 | 党建网/组织部 |
| `NEWS_LEAD` | 媒体线索 | 主流媒体 |

## 3. 来源等级矩阵（per PRD 3.2）

| 等级 | 定义 | 处理策略 |
|---|---|---|
| **S0** | 法定一手（统计公报、官方文件、审计报告） | 作为基线；冲突时优先 |
| **S1** | 国际组织/学术（IMF、OECD、CEIC、世界银行） | 校验用；可与 S0 并存 |
| **S2** | 商业数据库（Wind、Bloomberg、CEIC） | 校验用；记录来源 |
| **S3** | 主流媒体/公开报告 | 仅作背景，不作指标 |
| **S4** | 社交/自媒体 | 仅作研究线索 |

## 4. 已登记来源（来自 Stage 0 spikes）

### 4.1 S0-NBS-MONTHLY — 国家统计局月度发布

| 字段 | 值 |
|---|---|
| `domain` | `stats.gov.cn` |
| `organization` | 国家统计局 |
| `category` | `NATIONAL_BULLETIN` |
| `primary_url` | `https://www.stats.gov.cn/sj/zxfb/` |
| `backup_urls` | `["https://data.stats.gov.cn/"]`（API 403，目前作参考） |
| `update_frequency` | `MONTHLY`（每月 15 日左右；季度有增量） |
| `auth_note` | 公开；无需授权 |
| `access_method` | `HTML`（zxfb/） + `OCR`（ndsj/，扫描件） |
| `historical_coverage` | "zxfb/ 2010-至今；ndsj/ 2001-至今（多为 JPG 扫描）" |
| `stability_note` | URL 格式稳定；`ndsj/*.xls` 链接偶发失效；`data.stats.gov.cn` 有 WAF |
| `failure_handling` | 重试 3 次 → archive.org 备份 → 人工上传入口 |
| `enabled` | TRUE |
| `source_level` | S0 |

**Spike 1 验证产物**：
- 样本 URL：`https://www.stats.gov.cn/sj/zxfb/202608/t20260817_1965056.html`（1—7月份国民经济运行情况）
- 文件：`spikes/01-national-yearbook/sample.html`（388 KB）
- SHA-256：`dea13b8a4ff116ca91403b189cdd60705545b28200f9023c3d56e6db03f3939d`
- 解析：HTML 表格，**双行表头**（绝对值 vs 增速列），20 行（10 指标 × 2 期）
- 测试：20/20 通过

**关键发现（驱动 schema 决策）**：
1. **`ndsj/` 是 JPG 扫描件**，必须 OCR；**`zxfb/` 是 HTML 表格**，可程序化解析
2. **双行表头必须做列组映射**（absolute vs growth_rate）；单行解析器会全错
3. **`…`（省略号）= 抑制数据** → 写 NULL + confidence=0.0，**不静默丢弃**
4. **章节头行**（"分三大门类"）无数值 → 必须显式过滤
5. `data.stats.gov.cn` API 403 WAF → **HTML 抓取是当下可靠路径**

### 4.2 S0-SHENZHEN-BULLETIN — 深圳市政府公报

| 字段 | 值 |
|---|---|
| `domain` | `sz.gov.cn` |
| `organization` | 深圳市人民政府 |
| `category` | `MUNICIPAL_BULLETIN` |
| `primary_url` | `https://www.sz.gov.cn/zfgb/` |
| `backup_urls` | – |
| `update_frequency` | `YEARLY`（年度公报） |
| `auth_note` | 公开；无需授权 |
| `access_method` | `HTML`（散文形式 + 嵌入表格） |
| `historical_coverage` | "2020-至今" |
| `stability_note` | URL 格式稳定；按年份/gb 编号分目录 |
| `failure_handling` | 重试 3 次 → 截图人工上传 |
| `enabled` | TRUE |
| `source_level` | S0 |

**Spike 3 验证产物**：
- 样本 URL：`https://www.sz.gov.cn/zfgb/2025/gb1374/content/post_12212437.html`（深圳市 2024 年统计公报）
- 文件：`spikes/03-municipal-bulletin/sample.html`（61.4 KB）
- SHA-256：`d5e2c73196b43cecc8efa20e174d30bf78c382e21a1cda956f0637aeb9022d29`
- 解析：**散文 + 章节定位**（不是表格！），8 行（关键指标 + 子项）
- 测试：29/29 通过

**关键发现（驱动 schema 决策）**：
1. **公报是散文**，不是结构化表格；需要**章节定位** + 段落索引（`source_location.section_heading` + `paragraph_index` 必要）
2. **单位内嵌文中**（"全市地区生产总值 36801.85 亿元"），需命名实体识别
3. **`比较基础` 字段有时为 NULL**（如公报未注明），不能假设存在
4. **图表占位符穿插文中** → 解析时跳过 `class="chart"` 或 `<img>` 容器
5. **子项正则需要专门适配**（如"规模以上工业增加值同比增长 X%" 与"全部工业"是两个口径）
6. **`context_quote` 长度 5-200 字**是反幻觉的关键边界（过短 = 缺乏上下文，过长 = 容易截断）

### 4.3 S0-HUBEI-STATSBUREAU — 湖北省统计局月度发布

| 字段 | 值 |
|---|---|
| `domain` | `tjj.hubei.gov.cn` |
| `organization` | 湖北省统计局 |
| `category` | `PROVINCIAL_BULLETIN`（建议正式登记用此值；`PROVINCIAL_YEARBOOK` 用于年度合订本） |
| `primary_url` | `https://tjj.hubei.gov.cn/tjsj/sjkscx/tjyb/` |
| `backup_urls` | – |
| `update_frequency` | `MONTHLY` |
| `auth_note` | 公开；无需授权；直链 .xlsx 可下载 |
| `access_method` | `EXCEL`（单 sheet，无 chapter code） |
| `historical_coverage` | "月度统计报告至少近 1 年可下；年鉴合订本更早" |
| `stability_note` | 月度报告 URL 规律稳定；文件名带 P020… 时间戳 |
| `failure_handling` | curl 直下（**禁止 headless browser**，被 ERR_CONNECTION_RESET 拒绝） |
| `caveat_text` | "标题写'1-6月'实际是 Q2 单季；GDP/收入数据按季度披露" |
| `enabled` | TRUE |
| `source_level` | S0 |

**Spike 2 验证产物**：
- 样本 URL：`https://tjj.hubei.gov.cn/tjsj/sjkscx/tjyb/2026yb/202608/P020260804600767306528.xlsx`（2026 年 6 月月报）
- 文件：`spikes/02-provincial-yearbook/hubei_2026_06.xlsx`（11 KB）
- SHA-256：`c5cf5abeb4fdf97af52567f0640470d631bc9ac329dcc98f14e5d40bf6a5cac7`
- 解析：单 sheet xlsx，**列式单位**（unit 在 B 列），19 行（10+ 指标）
- 测试：30/30 通过（spike 02：湖北统计局 xlsx 月报；per-indicator 周期元数据）

**关键发现（驱动 schema 决策）**：

1. **单位布局差异**：省 xlsx 把单位放在 B 列与数据同列（**列式约定**），国家年鉴则单独 unit-row（**行式约定**）。**解析器必须按 source 适配**，不能用通用解析器。
2. **rate-only 行**：规模以上工业增加值行**只有增速**（如"5.2%"），无明确单位。Schema 必须允许 `observation.unit` 为 NULL（per doc 05 第 5 节缺失值处理），且 `indicator_definition.unit_canonical` 可为 "%"（增长率的标准单位）。
3. **子项前缀**：`#工业用电量`、`#民间投资` 用 `#` 前缀区分子项；指示器与父项映射走 `indicator_alias`。
4. **周期嵌入名称**：`上半年` 在 indicator 名称里，而国家年鉴用列头分周期。**严格归一化**：要求 source_data 进入前先做 alias 解。
5. **🚨 标题谎言**（**最严重发现**）：标题写"1-6月"实际是 **Q2 单季**数据，GDP/收入数据按季度披露。**必须**提取并登记脚注，否则会全错。Schema 加 `source_document.caveat_text` + `observation_quality_flag` 联动。
6. **无章节编号**：单 sheet，无 `E0201` 风格代码；定位必须从 URL/标题解析。

**操作注意**：
- 江苏/广东/四川省局对 headless browser 返回 ERR_CONNECTION_RESET → **必须 curl**直下，不能用 Selenium/Playwright
- 月度报告比年鉴合订本（zip）更易处理（小、单文件、不需解压）

### 4.4 扫描 PDF OCR — 双样本研究轨（非 Stage 0 验收项）

per `docs/15-stage0-p0p1-handoff-20260824.md` §4a U-3，spike 04 是研究追踪项，**不参与 Stage 0 Gate 0 判定**。来源登记保留两条独立样本，不互相冒充：

| 字段 | Legacy 数值表样本 | 陕西中文文本样本 |
|---|---|---|
| `domain` | `archive.org` | `wb.flk.npc.gov.cn` |
| `organization` | U.S. Bureau of Statistics | 全国人大常委会国家法律法规数据库 |
| `category` | `SCANNED_PDF_UPLOAD` | `SCANNED_PDF_RESEARCH` |
| `primary_url` | `https://archive.org/details/statisticalabst00unit` | `https://wb.flk.npc.gov.cn/dfxfg/PDF/d31411b562fc4226a7465f1c875afe67.pdf` |
| `auth_note` | 美国联邦政府作品；17 U.S.C. §105 | 公开、无需登录；法规正文依据《著作权法》第五条排除条款 |
| `access_method` | OCR（英文数值表） | OCR（四页灰度扫描 + 嵌入旧 OCR 文本层） |
| `source_level` | S3（非中国代表性） | S0（官方法定一手来源） |
| `purpose_note` | 保存 30×15 legacy 回归，不代表中国 | U-1 接受的中文 OCR 压力样本；U-3 非验收项 |

**陕西样本来源验证**：

- 文件：`spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf`
- SHA-256：`f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488`
- 1,007,943 bytes / 4 页 / `%PDF-1.4`
- Canon SC1011 + MP Navigator EX；每页 1259×1669 灰度 JPEG，200 DPI
- macOS `kMDItemWhereFroms` 记录上述全国人大官方直链；Chrome 下载来源元数据存在
- 用户通过官方直链下载并上传；CC 本机网络没有独立观测 HTTP 200，因此不伪造该证据，只验证 magic、结构、来源元数据、size 与 hash
- 嵌入层：3,230 个汉字；SHA-256 `cec93b67f8da16ecdd97b7e08ab2baf23995f2e61530afff3f1d6295dfdfc0bf`

**许可边界**：法规正文适用《中华人民共和国著作权法》第五条第一项的法律、法规及官方文件排除条款。该依据不扩张为对法规数据库界面、扫描版式或门户其他资产的“默认公共领域”声明；用途限定为内部 OCR 研究与可复现证据。

**陕西 OCR 评测（U-2 接受嵌入层作对照）**：

- 汉字一致率：**93.93%**（≥90%，达标）
- 全部非空白字符一致率：**90.05%**（同时披露，不替代主指标）
- needs_review：**1/4 页 = 25%**（≤30%，达标；定义为陕西研究轨页面 Han <90%，不等同 legacy 数值解析复核信号）
- numeric-cell accuracy：`null` / `not_applicable_non_tabular_source`，**不计 PASS**
- 研究轨结论：`MEETS_UNCHANGED_APPLICABLE_THRESHOLDS`
- Stage 0 effect：`none_per_U3_non_gating_research_sample`

嵌入层是旧 OCR，不是人工校对真值，存在 `预箅`、`收攴`、`本行畋区域` 等错误；新 OCR 正确输出 `预算`、`收支`、`本行政区域` 时仍会被参考层惩罚。报告数字因此是“与 U-2 接受参考层的一致率”，不是对人工真值的准确率估计。完整契约见 `spikes/04-scanned-pdf/README.md`、`provenance.json` 与 `data/extracts/04-scanned-pdf/shaanxi_text_eval_report.json`。

**Stage 1+ 实施要点（不在本轮启动）**：
- 上传入口必须包含出版方/授权来源声明与原始 DPI
- OCR 低置信度与页面级字符阈值必须进入复核队列
- 不批量抓取、不绕过 TLS/登录/付费墙、不使用商业 OCR
- 若未来要把法规样本用于验收，须另行建立人工校对真值并经用户重新裁定；本轮不得静默替换 U-2 参考

## 5. 来源 → 指标 → 页面 反向追溯链

每个连接器必须能回答：**这个来源服务于哪个指标、哪个研究问题、哪个页面？**

```
source_registry(NBS-MONTHLY)
    ↓ 提供
indicator_definition(GRP, GDP_growth, fixed_asset_investment, retail_sales, ...)
    ↓ 出现在
页面: 国家级总览 / 历史序列 / 周期对比
    ↓ 服务于
research_question(2026 年宏观经济趋势分析)
```

如果写连接器时无法反向追溯到任何研究问题，**不要写**（per PRD 12.5 R05）。

## 6. 连接器开发规范

### 6.1 三步法（每源必走）

1. **登记**：先填本表 + 提交 PR（即使只填了部分字段）
2. **取样**：下载一个具体样本到 `spikes/<id>-<name>/sample.html`
3. **验证**：写 `extract.py` + `test_extract.py` + `README.md`，必须 ≥1 测试通过

### 6.2 Spike 准入门槛（不通过则不上线）

| 维度 | 门槛 |
|---|---|
| **样本可达** | ≥1 样本下载成功 + SHA-256 已存 |
| **解析可重** | extract.py 在干净环境跑通，输出 deterministic |
| **测试覆盖** | ≥10 个 pytest 用例，覆盖：单位校验 / 合计校验 / 同比反算 / 缺失值 / 章节定位 |
| **失败可控** | 至少描述 1 类已知失败 + 兜底策略 |
| **追溯完整** | 每条 observation 有 source_id + source_location_id |

### 6.3 失败模式登记

每个来源必须记录已知失败模式，例如：

| 来源 | 已知失败 | 兜底 |
|---|---|---|
| stats.gov.cn zxfb | 偶发 503 | 指数退避 + archive.org |
| stats.gov.cn ndsj | xls 链接失效 | 备份 URL + 人工上传 |
| stats.gov.cn data | 403 WAF | 仅用 zxfb 路径 |
| 地方统计局 | 反爬（高频） | 1 req/s + robots.txt |

## 7. 来源使用守则（per PRD 9.1）

- ✅ **优先 S0 → S1 → S2 → S3 → S4**
- ✅ **冲突时并存不覆盖**，写 `source_disagreement`
- ✅ **每个 observation 必须有 source_id + source_location_id**
- ✅ **源文件 SHA-256 入库**（per schema/01-core.sql 中 `source_document.file_hash_sha256` 强制）
- ❌ **不绕过验证码/付费墙**（PRD 12.8 红线）
- ❌ **不抓取 robots.txt 禁止路径**
- ❌ **不缓存超过 30 天的 raw** 在应用服务器（用对象存储）

## 8. 与其他文档的关系

- 数据模型：`schema/01-core.sql` 中 `source_registry` / `source_document` / `source_location` / `ingestion_run` 四表
- 风险登记：`docs/09-risk-register.md` R08（授权稳定性）、R12（URL 漂移）
- 验收测试：`docs/10-acceptance-tests.md` 2.1-2.6（数据层）
- MVP 计划：`docs/08-mvp-plan.md` Stage 1 任务清单

## 9. I-05 来源等级治理 (Stage 0 Gate 0 R4)

来源等级分为两层：
- **`declared_source_level`**：上传者声明的等级（informational）
- **`source_level`**：平台 effective 等级（驱动业务决策）

### 9.1 强制约束

`source_document` 增加 CHECK 约束：
```sql
CHECK (source_level <> 'S0' OR verification_status = 'VERIFIED')
```

语义：
- **S0** = 法定一手（统计公报、官方文件） → 必须经平台核验（`verification_status = 'VERIFIED'`）
- **S1/S2/S3/S4** → 不强制核验（按层级递减可信度，UNVERIFIED 是合法状态）
- 上传者声明 S0 但未核验 → DB 拒绝（CheckViolation）

### 9.2 核验状态机

```
UNVERIFIED ──┬─→ PENDING ──→ VERIFIED   (平台通过)
             └─→ REJECTED                (平台驳回)
PENDING ────────→ UNVERIFIED             (回退重审)
VERIFIED ───────→ PENDING                (复核)
```

每次状态迁移通过 `AFTER UPDATE OF verification_status` 触发器自动写入
`source_document_verification_event`，记录：from/to 状态、from/to declared & effective 等级、
`verifier_id`（通过 `SET LOCAL app.verifier_id = '...'`）、`evidence_note`、`decided_at`。

### 9.3 审计表 schema (`source_document_verification_event`)

| 列 | 类型 | 说明 |
|---|---|---|
| `id` | UUID PK | 事件唯一标识 |
| `source_document_id` | UUID FK | 关联 source_document（ON DELETE RESTRICT） |
| `from_status` / `to_status` | enum | 迁移前后状态 |
| `from_declared_level` / `from_effective_level` | enum | 迁移前 declared/effective |
| `to_declared_level` / `to_effective_level` | enum | 迁移后 declared/effective |
| `verifier_id` | TEXT NOT NULL | 核验人/角色（来自 `app.verifier_id` GUC） |
| `evidence_note` | TEXT | 核验依据（链接/SHA/公告/制度依据） |
| `decided_at` | TIMESTAMPTZ | 决策时间（默认 NOW()） |

**审计表本身 append-only**：`source_document_verification_event_immutable()` trigger
拦截 UPDATE 与 DELETE（per source_document 同等不变量）。

### 9.4 测试覆盖

`tests/test_source_governance.py` 21 个用例覆盖：
1. S0 + UNVERIFIED/PENDING/REJECTED  → CheckViolation
2. S0 + VERIFIED  → ok
3. S1-S4 + UNVERIFIED  → ok
4. declared ≠ effective  → ok（两列独立）
5. UNVERIFIED → PENDING → VERIFIED  → 2 条审计事件
6. 审计表 UPDATE/DELETE 被拒
7. source_document 原有不可变性不被破坏（title/source_level 仍不可 UPDATE）
8. caveat_text 仍可 UPDATE（且不触发审计事件）

### 9.5 实际登记更新 (per R4 用户决策)

- `archive.org` 1909 美国统计摘要：`source_level` 由 S0 → **S3**；`declared_source_level` 记录为 S0
  - 原因：用户决策 #1 — 1909 美国样本不能作为中国经济治理平台的代表性扫描样本
  - 用途：仅作为 OCR 管线压力样本（非代表性）
- 所有中文登记（stats.gov.cn × 2 / tjj.hubei.gov.cn / sz.gov.cn / wb.flk.npc.gov.cn）保持 S0
- `wb.flk.npc.gov.cn` 陕西法规 PDF 仅用于 U-1/U-2 中文 OCR 研究轨；S0 表示官方来源等级，不把该非表格样本升级为 Stage 0 验收项

**重要澄清**：`source_registry/registry.csv` 仅有 `source_level` + `declared_source_level` 列，
**没有** `verification_status` 列。`verification_status` 属于 schema 中的 `source_document` 表
（per-document 平台核验状态），不在登记表层；登记表仅描述"原始来源等级 + uploader 声称等级"，
核验状态必须进入系统生成 source_document 记录后才会有意义。本节原先写"中文登记保持 S0 + VERIFIED"
的措辞不准确；中文四源 S0 仅表示来源等级主张，对应 source_document 行在入库时由 I-05 CHECK
约束强制 `verification_status='VERIFIED'`，但这与登记表本身无直接字段对应。