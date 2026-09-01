# M4.2 任免公告 二次探活 probe 报告（2026-09-01，knife 639）

> **类型**: 639-A.1 probe (read-only;不写 cegr.observation)
> **前置**: 638 DELIVERED;docs/58 §3 任免 PARTIAL/BLOCKED 已知 gap
> **范围**: 29 URL (6 中央 + 23 REACHABLE 试点省任免栏目)
> **架构师依据**: 638 PARTIAL 是首页非任免页;639 重打 6 中央 URL (HTTPS / 正确路径 / 任免栏目) + 23 试点省 `/zwgk/` 任免栏目

## 0. 顶层裁定

**MIXED** — 适用 29 cell, 实测 29 cell。

总分布:

- REACHABLE: 6
- PARTIAL: 8
- BLOCKED: 15

中央 vs 试点省分布:

- 中央 (ccdi 2 + npc 2 + 国务院 2 = 6): {'PARTIAL': 4, 'BLOCKED': 2}
- 试点省 (23 REACHABLE 继承自 638): {'BLOCKED': 13, 'PARTIAL': 4, 'REACHABLE': 6}

## 1. 实体逐项

| slug | verdict | http_code | 备注 |
|---|---|---|---|
| 中央纪委要闻 (central-discipline-yaowen) | PARTIAL | 200 | ok |
| 中央纪委审查调查 (central-discipline-shenji) | PARTIAL | 200 | ok |
| 全国人大任免 (npc-renmian) | BLOCKED | 0 | tls_reset |
| 全国人大要闻 (npc-news) | BLOCKED | 0 | tls_reset |
| 国务院政策 (central-zhengce) | PARTIAL | 200 | ok |
| 国务院要闻 (central-yaowen) | PARTIAL | 200 | ok |
| 北京任免 (beijing-renmian) | BLOCKED | 404 | ok |
| 上海任免 (shanghai-renmian) | PARTIAL | 200 | ok |
| 重庆任免 (chongqing-renmian) | PARTIAL | 200 | ok |
| 河北任免 (hebei-renmian) | BLOCKED | 404 | ok |
| 山西任免 (shanxi-renmian) | BLOCKED | 404 | ok |
| 内蒙古任免 (innermongolia-renmian) | BLOCKED | 0 | curl_err:curl: (28) Connection timed out after 15001 milliseconds
 |
| 辽宁任免 (liaoning-renmian) | BLOCKED | 404 | ok |
| 吉林任免 (jilin-renmian) | BLOCKED | 404 | ok |
| 黑龙江任免 (heilongjiang-renmian) | REACHABLE | 200 | ok |
| 江苏任免 (jiangsu-renmian) | BLOCKED | 404 | ok |
| 浙江任免 (zhejiang-renmian) | BLOCKED | 403 | ok |
| 安徽任免 (anhui-renmian) | BLOCKED | 403 | ok |
| 福建任免 (fujian-renmian) | REACHABLE | 200 | ok |
| 河南任免 (henan-renmian) | REACHABLE | 200 | ok |
| 湖南任免 (hunan-renmian) | BLOCKED | 404 | ok |
| 广东任免 (guangdong-renmian) | REACHABLE | 200 | ok |
| 海南任免 (hainan-renmian) | PARTIAL | 200 | ok |
| 四川任免 (sichuan-renmian) | BLOCKED | 403 | ok |
| 贵州任免 (guizhou-renmian) | REACHABLE | 200 | ok |
| 云南任免 (yunnan-renmian) | REACHABLE | 200 | ok |
| 陕西任免 (shaanxi-renmian) | BLOCKED | 404 | ok |
| 宁夏任免 (ningxia-renmian) | PARTIAL | 200 | ok |
| 新疆任免 (xinjiang-renmian) | BLOCKED | 403 | ok |

## 2. 方法学

REACHABLE: HTTP 200 + body 含 `任免|任免名单|appoint|removal|departure` marker。
PARTIAL: HTTP 200 + body 已加载但 marker 未命中（栏目命中任免路径不正确）。
BLOCKED: TLS reset / 403 WAF / 404 / connection error。
二次探活 URL 选择（继承 638 PARTIAL/BLOCKED 已知 gap）:
- ccdi: 638 PARTIAL `https://www.ccdi.gov.cn/` 是首页;639 重打 `/yaowen/` (要闻) + `/specialn/scjcf/` (审查调查,含部分任免)。
- npc: 638 BLOCKED `http://www.npc.gov.cn/` timeout;639 改 HTTPS `/npc/c2/` (任免) + `/npc/` (要闻)。
- 国务院: 638 BLOCKED `https://www.gov.cn/zwgk/zfgbg.htm` 404 (是政府工作报告路径);639 重打 `/zhengce/` (政策) + `/yaowen/` (要闻)。
- 试点省: 继承 638 23 个 `www.*.gov.cn/` REACHABLE;639 加探 `/zwgk/` 任免栏目 (BLOCKED 9 省 天津/山东/湖北/江西/广西/西藏/甘肃/青海 + 国务院 不探)。

## 3. 638 vs 639 对比

- 638 PARTIAL/BLOCKED 3 URL (ccdi 首页 + npc HTTP + 国务院 404) ⇒ 639 重打为 6 URL (ccdi 2 + npc 2 + 国务院 2)。
- 638 23 REACHABLE 试点省 `/` ⇒ 639 加探 `/zwgk/` 任免栏目 23 URL。

## 4. 数据源合规

✓ 全部政府源 (ccdi.gov.cn / npc.gov.cn / www.gov.cn / 23 www.*.gov.cn);✓ 无商业库;✓ 无用户裁定 URL。

## 5. 红线遵守

- ✓ 不写 cegr.observation
- ✓ 不静默硬编码 GDP 值
- ✓ 不爬网（仅探可达性,不抓内容入库）
- ✓ 脚本幂等（无 random / 无 time.sleep）
- ✓ 不宣称 Gate / O1 / M2 / M4 PASS
