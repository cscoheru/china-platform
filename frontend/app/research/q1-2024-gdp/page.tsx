// M2-e acceptance surface — 2024 annual GDP (knife 635 §1.E).
//
// Per docs/55 §T7 / knife 635 §1.E:
//   * Header MUST contain "M2-e 验收面 · 2024 年全年 GDP（5/31 + 1 全国）·
//     弱核对 QUARANTINED-WEAK · 非 Gate/O1/M2 PASS"
//   * USE_MOCK=false → render the real on-disk crosscheck report
//     (docs/reports/m2_2024_gdp_crosscheck_20260831.md) + coverage matrix.
//   * Display per-covered-province SHA prefix (8 chars) and source URL.
//   * DO NOT add new write APIs; DO NOT modify /provinces/jiangsu.
//
// This page is the bounded M2-e acceptance view: 1 indicator (M2_GDP_ANNUAL),
// 1 period (2024Y), 6 covered subjects (国家 + 5 省级), 26 BLOCKED 省级.
// It is NOT O1 / NOT M2 PASS / NOT Gate PASS.

import fs from "node:fs/promises";
import path from "node:path";
import { DemoBanner } from "../../DemoBanner";

export const dynamic = "force-dynamic";

const M2_GDP_ANNUAL_INDICATOR_ID = "a2000000-0000-0000-0000-00000000a001";
const NATIONAL_GEO_ENTITY_ID = "a2000000-0000-0000-0000-000000000000";

// SHA prefixes (knife 633 §PHOTO-2): 6 FETCHED archive HTMLs.
const COVERED_SUBJECTS: Array<{
  province_zh: string;
  admin_code: string;
  sha_prefix: string;
  url: string;
  domain: string;
  value_yi: number;
}> = [
  {
    province_zh: "中华人民共和国",
    admin_code: "00",
    sha_prefix: "3e732426d3cbdb84",
    url: "https://www.stats.gov.cn/sj/zxfb/202502/t20250228_1958817.html",
    domain: "stats.gov.cn",
    value_yi: 1349084.0,
  },
  {
    province_zh: "上海市",
    admin_code: "31",
    sha_prefix: "80aa92406e9846c3",
    url: "https://tjj.sh.gov.cn/tjgb/20250324/a7fe18c6d5c24d66bfca89c5bb4cdcfb.html",
    domain: "tjj.sh.gov.cn",
    value_yi: 53926.71,
  },
  {
    province_zh: "北京市",
    admin_code: "11",
    sha_prefix: "073a544f16a1f521",
    url: "https://tjj.beijing.gov.cn/tjsj_31433/tjkd_31444/202503/t20250319_2955569.html",
    domain: "tjj.beijing.gov.cn",
    value_yi: 49843.1,
  },
  {
    province_zh: "四川省",
    admin_code: "51",
    sha_prefix: "915c1b4537b3620c",
    url: "https://tjj.sc.gov.cn/scstjj/c112126/2025/3/17/35d7e3f9f0c34555a09c002535c26842.shtml",
    domain: "tjj.sc.gov.cn",
    value_yi: 64697.0,
  },
  {
    province_zh: "山东省",
    admin_code: "37",
    sha_prefix: "6ffaaffb3a0e9bd4",
    url: "http://tjj.shandong.gov.cn/art/2025/3/5/art_6196_10316729.html",
    domain: "tjj.shandong.gov.cn",
    value_yi: 98565.8,
  },
  {
    province_zh: "湖北省",
    admin_code: "42",
    sha_prefix: "3022e7cacdd44dce",
    url: "http://tjj.hubei.gov.cn/tjsj/tjgb/ndtjgb/qstjgb/202503/t20250321_5585085.shtml",
    domain: "tjj.hubei.gov.cn",
    value_yi: 60012.97,
  },
];

const NATIONAL_VALUE = 1349084.0;

async function readReport(): Promise<string> {
  // Repo root: from frontend/app/research/q1-2024-gdp → ../../../..
  const p = path.resolve(
    process.cwd(),
    "..",
    "..",
    "docs",
    "reports",
    "m2_2024_gdp_crosscheck_20260831.md",
  );
  try {
    return await fs.readFile(p, "utf-8");
  } catch {
    return "(crosscheck report not yet generated — run scripts/crosscheck_m2_2024_gdp.py)";
  }
}

export default async function Q12024GdpPage() {
  const crosscheck = await readReport();
  const sumCovered = COVERED_SUBJECTS
    .filter((s) => s.admin_code !== "00")
    .reduce((acc, s) => acc + s.value_yi, 0);
  const sumRatio = (sumCovered / NATIONAL_VALUE) * 100.0;
  const coverageRatio = (5 / 31) * 100.0;
  const blocked = 31 - 5;

  return (
    <section
      style={{
        fontFamily: "sans-serif",
        maxWidth: 1100,
        margin: "0 auto",
        padding: 24,
      }}
    >
      <h1 style={{ fontSize: 22 }}>
        M2-e 验收面 · 2024 年全年 GDP（5/31 + 1 全国）· 弱核对 QUARANTINED-WEAK
        · 非 Gate/O1/M2 PASS
      </h1>

      {/* 662 D5: demo 壳显式横幅. */}
      <DemoBanner
        reason="M2-e 验收面 · 5/31 + 1 全国 · 弱核对 QUARANTINED-WEAK · 非 Gate/O1/M2 PASS"
        source="docs/reports/m2_2024_gdp_crosscheck_20260831.md"
      />

      <p style={{ color: "#444", lineHeight: 1.6 }}>
        本页只展示 <strong>真 observation</strong>（来自 6 个 .gov.cn
        自取 HTML 公报；SHA 一跳锁定），不展示 mock 数据。
        <strong> 不代表 Gate / O1 / M2 PASS</strong>。本页面数据源 =
        <code> scripts/crosscheck_m2_2024_gdp.py </code>
        输出（docs/reports/m2_2024_gdp_crosscheck_20260831.md）。
      </p>

      <ul
        style={{
          background: "#fafafa",
          padding: "12px 24px",
          borderRadius: 6,
        }}
      >
        <li>
          indicator_id = <code>{M2_GDP_ANNUAL_INDICATOR_ID}</code>（
          GDP_ANNUAL 年度地区生产总值，区别于 M1 GDP 半年）
        </li>
        <li>
          national geo_entity_id = <code>{NATIONAL_GEO_ENTITY_ID}</code>
          （国家级合成行，不在 GB/T 2260）
        </li>
        <li>period = 2024-01-01 .. 2024-12-31（2024 全年）</li>
        <li>5/31 省级 COVERED；26/31 省级 BLOCKED（直连 anti-bot / TLS reset）</li>
        <li>USE_MOCK=false（数据来自 on-disk crosscheck 报告，非 mock）</li>
      </ul>

      <h2 style={{ fontSize: 18, marginTop: 28 }}>6 主体真 observation</h2>
      <table
        style={{
          borderCollapse: "collapse",
          width: "100%",
          marginTop: 8,
          fontSize: 14,
        }}
      >
        <thead>
          <tr style={{ background: "#f0f0f0" }}>
            <th style={th}>province_zh</th>
            <th style={th}>admin_code</th>
            <th style={th}>value (亿元)</th>
            <th style={th}>share of national</th>
            <th style={th}>SHA prefix 8</th>
            <th style={th}>source domain</th>
          </tr>
        </thead>
        <tbody>
          {COVERED_SUBJECTS.map((s) => (
            <tr key={s.admin_code}>
              <td style={td}>{s.province_zh}</td>
              <td style={td}>
                <code>{s.admin_code}</code>
              </td>
              <td style={{ ...td, textAlign: "right", fontWeight: 600 }}>
                {s.value_yi.toFixed(2)}
              </td>
              <td style={{ ...td, textAlign: "right" }}>
                {((s.value_yi / NATIONAL_VALUE) * 100).toFixed(2)}%
              </td>
              <td style={{ ...td, fontFamily: "monospace" }}>{s.sha_prefix}</td>
              <td style={td}>
                <a href={s.url}>{s.domain}</a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 style={{ fontSize: 18, marginTop: 28 }}>跨源核对 (knife 635 §1.D)</h2>
      <p style={{ lineHeight: 1.6 }}>
        本库 <strong>5 省观察值合计 = {sumCovered.toFixed(2)} 亿元</strong>
        ；国家观察值 = <strong>{NATIONAL_VALUE.toFixed(2)} 亿元</strong>。
        sum/national = <strong>{sumRatio.toFixed(2)}%</strong>，覆盖率 ={" "}
        {coverageRatio.toFixed(2)}%（5/31）。
      </p>
      <p style={{ lineHeight: 1.6 }}>
        <strong>方法局限</strong>：knife 635 §1.D 显式定义「无国家分省表时：用『31 省
        库内加总 vs 国家 GDP』作 弱核对，并标注方法局限」。
        当前覆盖率 16.1% ⇒ 本 crosscheck 自动降级为 <strong>QUARANTINED-WEAK</strong>。
        31 省全 COVERED 后升级为 STRONG（±0.5% 阈值）。
      </p>
      <p style={{ lineHeight: 1.6, color: "#a00" }}>
        ⚠ 26/31 省级 status=BLOCKED（knif 635 §1.C：anti-bot / TLS reset /
        直连域名仅返回目录页 / 公报 URL 未定位）。详见
        <code> source_registry/m2_2024_gdp_inventory.csv </code> 的{" "}
        <code>missing_reason</code> 列。本机 IP 被 .gov.cn WAF 阻断，无法补抓。
      </p>

      <h2 style={{ fontSize: 18, marginTop: 28 }}>
        Crosscheck 报告原文（knife 635 §1.D 输出）
      </h2>
      <pre
        style={{
          background: "#fafafa",
          padding: 16,
          borderRadius: 6,
          fontSize: 12,
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
          maxHeight: 600,
          overflow: "auto",
        }}
      >
        {crosscheck}
      </pre>

      <h2 style={{ fontSize: 18, marginTop: 28 }}>未做的部分（不镀铬）</h2>
      <ul>
        <li>❌ 31 省全 COVERED（→ M2-f/g，下一阶段，须用户提供政府源直连）</li>
        <li>❌ 跨源 NBS vs 国家发改委 vs 财政部 三方核对（→ M3+）</li>
        <li>❌ 把 5 省合计当 31 省合计（违反「不补零」红线）</li>
        <li>❌ 假设 BLOCKED 行的 value=0（违反「不静默硬编码」红线）</li>
      </ul>

      <hr style={{ marginTop: 32 }} />
      <p style={{ color: "#888", fontSize: 12 }}>
        数据源：6 个 .gov.cn 公报（SHA 一跳锁定）；crosscheck 由{" "}
        <code> scripts/crosscheck_m2_2024_gdp.py </code> 计算。
        本页为 M2-e 验收面，仅展示 1 指标 1 期间 6 真 observation + 26
        BLOCKED 行，与 Gate / O1 / M2 PASS 无关。
      </p>
      <p style={{ color: "#888", fontSize: 12 }}>
        [M2-e smoke] {`国家=${NATIONAL_VALUE} 5省合计=${sumCovered.toFixed(2)} 覆盖率=5/31=${coverageRatio.toFixed(2)}% blocked=${blocked}`}
      </p>
    </section>
  );
}

const th: React.CSSProperties = {
  border: "1px solid #ddd",
  padding: "6px 10px",
  textAlign: "left",
};

const td: React.CSSProperties = {
  border: "1px solid #eee",
  padding: "6px 10px",
};