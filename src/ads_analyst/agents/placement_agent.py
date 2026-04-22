from __future__ import annotations

from collections import defaultdict
from datetime import date

from .base import BaseAnalysisAgent
from ..domain.models import DrilldownFinding
from ..shared.metrics import acos, cvr, roas, safe_float
from ..shared.rules import PlacementThresholds


class PlacementAgent(BaseAnalysisAgent):
    layer = "placement"

    def __init__(self, db, thresholds: PlacementThresholds | None = None):
        super().__init__(db)
        self.thresholds = thresholds or PlacementThresholds()

    def analyze(
        self,
        tables: list[str],
        campaigns: list[str],
        start_date: date | None,
        end_date: date | None,
    ) -> list[DrilldownFinding]:
        target = set(campaigns)
        findings: list[DrilldownFinding] = []

        for table in tables:
            rows, mapping = self._read_rows(table=table, start_date=start_date, end_date=end_date)
            if not rows or "placement" not in mapping:
                continue

            by_campaign: dict[str, dict[str, dict[str, float]]] = defaultdict(
                lambda: defaultdict(lambda: {"spend": 0.0, "sales": 0.0, "orders": 0.0, "clicks": 0.0})
            )

            for row in rows:
                campaign = str(row.get(mapping["campaign_name"], "")).strip() or "UNKNOWN"
                if campaign not in target:
                    continue
                placement = str(row.get(mapping["placement"], "")).strip() or "UNKNOWN"
                bucket = by_campaign[campaign][placement]
                bucket["spend"] += safe_float(row.get(mapping.get("spend", "")))
                bucket["sales"] += safe_float(row.get(mapping.get("sales", "")))
                bucket["orders"] += safe_float(row.get(mapping.get("orders", "")))
                bucket["clicks"] += safe_float(row.get(mapping.get("clicks", "")))

            for campaign, placements in by_campaign.items():
                total_spend = sum(item["spend"] for item in placements.values())
                if total_spend <= 0:
                    continue

                for placement, metrics in placements.items():
                    spend_share = metrics["spend"] / total_spend
                    placement_roas = roas(metrics["sales"], metrics["spend"])
                    placement_acos = acos(metrics["spend"], metrics["sales"])
                    placement_cvr = cvr(metrics["orders"], metrics["clicks"])

                    if spend_share >= self.thresholds.min_spend_share and (
                        placement_roas < self.thresholds.roas_lt
                        or (
                            metrics["spend"] > self.thresholds.spend_sales_zero_spend_gt
                            and metrics["sales"] == 0
                        )
                    ):
                        findings.append(
                            DrilldownFinding(
                                campaign_name=campaign,
                                layer="placement",
                                issue=f"Low efficiency placement: {placement}",
                                evidence=(
                                    f"spend_share={spend_share:.1%}, spend=${metrics['spend']:.2f}, "
                                    f"ROAS={placement_roas:.2f}, ACOS={placement_acos:.1%}, CVR={placement_cvr:.1%}"
                                ),
                                action=(
                                    f"Shift budget away from {placement} and lower bid modifier on this placement; "
                                    "re-allocate budget to higher-ROAS placements."
                                ),
                                priority="P0",
                            )
                        )

        return findings

    def summarize_breakdown(
        self,
        tables: list[str],
        campaigns: list[str],
        start_date: date | None,
        end_date: date | None,
    ) -> dict[str, list[dict[str, float | str]]]:
        target = set(campaigns)
        by_campaign: dict[str, dict[str, dict[str, float]]] = defaultdict(
            lambda: defaultdict(lambda: {"spend": 0.0, "sales": 0.0, "orders": 0.0, "clicks": 0.0, "impressions": 0.0})
        )

        for table in tables:
            rows, mapping = self._read_rows(table=table, start_date=start_date, end_date=end_date)
            if not rows or "placement" not in mapping:
                continue

            for row in rows:
                campaign = str(row.get(mapping["campaign_name"], "")).strip() or "UNKNOWN"
                if campaign not in target:
                    continue
                placement = str(row.get(mapping["placement"], "")).strip() or "UNKNOWN"
                bucket = by_campaign[campaign][placement]
                bucket["spend"] += safe_float(row.get(mapping.get("spend", "")))
                bucket["sales"] += safe_float(row.get(mapping.get("sales", "")))
                bucket["orders"] += safe_float(row.get(mapping.get("orders", "")))
                bucket["clicks"] += safe_float(row.get(mapping.get("clicks", "")))
                bucket["impressions"] += safe_float(row.get(mapping.get("impressions", "")))

        result: dict[str, list[dict[str, float | str]]] = {}
        for campaign, placement_map in by_campaign.items():
            total_spend = sum(item["spend"] for item in placement_map.values())
            campaign_roas = roas(
                sum(item["sales"] for item in placement_map.values()),
                total_spend,
            )
            rows: list[dict[str, float | str]] = []
            for placement, metrics in placement_map.items():
                p_roas = roas(metrics["sales"], metrics["spend"])
                rows.append(
                    {
                        "placement": placement,
                        "spend": metrics["spend"],
                        "sales": metrics["sales"],
                        "orders": metrics["orders"],
                        "clicks": metrics["clicks"],
                        "impressions": metrics["impressions"],
                        "spend_share": (metrics["spend"] / total_spend) if total_spend else 0.0,
                        "roas": p_roas,
                        "acos": acos(metrics["spend"], metrics["sales"]),
                        "ctr": (metrics["clicks"] / metrics["impressions"]) if metrics["impressions"] else 0.0,
                        "cvr": cvr(metrics["orders"], metrics["clicks"]),
                        "roas_delta_vs_campaign": p_roas - campaign_roas,
                    }
                )

            rows.sort(key=lambda x: float(x["spend"]), reverse=True)
            result[campaign] = rows

        return result
