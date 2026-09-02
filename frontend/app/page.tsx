// Stage 2 / S2.0.1 + S2.7-a + S2.7-b + S2.8-lite + S2.9-lite — Home page.
//
// Lists indicators (real data by default, mock via NEXT_PUBLIC_USE_MOCK=true).
// Per knife 659 tasking §1.659-A: USE_MOCK 默认 false 真数据。
// Per knife 660 tasking §PART 2 (Track B 静态导出): 当 NEXT_PUBLIC_MART_DATA_PATH
//   被设置,从 frontend/data/mart_province_gdp_2024.json 读 28 省 + 3 缺失 数据,
//   渲染新 section "省 GDP 2024 真实数据";此时不需要 FastAPI backend。
// S2.7-a 增量:附 5 省列表入口 (per tasking 168 §NOW-2 「≥1 省路由壳或列表入口」)。
// S2.7-b-lite / S2.7-b-full-lite 增量:附 10 地市列表入口
// (per tasking 274 §NOW「首页十城导航入口」+ docs/46 §2)。
// S2.8-lite / S2.9-lite 增量:附七维度 + 同类对比入口
// (per tasking 277 §NOW「首页七维/对比导航入口」)。
// 列表本身仅为导航入口;不评分、不对比、不排名。

import { listIndicators, IS_MOCK_MODE, IS_MART_FIXTURE_MODE, IS_STATIC_MART_DATA_MODE } from "../lib/api";
import { CITY_SLUG_MAP, CITY_SLUG_LIST } from "../lib/city_slug_map";
import { getMartProvinceGdp2024 } from "../lib/mart-static";
// MOCK_PROVINCE_LIST retained (S1.18 历史资产 + 回退通道 per 659 tasking §1.659-A; 默认渲染已移除)

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const data = await listIndicators();
  // Track B (knife 660): read 28+3 province GDP from static JSON (when env set).
  // When env not set (e.g. local dev without NEXT_PUBLIC_MART_DATA_PATH), returns null
  // and the section is hidden — page still renders with existing Indicator inventory.
  const mart = getMartProvinceGdp2024();
  const cityModeLabel = IS_MART_FIXTURE_MODE
    ? "mart-shape demo（is_demo=true；非 O1）"
    : "mock（S2.7-b-lite；设 NEXT_PUBLIC_USE_MART_FIXTURE=1 切 mart）";
  return (
    <section>
      <h1>CEGR — 官方公开数据 · 结构化呈现（demo）</h1>
      <p style={{ color: "#666" }}>
        主入口：
        <a href="/public-extracts">/public-extracts</a>
        （四轨：NBS sample / NBS live 候选 / 深圳 / 湖北；可下载 JSON）。
        下方仍为 Stage 2 治理观察导航壳（省/市/七维）。皆 demo，
        <strong>非 O1 / 非 Gate PASS</strong>。
        {IS_MART_FIXTURE_MODE
          ? " Mart demo 管道已开：地市 /cities/{slug} 走 mart-shape（含演示人物）；"
          : IS_MOCK_MODE
            ? " Mock 模式：以下 indicator 为 S1.18 DEMO sentinel，"
            : " Live 模式：以下数据来自 FastAPI S1.10，"}
        {IS_MOCK_MODE && IS_MART_FIXTURE_MODE
          ? "首页 indicator 表仍为 mock（无后端时）。"
          : null}
        请同时关注页面顶部 <code>mode-banner</code>。
      </p>

      <p style={{ marginTop: 12 }}>
        <a href="/research/m1-series">/research/m1-series</a>
        {" "}— M1 验收面（湖北 2026 H1 GDP，1 行真 observation；非 31 省；非 Gate PASS）。
      </p>

      {mart && (
        <>
          <h2 style={{ marginTop: 32 }} data-testid="province-gdp-2024-heading">
            省 GDP 2024 真实数据（knife 659 mart + 660 静态导出）
          </h2>
          <p style={{ color: "#1a7f37", fontSize: 13 }}>
            ✅ 28 省 2024 真实数据（5 官方 + 23 转载锚定，per mart
            lineage_source）；3 省「数据暂缺（公报源缺文）」显式标记；
            lineage_ruling=<code>U6 2026-09-02</code>，lineage_is_demo=<code>false</code>。
            数据走 <code>NEXT_PUBLIC_MART_DATA_PATH</code>
            静态嵌入（newvps 上不需要 FastAPI backend）。
            {" "}
            <span data-testid="mart-row-count">
              渲染 {mart.total_count} 行（{mart.real_count} 真实 + {mart.missing_count} 缺失）
            </span>
            。
          </p>
          <table
            data-testid="province-gdp-2024-table"
            style={{
              borderCollapse: "collapse",
              width: "100%",
              fontSize: 13,
            }}
          >
            <thead>
              <tr style={{ background: "#eee" }}>
                <th style={cellStyle}>省份</th>
                <th style={cellStyle}>代码</th>
                <th style={cellStyle}>GDP（亿元）</th>
                <th style={cellStyle}>同比 (%)</th>
                <th style={cellStyle}>一产</th>
                <th style={cellStyle}>二产</th>
                <th style={cellStyle}>三产</th>
                <th style={cellStyle}>状态</th>
                <th style={cellStyle}>lineage source</th>
              </tr>
            </thead>
            <tbody>
              {mart.provinces.map((p) => {
                const isMissing = p.status === "DATA_MISSING";
                return (
                  <tr
                    key={p.province_code}
                    data-testid={`province-row-${p.province_code}`}
                    data-missing={isMissing ? "1" : "0"}
                    style={isMissing ? { background: "#fff8e1" } : undefined}
                  >
                    <td style={cellStyle}>{p.province_name}</td>
                    <td style={cellStyle}>
                      <code>{p.province_code}</code>
                    </td>
                    <td style={cellStyle}>{fmtNum(p.gdp_total)}</td>
                    <td style={cellStyle}>{fmtPct(p.gdp_growth)}</td>
                    <td style={cellStyle}>{fmtNum(p.primary_gdp)}</td>
                    <td style={cellStyle}>{fmtNum(p.secondary_gdp)}</td>
                    <td style={cellStyle}>{fmtNum(p.tertiary_gdp)}</td>
                    <td style={cellStyle}>
                      {isMissing ? (
                        <span
                          data-testid={`missing-badge-${p.province_code}`}
                          style={{ color: "#b45309", fontWeight: 600 }}
                          title={p.missing_reason ?? "数据暂缺"}
                        >
                          数据暂缺（公报源缺文）
                        </span>
                      ) : (
                        <span style={{ color: "#666" }}>正常</span>
                      )}
                    </td>
                    <td style={cellStyle}>
                      <code style={{ fontSize: 11 }}>{p.lineage_source}</code>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <p style={{ marginTop: 8, fontSize: 12, color: "#666" }}>
            数据来源: <code>{mart.mart_source}</code> · 导出于 {mart.as_of}。
            红线: 3 缺失省 5 个 metric 列全为 NULL(禁补零)。
          </p>
        </>
      )}

      <h2>Indicator inventory</h2>
      <table
        style={{
          borderCollapse: "collapse",
          width: "100%",
          fontSize: 14,
        }}
      >
        <thead>
          <tr style={{ background: "#eee" }}>
            <th style={cellStyle}>indicator_id</th>
            <th style={cellStyle}>geo_count</th>
            <th style={cellStyle}>obs_count</th>
            <th style={cellStyle}>latest_period</th>
          </tr>
        </thead>
        <tbody>
          {data.indicators.map((it) => (
            <tr key={it.indicator_id}>
              <td style={cellStyle}>
                <code>{it.indicator_id}</code>
              </td>
              <td style={cellStyle}>{it.geo_entity_count}</td>
              <td style={cellStyle}>{it.observation_count}</td>
              <td style={cellStyle}>{it.latest_period_start ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 style={{ marginTop: 32 }}>省级观察入口（S2.7-a 列表）</h2>
      <p style={{ color: "#666", fontSize: 13 }}>
        {IS_MOCK_MODE
          ? "Mock 模式：省列表来自 S1.18 DEMO sentinel（设 NEXT_PUBLIC_USE_MOCK=true 触发）。"
          : "真数据模式：省 GDP 数据来自 mart_province_gdp_2024（28 省 2024 真实数据 + 3 省数据暂缺）。"
        }
        {" "}省 GDP 区块走真数据 API + mart（per knife 659 tasking §1.659-A）。
      </p>
      <p style={{ fontSize: 13, color: "#555" }}>
        {" "}省 GDP 数据走 <code>/api/indicator</code>（FastAPI mart视图），3 缺失省显示「数据暂缺（公报源缺文）」状态。
        {" "}省详情页：<code>/provinces/[省代码]</code>。
      </p>

      <h2 style={{ marginTop: 32 }}>地市观察入口（S2.7-b-lite / S2.7-b-full-lite 列表）</h2>
      <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 14 }}>
        <thead>
          <tr style={{ background: "#eee" }}>
            <th style={cellStyle}>地市</th>
            <th style={cellStyle}>归属省份</th>
            <th style={cellStyle}>路由</th>
            <th style={cellStyle}>数据模式</th>
          </tr>
        </thead>
        <tbody>
          {CITY_SLUG_LIST.map((slug) => {
            const entry = CITY_SLUG_MAP[slug];
            return (
              <tr key={slug}>
                <td style={cellStyle}>{entry.nameZh}</td>
                <td style={cellStyle}>{entry.provinceSlug}</td>
                <td style={cellStyle}>
                  <a href={`/cities/${entry.slug}`}>/cities/{entry.slug}</a>
                </td>
                <td style={cellStyle}>{cityModeLabel}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p style={{ marginTop: 24, fontSize: 12, color: "#999" }}>
        注：本列表仅作导航入口；不做评分、不做对比、不排名。
      </p>

      <h2 style={{ marginTop: 32 }}>横向视角入口（S2.8-lite / S2.9-lite）</h2>
      <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 14 }}>
        <thead>
          <tr style={{ background: "#eee" }}>
            <th style={cellStyle}>入口</th>
            <th style={cellStyle}>路由</th>
            <th style={cellStyle}>演示范围</th>
            <th style={cellStyle}>数据模式</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style={cellStyle}>七维度观察卡</td>
            <td style={cellStyle}>
              <a href="/seven-dim">/seven-dim</a>
            </td>
            <td style={cellStyle}>
              1 区域 × 7 cell（POLICY_DELIVERY / FISCAL_EXECUTION / PROJECT_DELIVERY /
              ECONOMIC_ADAPTATION / PUBLIC_SERVICES / RISK_MANAGEMENT / GOAL_CONSISTENCY）
            </td>
            <td style={cellStyle}>mock（S2.8-lite）</td>
          </tr>
          <tr>
            <td style={cellStyle}>同类地区对比</td>
            <td style={cellStyle}>
              <a href="/peer-compare">/peer-compare</a>
            </td>
            <td style={cellStyle}>
              1 group × 4 members（focal 江苏 + peer 浙江 / 广东 / 山东；4 维度匹配依据）
            </td>
            <td style={cellStyle}>mock（S2.9-lite）</td>
          </tr>
          <tr>
            <td style={cellStyle}>公开提取 NBS sample 轨（demo）</td>
            <td style={cellStyle}>
              <a
                href="/public-extracts#track-nbs-sample"
                data-testid="home-public-extracts-nbs-sample"
              >
                /public-extracts#track-nbs-sample
              </a>
            </td>
            <td style={cellStyle}>
              stats.gov.cn / NATIONAL_BULLETIN 63 行（registry 本地样本
              --from-local-sample 结构化提取；per 回执 `350`）
            </td>
            <td style={cellStyle}>
              REGISTRY_SAMPLE · demo · 非 live O1
            </td>
          </tr>
          <tr>
            <td style={cellStyle}>公开提取 NBS live 候选轨（candidate demo）</td>
            <td style={cellStyle}>
              <a
                href="/public-extracts#track-nbs-live"
                data-testid="home-public-extracts-nbs-live"
              >
                /public-extracts#track-nbs-live
              </a>
            </td>
            <td style={cellStyle}>
              stats.gov.cn / NATIONAL_BULLETIN 60 行（WORM `zxfb`
              LIVE_CANDIDATE 提取；drift 候选；per 回执 `359` / `362`）
            </td>
            <td style={cellStyle}>
              LIVE_CANDIDATE · drift 候选 · 非 O1 收口
            </td>
          </tr>
          <tr>
            <td style={cellStyle}>公开提取湖北轨（xlsx demo）</td>
            <td style={cellStyle}>
              <a href="/public-extracts#track-hb">/public-extracts#track-hb</a>
            </td>
            <td style={cellStyle}>
              tjj.hubei.gov.cn / PROVINCIAL_BULLETIN 21 行 xlsx 月报统计
              （--from-local-sample --allow-disabled-local-sample 提取）
            </td>
            <td style={cellStyle}>
              REGISTRY_SAMPLE · xlsx · demo · live <code>enabled=FALSE</code>
              暂缓（非 live O1）
            </td>
          </tr>
          <tr>
            <td style={cellStyle}>公开提取四轨一览（overview strip）</td>
            <td style={cellStyle}>
              <a
                href="/public-extracts#overview"
                data-testid="home-public-extracts-overview"
              >
                /public-extracts#overview
              </a>
            </td>
            <td style={cellStyle}>
              stats.gov.cn / sz.gov.cn / tjj.hubei.gov.cn 7 列 × 4 行
              overview（轨 / domain / category / 行数 / SHA 前 8 / demo\|candidate
              标注 / 分节锚点；数据只读自既有 4 fixture，不重算；per 回执 `383`；
              smoke §12f 门）
            </td>
            <td style={cellStyle}>
              OVERVIEW · 四轨 demo · 非 O1
            </td>
          </tr>
        </tbody>
      </table>
      <p style={{ marginTop: 24, fontSize: 12, color: "#999" }}>
        注：仅展示计数；不评分、不排名、不派生"地区得分"（per docs/06 §6.6 + docs/42 §8 + docs/43 §8）。
      </p>
    </section>
  );
}

const cellStyle: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "6px 10px",
  textAlign: "left",
};

function fmtNum(v: number | null): string {
  if (v === null || v === undefined) return "—";
  if (typeof v !== "number") return "—";
  return v.toLocaleString("zh-CN", { maximumFractionDigits: 2 });
}

function fmtPct(v: number | null): string {
  if (v === null || v === undefined) return "—";
  if (typeof v !== "number") return "—";
  return v.toFixed(1);
}
