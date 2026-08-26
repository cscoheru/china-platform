"use client";

// Stage 2 / S2.9-lite — Peer-region comparison card grid component.
//
// Per docs/43 §3.2 (折叠态) + §3.3 (EvidenceChain 段级对比展开态)
// + §3.4 (七维度 cell 对比展开态) + §3.5 (React 组件最小形态)
// + tasking 244 §SCHEMA "peer 对比壳 (mock OK)".
//
// 红线 (per docs/43 §8 + docs/06 §6.6 + docs/05 §8.3):
//   - 禁全国实时排名 / 禁按 GDP 总量取 top N
//   - 仅展示计数 (n_observation / n_inference / n_judgment / cells_no_contradicts 等)
//   - 不评分 / 不排名 / 不派生"地区得分" / 不派生 peer_rank
//   - 不接 S2.7 EvidenceChain UI 改动 / 不接 S2.8 七维度 UI 改动 (per docs/43 §5.1 + §5.2)
//   - 不接 S2.10 Gate 2 评审包集成 (per docs/43 §5.4)

import type { ReactElement } from "react";
import { useState } from "react";
import {
  DEVELOPMENT_STAGE_META,
  INDUSTRY_BASE_META,
  LOCATION_TYPE_META,
  POPULATION_TIER_META,
  ROLE_IN_GROUP_META,
  type ComparisonGroupMemberProps,
  type PeerCompareGroup,
} from "../../lib/types_peer_compare";
import type { SevenDimCardId } from "../../lib/types_seven_dim";
import type { MockPeerCompareRegion } from "../../lib/mock_peer_compare";

interface PeerCompareCardProps {
  group: PeerCompareGroup;
  onToggle: () => void;
}

interface PeerCompareMemberRowProps {
  member: ComparisonGroupMemberProps;
}

function PeerCompareMemberRow({ member }: PeerCompareMemberRowProps): ReactElement {
  const meta = ROLE_IN_GROUP_META[member.roleInGroup];
  return (
    <li className="peer-compare-member">
      <span className="peer-compare-member__badge" aria-label={meta.label}>
        {meta.badge} {meta.zh}
      </span>
      <span className="peer-compare-member__name">{member.geoNameZh}</span>
      <span className="peer-compare-member__reason">{member.selectionReason}</span>
    </li>
  );
}

interface EvidenceBalanceRowProps {
  geoNameZh: string;
  roleInGroup: "focal" | "peer";
  nObservation: number;
  nInference: number;
  nJudgment: number;
  nDerived: number;
  nSupports: number;
  nContradicts: number;
}

function EvidenceBalanceRow({
  geoNameZh,
  roleInGroup,
  nObservation,
  nInference,
  nJudgment,
  nDerived,
  nSupports,
  nContradicts,
}: EvidenceBalanceRowProps): ReactElement {
  return (
    <tr className="peer-compare-evidence-row">
      <td className="peer-compare-evidence-row__name">
        {geoNameZh}
        <span className="peer-compare-evidence-row__role">
          {ROLE_IN_GROUP_META[roleInGroup].zh}
        </span>
      </td>
      <td className="peer-compare-evidence-row__count">{nObservation}</td>
      <td className="peer-compare-evidence-row__count">{nInference}</td>
      <td className="peer-compare-evidence-row__count">{nJudgment}</td>
      <td className="peer-compare-evidence-row__count">{nDerived}</td>
      <td className="peer-compare-evidence-row__count">{nSupports}</td>
      <td className="peer-compare-evidence-row__count">{nContradicts}</td>
    </tr>
  );
}

interface SevenDimRowProps {
  geoNameZh: string;
  roleInGroup: "focal" | "peer";
  cellsNoContradicts: number;
  cellsSupportsDominant: number;
  cellsContradictsDominant: number;
  totalSevenDimCells: number;
}

function SevenDimRow({
  geoNameZh,
  roleInGroup,
  cellsNoContradicts,
  cellsSupportsDominant,
  cellsContradictsDominant,
  totalSevenDimCells,
}: SevenDimRowProps): ReactElement {
  return (
    <tr className="peer-compare-seven-dim-row">
      <td className="peer-compare-seven-dim-row__name">
        {geoNameZh}
        <span className="peer-compare-seven-dim-row__role">
          {ROLE_IN_GROUP_META[roleInGroup].zh}
        </span>
      </td>
      <td className="peer-compare-seven-dim-row__count">{cellsNoContradicts}</td>
      <td className="peer-compare-seven-dim-row__count">{cellsSupportsDominant}</td>
      <td className="peer-compare-seven-dim-row__count">{cellsContradictsDominant}</td>
      <td className="peer-compare-seven-dim-row__count">{totalSevenDimCells}</td>
    </tr>
  );
}

function PeerCompareCard({ group, onToggle }: PeerCompareCardProps): ReactElement {
  const isExpanded = group.expanded ?? false;
  return (
    <article
      className="peer-compare-card"
      data-group-id={group.groupId}
      data-selection-method={group.selectionMethod}
      data-is-demo={group.isDemo}
    >
      <header className="peer-compare-card__header">
        <h3 className="peer-compare-card__title">
          同类地区对比 — {group.groupNameZh}
        </h3>
        <button
          type="button"
          className="peer-compare-card__toggle"
          onClick={onToggle}
          aria-expanded={isExpanded}
        >
          {isExpanded ? "收起 ▲" : "展开 ▼"}
        </button>
      </header>

      <section className="peer-compare-card__matching-criteria">
        <h4>匹配依据（per docs/10 §133）</h4>
        <ul>
          <li>
            人口: {POPULATION_TIER_META[group.populationTier].label}
          </li>
          <li>
            区位: {LOCATION_TYPE_META[group.locationType].label}
          </li>
          <li>
            产业: {INDUSTRY_BASE_META[group.industryBase].label}
          </li>
          <li>
            阶段: {DEVELOPMENT_STAGE_META[group.developmentStage].label}
          </li>
        </ul>
      </section>

      <section className="peer-compare-card__members">
        <h4>成员（focal + peers；{group.members.length} 个地区）</h4>
        <ul>
          {group.members.map((m) => (
            <PeerCompareMemberRow key={m.geoEntityId} member={m} />
          ))}
        </ul>
      </section>

      <section className="peer-compare-card__justification">
        <strong>selection_justification（per docs/10 §133）:</strong>
        <p>{group.selectionJustification}</p>
      </section>

      {isExpanded ? (
        <div className="peer-compare-card__body">
          <section className="peer-compare-card__evidence-balance">
            <h4>EvidenceChain 段级对比（per docs/43 §3.3）</h4>
            <p className="peer-compare-card__note">
              ⚠ 仅展示计数；不排名；不算分（per docs/06 §6.6）
            </p>
            <table>
              <thead>
                <tr>
                  <th>地区</th>
                  <th>n_observation (OUTPUT)</th>
                  <th>n_inference (OUTCOME)</th>
                  <th>n_judgment (OUTCOME)</th>
                  <th>n_derived (FEEDBACK)</th>
                  <th>n_supports</th>
                  <th>n_contradicts</th>
                </tr>
              </thead>
              <tbody>
                {group.members.map((m) => {
                  const eb = group.evidenceBalanceByMember?.find(
                    (b) => b.geoEntityId === m.geoEntityId,
                  );
                  if (!eb) return null;
                  return (
                    <EvidenceBalanceRow
                      key={m.geoEntityId}
                      geoNameZh={m.geoNameZh}
                      roleInGroup={m.roleInGroup}
                      nObservation={eb.nObservation}
                      nInference={eb.nInference}
                      nJudgment={eb.nJudgment}
                      nDerived={eb.nDerived}
                      nSupports={eb.nSupports}
                      nContradicts={eb.nContradicts}
                    />
                  );
                })}
              </tbody>
            </table>
          </section>

          <section className="peer-compare-card__seven-dim">
            <h4>七维度 cell region-level 对比（per docs/43 §3.4）</h4>
            <p className="peer-compare-card__note">
              ⚠ 仅展示 balance_status 计数；不评分；不排名；不派生地区得分（per docs/06 §6.6）
            </p>
            <table>
              <thead>
                <tr>
                  <th>地区</th>
                  <th>cells_no_contradicts</th>
                  <th>cells_supports_dominant</th>
                  <th>cells_contradicts_dominant</th>
                  <th>total_seven_dim_cells</th>
                </tr>
              </thead>
              <tbody>
                {group.members.map((m) => {
                  const sd = group.sevenDimByMember?.find(
                    (s) => s.geoEntityId === m.geoEntityId,
                  );
                  if (!sd) return null;
                  return (
                    <SevenDimRow
                      key={m.geoEntityId}
                      geoNameZh={m.geoNameZh}
                      roleInGroup={m.roleInGroup}
                      cellsNoContradicts={sd.cellsNoContradicts}
                      cellsSupportsDominant={sd.cellsSupportsDominant}
                      cellsContradictsDominant={sd.cellsContradictsDominant}
                      totalSevenDimCells={sd.totalSevenDimCells}
                    />
                  );
                })}
              </tbody>
            </table>
          </section>

          {group.isDemo ? (
            <div className="peer-compare-card__is-demo">is_demo: true</div>
          ) : null}
        </div>
      ) : null}
    </article>
  );
}

interface PeerCompareGridProps {
  region: MockPeerCompareRegion;
}

// 静态 segment Next.js 路由 — 不分支 params.*（per AGENTS.md 红线）
export default function PeerCompareGrid({
  region,
}: PeerCompareGridProps): ReactElement {
  const [expanded, setExpanded] = useState<boolean>(false);
  const handleToggle = (): void => {
    setExpanded((prev) => !prev);
  };
  return (
    <section
      className="peer-compare-grid"
      aria-label={`peer-region comparison for ${region.geoNameZh}`}
      data-geo-entity-id={region.geoEntityId}
    >
      <h2 className="peer-compare-grid__title">
        同类地区对比 — {region.geoNameZh}
      </h2>
      <PeerCompareCard
        group={{ ...region.group, expanded }}
        onToggle={handleToggle}
      />
    </section>
  );
}

// Re-export for downstream consumers needing SevenDimCardId type (per docs/43 §5.2 平行)
export type { SevenDimCardId };