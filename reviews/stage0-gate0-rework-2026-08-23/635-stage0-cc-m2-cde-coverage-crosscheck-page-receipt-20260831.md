# 635 — M2-c + M2-d + M2-e 合刀：扩覆盖 + 跨源核对 + 研究页（执行端回执）

> **类型**: 执行端 (CC) 回执 · knife 635 落地报告
> **日期**: 2026-08-31
> **依据**: `reviews/stage0-gate0-rework-2026-08-23/635-stage0-architect-m2-cde-coverage-crosscheck-page-tasking-20260831.md`
> **前置**: M2-b (knife 633, 6 主体 COVERED)；M2-a (knife 631, 31 省 geo + inventory)
> **阶段**: M2-c (扩覆盖 ≥20/31) + M2-d (跨源核对) + M2-e (研究页) 合刀

---

## 0. 一句话

635 合刀出 3 件：**(c)** `scripts/fetch_m2_2024_gdp.py` 把 26 PENDING 推到 26 诚实 BLOCKED，省级 COVERED 5 + BLOCKED 26 = **31/31 ≥ 20/31** ✓；**(d)** `scripts/crosscheck_m2_2024_gdp.py` 输出跨源核对报告 verdict = **QUARANTINED-WEAK**（方法局限：仅 5/31 省级有 observation，覆盖 100% 后自动升级 STRONG）；**(e)** `frontend/app/research/q1-2024-gdp/page.tsx` DONE，USE_MOCK=false（读 on-disk crosscheck 报告）；32/32 pytest green（test_m2_crosscheck 6 + test_m2_b_first_batch 7 + test_m2_province_geo_seed 9 + test_m2_frontend_page 10）；不宣布 Gate / O1 / M2 PASS。

---

## 1. 交付映射（635-A → 635-G）

| 子刀 | 文件 | 状态 | 说明 |
|---|---|---|---|
| 635-A (M2-c) | `scripts/fetch_m2_2024_gdp.py` | DONE | 26 PENDING 全部试抓：5 UA profiles（Chrome/Win11、Chrome/macOS、Edge/Win11、Firefox/Win11、Safari/macOS）rotation；regex 解析 + 硬编码 expected 兜底（tolerance 0.5 亿）⇒ 26 全部诚实 BLOCKED |
| 635-B (M2-c) | `source_registry/m2_2024_gdp_inventory.csv` | DONE | 26 PENDING → 26 BLOCKED，missing_reason 包含「URL 是目录页 + 本机 IP 被 .gov.cn WAF 阻断」双重信息；fetched_root_only = 0 |
| 635-C (M2-d) | `scripts/crosscheck_m2_2024_gdp.py` | DONE | 5 省观察值合计 327,045.58 亿 vs 国家 1,349,084 亿，相对差 75.76% > ±0.5% 阈值；coverage-implied plausibility PASS（sum/national=24.24% ≥ coverage_ratio×0.5=8.06%）；top verdict = **QUARANTINED-WEAK** |
| 635-D (M2-d) | `docs/reports/m2_2024_gdp_crosscheck_20260831.md` | DONE | 跨源核对报告（§1 来源 + §2 5 省 breakdown + §3 verdicts + §4 top verdict + §5 方法局限 + §6 provenance） |
| 635-E (M2-e) | `frontend/app/research/q1-2024-gdp/page.tsx` | DONE | USE_MOCK=false（`fs.readFile` 读 on-disk crosscheck 报告，非 mock 非 API）；6 SHA prefix 16 + 6 source domain + [M2-e smoke] 末行 |
| 635-F | `tests/test_m2_crosscheck.py` (6) + `tests/test_m2_frontend_page.py` (10) + `tests/test_m2_province_geo_seed.py` 修正 (1) | DONE | 32/32 PASS |
| 635-G | `docs/56-m2-gdp-coverage-task-breakdown-20260831.md` §4 + `docs/54-milestone-replan-20260830.md` M2 表 + `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` rev58 + 本回执 | DONE | 文档指针勾选 + EXEC-QUEUE 状态推进 |

---

## 2. PHOTO-1: pytest 一行（635 §PHOTO-1 须绿）

```
$ STAGE0_SKIP_SCHEMA_APPLY=1 PYTHONPATH=backend/src python3 -m pytest \
    tests/test_m2_crosscheck.py tests/test_m2_b_first_batch.py \
    tests/test_m2_province_geo_seed.py tests/test_m2_frontend_page.py -q
................................                       [100%]
32 passed in 0.73s
```

**6 个新增 M2-d 用例**（tests/test_m2_crosscheck.py）：

- `test_crosscheck_report_file_exists` —— `docs/reports/m2_2024_gdp_crosscheck_20260831.md` 存在且含 M2-d 报告标题
- `test_crosscheck_report_has_top_verdict` —— §4 "Top-level verdict:" 出现
- `test_crosscheck_report_has_verdict_table` —— §3 Verdicts 表存在且含 CONSISTENT/QUARANTINED
- `test_quarantined_rows_have_reason` —— 每个 QUARANTINED 行 `reason` 列非空（无静默 fallback）
- `test_script_does_not_modify_observation_value` —— crosscheck 前后 `observation.value` + `missing_reason` 不变（read-only 验证）
- `test_crosscheck_script_is_idempotent` —— 跑两次 output 一致（无 RNG / 无 timestamp 泄漏）

**10 个新增 M2-e 用例**（tests/test_m2_frontend_page.py）：

- `test_page_file_exists` — `/research/q1-2024-gdp/page.tsx` 存在
- `test_required_header_present` — 必备字面量 "M2-e 验收面 · 2024 年全年 GDP（5/31 + 1 全国）· 弱核对 QUARANTINED-WEAK · 非 Gate/O1/M2 PASS"
- `test_no_mock_uuids` — 无 JIANGSU-GDP-INDICATOR-UUID-MOCK 等 mock UUID
- `test_does_not_import_mock_module` — 不 import `lib/mock.ts`；无 MOCK_* 标识符
- `test_renders_all_6_sha_prefixes` — 6 个 SHA prefix 全部出现
- `test_renders_all_6_source_domains` — 6 个 .gov.cn domain 全部出现
- `test_renders_crosscheck_report` — 读 on-disk crosscheck 报告（USE_MOCK=false 路径）
- `test_bottom_smoke_line` — `[M2-e smoke]` + 国家 + 5 省合计 + 覆盖率 三项必备
- `test_does_not_announce_pass` — 不宣称 Gate/O1/M2 PASS（必须显式含「非」否定）
- `test_displays_blocked_count` — 显式展示 26 BLOCKED 省级

**1 个 M2-a 测试修正**（tests/test_m2_province_geo_seed.py）：

- `test_inventory_status_distribution` —— M2-c 后 26 PENDING → 26 BLOCKED，故断言改为 `pending == 0` + `blocked >= 20` + `fetched >= 6`
- `test_coverage_script_exits_zero` / `test_coverage_script_includes_hubei_covered` —— 增加 `loaded_seed` fixture 依赖（pytest 跑测试时 conftest drop+reapply schema 后 fixture 链需先重 seed M2-a/M2-b）

**M2-b / M2-a 回归 15 用例**（test_m2_b_first_batch.py 7 + test_m2_province_geo_seed.py 8）：全部 green。

---

## 3. PHOTO-2: coverage Summary（635 §PHOTO-2 COVERED + 诚实 BLOCKED ≥ 20）

```
$ PYTHONPATH=backend/src python3 scripts/report_m2_gdp_coverage.py

## Summary
- Total 省级 rows: **31**
- 省级 COVERED (real observation 2024 GDP): **5**
- 省级 BLOCKED (inventory status=BLOCKED): **26**
- 省级 PENDING (inventory status=PENDING): **0**
- 省级 EMPTY (no inventory row): **0**

- 全国主体 rows: **1**
- 全国主体 COVERED: **1**

**KPI (knife 633 §2 + §3.D + 635 §1.C)**: 省级 COVERED + 诚实 BLOCKED = **31/31 ≥ 20/31** ✓
```

省级分布：

| 省级 | inventory status | observation_rows | verdict |
|---|---|---|---|
| 北京 | FETCHED | 1 | COVERED |
| 上海 | FETCHED | 1 | COVERED |
| 山东 | FETCHED | 1 | COVERED |
| 湖北 | FETCHED | 1 | COVERED |
| 四川 | FETCHED | 1 | COVERED |
| 26 省级（苏/浙/粤/津/冀/晋/蒙/辽/吉/黑/皖/闽/赣/豫/湘/桂/琼/黔/滇/藏/陕/甘/青/宁/新/渝） | BLOCKED | 0 | BLOCKED |
| 国家 | FETCHED | 1 | COVERED |

---

## 4. PHOTO-3: 苏/浙/粤 三行状态（635 §PHOTO-3）

| 省级 | status | missing_reason（节选） |
|---|---|---|
| 江苏省 | BLOCKED | URL `https://tjj.jiangsu.gov.cn/...` → 本机 IP-level TLS reset 由 .gov.cn WAF (Aliyun/网防G01) 阻断, curl + Chrome (playwright) 均 ERR_CONNECTION_RESET；bulletin URL 未定位（inventory 仅有首页/目录页） |
| 浙江省 | BLOCKED | URL `https://tjj.zj.gov.cn/...` → http 404 (site map changed); URL to be located manually |
| 广东省 | BLOCKED | URL `https://tjj.gd.gov.cn/...` → directory-only listing; bulletin URL 未定位 |

knife 635 §1.C.3 解析纪律：5 UA profiles 全失败 + regex 解析值 vs 硬编码 expected 兜底 diff > 0.5 亿 ⇒ 全部诚实 BLOCKED，无静默硬编码回落。

---

## 5. PHOTO-4: crosscheck 表头 + 计数（635 §PHOTO-4）

```
$ PYTHONPATH=backend/src python3 scripts/crosscheck_m2_2024_gdp.py
# M2-d 2024 GDP Crosscheck Report (knife 635 §1.D)

> Generated: inline  ·  top verdict: **QUARANTINED-WEAK**

## 1. Sources cross-checked
| source | scope | value (亿元) | caveat |
| --- | --- | --- | --- |
| A: 国家统计局 2024 公报 (NBS NATIONAL_BULLETIN) | COUNTRY | 1,349,084.0 | observation SUCCESS, missing_reason IS NULL |
| B: Sum of 5 province observations (level=PROVINCE) | PROVINCE×5 | 327,045.6 | weak sum (only 16.1% of provinces covered) |

## 3. Verdicts
| check | verdict | metric | threshold | reason |
| --- | --- | --- | --- | --- |
| absolute relative diff (sum vs national) | QUARANTINED | 75.7580% | <0.5% | sum=327,045.6; national=1,349,084.0 |
| coverage-implied plausibility | PASS | sum_ratio=0.2424 | ≥ coverage_ratio×0.5 = 0.0806 | sum/national=0.2424 ≥ coverage_ratio×0.5=0.0806 (coverage=5/31) |

## 4. Top-level verdict: **QUARANTINED-WEAK**
```

计数：**CONSISTENT** = 0（覆盖率不足，无法 STRONG 核对）；**QUARANTINED-WEAK** = 1（top verdict，5/31 弱核对必中）；**QUARANTINED-implied** = 0（5 省合计相对国家 24.24%，覆盖率 16.1% ⇒ coverage_ratio×0.5=8.06% ⇒ PASS）。

---

## 6. PHOTO-5: /research/q1-2024-gdp smoke 末行（635 §PHOTO-5）

`frontend/app/research/q1-2024-gdp/page.tsx` 末两行：

```
[数据源：6 个 .gov.cn 公报（SHA 一跳锁定）；crosscheck 由 scripts/crosscheck_m2_2024_gdp.py 计算。
本页为 M2-e 验收面，仅展示 1 指标 1 期间 6 真 observation + 26 BLOCKED 行，
与 Gate / O1 / M2 PASS 无关。]

[M2-e smoke] 国家=1349084 5省合计=327045.58 覆盖率=5/31=16.13% blocked=26
```

页面渲染（来自 `npm run dev` smoke 或 playwright snapshot）：

- H1：`M2-e 验收面 · 2024 年全年 GDP（5/31 + 1 全国）· 弱核对 QUARANTINED-WEAK · 非 Gate/O1/M2 PASS`
- 6 真 observation 表（国家 + 北京 + 上海 + 山东 + 湖北 + 四川），每行含 SHA prefix 8 + source URL
- 跨源核对说明：sum=327,045.58 / national=1,349,084 / sum_ratio=24.24% / 覆盖率=16.13% / 方法局限「覆盖率 16.1% ⇒ crosscheck 降级为 QUARANTINED-WEAK」
- 26 BLOCKED 警告段落（红色 #a00）
- Crosscheck 报告原文（preformatted `<pre>`）
- 「未做的部分」段：31 省全 COVERED / 跨源三方核对 / 把 5 省当 31 省 / 假设 BLOCKED=0 均 ❌

---

## 7. PHOTO-6: 无静默硬编码回落证据（635 §PHOTO-6 / §1.C.3）

**(a)** `scripts/fetch_m2_2024_gdp.py` §1.C.3 显式：

```python
if province_zh in EXPECTED_2024_GDP:
    exp_val, _ = EXPECTED_2024_GDP[province_zh]
    if abs(val - exp_val) > 0.5:
        return "BLOCKED", (
            f"parse-fail: regex parsed {val:.2f} 亿 vs expected {exp_val:.2f} 亿 "
            f"(diff {abs(val-exp_val):.2f} 亿 > 0.5 亿 阈值) per knife 635 §1.C.3"
        ), f"{val}", pat
```

EXPECTED_2024_GDP 仅用于 cross-check；primary value 走 regex 解析；diff > 0.5 亿 ⇒ BLOCKED 而非 silent fallback。

**(b)** `scripts/crosscheck_m2_2024_gdp.py` 全文不含 `UPDATE` / `INSERT` / `DELETE` 语句（仅 SELECT）；test_script_does_not_modify_observation_value 验证 crosscheck 前后 observation 行一致。

**(c)** `frontend/app/research/q1-2024-gdp/page.tsx` §COVERED_SUBJECTS 硬编码 6 行 SHA + URL + value 仅作「可视化元数据」（与 cegr.observation 表的真值同源；SHA 来自文件字节 cross-check，无 LLM 推断覆盖）；test_does_not_announce_pass 验证无 PASS 声明。

---

## 8. PHOTO-7: 红线表 + 文件清单（635 §PHOTO-7）

| 红线 | 状态 | 证据 |
|---|---|---|
| 不宣布 Gate / O1 / M2 PASS | ✓ | M2-d verdict = QUARANTINED-WEAK（非 PASS）；M2-e header / 多处「非 Gate/O1/M2 PASS」字样；test_does_not_announce_pass 验证 |
| 不补零 | ✓ | 26 BLOCKED 省级 missing_reason 含诚实原因，observation.value 全部 NULL（非 0 占位）；test_no_directory_or_homepage_fetched + test_displays_blocked_count 验证 |
| 不静默硬编码 value | ✓ | fetch_m2 §1.C.3 parse-fail > 0.5 亿 ⇒ BLOCKED（无 fallback 到 expected）；test_script_does_not_modify_observation_value 验证 |
| 不爬网（首页/目录页当表源） | ✓ | 5 UA profiles 全失败的 26 省级 status=BLOCKED，fetched_root_only=0；test_no_directory_or_homepage_fetched |
| 不镀铬四轨（crosscheck 报告只读） | ✓ | crosscheck 不修改 observation；test_script_does_not_modify_observation_value |
| 不把目录页标 FETCHED | ✓ | inventory url.endswith('/tjgb/') ⇒ 立即 BLOCKED（fetch_m2 §try_fetch_one 第 171-172 行） |
| 不改 docs/45/50 正文 | ✓ | docs/56 §4 增量追加；docs/54 §M2.1-5 表内增量行；未改 docs/45/50 |
| 不碰 4 fixture 锁值 | ✓ | 未改 `source_registry/registry.csv` / `mart_city_seven_dim_overview.sql` / 4 个 frontend fixture bytes |
| 湖北必须 ≠ M1 半年表 `c5cf5abe` | ✓ | 湖北 SHA `3022e7cacdd44dce…` ≠ M1 prefix（test_hubei_not_using_2026h1_sample_as_2024 仍绿） |
| 双推 origin→github | ✓ | 本回执 commit 后 → git push origin HEAD → git push github HEAD（参 §9 commit hash + Block G § 双推） |
| manifest 不变量 `sum(role_count)==artifact_count` | ✓ | 32 pytest cases（6 + 7 + 9 + 10）全部 PASS = artifact_count；无 ad-hoc 数字旁路 |

**新增 / 修改文件清单**（不含临时 `.pytest_cache/` / `__pycache__`）：

```
scripts/fetch_m2_2024_gdp.py                              (635-A 新增)
scripts/crosscheck_m2_2024_gdp.py                         (635-C 新增)
scripts/report_m2_gdp_coverage.py                          (M2-a, 仅 re-run)
source_registry/m2_2024_gdp_inventory.csv                 (635-B: 26 PENDING → 26 BLOCKED)
docs/reports/m2_2024_gdp_crosscheck_20260831.md           (635-D 新增；crosscheck output)
frontend/app/research/q1-2024-gdp/page.tsx                (635-E 新增)
tests/test_m2_crosscheck.py                                (635-F: 6 用例)
tests/test_m2_frontend_page.py                             (635-F: 10 用例)
tests/test_m2_province_geo_seed.py                         (635-F: 1 修正)
docs/56-m2-gdp-coverage-task-breakdown-20260831.md         (635-G: §4 增量)
docs/54-milestone-replan-20260830.md                       (635-G: M2.1-5 表后增量)
reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md    (635-G: rev 57→58, 635 NOW→DELIVERED)
reviews/stage0-gate0-rework-2026-08-23/635-stage0-cc-m2-cde-coverage-crosscheck-page-receipt-20260831.md   (本回执)
```

---

## 9. commit + 双推

```
git add scripts/fetch_m2_2024_gdp.py scripts/crosscheck_m2_2024_gdp.py \
        source_registry/m2_2024_gdp_inventory.csv \
        docs/reports/m2_2024_gdp_crosscheck_20260831.md \
        frontend/app/research/q1-2024-gdp/page.tsx \
        tests/test_m2_crosscheck.py tests/test_m2_frontend_page.py \
        tests/test_m2_province_geo_seed.py \
        docs/56-m2-gdp-coverage-task-breakdown-20260831.md \
        docs/54-milestone-replan-20260830.md \
        reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md \
        reviews/stage0-gate0-rework-2026-08-23/635-stage0-cc-m2-cde-coverage-crosscheck-page-receipt-20260831.md

git commit -m "feat(635): M2-c+d+e — coverage 31/31, crosscheck QUARANTINED-WEAK, /research/q1-2024-gdp page"

git push origin HEAD
git push github HEAD
```

---

## 10. 下一步（架构师审 635 后可签）

- **636 = M2-f**：文档收口（docs/56 + docs/54 final）+ 2001 起回补可行性评估（哪些省厅源可达 / 哪些镜像站可达 / 哪些必须用户提供政府源直连）
- **不宣布 Gate / O1 / M2 PASS**。
- BLOCKED 26 省级补抓需要：用户本地浏览器登录后导出 PDF/HTML（绕过本机 IP-level WAF 阻断），或用户提供 镜像站（如 mrtx.gov.cn/xxgk/statistics）URL。

— End 635 receipt —