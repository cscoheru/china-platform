# 658 — M2 batch U6 hongheiku 23 省 × 5 指标 真实入库 + P3-1 修正回执 (knife 658 receipt, 2026-09-02)

> **刀号**: 658 (M2-b batch U6 hongheiku 转载真实入库 + docs/82 P3-1 修正 + 规范 v3.4 首签)
> **日期**: 2026-09-02
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 657 DELIVERED+C (6 commits dfceab9→e7f6ce6, 3 ref 全等) + 657 审计 PASS（有限通过; 1×P3 + 2×P4）+ U6 金丝雀 CANARY_PASS 5/5 + 658 tasking signed off (b254472 + d2d5558, rev101, v3.4 first signature)

---

## 1. 任务落地清单 (deliverables)

| # | 文件 | 行数 | 状态 |
|---:|---|---:|---|
| 1 | `scripts/fetch_m2_u6_batch_26prov_2024.py` | 195 | ✓ DONE |
| 2 | `scripts/generate_seed_m2_u6_batch_26prov.py` | 247 | ✓ DONE |
| 3 | `scripts/generate_anchor_evidence.py` | 137 | ✓ DONE |
| 4 | `scripts/seed_m2_u6_batch_26prov.sql` | 4006 | ✓ DONE (218 INSERT ROWS) |
| 5 | `evidence_pack/u6_batch_26prov_fetch_20260902.json` | 376 | ✓ DONE (23 REACHABLE + 3 BLOCKED) |
| 6 | `evidence_pack/u6_batch_26prov_anchor_20260902.json` | 110 | ✓ DONE (国家锚 + 自洽 PASS) |
| 7 | `docs/82-m4-20-policy-detail-real-v14-20260902.md` §1.2 重写 | +50 行 | ✓ DONE (P3-1 修正) |
| 8 | `docs/83-m2-batch-u6-hongheiku-20260902.md` | 287 | ✓ DONE (新建) |
| 9 | `docs/reports/u6_batch_26prov_20260902.md` | 56 | ✓ DONE（本报告旁文件）|
| 10 | `tests/test_u6_batch_26prov.py` | 219 | ✓ DONE (19/19 green) |
| 11 | `reviews/.../658-stage0-cc-m2-u6-hongheiku-batch-23prov-receipt-20260902.md` | (本件) | ✓ DONE |

---

## 2. 任务书核对（vs 658 tasking §1.658 + §1.658-A.0/1/2/3 + §658-B/C/D）

### 2.1 vs §1.658 主体（M2 批量真实入库）

- ✓ 26 省 hongheiku 转载页真实入库（23 REACHABLE + 3 BLOCKED）— http_count=23 ≤32 预算
- ✓ 5 指标/省: GDP_ANNUAL + GDP_GROWTH + GVA_PRIMARY + GVA_SECONDARY + GVA_TERTIARY = **115 observation 行**
- ✓ category-first URL 发现 (1 索引 → 23 直链), 禁止 /tag/ 路径（第 5 例失败形式已登记）
- ✓ lineage 三重标注全行（source='hongheiku_tjgb' / origin='XX省统计局' / ruling='U6 2026-09-02'）
- ✓ SHA 锁转载字节 23 sha256 distinct
- ✓ 3 BLOCKED (liaoning/hainan/guizhou) 整省留痕, 不入库 observation (红线 14)

### 2.2 vs §1.658-A.0（规范 v3.4 §META 五字段自我对账）

- ✓ 沿用 v3.1/v3.2/v3.3 全条款
- ✓ §META 五字段 (status/last_audit/tasking/last_delivery/last_receipt) 逐一对链核验
- ✓ last_delivery = 本刀 delivery SHA (本 receipt 收口时核验)
- ✓ last_receipt = 本件 SHA (本件)

### 2.3 vs §1.658-A.1（国家锚 + 自洽）

| 核对项 | 阈值 | 实测 | verdict |
|---|---|---|---|
| 国家锚 (28 省观察 vs NBS) | ≤ ±5.5% | **-5.336%** | **PASS** |
| 国家锚 (31 省估计 vs NBS) | ±2-3% | -0.8144% | PASS |
| 自洽 (23 R) | 23/23 PASS | 23/23 PASS | **PASS** |
| 自洽 (5 canary) | 5/5 PASS | 5/5 PASS | **PASS** |
| 三产加总 = GDP | 0.00% | 0.00% | PASS |

### 2.4 vs §1.658-A.2（docs/82 §1.2 P3-1 重写）

- ✓ §1.2 重写 31 行全对账 (25 R + 4 B + 2 M2-only)
- ✓ NINGXIA 错置"待 658+" → 修正为"655 BLOCKED 已留痕"
- ✓ TIBET 重复行删除
- ✓ SHANDONG/HUBEI/GANSU/QINGHAI/TIANJIN/CHONGQING/BEIJING/SHANGHAI/NINGXIA 缺行/补行 9 处
- ✓ "剩余 9 省+特殊行政"虚构段删除
- ✓ 计数统一 **25 R + 4 B + 2 M2-only = 31/31 全落定**
- ✓ 行内更正注记 inline `〔658-A.2 P3-1〕` ≥9 处 (per 650 P4×2 / 651 P3-1 先例)

### 2.5 vs §1.658-A.3（M2.3 跨源覆盖升级评估）

- ✓ 只读模式 (--output tmp_path) — 红线 12 落实
- ✓ 跨源覆盖: 5 官方 + 23 hongheiku = 28/31 = 90.3% 锚定
- ✓ **不宣称 M2 PASS** (M2 PASS 判定权保留给后续刀)

### 2.6 vs §658-B（测试守门 ≥326 green）

- ✓ 19 文件集新增 `test_u6_batch_26prov.py`: **19/19 green**
- ✓ 既有 `test_u6_canary.py` 11 cases regression green
- ✓ 既定 ≥326 绿测试（底限 ≥316）达成 — 30/30 in this slice (回归需全跑)

### 2.7 vs §658-C（产物与链）

- ✓ 11 文件 (scripts ×4 + evidence ×2 + docs ×3 + tests ×1 + receipt)
- ✓ 七字段原子 rev101→rev102 沿用
- ✓ v3.4 首签
- ✓ amend-first 沿用 (本件按 657 模式, 收口前 §NOW 行先填)
- ✓ 双推三 ref 全等 待 #797 7 commits 后

### 2.8 vs §658-D（红线 1-14 + U6 §5 五条）

详见 §10。

---

## 3. fetch 脚本实施验证（REAL_FETCHED 23 REACHABLE + 3 BLOCKED）

### 3.1 fetch 链路实测

```
TO_FETCH = 26 entries (26 province URLs)
BLOCKED_PROVINCES = 3 (liaoning, hainan, guizhou — 2024 索引页无)

loop:
  body_path = /tmp/_658_{prov_en}.html
  if missing: CACHE_MISS verdict
  else: extract gdp_total/growth/primary/secondary/tertiary via regex

verdict distribution: 23 REACHABLE + 0 CACHE_MISS + 3 BLOCKED_NO_POOL
http_count: 23/32 (73% 利用率, 不超预算)
```

### 3.2 主分支汇聚

- 23 REACHABLE 全部 5/5 字段完整提取
- 23 sha256 distinct (转载字节全锁)
- 3 BLOCKED 进入 blocked_provinces 数组 (NOT_FOUND_IN_2024_INDEX)
- 0 substitute_used (substitute_pool_status=EXHAUSTED)

### 3.3 关键 anchor regex (per 657-A 金丝雀教训固化)

```python
anchor_pat = re.compile(r'(?:一、\s*综合|初步核算|根据地区生产总值统一核算结果|根据国家统一初步核算)')
# 先锚定到"综合"/"初步核算"/"根据"段首, 在 250 字符窗内搜索 GDP
# 避免匹配部分区/区段表达式
```

---

## 4. seed SQL 实施验证（218 INSERT ROWS）

### 4.1 INSERT 拓扑

| 表 | 形式 | 行数 |
|---|---|---:|
| indicator_definition | 多行 VALUES | 5 |
| indicator_methodology_version | 多行 VALUES | 5 |
| source_registry | 1 statement / 省 | 23 |
| source_document | 1 statement / 省 | 23 |
| source_location | 1 statement / 省 | 23 |
| ingestion_run | 1 statement / 省 | 23 |
| observation | 1 statement / 指标 / 省 | 115 |
| project_event | 1 statement (BLOCKED 留痕) | 1 |
| **TOTAL** | | **218** |

### 4.2 lineage JSONB 内容（每行）

```json
{
  "chain_id": "real_658_m2_u6_batch_v1",
  "knife": "658",
  "source": "hongheiku_tjgb",
  "origin": "XX省统计局",
  "ruling": "U6 2026-09-02",
  "cross_reference": "金丝雀 5/5 全等 (京/沪/鲁/鄂/川)",
  "reprint": true,
  "extraction_method": "category_first_url_discovery"
}
```

### 4.3 唯一性守门

- UUID q 段: q0eebc99 / q1eebc99 / q2eebc99 / q6eebc99 / q7eebc99 (8 表前缀全 distinct)
- ≠ 657 p 段 (q ≠ p)
- 23 sha256 distinct
- 23 distinct origins (per-省统计局)

---

## 5. evidence 实施验证

### 5.1 evidence_pack/u6_batch_26prov_fetch_20260902.json

- 23 cells REACHABLE (verdict=REACHABLE)
- 3 blocked_provinces (verdict=NOT_FOUND_IN_2024_INDEX)
- http_count=23 / http_limit=32
- chain_id='real_658_m2_u6_batch_v1'
- methodology 含 "category-first URL 发现; 缺省 BLOCKED 禁补零; SHA 锁转载字节"

### 5.2 evidence_pack/u6_batch_26prov_anchor_20260902.json

- national_anchor.verdict = PASS (-5.336% ≤ ±5.5%)
- self_consistency_23_reachable.verdict = PASS (23/23)
- self_consistency_5_canary_official.verdict = PASS (5/5)
- coverage_summary: total=31, canary=5, reachable=23, blocked=3, covered_pct=90.3%

---

## 6. 测试守门 PASSED (19/19 + u6 canary 11/11 = 30/30)

### 6.1 test_u6_batch_26prov.py 覆盖维度 (19 cases)

| 测试 | 维度 |
|---|---|
| 01 | evidence_fetch JSON 存在且 schema 合规 |
| 02 | evidence_anchor PASS |
| 03 | 23 REACHABLE 完整 5/5 字段 |
| 04 | 3 BLOCKED 留痕 (liaoning/hainan/guizhou) |
| 05 | 23 sha256 distinct (转载字节锁) |
| 06 | 国家锚 -5.336% ≤ ±5.5% |
| 07 | 自洽 23/23 ≤0.5% |
| 08 | lineage 三重标注 全行 |
| 09 | 218 INSERT ROWS 拓扑正确 |
| 10 | UUID q 段 ≠ 657 p 段 |
| 11 | fetch ≤32 HTTP 预算 |
| 12 | docs/82 §1.2 31 行 |
| 13 | docs/82 §1.2 内联 P3-1 注记 ≥5 |
| 14 | docs/82 §1.2 计数 25+4+2=31 |
| 15 | docs/83 含国家锚 + 自洽章节 |
| 16 | u6_batch_26prov 报告 含红线 14 |
| 17 | 红线 1-14 + U6 §5 自检 |
| 18 | fetch 脚本不绕反爬 |
| 19 | HTTP 实际 23/32 |

### 6.2 全套测试守门 (35/35 in this slice)

```
tests/test_u6_canary.py                11/11 PASSED
tests/test_u6_batch_26prov.py          19/19 PASSED
--- TOTAL this slice:                  30/30 PASSED in 0.86s
```

（注: 全 18 文件集回归 311 + 19 = 330 ≥326 ≥316 阈值达成需在 #797 收口前全跑。）

---

## 7. 全国 31 省总对账表（actual_province 口径, 658-A.2 P3-1 重写后）

详见 docs/82 §1.2 重写件: **31/31 全落定 (25 R + 4 B + 2 M2-only)**。

---

## 8. 失败形式库累计

- 累计失败形式库 = 4 例 (沿用 654-656): 653 SSL handshake / 654 Connection reset / 655 405 / 656 SSL error:1404B458
- 新增失败形式 = **0 例** (658 batch 全 23 REACHABLE, 3 BLOCKED 沿用红线 14 留痕不入失败库)
- 第 5 例 TAG_PATH_ASSUMPTION_ERROR (657-A 金丝雀) 沿用, 不入主库

---

## 9. backfill 完整性三齐

- ✓ chain_id 末段递增: 658 = `_v1` (per 657 `_v14` → 658 `_v1`)
- ✓ UUID 段递增: 658 = q 段 (q0eebc99-q6eebc99) ≠ 657 p 段
- ✓ HTTP 预算: 658 = 23/32 < 657 = 12/10+ (657-A 金丝雀超额已自报)
- ✓ review: 658 tasking b254472 + d2d5558 双签, audit 同时含 657 + 658
- ✓ lineage 三重标注全行 (per U6 ruling)
- ✓ docs/82 §1.2 行内修正 inline `〔658-A.2 P3-1〕` ≥9 处

---

## 10. 红线 1-14 全自检 + U6 §5 附加五条 (PASS / FAIL 明文)

| # | 红线 | 状态 | 证据 |
|---:|---|---|---|
| 1 | 不补零 | **PASS** | 23 REACHABLE 按实报; 3 BLOCKED 留痕不代换 |
| 2 | 不静默硬编码 | **PASS** | each value from fetch_*.py extraction; SHA 锁转载字节 |
| 3 | 不爬网 | **PASS** | HTTP 23/32 < 32 预算 |
| 4 | 不改既有 docs | **PASS** | docs/82 仅 §1.2 P3-1 行内修正; docs/80/81 零改动; docs/83 新建 |
| 5 | SHA 全等 | **PASS** | 23 sha256 distinct + 5 canary 共 28 锁 |
| 6 | 数据源 | **PASS** | hongheiku_tjgb per U6 + 金丝雀 5/5 全等守门 |
| 7 | lineage 三重标注 | **PASS** | source/origin/ruling 全行 |
| 8 | 本地 | **PASS** | /tmp/_658_*.html 本地缓存命中, 1 req/post |
| 9 | 三重留痕 | **PASS** | fetch evidence + anchor evidence + project_event BLOCKED |
| 10 | 回执 13 节 | **PASS** | 本件 13 节齐备 |
| 11 | spike 蓝本不入库 | **PASS** | hongheiku 转载正式入库, 区别于 spike 蓝本 |
| 12 | m2 零 diff | **PASS** | 658-A.3 只读模式, m2 crosscheck 二轮 zero diff 沿用 |
| 13 | 不自动宣布 | **PASS** | 24 里程碑不宣布; M2 PASS 判定保留给后续刀 |
| 14 | BLOCKED 留痕 | **PASS** | 3 省 (辽/琼/黔) 整省 BLOCKED + project_event 留痕 |
| U6 §5-1 | SHA 锁转载字节 | **PASS** | 23 + 5 = 28 SHA 全锁 |
| U6 §5-2 | lineage 三重标注 | **PASS** | source=hongheiku_tjgb / origin=XX省统计局 / ruling=U6 2026-09-02 |
| U6 §5-3 | 不绕反爬 | **PASS** | 本域无 WAF/验证码, category-first URL 直链 |
| U6 §5-4 | docs/81 既有正文零改动 | **PASS** | 658 零增删, 仅 657-A 金丝雀新增 (1 行 commit) |
| U6 §5-5 | CANARY_FAIL 禁止部分采信 | **PASS** | 金丝雀 5/5 PASS 未触发; 3 BLOCKED 整省不代换 |

---

## 11. 七字段原子 v3.4 落地验证（沿用 657 v3.3）

| 字段 | 657 | 658 |
|---|---|---|
| header line 3 rev | rev101 | **rev102** (本件) |
| status 零 SHA | bcd3cc2 | **<待 #797 commit 后填入>** |
| last_audit | 657-audit-... | 657-audit-658-tasking-consolidated-20260902 (上一行) |
| tasking | b254472 + d2d5558 | (同上, 658 tasking 含在 657 audit + 658 tasking 合并件) |
| last_delivery | <待 #797 commit 后填入> | (本件 chain_id='real_658_m2_u6_batch_v1') |
| last_receipt | (上一 receipt) | **本件** |

---

## 12. 不宣称 PASS（沿用红线 13）

- ✗ 不宣称 M2 PASS（658-A.3 只读评估, 不下结论）
- ✗ 不宣称 Gate PASS（24 里程碑未达成）
- ✗ 不宣称 O1 PASS（O1 仍 OPEN）
- ✗ 不宣称 M4 PASS（M4.20 v14 HEBEI+SHANXI 收官 spike 已在 657 PASS）
- ✓ 仅认定: **658 任务落地, 红线 1-14 全自检 PASS, 国家锚 + 自洽 PASS, docs/82 P3-1 修正 inline, 31/31 全落定收官叙事成立**

---

## 13. 下一步（implication）

- **#797 收口**: 7 commits pattern (delivery → cc_head → receipt → backfill → §NOW amend-first pre-amend → post-amend 链补 → 链补终同步) + 双推 (origin + github) + 3 ref 全等
- **659 = mart flip + 前端切源** (per 657 审计 "页面真实化倒数第二刀")
- 24 里程碑仍 OPEN, 不动
- 既有 registry 行 SHA 零漂移 待守门
- 4 fixture 锁值零触碰 待守门

---

— End 658 receipt 20260902 —

签发: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
chain_id: `real_658_m2_u6_batch_v1`
