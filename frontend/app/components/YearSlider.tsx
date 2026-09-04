"use client";

// YearSlider.tsx — knife 667 年份范围选择器 (dual handle).
//
// Per 667 tasking §3: 在时序页提供 [yearStart, yearEnd] 范围选择 (2001-2026 inclusive).
// Per 660 红线 + docs/05 §8.3: 不锁死窗口 (用户可自由拖动); 不"排序/排名"年份.
// Per 红线-1 (2001-2019 DATA_MISSING): 范围可包含历史年, 但渲染时虚线 + "暂无数据" tooltip.
//
// 实现: 双 input[type=range] 横向并列 + 数字回显 + 重置按钮.
//   - 用 useEffect 同步受控/非受控 (受控优先,避免 onChange re-render 时滑块跳变)
//   - HTML range 输入原生可访问 (键盘 + 屏幕阅读器)
//   - data-testid 命名沿用 667 tasking 规范 (year-slider-*)

import type React from "react";
import { useCallback } from "react";

export interface YearSliderProps {
  yearStart: number;
  yearEnd: number;
  onChange: (yearStart: number, yearEnd: number) => void;
  /** 范围下界;缺省 2001 (per mart). */
  min?: number;
  /** 范围上界;缺省 2026 (per mart + 红线-2). */
  max?: number;
  /** 缺省窗口;若未指定, 默认 [2020, 2025] (mart coverage). */
  defaultRange?: readonly [number, number];
}

const DEFAULT_MIN = 2001;
const DEFAULT_MAX = 2026;
const DEFAULT_RANGE: readonly [number, number] = [2020, 2025];

export function YearSlider({
  yearStart,
  yearEnd,
  onChange,
  min = DEFAULT_MIN,
  max = DEFAULT_MAX,
  defaultRange = DEFAULT_RANGE,
}: YearSliderProps): React.ReactElement {
  const handleStartChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const v = Number(e.target.value);
      // yearStart 不能超过 yearEnd (向后端 Pydantic 验证对齐)
      const newStart = Math.min(v, yearEnd);
      onChange(newStart, yearEnd);
    },
    [yearEnd, onChange]
  );

  const handleEndChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const v = Number(e.target.value);
      const newEnd = Math.max(v, yearStart);
      onChange(yearStart, newEnd);
    },
    [yearStart, onChange]
  );

  const handleReset = useCallback(() => {
    onChange(defaultRange[0], defaultRange[1]);
  }, [defaultRange, onChange]);

  return (
    <div
      style={containerStyle}
      data-testid="year-slider"
      data-year-start={yearStart}
      data-year-end={yearEnd}
    >
      <div style={headerStyle} data-testid="year-slider-header">
        <span style={labelStyle}>年份范围:</span>
        <span style={rangeStyle} data-testid="year-slider-range">
          <strong>{yearStart}</strong>
          <span style={{ margin: "0 6px", color: "#666" }}>—</span>
          <strong>{yearEnd}</strong>
        </span>
        <span style={countStyle} data-testid="year-slider-count">
          ({yearEnd - yearStart + 1} 年)
        </span>
        <button
          type="button"
          onClick={handleReset}
          data-testid="year-slider-reset"
          style={resetBtnStyle}
        >
          重置 ({defaultRange[0]}–{defaultRange[1]})
        </button>
      </div>

      <div style={sliderRowStyle}>
        <label style={sliderColStyle}>
            <span style={sliderLabelStyle}>起 {yearStart}</span>
            <input
              type="range"
              min={min}
              max={max}
              step={1}
              value={yearStart}
              onChange={handleStartChange}
              aria-label="年份起点"
              data-testid="year-slider-start"
              style={sliderInputStyle}
            />
        </label>
        <label style={sliderColStyle}>
            <span style={sliderLabelStyle}>止 {yearEnd}</span>
            <input
              type="range"
              min={min}
              max={max}
              step={1}
              value={yearEnd}
              onChange={handleEndChange}
              aria-label="年份终点"
              data-testid="year-slider-end"
              style={sliderInputStyle}
            />
        </label>
      </div>

      <div style={scaleStyle} aria-hidden="true">
        <span>{min}</span>
        <span>{Math.floor((min + max) / 2)}</span>
        <span>{max}</span>
      </div>

      {(yearStart < 2020 || yearEnd === 2026) && (
        <p style={caveatStyle} data-testid="year-slider-caveat">
          ⚠ 当前窗口包含历史年 (2001-2019) 或未来年 (2026);{" "}
          这些年份 mart status=&quot;DATA_MISSING&quot; (新增红线-1/2),{" "}
          图表会显示为虚线 + 暂无数据 tooltip.
        </p>
      )}
    </div>
  );
}

const containerStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 8,
  padding: "10px 14px",
  border: "1px solid #ddd",
  borderRadius: 4,
  background: "#fafafa",
  fontSize: 13,
};

const headerStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 12,
  flexWrap: "wrap",
};

const labelStyle: React.CSSProperties = {
  fontWeight: 600,
  color: "#333",
};

const rangeStyle: React.CSSProperties = {
  fontSize: 14,
  color: "#000",
};

const countStyle: React.CSSProperties = {
  fontSize: 11,
  color: "#888",
};

const resetBtnStyle: React.CSSProperties = {
  marginLeft: "auto",
  padding: "3px 10px",
  border: "1px solid #ccc",
  borderRadius: 3,
  background: "#fff",
  color: "#555",
  cursor: "pointer",
  fontSize: 11,
};

const sliderRowStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "1fr 1fr",
  gap: 16,
  alignItems: "center",
};

const sliderColStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 4,
};

const sliderLabelStyle: React.CSSProperties = {
  fontSize: 11,
  color: "#666",
};

const sliderInputStyle: React.CSSProperties = {
  width: "100%",
  accentColor: "#0969da",
};

const scaleStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  fontSize: 10,
  color: "#888",
  padding: "0 4px",
};

const caveatStyle: React.CSSProperties = {
  margin: 0,
  padding: "4px 8px",
  background: "#fff8e1",
  border: "1px solid #ffeeba",
  borderRadius: 3,
  fontSize: 11,
  color: "#856404",
  lineHeight: 1.5,
};