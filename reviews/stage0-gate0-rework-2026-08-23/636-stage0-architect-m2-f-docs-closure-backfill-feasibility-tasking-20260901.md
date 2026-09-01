# 636 — M2-f：文档收口 + 2001 起回补可行性（执行端 tasking）

> **类型**: 架构师+程序员合并 → 自签 tasking
> **日期**: 2026-09-01
> **前置**: 635 DELIVERED（省级 5 COVERED + 26 BLOCKED = 31/31；crosscheck QUARANTINED-WEAK；研究页 DONE）
> **依据**: `docs/56` §1.M2-f + `docs/54` §M2.4
> **架构师审**: cursor 暂时不可用；本端按 memory `china-platform-exec-mechanism.md`（架构师+程序员合并授权）自签 tasking + 自交付。

---

## 0. 目标（唯一）

回答 **M2-f = 文档收口 + 2001 起回补可行性**：

1. **636-A 文档收口**：docs/56 §5（M2-f 落地）+ docs/54 §M2.4 收口 + EXEC-QUEUE rev59（636 NOW → DELIVERED）。所有指针闭环。
2. **636-B 2001-onwards 回补可行性**：probe **可达** 的政府/统计/研究机构历史数据库（**仅 NBS data.stats.gov.cn** + **各省 tjj.* 历年公报索引页可达性** + **全国统计年鉴镜像站**），不实际入库；输出 `docs/reports/m2_2001_backfill_feasibility_20260901.md` 含 REACHABLE / PARTIAL / BLOCKED 矩阵。
3. **636-C 测试 + 回执 + 双推**：`tests/test_m2_backfill_feasibility.py` ≥5 用例 + 636 回执 §PHOTO-1..6 + commit + origin→github 双推。

---

## 1. 禁（红线）

| 禁 | 来源 |
|---|---|
| 不宣布 Gate / O1 / M2 PASS | memory `china-platform-exec-mechanism.md` |
| 不补零（缺源即 BLOCKED，不可 zero-fill 当覆盖） | 635 §1.C / docs/08b |
| 不静默硬编码 value | 635 §1.C.3 |
| 不爬网（首页/目录页当表源） | 635 §1.C |
| 不买商业库 / 不接入第三方 API | memory `china-platform-587-data-source-governance.md` |
| 不让用户裁定任何数据源/URL/年份（除注册/登录/付费/UI 验收） | 数据源治理铁律 |
| 不实际 ingest 历史 observation | 636 §B 只做 probe，不写 cegr.observation |
| 不改 docs/45/50 正文 | 635 §PHOTO-7 红线 |
| 不碰 4 fixture 锁值 | 635 §PHOTO-7 |

---

## 2. 刀序

### 636-A 文档收口
- **A.1** `docs/56-m2-gdp-coverage-task-breakdown-20260831.md` 追加 §5「M2-f 落地」段（635/636 状态收口；M2-a/b/c/d/e/f 全 close；M2 PASS 仍 OPEN；M3 启动条件 列出）
- **A.2** `docs/54-milestone-replan-20260830.md` §M2.4 行追加 636 feasibility outcome（实际可及/不可及/部分可及）+ 不装 PASS 注释
- **A.3** `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` rev59：635 DELIVERED → 636 DELIVERED；636 行进入 §CHAIN_TAIL；M2 全部收口

### 636-B 2001-onwards 回补可行性 probe
- **B.1** `scripts/probe_m2_2001_backfill.py`:
  - 输入：years [2001..2024] (24 年) × entities [国家 + 31 省] (32 主体) = 768 cell
  - Probe 3 类源：
    1. NBS data.stats.gov.cn (公开 JSON API, 无 anti-bot, M2-b 已验证可达)
    2. 各省 tjj.* 历年公报索引页 (URL 模式 `/tjgb/list_*` 或类似) — 5 UA profiles
    3. 全国统计年鉴 mirror — 镜像站列表（CNKI 政府统计镜像 / stats.gov.cn 年鉴 / 中国经济社会大数据研究平台 等）
  - 每 cell verdict：
    - REACHABLE：HTTP 200 + body 含 GDP value marker
    - PARTIAL：HTTP 200 + 无 GDP marker (页面加载但内容不全)
    - BLOCKED：TLS reset / 404 / directory-only / empty
  - 输出：
    - `docs/reports/m2_2001_backfill_feasibility_20260901.md` (人读)
    - `evidence_pack/m2_2001_backfill_feasibility_20260901.json` (机读)
- **B.2** `tests/test_m2_backfill_feasibility.py` ≥5 用例:
  - 报告文件存在 + 标题正确
  - REACHABLE/PARTIAL/BLOCKED 计数打印
  - 国家 2001-2024 至少 N≥3 cell REACHABLE (实测应 ≥20)
  - 31 省 × 2001 起至少 1 源 REACHABLE (NBS proxy 给所有省年度 GDP)
  - 不写 cegr.observation (probe 只读)
  - 不静默 hardcode value

### 636-C 测试 + 回执 + 双推
- **C.1** `tests/test_m2_backfill_feasibility.py` ≥5 用例 PASS
- **C.2** `tests/test_m2_crosscheck.py tests/test_m2_b_first_batch.py tests/test_m2_province_geo_seed.py tests/test_m2_frontend_page.py tests/test_m2_backfill_feasibility.py` 全部 ≥37 用例 green
- **C.3** `reviews/stage0-gate0-rework-2026-08-23/636-stage0-cc-m2-f-docs-closure-backfill-feasibility-receipt-20260901.md` 含 §PHOTO-1..6
- **C.4** `git add` + `git commit -m "feat(636): M2-f 文档收口 + 2001-onwards 回补可行性 probe"` + `git push origin HEAD` + `git push github HEAD`

---

## 3. 完成条件（Acceptance Criteria）

- [ ] docs/56 §5 增量存在
- [ ] docs/54 §M2.4 收口行存在
- [ ] EXEC-QUEUE rev59，636 DELIVERED，§CHAIN_TAIL 含 636
- [ ] `docs/reports/m2_2001_backfill_feasibility_20260901.md` 存在且 verdict 矩阵完整
- [ ] `evidence_pack/m2_2001_backfill_feasibility_20260901.json` 存在
- [ ] pytest ≥37/37 PASS
- [ ] 不宣布 Gate / O1 / M2 PASS

---

## 4. 不做的（明确边界）

- ❌ 不 ingest 历史 observation（probe 只读）
- ❌ 不接 NBS JSON API 拿 2001-2024 历史（这是下一刀 M3.x / M-govdata-historic 的范围）
- ❌ 不修 4 fixture（registry.csv / mart_city_*.sql / frontend fixtures）
- ❌ 不改 docs/45/50
- ❌ 不声明 M2-f PASS（仅 M2-f 落地）

---

## 5. 红线自审（默认）

| 红线 | 自审 |
|---|---|
| 数据源唯一=政府/统计/研究机构 | ✓ NBS data.stats.gov.cn / tjj.* / 全国统计年鉴镜像 |
| 不爬网 | ✓ probe 命中即停，不存档 HTML（仅 verdict） |
| 不补零 | ✓ BLOCKED cell 不写 observation |
| 不静默硬编码 | ✓ REACHABLE cell 必须 regex parse + 兜底 cross-check |
| 不宣布 PASS | ✓ 本 tasking + 后续回执均不宣称 M2-f PASS |

— End 636 tasking —