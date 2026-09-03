-- backend/docker/init-mart-schema.sql
-- Container init script: cegr_mart schema bootstrap (knife 664h).
--
-- dbt 默认 schema 行为: 仅在 schema 存在时建表. 所以必须先 create schema.
-- mart schema 名与 dbt profiles.yml prod target 一致 (cegr_mart).
-- dbt 后续 dbt run --select tag:p2 --target prod 会建 mart_province_timeseries
-- 等所有 mart 表.
--
-- 执行: 仅容器首次启动时 (postgres image 自动跑 /docker-entrypoint-initdb.d/*.sql).

CREATE SCHEMA IF NOT EXISTS cegr_mart
    AUTHORIZATION postgres;

-- 让 dbt 有权限创建/修改 mart 表 (实际 postgres superuser, 不需要 grant)
-- 留空: dbt 自身有 superuser 权限.

COMMENT ON SCHEMA cegr_mart IS
    'P2 mart schema (knife 663 + 664). Contains mart_province_timeseries '
    '(8060 rows = 31 provinces × 10 indicators × 26 years).';