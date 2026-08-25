// Stage 2 / S2.0.1 — Jiangsu provincial observation page (skeleton shell).
//
// Per docs/34 §4.1 序 1-3: 至少首页 + 1 个省级观察页壳 + 调用/展示 indicator series.
// This page is the shell. S2.1-S2.6 will add: person/tenure, policy_document,
// project_event, budget_allocation, inference_record, claim_evidence_link
// into the six-segment evidence chain (per docs/08 §3.2).
//
// For now the page demonstrates:
//   - 省级 header + observation card count placeholder
//   - Indicator series table for Jiangsu GDP (mock or real)
//   - <DemoBadge /> next to every row whose lineage.is_demo === "true"
//   - 七维度观察卡 placeholder (per S2.8 未来刀)

import { indicatorSeries } from "../../../lib/api";
import { MOCK_PROVINCE_META } from "../../../lib/mock";
import { DemoBadge } from "../../DemoBadge";

export const dynamic = "force-dynamic";

interface PageProps {
  params: { province: string };
}

export default async function ProvincePage({ params }: PageProps) {
  // Only Jiangsu is shipped in S2.0.1; others fall back to "not yet supported".
  if (params.province !== "jiangsu") {
    return (
      <section>
        <h1>省级观察页：{params.province}</h1>
        <p style={{ color: "#888" }}>
          S2.0.1 骨架仅交付江苏省壳。其余 4 省待 S2.7-b ~ S2.7-e 落地。
        </p>
      </section>
    );
  }

  // S2.0.1 ships only the Jiangsu GDP series mock. Real SHA-locked data
  // lands in S2.0.2; <DemoBadge /> will auto-hide when is_demo becomes "false".
  const series = await indicatorSeries(
    "JIANGSU-GDP-INDICATOR-UUID-MOCK",
    "JIANGSU-GEO-UUID-MOCK"
  );

  const { province_name_zh, observation_card_count } = MOCK_PROVINCE_META;

  return (
    <section>
      <h1>
        {province_name_zh} 省级观察页 <small style={{ fontSize: 14, color: "#888" }}>S2.0.1 骨架</small>
      </h1>
      <p style={{ color: "#666" }}>
        六段证据链 UI 待 S2.7-b；七维度观察卡占位 {observation_card_count} 个。
      </p>

      <h2 style={{ marginTop: 24 }}>Indicator series · GDP growth (yoy %)</h2>
      <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 14 }}>
        <thead>
          <tr style={{ background: "#eee" }}>
            <th style={cellStyle}>period_start</th>
            <th style={cellStyle}>value</th>
            <th style={cellStyle}>unit</th>
            <th style={cellStyle}>verification</th>
            <th style={cellStyle}>source_level</th>
            <th style={cellStyle}>flags</th>
          </tr>
        </thead>
        <tbody>
          {series.series.map((pt) => (
            <tr key={`${pt.indicator_id}-${pt.period_start}`}>
              <td style={cellStyle}>{pt.period_start}</td>
              <td style={cellStyle}>{pt.value.toFixed(1)}</td>
              <td style={cellStyle}>{pt.unit}</td>
              <td style={cellStyle}>{pt.verification_status}</td>
              <td style={cellStyle}>{pt.source_level}</td>
              <td style={cellStyle}>
                <DemoBadge lineage={pt.lineage} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 style={{ marginTop: 32 }}>七维度观察卡（占位）</h2>
      <ul style={{ color: "#888", fontSize: 13 }}>
        <li>财政</li>
        <li>人口 / 人才</li>
        <li>产业</li>
        <li>基础设施</li>
        <li>环境</li>
        <li>治理</li>
        <li>创新</li>
      </ul>
      <p style={{ fontSize: 12, color: "#999", marginTop: 24 }}>
        S2.0.1 = 骨架；S2.1-S2.6 = 数据；S2.7-b ~ S2.7-e = 其余 4 省；S2.8 =
        七维度观察卡可点击展开。
      </p>
    </section>
  );
}

const cellStyle: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "6px 10px",
  textAlign: "left",
};