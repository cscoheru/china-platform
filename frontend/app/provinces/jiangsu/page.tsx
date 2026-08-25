// Stage 2 / S2.0.1 + S2.7-a — Jiangsu provincial observation page.
//
// Per docs/34 §4.1 序 1-3: 至少首页 + 1 个省级观察页壳 + 调用/展示 indicator series.
// S2.7-a 增量：挂上六段证据链 UI 雏形（per docs/06 §2 + tasking 168）。
//
// This page demonstrates:
//   - 省级 header + observation card count placeholder
//   - Indicator series table for Jiangsu GDP (mock or real)
//   - <DemoBadge /> next to every row whose lineage.is_demo === "true"
//   - <EvidenceChain /> 六段证据链 (CONDITION → COMMITMENT → INPUT →
//     PROCESS → OUTPUT → OUTCOME_RISK)
//   - 七维度观察卡 placeholder (per S2.8 未来刀)
//
// FIX per tasking 150 (Cursor 149 FAIL): the route is a STATIC segment at
// /provinces/jiangsu/, so it does NOT receive `params.province`. Earlier code
// compared `params.province !== "jiangsu"`, which is always true on a static
// route → page always rendered the "尚未支持" branch and never the series
// table. Fix: drop the param gate entirely; this page IS the jiangsu page by
// virtue of its file path. Other provinces land in S2.7-b ~ S2.7-e with their
// own static pages (or a [province]/ dynamic page when we move to 5+ provinces).

import { indicatorSeries } from "../../../lib/api";
import { MOCK_PROVINCE_META } from "../../../lib/mock";
import { getMockEvidenceChain } from "../../../lib/mock_evidence_chain";
import { DemoBadge } from "../../DemoBadge";
import { EvidenceChain } from "../../components/EvidenceChain";

export const dynamic = "force-dynamic";

export default async function ProvincePage() {
  // No params gate — this page IS the jiangsu page by virtue of its file path.
  // S2.0.1 ships only the Jiangsu GDP series mock. Real SHA-locked data
  // lands in S2.0.2; <DemoBadge /> will auto-hide when is_demo becomes "false".
  const series = await indicatorSeries(
    "JIANGSU-GDP-INDICATOR-UUID-MOCK",
    "JIANGSU-GEO-UUID-MOCK"
  );

  const { province_name_zh, observation_card_count } = MOCK_PROVINCE_META;
  const evidenceChain = getMockEvidenceChain("jiangsu");
  if (!evidenceChain) {
    // 这是 schema 错误而非 UI 选择：mock 必须提供六段。
    throw new Error("Evidence chain mock missing for jiangsu");
  }

  return (
    <section>
      <h1>
        {province_name_zh} 省级观察页 <small style={{ fontSize: 14, color: "#888" }}>S2.0.1 + S2.7-a</small>
      </h1>
      <p style={{ color: "#666" }}>
        六段证据链 UI 雏形见下；七维度观察卡占位 {observation_card_count} 个。
      </p>

      <EvidenceChain segments={evidenceChain.segments} />

      <h2 style={{ marginTop: 32 }}>Indicator series · GDP growth (yoy %)</h2>
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
        S2.7-a = 六段证据链 UI 雏形（mock）；S2.7-b ~ S2.7-e = 其余 4 省；
        S2.1 / S2.2 / S2.4 = 真实数据接入 person/tenure / policy / budget；
        S2.8 = 七维度观察卡可点击展开。
      </p>
    </section>
  );
}

const cellStyle: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "6px 10px",
  textAlign: "left",
};