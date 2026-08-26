// Stage 2 / S2.7-b-lite → S2.7-b-full-lite — 10 地市动态路由 `/cities/{slug}`。
//
// Per docs/46 §3.2 路由 A（顶层 /cities/{slug}） + §3.3 (文件路径约定) +
// `256` §SCHEMA "10 城 /cities/{slug} mock 壳" +
// `265` §SCHEMA "CityPage 可切 mock→mart-shape（feature-flag / 默认 demo）"。
//
// ⚠ Dynamic segment route（per AGENTS.md "Static-segment Next.js routes
// must NOT branch on params.*"）。10 城通过 generateStaticParams 预生成。
//
// Feature-flag 守门：
//   - 默认走 mock_cities.ts（S2.7-b-lite 已交；receipt 257）
//   - 设 `NEXT_PUBLIC_USE_MART_FIXTURE=1` 启用 CityPageMart（mart-shape 接驳；
//     per `265` §NOW-1；O1 收口前 is_demo=true + lineage.source_file_sha256 占位 '0'*64）
//
// 红线 (per docs/46 §1.2 + `256` §红线 + docs/47 §1.2 + `265` §红线 + docs/34 §1):
//   - 不擅自增减 10 城名单（Cursor 锁定）
//   - 不接真 SHA 样本 / 不接 O1 收口（mart-shape 在 full 刀接 dbt mart 真表）
//   - 不派生 score / rating / rank / total_score / confidence_score

import { notFound } from "next/navigation";
import { CityPage } from "../../components/CityPage";
import { CityPageMart } from "../../components/CityPageMart";
import { CITY_SLUG_LIST, getCityEntry } from "../../../lib/city_slug_map";
import { getMockCity } from "../../../lib/mock_cities";
import { getMartCityDemo } from "../../../lib/mart_city_demo";

// 静态预生成 10 城路由（per `256` §NOW-1）
export function generateStaticParams(): Array<{ slug: string }> {
  return CITY_SLUG_LIST.map((slug) => ({ slug }));
}

// 404 兜底：slug 命中锁定清单之外的请求一律 notFound（per docs/46 §3.1 slug 守门）
export const dynamicParams = false;

interface PageProps {
  params: { slug: string };
}

// Feature-flag 守门：默认 mock；显式启用 mart-shape（per `265` §NOW-1）
function shouldUseMartFixture(): boolean {
  return process.env.NEXT_PUBLIC_USE_MART_FIXTURE === "1";
}

export default function CityRoutePage({ params }: PageProps): React.ReactElement {
  const entry = getCityEntry(params.slug);
  if (!entry) {
    notFound();
  }
  if (shouldUseMartFixture()) {
    // mart-shape 接驳（per `265` §SCHEMA；默认 demo；lineage.source_file_sha256 占位 '0'*64）
    const mart = getMartCityDemo(params.slug);
    if (!mart) {
      notFound();
    }
    return <CityPageMart mart={mart} />;
  }
  // 默认 mock（per `256` §SCHEMA S2.7-b-lite 已交；receipt 257）
  const city = getMockCity(params.slug);
  if (!city) {
    notFound();
  }
  return <CityPage city={city} />;
}