"""Username normalization. Canonical form is NFKC-normalized, lower-cased,
trimmed, with invisible (Cf / Cc) characters removed.
"""

from __future__ import annotations

from typing import Optional

from .base import BaseNormalizer, blank_to_none
from .rules.username_rules import UsernameNormalizingRules


class UsernameNormalizer(BaseNormalizer):
    def apply(self, value: str) -> Optional[str]:
        value = blank_to_none(value)
        if value is None:
            return None
        return UsernameNormalizingRules.to_canonical(value)


# module-level singleton — instantiated once
_normalizer = UsernameNormalizer()


def normalize_username(value: str) -> Optional[str]:
    """Normalize to NFKC canonical form. Empty -> ``None``."""
    return _normalizer.apply(value)
