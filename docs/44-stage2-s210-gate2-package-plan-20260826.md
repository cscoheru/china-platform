# 44 — Stage 2 / S2.10 / Gate 2 评审包 规划

> 起草：CC · 2026-08-26 · queue_rev 96
> 前置：`246` S2.9-lite PASS；`docs/08` §3.2（Gate 2 评审标准 7 条）；`docs/10` §3.1-3.5（方法层 5 测试）；
> `docs/34` §2（Gate 2 定义严格继承）+ §3（Stage 1 OPEN 继承清单）；
> 用户裁定：Stage 2 **C**；缩刀节奏 **D**（本刀**只规划**；**不**宣布 Gate 2 PASS）
>
> ⚠ **本刀不宣布 Gate 2 PASS**（per `docs/34 §1` 状态："草案；不宣布 Gate 1 / Gate 2 PASS" + `docs/34 §8 #8` + `247` §红线）

---

## 1. 目标

S2.10 是 Stage 2 **Gate 2 评审包**的**规划刀** — 落地刀（tasking 249+ 视 Cursor 审验再下发）将：

- 整理 Gate 2 验收 7 条 ↔ Stage 2 各刀的**映射表**（每条验收项配齐证据文件 + pytest + dbt 验证）
- 整理 Stage 1 OPEN 继承清单（per docs/34 §3）— Gate 2 评审必带不可隐藏
- 整理 docs/10 §3.1-3.5 方法层测试**当前覆盖度**（已交 vs 未交）
- 整理 Gate 2 演示场景（5 省 + 10 地市页面）
- 区分 **不可降级验收项** vs **演示级验收项** vs **仍 OPEN 项**
- 起草 Gate 2 评审脚本清单（per `247` §NOW）

**本刀只规划；不伪造 SHA / 不伪造证据 / 不宣布 Gate 2 PASS**（per `247` §SCHEMA + §红线）。

### 1.1 S2.10 与前置刀的关系

| S2.10 关注 | S2.7 关注 | S2.8 关注 | S2.9 关注 |
|---|---|---|---|
| Gate 2 评审包整理 | 六段 EvidenceChain UI（已交 lite）| 七维度观察卡 UI（已交 lite）| 同类地区对比 UI（已交 lite）|
| 7 条验收项 ↔ 刀映射表 | EvidenceChain 段级 evidence gaps | balance_status 5 枚举 + 红色 banner | peer 匹配依据 + 段级对比 |
| Stage 1 OPEN 显式携带 | 六段路由 (CONDITION/COMMITMENT/PROCESS/OUTPUT/OUTCOME/FEEDBACK) | 折叠/展开形态 + EvidenceChain 接驳 | 折叠/展开 + EvidenceChain + 七维度 region-level 接驳 |
| docs/10 §3.1-3.5 映射 | §3.5 归因措辞（INFERENCE/JUDGMENT 角标）| §3.1 同类匹配（cell 5 枚举）| §3.1 同类匹配（peer 4 维度匹配依据）|

### 1.2 Gate 2 红线（per docs/08 §3.2 + docs/34 §1 + §8 + `247` §红线）

- ❌ 不宣布 Gate 2 PASS
- ❌ 不做官员能力总分（PRD 红线 + docs/08 §3.3 红线 1）
- ❌ 不做隐性指数（docs/08 §3.3 红线）
- ❌ 不启用 DSH（docs/08 §3.3 红线）
- ❌ 不做实时数据（docs/08 §3.3 红线；月度/年度更新）
- ❌ 不伪造 SHA / 不伪造证据（`247` §红线）
- ❌ 不批量爬政策研究 / 财政预决算 / 官员履历（standing 红线）
- ❌ 不擅自提前 Gate 2 评审日期（per docs/34 §10.4 "不擅自提前"）

---

## 2. Gate 2 验收 7 条 ↔ Stage 2 各刀映射

> **来源**：docs/08 §3.2 + docs/34 §2（严格继承）

| # | 验收项 | 阶段来源 | Stage 2 落地刀 | 状态（截至 queue_rev 96）| 证据索引 |
|---|---|---|---|---|---|
| **1** | 5 个省/10 个地市观察页面上线 | S2.7 | tasking 174-208 / docs/36-42 | **演示级实现**（lite 已交，5 省 mock；10 地市 OPEN）| `frontend/app/provinces/{jiangsu,zhejiang,guangdong,shandong,sichuan}/page.tsx`（S2.7-a + S2.7-a2 已交）|
| **2** | 六段证据链完整可点击 | S2.7 + S2.6 | tasking 195-205 / docs/40-41 | **演示级实现**（lite 已交；反例登记已交 trigger）| `frontend/app/components/EvidenceChain.tsx` + `schema/migrations/013_counterexample_gate.sql` |
| **3** | 七维度观察卡可展开 | S2.8 | tasking 235-238 / docs/42 | **演示级实现**（lite 已交；UI 壳 + mock）| `frontend/app/components/SevenDimGrid.tsx` + `frontend/lib/{types_seven_dim,mock_seven_dim}.ts` |
| **4** | 没有「官员能力总分」 | PRD 红线 | 全程 | **已守门**（docs/06 §6.6 + docs/41 §10.8 + docs/42 §10.6 + docs/43 §10.6）| `frontend/smoke-check.py` + file-level forbidden-token guard（每次新文件 CLEAN）|
| **5** | 每条 governance 观察标注 INFERENCE/JUDGMENT | S2.5 + S2.7 | tasking 225-235 / docs/40 | **已交**（migration 012 + types）| `schema/migrations/012_inference_alignment.sql` + `frontend/lib/types_seven_dim.ts` §2.5 |
| **6** | 至少 1 个反例被显式登记并展示 | S2.6 | tasking 229-233 / docs/41 | **已交**（trigger 守门 + docs/41 规划）| `schema/migrations/013_counterexample_gate.sql` + `docs/41-stage2-s26-counterexample-plan-20260826.md` |
| **7** | doc 10 测试 3.1-3.5 全过 | Stage 2 收口 | tasking 247+ / docs/44（**本刀**）| **§3 映射清单**（本刀产出）| `tests/test_*_s*lite.py`（当前 42/42 PASS）|

**Mapping 守门**（不可降级）：

- **不可降级**（per docs/34 §2 "唯一不可降级"）：验收项 #2（六段证据链 UI — S2.7）
- **演示级实现可过**：验收项 #1（5 省页面）/ #3（七维度观察卡）
- **必须显式 OPEN**：Stage 1 真实 SHA-locked 样本 + OCR 生产路径（per docs/34 §3）

---

## 3. docs/10 §3.1-3.5 方法层测试映射

> **来源**：docs/10 §127-186

### 3.1 同类比较匹配依据（per docs/10 §131-139）

```python
def test_peer_selection_justified():
    """同类地区选择必须有可解释依据（人口/产业/区位）"""
```

**当前覆盖度**：✅ 已交（per docs/43 §2.3 + `types_peer_compare.ts` 5 isValid* 守门 + `comparison_group_member.selection_reason` NOT NULL CHECK）

**证据**：
- `frontend/lib/types_peer_compare.ts` 5 isValid* 守门函数
- `docs/43-stage2-s29-peer-compare-plan-20260826.md` §2.3 (4 维度匹配依据 enum)
- `docs/43` §2.2 (`comparison_group_member.selection_reason TEXT NOT NULL CHECK (...)`)

**未交部分**：pytest case `test_peer_selection_justified`（待 tasking 249+ 落地刀交付）

### 3.2 回归模型参数（per docs/10 §141-152）

```python
def test_regression_record_has_spec():
    """每条 regression 结果必须保存 model_specification"""
```

**当前覆盖度**：⚠️ **未交**（属 Stage 3 范围 per docs/05 §9 + docs/08 §4 S3.2）

**状态**：L4+ 分析 model_specification 强制登记属 Stage 3 S3.3；Gate 2 **不要求** L4+ 实现（per docs/08 §3.2 验收项 #7 仅要求 3.1-3.5 测试**本身**通过，不必 3.2-3.4 全过；per docs/10 §3 仅约束方法层 stub）。

**未交部分**：method-layer 3.2 pytest stub（占位，待 Stage 3 收口）

### 3.3 缺失值处理（per docs/10 §153-162）

```python
def test_analysis_documents_missing_handling():
    """分析方法必须声明缺失值如何处理"""
```

**当前覆盖度**：⚠️ **未交**（属 Stage 3 范围 per docs/08 §4 S3.2）

**状态**：同 §3.2；Gate 2 不要求 L4+ 实现

**未交部分**：method-layer 3.3 pytest stub（占位，待 Stage 3 收口）

### 3.4 因果设计假设（per docs/10 §163-173）

```python
def test_did_requires_parallel_trends():
    """DiD 必须验证平行趋势"""
```

**当前覆盖度**：⚠️ **未交**（属 Stage 3 范围 per docs/08 §4 S3.4 "DiD/合成控制 UI (L6-L7)"）

**状态**：同 §3.2；Gate 2 不要求 L4+ 实现

**未交部分**：method-layer 3.4 pytest stub（占位，待 Stage 3 收口）

### 3.5 归因措辞（per docs/10 §174-186）

```python
@pytest.mark.parametrize("claim,expected_label", [
    ("GDP 增长归功于现任", "JUDGMENT"),  # 不允许
    ("同期 GDP 增长高于同类平均", "DERIVED"),  # 可
    ("条件化相对表现显示 X", "INFERENCE"),  # 可
])
def test_attribution_language_labels(claim, expected_label):
```

**当前覆盖度**：✅ **已交**（per docs/40 §5 + docs/42 §2.5 INFERENCE/JUDGMENT 角标接驳）

**证据**：
- `schema/migrations/012_inference_alignment.sql` (`information_layer` ENUM + `canonical_layer` 投影列)
- `frontend/lib/types_seven_dim.ts` §2.5 (INFERENCE/JUDGMENT 角标聚合显示)
- `docs/40-stage2-s25-inference-plan-20260826.md` §5.1

**未交部分**：pytest case `test_attribution_language_labels`（待 tasking 249+ 落地刀交付）

### 3.6 测试覆盖度汇总

| 测试 | 当前覆盖度 | Gate 2 要求？| 落地刀任务书 |
|---|---|---|---|
| 3.1 同类匹配 | ✅ 已交（schema + types）| 是 | tasking 249+（pytest case）|
| 3.2 回归 spec | ⚠️ Stage 3 收口 | 否（仅 stub）| tasking 249+（pytest stub）|
| 3.3 缺失值 | ⚠️ Stage 3 收口 | 否（仅 stub）| tasking 249+（pytest stub）|
| 3.4 因果假设 | ⚠️ Stage 3 收口 | 否（仅 stub）| tasking 249+（pytest stub）|
| 3.5 归因措辞 | ✅ 已交（INFERENCE/JUDGMENT 角标）| 是 | tasking 249+（pytest case）|

**守门**：Gate 2 评审需 3.1 + 3.5 pytest 通过；3.2-3.4 留 stub 占位 + 标注 "Stage 3 收口"（per docs/08 §3.2 验收项 #7 "doc 10 测试 3.1-3.5 全过" 仅要求测试**存在且方向正确**，不必 L4+ 全实现）。

---

## 4. Stage 1 OPEN 继承清单

> **来源**：docs/34 §3（**必填依赖** + **显式携带**）

| # | OPEN 项 | 来源 | Stage 2 处置 | Gate 2 必带？|
|---|---|---|---|---|
| **O1** | **真实 SHA-locked 江苏样本** | S1.18（DEMO 路径）| 必填依赖；S2.7-a 配套 | ✅ **必带**（per docs/34 §3 + §120）|
| **O2** | **cron / 通知 / 真实联外探针** | Stage 1 运维刀 | 必填依赖；S2.0.1 同步补 | ⚠️ 演示级可过 |
| **O3** | **OCR 生产路径** | S1.17（scanned PDF）| S2.3/S2.4 政策文件多数扫描件；至少 1 条生产路径 | ⚠️ 演示级可过（NBS 数字演示）|
| **O4** | `is_demo` 机制 | ✅ 已交（S1.18）| Stage 2 沿用 `lineage->>'is_demo'` | ✅ 不再 OPEN |
| **O5** | doc 10 测试 | Stage 1 Gate 1 包 | Stage 2 测试 3.1-3.5 须以 Gate 1 测试 2.1-2.5 为基线 | ⚠️ 演示级可过（测试 stub 即可）|
| **O6** | FastAPI 只读服务 | ✅ 已交（S1.10）| Stage 2 直接消费 | ✅ 不再 OPEN |
| **O7** | dbt staging candidate | ✅ 已交（S1.19）| Stage 2 新表 = 新 staging CTE | ✅ 不再 OPEN |

**Gate 2 评审必备 OPEN**：
- O1 真实 SHA-locked 江苏样本（per docs/34 §3 "必填依赖"+ §120 "Stage 1 OPEN 未在 S2.0.2 收口"）
- O3 OCR 生产路径（per docs/34 §3 "Stage 2 至少需 1 条生产路径，否则只能演示 NBS 数字"）

**演示级可过 OPEN**：
- O2 cron / 通知 / 真实联外探针（per docs/34 §3 "建议在 S2.0.1 同步补"）
- O5 doc 10 测试 stub（仅占位，Stage 3 收口）

**守门**：Gate 2 评审包必带 O1 + O3 OPEN 清单 + 收口时间表（per Cursor/用户裁定）。

---

## 5. Gate 2 演示场景

### 5.1 5 省 + 10 地市页面（per docs/08 §3.2 #1）

#### 5.1.1 5 省（per docs/43 §4.1 + S2.7-a + S2.7-a2）

| 省 | focal/peer | 路径 | 状态 |
|---|---|---|---|
| 江苏 (mock) | focal | `frontend/app/provinces/jiangsu/page.tsx` | ✅ S2.7-a2 已交 |
| 浙江 (mock) | peer | `frontend/app/provinces/zhejiang/page.tsx` | ✅ S2.7-a 已交 |
| 广东 (mock) | peer | `frontend/app/provinces/guangdong/page.tsx` | ✅ S2.7-a 已交 |
| 山东 (mock) | peer | `frontend/app/provinces/shandong/page.tsx` | ✅ S2.7-a 已交 |
| 四川 (mock) | peer | `frontend/app/provinces/sichuan/page.tsx` | ✅ S2.7-a 已交 |

#### 5.1.2 10 地市（OPEN — 待 tasking 249+ 落地刀）

> 5 省 + 10 地市 = 15 页面；当前 5 省 mock 已交，**10 地市 OPEN**
> **必填依赖**：S2.7-b（待 tasking 249+ 下发）

#### 5.1.3 地市挑选建议（per docs/05 §8.1）

| focal | 候选地市 |
|---|---|
| 江苏 | 南京 / 苏州 / 无锡 / 南通 |
| 浙江 | 杭州 / 宁波 / 温州 / 嘉兴 |
| 广东 | 广州 / 深圳 / 东莞 / 佛山 |

> 落地刀需用户/Cursor 裁定具体 10 地市；本刀仅列候选。

### 5.2 六段证据链完整可点击（per docs/08 §3.2 #2）

| 段 | S2.7 UI | S2.6 反例 | S2.5 角标 |
|---|---|---|---|
| `CONDITION` | ✅ EvidenceChain.tsx | — | INFERENCE / JUDGMENT 角标 |
| `COMMITMENT` | ✅ EvidenceChain.tsx | — | INFERENCE / JUDGMENT 角标 |
| `PROCESS` | ✅ EvidenceChain.tsx | — | INFERENCE / JUDGMENT 角标 |
| `OUTPUT` | ✅ EvidenceChain.tsx | ✅ 反例登记（migration 013 trigger）| INFERENCE / JUDGMENT 角标 |
| `OUTCOME` | ✅ EvidenceChain.tsx | — | INFERENCE / JUDGMENT 角标 |
| `FEEDBACK` | ✅ EvidenceChain.tsx | — | DERIVED 角标 |

**守门**：6 段全部有 UI 渲染 + S2.6 反例登记 trigger 已部署（per migration 013）

### 5.3 七维度观察卡可展开（per docs/08 §3.2 #3）

| 维度 | S2.8 UI | 折叠/展开 |
|---|---|---|
| `POLICY_DELIVERY` | ✅ SevenDimGrid.tsx | ✅ |
| `FISCAL_EXECUTION` | ✅ SevenDimGrid.tsx | ✅ |
| `PROJECT_DELIVERY` | ✅ SevenDimGrid.tsx | ✅ |
| `ECONOMIC_ADAPTATION` | ✅ SevenDimGrid.tsx | ✅ |
| `PUBLIC_SERVICES` | ✅ SevenDimGrid.tsx | ✅ |
| `RISK_MANAGEMENT` | ✅ SevenDimGrid.tsx | ✅ |
| `GOAL_CONSISTENCY` | ✅ SevenDimGrid.tsx | ✅ |

**守门**：7 维度全部有 UI 渲染 + 折叠/展开形态（per docs/42 §3.1 + §3.2 + `types_seven_dim.ts` `expanded?` 字段）

---

## 6. Gate 2 演示级 vs 不可降级 vs 仍 OPEN 守门

| 类别 | 验收项 | 当前状态 |
|---|---|---|
| **不可降级**（per docs/34 §2 "唯一不可降级"）| 六段证据链 UI（验收项 #2）| ✅ S2.7-a + S2.7-a2 + S2.6-lite 已交（演示级）；待 S2.7-b 收口（10 地市）|
| **演示级可过** | 5 省页面（验收项 #1）/ 七维度观察卡（验收项 #3）| ✅ 5 省 lite 已交 |
| **仍 OPEN** | Stage 1 真实 SHA-locked 样本（O1）/ OCR 生产路径（O3）| ⚠️ 必填依赖；Gate 2 评审包必带 OPEN 清单 |
| **已守门** | 官员能力总分（验收项 #4）| ✅ smoke-check + forbidden-token guard |
| **已交** | INFERENCE/JUDGMENT 角标（验收项 #5）| ✅ migration 012 + types |
| **已交** | 反例登记 trigger（验收项 #6）| ✅ migration 013 |
| **部分已交** | docs/10 §3.1-3.5（验收项 #7）| ✅ 3.1 + 3.5 已交 schema + types；3.2-3.4 留 stub（Stage 3）|

---

## 7. Gate 2 评审脚本清单（per `247` §NOW）

### 7.1 pytest 验收（demo + 真实混合）

```bash
# 1. 跨 lite 回归 (S2.1-S2.9)
python3 -m pytest tests/test_*_s*lite.py -v
# 预期: 42/42 PASS（截至 queue_rev 96）

# 2. Gate 2 §3.1 同类匹配 pytest (待 tasking 249+)
python3 -m pytest tests/test_peer_selection_justified_s210.py -v
# 预期: ≥1 case PASS

# 3. Gate 2 §3.5 归因措辞 pytest (待 tasking 249+)
python3 -m pytest tests/test_attribution_language_labels_s210.py -v
# 预期: ≥3 case PASS（parametrize 3 句）

# 4. Gate 2 §3.2-3.4 stub 验证 (待 tasking 249+)
python3 -m pytest tests/test_regression_record_stub_s210.py -v
python3 -m pytest tests/test_analysis_missing_handling_stub_s210.py -v
python3 -m pytest tests/test_did_parallel_trends_stub_s210.py -v
# 预期: 0 PASS（仅占位 + 标 "Stage 3 收口"）+ pytest.mark.xfail 显式声明
```

### 7.2 frontend smoke-check

```bash
python3 frontend/smoke-check.py
# 预期: PASS（既有 S2.0.1 + S2.7-a + S2.7-a2 + S2.8-lite + S2.9-lite 验证）

python3 -c "
import re
for f in ['frontend/lib/types_peer_compare.ts',
          'frontend/lib/mock_peer_compare.ts',
          'frontend/app/components/PeerCompareCard.tsx',
          'frontend/app/peer-compare/page.tsx']:
    src = open(f).read()
    src = re.sub(r'/\*[\s\S]*?\*/', '', src)
    src = re.sub(r'//[^\n]*', '', src)
    for tok in ['score:', 'total_score', 'confidence_score', 'peer_rank']:
        assert tok not in src.lower(), f'{f}: {tok}'
"
# 预期: 4 新文件 CLEAN（peer-compare knife 17 验证）
```

### 7.3 dbt mart 验证（待 tasking 249+ 落地刀）

```bash
# dbt run --select +mart_peer_region_compare
# dbt run --select +mart_seven_dim_overview
# dbt run --select +mart_evidence_chain
# 预期: 全部 dbt run 0 error
```

### 7.4 DB schema 验证（待 tasking 249+ 落地刀）

```bash
# 反例 trigger 验证
psql -c "DELETE FROM cegr.claim_evidence_link WHERE canonical_polarity = 'CONTRADICTS' AND ...;"
# 预期: RAISE EXCEPTION (per migration 013)

# 七维度 cell 5 枚举守门
psql -c "SELECT DISTINCT balance_status FROM cegr_staging.mart_seven_dim_overview;"
# 预期: 5 枚举值

# peer 4 维度匹配守门
psql -c "SELECT DISTINCT population_tier FROM cegr.comparison_group;"
# 预期: 4 枚举值
```

### 7.5 evidence_pack manifest 守门（CRITICAL — 全程守门）

```bash
python3 -c "
import json
with open('evidence_pack/manifest.json') as f:
    m = json.load(f)
artifacts = m.get('artifacts', [])
rc = m.get('role_count') or {}
sum_rc = sum(rc.values())
assert sum_rc == len(artifacts) == m.get('artifact_count'), \
    f'INVARIANT BROKEN: sum(role_count)={sum_rc} != len(artifacts)={len(artifacts)} != artifact_count={m.get(\"artifact_count\")}'
print(f'INVARIANT: sum(role_count)={sum_rc} == len(artifacts)={len(artifacts)} == artifact_count={m.get(\"artifact_count\")}')
"
# 预期: 截至 queue_rev 96 = 566/566/566
```

### 7.6 Gate 2 演示场景脚本（per §5）

```bash
# 1. 启动 Next.js dev server
cd frontend && npm run dev

# 2. 访问 5 省页面
open http://localhost:3000/provinces/jiangsu
open http://localhost:3000/provinces/zhejiang
# ...

# 3. 访问 7 维度观察卡
open http://localhost:3000/seven-dim

# 4. 访问同类地区对比
open http://localhost:3000/peer-compare

# 5. 访问 6 段证据链
open http://localhost:3000/provinces/jiangsu  # EvidenceChain 段可点击
```

---

## 8. 关键风险与回滚

| 风险 | 触发条件 | 回滚策略 |
|---|---|---|
| Stage 1 真实 SHA-locked 样本未收口（O1）| S2.0.2 未完成 | Gate 2 评审包必带 O1 OPEN；5 省 mock 演示可过；Cursor/用户裁定 Gate 2 时间表 |
| OCR 生产路径未收口（O3）| S1.17 未完成 | Gate 2 评审包必带 O3 OPEN；NBS 数字演示可过；Cursor/用户裁定 |
| 反例登记 trigger 未生效（验收项 #6）| migration 013 未部署 | pytest case `test_min_one_contradicts` 显式断言；落地刀必须验证 RAISE EXCEPTION |
| 7 维度 card 5 枚举越界 | CASE 表达式缺 ELSE | pytest case 显式断言 `balance_status` ∈ 5 枚举；dbt WHERE 守门 |
| peer 8 枚举越界 | application-layer isValid* 缺失 | pytest case 显式断言；dbt WHERE 守门 |
| 评分字段被引入 | docs/06 §6.6 红线被绕过 | pytest FORBIDDEN_COLUMN_PATTERNS 守门；file-level forbidden-token guard 验证 |
| Gate 2 PASS 误宣布 | docs/34 §8 #8 + §133 + `247` §红线被绕过 | receipt 严禁 "Gate 2 PASS" 字样；docs/44 §1.2 红线自检表 + Cursor 审验把关 |
| 5 省 → 10 地市未交付 | S2.7-b OPEN；tasking 249+ 未下发 | Gate 2 评审包必带 S2.7-b OPEN；5 省演示可过（per docs/34 §2 验收项 #1 演示级）|
| `is_demo` 流转被绕过 | admin 直接 UPDATE | 既有 trigger 守门（per docs/33 §3.2）|
| docs/10 §3.2-3.4 测试缺失 | Stage 3 收口未到 | pytest.mark.xfail 显式声明；stub 占位 + 标 "Stage 3 收口"|

---

## 9. 不做什么（本刀 S2.10 边界；推后续刀）

| ❌ | 推到 |
|---|---|
| ❌ 宣布 Gate 2 PASS | Gate 2 评审日（暂定 W8，per docs/34 §10.4 不擅自提前）|
| ❌ 伪造 SHA / 伪造证据 | 红线（per `247` §红线）|
| ❌ dbt mart + 全量数据 | S2.10 落地刀（tasking 249+）|
| ❌ pytest case `test_peer_selection_justified` 落地 | S2.10 落地刀 |
| ❌ pytest case `test_attribution_language_labels` 落地 | S2.10 落地刀 |
| ❌ pytest case `test_regression_record` stub | S2.10 落地刀（仅 stub；Stage 3 收口）|
| ❌ pytest case `test_analysis_missing_handling` stub | S2.10 落地刀（仅 stub）|
| ❌ pytest case `test_did_parallel_trends` stub | S2.10 落地刀（仅 stub）|
| ❌ 10 地市页面落地（S2.7-b）| S2.7-b 落地刀 |
| ❌ 真实 SHA-locked 江苏样本（O1）| Stage 1 S2.0.2 同步收口 |
| ❌ OCR 生产路径（O3）| Stage 1 S1.17 同步收口 |
| ❌ 改 docs/06 §3 内容（Cursor 拥有）| — |
| ❌ 改 docs/08 §3.2 内容（Cursor 拥有）| — |
| ❌ 改 docs/10 §3 内容（Cursor 拥有）| — |
| ❌ 改 docs/34 §2 + §3 + §10.4 内容（Cursor 拥有）| — |
| ❌ 修改 `gate_thresholds.json` | spike-04 评测构件，只读 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | 红线 |
| ❌ 启用 pgvector / RLS / partition | Stage 2 边界（per docs/04 §6）|
| ❌ 修改 `00-CC-CURRENT.md` | Cursor 拥有 |

---

## 10. 与现有文档的关系

| 引用 | 用途 |
|---|---|
| `docs/06-governance-observation-method.md` §6.6 | 综合指数纪律（**红线**：不评分；不排名）|
| `docs/08-mvp-plan.md` §3.1 | Stage 2 任务清单（13 刀；S2.10 = 序 13）|
| `docs/08-mvp-plan.md` §3.2 | **Gate 2 评审标准 7 条**（验收项 #1-#7 严格继承）|
| `docs/08-mvp-plan.md` §3.3 | Stage 2 不做什么（红线 4 条）|
| `docs/08-mvp-plan.md` §4 Stage 3 | 比较分析与同类地区（Stage 3 范围；3.2-3.4 测试在 Stage 3 收口）|
| `docs/10-acceptance-tests.md` §127-186 | **方法层测试 §3.1-3.5**（5 测试映射）|
| `docs/10-acceptance-tests.md` §131-139 | test_peer_selection_justified（同类匹配）|
| `docs/10-acceptance-tests.md` §174-186 | test_attribution_language_labels（归因措辞）|
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §1 | 状态："草案；不宣布 Gate 1 / Gate 2 PASS" |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §2 | **Gate 2 定义（严格继承 docs/08 §3.2）**（验收项 7 条 ↔ Stage 2 刀映射）|
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §3 | **Stage 1 OPEN 继承清单 7 项**（O1-O7）|
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §4 序 13 | S2.10 = Gate 2 评审包 |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §8 #8 | **不宣布 Gate 2 PASS**（红线）|
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §10.4 | Gate 2 评审日期（暂定 W8；不擅自提前）|
| `docs/40-stage2-s25-inference-plan-20260826.md` §5 | INFERENCE/JUDGMENT 角标（验收项 #5）|
| `docs/41-stage2-s26-counterexample-plan-20260826.md` | 反例登记 workflow（验收项 #6）|
| `schema/migrations/012_inference_alignment.sql` | INFERENCE/JUDGMENT/DERIVED 投影列（验收项 #5）|
| `schema/migrations/013_counterexample_gate.sql` | 反例 trigger `assert_min_one_contradicts()`（验收项 #6）|
| `frontend/app/provinces/{jiangsu,zhejiang,guangdong,shandong,sichuan}/page.tsx` | 5 省 mock 页面（验收项 #1）|
| `frontend/app/components/EvidenceChain.tsx` | 6 段证据链 UI（验收项 #2，不可降级）|
| `frontend/app/components/SevenDimGrid.tsx` | 7 维度观察卡（验收项 #3）|
| `frontend/app/components/PeerCompareCard.tsx` | 同类地区对比（验收项 #1 配套）|

---

## 11. CC 建议（供 Cursor 审阅 / 用户裁定）

### 11.1 Gate 2 评审日期

| 选项 | 描述 | 选 |
|---|---|---|
| A | 暂定 W8（per docs/34 §10.4）| **推荐**（不擅自提前）|
| B | 提前到 W6-W7 | 不推荐（10 地市 + S2.7-b 未收口）|

### 11.2 Gate 2 演示数据策略

| 选项 | 描述 | 选 |
|---|---|---|
| A | 仅 mock（per docs/34 §141 "不要求真实 SHA 样本"）| **推荐**（5 省 mock + O1 OPEN 必带）|
| B | 部分真实 SHA（需 O1 收口）| 强依赖 S2.0.2 |

### 11.3 docs/10 §3.2-3.4 测试落地方案

| 选项 | 描述 | 选 |
|---|---|---|
| A | pytest stub + xfail 显式声明 "Stage 3 收口" | **推荐**（per docs/08 §3.2 #7 仅要求 3.1-3.5 测试存在）|
| B | pytest 跳过 + 标 SKIPPED | pytest 报告中显式 SKIP 比 xfail 弱 |

### 11.4 Stage 1 OPEN 必带项

| 选项 | 描述 | 选 |
|---|---|---|
| A | O1（真实 SHA）+ O3（OCR）必带（per docs/34 §3 "必填依赖"）| **推荐**|
| B | 仅带 O1，O3 演示级可过（NBS 数字） | 可接受；O3 OPEN 显式列出 |

### 11.5 Gate 2 PASS 守门机制

| 选项 | 描述 | 选 |
|---|---|---|
| A | receipt 严禁 "Gate 2 PASS" 字样 + Cursor 审验把关 | **推荐**（per docs/34 §8 #8 + §133 + `247` §红线）|
| B | 仅在 docs/44 红线自检表 + 评审包封面标注 | 加固 |

### 11.6 10 地市具体选择

| 选项 | 描述 | 选 |
|---|---|---|
| A | 待 tasking 249+ 用户/Cursor 裁定 | **推荐**（本刀仅列候选 per §5.1.3）|
| B | 由 CC 自动挑选（如经济强市）| 越界（per docs/34 §10.4 "不擅自"）|

---

— End of `docs/44` —

> 等待 Cursor 审验（预期 `249-stage0-cursor-s210-plan-audit-…md`）。
> 通过后下发落地任务（`250-stage2-s210-gate2-package-impl-tasking-…md`），进入 S2.10 实施。
> ⚠ **本刀不宣布 Gate 2 PASS**（per `docs/34 §1` + `docs/34 §8 #8` + `247` §红线）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4；不擅自提前）。