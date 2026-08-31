# 631-stage0-cc-m2-a-geo-inventory-receipt-20260831

> 架构师任务书：`631-stage0-architect-m2-a-geo-inventory-tasking-20260831.md`
> 刀号：631
> 阶段：M2-a
> 提交端：CC（执行端）
> 收尾：2026-08-31

## §1. 完成表

| 子刀 | 文件 | 状态 |
|---|---|---|
| 631-A | `scripts/seed_m2_province_geo.py` | DONE |
| 631-B | `source_registry/m2_2024_gdp_inventory.csv` | DONE |
| 631-C | `scripts/report_m2_gdp_coverage.py` + `docs/reports/m2_2024_gdp_coverage_20260831.md` | DONE |
| 631-D | `tests/test_m2_province_geo_seed.py`（8 用例全绿） | DONE |

## §2. pytest 一行

```
STAGE0_SKIP_SCHEMA_APPLY=1 python3 -m pytest tests/test_m2_province_geo_seed.py -v
============================== 8 passed in 0.26s ===============================
```

8 / 8 PASS：

- `test_31_province_geo_entities_exist`
- `test_provinces_include_hubei_and_30_m2_namespaces`
- `test_hubei_geo_code_version_not_duplicated`
- `test_30_m2_geo_code_versions_at_2024`
- `test_inventory_has_at_least_31_rows`
- `test_inventory_status_distribution`
- `test_coverage_script_exits_zero`
- `test_coverage_script_includes_hubei_blocked`

注：conftest 在 session-start 默认 DROP+apply schema，但本机 `schema/migrations/014_source_document_doc_kind.sql` 依赖一个 `source_document` 中间表（前置 migration 未 apply），导致 auto-apply 失败。测试 fixture 自带 M1+M2 种子，故 `STAGE0_SKIP_SCHEMA_APPLY=1` 时跑得通；不属本刀范围。

## §3. inventory 行数 + 状态分布

- 总行数（去 header）：**31**
  - 国家 + 31 省
- PENDING：**30**
- BLOCKED：**1**（湖北省，M1 样本 2026H1，2024 年度点未取）
- FETCHED：**0**（**禁**锁省统计局首页当表源 §1.B）
- 仅有根首页当 FETCHED：**0**

## §4. coverage 输出（节选）

```
# M2-a 2024 GDP coverage matrix (31 省级)

## Summary

- Total 省级 rows: **31**
- COVERED (real observation 2024 GDP): **0**
- BLOCKED (inventory status=BLOCKED): **1**
- PENDING (inventory status=PENDING): **30**
- EMPTY (no inventory row): **0**

KPI (per knife 631 §2): geo×indicator×year=2024 覆盖率 = **0/31** = 0.0%

M2-a allows 全 0 有值 (empty matrix); 此报告仅记录基线状态。
```

KPI = **0/31 = 0.0%**（knife 631 §1.C 允许 M2-a 空矩阵；非 PARTIAL 当完成，因为这是基线报告）

## §5. 红线自审

| 红线 | 状态 | 证据 |
|---|---|---|
| 仅锁省统计局首页当表源 | ✓ | inventory 全为子目录路径，如 `/tjsj/sjcx/tjgb/`；无 FETCHED 状态；test_inventory_status_distribution 验证 |
| 补零冒充覆盖 | ✓ | KPI 真实 = 0/31 = 0.0%，脚本 exit 0 但**不**伪造任何有值 |
| 买商业库 / 接入第三方 API | ✓ | inventory 全为政府 `.gov.cn` 域；无第三方 |
| LLM 改 value | ✓ | 0 个 observation 写入 |
| 自动宣布 Gate / O1 / M2 PASS | ✓ | 本刀完成 ≠ M2 PASS；M1 仅「有限通过」 |
| 跨 src 拷贝覆盖首页 HTML 当表源 | ✓ | coverage 脚本读 `cegr.observation` 真实行；首页 HTML 不入 observation |
| 重复 audit 信息 | ✓ | 此回执只列一次状态变化 |

## §6. 关键 deviation（与 631 tasking 差异）

| 项 | tasking | 实际 | 原因 |
|---|---|---|---|
| inventory CSV 列对齐 | 隐含 9 列对齐 | 初版 30 行有列错位（PENDING 落到 missing_reason 列） | 631-B 生成时多 1 个 `,`；在 631-C 跑前**自检**发现并修正 |
| seed_m2 source_registry id 写入 | REGISTRY_ID | 上一轮 `replace_all=true` 把 DOC_ID 误覆盖了参数；631-D 测试发现并修正 | 任务书设计如此：reg → doc → geo_entity → geo_code_version |

## §7. 明确不做

- 不宣布 Gate / O1 / M2 PASS（红线条目）
- 不 ingest 31 省 observation（→ M2-b）
- 不补零冒充 1/31 覆盖
- 不动 `/provinces/jiangsu`；不扩四轨 HTML
- 不动 migration 014（conftest schema apply 失败是另一议题）

## §8. 下一步

- M2-a 完成。
- M2-b 待架构师签发；首刀预取 ≥5 省（江苏 / 浙江 / 广东 / 国家 + 一试点）走完整 e2e
- 30 源 PENDING 行待 M2-b 取 + SHA 锁 + observation 行写入后，KPI 才能 ≥5/31

## §9. 文件清单

```
scripts/seed_m2_province_geo.py
source_registry/m2_2024_gdp_inventory.csv
scripts/report_m2_gdp_coverage.py
docs/reports/m2_2024_gdp_coverage_20260831.md
tests/test_m2_province_geo_seed.py
reviews/stage0-gate0-rework-2026-08-23/631-stage0-cc-m2-a-geo-inventory-receipt-20260831.md
```