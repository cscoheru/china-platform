// 661 P1 切片 · 31 省 + NATIONAL 动态路由 `/provinces/{province_code}`.
//
// Per 661 tasking §1.661 (31 省详情动态路由真数据化, 5 静态 → 32 slug 动态).
// Per docs/87 §3.1 P1 先行 + docs/81 §3 国家锚核对 (NATIONAL 行 = 全国 2024 GDP).
//
// 设计要点:
// - 31 省代码 + NATIONAL = 32 slug; slug 用 lowercase (.toLowerCase()).
// - generateStaticParams 预生成 32 路由 (per `256` §NOW-1 同样模式, 用于 10 城).
// - dynamicParams = false (per docs/46 §3.1 slug 守门): 未在清单内的请求一律 404.
// - 数据从 mart JSON 读 (getProvinceByCode helper, per frontend/lib/mart-static.ts).
// - DATA_MISSING 3 省显示「数据暂缺」分支 (per docs/87 §3.1 + 660 receipt §1.C5).
// - 沿用 fmtNum 字符串 coerce 守门 (per 660-P1 教训).
// - 5 静态页 (guangdong/jiangsu/shandong/sichuan/zhejiang) 由 C3 删除; 动态路由接管.

import { notFound } from "next/navigation";
import { getProvinceByCode } from "../../../lib/mart-static";
import { SourcePopover } from "../../components/SourcePopover";

// 32 个合法 slug: 31 GB/T 2260 代码 + NATIONAL 锚行.
// lowercase = URL slug; getProvinceByCode() 内部 toUpperCase 匹配.
const VALID_CODES = [
  "BEIJING", "TIANJIN", "HEBEI", "SHANXI", "NEI_MENGGU",
  "LIAONING", "JILIN", "HEILONGJIANG", "SHANGHAI", "JIANGSU",
  "ZHEJIANG", "ANHUI", "FUJIAN", "JIANGXI", "SHANDONG",
  "HENAN", "HUBEI", "HUNAN", "GUANGDONG", "GUANGXI",
  "HAINAN", "CHONGQING", "SICHUAN", "GUIZHOU", "YUNNAN",
  "XIZANG", "SHAANXI", "GANSU", "QINGHAI", "NINGXIA", "XINJIANG",
  "NATIONAL",
];

export function generateStaticParams(): Array<{ province_code: string }> {
  return VALID_CODES.map((code) => ({ province_code: code.toLowerCase() }));
}

// 404 兜底: slug 命中锁定清单之外的请求一律 notFound (per docs/46 §3.1).
export const dynamicParams = false;

interface PageProps {
  params: { province_code: string };
}

interface MetricRow {
  key: string;
  label: string;
  unit: string;
}

const METRICS: MetricRow[] = [
  { key: "gdp_total", label: "GDP 总量", unit: "亿元" },
  { key: "gdp_growth", label: "GDP 增速", unit: "%" },
  { key: "primary_gdp", label: "一产增加值", unit: "亿元" },
  { key: "secondary_gdp", label: "二产增加值", unit: "亿元" },
  { key: "tertiary_gdp", label: "三产增加值", unit: "亿元" },
];

export default function ProvinceRoutePage({
  params,
}: PageProps): React.ReactElement {
  const code = params.province_code.toUpperCase();
  if (!VALID_CODES.includes(code)) {
    notFound();
  }

  const row = getProvinceByCode(code);
  if (!row) {
    notFound();
  }

  // DATA_MISSING 行 → 「数据暂缺」分支 (LIAONING / HAINAN / GUIZHOU 三省).
  // per docs/87 §3.1: 数据缺失禁补零, 显式标记.
  if (row.status === "DATA_MISSING") {
    return (
      <section>
        <h1 data-testid={`province-h-name-${row.province_code}`}>
          {row.province_name} · 2024 年 GDP · 数据暂缺
        </h1>
        <p style={{ color: "#b45309", fontWeight: 600 }} data-testid="data-missing-banner">
          ⚠ 本省 2024 年 GDP 公报源缺文,数据暂缺。
        </p>
        <p style={{ color: "#666", fontSize: 13 }}>
          missing_reason: <code style={{ fontSize: 12 }}>{row.missing_reason ?? "(未填)"}</code>
        </p>
        <p style={{ color: "#666", fontSize: 13 }}>
          lineage_source: <code style={{ fontSize: 12 }}>{row.lineage_source}</code>{" "}
          · lineage_ruling: <code style={{ fontSize: 12 }}>{row.lineage_ruling}</code>{" "}
          · lineage_is_demo: <code style={{ fontSize: 12 }}>{row.lineage_is_demo}</code>
        </p>
        <p style={{ marginTop: 16, fontSize: 12, color: "#999" }}>
          溯源:{" "}
          <SourcePopover
            sourceUrl={row.source_url}
            hashPrefix={row.source_hash_prefix}
            lineageSource={row.lineage_source}
            lineageOrigin={row.missing_reason ?? "(未填)"}
            ruling={row.lineage_ruling}
            sourceLabel="查看溯源"
            isDataMissing
          />
        </p>
        <p style={{ marginTop: 16, fontSize: 12, color: "#666" }}>
          完整度相关:{" "}
          <a href="/#data-completeness-panel">首页完整度面板</a>
          {" · "}
          <a href="/indicators">5 指标定义</a> (per 662 D2/D3)
        </p>
        <p style={{ marginTop: 24 }}>
          <a href="/">← 返回首页</a>
        </p>
      </section>
    );
  }

  // NATIONAL 行 (锚值) 与 28 真实行共用同一渲染; status 字段区分.
  const isNational = row.province_code === "NATIONAL";

  return (
    <section>
      <h1 data-testid={`province-h-name-${row.province_code}`}>
        {row.province_name} · 2024 年 GDP
        {isNational && (
          <span
            style={{
              display: "inline-block",
              marginLeft: 12,
              padding: "4px 10px",
              background: "#1a7f37",
              color: "#fff",
              fontSize: 12,
              fontWeight: 700,
              borderRadius: 3,
              letterSpacing: 0.5,
              verticalAlign: "middle",
            }}
            data-testid="national-badge"
          >
            OFFICIAL_ANCHOR
          </span>
        )}
      </h1>

      <p style={{ color: "#666", fontSize: 13 }}>
        数据来自 <code>{row.lineage_source}</code>
        {row.lineage_origin !== row.lineage_source && (
          <>
            {" "}({row.lineage_origin})
          </>
        )}
        {isNational && " · 国家统计局 2024 国民经济和社会发展统计公报 · 架构师端源自取"}
        。
      </p>

      <table
        style={{
          borderCollapse: "collapse",
          width: "100%",
          fontSize: 14,
          marginTop: 16,
        }}
        data-testid="province-metrics-table"
      >
        <thead>
          <tr style={{ background: "#eee" }}>
            <th style={cellStyle}>指标</th>
            <th style={cellStyle}>数值</th>
            <th style={cellStyle}>单位</th>
          </tr>
        </thead>
        <tbody>
          {METRICS.map((m) => {
            // Type narrowing: m.key is one of the 5 metric field names; mart row has those fields.
            const v = (row as unknown as Record<string, number | string | null>)[m.key];
            return (
              <tr
                key={m.key}
                data-testid={`metric-row-${m.key}`}
              >
                <td style={cellStyle}>{m.label}</td>
                <td
                  style={{
                    ...cellStyle,
                    fontWeight: 600,
                    fontFamily: "monospace",
                  }}
                >
                  {fmtNum(v, m.key === "gdp_growth")}
                </td>
                <td style={cellStyle}>{m.unit}</td>
              </tr>
            );
          })}
        </tbody>
      </table>

      <p style={{ marginTop: 24, fontSize: 13, color: "#555" }}>
        溯源:{" "}
        <SourcePopover
          sourceUrl={row.source_url}
          hashPrefix={row.source_hash_prefix}
          lineageSource={row.lineage_source}
          lineageOrigin={row.lineage_origin}
          ruling={row.lineage_ruling}
          sourceLabel={row.lineage_source}
        />
      </p>

      <p style={{ marginTop: 16, fontSize: 12, color: "#666" }}>
        完整度相关:{" "}
        <a href="/#data-completeness-panel">首页完整度面板</a>
        {" · "}
        <a href="/indicators">5 指标定义</a> (per 662 D2/D3)
      </p>

      <p style={{ marginTop: 24 }}>
        <a href="/">← 返回首页</a>
      </p>
    </section>
  );
}

const cellStyle: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "6px 10px",
  textAlign: "left",
};

// 660-P1 修复版 (沿用); 接受 string | number | null; 空串/NaN → "—".
function fmtNum(v: number | string | null, isPct: boolean): string {
  if (v === null || v === undefined) return "—";
  const raw = typeof v === "string" ? v.trim() : v;
  if (raw === "" || raw === undefined) return "—";
  const n = typeof raw === "string" ? Number(raw) : raw;
  if (!Number.isFinite(n)) return "—";
  if (isPct) return n.toFixed(1);
  return n.toLocaleString("zh-CN", { maximumFractionDigits: 2 });
}