// frontend/app/indicators/page.tsx — 662 D2 指标定义页.
//
// Per 662 tasking §1.662-D2: PRD §5.2 暴露 + PRD §3.2 来源等级 +
// PRD §7.2 数据完整度切片 (五指标 × 来源等级三档分布).
//
// 数据流 (禁手填 + 禁编造 caliber per 红线 8):
//   mart JSON
//     ↓ export-mart-data.py (架构师端)
//   frontend/data/mart_indicator_definitions_2024.json
//     ↓ getIndicatorDefinitions()  (build-time fs read, server component)
//   渲染 5 张指标卡 (key/label/unit/caliber/period) + 来源等级三档条形
//
// 退化处理: 指标定义文件缺失 → 显示"未配置"占位 (graceful degradation,
// 不 throw, 不冒充数据). per loadStaticIndicatorDefinitions() 三态语义.
//
// 红线:
//   - 多指标数据只准来自库/mart 导出 (禁手填)
//   - 禁编造 caliber (缺字段时显式 "(口径待补, 见 lineage_ruling)")
//   - demo 壳禁冒充真数据 (本页不是 demo, 是真实 PRD §5.2 暴露, LIVE 模式)

import type { ReactElement } from "react";
import { getIndicatorDefinitions } from "../../lib/mart-static";
import type { MartIndicatorDefinition } from "../../lib/mart-static";

export const metadata = {
  title: "指标定义 · 5 指标 × 来源等级",
};

export default function IndicatorsPage(): ReactElement {
  const data = getIndicatorDefinitions();

  // 三态: 缺失 → 空态 (graceful degradation, 不冒充)
  if (!data || data.indicators.length === 0) {
    return (
      <main className="indicators-page">
        <header className="indicators-page__header">
          <h1 data-testid="indicators-h">5 指标定义</h1>
        </header>
        <div
          data-testid="indicators-empty-state"
          style={{
            padding: 16,
            marginTop: 16,
            border: "1px dashed #ccc",
            borderRadius: 4,
            background: "#fafafa",
            color: "#666",
            fontSize: 13,
          }}
        >
          ⚠ 指标定义 JSON 未配置。请确认:
          <ol style={{ marginTop: 8, paddingLeft: 20 }}>
            <li>
              已运行 <code>python3 deploy/static-export/export-mart-data.py</code>
              </li>
            <li>
              <code>frontend/data/mart_indicator_definitions_2024.json</code> 已生成
            </li>
            <li>
              <code>NEXT_PUBLIC_MART_DATA_PATH</code> env 已注入 (指向 mart 主 JSON 同目录)
            </li>
          </ol>
        </div>
        <p style={{ marginTop: 24 }}>
          <a href="/">← 返回首页</a>
        </p>
      </main>
    );
  }

  return (
    <main className="indicators-page">
      <header className="indicators-page__header">
        <h1 data-testid="indicators-h">5 指标定义 · 来源等级分布</h1>
        <p style={{ color: "#666", fontSize: 13, marginTop: 8 }}>
          数据来源：<code>{data.mart_source}</code>
          {" · "}
          生成时间：<code>{data.as_of}</code>
          {" · "}
          裁定：<code>{data.lineage_ruling}</code>
        </p>
        <p style={{ color: "#666", fontSize: 13, marginTop: 4 }}>
          本页展示 5 个 GDP 指标的口径与来源等级分布; 全部数据来自
          mart 静态导出 (<code>{data.mart_source}</code>), 禁手填 + 禁编造 caliber。
          来源等级三档: <strong>OFFICIAL_INTAKED</strong> (统计局原文入库)
          · <strong>HONGHEIKU_TRANSLOAD</strong> (hongheiku 转录)
          · <strong>DATA_MISSING</strong> (本源缺文)。
        </p>
      </header>

      <section
        data-testid="indicator-cards"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))",
          gap: 16,
          marginTop: 24,
        }}
      >
        {data.indicators.map((ind) => (
          <IndicatorCard key={ind.key} ind={ind} />
        ))}
      </section>

      <section
        data-testid="national-anchor-section"
        style={{
          marginTop: 32,
          padding: 16,
          border: "1px solid #ddd",
          borderRadius: 4,
          background: "#e6f4ff",
        }}
      >
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>
          国家锚口径
        </h2>
        <p style={{ fontSize: 13, color: "#444", lineHeight: 1.6 }}>
          首页 <code>/</code> 表格顶部置首的 <strong>OFFICIAL_ANCHOR</strong> 行
          (全国 2024 GDP = <code>1,349,084.0</code> 亿元) 来自国家统计局
          《2024 年国民经济和社会发展统计公报》, 由架构师端源源自取入库
          (<code>lineage_source = OFFICIAL_INTAKED</code>, <code>lineage_origin = 国家统计局</code>)。
          该行作为全国锚值用于 31 省数据完整度核对 (per docs/81 §3 国家锚核对)。
        </p>
        <p style={{ fontSize: 12, color: "#666", marginTop: 8 }}>
          注: 国家锚仅含 <code>gdp_total</code> 字段;
          全国增速/一产/二产/三产暂留 <code>null</code>, 待 662+ 单独入库。
        </p>
      </section>

      <p style={{ marginTop: 24 }}>
        <a href="/">← 返回首页</a>
      </p>
    </main>
  );
}

/** 662 D2: 单指标卡 — key/label/unit/caliber/period + 来源等级三档条形. */
function IndicatorCard({ ind }: { ind: MartIndicatorDefinition }): ReactElement {
  const g = ind.source_grade_distribution;
  const total = g.OFFICIAL_INTAKED + g.HONGHEIKU_TRANSLOAD + g.DATA_MISSING;

  // CSS-only 条形 (不用 chart lib), 宽度按总数归一化.
  const pct = (n: number) => (total > 0 ? (n / total) * 100 : 0);

  return (
    <article
      data-testid={`indicator-card-${ind.key}`}
      style={{
        border: "1px solid #ddd",
        borderRadius: 4,
        padding: 14,
        background: "#fff",
      }}
    >
      <header style={{ marginBottom: 10 }}>
        <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 2 }}>
          {ind.label}{" "}
          <span
            style={{
              fontSize: 11,
              color: "#888",
              fontWeight: 400,
              fontFamily: "monospace",
            }}
          >
            ({ind.key})
          </span>
        </h3>
        <p
          style={{
            fontSize: 12,
            color: "#666",
            fontFamily: "monospace",
            marginBottom: 4,
          }}
        >
          单位：{ind.unit} · 周期：{ind.period}
        </p>
        <p style={{ fontSize: 12, color: "#444", lineHeight: 1.5 }}>
          口径：{ind.caliber}
        </p>
      </header>

      <div data-testid={`grade-bars-${ind.key}`}>
        <p
          style={{
            fontSize: 11,
            fontWeight: 700,
            color: "#444",
            marginBottom: 6,
          }}
        >
          来源等级分布（{total} 地区）
        </p>

        {/* OFFICIAL_INTAKED 条 */}
        <div
          style={gradeRowStyle}
          data-testid={`grade-bar-official-${ind.key}`}
        >
          <span style={gradeLabelStyle}>OFFICIAL_INTAKED</span>
          <span style={gradeCountStyle}>{g.OFFICIAL_INTAKED}</span>
          <div style={gradeBarOuterStyle}>
            <div
              style={{
                ...gradeBarInnerStyle,
                width: `${pct(g.OFFICIAL_INTAKED)}%`,
                background: "#1a7f37",
              }}
            />
          </div>
        </div>

        {/* HONGHEIKU_TRANSLOAD 条 */}
        <div
          style={gradeRowStyle}
          data-testid={`grade-bar-transload-${ind.key}`}
        >
          <span style={gradeLabelStyle}>HONGHEIKU_TRANSLOAD</span>
          <span style={gradeCountStyle}>{g.HONGHEIKU_TRANSLOAD}</span>
          <div style={gradeBarOuterStyle}>
            <div
              style={{
                ...gradeBarInnerStyle,
                width: `${pct(g.HONGHEIKU_TRANSLOAD)}%`,
                background: "#0969da",
              }}
            />
          </div>
        </div>

        {/* DATA_MISSING 条 */}
        <div
          style={gradeRowStyle}
          data-testid={`grade-bar-missing-${ind.key}`}
        >
          <span style={gradeLabelStyle}>DATA_MISSING</span>
          <span style={gradeCountStyle}>{g.DATA_MISSING}</span>
          <div style={gradeBarOuterStyle}>
            <div
              style={{
                ...gradeBarInnerStyle,
                width: `${pct(g.DATA_MISSING)}%`,
                background: "#b45309",
              }}
            />
          </div>
        </div>
      </div>
    </article>
  );
}

const gradeRowStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 8,
  marginBottom: 6,
  fontSize: 11,
};

const gradeLabelStyle: React.CSSProperties = {
  minWidth: 150,
  fontFamily: "monospace",
  color: "#444",
};

const gradeCountStyle: React.CSSProperties = {
  minWidth: 28,
  textAlign: "right",
  fontWeight: 700,
  fontFamily: "monospace",
  color: "#222",
};

const gradeBarOuterStyle: React.CSSProperties = {
  flex: 1,
  height: 10,
  background: "#f0f0f0",
  borderRadius: 2,
  overflow: "hidden",
};

const gradeBarInnerStyle: React.CSSProperties = {
  height: "100%",
  transition: "width 0.2s",
};
