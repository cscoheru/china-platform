// Stage 2 / S2.7-b-lite — 10 地市动态路由 `/cities/{slug}`。
//
// Per docs/46 §3.2 路由 A（顶层 /cities/{slug}） + §3.3 (文件路径约定) +
// `256` §SCHEMA "10 城 /cities/{slug} mock 壳"。
//
// ⚠ Dynamic segment route（per AGENTS.md "Static-segment Next.js routes
// must NOT branch on params.*"）。10 城通过 generateStaticParams 预生成。
//
// 红线 (per docs/46 §1.2 + `256` §红线 + docs/34 §1):
//   - 不擅自增减 10 城名单（Cursor 锁定）
//   - 不接 mart / person 真数据（OPEN → S2.7-b-full）

import { notFound } from "next/navigation";
import { CityPage } from "../../components/CityPage";
import { CITY_SLUG_LIST, getCityEntry } from "../../../lib/city_slug_map";
import { getMockCity } from "../../../lib/mock_cities";

// 静态预生成 10 城路由（per `256` §NOW-1）
export function generateStaticParams(): Array<{ slug: string }> {
  return CITY_SLUG_LIST.map((slug) => ({ slug }));
}

// 404 兜底：slug 命中锁定清单之外的请求一律 notFound（per docs/46 §3.1 slug 守门）
export const dynamicParams = false;

interface PageProps {
  params: { slug: string };
}

export default function CityRoutePage({ params }: PageProps): React.ReactElement {
  const entry = getCityEntry(params.slug);
  if (!entry) {
    notFound();
  }
  const city = getMockCity(params.slug);
  if (!city) {
    notFound();
  }
  return <CityPage city={city} />;
}