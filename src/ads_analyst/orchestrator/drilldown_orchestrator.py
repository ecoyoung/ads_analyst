from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import statistics

from ..agents.campaign_agent import CampaignAgent
from ..agents.placement_agent import PlacementAgent
from ..agents.search_term_agent import SearchTermAgent
from ..agents.targeting_agent import TargetingAgent
from ..database import DatabaseClient
from ..domain.models import DrilldownFinding, DrilldownReport
from ..shared.rules import ThresholdRules, default_threshold_rules


@dataclass(frozen=True)
class TableRegistry:
    campaign_tables: tuple[str, ...]
    placement_tables: tuple[str, ...]
    search_term_tables: tuple[str, ...]
    targeting_tables: tuple[str, ...]


def infer_table_registry(config_tables: tuple[str, ...]) -> TableRegistry:
    lower = [t.lower() for t in config_tables]

    def pick(*tokens: str) -> tuple[str, ...]:
        chosen = []
        for original, lowered in zip(config_tables, lower):
            if all(token in lowered for token in tokens):
                chosen.append(original)
        return tuple(chosen)

    def pick_campaign_tables() -> tuple[str, ...]:
        chosen = []
        for original, lowered in zip(config_tables, lower):
            if "campaign" not in lowered:
                continue
            if "placement" in lowered:
                continue
            chosen.append(original)
        return tuple(chosen)

    return TableRegistry(
        campaign_tables=pick_campaign_tables() if config_tables else (),
        placement_tables=pick("campaign", "placement") if config_tables else (),
        search_term_tables=pick("search", "term") if config_tables else (),
        targeting_tables=pick("targeting") if config_tables else (),
    )


class DrilldownOrchestrator:
    def __init__(self, db: DatabaseClient, rules: ThresholdRules | None = None):
        self.db = db
        self.rules = rules or default_threshold_rules()
        self.campaign_agent = CampaignAgent(db, thresholds=self.rules.campaign)
        self.placement_agent = PlacementAgent(db, thresholds=self.rules.placement)
        self.search_term_agent = SearchTermAgent(db, thresholds=self.rules.search_term)
        self.targeting_agent = TargetingAgent(db, thresholds=self.rules.targeting)

    def run(
        self,
        start_date: date | None,
        end_date: date | None,
        campaign_filter: str | None = None,
    ) -> DrilldownReport:
        trace: list[dict[str, object]] = []
        registry = infer_table_registry(self.db.config.tables)
        trace.append(
            {
                "step": "resolve_tables",
                "campaign_tables": list(registry.campaign_tables),
                "placement_tables": list(registry.placement_tables),
                "search_term_tables": list(registry.search_term_tables),
                "targeting_tables": list(registry.targeting_tables),
            }
        )

        campaign_tables = list(registry.campaign_tables)
        if not campaign_tables:
            raise ValueError("未在配置表中找到 campaign 表，请检查 database.md 的数据表配置。")

        campaign_kpis = self.campaign_agent.analyze(
            tables=campaign_tables,
            start_date=start_date,
            end_date=end_date,
        )
        trace.append(
            {
                "step": "campaign_screening",
                "campaign_count_before_filter": len(campaign_kpis),
            }
        )

        if campaign_filter:
            campaign_kpis = [item for item in campaign_kpis if campaign_filter.lower() in item.campaign_name.lower()]
            trace.append(
                {
                    "step": "campaign_filter",
                    "campaign_filter": campaign_filter,
                    "campaign_count_after_filter": len(campaign_kpis),
                }
            )

        abnormal_campaigns = [item.campaign_name for item in campaign_kpis if item.anomalies]
        trace.append(
            {
                "step": "abnormal_detection",
                "abnormal_campaigns": abnormal_campaigns,
                "routing_rule": "campaign anomalies trigger placement/search-term/targeting drilldown",
            }
        )

        findings: list[DrilldownFinding] = []
        placement_breakdown: dict[str, tuple[dict[str, object], ...]] = {}
        search_term_breakdown: dict[str, tuple[dict[str, object], ...]] = {}
        targeting_breakdown: dict[str, tuple[dict[str, object], ...]] = {}
        if abnormal_campaigns:
            findings.extend(
                self.placement_agent.analyze(
                    tables=list(registry.placement_tables),
                    campaigns=abnormal_campaigns,
                    start_date=start_date,
                    end_date=end_date,
                )
            )
            placement_breakdown = {
                k: tuple(v)
                for k, v in self.placement_agent.summarize_breakdown(
                    tables=list(registry.placement_tables),
                    campaigns=abnormal_campaigns,
                    start_date=start_date,
                    end_date=end_date,
                ).items()
            }
            findings.extend(
                self.search_term_agent.analyze(
                    tables=list(registry.search_term_tables),
                    campaigns=abnormal_campaigns,
                    start_date=start_date,
                    end_date=end_date,
                )
            )
            search_term_breakdown = {
                k: tuple(v)
                for k, v in self.search_term_agent.summarize_breakdown(
                    tables=list(registry.search_term_tables),
                    campaigns=abnormal_campaigns,
                    start_date=start_date,
                    end_date=end_date,
                ).items()
            }
            findings.extend(
                self.targeting_agent.analyze(
                    tables=list(registry.targeting_tables),
                    campaigns=abnormal_campaigns,
                    start_date=start_date,
                    end_date=end_date,
                )
            )
            targeting_breakdown = {
                k: tuple(v)
                for k, v in self.targeting_agent.summarize_breakdown(
                    tables=list(registry.targeting_tables),
                    campaigns=abnormal_campaigns,
                    start_date=start_date,
                    end_date=end_date,
                ).items()
            }
            trace.append(
                {
                    "step": "drilldown_layers",
                    "placement_rows": {k: len(v) for k, v in placement_breakdown.items()},
                    "search_term_rows": {k: len(v) for k, v in search_term_breakdown.items()},
                    "targeting_rows": {k: len(v) for k, v in targeting_breakdown.items()},
                }
            )

        actions = self._build_action_list(findings)
        range_text = f"{start_date or 'ALL'} ~ {end_date or 'ALL'}"
        campaign_comparison = self._build_campaign_comparison(campaign_kpis)
        trace.append(
            {
                "step": "synthesis",
                "finding_count": len(findings),
                "action_count": len(actions),
            }
        )

        notes = []
        if not abnormal_campaigns:
            notes.append("No abnormal campaigns detected by routing rules.")

        return DrilldownReport(
            date_range=range_text,
            campaign_kpis=tuple(campaign_kpis),
            abnormal_campaigns=tuple(abnormal_campaigns),
            findings=tuple(findings),
            actions=tuple(actions),
            notes=tuple(notes),
            campaign_comparison=tuple(campaign_comparison),
            placement_breakdown=placement_breakdown,
            search_term_breakdown=search_term_breakdown,
            targeting_breakdown=targeting_breakdown,
            analysis_trace=tuple(trace),
        )

    def _build_action_list(self, findings: list[DrilldownFinding]) -> list[str]:
        actions: list[str] = []
        seen: set[str] = set()
        for finding in sorted(findings, key=lambda x: (x.priority, x.campaign_name, x.layer)):
            action_text = f"[{finding.priority}] {finding.campaign_name} / {finding.layer}: {finding.action}"
            if action_text in seen:
                continue
            seen.add(action_text)
            actions.append(action_text)
        return actions

    def _build_campaign_comparison(self, campaign_kpis: list) -> list[dict[str, object]]:
        if not campaign_kpis:
            return []

        roas_values = [item.roas for item in campaign_kpis]
        acos_values = [item.acos for item in campaign_kpis]
        cvr_values = [item.cvr for item in campaign_kpis]
        ctr_values = [item.ctr for item in campaign_kpis]
        cpc_values = [item.cpc for item in campaign_kpis]
        spend_values = [item.spend for item in campaign_kpis]

        roas_median = statistics.median(roas_values)
        acos_median = statistics.median(acos_values)
        cvr_median = statistics.median(cvr_values)
        ctr_median = statistics.median(ctr_values)
        cpc_median = statistics.median(cpc_values)
        spend_median = statistics.median(spend_values)

        by_spend_rank = {item.campaign_name: idx + 1 for idx, item in enumerate(campaign_kpis)}

        rows: list[dict[str, object]] = []
        for item in campaign_kpis:
            anomaly_reasons: list[str] = []
            if item.anomalies:
                if item.roas < roas_median:
                    anomaly_reasons.append(f"ROAS below peer median ({item.roas:.2f} < {roas_median:.2f})")
                if item.acos > acos_median:
                    anomaly_reasons.append(f"ACOS above peer median ({item.acos:.2%} > {acos_median:.2%})")
                if item.cvr < cvr_median:
                    anomaly_reasons.append(f"CVR below peer median ({item.cvr:.2%} < {cvr_median:.2%})")
                if item.cpc > cpc_median:
                    anomaly_reasons.append(f"CPC above peer median ({item.cpc:.2f} > {cpc_median:.2f})")
                if item.ctr < ctr_median:
                    anomaly_reasons.append(f"CTR below peer median ({item.ctr:.2%} < {ctr_median:.2%})")

            rows.append(
                {
                    "campaign": item.campaign_name,
                    "spend_rank": by_spend_rank[item.campaign_name],
                    "spend": item.spend,
                    "spend_vs_median": item.spend - spend_median,
                    "roas": item.roas,
                    "roas_vs_median": item.roas - roas_median,
                    "acos": item.acos,
                    "acos_vs_median": item.acos - acos_median,
                    "cvr": item.cvr,
                    "cvr_vs_median": item.cvr - cvr_median,
                    "ctr": item.ctr,
                    "ctr_vs_median": item.ctr - ctr_median,
                    "cpc": item.cpc,
                    "cpc_vs_median": item.cpc - cpc_median,
                    "anomalies": list(item.anomalies),
                    "anomaly_reasons_vs_peers": anomaly_reasons,
                }
            )

        return rows
