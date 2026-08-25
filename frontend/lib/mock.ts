// Stage 2 / S2.0.1 — Mock data with explicit DEMO sentinel.
//
// Per docs/34 §4.2 + tasking 146 §SCHEMA:
//   "须能区分/展示 is_demo vs 未来真实 SHA（文案/角标即可）"
//
// Jiangsu GDP 2020-2024 mock series is the S1.18 DEMO sentinel pattern:
// every row carries lineage.is_demo="true". When S2.0.2 replaces with a
// real SHA-locked sample, lineage.is_demo will become "false" or absent,
// and <DemoBadge /> will hide itself automatically.

import type {
  IndicatorListItem,
  IndicatorListResponse,
  IndicatorSeriesResponse,
  Pagination,
} from "./types";

const JIANGSU_INDICATOR_ID = "JIANGSU-GDP-INDICATOR-UUID-MOCK";
const JIANGSU_GEO_ID = "JIANGSU-GEO-UUID-MOCK";

const listItems: IndicatorListItem[] = [
  {
    indicator_id: JIANGSU_INDICATOR_ID,
    geo_entity_count: 1,
    observation_count: 5,
    latest_period_start: "2024-12-31",
  },
];

export const MOCK_INDICATOR_LIST: IndicatorListResponse = {
  indicators: listItems,
  pagination: {
    page: 1,
    page_size: 50,
    total_count: listItems.length,
    has_next: false,
  },
};

const years = [2020, 2021, 2022, 2023, 2024];
const yoyRates = [3.7, 8.6, 2.8, 5.8, 5.2]; // hand-crafted per S1.12 / tasking 92 §1.1

const series = years.map((year, idx) => ({
  indicator_id: JIANGSU_INDICATOR_ID,
  geo_entity_id: JIANGSU_GEO_ID,
  period_start: `${year}-12-31`,
  period_end: `${year}-12-31`,
  period_type: "ANNUAL",
  value: yoyRates[idx],
  unit: "PERCENT",
  status: "PUBLISHED",
  comparison_basis: "YOY",
  source_domain: "stats.gov.cn",
  source_category: "PROVINCIAL_YEARBOOK",
  source_level: "S1",
  verification_status: "UNVERIFIED",
  extraction_method: "MANUAL",
  confidence: null,
  extracted_at: "2026-08-25T00:00:00+08:00",
  // S1.18 DEMO sentinel — every row carries is_demo="true".
  // Real SHA-locked sample (S2.0.2) will drop this field.
  lineage: {
    is_demo: "true",
    demo_reason:
      "no real source file fetched; hand-crafted per tasking 92 §1.1",
  },
}));

const pagination: Pagination = {
  page: 1,
  page_size: 500,
  total_count: series.length,
  has_next: false,
};

export const MOCK_JIANGSU_GDP_SERIES: IndicatorSeriesResponse = {
  indicator_id: JIANGSU_INDICATOR_ID,
  series,
  pagination,
};

export const MOCK_PROVINCE_META = {
  province_id: JIANGSU_GEO_ID,
  province_name_zh: "江苏省",
  province_name_en: "Jiangsu",
  observation_card_count: 7, // 七维度观察卡 placeholder
};