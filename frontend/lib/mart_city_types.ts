// Stage 2 / S2.7-b-full-lite — mart-shape TS 类型契约。
//
// Per docs/47 §3.1 (mart_city_evidence_chain) + §3.2 (mart_city_seven_dim_overview)
// + §3.3 (person/tenure 接入契约) + §4.1 (段级字段契约) + §4.2 (七维度 cell 契约) +
// `265` §SCHEMA "mart 形状 TS 类型"。
//
// ⚠ 本文件 = mart 形状 (mart-shape) TypeScript 投影；非 dbt SQL。
// dbt mart SQL 在 S2.7-b-full 落地刀 (tasking 26X+) 写。
//
// 红线 (per docs/47 §1.2 + `265` §红线 + docs/34 §1 + docs/06 §6.6 + docs/42 §8):
//   - 不引入 score / rating / rank / total_score / confidence_score / credibility_score 字段
//   - 不派生 "地区得分" / 不派生 "地区排名" / 不做 peer_rank
//   - 不接真 SHA 样本（lineage.source_file_sha256 = '0'*64 占位）
//   - 不接 O1 收口（mart 真数据在 full 刀写）

import type {
  InformationLayer,
  Polarity,
  EvidenceStrength,
} from "./types_cities";
import type { BalanceStatus, SevenDimCardId } from "./types_seven_dim";

// mart 行级 lineage 占位（per docs/47 §3.1 ⚠️ OPEN；O1 收口前恒为 '0'*64）
export const MART_LINEAGE_PLACEHOLDER_SHA = "0".repeat(64);
export const MART_IS_DEMO = "true" as const; // mart lineage->>'is_demo' string

// mart 行级 lineage 接口（per docs/47 §3.1 + §3.2）
export interface MartLineageProps {
  isDemo: boolean;            // 演示 sentinel（per docs/33 §3.2）
  sourceFileSha256: string;   // ⚠️ OPEN — 占位为 '0'*64 直到 O1 真实 SHA 收口
  demoReason: string;         // 演示成因（人工签名；说明为何 sha 占位）
}

// mart_city_evidence_chain 单行契约（per docs/47 §3.1）
export interface MartCityEvidenceChainRowProps {
  cityId: string;                          // JOIN geo_entity.geo_entity_id
  geoNameZh: string;                       // JOIN geo_entity.geo_name_zh
  provinceSlug: string;                    // 应用层守门 lineage->>'province_slug'
  segment: string;                         // 6 段（应用层 enum-style 守门；per docs/40 §2.3）
  canonicalStatement: string;              // JOIN inference_record.canonical_statement
  canonicalPolarity: Polarity;             // JOIN inference_record.canonical_polarity
  evidenceStrength: EvidenceStrength;      // JOIN inference_record.evidence_strength
  infoLayer: InformationLayer;             // JOIN inference_record.canonical_layer
  lineage: MartLineageProps;               // ⚠️ sha256 占位
}

// mart_city_seven_dim_overview 单行契约（per docs/47 §3.2）
export interface MartCitySevenDimOverviewRowProps {
  cityId: string;                          // JOIN geo_entity.geo_entity_id
  cardId: SevenDimCardId;                  // 7 维度（per docs/42 §2.4）
  nSupports: number;                       // 聚合 claim_evidence_link WHERE polarity='SUPPORTS'
  nContradicts: number;                    // 聚合 claim_evidence_link WHERE polarity='CONTRADICTS'
  nInference: number;                      // 聚合 inference_record WHERE canonical_layer='INFERENCE'
  nJudgment: number;                       // 聚合 inference_record WHERE canonical_layer='JUDGMENT'
  nDerived: number;                        // 聚合 inference_record WHERE canonical_layer='DERIVED'
  balanceStatus: BalanceStatus;            // 5 枚举派生（per docs/42 §2.5）
  lineage: MartLineageProps;               // ⚠️ sha256 占位
}

// person/tenure 接入契约（per docs/47 §3.3 + S2.1-lite mart_person_tenure）
export interface MartPersonTenureRowProps {
  personId: string;                        // JOIN person.person_id
  canonicalName: string;                   // JOIN person.canonical_name
  positionTitle: string;                   // JOIN position.title
  geoCanonicalName: string;                // JOIN geo_entity.canonical_name
  isCurrent: boolean;                      // JOIN tenure.is_current（应用层 enum 守门）
  lineage: MartLineageProps;               // ⚠️ sha256 占位
}

// mart mart-city 视图（聚合：1 城 1 行；按需展开七维度 + 段级 evidence）
export interface MartCityViewProps {
  cityId: string;                          // JOIN geo_entity.geo_entity_id
  geoNameZh: string;                       // JOIN geo_entity.geo_name_zh
  provinceSlug: string;                    // 应用层守门
  evidenceChain: MartCityEvidenceChainRowProps[]; // 段级 evidence
  sevenDimOverview: MartCitySevenDimOverviewRowProps[]; // 七维度 cell
  relatedPersons: MartPersonTenureRowProps[];          // person/tenure 接入（OPEN）
  lineage: MartLineageProps;                            // ⚠️ sha256 占位
}

// 应用层 enum-style 守门（per docs/47 §3.1 + §4.1）
// 仅校验 mart row 必备字段；schema ENUM 未动（per docs/40 §2.3）。
export function isValidMartLineage(lineage: MartLineageProps): boolean {
  // lineage.source_file_sha256 必须 = '0'*64 占位 OR 真实 SHA（O1 收口前恒为占位）
  if (lineage.sourceFileSha256.length !== 64) {
    return false;
  }
  // demoReason 非空（人工签名）
  if (lineage.demoReason.length === 0) {
    return false;
  }
  return true;
}

// mart 形状 Source-of-Truth 守门（per docs/47 §3.2 红线）
// 不允许 mart row 含 score / rating / rank / total_score 字段。
// TypeScript 编译时已禁；运行时再防御一次。
const FORBIDDEN_MART_FIELDS = [
  "score",
  "rating",
  "rank",
  "total_score",
  "confidence_score",
  "credibility_score",
  "peer_rank",
] as const;

export function assertMartRowHasNoForbiddenFields(
  row: Record<string, unknown>,
  rowName: string,
): void {
  for (const f of FORBIDDEN_MART_FIELDS) {
    if (f in row) {
      throw new Error(
        `FORBIDDEN: mart row "${rowName}" contains forbidden field "${f}" ` +
        `(per docs/06 §6.6 + docs/42 §8 + docs/47 §3.2 红线)`,
      );
    }
  }
}