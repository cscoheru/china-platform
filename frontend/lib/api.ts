// Stage 2 / S2.0.1 — Typed fetcher with mock switch.
//
// Per docs/34 §5:
//   - Read-only consumer of S1.10 FastAPI.
//   - No new write API; upload still goes through S1.13 admin.
//
// Per knife 659 tasking §1.659-A:
//   - USE_MOCK semantics flipped: NEXT_PUBLIC_USE_MOCK === "true" 才 mock
//   - Default is false (real data from FastAPI / mart), env switch is fallback
//   - mock 模块文件保留 (S1.18 历史资产 + 回退通道)
//
// Per knife 660 tasking §PART 2 (Track B 静态导出):
//   - 当 NEXT_PUBLIC_MART_DATA_PATH 被设置,listIndicators() 不再 call FastAPI,
//     改为从静态 JSON 文件构造 IndicatorListResponse (per mart data)。
//   - 此时 API_BASE 仍然保留(供 indicatorSeries 等其他 endpoint 兜底),
//     但 listIndicators 走静态路径,newvps 上不需要 FastAPI backend。

import type {
  IndicatorListResponse,
  IndicatorSeriesResponse,
  ProvinceTimeSeriesResponse,
  ProvinceTimeSeriesYearRange,
} from "./types";
import { MOCK_INDICATOR_LIST, MOCK_JIANGSU_GDP_SERIES } from "./mock";
import {
  getProvinceTimeSeriesByCode,
  isStaticMartDataEnabled,
  loadStaticMartData,
  type MartProvinceGdp2024,
} from "./mart-static";

const USE_MOCK =
  process.env.NEXT_PUBLIC_USE_MOCK === "true"; // default false (real data); set to "true" for mock fallback
// City mart-shape demo pipeline (S2.7-b-full-lite+). Independent of FastAPI mock.
const USE_MART_FIXTURE = process.env.NEXT_PUBLIC_USE_MART_FIXTURE === "1";
// Track B (knife 660): 静态导出模式. 当设置 NEXT_PUBLIC_MART_DATA_PATH 时,
// listIndicators() 直接从 JSON 文件读取 mart 数据(28 省 + 3 缺失),不走 FastAPI。
// newvps 上不需要 S1.10 FastAPI backend / dbt / DB。
const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function listIndicators(): Promise<IndicatorListResponse> {
  if (USE_MOCK) {
    return MOCK_INDICATOR_LIST;
  }
  if (isStaticMartDataEnabled()) {
    // Track B 静态导出:从 JSON 构造 synthetic IndicatorListResponse
    const mart = loadStaticMartData();
    if (mart) {
      return indicatorsFromMart(mart);
    }
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

/**
 * Build a synthetic IndicatorListResponse from mart_province_gdp_2024 JSON.
 * Track B (knife 660): one indicator CHINA-PROVINCE-GDP-2024 covering 28 real
 * provinces; 3 DATA_MISSING provinces are NOT counted in geo_entity_count
 * (per red line 1: 禁补零).
 */
function indicatorsFromMart(mart: MartProvinceGdp2024): IndicatorListResponse {
  const realCount = mart.real_count;
  return {
    indicators: [
      {
        indicator_id: "CHINA-PROVINCE-GDP-2024",
        geo_entity_count: realCount,
        observation_count: realCount,
        latest_period_start: "2024-12-31",
      },
    ],
    pagination: {
      page: 1,
      page_size: 50,
      total_count: 1,
      has_next: false,
    },
  };
}

// Re-export so callers can introspect which mode is active.
// Useful for the home page to render a banner.
export const IS_MOCK_MODE = USE_MOCK;
export const IS_MART_FIXTURE_MODE = USE_MART_FIXTURE;
export const IS_STATIC_MART_DATA_MODE = isStaticMartDataEnabled();

// ────────────────────────────────────────────────────────────────────────────
// P2 / knife 664 — Province time-series fetcher.
//
// Mode precedence (mirrors listIndicators):
//   1. static mart JSON (when NEXT_PUBLIC_MART_DATA_PATH set + file present)
//   2. real FastAPI /api/province-timeseries/{code}?year_start=&year_end=
//
// No mock for this endpoint yet (per docs/34 §5 + knife 659 USE_MOCK semantics).
// Real API is the canonical path; static JSON is the no-FastAPI fallback (per 660
// Track B + newvps deploy without S1.10 backend).
//
// Year range defaults to [2020, 2025] to match mart coverage (663 spec); 2001-2019
// + 2026 explicitly DATA_MISSING (新增红线-1/2) and still return rows but with
// status='DATA_MISSING' + value=null. Frontend surfaces those via dashed lines
// per 667 Recharts plan.
// ────────────────────────────────────────────────────────────────────────────

export async function getProvinceTimeSeries(
  provinceCode: string,
  yearRange?: ProvinceTimeSeriesYearRange
): Promise<ProvinceTimeSeriesResponse> {
  if (isStaticMartDataEnabled()) {
    const fromStatic = getProvinceTimeSeriesByCode(provinceCode, yearRange);
    if (fromStatic) return fromStatic;
  }
  const [yearStart, yearEnd] = yearRange ?? [2020, 2025];
  const url =
    `${API_BASE}/api/province-timeseries/${encodeURIComponent(provinceCode)}` +
    `?year_start=${yearStart}&year_end=${yearEnd}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`getProvinceTimeSeries: ${res.status}`);
  return (await res.json()) as ProvinceTimeSeriesResponse;
}

/**
 * List 31 provinces (summary only — no full points).
 * Returns empty array if mart is empty or API fails.
 *
 * Mirrors the /api/province-timeseries list endpoint shape (one row per province_code
 * with indicator_count + points_count metadata).
 */
export async function listProvinceTimeSeries(
  yearRange?: ProvinceTimeSeriesYearRange
): Promise<Array<Pick<ProvinceTimeSeriesResponse, "province_code" | "province_name" | "indicator_count" | "year_range" | "points_count">>> {
  const [yearStart, yearEnd] = yearRange ?? [2020, 2025];
  const url =
    `${API_BASE}/api/province-timeseries` +
    `?year_start=${yearStart}&year_end=${yearEnd}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`listProvinceTimeSeries: ${res.status}`);
  return (await res.json()) as Array<
    Pick<ProvinceTimeSeriesResponse, "province_code" | "province_name" | "indicator_count" | "year_range" | "points_count">
  >;
}
