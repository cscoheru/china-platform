# 09 — 风险登记（Risk Register）

> Stage 0 交付物 #09；对应 PRD 第 15 章 + 第 12 章。
> 风险来源：PRD 12.1-12.10 共 10 个风险 + Stage 0 实操中新增的运维风险。

## 风险矩阵

- **等级**：🔴 高 / 🟡 中 / 🟢 低
- **状态**：⬜ 未处理 / 🟡 规划中 / ✅ 已缓解 / ❌ 阻塞

## R01 — 统计口径变化

| 项 | 内容 |
|---|---|
| 来源 | PRD 12.1 |
| 等级 | 🔴 高 |
| 描述 | GDP 核算修订（经济普查后调整）、行业分类变化（GB/T 4754 修订）、固投口径变化（2011 年、2017 年）、常住人口口径（2010 年、2020 年普查） |
| 影响 | 历史数据不可比；同一指标名不同值；下游分析错误 |
| 措施 | 1) 指标定义版本化（`indicator_methodology_version` 表）；2) 保存数据 vintage（同时存"原始发布值"和"最新修订值"）；3) UI 明确 vintage；4) 跨年比较时强制显示口径差异 |
| 状态 | ✅ 已在 doc 04/05 中体现 |
| 责任人 | ETL/数据工程 |
| 检测方法 | 同比反算异常 + 跨来源一致性 |

## R02 — 行政区划变化

| 项 | 内容 |
|---|---|
| 来源 | PRD 12.2 |
| 等级 | 🔴 高 |
| 描述 | 撤县设区（如 2011 年重庆扩容）、撤地设市（如 1983 年）、合并拆分（如 2011 年巢湖拆分）、更名（如 2010 年襄樊→襄阳） |
| 影响 | 时间序列断裂；"重庆吞了四川"式数字错觉；任何跨期比较都可能错误 |
| 措施 | 1) `boundary_change_event` 表记录每次变化；2) `observation` 必带 `geo_version_id` 引用；3) 跨期比较 API 强制返回可比性标记；4) UI 显示"按当年边界 / 按当前边界"切换 |
| 状态 | ✅ 已在 doc 04 中体现 |
| 责任人 | 数据工程 + 标准化层 |
| 检测方法 | 测试集含已知的行政区划变化 case（如 2011 年巢湖） |

## R03 — 地方数据缺失和不一致

| 项 | 内容 |
|---|---|
| 来源 | PRD 12.3 |
| 等级 | 🔴 高 |
| 描述 | 地市、区县年鉴不完整；同一指标在不同来源数值不同（口径差异）；某些年份完全缺失；公报与年鉴数据打架 |
| 影响 | 用户对数据可信度失去信心；研究结论偏差 |
| 措施 | 1) 来源优先级明确（S0 > S1 > S2 > S3 > S4）；2) 冲突时**并存**而非覆盖，写 `source_disagreement` 记录；3) 缺失就是缺失，写 NULL + 缺失原因；4) 人工裁决走 `research_note` 记录 |
| 状态 | ⬜ 设计中（Stage 1 实施） |
| 责任人 | 数据工程 + 研究员 |
| 检测方法 | 同一指标跨源比对差异 > 阈值告警 |

## R04 — PDF 和 OCR 错误

| 项 | 内容 |
|---|---|
| 来源 | PRD 12.4 |
| 等级 | 🔴 高 |
| 描述 | 小数点错位（如 12.3 → 123）；单位错（如"亿元"误为"万元"）；负号缺失；表头错位；扫描倾斜/噪点；古字/异体字 |
| 影响 | 数值错误 → 后续分析错误；版本化追溯困难 |
| 措施 | 1) 版面坐标 + 单元格定位（`source_location`）；2) 规则校验（单位一致性、合计校验、同比反算）；3) 双引擎比对（tesseract + paddleocr）；4) OCR 置信度 <0.7 进人工复核队列；5) 低置信度不入正式数据表，写 `observation_quality_flag` |
| 状态 | 🟡 部分验证（OCR 管线代码就绪；spike 04 在真实扫描 PDF 上 BLOCKED — 缺公开样本；JPG 表已跑通真值对照） |
| 责任人 | ETL + 数据工程 |
| 检测方法 | 自动规则 + 抽样人工核对 |

## R05 — 全量爬取导致范围失控

| 项 | 内容 |
|---|---|
| 来源 | PRD 12.5 |
| 等级 | 🟡 中 |
| 描述 | 写了大量采集器，每个都跑通，但**回答不了研究问题**；或某源超规模（数千页年报）拖垮工程 |
| 影响 | 项目变成"数据仓库"而非"研究平台"；时间成本失控 |
| 措施 | 1) **来源连接器服务于已定义的页面/任务**（doc 04 中指标 → 页面反向追溯）；2) 每批新源先写"研究问题清单"，再写连接器；3) Gate 2 评审每个连接器的业务价值；4) 限制单源连接器代码量 |
| 状态 | ✅ 已在 doc 00 + doc 08 流程中体现 |
| 责任人 | 项目负责人 + CC |
| 检测方法 | 每 PR 评审问"这个连接器服务于哪个研究问题" |

## R06 — 官员和经济结果的错误归因

| 项 | 内容 |
|---|---|
| 来源 | PRD 12.6 |
| 等级 | 🔴 高 |
| 描述 | 把经济增长归功/归过于单一官员；忽略任期重叠、全国周期、上级政策、外部冲击；晋升/调任误读为绩效证据 |
| 影响 | 平台被批"主观评判"；损害可信度；潜在法律/声誉风险 |
| 措施 | 1) 不建立首期总分（doc 06）；2) 强制六段证据链（CONDITION→OUTCOME_RISK）；3) 任期归因约束（doc 06 第 5 节）；4) 任何归因结论必须有 ≥2 类证据 + 标注替代解释；5) 红线写进 doc 06 顶部 |
| 状态 | ✅ 已在 doc 06 完整体现 |
| 责任人 | 研究方法 + AI |
| 检测方法 | 自动检查：每条 governance 观察是否走完六段；每条 AI 输出是否标注 INFERENCE/JUDGMENT |

## R07 — 活动数量冒充执行效能

| 项 | 内容 |
|---|---|
| 来源 | PRD 12.7 |
| 等级 | 🟡 中 |
| 描述 | 把发文数、会议数、签约数、宣传数直接当绩效证据；"活动多 = 干得好" |
| 影响 | 平台被利用或被批；用户研究走偏 |
| 措施 | 1) 承诺—预算—实施—完成—结果链路（doc 06 第 2 节）；2) `project_event` 表区分 announce / sign / start / produce / reach_capacity 五态；3) 无法验证交付时**只标记为活动**，不进 outcome；4) UI 明确"活动 vs 产出 vs 结果" 三层 |
| 状态 | ✅ 已在 doc 06 + doc 04 中体现 |
| 责任人 | 研究方法 |
| 检测方法 | 任何 governance 观察如果只有活动证据，自动标记"产出未验证" |

## R08 — 数据授权和网站稳定性

| 项 | 内容 |
|---|---|
| 来源 | PRD 12.8 |
| 等级 | 🟡 中 |
| 描述 | 年鉴版权（部分需授权）；下载限速；验证码；链接失效（政府网站 URL 漂移）；反爬（CDN/JS 渲染）；**扫描 PDF 无公开免费源**（Spike 4 验证） |
| 影响 | 抓取中断；合规风险；扫描件无法入库 |
| 措施 | 1) 优先官方公开下载入口；2) 低频率访问（每源 ≤1 req/s 或按 robots.txt）；3) 原始版本全归档；4) **提供人工上传入口**（`/admin/upload`；扫描 PDF 强制入口）；5) 不绕过验证码/付费墙；6) URL 健康监控 + 自动告警；7) **scanned PDF 走管理员手动获取 → 强制授权声明 → OCR 入库** |
| 状态 | 🟡 部分验证（OCR 管线代码就绪；上传入口未实施；scanned PDF 真实样本 BLOCKED） |
| 责任人 | 数据工程 |
| 检测方法 | URL 健康探针 + ingest_run 失败率告警 + 上传 DPI 自检 |

## R09 — AI 幻觉和引用错配

| 项 | 内容 |
|---|---|
| 来源 | PRD 12.9 |
| 等级 | 🔴 高 |
| 描述 | 模型把不同年份/地区/同名官员混合；编造 source_id；数值与原文不一致；强行归因 |
| 影响 | 平台可信度崩塌；用户被误导 |
| 措施 | 1) 实体 ID 强制（person/geo/indicator 都用稳定 ID）；2) 结构化工具（不让 LLM 自由生成 SQL）；3) 证据引用门禁（任何输出必有 source_id）；4) 自动一致性测试（输入问题 → 查询 → 校验值与 DB 一致）；5) 人工审阅队列（高风险问题必经人）；6) Agent 进程只读 DB 角色 |
| 状态 | ⬜ Stage 4 启用 DSH 前必须做 |
| 责任人 | AI + 数据工程 |
| 检测方法 | doc 10 测试集中幻觉检测 |

## R10 — 研究立场和确认偏差

| 项 | 内容 |
|---|---|
| 来源 | PRD 12.10 |
| 等级 | 🟡 中 |
| 描述 | 先有结论再选数据；只记录支持某种判断的资料；研究方法选择偏倚 |
| 影响 | 平台被指"立场化"；用户怀疑客观性 |
| 措施 | 1) **预先登记**研究问题 + 比较组 + 模型（`research_question`/`comparison_group`/`model_specification` 三表强制）；2) 保留反例和相反证据（`claim_evidence_link` 表存正反证据）；3) 事实/计算/推断/判断分层（doc 04）；4) 每条结论必须标注证据强度；5) Gate 3 评审检查"是否有反例被忽略" |
| 状态 | ⬜ 设计中（Stage 2 末落地） |
| 责任人 | 研究方法 |
| 检测方法 | 每条 governance 观察必须有 ≥1 个反例或替代解释 |

## R11 — Stage 0 新增：OCR 工具链不可用（运维风险）

| 项 | 内容 |
|---|---|
| 来源 | Stage 0 Spike 4 风险 |
| 等级 | 🟡 中 |
| 描述 | tesseract + chi_sim 包未安装；paddleocr 体积大；pdf2image 依赖 poppler；OCR 准确率对老旧扫描件低 |
| 影响 | 历史扫描 PDF 无法入库 |
| 措施 | 1) 容器内预装 tesseract-ocr + tesseract-ocr-chi-sim；2) paddleocr 作为可选服务（按需启用）；3) 老旧扫描件走人工 OCR 上传入口；4) Spike 4 验证当前工具链 |
| 状态 | 🟡 部分验证（spike 04 真实扫描 PDF BLOCKED；JPG OCR 已跑通；容器化未完成） |
| 责任人 | 数据工程 |
| 检测方法 | OCR 测试集（含已知正确文本的扫描件） |

## R12 — Stage 0 新增：国家统计局 URL 漂移（运维风险）

| 项 | 内容 |
|---|---|
| 来源 | Stage 0 实操经验 |
| 等级 | 🟡 中 |
| 描述 | 政府网站改版/栏目调整导致历史 URL 失效；Excel 链接过期；jsessionid 漂移 |
| 影响 | 抓取持续失败；无降级 |
| 措施 | 1) URL 健康监控（每源每日 GET HEAD 探测）；2) source_registry 中维护多备选 URL；3) 历史 raw 已归档，重抓失败可手动提供新 URL；4) 失败 ≥3 次自动告警 |
| 状态 | ⬜ Stage 1 实施 |
| 责任人 | 数据工程 |
| 检测方法 | URL 监控 + ingest_run 失败率 |

## R13 — Stage 0 返工新增：真实样本 BLOCKED 即意味着 Gate 0 不通过

| 项 | 内容 |
|---|---|
| 来源 | Gate 0 返工指令（reviews/stage0-gate0-rework-2026-08-23） |
| 等级 | 🔴 高 |
| 描述 | 用户指令明确："若真实扫描 PDF 等外部条件仍未满足，如实回复 BLOCKED，不得用合成样本替代验收"；spike 04 真实扫描 PDF 在 Stage 0 截止前未能取得 |
| 影响 | Gate 0 不能以"已通过"提交；spike 04 真实样本必须保留为 BLOCKED 状态 |
| 措施 | 1) spike 04 标注明确 BLOCKED，不打 ✅；2) tests 跳过该 BLOCKED 项（pytest.skip）；3) Gate 0 总结保留"待用户授权"事项；4) 不允许 LLM 生成合成 PDF 替代；5) 用户书面授权后才进入 Gate 1 |
| 状态 | ❌ BLOCKED（spike 04） |
| 责任人 | 数据工程 + 用户决策 |
| 检测方法 | Gate 0 复验清单（02-Stage0-复验清单.md）逐项打勾 |

## R14 — Stage 0 返工新增：测试结果永真断言风险

| 项 | 内容 |
|---|---|
| 来源 | Gate 0 返工指令（reviews/stage0-gate0-rework-2026-08-23） |
| 等级 | 🔴 高 |
| 描述 | 首轮测试曾出现 `len(...) >= 0` 永真断言——空集合也"通过"；返工已替换为 `len(...) > 0` 和更严条件 |
| 影响 | 静默失败；Gate 误判 |
| 措施 | 1) 全部测试要求至少一条非永真断言（量化、对值、长度 > 0、状态字段）；2) 跳过 BLOCKED 用 `pytest.skip()`；3) pytest 默认无 cache；4) 新增 spike 测试 review checklist |
| 状态 | ✅ 已在返工中修正（spike 02/04 + test_schema_negative.py 13 项 + spike 00 双跑） |
| 责任人 | QA |
| 检测方法 | `tests/*/test_*.py` 逐文件评审 |

## R15 — Stage 0 返工新增：Schema 执行路径硬编码

| 项 | 内容 |
|---|---|
| 来源 | Gate 0 返工指令 |
| 等级 | 🟡 中 |
| 描述 | 首轮 spike 02 含 `/Users/kjonekong/...` 绝对路径硬编码；返工已改为 `Path(__file__).parent / "hubei_2026_06.xlsx"` |
| 影响 | 跨机器/容器部署失败 |
| 措施 | 1) 所有路径用 `__file__` 相对解析；2) Schema 用 `SETUP_DSN` 环境变量；3) 默认值只用于本地开发；4) CI 必须用环境变量注入 |
| 状态 | ✅ 已修正（spike 02/04/00 + test_schema_negative.py） |
| 责任人 | ETL + 数据工程 |
| 检测方法 | `grep -rn "/Users/kjonekong" spikes/ tests/` 应为零结果 |

## R16 — Stage 0 返工新增：UTF-8 OCR 与 OCR 子进程参数兼容性

| 项 | 内容 |
|---|---|
| 来源 | Gate 0 返工 spike 00 OCR 实操 |
| 等级 | 🟡 中 |
| 描述 | `text=True` + UTF-8 中文输出乱码；`--psm 6` 作为单参数传递被部分 tesseract 版本忽略；返工改用 `capture_output=True` + `.decode("utf-8", errors="replace")` + 显式 `-l` 和 `--psm` 分开参数 |
| 影响 | OCR 中文丢失；省份识别失败 |
| 措施 | 1) 统一 UTF-8 显式解码；2) 子进程参数必须用 list 形式，每个 flag 单独成项；3) tsv 模式 + 位置映射做省份识别；4) OCR 单元测试断言中文字符不丢失 |
| 状态 | ✅ spike 00 已修复；spike 04 待真实 PDF 验证 |
| 责任人 | ETL |
| 检测方法 | OCR 单元测试断言"湖北"等中文省份名出现在 TSV 中 |

## 风险汇总

| ID | 等级 | 状态 | 来源 |
|---|---|---|---|
| R01 统计口径 | 🔴 高 | ✅ | PRD 12.1 |
| R02 行政区划 | 🔴 高 | ✅ | PRD 12.2 |
| R03 地方缺失 | 🔴 高 | ⬜ | PRD 12.3 |
| R04 OCR 错误 | 🔴 高 | 🟡 部分验证 | PRD 12.4 |
| R05 范围失控 | 🟡 中 | ✅ | PRD 12.5 |
| R06 错误归因 | 🔴 高 | ✅ | PRD 12.6 |
| R07 活动冒充 | 🟡 中 | ✅ | PRD 12.7 |
| R08 授权稳定性 | 🟡 中 | 🟡 部分验证 | PRD 12.8 |
| R09 AI 幻觉 | 🔴 高 | ⬜ | PRD 12.9 |
| R10 确认偏差 | 🟡 中 | ⬜ | PRD 12.10 |
| R11 OCR 工具链 | 🟡 中 | 🟡 部分验证 | Stage 0 |
| R12 URL 漂移 | 🟡 中 | ⬜ | Stage 0 |
| R13 真实样本 BLOCKED | 🔴 高 | ❌ BLOCKED | 返工指令 |
| R14 永真断言 | 🔴 高 | ✅ | 返工指令 |
| R15 路径硬编码 | 🟡 中 | ✅ | 返工指令 |
| R16 OCR 子进程 | 🟡 中 | ✅ | 返工指令 |
| R17 natural key status | 🟡 中 | ✅ R3 闭环 | R3 返工 |
| R18 测试纯净性 | 🟡 中 | ✅ R3 闭环 | R3 返工 |
| R19 builder 自校验 | 🟡 中 | ✅ R3 闭环 | R3 返工 |
| R20 spike 04 样本偏差 | 🔴 高 | ❌ BLOCKED | R3 返工 |
| R21 spike 00/02/03 partial | 🔴 高 | ✅ 已闭环 | R3 返工 |

**统计（截至 R3 2026-08-23）**：
- 🔴 高 10 个 / 🟡 中 11 个 / 🟢 低 0 个
- ✅ 已闭环 12 个（R01/R02/R05/R06/R07/R14/R15/R16/R17/R18/R19/R21）
- 🟡 部分验证 3 个（R04/R08/R11）
- ⬜ 待 Stage 1 落地 4 个（R03, R09, R10, R12）
- ❌ BLOCKED 2 个（R13 真实样本 + R20 spike 04 偏差）

## R17 — Stage 0 R3 返工新增：status 不在 observation 自然键 → 触发器强制 append-only revision

| 项 | 内容 |
|---|---|
| 来源 | Gate 0 返工指令 R3-F（reviews/stage0-gate0-rework-2026-08-23） |
| 等级 | 🟡 中 |
| 描述 | R3-F 要求 status 不参与自然键；任何"修改 status 列就替换为不同观测"被禁止；状态变更只能走 observation_revision |
| 影响 | schema/01-core.sql 已修改 UNIQUE 约束；测试 test_natural_key_without_status_no_duplicate_base 等 39/39 通过 |
| 措施 | 1) schema 自然键已 R3 修复；2) 26 项 R3 新增 DB 测试通过；3) 现有 PRELIMINARY→FINAL 路径必须经 observation_revision；4) 任何绕过 trigger 的直接 UPDATE 会被 PL/pgSQL RaiseException 拒绝 |
| 状态 | ✅ R3 已闭环 |
| 责任人 | 数据工程 |

## R18 — Stage 0 R3 返工新增：测试纯净性契约

| 项 | 内容 |
|---|---|
| 来源 | Gate 0 返工指令 R3-H |
| 等级 | 🟡 中 |
| 描述 | 测试不得在工作区产生污染文件（如 data/should_not_exist.json） |
| 影响 | tests/test_cleanliness.py 11/11 通过；data/should_not_exist.json 已删除 |
| 措施 | 1) 契约测试验证 forbidden file list 不存在；2) git tracked hash 集合测试期间不变；3) 临时 IO 必须用 tmp_path/TemporaryDirectory |
| 状态 | ✅ R3 已闭环 |
| 责任人 | 数据工程 |

## R19 — Stage 0 R3 返工新增：evidence builder 自校验

| 项 | 内容 |
|---|---|
| 来源 | Gate 0 返工指令 R3-G |
| 等级 | 🟡 中 |
| 描述 | evidence builder 必须实际跑 pytest+psql、删除绝对路径+wall-clock、对自身不 hash、写后重新校验 hash |
| 影响 | scripts/build_evidence_pack.py 已重写；tests/test_evidence_builder.py 13/13 通过；manifest 423 artifacts |
| 措施 | 1) builder 真跑 psql+pytest，失败非 0 退出；2) manifest 不含自身 hash；3) manifest 不含 /Users/, /home/, /tmp/；4) artifact_count 由代码生成 = sum(role_count) |
| 状态 | ✅ R3 已闭环 |
| 责任人 | 数据工程 |

## R20 — Stage 0 R3 返工新增：spike 04 样本偏差需用户决策

| 项 | 内容 |
|---|---|
| 来源 | Gate 0 返工指令 R3-B |
| 等级 | 🔴 高 |
| 描述 | 唯一能 OCR 跑通的扫描 PDF 是 1909 美国统计摘要；与中国研究平台主题完全无关 |
| 影响 | numeric 0% / char 3.7% / needs_review 100% 全部远低于 Gate 阈值 |
| 措施 | 1) spike 04 维持 FAILED/BLOCKED 状态；2) gate_thresholds.json 列出阈值与用户决策项；3) 阈值降低需用户书面批准；4) 中国扫描 PDF 替代来源需用户授权 |
| 状态 | ❌ BLOCKED（待用户决策） |
| 责任人 | 用户决策 |

## R21 — Stage 0 R3 返工新增：31×22=682 槽位 + tracked-ZIP + 湖北月报 period metadata（已实施）

| 项 | 内容 |
|---|---|
| 来源 | Gate 0 返工指令 R3-C / R3-D / R3-E |
| 等级 | 🔴 高 |
| 描述 | R3-C/D/E 已实施并通过测试：国家年鉴 31×22 grid（`test_full_31x22_grid_exact` 断言 n=682；缺失槽位显式建模 `test_missing_cells_modeled_explicitly`）；tracked-ZIP-only 输入 + zip-slip 防护 + `locate_0109_in_zip` + clean-clone 缺 ZIP fail；湖北月报 per-indicator period metadata（`TestR3PeriodMetadata`：1-5月→CUMULATIVE_5MONTH / 月末→PERIOD_END_OF_MONTH / 上半年等，per-row period_start/end/label/type） |
| 影响 | spike 00/02/03 已恢复 PASSED（6 个 spike = 5 PASSED + 1 BLOCKED）；Gate 0 整体仍 BLOCKED（R13/R20 spike 04 真实样本） |
| 措施 | C/D/E 全部落地且测试通过；无 Stage 1 增量补做项 |
| 状态 | ✅ R3 已闭环 |
| 责任人 | 数据工程 |

## R22 — Stage 0 R4 返工新增：skip-as-PASS 反检测（R4-1）

| 项 | 内容 |
|---|---|
| 来源 | Codex R3 复核 REJECT 理由（1）；Gate 0 返工指令 R4-1 |
| 等级 | 🟡 中 |
| 描述 | mandatory 测试中隐藏 `pytest.skip`（缺样本/缺 tesseract/缺 git 等）实质等同"标记 PASSED 但未跑"，违反 §0 反 skip-as-PASS 契约 |
| 影响 | 测试绿灯不能证明提取器/契约/流程有效；Codex / Cursor 等复验方能识别并计入 REJECT 理由 |
| 措施 | 1) 删除 spike 00/04 中所有 `pytest.skip`/`pytest.skipif`，改为 `pytest.fail`（明确"缺样本 = 失败"）；2) `tests/test_cleanliness.py` H-2 子进程用 `--deselect <nodeid>` 替代 `pytest.skip` 防递归；3) builder `_parse_pytest_stats()` 解析 stdout，skipped > 0 → rc=2；4) 新增 `test_extractor_fails_when_sample_missing` / `test_extractor_fails_when_tesseract_missing` 显式断言 fail 路径 |
| 状态 | ✅ R4-1 已闭环；`test_cleanliness.py` 3 处环境防御性 skip（非 spike 缺失样本，保留） |
| 责任人 | 测试工程 |

## R23 — Stage 0 R4 返工新增：全国年鉴证据一致性 + 质量 BLOCKED 诚实记录（R4-2）

| 项 | 内容 |
|---|---|
| 来源 | Codex R3 复核 REJECT 理由（2）；Gate 0 返工指令 R4-2 |
| 等级 | 🔴 高 |
| 描述 | R3 期间 `per_column_accuracy.json` 输入与 extracted.json 不同源 + 准确率快照陈旧；存在 cherry-picking 列风险 |
| 影响 | 数字看似 PASS 但实际口径漂移；Gate 0 评审不能信任旧快照 |
| 措施 | 1) 新建 `build_per_column_accuracy.py`，输入即 `extracted.json`（同源）；2) 22 列全部覆盖，无 cherry-picking；3) 字节可重现测试（CLI 参数 `--input/--output`，无随机种子）；4) 诚实验证 `overall_verdict=BLOCKED`（needs_review=385/682=56.45% 触发 docs/08b 回滚线，绝不假装 PASS） |
| 状态 | ✅ R4-2 已闭环 |
| 责任人 | 数据工程 + 测试工程 |

## R24 — Stage 0 R4 返工新增：Evidence Builder 加固（R4-3）

| 项 | 内容 |
|---|---|
| 来源 | Codex R3 复核 REJECT 理由（3）；Gate 0 返工指令 R4-3 |
| 等级 | 🟡 中 |
| 描述 | 原 builder 用 `random.sample(artifacts, 5)` 随机抽查 5 个哈希；其余 420+ artifact 哈希无校验，存在"漏抽到被篡改 artifact"风险 |
| 影响 | manifest 可被部分篡改且 builder 不报 |
| 措施 | 1) 删除 `random.sample(5)`，改为 `verify_all_artifacts()` 全量逐项校验（路径唯一 + 相对 + 存在 + 大小 + SHA-256）；2) `EVIDENCE_PACK_TAMPER=<artifact-path>` 测试钩子模拟篡改非首 5 个 → builder rc=4；3) `_check_hook_env_clean()` 门控 SKIP_*/FORCE_*（无 `EVIDENCE_PACK_TEST_HOOKS=1` 一律拒绝，rc=6）；4) manifest 不在自身 artifacts + role_count 之和 == artifact_count |
| 状态 | ✅ R4-3 已闭环 |
| 责任人 | builder 工程 |

## R25 — Stage 0 R4 返工新增：I-05 来源等级治理（R4-4）

| 项 | 内容 |
|---|---|
| 来源 | Codex R3 复核 REJECT 理由（4）；Gate 0 返工指令 R4-4 |
| 等级 | 🟡 中 |
| 描述 | I-05（来源等级规则）原被误归为"用户决策项"；实质应是 dev 可落地的 schema + 审计 + 测试 + 文档 |
| 影响 | I-05 无法"已闭环"；治理约束无法自动化验证 |
| 措施 | 1) `schema/migrations/002_source_governance.sql`：(a) `declared_source_level` 列；(b) `source_level_s0_requires_verified` CHECK；(c) `source_document_verification_event` 审计表（append-only）；(d) 触发器自动记录 verification_status 迁移（含 `app.verifier_id` GUC）；2) `tests/test_source_governance.py` 21 测试（含 S1-S4 parametrize）；3) `source_registry/registry.csv` archive.org 1909 美国样本 S0→S3（per R4 用户决策）；4) `docs/03-source-registry.md §9` 完整章节 |
| 状态 | ✅ R4-4 已闭环；`tests/conftest.py` 默认自动 apply 002 链（R5-A） |
| 责任人 | schema 工程 + 数据治理 |

## R26 — Stage 0 R4 返工新增：默认 apply 链 + 文档同步（R5-A / R4-5）

| 项 | 内容 |
|---|---|
| 来源 | Cursor R4 复验 (`reviews/stage0-gate0-rework-2026-08-23/03-stage0-cursor复验.md`) §3.2/§3.4 |
| 等级 | 🟡 中 |
| 描述 | (a) pytest 与 builder 默认不 apply migration 002 → 默认流程下 governance 测试必失败；(b) docs/03 §4.4 "5/15 PASS" 与 eval_report.json 真实数字（0% / 3.7% / 100%）矛盾；(c) docs/11 文首 / §9.4 / §10 残留"205 passed" + "I-05 部分完成"；(d) docs/12 schema_negative 写 47（实测 39）；(e) docs/12 §6 R4-R1..R4-R4 风险 ID 在 docs/09 不存在 |
| 影响 | "237 passed 可复现 + 文档同步"声明不成立；R4-5/R4-6 不通过 |
| 措施 | 1) `tests/conftest.py` autouse session fixture：DB 可达时 DROP+链式 apply 01-core + migrations/*.sql（按字典序）；2) `scripts/build_evidence_pack.py` `run_db_apply()` 同款链式 apply（不只 01-core.sql）；3) docs/03 §4.1-4.4 测试数 + spike 04 真实数字修正；4) docs/11 文首 / §9.4 / §10 改 237 + I-05 已闭环；5) docs/12 §6 风险 ID 与 docs/09 R22-R26 对齐 |
| 状态 | ✅ R5 已闭环；Cursor §9 复跑命令链已独立验证 |
| 责任人 | 工程 + 文档 |

## 风险评审节奏

- **Gate 评审**（每阶段末）：逐条评审风险状态
- **月度风险扫描**：新风险登记 + 旧风险重新评估
- **重大事故**：24 小时内更新风险登记 + 写 RCA
