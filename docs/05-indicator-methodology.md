# 05 — 指标方法论（Indicator Methodology）

> Stage 0 交付物 #05；对应 PRD 第 15 章第 6 项 + 第 6.4 节 + 第 9 章。
> 回答三个问题：什么是一个"指标"、不同来源同名指标如何处理、口径变化怎么追溯。

## 1. 指标的"四个属性"（per PRD 5.2）

每个 `indicator_definition` 都有四个强制属性：

| 属性 | 说明 | 例 |
|---|---|---|
| **名（canonical_name）** | 规范名 | "地区生产总值" |
| **单位（unit_canonical）** | 标准单位 | "亿元" |
| **频率（frequency）** | 时间粒度 | YEAR/QUARTER/MONTH |
| **可比性说明（comparability_note）** | 跨期/跨地区比较注意事项 | "2010 年后使用新分类" |

加上可选属性：

| 属性 | 说明 |
|---|---|
| `price_basis` | 价格基础（NOMINAL/REAL/CHAIN） |
| `seasonally_adjusted` | 是否季调 |
| `is_cumulative` | 是否累计（"1-7月" vs "7月"） |
| `aggregation_method` | 聚合方法（SUM/AVG/END_OF_PERIOD/WEIGHTED） |
| `additivity` | 可加性（ADDITIVE/NON_ADDITIVE） |
| `formula` | 计算公式 |

## 2. 指标的"五态"（生命周期）

```
定义(v1) ──── 启用 ──── 应用 ──┬─ 口径修订 ── 定义(v2) ── 启用 ── 应用
                                │
                                └─ 停用 ───── 归档
```

| 状态 | 触发条件 | 处理 |
|---|---|---|
| **定义(v1)** | 首次登记 | 入库；indicator_definition |
| **启用** | enabled=true | 可被 observation 引用 |
| **应用** | observation 持续写入 | 正常 |
| **口径修订** | 方法/分类变化 | 写 `indicator_methodology_version` 新行；旧 v 不删 |
| **停用** | 不再使用 | indicator_definition.enabled=false；保留历史数据 |

**关键约束**：`indicator_definition` 不删除也不重命名，仅通过 `indicator_methodology_version` 记录版本变化。

## 3. 同名指标跨来源处理

### 3.1 冲突三态

```
来源 A ─┐                ┌── 一致 ──> 直接用 A
来源 B ─┤ (S0 vs S1) ────┤── 差异 ──> 并存 + source_disagreement 表
来源 C ─┘                └── 矛盾 ──> 标记 + 人工裁决（research_note）
```

### 3.2 三级处理策略

| 冲突等级 | 例子 | 策略 |
|---|---|---|
| **一致** | 国家统计局 vs IMF 的中国 GDP | 用 S0（国家统计局）；S1 存为校验 |
| **差异（轻微）** | 同年公报 vs 年鉴数据差 0.5% | 并存；标记 `comparison_basis` 不同 |
| **矛盾（严重）** | 同一指标同年差 >5% | 并存 + 写 `inference_record` 记录冲突；UI 上并列显示 |

**Spike 1 启示**：stats.gov.cn zxfb 数据为初步统计；年度修正后 yoy 会有 0.3-1.5% 差异，是正常修订。

### 3.3 `source_disagreement` 表（Stage 1 实现）

```sql
-- 待 Stage 1 添加
CREATE TABLE source_disagreement (
    id UUID PRIMARY KEY,
    indicator_id UUID,
    geo_entity_id UUID,
    calendar_period_id UUID,
    source_a_id UUID,
    source_a_value NUMERIC,
    source_b_id UUID,
    source_b_value NUMERIC,
    diff_pct NUMERIC,
    resolution TEXT,  -- 'USE_A' / 'USE_B' / 'PARSE' / 'PENDING'
    resolution_note TEXT,
    resolved_by TEXT,
    resolved_at TIMESTAMPTZ
);
```

## 4. 比较基础（Comparison Basis）

`observation.comparison_basis` 字段必须明确：

| 值 | 含义 | 例 |
|---|---|---|
| `NOMINAL` | 当年价 | 2024 年 GDP = 36801.85 亿元（按 2024 年价格） |
| `REAL` | 不变价（基年某年） | 2024 年 GDP = 28600 亿元（按 2015 年价格） |
| `CHAIN` | 链式（环比） | 2024 年 GDP = 30500 亿元（按链式价格指数） |

**关键约束**：
- 同一 `indicator_definition` 可有多个 `comparison_basis` 实例
- 跨年比较时**必须**先确认比较基础一致
- UI 上图表显示时必须标注比较基础

## 5. 缺失值处理（per PRD 9.4）

**纪律**：**缺失 = NULL + 缺失原因**；**禁止补零**、**禁止补均值**、**禁止线性插值**（除非明确声明 `is_imputed=TRUE`）。

| 场景 | 处理 | 写入字段 |
|---|---|---|
| 来源未发布 | NULL | `missing_reason='NOT_PUBLISHED'` |
| OCR 失败 | NULL | `missing_reason='OCR_FAILED'` |
| 行政区划不存在该期 | NULL | `missing_reason='GEO_NOT_EXIST_AT_PERIOD'` |
| 章节跳过（"…略"） | NULL | `missing_reason='SECTION_SKIPPED'` |
| 抑制（"…"） | NULL | `confidence=0.0` | `missing_reason='SUPPRESSED'` |
| 真正填补（线性插值） | 计算值 | `value=计算值, is_imputed=TRUE, missing_reason='IMPUTED_LINEAR'` |

**Spike 3 启示**：公报中"…"和"略"必须明确区分，UI 上应分别提示"抑制"和"未提及"。

## 6. 单位一致性检查（per doc 10 测试 2.1）

```python
def test_unit_drift_in_series():
    series = get_indicator_series("GDP", geo="江苏", period_range=("2001","2024"))
    units = {row.unit for row in series}
    assert len(units) == 1, f"单位漂移: {units}"
```

**实现机制**：
- `indicator_definition.unit_canonical` 是规范单位
- `observation.unit` 实际单位，必须与规范匹配或在白名单
- 异常时写 `observation_quality_flag`

## 7. 修订机制（per PRD 12.1 R01）

### 7.1 触发修订的情况

1. 统计制度变化（GDP 核算、行业分类）
2. 经济普查（每 5 年；第五次经济普查 2023 年末）
3. 人口普查（每 10 年）
4. 来源方主动修订

### 7.2 修订流程

```
observation_v1 (PRELIMINARY)
   ↓ 数月后来源方修订
observation_v2 (REVISED)  ← 新写一条 observation_revision
   ↓ 终值
observation_v3 (FINAL)    ← 再写一条 observation_revision
```

**纪律**：
- `observation` 表的 `value` 反映当前最新值（v3）
- 历史值通过 `observation_revision` 追溯
- UI 显示当前值 + 历史修订曲线

### 7.3 修订追溯查询

```sql
-- 查看某观测值的全部历史
SELECT rev_no, value, unit, status, revision_date, revision_reason, source_id
FROM observation_revision
WHERE observation_id = $1
ORDER BY revision_no;
```

## 8. 同类地区匹配（per doc 06 第 4 节）

### 8.1 匹配特征

`comparison_group` 表存匹配依据：
- 人口规模（<500万 / 500-1000万 / 1000-2000万 / >2000万）
- 区位（沿海/内陆/沿边）
- 产业基础（资源型/制造型/服务型/混合）
- 发展阶段（高收入/中等/欠发达）

### 8.2 匹配方法

- **手动匹配**（Stage 1）：由研究员指定 3-5 个可比地区
- **Mahalanobis 距离**（Stage 3）：自动找最相似地区
- **倾向得分**（Stage 3）：处理高维匹配

### 8.3 不允许的匹配

- ❌ 仅按 GDP 总量取 top N
- ❌ 不说明匹配依据
- ❌ 同一观察同时被分到多组（重叠即不可解释）

## 9. 分析方法登记（per doc 06 第 4 节）

| 等级 | 方法 | 必须登记 | 模型规格 |
|---|---|---|---|
| L1 | 趋势 | 仅数据 vintage | 不需要 |
| L2 | 同类比较 | comparison_group | 不需要 |
| L3 | 条件化表现 | input_data_vintage | 可选 |
| L4 | 面板 FE | model_specification | 必填 |
| L5 | 事件研究 | model_specification + event_window | 必填 |
| L6 | DiD | model_specification + comparison_group | 必填 |
| L7 | 合成控制 | model_specification + comparison_group + weights | 必填 |

每个 `analysis_run` 必须包含：
- `code_version`（git SHA；可复现）
- `input_data_vintage`（数据快照版本）
- `parameters` JSONB（具体参数）
- `result_payload` JSONB（结果）
- `model_spec_id` + `comparison_group_id`（L4+ 必填）

## 10. 命名规范

### 10.1 指标命名

| 类型 | 规范 | 例 |
|---|---|---|
| 概念 | `名词` | "地区生产总值" / "规模以上工业增加值" |
| 增长率 | `名词 + 增速` | "GDP 增速" / "规模以上工业增加值增速" |
| 结构占比 | `名词 + 占...比重` | "第三产业占 GDP 比重" |
| 比率 | `名词 + 比率` | "城镇化率" |

### 10.2 别名映射

```sql
-- 同一概念不同叫法
INSERT INTO indicator_alias VALUES
  (uuid_generate_v4(), <GDP_ID>, 'GDP', NULL, 'en'),
  (uuid_generate_v4(), <GDP_ID>, '地区生产总值', NULL, 'zh'),
  (uuid_generate_v4(), <GDP_ID>, 'GRP', NULL, 'en');
```

**用途**：把来源方不同表述映射到同一 `indicator_id`，避免重复入库。

## 11. 与其他文档的关系

- 数据模型：`docs/04-data-model.md` + `schema/01-core.sql`（`indicator_definition` / `indicator_alias` / `indicator_methodology_version` / `comparison_group`）
- 治理观察：`docs/06-governance-observation-method.md` 第 4 节（L1-L7）
- 风险登记：`docs/09-risk-register.md` R01（口径变化）、R10（确认偏差）
- 验收测试：`docs/10-acceptance-tests.md` 2.1-2.5（数据层测试）
- MVP 计划：`docs/08-mvp-plan.md` Stage 1 指标口径录入任务

## 12. Stage 0 不做什么

- ❌ 不实施 `source_disagreement` 表（Stage 1）
- ❌ 不实现 Mahalanobis 匹配（Stage 3）
- ❌ 不实施同期群分析（Cohort Analysis）
- ❌ 不建立指标间的因果 DAG（Stage 3+）
- ❌ 不实现指标 schema 自动从源文件推断（Stage 2）

## 13. Stage 0 spike 验证后调整（增量）

> 此节记录 spike 期间发现的指标口径调整。

### 13.1 跨省 schema 差异导致的指标别名治理（来自 Spike 2）

**现象**：省 xlsx 用列式单位（unit 在 B 列），国家年鉴用行式单位（unit-row）。同一"规模以上工业增加值"在不同源中位置、单位、可获得性都不同。

**决策**：
1. **`indicator_alias` 表必须按 source 分组**（不是全局别名）：同一指标在 A 省可能叫"规上工业"，在 B 省叫"规上工业（含军工）"，别名不能强制统一
2. **每个 source 的 alias 必须单独验证**：通过 `indicator_alias.source_id` 关联 `source_document`，记录哪个源哪个别名指向哪个 indicator
3. **跨源比较时必须显示 alias 路径**：UI 上"GDP"指标展开时显示"国家统计局口径"/"湖北口径"/"广东口径" 三套数据并列

### 13.2 增长率指标的标准单位（来自 Spike 2）

**问题**：省 xlsx 的"工业增加值增长率"行无明确单位。

**决策**：
- **增长率**的 `unit_canonical='%'`，`comparison_basis='YOY_RATE'`
- **增速**和**增长量**严格区分：增速是 %, 增长量是绝对值（元）
- **百分点**（如利率变化、税率调整）和**百分比**严格区分：
  - 百分点：`unit='ppt'`（percentage point）
  - 百分比：`unit='%'`
- **YoY / QoQ / MoM** 用 `comparison_basis` 区分而非不同 indicator

### 13.3 标题与数据不一致的处理（来自 Spike 2）

**问题**：湖北月报标题"1-6月"实际数据是 Q2 单季。

**决策**：
- **永远不信标题**，必须看脚注/附注/隐藏 metadata
- 写 `source_document.caveat_text` 字段登记
- schema `comparison_basis` 已移除 `Q2_ONLY`（`schema/01-core.sql:94`）；spike 02 改为 per-indicator 周期元数据（`CUMULATIVE_5MONTH` / `PERIOD_END_OF_MONTH` 等，`TestR3PeriodMetadata`），不再强制单一 Q2 口径
- UI 显示时**同时显示标题 + caveat**，提示"标题写 X 实际是 Y"
- 跨期比较时强制 caveat 检查（per doc 10 测试 3.5 归因措辞）