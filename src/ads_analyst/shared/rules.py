from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class CampaignThresholds:
    roas_lt: float = 1.0
    acos_gt: float = 1.0
    spend_sales_zero_spend_gt: float = 100.0
    cvr_drop_factor: float = 0.7
    cpc_rise_factor: float = 1.3
    min_days_for_trend: int = 6


@dataclass(frozen=True)
class PlacementThresholds:
    min_spend_share: float = 0.25
    roas_lt: float = 1.0
    spend_sales_zero_spend_gt: float = 50.0


@dataclass(frozen=True)
class SearchTermThresholds:
    spend_sales_zero_spend_gt: float = 20.0
    spend_acos_gate: float = 30.0
    acos_gt: float = 1.5
    p0_spend_gt: float = 50.0


@dataclass(frozen=True)
class TargetingThresholds:
    spend_sales_zero_spend_gt: float = 20.0
    spend_acos_gate: float = 30.0
    acos_gt: float = 1.5
    p0_spend_gt: float = 50.0


@dataclass(frozen=True)
class ThresholdRules:
    campaign: CampaignThresholds = CampaignThresholds()
    placement: PlacementThresholds = PlacementThresholds()
    search_term: SearchTermThresholds = SearchTermThresholds()
    targeting: TargetingThresholds = TargetingThresholds()


def _float(data: dict[str, object], key: str, default: float) -> float:
    value = data.get(key, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(data: dict[str, object], key: str, default: int) -> int:
    value = data.get(key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def default_threshold_rules() -> ThresholdRules:
    return ThresholdRules()


def load_threshold_rules(path: str | Path | None) -> ThresholdRules:
    if path is None:
        return default_threshold_rules()

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Threshold config not found: {file_path}")

    data = tomllib.loads(file_path.read_text(encoding="utf-8"))
    campaign_data = data.get("campaign", {}) if isinstance(data, dict) else {}
    placement_data = data.get("placement", {}) if isinstance(data, dict) else {}
    search_term_data = data.get("search_term", {}) if isinstance(data, dict) else {}
    targeting_data = data.get("targeting", {}) if isinstance(data, dict) else {}

    campaign = CampaignThresholds(
        roas_lt=_float(campaign_data, "roas_lt", 1.0),
        acos_gt=_float(campaign_data, "acos_gt", 1.0),
        spend_sales_zero_spend_gt=_float(campaign_data, "spend_sales_zero_spend_gt", 100.0),
        cvr_drop_factor=_float(campaign_data, "cvr_drop_factor", 0.7),
        cpc_rise_factor=_float(campaign_data, "cpc_rise_factor", 1.3),
        min_days_for_trend=_int(campaign_data, "min_days_for_trend", 6),
    )

    placement = PlacementThresholds(
        min_spend_share=_float(placement_data, "min_spend_share", 0.25),
        roas_lt=_float(placement_data, "roas_lt", 1.0),
        spend_sales_zero_spend_gt=_float(placement_data, "spend_sales_zero_spend_gt", 50.0),
    )

    search_term = SearchTermThresholds(
        spend_sales_zero_spend_gt=_float(search_term_data, "spend_sales_zero_spend_gt", 20.0),
        spend_acos_gate=_float(search_term_data, "spend_acos_gate", 30.0),
        acos_gt=_float(search_term_data, "acos_gt", 1.5),
        p0_spend_gt=_float(search_term_data, "p0_spend_gt", 50.0),
    )

    targeting = TargetingThresholds(
        spend_sales_zero_spend_gt=_float(targeting_data, "spend_sales_zero_spend_gt", 20.0),
        spend_acos_gate=_float(targeting_data, "spend_acos_gate", 30.0),
        acos_gt=_float(targeting_data, "acos_gt", 1.5),
        p0_spend_gt=_float(targeting_data, "p0_spend_gt", 50.0),
    )

    return ThresholdRules(
        campaign=campaign,
        placement=placement,
        search_term=search_term,
        targeting=targeting,
    )
