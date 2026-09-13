// Stage 2 / S2.7-b-lite → S2.7-b-full-lite+ → knife H-series — 10 地市动态路由 `/cities/{slug}`.
//
// Per docs/46 §3.2 路由 A（顶层 /cities/{slug}） + §3.3 (文件路径约定) +
// `256` §SCHEMA "10 城 /cities/{slug} mock 壳" +
// `265` §SCHEMA "CityPage 可切 mock→mart-shape" + knife H-series plan (2026-09-13).
//
// ⚠ Dynamic segment route（per AGENTS.md "Static-segment Next.js routes
// must NOT branch on params.*"）。10 城通过 generateStaticParams 预生成。
//
// Feature-flag 守门（knife H-series 翻转默认）:
//   - 默认 / `NEXT_PUBLIC_USE_MART_FIXTURE != "0"` → live mart (CityTimeseriesLive)
//   - `NEXT_PUBLIC_USE_MART_FIXTURE=0`              → mock fixture (CityPage via mock_cities)
//   - live mart 失败时（API 404 / 5xx / network）→ 退到 mart_city_demo fixture (CityPageMart)
//     保 UI 仍可见（per docs/05 §9 容错原则），但保留 is_demo 标记。
//
// 红线 (per docs/46 §1.2 + `256` §红线 + docs/47 §1.2 + `265` §红线 + docs/34 §1 + docs/87 §3.2):
//   - 不擅自增减 10 城名单（Cursor 锁定）
//   - 不接真 SHA 样本 / 不接 O1 收口（mart-shape 在 full 刀接 dbt mart 真表）
//   - 不派生 score / rating / rank / total_score / confidence_score
//   - DATA_MISSING 显式「数据缺失」（禁补零，per 红线-1/2/3）

import { notFound } from "next/navigation";

import { CityPage } from "../../components/CityPage";
import { CityPageMart } from "../../components/CityPageMart";
import { CityTimeseriesLive } from "../../components/CityTimeseriesLive";
import { CITY_SLUG_LIST, getCityEntry } from "../../../lib/city_slug_map";
import { getMockCity } from "../../../lib/mock_cities";
import { getMartCityDemo } from "../../../lib/mart_city_demo";
import { getCityTimeSeries } from "../../../lib/api";

// 静态预生成 10 城路由（per `256` §NOW-1）
export function generateStaticParams(): Array<{ slug: string }> {
  return CITY_SLUG_LIST.map((slug) => ({ slug }));
}

// 404 兜底：slug 命中锁定清单之外的请求一律 notFound（per docs/46 §3.1 slug 守门）
export const dynamicParams = false;

interface PageProps {
  params: { slug: string };
}

// Feature-flag 守门（knife H-series 翻转默认: 默认走 live mart）.
// 仅当显式设 `NEXT_PUBLIC_USE_MART_FIXTURE=0` 才退到 mock fixture.
function shouldUseMockFixture(): boolean {
  return process.env.NEXT_PUBLIC_USE_MART_FIXTURE === "0";
}

// 默认年份范围：与 FastAPI DEFAULT_YEAR_START/END 对齐 (per knife H1 端点).
const DEFAULT_YEAR_START = 2020;
const DEFAULT_YEAR_END = 2025;

export default async function CityRoutePage({
  params,
}: PageProps): Promise<React.ReactElement> {
  const entry = getCityEntry(params.slug);
  if (!entry) {
    notFound();
  }

  // Mock fixture 路径（per `256` §SCHEMA; 设 USE_MART_FIXTURE=0 启用）
  if (shouldUseMockFixture()) {
    const city = getMockCity(params.slug);
    if (!city) {
      notFound();
    }
    return <CityPage city={city} />;
  }

  // 默认走 live mart (CityTimeseriesLive). getCityTimeSeries throws on 4xx/5xx
  // (包括 4 直辖市 404 / invalid city_code 422), 退到 mart_city_demo fixture.
  try {
    const response = await getCityTimeSeries(entry.cityCode, [
      DEFAULT_YEAR_START,
      DEFAULT_YEAR_END,
    ]);
    return (
      <CityTimeseriesLive
        initialResponse={response}
        slug={entry.slug}
        nameZh={entry.nameZh}
        provinceSlug={entry.provinceSlug}
      />
    );
  } catch (err) {
    // live mart 不可用时退到 mart-shape fixture (per docs/05 §9 容错原则).
    // 控制台可见错误, 但 UI 仍可浏览 (is_demo=true 标注).
    if (typeof console !== "undefined") {
      console.warn(
        `[cities/${params.slug}] getCityTimeSeries(${entry.cityCode}) failed; ` +
          `falling back to mart_city_demo fixture.`,
        err
      );
    }
    const mart = getMartCityDemo(params.slug);
    if (!mart) {
      notFound();
    }
    return <CityPageMart mart={mart} />;
  }
}
