"""P2 / knife H-series — City time-series Pydantic models.

Per knife H1 plan (2026-09-13) — city mart 数据接驳公网.
Source of truth: cegr_mart.mart_city_timeseries (dbt mart, knife 934 部署 2030+ rows).

City code format: ^[A-Z][A-Z0-9_]+$ (must contain underscore).
Examples: GUANGDONG_SHENZHEN / JIANGSU_NANJING / ZHEJIANG_HANGZHOU.
4 直辖市 (BEIJING/SHANGHAI/TIANJIN/CHONGQING) excluded from city mart per 红线-7.

Status semantics (same as province):
  - status IS NULL              → real data cell (value present)
  - status = 'DATA_MISSING'     → explicitly missing (red line 1/2 + pending harvest)
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from china_platform.api.models.common import Pagination


class CityTimeSeriesPoint(BaseModel):
    """One row of cegr_mart.mart_city_timeseries (one city × one indicator × one year).

    Status field semantics:
      - None (NULL)         → real data cell; value is non-null
      - 'DATA_MISSING'      → explicit missing per knife 663 红线 1+2 or missing city/pending harvest
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "city_code": "GUANGDONG_SHENZHEN",
                "city_name": "深圳市",
                "province_code": "GUANGDONG",
                "indicator_key": "gdp_total",
                "indicator_label": "地区生产总值 (总量)",
                "unit": "亿元",
                "year": 2024,
                "value": 36801.7,
                "status": None,
                "missing_reason": None,
                "lineage_source_type": "HONGHEIKU_TRANSLOAD",
                "lineage_origin": "guangdong_tjj_shenzhen",
                "lineage_ruling": "K669b-i-batch2-2024-2026-09-12",
                "lineage_is_demo": "false",
            }
        }
    )

    city_code: str
    city_name: str
    province_code: str
    indicator_key: str
    indicator_label: str
    unit: str | None = None
    year: int
    value: float | None = None
    status: str | None = None
    missing_reason: str | None = None
    lineage_source_type: str
    lineage_origin: str | None = None
    lineage_ruling: str
    lineage_is_demo: str = "false"


class CityTimeSeriesResponse(BaseModel):
    """City time-series response envelope.

    Returns 200 + (possibly empty) points list when city_code has no rows in mart.
    Returns 404 only if city_code is malformed (FastAPI Path validation) OR
    city_code has zero rows across all 7 years × 10 indicators (truly unknown
    city code OR excluded 4 直辖市).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "city_code": "GUANGDONG_SHENZHEN",
                "city_name": "深圳市",
                "province_code": "GUANGDONG",
                "indicator_count": 10,
                "year_range": [2020, 2025],
                "points_count": 60,
                "points": [
                    {
                        "city_code": "GUANGDONG_SHENZHEN",
                        "city_name": "深圳市",
                        "province_code": "GUANGDONG",
                        "indicator_key": "gdp_total",
                        "indicator_label": "地区生产总值 (总量)",
                        "unit": "亿元",
                        "year": 2024,
                        "value": 36801.7,
                        "status": None,
                        "missing_reason": None,
                        "lineage_source_type": "HONGHEIKU_TRANSLOAD",
                        "lineage_origin": "guangdong_tjj_shenzhen",
                        "lineage_ruling": "K669b-i-batch2-2024-2026-09-12",
                        "lineage_is_demo": "false",
                    }
                ],
                "pagination": {
                    "page": 1,
                    "page_size": 500,
                    "total_count": 60,
                    "has_next": False,
                },
            }
        }
    )

    city_code: str
    city_name: str | None = None
    province_code: str | None = None
    indicator_count: int = Field(default=10, ge=1)
    year_range: tuple[int, int]
    points_count: int = Field(default=0, ge=0)
    points: list[CityTimeSeriesPoint] = Field(default_factory=list)
    pagination: Pagination