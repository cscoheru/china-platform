"""P2 / knife 664 — Province time-series Pydantic models.

Per docs/87 §3.2 P2 数据扩展 + knife 663 mart schema + knife 664 plan.
Source of truth: cegr_mart.mart_province_timeseries (dbt mart, 8060 rows).

Status semantics:
  - status IS NULL              → real data cell (value present)
  - status = 'DATA_MISSING'     → explicitly missing (red line 1/2 + pending harvest)
  - lineage 三件套 always populated (source_type / origin / ruling)
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from china_platform.api.models.common import Pagination


class ProvinceTimeSeriesPoint(BaseModel):
    """One row of cegr_mart.mart_province_timeseries (one province × one indicator × one year).

    Status field semantics:
      - None (NULL)         → real data cell; value is non-null
      - 'DATA_MISSING'      → explicit missing per knife 663 红线 1+2 or missing province/pending harvest
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "province_code": "BEIJING",
                "province_name": "北京",
                "indicator_key": "gdp_total",
                "indicator_label": "地区生产总值 (总量)",
                "unit": "亿元",
                "year": 2024,
                "value": 49843.1,
                "status": None,
                "missing_reason": None,
                "lineage_source_type": "OFFICIAL_INTAKED",
                "lineage_origin": "beijing_tjj",
                "lineage_ruling": "K663-2026-09-03",
                "lineage_is_demo": "false",
            }
        }
    )

    province_code: str
    province_name: str
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


class ProvinceTimeSeriesResponse(BaseModel):
    """Province time-series response envelope.

    Returns 200 + (possibly empty) points list when province_code has no rows.
    Returns 404 only if province_code is malformed (FastAPI Path validation).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "province_code": "BEIJING",
                "province_name": "北京",
                "indicator_count": 10,
                "year_range": [2020, 2025],
                "points_count": 60,
                "points": [
                    {
                        "province_code": "BEIJING",
                        "province_name": "北京",
                        "indicator_key": "gdp_total",
                        "indicator_label": "地区生产总值 (总量)",
                        "unit": "亿元",
                        "year": 2024,
                        "value": 49843.1,
                        "status": None,
                        "missing_reason": None,
                        "lineage_source_type": "OFFICIAL_INTAKED",
                        "lineage_origin": "beijing_tjj",
                        "lineage_ruling": "K663-2026-09-03",
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

    province_code: str
    province_name: str | None = None
    indicator_count: int = Field(default=10, ge=1)
    year_range: tuple[int, int]
    points_count: int = Field(default=0, ge=0)
    points: list[ProvinceTimeSeriesPoint] = Field(default_factory=list)
    pagination: Pagination