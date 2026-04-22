from __future__ import annotations

from dataclasses import dataclass
import os
import re
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    database: str
    user: str
    password: str
    charset: str = "utf8"
    tables: tuple[str, ...] = ()

    @property
    def dsn(self) -> str:
        return (
            f"host={self.host} port={self.port} dbname={self.database} "
            f"user={self.user} password={self.password}"
        )


def _extract_key_values(markdown_text: str) -> dict[str, str]:
    pairs: dict[str, str] = {}

    for key, value in re.findall(r"'([^']+)':\s*'([^']*)'", markdown_text):
        pairs[key.strip()] = value.strip()

    for key, value in re.findall(r"'([^']+)':\s*(\d+)", markdown_text):
        pairs[key.strip()] = value.strip()

    return pairs


def _extract_tables(markdown_text: str) -> tuple[str, ...]:
    tables: list[str] = []
    in_table_section = False

    for raw_line in markdown_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line == "数据表":
            in_table_section = True
            continue

        if not in_table_section:
            continue

        if line.startswith("```"):
            continue

        if re.fullmatch(r"[A-Za-z0-9_]+", line):
            tables.append(line)

    return tuple(tables)


def _extract_from_toml(path: Path) -> tuple[dict[str, str], tuple[str, ...]]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    db = data.get("database", {}) if isinstance(data, dict) else {}
    tables_section = data.get("tables", {}) if isinstance(data, dict) else {}

    kv = {
        "host": str(db.get("host", "")).strip(),
        "port": str(db.get("port", "5432")).strip(),
        "database": str(db.get("database", db.get("name", "postgres"))).strip(),
        "user": str(db.get("user", "")).strip(),
        "password": str(db.get("password", "")).strip(),
        "charset": str(db.get("charset", "utf8")).strip(),
    }

    table_names = tables_section.get("names", []) if isinstance(tables_section, dict) else []
    tables: list[str] = []
    if isinstance(table_names, list):
        for item in table_names:
            raw = str(item).strip()
            if re.fullmatch(r"[A-Za-z0-9_]+", raw):
                tables.append(raw)
    return kv, tuple(tables)


def _extract_from_env_file(path: Path) -> tuple[dict[str, str], tuple[str, ...]]:
    kv: dict[str, str] = {}
    tables: list[str] = []

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key == "ADS_DB_HOST":
            kv["host"] = value
        elif key == "ADS_DB_PORT":
            kv["port"] = value
        elif key == "ADS_DB_NAME":
            kv["database"] = value
        elif key == "ADS_DB_USER":
            kv["user"] = value
        elif key == "ADS_DB_PASSWORD":
            kv["password"] = value
        elif key == "ADS_DB_CHARSET":
            kv["charset"] = value
        elif key == "ADS_DB_TABLES":
            for item in value.split(","):
                table = item.strip()
                if re.fullmatch(r"[A-Za-z0-9_]+", table):
                    tables.append(table)

    return kv, tuple(tables)


def load_database_config(
    config_markdown_path: str | Path = "database.toml",
) -> DatabaseConfig:
    path = Path(config_markdown_path)
    if not path.exists():
        raise FileNotFoundError(f"未找到数据库配置文件: {path}")

    if path.suffix.lower() == ".toml":
        kv, tables = _extract_from_toml(path)
    elif path.name == ".env" or path.suffix.lower() == ".env":
        kv, tables = _extract_from_env_file(path)
    else:
        text = path.read_text(encoding="utf-8")
        kv = _extract_key_values(text)
        tables = _extract_tables(text)

    host = os.getenv("ADS_DB_HOST", kv.get("host", ""))
    port = int(os.getenv("ADS_DB_PORT", kv.get("port", "5432")))
    database = os.getenv("ADS_DB_NAME", kv.get("database", "postgres"))
    user = os.getenv("ADS_DB_USER", kv.get("user", ""))
    password = os.getenv("ADS_DB_PASSWORD", kv.get("password", ""))
    charset = os.getenv("ADS_DB_CHARSET", kv.get("charset", "utf8"))

    missing = [k for k, v in {
        "host": host,
        "user": user,
        "password": password,
    }.items() if not v]
    if missing:
        raise ValueError(f"数据库配置缺少必要字段: {', '.join(missing)}")

    return DatabaseConfig(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        charset=charset,
        tables=tables,
    )
