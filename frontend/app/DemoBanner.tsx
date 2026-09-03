// DemoBanner.tsx — 662 D5 demo 壳显式标注横幅.
//
// Per 662 tasking §1.662-D5 + docs/87 §3.1 P1 先行:
// 4 demo 页 (seven-dim / research/m1-series / research/q1-2024-gdp /
// public-extracts) 顶部插显式 DEMO/MOCK 横幅, 不冒充真数据, 静默 demo 风险.
//
// 与 DemoBadge 区别: DemoBadge 是 inline 标签 (在卡片或单元格里);
// DemoBanner 是 page-top aside (整页顶部黄色 banner).
//
// SSR 友好: 不需要 "use client" (server component).
// ARIA: aside 标签 + role="status" + 醒目 (黄色背景 + emoji + 强色文字).

import type { ReactElement } from "react";

export interface DemoBannerProps {
  /** 一行说明为什么是 demo / 演示范围 / 与真数据差距. */
  reason: string;
  /** 可选: 数据来源标签 (e.g. "mock_seven_dim.ts" / "1 行真 observation"). */
  source?: string;
}

export function DemoBanner({
  reason,
  source,
}: DemoBannerProps): ReactElement {
  return (
    <aside
      data-testid="demo-banner"
      role="status"
      aria-label="Demo 演示横幅"
      style={{
        marginTop: 12,
        marginBottom: 16,
        padding: "10px 14px",
        background: "#fff8e1",
        border: "1px solid #ffeeba",
        borderLeft: "4px solid #b45309",
        borderRadius: 3,
        fontSize: 13,
        color: "#856404",
        lineHeight: 1.6,
      }}
    >
      <strong style={{ marginRight: 6 }}>🎭 DEMO / MOCK</strong>
      <span style={{ marginRight: 8 }}>
        本页为演示页面, 不代表 O1 / Gate PASS / M2 PASS.
      </span>
      <span data-testid="demo-banner-reason">{reason}</span>
      {source && (
        <span style={{ marginLeft: 8, color: "#666" }}>
          数据源: <code style={{ fontSize: 11 }}>{source}</code>
        </span>
      )}
    </aside>
  );
}
