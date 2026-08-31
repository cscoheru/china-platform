# 56 — M2：2024 年国家 + 31 省 GDP 覆盖（任务拆分）

> 依据：`docs/54` §M2；`docs/08b` §1.2（U2）；用户 2026-08-31 **M1 有限通过** + 开 M2。
> **不宣布 Gate / O1 / M2 PASS。** M1 管线已通（湖北单点）；本里程碑扩面到 31 省年度 GDP。
> 商业库（U4）：M2 仍不买。禁首页 HTML 当 observation 源。

---

## 0. 目标（唯一）

回答 08b：**2024 年国家 + 31 省 GDP（及可得的三次产业）与官方口径一致率**；每条 observation 一跳回源且 SHA=文件字节；缺省写 `missing_reason`。

---

## 1. 刀序（合刀允许；首页刀禁止）

| 刀 | 内容 | 完成条件（摘要） |
|---|---|---|
| **M2-a** | 31 省 `geo_entity` 种子 + 2024 GDP **源清单**（表级 URL/文件，非首页）+ 覆盖率空表 | pytest：31 省 geo 存在；inventory CSV ≥31 行含 status |
| **M2-b** | 首批 ≥5 省（含湖北复用路径 + 苏/粤/浙优先）2024 GDP **表** ingest SUCCESS | 每省 ≥1 GDP observation；一跳 SHA |
| **M2-c** | 扩到 31 省；缺省 `missing_reason`；覆盖率报告可生成 | 覆盖率脚本 exit 0；&lt;20 省有值且无 missing → 不得退出 |
| **M2-d** | 跨源核对（国家 vs 省）；&lt;0.5% 一致否则 QUARANTINED | 31 行核对表 |
| **M2-e** | `/research/q1-2024-gdp`（或等价）+ caveat + 一跳 | smoke 绿；无 500 |
| **M2-f** | 文档/队列；可选回补 2001 起 GDP 族（达不到列不可得） | docs/54 M2 指针；不宣布 PASS |

首刀任务书：**631（M2-a）**。

---

## 2. KPI / 禁

**KPI：** `geo×indicator×year=2024` 覆盖率；核对一致率；非 demo observation 行数。  
**禁：** 11/15、首页字节、刀号、mart demo 冒充、江苏页绑他省数、自动 Gate PASS。

---

## 3. 与 M1 关系

复用：T1 UUID 模式、`ProvincialYearbookConnector` SUCCESS 路径、`int_indicator_timeseries`、series API、M1 验收页模式。  
湖北 2026H1 样本 **不是** 2024 年度点；M2 须另取 **2024 年** 官方表。

— End 56 —
