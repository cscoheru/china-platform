// Stage 2 / 公开提取呈现 — public-extracts 页面 (REGISTRY_SAMPLE / demo).
//
// Per tasking 349 §SCHEMA:
//   (1) 前端读 public_extracts — build-time fixture 快照自
//       data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN.json
//       (frontend/lib/public_extract_nbs.json, resolveJsonModule).
//   (2) 专用区块展示 NBS 提取表 (63 行全量), 显式标注 REGISTRY_SAMPLE /
//       demo — 非 live O1.
//   (3) 保留 mart demo 旗标逻辑; 不谎称真收口.
//
// 红线 (per 349 §红线): sample ≠ live; 不伪造; 不宣称 O1/Gate PASS.
// Per tasking 358 §SCHEMA (live candidate 并列): 同页第二区块展示
// NATIONAL_BULLETIN_LIVE_CANDIDATE (live deeplink 文章 drift 候选,
// frontend/lib/public_extract_nbs_live_candidate.json) — 显式
// LIVE_CANDIDATE / 非 O1 / 与 sample 分轨, 不覆盖 sample.
// Per tasking 370 §SCHEMA (深圳 REGISTRY_SAMPLE 分节): 同页第三区块展示
// sz.gov.cn MUNICIPAL_BULLETIN 散文抽取 (71 行,
// frontend/lib/public_extract_sz.json) — 显式 REGISTRY_SAMPLE / demo /
// 散文段落抽取; 不覆盖 NBS sample/live 两轨.
// 静态路由: 无 params.*, 无 force-dynamic (纯 fixture 消费).

import type { ReactElement } from "react";
import DemoBadge from "../DemoBadge";
import fixture from "../../lib/public_extract_nbs.json";
import liveCandidateFixture from "../../lib/public_extract_nbs_live_candidate.json";
import szFixture from "../../lib/public_extract_sz.json";

interface ExtractRow {
  [columnKey: string]: string;
}

interface PublicExtractFixture {
  domain: string;
  category: string;
  source_sample_path: string;
  source_archive_path: string;
  source_sha256: string;
  row_count: number;
  rows: ExtractRow[];
  extracted_at: string;
}

interface LiveCandidateFixture {
  domain: string;
  category: string;
  intake_status: string;
  is_demo: string;
  demo_reason: string;
  source_sample_path: string | null;
  source_deeplink_url: string;
  source_archive_path: string;
  source_sha256: string;
  row_count: number;
  rows: ExtractRow[];
  extracted_at: string;
}

const extract = fixture as PublicExtractFixture;
const live = liveCandidateFixture as LiveCandidateFixture;
const sz = szFixture as PublicExtractFixture;

// 列序 = 首行键序 (spike 提取保序); 不重排、不重命名、不 reinterpret.
const columnKeys: string[] =
  extract.rows.length > 0 ? Object.keys(extract.rows[0]) : [];
const liveColumnKeys: string[] =
  live.rows.length > 0 ? Object.keys(live.rows[0]) : [];
const szColumnKeys: string[] =
  sz.rows.length > 0 ? Object.keys(sz.rows[0]) : [];

const cellStyle: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "6px 10px",
  textAlign: "left",
};

export default function PublicExtractsPage(): ReactElement {
  return (
    <main className="public-extracts-page">
      <header className="public-extracts-page__header">
        <h1>
          公开提取样本 — NBS 月度公报表
          <DemoBadge
            lineage={{
              is_demo: "true",
              demo_reason:
                "REGISTRY_SAMPLE — registry 本地样本结构化提取 (spike 快照); " +
                "非 live O1; sample ≠ live closure",
            }}
          />
        </h1>
        <p style={{ color: "#856404", fontWeight: 600 }}>
          标注:REGISTRY_SAMPLE / demo — 数据来自 registry 锁定的本地样本
          (spike),经 --from-local-sample 结构化提取;**非** live O1 收口数据。
        </p>
      </header>

      <section className="public-extracts-page__provenance">
        <h2>来源溯源 (provenance)</h2>
        <table
          style={{ borderCollapse: "collapse", width: "100%", fontSize: 14 }}
        >
          <tbody>
            <tr>
              <th style={cellStyle}>domain</th>
              <td style={cellStyle}>
                <code>{extract.domain}</code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>category</th>
              <td style={cellStyle}>
                <code>{extract.category}</code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>intake_status</th>
              <td style={cellStyle}>
                <code>REGISTRY_SAMPLE_INTAKED</code>(is_demo=true)
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>source_sample_path</th>
              <td style={cellStyle}>
                <code>{extract.source_sample_path}</code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>source_archive_path (WORM)</th>
              <td style={cellStyle}>
                <code>{extract.source_archive_path}</code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>source_sha256</th>
              <td style={cellStyle}>
                <code style={{ fontSize: 11, wordBreak: "break-all" }}>
                  {extract.source_sha256}
                </code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>row_count</th>
              <td style={cellStyle}>{extract.row_count}</td>
            </tr>
            <tr>
              <th style={cellStyle}>extracted_at</th>
              <td style={cellStyle}>{extract.extracted_at}</td>
            </tr>
          </tbody>
        </table>
        <p style={{ marginTop: 8, fontSize: 12, color: "#999" }}>
          注:source_sha256 与 source_registry/registry.csv 中 stats.gov.cn /
          NATIONAL_BULLETIN 行的 file_hash_sha256 一致(样本锁定);live 收口
          (O1) 尚未宣布。live 探测已过 JS 壳门 (per tasking 355),当前为
          drift 候选 → 见下方 LIVE_CANDIDATE 分轨。
        </p>
      </section>

      <section className="public-extracts-page__table">
        <h2>提取表 ({extract.rows.length} 行,全量展示)</h2>
        <table
          style={{ borderCollapse: "collapse", width: "100%", fontSize: 14 }}
        >
          <thead>
            <tr style={{ background: "#eee" }}>
              {columnKeys.map((key) => (
                <th key={key} style={cellStyle}>
                  {key}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {extract.rows.map((row, idx) => (
              <tr key={idx}>
                {columnKeys.map((key) => (
                  <td key={key} style={cellStyle}>
                    {row[key] ?? ""}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        <p style={{ marginTop: 8, fontSize: 12, color: "#999" }}>
          注:列名/首行为 spike 提取原样 (原表两层表头被展平);仅展示,不派生
          指标、不评分、不排名。表内空白与「…」为源表原样保留,未补造。
        </p>
      </section>

      <hr style={{ margin: "32px 0", border: 0, borderTop: "1px solid #ccc" }} />

      <section className="public-extracts-page__live-candidate">
        <h2>
          Live 候选提取 — NBS 2026-08-21 文章 (drift)
          <DemoBadge
            lineage={{
              is_demo: live.is_demo,
              demo_reason: live.demo_reason,
            }}
          />
        </h2>
        <p style={{ color: "#856404", fontWeight: 600 }}>
          标注:LIVE_CANDIDATE — live deeplink 文章经 WORM 归档后结构化提取;
          SHA 对 registry 锚定为 drift(rc=4 候选,等用户裁定)。
          非 O1 收口数据;与上方 REGISTRY_SAMPLE 分轨互不覆盖。
        </p>

        <table
          style={{ borderCollapse: "collapse", width: "100%", fontSize: 14 }}
        >
          <tbody>
            <tr>
              <th style={cellStyle}>domain</th>
              <td style={cellStyle}>
                <code>{live.domain}</code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>category</th>
              <td style={cellStyle}>
                <code>{live.category}</code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>intake_status</th>
              <td style={cellStyle}>
                <code>{live.intake_status}</code>(is_demo={live.is_demo})
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>source_deeplink_url</th>
              <td style={cellStyle}>
                <code style={{ fontSize: 11, wordBreak: "break-all" }}>
                  {live.source_deeplink_url}
                </code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>source_archive_path (WORM)</th>
              <td style={cellStyle}>
                <code>{live.source_archive_path}</code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>source_sha256 (drift)</th>
              <td style={cellStyle}>
                <code style={{ fontSize: 11, wordBreak: "break-all" }}>
                  {live.source_sha256}
                </code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>row_count</th>
              <td style={cellStyle}>{live.row_count}</td>
            </tr>
            <tr>
              <th style={cellStyle}>extracted_at</th>
              <td style={cellStyle}>{live.extracted_at}</td>
            </tr>
          </tbody>
        </table>

        <h3 style={{ marginTop: 24 }}>候选提取表 ({live.rows.length} 行,全量)</h3>
        <table
          style={{ borderCollapse: "collapse", width: "100%", fontSize: 14 }}
        >
          <thead>
            <tr style={{ background: "#eee" }}>
              {liveColumnKeys.map((key) => (
                <th key={key} style={cellStyle}>
                  {key}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {live.rows.map((row, idx) => (
              <tr key={idx}>
                {liveColumnKeys.map((key) => (
                  <td key={key} style={cellStyle}>
                    {row[key] ?? ""}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        <p style={{ marginTop: 8, fontSize: 12, color: "#999" }}>
          注:live drift 候选按提取原样展示 (2026年8月中旬流通领域重要生产
          资料市场价格变动情况);仅展示,不派生指标、不评分、不排名。registry
          sample 锚定 (dea13b8a…) 未被本候选改动。
        </p>
      </section>

      <hr style={{ margin: "32px 0", border: 0, borderTop: "1px solid #ccc" }} />

      <section className="public-extracts-page__sz-registry-sample">
        <h2>
          深圳公报样本提取 — MUNICIPAL_BULLETIN (REGISTRY_SAMPLE)
          <DemoBadge
            lineage={{
              is_demo: "true",
              demo_reason:
                "REGISTRY_SAMPLE — sz.gov.cn 公报本地样本散文段落提取 " +
                "(--from-local-sample; 2026-08-26 live SSL 暂缓); 非 live O1",
            }}
          />
        </h2>
        <p style={{ color: "#856404", fontWeight: 600 }}>
          标注:REGISTRY_SAMPLE / demo — 深圳公报正文为散文形式 (数据表以
          图片嵌入),本表为公告段落的散文抽取,每行一个真实内容段落。
          非 live 数据 (SSL 暂缓,未做过 live 探测);与上方 NBS 两轨分轨互不覆盖。
        </p>

        <table
          style={{ borderCollapse: "collapse", width: "100%", fontSize: 14 }}
        >
          <tbody>
            <tr>
              <th style={cellStyle}>domain</th>
              <td style={cellStyle}>
                <code>{sz.domain}</code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>category</th>
              <td style={cellStyle}>
                <code>{sz.category}</code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>intake_status</th>
              <td style={cellStyle}>
                <code>REGISTRY_SAMPLE_INTAKED</code>(is_demo=true)
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>source_sample_path</th>
              <td style={cellStyle}>
                <code>{sz.source_sample_path}</code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>source_archive_path (WORM)</th>
              <td style={cellStyle}>
                <code>{sz.source_archive_path}</code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>source_sha256</th>
              <td style={cellStyle}>
                <code style={{ fontSize: 11, wordBreak: "break-all" }}>
                  {sz.source_sha256}
                </code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>row_count</th>
              <td style={cellStyle}>{sz.row_count}</td>
            </tr>
            <tr>
              <th style={cellStyle}>extracted_at</th>
              <td style={cellStyle}>{sz.extracted_at}</td>
            </tr>
          </tbody>
        </table>

        <h3 style={{ marginTop: 24 }}>散文段落表 ({sz.rows.length} 行,全量)</h3>
        <table
          style={{ borderCollapse: "collapse", width: "100%", fontSize: 14 }}
        >
          <thead>
            <tr style={{ background: "#eee" }}>
              {szColumnKeys.map((key) => (
                <th key={key} style={cellStyle}>
                  {key}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sz.rows.map((row, idx) => (
              <tr key={idx}>
                {szColumnKeys.map((key) => (
                  <td key={key} style={cellStyle}>
                    {row[key] ?? ""}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        <p style={{ marginTop: 8, fontSize: 12, color: "#999" }}>
          注:section 为公告中文序号节标 (一、综合 … 十二、城市环境和应急
          管理),paragraph 为原样段落文本;仅展示,不派生指标、不评分、不排名。
          深圳 HTTPS live 探测仍暂缓 (SSL BAD_ecPOINT,per registry 备注),
          本表不构成 live 收口。
        </p>
      </section>
    </main>
  );
}
