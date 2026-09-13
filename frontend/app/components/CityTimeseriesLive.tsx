"use client";

// CityTimeseriesLive.tsx — knife H-series 前端地市时序实时渲染组件.
//
// 渲染 cegr_mart.mart_city_timeseries raw 数据 (10 indicator × N year long format).
// 与旧 CityPageMart 不同: 不再渲染 demo evidenceChain / sevenDim / peer compare /
// relatedPersons (这些是 MartCityViewProps 演示形态, 与 raw mart schema 不兼容).
//
// 红线 (per docs/87 §3.2 + docs/34 §1 + 663 红线 + H-series plan):
//   - DATA_MISSING 必显式「数据缺失」灰色文本 (禁补零 / 禁编造)
//   - 不派生 score / rating / rank / peer_rank
//   - 不擅自增减 10 城名单 (走 city_slug_map.ts cityCode 字段)
//   - lineage.source_file_sha256 = '0'*64 占位 (per docs/47 §3.1, O1 收口前)
//
// 数据来源:
//   - props.initialResponse 由 server component (cities/[slug]/page.tsx) 预 fetch
//   - getCityTimeSeries() 返回 CityTimeSeriesResponse; 此处不再二次请求
//   - YearSlider 调整仅做 client-side in-memory filter; 不触发 server roundtrip
//
// 来源等级分布 (SourceGradeChip) 与 TimeSeriesExplorer 同模式: 按 filteredPoints
// 计算 OFFICIAL_INTAKED / HONGHEIKU_TRANSLOAD / DATA_MISSING 三档.

import type React from "react";
import { useMemo, useState } from "react";

import type {
  CityTimeSeriesPoint,
  CityTimeSeriesResponse,
  CityTimeSeriesYearRange,
} from "../../lib/types";
import type { SourceGradeSummary } from "../../lib/api";
import { YearSlider } from "./YearSlider";
import { SourceGradeChip } from "./SourceGradeChip";

export interface CityTimeseriesLiveProps {
  /** Server pre-fetched time-series response (default year range). */
  initialResponse: CityTimeSeriesResponse;
  /** City slug (e.g., "shenzhen"). 用于 header + lineage 标注. */
  slug: string;
  /** City 中文名 (e.g., "深圳市"). 来自 city_slug_map.ts 静态信息. */
  nameZh: string;
  /** Province 中文名 slug (e.g., "guangdong"). 来自 city_slug_map.ts. */
  provinceSlug: string;
}

const MIN_YEAR = 2001;
const MAX_YEAR = 2026;
const DEFAULT_RANGE: CityTimeSeriesYearRange = [2020, 2025];

/** Cell render state discriminated union. */
type CellRender =
  | { kind: "real"; value: number; unit: string | null }
  | { kind: "missing"; reason: string | null }
  | { kind: "out-of-range" };

function renderCell(point: CityTimeSeriesPoint | undefined): CellRender {
  if (!point) return { kind: "out-of-range" };
  if (point.value !== null && point.status !== "DATA_MISSING") {
    return { kind: "real", value: point.value, unit: point.unit };
  }
  return { kind: "missing", reason: point.missing_reason };
}

function formatReal(value: number): string {
  // 4 位有效数字 + 千位分隔 (人民币元单位 / 亿元 都能稳)
  if (Math.abs(value) >= 1000) {
    return value.toLocaleString("zh-CN", { maximumFractionDigits: 2 });
  }
  if (Math.abs(value) >= 1) {
    return value.toLocaleString("zh-CN", { maximumFractionDigits: 3 });
  }
  return value.toLocaleString("zh-CN", { maximumFractionDigits: 4 });
}

export function CityTimeseriesLive({
  initialResponse,
  slug,
  nameZh,
  provinceSlug,
}: CityTimeseriesLiveProps): React.ReactElement {
  const [yearStart, setYearStart] = useState<number>(initialResponse.year_range[0]);
  const [yearEnd, setYearEnd] = useState<number>(initialResponse.year_range[1]);

  // 切片: 仅按 year 窗口过滤; indicator 不过滤 (table 必显示 10 行全量).
  const filteredPoints = useMemo(
    () =>
      initialResponse.points.filter(
        (p) => p.year >= yearStart && p.year <= yearEnd
      ),
    [initialResponse.points, yearStart, yearEnd]
  );

  // Pivot: indicator_key -> year -> point (within window).
  const pivot = useMemo(() => {
    const byIndicator = new Map<string, Map<number, CityTimeSeriesPoint>>();
    for (const p of filteredPoints) {
      let yearMap = byIndicator.get(p.indicator_key);
      if (!yearMap) {
        yearMap = new Map();
        byIndicator.set(p.indicator_key, yearMap);
      }
      yearMap.set(p.year, p);
    }
    return byIndicator;
  }, [filteredPoints]);

  // 指标元数据 (按 canonical mart order: 首次遇到 = 保序).
  const indicators = useMemo(() => {
    const seen = new Map<string, { label: string; unit: string | null }>();
    for (const p of initialResponse.points) {
      if (!seen.has(p.indicator_key)) {
        seen.set(p.indicator_key, { label: p.indicator_label, unit: p.unit });
      }
    }
    return Array.from(seen.entries()).map(([key, v]) => ({
      key,
      label: v.label,
      unit: v.unit,
    }));
  }, [initialResponse.points]);

  const years = useMemo(() => {
    const out: number[] = [];
    for (let y = yearStart; y <= yearEnd; y++) out.push(y);
    return out;
  }, [yearStart, yearEnd]);

  // Source-grade summary (per 红线-4 不做"地区排名", 仅展示数据来源分布).
  const summary = useMemo<SourceGradeSummary>(() => {
    let off = 0;
    let hh = 0;
    let miss = 0;
    for (const p of filteredPoints) {
      if (p.value === null || p.status === "DATA_MISSING") {
        miss += 1;
      } else if (p.lineage_source_type === "OFFICIAL_INTAKED") {
        off += 1;
      } else if (p.lineage_source_type === "HONGHEIKU_TRANSLOAD") {
        hh += 1;
      }
    }
    return {
      OFFICIAL_INTAKED: off,
      HONGHEIKU_TRANSLOAD: hh,
      DATA_MISSING: miss,
      total: filteredPoints.length,
    };
  }, [filteredPoints]);

  const isOutOfRange = yearStart < 2020 || yearEnd > 2025;
  const hasNoData = summary.total === 0 || summary.DATA_MISSING === summary.total;

  return (
    <section
      data-testid="city-timeseries-live"
      data-city-slug={slug}
      data-city-code={initialResponse.city_code}
      data-year-start={yearStart}
      data-year-end={yearEnd}
      data-points-count={summary.total}
      style={containerStyle}
    >
      <h1 style={titleStyle} data-testid="city-timeseries-title">
        {nameZh} 地市时序（live mart）{" "}
        <small style={{ fontSize: 13, color: "#666", fontWeight: 400 }}>
          {initialResponse.province_code ?? provinceSlug} ·{" "}
          <code data-testid="city-code">{initialResponse.city_code}</code>
        </small>
      </h1>

      <p style={metaStyle}>
        数据源: <code>cegr_mart.mart_city_timeseries</code> · 指标数:{" "}
        <code>{initialResponse.indicator_count}</code> · 当前窗口:{" "}
        <code>
          {yearStart}–{yearEnd} ({yearEnd - yearStart + 1} 年)
        </code>{" "}
        · 数据点: <code>{summary.total}</code>{" "}
        <SourceGradeChip summary={summary} compact />
      </p>

      <YearSlider
        yearStart={yearStart}
        yearEnd={yearEnd}
        onChange={(s, e) => {
          setYearStart(s);
          setYearEnd(e);
        }}
        min={MIN_YEAR}
        max={MAX_YEAR}
        defaultRange={DEFAULT_RANGE}
      />

      {hasNoData && (
        <p style={emptyStyle} data-testid="city-timeseries-empty">
          ⚠ 当前 mart 中 <code>{initialResponse.city_code}</code> 全部 DATA_MISSING —{" "}
          公开统计源 (hongheiku) 暂未收录该城此窗口数据, 这是「hongheiku 0 entry」
          的合规表现, 禁补零 (per 红线-3).
        </p>
      )}

      {isOutOfRange && (
        <p style={caveatStyle} data-testid="city-timeseries-caveat">
          ⚠ 当前窗口包含历史年 (2001-2019) 或未来年 (2026); 这些年份 mart status=
          <code>DATA_MISSING</code> (红线-1/2), 表格对应列显示「数据缺失」灰色文本.
        </p>
      )}

      <div style={tableWrapStyle} data-testid="city-timeseries-table-wrap">
        <table style={tableStyle} data-testid="city-timeseries-table">
          <thead>
            <tr>
              <th style={thLeftStyle}>指标</th>
              {years.map((y) => (
                <th key={y} style={thStyle} data-testid={`th-year-${y}`}>
                  {y}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {indicators.map((ind) => {
              const yearMap = pivot.get(ind.key);
              return (
                <tr key={ind.key} data-testid={`row-${ind.key}`}>
                  <td style={tdLeftStyle} data-testid={`label-${ind.key}`}>
                    <div style={{ fontWeight: 600 }}>{ind.label}</div>
                    <div style={{ fontSize: 11, color: "#888" }}>
                      <code>{ind.key}</code>
                      {ind.unit ? <> · {ind.unit}</> : null}
                    </div>
                  </td>
                  {years.map((y) => {
                    const cell = renderCell(yearMap?.get(y));
                    if (cell.kind === "real") {
                      return (
                        <td
                          key={y}
                          style={tdStyle}
                          data-testid={`cell-${ind.key}-${y}`}
                          data-cell-state="real"
                        >
                          {formatReal(cell.value)}
                          {cell.unit ? (
                            <span style={{ fontSize: 10, color: "#888" }}>
                              {" "}
                              {cell.unit}
                            </span>
                          ) : null}
                        </td>
                      );
                    }
                    if (cell.kind === "missing") {
                      return (
                        <td
                          key={y}
                          style={tdMissingStyle}
                          data-testid={`cell-${ind.key}-${y}`}
                          data-cell-state="missing"
                          data-missing-reason={cell.reason ?? "unknown"}
                        >
                          数据缺失
                        </td>
                      );
                    }
                    return (
                      <td
                        key={y}
                        style={tdMissingStyle}
                        data-testid={`cell-${ind.key}-${y}`}
                        data-cell-state="out-of-range"
                      >
                        —
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p style={footerStyle}>
        S2.7-b-full+ 接驳 <code>cegr_mart.mart_city_timeseries</code> (knife H-series, 2026-09-13).{" "}
        Lineage 字段 (<code>lineage_source_type</code> /{" "}
        <code>lineage_origin</code> / <code>lineage_ruling</code>) 来自 dbt mart 列.{" "}
        Demo 标识: <code>lineage_is_demo={String(initialResponse.points[0]?.lineage_is_demo ?? "false")}</code>.
      </p>
    </section>
  );
}

// ── Inline styles (沿用 TimeSeriesExplorer 视觉基线; 不引外部 CSS) ──

const containerStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 12,
};

const titleStyle: React.CSSProperties = {
  margin: 0,
  fontSize: 20,
  fontWeight: 600,
  color: "#111",
};

const metaStyle: React.CSSProperties = {
  margin: 0,
  fontSize: 12,
  color: "#586069",
  lineHeight: 1.6,
};

const emptyStyle: React.CSSProperties = {
  margin: 0,
  padding: "8px 12px",
  background: "#fff8e1",
  border: "1px solid #ffe082",
  borderRadius: 3,
  fontSize: 12,
  color: "#856404",
};

const caveatStyle: React.CSSProperties = {
  margin: 0,
  padding: "6px 10px",
  background: "#f6f8fa",
  border: "1px solid #e1e4e8",
  borderRadius: 3,
  color: "#586069",
  fontSize: 12,
  lineHeight: 1.6,
};

const tableWrapStyle: React.CSSProperties = {
  overflowX: "auto",
  border: "1px solid #d0d7de",
  borderRadius: 4,
  background: "#fff",
};

const tableStyle: React.CSSProperties = {
  width: "100%",
  borderCollapse: "collapse",
  fontSize: 13,
};

const thStyle: React.CSSProperties = {
  padding: "8px 10px",
  background: "#f6f8fa",
  borderBottom: "1px solid #d0d7de",
  textAlign: "right",
  fontWeight: 600,
  color: "#24292f",
  minWidth: 80,
};

const thLeftStyle: React.CSSProperties = {
  ...thStyle,
  textAlign: "left",
  position: "sticky",
  left: 0,
  background: "#f6f8fa",
  zIndex: 1,
  minWidth: 200,
};

const tdStyle: React.CSSProperties = {
  padding: "6px 10px",
  borderBottom: "1px solid #eaecef",
  textAlign: "right",
  fontVariantNumeric: "tabular-nums",
  color: "#24292f",
};

const tdLeftStyle: React.CSSProperties = {
  ...tdStyle,
  textAlign: "left",
  position: "sticky",
  left: 0,
  background: "#fff",
  minWidth: 200,
};

const tdMissingStyle: React.CSSProperties = {
  padding: "6px 10px",
  borderBottom: "1px solid #eaecef",
  textAlign: "center",
  color: "#bbb",
  fontSize: 11,
  background: "#fafbfc",
};

const footerStyle: React.CSSProperties = {
  margin: 0,
  fontSize: 11,
  color: "#999",
  lineHeight: 1.5,
};
