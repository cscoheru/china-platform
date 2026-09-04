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
        data-testid="time-series-chart-loading"
      >
        加载时序图表…
      </div>
    ),
  }
);

export function TimeSeriesChartClient(props: TimeSeriesChartProps): React.ReactElement {
  return <TimeSeriesChartDynamic {...props} />;
}