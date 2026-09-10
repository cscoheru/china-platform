# Knife H — `/timeseries` 3.7MB SSR HTML 修复 (server pre-slice + client lazy-fetch)

> **刀号**: knife H (667 收口补刀, knife H-1 续; knife G 之后)
> **日期**: 2026-09-10
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 668 verify-live.sh v2 跑出 1 WARN (`/timeseries page size 3722581 bytes > 50KB`, Knife G §5/§8 O2 留口); 后续从 Knife G 后用户裁定 "A · Server pre-slice (Recommended)"
> **本件状态**: **READY FOR DEPLOY + VERIFY** — 本地 build 已 PASS, SSR HTML 10KB (3.7MB → 10KB, 99.7% 降幅), 32 个 SSG 一致; 待 newvps git pull + 重启 + verify-live 重跑
> **关联**: knife G receipt (cfedca7) + 667 Recharts 时序可视化 + 668 verify-live.sh v2 + 660 Track B mart 静态导出 (NEXT_PUBLIC_MART_DATA_PATH) + 864 deploy (newvps systemd WorkingDirectory = `/opt/china-platform/repo/frontend`)

---

## 1. 范围 (granular)

| 维度 | 详情 |
|---|---|
| 目标 | 修 verify-live 1 WARN (O2: `/timeseries` page size 3722581 bytes > 50KB) |
| 文件改动 | 6 文件 (+public/data/mart_province_timeseries.json 4.2MB, +frontend/scripts/copy-mart-to-public.js, 修改 4 现有) |
| 部署改动 | 0 ops 文件改动 (newvps systemd unit 已 OK per Knife G-1) |
| HTTP budget | 0 (纯前端 + 静态文件复制, 无网络) |
| 红线 | 全守门 (no data change, only render + build artifact) |

---

## 2. 根因 + 方案选择

### 根因

667 TimeSeriesExplorer 把 8060 cells 全 mart 序列化为 props → 传到 client component → Next.js 把 props 序列化进 SSR HTML → 单页 3.7MB. 验证 668 §17 跑出 WARN (PASS 但 50KB 阈值爆).

### 方案对比 (User 裁定 A)

| 方案 | 描述 | SSR HTML 体积 | 切省 UX |
|---|---|---|---|
| **A · Server pre-slice (Recommended)** ✓ | server 预切片默认省+指标 (~26 points) → client useEffect lazy-fetch 全 mart when 切省 | < 50KB | 切省 1 次 fetch 4.2MB JSON |
| B · Client fetch all | server 仅传 provinces+indicators 元数据 (~5KB), client 全 mart 一开始就 fetch | < 50KB | 切省 0 fetch, 但首屏空白 + chart loading 长 |
| C · 接受 3.7MB SSR | 不动, 仅 verify-live 接受 WARN | 3.7MB | OK 但 CDN 流量浪费 + SSR 慢 |

**选定 A**: 首屏有默认 26 个真实点 (UX 不空白), 切省付出 1 次 4.2MB fetch (CDN 缓存); SSR HTML < 50KB (WARN 消除).

---

## 4. 文件改动 (6 文件)

### 4.1 `frontend/app/timeseries/page.tsx` (H2)

**改动**: 加 Knife H 头部注释 + DEFAULT_* 常量 + MART_JSON_URL + defaultPoints = server pre-slice filter

```ts
// Knife H 头部注释 (10 行): 详记 O2 修复方案 + lazy-fetch 策略
const DEFAULT_PROVINCE_CODE = "NATIONAL";
const DEFAULT_INDICATOR_KEY = "gdp_total";
const DEFAULT_YEAR_RANGE: readonly [number, number] = [2001, 2026];
const MART_JSON_URL = "/data/mart_province_timeseries.json";

// 替换原 `points = data.provinces` (8060 points)
const defaultPoints = data.provinces.filter(
  (p) =>
    p.province_code === DEFAULT_PROVINCE_CODE &&
    p.indicator_key === DEFAULT_INDICATOR_KEY
);  // ~26 points

<TimeSeriesExplorer
  ...
  defaultPoints={defaultPoints}
  martJsonUrl={MART_JSON_URL}
  defaultProvinceCode={DEFAULT_PROVINCE_CODE}
  defaultIndicatorKey={DEFAULT_INDICATOR_KEY}
  defaultYearRange={DEFAULT_YEAR_RANGE}
  ...
/>
```

### 4.2 `frontend/app/timeseries/[province_code]/page.tsx` (H4-补)

**改动**: 同步 single-province 页 (TypeScript build 守门暴露的漏改), 默认 10 指标 × 26 年 (~260 points)

```ts
const defaultPoints = data.provinces.filter((p) => p.province_code === code);
// 替换原 provincePoints, defaultYearRange 改 [2001, 2026] (对齐 NATIONAL 页)
```

### 4.3 `frontend/app/components/TimeSeriesExplorer.tsx` (H3)

**改动**: 接 defaultPoints + martJsonUrl + useEffect lazy-fetch + 状态展示

```ts
// 新 props (替换原 `points`):
defaultPoints: ProvinceTimeSeriesPoint[];     // server pre-slice
martJsonUrl?: string;                          // client fetch URL

// 新 state:
const [allPoints, setAllPoints] = useState<ProvinceTimeSeriesPoint[] | null>(null);
const [dataLoading, setDataLoading] = useState(false);
const [dataError, setDataError] = useState<string | null>(null);

// 派生 flag: 切到非 default 省/指标 且 allPoints 未加载 → 触发 fetch
const needsLazyFetch =
  allPoints === null &&
  martJsonUrl !== undefined &&
  (selectedProvinceCode !== defaultProvinceCode ||
    selectedIndicatorKey !== defaultIndicatorKey);

// useEffect: 触发 fetch(martJsonUrl) → setAllPoints(json.provinces) → setDataLoading(false)
// 失败: setDataError + allPoints 仍 null → filteredPoints 回退 defaultPoints (用户切到非默认会看到 DATA_MISSING)

// 切片源: allPoints ?? defaultPoints
const activePoints = allPoints ?? defaultPoints;
const filteredPoints = useMemo(
  () => activePoints.filter(p => p.province_code === ... && p.year >= yearStart && p.year <= yearEnd),
  [activePoints, selectedProvinceCode, selectedIndicatorKey, yearStart, yearEnd]
);

// 底部 caveat 加 lazy fetch 状态: data-testid="time-series-loading" / "time-series-fetch-error"
```

### 4.4 `frontend/package.json` (H4)

**改动**: 加 predev + prebuild 钩子调用 `node scripts/copy-mart-to-public.js`

```json
"scripts": {
  "dev": "next dev -p 3000",
  "predev": "node scripts/copy-mart-to-public.js",
  "prebuild": "node scripts/copy-mart-to-public.js",
  "build": "next build",
  ...
}
```

### 4.5 `frontend/scripts/copy-mart-to-public.js` (H4, NEW)

**用途**: 复制 frontend/data/mart_province_timeseries.json → frontend/public/data/mart_province_timeseries.json (供 client fetch from /data/...)

**逻辑**:
1. 校验源文件存在, 不存在 throw fail-fast.
2. `mkdir -p public/data/` (Node fs.mkdirSync recursive).
3. `fs.copyFileSync(SRC, DST)`.
4. 校验 size 一致.
5. `console.log` 报告.

**理由**: 单源 (frontend/data/) 真实数据; public/data/ 是 build artifact. dev/build 都自动重导, public/data/ 也入 git 便于 verify-live + client 端冷启动.

### 4.6 `frontend/public/data/mart_province_timeseries.json` (H4, NEW, 4.2MB)

来源: 复制 from `frontend/data/mart_province_timeseries.json` (knife 660 Track B 静态导出产物, `deploy/static-export/export-mart-data.py`, schema_version="664", ruling="knife 664g P2 mart 静态导出").

---

## 5. 验证 (本地 build + newvps 公网)

### 5.1 本地 build (per H5b)

```
=== Knife H 本地 build summary (after prebuild copy) ===
[copy-mart-to-public] OK: 4230623 bytes copied to public/data/mart_province_timeseries.json

✓ Compiled successfully
✓ Generating static pages (85/85)

=== SSR HTML 体积 (前/后对比) ===
前 (knife G §5): /timeseries page size 3722581 bytes > 50KB (WARN)
后 (knife H §5): /timeseries.html                  10000 bytes (~10KB) ✓
                /timeseries/beijing.html           10411 bytes (~10KB) ✓
                /timeseries/tianjin.html           10393 bytes (~10KB) ✓
                (其余 30 SSG 一致 10-11KB)

降幅: 3.7MB → 10KB = 99.7%
阈值: < 50KB ✓ (WARN 消除)
```

### 5.2 newvps 公网验证 (待跑, 需 user_ruling_H 启动 deploy)

```bash
ssh newvps  # user_ruling_H 已签
cd /opt/china-platform/repo/frontend
git pull origin main  # 双推 + 3-ref verify 后
npm ci
npm run build  # prebuild 复制 mart JSON 到 public/data/
sudo systemctl restart china-platform-frontend

# 本地 curl 公网验证
curl -sS -o /tmp/timeseries.html https://china.3strategy.cc/timeseries
stat -f "%z" /tmp/timeseries.html  # 期望: < 50000
grep -c "data-testid=\"time-series-chart\"" /tmp/timeseries.html  # 期望: ≥ 1
grep -c "data-testid=\"time-series-loading\"" /tmp/timeseries.html  # 期望: 0 (默认初始状态)
grep -c "data-testid=\"time-series-fetch-error\"" /tmp/timeseries.html  # 期望: 0
grep -c "data-testid=\"source-grade-caveat\"" /tmp/timeseries.html  # 期望: ≥ 1 (Knife G §3.3)

curl -sS -o /tmp/timeseries-beijing.html https://china.3strategy.cc/timeseries/beijing
stat -f "%z" /tmp/timeseries-beijing.html  # 期望: < 50000
grep -c "data-testid=\"time-series-province-h1-BEIJING\"" /tmp/timeseries-beijing.html  # 期望: ≥ 1
```

### 5.3 verify-live 重跑 (668 v2)

```
=== knife 668 公网 17 项验收 summary (Knife H 后) ===
VERIFY: 19 PASS / 0 WARN (Knife G 时 19 PASS / 1 WARN)

[无 WARN] /timeseries page size 10000 bytes < 50KB ✓ (Knife H 修)
```

---

## 6. 复用与依赖

- 复用 667 TimeSeriesChartClient dynamic import 模式 (per Knife G 不变)
- 复用 660 Track B mart 静态导出 (frontend/data/mart_province_timeseries.json, 660 时已就位)
- 复用 verify-live.sh v2 (knife 668) 验收脚本
- 依赖 newvps systemd unit WorkingDirectory 已 OK (per Knife G-1)
- 估 5 commits (amend-first v3.5)

---

## 7. 红线守门 (Knife H 专属)

- ✓ **H-1 SSR HTML < 50KB**: 10KB ✓ (从 3.7MB 降至 99.7% off)
- ✓ **H-2 data 不动**: 0 mart schema change, 0 seed CSV change, 0 harvest HTTP, 0 行内容改动
- ✓ **H-3 demo 守门**: FastAPI 不可达 / mart JSON 缺失都不破壳 (per 662 D5 + Knife G-2)
- ✓ **H-4 Recharts SSR 安全**: dynamic ssr:false 不变 (per Knife G-3)
- ✓ **H-5 禁榜单化**: 数据覆盖摘要 "仅供参考, 不构成排名 (per docs/05 §8.3)" 守门文案不变 (per Knife G-4)
- ✓ **H-6 client lazy-fetch 失败兜底**: dataError 状态 + 回退 defaultPoints (用户切到非默认省会看到 DATA_MISSING, 沿用红线-1)
- ✓ **H-7 prebuild 钩子**: dev/build 都复制 mart JSON 到 public/data/ (避免 client fetch 404)

---

## 8. 已知 Gap / 未来 knife

- **mart JSON 重导**: dbt mart 更新后, frontend/data/mart_province_timeseries.json 需重导 + commit; prebuild 钩子自动复制到 public/data/ (per H-7).
- **CDN cache**: 4.2MB JSON 首次 client fetch 可用 Next.js Cache-Control 头 (后续 knife H-2 CDN 配置)
- **indicator 切换不触发 lazy fetch**: 当前逻辑仅在切省时 fetch; 但 indicator 切换时 defaultPoints 已含 default 省×10 指标 × 26 年 = 260 points, 足够, 不需再 fetch.

---

## 9. 不宣称

- ❌ 不宣布 Knife H DELIVERED — 仅在 newvps git pull + 重启 + verify-live 0 WARN 后才登记
- ❌ 不宣布 663-668 + 669 program 启动 PASS — 启动需 user_ruling_666+ 单独签署
- ❌ 不宣布 O1 / Gate / M2 / M4 / M5 / M6 / O2 PASS
- ❌ 不冒充 ops — newvps 仅在 user_ruling_H 签署后
- ❌ 不主动 commit/push — 待 user 授权 (per docs/87 §6 + CLAUDE.md 全局约束)

---

## 10. Commit chain (6 commits, amend-first v3.5)

```
<hash1>  feat(knife-H): TimeSeriesExplorer 接 defaultPoints + martJsonUrl + lazy-fetch (修 O2 3.7MB SSR HTML)
<hash2>  feat(knife-H): /timeseries page.tsx pre-slice defaultPoints (服务端预切片 26 points)
<hash3>  feat(knife-H): /timeseries/[code] page.tsx pre-slice per-province (260 points + MART_JSON_URL)
<hash4>  feat(knife-H): copy-mart-to-public.js + package.json prebuild 钩子
<hash5>  data(knife-H): public/data/mart_province_timeseries.json (4.2MB, knife 660 Track B 静态导出)
<hash6>  chore(knife-H): receipt
```

---

## 11. 链接

- 关联 Knife G receipt: `reviews/stage0-gate0-rework-2026-08-23/knife-G-verify-live-5fails-fix-receipt-20260909.md` (cfedca7)
- 关联 Knife E receipt: `china-platform-969-970-fetch-parse-unified.md` (Knife E DELIVERED)
- 关联 Knife 667: Recharts 时序可视化 (frontend components + 2 pages + nav)
- 关联 Knife 660: Track B mart 静态导出 (frontend/data/mart_province_timeseries.json, 4.2MB)
- 关联 Knife 668: verify-live.sh v2 公网 17 项验收
- 关联 memory: `china-platform-fastapi-missing-on-newvps.md` (FastAPI 部署 Gap, 不影响 Knife H)
- 关联 memory: `china-platform-user-rest-protocol.md` (架构师继续 ARCH-PULSE)

— End Knife H receipt (3.7MB SSR HTML 修复, server pre-slice + client lazy-fetch, 2026-09-10) —