---
name: amazon-targeting-analysis
description: Analyze Amazon Ads targeting performance as a drill-down step for abnormal campaigns. Use this skill when campaign analysis detects efficiency or conversion decline and needs targeting-level root-cause diagnosis, bid adjustment guidance, and targeting expression optimization.
---

# Amazon Targeting Analysis

## Purpose

This skill diagnoses targeting-level causes for campaign anomalies.

## Input Contract

Required inputs:
- campaign list (campaign_id or campaign_name)
- date range
- anomaly context from campaign layer

## Required References

1. [targeting field mapping](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/references/field-mapping-targeting.md)
2. [metric formulas](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/references/metric-formulas.md)
3. [routing rules](/Users/anker/Documents/ads_analyst/skills/custom/amazon-ads-drilldown-analysis/references/drilldown-routing-rules.md)

## Workflow

1. Aggregate by campaign and targeting entity.
2. Compute targeting metrics (spend, sales, orders, ROAS, ACOS, CVR, CPC, CTR).
3. Identify:
- high-spend low-return targets
- zero-sales targets with meaningful spend
- bid inefficiency and targeting expression mismatch
4. Output campaign-linked actions:
- bid down/up list
- targeting narrowing/expansion suggestions
- targeting expression cleanup suggestions

## Guardrails

- Do not run this as an isolated report detached from campaign anomalies.
- Do not suggest target or bid actions without spend and conversion evidence.

