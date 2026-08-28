# 577 — 任务书：O1 裁定登记 + S2.1-full dbt 层（合刀 · 需本地 DB）

- 编号：`577-stage2-o1-close-person-tenure-full-tasking-20260828`
- 前置：`575` 审计 PASS（574 docs 收口）；**用户裁定（2026-08-28）：O1 CLOSED (as-scoped)** — 本刀将该裁定登记入 docs，并解锁 S2.1-full
- 下发：CC 架构师终端；执行端：Claude Code 执行终端
- 日期：2026-08-28
- 验证深度：**需本地 DB**（dbt 实跑 + DB-backed pytest）；其余核验零网络
- 号位注：`576` 保留给未来「逐城真实源入仓」刀（本裁定路线不启用），链条缺口为有意登记

---

## Phase 0 — 本地 DB 起库（前置闸门）

1. `pg_isready -h 127.0.0.1 -p 55440`；无响应则启动 Homebrew postgresql（`brew services start postgresql@17` 或 `@16`，以 `brew list | grep postgres` 实测为准；本机**无 docker**）
2. 确认 `cegr_test` 库可连（DSN：`postgresql://postgres:postgres@127.0.0.1:55440/cegr_test`；口令若不符，以 `infra/.env.example` 记载为准调整）
3. 跑任一 DB-backed 测试文件确认 conftest 链式 apply（`DROP SCHEMA cegr CASCADE` + `01-core.sql` + migrations 001–013）成功
4. dbt 一律用 `.venv-dbt/bin/dbt`（**禁系统 python3 3.14**，mashumaro 不兼容）

## §NOW

**(A) O1 裁定登记（docs 三件套）**：
- docs/53 §5 **第 40 项**：O1 **CLOSED (as-scoped)**（用户裁定 2026-08-28）— 收口域 = NATIONAL_BULLETIN → nanjing CONDITION 真 SHA 入仓路径端到端打通（`538`→`560`→`572`→`573` 审计）；59 行其余城市/段 = 已登记缺口（第 39 项），**逐城真实源入仓保持 OPEN**（未来 `576` 号位刀）；「O1 仍 OPEN」历史行**不得删除**，裁定行追加其后
- docs/50：§4.4 里程碑表 +1 行（O1 CLOSED as-scoped 裁定行）+ intro 链尾 → `577`
- docs/45：文首刷新行（记录用户裁定 + 治理模型）+ §1 新段 + §6.2 行尾注 + §7 链头 `903 == 903 == 903`（按 bump 实际值）

**(B) S2.1-full demo seed**（新文件，per docs/36 §2 + s302 红线）：
- `data/seeds/person_tenure_demo.json`：30 person / 20 position / 60 tenure / 60 appointment_event / 60 person_source_evidence；**全部 demo**（lineage.is_demo='true'、source_file_sha256='0'*64、source_file_url='(DEMO_SEED_NO_FILE)'）；稳定 UUID（`a0000000-…-00000000005X` 族）；**无真实姓名/真实日期/真实 SHA**
- `scripts/seed_person_tenure_demo.py`：镜像 `seed_jiangsu_gdp_demo.py` 形态（load/unload/status；INSERT 全 `ON CONFLICT DO NOTHING`；unload=TRUNCATE CASCADE 六表）
- 验证新 seed 不复用 lite loader 的 probe UUID，避免 `ON CONFLICT DO NOTHING` 静默吞行

**(C) 6 个 dbt staging 模型**（新文件，镜像 `stg_observation.sql` 形态，`materialized='view'`）：
`stg_person.sql`、`stg_person_name_alias.sql`、`stg_position.sql`、`stg_tenure.sql`、`stg_appointment_event.sql`、`stg_person_source_evidence.sql`；并在 `_stg_sources.yml` +6 source 条目、`_stg_models.yml` +6 model 条目（unique/not_null 测试）

**(D) `dbt/models/marts/mart_person_tenure.sql`**（新文件，view）：tenure ⨝ person ⨝ position，LEFT JOIN geo_entity + appointment_event；**is_demo 显式暴露为最后一列**（per docs/36 §3）；**禁** score/rating/rank/total_score/confidence_score/credibility_score/peer_rank 词元

**(E) `tests/test_person_tenure_s21_full.py`**（新文件，DB-backed，复用 conftest `conn`/`tx` fixtures）：
- 5 表行数上限（30/20/60/60/60）
- seed 加载幂等（二次 load 行数不变）
- mart 列存在性 + is_demo 过滤（'true' 全量 / 'false' 空）
- overlap-positive 探针沿用 lite 语义（无 EXCLUDE，同 position 重叠 tenure 可插）
- 禁词静态扫描（先剥注释再扫）
- 不修改既有 `test_person_tenure_s21lite.py` / `test_mart_city_dbt_skel_s27bf.py`（回归必须保持全绿）

**(F) manifest bump**：`scripts/_knife577_manifest_bump.py`，NEW artifacts **+14**：
seed JSON（`data_contract_suite`）+ seed loader（`spike_helper`）+ 6 stg（`spike_helper`）+ mart（`spike_helper`）+ 新 pytest（`schema_negative_test`）+ bump 脚本（`spike_helper`）+ `577` 回执（`documentation`）+ **`575` 审计文件（`documentation`）** + **`00-EXEC-QUEUE.md`（`documentation`）** + **`scripts/exec_wake.sh`（`spike_helper`）** → **889 → 903**；断言 `sum(role_count) == artifact_count == len(artifacts) == 903`；yml/docs/既有文件为 SHA REFRESH 不增计数

**(G) 核验**（命令 + 输出原样粘贴进回执）：
```bash
.venv-dbt/bin/dbt run --profiles-dir dbt --select stg_person+ mart_person_tenure   # exit 0
python3 -m pytest tests/test_person_tenure_s21_full.py -q                          # 全绿 / exit 0
python3 -m pytest tests/test_person_tenure_s21lite.py tests/test_mart_city_dbt_skel_s27bf.py -q   # 回归 25+ 全绿
python3 frontend/smoke-check.py                                                    # exit 0
python3 -m pytest tests/ -q 2>&1 | tail -3                                         # 全量回归（live 依赖套件如实记录 skip 理由）
# 计数器（非减）：docs/45 ≥164 · docs/50 ≥25 · docs/53 ≥23；4 fixture 锁值不变；manifest 打印 903 903 903
```

**(H) 回执**：`reviews/stage0-gate0-rework-2026-08-23/577-stage0-cc-o1-close-person-tenure-full-receipt-20260828.md`
- 文件名含 `-cc-`；合刀单槽单回执，仅 `577`
- 交付 commit 含：docs/45/50/53、seed JSON + loader、6 stg + 2 yml、mart、新 pytest、bump 脚本、**`575` 审计文件**、本任务书、回执、**`00-EXEC-QUEUE.md`**（开工时 §ACK 填行 + 完成时 status→DELIVERED）、**`scripts/exec_wake.sh`**
- cc_head backfill 单独 commit（勿 amend）；`git push origin HEAD` → `git push github HEAD` 严格顺序

## 红线（零豁免）

- ❌ 不宣布 Gate 0/1/2 PASS；**O1 CLOSED (as-scoped) ≠ Gate 2 PASS ≠ Stage 2 收口**；逐城真实源入仓 OPEN 保留
- ❌ seed 无真实姓名/日期/SHA；不爬网灌履历；不加 EXCLUDE 约束；不动 migration 001–013
- ❌ 禁词词元（score 族）零出现；mart 不接 S2.7-b UI（前端接线另刀）
- ❌ 不动 registry.csv / gate_thresholds.json / 00-CC-CURRENT.md / 4 fixture 字节 / `mart_city_evidence_chain.sql`
- ❌ 无 --force / PAT / 公网 redeploy；既有「O1 仍 OPEN」历史行不删
- ✅ manifest 889 → 903 不变量；回执位于 `reviews/stage0-gate0-rework-2026-08-23/`

## 完成后

双推完成即停，回报 cc_head；架构师出 `578` 号位审计，随后发放 O3 决策备忘刀（`579`）。
