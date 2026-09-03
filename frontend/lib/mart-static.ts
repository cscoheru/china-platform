// frontend/lib/mart-static.ts — knife 660 Track B (静态导出) + 661 扩展 + 662 D2.
//
// Per 660 tasking §PART 2 + docs/53 §5 第 16 项 redeploy 运维行:
// newvps 上不需要 FastAPI backend + dbt + DB。mart 数据 (28 真实 + 3 缺失 +
// 1 NATIONAL 锚行 per 661) 在架构师端从 dbt/models/marts/mart_province_gdp_2024.sql
// 导出为 frontend/data/mart_province_gdp_2024.json (per export-mart-data.py),
// 提交进仓库,Next.js build 时通过 NEXT_PUBLIC_MART_DATA_PATH 读 JSON,
// 运行时零外部依赖。
//
// 662 D2: 同目录再读一份 mart_indicator_definitions_2024.json (5 指标定义 +
// 来源等级三档分布), 路径派生自 NEXT_PUBLIC_MART_DATA_PATH 的目录 (假设
// mart_province_gdp_2024.json 与 mart_indicator_definitions_2024.json 同目录);
// 不引入第二个 env var 减运维负担。
//
// Build 流程:
//   cd /opt/china-platform/frontend
//   NEXT_PUBLIC_MART_DATA_PATH=./data/mart_province_gdp_2024.json npm run build
//
// 守门:
//   - module init 时 (server-side only) 读 JSON;失败 → throw with actionable msg
//   - 32 行守门 (28 真实 + 3 缺失 + 1 NATIONAL) 在 export-mart-data.py 已做
//     --strict 验证;此处不重复
//   - 数据缺失省指标列必须为 null(per 红线 1)
//   - 661: source_url 是 lineage_source → 公共 URL 路由映射; source_hash_prefix
//     为 null (待 662+ dbt source_document JOIN)

import fs from "fs";
import path from "path";

import type {
  ProvinceTimeSeriesResponse,
  ProvinceTimeSeriesYearRange,
} from "./types";

export interface MartProvinceGdp2024Row {
  province_code: string;
  province_name: string;
  gdp_total: number | string | null;
  gdp_growth: number | string | null;
  primary_gdp: number | string | null;
  secondary_gdp: number | string | null;
  tertiary_gdp: number | string | null;
  growth_note: number | string | null;
  status: string | null; // null=real; 'DATA_MISSING'; 'OFFICIAL_ANCHOR' (661)
  missing_reason: string | null;
  lineage_source: string;
  lineage_origin: string;
  lineage_ruling: string;
  lineage_is_demo: string;
  // 661 扩展: 溯源 popover 三件套 (source_url + source_hash_prefix + lineage_ruling).
  source_url: string | null; // 公共 URL (lineage_source 路由)
  source_hash_prefix: string | null; // 8 字符 SHA 前缀 (661 留 null, 662+ 接入)
}

export interface MartProvinceGdp2024 {
  as_of: string;
  ruling: string;
  schema_version?: string; // 661: optional, '660' baseline vs '661' extension
  mart_source: string;
  total_count: number;
  real_count: number;
  missing_count: number;
  national_count?: number; // 661: optional, 1 if NATIONAL anchor row present
  data_missing_provinces: string[];
  lineage_ruling: string;
  lineage_is_demo: string;
  provinces: MartProvinceGdp2024Row[];
}

let cached: MartProvinceGdp2024 | null = null;
let loadError: Error | null = null;

/** True iff NEXT_PUBLIC_MART_DATA_PATH is set in env (build-time injection). */
export function isStaticMartDataEnabled(): boolean {
  return typeof process.env.NEXT_PUBLIC_MART_DATA_PATH === "string"
    && process.env.NEXT_PUBLIC_MART_DATA_PATH.length > 0;
}

/**
 * Read the mart JSON file from NEXT_PUBLIC_MART_DATA_PATH (build-time env).
 * Server-side only (uses fs). Cached after first read.
 *
 * Throws if path is set but file is missing or invalid JSON. Returns null if
 * path is not set (graceful degradation for local dev without env).
 */
export function loadStaticMartData(): MartProvinceGdp2024 | null {
  if (cached) return cached;
  if (loadError) throw loadError;

  const p = process.env.NEXT_PUBLIC_MART_DATA_PATH;
  if (!p) return null;

  const resolved = path.isAbsolute(p) ? p : path.join(process.cwd(), p);
  if (!fs.existsSync(resolved)) {
    loadError = new Error(
      `NEXT_PUBLIC_MART_DATA_PATH is set to ${p} but file not found at ${resolved}. ` +
        "Run deploy/static-export/export-mart-data.py --strict first."
    );
    throw loadError;
  }

  try {
    const raw = fs.readFileSync(resolved, "utf-8");
    cached = JSON.parse(raw) as MartProvinceGdp2024;
    return cached;
  } catch (e) {
    loadError = new Error(`Failed to load mart data from ${resolved}: ${(e as Error).message}`);
    throw loadError;
  }
}

/**
 * Convenience: return mart data or null. Use this in page components for
 * graceful degradation (page renders even if mart data is not configured).
 */
export function getMartProvinceGdp2024(): MartProvinceGdp2024 | null {
  if (!isStaticMartDataEnabled()) return null;
  return loadStaticMartData();
}

/**
 * 661: return the NATIONAL anchor row (全国 2024 GDP, OFFICIAL_ANCHOR).
 * Per docs/81 §3 国家锚核对 + 661 tasking §1.661. Returns null if mart data
 * is not loaded or no NATIONAL row is present (660 baseline would return null).
 *
 * Use this on the home page to render the 国家锚 row at top of the GDP table.
 */
export function getNationalAnchor(): MartProvinceGdp2024Row | null {
  const data = getMartProvinceGdp2024();
  if (!data) return null;
  return data.provinces.find((p) => p.province_code === "NATIONAL") ?? null;
}

/**
 * 661: look up a province (or NATIONAL) by its GB/T 2260 code.
 * Returns null if not found or mart data is not configured.
 *
 * Use this in dynamic province detail routes (C2) to fetch a single row by
 * [province_code] slug. DATA_MISSING provinces are returned with all metric
 * cols null — callers must check `status === "DATA_MISSING"` before display.
 */
export function getProvinceByCode(
  code: string
): MartProvinceGdp2024Row | null {
  const data = getMartProvinceGdp2024();
  if (!data) return null;
  return data.provinces.find((p) => p.province_code === code) ?? null;
}

// ────────────────────────────────────────────────────────────────────────────
// 662 D2: 指标定义 loader (mart_indicator_definitions_2024.json)
//
// 路径派生: 与主 mart JSON 同目录 (假设 export-mart-data.py 一次导出两份).
// 若派生路径不存在 → 返回 null (graceful degradation, /indicators 页显示
// "指标定义未配置").
// ────────────────────────────────────────────────────────────────────────────

/**
 * 662 D2: 单指标定义. caliber/period 默认填充 "(口径待补, 见 lineage_ruling)"
 * (per 红线 8 禁编造), 缺字段不会 throw.
 */
export interface MartIndicatorDefinition {
  key: string;                          // e.g. "gdp_total"
  label: string;                        // e.g. "GDP 总量"
  unit: string;                         // e.g. "亿元"
  caliber: string;                      // NBS 口径描述
  period: string;                       // e.g. "2024 年（全年）"
  source_grade_distribution: {
    OFFICIAL_INTAKED: number;
    HONGHEIKU_TRANSLOAD: number;
    DATA_MISSING: number;
  };
}

/**
 * 662 D2: 指标定义文件 schema. 与 mart 主 JSON 顶层字段对齐 (as_of /
 * ruling / schema_version / lineage_ruling / lineage_is_demo).
 */
export interface MartIndicatorDefinitionsFile {
  as_of: string;
  ruling: string;
  schema_version?: string;
  mart_source: string;
  lineage_ruling: string;
  lineage_is_demo: string;
  indicator_count: number;
  indicators: MartIndicatorDefinition[];
}

let cachedIndicatorDefs: MartIndicatorDefinitionsFile | null = null;
let indicatorDefsLoadError: Error | null = null;
let indicatorDefsLoadAttempted = false;
let indicatorDefsFileMissing = false; // graceful-degradation 标志

/**
 * 662 D2: 派生指标定义 JSON 的绝对路径.
 * 默认与 NEXT_PUBLIC_MART_DATA_PATH 同目录, 文件名 mart_indicator_definitions_2024.json.
 */
function deriveIndicatorDefsPath(martPath: string): string {
  const dir = path.dirname(martPath);
  return path.isAbsolute(martPath)
    ? path.join(dir, "mart_indicator_definitions_2024.json")
    : path.join(process.cwd(), dir, "mart_indicator_definitions_2024.json");
}

/**
 * 662 D2: 读取指标定义 JSON (build-time fs read + cache).
 *
 * 三态返回:
 *   - 成功: 返回 MartIndicatorDefinitionsFile
 *   - 文件不存在: 返回 null (graceful degradation, /indicators 页可显示空态)
 *   - JSON 解析失败: throw with actionable msg
 *
 * 与 loadStaticMartData() 不同: 指标定义文件缺失不算错误 (因为 662 之前
 * 的部署只有 mart 主 JSON), 所以需要三态语义.
 */
export function loadStaticIndicatorDefinitions(): MartIndicatorDefinitionsFile | null {
  if (cachedIndicatorDefs) return cachedIndicatorDefs;
  if (indicatorDefsLoadError) throw indicatorDefsLoadError;
  if (indicatorDefsFileMissing) return null;

  const martPath = process.env.NEXT_PUBLIC_MART_DATA_PATH;
  if (!martPath) {
    indicatorDefsFileMissing = true;
    return null;
  }

  const resolved = deriveIndicatorDefsPath(martPath);
  if (!fs.existsSync(resolved)) {
    // Graceful degradation: 缺文件不算错误, /indicators 页显示 "未配置" 提示.
    indicatorDefsFileMissing = true;
    return null;
  }

  try {
    const raw = fs.readFileSync(resolved, "utf-8");
    cachedIndicatorDefs = JSON.parse(raw) as MartIndicatorDefinitionsFile;
    indicatorDefsLoadAttempted = true;
    return cachedIndicatorDefs;
  } catch (e) {
    indicatorDefsLoadError = new Error(
      `Failed to load indicator definitions from ${resolved}: ${(e as Error).message}`
    );
    throw indicatorDefsLoadError;
  }
}

/**
 * 662 D2: 便捷函数. 若指标定义文件不存在 (含未配 env) 返回 null.
 */
export function getIndicatorDefinitions(): MartIndicatorDefinitionsFile | null {
  return loadStaticIndicatorDefinitions();
}

/**
 * 662 D2: 便捷函数. 返回指标定义数组 (5 个); 文件缺失返回 null.
 */
export function getIndicatorDefinitionList(): MartIndicatorDefinition[] | null {
  const data = getIndicatorDefinitions();
  return data?.indicators ?? null;
}

// ────────────────────────────────────────────────────────────────────────────
// P2 / knife 664: Province time-series mart loader (mart_province_timeseries.json)
//
// Schema: 31 provinces × 10 indicators × 26 years (2001-2026) = 8060 rows.
// 2001-2019 + 2026 → status='DATA_MISSING' (新增红线-1/2).
// 3 缺失省 (辽/琼/黔) → 全 DATA_MISSING (660 红线).
//
// 路径派生: 与 NEXT_PUBLIC_MART_DATA_PATH 同目录, 文件名
// mart_province_timeseries.json (assumes export-mart-data.py 一次导出多份).
//
// 三态返回 (镜像 indicator definitions loader):
//   - 成功: 返回 MartProvinceTimeSeriesFile
//   - 文件不存在: 返回 null (graceful degradation, /timeseries 页显示空态)
//   - JSON 解析失败: throw with actionable msg
// ────────────────────────────────────────────────────────────────────────────

export interface MartProvinceTimeSeriesFile {
  as_of: string;
  ruling: string;
  schema_version?: string;        // '664' baseline
  mart_source: string;            // 'cegr_mart.mart_province_timeseries'
  lineage_ruling: string;
  lineage_is_demo: string;
  total_rows: number;             // 8060 = 31 × 10 × 26
  unique_provinces: number;       // 31
  unique_indicators: number;      // 10
  year_range: readonly [number, number];  // [2001, 2026]
  indicators: string[];           // 10 indicator_keys
  provinces: MartProvinceTimeSeriesRow[];
}

export interface MartProvinceTimeSeriesRow {
  province_code: string;
  province_name: string;
  indicator_key: string;
  indicator_label: string;
  unit: string | null;
  year: number;
  value: number | null;
  status: string | null;
  missing_reason: string | null;
  lineage_source_type: string;
  lineage_origin: string | null;
  lineage_ruling: string;
  lineage_is_demo: string;
}

let cachedTimeSeries: MartProvinceTimeSeriesFile | null = null;
let timeSeriesLoadError: Error | null = null;
let timeSeriesLoadAttempted = false;
let timeSeriesFileMissing = false;  // graceful-degradation 标志

/**
 * P2 / knife 664: 派生 province-time-series JSON 的绝对路径.
 * 默认与 NEXT_PUBLIC_MART_DATA_PATH 同目录, 文件名 mart_province_timeseries.json.
 */
function deriveProvinceTimeSeriesPath(martPath: string): string {
  const dir = path.dirname(martPath);
  return path.isAbsolute(martPath)
    ? path.join(dir, "mart_province_timeseries.json")
    : path.join(process.cwd(), dir, "mart_province_timeseries.json");
}

/**
 * P2 / knife 664: 读取 province-time-series JSON (build-time fs read + cache).
 *
 * 三态返回 (镜像 loadStaticIndicatorDefinitions):
 *   - 成功: 返回 MartProvinceTimeSeriesFile
 *   - 文件不存在: 返回 null (graceful degradation, newvps 上 664g export 未跑也能跑)
 *   - JSON 解析失败: throw with actionable msg
 */
export function loadStaticProvinceTimeSeries(): MartProvinceTimeSeriesFile | null {
  if (cachedTimeSeries) return cachedTimeSeries;
  if (timeSeriesLoadError) throw timeSeriesLoadError;
  if (timeSeriesFileMissing) return null;

  const martPath = process.env.NEXT_PUBLIC_MART_DATA_PATH;
  if (!martPath) {
    timeSeriesFileMissing = true;
    return null;
  }

  const resolved = deriveProvinceTimeSeriesPath(martPath);
  if (!fs.existsSync(resolved)) {
    timeSeriesFileMissing = true;
    return null;
  }

  try {
    const raw = fs.readFileSync(resolved, "utf-8");
    cachedTimeSeries = JSON.parse(raw) as MartProvinceTimeSeriesFile;
    timeSeriesLoadAttempted = true;
    return cachedTimeSeries;
  } catch (e) {
    timeSeriesLoadError = new Error(
      `Failed to load province time-series from ${resolved}: ${(e as Error).message}`
    );
    throw timeSeriesLoadError;
  }
}

/**
 * P2 / knife 664: 便捷函数. 读取 province time-series JSON, 文件不存在返回 null.
 */
export function getProvinceTimeSeriesStatic(): MartProvinceTimeSeriesFile | null {
  return loadStaticProvinceTimeSeries();
}

/**
 * P2 / knife 664: 便捷函数. 按 province_code + year_range 过滤 mart 行.
 *
 * Returns null if mart JSON is not configured (graceful degradation).
 * Returns empty array if province_code not in mart.
 *
 * 性能: 8060 rows in-memory filter is fine for the data scale; if scale grows,
 * build a province_code index (Map<province_code, rows[]>) on cache load.
 */
export function getProvinceTimeSeriesByCode(
  provinceCode: string,
  yearRange?: readonly [number, number]
): ProvinceTimeSeriesResponse | null {
  const data = getProvinceTimeSeriesStatic();
  if (!data) return null;

  const filtered = data.provinces.filter((r) => {
    if (r.province_code !== provinceCode) return false;
    if (yearRange && (r.year < yearRange[0] || r.year > yearRange[1])) return false;
    return true;
  });

  const provinceName = filtered.length > 0 ? filtered[0].province_name : null;
  const [yearStart, yearEnd] = yearRange ?? data.year_range;

  return {
    province_code: provinceCode,
    province_name: provinceName,
    indicator_count: data.unique_indicators,
    year_range: [yearStart, yearEnd] as ProvinceTimeSeriesYearRange,
    points_count: filtered.length,
    points: filtered,
    pagination: {
      page: 1,
      page_size: filtered.length,
      total_count: filtered.length,
      has_next: false,
    },
  };
}
