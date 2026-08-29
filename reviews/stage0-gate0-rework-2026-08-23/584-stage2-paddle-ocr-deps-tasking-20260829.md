# 584 — 任务书：O3 §5.2.4 paddle-ocr 引擎依赖刀（local deps + Dockerfile layer + docs sync patch）

- 编号：`584-stage2-paddle-ocr-deps-tasking-20260829`
- 前置：`584-stage0-architect-s583-o3-impl-validate-api-doc-kind-audit-PASS-20260829`（583 审计 PASS；583 修复刀交付 validate_ocr_input API + migration 014 doc_kind；manifest 917 不变量）
- 规划蓝图：`docs/49-stage2-o3-ocr-prod-path-plan-20260826.md` §5.2.4（paddle-ocr 引擎依赖）+ §5.2.5（e2e pytest）+ §5.2.6（真实 PDF `--confirm-o3=PATH` 用户保留动作）
- 引擎裁定（per `579`）：**paddle-ocr**（用户 2026-08-28；§5.2.1 已关闭）
- 下发：CC 架构师终端 → 执行端（经 `00-EXEC-QUEUE.md`，PENDING → ACK → DELIVERED）
- 日期：2026-08-29
- 验证深度：**deps 引入决策单独审计 + Dockerfile layer 落地 + docs sync patch**（零 OCR pipeline 集成 = §5.2.5 单独刀；零真实 PDF 处理 = §5.2.6 用户保留动作）

---

## §NOW

**背景（per docs/49 §5.2.4 paddle-ocr 引擎依赖）**：O3 实装链 §5.2.4 闭合 = paddle-ocr 引擎 local deps 引入 + Dockerfile layer 落地。deps 引入决策单独审计（per 583 任务书 §NOW 红旗 + 584 审计 ⚠1 决议；不与 583 接口实装混在同一刀，避免回滚粒度过粗）。§5.2.5 合成扫描 fixture pytest + §5.2.6 真实 PDF 用户保留动作 走后续刀，本刀不触。

**架构师本刀关键决策**：
1. **deps 引入决策单独审计**：本刀 = `paddleocr` + `paddlepaddle` 依赖引入决策单独披露（含 deps 大小 / 镜像 layer 体积 / 系统库依赖 / license / 离线 wheel 来源 / 镜像 build 时间成本 / 与 stdlib `mimetypes` 协同模式）。**§5.2.5 合成扫描 fixture pytest 走单独刀**（避免 deps 引入与 e2e 测试耦合回滚）。
2. **Dockerfile layer 独立**：paddle-ocr 镜像层单独 `FROM` 段（不与既有 layer 混编）；缓存策略 = paddle-ocr deps 单独 layer（重建代价隔离）；既有 layer 零触动。
3. **零 OCR pipeline 集成**：本刀 = deps + Dockerfile 落地即可；paddleocr 调用 / OCR 文本提取 / source_document.doc_kind='OCR_SCAN' 写入走 §5.2.5 + §5.2.6。本刀完成定义不依赖 OCR pipeline 集成实跑。
4. **§584 audit ⚠1 docs sync patch**（per `584-stage0-architect-s583-...-audit-PASS-20260829` ⚠1 ACCEPTED with disclosure）：docs/45 §7 链头 invariant claim 916 → 917 对齐 actual manifest 917（per enumeration 收口）。docs/45 L93 demote 段 / L487 pack invariant table / docs/53 §5 第 44 项 L203 + L207 / docs/50 §4.4 第 44 项 L228 — 五处 docs 数字 916 → 917 修正。**docs sync 不动 manifest / 不动 commit SHA / 不增计数**（SHA REFRESH 类）。docs/45 + docs/49 + docs/53 已入 manifest → SHA REFRESH 计入；docs/50 房规不入 manifest → 显式 SKIP 不增计数。

---

### (A) `requirements.txt` 或 `pyproject.toml` — NEW paddle-ocr 依赖声明（**NOT-IN manifest → ADD +1**）

**新增 paddle-ocr 依赖**：选其一文件路径（per 当前项目依赖管理文件）：
- `requirements.txt`（如存在）→ append `paddleocr>=2.7.0.3` + `paddlepaddle>=2.6.0`
- `pyproject.toml`（如存在且为主要 manifest）→ `[project.dependencies]` 加 paddleocr + paddlepaddle
- 选文件决策 = 审计侧独立判断（按 docs/49 §5.2.4 字面 + 当前项目约定；如两文件并存则按主 manifest）

**deps 引入决策披露**（写入回执）：
- paddleocr 当前稳定版 + paddlepaddle 当前稳定版（执行端实测 `pip index versions` 或 `pip show` 拿实测版本，写入 receipt）
- 镜像 layer 体积增加（paddlepaddle ~ 400MB / paddleocr ~ 100MB 量级估；执行端实测 `pip install --dry-run` 拿体积估算）
- 系统库依赖（如 libgomp / openblas / avx 等；执行端镜像构建实测）
- license = Apache 2.0（paddlepaddle + paddleocr 均为 Apache 2.0；执行端 `pip show` 拿实测 license）
- 离线 wheel 来源策略 = PyPI（默认；如镜像层需要离线缓存则 Docker build 时预下载至独立 layer）
- 镜像 build 时间成本（paddlepaddle 编译 / 安装慢；按既有镜像 build 时间基线 + paddledeps 时间增量估）

**零触碰核对**：
- ❌ 不修改 `scripts/auto_ingest_public_source.py`（SHA 闸 / 防篡改机制零触碰）
- ❌ 不引入 cloud OCR（百度云 / 腾讯云 / 阿里云 OCR API / HTTP OCR 服务 一律禁止；paddleocr 必须 local-only）
- ❌ 不引入 paddleocr-online / paddleocr-cloud 等云 OCR 变体
- ❌ 不引入 paddlepaddle-gpu（CPU-only paddlepaddle = 默认；GPU variant 走后续刀单独议）

---

### (B) `Dockerfile` 或对应镜像 build 脚本 — NEW paddle-ocr layer（**NOT-IN manifest → ADD +1**）

**Dockerfile layer 隔离**（per `584` 任务书 §NOW 决策 2）：
- 既有 `FROM` 段零触动
- 新增独立 `RUN pip install paddleocr paddlepaddle` 段（**不与既有 `pip install` 段合并**）
- 缓存策略：`COPY requirements.txt / paddle-ocr-deps-requirements.txt` 单独 COPY（paddle-ocr deps 独立 layer cache key）
- 验证：`docker build` 成功 exit 0 + 镜像大小增量符合披露（**docker image inspect 体积增量实测写入回执**）

**镜像构建验证**：
- 执行端按项目约定镜像 build 命令实跑（如 `docker build -t puer-hub-app:test-584 .` 或类似）
- exit 0 + 镜像体积实测（如 `docker images | grep test-584`）
- paddle-ocr 镜像层独立 cache 验证（如 `docker history puer-hub-app:test-584` 看 layer 分段）
- **零 OCR pipeline 集成实跑**（不调用 paddleocr API；不引入 OCR 文本提取代码；不写真实 PDF fixture 处理）

**零触碰核对**：
- ❌ 不修改既有 `FROM` / `RUN apt-get` / `RUN pip install <既有 deps>` 段
- ❌ 不引入 GPU runtime（CUDA / cuDNN / nvidia-docker 等；CPU-only paddlepaddle = 默认）
- ❌ 不引入 cloud OCR 镜像层（任何 cloud OCR API client 禁止）
- ❌ 不修改 `docker-compose.yml`（服务编排零触动；镜像 build 验证跑后清理 test 镜像）

---

### (C) `tests/test_paddle_ocr_deps_584.py` — NEW 测试文件（**NOT-IN manifest → ADD +1**）

**测试覆盖**：
1. **deps 导入测试**：`import paddleocr` + `from paddleocr import PaddleOCR` 验证 deps 引入成功
2. **paddleocr 版本断言**：`paddleocr.__version__` 与 receipt 披露版本一致（如 `>=2.7.0.3`）
3. **paddlepaddle 版本断言**：`paddlepaddle.__version__` 与 receipt 披露版本一致（如 `>=2.6.0`）
4. **CPU-only 验证**：执行端实测 paddlepaddle 编译选项含 CPU-only（不依赖 CUDA）
5. **离线能力验证**：执行端实测 paddleocr 模型加载可在无网络环境（默认 paddleocr 模型首次下载 = 本刀不触模型下载；仅验证 import 即可）
6. **零 cloud OCR API 客户端验证**：执行端实测 paddleocr deps tree 无 cloud OCR client（如 `aip` / `tencentcloud` / `aliyun-ocr` 等）
7. **§584 audit ⚠1 docs sync 落点验证**：执行端实测 docs/45 + docs/53 + docs/50 五处 916 → 917 修正落地

**fixture 规范**：
- 不依赖网络 / 不写真实 OCR 模型 / 不写真实 PDF fixture
- 不修改既有任何 fixture（4 fixture 锁值不变 e30ee811 / 9232efdb / 937255a5 / 9056001c）
- 不引入新的 fixture 文件（deps 引入验证 = import + version check 即可，不写真实 OCR 处理）

**imports**：
- `import paddleocr`、`import paddlepaddle`、`from paddleocr import PaddleOCR`（按 paddleocr 2.7+ API）
- 零 paddleocr 模型下载 / 零 OCR pipeline 集成

---

### (D) docs 同步（**docs/45 + docs/53 + docs/50 三件同步；含 §584 audit ⚠1 docs sync patch**）

- **docs/49 §5.2.4 状态翻转**：段首标「**CLOSED per 584（2026-08-29）**」（deps + Dockerfile layer 落地）；§5.2.5/§5.2.6 保持 OPEN
- **docs/53 §5 新增第 45 项**（per 583 末项第 44 项后）：
  - blockquote 内容 = 584 实装登记（deps + Dockerfile layer + deps 引入决策披露 + docs sync patch）
  - 闭合范围明示 = 5.2.4（deps + Dockerfile layer）；保持 OPEN = 5.2.5/5.2.6 + O3 收口
- **docs/45 五处**（落点族 per `580` ⚠2 裁定 + 含 §584 audit ⚠1 docs sync patch）：
  - 文首 +1 刷新行（架构师治理模型第六刀 per 584）
  - §1 +1 段（O3 §5.2.4 引擎依赖刀登记 + deps 引入决策披露）
  - §5.5 尾 O3 bullet 行尾注 append（per `584`；5.2.4 CLOSED；5.2.5/5.2.6 OPEN）
  - §7 链头 `917 == 917 == 917`（per bump 实际值）+ knife 584 demote
  - §7 链头 ⚠1 docs sync patch：**L93 demote 段 `916 == 916 == 916` → `917 == 917 == 917`** + `manifest 911 → 916（+5 per bump 实际值）` → `917（+6 per enumeration 收口）` + **L487 pack invariant table `916 == 916 == 916` → `917 == 917 == 917`**（per §584 audit ⚠1 ACCEPTED with disclosure）
  - §3 零涉（无裁定变更）
- **docs/50**：
  - §4.4 +1 第 45 项行
  - intro 链尾 `→ 583` 续接 `→ 584`
  - §5.1 O3 状态行 append 处置标注（O3 5.2.4 CLOSED；5.2.5/5.2.6 OPEN；行内 append 不删行）
  - §4.4 第 44 项行 ⚠1 docs sync patch：**L228 `§7 链头 911 → 916` → `911 → 917`**

**「O3 仍 OPEN」计数非减**（5.2.5/5.2.6 仍 OPEN = O3 整体仍 OPEN）

---

### (E) manifest bump（**+6** 含 docs sync patch SHA REFRESH）

`scripts/_knife584_manifest_bump.py`：NEW **+6**（枚举即权威，每项实测 NOT-IN）：
- bump 脚本本身（`spike_helper`）
- `584` 回执（`documentation`）
- `583` 审计文件（`documentation`，只读随刀入库）
- `requirements.txt` 或 `pyproject.toml`（deps manifest，依项目主文件；如两文件皆改 = +2，本刀按主文件 +1）
- `Dockerfile` 或对应镜像 build 脚本（`infrastructure`，NEW 角色）
- `tests/test_paddle_ocr_deps_584.py`（`schema_negative_test`，NEW；复用 583 测试文件 role 模式）
- `schema/migrations/015_*`（**0 件，本刀零 schema 改动**；不增 schema_migration_ddl / schema_migration_log 角色）
→ **917 → 923**；断言 `sum(role_count) == artifact_count == len(artifacts) == 923`

**REFRESH**：
- `scripts/auto_ingest_public_source.py`（SHA 不变 = 未改）
- `scripts/intake_real_sha_if_present.py`（SHA 不变 = 未改）
- `docs/45 + docs/49 + docs/50 + docs/53`（**全部 SHA REFRESH 不增计数**；含 §584 audit ⚠1 docs sync patch 落地）
- `00-EXEC-QUEUE.md`（SHA REFRESH 不增计数）
- `00-EXEC-QUEUE.md` §CURRENT status 翻转（PENDING → ACK → DELIVERED 随刀入库）

**SKIP**：
- `docs/50` 房规未入 manifest（per 574/577/579/581/583 先例）；**docs sync patch 落地但不入 manifest**
- `schema/01-core.sql` 不动（base schema 锁）
- `00-CC-CURRENT.md` 不动（Cursor 冻结）
- `registry.csv` / `gate_thresholds.json` 不动（红线）

**任务书按先例不计数**（574/577/579/581/583 任务书均不入 manifest；584 任务书同）

---

### (F) 零网络核验（命令 + 输出原样粘贴进回执；**(1) 全量为本刀核心证据**）

```bash
python3 -m pytest tests/ -q                                          # 全量：预期 0 failed（≈585+ passed / 8 skipped / +584 新增 7+ 例测试；~14 分钟含 paddle-ocr 导入开销）
python3 -m pytest tests/test_paddle_ocr_deps_584.py -q                # 新文件单独实跑（7+ 例 PASS）
python3 -m pytest tests/test_validate_ocr_input_583.py -q             # 583 测试文件防回归（14 例 PASS）
python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -q          # 25 passed（零改动防回归）
python3 frontend/smoke-check.py                                      # PASS / exit 0
shasum -a 256 frontend/lib/public_extract_{nbs,nbs_live_candidate,sz,hubei}.json | cut -c1-8
                                                                    # e30ee811 9232efdb 937255a5 9056001c
grep -c "O3 仍 OPEN" docs/45-*.md                                   # ≥11（非减；5.2.5/5.2.6 仍 OPEN）
grep -c "第 45 项（此条）" docs/53-*.md                              # 1
grep -c "917 == 917 == 917" docs/45-*.md                            # ≥3（per §584 audit ⚠1 patch；§7 链头 + L93 demote + L487 pack table）
grep -c "916 == 916 == 916" docs/45-*.md                            # 0（stale 916 已清 ✅；§584 audit ⚠1 闭合）
grep -c "917 == 917 == 917" docs/53-*.md                            # ≥2（per §584 audit ⚠1 patch；第 44 项 blockquote L203 + L207）
grep -c "916 == 916 == 916" docs/53-*.md                            # 0
grep -c "917" docs/50-*.md | grep "第 44 项"                         # ≥1（per §584 audit ⚠1 patch；第 44 项行 §7 链头 `911 → 917`）
python3 -c "import json;m=json.load(open('evidence_pack/manifest.json'));print(len(m['artifacts']),m['artifact_count'],sum(m['role_count'].values()))"
                                                                    # 923 923 923
python3 -c "import paddleocr, paddlepaddle; print('paddleocr:', paddleocr.__version__); print('paddlepaddle:', paddlepaddle.__version__)"
                                                                    # paddleocr: 2.7.x.x / paddlepaddle: 2.6.x  实测版本写入回执
docker build -t <project-app>:test-584 . 2>&1 | tail -5              # 镜像 build exit 0 + 体积增量符合披露
docker images | grep test-584                                       # 镜像体积实测（写入回执）
docker history <project-app>:test-584 2>&1 | head -20                # layer 分段验证（paddle-ocr 独立 layer）
```

---

### (G) 回执 + 交付 commit

- 回执：`reviews/stage0-gate0-rework-2026-08-23/584-stage0-cc-paddle-ocr-deps-tasking-20260829-receipt.md`（含 `-cc-`；单槽单回执，仅 `584`）
- 交付 commit 含：
  - `requirements.txt` 或 `pyproject.toml`（MODIFIED，paddle-ocr deps append）
  - `Dockerfile` 或对应镜像 build 脚本（MODIFIED，paddle-ocr layer 增量）
  - `tests/test_paddle_ocr_deps_584.py`（NEW）
  - docs/49 + docs/50 + docs/53 + docs/45（MODIFIED，含 §584 audit ⚠1 docs sync patch 五处 916 → 917）
  - bump 脚本（NEW）
  - `583` 审计文件（NEW，只读随刀入库）
  - `584` 任务书（NEW，只读随刀入库）
  - `584` 回执（NEW）
  - `00-EXEC-QUEUE.md`（ACK 填行 + status→DELIVERED + note 回执号）
- cc_head backfill 单独 commit（勿 amend）；`git push origin HEAD` → `git push github HEAD` 严格顺序

---

## 红线（零豁免）

- ❌ 零生产代码变更（仅 `requirements.txt` / `pyproject.toml` deps append + Dockerfile paddle-ocr layer 增量；**`scripts/auto_ingest_public_source.py` 零触碰**；SHA 闸零弱化）
- ❌ 不引入 cloud OCR（百度云 / 腾讯云 / 阿里云 OCR API / HTTP OCR 服务 一律禁止；paddleocr 必须 local-only）
- ❌ 不引入 GPU runtime（CUDA / cuDNN / nvidia-docker 等；CPU-only paddlepaddle = 默认）
- ❌ 不引入 paddleocr-online / paddleocr-cloud 等云 OCR 变体
- ❌ 不写真实 OCR pipeline 集成（paddleocr.PaddleOCR().ocr() 调用 = §5.2.5；本刀仅 deps + import 验证）
- ❌ 不写真实 PDF fixture 处理（`--confirm-o3=PATH` 真实 PDF 用户保留动作 = §5.2.6）
- ❌ 不修改 migration 001-014 任何文件（migration 014 doc_kind 已落 per 583；本刀零 schema 改动）
- ❌ 不修改 `schema/01-core.sql`（base schema 锁）
- ❌ 不修改 `scripts/auto_ingest_public_source.py` / `scripts/intake_real_sha_if_present.py` 既有函数（**仅 deps + Dockerfile 增量**）
- ❌ 不修改 4 fixture 字节 / data/seeds/ / spikes/ 任何文件
- ❌ 不爬网 / 不 cloud OCR / 不 HTTP 出站（paddleocr 模型下载本刀不触 = §5.2.5 单独刀）
- ❌ 不写 dbt / mart / 前端任何文件
- ❌ 不宣布 Gate 0/1/2 PASS；不宣布 O3 收口；O3 整体仍 OPEN（5.2.5/5.2.6 + 真实 PDF 用户保留动作不变）
- ❌ 无 --force / PAT / 公网 redeploy；既有 OPEN 行零删减（docs/50 §5.1 O3 行 append 处置标注不删行）
- ✅ 全量 0 failed 为本刀完成定义；manifest 917 → 923 不变量（+6 枚举即权威；含 §584 audit ⚠1 docs sync patch 五处 SHA REFRESH）；回执位于 `reviews/stage0-gate0-rework-2026-08-23/`

---

## 完成后

双推完成即停，回报 cc_head；架构师出 `585` 号位审计；随后签发 **`585` = §5.2.5 O3 e2e pytest 刀**（合成扫描 fixture / syn-PDF 实跑守门）、**`586+` = §5.2.6 真实 PDF `--confirm-o3=PATH` 用户保留动作刀**（O3 收口必经用户操作）。**§584 audit ⚠1 docs sync patch 落地验证**：执行端在 receipt §零网络核验 实测 docs/45 / docs/53 / docs/50 五处 916 → 917 修正；patch 不动 manifest / 不动 commit SHA；docs sync 与 manifest invariant 真实 917 一致。

## 附：§584 audit ⚠1 docs sync patch 详单（执行端 patch 范围）

| # | 文件 | 行号 | 旧值 | 新值 |
|---|---|---|---|---|
| 1 | `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | L93 (583 demote 段) | `manifest 911 → 916（+5 per bump 实际值：bump + 回执 + 582 审计 + 2 个 migration 文件 + 测试文件 ADD）` | `manifest 911 → 917（+6 per enumeration 收口：bump + 回执 + 582 审计 + 2 个 migration 文件 + 测试文件 ADD；per §584 audit ⚠2 INCONSISTENT-1 enumeration wins）` |
| 2 | `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | L93 (583 demote 段) | `docs/45 §7 链头 916 == 916 == 916` | `docs/45 §7 链头 917 == 917 == 917` |
| 3 | `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | L487 (pack invariant table) | `bump + commit 后 916 == 916 == 916` | `bump + commit 后 917 == 917 == 917` |
| 4 | `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | L203 (第 44 项 blockquote (D) bullet) | `§7 链头 `911 → 916` + knife 583 demote` | `§7 链头 `911 → 917` + knife 583 demote` |
| 5 | `docs/53-stage2-public-ingest-ops-handbook-20260826.md` | L207 (第 44 项 blockquote 闭环行) | `§7 链头 `916 == 916 == 916` + knife 583 demote` | `§7 链头 `917 == 917 == 917` + knife 583 demote` |
| 6 | `docs/50-stage2-gate2-review-packet-draft-20260826.md` | L228 (§4.4 第 44 项行 (D) bullet) | `§7 链头 `911 → 916` + knife 583 demote` | `§7 链头 `911 → 917` + knife 583 demote` |

**patch 不动 manifest / 不动 commit SHA**；docs/45 + docs/49 + docs/53 SHA REFRESH 计入 manifest；docs/50 房规不入 manifest → 显式 SKIP 不增计数。**§584 audit ⚠1 docs sync gap 闭合** = docs claim 与 manifest invariant 真实 917 一致。