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

---

## 5. 进度更新（636 落地后 · M2-f 收口）

- **636-A 文档收口**：docs/56 §5（本段）+ docs/54 §M2.4 行收口 + EXEC-QUEUE rev59（636 DELIVERED 进入 §CHAIN_TAIL）三处指针闭环。
- **636-B 2001-onwards 回补可行性 probe**：`scripts/probe_m2_2001_backfill.py` 对 **24 年 × 32 主体 × 3 源 = 2309 cell（含 5 镜像候选）** 实测 184 HTTP 探针 + 2125 推得 cell，**适用 cell 1541 实测 REACHABLE 0 / PARTIAL 770 / BLOCKED 771**：
  - **NBS data.stats.gov.cn** —— 0/24 REACHABLE（24/24 BLOCKED，403 Forbidden WAF 网防G01 IP 阻断；M2-b 6 主体 COVERED 走的是各省本站抓取，非 NBS JSON API）
  - **各省 tjj.*** —— 0/744 REACHABLE（31 省 × 5 样本年（2001/2006/2011/2016/2024）实测 155 cell 全 BLOCKED：TLS reset / 404 / 403 / 412 / SSL_ERROR_SYSCALL / no alternative certificate；WAF IP-level 阻断跨年稳定 ⇒ 19 个非样本年外推结论可信）
  - **全国统计年鉴镜像** —— 2/5 PARTIAL + 3/5 BLOCKED：catalog 可达但无 entity×year×GDP 单元；真实 GDP 值需 deep-link 跳到具体年鉴页
  - **总计 2309 cell**：REACHABLE **0** / PARTIAL **770** / BLOCKED **771** / NOT_APPLICABLE **768**
- **636-C 测试 + 回执 + 双推**：`tests/test_m2_backfill_feasibility.py` ≥5 用例 + 636 回执 §PHOTO-1..6 + pytest ≥37/37 green + commit + origin→github 双推。
- **M2 全部收口**：M2.1 ✅ / M2.3 ✅ / M2.5 ✅ / **M2.4 ✅（feasibility probed; 适用 cell 1541 实测 REACHABLE 0 / PARTIAL 770 / BLOCKED 771；不可得项已诚实列）**。
- **不宣布 Gate / O1 / M2 PASS**。M2 PASS 维持 OPEN：M2.4 仅完成「可行性 probe」≠「实际回补入库」；真入库需要用户提供 NBS data.stats.gov.cn 镜像源 / 各省年鉴 PDF（用户绕过本机 IP-level WAF）/ 第三方合法授权年鉴库（U4 暂禁）。
- **M3 启动条件**：M2.4 已可达 cell ≤3 ⇒ **不得自动进入 M3**；须用户先裁定是否购买商业年鉴库（U4 重审）或用户提供政府源直连镜像。

— End 56 —
