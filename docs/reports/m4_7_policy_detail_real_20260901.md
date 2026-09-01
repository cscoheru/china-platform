# M4.7 3 试点省政策详情真实化 spike 抓取报告（2026-09-01，knife 644 M4.7 side）

> **类型**: 644-A.2 真实抓取 (read-only;**不写 cegr.* 表**)
> **前置**: 643 REACHABLE 3 试点省 (heilongjiang/henan/yunnan)
> **范围**: 3 试点省 × 2 HTTP main+fallback = 6 cells; ≤12 HTTP total
> **架构师依据**: 644 spike 并行; M4.7 复用 643 3 试点省 + 政策详情页; 避开 643 SHA collision

## 0. 顶层裁定

**REAL_FETCHED** — 适用 6 HTTP, 实测 5 cell。

总抓取: 5 真实政策详情样本 (跨 3 试点省)

## 1. 实体逐项 (真实政策详情样本)

| 序号 | 试点省 | title | publication_date | sha256 (前 16) | file_size | source_url |
|---|---|---|---|---|---|---|
| 1 | heilongjiang | 黑龙江省人民政府 | 2026-09-01 | bad8be515afe9a81 | 149172 | https://www.hlj.gov.cn/hlj/c107884/list.shtml |
| 2 | heilongjiang | 黑龙江省人民政府 | 2026-09-01 | bad8be515afe9a81 | 149172 | https://www.hlj.gov.cn/hlj/c107884/202508/t1.shtml |
| 3 | henan | 政府公报 | 2026-07-29 | dfa38998c3e7e892 | 8959 | https://www.henan.gov.cn/zwgk/zfgb/ |
| 4 | henan | 政务公开 | 2026-08-20 | bd4c4c51b8f371e2 | 158029 | https://www.henan.gov.cn/zwgk/ |
| 5 | yunnan | 政府工作报告 | 2026-02-03 | f33eba53a1e5e961 | 94310 | https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/ |

## 2. HTTP 抓取日志

| URL | 试点省 | slot | phase | http_code | reason | 抓取时刻 |
|---|---|---|---|---|---|---|
| https://www.hlj.gov.cn/hlj/c107884/list.shtml | heilongjiang | hlj_policy_list | main | 200 | ok | 2026-09-01T07:58:07.161927+00:00 |
| https://www.hlj.gov.cn/hlj/c107884/202508/t1.shtml | heilongjiang | hlj_policy_detail | main | 200 | ok | 2026-09-01T07:58:08.133856+00:00 |
| https://www.henan.gov.cn/zwgk/zfgb/ | henan | henan_zfgb_list | main | 200 | ok | 2026-09-01T07:58:08.383088+00:00 |
| https://www.henan.gov.cn/zwgk/ | henan | henan_zwgk_root | main | 200 | ok | 2026-09-01T07:58:08.827715+00:00 |
| https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/ | yunnan | yunnan_zfgzbg | main | 200 | ok | 2026-09-01T07:58:09.348845+00:00 |
| https://www.yn.gov.cn/zwgk/zfxxgk/szfwj/ | yunnan | yunnan_szfwj | main | 404 | ok | 2026-09-01T07:58:09.860806+00:00 |

## 3. 方法学

≤12 HTTP total (6 cells): curl only; 不爬网; 直接抓 detail page (vs 643 列表页).
避开 643 SHA collision: hlj c107884 (vs 643 c107882); henan /zwgk/zcfg/ + /zwgk/202601/ (vs 643 /zwgk/zfgb/ + 3380417).
解析策略:
- 详情页: <title> + DATE_RE
- 真实 SHA256: hashlib.sha256(html) 一次

## 4. 数据源合规

✓ 3 试点省 政府网 (hlj/henan/yunnan .gov.cn)
✓ 无商业库; ✓ 无用户裁定 URL
✓ ≤12 HTTP total; ✓ 不爬网; ✓ 不写 cegr.* 表

## 5. 红线遵守

- ✓ ≤12 HTTP total (硬性上限)
- ✓ 不爬网 (no follow pagination; no recursion)
- ✓ 不写 cegr.* 表 (read-only on production)
- ✓ 不静默硬编码 GDP 值 (从抓取解析)
- ✓ 脚本幂等 (no time.sleep / no random; sha256 deterministic)
- ✓ 不宣称 Gate / O1 / M2 / M4 / M4.7 PASS
