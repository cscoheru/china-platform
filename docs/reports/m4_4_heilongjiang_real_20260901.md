# M4.4 黑龙江政策真实化 spike 抓取报告（2026-09-01，knife 641）

> **类型**: 641-A.1 真实抓取 (read-only;**不写 cegr.* 表**)
> **前置**: 640 DELIVERED;docs/60 §2.1 关键反发现 (REACHABLE 2 = 黑龙江 zfwj/zfgb)
> **范围**: 1 索引 URL + ≤3 详情页 (≤4 HTTP total)
> **架构师依据**: 641 单 REACHABLE 试点省收口;沿用 638/639/640 WAF 假设

## 0. 顶层裁定

**REAL_FETCHED** — 适用 4 HTTP, 实测 3 cell。

总抓取: 3 真实政策样本

- 索引 URL: `https://www.hlj.gov.cn/hlj/c108368/zwgk.shtml`
- HTTP 计数: 4 (≤ 4 红线)
- 抓取状态: REAL_FETCHED

## 1. 实体逐项 (真实政策样本)

| 序号 | title | publication_date | publisher | doc_type | sha256 (前 16) | file_size | url |
|---|---|---|---|---|---|---|---|
| 1 | 黑龙江省人民政府关于王正军等任免职的通知_黑政干 | 2026-08-31 | 黑龙江省人民政府 | 通知 | 26e5379d86e6a5c6 | 21348 | https://www.hlj.gov.cn/hlj/c108378/202608/c00_31971131.shtml |
| 2 | 黑龙江省人民政府关于李水泉等任免职的通知_黑政干 | 2026-08-20 | 黑龙江省人民政府 | 通知 | 844e36dce66f0f0c | 19920 | https://www.hlj.gov.cn/hlj/c108378/202608/c00_31968515.shtml |
| 3 | 黑龙江省人民政府关于董妍等任免职的通知_黑政干 | 2026-07-31 | 黑龙江省人民政府 | 通知 | 95b32a28e854fc46 | 20558 | https://www.hlj.gov.cn/hlj/c108378/202607/c00_31963474.shtml |

## 2. HTTP 抓取日志

| URL | http_code | reason | 抓取时刻 |
|---|---|---|---|
| https://www.hlj.gov.cn/hlj/c108368/zwgk.shtml | 200 | ok | 2026-09-01T05:27:24.852491+00:00 |
| https://www.hlj.gov.cn/hlj/c108378/202608/c00_31971131.shtml | 200 | ok | 2026-09-01T05:27:25.075938+00:00 |
| https://www.hlj.gov.cn/hlj/c108378/202608/c00_31968515.shtml | 200 | ok | 2026-09-01T05:27:25.641996+00:00 |
| https://www.hlj.gov.cn/hlj/c108378/202607/c00_31963474.shtml | 200 | ok | 2026-09-01T05:27:25.932796+00:00 |

## 3. 方法学

≤4 HTTP total (1 索引 + ≤3 详情): curl only; 不爬网。
解析策略:
- 索引页: <a href> 标签 + 限定 hlj.gov.cn + /zwgk/zfwj/ 子路径 + anchor 含 DOCTYPE_RE 关键词
- 详情页: <title> + meta PubDate + DOCTYPE_RE 关键词 (title 推断)
- 真实 SHA256: hashlib.sha256(html) 一次
- 真实 file_size: len(html) bytes

## 4. 数据源合规

✓ www.hlj.gov.cn 政府源 (中央/省/市/县 政策承载路径)
✓ 无商业库;✓ 无用户裁定 URL
✓ ≤4 HTTP total; ✓ 不爬网; ✓ 不写 cegr.* 表

## 5. 红线遵守

- ✓ ≤4 HTTP total (1 index + ≤3 details)
- ✓ 不爬网 (no follow pagination; no recursion)
- ✓ 不写 cegr.* 表 (read-only on production)
- ✓ 不静默硬编码 GDP 值 (从抓取解析)
- ✓ 脚本幂等 (no time.sleep / no random; sha256 deterministic)
- ✓ 不宣称 Gate / O1 / M2 / M4 PASS
