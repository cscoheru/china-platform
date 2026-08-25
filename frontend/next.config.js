/** Stage 2 / S2.0.1 — Next.js config.
 *
 * Per docs/34 §5: frontend is read-only; no API rewrites; mock toggle via
 * NEXT_PUBLIC_USE_MOCK env (not a server proxy).
 */
const nextConfig = {
  reactStrictMode: true,
  // No rewrites — frontend talks to FastAPI directly via NEXT_PUBLIC_API_BASE.
  // Per tasking 146: no new write API; upload still goes through S1.13 admin.
};

module.exports = nextConfig;