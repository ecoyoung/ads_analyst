from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from ..config import load_database_config
from ..database import DatabaseClient
from ..orchestrator.drilldown_orchestrator import DrilldownOrchestrator
from ..reporting.artifact_writer import write_report_artifacts
from ..reporting.markdown_renderer import render_campaign_table, render_drilldown_report
from ..shared.rules import ThresholdRules, load_threshold_rules


def _parse_date(raw: str | None):
    if not raw:
        return None
    return datetime.strptime(raw, "%Y-%m-%d").date()


def cmd_db_check(db: DatabaseClient) -> int:
    print("== Database Connectivity ==")
    print(db.ping())
    print()

    if not db.config.tables:
        print("database.md has no configured tables.")
        return 0

    print("== Configured Table Status ==")
    for row in db.list_table_status(db.config.tables):
        if not row.exists:
            print(f"- {row.table_name}: NOT FOUND")
        else:
            print(f"- {row.table_name}: OK, rows={row.row_count}")
    return 0


def cmd_campaign_summary(
    db: DatabaseClient,
    rules: ThresholdRules,
    start_date: str | None,
    end_date: str | None,
    campaign_filter: str | None,
    output_root: str,
    lang: str,
) -> int:
    orchestrator = DrilldownOrchestrator(db, rules=rules)
    report = orchestrator.run(
        start_date=_parse_date(start_date),
        end_date=_parse_date(end_date),
        campaign_filter=campaign_filter,
    )
    markdown = render_campaign_table(report.campaign_kpis, lang=lang)
    artifacts = write_report_artifacts(
        report=report,
        markdown=markdown,
        output_root=Path(output_root),
        campaign_filter=campaign_filter,
        start_date=start_date,
        end_date=end_date,
        lang=lang,
    )
    print(markdown)
    print()
    print(f"Artifacts saved: {artifacts['run_dir']}")
    return 0


def cmd_drilldown_report(
    db: DatabaseClient,
    rules: ThresholdRules,
    start_date: str | None,
    end_date: str | None,
    campaign_filter: str | None,
    output_root: str,
    lang: str,
) -> int:
    orchestrator = DrilldownOrchestrator(db, rules=rules)
    report = orchestrator.run(
        start_date=_parse_date(start_date),
        end_date=_parse_date(end_date),
        campaign_filter=campaign_filter,
    )
    markdown = render_drilldown_report(report, lang=lang)
    artifacts = write_report_artifacts(
        report=report,
        markdown=markdown,
        output_root=Path(output_root),
        campaign_filter=campaign_filter,
        start_date=start_date,
        end_date=end_date,
        lang=lang,
    )
    print(markdown)
    print()
    print(f"Artifacts saved: {artifacts['run_dir']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ads Analyst (DeerFlow-style multi-agent architecture)"
    )
    parser.add_argument(
        "--config",
        default="database.toml",
        help="Database config file path (.toml recommended), default is database.toml",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("db-check", help="Validate database connectivity and configured tables")

    campaign = sub.add_parser("campaign-summary", help="Campaign KPI summary")
    campaign.add_argument("--start-date", help="Start date, format YYYY-MM-DD")
    campaign.add_argument("--end-date", help="End date, format YYYY-MM-DD")
    campaign.add_argument("--campaign-filter", help="Filter campaign by name keyword")
    campaign.add_argument(
        "--thresholds",
        default="thresholds.toml",
        help="Threshold rules config path, default is thresholds.toml",
    )
    campaign.add_argument(
        "--output-root",
        default="outputs",
        help="Output root for generated markdown/json artifacts, default is outputs",
    )
    campaign.add_argument(
        "--lang",
        choices=["zh", "en"],
        default="zh",
        help="Report language, default is zh",
    )

    drilldown = sub.add_parser(
        "drilldown-report",
        help="Campaign-first multi-layer drilldown (campaign -> placement/search-term/targeting)",
    )
    drilldown.add_argument("--start-date", help="Start date, format YYYY-MM-DD")
    drilldown.add_argument("--end-date", help="End date, format YYYY-MM-DD")
    drilldown.add_argument("--campaign-filter", help="Filter campaign by name keyword")
    drilldown.add_argument(
        "--thresholds",
        default="thresholds.toml",
        help="Threshold rules config path, default is thresholds.toml",
    )
    drilldown.add_argument(
        "--output-root",
        default="outputs",
        help="Output root for generated markdown/json artifacts, default is outputs",
    )
    drilldown.add_argument(
        "--lang",
        choices=["zh", "en"],
        default="zh",
        help="Report language, default is zh",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = load_database_config(Path(args.config))
    db = DatabaseClient(config)

    if args.command == "db-check":
        return cmd_db_check(db)
    if args.command == "campaign-summary":
        rules = load_threshold_rules(Path(args.thresholds))
        return cmd_campaign_summary(
            db=db,
            rules=rules,
            start_date=args.start_date,
            end_date=args.end_date,
            campaign_filter=args.campaign_filter,
            output_root=args.output_root,
            lang=args.lang,
        )
    if args.command == "drilldown-report":
        rules = load_threshold_rules(Path(args.thresholds))
        return cmd_drilldown_report(
            db=db,
            rules=rules,
            start_date=args.start_date,
            end_date=args.end_date,
            campaign_filter=args.campaign_filter,
            output_root=args.output_root,
            lang=args.lang,
        )

    raise ValueError(f"Unknown command: {args.command}")
