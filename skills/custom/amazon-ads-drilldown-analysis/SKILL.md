---
name: amazon-ads-drilldown-analysis
description: Orchestrate Amazon Ads diagnostics with linked drill-down analysis. Use this skill when users ask for ad performance analysis, campaign review, optimization strategy, or root-cause diagnosis. This skill enforces campaign-first analysis and mandatory placement plus search-term plus targeting drill-down for abnormal campaigns.
---

# Amazon Ads Drill-Down Analysis

## Purpose

This is the top-level orchestration skill for ads analysis.

It enforces one workflow:
1. Campaign screening
2. Abnormal campaign identification
3. Placement, Search Term, and Targeting drill-down for abnormal campaigns
4. Root-cause synthesis and action plan

## Related Skills

- [amazon-campaign-analysis](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/SKILL.md)
- [amazon-placement-analysis](/Users/anker/Documents/ads_analyst/skills/custom/amazon-placement-analysis/SKILL.md)
- [amazon-search-term-analysis](/Users/anker/Documents/ads_analyst/skills/custom/amazon-search-term-analysis/SKILL.md)
- [amazon-targeting-analysis](/Users/anker/Documents/ads_analyst/skills/custom/amazon-targeting-analysis/SKILL.md)

## Required References

1. [skill-architecture.md](references/skill-architecture.md)
2. [drilldown-routing-rules.md](references/drilldown-routing-rules.md)
3. [campaign field mapping](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/references/field-mapping-campaign.md)
4. [placement field mapping](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/references/field-mapping-placement.md)
5. [search term field mapping](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/references/field-mapping-search-term.md)
6. [targeting field mapping](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/references/field-mapping-targeting.md)
7. [metric formulas](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/references/metric-formulas.md)

## Hard Rules

- Never analyze placement, search term, or targeting as isolated reports without campaign context.
- Never end campaign analysis before completing drill-down for abnormal campaigns.
- Every optimization recommendation must map to a diagnosed root cause.
