// Stage 2 / B-OPT-NT (knife H-series, 2026-09-13) — Empty-state component for
// cities whose mart dimension is missing (hongheiku 0 entry, per 红线-3 禁补零).
//
// Why this exists:
//   FastAPI /api/city-timeseries/{code} returns 404 CITY_NOT_FOUND for cities
//   not in mart_city_timeseries (e.g., NANTONG — hongheiku 公开数据汇编未收录).
//   Before B-OPT-NT: 404 → fallback to mart_city_demo fixture → user saw demo
//   content mislabeled as if real. That violated 红线-8 (mart-only-data) intent:
//   a city with no data should NOT pretend to have demo data.
//
// What this renders:
//   - Header with city name + province slug (non-mart, from city_slug_map.ts)
//   - Clear "no data" notice tied to hongheiku source attribution
//   - List of peer cities (same province) that DO have data, so user can navigate
//   - data-testid="city-empty-state" + data-slug + data-no-data-reason for /qa E2E
//
// 红线 (per docs/05 §9 + docs/46 §1.2 + 红线-3 禁补零):
//   - 不派生 score / rating / rank / 不展示 mock 数据
//   - DATA_MISSING 显式说明 (禁补零 / 禁默认值)
//   - 文案明确指向「hongheiku 公开数据汇编暂无收录」(not "我们没抓到" — 是源端就没)

import type { ReactElement } from "react";
import { CITY_SLUG_LIST, CITY_SLUG_MAP } from "../../lib/city_slug_map";

interface CityEmptyStateProps {
  slug: string;
  nameZh: string;
  provinceSlug: string;
  cityCode: string;
}

export function CityEmptyState({
  slug,
  nameZh,
  provinceSlug,
  cityCode,
}: CityEmptyStateProps): ReactElement {
  // List same-province peer cities that DO have mart data (heuristic: any peer
  // not in the hongheiku 0-entry list — currently NANTONG is the only one). When
  // peer list is empty (e.g., all-province city is missing), hide the section.
  const peersInProvince = CITY_SLUG_LIST.filter((s) => {
    const entry = CITY_SLUG_MAP[s];
    return entry.provinceSlug === provinceSlug && entry.slug !== slug;
  });

  return (
    <section
      data-testid="city-empty-state"
      data-slug={slug}
      data-city-code={cityCode}
      data-no-data-reason="hongheiku_zero_entry"
      style={{
        maxWidth: 960,
        margin: "0 auto",
        padding: "32px 24px",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h1 style={{ fontSize: 22, marginBottom: 4 }}>
        {nameZh} 地市观察页{" "}
        <small style={{ fontSize: 13, color: "#888", fontWeight: 400 }}>
          （暂无收录）
        </small>
      </h1>
      <p style={{ color: "#666", fontSize: 13, marginTop: 4 }}>
        归属省份: <code>{provinceSlug}</code> · city_code:{" "}
        <code>{cityCode}</code>
      </p>

      <div
        style={{
          marginTop: 24,
          padding: "16px 20px",
          background: "#fef9e7",
          border: "1px solid #f1c40f",
          borderRadius: 4,
          color: "#7d6608",
        }}
      >
        <p style={{ margin: 0, fontSize: 14, lineHeight: 1.6 }}>
          <strong>本城市在 mart_city_timeseries 中暂无数据。</strong>
        </p>
        <p style={{ margin: "8px 0 0 0", fontSize: 13, lineHeight: 1.6 }}>
          数据来源为 hongheiku 公开数据汇编（hongheiku.com），汇编源端暂未收录{" "}
          <strong>{nameZh}</strong> 的年度统计指标。
          按红线-3 禁补零原则，本页不展示任何 demo / 派生数据，避免误导。
        </p>
        <p style={{ margin: "8px 0 0 0", fontSize: 12, color: "#9c7e0a" }}>
          相关治理信息见 <code>docs/05 §9 容错原则</code> +{" "}
          <code>docs/46 §1.2 红线</code>。如需收录，请走 source_registry 工单提交源 URL。
        </p>
      </div>

      {peersInProvince.length > 0 && (
        <section style={{ marginTop: 24 }}>
          <h2 style={{ fontSize: 16, marginBottom: 8 }}>
            同省其他地市（mart 有数据，可浏览）
          </h2>
          <ul style={{ fontSize: 14, lineHeight: 1.8, paddingLeft: 20 }}>
            {peersInProvince.map((peerSlug) => {
              const peer = CITY_SLUG_MAP[peerSlug];
              return (
                <li key={peerSlug}>
                  <a
                    href={`/cities/${peer.slug}`}
                    data-testid={`city-empty-state-peer-${peer.slug}`}
                  >
                    {peer.nameZh}
                  </a>{" "}
                  <span style={{ color: "#888", fontSize: 12 }}>
                    ({peer.cityCode})
                  </span>
                </li>
              );
            })}
          </ul>
        </section>
      )}

      <p style={{ marginTop: 24, fontSize: 12, color: "#999" }}>
        路线：本页不渲染任何评分 / 排名 / mock 数据；如需对比同省地市，请点击上方入口。
        完整 mart 收录范围见{" "}
        <a href="/" data-testid="city-empty-state-home-link">
          首页地市观察入口
        </a>
        。
      </p>
    </section>
  );
}
