import React from "react";
import { IS_MOCK_MODE } from "../lib/api";
import { ENV } from "../lib/env";
import { deriveBannerMode, type BannerMode } from "../lib/env";

// Stage 2 / S2.0.1 — Root layout.
//
// Per docs/34 §4.2: skeleton deliberately includes a top banner announcing
// mock-mode vs real-FastAPI mode so reviewers can never confuse the two.
// Per knife 659 tasking §1.659-A: banner 横幅文案更新
// "S1.18 DEMO observations" → "28 省 2024 真实数据（官方 5 + 转载锚定 23; 3 省源缺文）+ lineage 可溯"
// S2.7-b-full+: when NEXT_PUBLIC_USE_MART_FIXTURE=1, banner also names the
// mart-shape demo pipeline (still is_demo; not O1 / not Gate PASS).
//
// knife banner-config-extract (2026-09-14): mode derivation centralized via
// deriveBannerMode() in lib/env.ts. Layout banner handles 4 modes (live /
// mock / mart-fixture / static-mart); the "live-fetch-failed" mode is rendered
// by page.tsx where the fetch error is in scope.

export const metadata = {
  title: "CEGR — 官方公开数据 · 结构化呈现（demo）",
  description:
    "Official open-data extracts (four-track demo) + Stage 2 governance observation shells. Not O1 / not Gate PASS. Mart-shape city demo when NEXT_PUBLIC_USE_MART_FIXTURE=1.",
};

// Layout never has loadError context (no fetch here), so 4-mode switch.
const LAYOUT_BANNER_MODE: BannerMode = deriveBannerMode();

function bannerBackground(mode: BannerMode): string {
  switch (mode) {
    case "mart-fixture":
      return "#cfe2ff"; // info blue — mart demo pipeline
    case "mock":
      return "#fff3cd"; // warning yellow — mock fallback
    case "static-mart":
      return "#e2e3e5"; // neutral gray — static JSON file
    case "live":
    case "live-fetch-failed":
      return "#d4edda"; // success green — real FastAPI
  }
}

function bannerContent(mode: BannerMode): React.ReactNode {
  switch (mode) {
    case "mart-fixture":
      return (
        <>
          ℹ️ <strong>MART DEMO PIPELINE</strong> — 地市页走 mart-shape 演示管道
          （<code>NEXT_PUBLIC_USE_MART_FIXTURE=1</code>）。行级{" "}
          <code>is_demo=true</code>，SHA 占位；<strong>不是</strong> O1 真样本 /
          不宣布 Gate PASS。
          {IS_MOCK_MODE
            ? " Indicator 列表仍用 mock FastAPI（无后端时）。"
            : " Indicator 列表接 Live FastAPI。"}
        </>
      );
    case "mock":
      return (
        <>
          ⚠️ <strong>MOCK MODE</strong> — using mock data
          (NEXT_PUBLIC_USE_MOCK=true). Observations shown are S1.18 DEMO
          sentinels (placeholder SHA). 省 GDP 走 mock（S1.18 历史资产）。
        </>
      );
    case "static-mart":
      return (
        <>
          📦 <strong>STATIC MART MODE</strong> — 走 <code>NEXT_PUBLIC_MART_DATA_PATH</code>
          {" "}JSON 文件（<code>mart_province_gdp_2024.json</code>）。28 省 2024 +
          {" "}3 缺失 + 1 国家锚；此模式下 <strong>不需要</strong> FastAPI backend
          {" "}（per knife 660 Track B）。
        </>
      );
    case "live":
    case "live-fetch-failed":
      return (
        <>
          ✅ <strong>LIVE MODE</strong> — 28 省 2024 真实数据（官方 5 +
          转载锚定 23; 3 省源缺文）+ lineage 可溯。
          FastAPI at <code>{ENV.API_BASE}</code>.
          Per knife 659 tasking §1.659-A（USE_MOCK 语义翻转，默认 false 真数据）。
        </>
      );
  }
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
            background: bannerBackground(LAYOUT_BANNER_MODE),
            borderBottom: "1px solid #ccc",
            fontSize: 14,
          }}
          data-testid="mode-banner"
          data-banner-mode={LAYOUT_BANNER_MODE}
          data-mart-fixture={LAYOUT_BANNER_MODE === "mart-fixture" ? "1" : "0"}
          data-static-mart={LAYOUT_BANNER_MODE === "static-mart" ? "1" : "0"}
          data-mock={LAYOUT_BANNER_MODE === "mock" ? "1" : "0"}
        >
          {bannerContent(LAYOUT_BANNER_MODE)}
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
          {/* 662 D5: LIVE/DEMO 导航分组 (per docs/87 §3.1 P1 先行). */}
          <span
            data-testid="site-nav-live-group"
            style={{ marginRight: 12 }}
          >
            <strong style={{ color: "#1a7f37" }}>● LIVE 数据:</strong>{" "}
            <a href="/" data-testid="site-nav-home">首页</a>
            {" · "}
            <a href="/indicators" data-testid="site-nav-indicators">
              5 指标定义
            </a>
            {" · "}
            <a href="/provinces/beijing" data-testid="site-nav-province-sample">
              省详情样例
            </a>
            {" · "}
            <a href="/peer-compare" data-testid="site-nav-peer-compare">
              同类对比
            </a>
            {" · "}
            <a href="/timeseries" data-testid="site-nav-timeseries">
              26 年时序折线
            </a>
          </span>
          <span
            data-testid="site-nav-demo-group"
            style={{
              marginLeft: 12,
              paddingLeft: 12,
              borderLeft: "1px solid #ccc",
            }}
          >
            <strong style={{ color: "#b45309" }}>🎭 DEMO 壳:</strong>{" "}
            <a
              href="/public-extracts"
              data-testid="site-nav-public-extracts"
            >
              公开提取样本（四轨）
            </a>
            {" · "}
            <a
              href="/research/m1-series"
              data-testid="site-nav-m1-series"
            >
              M1 验收面
            </a>
            {" · "}
            <a
              href="/research/q1-2024-gdp"
              data-testid="site-nav-q1-2024-gdp"
            >
              M2-e 验收面
            </a>
            {" · "}
            <a href="/seven-dim" data-testid="site-nav-seven-dim">
              七维观察卡
            </a>
          </span>
          <span
            style={{
              marginLeft: 12,
              paddingLeft: 12,
              borderLeft: "1px solid #ccc",
              color: "#777",
              fontSize: 12,
            }}
          >
            四轨 demo / 非 O1 / 不宣布 Gate PASS（per tasking 409 · 662 D5）
          </span>
        </nav>
        <main style={{ padding: 24 }}>{children}</main>
      </body>
    </html>
  );
}
