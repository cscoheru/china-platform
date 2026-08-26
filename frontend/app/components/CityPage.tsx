// Stage 2 / S2.7-b-lite — 10 地市观察页组件（复用 S2.7-a 5 省模板）。
//
// Per docs/46 §4.1 (复用边界) + §6.1 (lite mock 壳范围) + `256` §SCHEMA：
//   - 复用 EvidenceChain（6 段，per docs/06 §2）
//   - 复用 SevenDimGrid（7 cell，per docs/42 §3）
//   - 复用 PeerCompareCard（同省地市横向，per docs/43 §4.1）
//
// 红线 (per docs/46 §1.2 + docs/34 §1 + `256` §红线):
//   - 不接 mart / person 真数据（OPEN → S2.7-b-full）
//   - 不引入 score / rating / rank / total_score 字段
//   - 不擅自增减 10 城名单（per Cursor 锁定）

import type { ReactElement } from "react";
import type { CityProps } from "../../lib/types_cities";
import { EvidenceChain } from "./EvidenceChain";
import SevenDimGrid from "./SevenDimGrid";
import PeerCompareCard from "./PeerCompareCard";

interface CityPageProps {
  city: CityProps;
}

export function CityPage({ city }: CityPageProps): ReactElement {
  return (
    <section data-testid="city-page" data-city-slug={city.slug} data-is-demo={city.lineage.isDemo}>
      <h1>
        {city.nameZh} 地市观察页 <small style={{ fontSize: 14, color: "#888" }}>S2.7-b-lite · mock 壳</small>
      </h1>
      <p style={{ color: "#666", fontSize: 13 }}>
        归属省份: <code>{city.provinceSlug}</code> · 七维度观察卡: <code>{city.observationCardCount}</code> · 演示模式: <code>is_demo=true</code>
      </p>

      <EvidenceChain segments={city.evidenceChain.segments} />

      <SevenDimGrid
        region={{
          geoEntityId: `city-geo-mock-${city.slug}`,
          geoNameZh: city.nameZh,
          cells: city.sevenDimCells,
        }}
      />

      <PeerCompareCard
        region={{
          geoEntityId: `city-geo-mock-${city.slug}`,
          geoNameZh: city.nameZh,
          group: city.peerCompareGroup,
        }}
      />

      <p style={{ fontSize: 12, color: "#999", marginTop: 24 }}>
        S2.7-b-lite = 10 城 mock 壳；S2.7-b-full = 接 <code>mart_city_evidence_chain</code> + person/tenure 真数据
        （OPEN；依赖 O1 真实 SHA + Stage 1 OPEN 收口）。
      </p>

      {city.slug === "shenzhen" ? (
        <section
          data-testid="city-page-public-extract-link"
          data-city-slug="shenzhen"
          style={{
            marginTop: 24,
            padding: "12px 16px",
            background: "#fff8e1",
            border: "1px solid #ffe082",
            fontSize: 13,
          }}
        >
          <h3 style={{ fontSize: 14, margin: "0 0 8px 0" }}>
            公开提取 — 深圳轨（per tasking 391）
          </h3>
          <p style={{ margin: "0 0 8px 0" }}>
            深圳统计公报散文段落表（sz.gov.cn MUNICIPAL_BULLETIN，71 行
            <code>{"{section, paragraph}"}</code>）已落在{" "}
            <a href="/public-extracts#track-sz">
              <code>/public-extracts#track-sz</code>
            </a>
            ；样本来自 registry 锚定的本地 spike，<strong>REGISTRY_SAMPLE demo，SSL
            暂缓未做过 live 探测，非 O1 收口</strong>（per 回执 368/371/383）。
          </p>
          <p style={{ margin: 0, fontSize: 12, color: "#856404" }}>
            注：本城页 mock 观察卡与公报散文轨互不覆盖 — mock 数据是城市观察卡
            演示，公报散文轨是公开源结构化提取演示；两者皆 demo，非 O1。
          </p>
        </section>
      ) : null}
    </section>
  );
}