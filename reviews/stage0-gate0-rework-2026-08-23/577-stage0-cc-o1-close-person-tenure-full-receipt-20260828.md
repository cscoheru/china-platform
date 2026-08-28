# 577 — 合刀：O1 CLOSED (as-scoped) 裁定登记 + S2.1-full dbt 层 · CC 回执

- 编号：`577-stage0-cc-o1-close-person-tenure-full-receipt-20260828`
- 任务书：`577-stage2-o1-close-person-tenure-full-tasking-20260828`（架构师治理模型第二刀，经 `00-EXEC-QUEUE.md` 签发：PENDING → ACK → DELIVERED；`00-CC-CURRENT.md` 维持冻结勿读勿写；前置 `575` 审计 PASS；合刀 A–H 同 commit、单槽单回执）
- 前置：`575-stage0-architect-s574-docs-closeout-audit-PASS-20260828`（574 docs 收口审计 PASS；本审计文件随本刀交付 commit 入库、只读未改）；**用户裁定 2026-08-28：O1 CLOSED (as-scoped)**（本刀登记该裁定并解锁 S2.1-full；**O1 CLOSED (as-scoped) ≠ Gate 2 PASS ≠ Stage 2 收口**）
- 作者：CC（执行端 Claude Code 终端）
- cc_head：见文末「下一步」（双推后回填）
- 日期：2026-08-28

---

## ⚠ 两处任务书内不一致的处理（显著披露）

1. **§F 计数**：任务书写「NEW +14 → 889 → 903」，但 §F 实列 **15 项**（seed JSON + seed loader + 6 stg + mart + 新 pytest + bump 脚本 + `577` 回执 + `575` 审计文件 + `00-EXEC-QUEUE.md` + `exec_wake.sh` = 1+1+6+1+1+1+1+1+1+1 = **15**），且实测 15 个路径全部不在 manifest（NONE）。§A 明文授权「§7 链头 `903 == 903 == 903`（**按 bump 实际值**）」→ 本刀按实际值 **889 + 15 = 904** 收口，docs/45 §7 链头写 `904 == 904 == 904`，bump 断言强制 904。
2. **§G dbt 命令**：字面命令 `.venv-dbt/bin/dbt run --profiles-dir dbt --select stg_person+ mart_person_tenure` 有两处与 dbt 1.12 实际行为不符：(a) 仓库根目录调用缺 `--project-dir dbt`（否则 `No dbt_project.yml found`）；(b) 选择器 `stg_person+` 是**下游**语义（= {stg_person, mart_person_tenure}），**不含** mart 的其余上游（stg_tenure / stg_position / stg_appointment_event）→ 冷图（conftest 每次 session `DROP SCHEMA cegr CASCADE` 连带清掉 cegr_staging 视图后）首跑该命令必然 ERROR（`relation "cegr_staging.stg_tenure" does not exist`，实测 TOTAL=2 PASS=1 ERROR=1）。处理：冷建用 `+mart_person_tenure`（= 5 模型：mart + 其 4 个被引用上游，exit 0）；再跑任务书字面命令（暖图，exit 0，TOTAL=2）；未被 mart 引用的 `stg_person_name_alias` / `stg_person_source_evidence` 单独 `--select` 实跑（exit 0，TOTAL=2）。测试文件内 dbt 调用用 `+mart_person_tenure` + `--project-dir dbt`。三段输出均原样粘贴于证据段。

## §NOW 对照

| 577 tasking §NOW | 交付 | 证据 |
|---|---|---|
| Phase 0 本地 DB 起库 | ✅ pg_isready 55440 accepting（`postgresql.conf` `port = 55440` + `brew services restart postgresql@17`；postgres 角色 + cegr_test 库新建）；lite 套件 5 passed / exit 0 证 conftest 链式 apply（DROP + 01-core + 001–013）；dbt 全程 `.venv-dbt/bin/dbt`（1.12.3，禁系统 python3 3.14）| 会话记录 |
| (A) O1 裁定登记 docs 三件套 | ✅ docs/53 §5 **第 40 项**（O1 CLOSED (as-scoped)；用户裁定 2026-08-28；收口域 = NATIONAL_BULLETIN → nanjing CONDITION 真 SHA 端到端 `538`→`560`→`572`→`573` 审计 PASS；59 行 = 已登记缺口（第 39 项）；逐城真实源入仓保持 OPEN（号位 `576` 保留）；「O1 仍 OPEN」历史行不删、裁定行追加其后）；docs/50 §4.4 +1 第 40 项行 + intro 链 `→ 574` 续接 `→ 577`（链尾以 `577` 收口）；docs/45 文首刷新行 + §1 新段 + §6.2 行尾注 + §7 链头 `904 == 904 == 904` + knife 574 demote | grep（证据段锚点表）|
| (B) demo seed | ✅ `data/seeds/person_tenure_demo.json`：30 person / 30 alias / 20 position / 60 tenure / 60 appointment_event / 60 person_source_evidence = 260 行 + 2 source 父行，全 demo（`lineage.is_demo='true'` / `source_file_sha256='0'*64` / `source_file_url='(DEMO_SEED_NO_FILE)'`）；稳定 UUID（`a0000000-…-` 族分段：person=70xx / alias=71xx / position=72xx / tenure=73xx / appt=74xx / evidence=75xx / 父行 7f0+7f1），无真实姓名（演示人员NN）/无真实日期（合成 2018–2024 窗口）/无真实 SHA；`scripts/seed_person_tenure_demo.py`：load/status/unload、全 `ON CONFLICT (id) DO NOTHING`、unload = TRUNCATE 六表 CASCADE、loader 内置 lite probe UUID 硬守门（撞库即 abort）；**不复用 lite probe UUID（…04f–…05a）经 pytest 静态断言 + loader 守门双重验证**。⚠ 修复记录：初版 registry `primary_url='(DEMO_SEED_NO_FILE)'` 与 lite probe 同值触发 `idx_source_registry_url` UNIQUE（全量序中 lite 后跑时炸），已改 `(DEMO_SEED_NO_FILE_PERSON_TENURE)` 独立 sentinel（source_document.url 仍为任务书 sentinel、无 UNIQUE 约束），修复后 lite 双测复绿 | pytest（证据段）|
| (C) 6 staging 模型 + 2 yml | ✅ `stg_person` / `stg_person_name_alias` / `stg_position` / `stg_tenure` / `stg_appointment_event` / `stg_person_source_evidence`（镜像 `stg_observation.sql`：`materialized='view'` + tags；id → *_id 改名）；`_stg_sources.yml` +7 条目（6 person 域 + 补 `geo_entity`——mart LEFT JOIN 需要而源文件此前未登记，dbt 编译实测报缺后补）；`_stg_models.yml` +6 模型条目（PK unique + 核心列 not_null）| dbt run exit 0 ×3（证据段）|
| (D) `mart_person_tenure.sql` | ✅ view；`stg_tenure ⨝ stg_person ⨝ stg_position` + `LEFT JOIN geo_entity / stg_appointment_event` + `LEFT JOIN source_document`（is_demo 推导源）；**`is_demo` 显式末列**（'true'/'false' 字符串 sentinel per docs/33 §3.2；从 source_document `caveat_text LIKE '%DEMO_SEED%' OR url='(DEMO_SEED_NO_FILE)'` 推导——tenure 无行级 JSONB lineage 列且 migration 001–013 冻结，与 loader `--status` 同规则）；禁词 score 族零出现（**mart 投影刻意不含 `rank_level`**——该词元含禁词子串，作为过滤维度留在 `stg_position`，docs/36 §2.3 本就钉死其非能力分）；pytest 列序断言 is_demo == 最后一列 | pytest（证据段）|
| (E) 新 pytest | ✅ `tests/test_person_tenure_s21_full.py` 6 例全绿：① 六表行数（30/30/20/60/60/60，任务书 5 表上限以精确计数满足）② 二次 load 幂等 ③ seed UUID 与 lite probe 不相交 ④ mart 列存在 + is_demo 末列 + 'true'=60 行 / 'false'=0 行（dbt 实跑）⑤ overlap-positive 探针（同 person 同 position 重叠双 tenure 可插 + 重叠数学断言 + 清理）⑥ 禁词扫描（剥注释后子串扫描 7 词元）；**未修改** `test_person_tenure_s21lite.py` / `test_mart_city_dbt_skel_s27bf.py`（字节零改动）| pytest（证据段）|
| (F) manifest bump | ✅ `scripts/_knife577_manifest_bump.py`：NEW **+15** → **889 → 904**（计数披露见文首 ⚠1）；REFRESH docs/45 / docs/53（不增计数）；docs/50 房规 SKIP（镜像 574 先例）；回执二次执行 REFRESH 至最终态；断言 `sum(role_count) == artifact_count == len(artifacts) == 904` | bump 输出（证据段）|
| (G) 核验 | ✅ dbt 三段 exit 0；新 pytest 6 passed / exit 0；回归 30 passed / exit 0（另 lite 单独 5 passed / exit 0）；smoke PASS / exit 0；全量 `tail -3` = **4 failed, 556 passed, 8 skipped**（4 个失败全部先于本刀存在：sample.html 磁盘 SHA 漂移 + data/ 目录白名单，git 实证两文件均匹配 HEAD，详见证据段）；计数器 docs/45 = 166（≥164）/ docs/50 = 27（≥25）/ docs/53 = 24（≥23）；4 fixture 锁值不变；manifest 904 904 904 | 证据段（命令 + 输出原样粘贴）|
| (H) 回执 + 交付 commit | ✅ 本文件名含 `-cc-`；合刀单槽单回执仅 `577`；交付 commit 含 docs/45/50/53、seed JSON + loader、6 stg + 2 yml、mart、新 pytest、bump 脚本、`575` 审计文件（只读）、本任务书（只读）、本回执、`00-EXEC-QUEUE.md`（ACK 已填 + status→DELIVERED）、`exec_wake.sh`、manifest.json | git（会话记录）|

## 证据（命令 + 输出原样粘贴）

```
$ .venv-dbt/bin/dbt run --project-dir dbt --profiles-dir dbt --select +mart_person_tenure   # 冷建（conftest DROP 后）
  Done. PASS=5 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=5      EXIT=0
  （mart + 4 个被引用上游 stg_tenure/stg_person/stg_position/stg_appointment_event；
    stg_person_name_alias / stg_person_source_evidence 不被 mart 引用，单独跑↓）

$ .venv-dbt/bin/dbt run --project-dir dbt --profiles-dir dbt --select stg_person+ mart_person_tenure   # 任务书 §G 字面命令（暖图重跑）
  Done. PASS=2 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=2      EXIT=0
  （选择器语义 + --project-dir 披露见文首 ⚠2；冷图首跑该命令实测 ERROR=1（stg_tenure 缺失），暖图 exit 0）

$ .venv-dbt/bin/dbt run --project-dir dbt --profiles-dir dbt --select stg_person_name_alias stg_person_source_evidence
  Done. PASS=2 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=2      EXIT=0

$ python3 -m pytest tests/test_person_tenure_s21_full.py -q
......                                                                   [100%]
6 passed in 4.59s                                                  EXIT=0

$ python3 -m pytest tests/test_person_tenure_s21lite.py tests/test_mart_city_dbt_skel_s27bf.py -q
..............................                                          [100%]
30 passed in 0.87s                                                 EXIT=0

$ python3 -m pytest tests/test_person_tenure_s21lite.py -q
.....                                                                   [100%]
5 passed in 0.85s                                                  EXIT=0

$ python3 frontend/smoke-check.py
=== S2.0.1 + S2.7-a + S2.7-a2 + S2.7-b-lite + S2.7-b-full-lite mart-shape + home nav (S2.7-a + S2.7-b + S2.8-lite + S2.9-lite, per tasking 280) smoke: PASS ===
                                                                   EXIT=0

$ python3 -m pytest tests/ -q 2>&1 | tail -3
FAILED tests/test_cleanliness.py::test_suite_leaves_no_worktree_trace_h2 - As...
FAILED tests/test_public_extract_frontend_fixture.py::test_fixture_provenance_sha_matches_registry
4 failed, 556 passed, 8 skipped in 782.43s (0:13:02)
  （4 failed 全部先于本刀存在于 HEAD：① test_auto_ingest_public_source_s52::test_regression_real_extracts_
    not_clobbered_by_pytest + ② test_public_extract_frontend_fixture::test_fixture_provenance_sha_matches_
    registry = spikes/01-national-yearbook/sample.html 磁盘 SHA dea13b8a… ≠ registry a7e4029d…（git status 实证
    sample.html 与 4 fixture 均匹配 HEAD d95d21e——漂移是提交态，非本刀工作区改动；registry.csv 红线不可动，
    留给架构师登记）；③ test_cleanliness::test_data_dir_has_only_gitkeep_or_known_subdirs = data/ 目录级白名单
    （意外集 {'seed_archives','seeds','public_extracts','public_archives'} 全部先于本刀存在——seeds/ 自江苏
    seed 刀即有）；④ h2 = 嵌套整套复跑 rc=1（内含 ①②③）。本刀修复对照：修复前全量 6 failed（含本刀曾引入的
    lite 2 失败——registry url UNIQUE 冲突，见 ⚠/§B），修 sentinel 后清零）

$ grep -o "O1 仍 OPEN" docs/45-*.md | wc -l        → 166   （基线 164，非减 ✅）
$ grep -o "O1 仍 OPEN" docs/50-*.md | wc -l        → 27    （基线 25，非减 ✅）
$ grep -o "O1 仍 OPEN" docs/53-*.md | wc -l        → 24    （基线 23，非减 ✅）

$ shasum -a 256 frontend/lib/public_extract_{nbs,nbs_live_candidate,sz,hubei}.json | cut -c1-8
e30ee811 / 9232efdb / 937255a5 / 9056001c   （disk == 锁值，4 fixture 字节未动）

$ python3 -c "import json;m=json.load(open('evidence_pack/manifest.json'));print(len(m['artifacts']),m['artifact_count'],sum(m['role_count'].values()))"
（bump 前）889 889 889 →（bump 后）904 904 904
```

### 文档锚点 + 计数

```
docs/53:「第 40 项（此条）· O1 CLOSED (as-scoped) 裁定登记」                     = 1
docs/50:「docs/53 §5 第 40 项 O1 CLOSED (as-scoped) 裁定登记」（里程碑行）        = 1
docs/50 intro:「→ `574` → `577`」                                                = 1
docs/50 intro:「链尾以 `577` 收口」                                               = 1
docs/45 文首:「架构师治理模型第二刀 + 新调度模型（per `577-…tasking`」            = 1
docs/45 §1:「O1 CLOSED (as-scoped) 裁定登记 + S2.1-full 实装（per `577`」         = 1
docs/45 §6.2 行尾注:「（合刀 per `577`」                                          = 1
docs/45 §7:「904 == 904 == 904」                                                  = 1
docs/45 §7 knife 574 demote:「前置 knife 574 = 合刀 A–F…」                        = 1
docs/45 stale「889 == 889 == 889」                                                = 0  （已由 §7 链头更新承接）
「O1 CLOSED (as-scoped)」出现：docs/45 = 9 / docs/50 = 6 / docs/53 = 3
既有「O1 仍 OPEN」历史行未删除（计数器只增不减：164→166 / 25→27 / 23→24）
00-EXEC-QUEUE.md（1688B）/ 575 审计文件（2938B）/ exec_wake.sh（2023B）在位待入库
```

```
$ python3 scripts/_knife577_manifest_bump.py（首跑）
ADD: data/seeds/person_tenure_demo.json (107604 bytes, sha=4afb8f09)
ADD: scripts/seed_person_tenure_demo.py (13203 bytes, sha=199312c4)
ADD: dbt/models/staging/stg_person.sql (473 bytes, sha=540869b6)
ADD: dbt/models/staging/stg_person_name_alias.sql (433 bytes, sha=3363672c)
ADD: dbt/models/staging/stg_position.sql (600 bytes, sha=f313121c)
ADD: dbt/models/staging/stg_tenure.sql (612 bytes, sha=d198755e)
ADD: dbt/models/staging/stg_appointment_event.sql (545 bytes, sha=493f743d)
ADD: dbt/models/staging/stg_person_source_evidence.sql (469 bytes, sha=2c2b6bef)
ADD: dbt/models/marts/mart_person_tenure.sql (2116 bytes, sha=3ee811a9)
ADD: tests/test_person_tenure_s21_full.py (12030 bytes, sha=e714cd11)
ADD: scripts/_knife577_manifest_bump.py (7500 bytes, sha=089cea7c)
ADD: reviews/stage0-gate0-rework-2026-08-23/577-stage0-cc-o1-close-person-tenure-full-receipt-20260828.md (19380 bytes, sha=66aecfb8)
ADD: reviews/stage0-gate0-rework-2026-08-23/575-stage0-architect-s574-docs-closeout-audit-PASS-20260828.md (2938 bytes, sha=f401a3ad)
ADD: reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md (1688 bytes, sha=884c8dfc)
ADD: scripts/exec_wake.sh (2023 bytes, sha=0149f533)
REFRESH: docs/45-stage2-s210-lite-gate2-review-index-20260826.md sha=ec66678c → 50076666 (267111 bytes; no count change)
NOT-IN-MANIFEST (房规 skip, no count change): docs/50-stage2-gate2-review-packet-draft-20260826.md
REFRESH: docs/53-stage2-public-ingest-ops-handbook-20260826.md sha=893ecd28 → 0aee13d8 (62054 bytes; no count change)
REFRESH (unchanged): reviews/stage0-gate0-rework-2026-08-23/577-stage0-cc-o1-close-person-tenure-full-receipt-20260828.md sha=66aecfb8
UPDATE artifact_count: 889 → 904
INVARIANT: sum(role_count)=904 == artifact_count=904 == len(artifacts)=904
OK manifest updated; added 15 artifacts

$ python3 scripts/_knife577_manifest_bump.py（末次：回执粘贴首跑输出后运行）
（+15 条目已在位 → SKIP；REFRESH 本回执 SHA → 本文件最终字节；docs/45/53 unchanged；
 INVARIANT 904 == 904 == 904 —— manifest 中本回执条目 SHA 即本文件最终态；此后本文件不再
 变更（cc_head backfill 为独立 commit，房规允许））
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | MODIFIED（§5 新增第 40 项 O1 CLOSED (as-scoped) 裁定登记 blockquote；第 21–39 项既有正文原样未动）| 已入 manifest（SHA REFRESH 不增计数）|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | MODIFIED（§4.4 +1 第 40 项裁定行 + intro 链尾续接 `→ 577`；第 21–39 项行既有正文原样未动）| **房规未入 manifest**（镜像 docs/52 先例；显式 SKIP 不增计数）|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | MODIFIED（文首 +1 刷新行 + §1 +1 段 + §6.2 行尾注 append + §7 链头 904 + knife 574 demote）| 已入 manifest（SHA REFRESH 不增计数）|
| `data/seeds/person_tenure_demo.json` | NEW（S2.1-full demo seed，260 行 + 2 父行，全 demo）| `data_contract_suite` |
| `scripts/seed_person_tenure_demo.py` | NEW（load/status/unload loader + lite probe UUID 硬守门）| `spike_helper` |
| `dbt/models/staging/stg_person.sql` 他 5 个 | NEW ×6（view，镜像 stg_observation 形态）| `spike_helper` |
| `dbt/models/staging/_stg_sources.yml` / `_stg_models.yml` | MODIFIED（+7 source 条目含 geo_entity 补登；+6 model 条目）| 未入 manifest（yml 房规，与既有 stg yml/SQL 先例一致——实测 `_stg_sources.yml`/`stg_observation.sql` 均不在 manifest）|
| `dbt/models/marts/mart_person_tenure.sql` | NEW（view，is_demo 显式末列；禁词零出现）| `spike_helper` |
| `tests/test_person_tenure_s21_full.py` | NEW（6 例 DB-backed）| `schema_negative_test` |
| `scripts/_knife577_manifest_bump.py` | NEW（本刀 bump 脚本：ADD +15 + REFRESH + 904 断言）| `spike_helper` |
| `reviews/.../575-stage0-architect-s574-docs-closeout-audit-PASS-20260828.md` | NEW（架构师资产，**只读随刀入库、内容零改动**）| `documentation` |
| `reviews/.../577-stage2-o1-close-person-tenure-full-tasking-20260828.md` | NEW（架构师任务书，**只读随刀入库**）| 未入 manifest（任务书按先例不计数；574 先例一致）|
| `reviews/.../577-stage0-cc-o1-close-person-tenure-full-receipt-20260828.md` | NEW（本文件）| `documentation` |
| `reviews/.../00-EXEC-QUEUE.md` | NEW（治理调度队列；本刀 §ACK 已填 + status→DELIVERED）| `documentation` |
| `scripts/exec_wake.sh` | NEW（macOS 唤醒脚本，只读随刀入库）| `spike_helper` |
| `evidence_pack/manifest.json` | MODIFIED（bump 产物：ADD +15 → 904；REFRESH docs/45 + docs/53 + 本回执最终态）| manifest 本体 |

注：本刀零 SQL 改动（migration 001–013 与 `mart_city_evidence_chain.sql` / `mart_city_seven_dim_overview.sql` 零触碰，仅新增 dbt view 文件）；registry.csv / gate_thresholds.json / `00-CC-CURRENT.md`（勿读勿写）/ 4 fixture 字节零触碰；无 EXCLUDE 约束新增；无爬网；未跟踪运行产物维持不入 manifest 房规。

## Pack 不变量

`_knife577_manifest_bump.py`：NEW_ARTIFACTS **+15** → **889 → 904**（任务书 §F 标注 +14→903 与实列 15 项不符，per §A「按 bump 实际值」以 904 收口，显著披露于本回执文首 ⚠1 + bump 脚本 docstring + 断言信息）；断言 `sum(role_count) == artifact_count == len(artifacts) == 904`（脚本内强制 + §G 实测 `904 904 904`）；docs/45 / docs/53 已入 manifest 文件 SHA REFRESH 不增计数；docs/50 房规未入 manifest（镜像 docs/52 / 574 先例）→ 显式 SKIP；yml 文件未入 manifest（实测既有 stg yml/SQL 同不入，房规一致）；本回执条目 SHA 经 bump 二次执行 REFRESH 至粘贴输出后的最终态。前置链条：knife 574 已落 886 → 889；knife 572 已落 884 → 886（此前链条见 574 回执 §Pack 不变量，原样承接不再复述）。

## 红线自查

- ❌ 未宣布 Gate 0/1/2 PASS：**O1 CLOSED (as-scoped) ≠ Gate 2 PASS ≠ Stage 2 收口**；逐城真实源入仓 OPEN 保留（号位 `576`）；docs/53 第 40 项 + docs/50 第 40 行/intro + docs/45 五处 + 本回执写明
- ❌ seed 无真实姓名（演示人员NN）/无真实日期（合成窗口）/无真实 SHA（`0*64`）；未爬网；未加 EXCLUDE 约束；migration 001–013 零改动（pytest 全量实证）
- ❌ 禁词词元（score 族）零出现于 mart（pytest 剥注释子串扫描 + mart 投影刻意排除 `rank_level`）；mart 未接 S2.7-b UI（前端零改动，smoke PASS 防回归）
- ❌ 未动 registry.csv / gate_thresholds.json / `00-CC-CURRENT.md`（勿读勿写）/ 4 fixture 字节（实测锁值 e30ee811 / 9232efdb / 937255a5 / 9056001c）/ `mart_city_evidence_chain.sql`
- ❌ 无 --force / PAT / 公网 redeploy；既有「O1 仍 OPEN」历史行不删（计数器 164→166 / 25→27 / 23→24 只增）
- ❌ 未谎称收口、未静默失败：全量 4 failed 如实记录并归因（全部先于本刀，git 实证匹配 HEAD）；本刀自引入问题（registry url UNIQUE 冲突）主动修复 + 披露修复对照
- ✅ manifest 889 → 904 不变量（实际值口径，显著披露）；回执位于 `reviews/stage0-gate0-rework-2026-08-23/`；文件名含 `-cc-`；合刀单槽单回执仅 `577`
- ✅ 不复述架构师长文（仅引用任务书/审计号 + 简短语）

## 下一步

`git push origin HEAD && git push github HEAD`（**必须双推、严格顺序** per tasking）→ 回填 cc_head（单独 commit，勿 amend，再双推）→ queue status → DELIVERED（已随本刀 commit）→ **停止并回报 cc_head**。架构师将出 `578` 号位审计，随后发放 O3 决策备忘刀（`579`）。
