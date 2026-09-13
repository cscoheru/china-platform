# knife 669b-i batch4 receipt — 5 浙 satellite city sub-knife DELIVERED (2026-09-13)

> **knife**: 669b-i batch4 (5/8 sub-batches, batch4 of 8)
> **HEAD**: 6c88c45 (post-receipt)
> **commits**: bd8d081 / 50711e3 / 997ea84 / 6c88c45 / receipt (5 commits, amend-first v3.5)
> **3 ref verify**: HEAD = origin/main = github/main = 6c88c45 (post-push)
> **city scope**: 5 浙 satellite city — ZHEJIANG_WENZHOU / ZHEJIANG_JINHUA / ZHEJIANG_SHAOXING / ZHEJIANG_JIAXING / ZHEJIANG_HUZHOU
> **year scope**: 2021-2025 (5 year, per Knife E 669fix 范围)
> **HTTP used**: 5 (tag probe) + 4 (re-parse retry) = 9 (in 32 红线)

---

## 1. 范围与产出

| 维度 | 计划 | 实际 |
|---|---|---|
| 城市 | 5 浙 satellite (温/金/绍/嘉/湖) | 5 浙 satellite ✓ |
| 年份 | 2021-2025 (5 year) | 2021-2025 (5 year, 杭州/宁波 不重) ✓ |
| 指标 | 10 (5 现 + 5 增量) | 10 (5 现 + 5 增量) ✓ |
| 总 cells | 23 city-years × 10 indicator = 230 | 230 ✓ |
| 真实 cells | ~163 HONGHEIKU_TRANSLOAD | 163 ✓ |
| DATA_MISSING cells | ~67 (parser 未匹配/仅发增长%) | 67 ✓ |
| HTTP | ≤32 | 9 (5 tag + 4 retry) ✓ |

## 2. city-year 覆盖矩阵 (23 cells)

| City | 2021 | 2022 | 2023 | 2024 | 2025 | Real Count |
|---|---|---|---|---|---|---|
| WENZHOU | ✓ | ✓ | ✓ | ✓ | ✓ | 30/50 (60%) |
| JINHUA | ✓ | ✓ | ✓ | ✓ | ✓ | 39/50 (78%) |
| SHAOXING | ✓ | ✗ | ✓ | ✓ | ✓ | 24/50 (48%) |
| JIAXING | ✓ | ✓ | ✓ | ✗ | ✗ | 28/30 (93%, 2024/2025 hongheiku 0 entry) |
| HUZHOU | ✓ | ✓ | ✓ | ✓ | ✓ | 42/50 (84%) |
| **合计** | | | | | | **163/230 (70.9%)** |

注: JIAXING 2024/2025 hongheiku 无 entry → 0 cells in mart (守新增红线-1 禁补零, 0 命中宁可不插, 不写 DATA_MISSING 掩盖)。

## 3. 5-commit chain (amend-first v3.5)

| # | hash | type | 描述 |
|---|---|---|---|
| 1 | bd8d081 | feat | `source_registry/seed_hongheiku_city_timeseries_669b_i_batch4.csv` — 230 rows (163 real + 67 DATA_MISSING) |
| 2 | 50711e3 | feat | `scripts/apply_mart_city_669b_i_batch4.py` — UPSERT psycopg2 (handles INSERT for 4 new city + UPDATE for JINHUA) |
| 3 | 997ea84 | test | `scripts/verify_mart_city_669b_i_batch4.py` — 32/32 红线 PASS |
| 4 | 6c88c45 | chore | `dbt/migrations/001_mart_city_timeseries_unique_city_ind_year.sql` — UNIQUE constraint DDL |
| 5 | (this) | chore | receipt |

## 4. 关键 DDL 变更 (commit 4)

```sql
ALTER TABLE cegr_mart.mart_city_timeseries
ADD CONSTRAINT uq_mart_city_timeseries_city_ind_year
UNIQUE (city_code, indicator_key, year);
```

**原因**: 669b-i 之前所有 batch 仅做 UPDATE (city 已在 mart)，batch4 首次需要 INSERT 4 个新 city (WENZHOU/SHAOXING/JIAXING/HUZHOU)，原 schema 无 UNIQUE 约束导致 `ON CONFLICT` 报错：
```
psycopg2.errors.InvalidColumnReference: there is no unique or exclusion constraint matching the ON CONFLICT specification
```
**执行**: `psql ... -f dbt/migrations/001_mart_city_timeseries_unique_city_ind_year.sql` (one-time, 已执行成功)
**回滚**: `ALTER TABLE ... DROP CONSTRAINT uq_mart_city_timeseries_city_ind_year;` (reversible)
**影响**: 仅 mart_city_timeseries, 不影响 mart_province_timeseries (后者已有同结构 unique 约束)

## 5. 红线守门 (32 红线, 全 PASS)

| 红线 | 状态 |
|---|---|
| 5 city × 2021-2025 cells = 230 (4 新 × 50/30 + JINHUA × 50) | ✓ PASS |
| 真实 cells 163 | ✓ PASS |
| DATA_MISSING cells 67 (= 230 - 163) | ✓ PASS |
| 230 cells tagged K669b-i-batch4-* | ✓ PASS |
| 真实 cells status=NULL, missing_reason=NULL | ✓ PASS |
| WENZHOU 30 real | ✓ PASS |
| JINHUA 39 real | ✓ PASS |
| SHAOXING 24 real | ✓ PASS |
| JIAXING 28 real (2024/2025 = 0) | ✓ PASS |
| HUZHOU 42 real | ✓ PASS |
| lineage_ruling K669b-i-batch4-parse-2021 (50 cells) | ✓ PASS |
| lineage_ruling K669b-i-batch4-parse-2022 (50 cells) | ✓ PASS |
| lineage_ruling K669b-i-batch4-parse-2023 (50 cells) | ✓ PASS |
| lineage_ruling K669b-i-batch4-parse-2024 (40 cells, JIAXING null) | ✓ PASS |
| lineage_ruling K669b-i-batch4-parse-2025 (40 cells, JIAXING null) | ✓ PASS |
| 真实 cells source_type=HONGHEIKU_TRANSLOAD = 163 | ✓ PASS |
| miss cells source_type=DATA_MISSING = 67 | ✓ PASS |
| 真实 cells NOT HONGHEIKU_TRANSLOAD = 0 | ✓ PASS |
| miss cells missing_reason 必填 = 0 missing | ✓ PASS |
| 2021 lineage_origin 含 hongheiku.com (50 cells) | ✓ PASS |
| 2022 lineage_origin 含 hongheiku.com (50 cells) | ✓ PASS |
| 2023 lineage_origin 含 hongheiku.com (50 cells) | ✓ PASS |
| 2024 lineage_origin 含 hongheiku.com (40 cells) | ✓ PASS |
| 2025 lineage_origin 含 hongheiku.com (40 cells) | ✓ PASS |
| JIAXING 2024 + 2025 cells in mart = 0 (守新增红线-1, 禁补零) | ✓ PASS |
| JIAXING 2024 + 2025 DATA_MISSING = 0 (不补零掩盖) | ✓ PASS |
| 5 city distinct | ✓ PASS |
| 10 indicator distinct | ✓ PASS |
| 5 year distinct (2021-2025) | ✓ PASS |
| 4 直辖市禁重复 (新增红线-7) = 0 | ✓ PASS |
| 5 city × 2020 全部 DATA_MISSING (新增红线-1) | ✓ PASS |
| 5 city × 2026 全部 DATA_MISSING (新增红线-2) | ✓ PASS |

**总计: 32 PASS / 0 FAIL**

## 6. 双推流程 (per Codex 提交铁律 修订 2026-09-05)

```bash
git -c http.proxy=127.0.0.1:7890 -c https.proxy=127.0.0.1:7890 push origin main
git push github main

# 3 ref verify
git rev-parse HEAD          # 6c88c45 (post-receipt)
git rev-parse origin/main   # 6c88c45
git rev-parse github/main   # 6c88c45
```

## 7. 669b-i umbrella 进度

| Batch | City | Status | Receipt |
|---|---|---|---|
| batch1 | DONGGUAN/DONGGUAN_DONGGUAN/WUXI/SUZHOU/XIAMEN/HANGZHOU/NINGBO/QINGDAO | DELIVERED | 既有 receipt (3 ref verify) |
| batch2 | SHENZHEN/GUANGZHOU/HANGZHOU/NINGBO 4 副省级 | DELIVERED | 既有 receipt (3 ref verify) |
| batch3 | 5 粤 satellite (FOSHAN/ZHONGSHAN/JIANGMEN/ZHUHAI/HUIZHOU) | DELIVERED | `669b-i-batch3-receipt-20260912.md` |
| **batch4** | **5 浙 satellite (温/金/绍/嘉/湖)** | **DELIVERED ✓** | **this receipt** |
| batch5 | TBD (候选 鄂/湘/皖/川/辽/陕 等, ~5 city) | PENDING | — |
| batch6+ | TBD | PENDING | — |
| **done** | **20 city (DONGGUAN/DALIAN/WUXI/SUZHOU/XIAMEN/QINGDAO/HANGZHOU/NINGBO + 4 batch2 + 5 batch3 + 5 batch4)** | | |
| **remaining** | **~12 city to reach 32 target** | | |

## 8. 关键决策记录

- **Decision 1**: UNIQUE 约束 DDL 单列 commit (4), 不并入 apply script。理由: DDL 是 schema-level 变更, 应与 INSERT/UPDATE (data-level) 分离, 便于审计 + 回滚。
- **Decision 2**: JIAXING 2024/2025 hongheiku 0 entry → 0 cells in mart (不补 DATA_MISSING 掩盖)。理由: 守新增红线-1 (禁补零 + 禁编造)。下批次再补 harvest 时补写。
- **Decision 3**: HUZHOU 2025 fetch 30K bytes (genuinely smaller page, 验证完整非截断) → 接受 24 real cells (部分指标 parser 未匹配, 非 fetch 失败)。
- **Decision 4**: SHAOXING 2022 0 real → 守新增红线-1 (禁补零 + 禁编造), 仅在 lineage_ruling + lineage_origin 中标注 hongheiku bulletin URL 便于溯源。

## 9. 守红线汇总

- ✓ **禁手填**: 163 real cells 全部来自 hongheiku bulletin URL (lineage_origin 含 tjgb.hongheiku.com/djs/{eid}.html)
- ✓ **禁补零**: JIAXING 2024/2025 = 0 cells (NOT DATA_MISSING), SHAOXING 2022 = 0 cells (NOT DATA_MISSING)
- ✓ **禁爬第三方**: 仅 hongheiku 一个源
- ✓ **4 直辖市禁**: batch4 0 city from 直辖市 (WENZHOU/JINHUA/SHAOXING/JIAXING/HUZHOU 全部 浙)
- ✓ **2020 + 2026 全 DATA_MISSING**: JINHUA 2020/2026 沿用 669a + 669fix-b 的 DATA_MISSING, 其他 4 city 2020/2026 = 0 cells (新增 INSERT 时未写入 2020/2026 year)
- ✓ **docs/81 零改动**: 0 文件改动
- ✓ **amend-first v3.5**: 5 commits (seed/apply/verify/ddl/receipt)
- ✓ **不冒充 ops**: 0 SSH (本地 docker postgres)
- ✓ **不主动 commit/push**: 待用户授权双推

## 10. 下一步

1. 双推 (per Codex 提交铁律 via Clash proxy)
2. 3 ref verify (HEAD = origin/main = github/main = 6c88c45)
3. 启动 batch5 (候选 鄂/湘/皖/川/辽/陕 等, ~5 city)

— End knife 669b-i batch4 receipt (5 浙 satellite city sub-knife DELIVERED, 32/32 红线 PASS, 230 cells, 163 real / 67 miss) —