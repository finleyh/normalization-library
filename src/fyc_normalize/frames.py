"""Optional DataFrame column helpers.

These are thin conveniences over the pure ``normalize_*`` functions. They are
NOT imported by the core package and pull in polars/pandas only when called,
so the library stays dependency-free unless you actually use a DataFrame.

    from fyc_normalize.frames import normalize_email_column
    df = normalize_email_column(df, "email")     # works for polars OR pandas

Or build your own one-liner — the core functions are the real API:

    df["email"] = df["email"].map(normalize_email)                  # pandas
    df.with_columns(pl.col("email").map_elements(normalize_email))  # polars
"""

from __future__ import annotations

from typing import Callable, Optional

from .anis import normalize_ani
from .domains import normalize_domain
from .emails import normalize_email
from .ips import normalize_cidr, normalize_ip
from .us_tins import normalize_us_tin
from .usernames import normalize_username


def _is_polars(df) -> bool:
    return type(df).__module__.split(".")[0] == "polars"


def normalize_column(df, column: str, fn: Callable[[str], Optional[str]]):
    """Return a new DataFrame with ``column`` rewritten by ``fn``.

    Detects polars vs pandas automatically. Unparseable rows become null/None.
    """
    if _is_polars(df):
        import polars as pl

        return df.with_columns(
            pl.col(column).map_elements(fn, return_dtype=pl.Utf8).alias(column)
        )
    # assume pandas-like
    out = df.copy()
    out[column] = out[column].map(fn)
    return out


def normalize_email_column(df, column: str = "value"):
    return normalize_column(df, column, normalize_email)


def normalize_ani_column(df, column: str = "value"):
    return normalize_column(df, column, normalize_ani)


def normalize_us_tin_column(df, column: str = "value"):
    return normalize_column(df, column, normalize_us_tin)


def normalize_ip_column(df, column: str = "value"):
    return normalize_column(df, column, normalize_ip)


def normalize_cidr_column(df, column: str = "value"):
    return normalize_column(df, column, normalize_cidr)


def normalize_domain_column(df, column: str = "value"):
    return normalize_column(df, column, normalize_domain)


def normalize_username_column(df, column: str = "value"):
    return normalize_column(df, column, normalize_username)
