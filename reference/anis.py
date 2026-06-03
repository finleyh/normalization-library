"""ANI (phone-number) normalization helpers for polars DataFrames.

Mirrors the shape of `emails.py`: a Normalizer class, a module-level
singleton, and a `normalize_ani_column` helper that returns a new
DataFrame with the target column rewritten to canonical E.164.
"""

import polars as pl

from meeseeks_box.utils.normalize.rules.ani_rules import AniNormalizingRules


class AniNormalizer:
    def __init__(self, default_region: str = "US"):
        self.default_region = default_region

    def apply(self, ani: str) -> str | None:
        return AniNormalizingRules.to_e164(ani, self.default_region)


# module level — instantiated once
_normalizer = AniNormalizer()


def normalize_ani_column(df: pl.DataFrame, column: str = "value") -> pl.DataFrame:
    """Rewrite `column` to E.164. Unparseable rows become null."""
    return df.with_columns(
        pl.col(column)
        .map_elements(_normalizer.apply, return_dtype=pl.Utf8)
        .alias(column)
    )
