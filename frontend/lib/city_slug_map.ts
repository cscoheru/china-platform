// Stage 2 / S2.7-b-lite — 10 地市 slug 映射表。
//
// Per docs/46 §3.1 (slug 约定):
//   - 字符集 [a-z0-9-]+
//   - 全局唯一（不与 province slug 冲突：province 已用 jiangsu/zhejiang/guangdong 等）
//   - 来源 = 中文地名 pinyin 去声调
//
// 红线 (per `256` §红线 + docs/34 §1 + docs/46 §1.2):
//   - 不擅自增减 10 城名单（Cursor 锁定）
//   - 不宣布 Gate 2 PASS
//   - 不做官员评分 / 排名

export interface CitySlugEntry {
  slug: string;
  nameZh: string;
  nameEn: string;
  provinceSlug: string; // 归属省份 slug（jiangsu / zhejiang / guangdong）
}

// 10 地市锁定清单（per `256` §SCHEMA "10 城 slug" + docs/46 §2）
//   江苏 4：南京/苏州/无锡/南通
//   浙江 3：杭州/宁波/温州
//   广东 3：广州/深圳/东莞
export const CITY_SLUG_MAP: Record<string, CitySlugEntry> = {
  nanjing: {
    slug: "nanjing",
    nameZh: "南京市",
    nameEn: "Nanjing",
    provinceSlug: "jiangsu",
  },
  suzhou: {
    slug: "suzhou",
    nameZh: "苏州市",
    nameEn: "Suzhou",
    provinceSlug: "jiangsu",
  },
  wuxi: {
    slug: "wuxi",
    nameZh: "无锡市",
    nameEn: "Wuxi",
    provinceSlug: "jiangsu",
  },
  nantong: {
    slug: "nantong",
    nameZh: "南通市",
    nameEn: "Nantong",
    provinceSlug: "jiangsu",
  },
  hangzhou: {
    slug: "hangzhou",
    nameZh: "杭州市",
    nameEn: "Hangzhou",
    provinceSlug: "zhejiang",
  },
  ningbo: {
    slug: "ningbo",
    nameZh: "宁波市",
    nameEn: "Ningbo",
    provinceSlug: "zhejiang",
  },
  wenzhou: {
    slug: "wenzhou",
    nameZh: "温州市",
    nameEn: "Wenzhou",
    provinceSlug: "zhejiang",
  },
  guangzhou: {
    slug: "guangzhou",
    nameZh: "广州市",
    nameEn: "Guangzhou",
    provinceSlug: "guangdong",
  },
  shenzhen: {
    slug: "shenzhen",
    nameZh: "深圳市",
    nameEn: "Shenzhen",
    provinceSlug: "guangdong",
  },
  dongguan: {
    slug: "dongguan",
    nameZh: "东莞市",
    nameEn: "Dongguan",
    provinceSlug: "guangdong",
  },
};

// 锁定清单数组（顺序固定 per Cursor 裁定）：10 项 = 江苏 4 + 浙江 3 + 广东 3
export const CITY_SLUG_LIST: readonly string[] = [
  "nanjing",
  "suzhou",
  "wuxi",
  "nantong",
  "hangzhou",
  "ningbo",
  "wenzhou",
  "guangzhou",
  "shenzhen",
  "dongguan",
];

// 应用层守门：slug 必须命中锁定清单（10 城名单不擅自改）
export function isValidCitySlug(slug: string): slug is keyof typeof CITY_SLUG_MAP {
  return Object.prototype.hasOwnProperty.call(CITY_SLUG_MAP, slug);
}

export function getCityEntry(slug: string): CitySlugEntry | null {
  return CITY_SLUG_MAP[slug] ?? null;
}