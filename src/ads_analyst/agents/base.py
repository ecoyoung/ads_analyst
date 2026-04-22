from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from typing import Any

from ..database import DatabaseClient
from ..shared.column_mapping import infer_mapping
from ..shared.metrics import safe_float


class BaseAnalysisAgent:
    layer: str | None = None

    def __init__(self, db: DatabaseClient):
        self.db = db

    def _safe_date(self, value: Any) -> date | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value

        text = str(value).strip()
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        return None

    def _read_rows(
        self,
        table: str,
        start_date: date | None,
        end_date: date | None,
    ) -> tuple[list[dict[str, Any]], dict[str, str]]:
        columns = self.db.get_table_columns(table)
        mapping = infer_mapping(columns, layer=self.layer)
        if "campaign_name" not in mapping:
            return [], mapping

        read_columns = sorted(set(mapping.values()))
        rows = self.db.fetch_rows(table=table, columns=read_columns)

        filtered: list[dict[str, Any]] = []
        date_column = mapping.get("date")
        for row in rows:
            if date_column:
                row_date = self._safe_date(row.get(date_column))
                if (start_date or end_date) and row_date is None:
                    continue
                if start_date and row_date and row_date < start_date:
                    continue
                if end_date and row_date and row_date > end_date:
                    continue
            filtered.append(row)
        return filtered, mapping

    def _aggregate_basic_metrics(
        self,
        rows: list[dict[str, Any]],
        mapping: dict[str, str],
    ) -> dict[str, dict[str, float]]:
        acc: dict[str, dict[str, float]] = defaultdict(
            lambda: {
                "spend": 0.0,
                "sales": 0.0,
                "orders": 0.0,
                "impressions": 0.0,
                "clicks": 0.0,
                "budget": 0.0,
            }
        )

        for row in rows:
            campaign = str(row.get(mapping["campaign_name"], "")).strip() or "UNKNOWN"
            metric = acc[campaign]
            metric["spend"] += safe_float(row.get(mapping.get("spend", "")))
            metric["sales"] += safe_float(row.get(mapping.get("sales", "")))
            metric["orders"] += safe_float(row.get(mapping.get("orders", "")))
            metric["impressions"] += safe_float(row.get(mapping.get("impressions", "")))
            metric["clicks"] += safe_float(row.get(mapping.get("clicks", "")))
            metric["budget"] += safe_float(row.get(mapping.get("budget", "")))

        return acc
