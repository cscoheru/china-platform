// Stage 2.7-i18n — knife banner-i18n.
//
// Thin wrapper around next-intl's getTranslations. Keeps banner message
// resolution isolated from JSX so:
//   - app/layout.tsx calls getBannerTranslations(mode, "layout")
//   - app/page.tsx   calls getBannerTranslations(mode, "page")
//
// This module exists to:
//   (a) absorb the mart-fixture sub-key split (IS_MOCK_MODE inline ternary
//       was previously in layout.tsx; per plan 决策 (c) 拆为 2 独立 mode entries)
//   (b) keep the JSX components clean of i18n machinery
//   (c) centralize the message-key ↔ BannerMode mapping in one place
//
// All functions are server-only (no "use client"). next-intl's getTranslations
// is request-scoped and never bundled to the client, so reading ENV / IS_MOCK_MODE
// here has zero bundle cost.
//
// Per knife banner-config-extract (2026-09-14, b64b865): the BannerMode union
// stays at 5 values. mart-fixture ternary is NOT a new BannerMode — it's a
// sub-key decision that lives here, in getBannerMessageKey().

import { getTranslations } from "next-intl/server";
import { IS_MOCK_MODE } from "./api";
import type { BannerMode } from "./env";

export type BannerScope = "layout" | "page";

/**
 * Resolve the i18n message namespace for a (mode, scope) pair.
 *
 * Examples (zh-CN default):
 *   ("live", "layout")             → "layout.live"
 *   ("live-fetch-failed", "page")  → "page.liveFetchFailed"   (camelCase key)
 *   ("mart-fixture", "layout")     → "layout.martFixtureMock"  if IS_MOCK_MODE
 *                                    "layout.martFixtureLive"  otherwise
 *   ("static-mart", "layout")      → "layout.staticMart"
 *
 * Returns the *namespace prefix* (e.g. "layout.live"). Callers then look up
 * sub-keys like t(`${ns}.icon`), t(`${ns}.title`), t(`${ns}.body`), etc.
 *
 * The camelCase conversion is intentional: JSON keys are camelCase by
 * convention; BannerMode is kebab-case for HTML attribute consistency.
 */
export function getBannerMessageKey(
  mode: BannerMode,
  scope: BannerScope
): string {
  // mart-fixture ternary split: layout has 2 sub-entries, page uses 1.
  if (mode === "mart-fixture" && scope === "layout") {
    return IS_MOCK_MODE ? "layout.martFixtureMock" : "layout.martFixtureLive";
  }

  // All other modes map directly; convert kebab-case → camelCase for JSON keys.
  const camelMode =
    mode === "static-mart"
      ? "staticMart"
      : mode === "live-fetch-failed"
        ? "liveFetchFailed"
        : mode;

  return `${scope}.${camelMode}`;
}

/**
 * Server-component wrapper. Returns next-intl's translation function scoped
 * to the "banner" namespace. Caller is responsible for choosing the right
 * sub-key via getBannerMessageKey() OR using a literal key.
 *
 * Example:
 *   const t = await getBannerTranslations("live", "layout");
 *   const title = t("layout.live.title");
 *
 * The mode + scope parameters are accepted for symmetry / future extensibility
 * (e.g. caching per (mode, scope)) but are not currently used to filter the
 * translation function — the caller passes the full dotted path.
 */
export async function getBannerTranslations(
  _mode: BannerMode,
  _scope: BannerScope
): Promise<ReturnType<typeof getTranslations>> {
  return await getTranslations("banner");
}