// Stage 2.7-b-lite — Centralized frontend env-var access.
//
// Per knife env-config (2026-09-13): consolidate all `process.env.NEXT_PUBLIC_*`
// reads into this single typed module. Replaces the previous scatter (5 files,
// 12+ `process.env.NEXT_PUBLIC_*` reads) with one declarative table so the
// Next.js build-time-injected env surface is exhaustively visible in one place.
//
// Why a single module:
//   - API_BASE defaulting drifted (8000 → 8001, knife api-base-fix 1fb9fc8) because
//     the default was duplicated across lib/api.ts and app/layout.tsx. Centralizing
//     makes default drift impossible to overlook.
//   - `process.env.NEXT_PUBLIC_MART_DATA_PATH` is read 5 times in lib/mart-static.ts;
//     renaming the var would silently miss 4 of the 5 reads. With one consumer
//     (`ENV.MART_DATA_PATH`), renames are atomic.
//   - Typed `as const` exports give callers narrow booleans (not `string | undefined`)
//     and avoid `=== "true"` string comparisons scattered through call sites.
//
// Backward compatibility:
//   - `IS_MOCK_MODE`, `IS_MART_FIXTURE_MODE`, `IS_STATIC_MART_DATA_MODE` are
//     re-exported from lib/api.ts (the historical import path) so callers like
//     app/layout.tsx + app/page.tsx that import from "../lib/api" keep working.
//
// Runtime sanity check (dev only, no production cost):
//   - `INJECTED_ENV_VARS` lists every env var this module consumes. In dev
//     we compare against `Object.keys(process.env)` for `NEXT_PUBLIC_*` keys
//     and warn on typos (e.g. NEXT_PUBLIC_MOCK instead of NEXT_PUBLIC_USE_MOCK).
//     In production this check is compiled out.

// knife env-config (2026-09-13): defaults locked to 127.0.0.1:8001 per knife
// api-base-fix (1fb9fc8). newvps 上 8000 端口被 portainer 占用 (返 404),
// FastAPI 实际在 127.0.0.1:8001 (docker-proxy 映射 china-platform-api
// 容器 8000→host 8001).
const DEFAULT_API_BASE = "http://127.0.0.1:8001";

export const ENV = {
  /** NEXT_PUBLIC_USE_MOCK === "true" → mock fallback. Default false (real FastAPI). */
  USE_MOCK: process.env.NEXT_PUBLIC_USE_MOCK === "true",
  /** NEXT_PUBLIC_USE_MART_FIXTURE === "1" → mart-shape demo pipeline. Default false. */
  USE_MART_FIXTURE: process.env.NEXT_PUBLIC_USE_MART_FIXTURE === "1",
  /** NEXT_PUBLIC_USE_MART_FIXTURE === "0" → force mock fixture (cities/[slug] only). Default false. */
  USE_MART_FIXTURE_OFF:
    process.env.NEXT_PUBLIC_USE_MART_FIXTURE === "0",
  /** NEXT_PUBLIC_API_BASE — FastAPI URL. Default 127.0.0.1:8001 (newvps docker-proxy). */
  API_BASE: process.env.NEXT_PUBLIC_API_BASE ?? DEFAULT_API_BASE,
  /** NEXT_PUBLIC_MART_DATA_PATH — path to mart JSON file. Empty string = no static mart. */
  MART_DATA_PATH: process.env.NEXT_PUBLIC_MART_DATA_PATH ?? "",
  /** NEXT_PUBLIC_LANG — UI locale for banner i18n. Default 'zh-CN'.
   *  knife banner-i18n (2026-09-14): consumed by next-intl's getRequestConfig
   *  (frontend/i18n/request.ts). Supported values: 'zh-CN' | 'en-US'.
   *  Any other value falls back to 'zh-CN' (with a dev-mode warn guard below). */
  LANG: process.env.NEXT_PUBLIC_LANG ?? "zh-CN",
} as const;

// Derived mode booleans (kept for backward compat with existing imports from lib/api.ts).
// These are the canonical names; lib/api.ts re-exports them.
export const IS_MOCK_MODE = ENV.USE_MOCK;
export const IS_MART_FIXTURE_MODE = ENV.USE_MART_FIXTURE;
export const IS_STATIC_MART_DATA_MODE = ENV.MART_DATA_PATH.length > 0;

// knife banner-config-extract (2026-09-14): single source of truth for banner mode.
// Replaces scattered IS_*_MODE checks in layout.tsx + page.tsx with one typed string.
// Priority order (per Plan 1, mirrors page.tsx getIndicatorEmptyStateMessage logic):
//   1. live-fetch-failed (loadError set) — error context overrides mode
//   2. static-mart (env NEXT_PUBLIC_MART_DATA_PATH set)
//   3. mart-fixture (env NEXT_PUBLIC_USE_MART_FIXTURE === "1")
//   4. mock (env NEXT_PUBLIC_USE_MOCK === "true")
//   5. live (default — "live-empty" is a page-level sub-state handled in page.tsx)
export type BannerMode =
  | "live"
  | "mock"
  | "mart-fixture"
  | "static-mart"
  | "live-fetch-failed";

export function deriveBannerMode(loadError?: string | null): BannerMode {
  if (loadError) return "live-fetch-failed";
  if (IS_STATIC_MART_DATA_MODE) return "static-mart";
  if (IS_MART_FIXTURE_MODE) return "mart-fixture";
  if (IS_MOCK_MODE) return "mock";
  return "live";
}

/**
 * Exhaustive list of NEXT_PUBLIC_* env vars consumed by the frontend.
 * Used by dev-mode sanity check below; serves as a documentation index.
 */
export const INJECTED_ENV_VARS = [
  "NEXT_PUBLIC_USE_MOCK",
  "NEXT_PUBLIC_USE_MART_FIXTURE",
  "NEXT_PUBLIC_API_BASE",
  "NEXT_PUBLIC_MART_DATA_PATH",
  "NEXT_PUBLIC_LANG",
] as const;

export type InjectedEnvVar = (typeof INJECTED_ENV_VARS)[number];

// Runtime typo guard (dev only, compiled out of production bundles).
// On every server start, compare actual process.env keys against the declared
// set; warn if any NEXT_PUBLIC_* key is present but not declared (typo) or
// if any declared key is unexpectedly absent (config dropped).
if (process.env.NODE_ENV !== "production") {
  const declared = new Set<string>(INJECTED_ENV_VARS);
  const injectedActual = Object.keys(process.env).filter((k) =>
    k.startsWith("NEXT_PUBLIC_")
  );
  for (const k of injectedActual) {
    if (!declared.has(k)) {
      // eslint-disable-next-line no-console
      console.warn(
        `[env-config] Undeclared NEXT_PUBLIC_* env var detected: ${k}. ` +
          `If intentional, add it to INJECTED_ENV_VARS in frontend/lib/env.ts.`
      );
    }
  }
  // knife banner-i18n (2026-09-14): warn if NEXT_PUBLIC_LANG is set to an
  // unsupported value. Mirrors the fallback in i18n/request.ts — both
  // locations must agree on the supported list, otherwise the dev warn
  // would fire for a value that request.ts silently accepts.
  const supportedLangs = new Set(["zh-CN", "en-US"]);
  if (
    process.env.NEXT_PUBLIC_LANG &&
    !supportedLangs.has(process.env.NEXT_PUBLIC_LANG)
  ) {
    // eslint-disable-next-line no-console
    console.warn(
      `[env-config] NEXT_PUBLIC_LANG="${process.env.NEXT_PUBLIC_LANG}" ` +
        `is not in supported list ["zh-CN","en-US"]. Falling back to "zh-CN". ` +
        `If intentional, extend the supported list in frontend/lib/env.ts + i18n/request.ts.`
    );
  }
}