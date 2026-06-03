"""US TIN normalization helpers for polars DataFrames.

Mirrors the shape of `emails.py`. Output canonical form is 9 raw decimal
digits (SSN / ITIN / ATIN) — see `us_tin_rules.py`. Per design decision, the
analytic table now stores TINs in plaintext normal form rather than hashed;
treat the table as sensitive.
"""

import polars as pl

from meeseeks_box.utils.normalize.rules.us_tin_rules import UsTinNormalizationRules


class UsTinNormalizer:
    def apply(self, tin: str) -> str | None:
        return UsTinNormalizationRules.normalize(tin)


# module level — instantiated once
_normalizer = UsTinNormalizer()


def normalize_us_tin_column(df: pl.DataFrame, column: str = "value") -> pl.DataFrame:
    """Rewrite `column` to 9-digit canonical US TIN. Invalid-shape rows become null."""
    return df.with_columns(
        pl.col(column)
        .map_elements(_normalizer.apply, return_dtype=pl.Utf8)
        .alias(column)
    )
