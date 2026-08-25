// Stage 2 / S2.7-a2 — Shandong provincial observation page (route shell).
//
// Per tasking 187 §NOW-1: 粤/川/鲁三省路由壳；六段可全空 ("未覆盖")。
// 复用 mock_evidence_chain；不接 S2.1 person 真数据 (留给 S2.7-b)。
//
// 路由是 STATIC segment (per tasking 150 fix)；不接收 params.province。

import { getMockEvidenceChain } from "../../../lib/mock_evidence_chain";
import { EvidenceChain } from "../../components/EvidenceChain";

export const dynamic = "force-static";

export default async function ProvincePage() {
  // No params gate — this page IS the shandong page by file path.
  const evidenceChain = getMockEvidenceChain("shandong");
  if (!evidenceChain) {
    throw new Error("Evidence chain mock missing for shandong");
  }

  return (
    <section>
      <h1>
        山东省 省级观察页{" "}
        <small style={{ fontSize: 14, color: "#888" }}>S2.7-a2 路由壳</small>
      </h1>
      <p style={{ color: "#666" }}>
        本页演示 S2.7-a2 三省路由壳契约（per tasking 187）：六段全部"未覆盖"，等 S2.7-b
        ~ S2.7-e 接入真实数据。
      </p>

      <EvidenceChain segments={evidenceChain.segments} />

      <p style={{ fontSize: 12, color: "#999", marginTop: 24 }}>
        路由壳仅用于验证六段 UI 在空数据下仍正确显示"未覆盖"标签；不做评分、不做对比。
      </p>
    </section>
  );
}
