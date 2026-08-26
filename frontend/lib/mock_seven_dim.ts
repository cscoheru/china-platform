// Stage 2 / S2.8-lite — Seven-dimension mock data (per tasking 238 §SCHEMA "可 mock").
//
// Per docs/42 §3.1 (折叠态) + §3.2 (展开态) + §4 (首批 ≤140 cell).
// 本 mock 仅 1 区域 × 7 维度 = 7 cell (UI shell 最小形态).
//
// 红线:
//   - 不爬网 / 不引入 seed 数据
//   - 不引入 score / rating / rank / total_score / confidence_score 字段
//   - is_demo = "true" (per docs/33 §3.2 sentinel)

import type {
  SevenDimCell,
  SevenDimCardId,
  BalanceStatus,
} from "./types_seven_dim";

export interface MockSevenDimRegion {
  geoEntityId: string;
  geoNameZh: string;
  cells: SevenDimCell[];
}

// 1 区域 × 7 维度 = 7 cell; 每 cell 故意不同 balance_status 演示 5 枚举:
//   POLICY_DELIVERY    → NO_CONTRADICTING_EVIDENCE (🔴 Gate 2 §3.2 硬卡)
//   FISCAL_EXECUTION   → SUPPORTS_DOMINANT (🟢)
//   PROJECT_DELIVERY   → NO_SUPPORTING_EVIDENCE (🟡)
//   ECONOMIC_ADAPTATION → SUPPORTS_DOMINANT (🟢)
//   PUBLIC_SERVICES    → CONTRADICTS_DOMINANT (🟠)
//   RISK_MANAGEMENT    → NO_CONTRADICTING_EVIDENCE (🔴 Gate 2 §3.2)
//   GOAL_CONSISTENCY   → NO_EVIDENCE (⚪ 空 cell; 笛卡尔积空 cell 演示)
export const MOCK_SEVEN_DIM_REGION: MockSevenDimRegion = {
  geoEntityId: "a0000000-0000-0000-0000-000000000001",
  geoNameZh: "江苏 (mock)",
  cells: [
    {
      claimId: "claim-001",
      cardId: "POLICY_DELIVERY",
      nSupports: 3,
      nContradicts: 0,
      nInference: 2,
      nJudgment: 0,
      nDerived: 0,
      balanceStatus: "NO_CONTRADICTING_EVIDENCE",
      isDemo: true,
      expanded: false,
    },
    {
      claimId: "claim-002",
      cardId: "FISCAL_EXECUTION",
      nSupports: 5,
      nContradicts: 1,
      nInference: 1,
      nJudgment: 0,
      nDerived: 1,
      balanceStatus: "SUPPORTS_DOMINANT",
      isDemo: true,
      expanded: false,
    },
    {
      claimId: "claim-003",
      cardId: "PROJECT_DELIVERY",
      nSupports: 0,
      nContradicts: 2,
      nInference: 0,
      nJudgment: 1,
      nDerived: 0,
      balanceStatus: "NO_SUPPORTING_EVIDENCE",
      isDemo: true,
      expanded: false,
    },
    {
      claimId: "claim-004",
      cardId: "ECONOMIC_ADAPTATION",
      nSupports: 4,
      nContradicts: 1,
      nInference: 2,
      nJudgment: 1,
      nDerived: 0,
      balanceStatus: "SUPPORTS_DOMINANT",
      isDemo: true,
      expanded: false,
    },
    {
      claimId: "claim-005",
      cardId: "PUBLIC_SERVICES",
      nSupports: 1,
      nContradicts: 2,
      nInference: 0,
      nJudgment: 0,
      nDerived: 0,
      balanceStatus: "CONTRADICTS_DOMINANT",
      isDemo: true,
      expanded: false,
    },
    {
      claimId: "claim-006",
      cardId: "RISK_MANAGEMENT",
      nSupports: 2,
      nContradicts: 0,
      nInference: 1,
      nJudgment: 0,
      nDerived: 0,
      balanceStatus: "NO_CONTRADICTING_EVIDENCE",
      isDemo: true,
      expanded: false,
    },
    {
      claimId: "claim-007",
      cardId: "GOAL_CONSISTENCY",
      nSupports: 0,
      nContradicts: 0,
      nInference: 0,
      nJudgment: 0,
      nDerived: 0,
      balanceStatus: "NO_EVIDENCE",
      isDemo: true,
      expanded: false,
    },
  ],
};

// helper: 按 cardId 取 cell (UI 渲染时用)
export function getCellByCardId(
  region: MockSevenDimRegion,
  cardId: SevenDimCardId,
): SevenDimCell | undefined {
  return region.cells.find((c) => c.cardId === cardId);
}

// helper: balanceStatus 分布统计 (per docs/42 §6.4 验收)
export function countBalanceStatus(
  region: MockSevenDimRegion,
): Record<BalanceStatus, number> {
  const counts: Record<BalanceStatus, number> = {
    NO_EVIDENCE: 0,
    NO_CONTRADICTING_EVIDENCE: 0,
    NO_SUPPORTING_EVIDENCE: 0,
    SUPPORTS_DOMINANT: 0,
    CONTRADICTS_DOMINANT: 0,
  };
  for (const cell of region.cells) {
    counts[cell.balanceStatus] += 1;
  }
  return counts;
}