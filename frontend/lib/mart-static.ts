// frontend/lib/mart-static.ts — knife 660 Track B (静态导出).
//
// Per 660 tasking §PART 2 + docs/53 §5 第 16 项 redeploy 运维行:
// newvps 上不需要 FastAPI backend + dbt + DB。mart 数据 (28 真实 + 3 缺失)
// 在架构师端从 dbt/models/marts/mart_province_gdp_2024.sql 导出为
// frontend/data/mart_province_gdp_2024.json (per export-mart-data.py),
// 提交进仓库,Next.js build 时通过 NEXT_PUBLIC_MART_DATA_PATH 读 JSON,
// 运行时零外部依赖。
//
// Build 流程:
//   cd /opt/china-platform/frontend
//   NEXT_PUBLIC_MART_DATA_PATH=./data/mart_province_gdp_2024.json npm run build
//
// 守门:
//   - module init 时 (server-side only) 读 JSON;失败 → throw with actionable msg
//   - 31 行守门 (28 真实 + 3 缺失 NULL 禁补零) 在 export-mart-data.py 已做
//     --strict 验证;此处不重复
//   - 数据缺失省指标列必须为 null(per 红线 1)

import fs from "fs";
import path from "path";

export interface MartProvinceGdp2024Row {
  province_code: string;
  province_name: string;
  gdp_total: number | null;
  gdp_growth: number | null;
  primary_gdp: number | null;
  secondary_gdp: number | null;
  tertiary_gdp: number | null;
  growth_note: number | null;
  status: string | null;
  missing_reason: string | null;
  lineage_source: string;
  lineage_origin: string;
  lineage_ruling: string;
  lineage_is_demo: string;
}

export interface MartProvinceGdp2024 {
  as_of: string;
  ruling: string;
  mart_source: string;
  total_count: number;
  real_count: number;
  missing_count: number;
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
