from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from .base import BaseAnalysisAgent
from ..domain.models import CampaignKPI
from ..shared.metrics import acos, cpc, ctr, cvr, roas, safe_float
from ..shared.rules import CampaignThresholds


class CampaignAgent(BaseAnalysisAgent):
    layer = "campaign"

    def __init__(self, db, thresholds: CampaignThresholds | None = None):
        super().__init__(db)
        self.thresholds = thresholds or CampaignThresholds()

    def analyze(
        self,
        tables: list[str],
        start_date: date | None,
        end_date: date | None,
    ) -> list[CampaignKPI]:
        campaign_totals: dict[str, dict[str, float]] = defaultdict(
            lambda: {
                "spend": 0.0,
                "sales": 0.0,
                "orders": 0.0,
                "impressions": 0.0,
                "clicks": 0.0,
                "budget": 0.0,
            }
        )
        daily: dict[str, dict[date, dict[str, float]]] = defaultdict(
            lambda: defaultdict(lambda: {"spend": 0.0, "sales": 0.0, "orders": 0.0, "clicks": 0.0})
        )

        for table in tables:
            rows, mapping = self._read_rows(table=table, start_date=start_date, end_date=end_date)
            if not rows:
                continue

            date_column = mapping.get("date")
            for row in rows:
                campaign = str(row.get(mapping["campaign_name"], "")).strip() or "UNKNOWN"
                totals = campaign_totals[campaign]
                spend = safe_float(row.get(mapping.get("spend", "")))
                sales = safe_float(row.get(mapping.get("sales", "")))
                orders = safe_float(row.get(mapping.get("orders", "")))
                impressions = safe_float(row.get(mapping.get("impressions", "")))
                clicks = safe_float(row.get(mapping.get("clicks", "")))
                budget = safe_float(row.get(mapping.get("budget", "")))

                totals["spend"] += spend
                totals["sales"] += sales
                totals["orders"] += orders
                totals["impressions"] += impressions
                totals["clicks"] += clicks
                totals["budget"] += budget

                if date_column:
                    day = self._safe_date(row.get(date_column))
                    if day:
                        d = daily[campaign][day]
                        d["spend"] += spend
                        d["sales"] += sales
                        d["orders"] += orders
                        d["clicks"] += clicks

        items: list[CampaignKPI] = []
        for campaign, totals in campaign_totals.items():
            spend = totals["spend"]
            sales = totals["sales"]
            orders = totals["orders"]
            impressions = totals["impressions"]
            clicks = totals["clicks"]
            budget = totals["budget"]

            metric_ctr = ctr(clicks, impressions)
            metric_cpc = cpc(spend, clicks)
            metric_cvr = cvr(orders, clicks)
            metric_acos = acos(spend, sales)
            metric_roas = roas(sales, spend)
            budget_utilization = spend / budget if budget else 0.0

            anomalies = self._detect_anomalies(
                spend=spend,
                sales=sales,
                metric_acos=metric_acos,
                metric_roas=metric_roas,
                daily_series=daily.get(campaign, {}),
            )

            items.append(
                CampaignKPI(
                    campaign_name=campaign,
                    spend=spend,
                    sales=sales,
                    orders=orders,
                    impressions=impressions,
                    clicks=clicks,
                    ctr=metric_ctr,
                    cpc=metric_cpc,
                    cvr=metric_cvr,
                    acos=metric_acos,
                    roas=metric_roas,
                    budget_utilization=budget_utilization,
                    anomalies=tuple(anomalies),
                )
            )

        items.sort(key=lambda x: x.spend, reverse=True)
        return items

    def _detect_anomalies(
        self,
        spend: float,
        sales: float,
        metric_acos: float,
        metric_roas: float,
        daily_series: dict[date, dict[str, float]],
    ) -> list[str]:
        anomalies: list[str] = []

        if metric_roas < self.thresholds.roas_lt:
            anomalies.append("ROAS<1")
        if metric_acos > self.thresholds.acos_gt:
            anomalies.append("ACOS>1")
        if spend > self.thresholds.spend_sales_zero_spend_gt and sales == 0:
            anomalies.append("Spend>100_and_Sales=0")

        if len(daily_series) >= self.thresholds.min_days_for_trend:
            days = sorted(daily_series.keys())
            split = max(1, len(days) // 2)
            first = days[:split]
            last = days[split:]
            first_cvr = self._avg_ratio(daily_series, first, "orders", "clicks")
            last_cvr = self._avg_ratio(daily_series, last, "orders", "clicks")
            first_cpc = self._avg_ratio(daily_series, first, "spend", "clicks")
            last_cpc = self._avg_ratio(daily_series, last, "spend", "clicks")

            if first_cvr > 0 and last_cvr < first_cvr * self.thresholds.cvr_drop_factor:
                anomalies.append("CVR_drop_30pct")
            if first_cpc > 0 and last_cpc > first_cpc * self.thresholds.cpc_rise_factor:
                anomalies.append("CPC_rise_30pct")

        return anomalies

    def _avg_ratio(
        self,
        daily_series: dict[date, dict[str, float]],
        days: list[date],
        numerator_key: str,
        denominator_key: str,
    ) -> float:
        if not days:
            return 0.0

        numerator_sum = 0.0
        denominator_sum = 0.0
        for day in days:
            row = daily_series[day]
            numerator_sum += row[numerator_key]
            denominator_sum += row[denominator_key]

        if denominator_sum == 0:
            return 0.0
        return numerator_sum / denominator_sum
