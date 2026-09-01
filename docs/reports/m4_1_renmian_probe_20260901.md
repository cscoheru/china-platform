# M4.1 任免公告 可达性 probe 报告（2026-09-01，knife 638）

> **类型**: 638-A.2 probe (read-only;不写 cegr.observation)
> **前置**: 637 DELIVERED (路径 C 接受);docs/57 §6 下一步
> **范围**: 3 URL (中央纪委 + 全国人大 + 国务院)

## 0. 顶层裁定

**MIXED** — 适用 3 cell, 实测 3 cell。

总分布:

- REACHABLE: 0
- PARTIAL: 1
- BLOCKED: 2

## 1. 实体逐项

| slug | verdict | http_code | 备注 |
|---|---|---|---|
| 中央纪委国家监委 (central-discipline) | PARTIAL | 200 | ok |
| 全国人大 (npc) | BLOCKED | 0 | timeout |
| 国务院 (central) | BLOCKED | 404 | ok |

## 2. 方法学

REACHABLE: HTTP 200 + body 含 `任免|任免名单|appoint|removal|departure` marker。
PARTIAL: HTTP 200 + body 已加载但 marker 未命中。
BLOCKED: TLS reset / 403 WAF / 404 / connection error。
Limited scope (3 URL): 任免公告省级人大公告可扩展 (后续刀 640+)。

## 3. 数据源合规

✓ 全部政府源 (ccdi.gov.cn / npc.gov.cn / www.gov.cn)；✓ 无商业库；✓ 无用户裁定 URL。

## 4. 红线遵守

- ✓ 不写 cegr.observation
- ✓ 不静默硬编码 GDP 值
- ✓ 不爬网（仅探可达性，不抓内容入库）
- ✓ 脚本幂等
- ✓ 不宣称 Gate / O1 / M2 / M4 PASS
