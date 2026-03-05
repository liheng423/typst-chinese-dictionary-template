#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import os
import re
import subprocess
from pathlib import Path

import rtoml


def _sanitize_name(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_]+", "_", name)
    name = name.strip("_")
    if not name:
        name = "col"
    if name[0].isdigit():
        name = f"col_{name}"
    return name


def _unique_names(names: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    out: list[str] = []
    for n in names:
        base = n
        idx = seen.get(base, 0)
        if idx:
            n = f"{base}_{idx}"
        seen[base] = idx + 1
        out.append(n)
    return out


def _read_header(csv_path: Path, delimiter: str, encoding: str) -> list[str]:
    with csv_path.open("r", encoding=encoding, newline="") as f:
        reader = csv.reader(f, delimiter=delimiter)
        header = next(reader, None)
    if not header:
        raise ValueError("CSV header is missing or empty.")
    return header


def _psql_cmd(args: argparse.Namespace) -> list[str]:
    cmd = ["psql", "-v", "ON_ERROR_STOP=1"]
    if args.host:
        cmd += ["-h", args.host]
    if args.port:
        cmd += ["-p", str(args.port)]
    if args.user:
        cmd += ["-U", args.user]
    if args.database:
        cmd += ["-d", args.database]
    return cmd


def _load_config(path: str | None) -> dict:
    if not path:
        return {}
    cfg_path = Path(path).expanduser().resolve()
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config not found: {cfg_path}")
    with cfg_path.open("r", encoding="utf-8") as f:
        return rtoml.load(f)


def _pick(cli_val, cfg_val, env_val, default_val):
    if cli_val not in (None, ""):
        return cli_val
    if cfg_val not in (None, ""):
        return cfg_val
    if env_val not in (None, ""):
        return env_val
    return default_val


def _run(cmd: list[str], env: dict[str, str]) -> None:
    subprocess.run(cmd, check=True, env=env)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import a CSV into PostgreSQL with auto table creation."
    )
    parser.add_argument("csv_path", help="Path to CSV file.")
    parser.add_argument("--config", default="", help="Path to TOML config file.")
    parser.add_argument("--schema", default=None, help="Target schema. Default: public")
    parser.add_argument("--table", default=None, help="Target table name. Default: CSV file stem")
    parser.add_argument("--delimiter", default=None, help="CSV delimiter. Default: ,")
    parser.add_argument("--encoding", default=None, help="CSV encoding. Default: utf-8")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--database", default=None)
    parser.add_argument("--user", default=None)
    parser.add_argument("--password", default=None)
    args = parser.parse_args()

    cfg = _load_config(args.config)
    cfg_db = cfg.get("db", {})
    cfg_csv = cfg.get("csv", {})
    cfg_table = cfg.get("table", {})

    args.schema = _pick(args.schema, cfg_table.get("schema"), None, "public")
    args.table = _pick(args.table, cfg_table.get("name"), None, "")
    args.delimiter = _pick(args.delimiter, cfg_csv.get("delimiter"), None, ",")
    args.encoding = _pick(args.encoding, cfg_csv.get("encoding"), None, "utf-8")

    args.host = _pick(args.host, cfg_db.get("host"), os.getenv("PGHOST"), "/tmp")
    args.port = int(_pick(args.port, cfg_db.get("port"), os.getenv("PGPORT"), "5432"))
    args.database = _pick(args.database, cfg_db.get("database"), os.getenv("PGDATABASE"), "postgres")
    args.user = _pick(args.user, cfg_db.get("user"), os.getenv("PGUSER"), "")
    args.password = _pick(args.password, cfg_db.get("password"), os.getenv("PGPASSWORD"), "")

    csv_path = Path(args.csv_path).expanduser().resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    table = args.table or csv_path.stem
    table = _sanitize_name(table)

    header = _read_header(csv_path, args.delimiter, args.encoding)
    columns = _unique_names([_sanitize_name(h) for h in header])

    full_table = f"{args.schema}.{table}"
    cols_sql = ", ".join(f"{c} TEXT" for c in columns)
    create_sql = f"DROP TABLE IF EXISTS {full_table}; CREATE TABLE {full_table} (id BIGSERIAL PRIMARY KEY, {cols_sql});"

    env = os.environ.copy()
    if args.password:
        env["PGPASSWORD"] = args.password

    base_cmd = _psql_cmd(args)
    _run(base_cmd + ["-c", create_sql], env)

    col_list = ", ".join(columns)
    copy_sql = (
        f"\\copy {full_table} ({col_list}) "
        f"FROM '{csv_path}' WITH (FORMAT csv, HEADER true, DELIMITER '{args.delimiter}', ENCODING '{args.encoding}')"
    )
    _run(base_cmd + ["-c", copy_sql], env)

    print(f"[INFO] Imported {csv_path} into {full_table}")


if __name__ == "__main__":
    main()
