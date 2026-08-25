// Stage 2 / S2.0.1 — Type definitions mirroring S1.10 FastAPI response shapes.
//
// Source of truth: backend/src/china_platform/api/models/indicator.py
// (IndicatorListItem, IndicatorListResponse, IndicatorSeriesPoint,
// IndicatorSeriesResponse). Keep this in sync when those change.
//
// Per docs/34 §5: frontend is read-only consumer; no write paths here.

export interface IndicatorListItem {
  indicator_id: string;
  geo_entity_count: number;
  observation_count: number;
  latest_period_start: string | null;
}

export interface IndicatorListResponse {
  indicators: IndicatorListItem[];
  pagination: Pagination;
}

export interface IndicatorSeriesPoint {
  indicator_id: string;
  geo_entity_id: string;
  period_start: string;
  period_end: string | null;
  period_type: string;
  value: number;
  unit: string | null;
  status: string | null;
  comparison_basis: string | null;
  source_domain: string | null;
  source_category: string | null;
  source_level: string | null; // "S0" | "S1" | "S2"
  verification_status: string | null; // "VERIFIED" | "UNVERIFIED" | ...
  extraction_method: string | null;
  confidence: number | null;
  extracted_at: string | null;
  // S1.18: lineage JSONB surfaced into API response.
  // When lineage.is_demo === "true", the row is a DEMO sentinel (placeholder
  // SHA '00..00', per docs/33 §3.2) and must render <DemoBadge />.
  lineage?: { is_demo?: string; demo_reason?: string } | null;
}

export interface IndicatorSeriesResponse {
  indicator_id: string;
  series: IndicatorSeriesPoint[];
  pagination: Pagination;
}

export interface Pagination {
  page: number;
  page_size: number;
  total_count: number;
  has_next: boolean;
}