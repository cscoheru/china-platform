import React from "react";
import { IS_MOCK_MODE } from "../lib/api";

// Stage 2 / S2.0.1 — Root layout.
//
// Per docs/34 §4.2: skeleton deliberately includes a top banner announcing
// mock-mode vs real-FastAPI mode so reviewers can never confuse the two.

export const metadata = {
  title: "CEGR — Stage 2 Skeleton (S2.0.1)",
  description:
    "Read-only observation layer over cegr_staging. Mock-mode by default.",
};

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
            background: IS_MOCK_MODE ? "#fff3cd" : "#d4edda",
            borderBottom: "1px solid #ccc",
            fontSize: 14,
          }}
          data-testid="mode-banner"
        >
          {IS_MOCK_MODE ? (
            <>
              ⚠️ <strong>SKELETON MODE</strong> — using mock data
              (NEXT_PUBLIC_USE_MOCK=true). Observations shown are S1.18 DEMO
              sentinels (placeholder SHA).
            </>
          ) : (
            <>
              ✅ <strong>LIVE MODE</strong> — FastAPI at
              {" "}
              {process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000"}.
              Real SHA-locked data (subject to Stage 1 OPEN gap).
            </>
          )}
        </header>
        <main style={{ padding: 24 }}>{children}</main>
      </body>
    </html>
  );
}