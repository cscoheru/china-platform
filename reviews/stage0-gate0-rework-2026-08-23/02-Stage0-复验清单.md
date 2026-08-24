# Stage 0 Gate 0 复验清单

本清单供 Claude Code 自检和评审方复验。任何标为“阻塞”的项目失败，结论均为“不通过”。

## 1. 工作区和提交证据

- [ ] 提交返工前后的 `git status --short --branch`。
- [ ] 提交实际 diff/stat，不用手写文件清单替代。
- [ ] 没有破坏性 reset、覆盖用户修改或删除未知文件。
- [ ] 未经用户指令，没有 commit、push 或进入 Stage 1。
- [ ] 最终 manifest 包含每个交付物的路径、大小、SHA-256 和来源。
- [ ] 必需样本没有被 `.gitignore` 意外排除，或已提供可重复下载与固定 hash 方案。

## 2. 四类指定样本，阻塞

### 国家统计年鉴表

- [ ] 原件确为国家统计年鉴表，不是月报或普通发布稿。
- [ ] 保留标题、年份、章节、表号、页码/sheet、单元格定位和脚注。
- [ ] 原件 hash 与 manifest、提取结果一致。
- [ ] 测试实际调用提取器，并核对已知单元格。

### 省级统计年鉴表

- [ ] 原件确为省级统计年鉴表，不是月报。
- [ ] 覆盖省级年鉴的真实结构差异。
- [ ] 每行具有 period、unit、source/hash、cell locator、confidence 和 footnote reference。
- [ ] 路径可移植，不含 `/Users/kjonekong/...` 硬编码。

### 地市统计公报

- [ ] 深圳或其他地市公报原件 hash 匹配。
- [ ] 每行有 context quote、section/paragraph locator、period、unit 和 confidence。
- [ ] 测试调用实现，而非只读取预生成 JSON。

### 真实扫描 PDF

- [ ] 原件是合法取得的真实图像型扫描 PDF。
- [ ] 记录页码、DPI、bbox、OCR 引擎和版本。
- [ ] 有人工真值表及单元格准确率。
- [ ] 低置信、缺单位、缺值任一情况都会进入复核队列。
- [ ] `data/extracts/04-scanned-pdf/extracted.json` 实际存在且路径与文档一致。
- [ ] E2E 测试要求非零行数并核对已知真值。

## 3. 数据语义，阻塞

- [ ] 湖北数据没有未经证实的 `Q2_ONLY` 强制结论。
- [ ] H1 累计、Q2 单季、季度频率三种概念被明确区分。
- [ ] 受脚注影响的每一行都引用脚注或 caveat。
- [ ] `…`、`—` 等缺失值被保留为 null，并记录 raw value 和 missing reason。
- [ ] 不把缺失值写成 0，也不静默删除缺失事实。
- [ ] 百分比使用 `%`，百分点使用 `ppt`，文档和测试一致。

## 4. Schema 空库执行，阻塞

- [ ] 使用 PostgreSQL 16 + PostGIS。
- [ ] 执行：

  ```bash
  psql -v ON_ERROR_STOP=1 -f schema/01-core.sql
  ```

- [ ] 退出码为 0，无被忽略的 SQL 错误。
- [ ] 使用 `btree_gist` 和正确的 `daterange`。
- [ ] 没有前向引用或非法 COMMENT。
- [ ] 存在时变 `geo_relation`。
- [ ] indicator definition 包含 PRD 最低字段，含地域范围。
- [ ] observation 关联 methodology version。
- [ ] 不同来源的同一指标/地区/时期观测可以并存。
- [ ] source、source location、source registry、ingestion 均有外键。
- [ ] observation 的 source location 必填且至少一种 locator 非空。
- [ ] observation、source document、revision 的不可变/append-only 由数据库保证。
- [ ] 删除父记录不会销毁修订历史。
- [ ] current observation 视图正确选择最新 revision。
- [ ] confidence、hash、revision number、有效期均有检查约束。

## 5. 数据库负例测试，阻塞

- [ ] 重叠地域有效期插入失败。
- [ ] 重叠方法学有效期插入失败。
- [ ] `valid_from > valid_to` 插入失败。
- [ ] 孤儿 source/source location 插入失败。
- [ ] 空定位插入失败。
- [ ] confidence 超出 0—1 插入失败。
- [ ] 非 SHA-256 hash 插入失败。
- [ ] revision number 非正整数插入失败。
- [ ] 更新或删除不可变事实失败。
- [ ] 删除 observation 不能清除 revision。
- [ ] 两个独立来源可以并存并参加跨源校验。

## 6. Python 测试，阻塞

- [ ] 默认命令无需特殊参数即可收集并通过：

  ```bash
  python3 -m pytest -q -p no:cacheprovider
  ```

- [ ] 退出码为 0。
- [ ] failed 为 0。
- [ ] 四类样本核心测试 skipped 为 0。
- [ ] 不存在同名模块 import mismatch。
- [ ] 不存在 `len(...) >= 0`、`missing <= total` 等永真断言。
- [ ] Spike 1—4 测试均调用对应实现。
- [ ] OCR 高置信但缺单位时 `needs_review=true`。
- [ ] OCR 高置信但缺值时 `needs_review=true`。
- [ ] OCR 低置信时 `needs_review=true`。
- [ ] OCR E2E 核对已知行、值、单位、bbox、confidence 和 review queue。
- [ ] 提交 Python、系统工具和语言包的可重建版本说明。

## 7. 8—12 周 MVP，阻塞

- [ ] 独立定义一个 8—12 周 MVP。
- [ ] 明确目标用户和首个研究问题。
- [ ] 有逐周任务、负责人/责任域、依赖和验收。
- [ ] 每项有风险、检测指标、回滚触发条件和回滚动作。
- [ ] Schema、数据、采集器、分析方法和发布均有回滚方案。
- [ ] 22—32 周计划仅标为长期路线图。
- [ ] 与 PRD 阶段不一致的建议列入偏差表。
- [ ] 未经用户批准的偏差没有进入正式基线。

## 8. 文档和风险一致性

- [ ] 风险状态严格区分已识别、已设计、部分验证、已缓解和 BLOCKED。
- [ ] R13—R16 已正式登记、明确合并或删除重复项。
- [ ] 真实 OCR 完成前，R04/R08/R11 未标为已缓解。
- [ ] 治理观察维度数量和映射与 PRD 一致。
- [ ] 用户上传资料默认未核验，不能仅凭声明成为 S0。
- [ ] source registry 文档与实际 CSV/校验工具一致。
- [ ] README、Schema README、docs/00—11 的路径和能力描述一致。

## 9. 最终总结一致性，阻塞

- [ ] 所有列出的文件实际存在。
- [ ] 行数、大小、表数、枚举数、记录数来自最终工作区。
- [ ] 每条命令都是实际执行的完整命令。
- [ ] 每个命令分别记录退出码和真实输出摘要。
- [ ] 脚本运行结果与 pytest 结果不被混写。
- [ ] 总耗时与各分项耗时数学一致。
- [ ] `BLOCKED` 和合成验证没有被标记为真实样本 PASSED。
- [ ] 最终总结包含 PRD 要求的做了什么、没做什么、文件、命令、结果、风险、决策和下一步。
- [ ] 最终状态只允许 `READY FOR GATE 0 RE-REVIEW` 或 `BLOCKED`，不得自行写“已通过”。

## 10. 红线复核

- [ ] 未批量抓取全国市县数据。
- [ ] 未建立官员能力总分或排名。
- [ ] 未收集私人、泄露或非公开个人信息。
- [ ] 未把活动数量直接当绩效。
- [ ] 未让 LLM 改写原始统计数据。
- [ ] 未绕过验证码、访问控制或付费墙。
- [ ] DSH/Agent 未进入核心 ETL、统计计算或数仓路径。
- [ ] 未进入 Stage 1。

## 复验结论规则

- 任一“阻塞”项未通过：**不通过**。
- 仅剩不会影响数据正确性、可追溯性、可执行性和范围基线的问题：可考虑“有限通过”。
- 所有阻塞项及重要问题均关闭，证据可独立复现：才可“通过”。

评审方将独立运行命令和抽查原始样本，不接受仅凭 Markdown 中的成功声明。
