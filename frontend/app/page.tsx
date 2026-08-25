// Stage 2 / S2.0.1 + S2.7-a — Home page.
//
// Lists indicators (mock by default). S2.7-a 增量：附 5 省列表入口
// （per tasking 168 §NOW-2 「≥1 省路由壳或列表入口」）。
// 列表本身仅为导航入口；不评分、不对比、不排名。

import { listIndicators, IS_MOCK_MODE } from "../lib/api";
import { MOCK_PROVINCE_LIST } from "../lib/mock_evidence_chain";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const data = await listIndicators();
  return (
    <section>
      <h1>CEGR — Stage 2 治理观察 (S2.0.1 + S2.7-a)</h1>
      <p style={{ color: "#666" }}>
        {IS_MOCK_MODE
          ? "Mock 模式：以下数据为 S1.18 DEMO sentinel，"
          : "Live 模式：以下数据来自 FastAPI S1.10，"}
        请同时关注页面顶部 <code>mode-banner</code>。
      </p>
      <h2>Indicator inventory</h2>
      <table
        style={{
          borderCollapse: "collapse",
          width: "100%",
          fontSize: 14,
        }}
      >
        <thead>
          <tr style={{ background: "#eee" }}>
            <th style={cellStyle}>indicator_id</th>
            <th style={cellStyle}>geo_count</th>
            <th style={cellStyle}>obs_count</th>
            <th style={cellStyle}>latest_period</th>
          </tr>
        </thead>
        <tbody>
          {data.indicators.map((it) => (
            <tr key={it.indicator_id}>
              <td style={cellStyle}>
                <code>{it.indicator_id}</code>
              </td>
              <td style={cellStyle}>{it.geo_entity_count}</td>
              <td style={cellStyle}>{it.observation_count}</td>
              <td style={cellStyle}>{it.latest_period_start ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 style={{ marginTop: 32 }}>省级观察入口（S2.7-a 列表）</h2>
      <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 14 }}>
        <thead>
          <tr style={{ background: "#eee" }}>
            <th style={cellStyle}>省份</th>
            <th style={cellStyle}>路由</th>
            <th style={cellStyle}>六段数据</th>
          </tr>
        </thead>
        <tbody>
          {MOCK_PROVINCE_LIST.map((p) => (
            <tr key={p.slug}>
              <td style={cellStyle}>{p.name_zh}</td>
              <td style={cellStyle}>
                <a href={`/provinces/${p.slug}`}>/provinces/{p.slug}</a>
              </td>
              <td style={cellStyle}>
                {p.has_full_chain ? "全段（mock）" : "空壳（演示未覆盖）"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p style={{ marginTop: 24, fontSize: 12, color: "#999" }}>
        注：本列表仅作导航入口；不做评分、不做对比、不做排名。
      </p>
    </section>
  );
}

const cellStyle: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "8px 12px",
  textAlign: "left",
};