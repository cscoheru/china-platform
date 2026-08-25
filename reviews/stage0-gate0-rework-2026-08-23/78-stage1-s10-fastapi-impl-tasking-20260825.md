# S1.10 — FastAPI 只读查询层实现任务书

- 编号：`78-stage1-s10-fastapi-impl-tasking-20260825`
- 前置：`77` 规划通过；`docs/24`

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 框架 | **FastAPI + Uvicorn**；**不用** SQLAlchemy/SQLModel |
| DB | **psycopg2 ThreadedConnectionPool**；每 session **`SET TRANSACTION READ ONLY`** |
| DSN | `CEGR_DSN` → `DATABASE_URL` → dev default |
| 数据源 | **`cegr_staging`** dbt views（须先 `dbt run`） |
| 核心验收 | **`GET /api/indicator/{id}/series`** 200 + 合法 JSON |
| auth | **本刀不做**（§13 遗留） |

## NOW

1. 按 `docs/24` §2 搭建 `backend/src/china_platform/api/`（app / deps / routers / schemas）
2. 实现 **12** endpoints（§6）；核心 `indicator/{id}/series`
3. Pydantic v2 响应 + `ErrorResponse`（§5/§7）
4. **≥9** integration tests（`httpx` TestClient；§10）
5. `pytest` 定向跑 API tests + pack → **非 OCR 刀可用 `SKIP_PYTEST=1` 仅当 pack 超时** → commit → **origin 优先** → 回执 **`79-stage0-cc-s10-impl-receipt-*.md`**
6. → **§POLL**（拆步交卷；禁止 30min 单工具一条龙）

## 红线

不 Gate 1 PASS；不 DSH；不批量爬取；不改 `gate_thresholds.json`；不写 `cegr` 原表。
