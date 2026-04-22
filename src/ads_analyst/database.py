from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from .config import DatabaseConfig

try:
    import psycopg
    from psycopg import sql
except Exception:  # pragma: no cover
    psycopg = None
    sql = None


@dataclass(frozen=True)
class TableStatus:
    table_name: str
    exists: bool
    row_count: int | None


class DatabaseClient:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._check_driver()

    def _check_driver(self) -> None:
        if psycopg is None:
            raise RuntimeError(
                "未安装 psycopg，请先执行: pip install -r requirements.txt"
            )

    def connect(self):
        return psycopg.connect(self.config.dsn)

    def ping(self) -> str:
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("select version()")
                row = cur.fetchone()
                return str(row[0]) if row else "unknown"

    def list_table_status(self, tables: tuple[str, ...]) -> list[TableStatus]:
        status_list: list[TableStatus] = []
        with self.connect() as conn:
            with conn.cursor() as cur:
                for table in tables:
                    cur.execute("select to_regclass(%s)", (table,))
                    exists = cur.fetchone()[0] is not None
                    if not exists:
                        status_list.append(
                            TableStatus(table_name=table, exists=False, row_count=None)
                        )
                        continue

                    cur.execute(
                        sql.SQL("select count(*) from {}").format(sql.Identifier(table))
                    )
                    row_count = int(cur.fetchone()[0])
                    status_list.append(
                        TableStatus(table_name=table, exists=True, row_count=row_count)
                    )

        return status_list

    def get_table_columns(self, table: str) -> list[str]:
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select column_name
                    from information_schema.columns
                    where table_schema = current_schema()
                      and table_name = %s
                    order by ordinal_position
                    """,
                    (table,),
                )
                return [str(r[0]) for r in cur.fetchall()]

    def fetch_rows(
        self,
        table: str,
        columns: list[str],
        date_column: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict[str, Any]]:
        if not columns:
            return []

        where_clauses = []
        params: list[Any] = []

        if date_column and start_date:
            where_clauses.append(
                sql.SQL("{} >= %s").format(sql.Identifier(date_column))
            )
            params.append(start_date)
        if date_column and end_date:
            where_clauses.append(
                sql.SQL("{} <= %s").format(sql.Identifier(date_column))
            )
            params.append(end_date)

        query = sql.SQL("select {} from {}").format(
            sql.SQL(", ").join(sql.Identifier(c) for c in columns),
            sql.Identifier(table),
        )

        if where_clauses:
            query += sql.SQL(" where ") + sql.SQL(" and ").join(where_clauses)

        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

        return [{col: row[idx] for idx, col in enumerate(columns)} for row in rows]

