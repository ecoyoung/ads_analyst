---
name: amazon-campaign-analysis
description: Analyze Amazon Ads campaign performance from PostgreSQL data and act as the entry point of drill-down diagnostics. Use this skill for campaign review, trend diagnosis, budget allocation, and anomaly detection that must trigger placement, search-term, and targeting drill-down for abnormal campaigns.
---

# Amazon Campaign Analysis

## Role in Architecture

This skill is the campaign-layer entry skill, not the final standalone conclusion layer.

It must:
1. Find abnormal campaigns.
2. Trigger placement, search-term, and targeting drill-down for those campaigns.
3. Merge findings into root-cause-based recommendations.

## Related Skills

- [amazon-ads-drilldown-analysis](/Users/anker/Documents/ads_analyst/skills/custom/amazon-ads-drilldown-analysis/SKILL.md)
- [amazon-placement-analysis](/Users/anker/Documents/ads_analyst/skills/custom/amazon-placement-analysis/SKILL.md)
- [amazon-search-term-analysis](/Users/anker/Documents/ads_analyst/skills/custom/amazon-search-term-analysis/SKILL.md)
- [amazon-targeting-analysis](/Users/anker/Documents/ads_analyst/skills/custom/amazon-targeting-analysis/SKILL.md)

## Data Scope

Campaign layer primary tables:
- `amazon_ads_sp_campaigns_innerbrightness`
- `amazon_ads_sb_campaigns_innerbrightness`

Drill-down layers (required for abnormal campaigns):
- `amazon_ads_sp_campaign_placement_innerbrightness`
- `amazon_ads_sb_campaign_placement_innerbrightness`
- `amazon_ads_sp_search_term_innerbrightness`
- `amazon_ads_sb_search_term_innerbrightness`
- `amazon_ads_sp_targeting_innerbrightness`
- `amazon_ads_sb_targeting_innerbrightness`

## Required References

1. [field-mapping-campaign.md](references/field-mapping-campaign.md)
2. [field-mapping-placement.md](references/field-mapping-placement.md)
3. [field-mapping-search-term.md](references/field-mapping-search-term.md)
4. [field-mapping-targeting.md](references/field-mapping-targeting.md)
5. [metric-formulas.md](references/metric-formulas.md)
6. [skill architecture](/Users/anker/Documents/ads_analyst/skills/custom/amazon-ads-drilldown-analysis/references/skill-architecture.md)
7. [routing rules](/Users/anker/Documents/ads_analyst/skills/custom/amazon-ads-drilldown-analysis/references/drilldown-routing-rules.md)

## Workflow

### Step 1: Campaign screening

At campaign level compute:
- Spend, Sales, Orders, Impressions, Clicks
- CTR, CPC, CVR, ACOS, ROAS
- budget utilization
- first 7 days vs last 7 days trends

### Step 2: Identify abnormal campaigns

Use routing rules to tag abnormal campaigns.

### Step 3: Mandatory drill-down

For each abnormal campaign:
1. run placement diagnostic
2. run search-term diagnostic
3. run targeting diagnostic
4. map findings back to campaign anomaly

### Step 4: Synthesis and actions

Output only root-cause-linked actions:
- budget reallocation
- bid tuning
- negative keyword actions
- placement mix adjustments

## Output Contract

Output must include:
1. campaign KPI summary
2. abnormal campaign list
3. campaign -> placement root cause links
4. campaign -> search-term root cause links
5. campaign -> targeting root cause links
6. prioritized actions (P0/P1) with expected impact

## Guardrails

- Never output final recommendations from campaign table alone when anomalies exist.
- Never run placement, search term, or targeting as detached flat reports.
- Every action must reference a specific campaign and evidence metric.
