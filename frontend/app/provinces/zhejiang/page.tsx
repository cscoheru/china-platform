// Stage 2 / S2.7-a — Zhejiang provincial observation page (route shell).
//
// Per tasking 168 §NOW-2: 至少 1 个省页可演示完整六段；另 ≥1 省路由壳或列表入口。
// 浙江 = 路由壳：六段全部"未覆盖"（演示 evidence_gaps 渲染）。
//
// 路由是 STATIC segment（per tasking 150 fix）；不接收 params.province。

import { getMockEvidenceChain } from "../../../lib/mock_evidence_chain";
import { EvidenceChain } from "../../components/EvidenceChain";

export const dynamic = "force-static";

export default async function ProvincePage() {
  // No params gate — this page IS the zhejiang page by file path.
  const evidenceChain = getMockEvidenceChain("zhejiang");
  if (!evidenceChain) {
    throw new Error("Evidence chain mock missing for zhejiang");
  }

  return (
    <section>
      <h1>
        浙江省 省级观察页{" "}
        <small style={{ fontSize: 14, color: "#888" }}>S2.7-a 路由壳</small>
      </h1>
      <p style={{ color: "#666" }}>
        本页演示"六段全部未覆盖"的渲染契约（per docs/06 §2.7 evidence_gaps）。
        真实数据由 S2.7-b ~ S2.7-e 接入。
      </p>

      <EvidenceChain segments={evidenceChain.segments} />

      <p style={{ fontSize: 12, color: "#999", marginTop: 24 }}>
        路由壳仅用于验证六段 UI 在空数据下仍正确显示"未覆盖"标签；不做评分、不做对比。
      </p>
    </section>
  );
}
