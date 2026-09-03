// frontend/lib/mart-static.ts — knife 660 Track B (静态导出) + 661 扩展.
//
// Per 660 tasking §PART 2 + docs/53 §5 第 16 项 redeploy 运维行:
// newvps 上不需要 FastAPI backend + dbt + DB。mart 数据 (28 真实 + 3 缺失 +
// 1 NATIONAL 锚行 per 661) 在架构师端从 dbt/models/marts/mart_province_gdp_2024.sql
// 导出为 frontend/data/mart_province_gdp_2024.json (per export-mart-data.py),
// 提交进仓库,Next.js build 时通过 NEXT_PUBLIC_MART_DATA_PATH 读 JSON,
// 运行时零外部依赖。
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
