// Stage 2 / S2.7-a — Six-segment evidence chain mock data.
//
// Per tasking 168 §SCHEMA: 数据 允许 mock（5 省或至少江苏 + ≥1 他省路由壳）。
// Per docs/06 §2: 固定六段必须全部出现；空段显式标"未覆盖"。
//
// 当前交付（S2.7-a2 后）：
//   - 江苏省：六段全有 mock 条目（demo 占位；lineage.is_demo="true" 仍生效）
//   - 浙江 / 广东 / 四川 / 山东：六段全有路由壳，条目全空（演示"未覆盖"渲染）
//
// S2.7-a2 增量（tasking 187）：广东 / 四川 / 山东由「仅 list 占位」升级为真实路由，
// 首页 5 省列表不再有死链。真实数据（含 S2.1 person/tenure）留给 S2.7-b。

import type { EvidenceChainResponse } from "./types";

// 三省空壳必须声明在江苏 / 浙江两条链之前：S2.7-a pytest
// (tests/test_evidence_chain_s27a.py case 5/6) 拿那两个变量声明当源码切片锚点，
// 浙江段一路切到文件尾并断言「恰好 6 个空段」。新省份插在锚点之后会污染切片。
const guangdongChain: EvidenceChainResponse = {
  province_id: "GUANGDONG-GEO-UUID-MOCK",
  segments: [
    { key: "CONDITION", items: [] },     // 演示"未覆盖"
    { key: "COMMITMENT", items: [] },    // 演示"未覆盖"
    { key: "INPUT", items: [] },         // 演示"未覆盖"
    { key: "PROCESS", items: [] },       // 演示"未覆盖"
    { key: "OUTPUT", items: [] },        // 演示"未覆盖"
    { key: "OUTCOME_RISK", items: [] },  // 演示"未覆盖"
  ],
};

const sichuanChain: EvidenceChainResponse = {
  province_id: "SICHUAN-GEO-UUID-MOCK",
  segments: [
    { key: "CONDITION", items: [] },     // 演示"未覆盖"
    { key: "COMMITMENT", items: [] },    // 演示"未覆盖"
    { key: "INPUT", items: [] },         // 演示"未覆盖"
    { key: "PROCESS", items: [] },       // 演示"未覆盖"
    { key: "OUTPUT", items: [] },        // 演示"未覆盖"
    { key: "OUTCOME_RISK", items: [] },  // 演示"未覆盖"
  ],
};

const shandongChain: EvidenceChainResponse = {
  province_id: "SHANDONG-GEO-UUID-MOCK",
  segments: [
    { key: "CONDITION", items: [] },     // 演示"未覆盖"
    { key: "COMMITMENT", items: [] },    // 演示"未覆盖"
    { key: "INPUT", items: [] },         // 演示"未覆盖"
    { key: "PROCESS", items: [] },       // 演示"未覆盖"
    { key: "OUTPUT", items: [] },        // 演示"未覆盖"
    { key: "OUTCOME_RISK", items: [] },  // 演示"未覆盖"
  ],
};

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
  guangdong: guangdongChain,
  sichuan: sichuanChain,
  shandong: shandongChain,
};

// 5 省列表入口（tasking 168 §NOW-2 起）。S2.7-a2 起每个 slug 都对应
// frontend/app/provinces/<slug>/page.tsx 真实路由，列表无死链。
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
