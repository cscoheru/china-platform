// Stage 2 / S2.8-lite — Seven-dimension observation card grid component.
//
// Per docs/42 §3.1 (折叠态) + §3.2 (展开态) + §3.3 (React 组件最小形态).
// 本组件仅消费 mock 数据 (per tasking 238 §SCHEMA "可 mock").
//
// 红线 (per docs/42 §8 + docs/06 §6.6):
//   - 禁官员评分 / 总分 / 排名 / 维度严重度 / 可信度
//   - 仅展示 (n_supports / n_contradicts); 不派生 score
//   - 不接 S2.9 同类对比全量 (同类区间位保留占位 + 注)

import type { ReactElement } from "react";
import { useState } from "react";
import {
  BALANCE_BADGES,
  SEVEN_DIM_CARDS,
  type BalanceStatus,
  type SevenDimCell,
  type SevenDimCardId,
} from "../../lib/types_seven_dim";
import type { MockSevenDimRegion } from "../../lib/mock_seven_dim";

interface SevenDimGridProps {
  region: MockSevenDimRegion;
}

interface SevenDimCardProps {
  cell: SevenDimCell;
  onToggle: (cardId: SevenDimCardId) => void;
}

function counterLabel(cell: SevenDimCell): string {
  return `${cell.nSupports} 支持 / ${cell.nContradicts} 反例`;
}

function inferenceBadges(cell: SevenDimCell): string {
  const parts: string[] = [];
  if (cell.nInference > 0) parts.push(`${cell.nInference} INFERENCE`);
  if (cell.nJudgment > 0) parts.push(`${cell.nJudgment} JUDGMENT`);
  if (cell.nDerived > 0) parts.push(`${cell.nDerived} DERIVED`);
  return parts.length === 0 ? "无" : parts.join(" / ");
}

function bannerClassFromStatus(status: BalanceStatus): string {
  return BALANCE_BADGES[status].bannerClass;
}

function SevenDimCard({ cell, onToggle }: SevenDimCardProps): ReactElement {
  const cardMeta = SEVEN_DIM_CARDS.find((c) => c.cardId === cell.cardId);
  if (!cardMeta) {
    return (
      <div className="seven-dim-card seven-dim-card--invalid">
        unknown cardId: {cell.cardId}
      </div>
    );
  }
  const badge = BALANCE_BADGES[cell.balanceStatus];
  return (
    <div
      className={`seven-dim-card banner-${bannerClassFromStatus(cell.balanceStatus)}`}
      data-card-id={cell.cardId}
      data-balance-status={cell.balanceStatus}
      data-is-demo={cell.isDemo}
    >
      <div className="seven-dim-card__header">
        <div className="seven-dim-card__title">
          {cardMeta.zh}{" "}
          <span className="seven-dim-card__title-en">({cardMeta.en})</span>
        </div>
        <button
          type="button"
          className="seven-dim-card__toggle"
          onClick={() => onToggle(cell.cardId)}
          aria-expanded={cell.expanded ?? false}
        >
          {cell.expanded ? "收起 ▲" : "展开 ▼"}
        </button>
      </div>

      <div className="seven-dim-card__balance">
        <span className="seven-dim-card__badge" aria-label={badge.label}>
          {badge.badge} {badge.label}
        </span>
        <span className="seven-dim-card__counter">{counterLabel(cell)}</span>
      </div>

      <div className="seven-dim-card__inference-badges">
        inference: {inferenceBadges(cell)}
      </div>

      {cell.expanded ? (
        <div className="seven-dim-card__body">
          <div className="seven-dim-card__sources">
            <strong>主要证据来源：</strong>
            {cardMeta.primaryEvidenceSources.join(" / ")}
          </div>
          <div className="seven-dim-card__risks">
            <strong>风险提示：</strong>
            {cardMeta.riskNotes.join(" / ")}
          </div>
          <div className="seven-dim-card__prd-mapping">
            <strong>PRD 6.3 映射：</strong>
            {cardMeta.prd6_3Mapping.join(" + ")}
          </div>
          <div className="seven-dim-card__evidence-gaps">
            <strong>evidence gaps：</strong>
            段级（per docs/06 §2.7）；S2.7 接驳点
          </div>
          <div className="seven-dim-card__same-region-interval">
            <strong>同类区间：</strong>
            <em>（S2.9 范围；此刀不接）</em>
          </div>
          {cell.isDemo ? (
            <div className="seven-dim-card__is-demo">is_demo: true</div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

export default function SevenDimGrid({
  region,
}: SevenDimGridProps): ReactElement {
  const [expanded, setExpanded] = useState<Record<SevenDimCardId, boolean>>(
    {} as Record<SevenDimCardId, boolean>,
  );
  const handleToggle = (cardId: SevenDimCardId): void => {
    setExpanded((prev) => ({ ...prev, [cardId]: !prev[cardId] }));
  };
  return (
    <section
      className="seven-dim-grid"
      aria-label={`seven-dimension observation grid for ${region.geoNameZh}`}
      data-geo-entity-id={region.geoEntityId}
    >
      <h2 className="seven-dim-grid__title">
        七维度观察卡 — {region.geoNameZh}
      </h2>
      <div className="seven-dim-grid__cards">
        {region.cells.map((cell) => (
          <SevenDimCard
            key={`${cell.claimId}-${cell.cardId}`}
            cell={{ ...cell, expanded: expanded[cell.cardId] ?? false }}
            onToggle={handleToggle}
          />
        ))}
      </div>
    </section>
  );
}