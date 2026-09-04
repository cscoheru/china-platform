"use client";

// ProvinceSelector.tsx — knife 667 省份下拉选择器.
//
// Per 667 tasking §2: 31 省 + NATIONAL 锚 + 排序按拼音 (Intl.Collator zh-Hans-CN).
// Per docs/05 §8.3 + 662 任务: 不做"省份排名"语义;选项按字典序固定.
// Per 红线 1 (DATA_MISSING): 选项包含辽/琼/黔,但选择后页面会显示 DATA_MISSING 提示.
//
// 实现: 原生 <select> + <option> (键盘可访问 + 屏幕阅读器友好).
//   - 缺省值由 props 控制 (受控);onChange 时回调.
//   - 按 province_code 提供 ARIA-label 增强可读性.

import type React from "react";
import type { ProvinceOption } from "../../lib/api";

export interface ProvinceSelectorProps {
  options: ProvinceOption[];
  value: string;
  onChange: (provinceCode: string) => void;
  /** 标签;缺省 "选择省份". */
  label?: string;
  /** 显式添加 NATIONAL 锚行选项 (默认 true, /timeseries overview 用). */
  includeNational?: boolean;
  /** 是否禁用 (e.g. 加载中). */
  disabled?: boolean;
}

export function ProvinceSelector({
  options,
  value,
  onChange,
  label = "选择省份",
  includeNational = true,
  disabled = false,
}: ProvinceSelectorProps): React.ReactElement {
  const nationalOpt: ProvinceOption = { province_code: "NATIONAL", province_name: "全国（国家锚）" };

  // 选项数组 = NATIONAL + 31 省(已按拼音排序 from listProvincesWithTimeSeries).
  const allOptions: ProvinceOption[] = includeNational
    ? [nationalOpt, ...options.filter((o) => o.province_code !== "NATIONAL")]
    : options;

  return (
    <div
      style={containerStyle}
      data-testid="province-selector"
      data-value={value}
      data-count={allOptions.length}
    >
      <label
        htmlFor="province-selector-input"
        style={labelStyle}
        data-testid="province-selector-label"
      >
        {label}
      </label>
      <select
        id="province-selector-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        data-testid="province-selector-input"
        style={selectStyle}
        aria-label={`${label}（共 ${allOptions.length} 项）`}
      >
        {allOptions.map((opt) => (
          <option
            key={opt.province_code}
            value={opt.province_code}
            data-testid={`province-option-${opt.province_code}`}
          >
            {opt.province_name} ({opt.province_code})
          </option>
        ))}
      </select>
    </div>
  );
}

const containerStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 8,
  padding: "6px 10px",
  border: "1px solid #ddd",
  borderRadius: 4,
  background: "#fafafa",
  fontSize: 13,
};

const labelStyle: React.CSSProperties = {
  fontWeight: 600,
  color: "#333",
};

const selectStyle: React.CSSProperties = {
  padding: "4px 8px",
  border: "1px solid #ccc",
  borderRadius: 3,
  background: "#fff",
  fontSize: 13,
  minWidth: 220,
};