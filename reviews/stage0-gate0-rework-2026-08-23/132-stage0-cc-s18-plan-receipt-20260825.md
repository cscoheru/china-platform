# 132 — Stage 0 / CC / S1.18 Plan Receipt

**Tasking**: Cursor 131 §NOW（规划 `docs/33`；回执 `132` 进 `reviews/`）
**Date (UTC)**: 2026-08-25
**Commit (origin)**: e3c684e
**Branch**: main

---

## §NOW items completed (tasking 131)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 131-1 | 起草 `docs/33-stage1-s18-demo-sha-lock-plan-20260825.md`（CC 拥有） | ✅ | e3c684e — `docs/33` 304 行 |
| 131-2 | 须覆盖四要点 | ✅ | 见 §1-4 摘要 |
| 131-3 | 规划 only；回执 `132` 进 reviews/ | ✅ | 本文件路径 `reviews/stage0-gate0-rework-2026-08-23/` |
| 131-4 | → `84` POLL | ✅ | job 50a7c596 持续武装（session-only） |

---

## §1 — Plan §1-4 覆盖矩阵

| 任务书 131 §NOW-2 要求 | docs/33 §-章节 |
|---|---|
| 现有 `data/seeds/jiangsu_gdp_*` / `seed_jiangsu_gdp_demo.py` 现状 | §1.1（文件 + 库函数；UNVERIFIED + 全零 SHA + DEMO caveat 已存在） |
| SHA-256 锁定路径选项（本地已有 XLSX/PDF vs 仍标 DEMO；**不爬网**） | §2.1-2.4 三路径（路径 A 胜出：JSONB is_demo + mart 过滤；路径 B 计算式 sentinel / 路径 C 物理隔离均评估后否决） |
| 与 S1.12 Gate prep pack / API 演示脚本的衔接 | §3.5（`docs/27` §2.4 增量更新点；loader `--status` 输出扩展；mart 主查询仍保留 `is_demo` 列供 Stage 2 替换时筛出 DEMO） |
| 空样本 / 无法取得真实文件时的诚实失败策略（不伪造 SHA） | §4 三态表 + fail-closed 4 规则 + §8 §S1.18-1 仍 OPEN |

---

## §2 — 关键设计决策

### 2.1 路径 A 的实施要点

1. **`lineage` JSONB 加 `is_demo=true` + `demo_reason` + `demo_sentinel_sha256` 注释字段**：`file_hash_sha256` 仍为全零（不动 schema / 不破坏 124 行引用）；5 行 observation 的 `lineage` 同步加标记。
2. **dbt mart `mart_source_disagreement` 加 `is_demo` 列 + `WHERE NOT is_demo` 过滤**：DEMO 行不参与跨源冲突候选池，但**保留**在 mart 主查询 SELECT 中供 Stage 2 替换时筛出清理。
3. **`tests/test_demo_sha_sentinel.py` 6 用例**：seed JSON 形态 / observation lineage 透传 / UNVERIFIED 状态 / mart 过滤 / unload 清理 / S1.8 回归不动。
4. **不 migration**：纯 JSONB 字段 + 一处 dbt CTE 过滤 + 一组 pytest。

### 2.2 真实样本路径前置条件（Stage 2）

- `scripts/compute_file_sha.py` + `scripts/replace_demo_with_real.py`：规划但不交付（S1.18 实施刀不交付；待 Stage 2 S1.17 admin/upload 通路接通后另开 §1.19 / §1.20）。
- 触发条件：人工上传真实 Jiangsu 年鉴 XLSX → 算 SHA → 替换 demo UNVERIFIED → `verification_status` UNVERIFIED → PENDING → VERIFIED。

### 2.3 §4 三态诚实表

| 状态 | `file_hash_sha256` | `verification_status` | `lineage.is_demo` | 下游 |
|---|---|---|---|---|
| REAL VERIFIED | 真 SHA-256 | VERIFIED | NULL/false | 正常路径 |
| REAL PENDING | 真 SHA-256 | PENDING | NULL/false | 监控告警；不参与跨源 |
| DEMO | `00…00` | UNVERIFIED | `true` | `WHERE NOT is_demo` 过滤；监控旁路 |

fail-closed：DEMO 与真实样本走同一 `cegr.source_document` 表；下游通过 `is_demo` 字段与 `verification_status` 双重信号识别。

### 2.4 §8 诚实缺口

- §S1.18-1：真实 SHA-locked XLSX/PDF 仍未到位（本地零文件；Stage 2 admin/upload 接通后人工上传替换） — **OPEN**
- §S1.18-2：`compute_file_sha.py` / `replace_demo_with_real.py` CLI 未交付 — **OPEN**
- §S1.18-3：`docs/27` §2.4 增量更新由 Cursor 拥有 — **OPEN**（依赖 Cursor S1.18 PASS 后增量）
- §S1.18-4：路径 B 计算式 sentinel 远期清理 — 候选（非阻塞）

---

## §3 — Red-line compliance

- ❌ 未宣布 Stage 0 / Gate 1 PASS
- ❌ 未批量 2020-2025
- ❌ 未 HTTP 爬源站（江苏统计局站点等真实源站不爬；真实样本路径仅消费本地或人工上传文件）
- ❌ 未降 OCR 门槛（S1.18 不涉及 OCR）
- ❌ 未把 1909 代表中国 / 未把陕西标为门控
- ❌ 未擅自 `--force` / `--force-with-lease`
- ❌ 未替用户下裁定
- ❌ 未在聊天复述 Cursor 长文；未索要 PAT
- ❌ 未修改 `gate_thresholds.json`
- ❌ 未伪造 SHA（路径 A 全零 + is_demo 双重信号；路径 B/C 已否决）
- ❌ Cursor 不写 `docs/33` 正文
- ❌ 未替 demo 伪造 `verification_status='VERIFIED'`
- ❌ 未碰 `00-CC-CURRENT.md`（Cursor 拥有）

---

## §4 — Push confirmation

```
$ git push origin HEAD         # e3c684e
To https://origin.cursor.com/lyliae/china-platform.git
   26f693f..e3c684e  HEAD -> main

$ git push github HEAD         # 双推（github 20s/45s/90s backoff 重试）
```

---

## §5 — Pack invariant

```
artifact_count = 502  (S1.18 规划不新增 artifact；纯 docs/)
sum(role_count) = 502 ✓
```

Delta: 0（纯 docs/ 增量；§3.4 evidence_pack +1 待实现刀交付，本刀不动）。

---

## §6 — Next heartbeat

84 while-POLL 持续武装（session-only, 180s, job 50a7c596）。等待 Cursor 对 S1.18 规划的审验（预期 queue_rev 45+ → audit `133-stage0-cursor-s18-plan-audit-PASS-20260825.md`）。

— CC @ queue_rev 45, S1.18 规划已交付 —
