// M1 acceptance surface — Hubei 2026 H1 GDP (bulletin sample).
//
// Per docs/55 §T6 (knife 629 §2 T6):
//   * Header MUST contain "M1 验收面 · 湖北 2026 上半年 GDP（公报样本）· 非 31 省 · 非 Gate PASS"
//   * USE_MOCK=false → fetch the T5 FastAPI series endpoint (NO mock UUIDs).
//   * Display caveat, SHA prefix (8 chars), and source URL.
//   * Do NOT modify /provinces/jiangsu or any other demo route.
//
// This page is the bounded M1 acceptance view: ONE province (Hubei), ONE
// indicator (GDP), ONE period (2026-01-01..2026-06-30), ONE real observation.
// It is **not** O1 / not Gate PASS.

import { indicatorSeries } from "../../../lib/api";
import { DemoBanner } from "../../DemoBanner";

export const dynamic = "force-dynamic";

const HUBEI_GDP_INDICATOR_ID = "a1000000-0000-0000-0000-000000000010";
const HUBEI_PROVINCE_ID = "a1000000-0000-0000-0000-000000000001";
const SOURCE_URL = "https://tjj.hubei.gov.cn/tjsj/sjkscx/tjyb/";

// NOTE: try/catch wraps the FastAPI fetch so the demo banner + caveats
//   still render when the backend is unreachable (e.g. newvps-only deploy
//   without FastAPI container). Per 662 D5: demo shell MUST stay labelled
//   regardless of backend availability — silent failure violates demo 守门.
export default async function M1SeriesPage() {
  let points: Awaited<ReturnType<typeof indicatorSeries>>["series"] = [];
  let fetchError: string | null = null;
  try {
    const data = await indicatorSeries(HUBEI_GDP_INDICATOR_ID, HUBEI_PROVINCE_ID);
    points = data.series;
  } catch (err) {
    fetchError = err instanceof Error ? err.message : String(err);
  }

  return (
    <section style={{ fontFamily: "sans-serif", maxWidth: 960, margin: "0 auto", padding: 24 }}>
      <h1 style={{ fontSize: 22 }}>
        M1 验收面 · 湖北 2026 上半年 GDP（公报样本）· 非 31 省 · 非 Gate PASS
      </h1>

      {/* 662 D5: demo 壳显式横幅. */}
      <DemoBanner
        reason="M1 验收面 · 1 行真 observation · 非 31 省 · 非 Gate PASS"
        source="spikes/02-provincial-yearbook/hubei_2026_06.xlsx"
      />

      {fetchError && (
        <p
          style={{
            color: "#a00",
            background: "#fef2f2",
            border: "1px solid #fecaca",
            padding: "8px 12px",
            borderRadius: 3,
            fontSize: 13,
          }}
          data-testid="m1-fetch-error"
        >
          ⚠ FastAPI 暂不可达 ({fetchError}). 本页为 demo 壳, 不依赖后端.
          按 662 D5 demo 守门: 横幅仍展示, 数据点表格降级为空 (points=[]).
        </p>
      )}

      <p style={{ color: "#444", lineHeight: 1.6 }}>
        本页只展示一条 <strong>真 observation</strong>（来自
        <code> spikes/02-provincial-yearbook/hubei_2026_06.xlsx </code>
        ，SHA 前 8 = <code>c5cf5abe</code>）。它不是 31 省汇总，
        <strong> 不代表 Gate / O1 / M1 PASS</strong>。
      </p>

      <ul style={{ background: "#fafafa", padding: "12px 24px", borderRadius: 6 }}>
        <li>indicator_id = <code>{HUBEI_GDP_INDICATOR_ID}</code>（湖北 GDP）</li>
        <li>geo_entity_id = <code>{HUBEI_PROVINCE_ID}</code>（湖北省）</li>
        <li>period = 2026-01-01 .. 2026-06-30（2026 上半年）</li>
        <li>源 URL（非首页） = <a href={SOURCE_URL}>{SOURCE_URL}</a></li>
      </ul>

      <h2 style={{ fontSize: 18, marginTop: 28 }}>时序点（≤ 1 行）</h2>

      {points.length === 0 ? (
        <p style={{ color: "#a00" }}>
          未拿到任何 series 点；请检查 cegr_test 数据库 / dbt view /
          FastAPI 是否可达。
        </p>
      ) : (
        <table
          style={{
            borderCollapse: "collapse",
            width: "100%",
            marginTop: 8,
            fontSize: 14,
          }}
        >
          <thead>
            <tr style={{ background: "#f0f0f0" }}>
              <th style={th}>period</th>
              <th style={th}>value</th>
              <th style={th}>unit</th>
              <th style={th}>source_domain</th>
              <th style={th}>SHA prefix 8</th>
            </tr>
          </thead>
          <tbody>
            {points.map((pt) => (
              <tr key={`${pt.indicator_id}-${pt.geo_entity_id}-${pt.period_start}`}>
                <td style={td}>
                  {pt.period_start} .. {pt.period_end}
                </td>
                <td style={{ ...td, textAlign: "right", fontWeight: 600 }}>
                  {pt.value.toFixed(2)}
                </td>
                <td style={td}>{pt.unit ?? "—"}</td>
                <td style={td}>{pt.source_domain ?? "—"}</td>
                <td style={{ ...td, fontFamily: "monospace" }}>
                  {pt.source_hash_prefix ?? "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h2 style={{ fontSize: 18, marginTop: 28 }}>Caveat（不可删）</h2>
      {points.length === 0 ? (
        <p>—</p>
      ) : (
        points.map((pt) => (
          <blockquote
            key={`cav-${pt.indicator_id}-${pt.period_start}`}
            style={{
              borderLeft: "3px solid #888",
              margin: "8px 0",
              padding: "4px 12px",
              color: "#555",
              background: "#fafafa",
            }}
          >
            {pt.caveat_text || "（无 caveat）"}
          </blockquote>
        ))
      )}

      <hr style={{ marginTop: 32 }} />
      <p style={{ color: "#888", fontSize: 12 }}>
        数据源：湖北省统计局 2026 年 6 月公报（Hubei 2026-06 bulletin
        sample，SHA c5cf5abeb4fdf97af52567f0640470d631bc9ac329dcc98f14e5d40bf6a5cac7）。
        本页为 M1 验收面，仅含 1 省 1 指标 1 期间，与 Gate / O1 / M1 PASS 无关。
      </p>
    </section>
  );
}

const th: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "6px 10px",
  textAlign: "left",
};

const td: React.CSSProperties = {
  border: "1px solid #eee",
  padding: "6px 10px",
};
