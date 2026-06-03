"""US TIN normalization. Canonical form is 9 raw decimal digits.

Handles any 9-digit US Taxpayer Identification Number by shape: SSN, ITIN,
and ATIN all share the 9-digit form. Validation here is shape-only (exactly
9 digits after stripping separators); issuance rules are not enforced.

NOTE: normalized TINs (especially SSNs) are sensitive plaintext PII. Handle
and store with care.
"""

from __future__ import annotations

from typing import Optional

from .base import BaseNormalizer, blank_to_none
from .rules.us_tin_rules import UsTinNormalizationRules


class UsTinNormalizer(BaseNormalizer):
    def apply(self, value: str) -> Optional[str]:
        value = blank_to_none(value)
        if value is None:
            return None
        return UsTinNormalizationRules.normalize(value)


# module-level singleton — instantiated once
_normalizer = UsTinNormalizer()


def normalize_us_tin(value: str) -> Optional[str]:
    """Normalize to a 9-digit canonical US TIN. Invalid shape -> ``None``."""
    return _normalizer.apply(value)
