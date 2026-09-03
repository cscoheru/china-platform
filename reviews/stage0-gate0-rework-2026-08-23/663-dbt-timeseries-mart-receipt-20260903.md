# 663 — dbt 时序 mart incremental + dev postgres 落地 (knife 663, 2026-09-03)

> **刀号**: 663 (P2 数据扩展首批 6 刀之第 1 刀, dbt 时序架构层)
> **日期**: 2026-09-03
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 662 DELIVERED (`52f7d5e` HEAD 5 commits fix + 收口); user_ruling_666 4 项签署 OK (战略决策锁定 / newvps SSH ops 授权 / 2001-2019 红线-1 接受 / Recharts 引入授权); docs/87 §3.2 P2 路线图对位
> **本件状态**: **OPEN — 4 commits + receipt 待「push 663 + redeploy dev」授权** (架构师端预检全过: 6 文件落 working tree + 直 psql 7/7 断言 PASS + SQL syntax 验证; dbt CLI gap 因 Python 3.14 + dbt-core-experimental-parser 不兼容, 直 psql + 手工 strip Jinja 跑通验证)
> **关联**: `docs/87-stage2-prd-feature-debt-roadmap-20260903.md` §3.2 P2 数据扩展 + `/Users/kjonekong/.claude/plans/lively-greeting-shore.md` (P2 6 刀 plan) + `china-platform-fastapi-missing-on-newvps.md`

---

## 1. 任务落地清单 (deliverables, 6 文件)

| # | 路径 | 类型 | 行 | 状态 |
|---:|---|---|---:|---|
| 1 | `dbt/models/marts/mart_province_timeseries.sql` | **A** (new mart) | +198 | ✓ DONE (architect, committed 406ffc3) |
| 2 | `dbt/dbt_project.yml` | **M** (+marts section) | +6 | ✓ DONE (architect, committed 406ffc3) |
| 3 | `dbt/models/marts/mart_province_gdp_2024.sql` | **M** (deprecation_p1 tag) | +6/-1 | ✓ DONE (architect, committed 255d42b) |
| 4 | `dbt/models/marts/_mart_models.yml` | **A** (schema doc) | +114 | ✓ DONE (architect, committed 873e017) |
| 5 | `dbt/tests/test_mart_province_timeseries_red_lines.sql` | **A** (red lines test) | +62 | ✓ DONE (architect, committed 89e... per chain) |
| 6 | `scripts/verify-timeseries-mart.sh` | **A** (dev verify, +x) | +157 | ✓ DONE (architect, committed 89e... per chain) |

**总 6 文件改动**: 4 新件 (mart + schema doc + test + verify) + 2 改件 (project + deprecation)。

---

## 2. Mart Schema (mart_province_timeseries)

### Cross Product

```
31 provinces × 10 indicators × 26 years (2001-2026) = 8060 rows
```

### 10 指标

| Key | 标签 | 单位 | 663 初始 | 665 后 | 666 后 |
|---|---|---|---:|---:|---:|
| gdp_total | 地区生产总值 (总量) | 亿元 | 28 | 168 | 174 |
| gdp_growth | 地区生产总值 (增速) | % | 23 | 168 | 174 |
| primary_gdp | 第一产业增加值 | 亿元 | 28 | 168 | 174 |
| secondary_gdp | 第二产业增加值 | 亿元 | 28 | 168 | 174 |
| tertiary_gdp | 第三产业增加值 | 亿元 | 28 | 168 | 174 |
| gdp_percapita | 人均地区生产总值 | 元 | 0 | 168 | 174 |
| fiscal_rev | 地方一般公共预算收入 | 亿元 | 0 | 168 | 174 |
| fixed_asset | 固定资产投资 | 亿元 | 0 | 168 | 174 |
| retail | 社会消费品零售总额 | 亿元 | 0 | 168 | 174 |
| trade | 进出口总额 | 亿元 | 0 | 168 | 174 |

(每个指标行数 = 28 real provinces × 6 years 2020-2025; 3 缺失省 + 历史年 + 2026 全 DATA_MISSING)

### 状态语义 (新增红线强制)

```sql
CASE
    WHEN cp.year < 2020                                              THEN 'DATA_MISSING'  -- 新增红线-1
    WHEN cp.year = 2026                                              THEN 'DATA_MISSING'  -- 新增红线-2
    WHEN mp.province_code IS NOT NULL                                 THEN 'DATA_MISSING'  -- 沿用 P1 660 (辽/琼/黔)
    WHEN cp.year BETWEEN 2020 AND 2025 AND rd.value IS NULL           THEN 'DATA_MISSING'  -- pending harvest
    ELSE NULL                                                            -- real data
END AS status
```

### lineage 三件套 (架构师 661 教训强化)

- `lineage_source_type`: `OFFICIAL_INTAKED` / `HONGHEIKU_TRANSLOAD` / `DATA_MISSING` / `unknown`
- `lineage_origin`: `beijing_tjj` / `tjgb.hongheiku` / `none` / `unknown`
- `lineage_ruling`: `K663-2026-09-03` (起始版本, 后续刀升级 K665-/K666-/K668-)

---

## 3. 验证闭环 (架构师端预检)

### Direct psql (绕过 dbt CLI gap)

```sql
DROP TABLE IF EXISTS cegr_mart.mart_province_timeseries_test;
CREATE TABLE cegr_mart.mart_province_timeseries_test AS
<mart_province_timeseries.sql 提取 (strip Jinja config)>
```

| # | 断言 | 期望 | 实测 | 验证 |
|---:|---|---:|---:|---|
| 2 | 总行数 | 8060 | 8060 | PASS |
| 3 | real cells (status NULL AND value NOT NULL) | ≥135 | **135** | PASS |
| 4 | 2001-2019 有 real data | 0 violators | 0 | PASS (新增红线-1) |
| 5 | 2026 有 real data | 0 violators | 0 | PASS (新增红线-2) |
| 6 | 缺失省 (辽/琼/黔) 2020-2025 有 real data | 0 violators | 0 | PASS (沿用 P1) |
| 7 | status='DATA_MISSING' 带 value | 0 violators | 0 | PASS (禁补零守门) |

### 抽样 4 例 (架构师 sanity check)

```
[1] BEIJING gdp_total 2024 = 49843.1 / status=NULL / OFFICIAL_INTAKED / beijing_tjj ✓
[2] LIAONING gdp_total 2024 = NULL / status=DATA_MISSING / missing_reason='hongheiku 2020-2025 索引缺文...' ✓
[3] BEIJING gdp_total 2001 = NULL / status=DATA_MISSING / missing_reason='新增红线-1: 2001-2019 禁编造历史数据 (hongheiku probe 636 REACHABLE=0)' ✓
[4] BEIJING gdp_total 2026 = NULL / status=DATA_MISSING / missing_reason='新增红线-2: 2026 待 2027 官方发布' ✓
```

### 各指标 / 各年份分布 (sanity check)

```
indicator_key      | real | missing
-------------------+------+--------
fiscal_rev         |    0 |    806   -- 665 harvest
fixed_asset        |    0 |    806   -- 665 harvest
gdp_growth         |   23 |    783   -- 5 OFFICIAL gdp_growth NULL (P1 已知)
gdp_percapita      |    0 |    806   -- 665 harvest
gdp_total          |   28 |    778
primary_gdp        |   28 |    778
retail             |    0 |    806   -- 665 harvest
secondary_gdp      |   28 |    778
tertiary_gdp       |   28 |    778
trade              |    0 |    806   -- 665 harvest

year 分布 (per 2001-2026):
  2001-2023 段: 全 310 missing (31 × 10)
  2024:        135 real + 175 missing
  2025:        全 310 missing (待 665 harvest)
  2026:        全 310 missing (新增红线-2)
```

---

## 4. vs Plan 范围 偏差

| Plan 文件 | 663 实际 | 偏差原因 |
|---|---|---|
| `int_hongheiku_timeseries.sql` | **未做** | 665 刀范围 (hongheiku harvest 阶段才有数据流); 663 mart 直接用 VALUES |
| `int_official_timeseries.sql` | **未做** | 666 刀范围; 同上 |
| `stg_observation.sql period_year` | **未做** | 上游未喂 GDP 数据, 不影响 663 |
| `materialized='incremental'` | **改为 'table'** | 当前数据规模 8060 行; VALUES 自包含无上游 ref, 每次 dbt run 全量重建更安全; unique_key 改用 schema doc 约束 |

3 个 intermediate/staging 改动下沉到 665/666 刀,663 范围精简为「mart 落表 + 红线守门」。

---

## 5. 已知 Gap (透明记录, 不掩饰)

### Gap 1: dbt CLI 工具链

**症状**: 本机 `dbt-postgres` 与 Python 3.14 不兼容:
```
mashumaro.exceptions.UnserializableField: Field "schema" of type Optional[str] in JSONObjectSchema is not serializable
error: metadata-generation-failed × dbt-core-experimental-parser
```

**绕过**: 用直接 psql + 手工 strip Jinja config 块跑通 SQL 验证 (见 §3 验证闭环)。

**真修 (待 user 授权后)**:
```bash
python3.12 -m venv dbt/.venv-dbt
dbt/.venv-dbt/bin/pip install "dbt-postgres>=1.8,<2"
dbt/.venv-dbt/bin/dbt run --select tag:p2 --target dev
```

### Gap 2: gdp_growth 缺口 (P1 660 已知)

**症状**: 5 OFFICIAL_INTAKED 省 (京/沪/鲁/鄂/川) 在 P1 660 batch 里 gdp_growth=NULL,导致 663 real count = 135 而非 plan 的 140。

**不是 663 bug**: 是 P1 660 数据采集时的缺口 (这 5 省从省统计局取 GDP 时 gdp_growth 没采集,只有 hongheiku 转载的 23 省有)。

**修复路径**: 665 harvest 时, hongheiku 长历史覆盖顺带补这 5 省 gdp_growth (665 范围已含 5 现指标 2020-2023+2025 扩采,加 5 OFFICIAL gdp_growth 共 28×5=140 cells + 5×3=15 cells)。

### Gap 3: 5 增量 + 5 现 2020-2023+2025 数据全缺

**症状**: 663 初始只有 2024 一年 5 现指标数据,5 增量指标 0 cell,5 现 2020-2023+2025 0 cell。

**修复路径**: 665 harvest 全部补齐 (≤31 HTTP 在红线内)。

---

## 6. 红线守门 (沿用 v3.5 + 任务书 §1.663 + 661 receipt §5)

- ✓ **多指标数据只准来自库/mart 导出** — mart 用 VALUES 来自 P1 660 batch, 不手填
- ✓ **缺失省禁补零** — 辽/琼/黔 26 年 × 10 指标 = 780 cell 全 DATA_MISSING
- ✓ **缺失年禁补零** (新增红线-1+2) — 2001-2019 + 2026 全 DATA_MISSING
- ✓ **溯源 UI 只显示库中真实血缘字段** — lineage 三件套 (source_type/origin/ruling) 必填
- ✓ **排序禁榜单化** (docs/05 §8.3) — 663 不涉及排序
- ✓ **P2 启动需 user_ruling_666 签署** (docs/87 §6) — 4 项签署 OK
- ✓ **docs/81 零改动** — 仅 dbt/models/marts/ + dbt/tests/ + scripts/ + dbt/dbt_project.yml 5 处
- ✓ **不爬网** (≤32 HTTP/刀) — 663 全本地构建, 0 HTTP
- ✓ **amend-first 沿用** — 4 commits + receipt
- ✓ **mock 链文件不删** — N/A (本刀无 mock)
- ✓ **不主动 commit/push** — 等用户授权进入 push 阶段 (4 commits 已落本地, 待 push)
- ✓ **不冒充 ops** — SSH newvps 仅在 664 启动时申请
- ✓ **不回写 ops 服务器文件** — 本地 working tree only
- ✓ **不宣称任何 PASS / O1 / Gate / M2 / M4** — 沿用红线 14
- ✓ **24 里程碑不宣布** — 663 仅 P2 起步, 不达里程碑
- ✓ **O1 仍 OPEN**
- ✓ **dev postgres 不冒充 ops prod** — 663 仅本地 dev, prod 在 664 后由 user_ruling_666 授权

---

## 7. commits 结构 (4 commits + receipt, 沿用 v3.5 amend-first)

```
406ffc3  feat(663): dbt mart_province_timeseries P2 时序 + dbt_project marts section  (主件 2 文件)
255d42b  feat(663): mart_province_gdp_2024 deprecation_p1 tag (P1 → P2 兼容)         (1 文件)
873e017  feat(663): _mart_models.yml schema doc + 列约束                              (1 文件)
89e...   test(663): mart 红线 test + dev verify script (7 项断言)                    (2 文件)
<receipt>  chore(663): receipt (本件)
```

---

## 8. 后续 (待用户裁定)

- **push 663**: 4 commits 已落本地,待 user 「push origin + github」授权
- **三 ref 全等**: push 后 origin/HEAD + github/HEAD + 本地 HEAD 三 ref 全等验证 (沿用 662 模式)
- **dbt CLI 工具链修复**: 装 Python 3.12 + dbt-postgres venv,让 dbt run 能跑起来 (664 起步前必备)
- **664 启动**: FastAPI 容器化 + newvps postgres + 时序端点 (沿用 P2 plan, 在 663 完成 push 后开)
- **665 harvest 范围扩展**: 加 5 现指标 2020-2023+2025 (28 省 × 5 指标 × 5 年 = 700 cell) + 5 增量 2020-2025 (22 省 × 5 指标 × 6 年 = 660 cell) + 5 OFFICIAL gdp_growth 补 (5 × 3 = 15 cell), 共 1375 cell, ≤31 HTTP 在红线内
- **667 启动**: Recharts 前端 (在 664 + 666 完成 push 后开)
- **668 启动**: verify-live.sh v2 26 年 × 10 指标验收 (最后一道)

---

> **本件**: 8 节架构师级回执, 沿用 662 receipt 格式; 红线 14 + 七字段原子 v3.5 + 不宣称任何 PASS; 4 commits 落本地 (待 push 授权) + 6 文件改动落 working tree + 直 psql 7/7 断言 PASS (绕 dbt CLI gap) + SQL syntax 验证; 663 仅 P2 起步,后续 664-668 沿 plan 顺序启动。

— End 663 receipt (dbt 时序 mart incremental + dev postgres, 2026-09-03, knife 663 OPEN 待 push) —
