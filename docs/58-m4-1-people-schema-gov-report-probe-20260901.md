# 58 — M4.1 人物表 schema 收口 + 政府工作报告数据可得性 probe（2026-09-01，knife 638）

> **类型**: 架构师级审查文档（执行端 self-deliver；非用户问句）
> **依据**: `docs/57-m3-launch-conditions-review-20260901.md` §6 下一步 + `docs/54-milestone-replan-20260830.md` §M4.1 + 636 probe 方法学
> **不宣布 Gate / O1 / M2 / M4 PASS。**
> **架构师裁定：M4.2 任免数据 demo 推荐 ccdi.gov.cn 公告列表页 + 23 试点省人民政府首页（路径可用率 23/32 = 71.9%；任免公告路径待 639 二次探活）**

---

## 1. M4.1 落地终态（截至 2026-09-01）

| sub-knife | 状态 | 关键 KPI |
|---|---|---|
| **638-A.1** 政府工作报告 probe | ✅ DONE | `scripts/probe_gov_report_2024.py` 32/32 实测；23 REACHABLE / 0 PARTIAL / 9 BLOCKED |
| **638-A.2** 任免公告 probe | ✅ DONE | `scripts/probe_renmian_announcement_2024.py` 3/3 实测；0 REACHABLE / 1 PARTIAL / 2 BLOCKED |
| **638-A.3** 人物表 schema 收口 | ✅ DONE | `schema/migrations/015-m4-1-people-schema.sql` 加性 ADD COLUMN（is_demo / last_verified_at）+ 3 索引；零 DROP / 零 RENAME / 零 FK / 零 CHECK |
| **638-A.4** docs/58 | ✅ DONE | 本文件 §1-§6 六段 |

**M4.1 收口结论：**
- schema 收口完成（015 additive DDL）
- 政府工作报告可达性 **超预期**（23/32 = 71.9% REACHABLE，636 §2 WAF IP-level 阻断假设需重新审视 — 路径差异显著）
- 任免公告路径 **仍阻塞**（ccdi PARTIAL 是首页可达非任免公告可达；npc timeout；国务院 404 是 URL 错）

---

## 2. 政府工作报告 probe 数据（基于 638-A.1）

**总分布：32 cell 实测 = REACHABLE 23 / PARTIAL 0 / BLOCKED 9**（详见 `evidence_pack/m4_1_gov_report_probe_20260901.json`）。

### 2.1 试点省 verdict（per docs/54 §3 U3：江苏/广东/浙江 + 山东/四川已有 UI）

| 试点省 | verdict | http_code | 备注 |
|---|---|---|---|
| 江苏省 | **REACHABLE** | 200 | www.jiangsu.gov.cn/ 通 |
| 广东省 | **REACHABLE** | 200 | www.gd.gov.cn/ 通 |
| 浙江省 | **REACHABLE** | 200 | www.zj.gov.cn/ 通 |
| 山东省 | **BLOCKED** | TLS_reset | www.shandong.gov.cn/ TLS 层被 WAF reset（与 636 tjj.* 一致） |
| 四川省 | **REACHABLE** | 200 | www.sc.gov.cn/ 通 |

### 2.2 BLOCKED 9 实体

| 实体 | verdict | 根因 |
|---|---|---|
| 国务院（central） | BLOCKED | **HTTP 404** — 探针 URL `https://www.gov.cn/zwgk/zfgbg.htm` 不存在；非 WAF，是 URL 错 |
| 天津市 | BLOCKED | TLS reset（WAF） |
| 江西省 | BLOCKED | TLS reset（WAF） |
| 山东省 | BLOCKED | TLS reset（WAF） |
| 湖北省 | BLOCKED | TLS reset（WAF） |
| 广西壮族自治区 | BLOCKED | TLS reset（WAF） |
| 西藏自治区 | BLOCKED | TLS reset（WAF） |
| 甘肃省 | BLOCKED | TLS reset（WAF） |
| 青海省 | BLOCKED | TLS reset（WAF） |

### 2.3 636 WAF 假设修正

**636 §2 假设**：`本机 IP 125.93.9.191 在 .gov.cn WAF 黑名单 ⇒ 所有 .gov.cn 站点阻断`（基于 tjj.* 31 省统计公报探针）。

**638-A.1 实测修正**：
- 23/31 省 人民政府首页 (`www.*.gov.cn/`) REACHABLE → 636 假设在 `www.*.gov.cn/` 路径**不成立**
- 31/31 省 `tjj.*.gov.cn/*` BLOCKED（636 已证）→ `tjj.*` 子域被针对性 WAF 阻断
- 9 省 + 国务院 路径存在差异（首页 vs 子域 vs /zwgk/zfgbg.htm）

**架构师分析**：WAF 阻断**非全 IP-level**，而是**子域名/路径选择性**。`tjj.*` 子域 100% 阻断；`www.*` 首页部分可达；`/zwgk/zfgbg.htm` 等深路径可能 URL 失效或被 WAF。

**对 M4.2 的含义**：政府工作报告路径 = `www.*.gov.cn/` 起点 + 部委厅局子页查找（23 省可达为强起点）。任免公告路径 = ccdi.gov.cn 公告列表页（PARTIAL 提示首页可达，任免公告列表未直接探）。

---

## 3. 任免公告 probe 数据（基于 638-A.2）

**总分布：3 cell 实测 = REACHABLE 0 / PARTIAL 1 / BLOCKED 2**（详见 `evidence_pack/m4_1_renmian_probe_20260901.json`）。

| 实体 | verdict | http_code | 备注 |
|---|---|---|---|
| 中央纪委国家监委 (ccdi.gov.cn) | **PARTIAL** | 200 | 首页通，但无 `任免\|任免名单` marker — 探针 URL 是首页非任免公告页 |
| 全国人大 (npc.gov.cn) | **BLOCKED** | 0 | timeout（15s 内未响应） |
| 国务院 (gov.cn) | **BLOCKED** | 404 | 探针 URL `/zwgk/zfgbg.htm` 404（非任免公告页） |

**任免公告可达性结论**：
- ccdi.gov.cn 首页可达 ⇒ 任免公告具体页面**可能**可达（639 二次探：ccdi 公告列表 / 审查调查栏目）
- npc.gov.cn timeout（可能 WAF reset 或响应慢；639 重探 URL 用 `https://` 而非 `http://`）
- 国务院 探针 URL 错（638 用 `/zwgk/zfgbg.htm` 是政府工作报告路径非任免公告路径；639 须用全国人大事务栏目 URL）

**任免公告路径不充分是 638 已知 gap**，架构师不假装齐 ⇒ M4.2 启动时 639 必做二次探活。

---

## 4. 人物表 schema 收口（基于 638-A.3）

**`schema/migrations/015-m4-1-people-schema.sql` 加性变更：**

| 表 | 加列 | 类型 | 默认 | 注释 |
|---|---|---|---|---|
| person | `is_demo` | BOOLEAN | NULL | TRUE = demo/示例数据；FALSE = 真实数据；默认 NULL = 既有数据待 016+ 迁移 |
| person | `last_verified_at` | TIMESTAMPTZ | NULL | 最近一次成功一跳回源验证戳 |
| appointment_event | `is_demo` | BOOLEAN | NULL | 与 person.is_demo 一致 |

**索引（3 个）：**
- `idx_person_is_demo` ON person(is_demo)
- `idx_person_last_verified_at` ON person(last_verified_at)
- `idx_appointment_event_is_demo` ON appointment_event(is_demo)

**红线遵守（继承 008 discipline）：**
- ❌ 不 DROP / 不 RENAME 既有列
- ❌ 不加 FK 约束（FK 落到 016+）
- ❌ 不加 CHECK 约束（既有 NULL 行处理需先 backfill；CHECK 后置）
- ❌ 不动 source_registry / mart_*.sql / 4 frontend fixture bytes
- ❌ 不做官员能力分 / 总分 / 排名（is_demo 是隔离标记非评分字段）

**既有数据兼容：** 既有 person / appointment_event 行 `is_demo` 默认 NULL；015 完成后由 016+ 单独议 backfill 脚本（无 current real rows，5 negative tests 必仍 pass）。

---

## 5. M4.2 / M4.3 下一步

### 5.1 M4.2 任免数据 demo（建议 639）

**架构师推荐 scope（M4.2 启动时再议）：**

1. **639-A.1 ccdi 公告列表页 + 任免公告页二次探活** — 探 URL `https://www.ccdi.gov.cn/specialn/scjcf/` 或类似栏目；预计 1-3 个 REACHABLE
2. **639-A.2 23 试点省任免公告路径探活** — 在 638 23 个 REACHABLE 的 `www.*.gov.cn/` 起点上探 `/zwgk/zwxxgkzl/` 或 `/zwgk/zwxxgk/` 路径
3. **639-A.3 demo 表最小实现** — 用 is_demo=true 隔离；写入 ≤ 5 条 demo 人物 + 任期记录（schema 已存在）；不跳真实数据源
4. **639-A.4 docs/59 M4.2 落地终态** — 类比 docs/58 六段结构
5. **639-B 测试 ≥ 6 用例 + 639-C 回执 + 双推**

**M4.2 红线：**
- is_demo=true 显式隔离
- 不爬网（probe 仍只探可达性）
- 不写 cegr.observation 真实行
- demo 数据至少 1 条 source_document_id + source_url 一跳回 SHA

### 5.2 M4.3 政策项目 demo（建议 640）

依 schema 已存在（`policy_document` / `policy_commitment` / `project_event`，per 01-core.sql L711+）。
M4.3 在 M4.2 demo 验证后启动；不预支 scope。

---

## 6. 下一步（639 = M4.2）

- **639 = M4.2 任免数据 demo**（架构师 tasking 在 638 接受后签发）
- 639 探活范围：ccdi 公告列表页 + 23 试点省 `www.*.gov.cn/` 任免路径 + 国务院正确 URL
- 639 demo 数据：≤ 5 条人物 + 任期，is_demo=true 隔离
- **不宣布 Gate / O1 / M2 / M4 PASS**。
- 用户对 638 推荐的接受/驳回路径：
  - 接受 → 639 启动
  - 驳回 → 用户裁定 M4.2 re-scope 或 640 (M4.3 跳过 demo 直接接真实)

— End 58 —