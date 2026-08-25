// Stage 2 / S2.0.1 — Home page.
//
// Lists indicators (mock by default). Onward navigation to a province
// observation page will land in S2.1-S2.7. For now this is just the inventory.

import { listIndicators, IS_MOCK_MODE } from "../lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const data = await listIndicators();
  return (
    <section>
      <h1>CEGR — Stage 2 治理观察 (S2.0.1 骨架)</h1>
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
      <p style={{ marginTop: 24, fontSize: 13, color: "#888" }}>
        省级观察页壳：<a href="/provinces/jiangsu">江苏省</a>
      </p>
    </section>
  );
}

const cellStyle: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "8px 12px",
  textAlign: "left",
};