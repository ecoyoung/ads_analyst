from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CampaignKPI:
    campaign_name: str
    spend: float
    sales: float
    orders: float
    impressions: float
    clicks: float
    ctr: float
    cpc: float
    cvr: float
    acos: float
    roas: float
    budget_utilization: float
    anomalies: tuple[str, ...] = ()


@dataclass(frozen=True)
class DrilldownFinding:
    campaign_name: str
    layer: str
    issue: str
    evidence: str
    action: str
    priority: str = "P1"


@dataclass(frozen=True)
class DrilldownReport:
    date_range: str
    campaign_kpis: tuple[CampaignKPI, ...] = ()
    abnormal_campaigns: tuple[str, ...] = ()
    findings: tuple[DrilldownFinding, ...] = ()
    actions: tuple[str, ...] = ()
    notes: tuple[str, ...] = field(default_factory=tuple)
    campaign_comparison: tuple[dict[str, Any], ...] = ()
    placement_breakdown: dict[str, tuple[dict[str, Any], ...]] = field(default_factory=dict)
    search_term_breakdown: dict[str, tuple[dict[str, Any], ...]] = field(default_factory=dict)
    targeting_breakdown: dict[str, tuple[dict[str, Any], ...]] = field(default_factory=dict)
    analysis_trace: tuple[dict[str, Any], ...] = ()
