"use client";

// SourcePopover.tsx — 661 溯源 popover 三件套 + 662 扩血缘二件套.
//
// Per 661 tasking §1.661 第 3 件 + 红线 8 「溯源 UI 只显示库中真实血缘字段」(禁编造 source).
// Per 662 tasking §1.662-D1: 加 lineage_source + lineage_origin 两字段 (PRD §3.3 血缘全量露出).
// Per docs/87 §3.1 P1 先行 + docs/81 §3 国家锚核对.
//
// 五件套渲染顺序: URL → SHA 前缀 → lineage_source → lineage_origin → 裁定.
// 缺字段时按红线 8 显式 "—" + 解释, 不编造.
// DATA_MISSING 行 lineage_source = "DATA_MISSING" 字符串显式, lineage_origin
// 显示 missing_reason (而非统计局名).
//
// 实现: 用语义 HTML <details>/<summary>;点击 summary 展开/收起五件套.
// 不需要 React state (浏览器原生);SSR 友好 + 无 hydration mismatch 风险.
// ARIA: <details> 默认带 role="group" + aria-expanded 状态, accessibility tools 识别良好.

import type React from "react";

export interface SourcePopoverProps {
  /** 公网可访问 URL;缺失省此处为 null. */
  sourceUrl: string | null;
  /** 8 字符 SHA256 前缀 (dbt source_document JOIN 暂留 null, 662+ 接入). */
  hashPrefix: string | null;
  /**
   * 来源等级三档之一 (从 mart JSON lineage_source 透传):
   *  OFFICIAL_INTAKED | HONGHEIKU_TRANSLOAD (或 hongheiku_tjgb) | DATA_MISSING.
   * DATA_MISSING 行此处仍为 "hongheiku_tjgb" (mart 真实值);用 `isDataMissing`
   * 显式 flag 标识缺文状态, 不要用字符串 == 判断 (会漏).
   */
  lineageSource: string;
  /**
   * 出处机构/部门 (从 mart JSON lineage_origin 透传).
   * DATA_MISSING 行此处显示 missing_reason (而非 mart lineage_origin 字段,
   * 因 mart 里 DATA_MISSING 行的 lineage_origin="hongheiku_tjgb" 与来源
   * 等级重复, 无信息量; 改显示 missing_reason 更清晰).
   */
  lineageOrigin: string;
  /** 裁定字符串 (e.g. "U6 2026-09-02"). */
  ruling: string;
  /** 简短显示用 (e.g. lineage_source "OFFICIAL_INTAKED");缺省回退 "查看溯源"/"无溯源". */
  sourceLabel?: string;
  /**
   * 显式 DATA_MISSING 标识. 调用方按 row.status 传, 不要靠 lineageSource 字符串.
   * true 时: lineage_origin 渲染加 "(本行为 DATA_MISSING, 此处为 missing_reason)" 注解.
   */
  isDataMissing?: boolean;
}

export function SourcePopover({
  sourceUrl,
  hashPrefix,
  lineageSource,
  lineageOrigin,
  ruling,
  sourceLabel,
  isDataMissing = false,
}: SourcePopoverProps): React.ReactElement {
  // 缺字段时按红线 8 显式 "—" + 解释, 不编造.
  const urlEl = sourceUrl ? (
    <a href={sourceUrl} target="_blank" rel="noopener noreferrer" style={linkStyle}>
      {sourceUrl}
    </a>
  ) : (
    <span style={missingStyle} data-testid="source-url-missing">
      — (DATA_MISSING 行无源 URL)
    </span>
  );

  const hashEl = hashPrefix ? (
    <code style={{ fontSize: 11 }}>{hashPrefix}</code>
  ) : (
    <span style={missingStyle} data-testid="source-hash-missing">
      — (待 662+ dbt source_document JOIN)
    </span>
  );

  // 662: 五件套新增第 3-4 件 — lineage_source + lineage_origin.
  // isDataMissing 显式 flag (按 row.status) 决定 lineage_origin 注解样式.
  const lineageSourceEl = (
    <code style={{ fontSize: 11 }} data-testid="lineage-source-value">
      {lineageSource}
    </code>
  );
  const lineageOriginEl = isDataMissing ? (
    <span style={missingStyle} data-testid="lineage-origin-missing-reason">
      {lineageOrigin} <em>(本行为 DATA_MISSING, 此处为 missing_reason)</em>
    </span>
  ) : (
    <span data-testid="lineage-origin-value">{lineageOrigin}</span>
  );

  return (
    <details style={detailsStyle} data-testid="source-popover">
      <summary style={summaryStyle} data-testid="source-popover-summary">
        {sourceLabel ?? (sourceUrl ? "查看溯源" : "无溯源")}
      </summary>
      <div style={contentStyle} data-testid="source-popover-content">
        <div style={rowStyle}>
          <span style={labelStyle}>URL:</span>
          <span>{urlEl}</span>
        </div>
        <div style={rowStyle}>
          <span style={labelStyle}>SHA 前缀:</span>
          <span>{hashEl}</span>
        </div>
        <div style={rowStyle}>
          <span style={labelStyle}>来源等级:</span>
          <span>{lineageSourceEl}</span>
        </div>
        <div style={rowStyle}>
          <span style={labelStyle}>出处:</span>
          <span>{lineageOriginEl}</span>
        </div>
        <div style={rowStyle}>
          <span style={labelStyle}>裁定:</span>
          <span>
            <code style={{ fontSize: 11 }}>{ruling}</code>
          </span>
        </div>
      </div>
    </details>
  );
}

const detailsStyle: React.CSSProperties = {
  display: "inline-block",
  fontSize: 12,
};

const summaryStyle: React.CSSProperties = {
  cursor: "pointer",
  padding: "2px 6px",
  border: "1px solid #ccc",
  borderRadius: 3,
  background: "#f6f6f6",
  userSelect: "none",
  listStyle: "none",
};

const contentStyle: React.CSSProperties = {
  marginTop: 4,
  padding: 8,
  border: "1px solid #ddd",
  borderRadius: 3,
  background: "#fafafa",
  minWidth: 320,
  maxWidth: 480,
  fontSize: 12,
  lineHeight: 1.5,
};

const rowStyle: React.CSSProperties = {
  display: "flex",
  gap: 8,
  marginBottom: 4,
  alignItems: "flex-start",
};

const labelStyle: React.CSSProperties = {
  fontWeight: 600,
  minWidth: 64,
  flexShrink: 0,
};

const linkStyle: React.CSSProperties = {
  color: "#0969da",
  textDecoration: "underline",
  wordBreak: "break-all",
};

const missingStyle: React.CSSProperties = {
  color: "#999",
  fontStyle: "italic",
};