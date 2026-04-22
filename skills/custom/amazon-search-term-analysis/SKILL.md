---
name: amazon-search-term-analysis
description: Analyze Amazon Ads search term performance as a drill-down step for abnormal campaigns. Use this skill when campaign analysis detects conversion or efficiency decline and needs term-level root-cause diagnosis, negative keyword candidates, and bid optimization suggestions.
---

# Amazon Search Term Analysis

## Purpose

This skill diagnoses search-term-level causes for campaign anomalies.

## Input Contract

Required inputs:
- campaign list (campaign_id or campaign_name)
- date range
- anomaly context from campaign layer

## Required References

1. [search term field mapping](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/references/field-mapping-search-term.md)
2. [metric formulas](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/references/metric-formulas.md)
3. [routing rules](/Users/anker/Documents/ads_analyst/skills/custom/amazon-ads-drilldown-analysis/references/drilldown-routing-rules.md)

## Workflow

1. Aggregate by campaign, search_term, and match_type.
2. Compute term metrics (spend, sales, orders, ROAS, ACOS, CVR, CPC).
3. Identify:
- high-spend low-return terms
- zero-sales terms with meaningful spend
- match-type drift
- bid inefficiency pockets
4. Output campaign-linked actions:
- negative keyword candidates
- bid down/up lists
- match-type migration suggestions

## Guardrails

- Do not run this as an isolated report detached from campaign anomalies.
- Do not suggest negatives or bid actions without spend and conversion evidence.

