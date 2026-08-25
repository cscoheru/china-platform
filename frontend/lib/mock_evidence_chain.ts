// Stage 2 / S2.7-a — Six-segment evidence chain mock data.
//
// Per tasking 168 §SCHEMA: 数据 允许 mock（5 省或至少江苏 + ≥1 他省路由壳）。
// Per docs/06 §2: 固定六段必须全部出现；空段显式标"未覆盖"。
//
// 当前交付：
//   - 江苏省：六段全有 mock 条目（demo 占位；lineage.is_demo="true" 仍生效）
//   - 浙江省：六段全有路由壳，但条目大多为空（用于演示"未覆盖"渲染）
//   - 广东省 / 四川省 / 山东省：仅占位 list（路线壳入口）

import type { EvidenceChainResponse } from "./types";

const jiangsuChain: EvidenceChainResponse = {
  province_id: "JIANGSU-GEO-UUID-MOCK",
  segments: [
    {
      key: "CONDITION",
      items: [
        {
          title: "沿海区位 + 长三角一体化",
          source_label: "MOCK · docs/06 §2.1 区位",
          note: "占位说明：mock 阶段；真实数据由 S2.1-S2.6 接入。",
        },
        {
          title: "制造业基础（规上工业产值全国前列）",
          source_label: "MOCK · docs/06 §2.1 产业基础",
        },
      ],
    },
    {
      key: "COMMITMENT",
      items: [
        {
          title: "三年内引进 100 家规上工业企业",
          source_label: "MOCK · 政府工作报告（占位）",
          note: "占位；S2.2 接入 policy_document/government_commitment 表。",
        },
      ],
    },
    {
      key: "INPUT",
      items: [
        {
          title: "省级产业引导基金（占位规模）",
          source_label: "MOCK · 财政厅口径",
        },
      ],
    },
    {
      key: "PROCESS",
      items: [
        {
          title: "审批时长压缩（占位）",
          source_label: "MOCK · 政务办",
        },
      ],
    },
    {
      key: "OUTPUT",
      items: [
        {
          title: "新增规上工业企业数（占位）",
          source_label: "MOCK · 统计公报",
        },
      ],
    },
    {
      key: "OUTCOME_RISK",
      items: [
        {
          title: "规上工业增加值增速（占位）",
          source_label: "MOCK · 统计公报",
        },
      ],
    },
  ],
};

const zhejiangChain: EvidenceChainResponse = {
  province_id: "ZHEJIANG-GEO-UUID-MOCK",
  segments: [
    { key: "CONDITION", items: [] },     // 演示"未覆盖"
    { key: "COMMITMENT", items: [] },    // 演示"未覆盖"
    { key: "INPUT", items: [] },         // 演示"未覆盖"
    { key: "PROCESS", items: [] },       // 演示"未覆盖"
    { key: "OUTPUT", items: [] },        // 演示"未覆盖"
    { key: "OUTCOME_RISK", items: [] },  // 演示"未覆盖"
  ],
};

export const MOCK_EVIDENCE_CHAIN_BY_PROVINCE: Record<string, EvidenceChainResponse> = {
  jiangsu: jiangsuChain,
  zhejiang: zhejiangChain,
};

// 用于"5 省方向"的第一步：省份列表入口（per tasking 168 §NOW-2
// 「另 ≥1 省路由壳或列表入口」）
export interface ProvinceListEntry {
  slug: string;
  name_zh: string;
  has_full_chain: boolean;
}

export const MOCK_PROVINCE_LIST: ProvinceListEntry[] = [
  { slug: "jiangsu", name_zh: "江苏省", has_full_chain: true },
  { slug: "zhejiang", name_zh: "浙江省", has_full_chain: false },
  { slug: "guangdong", name_zh: "广东省", has_full_chain: false },
  { slug: "sichuan", name_zh: "四川省", has_full_chain: false },
  { slug: "shandong", name_zh: "山东省", has_full_chain: false },
];

export function getMockEvidenceChain(slug: string): EvidenceChainResponse | null {
  return MOCK_EVIDENCE_CHAIN_BY_PROVINCE[slug] ?? null;
}
