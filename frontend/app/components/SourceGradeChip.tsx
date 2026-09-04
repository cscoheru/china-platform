"use client";

// SourceGradeChip.tsx — knife 667 来源等级分布 chip.
//
// Per 667 tasking §4: 7-dim grid 风格 badge 显示 OFFICIAL_INTAKED / HONGHEIKU_TRANSLOAD
// / DATA_MISSING 三档计数. **不**做榜单化 (per docs/05 §8.3);仅展示计数 + 总数.
// Per 660 任务文档 + mart schema: lineage_source_type 三档语义:
//   - OFFICIAL_INTAKED    : 5 现指标 from 省统计局 (knife 660 + 666 加 粤苏浙)
//   - HONGHEIKU_TRANSLOAD : from tjgb.hongheiku.com re-post (5 现 + 5 增量)
//   - DATA_MISSING        : 显式缺失 (红线-1/2 + missing provinces + pending harvest)
//
// 注意: mart 中 DATA_MISSING 的 lineage_source_type 仍填 "hongheiku_tjgb" 或 "DATA_MISSING";
// 计数按 row.value IS NULL || status='DATA_MISSING' 累计 (与 export 脚本一致).
//
// 颜色: 与首页 7-dim grid chip 风格对齐 (绿色 OFFICIAL + 琥珀 HONGHEIKU + 灰 DATA_MISSING).

import type React from "react";
import type { SourceGradeSummary } from "../../lib/api";

export interface SourceGradeChipProps {
  summary: SourceGradeSummary;
  /** 标题行;缺省 "来源等级分布". */
  label?: string;
  /** 紧凑模式: 隐藏总数 + 各档百分比,只显示三个 chip. */
  compact?: boolean;
}

const COLOR_OFFICIAL = "#1a7f37";   // green-700
const COLOR_HONGHEIKU = "#b45309";   // amber-700
const COLOR_MISSING = "#666";       // gray

export function SourceGradeChip({
  summary,
  label = "来源等级分布",
  compact = false,
}: SourceGradeChipProps): React.ReactElement {
  const pct = (n: number): string => {
    if (summary.total === 0) return "0%";
    return `${((n / summary.total) * 100).toFixed(1)}%`;
  };

  return (
    <div
      style={chipContainerStyle}
      data-testid="source-grade-chip"
      data-official={summary.OFFICIAL_INTAKED}
      data-hongheiku={summary.HONGHEIKU_TRANSLOAD}
      data-missing={summary.DATA_MISSING}
      data-total={summary.total}
    >
      {!compact && (
        <div style={headerStyle} data-testid="source-grade-label">
          {label}
          <span style={totalStyle} data-testid="source-grade-total">
            {" "}· 合计 {summary.total} cells
          </span>
        </div>
      )}
      <div style={pillsContainerStyle} data-testid="source-grade-pills">
        <Pill
          color={COLOR_OFFICIAL}
          label="OFFICIAL_INTAKED"
          count={summary.OFFICIAL_INTAKED}
          pct={pct(summary.OFFICIAL_INTAKED)}
          testid="source-grade-pill-official"
        />
        <Pill
          color={COLOR_HONGHEIKU}
          label="HONGHEIKU_TRANSLOAD"
          count={summary.HONGHEIKU_TRANSLOAD}
          pct={pct(summary.HONGHEIKU_TRANSLOAD)}
          testid="source-grade-pill-hongheiku"
        />
        <Pill
          color={COLOR_MISSING}
          label="DATA_MISSING"
          count={summary.DATA_MISSING}
          pct={pct(summary.DATA_MISSING)}
          testid="source-grade-pill-missing"
        />
      </div>
      {!compact && summary.total > 0 && (
        <p style={caveatStyle} data-testid="source-grade-caveat">
          ⚠ 计数仅反映 mart 行级别;不构成省份或时间点排名 (per docs/05 §8.3)。
        </p>
      )}
    </div>
  );
}

function Pill({
  color,
  label,
  count,
  pct,
  testid,
}: {
  color: string;
  label: string;
  count: number;
  pct: string;
  testid: string;
}): React.ReactElement {
  return (
    <span
      style={{
        ...pillStyle,
        borderColor: color,
        color: color,
      }}
      data-testid={testid}
      data-count={count}
    >
      <strong style={{ marginRight: 4 }}>{count}</strong>
      <span style={{ fontSize: 11 }}>{label}</span>
      <span style={{ marginLeft: 4, fontSize: 11, color: "#888" }}>{pct}</span>
    </span>
  );
}

const chipContainerStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 6,
  padding: "8px 12px",
  border: "1px solid #ddd",
  borderRadius: 4,
  background: "#fafafa",
  fontSize: 12,
};

const headerStyle: React.CSSProperties = {
  fontWeight: 700,
  fontSize: 13,
  color: "#333",
};

const totalStyle: React.CSSProperties = {
  fontWeight: 400,
  fontSize: 11,
  color: "#666",
};

const pillsContainerStyle: React.CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: 6,
};

const pillStyle: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  padding: "3px 8px",
  border: "1px solid",
  borderRadius: 12,
  background: "#fff",
  fontSize: 12,
};

const caveatStyle: React.CSSProperties = {
  margin: 0,
  fontSize: 11,
  color: "#666",
  lineHeight: 1.5,
};