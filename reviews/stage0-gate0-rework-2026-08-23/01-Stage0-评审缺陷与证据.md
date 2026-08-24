# Stage 0 评审缺陷与证据附件

评审日期：2026-08-23  
评审结论：**不通过**  
阶段状态：**继续停止，不得进入 Stage 1**

## 一、阻塞问题

### B-01 四类指定样本未完成

- 严重性：P0
- 置信度：10/10
- PRD 证据：`china-economy-governance-research-platform-prd-v0.1.md:691-692`
- 成果证据：
  - `spikes/01-national-yearbook/README.md:5-16` 明确样本是国家月度经济报告；
  - `spikes/02-provincial-yearbook/extract.py:4-12` 明确样本是湖北月报；
  - `spikes/04-scanned-pdf/README.md:3` 明确真实扫描 PDF 为 BLOCKED；
  - `docs/11-stage0-review.md:33-42` 却声明四个 spike 全部 PASSED。
- 影响：未验证国家/省级年鉴特有结构，也没有真实 OCR 准确率和版面证据。
- 关闭条件：国家年鉴、省级年鉴、地市公报、真实扫描 PDF 四类逐一具备原件、hash、定位、结果和测试。

### B-02 Schema 无法执行

- 严重性：P0
- 置信度：10/10
- 证据：
  - `schema/01-core.sql:12` 启用 `btree_gin`，但 `:159-162`、`:260-263` 使用需要 `btree_gist` 的 GiST 排他约束；
  - `:161`、`:262` 对 DATE 使用 `tstzrange`；
  - `:683-684` 在目标表创建前声明外键；
  - `:720` 是非法 `COMMENT ON TABLE` 语法；
  - `docs/11-stage0-review.md:344` 仍称“可执行（DDL 完整）”。
- 影响：空库建表会中止，Stage 1 无法以此 Schema 为基线。
- 关闭条件：在全新 PostgreSQL 16 + PostGIS 数据库运行 `psql -v ON_ERROR_STOP=1 -f schema/01-core.sql`，退出码为 0。

### B-03 核心模型和数据血缘未满足 PRD

- 严重性：P1，Gate 阻塞
- 置信度：10/10
- 证据：
  - PRD `:213-233` 要求 `geo_relation` 和 indicator 地域范围；Schema 缺失；
  - `schema/01-core.sql:291-292` 注释声称唯一键包含 methodology version，实际没有；
  - `:282-284` 的 source、location、ingestion 引用没有外键，后两项可空；
  - `:344`、`:391` 的 source registry 引用没有外键；
  - `:306` 使用 `ON DELETE CASCADE`，可连同 observation 删除 revision 历史。
- 影响：不能强制一跳回源，不能可靠保存时变地域和口径版本，也不能保证历史不可变。
- 关闭条件：模型、外键、自然键、不可变约束和数据库负例测试全部落地。

### B-04 缺少 8—12 周 MVP

- 严重性：P0
- 置信度：10/10
- PRD 证据：`china-economy-governance-research-platform-prd-v0.1.md:695`
- 成果证据：`docs/08-mvp-plan.md:6-17` 总计 22—32 周。
- 附加问题：没有完整的数据、Schema、采集器、模型和发布回滚方案。
- 关闭条件：提交独立的 8—12 周 MVP；现有内容降级为长期路线图。

### B-05 阶段基线被静默改写

- 严重性：P0
- 置信度：10/10
- 证据：
  - PRD `:609-637` 规定 Stage 1 全国及 31 省、Stage 2 试点地市、Stage 3 人物政策；
  - `docs/08-mvp-plan.md:23-36` 的 Stage 1 仅少量来源和省份；
  - `docs/08-mvp-plan.md:64-89` 的 Stage 2 已提前进入人物、政策和治理页面；
  - `docs/11-stage0-review.md:250-258` 又建议江苏单省优先。
- 影响：后续 Gate 编号、范围和验收失去唯一基线。
- 关闭条件：建立 PRD 偏差表；所有基线变更由用户明确批准，然后统一全部文档。

### B-06 湖北期间语义存在高风险错误

- 严重性：P1，数据正确性阻塞
- 置信度：9/10
- 证据：
  - 原表列为“1-6月”，指标名为“上半年”；
  - `data/extracts/02-provincial-yearbook/extracted.json:8` 为 `cumulative_half_year`；
  - `spikes/02-provincial-yearbook/README.md:56`、`docs/05-indicator-methodology.md:272-278` 却解释为 Q2 单季；
  - 原脚注仅为“GDP、居民收入为季度数”。
- 影响：半年累计可能被错误当成单季数据，污染时间序列和跨源比较。
- 关闭条件：取得权威口径确认；逐行保存 period、period_type、footnote reference 和 caveat；未确认前不得强制 Q2_ONLY。

### B-07 测试绿灯不能证明提取器有效

- 严重性：P1，Gate 阻塞
- 置信度：10/10
- 实际命令：

  ```text
  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
  => 3 个 import file mismatch，退出码 2

  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider --import-mode=importlib
  => 87 passed in 1.54s，0 failed，0 skipped
  ```

- 证据：
  - `spikes/04-scanned-pdf/test_extract.py:330-356` 使用 `len(cells) >= 0`；
  - `:446-501` 使用 `len(rows) >= 0`；
  - `spikes/04-scanned-pdf/test_extract.py:216-228` 的缺单位测试在平均置信度 0.817 时没有任何断言；
  - `spikes/01-national-yearbook/test_extract.py`、Spike 2 和 Spike 3 测试主要读取预生成 JSON，没有调用提取器。
- 影响：代码损坏、OCR 零识别或缺单位时仍可能显示全部测试通过。
- 关闭条件：默认 pytest 通过，测试实际调用实现，无永真断言，OCR E2E 核对已知真值。

### B-08 缺失值和逐行血缘实现与文档相反

- 严重性：P1，Gate 阻塞
- 置信度：10/10
- 证据：
  - `spikes/01-national-yearbook/extract.py:111-128` 仅在 value 非空时追加 observation，静默丢弃 `…`、`—`；
  - 当前国家产物为 0 个 null、0 个 missing_reason；
  - `spikes/02-provincial-yearbook/extract.py:59-72` 的每行只有 indicator、alias、unit、value、growth_rate；
  - 省级 19 行没有 cell locator、行级 source/hash、confidence、period/caveat。
- 影响：无法区分未报、抑制和不适用，也不能从省级结果精确回到原单元格。
- 关闭条件：缺失 observation 被保留并写明原因；省级逐行血缘字段和测试全部补齐。

## 二、重要非阻塞问题

### I-01 最终总结不是最终工作区快照

- 严重性：P1
- 置信度：10/10
- 实际 Schema 为 914 行、10 个 `CREATE TYPE`，总结称约 640 行、12 个枚举。
- docs/00—10 多数行数与 `docs/11-stage0-review.md:13-25` 不符。
- `data/extracts/04-scanned-pdf/extracted.json` 不存在，但总结 `:135-143` 声称存在。
- 总耗时写约 16 分钟，分项 20+10+20+30 分钟实际为约 80 分钟。

### I-02 省级 spike 不可移植且样本被忽略

- 严重性：P1
- 置信度：10/10
- `spikes/02-provincial-yearbook/extract.py:30-32` 和测试硬编码本机绝对路径。
- `.gitignore:77` 的 `*.xlsx` 会忽略 `hubei_2026_06.xlsx`。
- 换目录或全新 clone 后不能独立复验 31 个测试及原始 hash。

### I-03 来源登记交付物不一致

- 严重性：P1
- 置信度：10/10
- `docs/00-project-assessment.md:93`、`source_registry/README.md:3` 声称存在 `source_registry/registry.csv`，实际不存在。
- `README.md` 还声称有 CSV 校验工具，实际未发现。

### I-04 风险登记状态不可信

- 严重性：P1
- 置信度：10/10
- R04/R11 在无真实扫描样本情况下标为已缓解。
- R08、R10 的正文状态和汇总状态不一致。
- 最终总结新增 R13—R16，但承认没有正式登记。

### I-05 方法和来源等级规则不一致

- 严重性：P1/P2
- 置信度：9—10/10
- `docs/04-data-model.md:346-358` 与 `docs/05-indicator-methodology.md:258-268` 对 `%`、`ppt` 定义冲突。
- `docs/06-governance-observation-method.md:99` 称七维度，表格实际列出八项。
- `docs/03-source-registry.md:167-184` 允许上传者声明官方出版后成为 S0，缺少平台核验状态。

## 三、证据不足

当前没有形成可独立保存和回放的以下材料：

- CC 原始 Stage 0 计划；
- 稳定的基线 commit 或完整 diff；
- 原始测试日志；
- Schema 空库执行日志；
- 真实扫描 PDF 和人工真值对照；
- 四类指定样本统一 manifest；
- 完整的 8—12 周 MVP 回滚表。

## 四、已确认的正面证据

- docs/00—10 均存在，主题覆盖基本齐全。
- 三份现有本地原件的 SHA-256 与 README/JSON 一致。
- 01/02/03 现有产物分别为 20/19/8 行。
- 深圳公报产物具备 context_quote、section locator 和 confidence。
- 使用 `--import-mode=importlib` 时确有 87/87 通过，不是虚构数量。
- DSH 三路线矩阵和“核心 ETL 不依赖 DSH”边界基本符合 PRD。
- 官员总分、私人信息、活动冒充绩效和 LLM 改写原始数据等红线已在文档层面明确。
- CC 已停止，未自行进入 Stage 1。

上述正面项可以保留，但不能抵消 Gate 阻塞项。
