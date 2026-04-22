from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .agents.campaign_agent import CampaignAgent
from .database import DatabaseClient


@dataclass(frozen=True)
class CampaignSummary:
    campaign: str
    impressions: float
    clicks: float
    spend: float
    sales: float
    orders: float

    @property
    def ctr(self) -> float:
        return self.clicks / self.impressions if self.impressions else 0.0

    @property
    def cpc(self) -> float:
        return self.spend / self.clicks if self.clicks else 0.0

    @property
    def cvr(self) -> float:
        return self.orders / self.clicks if self.clicks else 0.0

    @property
    def acos(self) -> float:
        return self.spend / self.sales if self.sales else 0.0

    @property
    def roas(self) -> float:
        return self.sales / self.spend if self.spend else 0.0


def summarize_campaigns(
    db: DatabaseClient,
    table: str,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[CampaignSummary]:
    agent = CampaignAgent(db)
    rows = agent.analyze(
        tables=[table],
        start_date=start_date,
        end_date=end_date,
    )

    return [
        CampaignSummary(
            campaign=item.campaign_name,
            impressions=item.impressions,
            clicks=item.clicks,
            spend=item.spend,
            sales=item.sales,
            orders=item.orders,
        )
        for item in rows
    ]


def render_summary_markdown(rows: list[CampaignSummary]) -> str:
    if not rows:
        return "无可用数据。"

    lines = [
        "| Campaign | Spend | Sales | Orders | Impressions | Clicks | CTR | CVR | ACoS | ROAS |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for r in rows:
        lines.append(
            "| {campaign} | ${spend:.2f} | ${sales:.2f} | {orders:.0f} | {impressions:.0f} | "
            "{clicks:.0f} | {ctr:.2%} | {cvr:.2%} | {acos:.2%} | {roas:.2f} |".format(
                campaign=r.campaign,
                spend=r.spend,
                sales=r.sales,
                orders=r.orders,
                impressions=r.impressions,
                clicks=r.clicks,
                ctr=r.ctr,
                cvr=r.cvr,
                acos=r.acos,
                roas=r.roas,
            )
        )

    return "\n".join(lines)
