"""Username normalization helpers for polars DataFrames.

Mirrors the shape of `emails.py`. Output canonical form is the NFKC-normalized,
lower-cased, trimmed username with invisible (Cf / Cc) characters removed —
see `username_rules.py` for the rationale.
"""

import polars as pl

from meeseeks_box.utils.normalize.rules.username_rules import UsernameNormalizingRules


class UsernameNormalizer:
    def apply(self, username: str) -> str | None:
        return UsernameNormalizingRules.to_canonical(username)


# module level — instantiated once
_normalizer = UsernameNormalizer()


def normalize_username_column(df: pl.DataFrame, column: str = "value") -> pl.DataFrame:
    """Rewrite `column` to NFKC canonical form. Empty rows become null."""
    return df.with_columns(
        pl.col(column)
        .map_elements(_normalizer.apply, return_dtype=pl.Utf8)
        .alias(column)
    )
