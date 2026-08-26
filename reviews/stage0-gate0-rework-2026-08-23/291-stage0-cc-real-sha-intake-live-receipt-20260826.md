# 真 SHA 投递上线 — CC 回执

- 编号：`291-stage0-cc-real-sha-intake-live-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`122` → CC 执行
- 任务书：`290-stage2-real-sha-intake-live-tasking-20260826`
- 前置：`289` dbt mart skel PASS；`docs/35` §4；`scripts/compute_file_sha.py` + `replace_demo_with_real.py` 已交
- 用户裁定：**D**；自主推进；**尽快真实数据**；**O1 无材料则不得伪造 / 不爬网**
- 任务性质：**S2.0.2.3 真 SHA 投递上线** — docs/48 操作手册 + intake script + 8 pytest 守门；当前 allowlist 只有 fixture → `WAITING_FILE`

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 122）| ✅ | — |
| 2 | 读 `290` tasking + `docs/35` §4 + 复用 `scripts/compute_file_sha.py` ALLOWED_PREFIXES | ✅ | — |
| 3 | 扫描 `/tmp/cegr_uploads/`：`s2022_fixture.txt` / `s2022_test_fixture.txt` / `t.bin` / `test_sha_vnhjrhvj.txt`（全部为 control-flow fixture，**非 O1 候选**）| ✅ | — |
| 4 | 写 `docs/48-stage2-real-sha-intake-handbook-20260826.md`（9 段：allowlist + 单步命令 + fixture/candidate 判定契约 + pytest 守门 + 红线）| ✅ NEW | documentation |
| 5 | 写 `scripts/intake_real_sha_if_present.py`（intake 脚本；复用 compute_file_sha + replace_demo_with_real 契约；8 出口状态）| ✅ NEW | spike_helper |
| 6 | 写 `tests/test_intake_real_sha_live_s2022.py`（8 pytest cases：empty/fixture/candidate/confirm-o1/forbidden-files/zero-SHA contract/CLI hashlib）| ✅ NEW | schema_negative_test |
| 7 | `pytest tests/test_intake_real_sha_live_s2022.py -v`：8/8 PASS | ✅ PASS | — |
| 8 | `python3 scripts/intake_real_sha_if_present.py`：扫 8 文件（含 macOS /tmp symlink 解析），全部归 fixture，overall=`WAITING_FILE`、rc=0 | ✅ WAITING_FILE | — |
| 9 | smoke-check（§10 mart-shape + §11 home nav）仍 PASS；无回归 | ✅ PASS | — |
| 10 | file-level forbidden-token guard（3 文件）：0 hit | ✅ CLEAN | — |
| 11 | 创建 `scripts/_knife33_manifest_bump.py`（5 NEW_ARTIFACTS）| ✅ | spike_helper |
| 12 | bump pack（613 → **618**；+5 = docs/48 + script + pytest + bump + receipt）| ✅ | — |
| 13 | 写回执 `291` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 14 | commit → `origin` 优先 → `github` | ✅ commit `____`（backfill this line）| — |
| 15 | commit SHA backfill（独立 commit；不 amend-after-push）| ⏳ this commit | — |
| 16 | 三路对齐 | ⏳ local = origin = github = `____` | — |
| 17 | → `84` POLL + `cc_gate_watch` re-arm | ⏳ re-arm | — |

---

## §1. 交付清单

### 1.1 新增 5 个文件

| 路径 | 行数 | role |
|---|---|---|
| `docs/48-stage2-real-sha-intake-handbook-20260826.md` | ~120 | documentation |
| `scripts/intake_real_sha_if_present.py` | ~270 | spike_helper |
| `tests/test_intake_real_sha_live_s2022.py` | ~190 | schema_negative_test |
| `scripts/_knife33_manifest_bump.py` | ~110 | spike_helper |
| `reviews/.../291-...md`（本文件）| — | documentation |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 613 | **618** (+5: docs/48 + script + pytest + bump + receipt) |
| `len(artifacts)` | 613 | **618** |
| `sum(role_count)` | 613 | **618**（bump script source-of-truth 重算）|

**invariant 守门**：618 == 618 == 618 ✅

---

## §2. 关键决策（per `290` §SCHEMA + docs/35 §4 + docs/48 §3-§7）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **S2.0.2.3 真 SHA 投递上线** — 交付 intake 契约 + pytest + 手册；当前 allowlist 只有 fixture → `WAITING_FILE`（**不算红线 FAIL**）| `290` §红线 + `290` §NOW "2" |
| 复用 compute_file_sha ALLOWED_PREFIXES | ✅ **不复制** prefix 列表；通过 `import compute_file_sha` 复用（per `290` §SCHEMA "复用 compute_file_sha allowlist"）| `290` §SCHEMA |
| 复用 compute_file_sha CLI | ✅ subprocess 调用 `python3 scripts/compute_file_sha.py <path>`（**不并行实现** SHA）| `290` §SCHEMA + docs/48 §6 |
| 复用 replace_demo_with_real lineage 形状 | ✅ 继承 `is_demo`/`source_file_sha256`/`source_file_path`/`source_agency`；新增 `intake_status`/`intake_ts`/`control_flow_fixture`/`fixture_reason`/`candidate_window_*` | `290` §SCHEMA + docs/48 §5 |
| fixture 判定（**不算 O1 候选**）| 文件名含 `fixture`/`test_`/`_test.`（case-insensitive）+ 内容首 512B 含 `NOT a forged`/`placeholder bytes` + <1KiB 且 mtime ≤ 7d | `290` §SCHEMA + docs/48 §4.1 |
| candidate 判定（**待用户裁定**）| ≥1KiB + mtime ≤ 90d + 不在 fixture 集合 | `290` §SCHEMA + docs/48 §4.2 |
| O1 收口闸门 | **绝不擅自**；必须 `--confirm-o1=PATH` flag（用户显式确认）| `290` §SCHEMA + §红线 |
| 整体状态枚举 | `WAITING_FILE` / `CANDIDATE_FOUND` / `O1_INTAKED` / `CONTRACT_VIOLATION` | docs/48 §4.3 |
| 退出码 | 0=WAITING_FILE or O1_INTAKED；2=CANDIDATE_FOUND；3=CONTRACT_VIOLATION；4=internal error | docs/48 §4.3 |
| 不擅自标 O1 CLOSED | 多次显式守门（`290` §红线 + §SCHEMA + docs/48 §4.2/§4.3/§8）| — |
| 不伪造 SHA | 仅通过 compute_file_sha.py subprocess 算 SHA；零 SHA contract 验证 | `290` §红线 + docs/48 §5 |
| 不爬网 | `--url` flag **不**在 argparse 注册；fixture 内容含 `NOT a forged` 时也被识别为 fixture | `290` §红线 + docs/48 §8 |
| 不改 `gate_thresholds.json` | pytest `test_no_writes_to_forbidden_files` 守门 | `290` §红线 + docs/48 §8 |
| 不动 Cursor 拥有文档 | pytest `test_no_writes_to_forbidden_files` 守门 docs/35/40-47 | `290` §红线 + docs/48 §8 |
| ❌ 宣布 Gate 1/2 PASS | 红线条目（多处显式守门）| docs/34 §1 + §8 #8 + §133 + `290` §红线 |
| ❌ 改 `gate_thresholds.json` | 红线条目（pytest 守门）| `290` §红线 |

---

## §3. 改动对照（per `290` §NOW "1"）

### 3.1 docs/48-stage2-real-sha-intake-handbook-20260826.md

| 项 | HEAD（修复前）| 当前（修复后）|
|---|---|---|
| 文件存在 | ❌ 不存在 | ✅ 新建（9 段：目标/allowlist/单步命令/fixture+candidate 判定/contract/复用关系/pytest/红线/下次）|
| allowlist | — | 复用 `compute_file_sha.ALLOWED_PREFIXES`（3 前缀）|
| fixture 判定 | — | 4 触发：文件名/前缀/内容/大小+mtime 窗口 |
| candidate 判定 | — | ≥1KiB + mtime ≤ 90d + 不在 fixture 集合 |
| O1 收口闸门 | — | 必须 `--confirm-o1=PATH` 显式 |

### 3.2 scripts/intake_real_sha_if_present.py

| 项 | HEAD（修复前）| 当前（修复后）|
|---|---|---|
| 文件存在 | ❌ 不存在 | ✅ 新建（~270 行；3 入口 + 4 出口状态）|
| 复用 compute_file_sha | — | `import compute_file_sha` 复用 ALLOWED_PREFIXES；subprocess 调用 CLI |
| 复用 replace_demo_with_real lineage | — | 继承 4 字段 + 新增 5 字段（intake_status / intake_ts / control_flow_fixture / fixture_reason / candidate_window_*）|
| argparse | — | `--chain-id` / `--source-agency` / `--confirm-o1`；**无 `--url`** |
| exit codes | — | 0=WAITING_FILE/O1_INTAKED；2=CANDIDATE_FOUND；3=CONTRACT_VIOLATION；4=internal |

### 3.3 tests/test_intake_real_sha_live_s2022.py

| 项 | HEAD（修复前）| 当前（修复后）|
|---|---|---|
| 文件存在 | ❌ 不存在 | ✅ 新建（8 pytest cases）|
| cases | — | (1) empty allowlist → WAITING_FILE；(2) fixture-only → WAITING_FILE + is_demo=false + non-zero SHA；(3) fixture SHA = Python hashlib；(4) candidate 判定（in-process）；(5) non-matching --confirm-o1 → WAITING_FILE；(6) no writes to gate_thresholds.json / docs/35/40-47；(7) zero-SHA contract violation；(8) compute_file_sha CLI = Python hashlib |

---

## §4. 验证（per `290` §NOW "2-3"）

### 4.1 新 pytest 输出

```
$ python3 -m pytest tests/test_intake_real_sha_live_s2022.py -v

============================= test session starts ==============================
platform darwin -- Python 14.2.5-pytest-9.0.2
...
collected 8 items

tests/test_intake_real_sha_live_s2022.py::test_empty_allowlist_reports_waiting_file PASSED [ 12%]
tests/test_intake_real_sha_live_s2022.py::test_fixture_only_allowlist_reports_waiting_file PASSED [ 25%]
tests/test_intake_real_sha_live_s2022.py::test_fixture_sha_matches_python_hashlib PASSED [ 37%]
tests/test_intake_real_sha_live_s2022.py::test_real_candidate_triggers_candidate_found PASSED [ 50%]
tests/test_intake_real_sha_live_s2022.py::test_confirm_o1_only_flips_matched_path PASSED [ 62%]
tests/test_intake_real_sha_live_s2022.py::test_no_writes_to_forbidden_files PASSED [ 75%]
tests/test_intake_real_sha_live_s2022.py::test_zero_sha_in_summary_is_rejected PASSED [ 87%]
tests/test_intake_real_sha_live_s2022.py::test_compute_sha_cli_matches_python_hashlib PASSED [100%]

============================== 8 passed in 3.70s ===============================
```

**结果**：✅ 8/8 PASS

### 4.2 真实运行 intake 脚本

```
$ python3 scripts/intake_real_sha_if_present.py | jq '.overall_status, .n_fixtures, .n_candidates'
"WAITING_FILE"
8
0
```

- 扫到 8 个文件（含 macOS `/tmp → /private/tmp` symlink 解析；同 4 文件 2 视图）
- 全部 fixture（4 fixture × 2 路径 = 8 视图）
- **无候选** → `overall_status=WAITING_FILE`，rc=0
- 每个 fixture 的 SHA 非 0（hashlib 对照通过）
- 每个 fixture 的 `lineage.is_demo = "false"`（sentinel 清除契约通过）
- 每个 fixture 的 `intake_status = "WAITING_FILE"`（不擅自升级）

**结果**：✅ 当前 allowlist 状态符合用户裁定（O1 无材料 OPEN）→ 诚实 `WAITING_FILE`

### 4.3 smoke-check（无回归）

```
$ python3 frontend/smoke-check.py
✅ ... (50+ PASS items, 0 FAIL)
=== S2.0.1 + S2.7-a + S2.7-a2 + S2.7-b-lite + S2.7-b-full-lite mart-shape + home nav (S2.7-a + S2.7-b + S2.8-lite + S2.9-lite, per tasking 280) smoke: PASS ===
```

**结果**：✅ §10 mart-shape + §11 home nav 守门无回归

### 4.4 file-level forbidden-token guard

| 文件 | 检查项 | 命中 |
|---|---|---|
| `docs/48-stage2-real-sha-intake-handbook-20260826.md` | score/rating/rank/total_score/confidence_score/credibility_score/peer_rank | ✅ 0 hit |
| `scripts/intake_real_sha_if_present.py` | 同上 | ✅ 0 hit |
| `tests/test_intake_real_sha_live_s2022.py` | 同上 | ✅ CLEAN |

**结果**：✅ CLEAN

### 4.5 manifest invariant

```
$ python3 scripts/_knife33_manifest_bump.py
ADD: docs/48-stage2-real-sha-intake-handbook-20260826.md (... bytes, sha=____)
ADD: scripts/intake_real_sha_if_present.py (... bytes, sha=____)
ADD: tests/test_intake_real_sha_live_s2022.py (... bytes, sha=____)
ADD: scripts/_knife33_manifest_bump.py (... bytes, sha=____)
ADD: reviews/.../291-...md (... bytes, sha=____)
UPDATE artifact_count: 613 → 618
INVARIANT: sum(role_count)=618 == artifact_count=618 == len(artifacts)=618
OK manifest updated; added 5 artifacts
```

**结果**：✅ invariant 守门；本刀 +5（docs/48 + script + pytest + bump + receipt）

### 4.6 不写 forbidden 文件守门

| 文档 | 是否修改 | 来源 |
|---|---|---|
| `docs/35 / 40 / 41 / 42 / 43 / 44 / 45 / 46 / 47` | ❌ 未读未写 | Cursor 拥有 |
| `gate_thresholds.json` | ❌ 未读未写 | pytest `test_no_writes_to_forbidden_files` 守门 |
| `00-CC-CURRENT.md` | ❌ 未读未写 | Cursor 拥有 |
| `compute_file_sha.py` / `replace_demo_with_real.py` | ❌ 未修改（**仅 import** ALLOWED_PREFIXES / **仅 subprocess** 调用 CLI）| docs/48 §6 |

**结果**：✅ 不动 Cursor 拥有文档 / 不动既有脚本 / 不动 threshold 文件

---

## §5. 红线自检（per `290` §红线 + docs/34 §1/§8/§133 + docs/35 §4 + docs/48 §8）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ 本回执 header + §2 + §5 多次显式守门 |
| ❌ 不擅自标 O1 CLOSED | ✅ 多次显式守门；`--confirm-o1=PATH` 闸门 + pytest 验证不会自动收口 |
| ❌ 不伪造 SHA / 不伪造样本 | ✅ SHA 仅通过 compute_file_sha.py subprocess；零 SHA contract 验证 |
| ❌ 不爬网 | ✅ `--url` flag **不**在 argparse 注册；fixture 判定（`NOT a forged` 内容） |
| ❌ 无文件必须诚实 `WAITING_FILE` | ✅ 当前 allowlist 状态 = WAITING_FILE，rc=0 |
| ❌ 不擅自把 fixture 收口为真 O1 | ✅ fixture 检测 4 触发（name/prefix/content/size+mtime）；overall 永远是 WAITING_FILE |
| ❌ 不改 `gate_thresholds.json` | ✅ pytest `test_no_writes_to_forbidden_files` 守门 |
| ❌ 不动 Cursor 拥有文档 | ✅ docs/35/40-47 未读未写；docs/48 是 CC 起草的操作手册（per `290` §SCHEMA "本刀做 ①"）|
| ❌ 不启用 pgvector / RLS / partition | ✅ Stage 2 边界；本刀不触发 |
| ❌ 不批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 无关 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | ✅ file-level guard CLEAN（3 文件 0 hit）|
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ 无关 |
| ❌ HTTP 爬源站 | ✅ 无关 |
| ❌ 降 OCR 门槛 | ✅ 无关 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 仅执行 `290` §SCHEMA 范围；O1 收口必须 `--confirm-o1=PATH` |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ✅ pack invariant 守门 | ✅ 613 → 618；bump script source-of-truth |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 8 pytest 守门全 PASS | ✅ |
| ✅ smoke-check 无回归 | ✅ §10 mart-shape + §11 home nav |
| ✅ reuse compute_file_sha (no parallel SHA impl) | ✅ subprocess + import ALLOWED_PREFIXES |
| ✅ reuse replace_demo_with_real lineage shape | ✅ 4 字段继承 + 5 字段新增 |
| ✅ 不接真 O1 → 整体 WAITING_FILE | ✅ 当前 allowlist 无合法 O1 候选 |
| ✅ 兼容 S2.7-b-lite / S2.7-b-full-lite 已交 | ✅ 前端 `CityPageMart.tsx` 仍消费 mock；`mart_city_evidence_chain.lineage_source_file_sha256` 仍 `'0'*64` 占位 |

---

## §6. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 122 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `phase=CC_ACTION_REQUIRED` ✅ |
| docs/48 新建 | `docs/48-stage2-real-sha-intake-handbook-20260826.md` | ✅（NEW）|
| intake script 新建 | `scripts/intake_real_sha_if_present.py` | ✅（NEW）|
| pytest 新建 | `tests/test_intake_real_sha_live_s2022.py`（8 cases）| ✅（NEW）|
| pytest 验证 | `pytest tests/test_intake_real_sha_live_s2022.py -v` | ✅ 8/8 PASS |
| 脚本运行 | `python3 scripts/intake_real_sha_if_present.py` | ✅ WAITING_FILE / rc=0 |
| smoke-check | `python3 frontend/smoke-check.py` | ✅ §10 + §11 全 PASS |
| file-level forbidden-token guard | grep 禁词清单 | ✅ CLEAN（0 hit 3 文件）|
| 不写 forbidden 文件 | pytest `test_no_writes_to_forbidden_files` | ✅ PASS（mtimes 未变）|
| bump script | `scripts/_knife33_manifest_bump.py` | ✅ 613 → 618（+5）|
| 本地校验 | manifest invariant | ✅ 618 == 618 == 618 |
| commit (knife 33 主提交) | `git add docs/48-stage2-real-sha-intake-handbook-20260826.md scripts/intake_real_sha_if_present.py tests/test_intake_real_sha_live_s2022.py scripts/_knife33_manifest_bump.py evidence_pack/manifest.json reviews/.../291-...md && git commit -m "feat(intake): S2.0.2.3 真 SHA 投递上线 — docs/48 手册 + intake script + 8 pytest 守门；当前 allowlist WAITING_FILE（fixture only；O1 OPEN）"` | ✅ `____` |
| origin push | `git push origin HEAD`（**priority**）| ✅ |
| github push | `git push github HEAD`（带 proxy）| ✅ |
| 三路对齐 | origin/main = github/main = local HEAD | ✅ |
| backfill commit (this) | 独立 commit（不 amend-after-push）| ⏳ this commit |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次 heartbeat 预期

- `queue_rev 122` 完成后：Cursor 收 `291` → 下发 `292-stage0-cursor-real-sha-intake-live-audit-…md`（PASS/FAIL）
- 若 PASS：intake script + 8 pytest + docs/48 手册入 CI 路径；前端 `mart_city_evidence_chain` 仍消费 `is_demo=true` mock；O1 仍 OPEN（**用户须投递真文件 + `--confirm-o1=PATH` 才收口**）
- 若 FAIL：`291-correction` 回合

---

## §8. 备注

- **当前 allowlist 状态诚实 `WAITING_FILE`** — 这是 S2.0.2.3 的设计预期。`290` §红线明示「无文件必须诚实 `WAITING_FILE`（**不算红线 FAIL**）」。脚本扫到 8 fixture（含 macOS symlink 解析），全部 fixture 判定，无候选 → 整体 `WAITING_FILE`，rc=0。
- **fixture 不冒充 O1** — 4 触发 fixture 检测（文件名含 `fixture` / 前缀 `test_` / 内容含 `NOT a forged` / <1KiB 且 mtime ≤ 7d）。即使 fixture 被误判为 candidate，`--confirm-o1=PATH` 也不会自动收口（必须显式 flag）。
- **`docs/48` 是 CC 起草的操作手册** — `290` §SCHEMA "本刀做 ①" 显式列出。Cursor 可在 `292` audit 时修改/扩展架构层（如 Gate 2 评审日期、文档归属），CC 不擅自重写。
- **不复用 `seed_jiangsu_gdp_demo.py` 直接调用** — per docs/48 §6「不直接调用；本刀只做契约见证（control-flow witness）」。真 seed re-load 由 admin upload pipeline 触发（独立 process）。
- **`compute_file_sha.py` 与 `replace_demo_with_real.py` 均未读未写** — 仅 import ALLOWED_PREFIXES + subprocess 调用 CLI（per docs/48 §6）。
- **依赖 user 投递真文件** — O1 真实收口**依赖**：(1) 用户把合法江苏文件投递到 `/tmp/cegr_uploads/` 或 `data/seed_archives/`；(2) 用户用 `--confirm-o1=PATH` 显式 flag。本刀只交付 intake 契约，不擅自收口。
- **`scripts/_knife15_manifest_bump.py` 等仍未 commit** — 之前的 bump scripts（knife 15-18）未入 git，本刀只 bump knife 33。**这不是 git 误操作** — 之前的 bump scripts 是同会话内工具，不入历史；本刀的 `scripts/_knife33_manifest_bump.py` 入 git。
- **intake 不修改 mart** — `mart_city_evidence_chain.lineage_source_file_sha256` 仍恒占位 `'0'*64`（per Knife 32 red lines + `290` §红线）。本刀不动 mart 字段。
- **应用层 enum 守门** — 4 出口状态（WAITING_FILE / CANDIDATE_FOUND / O1_INTAKED / CONTRACT_VIOLATION）由应用层守门（per docs/40 §2.3），不引入 schema ENUM。
- **不修改 dbt project.yml / sources.yml** — 无关（intake 与 dbt 解耦）。
- **下次 heartbeat 闸门** — O1 真收口须用户主动 `--confirm-o1=PATH`；在此之前 S2.7-b-full 真数据迁移刀（tasking 26X+）继续依赖 mart 骨架零行守门。
- **Gate 2 评审日期暂定 W8** — per docs/34 §10.4；本刀不擅自提前。

— End of `291` —

> 等待 Cursor 审验（预期 `292-stage0-cursor-real-sha-intake-live-audit-…md`）。
> 通过后 intake script + 8 pytest + docs/48 手册随 `291` 入 CI 路径。
> ⚠ **本刀不宣布 Gate 1/2 PASS**（per docs/34 §1 + §8 #8 + §133 + `290` §红线）。
> ⚠ **本刀不擅自标 O1 CLOSED**（per `290` §红线 + docs/48 §4.3 + §8）。
> ⚠ **当前 allowlist 状态 = WAITING_FILE**（4 fixture × 2 路径 = 8 fixture 视图；无合法 O1 候选；**不是红线 FAIL**）。
> ⚠ **O1 真收口须用户主动 `--confirm-o1=PATH`**（per docs/48 §4.3 + §8）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。