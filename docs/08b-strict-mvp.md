# 08b — 严格 8—12 周 MVP（Strict 8—12 Week MVP）

> 与 `docs/08-mvp-plan.md`（22—32 周长期路线图）并列。
> 现行 MVP 是 PRD 基线的最低验收版，不预埋 Stage 1 之后的范围。
> 触发回滚后回到 `docs/08-mvp-plan.md` 长期路线图重新评估。
> 最后更新：2026-08-23

---

## 1. 用户和首个研究问题

### 1.1 目标用户（MVP 阶段唯一）

**公开研究者和调查记者**——可独立验证、可下载原始出处、关心口径真实性胜过数据量。

**非用户**（明确排除）：
- 商业咨询、政府内部、政策推荐等场景；
- 任何把"官员总分""综合排名"作为输出的需求；
- 需要实时大屏/告警/对接生产的场景。

### 1.2 首个研究问题（唯一）

> **2024 年中国 31 省级行政区的地区生产总值（GDP）、第一/二/三产业增加值，与官方口径一致率如何？跨省之间差异是否在历史修订范围内？**

这一个问题能驱动：
- Schema 端到端落库（NBS 1 个源 + 31 个省级年鉴）；
- 4 类样本的国家 + 省级双验证；
- 数据血缘 + 修订链路；
- 跨源一致性自动核对；
- 拒绝"总分""排名"等红线输出。

---

## 2. 逐周任务（8—12 周，仅此一种基线）

| 周 | 任务 | 责任人 | 依赖 | 验收 |
|---|---|---|---|---|
| **W1** | 部署 PostgreSQL 17 + PostGIS 容器；空库执行 `schema/01-core.sql` 退出码 0；生成 `schema/migrations/001_create_core.log` | Schema Owner | — | DB 可连接；`\dt cegr.*` 显示 41 张表 |
| **W1** | 来源登记 CSV 与校验脚本：4 个核心源（国家统计局 + 31 省统计局 + 用户上传 + DSH/M3 模型库）；`source_registry/registry.csv` 真实存在 | Source Owner | W1 DB | 4 行 CSV，hash 与 URL 一致 |
| **W2** | 落地 Stage 0 提取器为生产 ETL：national-yearbook-table（JPG→OCR）、provincial-yearbook-table（xls→xlrd）、municipal-bulletin（HTML→bs4） | ETL Owner | W1 DB | Spike 00 测试在 CI 通过 |
| **W2** | 上传入口（用户授权后）：`/admin/upload` 接收扫描 PDF；OCR 走 spike 04 `extract_04_scanned_pdf.py`（**当前诚实 BLOCKED**，待中文样本提供后正式启用）；BLOCKED 时返回明确 503 + 原因 | ETL Owner | W1 DB | 接受一个测试 PDF；extracted.json 含 needs_review 队列 |
| **W3** | H1 累计 vs Q2 单季 vs 全年的口径识别逻辑；建立"待核验 caveat"登记机制；H1 累计单列 vs Q2 单季单列互不混用 | Methodology Owner | W2 ETL | 测试覆盖 3 种口径各 1 个真实样本 |
| **W3** | Stage 0 文档冻结（00—11 + 08b MVP + 09 风险登记 + 10 验收 + 11 总结）；不再迭代 | Docs Owner | W2 | 文档与 Git commit 一一对应 |
| **W4** | 数据落库：国家统计年鉴 C03-09 表 → `observation` 表（682 行）；湖北 0109-地区生产总值 → 480 行；深圳公报（8 行） | Data Owner | W2 ETL | 跨源核对：湖北 2024 GDP ≈ 60013（4 位精度） |
| **W5** | 用户上传通道接通：手动上传 1 张**真实**扫描 PDF（不得用合成 PDF 替代）；OCR 提取；进入 needs_review 队列；不自动入库（待人工核验）。**若真实扫描 PDF 仍未取得，W5 整体保持 BLOCKED，不得用合成样本填空** | ETL Owner | W4 | 1 个真实 PDF 走完全链路 **或** 显式 BLOCKED 状态 |
| **W6** | 跨源一致性核对：同一 (indicator, geo, period) 跨多源差异 < 0.5% 视为一致；进入统计 | QA Owner | W4 | 核对报告：31 省各 1 行 |
| **W6** | `tests/test_schema_negative.py` 在 CI 跑通（13 项负例） | QA Owner | W1 DB | 13/13 通过 |
| **W7** | 风险扫描：R01/R02/R04/R08/R11/R12/R13/R14 状态评估；真实上传证据收集 | Risk Owner | W4-W6 | 风险登记表更新；新增/关闭登记 |
| **W7** | 第一个研究问题答复页面：`/research/q1-2024-gdp` 显示 31 省 + 跨源核对 + caveat 链 | Frontend Owner | W4-W6 | 公开访问无 500；1 跳回源 |
| **W8** | Gate 1 验收：4 类样本入库存档；默认 pytest 通过；Schema 0 警告；3 类样本精度达标；扫描 PDF 真实或 BLOCKED | All | 全部 | `READY FOR GATE 1` 或 `BLOCKED` |
| **W9** | 缓冲周：W4-W7 任意阶段延迟时启用；不动基线 | — | — | 仅在 W8 未达时启动 |
| **W10** | 长期路线图重评估：是否进入 Stage 2（地市扩展）；若是，更新 PRD 偏差表并交用户审批 | Lead | W8 + 用户决策 | 不自动进入 |
| **W11-W12** | 备份 + 文档 + 移交；不在 MVP 范围扩展 | Lead | W10 | 移交清单 |

---

## 3. 依赖关系（已锁定）

```
W1 (DB + Schema)
 ├─→ W2 (ETL 落库)
 │    └─→ W4 (数据入库)
 │         ├─→ W5 (上传通道)
 │         ├─→ W6 (跨源核对)
 │         │    └─→ W7 (风险扫描)
 │         │         └─→ W8 (Gate 1)
 │         └─→ W7
 ├─→ W3 (口径 + 文档冻结)
 └─→ W6 (负例测试)

W8 → W9 (缓冲) → W10 (PRD 偏差表) → W11-W12 (移交)
```

---

## 4. 风险和触发指标

| 风险 | 检测指标 | 触发 | 回滚动作 |
|---|---|---|---|
| **R-Schema-Exec** Schema 不能在新 PG 实例执行 | `psql -v ON_ERROR_STOP=1` 退出码 ≠ 0 | 任一执行失败 | 回到 W1；不进入 W2 |
| **R-Sample-Real** 真实样本缺失 | `data/extracts/00-*/extracted.json` 行数 = 0 | 任一 spike 0 行 | 视为 BLOCKED；Gate 1 不通过；不开 W8 |
| **R-OCR-Conf** OCR 准确率 < 80% | needs_review 队列 > 50% | 任一行 W6 失败 | 上传通道暂停；要求人工核验 |
| **R-Cross-Src** 跨源差异 > 0.5% | 一致性核对报告 | > 3 省 | 锁定该省为 `QUARANTINED`；不展示 |
| **R-Time** 任务累计延迟 > 1 周 | 任一周未达成 | W6 末未达 | 启用 W9 缓冲；不延长 MVP |

### 4.1 5 个领域回滚阈值（per 返工指令七）

任一领域未达 PASS 或未显式登记 BLOCKED，Gate 1 整体回滚：

| 领域 | Spike | PASS 条件 | BLOCKED 条件 |
|---|---|---|---|
| 国家年鉴表（多列 JPG） | spike 00 | ≥ 4 列对得上 NBS 官方值；其余列明确登记 `missing_reason` | 任一列无 `missing_reason` 又对不上 |
| 国家年鉴（月度 HTML） | spike 01 | ≥ 3 行真值对照通过 | HTML 表抽取 0 行 |
| 省级年鉴（ZIP/xls） | spike 02 | deterministic rebuild 两次 byte-identical；≥ 1 行真值对照 | rebuild 不稳定或样本缺失 |
| 市级公报（HTML） | spike 03 | ≥ 3 行真值对照通过 | 抽取 0 行 |
| 扫描 PDF OCR | spike 04 | 真实扫描 PDF OCR 真值对照通过 | **真实扫描 PDF 缺失时 spike 04 = BLOCKED ⇒ Gate 0 = BLOCKED** |

BLOCKED 项目必须显式登记 + 责任人 + 重启条件，不得混为 PASS。

### 4.2 偏差处理

任何与 PRD 基线的偏差（含 R-Sample-Real / R-OCR-Conf 触发）必须先经用户批准后才进入正式基线。详见 §7。

---

## 5. 排除项（明确不在 MVP 范围）

- ❌ 批量抓取全国 300+ 地市数据（per PRD + 用户指令）
- ❌ 官员能力总分、排名、绩效画像（per PRD 6.6）
- ❌ 私人/泄露/非公开个人信息（per PRD 11.5）
- ❌ Stage 1 全部功能（人物、政策、预算、跟踪项目）
- ❌ pgvector 嵌入（Stage 4 评估后决定）
- ❌ DSH / Agent 自动决策（Stage 4 评估后决定）
- ❌ 实时大屏 / 告警 / 通知
- ❌ 商业 API 对接 / 商业数据库
- ❌ 移动端 / 多语言

---

## 6. Gate 进入与退出

### 6.1 进入 Gate 1（Week 8 末）

必须满足（评审方逐项打勾）：
- [ ] 4 类 PRD 指定样本全部具备原件、hash、定位、结果和测试
- [ ] 真实扫描 PDF 完成 OCR 真值对照 **或** 保持 BLOCKED 状态
- [ ] Schema 在全新 PostgreSQL 17 + PostGIS 上完整执行成功（退出码 0）
- [ ] 核心模型、来源外键和不可变机制满足 PRD
- [ ] 默认 pytest 命令通过（实测 131 passed + 1 skipped BLOCKED）
- [ ] 所有测试实际调用实现，无永真断言
- [ ] 湖北期间语义已确认或保持明确的待核验状态
- [ ] 风险状态与证据相符（R01/R02/R04/R08/R11/R12/R13/R14 评估完成）
- [ ] 最终总结与工作区逐项一致
- [ ] 未进入 Stage 2，未 commit，未 push

### 6.2 退出 Gate 1（用户批准后）

- 进入 W10：评估是否启动 Stage 2（地市扩展）
- 若进入：必须更新 PRD 偏差表并交用户批准
- 若不进入：保持 MVP 状态；下一轮仅做缺陷修复

---

## 7. 与 PRD 基线的偏差表

> 现行 MVP 在 PRD 第 15 章阶段基线内，无基线变更。
> 若未来 Gate 1 评审方建议缩小 Stage 1 范围（例如"先做江苏"），必须先把以下内容提交用户决策：

| PRD 基线 | 候选偏差 | 原因 | 影响 | 需要用户批准的决策 |
|---|---|---|---|---|
| Stage 1 = 全国 + 31 省 + 4 类数据源 | 仅做江苏单省 | 节省开发周期 | Stage 1 范围缩小；其他 30 省延后到 Stage 2 | **不推荐**：违背 PRD 阶段范围 |
| Stage 2 = 试点 5-10 个地市 | 不做地市 | 节省开发周期 | Stage 2 推迟 | **不推荐**：违背 PRD 阶段范围 |
| Stage 3 = 人物政策项目跟踪 | 仅做政策文件 | 节省开发周期 | Stage 3 部分推迟 | **不推荐**：违背 PRD 阶段范围 |
| 全部走自动化 ETL | 引入 DSH/Agent 决策 | 提高效率 | 违背 PRD 12.7 红线 | **禁止**：越红线 |
| 8—12 周 MVP | 22—32 周长期 | 涵盖更多功能 | 增加交付时间与不确定性 | 已保留为长期路线图 |

> 任何"建议偏差"必须先经用户批准后才进入正式基线；
> 未经批准的偏差不得进入 MVP 文档。

---

## 8. 完成定义（Definition of Done）

只有以下全部满足，才能在 Gate 1 中提交 `READY FOR GATE 1`：

1. **数据层**
   - 4 类样本皆有原件 + hash + 定位 + 提取结果 + 完整测试
   - 真实扫描 PDF 完成 OCR 真值对照 **或** 标记 BLOCKED + 待用户授权
   - 默认 pytest 通过（实测 ≥ 130 passed；无失败；BLOCKED skipped 显式标注）
2. **Schema 层**
   - 在空 PG 17 + PostGIS 上 `psql -v ON_ERROR_STOP=1 -f schema/01-core.sql` 退出码 0
   - 13 个负例测试在 CI 通过
3. **模型层**
   - 跨源独立 observation 可并存（实测）
   - observation 走 append-only；删 observation 不毁 revision（实测）
4. **口径层**
   - H1 累计 / Q2 单季 / 全年三口径独立列示
   - `%` vs `ppt` 在所有文档一致
5. **风险与文档**
   - R13—R16 正式登记或合并
   - 真实 OCR 缺失时 R04/R08/R11 不标"已缓解"
   - 最终总结行数与工作区一致

**违反以上任何一项即 BLOCKED。**

---

## 9. 与 `docs/08-mvp-plan.md` 的关系

- `docs/08-mvp-plan.md` = 长期路线图（22—32 周）
- `docs/08b-strict-mvp.md` = 本文件，严格 8—12 周 MVP
- 当前 Stage 0 范围以本文件为基线
- Stage 1 启动后，回到 `08-mvp-plan.md` 重评估
