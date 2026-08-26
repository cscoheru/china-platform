// Stage 2 / S2.7-b-lite — 10 地市观察页类型契约。
//
// Per docs/46 §5.2 (段级 evidence 6 段适配) + §6.1 (lite mock 壳范围) +
// `256` §SCHEMA。
//
// 红线 (per docs/46 §1.2 + `256` §红线 + docs/34 §1):
//   - 不引入 score / rating / rank / total_score / confidence_score 字段
//   - 不动 information_layer ENUM（应用层 enum-style 守门）
//   - 不接 mart / person 真数据（OPEN → S2.7-b-full）

import type { EvidenceChainSegment, EvidenceSegmentKey } from "./types";
import type { SevenDimCell } from "./types_seven_dim";
import type { PeerCompareGroup } from "./types_peer_compare";

// 信息层 enum-style 守门（per docs/40 §2.3 + 01-core.sql §25-30）
// 应用层守门；schema ENUM 未动；migration 012 仅在 inference_record 加 canonical_layer TEXT 投影。
export const INFORMATION_LAYER = ["FACT", "DERIVED", "INFERENCE", "JUDGMENT"] as const;
export type InformationLayer = (typeof INFORMATION_LAYER)[number];

export function isValidInformationLayer(s: string): s is InformationLayer {
  return (INFORMATION_LAYER as readonly string[]).includes(s);
}

// 极性 enum-style 守门（per 01-core.sql polarity CHECK + docs/40 §2）
export const POLARITY = ["SUPPORTS", "CONTRADICTS", "NEUTRAL"] as const;
export type Polarity = (typeof POLARITY)[number];

export function isValidPolarity(s: string): s is Polarity {
  return (POLARITY as readonly string[]).includes(s);
}

// 证据强度 enum-style 守门（per docs/41 §3.5）
export const EVIDENCE_STRENGTH = ["STRONG", "MODERATE", "WEAK"] as const;
export type EvidenceStrength = (typeof EVIDENCE_STRENGTH)[number];

export function isValidEvidenceStrength(s: string): s is EvidenceStrength {
  return (EVIDENCE_STRENGTH as readonly string[]).includes(s);
}

// 地市段级 evidence props（per docs/46 §5.2 OPEN → 本刀仅 mock 壳，不强约束）
export interface CitySegmentEvidenceProps {
  segment: EvidenceSegmentKey;
  canonicalStatement: string;
  canonicalPolarity: Polarity;
  evidenceStrength: EvidenceStrength;
  infoLayer: InformationLayer;
  lineage: { isDemo: boolean };
}

// 地市观察页 props（per docs/46 §4.1 复用 S2.7-a 5 省模板）
export interface CityProps {
  slug: string;
  nameZh: string;
  nameEn: string;
  provinceSlug: string;
  evidenceChain: { segments: EvidenceChainSegment[] };
  sevenDimCells: SevenDimCell[];
  peerCompareGroup: PeerCompareGroup;
  observationCardCount: number; // 七维度观察卡 placeholder count
  lineage: { isDemo: boolean }; // per docs/33 §3.2 sentinel
}