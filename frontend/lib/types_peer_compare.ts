// Stage 2 / S2.9-lite — Peer-region comparison card type definitions.
//
// Per docs/43 §2.1 (comparison_group schema) + §2.2 (comparison_group_member schema)
// + §2.3 (4 维度匹配依据) + §2.7 (8 枚举守门) + tasking 244 §SCHEMA "peer 对比壳 (mock OK)".
//
// 红线 (per docs/43 §8 + docs/06 §6.6 + docs/05 §8.3):
//   - 禁全国实时排名（per docs/34 §4.3 + docs/05 §8.3 红线）
//   - 禁按 GDP 总量取 top N（per docs/05 §8.3 红线）
//   - 禁 Mahalanobis 距离 / 倾向得分自动匹配（Stage 3 范围）
//   - 禁官员评分 / 总分 / 排名 / peer_rank
//   - 不引入 score / rating / total_score / peer_rank / confidence_score 字段
//   - 应用层 enum-style 守门（不引入 schema ENUM，per docs/40 §2.3 平行）
//   - selection_method 仅 manual 落地（per docs/43 §2.7）

// §2.3 + §2.7: 4 维度匹配依据 enum（per docs/05 §8.1）
export const POPULATION_TIER = [
  "<500万",
  "500-1000万",
  "1000-2000万",
  ">2000万",
] as const;

export type PopulationTier = (typeof POPULATION_TIER)[number];

export const LOCATION_TYPE = ["coastal", "inland", "border"] as const;

export type LocationType = (typeof LOCATION_TYPE)[number];

export const INDUSTRY_BASE = [
  "resource",
  "manufacturing",
  "service",
  "mixed",
] as const;

export type IndustryBase = (typeof INDUSTRY_BASE)[number];

export const DEVELOPMENT_STAGE = ["high", "middle", "low"] as const;

export type DevelopmentStage = (typeof DEVELOPMENT_STAGE)[number];

// §2.7: 成员角色 enum（per docs/43 §10.7）
export const ROLE_IN_GROUP = ["focal", "peer"] as const;

export type RoleInGroup = (typeof ROLE_IN_GROUP)[number];

// §2.7: selection_method enum（落地刀仅 manual；mahalanobis/propensity 为 Stage 3）
export const SELECTION_METHOD = ["manual", "mahalanobis", "propensity"] as const;

export type SelectionMethod = (typeof SELECTION_METHOD)[number];

// 应用层 enum-style 守门（per docs/43 §2.7）
export function isValidPopulationTier(s: string): s is PopulationTier {
  return (POPULATION_TIER as readonly string[]).includes(s);
}

export function isValidLocationType(s: string): s is LocationType {
  return (LOCATION_TYPE as readonly string[]).includes(s);
}

export function isValidIndustryBase(s: string): s is IndustryBase {
  return (INDUSTRY_BASE as readonly string[]).includes(s);
}

export function isValidDevelopmentStage(s: string): s is DevelopmentStage {
  return (DEVELOPMENT_STAGE as readonly string[]).includes(s);
}

export function isValidRoleInGroup(s: string): s is RoleInGroup {
  return (ROLE_IN_GROUP as readonly string[]).includes(s);
}

// §2.7: 8 枚举元数据（per docs/43 §2.3 + §2.7）
// 仅展示元数据；不评分；不派生"地区得分"
export const POPULATION_TIER_META: Record<PopulationTier, { zh: string; label: string }> = {
  "<500万": { zh: "<500万", label: "人口 <500万" },
  "500-1000万": { zh: "500-1000万", label: "人口 500-1000万" },
  "1000-2000万": { zh: "1000-2000万", label: "人口 1000-2000万" },
  ">2000万": { zh: ">2000万", label: "人口 >2000万" },
};

export const LOCATION_TYPE_META: Record<LocationType, { zh: string; label: string }> = {
  coastal: { zh: "沿海", label: "沿海 (coastal)" },
  inland: { zh: "内陆", label: "内陆 (inland)" },
  border: { zh: "沿边", label: "沿边 (border)" },
};

export const INDUSTRY_BASE_META: Record<IndustryBase, { zh: string; label: string }> = {
  resource: { zh: "资源型", label: "资源型 (resource)" },
  manufacturing: { zh: "制造型", label: "制造型 (manufacturing)" },
  service: { zh: "服务型", label: "服务型 (service)" },
  mixed: { zh: "混合", label: "混合 (mixed)" },
};

export const DEVELOPMENT_STAGE_META: Record<DevelopmentStage, { zh: string; label: string }> = {
  high: { zh: "高收入", label: "高收入 (high)" },
  middle: { zh: "中等", label: "中等 (middle)" },
  low: { zh: "欠发达", label: "欠发达 (low)" },
};

export const ROLE_IN_GROUP_META: Record<RoleInGroup, { zh: string; label: string; badge: string }> = {
  focal: { zh: "基准", label: "focal (本对比基准)", badge: "🎯" },
  peer: { zh: "同类", label: "peer (同类地区)", badge: "🔗" },
};

// §3.5: peer-compare 组件 props（per docs/43 §3.5）
export interface ComparisonGroupMemberProps {
  geoEntityId: string;
  geoNameZh: string;
  roleInGroup: RoleInGroup;
  selectionReason: string; // 非空（per docs/10 §133 + docs/43 §2.2）
}

// §3.5 + §2.4: mart_peer_region_compare 投影（per docs/43 §2.4 + §5.1 + §5.2）
export interface EvidenceBalanceByMember {
  geoEntityId: string;
  nObservation: number;
  nInference: number;
  nJudgment: number;
  nDerived: number;
  nSupports: number;
  nContradicts: number;
}

export interface SevenDimByMember {
  geoEntityId: string;
  cellsNoContradicts: number;
  cellsSupportsDominant: number;
  cellsContradictsDominant: number;
  totalSevenDimCells: number;
}

// §2.1 + §2.2: comparison_group 主 props（per docs/43 §2.1 + §2.2 + §3.5）
export interface ComparisonGroupProps {
  groupId: string;
  groupNameZh: string;
  populationTier: PopulationTier;
  locationType: LocationType;
  industryBase: IndustryBase;
  developmentStage: DevelopmentStage;
  selectionMethod: SelectionMethod; // 落地刀仅 "manual"
  selectionJustification: string; // 非空（per docs/10 §133 + docs/43 §7）
  members: ReadonlyArray<ComparisonGroupMemberProps>;
  // mart_peer_region_compare 输出（per docs/43 §2.4 + §3.5）
  evidenceBalanceByMember?: ReadonlyArray<EvidenceBalanceByMember>;
  sevenDimByMember?: ReadonlyArray<SevenDimByMember>;
  isDemo: boolean; // per docs/33 §3.2 sentinel
  expanded?: boolean;
}

// §3.5: PeerCompareGroup 接口（per docs/43 §3.5）
export interface PeerCompareGroup extends ComparisonGroupProps {
  geoEntityId?: string;
}