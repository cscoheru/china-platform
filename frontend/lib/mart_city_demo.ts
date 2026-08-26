// Stage 2 / S2.7-b-full-lite — 10 地市 mart-shape 演示 fixture。
//
// Per docs/47 §3.1 (mart_city_evidence_chain 投影) + §3.2 (mart_city_seven_dim_overview 投影)
// + §3.3 (person/tenure 接入契约 demo) + `302` §SCHEMA "10 城 demo relatedPersons/tenure"。
//
// ⚠ 本文件 = mart-shape demo fixture（TypeScript 投影）；
// dbt mart 真表在 S2.7-b-full 落地刀 (tasking 26X+) 写。
// lineage.source_file_sha256 全部为 '0'*64 占位（per docs/47 §3.1 ⚠️ OPEN）。
//
// 红线 (per docs/47 §1.2 + `302` §红线 + docs/34 §1 + docs/06 §6.6 + docs/42 §8):
//   - 不爬网 / 不引入 seed 数据
//   - 不引入 score / rating / rank / total_score / confidence_score / credibility_score
//   - 不派生 "地区得分" / 不派生 "地区排名" / 不做 peer_rank
//   - 不接真 SHA 样本（lineage.source_file_sha256 = '0'*64 占位）
//   - 不接 person/tenure 真数据（canonical_name 全部 demo 占位 "演示 人物"；UI 必显式 demo 标识）
//   - 不擅自增减 10 城名单（Cursor 锁定）

import {
  MART_IS_DEMO,
  MART_LINEAGE_PLACEHOLDER_SHA,
  assertMartRowHasNoForbiddenFields,
  type MartCityViewProps,
  type MartLineageProps,
  type MartPersonTenureRowProps,
} from "./mart_city_types";
import { CITY_SLUG_MAP, CITY_SLUG_LIST } from "./city_slug_map";
import { BALANCE_STATUS, type BalanceStatus, type SevenDimCardId } from "./types_seven_dim";

const SEGMENTS_6 = [
  "CONDITION",
  "COMMITMENT",
  "INPUT",
  "PROCESS",
  "OUTPUT",
  "OUTCOME_RISK",
] as const;

const SEVEN_DIM_CARD_IDS: SevenDimCardId[] = [
  "POLICY_DELIVERY",
  "FISCAL_EXECUTION",
  "PROJECT_DELIVERY",
  "ECONOMIC_ADAPTATION",
  "PUBLIC_SERVICES",
  "RISK_MANAGEMENT",
  "GOAL_CONSISTENCY",
];

// mart-shape lineage 占位（per docs/47 §3.1 ⚠️ OPEN；O1 收口前恒为 '0'*64）
function buildMartLineage(citySlug: string): MartLineageProps {
  return {
    isDemo: true,
    sourceFileSha256: MART_LINEAGE_PLACEHOLDER_SHA,
    demoReason:
      `S2.7-b-full-lite 演示 fixture；` +
      `${citySlug} mart-shape 投影；` +
      `O1 真实 SHA 收口前 source_file_sha256 恒为 '0'*64 占位。`,
  };
}

// mart-shape evidence chain 行级（演示 6 段；非空段与 lite mock 平行）
function buildMartEvidenceChain(citySlug: string) {
  const lineage = buildMartLineage(citySlug);
  const cityNameZh = CITY_SLUG_MAP[citySlug].nameZh;
  // 每城 6 段；仅 CONDITION 1 条占位；其余 5 段空演示"未覆盖"（per docs/44 §1.1 S2.7-a 段级）
  return SEGMENTS_6.map((segment, idx) => {
    const row = {
      cityId: `city-geo-mock-${citySlug}`,
      geoNameZh: cityNameZh,
      provinceSlug: CITY_SLUG_MAP[citySlug].provinceSlug,
      segment,
      canonicalStatement:
        idx === 0
          ? `${cityNameZh} 区位与产业基础（mart-shape 演示占位；S2.7-b-full 接 inference_record.canonical_statement）`
          : "",
      canonicalPolarity: idx === 0 ? ("SUPPORTS" as const) : ("NEUTRAL" as const),
      evidenceStrength: idx === 0 ? ("MODERATE" as const) : ("WEAK" as const),
      infoLayer: idx === 0 ? ("DERIVED" as const) : ("FACT" as const),
      lineage,
    };
    assertMartRowHasNoForbiddenFields(row as unknown as Record<string, unknown>, `mart_evidence_chain[${idx}]`);
    return row;
  });
}

// mart-shape 七维度 cell 行级（演示 5 枚举轮转 + 2 余量 = 7 cell；与 lite mock 平行）
function buildMartSevenDimOverview(citySlug: string) {
  const lineage = buildMartLineage(citySlug);
  // 5 枚举循环 + 2 余量 = 7 cell（per docs/47 §3.2 balanceStatus 5 枚举）
  const rotation: BalanceStatus[] = [
    BALANCE_STATUS[0], // NO_EVIDENCE
    BALANCE_STATUS[1], // NO_CONTRADICTING_EVIDENCE (🔴 Gate 2 §3.2 硬卡)
    BALANCE_STATUS[2], // NO_SUPPORTING_EVIDENCE
    BALANCE_STATUS[3], // SUPPORTS_DOMINANT
    BALANCE_STATUS[4], // CONTRADICTS_DOMINANT
    BALANCE_STATUS[3], // SUPPORTS_DOMINANT
    BALANCE_STATUS[0], // NO_EVIDENCE
  ];
  return SEVEN_DIM_CARD_IDS.map((cardId, idx) => {
    const row = {
      cityId: `city-geo-mock-${citySlug}`,
      cardId,
      nSupports: rotation[idx] === BALANCE_STATUS[3] ? 4 : rotation[idx] === BALANCE_STATUS[4] ? 1 : 2,
      nContradicts: rotation[idx] === BALANCE_STATUS[4] ? 3 : rotation[idx] === BALANCE_STATUS[2] ? 2 : 0,
      nInference: 1,
      nJudgment: 0,
      nDerived: 0,
      balanceStatus: rotation[idx],
      lineage,
    };
    assertMartRowHasNoForbiddenFields(row as unknown as Record<string, unknown>, `mart_seven_dim_overview[${idx}]`);
    return row;
  });
}

// mart-shape person/tenure 接入契约最小子集（per docs/47 §3.3 + `302` §SCHEMA）
//
// 每城 2 行 demo：市委书记 + 市长。canonical_name 全部 demo 占位（"演示 人物 N (mock)"），
// **绝不**写真实姓名（per `302` §红线 "不伪造真身份材料"）。
// 真实 person/tenure 接入在 S2.1-lite `mart_person_tenure` PASS 后由 S2.7-b-full 真数据
// 迁移刀 (tasking 26X+) 替换。
function buildMartRelatedPersons(citySlug: string): MartPersonTenureRowProps[] {
  const lineage = buildMartLineage(citySlug);
  const cityNameZh = CITY_SLUG_MAP[citySlug].nameZh;
  const demoRows: Array<{
    personId: string;
    canonicalName: string;
    positionTitle: string;
  }> = [
    {
      personId: `demo-person-${citySlug}-secretary`,
      canonicalName: `演示 人物 A (mock, ${citySlug})`,
      positionTitle: "市委书记（演示职位）",
    },
    {
      personId: `demo-person-${citySlug}-mayor`,
      canonicalName: `演示 人物 B (mock, ${citySlug})`,
      positionTitle: "市长（演示职位）",
    },
  ];
  return demoRows.map((d, idx) => {
    const row: MartPersonTenureRowProps = {
      personId: d.personId,
      canonicalName: d.canonicalName,
      positionTitle: d.positionTitle,
      geoCanonicalName: cityNameZh,
      isCurrent: true, // demo 演示均视为现任；真实 is_current 由 S2.1-lite 落地
      lineage,
    };
    assertMartRowHasNoForbiddenFields(
      row as unknown as Record<string, unknown>,
      `mart_related_persons[${idx}]`,
    );
    return row;
  });
}

// mart-shape 地市视图聚合（per docs/47 §3.1 + §3.2 + §3.3）
function buildMartCityView(citySlug: string): MartCityViewProps {
  const lineage = buildMartLineage(citySlug);
  return {
    cityId: `city-geo-mock-${citySlug}`,
    geoNameZh: CITY_SLUG_MAP[citySlug].nameZh,
    provinceSlug: CITY_SLUG_MAP[citySlug].provinceSlug,
    evidenceChain: buildMartEvidenceChain(citySlug),
    sevenDimOverview: buildMartSevenDimOverview(citySlug),
    relatedPersons: buildMartRelatedPersons(citySlug),
    lineage,
  };
}

export const MART_CITY_DEMO: Record<string, MartCityViewProps> = Object.fromEntries(
  CITY_SLUG_LIST.map((slug) => [slug, buildMartCityView(slug)]),
);

export function getMartCityDemo(slug: string): MartCityViewProps | null {
  return MART_CITY_DEMO[slug] ?? null;
}

// 守门常量导出（供 pytest / smoke-check 复用）
export const MART_CITY_DEMO_COUNT = CITY_SLUG_LIST.length;
export const MART_CITY_DEMO_PROVINCE_SLUGS = Array.from(
  new Set(CITY_SLUG_LIST.map((slug) => CITY_SLUG_MAP[slug].provinceSlug)),
);
export const MART_IS_DEMO_SENTINEL = MART_IS_DEMO;
// 10 城 × 2 行 demo（市委书记 + 市长）= 20 demo 相关人物行（per `302` §SCHEMA）
export const MART_CITY_DEMO_RELATED_PERSONS_PER_CITY = 2;
export const MART_CITY_DEMO_RELATED_PERSONS_TOTAL =
  MART_CITY_DEMO_COUNT * MART_CITY_DEMO_RELATED_PERSONS_PER_CITY;