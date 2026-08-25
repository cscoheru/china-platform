// DemoBadge — renders only when lineage.is_demo === "true".
//
// Per tasking 146 §SCHEMA: "须能区分/展示 is_demo vs 未来真实 SHA".
// This is the contract: when S2.0.2 ships real SHA-locked data, the badge
// auto-disappears (no frontend code change required).
//
// Stage 2 / S2.0.1.

import React from "react";

interface DemoBadgeProps {
  lineage?: { is_demo?: string; demo_reason?: string } | null;
}

export function DemoBadge({ lineage }: DemoBadgeProps): React.ReactElement | null {
  if (lineage?.is_demo !== "true") return null;
  return (
    <span
      data-testid="demo-badge"
      title={lineage.demo_reason ?? "DEMO sentinel"}
      style={{
        display: "inline-block",
        marginLeft: 8,
        padding: "2px 8px",
        background: "#fff3cd",
        color: "#856404",
        border: "1px solid #ffeeba",
        borderRadius: 4,
        fontSize: 12,
        fontWeight: 600,
      }}
    >
      DEMO · placeholder SHA
    </span>
  );
}

export default DemoBadge;