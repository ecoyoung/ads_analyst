from __future__ import annotations

from collections import defaultdict
from datetime import date

from .base import BaseAnalysisAgent
from ..domain.models import DrilldownFinding
from ..shared.metrics import acos, cvr, roas, safe_float
from ..shared.rules import SearchTermThresholds


class SearchTermAgent(BaseAnalysisAgent):
    layer = "search_term"

    def __init__(self, db, thresholds: SearchTermThresholds | None = None):
        super().__init__(db)
        self.thresholds = thresholds or SearchTermThresholds()

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
            if not rows or "search_term" not in mapping:
                continue

            grouped: dict[tuple[str, str, str], dict[str, float]] = defaultdict(
                lambda: {"spend": 0.0, "sales": 0.0, "orders": 0.0, "clicks": 0.0}
            )

            for row in rows:
                campaign = str(row.get(mapping["campaign_name"], "")).strip() or "UNKNOWN"
                if campaign not in target:
                    continue

                search_term = str(row.get(mapping["search_term"], "")).strip() or "UNKNOWN"
                match_type_col = mapping.get("match_type")
                match_type = str(row.get(match_type_col, "UNKNOWN")).strip() if match_type_col else "UNKNOWN"

                metric = grouped[(campaign, search_term, match_type)]
                metric["spend"] += safe_float(row.get(mapping.get("spend", "")))
                metric["sales"] += safe_float(row.get(mapping.get("sales", "")))
                metric["orders"] += safe_float(row.get(mapping.get("orders", "")))
                metric["clicks"] += safe_float(row.get(mapping.get("clicks", "")))

            for (campaign, search_term, match_type), metric in grouped.items():
                term_roas = roas(metric["sales"], metric["spend"])
                term_acos = acos(metric["spend"], metric["sales"])
                term_cvr = cvr(metric["orders"], metric["clicks"])

                if (
                    metric["spend"] > self.thresholds.spend_sales_zero_spend_gt
                    and metric["sales"] == 0
                ) or (
                    metric["spend"] > self.thresholds.spend_acos_gate
                    and term_acos > self.thresholds.acos_gt
                ):
                    findings.append(
                        DrilldownFinding(
                            campaign_name=campaign,
                            layer="search_term",
                            issue=f"Inefficient term: {search_term}",
                            evidence=(
                                f"match_type={match_type}, spend=${metric['spend']:.2f}, sales=${metric['sales']:.2f}, "
                                f"ROAS={term_roas:.2f}, ACOS={term_acos:.1%}, CVR={term_cvr:.1%}"
                            ),
                            action=(
                                "Add negative keyword or reduce bid for this term; keep budget for terms with stable conversion."
                            ),
                            priority="P0" if metric["spend"] > self.thresholds.p0_spend_gt else "P1",
                        )
                    )

        findings.sort(key=lambda x: (x.campaign_name, x.priority, x.issue))
        return findings

    def summarize_breakdown(
        self,
        tables: list[str],
        campaigns: list[str],
        start_date: date | None,
        end_date: date | None,
        top_n: int = 20,
    ) -> dict[str, list[dict[str, float | str]]]:
        target = set(campaigns)
        grouped: dict[tuple[str, str, str], dict[str, float]] = defaultdict(
            lambda: {"spend": 0.0, "sales": 0.0, "orders": 0.0, "clicks": 0.0, "impressions": 0.0}
        )

        for table in tables:
            rows, mapping = self._read_rows(table=table, start_date=start_date, end_date=end_date)
            if not rows or "search_term" not in mapping:
                continue

            for row in rows:
                campaign = str(row.get(mapping["campaign_name"], "")).strip() or "UNKNOWN"
                if campaign not in target:
                    continue

                search_term = str(row.get(mapping["search_term"], "")).strip() or "UNKNOWN"
                match_type_col = mapping.get("match_type")
                match_type = str(row.get(match_type_col, "UNKNOWN")).strip() if match_type_col else "UNKNOWN"

                metric = grouped[(campaign, search_term, match_type)]
                metric["spend"] += safe_float(row.get(mapping.get("spend", "")))
                metric["sales"] += safe_float(row.get(mapping.get("sales", "")))
                metric["orders"] += safe_float(row.get(mapping.get("orders", "")))
                metric["clicks"] += safe_float(row.get(mapping.get("clicks", "")))
                metric["impressions"] += safe_float(row.get(mapping.get("impressions", "")))

        by_campaign: dict[str, list[dict[str, float | str]]] = defaultdict(list)
        campaign_totals: dict[str, dict[str, float]] = defaultdict(lambda: {"spend": 0.0, "sales": 0.0})
        for (campaign, _, _), metric in grouped.items():
            campaign_totals[campaign]["spend"] += metric["spend"]
            campaign_totals[campaign]["sales"] += metric["sales"]

        for (campaign, search_term, match_type), metric in grouped.items():
            c_roas = roas(campaign_totals[campaign]["sales"], campaign_totals[campaign]["spend"])
            t_roas = roas(metric["sales"], metric["spend"])
            by_campaign[campaign].append(
                {
                    "search_term": search_term,
                    "match_type": match_type,
                    "spend": metric["spend"],
                    "sales": metric["sales"],
                    "orders": metric["orders"],
                    "clicks": metric["clicks"],
                    "impressions": metric["impressions"],
                    "roas": t_roas,
                    "acos": acos(metric["spend"], metric["sales"]),
                    "ctr": (metric["clicks"] / metric["impressions"]) if metric["impressions"] else 0.0,
                    "cvr": cvr(metric["orders"], metric["clicks"]),
                    "roas_delta_vs_campaign": t_roas - c_roas,
                }
            )

        for campaign in by_campaign:
            by_campaign[campaign].sort(key=lambda x: float(x["spend"]), reverse=True)
            by_campaign[campaign] = by_campaign[campaign][:top_n]

        return dict(by_campaign)
