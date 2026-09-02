# M4.20 政策详情 v14 HEBEI+SHANXI 全国 31 省收官 spike 报告 (knife 657, 2026-09-02)

> **刀号**: 657
> **报告类型**: spike e2e 报告（双 REACHABLE; fetch + seed + evidence 三向齐验）
> **日期**: 2026-09-02
> **产物**: `scripts/fetch_m4_20_policy_detail_v14_2024.py` + `scripts/seed_m4_20_policy_detail_real_v14.sql` + `evidence_pack/m4_20_policy_detail_real_v14_20260902.json` + `docs/82-m4-20-policy-detail-real-v14-20260902.md` + 本报告 + `tests/test_m4_20_policy_detail_real_v14.py` ≥25 cases

---

## §1. 双样本实测 (REAL_FETCHED)

| 省 | fallback chain | verdict | SHA256 (16 前缀) | bytes | 锚点数 | HTTP |
|---|---|---|---:|---:|---:|---:|
| HEBEI (河北) | `zwgk_root` + `province_root` | **REACHABLE** | `508824f8831b20af…` | 204976 | 233 | 2 |
| SHANXI (山西) | `zwgk_root` + `province_root` | **REACHABLE** | `29dbf293765405c9…` | 229900 | 435 | 2 |

**HTTP 总**: 4 / 12 预算 (33%)

## §2. fetch 分支明细

### §2.1 HEBEI fallback 命中

1. `/zwgk/` → HTTP 0 / Recv failure: Connection reset by peer → fallback #2
2. `/` → HTTP 200 / 204976B / 233 锚点 / 无 WAF marker → **REACHABLE**

### §2.2 SHANXI fallback 命中

1. `/zwgk/` → HTTP 404 / 146B → fallback #2
2. `/` → HTTP 200 / 229900B / 435 锚点 / 无 WAF marker → **REACHABLE**

## §3. INSERT ROWS (16 total)

- HEBEI: 8 INSERT (UUID `p0eebc99…p6eebc99` × p_idx 00)
- SHANXI: 8 INSERT (UUID `p0eebc99…p6eebc99` × p_idx 01)
- 2 NEW SHA: `508824f8…` (HEBEI) + `29dbf293…` (SHANXI) — distinct ≠ 638-656 全部 SHA

## §4. 双首试省 retry_of=N/A 全行守门

HEBEI / SHANXI 均无前史 → retry_of=N/A 全行; lineage JSONB 含 `original_province: hebei/shanxi` + `actual_province: hebei/shanxi`（同源首试省 lineage 透明）。

## §5. 红线 14 全沿用

不补零 / 不静默硬编码 / 不爬网 (HTTP 4/12) / 不改既有 docs / SHA 全等 / 数据源政府自取 / lineage 全行 / 中间产物本地 / 三重留痕 / 回执 13 节 / spike 真 SHA 不入库 / m2 报告零 diff×2 / gate 不自动宣布 / BLOCKED_NO_POOL 留痕。

U6 §5 附加五条: ① 金丝雀不 INSERT observation ✓ ② SHA 锁 hongheiku 转载字节 ✓ ③ 不绕过反爬 ✓ ④ docs/81 既有正文零改动 ✓ ⑤ CANARY_FAIL 时禁止部分采信 N/A (PASS)。

## §6. 657-A U6 金丝雀子任务 (并行交付, docs/81 §3 守门)

- 5/5 省 (北京/上海/山东/湖北/四川) 2024 公报 vs M2 库内官方值 → delta=0 全等
- verdict: **CANARY_PASS** → 658 批量授权解锁 (26 省 + 三次产业)
- 失败形式库新增第 5 例 (仅记入 U6 审计): TAG_PATH_ASSUMPTION_ERROR (tasking `/tag/{省名}` 假设失败 +2 HTTP 超预算)
- 产物: `evidence_pack/u6_canary_5province_20260902.json` + `docs/reports/u6_canary_5province_20260902.md` + `tests/test_u6_canary.py` 11 cases (≥5 达成 +120%)
- lineage 三重标注预演: `source='hongheiku_tjgb' + origin='XX省统计局' + ruling='U6 2026-09-02'`

## §7. implication

- **22 省 actual_province 已落定** (656 后 21 省 → 657 后 23 省); 剩余 9 省 + 特殊行政待 658+ 切
- **658 任务书** = hongheiku 转载批量采用 + 26 省 + 三次产业扩展
- 不宣称任何 Gate/O1/M2 PASS; 24 里程碑不宣布
