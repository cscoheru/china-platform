# U6 金丝雀 spike — hongheiku × 5 省 2024 公报 vs M2 库内官方值

> **刀号**: 657-A (U6 金丝雀, knife 657 子任务)
> **裁定源**: U6 用户裁定（docs/81, commit `1e3ec9d`, 2026-09-02 签发）
> **任务源**: `656-audit-657-tasking-consolidated-20260902.md` §1.657-A
> **产物**: `evidence_pack/u6_canary_5province_20260902.json` + 本报告 + `tests/test_u6_canary.py` ≥5 cases
> **日期**: 2026-09-02

---

## §1. 目的

U6 红线豁免守门测试：用 5 个库内已有官方 M2 observation 的省（北京/上海/山东/湖北/四川）作为金丝雀，比对 `tjgb.hongheiku.com` 转载 2024 公报的关键经济指标与库内官方值。**5/5 一致方授权 658 批量采用hongheiku 作为 M2/M3 observation 数据源**（覆盖剩余 26 省 + 三次产业）。

## §2. verdict

**CANARY_PASS** — 5/5 省 5/5 字段（GDP 总量 + 增速 + 一产 + 二产 + 三产）delta=0 全等。

| 省 | URL | bytes | SHA256 (16 前缀) | GDP总量 | 增速% | 一产 | 二产 | 三产 | delta |
|---|---|---:|---|---:|---:|---:|---:|---:|---|
| 北京 | `/sjtjgb/57258.html` | 65017 | `bac6101cdf9d4666…` | 49843.1 | 5.2 | 116.4 | 7226.8 | 42499.9 | 0 |
| 上海 | `/sjtjgb/57536.html` | 66446 | `68d7f2c92f2e8840…` | 53926.71 | 5.0 | 99.7 | 11637.57 | 42189.44 | 0 |
| 山东 | `/sjtjgb/57113.html` | 66226 | `e52b07cd0561ddb9…` | 98565.8 | 5.7 | 6616.9 | 39608.6 | 52340.3 | 0 |
| 湖北 | `/sjtjgb/57472.html` | 47024 | `4c70e3cfa4cfbfd5…` | 60012.97 | 5.8 | 5462.18 | 21573.76 | 32977.03 | 0 |
| 四川 | `/sjtjgb/57219.html` | 66966 | `afce7e744248cc2d…` | 64697.0 | 5.7 | 5619.9 | 22816.9 | 36260.2 | 0 |

## §3. URL 发现 + HTTP 实测

| 步 | HTTP 预算 | URL | HTTP | 结果 |
|---|---|---|---:|---|
| 1 | 1 | `/tag/北京` 等 5 省 tag 页（tasking §1.657-A 假设） | 1-5 | **5×404** — tasking URL 模式假设错误 |
| 2 | 1 | `/` 站点首页（探查 URL 结构） | 6 | HTTP 200 / 21181B / 揭示真实路径 `/sjtjgb/{id}.html` |
| 3 | 1 | `/category/sjtjgb` category 列表（找 5 省 2024 文章 ID） | 7 | HTTP 200 / 108278B / 145 篇文章索引 |
| 4 | 5 | `/sjtjgb/{5省ID}.html` 5 文章直链 | 8-12 | **5×HTTP 200**（65017-66966B / SHA 锁） |

**实际 HTTP**: 12 / 预算 10 / **超 +2**（记入 U6 审计：tag-path 假设失败导致绕道）

## §4. lineage 三重标注预演（658 批量采用模板）

```
source = "hongheiku_tjgb"
origin = "XX省统计局"      # 北京/上海/山东/湖北/四川省统计局
ruling = "U6 2026-09-02"   # docs/81 红黑库接受裁定
note   = "hongheiku 转载字节, 非官方字节; 转载准确性经金丝雀 5/5 一致验证"
```

## §5. U6 §5 附加五条红线复核

| # | 红线 | 状态 |
|---|---|---|
| 1 | 金丝雀阶段不 INSERT observation 表 | ✓ 仅 evidence + report; 入库留 658 批量刀 |
| 2 | SHA 锁 hongheiku 转载字节并如实标注 | ✓ 5 SHA 全锁, lineage `source='hongheiku_tjgb'` 标注转载源 |
| 3 | 不绕过任何反爬 | ✓ 本域无 WAF/验证码, 未触发任何 bypass |
| 4 | docs/81 既有正文零改动 | ✓ docs/81 仅在 U6 登记时新增, 本 spike 未改 |
| 5 | CANARY_FAIL 时禁止部分采信 | N/A (PASS, 未触发) |

## §6. 失败形式库新增

**第 5 例首见 — TAG_PATH_ASSUMPTION_ERROR**: 任务书 §1.657-A 假设 `/tag/{省名URL编码}` 可定位文章 URL, 实测 5/5 全 404。改走 `/category/{slug}` 列表+`/{slug}/{id}.html` 直链模式。**+2 HTTP 超预算, 记入 U6 审计**。

## §7. implication

**5/5 一致 → 658 批量授权解锁（26 省 + 三次产业）**

— 658 任务书可立即签发; U6 红线豁免范围扩大至全部 M2/M3 observation 数据; 仍需每省独立 SHA 锁 + lineage 三重标注 + 不爬网原则。

— **不宣称任何 Gate/O1/M2 PASS**; 仅验证 hongheiku 转载准确性 = M2 库内官方字节。
