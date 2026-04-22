---
name: amazon-placement-analysis
description: Analyze Amazon Ads placement performance as a drill-down step for abnormal campaigns. Use this skill when campaign analysis detects performance issues and needs placement-level root-cause diagnosis and budget reallocation guidance.
---

# Amazon Placement Analysis

## Purpose

This skill diagnoses placement-level performance for specific campaigns flagged by campaign analysis.

## Input Contract

Required inputs:
- campaign list (campaign_id or campaign_name)
- date range
- anomaly context from campaign layer (for example ROAS drop, CVR drop, CPC spike)

## Required References

1. [placement field mapping](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/references/field-mapping-placement.md)
2. [metric formulas](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/references/metric-formulas.md)
3. [routing rules](/Users/anker/Documents/ads_analyst/skills/custom/amazon-ads-drilldown-analysis/references/drilldown-routing-rules.md)

## Workflow

1. Aggregate by campaign and placement.
2. Compute placement metrics (spend share, ROAS, ACOS, CVR, CTR).
3. Identify efficiency gaps across placements.
4. Output concrete reallocation actions linked to campaign anomalies.

## Guardrails

- Do not run this as a standalone strategy report without campaign anomaly context.
- Do not produce broad recommendations without campaign-specific evidence.

