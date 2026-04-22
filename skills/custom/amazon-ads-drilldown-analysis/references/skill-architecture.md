# Ads Analysis Skill Architecture

## Layered Structure

1. Orchestrator layer
- `amazon-ads-drilldown-analysis`

2. Entry diagnostic layer
- `amazon-campaign-analysis`

3. Drill-down diagnostic layer
- `amazon-placement-analysis`
- `amazon-search-term-analysis`
- `amazon-targeting-analysis`

4. Shared reference layer
- Campaign mapping
- Placement mapping
- Search term mapping
- Targeting mapping
- Metric formulas

## Dependency Graph

`amazon-ads-drilldown-analysis`
-> `amazon-campaign-analysis`
-> (`amazon-placement-analysis` + `amazon-search-term-analysis` + `amazon-targeting-analysis`)
-> synthesis and action plan

## Why This Architecture

- Campaign is the control plane (budget, efficiency, trend, anomaly entry).
- Placement explains traffic-position quality and distribution efficiency.
- Search term explains query-level waste and conversion loss.
- Targeting explains target-level bid/expression quality and structure risk.
- Final recommendations are valid only after cross-validation of all linked layers.
