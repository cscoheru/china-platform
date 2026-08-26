import React from "react";
import { IS_MOCK_MODE, IS_MART_FIXTURE_MODE } from "../lib/api";

// Stage 2 / S2.0.1 — Root layout.
//
// Per docs/34 §4.2: skeleton deliberately includes a top banner announcing
// mock-mode vs real-FastAPI mode so reviewers can never confuse the two.
// S2.7-b-full+: when NEXT_PUBLIC_USE_MART_FIXTURE=1, banner also names the
// mart-shape demo pipeline (still is_demo; not O1 / not Gate PASS).

export const metadata = {
  title: "CEGR — 官方公开数据 · 结构化呈现（demo）",
  description:
    "Official open-data extracts (four-track demo) + Stage 2 governance observation shells. Not O1 / not Gate PASS. Mart-shape city demo when NEXT_PUBLIC_USE_MART_FIXTURE=1.",
};

function bannerBackground(): string {
  if (IS_MART_FIXTURE_MODE) return "#cfe2ff"; // info blue — mart demo pipeline
  if (IS_MOCK_MODE) return "#fff3cd";
  return "#d4edda";
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body
        style={{
          fontFamily:
            "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif",
          margin: 0,
          padding: 0,
          background: "#fafafa",
          color: "#222",
        }}
      >
        <header
          style={{
            padding: "12px 20px",
            background: bannerBackground(),
            borderBottom: "1px solid #ccc",
            fontSize: 14,
          }}
          data-testid="mode-banner"
          data-mart-fixture={IS_MART_FIXTURE_MODE ? "1" : "0"}
        >
          {IS_MART_FIXTURE_MODE ? (
            <>
              ℹ️ <strong>MART DEMO PIPELINE</strong> — 地市页走 mart-shape 演示管道
              （<code>NEXT_PUBLIC_USE_MART_FIXTURE=1</code>）。行级{" "}
              <code>is_demo=true</code>，SHA 占位；<strong>不是</strong> O1 真样本 /
              不宣布 Gate PASS。
              {IS_MOCK_MODE
                ? " Indicator 列表仍用 mock FastAPI（无后端时）。"
                : " Indicator 列表接 Live FastAPI。"}
            </>
          ) : IS_MOCK_MODE ? (
            <>
              ⚠️ <strong>SKELETON MODE</strong> — using mock data
              (NEXT_PUBLIC_USE_MOCK=true). Observations shown are S1.18 DEMO
              sentinels (placeholder SHA).
            </>
          ) : (
            <>
              ✅ <strong>LIVE MODE</strong> — FastAPI at{" "}
              {process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000"}.
              Real SHA-locked data (subject to Stage 1 OPEN gap).
            </>
          )}
        </header>
        <nav
          style={{
            padding: "8px 20px",
            background: "#f0f0f0",
            borderBottom: "1px solid #ccc",
            fontSize: 13,
          }}
          data-testid="site-nav"
        >
          <a href="/" data-testid="site-nav-home">首页</a>
          {" · "}
          <a
            href="/public-extracts"
            data-testid="site-nav-public-extracts"
          >
            公开提取样本（四轨 demo）
          </a>
          <span style={{ marginLeft: 12, color: "#777", fontSize: 12 }}>
            全站顶栏常驻链；四轨 demo / 非 O1 / 不宣布 Gate PASS（per tasking 409）
          </span>
        </nav>
        <main style={{ padding: 24 }}>{children}</main>
      </body>
    </html>
  );
}
