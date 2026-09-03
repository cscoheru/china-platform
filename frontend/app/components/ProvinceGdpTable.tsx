"use client";

// ProvinceGdpTable.tsx — 661 P1 首页 5 指标 tab 切换 + 国家锚行 + 溯源 popover.
//                          662 扩: 溯源 popover 五件套 (lineage_source/origin) + 排序交互.
//
// Per 661 tasking §1.661 (首页多指标切换 + 国家锚行 + 溯源 UI 三件套).
// Per docs/87 §3.1 P1 先行 + user_ruling_661 锁定 tab 切换器.
// Per docs/81 §3 国家锚核对 (NATIONAL 行 = 全国 2024 GDP, 1,349,084.0 亿元).
// Per 662 tasking §1.662-D1 (扩 lineage_source/origin) + §1.662-D4 (排序交互 + 禁榜单化):
//   docs/05 §8.3 「全国实时排名红线」禁榜单化 → 排序按钮 + 顶部口径提示, 不用"排名"词.
//
// 设计:
// - 客户端组件 (tab + sort state 用 useState);mart 数据从 page.tsx (server) 透传.
// - 5 指标 tab 顶部水平排列: 总量 / 增速 / 一产 / 二产 / 三产.
//   active tab 列加粗 (header + 数值);其他 4 列弱化显示.
// - 662+: sort-bar (5 排序按钮 + asc/desc 切换) + 口径提示;active sort key 高亮 (沿用 tab 风格).
// - NATIONAL 行置顶, OFFICIAL_ANCHOR badge + 强调样式;不参与排序.
// - 28 真省行按 sortState 重排; DATA_MISSING 3 省行始终排末尾.
// - 每行末 SourcePopover (五件套: URL + SHA + lineage_source + lineage_origin + 裁定).
// - DATA_MISSING 行 metrics 全 null, SourcePopover 五件套中 hash/source 都标 "—".

import type React from "react";
import { useMemo, useState } from "react";
import type { MartProvinceGdp2024 } from "../../lib/mart-static";
import { SourcePopover } from "./SourcePopover";

type MetricKey =
  | "gdp_total"
  | "gdp_growth"
  | "primary_gdp"
  | "secondary_gdp"
  | "tertiary_gdp";

// 662 D4: 排序键复用 metric key; 方向 asc/desc 二选一.
type SortDir = "asc" | "desc";
type SortKey = MetricKey;

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
  // 662 D4: 排序状态. null = 按 GB/T 2260 默认顺序; 否则按 {key, dir} 重排 28 真省.
  const [sortState, setSortState] = useState<{ key: SortKey; dir: SortDir } | null>(null);

  // NATIONAL 行从 mart JSON 里取 (架构师端已置首); 不重复用 getNationalAnchor(),
  // 因为 mart 数组顺序就是权威顺序 (per docs/87 §3.1 + export-mart-data.py 行 244).
  const national = mart.provinces.find((p) => p.province_code === "NATIONAL");
  const otherRows = mart.provinces.filter((p) => p.province_code !== "NATIONAL");

  // 662 D4: 28 真省 (real) 与 3 DATA_MISSING 分流. 排序仅作用于 real; DATA_MISSING 排末尾.
  const realRows = useMemo(() => otherRows.filter((p) => p.status !== "DATA_MISSING"), [otherRows]);
  const missingRows = useMemo(
    () => otherRows.filter((p) => p.status === "DATA_MISSING"),
    [otherRows]
  );

  // 排序后的 28 真省行. 无 sortState 时保持 GB/T 2260 默认顺序 (mart 数组权威序).
  const sortedRealRows = useMemo(() => {
    if (!sortState) return realRows;
    const { key, dir } = sortState;
    const mul = dir === "asc" ? 1 : -1;
    return [...realRows].sort((a, b) => {
      const av = a[key];
      const bv = b[key];
      const an = typeof av === "string" ? Number(av) : av;
      const bn = typeof bv === "string" ? Number(bv) : bv;
      // null/NaN 排到末尾 (无论 asc/desc)
      const aValid = typeof an === "number" && Number.isFinite(an);
      const bValid = typeof bn === "number" && Number.isFinite(bn);
      if (!aValid && !bValid) return 0;
      if (!aValid) return 1;
      if (!bValid) return -1;
      return (an - bn) * mul;
    });
  }, [realRows, sortState]);

  // 排序时口径提示: 计算当前排序键下 28 真省的 lineage_source 三档分布.
  const sortCaveat = useMemo(() => {
    if (!sortState) return null;
    let official = 0;
    let transload = 0;
    let missing = 0;
    for (const p of realRows) {
      if (p.lineage_source === "OFFICIAL_INTAKED") official++;
      else if (p.lineage_source === "HONGHEIKU_TRANSLOAD") transload++;
      else missing++;
    }
    return { official, transload, missing, total: realRows.length };
  }, [sortState, realRows]);

  const activeSortLabel = sortState
    ? METRIC_TABS.find((t) => t.key === sortState.key)?.label ?? sortState.key
    : null;
  const sortDirLabel = sortState?.dir === "asc" ? "升序" : "降序";

  return (
    <div>
      {/* 662 D4: 排序 bar — 5 排序按钮 + asc/desc 切换 + 口径提示. */}
      <div
        style={sortBarContainerStyle}
        data-testid="sort-bar"
        aria-label="排序口径切换"
      >
        <span style={{ marginRight: 4, color: "#666", fontSize: 12 }}>
          排序:
        </span>
        {METRIC_TABS.map((tab) => {
          const isActive = sortState?.key === tab.key;
          return (
            <button
              key={`sort-${tab.key}`}
              type="button"
              onClick={() => {
                // 同 key 再次点击 → 反转方向; 切换 key → 默认 desc.
                if (sortState?.key === tab.key) {
                  setSortState({
                    key: tab.key,
                    dir: sortState.dir === "asc" ? "desc" : "asc",
                  });
                } else {
                  setSortState({ key: tab.key, dir: "desc" });
                }
              }}
              data-testid={`sort-btn-${tab.key}`}
              aria-pressed={isActive}
              style={isActive ? sortBtnActiveStyle : sortBtnInactiveStyle}
            >
              {tab.short}
              {isActive && sortState && (
                <span data-testid={`sort-dir-${tab.key}`} style={{ marginLeft: 4 }}>
                  {sortState.dir === "asc" ? "↑" : "↓"}
                </span>
              )}
            </button>
          );
        })}
        {sortState && (
          <button
            type="button"
            onClick={() => setSortState(null)}
            data-testid="sort-clear"
            style={sortClearStyle}
          >
            清除排序
          </button>
        )}
      </div>

      {/* 662 D4: 排序时口径提示 (禁榜单化红线). 仅在 sortState 非空时渲染. */}
      {sortCaveat && activeSortLabel && (
        <p
          style={sortCaveatStyle}
          data-testid="sort-caveat"
        >
          ⚠ 本排序按 <strong>{activeSortLabel}</strong> {sortDirLabel};
          数据来源等级 = OFFICIAL_INTAKED {sortCaveat.official} 省 +
          HONGHEIKU_TRANSLOAD {sortCaveat.transload} 省 + DATA_MISSING
          {" "}{sortCaveat.missing} 省 (合计 {sortCaveat.total});{" "}
          <strong>仅供参考, 不构成排名 (per docs/05 §8.3)</strong>。
        </p>
      )}

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
          {/* NATIONAL 锚行 (per docs/81 §3, 置顶, OFFICIAL_ANCHOR badge).
              662: 不参与排序, 永远置顶. */}
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
                  lineageSource={national.lineage_source}
                  lineageOrigin={national.lineage_origin}
                  ruling={national.lineage_ruling}
                  sourceLabel={national.lineage_source}
                />
              </td>
            </tr>
          )}

          {/* 28 真省行 (按 sortState 重排; 无 sortState 时按 mart 默认 GB/T 2260 序). */}
          {sortedRealRows.map((p) => {
            return (
              <tr
                key={p.province_code}
                data-testid={`province-row-${p.province_code}`}
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
                  <span style={{ color: "#666", fontSize: 11 }}>正常</span>
                </td>
                <td style={cellStyle}>
                  <SourcePopover
                    sourceUrl={p.source_url}
                    hashPrefix={p.source_hash_prefix}
                    lineageSource={p.lineage_source}
                    lineageOrigin={p.lineage_origin}
                    ruling={p.lineage_ruling}
                    sourceLabel={p.lineage_source}
                  />
                </td>
              </tr>
            );
          })}

          {/* 662 D4: DATA_MISSING 3 省始终排末尾 (不参与排序). */}
          {missingRows.map((p) => (
            <tr
              key={p.province_code}
              data-testid={`province-row-${p.province_code}`}
              data-missing="1"
              style={{ background: "#fff8e1" }}
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
                <span
                  data-testid={`missing-badge-${p.province_code}`}
                  style={{ color: "#b45309", fontWeight: 600, fontSize: 11 }}
                  title={p.missing_reason ?? "数据暂缺"}
                >
                  数据暂缺
                </span>
              </td>
              <td style={cellStyle}>
                <SourcePopover
                  sourceUrl={p.source_url}
                  hashPrefix={p.source_hash_prefix}
                  lineageSource={p.lineage_source}
                  lineageOrigin={p.missing_reason ?? "(未填)"}
                  ruling={p.lineage_ruling}
                  sourceLabel={p.lineage_source}
                  isDataMissing
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const sortBarContainerStyle: React.CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: 4,
  marginBottom: 8,
  alignItems: "center",
};

const sortBtnInactiveStyle: React.CSSProperties = {
  padding: "4px 10px",
  border: "1px solid #ccc",
  borderRadius: 3,
  background: "#f6f6f6",
  color: "#555",
  cursor: "pointer",
  fontSize: 12,
  fontWeight: 400,
};

const sortBtnActiveStyle: React.CSSProperties = {
  ...sortBtnInactiveStyle,
  background: "#dde7ff",
  color: "#0969da",
  fontWeight: 700,
  border: "1px solid #0969da",
};

const sortClearStyle: React.CSSProperties = {
  padding: "4px 10px",
  border: "1px solid #ddd",
  borderRadius: 3,
  background: "#fff",
  color: "#666",
  cursor: "pointer",
  fontSize: 11,
  fontWeight: 400,
  marginLeft: 8,
};

const sortCaveatStyle: React.CSSProperties = {
  margin: "4px 0 8px 0",
  padding: "6px 10px",
  background: "#fff8e1",
  border: "1px solid #ffeeba",
  borderRadius: 3,
  color: "#856404",
  fontSize: 12,
  lineHeight: 1.5,
};

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