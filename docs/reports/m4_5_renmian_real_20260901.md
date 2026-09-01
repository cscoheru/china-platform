# M4.5 6 试点省任免真实化 spike 抓取报告（2026-09-01，knife 642 M4.5 side）

> **类型**: 642-A.2 真实抓取 (read-only;**不写 cegr.* 表**)
> **前置**: 639 REACHABLE 6 任免源 (黑龙江/福建/河南/广东/贵州/云南)
> **范围**: 6 试点省 × 1 detail each = ≤6 cells; ≤12 HTTP total (6 indices + 6 details)
> **架构师依据**: 642 spike 并行; M4.5 复用 639 6 REACHABLE 路径; spike 不重 probe

## 0. 顶层裁定

**REAL_FETCHED** — 适用 10 HTTP, 实测 4 cell。

总抓取: 4 真实任免样本 (跨 6 试点省)

## 1. 实体逐项 (真实任免样本)

| 序号 | 试点省 | title | publication_date | sha256 (前 16) | file_size | url |
|---|---|---|---|---|---|---|
| 1 | heilongjiang | 黑龙江省人民政府关于王正军等任免职的通知_黑政干 | 2026-08-31 | 26e5379d86e6a5c6 | 21348 | https://www.hlj.gov.cn/hlj/c108378/202608/c00_31971131.shtml |
| 2 | henan | 河南省人民政府关于狄绯等3人职务任免的通知_豫政任 | 2026-08-21 | cd6aff30260779ef | 6336 | https://www.henan.gov.cn/2026/08-21/3401380.html |
| 3 | guangdong | 省人大常委会2026年5月份人事任免&nbsp;&nbsp;广东省人民政府门户网站 | 2026-06-29 | 4349ee0ff814d38a | 58322 | https://www.gd.gov.cn/zwgk/rsxx/content/post_4917420.html |
| 4 | guizhou | 省人民政府关于刘锐等任免职的通知（黔府任〔2026〕44号） | 2026-08-28 | fede03baaeecd8f6 | 72863 | https://www.guizhou.gov.cn/zwgk/zcfg/szfwj/qfr/202608/t20260828_90796146.html |

## 2. HTTP 抓取日志

| URL | 试点省 | phase | http_code | reason | 抓取时刻 |
|---|---|---|---|---|---|
| https://www.hlj.gov.cn/hlj/c108368/zwgk.shtml | heilongjiang | landing | 200 | ok | 2026-09-01T05:47:32.567635+00:00 |
| https://www.hlj.gov.cn/hlj/c108378/202608/c00_31971131.shtml | heilongjiang | detail | 200 | ok | 2026-09-01T05:47:32.852864+00:00 |
| https://www.fujian.gov.cn/zwgk/ | fujian | landing | 200 | ok | 2026-09-01T05:47:35.983839+00:00 |
| https://www.henan.gov.cn/zwgk/ | henan | landing | 200 | ok | 2026-09-01T05:47:36.347289+00:00 |
| https://www.henan.gov.cn/2026/08-21/3401380.html | henan | detail | 200 | ok | 2026-09-01T05:47:36.592420+00:00 |
| https://www.gd.gov.cn/zwgk/ | guangdong | landing | 200 | ok | 2026-09-01T05:47:37.001789+00:00 |
| https://www.gd.gov.cn/zwgk/rsxx/content/post_4917420.html | guangdong | detail | 200 | ok | 2026-09-01T05:47:37.398810+00:00 |
| https://www.guizhou.gov.cn/zwgk/ | guizhou | landing | 200 | ok | 2026-09-01T05:47:37.790027+00:00 |
| https://www.guizhou.gov.cn/zwgk/zcfg/szfwj/qfr/202608/t20260828_90796146.html | guizhou | detail | 200 | ok | 2026-09-01T05:47:39.767974+00:00 |
| https://www.yn.gov.cn/zwgk/ | yunnan | landing | 200 | ok | 2026-09-01T05:47:40.995660+00:00 |

## 3. 方法学

≤12 HTTP total (6 indices + 6 details): curl only; 不爬网。
解析策略:
- 索引页: <a href> + RENMIAN_RE 关键词 (任免职/任免通知/任命/免职)
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
