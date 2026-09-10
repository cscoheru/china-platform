"use client";

// TimeSeriesExplorer.tsx — knife 667 时序可视化交互组件.
//
// 客户端组件: 持有年份窗口 + 当前选省 + 当前选指标 三个 useState.
// 数据策略 (Knife H server pre-slice, 修 O2 3.7MB SSR HTML WARN):
//   * 初始数据 = defaultPoints (server pre-slice, ~26 points = default 省 × default 指标 × 26 年).
//   * 用户切换省/指标时 → useEffect 触发 lazy fetch martJsonUrl → 全 mart 缓存到 allPoints state.
//   * filteredPoints: 当 allPoints 已加载用 allPoints; 否则用 defaultPoints (覆盖 default 选择).
//   * 若 lazy fetch 失败 → 仍用 defaultPoints (覆盖 default 选择; 用户切到非默认会看到 DATA_MISSING).
//
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
//   - allPoints: lazy-fetched 全 mart (null = 未加载, 用 defaultPoints 兜底)
//   - dataLoading: lazy fetch 进行中
//   - dataError: lazy fetch 失败 (回退 defaultPoints)
//
// Per 红线-4 (禁榜单化): 不实现"省份对比"或"指标排名"功能.
// Per 红线-1/2 (DATA_MISSING 守门): 不修改 mart rows; null value 直接喂 chart 让
//   connectNulls={false} 自然断线.

import type React from "react";
import { useEffect, useMemo, useState } from "react";

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
  /**
   * Server pre-slice 的 default 选省 + 选指标 全年序列 (~26 points).
   * Per Knife H (O2 修): 不再传全 mart (8060 points) 触发 3.7MB SSR HTML.
   */
  defaultPoints: ProvinceTimeSeriesPoint[];
  /**
   * 完整 mart JSON 的 client-side URL (e.g. "/data/mart_province_timeseries.json").
   * 当用户切换省/指标超出 defaultPoints 覆盖时, 客户端 lazy-fetch 此 URL.
   * 若未提供, 用户切换省/指标会看到 DATA_MISSING (不回退报错).
   */
  martJsonUrl?: string;
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

// 全 mart JSON 文件顶层 schema (Knife H lazy-fetch 解析). 仅取我们用到的字段.
interface MartTimeSeriesJson {
  provinces: ProvinceTimeSeriesPoint[];
}

export function TimeSeriesExplorer({
  provinces,
  indicators,
  defaultPoints,
  martJsonUrl,
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

  // Knife H lazy-fetch state. allPoints = null 表示还未加载, 用 defaultPoints.
  const [allPoints, setAllPoints] = useState<ProvinceTimeSeriesPoint[] | null>(null);
  const [dataLoading, setDataLoading] = useState(false);
  const [dataError, setDataError] = useState<string | null>(null);

  // 用户切换省/指标时若 allPoints 未加载且切到非 default, 触发 lazy fetch.
  const needsLazyFetch =
    allPoints === null &&
    martJsonUrl !== undefined &&
    (selectedProvinceCode !== defaultProvinceCode ||
      selectedIndicatorKey !== defaultIndicatorKey);

  useEffect(() => {
    if (!needsLazyFetch) return;
    if (dataLoading) return;
    setDataLoading(true);
    setDataError(null);
    fetch(martJsonUrl!)
      .then((r) => {
        if (!r.ok) {
          throw new Error(`HTTP ${r.status} fetching ${martJsonUrl}`);
        }
        return r.json() as Promise<MartTimeSeriesJson>;
      })
      .then((json) => {
        if (Array.isArray(json.provinces)) {
          setAllPoints(json.provinces);
        } else {
          throw new Error("mart JSON missing 'provinces' array");
        }
        setDataLoading(false);
      })
      .catch((err) => {
        setDataError(err instanceof Error ? err.message : String(err));
        setDataLoading(false);
        // allPoints 仍为 null → filteredPoints 回退 defaultPoints (用户切到非默认会显示 DATA_MISSING).
      });
  }, [needsLazyFetch, martJsonUrl, dataLoading]);

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

  // 切片: province + indicator + year range. 数据源: allPoints 优先, 否则 defaultPoints.
  const activePoints = allPoints ?? defaultPoints;
  const filteredPoints = useMemo(() => {
    return activePoints.filter(
      (p) =>
        p.province_code === selectedProvinceCode &&
        p.indicator_key === selectedIndicatorKey &&
        p.year >= yearStart &&
        p.year <= yearEnd
    );
  }, [activePoints, selectedProvinceCode, selectedIndicatorKey, yearStart, yearEnd]);

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

      {/* 底部说明: 当前窗口 + 缺失提示 + Knife H lazy fetch 状态. */}
      <p style={caveatStyle} data-testid="time-series-caveat">
        当前窗口 {yearStart}–{yearEnd} ({yearEnd - yearStart + 1} 年) ·
        · 指标 {selectedIndicator?.indicator_label} ({selectedIndicatorKey}) ·
        · {filteredPoints.length} 数据点 ({activeSummary.DATA_MISSING} 个 DATA_MISSING 显示为虚线,
        per 红线-1/2 禁补零)
        {dataLoading && (
          <> · <span data-testid="time-series-loading">正在加载全 mart (Knife H lazy-fetch)…</span></>
        )}
        {dataError && !dataLoading && (
          <> · <span data-testid="time-series-fetch-error" style={{ color: "#a00" }}>
            全 mart 加载失败 ({dataError}); 仅显示默认切片.
          </span></>
        )}
        {allPoints && !dataLoading && (
          <> · 全 mart 已缓存 ({allPoints.length} 点)</>
        )}
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