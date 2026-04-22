# ads_analyst

DeerFlow-style multi-agent architecture for Amazon Ads diagnostics.

## What This Project Does

- Checks PostgreSQL connectivity and table availability
- Runs campaign-first diagnostics
- Enforces mandatory drill-down for abnormal campaigns:
  - Placement
  - Search Term
  - Targeting
- Outputs root-cause-linked action recommendations

## Standardized Architecture

```text
src/ads_analyst
├── app/
│   └── cli.py                     # CLI entry and command routing
├── orchestrator/
│   └── drilldown_orchestrator.py  # campaign -> placement/search-term/targeting orchestration
├── agents/
│   ├── base.py                    # shared data-reading/filtering utilities
│   ├── campaign_agent.py          # campaign screening + anomaly detection
│   ├── placement_agent.py         # placement root-cause analysis
│   ├── search_term_agent.py       # term-level root-cause analysis
│   └── targeting_agent.py         # targeting-level root-cause analysis
├── domain/
│   └── models.py                  # report/kpi/finding data contracts
├── reporting/
│   └── markdown_renderer.py       # markdown output contract
├── shared/
│   ├── column_mapping.py          # unified field alias inference
│   └── metrics.py                 # safe metric formulas
├── infra/
│   └── database.py                # infrastructure compatibility exports
├── config.py                      # load database config (toml/env/legacy markdown + env override)
├── database.py                    # PostgreSQL client
├── campaign_service.py            # backward-compatible summary API
└── cli.py                         # backward-compatible module entry
```

## Install

```bash
pip install -r requirements.txt
```

## Commands

1) DB check

```bash
PYTHONPATH=src python3 -m ads_analyst.cli db-check
```

2) Campaign KPI summary

```bash
PYTHONPATH=src python3 -m ads_analyst.cli campaign-summary --start-date 2026-04-04 --end-date 2026-04-17
```

3) Drilldown report (recommended)

```bash
PYTHONPATH=src python3 -m ads_analyst.cli drilldown-report --start-date 2026-04-04 --end-date 2026-04-17
```

4) Filter by campaign keyword

```bash
PYTHONPATH=src python3 -m ads_analyst.cli drilldown-report --campaign-filter magnesium
```

5) Use custom threshold rules

```bash
PYTHONPATH=src python3 -m ads_analyst.cli drilldown-report --thresholds ./thresholds.toml
```

6) Write markdown + intermediate JSON artifacts for each run

```bash
PYTHONPATH=src python3 -m ads_analyst.cli drilldown-report --output-root ./outputs
```

7) Generate Chinese/English report

```bash
PYTHONPATH=src python3 -m ads_analyst.cli drilldown-report --lang zh
PYTHONPATH=src python3 -m ads_analyst.cli drilldown-report --lang en
```

Per run, the tool writes:
- `report.md`
- `report.json`
- `campaign_kpis.json`
- `campaign_comparison.json`
- `placement_breakdown.json`
- `search_term_breakdown.json`
- `targeting_breakdown.json`
- `findings.json`
- `actions.json`
- `analysis_trace.json` (structured audit log, not hidden model chain-of-thought)
- `manifest.json`

## Config Priority

Recommended config file: `database.toml`.

Supported config formats:
- `.toml` (recommended, mainstream)
- `.env` style key-value file
- legacy `database.md` (backward compatible)

Environment variables override file config:

- `ADS_DB_HOST`
- `ADS_DB_PORT`
- `ADS_DB_NAME`
- `ADS_DB_USER`
- `ADS_DB_PASSWORD`
- `ADS_DB_CHARSET`

### `database.toml` example

```toml
[database]
host = "127.0.0.1"
port = 5432
database = "postgres"
user = "your_db_user"
password = "your_db_password"
charset = "utf8"

[tables]
names = ["amazon_ads_sp_campaigns_innerbrightness"]
```

## Notes

- This repository currently includes skill documentation under `skills/custom/*` that defines a layered drilldown architecture.
- The runtime code now follows the same layered standard and can be extended per skill layer independently.
- Thresholds are centralized in `thresholds.toml` (campaign/placement/search_term/targeting).
