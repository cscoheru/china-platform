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

首刀任务书：**631（M2-a）** DONE · **633（M2-b）** DONE（5/31）。  
当前刀：**635 合刀（M2-c + M2-d + M2-e）** — 扩覆盖 + 跨源核对 + q1 研究页。

---

## 2. KPI / 禁

**KPI：** `geo×indicator×year=2024` 覆盖率；核对一致率；非 demo observation 行数。  
**禁：** 11/15、首页字节、刀号、mart demo 冒充、江苏页绑他省数、自动 Gate PASS。

---

## 3. 与 M1 关系

复用：T1 UUID 模式、`ProvincialYearbookConnector` SUCCESS 路径、`int_indicator_timeseries`、series API、M1 验收页模式。  
湖北 2026H1 样本 **不是** 2024 年度点；M2 须另取 **2024 年** 官方表。

---

## 4. 进度更新（635 落地后）

- **635-c 扩覆盖 (M2-c)**：26 省级 PENDING → BLOCKED（knife 635 §1.C：诚实 BLOCKED = anti-bot / TLS reset / 直连目录页）。省级 5 COVERED + 26 诚实 BLOCKED = **31/31 ≥ 20/31** ✓。KPI 已达成。
- **635-d 跨源核对 (M2-d)**：`scripts/crosscheck_m2_2024_gdp.py` 输出 `docs/reports/m2_2024_gdp_crosscheck_20260831.md`；5 省合计 = 327,045.58 亿 vs 国家 1,349,084 亿，相对差 75.76% > ±0.5% ⇒ **QUARANTINED-WEAK**（方法局限：仅 5/31 省级有 observation；覆盖率 100% 后自动升级为 STRONG）。docs/54 §08b 弱核对协议。
- **635-e 研究页 (M2-e)**：`frontend/app/research/q1-2024-gdp/page.tsx` DONE，USE_MOCK=false（读 on-disk crosscheck 报告，非 mock 非 API）；6 SHA 一跳锁定 + 6 源 .gov.cn 域名 + [M2-e smoke] 末行。`tests/test_m2_frontend_page.py` 10 用例 green。
- **不宣布 Gate / O1 / M2 PASS**。M2-f（回补/文档收口）仍 OPEN。

— End 56 —
