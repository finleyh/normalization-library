"""US TIN normalization rules (SSN / ITIN / ATIN — any 9-digit US TIN).

The canonical form is **9 raw decimal digits** (no dashes, no spaces) —
chosen because it is the smallest unambiguous representation and trivial to
join against in SQL or polars.

NOTE: a normalized TIN is sensitive plaintext PII. Treat any table that
stores it as sensitive.
"""

import re


class UsTinNormalizationRules:
    @staticmethod
    def strip_hyphens(local: str) -> str:
        return re.sub(r"-", "", local)

    @staticmethod
    def strip_illegalchars(local: str) -> str:
        return re.sub(r"[^\d]", "", local)

    @staticmethod
    def normalize(local: str) -> str | None:
        """Return canonical 9-digit TIN, or None if input is not a valid shape.

        Validity here is shape-only: exactly 9 decimal digits after stripping
        non-digits. We do not enforce issuance rules (e.g. SSA area numbers or
        ITIN ranges) — that is out of scope for an analytic exposure table.
        """
        if local is None:
            return None
        digits = re.sub(r"[^\d]", "", local)
        if len(digits) != 9:
            return None
        return digits
