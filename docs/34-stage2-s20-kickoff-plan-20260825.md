# Stage 2 启动规划 — docs/34

- 编号：`docs/34-stage2-s20-kickoff-plan-20260825.md`
- 拥有者：CC
- 前置：`142`（用户裁定 C）、`143`（S2.0 任务书）、`docs/08` §3
- 范围：**规划 only**；实现另开
- 状态：草案；不宣布 Gate 1 / Gate 2 PASS

---

## 1. Stage 2 目标（对齐 docs/08 §3）

把 Stage 1 已入库的「S0/S1 fact 数据」提升为**治理观察页面**——让用户能在 5 个省级页面上，以**六段证据链 + 七维度观察卡**的形式，看到从 indicator / source_document → policy / person / budget / project → INFERENCE / JUDGMENT 的完整链路。

Stage 2 不做新数据源采集；只在 Stage 1 数据底座之上做：

1. **新治理实体入库**（person/tenure、policy_document、project_event、budget_allocation、inference_record、claim_evidence_link）
2. **可演示的前端**（Next.js，5 个省级页面，六段证据链 UI，七维度观察卡）
3. **至少 1 个反例被显式登记并展示**（per Gate 2 §3.2 硬要求）

---

## 2. Gate 2 定义（严格继承 docs/08 §3.2）

| 验收项 | 阶段来源 | 备注 |
|---|---|---|
| 5 个省/10 个地市观察页面上线 | S2.7 | **核心 UI 刀** |
| 六段证据链完整可点击 | S2.7 + S2.6 | 反例登记必须有 |
| 七维度观察卡可展开 | S2.8 | 与 S2.7 紧耦合 |
| **没有「官员能力总分」** | PRD 红线 | §3.3 红线 1 |
| 每条 governance 观察标注 INFERENCE/JUDGMENT | S2.5 + S2.7 | UI 角标 |
| 至少 1 个反例被显式登记并展示 | S2.6 | 不可推迟 |
| doc 10 测试 3.1-3.5 全过 | Stage 2 收口 | |

**关键观察**：六段证据链 UI（S2.7）是**唯一不可降级**的验收项；其他都可以「演示级实现」先过。

---

## 3. 从 Stage 1 继承的 OPEN 清单

按 `142` 接受；本 Stage 必须显式携带而非假装已过：

| OPEN 项 | 来源 | 在 Stage 2 中的处置 |
|---|---|---|
| **真实 SHA-locked 江苏样本** | S1.18（DEMO 路径） | **必填依赖**：S2.7 的省级观察页无法演示真实证据链，除非此 OPEN 收口；Stage 2 第一刀配套 |
| **cron / 通知 / 真实联外探针** | Stage 1 运维刀 | **必填依赖**：Stage 2 ingest run 监测依赖真实 URL probe；建议在 S2.0.1 同步补 |
| **OCR 生产路径** | S1.17 (scanned PDF) | S2.3 / S2.4 的政策文件入库多数为扫描件；Stage 2 至少需 1 条生产路径，否则只能演示 NBS 数字 |
| **`is_demo` 机制** | ✅ 已交（S1.18） | Stage 2 所有新表沿用 `lineage->>'is_demo'` 约定；不复刻魔数 |
| **doc 10 测试** | Stage 1 Gate 1 包 | Stage 2 测试 3.1-3.5 须以 Gate 1 测试 2.1-2.5 为基线 |
| **FastAPI 只读服务**（S1.10） | ✅ 已交 | Stage 2 前端直接消费；不另起 API |
| **dbt staging candidate**（S1.19） | ✅ 已交 | Stage 2 新表 = 新 staging candidate CTE，遵循 `133` §1「过滤落 staging 优于 mart」 |

**红线提醒**：Stage 2 不关闭以上 OPEN 中的任何一个即可推进，但**江苏 SHA 样本与 OCR 生产路径**是 Stage 2 真实演示的硬卡点，建议在 S2.0.1/S2.0.2 同步收口，不算 Stage 2 实现刀的 scope 扩大。

---

## 4. 建议首刀序（含依赖论证）

### 4.1 推荐序列

| 序 | 任务代号 | 内容 | 估时 | 依赖 |
|---|---|---|---|---|
| **1** | **S2.0.1** | Next.js 骨架 + `/api/observations/...` 演示接口（mock 数据可） | 2-3 天 | S1.10 (FastAPI 只读) |
| **2** | **S2.0.2** | 真实 SHA-locked 江苏样本替换 + URL probe 真实化 | 2-3 天 | Stage 1 OPEN |
| **3** | **S2.7-a** | 六段证据链 UI 雏形（用 mock 5 省数据） | 1 周 | S2.0.1 |
| **4** | **S2.1** | person/tenure/position 表 + 数据契约 + 首批入库 | 1 周 | S1.x (schema 已含位置) |
| **5** | **S2.7-b** | person/tenure 接入六段证据链 | 3 天 | S2.1 + S2.7-a |
| **6** | **S2.2** | policy_document/policy_target/government_commitment | 1-2 周 | S1.x |
| **7** | **S2.3** | project_event + 五态机 UI | 1-2 周 | S2.7-b |
| **8** | **S2.4** | budget_allocation/execution | 1-2 周 | S1.x |
| **9** | **S2.5** | inference_record + 推断 API | 1 周 | S2.1-S2.4 |
| **10** | **S2.6** | claim_evidence_link + 反例登记 | 1 周 | S2.5 |
| **11** | **S2.8** | 七维度观察卡 | 1 周 | S2.7 + S2.5 |
| **12** | **S2.9** | 同类地区对比（手工选择初版） | 1 周 | S2.7 |
| **13** | **S2.10** | Gate 2 评审包 | 3 天 | 上述全部 |

### 4.2 为什么先 S2.0.1 而非 S2.1

`143` 任务书给的两个默认方向是 **S2.7 骨架** 或 **S2.1 person/tenure**。CC 推荐 **S2.0.1 Next.js 骨架 + API 演示**，理由：

1. **UI 是 API 契约** —— 六段证据链 UI（Gate 2 硬要求）如果在 S2.1 之后设计，person/tenure 的字段会被锁死在 UI 不需要的形状上；先有 UI mock，可以反向验证 S2.1 字段集是否够用
2. **真实 SHA-locked 江苏样本**（Stage 1 OPEN）需要 UI 验证「真实 SHA vs DEMO sentinel」是否能区分展示；S2.0.1 是首个可以端到端看到这一区别的刀
3. **FastAPI 只读服务（S1.10）**已经交付，骨架直接复用，避免 S2.1 做完才发现 API 字段缺
4. **person/tenure 可并行规划**：S2.0.1 期间，CC 可以并行做 S2.1 的 dbt staging candidate 与数据契约，骨架就绪时 S2.1 同步上

### 4.3 不在 Stage 2 内的刀（边界声明）

- ❌ 真实 OCR 生产流水线（属 Stage 1 OPEN；S2.0.2 同步收口，但不扩 Stage 2 scope）
- ❌ pgvector embedding（PRD 红线 + §3.3 红线）
- ❌ 任何官员能力评分（PRD 红线 + §3.3 红线 1）
- ❌ DSH 启用（§3.3 红线 + §7）
- ❌ 实时数据流（§3.3 红线；月度/年度更新）
- ❌ pgvector / 隐性指数（§3.3）
- ❌ 全国实时排名（Stage 3 红线，提前防越界）

---

## 5. 与现有组件的边界

| 现有组件 | Stage 2 用法 | 不做什么 |
|---|---|---|
| **FastAPI 只读服务**（S1.10） | Stage 2 所有新观察页的 `/api/...` 端点 | 不扩展成写 API；Stage 2 写路径走 admin upload (S1.13) |
| **dbt staging candidate**（S1.19） | S2.1-S2.4 每个新表 = 一个 staging candidate CTE + 一个 mart | 不直接改 mart 层（`133` §1 约束） |
| **admin upload**（S1.13） | Stage 2 新表 ingest run 仍走 admin upload UI | 不绕过 admin upload 写库 |
| **URL probe**（S1.17） | Stage 2 新 source_document 上传前仍走 URL probe | 不爬源站（PRD 红线） |
| **`is_demo` sentinel**（S1.18） | 所有新观察 row 必须含 `lineage->>'is_demo'` | 不复刻「S0 SHA-locked 用真值 / S2 行用 demo」的隐式约定 |
| **observation_no_delete / source_document_no_delete 触发器**（S1.x） | Stage 2 测试 fixture 仍走 TRUNCATE CASCADE | 不绕过触发器写 DDL（除非通过正式 schema migration） |
| **Stage 1 证据包**（504 artifacts） | Stage 2 实现刀起，新增 artifact 按 `role_count` 同步累加 | 不破坏 `sum(role_count)==artifact_count` 不变量 |

---

## 6. 关键风险与回滚点

| 风险 | 触发条件 | 回滚策略 |
|---|---|---|
| S2.0.1 Next.js 选型与现有 FastAPI 风格不一致 | 路由命名、错误处理、序列化约定 | 复用 S1.10 已定约定；S2.0.1 PR 必须通过 review |
| S2.1-S2.4 任一表 schema 改了 2 次以上 | 字段反复调整 | 走数据契约 ADR；不在主分支沉淀「试错 schema」 |
| OCR OPEN 在 S2.2/S2.4 阻塞 | 政策文件全是扫描件 | S2.0.2 用 NBS 数字样本演示；OCR OPEN 不阻塞演示 |
| 反例登记流于形式（S2.6 弱化） | 没有真实反例被登记 | Gate 2 §3.2「至少 1 个反例被显式登记」硬卡；S2.6 单独 tasking 而非 S2.5 子任务 |
| Stage 1 OPEN 未在 S2.0.2 收口 | 真实 SHA 样本缺失 | Stage 2 仍可推进，但 Gate 2 演示只能用 DEMO sentinel；Cursor/用户后续裁定 |

---

## 7. 不做什么（per docs/08 §3.3 + PRD 红线）

1. ❌ 不做官员能力评分
2. ❌ 不做隐性指数
3. ❌ 不启用 DSH
4. ❌ 不做实时数据流（月度/年度更新止步）
5. ❌ 不做全国实时排名
6. ❌ 不做 pgvector embedding
7. ❌ 不宣布 Gate 1 PASS（继承 `142` §书面接受）
8. ❌ 不宣布 Gate 2 PASS（未到 Gate 2 评审）
9. ❌ 不擅自扩 Stage 2 scope（per `143` §红线）
10. ❌ 不改 `gate_thresholds.json`（spike-04 评测构件，只读）

---

## 8. 验收策略（per Gate 2 §3.2）

- **功能演示**：5 个省级页面 + 六段证据链 + 七维度观察卡，**不要求真实 SHA 样本**（属 OPEN）
- **真实样本**：S2.0.2 收口后，1 个省必须有真实 SHA-locked 数据
- **反例登记**：S2.6 至少登记 1 条，UI 可见
- **测试**：doc 10 §3.1-3.5 全过；S1.x §2.1-2.5 不回归

---

## 9. 与现有文档的关系

- 继承 `docs/08` §3（Stage 2 定义）
- 继承 `docs/04`（数据模型，person/tenure/policy/budget/project 表的位置）
- 继承 `docs/06`（governance observation method，INFERENCE/JUDGMENT 标注约定）
- 继承 `docs/10`（验收测试 3.1-3.5）
- 补充 `docs/28` (S1.13 admin upload) 关于新表 ingest run 的边界
- 补充 `docs/31` (S1.16 cross-source dbt) 关于 staging candidate 的扩展规则

---

## 10. CC 建议（供 Cursor 审阅 / 用户裁定）

1. **采纳本规划**（默认：CC 起草，Cursor 审阅，用户在 Gate 2 前可修改）
2. **S2.0.1 + S2.0.2 并行** 收口 Stage 1 OPEN 与 Next.js 骨架；预估 5-6 天
3. **S2.1 person/tenure 与 S2.7-a UI 雏形并行**（CC 规划期已论证）
4. **Gate 2 评审日期**：暂定 W8，与 `docs/08` §3 一致；不擅自提前

— End —