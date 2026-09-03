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
import { getMartProvinceGdp2024 } from "./mart-static";

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

// ---------------------------------------------------------------------------
// 661 P1 · Real peer-compare group from mart data.
// Per docs/87 §3.1 P1 先行 + C4 + 红线 6 「不评分不排名」+ docs/43 §8 「selection_method=manual」.
// Mock 链 (上方 MOCK_PEER_COMPARE_REGION 等) 完整保留作为回退通道,per 红线 4 「mock 不删」.
// ---------------------------------------------------------------------------

export interface RealPeerCompareMetric {
  key: string;
  label: string;
  unit: string;
  isPct?: boolean;
}

export interface RealPeerCompareMember {
  province_code: string;
  province_name: string;
  role: "focal" | "peer";
  metrics: {
    gdp_total: number | string | null;
    gdp_growth: number | string | null;
    secondary_gdp: number | string | null;
    tertiary_gdp: number | string | null;
  };
  lineage_source: string;
  lineage_origin: string;
  source_url: string | null;
  source_hash_prefix: string | null;
  status: string | null;
}

export interface RealPeerCompareGroup {
  group_id: string;
  group_name_zh: string;
  focal: RealPeerCompareMember;
  peers: RealPeerCompareMember[];
  metric_keys: RealPeerCompareMetric[];
  selection_method: "manual";
  selection_justification: string;
  data_source: string; // e.g. "mart_province_gdp_2024"
  is_real_data: true;
}

// 661 P1 切片选定的 4 省: 江苏(focal) + 浙江/广东/山东(peer).
// 选择依据沿用 mock 历史 (沿海+混合+高发展阶段),但数据全部来自 mart 静态导出.
// 禁按 GDP 总量取 top N (per docs/05 §8.3);4 省名单与 mock 一致 (仅口径替换).
const REAL_PEER_COMPARE_TARGETS: Array<{
  code: string;
  role: "focal" | "peer";
  reason: string;
}> = [
  {
    code: "JIANGSU",
    role: "focal",
    reason: "本对比基准 (focal); 沿海+制造+高收入",
  },
  {
    code: "ZHEJIANG",
    role: "peer",
    reason: "沿海+混合+高收入; 与江苏相邻,产业可比",
  },
  {
    code: "GUANGDONG",
    role: "peer",
    reason: "沿海+服务+高收入; 同属东部沿海发达省份",
  },
  {
    code: "SHANDONG",
    role: "peer",
    reason: "沿海+制造+中等; 与江苏产业基础相近",
  },
];

const REAL_PEER_COMPARE_METRICS: RealPeerCompareMetric[] = [
  { key: "gdp_total", label: "GDP 总量", unit: "亿元" },
  { key: "gdp_growth", label: "GDP 增速", unit: "%", isPct: true },
  { key: "secondary_gdp", label: "二产增加值", unit: "亿元" },
  { key: "tertiary_gdp", label: "三产增加值", unit: "亿元" },
];

/**
 * 661 P1: 用 mart 静态导出构造真实数据 peer-compare group.
 * 仅当 mart 数据存在 (NEXT_PUBLIC_MART_DATA_PATH 已配置) 时返回, 否则 null
 * (page.tsx 走 mock 回退通道).
 *
 * 红线:
 *  - 不评分不排名 (per docs/06 §6.6)
 *  - selection_method = "manual" (per docs/43 §8)
 *  - 数据全部来自 mart 静态导出 (禁手填 per 红线 6)
 *  - DATA_MISSING 成员 metrics 字段为 null (禁补零 per 红线 1)
 *  - 不接 EvidenceChain / 七维度 cell 对比 (per docs/43 §5.1 + §5.2; P3 深水区)
 */
export function buildRealPeerCompareGroup(): RealPeerCompareGroup | null {
  const mart = getMartProvinceGdp2024();
  if (!mart) return null;

  const byCode = new Map(mart.provinces.map((p) => [p.province_code, p]));
  const members: RealPeerCompareMember[] = [];
  for (const t of REAL_PEER_COMPARE_TARGETS) {
    const row = byCode.get(t.code);
    if (!row) {
      // 4 省名单任何一项未在 mart 中找到 → 整组不可用, 走 mock 回退
      return null;
    }
    members.push({
      province_code: row.province_code,
      province_name: row.province_name,
      role: t.role,
      metrics: {
        gdp_total: row.gdp_total,
        gdp_growth: row.gdp_growth,
        secondary_gdp: row.secondary_gdp,
        tertiary_gdp: row.tertiary_gdp,
      },
      lineage_source: row.lineage_source,
      lineage_origin: row.lineage_origin,
      source_url: row.source_url,
      source_hash_prefix: row.source_hash_prefix,
      status: row.status,
    });
  }

  const focal = members.find((m) => m.role === "focal");
  const peers = members.filter((m) => m.role === "peer");
  if (!focal || peers.length !== 3) {
    return null; // 不变量违反, 走 mock 回退
  }

  return {
    group_id: "peer-compare-661-real",
    group_name_zh: "东部沿海发达省份对比组 (real data, knife 661 P1)",
    focal,
    peers,
    metric_keys: REAL_PEER_COMPARE_METRICS,
    selection_method: "manual",
    selection_justification:
      "东部沿海发达省份对比组 (real data): 4 省均属沿海+混合产业+高发展阶段; 江苏为本对比基准 (focal), 浙江/广东/山东为可比同类 (peer). 匹配依据 = 区位 (coastal) + 产业 (mixed) + 阶段 (high) + 人口规模 (1000-2000万). 不按 GDP 总量取 top N (per docs/05 §8.3 红线). 4 省名单与 S2.9-lite mock 一致, 数据全部来自 mart_province_gdp_2024 (knife 660 Track B + 661 扩展), 仅口径替换. 不接 EvidenceChain / 七维度 cell 对比 (per docs/43 §5.1 + §5.2; P3 深水区).",
    data_source: mart.mart_source,
    is_real_data: true,
  };
}