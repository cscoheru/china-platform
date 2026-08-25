// Stage 2 / S2.0.1 — Typed fetcher with mock switch.
//
// Per docs/34 §5:
//   - Read-only consumer of S1.10 FastAPI.
//   - No new write API; upload still goes through S1.13 admin.
//   - Mock mode allows the skeleton to render without Postgres.
//
// Set NEXT_PUBLIC_USE_MOCK=true to skip FastAPI and return lib/mock.ts.

import type { IndicatorListResponse, IndicatorSeriesResponse } from "./types";
import { MOCK_INDICATOR_LIST, MOCK_JIANGSU_GDP_SERIES } from "./mock";

const USE_MOCK =
  process.env.NEXT_PUBLIC_USE_MOCK !== "false"; // default true (skeleton mode)
const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function listIndicators(): Promise<IndicatorListResponse> {
  if (USE_MOCK) {
    return MOCK_INDICATOR_LIST;
  }
  const res = await fetch(`${API_BASE}/api/indicator?page=1&page_size=50`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`listIndicators: ${res.status}`);
  return (await res.json()) as IndicatorListResponse;
}

export async function indicatorSeries(
  indicatorId: string,
  geoEntityId?: string
): Promise<IndicatorSeriesResponse> {
  if (USE_MOCK) {
    // The mock only ships one series: MOCK_JIANGSU_GDP_SERIES.
    if (indicatorId !== MOCK_JIANGSU_GDP_SERIES.indicator_id) {
      return {
        indicator_id: indicatorId,
        series: [],
        pagination: { page: 1, page_size: 500, total_count: 0, has_next: false },
      };
    }
    if (geoEntityId && geoEntityId !== "JIANGSU-GEO-UUID-MOCK") {
      return {
        indicator_id: indicatorId,
        series: [],
        pagination: { page: 1, page_size: 500, total_count: 0, has_next: false },
      };
    }
    return MOCK_JIANGSU_GDP_SERIES;
  }
  const url = geoEntityId
    ? `${API_BASE}/api/indicator/${indicatorId}/series/${geoEntityId}`
    : `${API_BASE}/api/indicator/${indicatorId}/series`;
  const res = await fetch(`${url}?page=1&page_size=500`, { cache: "no-store" });
  if (!res.ok) throw new Error(`indicatorSeries: ${res.status}`);
  return (await res.json()) as IndicatorSeriesResponse;
}

// Re-export so callers can introspect which mode is active.
// Useful for the home page to render a banner.
export const IS_MOCK_MODE = USE_MOCK;