// Stage 2 / S2.7-b-full-lite — 10 地市 mart-shape 接驳组件。
//
// Per docs/47 §3.1 (mart_city_evidence_chain 投影) + §3.2 (mart_city_seven_dim_overview 投影)
// + §3.3 (person/tenure 接入契约 demo) + §4.1 (段级字段契约) + §4.2 (七维度 cell 契约)
// + `265` §SCHEMA "CityPage 可切 mock→mart-shape"（feature-flag，默认 demo）
// + `302` §SCHEMA "10 城 demo relatedPersons/tenure 接驳"。
//
// ⚠ 默认走 mock_cities（per [slug]/page.tsx 的 feature-flag）。
// 设 `NEXT_PUBLIC_USE_MART_FIXTURE=1` 启用 mart-shape 接驳（per `265` §NOW-1）。
//
// 红线 (per docs/47 §1.2 + `302` §红线 + docs/34 §1 + docs/06 §6.6 + docs/42 §8):
//   - 不派生 score / rating / rank / total_score / confidence_score
//   - 不做"地区得分" / 不做"地区排名" / 不做 peer_rank
//   - 不接真 SHA 样本（lineage.source_file_sha256 = '0'*64 占位）
//   - 不接 person/tenure 真数据（canonical_name 全部 demo 占位；is_demo 显式标注）

import type { ReactElement } from "react";
import type { MartCityViewProps } from "../../lib/mart_city_types";
import { EvidenceChain } from "./EvidenceChain";
import SevenDimGrid from "./SevenDimGrid";
import PeerCompareCard from "./PeerCompareCard";
import type {
  EvidenceChainSegment,
  EvidenceItem,
  EvidenceSegmentKey,
} from "../../lib/types";
import type {
  PeerCompareGroup,
  ComparisonGroupMemberProps,
  EvidenceBalanceByMember,
  SevenDimByMember,
} from "../../lib/types_peer_compare";
import type { SevenDimCell } from "../../lib/types_seven_dim";
import { CITY_SLUG_MAP, CITY_SLUG_LIST } from "../../lib/city_slug_map";

// mart-shape → EvidenceChain 适配器（per docs/47 §4.1）
// mart 行：{ cityId, segment, canonicalStatement, infoLayer, lineage } → UI segment
function martToSegments(mart: MartCityViewProps): EvidenceChainSegment[] {
  return mart.evidenceChain.map((row) => {
    const segment: EvidenceSegmentKey = row.segment as EvidenceSegmentKey;
    const items: EvidenceItem[] = row.canonicalStatement
      ? [
          {
            title: row.canonicalStatement,
            source_label: `MOCK · mart-shape · docs/47 §3.1 · ${row.cityId}`,
            note:
              `info_layer=${row.infoLayer} · polarity=${row.canonicalPolarity} · ` +
              `strength=${row.evidenceStrength} · is_demo=${row.lineage.isDemo}`,
          },
        ]
      : []; // 空段演示"未覆盖"（per docs/44 §1.1 S2.7-a 段级证据链接驳）
    return { key: segment, items };
  });
}

// mart-shape → SevenDimCell 适配器（per docs/47 §4.2）
function martToSevenDimCells(mart: MartCityViewProps): SevenDimCell[] {
  return mart.sevenDimOverview.map((row, idx) => ({
    claimId: `mart-claim-${mart.cityId}-${idx + 1}`,
    cardId: row.cardId,
    nSupports: row.nSupports,
    nContradicts: row.nContradicts,
    nInference: row.nInference,
    nJudgment: row.nJudgment,
    nDerived: row.nDerived,
    balanceStatus: row.balanceStatus,
    isDemo: row.lineage.isDemo,
    geoEntityId: mart.cityId,
    expanded: false,
  }));
}

// mart-shape → PeerCompareGroup 适配器（per docs/47 §4.3）
// focal = 本城；peers = 同省其他地市（继承 lite mock 同省地市横向）
function martToPeerCompareGroup(mart: MartCityViewProps): PeerCompareGroup {
  const provinceSlug = mart.provinceSlug;
  const focalEntry = CITY_SLUG_MAP[mart.cityId.replace(/^city-geo-mock-/, "")];
  const peersInProvince = CITY_SLUG_LIST
    .filter((slug) => CITY_SLUG_MAP[slug].provinceSlug === provinceSlug && slug !== focalEntry?.slug);

  const members: ComparisonGroupMemberProps[] = [
    {
      geoEntityId: mart.cityId,
      geoNameZh: `${mart.geoNameZh} (mart focal)`,
      roleInGroup: "focal",
      selectionReason: "本对比基准（focal）；同省地市横向对比",
    },
    ...peersInProvince.map<ComparisonGroupMemberProps>((peerSlug) => ({
      geoEntityId: `city-geo-mock-${peerSlug}`,
      geoNameZh: `${CITY_SLUG_MAP[peerSlug].nameZh} (mart peer)`,
      roleInGroup: "peer",
      selectionReason: `同省地市（peer）；与 ${mart.geoNameZh} 区位/产业可比`,
    })),
  ];

  const evidenceBalanceByMember: EvidenceBalanceByMember[] = members.map((m) => ({
    geoEntityId: m.geoEntityId,
    nObservation: 32,
    nInference: 8,
    nJudgment: 3,
    nDerived: 1,
    nSupports: 11,
    nContradicts: 4,
  }));

  const sevenDimByMember: SevenDimByMember[] = members.map((m) => ({
    geoEntityId: m.geoEntityId,
    cellsNoContradicts: 1,
    cellsSupportsDominant: 3,
    cellsContradictsDominant: 1,
    totalSevenDimCells: 7,
  }));

  return {
    groupId: `mart-city-group-${focalEntry?.slug ?? mart.cityId}`,
    groupNameZh: `${provinceSlug} 同省地市对比组 (mart-shape)`,
    populationTier: "1000-2000万",
    locationType: "coastal",
    industryBase: "mixed",
    developmentStage: "high",
    selectionMethod: "manual", // 仅 manual 落地（per docs/43 §2.7）
    selectionJustification:
      `同省地市横向对比组 (mart-shape)：4 城均属沿海+混合产业+高发展阶段；` +
      `${mart.geoNameZh} 为本对比基准 (focal)，` +
      `${peersInProvince.map((s) => CITY_SLUG_MAP[s].nameZh).join("/")} 为可比同类 (peer)。` +
      `不按 GDP 总量取 top N（per docs/05 §8.3 红线）。`,
    members,
    evidenceBalanceByMember,
    sevenDimByMember,
    isDemo: true,
    expanded: false,
  };
}

interface CityPageMartProps {
  mart: MartCityViewProps;
}

export function CityPageMart({ mart }: CityPageMartProps): ReactElement {
  const segments = martToSegments(mart);
  const cells = martToSevenDimCells(mart);
  const group = martToPeerCompareGroup(mart);
  return (
    <section
      data-testid="city-page-mart"
      data-city-slug={mart.cityId}
      data-is-demo={mart.lineage.isDemo}
      data-source-file-sha256-prefix={mart.lineage.sourceFileSha256.slice(0, 8)}
    >
      <h1>
        {mart.geoNameZh} 地市观察页{" "}
        <small style={{ fontSize: 14, color: "#888" }}>
          S2.7-b-full-lite · mart-shape 接驳（is_demo=true；source_file_sha256 占位）
        </small>
      </h1>
      <p style={{ color: "#666", fontSize: 13 }}>
        归属省份: <code>{mart.provinceSlug}</code> · 七维度观察卡:{" "}
        <code>{mart.sevenDimOverview.length}</code> · 演示模式:{" "}
        <code>is_demo={String(mart.lineage.isDemo)}</code> · sha256:{" "}
        <code>{mart.lineage.sourceFileSha256.slice(0, 16)}…</code>
      </p>

      <EvidenceChain segments={segments} />

      <SevenDimGrid
        region={{
          geoEntityId: mart.cityId,
          geoNameZh: mart.geoNameZh,
          cells,
        }}
      />

      <PeerCompareCard
        region={{
          geoEntityId: mart.cityId,
          geoNameZh: mart.geoNameZh,
          group,
        }}
      />

      {/* person/tenure demo 接驳（per docs/47 §3.3 + `302` §SCHEMA）*/}
      <section
        data-testid="city-page-mart-related-persons"
        data-related-persons-count={mart.relatedPersons.length}
        data-is-demo={mart.lineage.isDemo}
        style={{ marginTop: 24, padding: "12px 16px", background: "#fafafa", border: "1px solid #eee" }}
      >
        <h3 style={{ fontSize: 14, margin: "0 0 8px 0" }}>
          履历卡（person/tenure demo 接驳 · per docs/47 §3.3）
          <small style={{ marginLeft: 8, color: "#888", fontSize: 12 }}>
            is_demo=true · 演示人物（mock）· 不构成真实身份核验
          </small>
        </h3>
        <ul style={{ margin: 0, paddingLeft: 20, fontSize: 13 }}>
          {mart.relatedPersons.map((p) => (
            <li key={p.personId} style={{ marginBottom: 4 }}>
              <code>{p.canonicalName}</code>
              {" — "}
              <span>{p.positionTitle}</span>
              {" · "}
              <span style={{ color: "#666" }}>{p.geoCanonicalName}</span>
              {" · "}
              <span style={{ color: p.isCurrent ? "#0a0" : "#888" }}>
                {p.isCurrent ? "现任" : "历任"}
              </span>
            </li>
          ))}
        </ul>
        <p style={{ fontSize: 11, color: "#999", marginTop: 8, marginBottom: 0 }}>
          canonical_name 全部为演示占位（per `302` §红线 "不伪造真身份材料"）；
          真实 person/tenure 接入待 S2.1-lite `mart_person_tenure` PASS 后由 S2.7-b-full 真数据迁移刀替换。
        </p>
      </section>

      <p style={{ fontSize: 12, color: "#999", marginTop: 24 }}>
        S2.7-b-full-lite = mart-shape 接驳（演示 fixture；lineage.source_file_sha256 占位）；
        S2.7-b-full = 接 dbt mart 真表 + O1 真实 SHA 收口（OPEN；依赖 O1 收口 + Stage 1 OPEN 收口 + S2.1-lite PASS）。
      </p>
    </section>
  );
}