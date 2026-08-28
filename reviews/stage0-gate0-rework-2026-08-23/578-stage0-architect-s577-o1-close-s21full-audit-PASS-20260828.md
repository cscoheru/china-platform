# 578 — 架构师审计：回执 577（O1 CLOSED (as-scoped) 裁定登记 + S2.1-full dbt 层合刀）· PASS

- 编号：`578-stage0-architect-s577-o1-close-s21full-audit-PASS-20260828`
- 审计对象：`577-stage0-cc-o1-close-person-tenure-full-receipt-20260828`（交付 `c8e2b9a` + backfill `7c9668e`）
- 对照任务书：`577-stage2-o1-close-person-tenure-full-tasking-20260828`
- 审计者：CC 架构师终端（只读核验 + 本地 DB 动态复跑，不改实现、不 commit）
- 日期：2026-08-28
- 裁定：**PASS**（§NOW A–H 全达成；两处任务书侧偏差 ACCEPTED（责任在任务书标注，执行端处置正确且显著披露）；红线零违反）

## 审计证据（2026-08-28T22:3x+08:00 实测，原样粘贴）

```
=== A. 双推收敛 ===
HEAD = origin/main = github/main = 7c9668e          ✅（交付 c8e2b9a + backfill 7c9668e 严格顺序）
=== B. 交付 commit 清单（c8e2b9a）===
22 files changed, +4481/−13 — docs/45/50/53 + manifest + seed JSON(2779 行增量)
+ loader + 6 stg + 2 yml + mart + 新 pytest + bump + 575 审计 + 任务书 + 回执
+ 00-EXEC-QUEUE.md + exec_wake.sh                                   ✅（H 项）
=== C. 受保护文件漂移（d95d21e→HEAD，git diff --name-only）===
registry.csv / spikes/04-scanned-pdf/gate_thresholds.json / 00-CC-CURRENT.md /
4×public_extract_*.json / mart_city_evidence_chain.sql /
mart_city_seven_dim_overview.sql / schema/（migration 001–013）→
（空 = 零漂移）                                                       ✅
=== C2. 既有测试零改动声明复核 ===
tests/test_person_tenure_s21lite.py / test_mart_city_dbt_skel_s27bf.py →（空）✅
=== D. 「O1 仍 OPEN」计数器（非减 ✓ 且增长） ===
docs/45: 166（≥164）  docs/50: 27（≥25）  docs/53: 24（≥23）          ✅
=== E. 4 fixture 锁值 ===
e30ee811 9232efdb 937255a5 9056001c                                  ✅
=== F. manifest 不变量 ===
904 904 904                                                          ✅（889 + 15）
=== G. 单槽单回执 ===
577-stage0-cc-…-receipt 恰 1 个                                       ✅
=== H. docs 锚点 ===
docs/53「第 40 项（此条）」=1 · 含「O1 CLOSED (as-scoped)」=1          ✅（NOW-A）
docs/45 §7「904 == 904 == 904」=1 · stale「889 == 889 == 889」=0      ✅（NOW-A/F）
docs/50「→ `574` → `577`」=1（链尾以 577 收口）                       ✅（NOW-A）
=== I. seed 卫生（python3 实测 data/seeds/person_tenure_demo.json）===
行数 30 person / 30 alias / 20 position / 60 tenure / 60 appointment_events
/ 60 evidences = 260；顶层 lineage.is_demo='true' + source_file_sha256='0'*64；
sentinel url (DEMO_SEED_NO_FILE_PERSON_TENURE) 在位；lite probe UUID（…04f–…05a）
零泄漏；30 个姓名全部「演示」前缀（无真实姓名）                        ✅（NOW-B）
=== J. mart/stg 禁词与结构（剥注释实扫）===
mart_person_tenure.sql：score/rating/rank 全 CLEAN；`is_demo` 实文确认为
末投影列（`END AS is_demo`，行 48）；投影用 `pos.level` 刻意排除
`rank_level`；materialized='view'；JOIN 结构 = tenure⨝person⨝position +
LEFT JOIN geo_entity/appointment_event/source_document                ✅（NOW-D）
6×stg_*.sql：score/rating CLEAN                                       ✅（NOW-C）
=== K. 动态复跑（DB 55440 accepting）===
python3 -m pytest tests/test_person_tenure_s21_full.py
  tests/test_person_tenure_s21lite.py tests/test_mart_city_dbt_skel_s27bf.py -q
→ 36 passed in 4.38s / EXIT=0（6 新 + 5 lite + 25 s27bf）             ✅（NOW-E/G）
python3 frontend/smoke-check.py → PASS / EXIT=0                      ✅（NOW-G）
```

## 偏差裁定（两处，均 ACCEPTED · 责任在任务书侧）

| # | 内容 | 架构师裁定 |
|---|---|---|
| ⚠1 | 任务书 §F 标注「+14 → 903」，但实列 15 项（1+1+6+1+1+1+1+1+1+1）| **任务书算术标注错误**（架构师侧）；§F 枚举清单 + §A「§7 链头按 bump 实际值」为授权依据；执行端按 15 项实收 → 904 并于回执文首显著披露 — 处置正确。**904 为权威值**，本审计实测 `904 904 904` 印证 |
| ⚠2 | 任务书 §G dbt 字面命令缺 `--project-dir dbt`，且 `stg_person+` 为下游选择器（冷图首跑必 ERROR）| **任务书命令书写缺陷**（架构师侧）；执行端冷建改用 `+mart_person_tenure`（5 模型 exit 0）、暖图复跑字面命令（exit 0）、孤立 2 stg 单独实跑（exit 0），三段输出原样粘贴 — 处置正确且透明 |

## 继承问题登记（非本刀引入，随本审计建档）

全量套件 **4 failed, 556 passed, 8 skipped**（13 分钟实测档，回执证据段）——执行端逐项归因并 git 实证**全部先于本刀存在于 HEAD `d95d21e` 提交态**：

1. `test_auto_ingest_public_source_s52` + `test_public_extract_frontend_fixture`（2 例）：`spikes/01-national-yearbook/sample.html` 磁盘 SHA（dea13b8a…）≠ registry 行 SHA（a7e4029d…，`538` 裁定值）— 提交态漂移；registry.csv 红线不可动，**留架构师登记**
2. `test_cleanliness::data_dir` 白名单：`{'seed_archives','seeds','public_extracts','public_archives'}` 均先于本刀存在
3. h2 嵌套复跑 rc=1（内含上述）

处置：**交下一刀（579）在 docs 登记归因与处置选项**（改 sample 字节对齐 registry / 或 registry 加注 spike 样例非同一文件 — 届时按红线路径裁定）；本审计不修改任何实现。

## 红线自查（审计侧）

- ✅ O1 CLOSED (as-scoped) 登记未越界：docs 三处 + 回执均写明「≠ Gate 2 PASS ≠ Stage 2 收口」；逐城真实源入仓 OPEN 保留（`576` 号位）；「O1 仍 OPEN」历史行零删除（166/27/24 只增）
- ✅ seed 零真实姓名/日期/SHA；未爬网；未加 EXCLUDE；migration 001–013 零触碰
- ✅ registry / thresholds / CURRENT / 4 fixture / `mart_city_evidence_chain.sql` 零触碰（C 项空 diff + E 项锁值）
- ✅ 无 --force / PAT / 公网 redeploy；合刀单槽单回执；回执位于 `reviews/stage0-gate0-rework-2026-08-23/`
- ✅ 全量 4 failed 如实归因非静默失败（继承问题单列登记）

## 后续

- 本审计文件（578）不单独 commit，随下一刀交付 commit 入库（manifest `documentation` +1，届时 bump 按实际值）
- 队列 `00-EXEC-QUEUE.md` status → **AUDITED**（架构师写；改动随 579 交付入库）
- 下一刀：**`579` — O3 决策备忘刀**（O3 引擎方案呈现供用户裁定 + 全量 4 failed 继承问题 docs 登记），任务书另发
