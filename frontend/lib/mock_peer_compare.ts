// Stage 2 / S2.9-lite — Peer-region comparison mock data (per tasking 244 §SCHEMA "可 mock").
//
// Per docs/43 §3.5 (peer-compare props) + §4.1 (5 focal × 3 peer = 20 行 seed 草拟) +
// §10.7 (focal/peer 双值) + tasking 244 §SCHEMA "peer 对比壳 (mock OK)".
// 本 mock 仅 1 group (focal 江苏 + 3 peer 浙江/广东/山东)；UI shell 最小形态.
//
// 红线 (per docs/43 §8 + docs/05 §8.3 + docs/06 §6.6):
//   - 禁全国实时排名 / 禁按 GDP 总量取 top N (per docs/05 §8.3)
//   - 不引入 score / rating / peer_rank / total_score 字段
//   - selection_method = "manual"（仅落地 manual；mahalanobis/propensity 为 Stage 3 范围）
//   - is_demo = "true" (per docs/33 §3.2 sentinel)

import type {
  PeerCompareGroup,
  ComparisonGroupMemberProps,
  EvidenceBalanceByMember,
  SevenDimByMember,
} from "./types_peer_compare";

export interface MockPeerCompareRegion {
  geoEntityId: string;
  geoNameZh: string;
  group: PeerCompareGroup;
}

// 1 group × 1 focal + 3 peer = 4 members; 演示 4 维度匹配依据齐全
//   focal: 江苏 (mock)
//   peers: 浙江 / 广东 / 山东
//   匹配依据: coastal + mixed + high (per docs/43 §4.1 + §10.8)
const MEMBERS: ComparisonGroupMemberProps[] = [
  {
    geoEntityId: "a0000000-0000-0000-0000-000000000001",
    geoNameZh: "江苏 (mock focal)",
    roleInGroup: "focal",
    selectionReason: "本对比基准（focal）；沿海+制造+高收入",
  },
  {
    geoEntityId: "a0000000-0000-0000-0000-000000000002",
    geoNameZh: "浙江 (mock peer)",
    roleInGroup: "peer",
    selectionReason: "沿海+混合+高收入；与江苏相邻，产业可比",
  },
  {
    geoEntityId: "a0000000-0000-0000-0000-000000000003",
    geoNameZh: "广东 (mock peer)",
    roleInGroup: "peer",
    selectionReason: "沿海+服务+高收入；同属东部沿海发达省份",
  },
  {
    geoEntityId: "a0000000-0000-0000-0000-000000000004",
    geoNameZh: "山东 (mock peer)",
    roleInGroup: "peer",
    selectionReason: "沿海+制造+中等；与江苏产业基础相近，发展阶段略低",
  },
];

// mart_peer_region_compare 投影（per docs/43 §2.4 + §5.1 + §5.2）
// 仅展示计数；不评分；不排名；不派生地区得分
const EVIDENCE_BALANCE: EvidenceBalanceByMember[] = [
  {
    geoEntityId: "a0000000-0000-0000-0000-000000000001",
    nObservation: 142,
    nInference: 38,
    nJudgment: 12,
    nDerived: 4,
    nSupports: 47,
    nContradicts: 18,
  },
  {
    geoEntityId: "a0000000-0000-0000-0000-000000000002",
    nObservation: 138,
    nInference: 35,
    nJudgment: 14,
    nDerived: 3,
    nSupports: 45,
    nContradicts: 16,
  },
  {
    geoEntityId: "a0000000-0000-0000-0000-000000000003",
    nObservation: 156,
    nInference: 42,
    nJudgment: 16,
    nDerived: 5,
    nSupports: 51,
    nContradicts: 22,
  },
  {
    geoEntityId: "a0000000-0000-0000-0000-000000000004",
    nObservation: 121,
    nInference: 29,
    nJudgment: 9,
    nDerived: 2,
    nSupports: 38,
    nContradicts: 14,
  },
];

// 七维度 cell region-level 聚合（per docs/43 §2.4 + §5.2）
// 仅展示 region-level 聚合；不做 card-level 横向对比（避免引入地区×维度排名）
const SEVEN_DIM_BY_MEMBER: SevenDimByMember[] = [
  {
    geoEntityId: "a0000000-0000-0000-0000-000000000001",
    cellsNoContradicts: 2,
    cellsSupportsDominant: 3,
    cellsContradictsDominant: 1,
    totalSevenDimCells: 7,
  },
  {
    geoEntityId: "a0000000-0000-0000-0000-000000000002",
    cellsNoContradicts: 2,
    cellsSupportsDominant: 4,
    cellsContradictsDominant: 0,
    totalSevenDimCells: 7,
  },
  {
    geoEntityId: "a0000000-0000-0000-0000-000000000003",
    cellsNoContradicts: 1,
    cellsSupportsDominant: 5,
    cellsContradictsDominant: 1,
    totalSevenDimCells: 7,
  },
  {
    geoEntityId: "a0000000-0000-0000-0000-000000000004",
    cellsNoContradicts: 2,
    cellsSupportsDominant: 3,
    cellsContradictsDominant: 2,
    totalSevenDimCells: 7,
  },
];

export const MOCK_PEER_COMPARE_REGION: MockPeerCompareRegion = {
  geoEntityId: "a0000000-0000-0000-0000-000000000001",
  geoNameZh: "江苏 (mock)",
  group: {
    groupId: "group-001",
    groupNameZh: "东部沿海发达省份对比组 (mock)",
    populationTier: "1000-2000万",
    locationType: "coastal",
    industryBase: "mixed",
    developmentStage: "high",
    selectionMethod: "manual",
    selectionJustification:
      "东部沿海发达省份对比组：4 省均属沿海+混合产业+高发展阶段；江苏为本对比基准 (focal)，浙江/广东/山东为可比同类 (peer)。匹配依据 = 区位 (coastal) + 产业 (mixed) + 阶段 (high) + 人口规模 (1000-2000万)。不按 GDP 总量取 top N（per docs/05 §8.3 红线）。",
    members: MEMBERS,
    evidenceBalanceByMember: EVIDENCE_BALANCE,
    sevenDimByMember: SEVEN_DIM_BY_MEMBER,
    isDemo: true,
    expanded: false,
  },
};

// helper: 按 geoEntityId 取 member
export function getMemberByGeoId(
  group: PeerCompareGroup,
  geoEntityId: string,
): ComparisonGroupMemberProps | undefined {
  return group.members.find((m) => m.geoEntityId === geoEntityId);
}

// helper: 按 geoEntityId 取 evidence balance
export function getEvidenceBalanceByGeoId(
  group: PeerCompareGroup,
  geoEntityId: string,
): EvidenceBalanceByMember | undefined {
  return group.evidenceBalanceByMember?.find((b) => b.geoEntityId === geoEntityId);
}

// helper: 按 geoEntityId 取七维度 cell 聚合
export function getSevenDimByGeoId(
  group: PeerCompareGroup,
  geoEntityId: string,
): SevenDimByMember | undefined {
  return group.sevenDimByMember?.find((s) => s.geoEntityId === geoEntityId);
}