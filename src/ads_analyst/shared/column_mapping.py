from __future__ import annotations

from typing import Iterable


def _norm(name: str) -> str:
    return name.strip().lower().replace("_", "").replace(" ", "")


COMMON_ALIASES: dict[str, tuple[str, ...]] = {
    "date": ("date", "report_date", "day", "stat_date", "日期", "时间"),
    "campaign_id": ("campaign_id", "campaignid", "广告活动id"),
    "campaign_name": (
        "campaign_name",
        "campaign",
        "campaignname",
        "广告活动",
        "广告活动名称",
    ),
    "impressions": ("impressions", "impression", "展示量", "曝光量"),
    "clicks": ("clicks", "click", "点击量"),
    "spend": ("spend", "cost", "ad_spend", "花费"),
    "sales": (
        "sales14d",
        "sales7d",
        "sales30d",
        "sales_clicks",
        "sales",
        "ad_sales",
        "attributed_sales_14d",
        "广告销售额",
    ),
    "orders": (
        "purchases14d",
        "purchases7d",
        "purchases30d",
        "purchases_clicks",
        "purchases",
        "orders",
        "ad_orders",
        "attributed_conversions_14d",
        "广告订单",
    ),
    "budget": ("campaign_budget_amount", "budget_amount", "budget", "活动预算"),
}

LAYER_ALIASES: dict[str, dict[str, tuple[str, ...]]] = {
    "placement": {
        "placement": ("placement_classification", "placement", "流量位置"),
    },
    "search_term": {
        "search_term": ("search_term", "searchterm", "搜索词"),
        "match_type": ("match_type", "keyword_type", "匹配类型"),
        "bid": ("keyword_bid", "bid", "出价"),
    },
    "targeting": {
        "targeting": (
            "targeting_text",
            "targeting_expression",
            "targeting",
            "keyword_text",
            "keyword",
            "定向文本",
        ),
        "match_type": ("match_type", "keyword_type", "targeting_type", "匹配类型"),
        "bid": ("keyword_bid", "bid", "出价"),
    },
}


def infer_mapping(columns: Iterable[str], layer: str | None = None) -> dict[str, str]:
    normalized = {_norm(col): col for col in columns}
    merged: dict[str, tuple[str, ...]] = dict(COMMON_ALIASES)

    if layer and layer in LAYER_ALIASES:
        merged.update(LAYER_ALIASES[layer])

    mapping: dict[str, str] = {}
    for logical_name, aliases in merged.items():
        for alias in aliases:
            hit = normalized.get(_norm(alias))
            if hit:
                mapping[logical_name] = hit
                break

    return mapping
