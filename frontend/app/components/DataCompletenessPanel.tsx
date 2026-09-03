"use client";

// DataCompletenessPanel.tsx — 662 D3 数据完整度面板.
//
// Per 662 tasking §1.662-D3 + PRD §7.2 数据完整度切片.
// 三段式:
//   1. 顶部统计 (real/missing/national count + lineage_ruling)
//   2. CoverageMatrix 嵌入 (31 省 × 5 指标覆盖矩阵)
//   3. DATA_MISSING 3 省公示 (LIAONING/HAINAN/GUIZHOU 每省一行)
//
// 红线:
//   - 多指标数据只准来自库/mart 导出 (禁手填) — 直接消费 mart JSON.
//   - 缺失省禁补零 + 公示必标 missing_reason (per docs/87 §3.1 + 660 receipt §1.C5).

import type React from "react";
import type { MartProvinceGdp2024 } from "../../lib/mart-static";
import { CoverageMatrix } from "./CoverageMatrix";

export interface DataCompletenessPanelProps {
  mart: MartProvinceGdp2024;
}

export function DataCompletenessPanel({
  mart,
}: DataCompletenessPanelProps): React.ReactElement {
  const missingRows = mart.provinces.filter((p) => p.status === "DATA_MISSING");

  return (
    <section
      data-testid="data-completeness-panel"
      style={{
        marginTop: 32,
        padding: 16,
        border: "1px solid #ddd",
        borderRadius: 4,
        background: "#fafafa",
      }}
    >
      <h2
        data-testid="data-completeness-h"
        style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}
      >
        数据完整度
      </h2>

      {/* 1. 顶部统计. */}
      <div
        data-testid="data-completeness-stats"
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 16,
          fontSize: 13,
          color: "#444",
        }}
      >
        <span data-testid="stat-total">
          全部：<strong>{mart.total_count}</strong> 行
        </span>
        <span data-testid="stat-real" style={{ color: "#1a7f37" }}>
          真省：<strong>{mart.real_count}</strong> 行
        </span>
        <span data-testid="stat-missing" style={{ color: "#b45309" }}>
          DATA_MISSING：<strong>{mart.missing_count}</strong> 行
        </span>
        <span data-testid="stat-national" style={{ color: "#0969da" }}>
          NATIONAL 锚：<strong>{mart.national_count ?? 1}</strong> 行
        </span>
        <span data-testid="stat-ruling" style={{ color: "#666" }}>
          裁定：<code>{mart.lineage_ruling}</code>
        </span>
      </div>

      {/* 2. CoverageMatrix 嵌入. */}
      <CoverageMatrix mart={mart} />

      {/* 3. DATA_MISSING 3 省公示. */}
      <div
        data-testid="data-missing-publicity"
        style={{
          marginTop: 16,
          padding: 12,
          border: "1px solid #ffeeba",
          background: "#fff8e1",
          borderRadius: 3,
        }}
      >
        <h3
          style={{
            fontSize: 14,
            fontWeight: 700,
            color: "#856404",
            marginBottom: 8,
          }}
        >
          ⚠ DATA_MISSING {missingRows.length} 省公示
        </h3>
        <p style={{ fontSize: 11, color: "#856404", marginBottom: 8 }}>
          以下 {missingRows.length} 省 2024 年 GDP 公报源缺文（详见各 missing_reason）;
          数据暂缺, 禁补零（per 红线 1）。
        </p>
        <table
          style={{
            width: "100%",
            fontSize: 12,
            borderCollapse: "collapse",
            background: "#fff",
          }}
        >
          <thead>
            <tr style={{ background: "#f6f6f6" }}>
              <th style={pubCellStyle}>省份</th>
              <th style={pubCellStyle}>代码</th>
              <th style={pubCellStyle}>missing_reason</th>
              <th style={pubCellStyle}>来源</th>
            </tr>
          </thead>
          <tbody>
            {missingRows.map((p) => (
              <tr
                key={p.province_code}
                data-testid={`publicity-row-${p.province_code}`}
              >
                <td style={{ ...pubCellStyle, ...pubNameStyle }}>
                  <a
                    href={`/provinces/${p.province_code.toLowerCase()}`}
                    style={{ color: "#0969da", textDecoration: "underline" }}
                  >
                    {p.province_name}
                  </a>
                </td>
                <td style={{ ...pubCellStyle, ...pubCodeStyle }}>
                  {p.province_code}
                </td>
                <td style={{ ...pubCellStyle, ...pubReasonStyle }}>
                  {p.missing_reason ?? "(未填)"}
                </td>
                <td style={{ ...pubCellStyle, ...pubCodeStyle }}>
                  {p.lineage_source}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p style={{ marginTop: 12, fontSize: 11, color: "#999" }}>
        数据来源：<code>{mart.mart_source}</code> · 架构师端自取, 禁手填与编造。
      </p>
    </section>
  );
}

const pubCellStyle: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "4px 8px",
  textAlign: "left",
};

const pubNameStyle: React.CSSProperties = {
  fontWeight: 600,
};

const pubCodeStyle: React.CSSProperties = {
  fontFamily: "monospace",
  fontSize: 11,
  color: "#666",
};

const pubReasonStyle: React.CSSProperties = {
  fontFamily: "monospace",
  fontSize: 11,
  color: "#b45309",
};
