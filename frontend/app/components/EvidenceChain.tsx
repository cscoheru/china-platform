// Stage 2 / S2.7-a — Six-segment evidence chain UI prototype.
//
// Per docs/06 §2 + tasking 168:
//   固定顺序：CONDITION → COMMITMENT → INPUT → PROCESS → OUTPUT → OUTCOME_RISK
//   "缺一不可的展示契约"：六段都必须渲染；空段显式标"未覆盖"，绝不省略。
//
// 红线 (per tasking 168):
//   - 禁止官员能力分 / 总分 / 排名（只列证据条目，不评价好坏）
//   - 不 DSH；不爬网；不改 gate_thresholds.json
//   - 不扩 S2.1 person/tenure schema（留给后续刀）
//
// 交互：点击段头展开/收起证据条目列表。无评分、无排序。
// 数据：mock 占位（per tasking 168 §SCHEMA「数据 允许 mock」）。

import type { EvidenceChainSegment } from "../../lib/types";

const SEGMENT_META: Record<EvidenceChainSegment["key"], {
  order: number;
  zh: string;
  en: string;
  description: string;
}> = {
  CONDITION: {
    order: 1,
    zh: "条件",
    en: "CONDITION",
    description: "观察对象继承的发展基础：区位、资源、产业基础、人口、人才、历史债务、全国周期",
  },
  COMMITMENT: {
    order: 2,
    zh: "承诺",
    en: "COMMITMENT",
    description: "主政者公开目标：政府工作报告、预算报告、政策文件、任前公示、重大活动",
  },
  INPUT: {
    order: 3,
    zh: "投入",
    en: "INPUT",
    description: "兑现承诺投入的资源：财政、土地、融资、组织、政策工具",
  },
  PROCESS: {
    order: 4,
    zh: "执行",
    en: "PROCESS",
    description: "资源转化为产出的过程：预算执行率、审批时长、项目节点、政策落地、信息公开、纠偏",
  },
  OUTPUT: {
    order: 5,
    zh: "产出",
    en: "OUTPUT",
    description: "直接结果（不评价好坏）：设施建成、服务供给、企业落地、就业岗位、吸引投资",
  },
  OUTCOME_RISK: {
    order: 6,
    zh: "结果与风险",
    en: "OUTCOME_RISK",
    description: "中长期效果：收入、生产率、就业、创新、公共服务、生态、债务、房地产、人口",
  },
};

export interface EvidenceChainProps {
  segments: EvidenceChainSegment[];
}

export function EvidenceChain({ segments }: EvidenceChainProps): React.ReactElement {
  // 校验完整性：六段都必须存在（per docs/06 §2「缺一不可」）。即使 mock 也是
  // 六段；缺段是 schema 错误，不是 UI 选择。
  const expectedOrder = ["CONDITION", "COMMITMENT", "INPUT", "PROCESS", "OUTPUT", "OUTCOME_RISK"];
  const providedKeys = new Set(segments.map((s) => s.key));
  const missing = expectedOrder.filter((k) => !providedKeys.has(k as EvidenceChainSegment["key"]));
  if (missing.length > 0) {
    throw new Error(
      `EvidenceChain: missing required segments: ${missing.join(", ")}. ` +
      `Per docs/06 §2, all 6 segments are required.`
    );
  }

  // 按固定顺序排序（防御性：上游可能乱序）
  const ordered = [...segments].sort(
    (a, b) => SEGMENT_META[a.key].order - SEGMENT_META[b.key].order
  );

  return (
    <section data-testid="evidence-chain" aria-label="六段证据链">
      <h2 style={{ marginTop: 24 }}>
        六段证据链 <small style={{ fontSize: 12, color: "#888" }}>(S2.7-a 雏形 · mock 数据)</small>
      </h2>
      <p style={{ fontSize: 12, color: "#888" }}>
        每条治理观察 = 条件 → 承诺 → 投入 → 执行 → 产出 → 结果与风险（六段缺一不可；
        空段显式标"未覆盖"，不省略）。
      </p>
      <ol style={{ listStyle: "none", padding: 0, marginTop: 16 }}>
        {ordered.map((seg) => {
          const meta = SEGMENT_META[seg.key];
          const isEmpty = seg.items.length === 0;
          return (
            <li
              key={seg.key}
              data-testid={`evidence-segment-${seg.key}`}
              style={{
                border: "1px solid #ddd",
                borderRadius: 4,
                marginBottom: 8,
                padding: "10px 14px",
                background: isEmpty ? "#fafafa" : "#fff",
              }}
            >
              <details>
                <summary
                  style={{
                    cursor: "pointer",
                    fontWeight: 500,
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                  }}
                >
                  <span style={{ color: "#666", fontSize: 12 }}>
                    {meta.order}.
                  </span>
                  <span>
                    {meta.zh} <small style={{ color: "#888" }}>({meta.en})</small>
                  </span>
                  {isEmpty ? (
                    <span
                      data-testid={`segment-gap-${seg.key}`}
                      style={{
                        marginLeft: 8,
                        padding: "2px 8px",
                        background: "#fff3cd",
                        color: "#856404",
                        fontSize: 11,
                        borderRadius: 3,
                      }}
                    >
                      未覆盖
                    </span>
                  ) : (
                    <span
                      data-testid={`segment-count-${seg.key}`}
                      style={{
                        marginLeft: 8,
                        padding: "2px 8px",
                        background: "#e7f3ff",
                        color: "#004085",
                        fontSize: 11,
                        borderRadius: 3,
                      }}
                    >
                      {seg.items.length} 条证据
                    </span>
                  )}
                </summary>
                <div style={{ marginTop: 8, fontSize: 13, color: "#555" }}>
                  <p style={{ margin: "0 0 8px 0", color: "#666", fontSize: 12 }}>
                    {meta.description}
                  </p>
                  {isEmpty ? (
                    <p style={{ color: "#999", fontStyle: "italic" }}>
                      该段暂无证据条目；按 docs/06 §2.7，inference_record.evidence_gaps
                      会记录此处缺失。
                    </p>
                  ) : (
                    <ul style={{ margin: 0, paddingLeft: 18 }}>
                      {seg.items.map((item, idx) => (
                        <li key={idx} data-testid={`evidence-item-${seg.key}-${idx}`}>
                          <strong>{item.title}</strong>
                          {item.source_label ? (
                            <span style={{ color: "#888", marginLeft: 6 }}>
                              · 来源：{item.source_label}
                            </span>
                          ) : null}
                          {item.note ? (
                            <div style={{ color: "#666", fontSize: 12, marginTop: 2 }}>
                              {item.note}
                            </div>
                          ) : null}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </details>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
