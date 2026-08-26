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
// Per tasking 376 §SCHEMA (湖北 REGISTRY_SAMPLE 分节): 同页第四区块展示
// tjj.hubei.gov.cn PROVINCIAL_BULLETIN xlsx 提取 (21 行, live enabled=FALSE
// 暂缓, frontend/lib/public_extract_hubei.json) — 显式 REGISTRY_SAMPLE /
// demo / xlsx 提取 / live FALSE 暂缓非 O1; 不覆盖 NBS+深圳三轨.
// Per tasking 382 §SCHEMA (四轨一览条): 页首增四轨 summary (非 card 堆砌);
// 读自既有 4 fixture (NBS sample/live + 深圳 + 湖北), 不重算; 锚点链到各
// 分节 section; 四轨皆 demo/candidate 演示, 非 O1/Gate PASS.
// Per tasking 388 §SCHEMA (JSON 静态下载): 4 fixture 字节一致拷到
// frontend/public/public-extracts/{nbs,nbs-live-candidate,sz,hubei}.json
// (download attr); 一览表增「下载 JSON」列 (8 列) → /public-extracts/*.json.
// 静态路由: 无 params.*, 无 force-dynamic (纯 fixture 消费).

import type { ReactElement } from "react";
import DemoBadge from "../DemoBadge";
import fixture from "../../lib/public_extract_nbs.json";
import liveCandidateFixture from "../../lib/public_extract_nbs_live_candidate.json";
import szFixture from "../../lib/public_extract_sz.json";
import hbFixture from "../../lib/public_extract_hubei.json";

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
const hb = hbFixture as PublicExtractFixture;

// 列序 = 首行键序 (spike 提取保序); 不重排、不重命名、不 reinterpret.
const columnKeys: string[] =
  extract.rows.length > 0 ? Object.keys(extract.rows[0]) : [];
const liveColumnKeys: string[] =
  live.rows.length > 0 ? Object.keys(live.rows[0]) : [];
const szColumnKeys: string[] =
  sz.rows.length > 0 ? Object.keys(sz.rows[0]) : [];
const hbColumnKeys: string[] =
  hb.rows.length > 0 ? Object.keys(hb.rows[0]) : [];

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

      <section
        className="public-extracts-page__overview-strip"
        id="overview"
      >
        <h2>四轨一览 (overview) — 4 个 REGISTRY_SAMPLE / LIVE_CANDIDATE demo 演示</h2>
        <table
          style={{
            borderCollapse: "collapse",
            width: "100%",
            fontSize: 14,
          }}
        >
          <thead>
            <tr style={{ background: "#eee" }}>
              <th style={cellStyle}>轨</th>
              <th style={cellStyle}>domain</th>
              <th style={cellStyle}>category</th>
              <th style={cellStyle}>行数</th>
              <th style={cellStyle}>SHA 前 8</th>
              <th style={cellStyle}>demo|candidate 标注</th>
              <th style={cellStyle}>分节锚点</th>
              <th style={cellStyle}>下载 JSON</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={cellStyle}>NBS sample</td>
              <td style={cellStyle}>
                <code>{extract.domain}</code>
              </td>
              <td style={cellStyle}>
                <code>{extract.category}</code>
              </td>
              <td style={cellStyle}>{extract.row_count}</td>
              <td style={cellStyle}>
                <code>{extract.source_sha256.slice(0, 8)}</code>
              </td>
              <td style={cellStyle}>
                demo (REGISTRY_SAMPLE_INTAKED)
              </td>
              <td style={cellStyle}>
                <a href="#track-nbs-sample">↓ NBS sample 分节</a>
              </td>
              <td style={cellStyle}>
                <a
                  href="/public-extracts/nbs.json"
                  download="public-extracts-nbs.json"
                >
                  ⬇ nbs.json
                </a>
              </td>
            </tr>
            <tr>
              <td style={cellStyle}>NBS live 候选</td>
              <td style={cellStyle}>
                <code>{live.domain}</code>
              </td>
              <td style={cellStyle}>
                <code>{live.category}</code>
              </td>
              <td style={cellStyle}>{live.row_count}</td>
              <td style={cellStyle}>
                <code>{live.source_sha256.slice(0, 8)}</code>
              </td>
              <td style={cellStyle}>
                candidate (LIVE_CANDIDATE, drift)
              </td>
              <td style={cellStyle}>
                <a href="#track-nbs-live">↓ NBS live 候选分节</a>
              </td>
              <td style={cellStyle}>
                <a
                  href="/public-extracts/nbs-live-candidate.json"
                  download="public-extracts-nbs-live-candidate.json"
                >
                  ⬇ nbs-live-candidate.json
                </a>
              </td>
            </tr>
            <tr>
              <td style={cellStyle}>深圳 sample</td>
              <td style={cellStyle}>
                <code>{sz.domain}</code>
              </td>
              <td style={cellStyle}>
                <code>{sz.category}</code>
              </td>
              <td style={cellStyle}>{sz.row_count}</td>
              <td style={cellStyle}>
                <code>{sz.source_sha256.slice(0, 8)}</code>
              </td>
              <td style={cellStyle}>
                demo (REGISTRY_SAMPLE_INTAKED, 散文)
              </td>
              <td style={cellStyle}>
                <a href="#track-sz">↓ 深圳分节</a>
              </td>
              <td style={cellStyle}>
                <a
                  href="/public-extracts/sz.json"
                  download="public-extracts-sz.json"
                >
                  ⬇ sz.json
                </a>
              </td>
            </tr>
            <tr>
              <td style={cellStyle}>湖北 sample</td>
              <td style={cellStyle}>
                <code>{hb.domain}</code>
              </td>
              <td style={cellStyle}>
                <code>{hb.category}</code>
              </td>
              <td style={cellStyle}>{hb.row_count}</td>
              <td style={cellStyle}>
                <code>{hb.source_sha256.slice(0, 8)}</code>
              </td>
              <td style={cellStyle}>
                demo (REGISTRY_SAMPLE_INTAKED, xlsx)
              </td>
              <td style={cellStyle}>
                <a href="#track-hb">↓ 湖北分节</a>
              </td>
              <td style={cellStyle}>
                <a
                  href="/public-extracts/hubei.json"
                  download="public-extracts-hubei.json"
                >
                  ⬇ hubei.json
                </a>
              </td>
            </tr>
          </tbody>
        </table>
        <p
          style={{
            marginTop: 8,
            fontSize: 12,
            color: "#999",
          }}
        >
          注:四轨皆 demo/candidate 演示 (NBS sample REGISTRY_SAMPLE / NBS live
          候选 LIVE_CANDIDATE drift / 深圳 REGISTRY_SAMPLE 散文 / 湖北 REGISTRY_SAMPLE
          xlsx); 数据只读自既有 4 fixture, 不重算; live 探测均暂缓 (NBS live
          drift 待 user 裁定; 深圳 HTTPS SSL BAD_ecPOINT; 湖北 enabled=FALSE);
          非 O1 收口, 非 Gate PASS (per docs/45 §1 + §6.2 + §7 不变量链 690)。
        </p>
      </section>

      <section className="public-extracts-page__provenance" id="track-nbs-sample">
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

      <section className="public-extracts-page__live-candidate" id="track-nbs-live">
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

      <section className="public-extracts-page__sz-registry-sample" id="track-sz">
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

      <hr style={{ margin: "32px 0", border: 0, borderTop: "1px solid #ccc" }} />

      <section className="public-extracts-page__hb-registry-sample" id="track-hb">
        <h2>
          湖北月报样本提取 — PROVINCIAL_BULLETIN (REGISTRY_SAMPLE, xlsx)
          <DemoBadge
            lineage={{
              is_demo: "true",
              demo_reason:
                "REGISTRY_SAMPLE — tjj.hubei.gov.cn 月度统计 xlsx 本地样本提取 " +
                "(--from-local-sample --allow-disabled-local-sample; live enabled=FALSE 暂缓); " +
                "非 live O1",
            }}
          />
        </h2>
        <p style={{ color: "#856404", fontWeight: 600 }}>
          标注:REGISTRY_SAMPLE / demo — 湖北统计局月报为 xlsx 直链样本,经
          connector extract_xlsx_tables 提取; live 探测暂缓 (enabled=FALSE,
          JS-shell / 341 技术暂缓),本表不构成 live 收口; 与上方 NBS sample/live
          + 深圳 sample 三轨分轨互不覆盖。
        </p>

        <table
          style={{ borderCollapse: "collapse", width: "100%", fontSize: 14 }}
        >
          <tbody>
            <tr>
              <th style={cellStyle}>domain</th>
              <td style={cellStyle}>
                <code>{hb.domain}</code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>category</th>
              <td style={cellStyle}>
                <code>{hb.category}</code>
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
                <code>{hb.source_sample_path}</code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>source_archive_path (WORM)</th>
              <td style={cellStyle}>
                <code>{hb.source_archive_path}</code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>source_sha256</th>
              <td style={cellStyle}>
                <code style={{ fontSize: 11, wordBreak: "break-all" }}>
                  {hb.source_sha256}
                </code>
              </td>
            </tr>
            <tr>
              <th style={cellStyle}>row_count</th>
              <td style={cellStyle}>{hb.row_count}</td>
            </tr>
            <tr>
              <th style={cellStyle}>extracted_at</th>
              <td style={cellStyle}>{hb.extracted_at}</td>
            </tr>
          </tbody>
        </table>

        <h3 style={{ marginTop: 24 }}>
          月报统计表 ({hb.rows.length} 行,全量)
        </h3>
        <table
          style={{ borderCollapse: "collapse", width: "100%", fontSize: 14 }}
        >
          <thead>
            <tr style={{ background: "#eee" }}>
              {hbColumnKeys.map((key) => (
                <th key={key} style={cellStyle}>
                  {key || <span style={{ color: "#aaa" }}>(未命名)</span>}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {hb.rows.map((row, idx) => (
              <tr key={idx}>
                {hbColumnKeys.map((key) => (
                  <td key={key} style={cellStyle}>
                    {row[key] ?? ""}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        <p style={{ marginTop: 8, fontSize: 12, color: "#999" }}>
          注:列名/首行为 xlsx 提取原样 (含空列名 + 前导空格);
          仅展示,不派生指标、不评分、不排名。湖北 live 仍暂缓
          (enabled=FALSE, JS-shell tech-blocked; per Cursor 341),
          本表不构成 live 收口。
        </p>
      </section>
    </main>
  );
}
