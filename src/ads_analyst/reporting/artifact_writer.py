from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from ..domain.models import DrilldownReport


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {k: _to_jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_jsonable(v) for v in value]
    return value


def _slug(text: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in text.lower())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "all"


def write_report_artifacts(
    report: DrilldownReport,
    markdown: str,
    output_root: Path,
    campaign_filter: str | None,
    start_date: str | None,
    end_date: str | None,
    lang: str = "zh",
) -> dict[str, str]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_root / f"run_{timestamp}_{_slug(campaign_filter or 'all')}"
    run_dir.mkdir(parents=True, exist_ok=True)

    report_json = _to_jsonable(report)

    files = {
        "report_markdown": run_dir / "report.md",
        "report_json": run_dir / "report.json",
        "campaign_kpis_json": run_dir / "campaign_kpis.json",
        "campaign_comparison_json": run_dir / "campaign_comparison.json",
        "placement_breakdown_json": run_dir / "placement_breakdown.json",
        "search_term_breakdown_json": run_dir / "search_term_breakdown.json",
        "targeting_breakdown_json": run_dir / "targeting_breakdown.json",
        "findings_json": run_dir / "findings.json",
        "actions_json": run_dir / "actions.json",
        "analysis_trace_json": run_dir / "analysis_trace.json",
        "manifest_json": run_dir / "manifest.json",
    }

    files["report_markdown"].write_text(markdown, encoding="utf-8")
    files["report_json"].write_text(json.dumps(report_json, ensure_ascii=False, indent=2), encoding="utf-8")
    files["campaign_kpis_json"].write_text(
        json.dumps(report_json.get("campaign_kpis", []), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    files["campaign_comparison_json"].write_text(
        json.dumps(report_json.get("campaign_comparison", []), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    files["placement_breakdown_json"].write_text(
        json.dumps(report_json.get("placement_breakdown", {}), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    files["search_term_breakdown_json"].write_text(
        json.dumps(report_json.get("search_term_breakdown", {}), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    files["targeting_breakdown_json"].write_text(
        json.dumps(report_json.get("targeting_breakdown", {}), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    files["findings_json"].write_text(
        json.dumps(report_json.get("findings", []), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    files["actions_json"].write_text(
        json.dumps(report_json.get("actions", []), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    files["analysis_trace_json"].write_text(
        json.dumps(report_json.get("analysis_trace", []), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "date_range": report.date_range,
        "campaign_filter": campaign_filter,
        "start_date": start_date,
        "end_date": end_date,
        "language": lang,
        "abnormal_campaign_count": len(report.abnormal_campaigns),
        "finding_count": len(report.findings),
        "action_count": len(report.actions),
        "files": {k: str(v) for k, v in files.items()},
        "note": "analysis_trace is a structured audit log, not private model chain-of-thought.",
    }
    files["manifest_json"].write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "run_dir": str(run_dir),
        **{k: str(v) for k, v in files.items()},
    }
