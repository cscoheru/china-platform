"use client";

// CoverageMatrix.tsx — 662 D3 数据完整度面板之覆盖矩阵.
//
// Per 662 tasking §1.662-D3: 31 省 × 5 指标覆盖矩阵 + 3 省 DATA_MISSING 公示.
// Per docs/87 §3.1 P1 先行 + PRD §7.2 数据完整度切片.
//
// 设计:
// - 31 行 × 5 列 (rows = 31 GB/T 2260 省代码, 排除 NATIONAL 锚行;
//   cols = 5 metric keys).
// - 每个 cell:
//   - 指标值非 null → "✓" (浅绿 #e6ffed)
//   - 指标值 null (DATA_MISSING 行) → "—" (浅黄 #fff8e1)
//   - 行级 "覆盖率 = 28/31" (行级所有 5 列都 ✓ 才算"完整覆盖")
// - 列级 "指标 X 覆盖率 = 28/31" 在底部 footer row 显示.
// - 紧凑字号 12px + sticky header (overflow-x scroll 内嵌).
// - data-testid 完整覆盖 (matrix / row-code-X / cell-X-Y / summary).
//
// 红线:
//   - 多指标数据只准来自库/mart 导出 (禁手填) — 直接消费 mart JSON, 无派生.
//   - 缺失省禁补零 — DATA_MISSING cell 显式 "—", 禁编造数值.

import type React from "react";
import { useMemo } from "react";
import type { MartProvinceGdp2024 } from "../../lib/mart-static";

type MetricKey =
  | "gdp_total"
  | "gdp_growth"
  | "primary_gdp"
  | "secondary_gdp"
  | "tertiary_gdp";

const METRIC_KEYS: MetricKey[] = [
  "gdp_total",
  "gdp_growth",
  "primary_gdp",
  "secondary_gdp",
  "tertiary_gdp",
];

const METRIC_LABELS: Record<MetricKey, string> = {
  gdp_total: "总量",
  gdp_growth: "增速",
  primary_gdp: "一产",
  secondary_gdp: "二产",
  tertiary_gdp: "三产",
};

export interface CoverageMatrixProps {
  mart: MartProvinceGdp2024;
}

export function CoverageMatrix({ mart }: CoverageMatrixProps): React.ReactElement {
  // 31 行 (排除 NATIONAL 锚行, 因为锚行是核对基准不参与覆盖统计).
  const rows = useMemo(
    () => mart.provinces.filter((p) => p.province_code !== "NATIONAL"),
    [mart]
  );

  // 31 行共 31 × 5 = 155 cells.
  // 28 real × 5 = 140 ✓ + 3 missing × 5 = 15 — = 155 total.
  const totalCells = rows.length * METRIC_KEYS.length;

  // 行级覆盖率 = 该行 5 个指标全 ✓ 的行数 / 31.
  // 列级覆盖率 = 该列所有 ✓ 的 cell 数 / 31.
  const rowCoverage = useMemo(() => {
    let fullyCovered = 0;
    for (const r of rows) {
      const allOk = METRIC_KEYS.every((mk) => {
        const v = r[mk];
        return v !== null && v !== undefined && v !== "";
      });
      if (allOk) fullyCovered++;
    }
    return { fullyCovered, total: rows.length };
  }, [rows]);

  const colCoverage = useMemo(() => {
    const m: Record<MetricKey, { ok: number; total: number }> = {
      gdp_total: { ok: 0, total: rows.length },
      gdp_growth: { ok: 0, total: rows.length },
      primary_gdp: { ok: 0, total: rows.length },
      secondary_gdp: { ok: 0, total: rows.length },
      tertiary_gdp: { ok: 0, total: rows.length },
    };
    for (const r of rows) {
      for (const mk of METRIC_KEYS) {
        const v = r[mk];
        if (v !== null && v !== undefined && v !== "") {
          m[mk].ok++;
        }
      }
    }
    return m;
  }, [rows]);

  // 整体 ✓ cell 数 (140 期望).
  const totalOk = useMemo(() => {
    let ok = 0;
    for (const r of rows) {
      for (const mk of METRIC_KEYS) {
        const v = r[mk];
        if (v !== null && v !== undefined && v !== "") ok++;
      }
    }
    return ok;
  }, [rows]);

  return (
    <div
      data-testid="coverage-matrix"
      style={{
        overflowX: "auto",
        marginTop: 12,
        border: "1px solid #ddd",
        borderRadius: 4,
        background: "#fff",
      }}
    >
      <table
        style={{
          borderCollapse: "collapse",
          width: "100%",
          fontSize: 12,
        }}
      >
        <thead>
          <tr style={{ background: "#eee", position: "sticky", top: 0 }}>
            <th style={cellStyle}>省份</th>
            <th style={cellStyle}>代码</th>
            {METRIC_KEYS.map((mk) => (
              <th
                key={mk}
                style={{ ...cellStyle, ...headerCellStyle }}
                data-testid={`coverage-th-${mk}`}
              >
                {METRIC_LABELS[mk]}
                <br />
                <span
                  style={{
                    fontSize: 9,
                    color: "#888",
                    fontFamily: "monospace",
                  }}
                >
                  {mk}
                </span>
              </th>
            ))}
            <th style={{ ...cellStyle, ...headerCellStyle }}>行级覆盖率</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((p) => {
            const isMissing = p.status === "DATA_MISSING";
            const allOk = METRIC_KEYS.every((mk) => {
              const v = p[mk];
              return v !== null && v !== undefined && v !== "";
            });
            return (
              <tr
                key={p.province_code}
                data-testid={`coverage-row-${p.province_code}`}
                data-status={isMissing ? "DATA_MISSING" : "OK"}
                style={isMissing ? rowMissingStyle : undefined}
              >
                <td style={{ ...cellStyle, ...nameCellStyle }}>
                  <a
                    href={`/provinces/${p.province_code.toLowerCase()}`}
                    style={{ color: "#0969da", textDecoration: "underline" }}
                    data-testid={`coverage-link-${p.province_code}`}
                  >
                    {p.province_name}
                  </a>
                </td>
                <td style={{ ...cellStyle, ...codeCellStyle }}>
                  {p.province_code}
                </td>
                {METRIC_KEYS.map((mk) => {
                  const v = p[mk];
                  const ok =
                    v !== null && v !== undefined && v !== "" ? true : false;
                  return (
                    <td
                      key={mk}
                      data-testid={`coverage-cell-${p.province_code}-${mk}`}
                      data-status={ok ? "OK" : "MISSING"}
                      style={{
                        ...cellStyle,
                        ...(ok ? cellOkStyle : cellMissingStyle),
                      }}
                    >
                      {ok ? "✓" : "—"}
                    </td>
                  );
                })}
                <td
                  style={{
                    ...cellStyle,
                    ...(allOk ? cellOkStyle : cellMissingStyle),
                  }}
                  data-testid={`coverage-row-coverage-${p.province_code}`}
                >
                  {allOk ? "5/5" : "0/5"}
                </td>
              </tr>
            );
          })}
          {/* 汇总 footer 行. */}
          <tr
            data-testid="coverage-footer"
            style={{ background: "#f6f6f6", fontWeight: 700 }}
          >
            <td colSpan={2} style={{ ...cellStyle, ...footerLabelStyle }}>
              指标级覆盖率 (✓ cells / 31)
            </td>
            {METRIC_KEYS.map((mk) => {
              const c = colCoverage[mk];
              return (
                <td
                  key={mk}
                  data-testid={`coverage-col-coverage-${mk}`}
                  style={{ ...cellStyle, ...footerCellStyle }}
                >
                  {c.ok}/{c.total}
                </td>
              );
            })}
            <td style={{ ...cellStyle, ...footerCellStyle }}>
              {rowCoverage.fullyCovered}/{rowCoverage.total}
            </td>
          </tr>
        </tbody>
      </table>

      <p
        style={{
          padding: "6px 10px",
          margin: 0,
          fontSize: 11,
          color: "#666",
          background: "#fafafa",
          borderTop: "1px solid #ddd",
        }}
        data-testid="coverage-summary"
      >
        31 省 × 5 指标 = {totalCells} cells; ✓ = {totalOk} ({((totalOk / totalCells) * 100).toFixed(1)}%);
        — = {totalCells - totalOk} ({(((totalCells - totalOk) / totalCells) * 100).toFixed(1)}%);
        行级全覆盖率 {rowCoverage.fullyCovered}/{rowCoverage.total}.
        NATIONAL 锚行 (全国 2024 GDP) 不参与覆盖统计, 仅作核对基准.
      </p>
    </div>
  );
}

const cellStyle: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "4px 8px",
  textAlign: "center",
};

const headerCellStyle: React.CSSProperties = {
  background: "#f6f6f6",
  fontWeight: 700,
};

const nameCellStyle: React.CSSProperties = {
  textAlign: "left",
  fontWeight: 600,
};

const codeCellStyle: React.CSSProperties = {
  fontFamily: "monospace",
  fontSize: 10,
  color: "#666",
};

const rowMissingStyle: React.CSSProperties = {
  background: "#fff8e1",
};

const cellOkStyle: React.CSSProperties = {
  background: "#e6ffed",
  color: "#1a7f37",
  fontWeight: 700,
};

const cellMissingStyle: React.CSSProperties = {
  background: "#fff8e1",
  color: "#b45309",
  fontWeight: 700,
};

const footerLabelStyle: React.CSSProperties = {
  textAlign: "right",
  fontWeight: 700,
};

const footerCellStyle: React.CSSProperties = {
  background: "#e6ffed",
  color: "#1a7f37",
  fontWeight: 700,
};
