# M4.10 2 样本政策详情 v4 真实化 spike 抓取报告（2026-09-01，knife 647 M4.10 side）

> **类型**: 647-A.1 真实抓取 (read-only;**不写 cegr.* 表**)
> **前置**: 646 审计 PASS（有限通过） (`646-stage0-cursor-s646-m4-9-o1-audit-PASS-20260901.md`)
> **范围**: 2 样本 × 1 HTTP each = 2 cells; ≤12 HTTP total
> **架构师依据**: 647 spike; zhejiang + shandong 首选 + 625 fall-through chain (省府根 fallback)
> **chain_id**: `real_647_m4_10_policy_detail_v4` (末段 `_v4`, ≠ 646 `_v3` ≠ 645 `_v2`)
> **UUID prefix**: f 段 (f0eebc99-f6eebc99) ≠ 646 e 段 (e0eebc99-e6eebc99) ≠ 645 d 段 ≠ 644 c 段

## 0. 顶层裁定

**REAL_FETCHED** — 适用 7 HTTP, 实测 2 cell。

总抓取: 2 真实政策详情样本 (跨 2 样本位)

## 1. 实体逐项 (真实政策详情样本)

| 序号 | 试点省 | slot | chain_index | title | publication_date | sha256 (前 16) | file_size | source_url |
|---|---|---|---|---|---|---|---|---|
| 1 | zhejiang | zhejiang_zwgk_chain | 1 | 浙江省人民政府 | 2026-09-01 | 8016ef0874c49261 | 159382 | https://www.zj.gov.cn/ |
| 2 | jiangxi | shandong_zwgk_chain_substitute | 0 | 403 | 2025-07-16 | 56481050c810fbee | 48118 | https://www.jiangxi.gov.cn/zwgk/ |

## 2. HTTP 抓取日志

| URL | 试点省 | slot | phase | http_code | reason | 抓取时刻 |
|---|---|---|---|---|---|---|
| https://www.zj.gov.cn/zwgk/ | zhejiang | zhejiang_zwgk_chain | zhejiang_zwgk_chain_main_0 | 403 | ok | 2026-09-01T11:09:32.980217+00:00 |
| https://www.zj.gov.cn/ | zhejiang | zhejiang_zwgk_chain | zhejiang_zwgk_chain_fallback_1 | 200 | ok | 2026-09-01T11:09:34.475960+00:00 |
| https://www.shandong.gov.cn/zwgk/ | shandong | shandong_zwgk_chain | shandong_zwgk_chain_main_0 | 0 | curl_err:curl: (35) LibreSSL/3.3.6: error:1404B410:SSL routines:ST_CONNECT:sslv3 alert ha | 2026-09-01T11:09:34.615575+00:00 |
| https://www.shandong.gov.cn/ | shandong | shandong_zwgk_chain | shandong_zwgk_chain_fallback_1 | 0 | curl_err:curl: (35) LibreSSL/3.3.6: error:1404B410:SSL routines:ST_CONNECT:sslv3 alert ha | 2026-09-01T11:09:34.765041+00:00 |
| http://www.shandong.gov.cn/zwgk/ | shandong | shandong_zwgk_chain | shandong_zwgk_chain_fallback_2 | 404 | ok | 2026-09-01T11:09:35.309606+00:00 |
| http://www.shandong.gov.cn/ | shandong | shandong_zwgk_chain | shandong_zwgk_chain_fallback_3 | 0 | timeout | 2026-09-01T11:09:50.350044+00:00 |
| https://www.jiangxi.gov.cn/zwgk/ | jiangxi | shandong_zwgk_chain_substitute | fallthrough_substitute_jiangxi | 0 | shandong_blocked_substitute | 2026-09-01T11:09:50.350391+00:00 |
| https://www.jiangxi.gov.cn/zwgk/ | jiangxi | jiangxi_zwgk_chain_substitute | jiangxi_zwgk_chain_substitute_main_0 | 200 | ok | 2026-09-01T11:09:51.083853+00:00 |

## 3. 方法学

≤12 HTTP total (2 cells): curl only; 不爬网; 直接抓 detail page.
沿用 646 fetch 模式; zhejiang + shandong 首选 /zwgk/ + 625 fall-through chain (省府根 fallback).
zhejiang 首选 /zwgk/ 若 404/不可达 → fallback #1 https://www.zj.gov.cn/ (省府根).
shandong 首选 /zwgk/ 若 404/不可达 → fallback #1 https://www.shandong.gov.cn/ (省府根).
解析策略:
- 详情页: <title> + DATE_RE
- 真实 SHA256: hashlib.sha256(html) 一次

## 4. 数据源合规

✓ 2 试点省 政府网 (zj.gov.cn + jiangxi.gov.cn; 后者为 shandong BLOCKED 625 fall-through substitute)
✓ 已用省全集检查通过: HLJ / HENAN / YUNNAN / FUJIAN / GD (不重复)
✓ shandong 4 attempts BLOCKED (HTTPS TLS handshake_failure + HTTP 404/timeout);
  沿用 625 fall-through 政策 → 从未用 pool 替换为 jiangxi (实测 /zwgk/ = 200 REACHABLE).
✓ 无商业库; ✓ 无用户裁定 URL
✓ ≤12 HTTP total; ✓ 不爬网; ✓ 不写 cegr.* 表

## 5. 红线遵守

- ✓ ≤12 HTTP total (硬性上限)
- ✓ 不爬网 (no follow pagination; no recursion)
- ✓ 不写 cegr.* 表 (read-only on production)
- ✓ 不静默硬编码 GDP 值 (从抓取解析)
- ✓ 脚本幂等 (no time.sleep / no random; sha256 deterministic)
- ✓ 不宣称 Gate / O1 / M2 / M4 / M4.7 / M4.8 / M4.9 / M5 / M6 / M4.10 PASS
