// Stage 2 / S2.7-b-lite — 10 地市观察页 mock 数据（壳）。
//
// Per docs/46 §6.1 (lite mock 壳范围) + `256` §SCHEMA "本刀只 mock 壳"：
//   - 10 城 × 六段证据链 mock（继承 5 省模板 6 段契约；按段填充占位说明）
//   - 10 城 × 七维度 cell mock（继承 S2.8-lite 7 cell + 5 枚举守门）
//   - 10 城 × 同类地区对比（同省地市横向：per docs/46 §11.5）
//   - is_demo = true（per docs/33 §3.2 sentinel）
//
// 红线 (per docs/46 §1.2 + `256` §红线 + docs/34 §1 + docs/43 §8):
//   - 不爬网 / 不引入 seed 数据
//   - 不引入 score / rating / rank / total_score / confidence_score 字段
//   - 不接 mart / person 真数据（OPEN → S2.7-b-full）
//   - 不做官员评分 / 排名 / 总分

import type { CityProps } from "./types_cities";
import {
  CITY_SLUG_MAP,
  CITY_SLUG_LIST,
  type CitySlugEntry,
} from "./city_slug_map";
import { BALANCE_STATUS } from "./types_seven_dim";
import type { EvidenceChainSegment } from "./types";
import type { ComparisonGroupMemberProps, PeerCompareGroup, SevenDimByMember, EvidenceBalanceByMember } from "./types_peer_compare";
import type { BalanceStatus, SevenDimCell, SevenDimCardId } from "./types_seven_dim";

const CITY_GEO_ID_PREFIX = "city-geo-mock-";

// 6 段 mock 骨架（lite 阶段：5 段空 + 1 段 CONDITION 各城 1 条占位）
// 每城至少一段非空 + 其余段"未覆盖"标记（per docs/45 §2 #2 六段缺一不可）
function buildCityEvidenceChain(citySlug: string): EvidenceChainSegment[] {
  return [
    {
      key: "CONDITION",
      items: [
        {
          title: `${CITY_SLUG_MAP[citySlug].nameZh} 区位与产业基础（占位）`,
          source_label: `MOCK · docs/46 §5.2 · ${citySlug}`,
          note: "占位说明；S2.7-b-full 接 mart_city_evidence_chain 后切换为真实数据。",
        },
      ],
    },
    { key: "COMMITMENT", items: [] },   // 演示"未覆盖"
    { key: "INPUT", items: [] },        // 演示"未覆盖"
    { key: "PROCESS", items: [] },      // 演示"未覆盖"
    { key: "OUTPUT", items: [] },       // 演示"未覆盖"
    { key: "OUTCOME_RISK", items: [] }, // 演示"未覆盖"
  ];
}

// 7 cell mock（演示 5 枚举；占位均衡）
function buildCitySevenDimCells(citySlug: string): SevenDimCell[] {
  const cityEntry = CITY_SLUG_MAP[citySlug];
  // 5 枚举循环 + 2 余量 = 7 cell
  const rotation: BalanceStatus[] = [
    BALANCE_STATUS[0], // NO_EVIDENCE
    BALANCE_STATUS[1], // NO_CONTRADICTING_EVIDENCE (🔴 Gate 2 §3.2 硬卡)
    BALANCE_STATUS[2], // NO_SUPPORTING_EVIDENCE
    BALANCE_STATUS[3], // SUPPORTS_DOMINANT
    BALANCE_STATUS[4], // CONTRADICTS_DOMINANT
    BALANCE_STATUS[3], // SUPPORTS_DOMINANT
    BALANCE_STATUS[0], // NO_EVIDENCE
  ];
  const cardIds: SevenDimCardId[] = [
    "POLICY_DELIVERY",
    "FISCAL_EXECUTION",
    "PROJECT_DELIVERY",
    "ECONOMIC_ADAPTATION",
    "PUBLIC_SERVICES",
    "RISK_MANAGEMENT",
    "GOAL_CONSISTENCY",
  ];
  return cardIds.map((cardId, idx) => ({
    claimId: `claim-${cityEntry.slug}-${idx + 1}`,
    cardId,
    nSupports: rotation[idx] === BALANCE_STATUS[3] ? 4 : rotation[idx] === BALANCE_STATUS[4] ? 1 : 2,
    nContradicts: rotation[idx] === BALANCE_STATUS[4] ? 3 : rotation[idx] === BALANCE_STATUS[2] ? 2 : 0,
    nInference: 1,
    nJudgment: 0,
    nDerived: 0,
    balanceStatus: rotation[idx],
    isDemo: true,
    expanded: false,
  }));
}

// 同省地市横向对比（per docs/46 §11.5 选项 A + docs/43 §4.1）
// focal = 本城；peers = 同省其他地市（不含 focal 自身）
function buildCityPeerCompareGroup(cityEntry: CitySlugEntry): PeerCompareGroup {
  const peersInProvince = CITY_SLUG_LIST
    .filter((slug) => CITY_SLUG_MAP[slug].provinceSlug === cityEntry.provinceSlug && slug !== cityEntry.slug);

  const members: ComparisonGroupMemberProps[] = [
    {
      geoEntityId: `${CITY_GEO_ID_PREFIX}${cityEntry.slug}`,
      geoNameZh: `${cityEntry.nameZh} (mock focal)`,
      roleInGroup: "focal",
      selectionReason: "本对比基准（focal）；同省地市横向对比",
    },
    ...peersInProvince.map<ComparisonGroupMemberProps>((peerSlug) => ({
      geoEntityId: `${CITY_GEO_ID_PREFIX}${peerSlug}`,
      geoNameZh: `${CITY_SLUG_MAP[peerSlug].nameZh} (mock peer)`,
      roleInGroup: "peer",
      selectionReason: `同省地市（peer）；与 ${cityEntry.nameZh} 区位/产业可比`,
    })),
  ];

  // evidence_balance / seven_dim 占位（mock；不评分；不排名）
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
    groupId: `city-group-${cityEntry.slug}`,
    groupNameZh: `${cityEntry.provinceSlug} 同省地市对比组 (mock)`,
    populationTier: "1000-2000万",
    locationType: "coastal",
    industryBase: "mixed",
    developmentStage: "high",
    selectionMethod: "manual", // 仅 manual 落地（per docs/43 §2.7）
    selectionJustification:
      `同省地市横向对比组：4 城均属沿海+混合产业+高发展阶段；${cityEntry.nameZh} 为本对比基准 (focal)，` +
      `${peersInProvince.map((s) => CITY_SLUG_MAP[s].nameZh).join("/")} 为可比同类 (peer)。` +
      `匹配依据 = 区位 (coastal) + 产业 (mixed) + 阶段 (high) + 人口规模 (1000-2000万)。` +
      `不按 GDP 总量取 top N（per docs/05 §8.3 红线）。`,
    members,
    evidenceBalanceByMember,
    sevenDimByMember,
    isDemo: true,
    expanded: false,
  };
}

function buildCityProps(citySlug: string): CityProps {
  const entry = CITY_SLUG_MAP[citySlug];
  return {
    slug: entry.slug,
    nameZh: entry.nameZh,
    nameEn: entry.nameEn,
    provinceSlug: entry.provinceSlug,
    evidenceChain: { segments: buildCityEvidenceChain(citySlug) },
    sevenDimCells: buildCitySevenDimCells(citySlug),
    peerCompareGroup: buildCityPeerCompareGroup(entry),
    observationCardCount: 7, // 七维度观察卡 placeholder count
    lineage: { isDemo: true },
  };
}

export const MOCK_CITIES: Record<string, CityProps> = Object.fromEntries(
  CITY_SLUG_LIST.map((slug) => [slug, buildCityProps(slug)]),
);

export function getMockCity(slug: string): CityProps | null {
  return MOCK_CITIES[slug] ?? null;
}