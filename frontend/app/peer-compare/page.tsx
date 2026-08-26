// Stage 2 / S2.9-lite — Peer-region comparison demo page (mock).
//
// Per tasking 244 §SCHEMA "peer 对比壳 (mock OK)".
// 本页面仅消费 mock_peer_compare.ts; 不接后端 / 不接 dbt / 不接 mart.
//
// 红线 (per docs/43 §8 + docs/06 §6.6 + docs/05 §8.3):
//   - 禁全国实时排名 / 禁按 GDP 总量取 top N
//   - 不爬网 / 不写 seed
//   - 不引入 score / rating / peer_rank 字段
//   - 演示级 UI shell; 非生产路径
//   - selection_method = "manual"（仅 manual 落地；mahalanobis/propensity 为 Stage 3 范围）

import type { ReactElement } from "react";
import PeerCompareGrid from "../components/PeerCompareCard";
import { MOCK_PEER_COMPARE_REGION } from "../../lib/mock_peer_compare";

export default function PeerComparePage(): ReactElement {
  return (
    <main className="peer-compare-page">
      <header className="peer-compare-page__header">
        <h1>Stage 2 / S2.9-lite 同类地区对比 (mock)</h1>
        <p>
          本页面仅演示同类地区对比卡的折叠/展开 UI 形态；
          数据来自 <code>frontend/lib/mock_peer_compare.ts</code>，不接后端。
        </p>
        <p className="peer-compare-page__note">
          ⚠ 仅展示计数；不排名；不算分（per docs/06 §6.6 红线）
        </p>
      </header>
      <PeerCompareGrid region={MOCK_PEER_COMPARE_REGION} />
    </main>
  );
}