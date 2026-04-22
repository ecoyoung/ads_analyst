# Field Mapping: Search Term（含中文字段名与含义）

## Scope

- SP 表: `amazon_ads_sp_search_term_innerbrightness`
- SB 表: `amazon_ads_sb_search_term_innerbrightness`

## Normalized Mapping

| 统一字段 | SP 字段 | SB 字段 | 中文字段名 | 字段含义 | 口径注意 |
|---|---|---|---|---|---|
| `report_date` | `date` | `date` | 日期 | 报表日期（日粒度） | 主过滤日期 |
| `campaign_id` | `campaign_id` | `campaign_id` | 广告活动ID | 所属 Campaign 标识 | 与 campaign 主层关联 |
| `campaign_name` | `campaign_name` | `campaign_name` | 广告活动名称 | 所属活动名称 | 下钻归因链接 |
| `ad_group_name` | `ad_group_name` | `ad_group_name` | 广告组名称 | 所属 ad group | 组级归因 |
| `search_term` | `search_term` | `search_term` | 搜索词 | 用户真实搜索词 | 根因定位核心字段 |
| `match_type` | `match_type` | `match_type` | 匹配类型 | 精准/词组/广泛等 | 结构漂移分析 |
| `keyword_text` | `keyword` | `keyword_text` | 关键词文本 | 投放关键词文本 | SP/SB 字段名不同 |
| `keyword_bid` | `keyword_bid` | `keyword_bid` | 关键词出价 | 关键词当前出价 | 出价优化依据 |
| `impressions` | `impressions` | `impressions` | 展示量 | 搜索词展示次数 | CTR 分母 |
| `clicks` | `clicks` | `clicks` | 点击量 | 搜索词点击次数 | CPC/CVR 分母 |
| `spend` | `spend`（回退 `cost`） | `cost` | 花费 | 搜索词消耗金额 | SP/SB 字段差异 |
| `sales` | `sales14d` | `sales_clicks`（回退 `sales`） | 归因销售额 | 搜索词归因销售额 | SB 优先 clicks 归因 |
| `orders` | `purchases14d` | `purchases_clicks`（回退 `purchases`） | 归因订单量 | 搜索词归因订单数 | SB 优先 clicks 归因 |
| `campaign_status` | `campaign_status` | `campaign_status` | 广告活动状态 | 所属活动状态 | 判断是否受状态影响 |

## Root-Cause Focus

用于定位：
- 高花费低产出词
- 花费有点击但无销售词
- 匹配类型效率劣化
- 关键词出价与产出不匹配

