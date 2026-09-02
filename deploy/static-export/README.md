# knife 660 Track B 静态导出部署包

> **刀号**: 660 (Track B = 静态导出,无需 FastAPI backend)
> **日期**: 2026-09-02
> **目标**: 把 china-platform frontend 从 mock 切到 mart 真实数据,公网 china.3strategy.cc 全程不需要 FastAPI backend / dbt / Postgres。
> **关联**: docs/85 runbook + 660 tasking `659-audit-660-tasking-consolidated-20260902.md` PART 2 + docs/53 §5 第 16 项 📍 运维登记。

## 这是什么

```
deploy/static-export/
├── export-mart-data.py     # 架构师端: dbt mart SQL → JSON
├── precheck.sh             # ops 端 precheck: env / systemd / nginx / 写权限
├── deploy.sh               # ops 端 redeploy: git pull → npm ci → build → restart
└── README.md               # 本文件
```

## 数据流(Track B vs Track A)

```
Track B (本包)                          Track A (可选, 后续刀)
═══════════════                          ════════════════════════
[dbt mart SQL]                           [dbt mart SQL]
       │                                        │
       ▼                                        ▼
[export-mart-data.py]                   [dbt run]
       │                                        │
       ▼                                        ▼
[data/mart_province_gdp_2024.json]      [Postgres mart view]
       │                                        │
       ▼                                        ▼
[git commit, push]                       [FastAPI /api/indicator]
       │                                        │
       ▼                                        ▼
[newvps: npm run build]                  [newvps: npm run build]
[NEXT_PUBLIC_MART_DATA_PATH=...]        [NEXT_PUBLIC_API_BASE=...]
       │                                        │
       ▼                                        ▼
[bundle 嵌入 JSON, 零运行时依赖]          [运行时 fetch → FastAPI]
```

**Track B 优点**: newvps 上不需要 Python / venv / Postgres / SQLite / dbt / FastAPI systemd service — 只需 Node.js + npm + systemd + nginx。
**Track A 后续**: 当 660 收口稳定,刀 661+ 可评估切到 Track A 增加数据实时性。

## ops 执行步骤(精简版)

```bash
# 1. SSH 到 newvps (用 ssh puer-hk 别名, 永远不要 aliyun -p 16921)
ssh newvps

# 2. precheck
cd /opt/china-platform/frontend
bash <(curl -sS https://raw.githubusercontent.com/cscoheru/china-platform/main/deploy/static-export/precheck.sh)
# 期望: ALL PASS

# 3. 一键 redeploy
cd /opt/china-platform/frontend
bash <(curl -sS https://raw.githubusercontent.com/cscoheru/china-platform/main/deploy/static-export/deploy.sh)
# 或本地 rsync 后跑
bash /opt/china-platform/frontend/deploy/static-export/deploy.sh

# 4. 通知架构师 (CC 端) 做公网 curl 验收
# 期望 https://china.3strategy.cc/ 显示:
#   - banner: ✅ LIVE MODE — 28 省 2024 真实数据 + lineage 可溯
#   - 省 GDP 表: 31 行 (28 真实 + 3 缺失)
#   - 3 缺失省显式 "数据暂缺（公报源缺文）" badge
```

## 架构师端执行步骤(此包开发期,运维期不需要)

```bash
# 在架构师端 (此机) 跑:
cd /path/to/china-platform

# 1. 重新生成 JSON (mart SQL 改动后必跑)
python3 deploy/static-export/export-mart-data.py --strict
# 期望: OK: 31 rows -> frontend/data/mart_province_gdp_2024.json

# 2. 提交 + 推送
git add frontend/data/mart_province_gdp_2024.json
git commit -m "chore(660): refresh mart JSON (knife 660 Track B static export)"
git push origin main

# 3. 通知 ops 在 newvps 跑 deploy.sh
```

## 与 docs/53 §5 第 16 项 🔧 老命令链的差异

| 项 | 老 (446 baseline) | 新 (660 Track B) |
|---|---|---|
| 关键 env | `NEXT_PUBLIC_USE_MOCK=true` | `NEXT_PUBLIC_MART_DATA_PATH=./data/...` |
| USE_MOCK 默认 | 老 = `!== "false"` (default true) | 659 翻转为 `=== "true"` (default false) |
| 数据来源 | mock FastAPI / `MOCK_INDICATOR_LIST` | 静态 JSON (`mart_province_gdp_2024.json`) |
| FastAPI 依赖 | 必需 | 不必需 (Track B) |
| dbt 依赖 | 必需 (前端 fetch → FastAPI → mart view) | 不必需 (JSON 提前生成) |
| Postgres / SQLite | 必需 (mart view 从 observation 表) | 不必需 |

## 守门 (per 660 tasking)

1. **JSON 红线** (export-mart-data.py --strict):
   - 31 行 (28 真实 + 3 缺失)
   - 缺失省: gdp_total / gdp_growth / primary_gdp / secondary_gdp / tertiary_gdp 全 NULL (禁补零)
   - lineage_ruling = 'U6 2026-09-02' 全行
   - lineage_is_demo = 'false' 全行
2. **公网验收** (CC 端 curl 矩阵, 见 docs/85 §6):
   - A: HTTP 200
   - B: banner 含 "LIVE MODE"
   - C: 4 守门文案 ("28 省 2024 真实数据" / "官方 5 + 转载锚定 23" / "3 省源缺文" / "lineage 可溯")
   - D: JIANGSU mock sentinel 残留 = 0
   - E: data-mart-fixture = "0"
   - F: /public-extracts HTTP 200 + 4 锚点全命中
   - G: 本地 git HEAD = origin/main = github/main
   - H (新增): province-gdp-2024-table 渲染 31 行 (28 真实 + 3 缺失)
   - I (新增): 3 缺失省 "数据暂缺" badge 命中
   - J (新增): data-testid="province-row-{code}" 全 31 个命中
3. **测试**:
   - `frontend/smoke-check.py` §16 静态导出 4 守门
   - `tests/test_mart_static_export_s660.py` (新增, ≥8 cases)

## 不在 660 范围 (后续刀)

- ❌ FastAPI backend 部署 (Track A, 661+)
- ❌ 容器化 (preview 容器化择机另刀, per docs/53 §5 第 16 项)
- ❌ 换服务器 (沿用 newvps)
- ❌ 改 4 fixture 字节 (per docs/45 §1 + §6.2 + §7 守门)
- ❌ 宣布 O1 / Gate / M2 / M4 PASS

## 常见问题

**Q: 老命令链 (NEXT_PUBLIC_USE_MOCK=true) 还能用吗?**
A: 能,但仍走 mock 路径,看不到真数据。660 任务就是把它切掉。

**Q: CF 缓存怎么办? deploy.sh 完成后首页仍显示 demo?**
A: CF 橙云边缘节点可能缓存 8-27 旧 HTML (per 446 baseline 推测)。ops 在 CF dashboard 手动 Purge Cache (URL: china.3strategy.cc/) 或 nginx 层加 `Cache-Control: no-store`。

**Q: Track B JSON 不更新怎么办?**
A: 架构师端跑 `python3 deploy/static-export/export-mart-data.py --strict`,commit + push,然后 ops 跑 deploy.sh (会自动 git pull)。

**Q: FastAPI 还跑着的话,会冲突吗?**
A: 不会。Track B 不调 FastAPI,FastAPI 仍可独立运行。Track A 切回去只需要 unset `NEXT_PUBLIC_MART_DATA_PATH`。

— End README 20260902 —
