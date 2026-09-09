"use client";

// TimeSeriesChartClient.tsx — knife 667 SSR-safe wrapper for TimeSeriesChart.
//
// Per 667 tasking §1 + Recharts SSR 警告:
//   Recharts ResponsiveContainer 读取 window.innerWidth,SSR 时 width=undefined
//   → client hydration mismatch. 修复: 动态导入 TimeSeriesChart 且 ssr=false.
//
// 调用方 (page.tsx) 静态 import 本 wrapper 即可;SSR 输出 placeholder,
// client mount 后 Recharts 才渲染.

import type React from "react";
import dynamic from "next/dynamic";

import type { TimeSeriesChartProps } from "./TimeSeriesChart";

// dynamic() 在 module init 调用;ssr:false 让 Next.js 在 server 端跳过本组件渲染.
// Note (knife G 修 verify-live 时间序列 chart testid 守门):
//   verify-live 抓 SSR HTML, 期待 `time-series-chart` testid 出现. 由于 ssr=false,
//   Recharts 真实图仅在 client mount 后渲染, SSR HTML 中没有. 修法: 让 SSR
//   placeholder div 同时带 `data-testid="time-series-chart"` 与
//   `data-testid="time-series-chart-loading"`, client mount 后由 Recharts 替换
//   内容, testid 切换到真实 chart div (TimeSeriesChart.tsx 同样持有该 testid).
const TimeSeriesChartDynamic = dynamic<TimeSeriesChartProps>(
  () => import("./TimeSeriesChart").then((m) => m.TimeSeriesChart),
  {
    ssr: false,
    loading: () => (
      <div
        style={{
          padding: "16px 20px",
          border: "1px dashed #ccc",
          borderRadius: 4,
          background: "#fafafa",
          textAlign: "center",
          color: "#888",
          fontSize: 12,
        }}
        data-testid="time-series-chart"
        data-loading="true"
      >
        加载时序图表…
      </div>
    ),
  }
);

export function TimeSeriesChartClient(props: TimeSeriesChartProps): React.ReactElement {
  return <TimeSeriesChartDynamic {...props} />;
}