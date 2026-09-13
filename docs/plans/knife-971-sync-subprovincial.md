# knife 971 — sync dev→prod 副省级 city mart 数据 (2026-09-13)

> **刀号**: 971 (sub-knife 1/1, sync 模式)
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: H-series H1+H2+H3 全部 DONE+DEPLOYED (commit b6eba49); dev (127.0.0.1:55440 cegr_test) 87 city / prod (newvps china-platform-pg cegr_test) 79 city, **prod 缺 8 副省级 city**
> **本件状态**: **READY FOR EXECUTION** — 等 user 选定 sync 范围 (A/B/C 三选一) + user_ruling_666+ 授权 ops (sync 涉及 prod 数据库写)
> **关联**: knife 669b-i 8 batch + K669a-2020 副省级 attribution, K669fix-b-2020, K669b-i-dongguan-no-bulletin-2020 (8 lineage_ruling 类)

---

## Context (为什么做这件事)

### 用户质询 (2026-09-13)

> 「下一刀」 → 选定「修 DONGGUAN」(修 10 slug 中仅剩的 1 城 live)

### 直答 + 调查发现

DONGGUAN mart 实际**已经在 dev 部署 60 cells** (knife 669b-i-dongguan-no-bulletin-2020 + parse-2021/22/23/25 + batch1-2024 + pending-2026 lineage), 但前端 → 公网 → FastAPI 返 404 CITY_NOT_FOUND。

根因排查:
- `dev` cegr_mart.mart_city_timeseries: **87 city** (DONGGUAN 60 cells)
- `prod` cegr_mart.mart_city_timeseries: **79 city** (DONGGUAN 0 cells)
- dev→prod 历史 sync 漏了 **8 副省级 city** (K669a-2020 attribution 时期 + K669b-i dongguan/xiamen/foshan/suzhou/wuxi/dalian/qingdao sub-knife 期间未推 prod)

### 8 副省级 详细 (dev mart 现状, 守 5 红线 PASS):

| city_code | year | cells | real/miss | lineage_ruling |
|---|---|---|---|---|
| FUJIAN_XIAMEN | 2020 | 10 | 0/10 | K669b-i-xiamen-no-bulletin-tag-2020 |
| FUJIAN_XIAMEN | 2021-2025 | 50 | 39/11 | K669b-i-xiamen-parse-{year} (5 versions) |
| FUJIAN_XIAMEN | 2024 | 10 | 7/3 | K669b-i-batch1-parse-2024 |
| FUJIAN_XIAMEN | 2026 | 10 | 0/10 | pending |
| GUANGDONG_DONGGUAN | 2020 | 10 | 0/10 | K669b-i-dongguan-no-bulletin-2020 |
| GUANGDONG_DONGGUAN | 2021-2025 | 50 | 47/3 | K669b-i-dongguan-parse-{year} (5 versions) |
| GUANGDONG_DONGGUAN | 2024 | 10 | 10/0 | K669b-i-batch1-parse-2024 |
| GUANGDONG_DONGGUAN | 2026 | 10 | 0/10 | pending |
| GUANGDONG_FOSHAN | 2020 | 10 | 0/10 | K669fix-b-2020 |
| GUANGDONG_FOSHAN | 2021-2025 | 50 | 0/50 | K669b-i-batch3-parse-{year} (5 versions) |
| GUANGDONG_FOSHAN | 2026 | 10 | 0/10 | pending |
| JIANGSU_SUZHOU | 2020 | 10 | 0/10 | K669b-i-suzhou-no-bulletin-djs-2020 |
| JIANGSU_SUZHOU | 2021/22/24/25 | 40 | 35/5 | K669b-i-suzhou-parse-{year} (4 versions) |
| JIANGSU_SUZHOU | 2023 | 10 | 0/10 | K669b-i-suzhou-no-bulletin-2023 (hongheiku 0 entry 守红线-3) |
| JIANGSU_SUZHOU | 2024 | 10 | 8/2 | K669b-i-batch1-parse-2024 |
| JIANGSU_SUZHOU | 2026 | 10 | 0/10 | pending |
| JIANGSU_WUXI | 2020 | 10 | 0/10 | K669b-i-wuxi-no-bulletin-djs-2020 |
| JIANGSU_WUXI | 2021/23/24/25 | 40 | 35/5 | K669b-i-wuxi-parse-{year} (4 versions) |
| JIANGSU_WUXI | 2022 | 10 | 0/10 | K669b-i-wuxi-no-bulletin-2022 (hongheiku 0 entry 守红线-3) |
| JIANGSU_WUXI | 2024 | 10 | 9/1 | K669b-i-batch1-parse-2024 |
| JIANGSU_WUXI | 2026 | 10 | 0/10 | pending |
| LIAONING_DALIAN | 2020 | 10 | 0/10 | K669b-i-dalian-no-bulletin-2020 |
| LIAONING_DALIAN | 2021-2025 | 50 | 38/12 | K669b-i-dalian-parse-{year} (5 versions) |
| LIAONING_DALIAN | 2024 | 10 | 8/2 | K669b-i-batch1-parse-2024 |
| LIAONING_DALIAN | 2026 | 10 | 0/10 | pending |
| SHANDONG_QINGDAO | 2020 | 10 | 6/4 | K669b-i-qingdao-parse-2020 |
| SHANDONG_QINGDAO | 2021-2025 | 50 | 29/21 | K669b-i-qingdao-parse-{year} (5 versions) |
| SHANDONG_QINGDAO | 2026 | 10 | 0/10 | pending |
| ZHEJIANG_NINGBO | 2020 | 10 | 0/10 | K669fix-b-2020 |
| ZHEJIANG_NINGBO | 2021-2025 | 50 | 44/6 | K669b-i-batch2-parse-{year} (5 versions) |
| ZHEJIANG_NINGBO | 2026 | 10 | 0/10 | pending |
| **TOTAL** | 7 year | **560 cells** | **249 real / 311 miss** | 8 lineage_ruling 类 |

### 守 5 红线 PASS (已 dev 实证):

- ✓ 4 直辖市禁 (BEIJING_BEIJING/SHANGHAI_SHANGHAI/TIANJIN_TIANJIN/CHONGQING_CHONGQING): 0 cells in dev mart_city_timeseries
- ✓ 红线-1 (2001-2019 历史年): dev mart 无 2001-2019 cells
- ✓ 红线-2 (2026 全 DATA_MISSING): 8 城 2026 都 pending = DATA_MISSING
- ✓ 红线-3 (hongheiku 0 entry 禁补零): SUZHOU 2023 + WUXI 2022 等都标 no-bulletin, value=NULL, status=DATA_MISSING
- ✓ 红线-7 (无 4 直辖市): dev mart 守

### 前端 10 slug (Cursor 锁定清单) 受影响分析:

- 江苏 4 slug: nanjing/suzhou/wuxi/nantong
  - **suzhou** 在 prod 缺 → 公网 /cities/suzhou 走 fallback to demo (B-OPT-NT 之前的 fallback 路径)
  - **wuxi** 在 prod 缺 → 同上
  - nantong 在 prod (no-bulletin K669a-2020 attribution) → 走 EmptyState (B-OPT-NT 修复后正确行为)
  - nanjing 在 prod → live mart ✓
- 浙江 3 slug: hangzhou/ningbo/wenzhou
  - **ningbo** 在 prod 缺 → fallback to demo
  - hangzhou/wenzhou 在 prod → live mart ✓
- 广东 3 slug: guangzhou/shenzhen/dongguan
  - **dongguan** 在 prod 缺 → fallback to demo (B-OPT-NT 触发 404 → EmptyState)
  - guangzhou/shenzhen 在 prod → live mart ✓

**前端 10 slug 中 prod mart 缺数据 = 4 城** (suzhou/wuxi/ningbo/dongguan). 修这 4 城 → 公网 9 slug 走 live (nantong 仍 EmptyState 红线-3).

### 修正路径 = 3 选项 (等 user 选)

---

## 选项 A: sync 前端 4 slug 优先 (suzhou/wuxi/ningbo/dongguan) [推荐]

### 范围

4 城 × 7 年 × 10 指标 = **280 cells**. 直接修前端可见 4 slug (Cursor 锁定清单), 公网 9/10 slug 走 live.

### 红线守门 (sync 专属)

- ✓ **UPDATE-ONLY (不 DROP 不 TRUNCATE)**: `INSERT ON CONFLICT (city_code, indicator_key, year) DO UPDATE SET value=EXCLUDED.value, status=EXCLUDED.status, missing_reason=EXCLUDED.missing_reason, lineage_source_type=EXCLUDED.lineage_source_type, lineage_origin=EXCLUDED.lineage_origin, lineage_ruling=EXCLUDED.lineage_ruling, lineage_is_demo=EXCLUDED.lineage_is_demo`
- ✓ **守历史溯源守恒**: 若 prod 已有相同 (city_code, indicator_key, year) 行, 新 lineage_ruling 覆盖旧 (守 user R671 "sync dev→prod 应覆盖", 因为 dev 已是 verified state, prod 应 sync)
- ✓ **dry-run mode**: `--dry-run` 跑 count + diff 不写 prod
- ✓ **count verify**: sync 前 count dev, sync 后 count prod, 等于
- ✓ **4 直辖市禁**: 8 城都不含 4 直辖市 (守红线-7), 写 SQL 时仍加 WHERE city_code NOT IN ('BEIJING_BEIJING',...) 兜底
- ✓ **year 范围 2020-2026**: WHERE year BETWEEN 2020 AND 2026 (守红线-1+2)

### 关键文件改动 (3 文件, 1 新 + 1 新 + 1 部署)

| 路径 | 类型 | 改动 |
|---|---|---|
| `scripts/sync_dev_to_prod_subprovincial.py` | **A** | 280 cells sync, UPDATE-ONLY psycopg2 pattern, dry-run 模式 + count verify + lineage_ruling 守门 |
| `scripts/verify_sync_subprovincial_prod.py` | **A** | 5/5 红线 PASS verify (8 city distinct / 4 city × 7 year × 10 indicator = 280 cells / 4 直辖市 0 / 2001-2019 + 2026 全空 / lineage_ruling K971 sync 标记) |
| newvps deploy | **deploy** | `docker exec china-platform-pg psql -U postgres -d cegr_test -f scripts/verify_sync_subprovincial_prod.sql` 或 SSH newvps 跑 verify script |
| (optional) receipt | **chore** | `reviews/stage0-gate0-rework-2026-08-23/971-sync-subprovincial-receipt-20260913.md` |

### 预估 commits (沿用 amend-first v3.5)

```
971 (3 commits):
  <hash1>  feat(971): sync_dev_to_prod_subprovincial.py — UPDATE-ONLY psycopg2 pattern, 4 city × 7 year × 10 indicator = 280 cells
  <hash2>  feat(971): verify_sync_subprovincial_prod.py — 5/5 红线 PASS verify
  <hash3>  chore(971): receipt (8 副省级 sync dev→prod DELIVERED, 280/280 PASS, 4 直辖市 0, 2020前+2026 守红线, lineage_ruling 守门, sync 范围 = 4 slug 优先)
```

预估治理集: 3 commits + 1 receipt, 公网可见变化 (4 slug 从 fallback → live).

预估部署耗时:
- sync script 写: ~15min (psycopg2 pattern 沿用 batch3 + single-%→%% escape fix)
- verify script 写: ~10min (5 红线 PASS 沿用 batch3 verify template)
- newvps ssh 跑 sync + verify: ~5min
- 公网 smoke test 4 城: ~10min
- 接收 + commit: ~5min

### 验证步骤

```bash
# newvps (per user_ruling_666+ SSH ops 授权)
ssh newvps 'docker exec -i china-platform-pg psql -U postgres -d cegr_test < scripts/sync_dev_to_prod_subprovincial.sql'
# 期望: INSERT 0 280 (UPDATE 0 because prod 原本无这些 cell)

ssh newvps 'docker exec china-platform-pg psql -U postgres -d cegr_test -c "SELECT count(*) FROM cegr_mart.mart_city_timeseries WHERE city_code IN ('"'"'JIANGSU_SUZHOU'"'"','"'"'JIANGSU_WUXI'"'"','"'"'ZHEJIANG_NINGBO'"'"','"'"'GUANGDONG_DONGGUAN'"'"');"'
# 期望: 280 (4 city × 7 year × 10 indicator)

# 公网 smoke (curl)
for slug in suzhou wuxi ningbo dongguan; do
  curl "https://china.3strategy.cc/cities/$slug" | grep -oE 'data-testid="(city-timeseries-live|city-empty-state|mart_city_demo)"' | sort -u
  # 期望 suzhou/wuxi/ningbo/dongguan = city-timeseries-live
done

# 公网 API 直接验
curl "https://china.3strategy.cc/api/city-timeseries/JIANGSU_SUZHOU?year_start=2024&year_end=2024" | jq '.points_count'
# 期望: 10 (10 indicators × 1 year)
```

### 不宣称

- ❌ 不宣布 971 PASS — 仅 DELIVERED + SYNC + VERIFIED + DBL-PUSHED 后登记
- ❌ 不冒充 ops — newvps sync 仅 user_ruling_666+ 签署后
- ❌ 不回写 ops 文件
- ❌ 不爬网 — 0 HTTP (sync 模式, 数据已 dev 验证)
- ❌ 不 DROP / 不 TRUNCATE prod mart 表 — 仅 INSERT ON CONFLICT DO UPDATE 受影响行

---

## 选项 B: sync 全部 8 副省级 (含 frontend 无 slug 的 4 城)

### 范围

8 城 × 7 年 × 10 指标 = **560 cells**. 修 4 slug + 扩 4 副省级 mart-only city (xiamen/foshan/dalian/qingdao).

### 优点

- dev→prod 完全一致 (79+8=87 city, 守一致)
- 4 副省级未来若加入前端 slug 列表 (解除锁定后) 已有数据
- 历史同步遗漏完整修复

### 缺点

- 4 副省级 (xiamen/foshan/dalian/qingdao) 修了前端无可见 UI 反馈
- 数据规模扩 2 倍 (560 vs 280), 增加 sync 风险 surface
- 涉及 8 城 ops 操作, user_ruling_666+ 授权级别更高

### 红线守门: 同 A (UPDATE-ONLY + dry-run + 5 红线 PASS)

### commits: 同 A (3 commits + 1 receipt)

### 验证: 同 A (8 城 smoke + 8 city count verify)

---

## 选项 C: 仅 sync DONGGUAN (1 城) [user 原选, 但范围偏窄]

### 范围

1 城 × 7 年 × 10 指标 = **60 cells**. 仅修前端 10 slug 中 dongguan.

### 优点

- 最小 ops surface (60 cells, 1 城)
- 守 user 原选最小范围

### 缺点

- 仍有 3 slug (suzhou/wuxi/ningbo) 公网走 fallback to demo
- dev→prod 仍有 7 城同步遗漏 (xiamen/foshan/suzhou/wuxi/dalian/qingdao/ningbo)
- 同一 root cause (dev→prod sync 漏 8 副省级) 没彻底修

---

## 关键文件 (实施时查阅)

**Backend (sync 源)**:
- `dev cegr_mart.mart_city_timeseries` — 8 副省级 560 cells (守 5 红线 PASS)

**Prod (sync 目标)**:
- `china-platform-pg` (newvps) `cegr_mart.mart_city_timeseries` — 79 city / 缺 8 副省级

**已有工具 (复用)**:
- `scripts/load_seed_and_mart_prod.py` — 664 load_seed_and_mart_prod.py, bypass dbt CLI for newvps prod deployment (host port 5432 mapping); 但 china-platform-pg 现在无 host port mapping, 必须 `docker exec china-platform-pg psql` 而非 host psql
- `scripts/apply_mart_city_669b_i_batch3.py` — psycopg2 INSERT ON CONFLICT DO UPDATE pattern (UPDATE-ONLY 不 DROP), single-%→%% escape fix, OR-clause params binding fix (复用这 3 模式)
- `scripts/verify_mart_city_669b_i_batch3.py` — 30+ 红线 PASS verify template (复用 Section 1-5)

**Frontend (验证)**:
- `/cities/{suzhou,wuxi,ningbo,dongguan}` 公网 443 → 8001 → FastAPI → postgres → 200 + city-timeseries-live testid 命中
- `/` H3 数据完整度列: 4 slug 从 miss → real 计数上升

---

## P2 红线延续 (沿用 knife 663-668/669, 不变)

- **多指标数据只准来自 mart 导出** (sync dev→prod, dev 已 verified)
- **缺失 city / 缺失年 禁补零** (sync 8 城全 DATA_MISSING 行 value=NULL 不变)
- **不爬网** (sync 模式, 数据已 dev 验证, 0 HTTP)
- **amend-first 沿用** (3 commits: sync + verify + receipt)
- **mock 链文件不删** (mart_city_demo.ts 保留)
- **不主动 commit/push** (待 user 授权)
- **不冒充 ops** (newvps sync 仅 user_ruling_666+ 签署后)
- **不宣称任何 PASS** (仅 DELIVERED + SYNC + VERIFIED + DBL-PUSHED 后登记)
- **不 DROP / 不 TRUNCATE** (UPDATE-ONLY, 守历史溯源守恒)
- **docs/81 零改动** (knife 971 改 scripts/, 不动 docs/)

---

## user_ruling_971 签署清单 (CRITICAL)

### 待 user 签署 (per 当前会话 2026-09-13 调查发现)

- [ ] **范围选 A / B / C** (4 slug 优先 / 8 副省级全 / 1 城 DONGGUAN)
- [ ] **ops 授权 user_ruling_666+** (sync 涉及 prod 数据库写, 沿用 666 SSH ops 授权)
- [ ] **commit + push 授权** (沿用 Codex 提交铁律 2026-09-05, push via Clash proxy)

---

## 链接

- 关联 knife H-series H1 (8d1e399) — /api/city-timeseries/{city_code} 端点
- 关联 knife 669b-i umbrella — 8 batch × 35 city (其中 8 副省级 dev 已 verify 但 prod 漏 sync)
- 关联记忆: [[china-platform-fastapi-missing-on-newvps]] (FastAPI 在 newvps 实证)
- 关联记忆: [[china-platform-rebase-before-push]] (双推前 fetch + rebase 流程)

— End knife 971 sketch (sync dev→prod 副省级 city, 2026-09-13, 等 user 选范围 + user_ruling_666+ 授权) —
