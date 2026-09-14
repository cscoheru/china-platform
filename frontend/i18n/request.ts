// Stage 2.7-i18n — knife banner-i18n.
//
// next-intl request-scoped config. Reads NEXT_PUBLIC_LANG from the env (which
// itself is derived from ENV.LANG in lib/env.ts, but next-intl's getRequestConfig
// runs in a server context where process.env is available directly).
//
// Per next-intl 3.x docs (https://next-intl.dev/docs/getting-started/app-router):
// getRequestConfig is called once per request (server-side); it is NOT bundled
// into the client, so reading process.env here is safe. The dynamic import
// `await import(`../messages/${locale}/banner.json`)` lets next-intl's bundler
// tree-shake unused locale JSONs at build time.
//
// Falls back to 'zh-CN' to satisfy the red line "banner text must remain Chinese
// by default" (per knife banner-config-extract closure 2026-09-14). Supported
// locales are kept in sync with the dev-mode warn guard in lib/env.ts.
//
// No [locale] routing segment — server-side only locale switching via env var.
// future-proofs without committing to URL-based i18n yet.

import { getRequestConfig } from "next-intl/server";

const SUPPORTED_LOCALES = ["zh-CN", "en-US"] as const;
type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];

function isSupported(locale: string): locale is SupportedLocale {
  return (SUPPORTED_LOCALES as readonly string[]).includes(locale);
}

export default getRequestConfig(async () => {
  const raw = process.env.NEXT_PUBLIC_LANG ?? "zh-CN";
  const locale: SupportedLocale = isSupported(raw) ? raw : "zh-CN";

  return {
    locale,
    messages: (await import(`../messages/${locale}/banner.json`)).default,
  };
});