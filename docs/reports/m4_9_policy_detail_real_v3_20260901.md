# M4.9 2 样本政策详情 v3 真实化 spike 抓取报告（2026-09-01，knife 646 M4.9 side）

> **类型**: 646-A.1 真实抓取 (read-only;**不写 cegr.* 表**)
> **前置**: 645 DELIVERED + 审计 PASS (`645-stage0-cursor-s645-m6-m4-8-audit-PASS-20260901.md`)
> **范围**: 2 样本 × 1 HTTP each = 2 cells; ≤12 HTTP total
> **架构师依据**: 646 spike; fujian + guangdong 首选 + 625 fall-through chain (gd /zwgk/ → gd /zwgk/zcfg/ → guizhou /zwgk/)
> **chain_id**: `real_646_m4_9_policy_detail_v3` (末段 `_v3`, ≠ 645 `_v2`)
> **UUID prefix**: e 段 (e0eebc99-e6eebc99) ≠ 645 d 段 (d0eebc99-d6eebc99) ≠ 644 c 段

## 0. 顶层裁定

**REAL_FETCHED** — 适用 2 HTTP, 实测 2 cell。

总抓取: 2 真实政策详情样本 (跨 2 样本位)

## 1. 实体逐项 (真实政策详情样本)

| 序号 | 试点省 | slot | chain_index | title | publication_date | sha256 (前 16) | file_size | source_url |
|---|---|---|---|---|---|---|---|---|
| 1 | fujian | fujian_zwgk_root | n/a | 政务公开 | 2025-4-24 | fceb8c0ac80c5d3c | 682079 | https://www.fujian.gov.cn/zwgk/ |
| 2 | guangdong | guangdong_zwgk_chain | 0 | 政务公开&nbsp;&nbsp;广东省人民政府门户网站 |  | 49eed23efcb2954e | 73836 | https://www.gd.gov.cn/zwgk/ |

## 2. HTTP 抓取日志

| URL | 试点省 | slot | phase | http_code | reason | 抓取时刻 |
|---|---|---|---|---|---|---|
| https://www.fujian.gov.cn/zwgk/ | fujian | fujian_zwgk_root | main | 200 | ok | 2026-09-01T09:46:52.759503+00:00 |
| https://www.gd.gov.cn/zwgk/ | guangdong | guangdong_zwgk_chain | gd_chain_main_0 | 200 | ok | 2026-09-01T09:46:53.376448+00:00 |

## 3. 方法学

≤12 HTTP total (2 cells): curl only; 不爬网; 直接抓 detail page.
沿用 644/645 fetch 模式; fujian + guangdong 首选 + 625 fall-through chain.
guangdong 首选 /zwgk/ 若 404/不可达 → fallback #1 /zwgk/zcfg/ → fallback #2 guizhou /zwgk/.
解析策略:
- 详情页: <title> + DATE_RE
- 真实 SHA256: hashlib.sha256(html) 一次

## 4. 数据源合规

✓ 2 试点省 政府网 (fujian.gov.cn / gd.gov.cn)
✓ 无商业库; ✓ 无用户裁定 URL
✓ ≤12 HTTP total; ✓ 不爬网; ✓ 不写 cegr.* 表

## 5. 红线遵守

- ✓ ≤12 HTTP total (硬性上限)
- ✓ 不爬网 (no follow pagination; no recursion)
- ✓ 不写 cegr.* 表 (read-only on production)
- ✓ 不静默硬编码 GDP 值 (从抓取解析)
- ✓ 脚本幂等 (no time.sleep / no random; sha256 deterministic)
- ✓ 不宣称 Gate / O1 / M2 / M4 / M4.7 / M4.8 / M5 / M6 / M4.9 PASS
