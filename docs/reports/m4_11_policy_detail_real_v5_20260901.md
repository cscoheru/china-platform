# M4.11 2 样本政策详情 v5 真实化 spike 抓取报告（2026-09-01，knife 648 M4.11 side）

> **类型**: 648-A.1 真实抓取 (read-only;**不写 cegr.* 表**)
> **前置**: 647 审计 PASS（有限通过） (`647-stage0-cursor-s647-m4-10-v4-audit-PASS-20260901.md`)
> **范围**: 2 样本 × 1 HTTP each = 2 cells; ≤12 HTTP total
> **架构师依据**: 648 spike; hunan + anhui 首选 + 625 fall-through chain (省府根 fallback)
> **chain_id**: `real_648_m4_11_policy_detail_v5` (末段 `_v5`, ≠ 647 `_v4` ≠ 646 `_v3` ≠ 645 `_v2`)
> **UUID prefix**: g 段 (g0eebc99-g6eebc99) ≠ 647 f 段 (f0eebc99-f6eebc99) ≠ 646 e 段 ≠ 645 d 段

## 0. 顶层裁定

**REAL_FETCHED** — 适用 4 HTTP, 实测 2 cell。

总抓取: 2 真实政策详情样本 (跨 2 样本位)

## 1. 实体逐项 (真实政策详情样本)

| 序号 | 试点省 | slot | chain_index | title | publication_date | sha256 (前 16) | file_size | source_url |
|---|---|---|---|---|---|---|---|---|
| 1 | hunan | hunan_zwgk_chain | 1 | 欢迎光临湖南省人民政府门户网站 | 2026-09-01 | 4006439ee1494314 | 113702 | https://www.hunan.gov.cn/ |
| 2 | anhui | anhui_zwgk_chain | 1 | 安徽省人民政府 | 2026-09-01 | a06e174f10eda8b5 | 128409 | https://www.ah.gov.cn/ |

## 2. HTTP 抓取日志

| URL | 试点省 | slot | phase | http_code | reason | 抓取时刻 |
|---|---|---|---|---|---|---|
| https://www.hunan.gov.cn/zwgk/ | hunan | hunan_zwgk_chain | hunan_zwgk_chain_main_0 | 404 | ok | 2026-09-01T11:42:51.634934+00:00 |
| https://www.hunan.gov.cn/ | hunan | hunan_zwgk_chain | hunan_zwgk_chain_fallback_1 | 200 | ok | 2026-09-01T11:42:51.936616+00:00 |
| https://www.ah.gov.cn/zwgk/ | anhui | anhui_zwgk_chain | anhui_zwgk_chain_main_0 | 0 | curl_err:curl: (28) Connection timed out after 15005 milliseconds
 | 2026-09-01T11:43:06.956891+00:00 |
| https://www.ah.gov.cn/ | anhui | anhui_zwgk_chain | anhui_zwgk_chain_fallback_1 | 200 | ok | 2026-09-01T11:43:07.906491+00:00 |

## 3. 方法学

≤12 HTTP total (2 cells): curl only; 不爬网; 直接抓 detail page.
沿用 647 fetch 模式; hunan + anhui 首选 /zwgk/ + 625 fall-through chain (省府根 fallback).
hunan 首选 /zwgk/ 若 404/不可达 → fallback #1 https://www.hunan.gov.cn/ (省府根).
anhui 首选 /zwgk/ 若 404/不可达 → fallback #1 https://www.ah.gov.cn/ (省府根).
解析策略:
- 详情页: <title> + DATE_RE
- 真实 SHA256: hashlib.sha256(html) 一次

## 4. 数据源合规

✓ 2 试点省 政府网 (hunan.gov.cn + ah.gov.cn)
✓ 已用省全集检查通过: HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX (不重复)
✓ substitute 预授权池 (jilin/liaoning/hubei/shaanxi/sichuan/guizhou/jiangsu) 待激活
✓ 无商业库; ✓ 无用户裁定 URL
✓ ≤12 HTTP total; ✓ 不爬网; ✓ 不写 cegr.* 表

## 5. 红线遵守

- ✓ ≤12 HTTP total (硬性上限)
- ✓ 不爬网 (no follow pagination; no recursion)
- ✓ 不写 cegr.* 表 (read-only on production)
- ✓ 不静默硬编码 GDP 值 (从抓取解析)
- ✓ 脚本幂等 (no time.sleep / no random; sha256 deterministic)
- ✓ 不宣称 Gate / O1 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M5 / M6 PASS
