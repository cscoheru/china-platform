# 637 — M3 启动条件审查（执行端 tasking）

> **类型**: 架构师+程序员合并 → 自签 tasking
> **日期**: 2026-09-01
> **前置**: 636 DELIVERED（M2 全部收口；probe 适用 cell 1541 实测 REACHABLE 0 / PARTIAL 770 / BLOCKED 771）
> **依据**: `docs/56` §5「M3 启动条件」+ `docs/54` §M3 + 636 receipt §9「下一步」
> **架构师审**: cursor 暂时不可用；本端按 memory `china-platform-exec-mechanism.md`（架构师+程序员合并授权）自签 tasking + 自交付。
> **数据源治理铁律（2026-08-29 立）**：执行端不可提任何用户裁定事项；不提供「选 A / B / C」选项问句。本刀给出**架构师裁定 + 推荐路径**，等用户接受/驳回。

---

## 0. 目标（唯一）

回答 **M3 启动条件审查** = **M2 收口是否构成 M3 自动启动条件；若否，转向何处**：

1. **637-A M3 启动条件审查文档**：`docs/57-m3-launch-conditions-review-20260901.md` 包含：
   - §1 M2 全收口终态（M2.1/2/3/4/5 5/5 状态；M2 PASS 维持 OPEN 原因）
   - §2 M3 启动硬阻断分析（636 probe 实测：NBS / tjj.* / 年鉴镜像均 0 REACHABLE；不可在本机直接 ingest）
   - §3 三条可能路径分析（数据源镜像 / 商业年鉴库授权 / 维持现状转 M4-M5）—— 仅作架构师分析，不作用户问句
   - §4 架构师推荐（路径 C：维持 M2 现状 + 转向 M4-M5；理由：M3 数据依赖项硬阻断；M4-M5 无数据依赖项可独立推进）
   - §5 M4 / M5 优先序（人物政策优先于分析方法；M4.1 = schema + 数据可得性 probe）
   - §6 下一步（638 = M4.1 人物表 schema + 数据可得性 probe）
2. **637-B 测试 + 回执 + 双推**：`tests/test_m3_launch_conditions_review.py` ≥5 用例 + 637 回执 §PHOTO-1..6 + commit + origin→github 双推。

---

## 1. 禁（红线）

| 禁 | 来源 |
|---|---|
| 不宣布 Gate / O1 / M2 PASS | memory `china-platform-exec-mechanism.md` |
| 不提供「选 A / B / C」选项让用户裁定 | 数据源治理铁律（2026-08-29） |
| 不爬网 | 636 §PHOTO-7 |
| 不实际 ingest 任何数据 | M3 启动条件未达成，不入库 |
| 不让用户登录 NBS / tjj.* 提供镜像源 | 铁律（执行端不提任何用户裁定） |
| 不接商业库（U4 暂禁） | docs/54 §8 U4 |
| 不改 docs/45/50 正文 | 635 §PHOTO-7 红线 |
| 不碰 4 fixture 锁值 | 635 §PHOTO-7 |

---

## 2. 刀序

### 637-A 启动条件审查文档

- **A.1** `docs/57-m3-launch-conditions-review-20260901.md` 创建（含 §1-§6 六段）
- **A.2** `docs/56-m2-gdp-coverage-task-breakdown-20260831.md` 追加 §6「M3 启动审查（637 落地）」段（指向 docs/57）
- **A.3** `docs/54-milestone-replan-20260830.md` §M3 前追加 637 推荐（路径 C）
- **A.4** `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` rev60：636 DELIVERED → 637 NOW → DELIVERED；§CHAIN_TAIL 增 637

### 637-B 测试

- **B.1** `tests/test_m3_launch_conditions_review.py` ≥5 用例：
  - 文档文件存在 + 含 §1-§6 全部 6 段
  - §2 含 636 probe 引用 + REACHABLE 0 数据
  - §3 含三条路径分析（数据源镜像 / 商业库 / 维持现状）—— 但**不是问句**（必须含「架构师推荐」字样，不含「请选择」/「您希望」问句）
  - §4 含明确推荐（路径 C 或等价）
  - §5 含 M4 / M5 优先序
  - §6 含 638 下一步刀序
  - 不修改 cegr.observation（review 只读）
  - 不静默硬编码 value

### 637-C 回执 + 双推

- **C.1** 全 M2 套件 + test_m3_launch ≥5 用例 → ≥45/45 green
- **C.2** `reviews/stage0-gate0-rework-2026-08-23/637-stage0-cc-m3-launch-conditions-review-receipt-20260901.md` 含 §PHOTO-1..6
- **C.3** `git add` + `git commit -m "feat(637): M3 启动条件审查 — 架构师推荐路径 C (维持现状 + 转向 M4-M5)"` + `git push origin HEAD` + `git push github HEAD`

---

## 3. 完成条件（Acceptance Criteria）

- [ ] docs/57 §1-§6 六段全部存在
- [ ] docs/56 §6 增量存在
- [ ] docs/54 §M3 前 637 推荐存在
- [ ] EXEC-QUEUE rev60，637 DELIVERED，§CHAIN_TAIL 含 637
- [ ] `tests/test_m3_launch_conditions_review.py` ≥5 用例 PASS
- [ ] pytest ≥45/45 PASS
- [ ] 不宣布 Gate / O1 / M2 PASS
- [ ] 不提供用户裁定问句
- [ ] 不接商业库 / 不爬网 / 不 ingest

---

## 4. 不做的（明确边界）

- ❌ 不让用户选 A/B/C（数据源治理铁律）
- ❌ 不 ingest M3.1 江苏试点数据（M3 数据依赖项硬阻断）
- ❌ 不买商业年鉴库（U4 暂禁）
- ❌ 不改 docs/45/50
- ❌ 不宣布 M3 启动（M3 启动条件不达成）

---

## 5. 红线自审（默认）

| 红线 | 自审 |
|---|---|
| 数据源治理铁律 | ✓ 架构师裁定单一推荐路径；不向用户问句 |
| 不爬网 | ✓ 637 review 只读文档 |
| 不 ingest | ✓ 不写 cegr.observation |
| 不宣布 PASS | ✓ M2 / Gate / O1 PASS 维持 OPEN |
| 不让用户登录提供镜像源 | ✓ 637 推荐路径 C，避开需用户提供源的 A/B 路径 |

— End 637 tasking —