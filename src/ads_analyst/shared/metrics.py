from __future__ import annotations

from decimal import Decimal
from typing import Any


def safe_float(value: Any) -> float:
    if value is None or isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float, Decimal)):
        return float(value)

    text = str(value).strip()
    if not text or text in {"-", "--", "nan", "NaN", "None"}:
        return 0.0

    cleaned = text.replace(",", "").replace("$", "").replace("%", "")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def ctr(clicks: float, impressions: float) -> float:
    return safe_ratio(clicks, impressions)


def cpc(spend: float, clicks: float) -> float:
    return safe_ratio(spend, clicks)


def cvr(orders: float, clicks: float) -> float:
    return safe_ratio(orders, clicks)


def acos(spend: float, sales: float) -> float:
    return safe_ratio(spend, sales)


def roas(sales: float, spend: float) -> float:
    return safe_ratio(sales, spend)
