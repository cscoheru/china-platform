# 85 — 公网 redeploy runbook (knife 660 Track B, 2026-09-02)

> **刀号**: 660
> **类型**: 架构师级审查 (per 660 tasking §PART 2 + docs/84 模式 8 节架构师级审查体例)
> **日期**: 2026-09-02
> **前置**: 659 DELIVERED+C + 659 audit 修订 PASS (351/351 两遍 + m2 零 diff×2, 收口 commit `3f8e451` per `00-CC-CURRENT.md`) + 658 AUDIT-REVISED 维持 PASS (docs/82 终修) + 用户指令"真实生产站: china.3strategy.cc 需要纳入 660 范围,不是 china.rana.asia; 路径选 A, 新 vps 部署后的问题请自行解决"
> **范围**: Track B 静态导出 = mart SQL → JSON → build-time embedded, newvps 上不需要 FastAPI backend
> **关联**: `deploy/static-export/{export-mart-data.py, precheck.sh, deploy.sh, README.md}` + `frontend/lib/mart-static.ts` + `frontend/lib/api.ts` (Track B 分支) + `frontend/app/page.tsx` (mart section) + `frontend/data/mart_province_gdp_2024.json` + `frontend/smoke-check.py` §16

---

## 1. 任务背景与定位

### 1.1 660 = Track B 静态导出刀 (公网 redeploy)

**授权链**: 659 DELIVERED+C + 659 修订 PASS + 用户质询"已完成前端切源,为什么前端还是 demo 状态,是否没有部署到服务器" + 用户对 `china.3strategy.cc` 公网站点的确认 + 4 步实施指令 (ops 改 build 命令 + rsync 新代码 + systemctl restart + CC 公网 curl 验收)。

**核心动作 (Track B 静态导出)**:
- **架构师端 export**: `deploy/static-export/export-mart-data.py` ≈ 280 行, regex 解析 `dbt mart mart_province_gdp_2024.sql` 三个 CTE (province_codes/real_data/missing_provinces) 的 VALUES 元组, Python 层执行 LEFT JOIN + CASE/COALESCE, 输出 `frontend/data/mart_province_gdp_2024.json` (31 行 = 28 真实 + 3 缺失), 自带 `--strict` red-line audit (违规 exit 2)
- **前端接入**: `frontend/lib/mart-static.ts` ≈ 85 行 (isStaticMartDataEnabled + loadStaticMartData + getMartProvinceGdp2024 + TS 类型) + `frontend/lib/api.ts` 加 Track B 分支 (synthetic IndicatorListResponse) + `frontend/app/page.tsx` 渲染 mart section (31 行 + 3 「数据暂缺」badge + data-testid × 6)
- **ops 端 deploy 包**: `deploy/static-export/precheck.sh` (Node ≥18 + systemd + nginx + 写权限 + .env leakage) + `deploy/static-export/deploy.sh` (precheck → git pull → npm ci → 验证 mart JSON → npm run build with NEXT_PUBLIC_MART_DATA_PATH → systemctl restart → localhost:3000 sanity)
- **守门**: `frontend/smoke-check.py` §16 新增 7 子守门 (a-g) + `tests/test_mart_static_export_s660.py` 新增 ≥8 cases + README §守门 (JSON 红线 + 公网 A-G+H/I/J + 测试)

### 1.2 Track B vs Track A 决策

| 维度 | Track B (本刀) | Track A (后续 661+) |
|---|---|---|
| newvps 依赖 | Node + npm + systemd + nginx | + Python venv + dbt + Postgres + SQLite + FastAPI systemd service |
| 数据流 | mart SQL → JSON (架构师端) → build-time embedded | mart SQL → dbt run → Postgres view → FastAPI 运行时 fetch |
| 数据实时性 | Build 时锁定 (需重新跑 export + commit + push + redeploy) | 实时 (DB UPDATE 后下次 fetch 即可) |
| 部署复杂度 | 低 (无需 FastAPI 容器) | 高 (需 4 服务 systemd) |
| 守门 | smoke §16 (静态 JSON 守门) | smoke + FastAPI integration test |
| 选定 | **660 选定** (per 用户指令"服务器上没有不回部署吗?") | 661+ 评估 |

**为什么选 Track B**: 用户明确指出"服务器上没有不回部署吗?",意即"服务器上无 FastAPI/DB 也能跑"。Track B 把 mart 数据 JSON 化嵌入 build 产物, newvps 上零运行时依赖。

### 1.3 与 659 同构 + 差异性

| 项 | 659 (mart flip + 前端切源) | 660 (Track B 静态导出) |
|---|---|---|
| 类型 | mart flip + USE_MOCK 翻转 | Track B JSON 嵌入 + ops deploy |
| 范围 | dbt mart 模型 + frontend USE_MOCK 翻转 | export script + mart-static.ts + deploy 包 |
| 文件数 | 7 subagent 文件 + docs/84 + receipt/evidence | 4 deploy 文件 + 3 frontend 文件 + JSON 输出 + smoke §16 |
| 数据来源 | `/api/indicator` (FastAPI mart view) | `frontend/data/mart_province_gdp_2024.json` (build-time embed) |
| 公网目标 | china.3strategy.cc (部署依赖 FastAPI) | china.3strategy.cc (Track B 零运行时依赖) |

---

## 2. 数据流设计

### 2.1 Track B 数据流 (本刀选定)

```
[dbt mart mart_province_gdp_2024.sql]    ← 659 收口的 mart 模型
       │
       ▼
[deploy/static-export/export-mart-data.py]  ← 架构师端 (Python + regex 解析)
       │   (3 CTE 解析: province_codes/real_data/missing_provinces)
       │   (Python 层 LEFT JOIN + CASE/COALESCE)
       │   (--strict red-line audit, 违规 exit 2)
       ▼
[frontend/data/mart_province_gdp_2024.json]  ← 15361 bytes, 31 行
       │   (total_count=31, real_count=28, missing_count=3)
       │   (lineage_ruling='U6 2026-09-02', lineage_is_demo='false')
       ▼
[git commit + push origin main]            ← 架构师端
       │
       ▼
[newvps: deploy/static-export/precheck.sh]  ← ops 端, 全 [OK] 才进 deploy.sh
       │
       ▼
[newvps: deploy/static-export/deploy.sh]
    ├── git pull --ff-only
    ├── npm ci
    ├── 验证 mart JSON (31/28/3)
    ├── unset NEXT_PUBLIC_USE_MOCK
    ├── export NEXT_PUBLIC_MART_DATA_PATH=./data/mart_province_gdp_2024.json
    ├── npm run build  (build-time JSON 嵌入 bundle)
    ├── sudo systemctl restart china-platform-frontend
    └── curl localhost:3000 sanity check
       │
       ▼
[CC 公网 curl 验收]                         ← 架构师端
    https://china.3strategy.cc/
    ├── banner: ✅ LIVE MODE — 28 省 2024 真实数据 + lineage 可溯
    ├── province-gdp-2024-table 渲染 31 行 (28 真实 + 3 缺失)
    ├── 3 缺失省: 数据暂缺（公报源缺文）badge
    └── JIANGSU mock sentinel 残留 = 0
```

### 2.2 SQLite 3.50.4 限制绕开

**问题**: 朴素思路是 dbt mart → SQLite → SQL 执行 (e.g. `SELECT * FROM (VALUES ...) AS t(...)`) → JSON。但 SQLite 3.50.4 不支持顶层 `VALUES AS t` 语法, 最小测试也失败。

**解法**: 完全放弃 SQL 执行, 改用 regex 解析 mart SQL 三个 CTE 的 VALUES 元组, 在 Python 层执行 LEFT JOIN + CASE/COALESCE 转换逻辑。
- `parse_values_tuples(sql_text, cte_name)` 提取 `(...)` 元组列表
- `apply_case_join(tuples, key_col, fill_col)` Python 模拟 SQL CASE WHEN NULL END
- 输出 dict 与 mart 字段一一对应

**优势**:
- 不依赖 SQLite / Postgres 客户端
- 不依赖 dbt runtime
- 架构师端任何机器 Python 3.8+ 可跑

### 2.3 Track A 后续 (刀 661+ 评估)

Track A 是把 mart SQL 在 newvps 上 `dbt run` → Postgres mart view → FastAPI 运行时 fetch。优点是数据实时更新, 缺点是新 vps 需要 4 服务 systemd + Python venv + dbt 适配。

**661+ 触发条件** (任一):
- mart 数据每日变动 (e.g. 新统计局月报) → Track B 需每日 export+commit+push+redeploy
- 多源数据混合 (mart 来源 > 1)
- 需支持运行时 query (e.g. ?period=2023-Q3)

---

## 3. 实施内容

### 3.1 架构师端 — export-mart-data.py (≈ 280 行)

**核心函数**:
- `parse_values_tuples(sql_text: str, cte_name: str) -> List[Tuple]` — regex 解析 mart SQL 的 VALUES 元组
- `build_province_dict(province_tuples, real_tuples, missing_tuples) -> List[Dict]` — Python 层 LEFT JOIN + CASE
- `audit_red_lines(mart: dict) -> List[str]` — 8 条 red-line 自检 (total=31, real=28, missing=3, lineage_ruling 全行, lineage_is_demo='false', 缺失省 5 列 NULL, lineage 三重全行, GB/T 2260 顺序)
- `export_mart_json(strict: bool) -> int` — 主流程 (read mart → parse → join → audit → write JSON)

**验证** (架构师端跑过):
```bash
$ python3 deploy/static-export/export-mart-data.py --strict
OK: 31 rows -> frontend/data/mart_province_gdp_2024.json
[OK]   total=31
[OK]   real=28, missing=3
[OK]   lineage_ruling='U6 2026-09-02' 全行
[OK]   lineage_is_demo='false' 全行
[OK]   缺失省 5 指标列全 NULL (红线 1, 禁补零)
[OK]   lineage 三重标注全行
[OK]   GB/T 2260 顺序正确
exit=0
```

### 3.2 前端接入

**`frontend/lib/mart-static.ts` (≈ 85 行)**:
```ts
const MART_DATA_PATH = process.env.NEXT_PUBLIC_MART_DATA_PATH;
let cached: MartProvinceGdp2024 | null = null;
export function isStaticMartDataEnabled(): boolean { return !!MART_DATA_PATH; }
export function loadStaticMartData(): MartProvinceGdp2024 | null { ... }
export function getMartProvinceGdp2024(): MartProvinceGdp2024 | null { ... }
```

**`frontend/lib/api.ts` (Track B 分支)**:
```ts
if (isStaticMartDataEnabled()) {
  const mart = loadStaticMartData();
  if (mart) return indicatorsFromMart(mart);  // synthetic IndicatorListResponse
}
const res = await fetch(`${API_BASE}/api/indicator?...`);  // Track A fallback
```

**`frontend/app/page.tsx` (mart section)**:
- `{mart && (...table 31 行 + 3 missing badge...)}` — Track B 开启时渲染, 否则隐藏
- `data-testid`: `province-gdp-2024-heading`, `province-gdp-2024-table`, `mart-row-count`, `province-row-{code}`, `missing-badge-{code}`
- 缺失省: `style={{ background: "#fff8e1" }}` + `data-missing="1"`

### 3.3 ops 端 deploy 包

**`deploy/static-export/precheck.sh` (≈ 85 行)** — 5 节:
1. Node.js ≥ 18 (Next.js 14+ 要求)
2. systemd + `china-platform-frontend.service` registered
3. nginx + `/etc/nginx/sites-enabled/china.3strategy.cc.conf` + syntax ok
4. `/opt/china-platform/frontend` writable
5. .env* leakage (NEXT_PUBLIC_USE_MOCK=true 必须 [FAIL])

**`deploy/static-export/deploy.sh` (≈ 95 行)** — 7 步 + 7 exit codes:
1. precheck (inline, fail fast)
2. `git pull --ff-only`
3. `npm ci`
4.1. 验证 mart JSON (total=31, real=28, missing=3)
4.2. `unset NEXT_PUBLIC_USE_MOCK` + `export NEXT_PUBLIC_MART_DATA_PATH` + `npm run build`
5. `sudo systemctl restart china-platform-frontend`
6. `curl localhost:3000` sanity
7. summary + 通知 CC 端做公网验收

**关键差异 vs 老 446 baseline 命令链**:
| 项 | 老 (446) | 新 (660 Track B) |
|---|---|---|
| USE_MOCK env | `NEXT_PUBLIC_USE_MOCK=true` 硬编码 | unset (默认 false 真数据) |
| 数据来源 env | (无) | `NEXT_PUBLIC_MART_DATA_PATH=./data/...` |
| 运行时 FastAPI | 必需 | 不必需 |

### 3.4 README + 守门登记

`deploy/static-export/README.md` (≈ 150 行):
- 这是什么 (4 文件清单)
- 数据流图 (Track B vs Track A)
- ops 4 步执行 (SSH + precheck + deploy + 通知 CC)
- 架构师端 3 步 (export + commit + push)
- 与 446 老命令链差异表
- 守门清单 (JSON 红线 + 公网 A-G+H/I/J + 测试)
- 不在 660 范围 (FastAPI/容器化/换服务器/4 fixture 字节锁/O1 PASS)
- 常见问题 (CF 缓存/JSON 不更新/FastAPI 兼容)

---

## 4. 测试守门

### 4.1 smoke-check.py §16 (新增 7 子守门)

| § | 守门 | 文件 |
|---|---|---|
| 16a | mart JSON 31 行 + lineage_ruling + lineage_is_demo | `frontend/data/mart_province_gdp_2024.json` |
| 16b | mart-static.ts 4 API 表面齐 | `frontend/lib/mart-static.ts` |
| 16c | api.ts Track B 分支 (4 imports + indicatorsFromMart) | `frontend/lib/api.ts` |
| 16d | page.tsx mart section 渲染 (heading/table/31 rows/3 missing badge) | `frontend/app/page.tsx` |
| 16e | deploy 包 4 文件齐 | `deploy/static-export/` |
| 16f | DATA_MISSING 3 省 5 指标列全 NULL + lineage 三重 | mart JSON |
| 16g | 无 JIANGSU mock sentinel | mart JSON |

### 4.2 tests/test_mart_static_export_s660.py (新建 ≥8 cases)

| case | 验证内容 |
|---|---|
| `test_01_mart_json_exists_and_valid` | `frontend/data/mart_province_gdp_2024.json` 在位 + JSON 解析 OK |
| `test_02_mart_json_31_rows` | total=31 |
| `test_03_mart_json_28_real_3_missing` | real=28, missing=3 |
| `test_04_mart_json_lineage_ruling_uniform` | lineage_ruling='U6 2026-09-02' 全行 |
| `test_05_mart_json_lineage_is_demo_false` | lineage_is_demo='false' 全行 |
| `test_06_mart_json_3_missing_have_null_metric_cols` | DATA_MISSING 省 5 列 NULL (红线 1) |
| `test_07_mart_json_no_jiangsu_mock_sentinel` | 无 JIANGSU-GDP-INDICATOR-UUID-MOCK |
| `test_08_mart_static_ts_api_surface` | lib/mart-static.ts 导出 4 API |
| `test_09_api_ts_track_b_branch` | api.ts 含 Track B 分支 + indicatorsFromMart |
| `test_10_page_tsx_mart_section_render` | page.tsx 渲染 mart section + data-testid |
| `test_11_deploy_package_files` | deploy/static-export/ 4 文件齐 |
| `test_12_export_script_strict_mode` | export-mart-data.py --strict exit 0 |

### 4.3 与 659 同构

| 项 | 659 测试 | 660 测试 |
|---|---|---|
| 守门数 | smoke §15 (8 子守门) + test_mart_province_gdp_real.py (12 cases) | smoke §16 (7 子守门) + test_mart_static_export_s660.py (≥8 cases) |
| 文件锁值 | mart SQL + 4 frontend fixture | mart JSON (build-time embed) + deploy 包 4 文件 |
| 公网验收 | (无, 660 引入) | A-G+H/I/J (10 项) |

---

## 5. 公网 redeploy 步骤 (per docs/53 §5 第 16 项 📍 运维登记)

### 5.1 边界严守 (per 回执 446 §分工 + v3.5 规范)

**架构师端** (本机): 写代码 + 跑 export + commit + push。**不 SSH 到 newvps** (没 key, 无 ops 授权)。

**ops 端** (newvps 207.57.134.99:16921 via `ssh puer-hk` host alias ONLY — **永远不要 aliyun -p 16921**, 那是 mail.rana.asia): 跑 precheck + deploy.sh + systemctl restart + localhost sanity。**不回写代码到架构师端仓库** (per v3.5 禁执行端越权预写)。

**CC 公网验收端** (本机): `curl https://china.3strategy.cc/` A-G+H/I/J 矩阵。**不修改 ops 服务器任何文件**。

### 5.2 ops 端 4 步执行 (per README §ops 执行步骤)

```bash
# 1. SSH (永远不要 aliyun -p 16921)
ssh puer-hk

# 2. precheck (env / systemd / nginx / 写权限 / .env leakage)
cd /opt/china-platform/frontend
bash <(curl -sS https://raw.githubusercontent.com/cscoheru/china-platform/main/deploy/static-export/precheck.sh)
# 期望: ALL PASS

# 3. 一键 redeploy
bash /opt/china-platform/frontend/deploy/static-export/deploy.sh
# 或 rsync 后跑本地脚本

# 4. 通知架构师 (CC 端) 做公网 curl 验收
```

### 5.3 deploy.sh 退出码 (per deploy.sh 注释)

| exit | 含义 | ops 动作 |
|---:|---|---|
| 0 | 成功 | 通知 CC 端验收 |
| 1 | precheck 失败 | 解决 [FAIL] 行后重跑 |
| 2 | git pull --ff-only 冲突 | 手工 rebase / merge |
| 3 | npm ci 失败 | 检查 npm registry / node 版本 |
| 4 | npm run build 失败 | 检查 mart JSON + env vars |
| 5 | systemctl restart 失败 | 检查 service unit |

---

## 6. 公网验收矩阵 (CC 端 A-G + H/I/J 10 项)

per 660 tasking §PART 2 + deploy/static-export/README.md §守门.2:

| 编号 | 验收 | 期望 | 命令 |
|---|---|---|---|
| **A** | HTTP 200 | china.3strategy.cc/ → 200 | `curl -sS -o /dev/null -w '%{http_code}' https://china.3strategy.cc/` |
| **B** | banner 含 LIVE MODE | 含 "LIVE MODE" | `curl -sS https://china.3strategy.cc/ \| grep "LIVE MODE"` |
| **C** | 4 守门文案 | "28 省 2024 真实数据" + "官方 5 + 转载锚定 23" + "3 省源缺文" + "lineage 可溯" | `curl -sS https://china.3strategy.cc/ \| grep -E "28 省 2024 真实数据\|官方 5 + 转载锚定 23\|3 省源缺文\|lineage 可溯"` |
| **D** | JIANGSU mock sentinel 残留 = 0 | 无 "JIANGSU-GDP-INDICATOR-UUID-MOCK" | `curl -sS https://china.3strategy.cc/ \| grep -c JIANGSU-GDP-INDICATOR-UUID-MOCK` (期望 0) |
| **E** | data-mart-fixture = "0" | data-mart-fixture 属性值 = 0 | `curl -sS https://china.3strategy.cc/ \| grep -oP 'data-mart-fixture="[^"]*"'` |
| **F** | /public-extracts HTTP 200 + 4 锚点 | /public-extracts/ → 200 + 4 anchor 命中 | `curl -sS https://china.3strategy.cc/public-extracts/ \| grep -E "track-nbs-sample\|track-nbs-live\|track-sz\|track-hb"` |
| **G** | 本地 git HEAD = origin/main = github/main | 3 ref 全等 | `git rev-parse HEAD` ≡ `git rev-parse origin/main` ≡ `git rev-parse github/main` |
| **H** (新增) | province-gdp-2024-table 渲染 31 行 | `<table data-testid="province-gdp-2024-table">` 包含 31 个 `<tr data-testid="province-row-*">` | `curl -sS https://china.3strategy.cc/ \| grep -c 'data-testid="province-row-'` (期望 31) |
| **I** (新增) | 3 缺失省 "数据暂缺" badge 命中 | 含 3 个 `missing-badge-{LN,HAINAN,GUIZHOU}` | `curl -sS https://china.3strategy.cc/ \| grep -E 'missing-badge-(210000|460000|520000)'` (期望 3) |
| **J** (新增) | data-testid="province-row-{code}" 全 31 个命中 | 31 province-row-{code} | `curl -sS https://china.3strategy.cc/ \| grep -oP 'data-testid="province-row-[0-9]+"' \| sort -u \| wc -l` (期望 31) |

**验收不通过 fallback**:
- A 失败 → DNS / CF / nginx / systemd 链排查 (per docs/53 §5 第 16 项)
- B/C/D 失败 → 仍是 mock 路径, NEXT_PUBLIC_USE_MOCK=true 没 unset 或 env 没生效 → 重新跑 deploy.sh
- E 失败 → mart fixture env 残留 (track B fixture sentinel 没被覆盖)
- F 失败 → /public-extracts 静态路径未走 fixture (per tasking 349/420/424)
- G 失败 → 双推未完成 (per 659 模式 + 三 ref 全等)
- H/I/J 失败 → Track B 没启用 (NEXT_PUBLIC_MART_DATA_PATH 未生效 或 mart JSON 没嵌入 bundle)

---

## 7. 红线 14 + Track B 附加 5 条 (per 658 §10 沿用 + 660 README §守门)

### 7.1 红线 14 (沿用 659)

1. ❌ 不宣布 O1 / Gate / M2 / M4 PASS
2. ❌ 不改 4 fixture 字节锁 (nbs / nbs_live / sz / hb)
3. ❌ docs/81 零改动
4. ❌ 缺失省指标列 NULL 禁补零
5. ❌ mock 链文件不删 (S1.18 历史资产 + 回退通道)
6. ❌ 24 里程碑不宣布
7. ❌ 既有 registry 行 SHA 零漂移
8. ❌ 不爬网 (≤32 HTTP)
9. ❌ amend-first 沿用
10. ❌ docs/53 §5 第 16 项 老命令链 不退化
11. ❌ 不主动 commit (只在用户明确要求时才执行)
12. ❌ 不主动 push (除非用户说"自动发布")
13. ❌ 不主动 SSH 到 newvps (没 key, 无 ops 授权)
14. ❌ 不宣称 PASS (架构师/ops/CC 边界)

### 7.2 Track B 附加 5 条 (660 README §守门.1)

15. ✅ mart JSON 31 行 (28 真实 + 3 缺失) — `export-mart-data.py --strict` 自检
16. ✅ lineage_ruling = 'U6 2026-09-02' 全行 — 红线: ruling 变更必须新刀, 不能 update
17. ✅ lineage_is_demo = 'false' 全行 — 红线: 不可降级为 demo
18. ✅ DATA_MISSING 3 省 (LIAONING/HAINAN/GUIZHOU) 5 指标列全 NULL — 红线 1 禁补零
19. ✅ lineage 三重标注全行 (lineage_source / lineage_origin / lineage_ruling) — 红线: 不可缺列

---

## 8. 不宣称 PASS (沿用红线 13)

**660 状态**:
- ❌ 不宣布 Track B PASS — 待 ops 跑 deploy.sh + CC 公网 curl A-G+H/I/J 全 PASS 才算 PASS
- ❌ 不宣布 china.3strategy.cc 切源完成 — 待 §6 10 项验收矩阵全绿
- ❌ 不宣布 O1 / Gate / M2 / M4 PASS — 660 仅是 §1 mart flip + 前端切源刀, 不涉及 O1 收口
- ❌ 不宣布 docs/84 已升级 — docs/84 = 659 收口文档, 660 仅 append §1.3 差异表
- ❌ 不冒充 ops 执行 — ops 在 newvps 上的 SSH + systemctl 行为, 架构师端只 verify (公网 curl)
- ❌ 不回写 ops 服务器文件 — per v3.5 禁执行端越权预写
- ❌ 不踩 docs/53 §5 第 16 项 老命令链 — NEXT_PUBLIC_USE_MOCK=true 硬编码链路已废弃
- ❌ 不动 4 fixture 字节锁 — nbs / nbs_live / sz / hb fixture SHA 零漂移
- ❌ 不动 docs/81 — 内容零改动

---

## 9. 下一步 (implication)

### 9.1 等 ops 执行 + CC 公网验收 (刀 660 收口)

**任务 #816** = 等 ops 跑 `deploy/static-export/deploy.sh` 并通知 CC 做公网 curl 验收。

**验收通过 → 660 收口**:
- 9 commits 模式 (架构师端 export + 3 frontend file + smoke §16 + docs/85 + 收官叙事)
- 7+ subagent 文件修改保留
- 双推 (origin + github) + 3 ref 全等
- receipt 13 节齐备

**验收不通过 → 660 暂不收口**:
- CC 报告具体失败项 (A-G+H/I/J 编号 + 期望 vs 实际)
- 架构师端诊断 (常见: CF 缓存 / env 漏生效 / mart JSON 未嵌入 bundle)
- 不宣布 PASS, 走 `investigate` 流程

### 9.2 后续刀评估

- **刀 661** = Track A (FastAPI + DB backend on newvps) — 评估触发条件 (数据每日变动 / 多源 / 运行时 query)
- **刀 662** = container 化 (preview 容器化择机另刀, per docs/53 §5 第 16 项)
- **刀 663+** = 31 省 × 多指标 (mart 扩展: GDP + 人口 + 财政 + 投资), 视 Track B 稳定度

### 9.3 与 docs/84 关系

docs/84 = 659 mart flip + 前端切源 架构师级审查 (8 节, 299 行, 含 P3-2 终修)
docs/85 = 660 Track B 静态导出公网 redeploy runbook (9 节, 本文, 含 deploy.sh + 验收矩阵)

两者层级关系: docs/84 = mart 数据层 (dbt mart 31 行), docs/85 = 公网部署层 (JSON 嵌入 + ops redeploy)。

— End docs/85 20260902 —