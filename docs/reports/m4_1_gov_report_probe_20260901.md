# M4.1 政府工作报告 可达性 probe 报告（2026-09-01，knife 638）

> **类型**: 638-A.1 probe (read-only;不写 cegr.observation)
> **前置**: 637 DELIVERED (路径 C 接受);docs/57 §6 下一步
> **环境**: 本机 IP `125.93.9.191`（继承 636 WAF IP-level 阻断上下文）

## 0. 顶层裁定

**MIXED** — 适用 32 cell, 实测 32 cell。

总分布:

- REACHABLE: 23
- PARTIAL: 0
- BLOCKED: 9

## 1. 实体逐项

| slug | verdict | 备注 |
|---|---|---|
| 国务院 (central) | BLOCKED | HTTP 404 |
| 北京市 (beijing) | REACHABLE | HTTP 200 |
| 天津市 (tianjin) | BLOCKED | tls_reset |
| 上海市 (shanghai) | REACHABLE | HTTP 200 |
| 重庆市 (chongqing) | REACHABLE | HTTP 200 |
| 河北省 (hebei) | REACHABLE | HTTP 200 |
| 山西省 (shanxi) | REACHABLE | HTTP 200 |
| 内蒙古自治区 (innermongolia) | REACHABLE | HTTP 200 |
| 辽宁省 (liaoning) | REACHABLE | HTTP 200 |
| 吉林省 (jilin) | REACHABLE | HTTP 200 |
| 黑龙江省 (heilongjiang) | REACHABLE | HTTP 200 |
| 江苏省 (jiangsu) | REACHABLE | HTTP 200 |
| 浙江省 (zhejiang) | REACHABLE | HTTP 200 |
| 安徽省 (anhui) | REACHABLE | HTTP 200 |
| 福建省 (fujian) | REACHABLE | HTTP 200 |
| 江西省 (jiangxi) | BLOCKED | curl_err:curl: (60) SSL: no alternative certificate subject name matches target host name |
| 山东省 (shandong) | BLOCKED | curl_err:curl: (35) LibreSSL/3.3.6: error:1404B410:SSL routines:ST_CONNECT:sslv3 alert ha |
| 河南省 (henan) | REACHABLE | HTTP 200 |
| 湖北省 (hubei) | BLOCKED | HTTP 412 |
| 湖南省 (hunan) | REACHABLE | HTTP 200 |
| 广东省 (guangdong) | REACHABLE | HTTP 200 |
| 广西壮族自治区 (guangxi) | BLOCKED | curl_err:curl: (35) LibreSSL/3.3.6: error:1404B458:SSL routines:ST_CONNECT:tlsv1 unrecogn |
| 海南省 (hainan) | REACHABLE | HTTP 200 |
| 四川省 (sichuan) | REACHABLE | HTTP 200 |
| 贵州省 (guizhou) | REACHABLE | HTTP 200 |
| 云南省 (yunnan) | REACHABLE | HTTP 200 |
| 西藏自治区 (tibet) | BLOCKED | curl_err:curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL in connection to www.xizang.g |
| 陕西省 (shaanxi) | REACHABLE | HTTP 200 |
| 甘肃省 (gansu) | BLOCKED | HTTP 412 |
| 青海省 (qinghai) | BLOCKED | tls_reset |
| 宁夏回族自治区 (ningxia) | REACHABLE | HTTP 200 |
| 新疆维族自治区 (xinjiang) | REACHABLE | HTTP 200 |

## 2. 方法学

REACHABLE: HTTP 200 + body 含 `政府工作报告|人民政府|工作报告` marker。
PARTIAL: HTTP 200 + body 已加载但 marker 未命中（catalog-only landing）。
BLOCKED: TLS reset / 403 WAF / 404 / connection error。
Targets: 1 国务院 (www.gov.cn/zwgk/zfgbg.htm) + 31 省人民政府首页。
继承 636 §2 WAF IP-level 阻断上下文（本机 IP 125.93.9.191）。

## 3. 数据源合规

✓ 全部 gov.cn 政府源；✓ 无商业库；✓ 无用户裁定 URL。

## 4. 红线遵守

- ✓ 不写 cegr.observation
- ✓ 不静默硬编码 GDP 值
- ✓ 不爬网（仅探可达性，不抓内容入库）
- ✓ 脚本幂等（无 random / 无 time.sleep）
- ✓ 不宣称 Gate / O1 / M2 / M4 PASS
