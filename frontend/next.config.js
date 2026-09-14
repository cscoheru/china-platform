/** Stage 2 / S2.0.1 — Next.js config.
 *
 * Per docs/34 §5: frontend is read-only; no API rewrites; mock toggle via
 * NEXT_PUBLIC_USE_MOCK env (not a server proxy).
 *
 * knife banner-i18n (2026-09-14): next-intl plugin for request-scoped i18n
 * config. Reads NEXT_PUBLIC_LANG; no [locale] routing segment required.
 * Per knife banner-config-extract closure (b64b865): keep 5 BannerMode union;
 * sub-key split for mart-fixture ternary lives in lib/i18n.ts.
 */
const createNextIntlPlugin = require("next-intl/plugin");
const withNextIntl = createNextIntlPlugin("./i18n/request.ts");

const nextConfig = {
  reactStrictMode: true,
  // No rewrites — frontend talks to FastAPI directly via NEXT_PUBLIC_API_BASE.
  // Per tasking 146: no new write API; upload still goes through S1.13 admin.
};

module.exports = withNextIntl(nextConfig);