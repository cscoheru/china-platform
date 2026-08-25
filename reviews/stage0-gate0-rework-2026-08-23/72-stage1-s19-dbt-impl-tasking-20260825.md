# S1.9 — dbt staging 实现任务书

- 编号：`72-stage1-s19-dbt-impl-tasking-20260825`
- 前置：`71` 规划通过；`docs/23`

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| dbt 输出 schema | **`cegr_staging`**（view only） |
| materialization | **全部 `view`**；本刀不做 incremental |
| 密码 | **仅** `profiles.yml.example` + env var；`dbt/profiles.yml` **入 .gitignore** |
| 写 `cegr` 原表 | **禁止** |
| seeds | **本刀不做**（§8 遗留） |

## NOW

1. 初始化 `dbt/`（`dbt_project.yml`、`packages.yml` 含 `dbt_utils`、macros）
2. 实现 **5** staging + **2** intermediate SQL（`docs/23` §3–§4）
3. `tests/generic/` 至少 **3** 个自定义 generic test（或 docs/23 所列子集）
4. `dbt deps && dbt run && dbt test`（dev target；空表须 pass）
5. 定向 pytest（若有）+ pack → **非 OCR 刀可用 `SKIP_PYTEST=1` 仅当默认 pack 再次超时** → commit → **origin 优先** → 回执 **`73-stage0-cc-s19-impl-receipt-*.md`**
6. → **§POLL**（拆步交卷；禁止 30min 单工具一条龙）

## 红线

不 Gate 1 PASS；不 DSH；不批量爬取；不改 `gate_thresholds.json`。
