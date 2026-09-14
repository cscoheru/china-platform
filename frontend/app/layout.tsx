import React from "react";
import { IS_MOCK_MODE } from "../lib/api";
import { ENV } from "../lib/env";
import { deriveBannerMode, type BannerMode } from "../lib/env";
import { getBannerTranslations } from "../lib/i18n";

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

/**
 * Async server-component banner content. Reads message strings from the
 * next-intl "banner" namespace (frontend/messages/{LANG}/banner.json).
 *
 * Per knife banner-i18n (2026-09-14): mart-fixture ternary split lives in
 * getBannerMessageKey() — this function just dispatches on mode and looks
 * up the right sub-keys. The pre-bundle BannerMode union stays at 5.
 *
 * live-fetch-failed is unreachable in layout (loadError not in scope here),
 * but the switch still handles it for exhaustiveness: it falls back to the
 * live banner content (same green background).
 */
async function getLayoutBannerContent(
  mode: BannerMode
): Promise<React.ReactNode> {
  const t = await getBannerTranslations(mode, "layout");
  switch (mode) {
    case "mart-fixture": {
      const subKey = IS_MOCK_MODE ? "martFixtureMock" : "martFixtureLive";
      return (
        <>
          {t(`layout.${subKey}.icon`)}{" "}
          <strong>{t(`layout.${subKey}.title`)}</strong>
          {" — "}
          {t(`layout.${subKey}.body`)}
          {t(`layout.${subKey}.indicatorNote`)}
        </>
      );
    }
    case "mock":
      return (
        <>
          {t("layout.mock.icon")} <strong>{t("layout.mock.title")}</strong>
          {" — "}
          {t("layout.mock.body")}
        </>
      );
    case "static-mart":
      return (
        <>
          {t("layout.staticMart.icon")}{" "}
          <strong>{t("layout.staticMart.title")}</strong>
          {" — "}
          {t("layout.staticMart.body")}
        </>
      );
    case "live":
      return (
        <>
          {t("layout.live.icon")} <strong>{t("layout.live.title")}</strong>
          {" — "}
          {t("layout.live.body")} FastAPI at <code>{ENV.API_BASE}</code>.{" "}
          {t("layout.live.apiNote", { apiBase: ENV.API_BASE })}
        </>
      );
    case "live-fetch-failed":
      // Unreachable in layout (no fetch here), but kept for exhaustive switch.
      // Renders the same green-banner content as "live".
      return (
        <>
          {t("layout.live.icon")} <strong>{t("layout.live.title")}</strong>
          {" — "}
          {t("layout.live.body")} FastAPI at <code>{ENV.API_BASE}</code>.{" "}
          {t("layout.live.apiNote", { apiBase: ENV.API_BASE })}
        </>
      );
  }
}

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const bannerNode = await getLayoutBannerContent(LAYOUT_BANNER_MODE);
  return (
    <html lang={ENV.LANG} data-lang={ENV.LANG}>
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
          data-lang={ENV.LANG}
        >
          {bannerNode}
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
