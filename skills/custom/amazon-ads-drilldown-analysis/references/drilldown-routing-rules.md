# Drill-Down Routing Rules

## Campaign -> Drill-Down Trigger

Trigger drill-down when any campaign meets one or more conditions:

- `ROAS < 1`
- `ACOS > 1`
- `CVR` drops by more than 30% versus campaign 14-day average
- `CPC` rises by more than 30% versus campaign 14-day average
- `Spend > $100` and `Sales = 0`

## Mandatory Drill-Down Path

For each abnormal campaign:

1. Run placement drill-down:
- check spend share by placement
- identify low-efficiency placement buckets

2. Run search-term drill-down:
- identify high-spend low-sales terms
- identify zero-sales terms
- identify match-type drift and bid inefficiency

3. Run targeting drill-down:
- identify high-spend low-sales targets
- identify zero-sales targets
- identify targeting expression mismatch and bid inefficiency

4. Synthesize:
- determine whether root cause is placement structure, term quality, bid, or mixed factors
- determine whether targeting structure or targeting expression quality is a key driver

## Prohibited Pattern

- Full campaign report
- Separate placement report
- Separate search term report
- Separate targeting report
- No per-campaign causal linkage

This pattern is invalid and must not be used.
