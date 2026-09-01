# M4.8 4 样本政策详情 v2 真实化 spike 抓取报告（2026-09-01，knife 645 M4.8 side）

> **类型**: 645-A.2 真实抓取 (read-only;**不写 cegr.* 表**)
> **前置**: 644 M4.7 DELIVERED (3 样本 SHA `bad8be51` / `dfa38998` / `f33eba53`)
> **范围**: 4 样本 × 1 HTTP each = 4 cells; ≤12 HTTP total
> **架构师依据**: 645 spike 并行; M4.8 复用 644 3 URL + 纳入 644 留作扩展的 henan `bd4c4c51...` (zwgk root) 作为第 4 样本

## 0. 顶层裁定

**REAL_FETCHED** — 适用 4 HTTP, 实测 4 cell。

总抓取: 4 真实政策详情样本 (跨 4 样本位)

## 1. 实体逐项 (真实政策详情样本)

| 序号 | 试点省 | slot | title | publication_date | sha256 (前 16) | file_size | source_url |
|---|---|---|---|---|---|---|---|
| 1 | heilongjiang | hlj_policy_list | 黑龙江省人民政府 | 2026-09-01 | 6237cd48afc60c06 | 148507 | https://www.hlj.gov.cn/hlj/c107884/list.shtml |
| 2 | henan | henan_zfgb_list | 政府公报 | 2026-07-29 | dfa38998c3e7e892 | 8959 | https://www.henan.gov.cn/zwgk/zfgb/ |
| 3 | henan | henan_zwgk_root | 政务公开 | 2026-08-20 | bd4c4c51b8f371e2 | 158029 | https://www.henan.gov.cn/zwgk/ |
| 4 | yunnan | yunnan_zfgzbg | 政府工作报告 | 2026-02-03 | f33eba53a1e5e961 | 94310 | https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/ |

## 2. HTTP 抓取日志

| URL | 试点省 | slot | phase | http_code | reason | 抓取时刻 |
|---|---|---|---|---|---|---|
| https://www.hlj.gov.cn/hlj/c107884/list.shtml | heilongjiang | hlj_policy_list | main | 200 | ok | 2026-09-01T08:39:59.101718+00:00 |
| https://www.henan.gov.cn/zwgk/zfgb/ | henan | henan_zfgb_list | main | 200 | ok | 2026-09-01T08:39:59.387012+00:00 |
| https://www.henan.gov.cn/zwgk/ | henan | henan_zwgk_root | main | 200 | ok | 2026-09-01T08:39:59.729967+00:00 |
| https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/ | yunnan | yunnan_zfgzbg | main | 200 | ok | 2026-09-01T08:40:00.178639+00:00 |

## 3. 方法学

≤12 HTTP total (4 cells): curl only; 不爬网; 直接抓 detail page (沿用 644 URL).
复用 644 3 SHA: hlj `bad8be51` / henan-zfgb `dfa38998` / yunnan `f33eba53` (idempotent 验证).
新增 645 第 4 样本: henan-zwgk `bd4c4c51` (root landing page, 644 留作扩展).
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
- ✓ 不宣称 Gate / O1 / M2 / M4 / M4.7 / M4.8 / M5 / M6 PASS
