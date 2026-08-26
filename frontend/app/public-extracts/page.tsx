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
// 静态路由: 无 params.*, 无 force-dynamic (纯 fixture 消费).

import type { ReactElement } from "react";
import DemoBadge from "../DemoBadge";
import fixture from "../../lib/public_extract_nbs.json";

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

const extract = fixture as PublicExtractFixture;

// 列序 = 首行键序 (spike 提取保序); 不重排、不重命名、不 reinterpret.
const columnKeys: string[] =
  extract.rows.length > 0 ? Object.keys(extract.rows[0]) : [];

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
          (O1) 尚未宣布,live 探测仍为 JS 壳 tech-blocked (rc=7)。
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
    </main>
  );
}
