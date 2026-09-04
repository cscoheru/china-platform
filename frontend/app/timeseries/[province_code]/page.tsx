// 667 P2 时序可视化 · 单省详情页 `/timeseries/[province_code]`.
//
// Per 667 tasking §2: 31 省 + NATIONAL = 32 slug 时序详情页.
// Per docs/87 §3.2 + 661 P1 切片: 与 `/provinces/{code}` 区别 — 后者只看 2024 切片,
//   时序页看 2001–2026 完整时间序列.
//
// 设计:
//   - Server component 读 mart JSON;按 province_code 预切片 (避免 client 端 8060 row filter).
//   - 32 个合法 slug (per docs/46 §3.1 守门);generateStaticParams 预生成.
//   - DATA_MISSING 3 省 (辽/琼/黔) 仍渲染页面但 explorer 显示全 DATA_MISSING (per 红线-1).
//   - dynamicParams = false (未在清单内一律 404).

import { notFound } from "next/navigation";

import {
  listIndicatorsWithTimeSeries,
  listProvincesWithTimeSeries,
  listSourceGradesByProvince,
  listSourceGradesNational,
} from "../../../lib/api";
import { getProvinceTimeSeriesStatic } from "../../../lib/mart-static";
import { TimeSeriesExplorer } from "../../components/TimeSeriesExplorer";

// 32 个合法 slug: 31 GB/T 2260 代码 + NATIONAL 锚行 (与 /provinces/{code} 清单一致).
const VALID_CODES = [
  "BEIJING", "TIANJIN", "HEBEI", "SHANXI", "NEI_MENGGU",
  "LIAONING", "JILIN", "HEILONGJIANG", "SHANGHAI", "JIANGSU",
  "ZHEJIANG", "ANHUI", "FUJIAN", "JIANGXI", "SHANDONG",
  "HENAN", "HUBEI", "HUNAN", "GUANGDONG", "GUANGXI",
  "HAINAN", "CHONGQING", "SICHUAN", "GUIZHOU", "YUNNAN",
  "XIZANG", "SHAANXI", "GANSU", "QINGHAI", "NINGXIA", "XINJIANG",
  "NATIONAL",
];

export function generateStaticParams(): Array<{ province_code: string }> {
  return VALID_CODES.map((code) => ({ province_code: code.toLowerCase() }));
}

// 404 兜底: slug 命中锁定清单之外的请求一律 notFound (per docs/46 §3.1).
export const dynamicParams = false;

interface PageProps {
  params: { province_code: string };
}

export default function ProvinceTimeSeriesPage({
  params,
}: PageProps): React.ReactElement {
  const code = params.province_code.toUpperCase();
  if (!VALID_CODES.includes(code)) {
    notFound();
  }

  const data = getProvinceTimeSeriesStatic();
  if (!data) {
    return (
      <section>
        <h1 data-testid={`timeseries-province-h1-${code}`}>
          时序可视化 · {code} · 数据未配置
        </h1>
        <p style={{ color: "#b45309" }} data-testid="timeseries-mart-missing">
          ⚠ Mart JSON 未配置. 请先运行 <code>deploy/static-export/export-mart-data.py</code>.
        </p>
      </section>
    );
  }

  // 预切片: 仅传当前省 rows 给 client (避免 client filter 8060 rows).
  const provincePoints = data.provinces.filter((p) => p.province_code === code);

  // Data Missing banner: 若所有 cells 都 missing → 显式提示 (per 红线-1).
  const anyReal = provincePoints.some(
    (p) => p.value !== null && p.status !== "DATA_MISSING"
  );

  const provinces = listProvincesWithTimeSeries();
  const indicators = listIndicatorsWithTimeSeries();
  const perProvinceSummary = listSourceGradesByProvince(code);
  const nationalSummary = listSourceGradesNational();

  // 当前省中文名 (用于 banner 标题).
  const provinceName =
    provinces.find((p) => p.province_code === code)?.province_name ?? code;

  return (
    <section data-testid={`timeseries-province-page-${code}`}>
      <h1 data-testid={`timeseries-province-h1-${code}`}>
        时序可视化 · {provinceName} ({code}) · 26 年 × 10 指标
      </h1>

      {!anyReal && (
        <p
          style={{
            color: "#b45309",
            fontWeight: 600,
            background: "#fff8e1",
            border: "1px solid #ffeeba",
            padding: "8px 12px",
            borderRadius: 3,
          }}
          data-testid={`timeseries-province-all-missing-${code}`}
        >
          ⚠ {provinceName} 历年所有指标均 DATA_MISSING (hongheiku 索引缺文,
          沿用 660 红线). 详情见{" "}
          <a
            href="/research/m1-series"
            style={{ color: "#0969da", textDecoration: "underline" }}
          >
            M1 验收面
          </a>
          .
        </p>
      )}

      <TimeSeriesExplorer
        provinces={provinces}
        indicators={indicators}
        points={provincePoints}
        perProvinceSummary={perProvinceSummary}
        nationalSummary={nationalSummary}
        defaultProvinceCode={code}
        defaultIndicatorKey="gdp_total"
        defaultYearRange={[2020, 2025]}
      />

      <section style={{ marginTop: 24 }} data-testid="timeseries-province-meta">
        <p style={{ fontSize: 13, color: "#555", lineHeight: 1.6 }}>
          切换省份:{" "}
          {provinces.slice(0, 8).map((p, idx) => (
            <span key={p.province_code}>
              {idx > 0 && " · "}
              <a
                href={`/timeseries/${p.province_code.toLowerCase()}`}
                style={{ color: "#0969da", textDecoration: "underline" }}
                data-testid={`timeseries-province-link-${p.province_code}`}
              >
                {p.province_name}
              </a>
            </span>
          ))}
          {" "}
          (按拼音排序, 共 {provinces.length} 项 + NATIONAL)
        </p>
      </section>
    </section>
  );
}