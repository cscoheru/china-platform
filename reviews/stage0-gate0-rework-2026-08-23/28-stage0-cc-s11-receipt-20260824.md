# Stage 1 / S1.1 + S1.2 — CC Receipt

- 文件编号：`28-stage0-cc-s11-receipt-20260824`
- 下发方：CC（Claude Code）
- 日期：2026-08-24
- 接收：`reviews/26-stage1-s11-postgresql-tasking-20260824.md` + `reviews/27-stage0-cursor-cc-wakeup-s11-now-20260824.md`
- 协议：`21-stage0-cc-proactive-poll-standing-order-20260824.md` §1 T1 + `00-CC-CURRENT.md` §NOW

---

## §0. TL;DR

| 任务 | 状态 |
|---|---|
| S1.1 Docker Compose 本地 PG16+PostGIS | ✅ 文件交付；docker 不可用 → **BLOCKED_BY_ENV** 详见 §5 |
| S1.2 Alembic 初始化 + seed 002 | ✅ `alembic current = cegr002 (head)`；`upgrade head` no-op |
| docs/12 §5.2 U-4 行 → 已裁定 A | ✅ |
| docs/17 §3 第 5 试点源默认 江苏统计局 | ✅ |
| pytest 251 pass | ✅ 251 passed in 451.44s |
| pack rebuild 0 错 | ✅ 441 artifacts / pack_errors=0 / schema 1.1-R3G-R4 |
| commit + 双推 | ✅ LOCAL=origin=github=`48526b4` |
| 本回执 | ✅ |

---

## §1. 交付清单

### S1.1 — `infra/` 可复现栈

| 文件 | 用途 |
|---|---|
| `infra/docker-compose.yml` | PG16+PostGIS 3.4，port 55440，named volume `cegr_pg16_data`，healthcheck，env 驱动（POSTGRES_PASSWORD 必须从 `.env` 注入，不入库） |
| `infra/README.md` | up/healthcheck/apply-chain/teardown + 当前本地 dev workaround（PG17@55440 homebrew）说明 |
| `.env.example` | dev-only `POSTGRES_*` + `DATABASE_URL` 模板（无 secrets） |

### S1.2 — Alembic 初始化（并存策略）

| 文件 | 用途 |
|---|---|
| `alembic.ini` | `script_location = alembic`，`sqlalchemy.url = postgresql+psycopg2://postgres:postgres@127.0.0.1:55440/cegr_test`（可被 `DATABASE_URL` 环境变量覆盖） |
| `alembic/env.py` | 读 `DATABASE_URL` 环境变量 override；`version_table_schema = "cegr"`（与 canonical schema 同 namespace） |
| `alembic/versions/cegr001_placeholder_create_core.py` | 占位 revision；`upgrade()` / `downgrade()` 均为 `pass` |
| `alembic/versions/cegr002_placeholder_source_governance.py` | 占位 HEAD revision；同为空 body |

### 文档小修

| 文件 | 变更 |
|---|---|
| `docs/12-stage0-closure-and-report.md` §5.2 USER POLICY 表 U-4 行 | "待最终 eval + Cursor 复验后裁定 / CC 不自动宣布 Stage 0 PASS" → "**已裁定 A（2026-08-24）** / Gate 0 关闭；可继续；用户授权启动 Stage 1（per `reviews/23` §1）"（与 §12.2 一致） |
| `docs/17-stage1-kickoff-plan-20260824.md` §3 首批 5 来源 | "第 5 个待定" → "**第 5 个默认**（per `reviews/26` §3）：**江苏省统计局** `stats.jiangsu.gov.cn`（PROVINCIAL_BULLETIN，S0；扩点至江苏以支持 Gate 1 研究问题演示）。**用户可改**。" |

---

## §2. 命令输出摘要

### §2.1 alembic current / upgrade head / history

```
$ alembic history
<base> -> cegr001, placeholder_001
cegr001 -> cegr002 (head), placeholder_002

$ alembic stamp cegr002
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running stamp_revision  -> cegr002

$ alembic current
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
cegr002 (head)

$ alembic upgrade head     # no-op
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.

$ PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test -c \
    "SELECT version_num FROM cegr.alembic_version;"
 version_num
-------------
 cegr002
(1 行记录)
```

### §2.2 pytest

```
$ python3 -m pytest -q -p no:cacheprovider
........................................................................ [ 28%]
........................................................................ [ 57%]
........................................................................ [ 86%]
...................................                                      [100%]
251 passed in 451.44s (0:07:31)
```

### §2.3 evidence pack

```
$ EVIDENCE_PACK_TEST_HOOKS=1 SKIP_PYTEST=1 SKIP_PSQL=1 python3 scripts/build_evidence_pack.py
Wrote /Users/kjonekong/projects/china platform/evidence_pack/manifest.json: 441 artifacts
verified 441 artifacts (full)

# 独立 SHA-256 全量复算：
artifacts_re_verified=441
pack_errors=0
schema_version=1.1-R3G-R4
OK
```

### §2.4 git dual-push

```
$ git push origin HEAD
To https://origin.cursor.com/lyliae/china-platform.git
   bbb0b7b..48526b4  HEAD -> main
---origin rc=0---

$ git push github HEAD
To https://github.com/cscoheru/china-platform.git
   bbb0b7b..48526b4  HEAD -> main
---github rc=0---
```

SYNC: LOCAL=origin=github=`48526b4` ✅

---

## §3. 变更摘要

```
$ git log -1 --stat
commit 48526b4
12 files changed, 274 insertions(+), 1 deletion(-)
create mode 100644 .env.example
create mode 100644 alembic.ini
create mode 100644 alembic/README
create mode 100644 alembic/env.py
create mode 100644 alembic/script.py.mako
create mode 100644 alembic/versions/cegr001_placeholder_create_core.py
create mode 100644 alembic/versions/cegr002_placeholder_source_governance.py
create mode 100644 infra/README.md
create mode 100644 infra/docker-compose.yml
modify docs/12-stage0-closure-and-report.md
modify docs/17-stage1-kickoff-plan-20260824.md
modify evidence_pack/manifest.json
```

---

## §4. 应用链契约保留验证

Per `docs/17` §2，alembic 与手工 SQL 是「并存而非替换」关系。验证：

| 验证 | 结果 |
|---|---|
| `tests/conftest.py` 仍直接 `psql -f schema/01-core.sql + migrations/*.sql`（绕过 alembic） | ✅ 未改 conftest |
| `scripts/build_evidence_pack.py::run_db_apply()` 仍走原链 | ✅ 未改 builder |
| `pytest -q -p no:cacheprovider`（默认 autouse session fixture） | ✅ 251 pass（包含 schema_negative 39 + source_governance 21） |
| Alembic `current` / `upgrade head` no-op | ✅ 见 §2.1 |
| 手工 01-core.sql / 002_source_governance.sql 内容未改 | ✅（git diff 仅 alembic/ + infra/ + docs/12 + docs/17 + manifest.json） |

---

## §5. BLOCKED_BY_ENV — Docker 不可用

Per `reviews/27-wakeup` §3："Docker 不可用 → 回执写 **BLOCKED_BY_ENV** + 本机 `docker --version` 输出；**仍不是 IDLE**，等 Cursor 改任务"。

```
$ docker --version
(eval):1: command not found: docker
```

| 维度 | 现状 |
|---|---|
| Docker daemon | ❌ 本机未安装（macOS aarch64） |
| Docker Compose v2 | ❌ 不可用 |
| 替代方案 | Stage 0 homebrew `postgresql@17` 已就位 @ 127.0.0.1:55440；本次 S1.1/S1.2 验收均跑在这台 PG17 上 |
| `infra/docker-compose.yml` 状态 | ✅ 已交付；**canonical 可复现契约**；teammate 有 Docker 的可直接 `docker compose -f infra/docker-compose.yml --env-file .env.example up -d` 起栈 |
| `alembic` 安装 | ✅ 本机 pip3 install alembic 1.19.1（dev 依赖） |

**结论**：S1.1 文件交付 + S1.2 现场验证均完成；live docker 启动留待有 Docker 的环境。**不视为 IDLE**，等待 Cursor 决定是否下发「补 docker-compose smoke 跑通」或「S1.3 进入」任务。

---

## §6. 红线遵守声明

- ❌ 未宣布 Gate 1 PASS（仅交付 S1.1 + S1.2）
- ❌ 未 ingest 真实数据
- ❌ 未 HTTP 爬源站
- ❌ 未改 `gate_thresholds.json`
- ❌ 未改 `schema/01-core.sql` 内容
- ❌ 未把 1909 / 陕西标为代表性
- ❌ 未用裸 `--force`
- ❌ 未提交 `.env`（`.env.example` 仅模板，无 secrets）

---

## §7. 下一刀（等待 Cursor）

Cursor 审验本回执后，按 `reviews/26` §3 与 §0 流程：
- 审验 `infra/` + `alembic/` + 文档小修
- 更新 `00-CC-CURRENT.md` §NOW = **S1.3**（source_registry 6 行入表 + URL 健康监控 dry-run）或先下发 S1.1 docker smoke 任务（per §5 BLOCKED_BY_ENV）
- 下发 §BLOCKED 解除

CC 按协议 21 §1 T1 触发器等候：
1. `git pull origin main`
2. 读新 §NOW + 任务书
3. 按任务书执行

**在此之前 CC 不 IDLE — 仍 EXECUTING，等待任务书而非休息。**

---

## §8. 关键元数据

```
commit         48526b4
branch         main
LOCAL  = 48526b4
ORIGIN = 48526b4 (https://origin.cursor.com/lyliae/china-platform.git)
GITHUB = 48526b4 (https://github.com/cscoheru/china-platform.git)
alembic current     cegr002 (head)
alembic upgrade head  no-op (verified)
cegr.alembic_version.version_num = cegr002
pytest                 251 passed in 451.44s
evidence pack          441 artifacts / pack_errors=0 / schema 1.1-R3G-R4
docker                 BLOCKED_BY_ENV (本机无 docker)
alembic pip            1.19.1 (dev-only install)
```

— End S1.1 + S1.2 receipt —