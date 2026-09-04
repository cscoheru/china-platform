"use client";

// TimeSeriesChart.tsx — knife 667 Recharts 时序折线图.
//
// Per 667 tasking §1 + 红线-4 (Recharts 仅用于时序折线, 禁榜单/排名):
//   单指标 × 单省份 × [yearStart, yearEnd] 时序;不叠加多省份对比.
// Per 红线-1/2 (DATA_MISSING 守门): null values → 折线断开 (connectNulls=false);
//   DATA_MISSING 年份在 X 轴显示灰色虚线刻度 + tooltip 显示 "暂无数据 (DATA_MISSING)".
// Per 红线 (禁补零): 绝不把 null 替换为 0;绝不"平滑"插值.
//
// SSR 警告: Recharts ResponsiveContainer 读 window.innerWidth;Next.js 14 SSR 时
// width=undefined → hydration mismatch. 修复: 调用方用 dynamic(import, { ssr: false })
// 引入本组件,不要在 import chain 中静态 import.
//
// 实现:
//   - 单一 LineChart + Line (实线, value != null 点)
//   - connectNulls={false} 让 null 年份自然断线 (per 红线-1/2)
//   - ReferenceLine (gray dashed) 在 DATA_MISSING 年份 X 轴标注
//   - Tooltip 显示 year / value / unit / lineage_source_type
//   - Y 轴: 自动 scale;空值时显示 "—" 占位

import type React from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipContentProps,
} from "recharts";

import type { ProvinceTimeSeriesPoint } from "../../lib/types";

export interface TimeSeriesChartProps {
  /** Indicator key (e.g. 'gdp_total'). Used for axis label + tooltip header. */
  indicatorKey: string;
  /** Indicator 中文 label (e.g. '地区生产总值'). */
  indicatorLabel: string;
  /** 单位 (e.g. '亿元' / '%' / '元');null 不显示. */
  unit: string | null;
  /** 完整时序点(包含 null value = DATA_MISSING 年份). */
  points: ProvinceTimeSeriesPoint[];
  /** 折线颜色;缺省 "#0969da" (GitHub blue). */
  color?: string;
  /** 容器高度 px; 缺省 320. */
  height?: number;
}

const DEFAULT_COLOR = "#0969da";

interface ChartRow {
  year: number;
  value: number | null;
  status: string | null;
  lineage_source_type: string;
  missing_reason: string | null;
}

export function TimeSeriesChart({
  indicatorKey,
  indicatorLabel,
  unit,
  points,
  color = DEFAULT_COLOR,
  height = 320,
}: TimeSeriesChartProps): React.ReactElement {
  // 过滤 + 排序 points (按 year asc).
  const rows: ChartRow[] = [...points]
    .sort((a, b) => a.year - b.year)
    .map((p) => ({
      year: p.year,
      value: p.value,
      status: p.status,
      lineage_source_type: p.lineage_source_type,
      missing_reason: p.missing_reason,
    }));

  // DATA_MISSING 年份列表 (status='DATA_MISSING' 或 value=null).
  const missingYears = rows
    .filter((r) => r.value === null || r.status === "DATA_MISSING")
    .map((r) => r.year);

  const realCount = rows.length - missingYears.length;
  const allYears = rows.map((r) => r.year);

  // X 轴 ticks: 每 5 年一个标签 + 所有 DATA_MISSING 年份 (确保断点可见).
  const tickEvery5: number[] = (() => {
    if (allYears.length === 0) return [];
    const yMin = Math.min(...allYears);
    const yMax = Math.max(...allYears);
    const ticks: number[] = [];
    for (let y = Math.ceil(yMin / 5) * 5; y <= yMax; y += 5) {
      ticks.push(y);
    }
    if (yMin % 5 !== 0) ticks.unshift(yMin);
    return ticks;
  })();

  if (rows.length === 0) {
    return (
      <div
        style={emptyContainerStyle}
        data-testid="time-series-chart-empty"
        data-indicator={indicatorKey}
      >
        <p style={{ color: "#999" }}>
          该指标在所选时间范围内无数据. 尝试调整年份窗口.
        </p>
      </div>
    );
  }

  return (
    <div
      style={chartContainerStyle}
      data-testid="time-series-chart"
      data-indicator={indicatorKey}
      data-points={rows.length}
      data-real={realCount}
      data-missing={missingYears.length}
    >
      <div style={chartHeaderStyle} data-testid="time-series-chart-header">
        <strong>{indicatorLabel}</strong>
        <span style={unitStyle} data-testid="time-series-chart-unit">
          {unit ? `（单位: ${unit}）` : ""}
        </span>
        <span style={metaStyle} data-testid="time-series-chart-meta">
          · {realCount} 个真实数据点
          {missingYears.length > 0 && (
            <span style={{ color: "#b45309", marginLeft: 8 }}>
              + {missingYears.length} 个 DATA_MISSING 年份（虚线）
            </span>
          )}
        </span>
      </div>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={rows}
          margin={{ top: 16, right: 24, left: 16, bottom: 8 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis
            dataKey="year"
            type="number"
            domain={["dataMin", "dataMax"]}
            ticks={tickEvery5}
            tickFormatter={(v) => String(v)}
            stroke="#666"
            fontSize={11}
          />
          <YAxis
            stroke="#666"
            fontSize={11}
            tickFormatter={(v: number) =>
              typeof v === "number" ? v.toLocaleString("zh-CN") : ""
            }
            width={64}
          />
          <Tooltip content={(props) => <ChartTooltip {...props} indicatorLabel={indicatorLabel} unit={unit} />} />

          {/* DATA_MISSING 年份 ReferenceLine (灰色虚线垂直标记, X 轴对齐). */}
          {missingYears.map((y) => (
            <ReferenceLine
              key={`missing-${y}`}
              x={y}
              stroke="#b45309"
              strokeDasharray="4 4"
              strokeWidth={1}
              label={{
                value: "无",
                position: "top",
                fill: "#b45309",
                fontSize: 10,
              }}
              data-testid={`missing-ref-${y}`}
            />
          ))}

          {/* 主折线 (实线, null value 自动断开 — per 红线-1/2 禁补零). */}
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            dot={{ r: 3, fill: color }}
            activeDot={{ r: 5 }}
            connectNulls={false}
            isAnimationActive={false}
            data-testid="time-series-line"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

// ────────────────────────────────────────────────────────────────────────────
// Custom Tooltip: 显示 year / value / unit / lineage_source_type / missing_reason.
// DATA_MISSING 年份 (value=null) 显示 "暂无数据" + missing_reason (per 红线-1/2).
// ────────────────────────────────────────────────────────────────────────────

function ChartTooltip(
  props: TooltipContentProps & {
    indicatorLabel: string;
    unit: string | null;
  }
): React.ReactElement | null {
  const { active, payload, indicatorLabel, unit } = props;
  if (!active || !payload || payload.length === 0) return null;
  const row = payload[0]?.payload as ChartRow | undefined;
  if (!row) return null;

  const isMissing = row.value === null || row.status === "DATA_MISSING";

  return (
    <div
      style={tooltipContainerStyle}
      data-testid="chart-tooltip"
      data-year={row.year}
      data-missing={isMissing ? "1" : "0"}
    >
      <div style={tooltipHeaderStyle} data-testid="chart-tooltip-header">
        <strong>{row.year}</strong>
        <span style={{ marginLeft: 6, color: "#666" }}>{indicatorLabel}</span>
      </div>
      {isMissing ? (
        <div style={tooltipMissingStyle} data-testid="chart-tooltip-missing">
          <strong>暂无数据 (DATA_MISSING)</strong>
          {row.missing_reason && (
            <div style={tooltipReasonStyle}>{row.missing_reason}</div>
          )}
        </div>
      ) : (
        <div style={tooltipValueStyle} data-testid="chart-tooltip-value">
          <strong>
            {typeof row.value === "number"
              ? row.value.toLocaleString("zh-CN", { maximumFractionDigits: 2 })
              : "—"}
            {unit && <span style={{ marginLeft: 4, fontWeight: 400, color: "#666" }}>{unit}</span>}
          </strong>
          <div style={tooltipLineageStyle} data-testid="chart-tooltip-lineage">
            {row.lineage_source_type}
          </div>
        </div>
      )}
    </div>
  );
}

const chartContainerStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 6,
  padding: "12px 14px",
  border: "1px solid #ddd",
  borderRadius: 4,
  background: "#fff",
};

const chartHeaderStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "baseline",
  gap: 8,
  fontSize: 13,
  color: "#333",
};

const unitStyle: React.CSSProperties = {
  fontSize: 11,
  color: "#888",
};

const metaStyle: React.CSSProperties = {
  fontSize: 11,
  color: "#666",
};

const emptyContainerStyle: React.CSSProperties = {
  padding: "16px 20px",
  border: "1px dashed #ccc",
  borderRadius: 4,
  background: "#fafafa",
  textAlign: "center",
};

const tooltipContainerStyle: React.CSSProperties = {
  padding: "8px 10px",
  border: "1px solid #ccc",
  borderRadius: 3,
  background: "#fff",
  fontSize: 12,
  lineHeight: 1.5,
  boxShadow: "0 2px 4px rgba(0,0,0,0.08)",
  minWidth: 200,
};

const tooltipHeaderStyle: React.CSSProperties = {
  marginBottom: 4,
};

const tooltipValueStyle: React.CSSProperties = {
  color: "#000",
};

const tooltipMissingStyle: React.CSSProperties = {
  color: "#b45309",
};

const tooltipReasonStyle: React.CSSProperties = {
  marginTop: 2,
  fontSize: 11,
  color: "#666",
  fontStyle: "italic",
};

const tooltipLineageStyle: React.CSSProperties = {
  marginTop: 2,
  fontSize: 10,
  color: "#888",
  fontFamily: "monospace",
};