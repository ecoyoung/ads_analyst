# Field Mapping: Campaign（含中文字段名与含义）

## Scope

- SP 表: `amazon_ads_sp_campaigns_innerbrightness`
- SB 表: `amazon_ads_sb_campaigns_innerbrightness`

## Normalized Mapping

| 统一字段 | SP 字段 | SB 字段 | 中文字段名 | 字段含义 | 口径注意 |
|---|---|---|---|---|---|
| `report_date` | `date` | `date` | 日期 | 报表日期（日粒度） | 作为主过滤日期 |
| `campaign_id` | `campaign_id` | `campaign_id` | 广告活动ID | Campaign 唯一标识 | 与下钻层关联键 |
| `campaign_name` | `campaign_name` | `campaign_name` | 广告活动名称 | 活动名称 | 产品线过滤常用字段 |
| `campaign_status` | `campaign_status` | `campaign_status` | 广告活动状态 | 启用/暂停等状态 | 异常排查必看 |
| `impressions` | `impressions` | `impressions` | 展示量 | 广告展示次数 | CTR 分母 |
| `clicks` | `clicks` | `clicks` | 点击量 | 广告点击次数 | CPC/CVR 分母 |
| `spend` | `spend`（回退 `cost`） | `cost` | 花费 | 广告消耗金额 | SP/SB 字段名不同 |
| `sales` | `sales14d` | `sales_clicks`（回退 `sales`） | 归因销售额 | 广告归因销售额 | SB 优先 clicks 归因 |
| `orders` | `purchases14d` | `purchases_clicks`（回退 `purchases`） | 归因订单量 | 广告归因订单数 | SB 优先 clicks 归因 |
| `budget_amount` | `campaign_budget_amount` | `campaign_budget_amount` | 活动预算 | Campaign 预算金额 | 预算消耗率分母 |
| `budget_type` | `campaign_budget_type` | `campaign_budget_type` | 预算类型 | 日预算/总预算 | 解释预算策略 |
| `ctr_raw` | `click_through_rate` | 派生计算 | 点击率 | 点击/展示 | 建议重算统一口径 |
| `cpc_raw` | `cost_per_click` | 派生计算 | 平均点击花费 | 花费/点击 | 建议重算统一口径 |
| `acos_raw` | `acos_clicks14d` | 派生计算 | ACOS | 花费/销售额 | 缺失则按公式重算 |
| `roas_raw` | `roas_clicks14d` | 派生计算 | ROAS | 销售额/花费 | 缺失则按公式重算 |
| `top_of_search_is` | `top_of_search_impression_share` | `top_of_search_impression_share`（若有） | 搜索顶部展示份额 | Top of Search 竞争力 | EM 抢位关键指标 |
| `bidding_strategy` | `campaign_bidding_strategy` | n/a | 竞价策略 | 动态竞价策略类型 | SP 独有 |

## Fallback Rules

1. 花费字段
- SP: 先 `spend`，空值回退 `cost`
- SB: 使用 `cost`

2. 销售与订单口径
- SP: 使用 14 天点击归因 (`sales14d`, `purchases14d`)
- SB: 优先点击归因 (`sales_clicks`, `purchases_clicks`)

3. 指标重算
- 预计算字段缺失或异常时，按 `metric-formulas.md` 重算

