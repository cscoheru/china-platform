"use client";

// ProvinceGdpTable.tsx — 661 P1 首页 5 指标 tab 切换 + 国家锚行 + 溯源 popover.
//
// Per 661 tasking §1.661 (首页多指标切换 + 国家锚行 + 溯源 UI 三件套).
// Per docs/87 §3.1 P1 先行 + user_ruling_661 锁定 tab 切换器.
// Per docs/81 §3 国家锚核对 (NATIONAL 行 = 全国 2024 GDP, 1,349,084.0 亿元).
//
// 设计:
// - 客户端组件 (tab 状态用 useState);mart 数据从 page.tsx (server) 透传.
// - 5 指标 tab 顶部水平排列: 总量 / 增速 / 一产 / 二产 / 三产.
//   active tab 列加粗 (header + 数值);其他 4 列弱化显示.
// - NATIONAL 行置顶, OFFICIAL_ANCHOR badge + 强调样式.
// - 每行末 SourcePopover (三件套: source_url + source_hash_prefix + lineage_ruling).
// - DATA_MISSING 行 metrics 全 null, SourcePopover 三件套中 hash/source 都标 "—".

import type React from "react";
import { useState } from "react";
import type { MartProvinceGdp2024 } from "../../lib/mart-static";
import { SourcePopover } from "./SourcePopover";

type MetricKey =
  | "gdp_total"
  | "gdp_growth"
  | "primary_gdp"
  | "secondary_gdp"
  | "tertiary_gdp";

interface MetricTab {
  key: MetricKey;
  label: string;
  short: string;
}

const METRIC_TABS: MetricTab[] = [
  { key: "gdp_total", label: "GDP 总量", short: "总量" },
  { key: "gdp_growth", label: "GDP 增速", short: "增速" },
  { key: "primary_gdp", label: "一产增加值", short: "一产" },
  { key: "secondary_gdp", label: "二产增加值", short: "二产" },
  { key: "tertiary_gdp", label: "三产增加值", short: "三产" },
];

export interface ProvinceGdpTableProps {
  mart: MartProvinceGdp2024;
}

export function ProvinceGdpTable({
  mart,
}: ProvinceGdpTableProps): React.ReactElement {
  const [activeMetric, setActiveMetric] = useState<MetricKey>("gdp_total");

  // NATIONAL 行从 mart JSON 里取 (架构师端已置首); 不重复用 getNationalAnchor(),
  // 因为 mart 数组顺序就是权威顺序 (per docs/87 §3.1 + export-mart-data.py 行 244).
  const national = mart.provinces.find((p) => p.province_code === "NATIONAL");
  const otherRows = mart.provinces.filter((p) => p.province_code !== "NATIONAL");

  return (
    <div>
      {/* 5 指标 tab 切换器 (顶部水平排列). */}
      <div
        style={tabsContainerStyle}
        role="tablist"
        aria-label="GDP 指标切换"
        data-testid="metric-tabs"
      >
        {METRIC_TABS.map((tab) => {
          const isActive = tab.key === activeMetric;
          return (
            <button
              key={tab.key}
              role="tab"
              aria-selected={isActive}
              aria-controls="province-gdp-tbody"
              data-testid={`metric-tab-${tab.key}`}
              onClick={() => setActiveMetric(tab.key)}
              style={
                isActive ? tabButtonActiveStyle : tabButtonInactiveStyle
              }
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      <table
        data-testid="province-gdp-2024-table"
        style={{
          borderCollapse: "collapse",
          width: "100%",
          fontSize: 13,
          marginTop: 8,
        }}
      >
        <thead>
          <tr style={{ background: "#eee" }}>
            <th style={cellStyle}>省份</th>
            <th style={cellStyle}>代码</th>
            {METRIC_TABS.map((tab) => {
              const isActive = tab.key === activeMetric;
              return (
                <th
                  key={tab.key}
                  style={
                    isActive
                      ? { ...cellStyle, ...headerActiveStyle }
                      : { ...cellStyle, ...headerInactiveStyle }
                  }
                  data-testid={`th-${tab.key}`}
                >
                  {tab.short}
                </th>
              );
            })}
            <th style={cellStyle}>状态</th>
            <th style={cellStyle}>溯源</th>
          </tr>
        </thead>
        <tbody id="province-gdp-tbody">
          {/* NATIONAL 锚行 (per docs/81 §3, 置顶, OFFICIAL_ANCHOR badge). */}
          {national && (
            <tr
              data-testid={`province-row-${national.province_code}`}
              data-national="1"
              data-status={national.status}
              style={nationalRowStyle}
            >
              <td style={{ ...cellStyle, fontWeight: 700 }}>
                {national.province_name}
                <span
                  style={officialBadgeStyle}
                  data-testid="national-badge"
                  title="国家统计局 2024 国民经济和社会发展统计公报 · 架构师端源自取"
                >
                  {" "}
                  OFFICIAL_ANCHOR
                </span>
              </td>
              <td style={cellStyle}>
                <code style={{ fontSize: 11 }}>{national.province_code}</code>
              </td>
              {METRIC_TABS.map((tab) => {
                const isActive = tab.key === activeMetric;
                const v = national[tab.key];
                return (
                  <td
                    key={tab.key}
                    style={
                      isActive
                        ? { ...cellStyle, ...cellActiveStyle }
                        : { ...cellStyle, ...cellInactiveStyle }
                    }
                    data-testid={`national-cell-${tab.key}`}
                  >
                    {fmtNum(v)}
                  </td>
                );
              })}
              <td style={cellStyle}>
                <span
                  style={{ color: "#1a7f37", fontWeight: 600, fontSize: 11 }}
                >
                  国家锚 (1,349,084.0)
                </span>
              </td>
              <td style={cellStyle}>
                <SourcePopover
                  sourceUrl={national.source_url}
                  hashPrefix={national.source_hash_prefix}
                  ruling={national.lineage_ruling}
                  sourceLabel={national.lineage_source}
                />
              </td>
            </tr>
          )}

          {/* 31 省行 (28 真 + 3 DATA_MISSING). */}
          {otherRows.map((p) => {
            const isMissing = p.status === "DATA_MISSING";
            return (
              <tr
                key={p.province_code}
                data-testid={`province-row-${p.province_code}`}
                data-missing={isMissing ? "1" : "0"}
                style={
                  isMissing
                    ? { background: "#fff8e1" }
                    : undefined
                }
              >
                <td style={cellStyle}>
                  <a
                    href={`/provinces/${p.province_code.toLowerCase()}`}
                    style={{ color: "#0969da", textDecoration: "underline" }}
                    data-testid={`province-link-${p.province_code}`}
                  >
                    {p.province_name}
                  </a>
                </td>
                <td style={cellStyle}>
                  <code style={{ fontSize: 11 }}>{p.province_code}</code>
                </td>
                {METRIC_TABS.map((tab) => {
                  const isActive = tab.key === activeMetric;
                  const v = p[tab.key];
                  return (
                    <td
                      key={tab.key}
                      style={
                        isActive
                          ? { ...cellStyle, ...cellActiveStyle }
                          : { ...cellStyle, ...cellInactiveStyle }
                      }
                      data-testid={`cell-${p.province_code}-${tab.key}`}
                    >
                      {fmtNum(v)}
                    </td>
                  );
                })}
                <td style={cellStyle}>
                  {isMissing ? (
                    <span
                      data-testid={`missing-badge-${p.province_code}`}
                      style={{ color: "#b45309", fontWeight: 600, fontSize: 11 }}
                      title={p.missing_reason ?? "数据暂缺"}
                    >
                      数据暂缺
                    </span>
                  ) : (
                    <span style={{ color: "#666", fontSize: 11 }}>正常</span>
                  )}
                </td>
                <td style={cellStyle}>
                  <SourcePopover
                    sourceUrl={p.source_url}
                    hashPrefix={p.source_hash_prefix}
                    ruling={p.lineage_ruling}
                    sourceLabel={isMissing ? undefined : p.lineage_source}
                  />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

const tabsContainerStyle: React.CSSProperties = {
  display: "flex",
  gap: 4,
  marginBottom: 0,
  borderBottom: "2px solid #ddd",
};

const tabButtonInactiveStyle: React.CSSProperties = {
  padding: "8px 16px",
  border: "1px solid #ccc",
  borderBottom: "none",
  borderRadius: "4px 4px 0 0",
  background: "#f6f6f6",
  color: "#666",
  cursor: "pointer",
  fontSize: 13,
  fontWeight: 400,
};

const tabButtonActiveStyle: React.CSSProperties = {
  ...tabButtonInactiveStyle,
  background: "#fff",
  color: "#000",
  fontWeight: 700,
  borderBottom: "2px solid #fff",
  marginBottom: -2,
};

const cellStyle: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "6px 10px",
  textAlign: "left",
};

const headerActiveStyle: React.CSSProperties = {
  background: "#fff3a0",
  fontWeight: 700,
};

const headerInactiveStyle: React.CSSProperties = {
  color: "#999",
  fontWeight: 400,
};

const cellActiveStyle: React.CSSProperties = {
  fontWeight: 700,
  background: "#fffce0",
};

const cellInactiveStyle: React.CSSProperties = {
  color: "#999",
  fontWeight: 400,
};

const nationalRowStyle: React.CSSProperties = {
  background: "#e6f4ff",
  borderLeft: "3px solid #0969da",
};

const officialBadgeStyle: React.CSSProperties = {
  display: "inline-block",
  marginLeft: 8,
  padding: "2px 6px",
  background: "#1a7f37",
  color: "#fff",
  fontSize: 10,
  fontWeight: 700,
  borderRadius: 3,
  letterSpacing: 0.5,
};

function fmtNum(v: number | string | null): string {
  if (v === null || v === undefined) return "—";
  const raw = typeof v === "string" ? v.trim() : v;
  if (raw === "" || raw === undefined) return "—";
  const n = typeof raw === "string" ? Number(raw) : raw;
  if (!Number.isFinite(n)) return "—";
  return n.toLocaleString("zh-CN", { maximumFractionDigits: 2 });
}