"use client";

// TimeSeriesExplorer.tsx — knife 667 时序可视化交互组件.
//
// 客户端组件: 持有年份窗口 + 当前选省 + 当前选指标 三个 useState.
// 数据来自父 server component (page.tsx) 一次性传入,避免 SSR 拉取.
// 子组件:
//   - ProvinceSelector (省级下拉)
//   - YearSlider (年份窗口)
//   - TimeSeriesChartClient (Recharts 折线图, SSR 安全)
//   - SourceGradeChip (来源等级分布 badge)
//
// 状态管理:
//   - yearStart / yearEnd:  受控窗口
//   - selectedProvinceCode: 受控选省
//   - selectedIndicatorKey: 受控选指标
//   - 数据切片: useMemo 算 filteredPoints (按 province + indicator + year_range)
//
// Per 红线-4 (禁榜单化): 不实现"省份对比"或"指标排名"功能.
// Per 红线-1/2 (DATA_MISSING 守门): 不修改 mart rows; null value 直接喂 chart 让
//   connectNulls={false} 自然断线.

import type React from "react";
import { useMemo, useState } from "react";

import {
  type IndicatorOption,
  type ProvinceOption,
  type SourceGradeSummary,
} from "../../lib/api";
import type { ProvinceTimeSeriesPoint } from "../../lib/types";

import { ProvinceSelector } from "./ProvinceSelector";
import { YearSlider } from "./YearSlider";
import { TimeSeriesChartClient } from "./TimeSeriesChartClient";
import { SourceGradeChip } from "./SourceGradeChip";

export interface TimeSeriesExplorerProps {
  /** 所有省份选项 (拼音排序). */
  provinces: ProvinceOption[];
  /** 所有指标选项 (mart canonical order). */
  indicators: IndicatorOption[];
  /** 完整时序点 (8060 row subset, 已按 province filter). */
  points: ProvinceTimeSeriesPoint[];
  /** 当前选省对应 source-grade summary (server 预计算). */
  perProvinceSummary: SourceGradeSummary;
  /** NATIONAL 聚合 source-grade (server 预计算). */
  nationalSummary: SourceGradeSummary;
  /** 初始选省代码;缺省 "NATIONAL". */
  defaultProvinceCode?: string;
  /** 初始选指标;缺省 "gdp_total". */
  defaultIndicatorKey?: string;
  /** 初始年份窗口;缺省 [2020, 2025]. */
  defaultYearRange?: readonly [number, number];
}

const DEFAULT_PROVINCE = "NATIONAL";
const DEFAULT_INDICATOR = "gdp_total";
const DEFAULT_RANGE: readonly [number, number] = [2020, 2025];

export function TimeSeriesExplorer({
  provinces,
  indicators,
  points,
  perProvinceSummary,
  nationalSummary,
  defaultProvinceCode = DEFAULT_PROVINCE,
  defaultIndicatorKey = DEFAULT_INDICATOR,
  defaultYearRange = DEFAULT_RANGE,
}: TimeSeriesExplorerProps): React.ReactElement {
  const [yearStart, setYearStart] = useState<number>(defaultYearRange[0]);
  const [yearEnd, setYearEnd] = useState<number>(defaultYearRange[1]);
  const [selectedProvinceCode, setSelectedProvinceCode] = useState<string>(defaultProvinceCode);
  const [selectedIndicatorKey, setSelectedIndicatorKey] = useState<string>(defaultIndicatorKey);

  // 当前选指标元数据 (用于图表轴 label).
  const selectedIndicator = useMemo(
    () => indicators.find((i) => i.indicator_key === selectedIndicatorKey) ?? indicators[0],
    [indicators, selectedIndicatorKey]
  );

  // 当前选省元数据 (用于标题).
  const selectedProvince = useMemo(
    () => provinces.find((p) => p.province_code === selectedProvinceCode),
    [provinces, selectedProvinceCode]
  );

  // 切片: province + indicator + year range.
  const filteredPoints = useMemo(() => {
    return points.filter(
      (p) =>
        p.province_code === selectedProvinceCode &&
        p.indicator_key === selectedIndicatorKey &&
        p.year >= yearStart &&
        p.year <= yearEnd
    );
  }, [points, selectedProvinceCode, selectedIndicatorKey, yearStart, yearEnd]);

  // 选 NATIONAL 时切到 nationalSummary;其他省切 perProvinceSummary (单选).
  const activeSummary: SourceGradeSummary = useMemo(() => {
    if (selectedProvinceCode === "NATIONAL") return nationalSummary;
    // 单省 source-grade 仅就当前 indicator 算 (避免 9 指标都混入, 让用户更聚焦).
    const real = filteredPoints.filter(
      (p) => p.value !== null && p.status !== "DATA_MISSING"
    ).length;
    const missing = filteredPoints.length - real;
    let off = 0;
    let hh = 0;
    for (const p of filteredPoints) {
      if (p.value === null || p.status === "DATA_MISSING") continue;
      if (p.lineage_source_type === "OFFICIAL_INTAKED") off++;
      else if (p.lineage_source_type === "HONGHEIKU_TRANSLOAD") hh++;
    }
    return {
      OFFICIAL_INTAKED: off,
      HONGHEIKU_TRANSLOAD: hh,
      DATA_MISSING: missing,
      total: filteredPoints.length,
    };
  }, [selectedProvinceCode, nationalSummary, filteredPoints]);

  return (
    <div style={explorerContainerStyle} data-testid="time-series-explorer">
      {/* 控件 bar (3 列: 省份 + 年份窗口 + 指标). */}
      <div style={controlsBarStyle} data-testid="time-series-controls">
        <ProvinceSelector
          options={provinces}
          value={selectedProvinceCode}
          onChange={setSelectedProvinceCode}
          label="选省:"
        />

        <select
          value={selectedIndicatorKey}
          onChange={(e) => setSelectedIndicatorKey(e.target.value)}
          data-testid="indicator-selector"
          aria-label="选择指标"
          style={indicatorSelectStyle}
        >
          {indicators.map((ind) => (
            <option key={ind.indicator_key} value={ind.indicator_key}>
              {ind.indicator_label}（{ind.unit ?? "—"}）
            </option>
          ))}
        </select>

        <YearSlider
          yearStart={yearStart}
          yearEnd={yearEnd}
          onChange={(s, e) => {
            setYearStart(s);
            setYearEnd(e);
          }}
        />
      </div>

      {/* 标题 + 来源 chip. */}
      <div style={headerRowStyle} data-testid="time-series-header">
        <h2 style={titleStyle} data-testid="time-series-title">
          {selectedIndicator?.indicator_label ?? selectedIndicatorKey}
          {" · "}
          {selectedProvince
            ? selectedProvince.province_name
            : selectedProvinceCode}
          {" 时序折线图"}
        </h2>
        <SourceGradeChip summary={activeSummary} compact />
      </div>

      {/* 折线图 (Recharts, SSR-safe). */}
      <TimeSeriesChartClient
        indicatorKey={selectedIndicatorKey}
        indicatorLabel={selectedIndicator?.indicator_label ?? selectedIndicatorKey}
        unit={selectedIndicator?.unit ?? null}
        points={filteredPoints}
      />

      {/* 底部说明: 当前窗口 + 缺失提示. */}
      <p style={caveatStyle} data-testid="time-series-caveat">
        当前窗口 {yearStart}–{yearEnd} ({yearEnd - yearStart + 1} 年) ·
        · 指标 {selectedIndicator?.indicator_label} ({selectedIndicatorKey}) ·
        · {filteredPoints.length} 数据点 ({activeSummary.DATA_MISSING} 个 DATA_MISSING 显示为虚线,
        per 红线-1/2 禁补零)
      </p>
    </div>
  );
}

const explorerContainerStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 12,
};

const controlsBarStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "auto auto 1fr",
  gap: 12,
  alignItems: "flex-start",
};

const indicatorSelectStyle: React.CSSProperties = {
  padding: "4px 8px",
  border: "1px solid #ccc",
  borderRadius: 3,
  background: "#fff",
  fontSize: 13,
  minWidth: 220,
};

const headerRowStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 8,
};

const titleStyle: React.CSSProperties = {
  margin: 0,
  fontSize: 18,
  color: "#000",
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