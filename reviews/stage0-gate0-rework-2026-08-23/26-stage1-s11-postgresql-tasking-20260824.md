# Stage 1 — S1.1 PostgreSQL + Alembic 初始化任务书

- 文件编号：`26-stage1-s11-postgresql-tasking-20260824`
- 下发方：Cursor
- 日期：2026-08-24
- 依据：`docs/17` §1 S1.1/S1.2；`25` 审验 ACK
- 范围：**W1 第一周**；仍 **试点**，非生产公网

---

## §0. TL;DR

| 任务 | 交付 |
|---|---|
| S1.1 | 可复现 PG16+PostGIS 本地栈（docker-compose）+ 连接文档 |
| S1.2 | `alembic/` 初始化；`alembic_version`=002；`upgrade head` no-op |
| 小修 | `docs/12` §1 U-4 表行 → 已裁定 A |
| 验证 | 251 pytest 仍过；schema 39+21 仍过 |
| 禁止 | 批量爬取；改 01-core 语义；降 OCR 门槛 |

---

## §1. S1.1 — Docker Compose 本地 PG16 + PostGIS

1. 新增 `infra/docker-compose.yml`（或 `docker/docker-compose.db.yml`）：
   - PostgreSQL **16** + PostGIS 3.x
   - 端口默认 **55440**（与 Stage 0 测试习惯一致，可 env 覆盖）
   - 库名 `cegr_test`；用户/密码经 `.env.example`（**不入库** `.env`）
2. 新增 `infra/README.md`：`docker compose up -d`、healthcheck、`psql` 连接串
3. **不**暴露公网；**不**改 CI 密钥

**退出标准：**

```bash
docker compose -f infra/docker-compose.yml up -d
PGPASSWORD=... psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test -c 'SELECT PostGIS_Version();'
# apply 链（与 conftest 同）exit 0
```

---

## §2. S1.2 — Alembic 初始化（并存策略）

按 `docs/17` §2：

1. `alembic init alembic`（或项目约定路径）
2. `env.py` 读 `DATABASE_URL`；target schema `cegr`
3. 手工 SQL **不**迁入 Alembic revision 内容；仅：
   - `alembic_version` 表 seed = `002`
   - `alembic history` 显示 001、002 占位节点（空 upgrade 或 stamp）
4. `tests/conftest.py` **仍**直接 psql apply — 本阶段不改为 Alembic-only

**退出标准：**

```bash
alembic current   # 002
alembic upgrade head  # no-op
python3 -m pytest tests/test_schema_negative.py tests/test_source_governance.py -q
```

---

## §3. 文档小修

- `docs/12-stage0-closure-and-report.md` §1 用户裁定表 U-4 行 → 与 §12.2 一致（已裁定 A）
- `docs/17` §3：第 5 试点源默认 **江苏统计局**（`stats.jiangsu.gov.cn` 类）；footnote「Cursor 默认，用户可改」

若改 pack 内 docs → rebuild → **441+ / pack_errors=0**

---

## §4. Commit + 双推 + 回执

```
feat(infra): add PG16+PostGIS compose and Alembic scaffold (S1.1/S1.2)

Per docs/17 and reviews/26. Alembic coexists with hand-written 001/002;
conftest apply chain unchanged.
```

回执：`27-stage0-cc-s11-receipt-YYYYMMDD.md`

---

## §5. 红线

- ❌ 不 ingest 真实数据
- ❌ 不 HTTP 爬源站
- ❌ 不改 `gate_thresholds.json`
- ❌ 不宣布 Gate 1 PASS

— End S1.1 tasking —
