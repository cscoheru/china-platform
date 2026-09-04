// 667 P2 时序可视化 · 全国总览页 `/timeseries`.
//
// Per 667 tasking §1: 全 31 省 + NATIONAL 数据折线图 (默认选省 = NATIONAL).
// Per docs/87 §3.2 P2 路线 + user_ruling_667: Recharts 仅用于时序折线 (新增红线-4).
// Per docs/05 §8.3 + 红线-1/2: 不排名/榜单化;DATA_MISSING 年份虚线 + tooltip.
//
// 设计:
//   - Server component 读 mart JSON (Track B 静态导出, no FastAPI 依赖).
//   - 将数据透传给 client component <TimeSeriesExplorer />;SSR 阶段不渲染 Recharts
//     (per Recharts SSR warning; 客户端 dynamic import 解决).
//   - generateStaticParams 预生成 (empty array = all clients use single route since
//     selected province is client-side state;但为了 ISR cache hint, 我们仍然静态化
//     /timeseries).
//
// 守门:
//   - mart 未配置 → 渲染 "数据未配置" placeholder (graceful degradation).
//   - 31 省代码 + NATIONAL = 32 slug; 沿用 docs/46 §3.1 守门清单.

import {
  listProvincesWithTimeSeries,
  listIndicatorsWithTimeSeries,
  listSourceGradesNational,
} from "../../lib/api";
import { getProvinceTimeSeriesStatic } from "../../lib/mart-static";
import { TimeSeriesExplorer } from "../components/TimeSeriesExplorer";

export default function TimeSeriesOverviewPage(): React.ReactElement {
  const data = getProvinceTimeSeriesStatic();
  if (!data) {
    return (
      <section>
        <h1 data-testid="timeseries-h1">时序可视化</h1>
        <p style={{ color: "#b45309" }} data-testid="timeseries-mart-missing">
          ⚠ Mart JSON 未配置. 请先运行 <code>deploy/static-export/export-mart-data.py</code>{" "}
          导出 <code>mart_province_timeseries.json</code>, 或设置环境变量{" "}
          <code>NEXT_PUBLIC_MART_DATA_PATH</code>。
        </p>
      </section>
    );
  }

  const provinces = listProvincesWithTimeSeries();
  const indicators = listIndicatorsWithTimeSeries();
  const nationalSummary = listSourceGradesNational();
  const points = data.provinces;

  return (
    <section data-testid="timeseries-overview-page">
      <h1 data-testid="timeseries-h1">
        时序可视化 · 全国总览（31 省 + NATIONAL 锚）
      </h1>
      <p style={{ color: "#666", fontSize: 13 }} data-testid="timeseries-intro">
        5 现 + 5 增量指标 × 26 年 (2001–2026) × 31 省 + NATIONAL = 8060 cells mart 数据。
        DATA_MISSING 年份 (2001–2019 / 2026 / 缺失省) 在图表中显示为虚线 + tooltip
        提示, 不补零 (per docs/87 §3.2 + 红线-1/2).
      </p>

      <TimeSeriesExplorer
        provinces={provinces}
        indicators={indicators}
        points={points}
        perProvinceSummary={nationalSummary}
        nationalSummary={nationalSummary}
        defaultProvinceCode="NATIONAL"
        defaultIndicatorKey="gdp_total"
        defaultYearRange={[2020, 2025]}
      />

      <section style={{ marginTop: 24 }} data-testid="timeseries-coverage">
        <h2 style={{ fontSize: 16 }}>数据覆盖摘要</h2>
        <p style={{ fontSize: 13, color: "#555", lineHeight: 1.6 }}>
          完整 mart 含 {data.total_rows} 行 (31 省 × 10 指标 × 26 年);
          实际采集数据来自 hongheiku 公报 (per 665 program 1435+ cells) +
          5 OFFICIAL_INTAKED 省 (京/沪/鲁/鄂/川 per 660 baseline) + 3 省升级
          (粤/苏/浙 per 666 Option B).{" "}
          <strong>仅供参考, 不构成排名 (per docs/05 §8.3)</strong>;{" "}
          详见{" "}
          <a href="/research/m1-series" style={{ color: "#0969da" }}>
            M1 验收面
          </a>
          .
        </p>
      </section>
    </section>
  );
}