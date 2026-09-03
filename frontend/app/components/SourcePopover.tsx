"use client";

// SourcePopover.tsx — 661 溯源 popover 三件套 (source_url + source_hash_prefix + lineage_ruling).
//
// Per 661 tasking §1.661 第 3 件 + 红线 8 「溯源 UI 只显示库中真实血缘字段」(禁编造 source).
// Per docs/87 §3.1 P1 先行 + docs/81 §3 国家锚核对.
//
// 实现: 用语义 HTML <details>/<summary>;点击 summary 展开/收起三件套.
// 不需要 React state (浏览器原生);SSR 友好 + 无 hydration mismatch 风险.
// ARIA: <details> 默认带 role="group" + aria-expanded 状态, accessibility tools 识别良好.

import type React from "react";

export interface SourcePopoverProps {
  /** 公网可访问 URL;缺失省此处为 null. */
  sourceUrl: string | null;
  /** 8 字符 SHA256 前缀 (dbt source_document JOIN 暂留 null, 662+ 接入). */
  hashPrefix: string | null;
  /** 裁定字符串 (e.g. "U6 2026-09-02"). */
  ruling: string;
  /** 简短显示用 (e.g. lineage_source "OFFICIAL_INTAKED"). */
  sourceLabel?: string;
}

export function SourcePopover({
  sourceUrl,
  hashPrefix,
  ruling,
  sourceLabel,
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