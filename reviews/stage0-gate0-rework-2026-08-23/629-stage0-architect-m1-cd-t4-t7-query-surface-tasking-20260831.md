# 629 — M1-c+d 合刀：T4–T7 可查询面 + 集中摄影（架构师任务书）

> **类型**: Architect 签发（不写实现 / 不 commit 实现）
> **日期**: 2026-08-31
> **依据**: `docs/55` §T4–T7；用户 2026-08-31「合并大任务 + 执行端完成后集中摄影」+「签」
> **前置**: M1-b `0ee445e` · 628 PASS · GDP observation SUCCESS（31336.72 亿元）
> **禁止**: 宣布 Gate / O1 / M1 PASS；首页 HTML；改 `/provinces/jiangsu` 显示湖北；mart demo 冒充真值

---

## 0. 一句话

把 M1-b 已入库的 **湖北 GDP 真 observation** 打通到 **dbt view → FastAPI series → 一页前端 → 文档/队列**，**一次回执集中摄影**。

---

## 1. 锁定常量（禁止换）

| 项 | 值 |
|---|---|
| 指定表 | `spikes/02-provincial-yearbook/hubei_2026_06.xlsx` |
| SHA-256 | `c5cf5abeb4fdf97af52567f0640470d631bc9ac329dcc98f14e5d40bf6a5cac7` |
| GDP indicator_id | `a1000000-0000-0000-0000-000000000010` |
| geo_entity_id（湖北） | `a1000000-0000-0000-0000-000000000001` |
| period | 2026-01-01 .. 2026-06-30（2026H1） |
| 期望 value | **31336.72** 亿元 |
| source_domain | `tjj.hubei.gov.cn` |
| 页路由 | **`/research/m1-series`**（新建；勿绑江苏页） |

---

## 2. 交付范围（T4+T5+T6+T7 合一）

### T4 — dbt / staging 能看见真行

**完成条件:** `cegr_staging.int_indicator_timeseries` 含湖北 GDP 点（`value IS NOT NULL`）。

**做法（二选一，优先 A）:**

- **A.** `dbt run --select stg_observation stg_source_document int_indicator_timeseries`（profile 指向 `cegr_test`）
- **B.** 若 CI/本地无 dbt：用 **与** `dbt/models/**` **同构** 的 SQL 脚本创建/刷新 view（不得改 model 语义）

**新建:** `tests/test_m1_dbt_timeseries.py`

- 断言 view 中 `indicator_id` + `geo_entity_id` + `value=31336.72` + `unit` 含「亿元」+ `source_domain='tjj.hubei.gov.cn'`

**不做:** 新 mart demo 行；不改 `001–014` migration 原文（014 search_path 债可记 receipt，不本刀修）。

---

### T5 — FastAPI series 真值

**完成条件:**

- `GET /api/indicator/{gdp_id}/series` → `series.length ≥ 1`，含 value/unit/source_domain
- `GET /api/indicator/{gdp_id}/series/{hubei_geo_id}` → 同上且 geo 过滤正确
- **不读 mock**；沿用 `backend/src/china_platform/api/routes/indicators.py` 的 `int_indicator_timeseries` JOIN

**新建:** `tests/test_m1_api_series.py`（TestClient + T1 UUID）

- 测试前：seed + ingest（可复用 `test_m1_first_series` 模式）+ 确保 T4 view 已 materialized
- 勿破坏 `tests/test_api_s110.py`「空 series 仍 200」约定

**可选最小 diff:** 若前端需 provenance，在 `IndicatorSeriesPoint` 增 `caveat_text` 或 `source_hash_prefix`（8 字符）— **禁止** 前端硬编码 MOCK UUID `JIANGSU-GDP-INDICATOR-UUID-MOCK`。

---

### T6 — 前端验收页

**完成条件:** `frontend/app/research/m1-series/page.tsx`

- `NEXT_PUBLIC_USE_MOCK=false` 时 **fetch** T5 API（不走 `lib/mock.ts`）
- 页头必含：**「M1 验收面 · 湖北 2026 上半年 GDP（公报样本）· 非 31 省 · 非 Gate PASS」**
- 展示 **caveat**（API 字段或页面从 series 元数据读取；不得删）
- 表格/图表 ≥1 真值；可显示 SHA 前 8 + 源 URL（非首页）
- **不改** `/provinces/jiangsu`

**附带:**

- `frontend/app/page.tsx`：一行链到 `/research/m1-series`（可选，一条即可）
- `frontend/smoke-check.py`：本页存在 + 禁词守门（无 score/rank 等 mart 禁词）
- `tests/test_m1_frontend_page.py`：源码含 API 路径；不含 MOCK UUID

**验收:** `python3 frontend/smoke-check.py` exit 0；本地 `USE_MOCK=false` 目视 ≥1 行。

---

### T7 — 文档与调度

- `docs/55` §5 退出清单 T4–T7 勾选（T0–T3 保持已勾）
- `docs/01` L2 行：改为「M1 指定表已 SUCCESS + 可查询面已通」（按实际措辞）
- `docs/54` M1 段：已有「拆分见 docs/55」则核对，无则补一行指针
- `reviews/…/00-EXEC-QUEUE.md` §NOW → **「M1 待用户有限通过候选」** 或 **「下一里程碑 M2」**（勿写 Gate PASS）
- `docs/00-COMPASS.md` NOW 同步（Architect 或 CC 本刀末尾更新，≤80 行）

---

## 3. 集中摄影（§PHOTO — 全部写入**一份**回执）

执行端 **禁止** 拆多份 receipt。完成实现后，在 **单一回执** 内按序粘贴以下取证块（可复制 SQL/命令输出，可截断至关键行，但须可复验）：

### PHOTO-1 — 全量 pytest（一条命令）

```bash
PYTHONPATH=backend/src python3 -m pytest \
  tests/test_m1_first_series.py \
  tests/test_m1_reference_seed.py \
  tests/test_m1_dbt_timeseries.py \
  tests/test_m1_api_series.py \
  tests/test_m1_frontend_page.py \
  -q
```

回执贴：**末行**（例 `NN passed in Xs`）。任一失败 = 不交卷。

### PHOTO-2 — dbt view 真行

```sql
SELECT indicator_id, geo_entity_id, value, unit, source_domain, period_start, period_end
FROM cegr_staging.int_indicator_timeseries
WHERE indicator_id = 'a1000000-0000-0000-0000-000000000010'
  AND geo_entity_id = 'a1000000-0000-0000-0000-000000000001';
```

须见 `value=31336.72`、`source_domain=tjj.hubei.gov.cn`。

### PHOTO-3 — API 一跳

```bash
curl -s "http://127.0.0.1:8000/api/indicator/a1000000-0000-0000-0000-000000000010/series/a1000000-0000-0000-0000-000000000001" | head -c 800
```

（TestClient 等价 JSON 亦可。）须含 value、unit、source_domain；**非空 series**。

### PHOTO-4 — 文件 SHA

```bash
shasum -a 256 spikes/02-provincial-yearbook/hubei_2026_06.xlsx | cut -c1-70
```

须 `c5cf5abeb4fdf97a…`。

### PHOTO-5 — 前端 smoke

```bash
python3 frontend/smoke-check.py 2>&1 | tail -5
```

exit 0；输出含 `m1-series` 或等价 PASS 行。

### PHOTO-6 — 红线自审表

| 红线 | ✓/✗ |
|---|---|
| 未宣布 Gate/O1/M1 PASS | |
| 未取统计局首页当源 | |
| 江苏页未显示湖北 GDP | |
| 未用 mart demo 冒充 | |
| KPI=真 observation（非 11/15） | |

### PHOTO-7 — 改动文件清单

表格：路径 | 新增/修改 | 一句话。

---

## 4. 回执格式

**唯一文件:** `reviews/stage0-gate0-rework-2026-08-23/629-stage0-cc-m1-cd-t4-t7-receipt-YYYYMMDD.md`

结构：

1. §0 一句话
2. §1 T4–T7 映射表（对照本文 §2）
3. **§PHOTO** — 按 PHOTO-1..7 顺序，**集中摄影**
4. §红线
5. cc_head commit SHA

双推：`git push origin HEAD && git push github HEAD` → POLL。

---

## 5. 明确不做

- Gate / O1 / M1 PASS 宣告
- 626 / 首页 HTML 里程碑
- 扩省、四轨 deeplink 系列、改 docs/45/50 正文
- 重写 migration 014（可 disclosure）
- 把 T6 做成第二个 public-extracts 克隆

---

## 6. Cursor 审验点（629 回执后）

- PHOTO-1 全绿
- PHOTO-2 value=31336.72 且 domain=湖北统计局域
- PHOTO-3 非 mock
- PHOTO-5 smoke 含 m1-series
- docs/55 T4–T7 已勾
- 仍 **不** 宣布 Gate PASS

— End 629 —
