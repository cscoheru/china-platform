# M4.3 政策源 二次探活 probe 报告（2026-09-01，knife 640）

> **类型**: 640-A.1 probe (read-only;不写 cegr.observation)
> **前置**: 639 DELIVERED;docs/59 §5.1 明确 6 REACHABLE 任免源 ≠ 政策源
> **范围**: 13 URL (10 试点省政策承载路径 + 1 ccdi + 1 国务院 政策库)
> **架构师依据**: 640 沿用 638/639 路径选择性 WAF 假设修正;政策承载路径候选

## 0. 顶层裁定

**BLOCKED** — 适用 12 cell, 实测 12 cell;9/12 = 75% BLOCKED 是最强反例。

总分布:

- REACHABLE: 2
- PARTIAL: 1
- BLOCKED: 9

中央 vs 试点省分布:

- 中央 (ccdi /ldwd/ + 国务院 /zhengce/zhengceku/ = 2): {'PARTIAL': 1, 'BLOCKED': 1}
- 试点省 (10 政策承载路径 /zwgk/zfwj/ + /zwgk/zfgb/ + /zwgk/ghjh/): {'REACHABLE': 2, 'BLOCKED': 8}

## 1. 实体逐项

| slug | verdict | http_code | 备注 |
|---|---|---|---|
| 黑龙江政策文件 (heilongjiang-policy-zfwj) | REACHABLE | 200 | ok |
| 黑龙江政府公报 (heilongjiang-policy-zfgb) | REACHABLE | 200 | ok |
| 福建政策文件 (fujian-policy-zfwj) | BLOCKED | 404 | ok |
| 福建政府公报 (fujian-policy-zfgb) | BLOCKED | 404 | ok |
| 河南政策文件 (henan-policy-zfwj) | BLOCKED | 404 | ok |
| 河南规划计划 (henan-policy-ghjh) | BLOCKED | 404 | ok |
| 广东政策文件 (guangdong-policy-zfwj) | BLOCKED | 404 | ok |
| 广东政府公报 (guangdong-policy-zfgb) | BLOCKED | 404 | ok |
| 贵州政策文件 (guizhou-policy-zfwj) | BLOCKED | 404 | ok |
| 云南政策文件 (yunnan-policy-zfwj) | BLOCKED | 404 | ok |
| 中央纪委领导/制度 (central-discipline-ldwd) | PARTIAL | 200 | ok |
| 国务院政策库 (central-zhengceku) | BLOCKED | 403 | ok |

## 2. 方法学

REACHABLE: HTTP 200 + body 含 `政策文件|政府公报|规划计划|政府工作报告|五年规划|规范性文件|policy|regulation|five.year.plan` marker。
PARTIAL: HTTP 200 + body 已加载但 marker 未命中（栏目命中政策路径不正确）。
BLOCKED: TLS reset / 403 WAF / 404 / connection error。
二次探活 URL 选择（继承 639 PARTIAL/BLOCKED 已知 gap）:
- 试点省: 639 REACHABLE 6 试点省的 /zwgk/ 任免栏目,640 重打 /zwgk/zfwj/ (政府文件) + /zwgk/zfgb/ (政府公报) + /zwgk/ghjh/ (规划计划) 政策承载路径。
- ccdi: 639 PARTIAL /yaowen/ + /specialn/scjcf/ 是要闻 / 审查调查栏;640 试 /ldwd/ (领导/制度) 含部分政策。
- 国务院: 639 PARTIAL /zhengce/ 是政策栏;640 加试 /zhengce/zhengceku/ (政策库) 子栏目。

## 3. 639 vs 640 对比

- 639 6 REACHABLE 任免源 (/zwgk/) ⇒ 640 重打为 10 政策承载路径
  (/zwgk/zfwj/ + /zwgk/zfgb/ + /zwgk/ghjh/) → **仅 黑龙江 /zwgk/zfwj/
  + /zwgk/zfgb/ REACHABLE 2** (黑龙江任免 REACHABLE → 政策也 REACHABLE;
  其他 5 省任免 REACHABLE → 政策 BLOCKED 404)
- 639 PARTIAL 中央 (ccdi 2 + 国务院 2) ⇒ 640 重打 ccdi /ldwd/ PARTIAL +
  国务院 /zhengce/zhengceku/ BLOCKED (403 WAF,与 639 PARTIAL /zhengce/ 一致)
- 639 BLOCKED 15 (npc TLS reset + 13 试点省 404/403) ⇒ 640 不复用,640
  仅探 6 REACHABLE 试点省政策路径(避开 BLOCKED)
- **关键反发现 (架构师裁定)**: 6 REACHABLE 任免源中仅 1 省 (黑龙江) 的
  政策承载路径真正可达;其他 5 省 /zwgk/zfwj/ /zwgk/zfgb/ 全 404 (路径
  不存在而非 WAF,因黑龙江同路径可达)。这反驳了"任免源 ≈ 政策源"
  隐含假设,**政策 demo 不得绑定具体省份名**;640 demo 用 3 个 synthetic
  `M4.3 demo province N` geo_entity 替代真实省份(详见 docs/60 §3)。

## 4. 数据源合规

✓ 全部政府源 (ccdi.gov.cn / www.gov.cn / 6 www.*.gov.cn 政策承载路径);✓ 无商业库;✓ 无用户裁定 URL。

## 5. 红线遵守

- ✓ 不写 cegr.observation
- ✓ 不静默硬编码 GDP 值
- ✓ 不爬网（仅探可达性,不抓内容入库）
- ✓ 脚本幂等（无 random / 无 time.sleep）
- ✓ 不宣称 Gate / O1 / M2 / M4 PASS
