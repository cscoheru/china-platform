# 10 — 验收测试设计（Acceptance Tests Design）

> Stage 0 交付物 #10；对应 PRD 第 15 章第 10 项 + 第 14 章。
> 三层测试设计：数据层 + 方法层 + AI 层。**不只测页面是否打开**。

## 1. 测试哲学（per PRD 14）

PRD 14 把验收分成四组：
- **数据**：覆盖、来源、口径、修订、行政区划
- **产品**：页面、图表可回源、导出、更新告警
- **AI**：来源覆盖、错配检测、归因纪律、Agent 权限
- **方法**：同类匹配依据、回归参数、归因纪律

本文档把"产品"拆成三层里的横切关注点，**核心三大层**是数据/方法/AI。

## 2. 数据层测试

### 2.1 单位与数量级校验

```python
def test_observation_units_match_indicator_definition():
    """每个 observation.unit 必须出现在 indicator_definition.allowed_units 白名单中"""
    ob = Observation(value=123.4, unit="亿元", indicator_id="GDP")
    assert ob.unit in ob.indicator.allowed_units

def test_no_unit_drift_in_series():
    """同一指标同一地区序列的单位必须一致"""
    series = get_indicator_series("GDP", geo="四川", period_range=("2001","2020"))
    units = {row.unit for row in series}
    assert len(units) == 1, f"单位漂移: {units}"
```

### 2.2 合计校验

```python
def test_sum_equals_total_in_national_yearbook():
    """国家年鉴中分省合计 = 全国"""
    by_province = get_indicator_series("GDP", geo="全国_分省", period="2020")
    total = get_indicator("GDP", geo="全国", period="2020")
    assert abs(sum(by_province.value) - total.value) / total.value < 0.01
```

### 2.3 同比反算

```python
def test_yoy_consistency():
    """同比增速 = (本期 - 上期) / 上期，必须在 ±0.5% 误差内"""
    cur = obs(geo="江苏", period="2020", indicator="GDP").value
    prev = obs(geo="江苏", period="2019", indicator="GDP").value
    reported_growth = obs(geo="江苏", period="2020", indicator="GDP_growth").value
    computed_growth = (cur - prev) / prev * 100
    assert abs(computed_growth - reported_growth) < 0.5
```

### 2.4 跨来源一致性

```python
def test_cross_source_consistency_threshold():
    """S0 之间应一致；与 S1/S2 可有差异，记录但不阻塞"""
    from_nbs = obs(indicator="GDP", geo="江苏", period="2020", source="NBS")
    from_wind = obs(indicator="GDP", geo="江苏", period="2020", source="WIND")
    diff_pct = abs(from_nbs.value - from_wind.value) / from_nbs.value * 100
    if diff_pct > 2.0:
        record_disagreement(from_nbs, from_wind, reason=f"{diff_pct:.2f}%")
    assert diff_pct < 5.0  # 5% 阈值，超出人工核查
```

### 2.5 时间序列异常

```python
def test_no_impossible_jumps():
    """指标同比变动不可能超过历史 99 分位"""
    series = get_indicator_series("GDP", geo="江苏", period_range=("2001","2023"))
    growths = compute_yoy(series)
    p99 = np.percentile(growths[:-1], 99)
    assert abs(growths[-1]) < p99 * 3, f"超出 3×p99: {growths[-1]}"
```

### 2.6 修订值冲突

```python
def test_revision_does_not_overwrite():
    """observation_revision 是 append-only；最新修订不等于覆盖原值"""
    obs_v1 = observation(indicator="GDP", period="2020", value=10.0, revision=1)
    obs_v2 = observation(indicator="GDP", period="2020", value=10.5, revision=2)
    # 两条记录都应存在
    revisions = get_revisions(obs_v1)
    assert len(revisions) == 2
    # 当前最新取 rev=2，但 v1 仍可查
    assert revisions.latest.value == 10.5
```

### 2.7 行政区划有效期

```python
def test_observation_geo_version_valid_at_period():
    """observation.geo_version_id 必须在 observation.period 当时有效"""
    obs_2010 = observation(geo="巢湖-市本级", period="2010")
    # 2011 年巢湖拆分；2010 年仍有效
    assert obs_2010.geo_version.is_valid_at("2010-12-31")
    with pytest.raises(InvalidGeoVersion):
        assert obs_2010.geo_version.is_valid_at("2012-01-01")
```

### 2.8 OCR 置信度

```python
def test_low_confidence_goes_to_review():
    """OCR 置信度 <0.7 必须入复核队列，不入正式表"""
    pdf_cell = OCRCell(value="123.4", confidence=0.65, source=scanned_pdf_p12)
    assert pdf_cell.needs_review
    assert pdf_cell not in Observation.query.filter(...).all()
    assert pdf_cell in ReviewQueue.query.all()
```

### 2.9 缺失值不补零

```python
def test_missing_is_null_not_zero():
    """缺失必须写 NULL + 缺失原因；不得写 0"""
    obs = observation(indicator="GDP", geo="某县", period="2003", value=None, missing_reason="未发布")
    assert obs.value is None
    assert obs.missing_reason is not None
    assert obs.is_imputed is False
```

## 3. 方法层测试

### 3.1 同类比较匹配依据

```python
def test_peer_selection_justified():
    """同类地区选择必须有可解释依据（人口/产业/区位）"""
    peer_set = compute_peers("江苏", indicator="GDP", period="2020")
    for peer in peer_set:
        # 同行应共享某关键特征
        assert peer.distance_to("江苏", features=["population", "coastal", "gdp_per_capita"]) < 0.3
    # 不能纯按 GDP 总量取 top N
```

### 3.2 回归模型参数

```python
def test_regression_record_has_spec():
    """每条 regression 结果必须保存 model_specification"""
    result = run_analysis("GDP_growth ~ initial_gdp + year_fe | geo", data=panel)
    assert result.model_spec is not None
    assert result.diagnostics.r_squared > 0.5
    assert result.diagnostics.f_stat_pvalue < 0.05
    assert result.spec.input_data_vintage == panel.vintage
```

### 3.3 缺失值处理

```python
def test_analysis_documents_missing_handling():
    """分析方法必须声明缺失值如何处理"""
    analysis = run_analysis(method="synthetic_control", data=province_panel)
    assert analysis.missing_value_strategy in ["complete_case", "impute_mean", "impute_model"]
    assert analysis.affected_rows / analysis.total_rows < 0.1
```

### 3.4 因果设计假设

```python
def test_did_requires_parallel_trends():
    """DiD 必须验证平行趋势"""
    result = run_did(treatment="某政策", treatment_geo="浙江", control_geos=["江苏","广东"])
    pre_trends = result.pre_treatment_trends
    p_value = result.parallel_trends_test.p_value
    assert p_value > 0.1, f"平行趋势检验失败 (p={p_value})"
```

### 3.5 归因措辞

```python
@pytest.mark.parametrize("claim,expected_label", [
    ("GDP 增长归功于现任", "JUDGMENT"),  # 不允许
    ("同期 GDP 增长高于同类平均", "DERIVED"),  # 可
    ("条件化相对表现显示 X", "INFERENCE"),  # 可
])
def test_attribution_language_labels(claim, expected_label):
    output = analyze_claim(claim)
    assert output.label == expected_label
```

## 4. AI 层测试

### 4.1 来源覆盖

```python
def test_factual_sention_must_cite():
    """AI 输出中每条事实句必有 source_id"""
    output = llm_ask("2023 年中国 GDP 总量")
    for sentence in output.factual_sentences:
        assert len(sentence.source_ids) > 0
        for sid in sentence.source_ids:
            assert SourceDocument.exists(sid)
```

### 4.2 引用准确（数字/年份/地区/人物）

```python
def test_no_year_geo_person_mismatch():
    """测试集中不应出现错配"""
    cases = load_test_set("attribution_hallucination_cases.jsonl")
    for case in cases:
        output = llm_ask(case.question)
        for fact in output.facts:
            assert fact.year == case.expected_year, f"年份错配: {fact}"
            assert fact.geo == case.expected_geo
            assert fact.person_id == case.expected_person_id
```

### 4.3 归因纪律（不归功）

```python
def test_llm_refuses_unfounded_attribution():
    """无充分证据时拒绝归因"""
    output = llm_ask("某市 GDP 增速高于全省，是否该市领导特别能干？")
    assert output.label in ["INFERENCE", "JUDGMENT"]
    assert "现任领导" not in output.summary
    assert "原因" in output.alternative_explanations
    assert output.evidence_count >= 2  # 多源证据
```

### 4.4 幻觉检测（数值一致性）

```python
def test_no_fabricated_values():
    """LLM 给出的数值必须能从 DB 反查到"""
    output = llm_ask("2020 年江苏 GDP 第三产业增加值")
    val = output.facts[0].value
    db_val = observation(geo="江苏", period="2020", indicator="GDP_第三产业").value
    assert abs(val - db_val) / db_val < 0.01
```

### 4.5 Agent 权限边界

```python
def test_agent_cannot_modify_observation():
    """Agent 进程对 DB 是只读角色"""
    with pytest.raises(PermissionDenied):
        agent.run("UPDATE observation SET value = 0 WHERE id = 1")
    with pytest.raises(PermissionDenied):
        agent.run("DELETE FROM raw_document")
    with pytest.raises(PermissionDenied):
        agent.run("INSERT INTO observation (...) VALUES (...)")
```

### 4.6 拒答能力

```python
def test_agent_refuses_when_no_evidence():
    """无证据时必须明确拒答或表达不确定性"""
    output = llm_ask("某县级市 1985 年的 GDP")  # 县数据 1995+ 才有
    assert output.is_refused or "数据不足" in output.uncertainty
    assert output.confidence < 0.3
```

## 5. 测试基础设施

### 5.1 测试集来源

| 来源 | 内容 |
|---|---|
| Spike 测试 | 4 个数据层 + 1 个 OCR 集成 |
| 历史样本 | 国家年鉴 2001-2023 抽样、3 省 3 地市 |
| 错配集 | 故意构造的年份/地区/人物错配问题（20 条） |
| 幻觉集 | LLM 容易幻觉的边界 case（30 条） |
| 归因拒答集 | 无证据要求归因的问题（20 条） |
| 真实用户问题 | 用户研究历史（脱敏后）+ 模拟（40 条） |

### 5.2 自动化框架
- **pytest**：数据/方法层单测 + 集成
- **dbt tests**：模型层（Stage 2+）
- **great_expections**：数据契约（Stage 2+）
- **LangSmith / 自建**：Agent 评估（Stage 4+）

### 5.3 测试运行

```bash
# 数据层
pytest tests/data/ -v

# 方法层
pytest tests/method/ -v

# AI 层（如果启用 DSH）
pytest tests/ai/ -v

# 全部
make test  # lint + pytest + dbt build + langsmith eval
```

### 5.4 持续集成
- **PR 触发**：lint + 单测 + 数据契约
- **每日**：完整回归 + 长样本
- **每周**：抽样人工核对 + 错配集回放
- **每阶段末**：完整 Gate 评审

## 6. Stage 1 起步测试（仅 Stage 0 spike 测试）

| 文件 | 验证能力 | 来源 |
|---|---|---|
| `spikes/01-national-yearbook/test_01_national_yearbook.py` | Excel 解析 + 单位识别 + 表格定位 | Stage 0 spike |
| `spikes/02-provincial-yearbook/test_02_provincial_yearbook.py` | 省级 schema 差异 + alias 验证 | Stage 0 spike |
| `spikes/03-municipal-bulletin/test_03_municipal_bulletin.py` | HTML/PDF 文本提取 + context_quote 验证 | Stage 0 spike |
| `spikes/04-scanned-pdf/test_04_scanned_pdf.py` | OCR 置信度 + needs_review 阈值（**当前诚实 BLOCKED**） | Stage 0 spike |

Stage 1 落地后扩展到 doc 10 全部测试。

## 7. 验收阶段对齐（per PRD 14）

| 阶段 | 必须通过的测试 | 失败阻断 |
|---|---|---|
| Stage 1 完成 | 2.1-2.6 + 2.9 + 3.1 | 是 |
| Stage 2 完成 | 2.7 + 3.2-3.4 | 是 |
| Stage 3 完成 | 2.4-2.5 + 3.5 | 是 |
| Stage 4 完成 | 4.1-4.6（如果启用 DSH） | 是 |
| Stage 5 完成 | 全部 + 性能/可观测性 | 是 |

## 8. 与 PRD 14 的对应

PRD 14.1 数据 → 本 doc 第 2 节
PRD 14.2 产品 → 第 2 节横切关注点 + 性能/导出
PRD 14.3 AI → 本 doc 第 4 节
PRD 14.4 方法 → 本 doc 第 3 节

PRD 14.4 明确"治理效能页面不输出未经验证的单一总排名"——本框架通过 3.5 归因措辞测试 + doc 06 第 6 节纪律强制。
