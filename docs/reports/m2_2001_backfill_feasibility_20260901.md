# M2-f — 2001 起回补可行性 probe 报告（knife 636）

> Generated: 2026-09-01T02:42:02.162605+00:00 ·  top verdict: **回补 2001 起 → 不可在本机直接 ingest**

## 1. 探针矩阵

- 实体: 32 (1 国家 + 31 省)
- 年份: 24 (2001–2024)
- 源类: 3 (NBS data.stats.gov.cn JSON API / 各省 tjj.* 历年公报索引 / 全国统计年鉴镜像)
- Cell 总数: **2309** (32 × 24 × 3)
- 实际 HTTP 探针: **184** cells (NBS 24 国家年 + tjj 31 省 × 5 样本年 + 年鉴 5 镜像)
- 推得 cell (extrapolated): **2125**

## 2. Verdicts 计数

| verdict | 全部 cell |
|---|---|
| REACHABLE | 0 |
| PARTIAL | 770 |
| BLOCKED | 771 |
| NOT_APPLICABLE | 768 |
| NOT_PROBED | 0 |

**Top-level verdict: REACHABLE 0 / PARTIAL 770 / BLOCKED 771 / NOT_APPLICABLE 768**
（适用 cell 1541：BLOCKED 771 + PARTIAL 770；REACHABLE 0；无任何 entity×year×GDP 单元可达）

## 3. 按源拆分

| source | REACHABLE | PARTIAL | BLOCKED | NOT_APPLICABLE |
|---|---|---|---|---|
| NBS_API | 0 | 0 | 24 | 744 |
| PROVINCE_TJJ | 0 | 0 | 744 | 24 |
| YEARBOOK_MIRROR | 0 | 770 | 3 | 0 |

## 4. 实测样本 cells (有 HTTP 探针)

| entity | year | source | http | verdict | reason |
|---|---|---|---|---|---|
| 国家 | 2001 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2002 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2003 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2004 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2005 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2006 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2007 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2008 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2009 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2010 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2011 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2012 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2013 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2014 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2015 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2016 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2017 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2018 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2019 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2020 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2021 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2022 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2023 | NBS_API | 403 | BLOCKED | ok |
| 国家 | 2024 | NBS_API | 403 | BLOCKED | ok |
| 上海市 | 2001 | PROVINCE_TJJ | 200 | BLOCKED | ok |
| 上海市 | 2006 | PROVINCE_TJJ | 200 | BLOCKED | ok |
| 上海市 | 2011 | PROVINCE_TJJ | 200 | BLOCKED | ok |
| 上海市 | 2016 | PROVINCE_TJJ | 200 | BLOCKED | ok |
| 上海市 | 2024 | PROVINCE_TJJ | 200 | BLOCKED | ok |
| 云南省 | 2001 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 云南省 | 2006 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 云南省 | 2011 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 云南省 | 2016 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 云南省 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 内蒙古自治区 | 2001 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 内蒙古自治区 | 2006 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL  |
| 内蒙古自治区 | 2011 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL  |
| 内蒙古自治区 | 2016 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL  |
| 内蒙古自治区 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 北京市 | 2001 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 北京市 | 2006 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 北京市 | 2011 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 北京市 | 2016 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 北京市 | 2024 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 吉林省 | 2001 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 吉林省 | 2006 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 吉林省 | 2011 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 吉林省 | 2016 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 吉林省 | 2024 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 四川省 | 2001 | PROVINCE_TJJ | 403 | BLOCKED | ok |
| 四川省 | 2006 | PROVINCE_TJJ | 403 | BLOCKED | ok |
| 四川省 | 2011 | PROVINCE_TJJ | 403 | BLOCKED | ok |
| 四川省 | 2016 | PROVINCE_TJJ | 403 | BLOCKED | ok |
| 四川省 | 2024 | PROVINCE_TJJ | 403 | BLOCKED | ok |
| 天津市 | 2001 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 天津市 | 2006 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 天津市 | 2011 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 天津市 | 2016 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 天津市 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 宁夏回族自治区 | 2001 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 宁夏回族自治区 | 2006 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 宁夏回族自治区 | 2011 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 宁夏回族自治区 | 2016 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 宁夏回族自治区 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL  |
| 安徽省 | 2001 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 安徽省 | 2006 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 安徽省 | 2011 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 安徽省 | 2016 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 安徽省 | 2024 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 山东省 | 2001 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (60) SSL: no alternative certificate subject  |
| 山东省 | 2006 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (60) SSL: no alternative certificate subject  |
| 山东省 | 2011 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (60) SSL: no alternative certificate subject  |
| 山东省 | 2016 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (60) SSL: no alternative certificate subject  |
| 山东省 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (60) SSL: no alternative certificate subject  |
| 山西省 | 2001 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 山西省 | 2006 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 山西省 | 2011 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 山西省 | 2016 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 山西省 | 2024 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 广东省 | 2001 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL  |
| 广东省 | 2006 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 广东省 | 2011 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL  |
| 广东省 | 2016 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 广东省 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 广西壮族自治区 | 2001 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL/3.3.6: error:1404B458:SSL routi |
| 广西壮族自治区 | 2006 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL/3.3.6: error:1404B458:SSL routi |
| 广西壮族自治区 | 2011 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL/3.3.6: error:1404B458:SSL routi |
| 广西壮族自治区 | 2016 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL/3.3.6: error:1404B458:SSL routi |
| 广西壮族自治区 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL/3.3.6: error:1404B458:SSL routi |
| 新疆维吾尔自治区 | 2001 | PROVINCE_TJJ | 403 | BLOCKED | ok |
| 新疆维吾尔自治区 | 2006 | PROVINCE_TJJ | 403 | BLOCKED | ok |
| 新疆维吾尔自治区 | 2011 | PROVINCE_TJJ | 403 | BLOCKED | ok |
| 新疆维吾尔自治区 | 2016 | PROVINCE_TJJ | 403 | BLOCKED | ok |
| 新疆维吾尔自治区 | 2024 | PROVINCE_TJJ | 403 | BLOCKED | ok |
| 江苏省 | 2001 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 江苏省 | 2006 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 江苏省 | 2011 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 江苏省 | 2016 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 江苏省 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 江西省 | 2001 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 江西省 | 2006 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 江西省 | 2011 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL  |
| 江西省 | 2016 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 江西省 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 河北省 | 2001 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 河北省 | 2006 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 河北省 | 2011 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 河北省 | 2016 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 河北省 | 2024 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 河南省 | 2001 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 河南省 | 2006 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 河南省 | 2011 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 河南省 | 2016 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 河南省 | 2024 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 浙江省 | 2001 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 浙江省 | 2006 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 浙江省 | 2011 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 浙江省 | 2016 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 浙江省 | 2024 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 海南省 | 2001 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 海南省 | 2006 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 海南省 | 2011 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL  |
| 海南省 | 2016 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 海南省 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 湖北省 | 2001 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 湖北省 | 2006 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 湖北省 | 2011 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 湖北省 | 2016 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 湖北省 | 2024 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 湖南省 | 2001 | PROVINCE_TJJ | 403 | BLOCKED | ok |
| 湖南省 | 2006 | PROVINCE_TJJ | 403 | BLOCKED | ok |
| 湖南省 | 2011 | PROVINCE_TJJ | 403 | BLOCKED | ok |
| 湖南省 | 2016 | PROVINCE_TJJ | 403 | BLOCKED | ok |
| 湖南省 | 2024 | PROVINCE_TJJ | 403 | BLOCKED | ok |
| 甘肃省 | 2001 | PROVINCE_TJJ | 412 | BLOCKED | ok |
| 甘肃省 | 2006 | PROVINCE_TJJ | 412 | BLOCKED | ok |
| 甘肃省 | 2011 | PROVINCE_TJJ | 412 | BLOCKED | ok |
| 甘肃省 | 2016 | PROVINCE_TJJ | 412 | BLOCKED | ok |
| 甘肃省 | 2024 | PROVINCE_TJJ | 412 | BLOCKED | ok |
| 福建省 | 2001 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 福建省 | 2006 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 福建省 | 2011 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 福建省 | 2016 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 福建省 | 2024 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 西藏自治区 | 2001 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 西藏自治区 | 2006 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 西藏自治区 | 2011 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL  |
| 西藏自治区 | 2016 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 西藏自治区 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL  |
| 贵州省 | 2001 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 贵州省 | 2006 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL  |
| 贵州省 | 2011 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 贵州省 | 2016 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 贵州省 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 辽宁省 | 2001 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 辽宁省 | 2006 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 辽宁省 | 2011 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 辽宁省 | 2016 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 辽宁省 | 2024 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 重庆市 | 2001 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 重庆市 | 2006 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 重庆市 | 2011 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 重庆市 | 2016 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 重庆市 | 2024 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 陕西省 | 2001 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 陕西省 | 2006 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 陕西省 | 2011 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 陕西省 | 2016 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 陕西省 | 2024 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 青海省 | 2001 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL/3.3.6: error:1404B458:SSL routi |
| 青海省 | 2006 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL/3.3.6: error:1404B458:SSL routi |
| 青海省 | 2011 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL/3.3.6: error:1404B458:SSL routi |
| 青海省 | 2016 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL/3.3.6: error:1404B458:SSL routi |
| 青海省 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | curl_err:curl: (35) LibreSSL/3.3.6: error:1404B458:SSL routi |
| 黑龙江省 | 2001 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 黑龙江省 | 2006 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 黑龙江省 | 2011 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 黑龙江省 | 2016 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| 黑龙江省 | 2024 | PROVINCE_TJJ | 404 | BLOCKED | ok |
| ALL | any | YEARBOOK_MIRROR | 200 | PARTIAL | ok |
| ALL | any | YEARBOOK_MIRROR | 200 | PARTIAL | ok |
| ALL | any | YEARBOOK_MIRROR | 404 | BLOCKED | ok |
| ALL | any | YEARBOOK_MIRROR | 0 | BLOCKED | tls_reset |
| ALL | any | YEARBOOK_MIRROR | 404 | BLOCKED | ok |

## 5. 方法论与推得依据

- **NBS_API**: Probe 国家×24 years (dbcode=hgnd, value A0201=地区生产总值)
- **PROVINCE_TJJ**: Probe 31 provinces × 5 sample years ([2001, 2006, 2011, 2016, 2024]); non-sample years extrapolated from same province's sample verdict (WAF block is IP-level, stable across years)
- **YEARBOOK_MIRROR**: Probe 5 candidate mirror URLs; verdict extrapolated to all 768 cells (catalog-only pages cannot provide entity×year×GDP)

## 6. 结论

**实测关键事实（knob 636 探针结果）：**

- **NBS data.stats.gov.cn JSON API** —— 0/24 cell REACHABLE
  国家×24 年 (2001–2024) 全 WAF 403 阻断 (eventID 网防G01)
  原因：本机 IP 125.93.9.191 被 .gov.cn WAF IP-level 阻断 (knife 635 §1.C 已实测)
- **各省 tjj.*** —— 744 BLOCKED cells (extrapolated from 31 省 × 5 样本年 sample)
  原因：HTTPS TLS reset / 404 / directory-only listing (knife 635 §1.C 全 UA rotation 失败)
- **全国统计年鉴镜像** —— 770 PARTIAL + 3 BLOCKED cells (catalog only)
  catalog 可达但缺 entity×year×GDP 单元；真实 GDP 值需 deep-link 跳到具体年鉴页

**总结论：本机无法在不绕过 WAF 的前提下回补 2001-2024 年国家/省 GDP。**

**可行性结论 (knob 636 §1 收口)：**

1. **M2.4 (回补 2001 起) 仅做可行性 probe 完成；不入库** — 适用 cell 1541 实测 **REACHABLE 0 / PARTIAL 770 / BLOCKED 771**；真入库需要:
   - 用户提供 NBS data.stats.gov.cn 直连镜像 (本机 IP 被 WAF 阻断)
   - 或用户提供 31 省 tjj.* 政府源 PDF/HTML (用户浏览器绕过本机 IP-level WAF)
   - 或用户重审 U4 (购买商业年鉴库授权)
2. **不宣布 Gate / O1 / M2 PASS**
3. **probe ≠ ingest**：本脚本只读，不写 cegr.observation
4. **方法局限**：tjj.* 仅 5/24 年实测；其余 19 年外推（WAF IP-level 阻断跨年稳定，结论可信）

— End probe report —
