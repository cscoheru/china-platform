// Stage 2 / S2.8-lite — Seven-dimension observation grid demo page (mock).
//
// Per tasking 238 §SCHEMA "七维卡 UI 壳 (mock OK)".
// 本页面仅消费 mock_seven_dim.ts; 不接后端 / 不接 dbt / 不接 mart.
//
// 红线 (per docs/42 §8 + docs/06 §6.6):
//   - 不爬网 / 不写 seed
//   - 不引入 score / rating / rank 列
//   - 演示级 UI shell; 非生产路径

import type { ReactElement } from "react";
import SevenDimGrid from "../components/SevenDimGrid";
import { MOCK_SEVEN_DIM_REGION } from "../../lib/mock_seven_dim";
import { DemoBanner } from "../DemoBanner";

export default function SevenDimPage(): ReactElement {
  return (
    <main className="seven-dim-page">
      <header className="seven-dim-page__header">
        <h1>Stage 2 / S2.8-lite 七维度观察卡 (mock)</h1>
        <p>
          本页面仅演示七维度卡的折叠/展开 UI 形态；
          数据来自 <code>frontend/lib/mock_seven_dim.ts</code>，不接后端。
        </p>
      </header>
      {/* 662 D5: demo 壳显式横幅. */}
      <DemoBanner
        reason="S2.8-lite mock 七维度观察卡 · 仅 1 区域 × 7 cell, 非 31 省 · 非 Gate PASS"
        source="frontend/lib/mock_seven_dim.ts"
      />
      <SevenDimGrid region={MOCK_SEVEN_DIM_REGION} />
    </main>
  );
}