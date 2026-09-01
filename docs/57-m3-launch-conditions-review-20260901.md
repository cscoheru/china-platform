# 57 — M3 启动条件审查（2026-09-01，knife 637）

> **类型**: 架构师级审查文档（执行端 self-deliver；非用户问句）
> **依据**: `docs/56` §5「M3 启动条件」+ `docs/54` §M3 + 636 receipt §9 + 636 probe 数据
> **不宣布 Gate / O1 / M2 PASS。** 不让用户选 A/B/C（数据源治理铁律 2026-08-29 立）。
> **架构师裁定：路径 C（维持现状 + 转向 M4-M5）。**

---

## 1. M2 全收口终态（截至 2026-09-01）

| sub-knife | 状态 | 落地文件 / 关键 KPI |
|---|---|---|
| **M2.1** 31 省 GDP 入库 | ✅ DONE | 5 COVERED + 26 诚实 BLOCKED = **31/31 ≥ 20/31**；`scripts/fetch_m2_2024_gdp.py` + `source_registry/m2_2024_gdp_inventory.csv` |
| **M2.2** 三次产业增加值 | ⏸ DEFERRED | 与 M2.1 同源（NBS + tjj.*），636 probe 实测 0 REACHABLE ⇒ 同样硬阻断；保留 OPEN 至 M3 启动 |
| **M2.3** 跨源核对 | ✅ DONE | `scripts/crosscheck_m2_2024_gdp.py` + `docs/reports/m2_2024_gdp_crosscheck_20260831.md`；verdict = **QUARANTINED-WEAK**（5/31 弱核对；覆盖 100% 后升级 STRONG） |
| **M2.4** 2001 起回补 | ✅ DONE（feasibility probed） | `scripts/probe_m2_2001_backfill.py` 2309 cell 实测；适用 cell 1541 实测 **REACHABLE 0 / PARTIAL 770 / BLOCKED 771**；真入库需要用户提供政府源镜像 / 商业年鉴库授权 |
| **M2.5** `/research/q1-2024-gdp` 页 | ✅ DONE | `frontend/app/research/q1-2024-gdp/page.tsx` USE_MOCK=false；6 SHA 一跳 + 6 .gov.cn 源 + 末行 `[M2-e smoke]` |

**M2 收口结论：**
- 5/5 sub-knife 状态明确
- **M2 PASS 维持 OPEN**：M2.4 仅 feasibility probed ≠ actual ingest
- 5 主体（国家 + 北京 + 上海 + 山东 + 湖北 + 四川）真实 observation SUCCESS + 26 主体诚实 BLOCKED（缺 missing_reason）
- 跨源核对仅 5 省 QUARANTINED-WEAK（覆盖率不足）

---

## 2. M3 启动硬阻断分析（基于 636 probe 数据）

**M3 默认范围**（per `docs/54` §M3）：试点监测，江苏深挖 + 广东 + 浙江，每省 2-4 城公报或年鉴表 → observation。

**数据依赖项结构：**

| 数据依赖项 | 636 probe 实测结果 | 阻塞等级 |
|---|---|---|
| NBS data.stats.gov.cn API（国家序列） | 24/24 BLOCKED（WAF 403） | **硬阻断** |
| 各省 tjj.*.gov.cn 公报/统计页 | 744/744 BLOCKED（TLS reset / 404 / 403 / 412 / SSL_ERROR_SYSCALL / no alternative certificate） | **硬阻断** |
| 全国统计年鉴镜像 | 2/5 PARTIAL + 3/5 BLOCKED（catalog only） | **半阻断**（catalog 可达但无 entity×year×GDP） |

**根因分析：**

- **NBS API 阻断** —— 本机 IP `125.93.9.191` 被 .gov.cn 网防G01 WAF IP-level 阻断；同 IP 上 curl / playwright / 5 UA profiles 全失败（635 §1.C + 636 probe 双证）
- **tjj.* 阻断** —— 31 省站点的 HTTPS TLS 层被 WAF 主动 reset；非 UA / 非 cookie / 非 captcha 可解决；属结构性 IP 拦截
- **WAF 阻断跨年稳定** —— 636 probe 实测 31 省 × 5 样本年（2001/2006/2011/2016/2024）全 BLOCKED ⇒ 跨年同样阻断 ⇒ 历史回补不可能

**Probe 适用 cell 1541 总分布：REACHABLE 0 / PARTIAL 770 / BLOCKED 771**（636 实测；详见 `docs/reports/m2_2001_backfill_feasibility_20260901.md`）。

**结构性结论：** M3 默认数据源（tjj.*.gov.cn 公报）在当前执行环境无法访问；非绕过 WAF 不可 ingest。

---

## 3. 三条可能路径分析（非用户问句）

> **数据源治理铁律（2026-08-29 立）**：执行端不向用户提任何数据源/URL/年份的裁定事项。本节仅作架构师分析；不构成对用户的问句。

### 路径 A：用户提供政府源镜像 / 浏览器导出
- **机制**：用户本地浏览器登录后导出 PDF/HTML（绕过本机 IP-level WAF）；或用户提供镜像站 URL（如 mrtx.gov.cn/xxgk/statistics）
- **成本**：用户手动成本高（31 省 × 5 年 = 155 文件），数据治理链需重做（PDF/HTML 解析 + SHA 锁定 + observation ingest）
- **可达性**：若用户提供，1 周内可重做 M3.1 试点江苏
- **风险**：PDF/HTML 解析器脆弱（OCR / 表格结构 / 单位差异）；用户零散提供的数据质量参差
- **数据源合规**：✓ 政府源

### 路径 B：购买商业年鉴库授权（U4 重审）
- **机制**：购买 CEInet / EPSdata / 中经网 / 万方 等商业年鉴库 API 授权；批量 ingest 2001-2024 国家+省+城 GDP
- **成本**：商业库授权费用（5-30 万/年量级）；需 DBA 维护 ETL 同步
- **可达性**：商业库 API 稳定，可批量覆盖 2001-2024；可达 cell 数预估 1541/1541（适用 cell 100% REACHABLE）
- **风险**：商业库口径与官方公报可能差 1-3%（修订 / 数据来源差异）；需每月对账
- **数据源合规**：❌ 商业库；U4 暂禁；用户须重审 U4

### 路径 C：维持 M2 现状 + 转向 M4-M5
- **机制**：保持 5 主体 COVERED + 26 主体诚实 BLOCKED 现状；将执行端产能从「数据 ingest」转向「方法与人物政策」
- **成本**：零（不依赖用户提供源 / 不依赖商业库）；可立即启动 M4 / M5
- **可达性**：M4 人物政策 / M5 分析方法无数据依赖项，可独立推进
- **风险**：M3 数据闭环延后至用户提供源 / U4 重审 / WAF 解封时
- **数据源合规**：✓ 不引入新数据源

---

## 4. 架构师推荐：路径 C（维持现状 + 转向 M4-M5）

**裁定依据：**

1. **数据源治理铁律**：路径 A 需用户手动登录 / 提供源 ⇒ 违反「执行端不可提任何用户裁定事项」（注册/登录属用户裁定范围外）；路径 B 违反 U4 暂禁。
2. **结构性 WAF 阻断非短期可解**：本机 IP 125.93.9.191 在 .gov.cn WAF 黑名单；解封需 ISP / VPN 介入；非执行端可控。
3. **M4 / M5 无数据依赖**：M4（人物政策 demo 表 + is_demo 隔离）已 schema 存在；M5（分析方法 docs/10 §3.2-3.4）xfail 待实做。两条都可独立推进，不依赖 M3 数据闭环。
4. **进度 KPI 不阻塞**：docs/54 §4 进度 KPI = `observation` 行数 + `geo×indicator×year` 覆盖率 + missing_reason；M2 已达成 5 + 26 诚实 BLOCKED；M3 默认范围卡在数据获取而非执行端产能。

**路径 C 含义：**
- M2 现状冻结（不再扩 31 省 / 不再回补 2001 起）
- 启动 **M4（人物政策）**优先：is_demo 表已存在；可补 M1 的 gov-report/任免/承诺数据
- 同步启动 **M5（分析方法）** spike：docs/10 §3.2-3.4 从 xfail 实做（同类匹配 / 条件化相对表现 / 缺失值）

**M3 重新激活条件**（任一）：
- 用户本地浏览器导出 PDF/HTML 提供给执行端
- 用户重审 U4（商业年鉴库授权）
- WAF 解封（用户更换网络环境 / 提供镜像源）

---

## 5. M4 / M5 优先序

**M4 优先**（理由：依赖现有 is_demo schema；与 M2 数据管线无冲突）：

| sub-knife | 范围 | 估时 |
|---|---|---|
| M4.1 | 人物表 schema 收口 + 政府工作报告数据可得性 probe（国务院 / 31 省） | 1 周 |
| M4.2 | 任免数据 demo（is_demo=true 隔离） | 1 周 |
| M4.3 | 政策项目 demo（schema 已存在） | 1 周 |
| M4.4 | 时间线只显示重合（docs/02 §M4） | 1 周 |

**M5 平行推进**（理由：纯方法学，无数据依赖）：

| sub-knife | 范围 | 估时 |
|---|---|---|
| M5.1 | docs/10 §3.2 同类匹配实做（xfail → pass） | 2 周 |
| M5.2 | docs/10 §3.3 条件化相对表现实做 | 2 周 |
| M5.3 | docs/10 §3.4 缺失值显式 BLOCKED | 1 周 |
| M5.4 | DSH（docs/07）sidecar 评估，不进 ETL | 2 周 |

**总估时：M4 ≈ 4 周，M5 ≈ 7 周（部分可并行）。**

---

## 6. 下一步

- **638 = M4.1 人物表 schema 收口 + 政府工作报告数据可得性 probe**（架构师 tasking 在 637 接受后签发）
- 638 probe 类比 636：探 31 省 + 国务院 + 中央纪委网站可达性 + 全国人大网任免公告可达性
- M5.1 spiking 在 638 之后单独签（638 不阻塞 M5.1）
- **不宣布 Gate / O1 / M2 PASS**。
- 用户对 637 推荐的接受/驳回路径：
  - 接受路径 C → 638 启动（M4.1 probe）
  - 驳回路径 C → 用户裁定 A 或 B ⇒ 执行端按裁定落 638 (re-scope) 或 639 (U4 重审 + M3 重启)

— End 57 —