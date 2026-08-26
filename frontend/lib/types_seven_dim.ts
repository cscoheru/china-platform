// Stage 2 / S2.8-lite — Seven-dimension observation card type definitions.
//
// Per docs/42 §2.1 (七维度契约) + §2.4 (balance_status 5 枚举) + §2.5 (INFERENCE 角标)
// + tasking 238 §SCHEMA "七维卡最小壳 (mock OK)".
//
// 红线 (per docs/42 §8 + docs/06 §6.6):
//   - 禁官员评分 / 总分 / 排名 / 维度严重度 / 可信度
//   - 不引入 score / rating / total_score / confidence_score / credibility_score 字段
//   - 应用层 enum-style 守门（不引入 schema ENUM，per docs/40 §2.3 平行）
//
// 7 维度严格按 docs/06 §3 校准（POLICY_DELIVERY 合并 PRD 政策兑现 + 政务透明）。

export const SEVEN_DIM_CARDS = [
  {
    cardId: "POLICY_DELIVERY",
    zh: "政策兑现与政务透明",
    en: "Policy Delivery & Transparency",
    prd6_3Mapping: ["政策兑现", "政务透明"],
    primaryEvidenceSources: [
      "政府工作报告",
      "五年规划",
      "预算报告",
      "信息公开年报",
      "回应率",
      "统计修订说明",
    ],
    riskNotes: ["抽象承诺", "目标漂移", "公开 ≠ 易读"],
  },
  {
    cardId: "FISCAL_EXECUTION",
    zh: "财政执行",
    en: "Fiscal Execution",
    prd6_3Mapping: ["财政执行"],
    primaryEvidenceSources: [
      "决算",
      "预算执行通报",
      "绩效自评",
      "审计报告",
    ],
    riskNotes: ["调整预算", "决算时滞"],
  },
  {
    cardId: "PROJECT_DELIVERY",
    zh: "项目交付",
    en: "Project Delivery",
    prd6_3Mapping: ["项目交付"],
    primaryEvidenceSources: ["审批平台", "招投标", "公共资源交易"],
    riskNotes: ["签约注水", "烂尾"],
  },
  {
    cardId: "ECONOMIC_ADAPTATION",
    zh: "经济适应",
    en: "Economic Adaptation",
    prd6_3Mapping: ["经济适应"],
    primaryEvidenceSources: ["统计公报", "税收", "产业用电", "专利"],
    riskNotes: ["短期波动 vs 长期趋势"],
  },
  {
    cardId: "PUBLIC_SERVICES",
    zh: "公共服务",
    en: "Public Services",
    prd6_3Mapping: ["公共服务"],
    primaryEvidenceSources: ["教育/医疗/养老统计公报", "12345"],
    riskNotes: ["满意度抽样代表性"],
  },
  {
    cardId: "RISK_MANAGEMENT",
    zh: "风险管理",
    en: "Risk Management",
    prd6_3Mapping: ["风险管理"],
    primaryEvidenceSources: ["债务限额", "土地出让金", "房地产销售", "生态公报"],
    riskNotes: ["隐性债务", "报表美化"],
  },
  {
    cardId: "GOAL_CONSISTENCY",
    zh: "目标一致性",
    en: "Goal Consistency",
    prd6_3Mapping: ["目标一致性"],
    primaryEvidenceSources: ["工作报告 vs 实际数据", "第三方评估"],
    riskNotes: ["因果 vs 相关"],
  },
] as const;

export type SevenDimCardId = (typeof SEVEN_DIM_CARDS)[number]["cardId"];

// 应用层 enum-style 守门: SEVEN_DIM_CARD_IDS 是 7 维度的运行时合法值集合.
// 用于 dbt model WHERE card_id IN (SELECT unnest(...)) 守门; 用于 React props 校验.
export const SEVEN_DIM_CARD_IDS: readonly SevenDimCardId[] = SEVEN_DIM_CARDS.map(
  (c) => c.cardId,
);

// Balance status 5 枚举 (per docs/42 §2.4 + Gate 2 §3.2 反例守门).
// NO_CONTRADICTING_EVIDENCE 是 Gate 2 §3.2 硬卡的红色 banner 触发条件.
// 仅计数 + 枚举; 不评分; 不派生 "严重度" / "可信度".
export const BALANCE_STATUS = [
  "NO_EVIDENCE",
  "NO_CONTRADICTING_EVIDENCE",
  "NO_SUPPORTING_EVIDENCE",
  "SUPPORTS_DOMINANT",
  "CONTRADICTS_DOMINANT",
] as const;

export type BalanceStatus = (typeof BALANCE_STATUS)[number];

// 应用层守门函数: balance_status 必须是合法枚举值.
// 若返回 false, 调用方应拒绝渲染并记日志 (per docs/42 §2.6).
export function isValidBalanceStatus(s: string): s is BalanceStatus {
  return (BALANCE_STATUS as readonly string[]).includes(s);
}

export function isValidSevenDimCardId(s: string): s is SevenDimCardId {
  return (SEVEN_DIM_CARD_IDS as readonly string[]).includes(s);
}

// 卡片显示元数据: 折叠态 / 展开态均消费 (per docs/42 §3.1 / §3.2).
// banner color 仅展示; 不评分.
export interface BalanceBadge {
  status: BalanceStatus;
  badge: "🔴" | "🟡" | "🟢" | "🟠" | "⚪";
  label: string;
  bannerClass: "red" | "yellow" | "green" | "orange" | "gray";
}

export const BALANCE_BADGES: Record<BalanceStatus, BalanceBadge> = {
  NO_EVIDENCE: {
    status: "NO_EVIDENCE",
    badge: "⚪",
    label: "无证据",
    bannerClass: "gray",
  },
  NO_CONTRADICTING_EVIDENCE: {
    status: "NO_CONTRADICTING_EVIDENCE",
    badge: "🔴",
    label: "反例未登记",
    bannerClass: "red",
  },
  NO_SUPPORTING_EVIDENCE: {
    status: "NO_SUPPORTING_EVIDENCE",
    badge: "🟡",
    label: "支持证据缺失",
    bannerClass: "yellow",
  },
  SUPPORTS_DOMINANT: {
    status: "SUPPORTS_DOMINANT",
    badge: "🟢",
    label: "支持证据占优",
    bannerClass: "green",
  },
  CONTRADICTS_DOMINANT: {
    status: "CONTRADICTS_DOMINANT",
    badge: "🟠",
    label: "反例占优",
    bannerClass: "orange",
  },
};

// 七维度 cell props (per docs/42 §3.3).
export interface SevenDimCellProps {
  claimId: string;
  cardId: SevenDimCardId;
  nSupports: number;
  nContradicts: number;
  nInference: number;
  nJudgment: number;
  nDerived: number;
  balanceStatus: BalanceStatus;
  isDemo: boolean;
  expanded?: boolean;
}

// 七维度 cell 投影行 (per docs/42 §2.2 mart_seven_dim_overview).
// 此接口不导出到 schema; 仅前端 props 消费.
export interface SevenDimCell extends SevenDimCellProps {
  geoEntityId?: string;
}