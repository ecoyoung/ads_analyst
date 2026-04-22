# Metric Formulas

Use these formulas when source fields are missing, null, or inconsistent.

## Base Fields

- `spend` = normalized spend from mapping files
- `sales` = normalized sales from mapping files
- `orders` = normalized orders from mapping files
- `clicks` = clicks
- `impressions` = impressions

## Base Field Labels (CN)

| 统一字段 | 中文字段名 | 含义 |
|---|---|---|
| `spend` | 花费 | 广告消耗金额 |
| `sales` | 归因销售额 | 广告归因销售金额 |
| `orders` | 归因订单量 | 广告归因订单数 |
| `clicks` | 点击量 | 点击次数 |
| `impressions` | 展示量 | 展示次数 |
| `budget_amount` | 活动预算 | 预算金额 |

## Formulas

- `CTR = clicks / impressions`
- `CPC = spend / clicks`
- `CVR = orders / clicks`
- `ACOS = spend / sales`
- `ROAS = sales / spend`
- `CPA = spend / orders`
- `budget_utilization = spend / budget_amount`

## Safety Rules

1. If denominator is 0, return 0 (or null if report explicitly requires null).
2. Use consistent attribution window within a report:
- SP: 14-day clicks-attributed (`sales14d`, `purchases14d`)
- SB: clicks-attributed (`sales_clicks`, `purchases_clicks`) first
3. Do not mix raw precomputed and recalculated metrics within the same section without marking it.

## Suggested Anomaly Thresholds

- CVR shock: `daily_cvr < mean_14d_cvr * 0.6`
- CPC spike: `daily_cpc > mean_14d_cpc * 1.5`
- impression crash: `daily_impressions < mean_14d_impressions * 0.4`
- zero-return spend: `spend > 20 and sales = 0`
