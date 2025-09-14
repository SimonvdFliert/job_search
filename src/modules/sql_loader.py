from __future__ import annotations
from importlib.resources import files


# We treat modules/sql/ as a package so we can bundle SQL at build time.
_SQL_PKG = "src.modules.sql"

def load_sql(filename: str) -> str:
    """Load an .sql file from modules/sql/ with UTF-8 decoding."""
    return files(_SQL_PKG).joinpath(filename).read_text(encoding="utf-8")
