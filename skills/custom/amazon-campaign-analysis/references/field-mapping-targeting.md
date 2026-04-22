# Field Mapping: Targeting（含中文字段名与含义）

## Scope

- SP 表: `amazon_ads_sp_targeting_innerbrightness`
- SB 表: `amazon_ads_sb_targeting_innerbrightness`

## Normalized Mapping

| 统一字段 | SP 字段 | SB 字段 | 中文字段名 | 字段含义 | 口径注意 |
|---|---|---|---|---|---|
| `report_date` | `date` | `date` | 日期 | 报表日期（日粒度） | 主过滤日期 |
| `campaign_id` | `campaign_id` | `campaign_id` | 广告活动ID | 所属 Campaign 标识 | 与 campaign 主层关联 |
| `campaign_name` | `campaign_name` | `campaign_name` | 广告活动名称 | 所属活动名称 | 下钻归因链接 |
| `ad_group_id` | `ad_group_id` | `ad_group_id` | 广告组ID | 所属广告组ID | 组级归因 |
| `ad_group_name` | `ad_group_name` | `ad_group_name` | 广告组名称 | 所属广告组名称 | 结果展示字段 |
| `targeting_entity_id` | `keyword_id` | `targeting_id`（回退 `keyword_id`） | 定向实体ID | 关键词/定向对象唯一标识 | SP/SB 维度键不同 |
| `targeting_text` | `targeting`（回退 `keyword`） | `targeting_text`（回退 `targeting_expression`/`keyword_text`） | 定向文本 | 定向表达式或关键词文本 | 需统一文本口径 |
| `targeting_expression` | `targeting` | `targeting_expression` | 定向表达式 | 定向规则表达式 | SP 多为简化字段 |
| `targeting_type` | `keyword_type`（回退 `match_type`） | `targeting_type`（回退 `keyword_type`） | 定向类型 | 关键词/商品/受众等类型 | SP/SB 枚举不同 |
| `match_type` | `match_type` | `match_type` | 匹配类型 | 精准/词组/广泛等 | 结构漂移分析 |
| `keyword_bid` | `keyword_bid` | `keyword_bid` | 关键词出价 | 定向当前出价 | 出价优化依据 |
| `target_status` | `ad_keyword_status` | `ad_keyword_status` | 定向状态 | 定向条目启停状态 | 状态排查必看 |
| `campaign_status` | `campaign_status` | `campaign_status` | 广告活动状态 | 所属活动状态 | 联合状态判断 |
| `impressions` | `impressions` | `impressions` | 展示量 | 定向展示次数 | CTR 分母 |
| `clicks` | `clicks` | `clicks` | 点击量 | 定向点击次数 | CPC/CVR 分母 |
| `spend` | `cost`（回退 `spend`） | `cost` | 花费 | 定向消耗金额 | SP 该表以 `cost` 为主 |
| `sales` | `sales14d` | `sales_clicks`（回退 `sales`） | 归因销售额 | 定向归因销售额 | SB 优先 clicks 归因 |
| `orders` | `purchases14d` | `purchases_clicks`（回退 `purchases`） | 归因订单量 | 定向归因订单数 | SB 优先 clicks 归因 |
| `top_of_search_is` | `top_of_search_impression_share` | `top_of_search_impression_share`（若有） | 搜索顶部展示份额 | 定向在顶部位置竞争力 | 竞争强度参考 |

## Targeting Root-Cause Focus

用于定位：
- 高花费低产出的定向对象
- 花费有点击但无销售的定向对象
- 定向表达式过宽或失真
- 出价与产出不匹配

