# M4.6 6 试点省政府工作报告真实化 spike 抓取报告（2026-09-01，knife 643 M4.6 side）

> **类型**: 643-A.2 真实抓取 (read-only;**不写 cegr.* 表**)
> **前置**: 638 REACHABLE 23/32 列表 (zfgb 路径) + 642 6 试点省列表 (heilongjiang/fujian/henan/guangdong/guizhou/yunnan)
> **范围**: 6 试点省 × 1 detail each = ≤6 cells; ≤12 HTTP total (6 indices + 6 details)
> **架构师依据**: 643 spike 并行; M4.6 复用 638 政府报告 zfgb 路径 + 642 6 试点省

## 0. 顶层裁定

**REAL_FETCHED** — 适用 9 HTTP, 实测 3 cell。

总抓取: 3 真实政府工作报告样本 (跨 6 试点省)

## 1. 实体逐项 (真实政府工作报告样本)

| 序号 | 试点省 | title | publication_date | sha256 (前 16) | file_size | url |
|---|---|---|---|---|---|---|
| 1 | heilongjiang | 省政府公报 | 2026-02-13 | e68099df39fa09ba | 819 | https://www.hlj.gov.cn/hlj/c107882/redirect_firstChannel.shtml |
| 2 | henan | 河南省人民政府公报2026年第14号（总第554号）_公报首页 | 2026-07-29 | 631094910323dc63 | 13457 | https://www.henan.gov.cn/2026/07-29/3380417.html |
| 3 | yunnan | 云南省人民政府公报 | 2026-08-15 | 93fe23b32d083581 | 79137 | https://www.yn.gov.cn/zwgk/zfgb/ |

## 2. HTTP 抓取日志

| URL | 试点省 | phase | http_code | reason | 抓取时刻 |
|---|---|---|---|---|---|
| https://www.hlj.gov.cn/zwgk/zfgb/ | heilongjiang | landing | 200 | ok | 2026-09-01T06:38:49.666178+00:00 |
| https://www.hlj.gov.cn/hlj/c107882/redirect_firstChannel.shtml | heilongjiang | detail | 200 | ok | 2026-09-01T06:38:49.916064+00:00 |
| https://www.fujian.gov.cn/zwgk/zfgb/ | fujian | landing | 404 | ok | 2026-09-01T06:38:50.196032+00:00 |
| https://www.henan.gov.cn/zwgk/zfgb/ | henan | landing | 200 | ok | 2026-09-01T06:38:50.651709+00:00 |
| https://www.henan.gov.cn/2026/07-29/3380417.html | henan | detail | 200 | ok | 2026-09-01T06:38:50.890633+00:00 |
| https://www.gd.gov.cn/zwgk/zfgb/ | guangdong | landing | 404 | ok | 2026-09-01T06:38:51.047000+00:00 |
| https://www.guizhou.gov.cn/zwgk/zcfg/szfwj/ | guizhou | landing | 200 | ok | 2026-09-01T06:38:51.227449+00:00 |
| https://www.yn.gov.cn/zwgk/zfgb/ | yunnan | landing | 200 | ok | 2026-09-01T06:38:52.465606+00:00 |
| https://www.yn.gov.cn/zwgk/zfgb/ | yunnan | detail | 200 | ok | 2026-09-01T06:38:52.827259+00:00 |

## 3. 方法学

≤12 HTTP total (6 indices + 6 details): curl only; 不爬网。
解析策略 (vs 642 任免不同):
- 索引页: <a href> + GOV_REPORT_RE 关键词 (政府工作|工作报告|政府报告|年度工作|政府公报|规划计划|五年规划)
- 详情页: <title> + DATE_RE
- 真实 SHA256: hashlib.sha256(html) 一次

## 4. 数据源合规

✓ 6 试点省 政府网 (hlj/fujian/henan/gd/guizhou/yn .gov.cn)
✓ 无商业库; ✓ 无用户裁定 URL
✓ ≤12 HTTP total; ✓ 不爬网; ✓ 不写 cegr.* 表

## 5. 红线遵守

- ✓ ≤12 HTTP total (硬性上限)
- ✓ 不爬网 (no follow pagination; no recursion)
- ✓ 不写 cegr.* 表 (read-only on production)
- ✓ 不静默硬编码 GDP 值 (从抓取解析)
- ✓ 脚本幂等 (no time.sleep / no random; sha256 deterministic)
- ✓ 不宣称 Gate / O1 / M2 / M4 PASS
