from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

Coordinate = Tuple[float, float]  # (lng, lat)

PolygonRing = List[Coordinate]

MultiPolygon = List[List[PolygonRing]]



@dataclass
class BoundingBox:
    name: str
    province: str
    min_lat: float
    max_lat: float
    min_lng: float
    max_lng: float



@dataclass
class SamplePoint:
    id: str
    province: str
    scope_name: str
    lat: float
    lng: float
    weather_model: Optional[str] = None
    cloud_cover: Optional[float] = None
    humidity: Optional[float] = None
    visibility_m: Optional[float] = None
    wind_speed: Optional[float] = None
    moon_factor: Optional[float] = None
    elevation_m: Optional[float] = None
    # Nightly aggregation (computed over astronomical twilight window)
    night_avg_cloud: Optional[float] = None
    night_worst_cloud: Optional[float] = None
    night_avg_humidity: Optional[float] = None
    night_avg_visibility: Optional[float] = None
    night_avg_wind: Optional[float] = None
    night_avg_temperature: Optional[float] = None
    night_max_gust: Optional[float] = None
    moon_interference: Optional[float] = None  # 0=强干扰, 100=无干扰
    moonrise: Optional[str] = None
    moonset: Optional[str] = None
    moon_dark_window: Optional[str] = None
    night_avg_dew_point: Optional[float] = None
    night_max_precip: Optional[float] = None
    night_min_cloud_base: Optional[float] = None
    night_avg_cloud_low: Optional[float] = None
    night_avg_cloud_mid: Optional[float] = None
    night_avg_cloud_high: Optional[float] = None
    night_weather_codes: Optional[List[int]] = None
    usable_hours: Optional[float] = None
    longest_usable_streak_hours: Optional[float] = None
    best_window_start: Optional[str] = None
    best_window_end: Optional[str] = None
    best_window_segment: Optional[str] = None
    cloud_stddev: Optional[float] = None
    cloud_stability: Optional[str] = None
    worst_cloud_segment: Optional[str] = None
    stage1_status: str = "pending"
    merged_into: Optional[str] = None
    weather_source: Optional[str] = None
    fetch_attempts: int = 0
    fetch_recovered: bool = False
    fetch_error_type: Optional[str] = None
    fetch_error_message: Optional[str] = None
    final_score: Optional[float] = None
    score_breakdown: Optional[dict] = None


# Major Chinese cities used for light-pollution estimation (name, lat, lng)
