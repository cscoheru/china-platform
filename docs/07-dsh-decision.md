# 07 — DSH 决策矩阵（DSH Three-Tier Decision Matrix）

> Stage 0 交付物 #07；对应 PRD 第 15 章第 9 项 + 第 8.3 节。
> 核心结论（详见第 6 节）：**核心 ETL/统计/数据仓库不依赖 DSH；DSH 作为可选研究 Agent sidecar 在 Stage 4 末再评估**。

## 1. 决策背景

### 1.1 什么是 DSH
- DSH（DeepSeek Harness）：Anthropic-style agent harness，可调用只读工具
- 适用于：研究编排、自然语言提问、报告草稿生成
- 不适用于：确定性 ETL、统计计算、数仓

### 1.2 为什么必须做这个决策
PRD 1.3 / 8.3 明确禁止把 DSH 当数据仓库。但**是否启用**以及**以何种方式启用**需要技术验证，不能空想。本文档给出三档决策矩阵。

### 1.3 决策时间窗
- Stage 1-3：**完全不引入** DSH（避免早期路径锁定）
- Stage 4：**通过技术验证决定**是否引入，以何种角色引入
- Stage 5：按 Stage 4 决策执行

## 2. 三档路线定义

### 2.1 路线 A：不使用 DSH（不启用）
- 完全不引入任何 LLM agent runtime
- 所有研究/查询走 SQL + API + Jupyter
- 报告生成用模板 + Python 脚本

### 2.2 路线 B：DSH 作为只读研究 Agent Sidecar
- DSH 作为独立容器部署
- 仅封装 11 个**只读工具**（per PRD 8.3 + 本文档 4 节）
- **不进入** ETL/统计计算路径
- Agent 与 DB 之间强制：白名单 SQL + 强制 source_id 返回
- Agent 输出必须能在 UI 上一键回放 evidence

### 2.3 路线 C：DSH 作为完整 Agent Runtime
- DSH 接管更多环节：指标建议生成、政策摘要、对比报告草稿
- 仍保持只读；不写 DB
- 假设承担更多"研究助理"角色

## 3. 决策矩阵（10 维度 × 3 路线）

每个维度评分：⭐ 1 / ⭐⭐ 2 / ⭐⭐⭐ 3 / ⭐⭐⭐⭐ 4 / ⭐⭐⭐⭐⭐ 5

| 维度 | A 不使用 | B Sidecar | C 完整 Runtime | 备注 |
|---|---|---|---|---|
| **D1 数据准确性**（不污染 observation） | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | A 最稳；C 风险最大 |
| **D2 审计可追溯**（每条结论可回 source） | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | A 强；C 难 |
| **D3 工程复杂度**（实施/运维） | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | A 简单；C 复杂 |
| **D4 PRD 1.3 合规**（红线） | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 三档都满足（只要不写库） |
| **D5 PRD 10.3 合规**（回答格式分层） | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | B/C 优势 |
| **D6 用户查询体验**（自然语言提问） | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | A 弱；C 强 |
| **D7 报告草稿生成** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | C 最强 |
| **D8 投入产出比**（ROI） | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | A 几乎零成本；C 需高投入 |
| **D9 失败模式可控**（幻觉/权限/成本爆炸） | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | A 0 幻觉风险；C 多 |
| **D10 长期演进**（可扩展到其他模型） | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | A/B 不绑定单一 runtime |
| **总分** | **46** | **39** | **33** | A > B > C |

### 关键观察
1. **A 在前 4 个"硬约束"维度全满分**——这是 PRD 红线要求
2. **B 在"用户查询体验"上显著优于 A**——这是 A 的主要弱点
3. **C 在 ROI 上明显偏低**——投入大、风险大、收益不确定
4. **三档总分接近**——决策本质是 trade-off，不是"哪档更好"

## 4. PRD 8.3 的 11 个只读工具（如果选 B/C）

这些工具**必须按 PRD 规格实现**，任何超出白名单的工具需 ADR 评估。

```python
# 工具清单（每个都强制返回 source_evidence）

@tool
def get_indicator_series(indicator: str, geo: str, period_range: tuple[str, str]) -> dict:
    """返回 (period, value, unit, source_id, vintage, confidence) 序列"""

@tool
def compare_regions(geo_list: list[str], indicators: list[str], period: str) -> dict:
    """返回对比表（含同类区间）"""

@tool
def get_indicator_definition(indicator: str) -> dict:
    """返回概念/单位/频率/口径版本/可比性说明"""

@tool
def get_source_evidence(source_id: str) -> dict:
    """返回原始 source_document + 定位"""

@tool
def search_policy_documents(query: str, filters: dict) -> list[dict]:
    """返回政策文件列表 + 高亮片段"""

@tool
def get_official_tenure(person_id: str) -> dict:
    """返回公开履历 + 任期时间线（不评价）"""

@tool
def get_commitment_progress(commitment_id: str) -> dict:
    """返回承诺 vs 当前进度（不评分）"""

@tool
def get_project_timeline(project_id: str) -> dict:
    """返回项目生命周期节点"""

@tool
def run_approved_analysis(analysis_id: str) -> dict:
    """执行已审批的分析（白名单内的）"""

@tool
def build_chart_spec(query: str) -> dict:
    """返回图表 spec（Vega-Lite），前端渲染"""

@tool
def draft_cited_report(question: str) -> dict:
    """生成带 evidence_id 链接的草稿"""
```

### 4.1 强制约束
- 11 个工具**只读**，无 write/update/delete
- 每个返回必须包含 `source_evidence: list[source_id]`
- 任何 SQL 通过白名单 query builder 生成（防 SQL 注入 + 防越权）
- Agent 进程对 DB 连接用**只读角色**
- 工具调用有 rate limit + audit log

### 4.2 不允许的工具（per PRD 8.3 末段）
- ❌ 任意 SQL 执行
- ❌ 任意文件读取
- ❌ 任意 HTTP 请求（除白名单域名）
- ❌ 直接访问生产数据库（必须走 API 层）
- ❌ 修改原始数据
- ❌ 发布无来源结论

## 5. Stage 4 技术验证方案（如果届时选 B/C）

### 5.1 验证集设计（必须做）
- 100 个真实研究问题样本（用户使用历史 + 模拟）
- 覆盖：宏观查询、地区对比、政策追溯、任期时间线、承诺兑现
- 每个问题有 ground truth（从 doc 04/05 schema 直接查）

### 5.2 评估指标
- **准确性**：返回数据的 source_id 是否都存在
- **可追溯性**：人工抽查 30%，每条结论能否 1 跳回 source
- **幻觉率**：返回的指标/数值/任期是否与 DB 一致
- **拒答率**：不该答时是否明确拒答
- **延迟**：P95 < 5s
- **成本**：每千次调用 token 消耗
- **权限违反次数**：0 是硬要求

### 5.3 决策门槛
- B 启用条件：幻觉率 <2%，可追溯率 ≥98%，成本可控
- C 启用条件：B 全部满足 + ROI 测算为正
- 任一不满足：降级到 A，直到满足为止

## 6. 最终建议

### 6.1 Stage 0 决策
**采用 B 作为远期方向，A 作为 Stage 1-3 的事实选择**。
- 即：现阶段**不实施** DSH（避免 Stage 1-3 路径锁定）
- 远期**预留** B 路线作为 Stage 4 评估对象
- **明确拒绝** C 作为远期方向（ROI 偏低、风险偏大、PRD 1.3 红线多）

### 6.2 理由

| 决策点 | 选择 | 理由 |
|---|---|---|
| Stage 1-3 | 不引入 DSH | PRD 1.3 红线 + 数据底座未稳，引入会污染路径 |
| Stage 4 评估对象 | B（sidecar） | 在保留 PRD 红线前提下提供研究体验提升 |
| 是否考虑 C | 否（至少 Stage 5 前不考虑） | 投入大、风险大、PRD 红线边缘 |

### 6.3 触发回滚到 A 的条件
- B 启用后幻觉率 >5%
- 任何权限违反事件
- 每月成本超过预算 2 倍
- 用户决定撤回研究 Agent 体验

## 7. 不做什么

- ❌ 不在 Stage 0 部署 DSH 容器
- ❌ 不在 Stage 1-3 写 DSH 工具实现
- ❌ 不把 DSH 作为 ETL 调度替代
- ❌ 不让 DSH 直接读写 observation 表
- ❌ 不让 DSH 跳过 API 层直连 DB

## 8. 相关 ADR

- 决策待 Stage 4 末定稿时写 `docs/adr/0001-dsh-sidecar-decision.md`
- 评估结果写 `docs/07-dsh-decision-evaluation.md`（Stage 4 末更新）
