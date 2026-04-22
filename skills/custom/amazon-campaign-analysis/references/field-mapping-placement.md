# Field Mapping: Placement（含中文字段名与含义）

## Scope

- SP 表: `amazon_ads_sp_campaign_placement_innerbrightness`
- SB 表: `amazon_ads_sb_campaign_placement_innerbrightness`

## Normalized Mapping

| 统一字段 | SP 字段 | SB 字段 | 中文字段名 | 字段含义 | 口径注意 |
|---|---|---|---|---|---|
| `report_date` | `date` | `date` | 日期 | 报表日期（日粒度） | 主过滤日期 |
| `campaign_id` | `campaign_id` | `campaign_id` | 广告活动ID | Campaign 唯一标识 | 与 campaign 主层关联 |
| `campaign_name` | `campaign_name` | `campaign_name` | 广告活动名称 | 活动名称 | 结果展示字段 |
| `placement` | `placement_classification` | `placement_classification` | 流量位置 | 展示位置分类（Top/Detail/Other） | 位置结构分析核心 |
| `impressions` | `impressions` | `impressions` | 展示量 | 该位置展示次数 | CTR 分母 |
| `clicks` | `clicks` | `clicks` | 点击量 | 该位置点击次数 | CPC/CVR 分母 |
| `spend` | `spend`（回退 `cost`） | `cost` | 花费 | 该位置广告花费 | SP/SB 字段差异 |
| `sales` | `sales14d` | `sales_clicks`（回退 `sales`） | 归因销售额 | 该位置归因销售额 | SB 优先 clicks 归因 |
| `orders` | `purchases14d` | `purchases_clicks`（回退 `purchases`） | 归因订单量 | 该位置归因订单数 | SB 优先 clicks 归因 |

## Placement Analysis Intent

用于回答：
- 哪个位置吃掉预算但转化弱
- 哪个位置是主要产出来源
- 是否需要在位置间重分配预算

