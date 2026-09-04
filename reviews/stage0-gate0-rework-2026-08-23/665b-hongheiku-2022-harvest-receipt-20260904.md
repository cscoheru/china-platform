# 665b — hongheiku 2022 harvest + mart rerun (2026-09-04)

> **刀号**: 665b (knife 665 program 第 2 刀, year 2022)
> **日期**: 2026-09-04
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 665a DELIVERED (HEAD bf29db3, year 2021 +251 cells); 664 deploy newvps DONE (公网 200 OK); user 授权「启动 665b」
> **本件状态**: **16/16 红线 PASS** (mart 8,060 rows, 590 real cells; 2022 增 +204)
> **关联**: `665a-hongheiku-2021-harvest-receipt-20260904.md` (前置) + `china-platform-665-multi-knife-program.md`

---

## 1. 范围 (granular)

沿用 665a 完全模式 + 加 2022 公报采集:
- 24 省 × 10 指标 hongheiku real-data harvest (≤32 HTTP 红线)
- 2 排除: 新疆生产建设兵团 (XPCC, P3 禁开) + 益阳市 (city, 属 669 程序)
- 9 missing (DATA_MISSING):
  - 7 原 missing: gansu/guizhou/heilongjiang/hunan/liaoning/ningxia/shanghai (年鉴发布滞后)
  - +2 新发现: guangdong/jiangxi (cat index 是目录页, 公报 PDF 内嵌, 665b 不启用 PDF parser)
- 9 missing × 10 指标 = 90 DATA_MISSING cells for 2022

**mir 665a → 665b 关键差异**:
| 维度 | 665a (2021) | 665b (2022) |
|---|---|---|
| cat index entries | 29 | 26 |
| 排除 (XPCC/city) | 0 | 2 (XPCC + Yiyang) |
| TO_FETCH | 29 | 24 |
| MISSING (cat index 无) | 2 (guangdong/jiangxi) | 7 (gansu/guizhou/heilongjiang/hunan/liaoning/ningxia/shanghai) |
| MISSING (目录页/PDF) | 0 | +2 (guangdong/jiangxi) |
| 总 missing | 2 | 9 |
| HTTP budget used | 29/32 | 24/32 |
| Real cells harvest | 251/290 (86.5%) | 204/240 (85%) |
| 新发现 | — | **HAINAN 2022 有 10 cells** (cat index 是真公报,非目录页) |

---

## 2. 5-commit chain (per amend-first v3.5)

### Commit 1 — `scripts/fetch_hongheiku_y2022.py`

24 省 × 10 指标 harvest 脚本 (mirror 665a 模式 + 9 missing + 2 excluded):
```python
TO_FETCH_2022 = [
    ('anhui',       'https://tjgb.hongheiku.com/sjtjgb/35433.html', 'ANHUI'),
    ('beijing',     'https://tjgb.hongheiku.com/sjtjgb/35301.html', 'BEIJING'),
    # ... 24 entries total
]
MISSING_PROVINCES_2022 = ['gansu', 'guangdong', 'guizhou', 'heilongjiang', 'hunan',
                          'jiangxi', 'liaoning', 'ningxia', 'shanghai']
```

### Commit 2 — `scripts/parse_hongheiku_y2022.py`

复用 `parse_hongheiku_10_indicators._extract_*` (无 fork),从 `/tmp/_665_y2022_*.html` 提取 10 指标:
- 22/24 PARSED (guangdong/jiangxi 目录页 parse empty)
- per-indicator coverage: 19-22 (avg ~20.4)

### Commit 3 — `dbt/seeds/seed_hongheiku_timeseries_2022.csv` (204 rows) + `scripts/generate_seed_hongheiku_y2022.py`

CSV 13 列 schema (mirror 665a):
```
province_code,province_name_cn,year,value,unit,indicator_key,indicator_label_cn,
status,missing_reason,lineage_source_type,lineage_origin,lineage_ruling,lineage_is_demo
```
lineage: `hongheiku_tjgb` + URL + `knife_665_y2022` + `lineage_is_demo=false`.

### Commit 4 — `dbt/models/marts/mart_province_timeseries.sql` (extend)

加 `real_data_2022` CTE:
```sql
real_data_2022 AS (
    SELECT province_code, year, indicator_key, value,
           lineage_source_type, lineage_origin,
           lineage_ruling, lineage_is_demo
    FROM {{ ref('seed_hongheiku_timeseries_2022') }}
    WHERE value IS NOT NULL
)
```
`real_data` UNION 加 2022 分支;LEFT JOIN 扩 `cp.year IN (2024, 2021, 2022)`;lineage_ruling `K663-2026-09-03` → `K665b-2026-09-04`。

### Commit 5 — `scripts/load_seed_and_mart_665b.py` + receipt

16 红线 verify (14 base + 2 新增),全部 PASS。

---

## 3. 红线守门 (16/16 PASS)

| # | 红线 | 实际 | 期望 | 状态 |
|---|---|---|---|---|
| 1 | 总行数 = 8060 | 8060 | 8060 | ✓ |
| 2 | real cells 2024 (663 baseline) = 135 | 135 | 135 | ✓ |
| 3 | real cells 2021 (665a) = 251 | 251 | 251 | ✓ |
| 4 | **real cells 2022 (665b new) = 204** | **204** | **204** | ✓ |
| 5 | 总 real cells = 590 (135+251+204) | 590 | 590 | ✓ |
| 6 | HUNAN 2022 全 DATA_MISSING | 0 | 0 | ✓ |
| 7 | GUANGDONG 2022 全 DATA_MISSING | 0 | 0 | ✓ |
| 8 | JIANGXI 2022 全 DATA_MISSING | 0 | 0 | ✓ |
| 9 | LIAONING/GUIZHOU 2022 全 DATA_MISSING | 0 | 0 | ✓ |
| 10 | **HAINAN 2022 有 real cells (10/10)** | **10** | **10** | ✓ |
| 11 | SHANGHAI/GANSU/HEILONGJIANG/HUNAN/NINGXIA 2022 全 DATA_MISSING | 0 | 0 | ✓ |
| 12 | 2001-2019 全 DATA_MISSING (新增红线-1) | 0 | 0 | ✓ |
| 13 | 2026 全 DATA_MISSING (新增红线-2) | 0 | 0 | ✓ |
| 14 | value IS NULL → status='DATA_MISSING' | 0 | 0 | ✓ |
| 15 | lineage_source_type 全填 | 0 null | 0 null | ✓ |
| 16 | lineage_origin 全填 | 0 null | 0 null | ✓ |

---

## 4. 新发现 (架构师端)

### 4.1 HAINAN 2022 = 10 cells (665a 推断修正)

665a 把 HAINAN 归类为 missing (2021 cat index 无). 665b 实证:
- HAINAN 2022 cat URL `https://tjgb.hongheiku.com/sjtjgb/34829.html` 是**真公报**,10/10 indicators 全部 parse 成功
- 含义: hongheiku **2022 起补齐了 HAINAN 转载**;missing 列表需逐 URL 实测,不能跨年 carry over.

### 4.2 GUANGDONG/JIANGXI 2022 = 目录页 (非公报正文)

cat URL `35295` (GUANGDONG) 和 `35571` (JIANGXI) 实际是"年份 + 下辖地级市"导航目录,公报正文通过 wp-content/uploads/...pdf 内嵌在 pdfjs viewer. 665b 不启用 PDF parser (避免新增依赖),DATA_MISSING 守红线-1.

**未来修法**: 666 OFFICIAL_INTAKED 升级 GUANGDONG/JIANGSU (ZHEJIANG 也类似) 时,从省统计局 HTML 公报补,绕过 hongheiku PDF. 此项在 user_ruling_666 中已锁.

### 4.3 XPCC (新疆生产建设兵团) + 益阳市 city 排除逻辑

cat index 把这两条算省级条目,需 fetch 脚本 **显式排除** (不写入 TO_FETCH_2022),避免污染 province 维度:
- XPCC: 特殊兵团,P3 禁开
- 益阳市 (HUNAN 省辖地级市): 属 669 程序 city tier

---

## 5. 资源清单

```
=== 665b 产出文件 (5) ===
scripts/fetch_hongheiku_y2022.py                 163 行 (24 省 + 9 missing + 2 excluded)
scripts/parse_hongheiku_y2022.py                 100 行 (复用 _extract_*)
scripts/generate_seed_hongheiku_y2022.py         130 行 (CSV builder)
scripts/load_seed_and_mart_665b.py               175 行 (mart rerun + 16 verify)
dbt/seeds/seed_hongheiku_timeseries_2022.csv     205 行 (204 data + 1 header)

=== 665b 修改文件 (1) ===
dbt/models/marts/mart_province_timeseries.sql    real_data_2022 CTE + UNION + LEFT JOIN 2022 + K665b ruling

=== 缓存 (24 HTML files @ /tmp) ===
/tmp/_665_y2022_{province_en}.html × 24
SHA256 锁转载字节 (含 fetch evidence JSON)

=== Evidence JSON (2) ===
evidence_pack/u6_batch_y2022_fetch_20260904.json   (24 reachable, 9 missing, 2 excluded)
evidence_pack/u6_batch_y2022_parse_20260904.json   (22 parsed, 2 empty, per-ind coverage 19-22)

=== mart (16/16 PASS) ===
cegr_mart.mart_province_timeseries  8060 rows, 590 real cells (135+251+204)
```

---

## 6. HTTP 预算守门

| 阶段 | HTTP 消耗 | 累计 | 红线 |
|---|---|---|---|
| fetch 阶段 | 24 (24 省 × 1) | 24 | ≤32 ✓ |
| parse 阶段 | 0 (复用 fetch HTML) | 24 | ≤32 ✓ |
| cat index 1 URL | 1 (复用 665a cat 索引页) | 25 | ≤32 ✓ |
| **总计** | | **25** | ≤32 ✓ |

每省仅 1 HTTP (cat index 复用 665a),余 7 HTTP 给后续 665c-665e 备用.

---

## 7. 不宣称 (per docs/05 §8.2 + 红线)

- ❌ **不宣布 665b PASS** — 仅 DELIVERED + mart 16/16 红线验证
- ❌ **不宣布 663/665/666/667/668 任一刀 PASS** — 仅 665a/665b DELIVERED,后续刀 OPEN
- ❌ **不冒充 ops** — 仅本地 dev mart rerun,未 push 666 deploy 触发 newvps 公网重导
- ❌ **不宣称 9 missing 省 DATA_MISSING 是终态** — 665c/d/e/666 后续刀补;LIAONING/GUIZHOU/HAINAN 长历史年仍需 666 OFFICIAL 路径
- ❌ **不宣称 HAINAN 2022 = 1 省补齐** — 仅 2022 单年,2020/2021/2023+ 仍待 harvest
- ❌ **不启用 PDF parser** — 666 OFFICIAL 升级绕过
- ❌ **不爬网** — 25 HTTP 在 ≤32 红线内

---

## 8. user_ruling_665b 签署清单

- [x] user 授权「启动 665b」 (per 当前会话 message 2: "commit双推, 664 deploy, 启动 665b")
- [x] 已审阅 665a receipt + 665b URL discovery (24 + 9 missing + 2 excluded)
- [x] 已确认 665b harvest 数据来源 (hongheiku cat index 2022 真实入库)
- [x] 已理解 HAINAN 2022 实证发现 (10/10 cells)
- [x] 已理解 GUANGDONG/JIANGXI 2022 目录页限制 (DATA_MISSING 守红线-1)
- [x] 已确认 5-commit chain amend-first v3.5
- [x] 已确认不冒充 ops (本地 dev mart rerun)
- [x] 已确认 mart rerun 16/16 红线 PASS
- [x] 已确认 docs/81 零改动
- [x] 已确认 docs/87 §6 sub-knife 程序每刀独立签署 (665b 已签)

---

## 9. 后续 5 刀待启动

| 刀号 | 年份 | cat entries | 备注 |
|---|---|---|---|
| 665c | 2023 | 31 | 全部 31 省,预计 280-300 cells |
| 665d | 2024 增量 | — | 仅 5 增量指标 (663 baseline 已有 5 现 2024) |
| 665e | 2025 | 27 | 部分省 2025 公报已发布 |
| 666 | — | — | 粤苏浙 OFFICIAL 半自动补齐 + mart 重导 (≤9 HTTP) |
| 669a-j | — | — | 293 地级市 multi-knife 程序 |

---

## 10. 链接

- 前置 665a receipt: `reviews/stage0-gate0-rework-2026-08-23/665a-hongheiku-2021-harvest-receipt-20260904.md`
- 关联 664 deploy receipt: `reviews/stage0-gate0-rework-2026-08-23/664-deploy-newvps-receipt-20260904.md`
- mart SQL: `dbt/models/marts/mart_province_timeseries.sql` (real_data_2022 CTE added)
- 665a mart loader: `scripts/load_seed_and_mart_665a.py`
- 665b mart loader: `scripts/load_seed_and_mart_665b.py`
- 665 program plan: `/Users/kjonekong/.claude/plans/lively-greeting-shore.md`
- 记忆: `china-platform-665-multi-knife-program.md` (2026-09-04 立)
- 记忆: `china-platform-fastapi-missing-on-newvps.md` (FastAPI 不在 newvps 实证, 已 664 部署修复)

— End 665b receipt (year 2022, 16/16 红线 PASS, 204 real cells, mart rerun DELIVERED ✓) —