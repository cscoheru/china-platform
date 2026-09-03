// Stage 2 / S2.9-lite + 661 P1 — Peer-region comparison page.
//
// Per tasking 244 §SCHEMA "peer 对比壳 (mock OK)".
// 661 升级 per docs/87 §3.1 P1 先行 + C4: real data 化 (mart 静态导出).
//
// 数据源选择 (per docs/87 §3.1 + 红线 4 「mock 不删」):
//   1. 优先 buildRealPeerCompareGroup() (mart 静态导出真数据)
//   2. 回退 MOCK_PEER_COMPARE_REGION (历史资产 + NEXT_PUBLIC_USE_MOCK=true 路径)
//
// 红线 (per docs/43 §8 + docs/06 §6.6 + docs/05 §8.3):
//   - 不评分 / 不排名 / 不派生地区得分
//   - 禁按 GDP 总量取 top N
//   - selection_method = "manual"
//   - 4 省名单固定 (江苏 + 浙江/广东/山东), 不动态扩
//   - 不爬网 / 不接后端

import type { ReactElement } from "react";
import PeerCompareGrid from "../components/PeerCompareCard";
import {
  MOCK_PEER_COMPARE_REGION,
  buildRealPeerCompareGroup,
  type RealPeerCompareGroup,
} from "../../lib/mock_peer_compare";
import { SourcePopover } from "../components/SourcePopover";

export default function PeerComparePage(): ReactElement {
  const real = buildRealPeerCompareGroup();

  if (real) {
    return <RealPeerCompareView group={real} />;
  }

  // 回退通道: mart 未配置或 4 省名单缺失时走 mock (per 红线 4).
  return (
    <main className="peer-compare-page">
      <header className="peer-compare-page__header">
        <h1>Stage 2 / S2.9-lite 同类地区对比 (mock · 回退通道)</h1>
        <p>
          本页面仅演示同类地区对比卡的折叠/展开 UI 形态；
          数据来自 <code>frontend/lib/mock_peer_compare.ts</code>，不接后端。
        </p>
        <p className="peer-compare-page__note">
          ⚠ 仅展示计数；不排名；不算分（per docs/06 §6.6 红线）
        </p>
      </header>
      <PeerCompareGrid region={MOCK_PEER_COMPARE_REGION} />
    </main>
  );
}

// 661 P1 real-data 视图: 4 省 × 4 指标 (总量/增速/二产/三产) 真实 mart 数据.
// 不调用 PeerCompareCard (它需要 evidence/seven-dim 字段, 661 不接 per docs/43 §5.1+§5.2).
function RealPeerCompareView({
  group,
}: {
  group: RealPeerCompareGroup;
}): ReactElement {
  const allMembers = [group.focal, ...group.peers];
  return (
    <main className="peer-compare-page">
      <header className="peer-compare-page__header">
        <h1 data-testid="peer-compare-h">
          {group.group_name_zh}
        </h1>
        <p style={{ color: "#1a7f37", fontSize: 13 }}>
          ✅ 4 省 2024 真实数据，全部来自 <code>{group.data_source}</code>
          （knife 660 Track B + 661 P1 切片）。
          selection_method=<code>{group.selection_method}</code>（仅 manual 落地）。
        </p>
        <p style={{ color: "#666", fontSize: 13 }}>
          {group.selection_justification}
        </p>
        <p style={{ color: "#666", fontSize: 13 }}>
          ⚠ 仅展示数值；不评分；不排名；不派生地区得分（per docs/06 §6.6 红线）
        </p>
      </header>

      <table
        data-testid="peer-compare-real-table"
        style={{
          borderCollapse: "collapse",
          width: "100%",
          fontSize: 13,
          marginTop: 16,
        }}
      >
        <thead>
          <tr style={{ background: "#eee" }}>
            <th style={cellStyle}>地区</th>
            <th style={cellStyle}>角色</th>
            {group.metric_keys.map((m) => (
              <th key={m.key} style={cellStyle}>
                {m.label} ({m.unit})
              </th>
            ))}
            <th style={cellStyle}>溯源</th>
          </tr>
        </thead>
        <tbody>
          {allMembers.map((m) => (
            <tr
              key={m.province_code}
              data-testid={`peer-row-${m.province_code}`}
              data-role={m.role}
              style={
                m.role === "focal"
                  ? { background: "#e6f4ff", fontWeight: 600 }
                  : undefined
              }
            >
              <td style={cellStyle}>{m.province_name}</td>
              <td style={cellStyle}>
                <span
                  style={{
                    display: "inline-block",
                    padding: "2px 6px",
                    background: m.role === "focal" ? "#0969da" : "#999",
                    color: "#fff",
                    fontSize: 10,
                    fontWeight: 700,
                    borderRadius: 3,
                  }}
                  data-testid={`peer-role-${m.province_code}`}
                >
                  {m.role.toUpperCase()}
                </span>
              </td>
              {group.metric_keys.map((mk) => {
                const v = m.metrics[mk.key as keyof typeof m.metrics];
                return (
                  <td
                    key={mk.key}
                    style={cellStyle}
                    data-testid={`peer-cell-${m.province_code}-${mk.key}`}
                  >
                    {mk.isPct ? fmtPct(v) : fmtNum(v)}
                  </td>
                );
              })}
              <td style={cellStyle}>
                <SourcePopover
                  sourceUrl={m.source_url}
                  hashPrefix={m.source_hash_prefix}
                  lineageSource={m.lineage_source}
                  lineageOrigin={m.lineage_origin}
                  ruling="U6 2026-09-02"
                  sourceLabel={m.lineage_source}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <p style={{ marginTop: 24 }}>
        <a href="/">← 返回首页</a>
      </p>
    </main>
  );
}

const cellStyle: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "6px 10px",
  textAlign: "left",
};

// 660-P1 修复版 (沿用); 接受 string | number | null.
function fmtNum(v: number | string | null): string {
  if (v === null || v === undefined) return "—";
  const raw = typeof v === "string" ? v.trim() : v;
  if (raw === "" || raw === undefined) return "—";
  const n = typeof raw === "string" ? Number(raw) : raw;
  if (!Number.isFinite(n)) return "—";
  return n.toLocaleString("zh-CN", { maximumFractionDigits: 2 });
}

function fmtPct(v: number | string | null): string {
  if (v === null || v === undefined) return "—";
  const raw = typeof v === "string" ? v.trim() : v;
  if (raw === "" || raw === undefined) return "—";
  const n = typeof raw === "string" ? Number(raw) : raw;
  if (!Number.isFinite(n)) return "—";
  return n.toFixed(1);
}