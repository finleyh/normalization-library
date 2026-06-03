"""ANI (phone-number) normalization. Canonical form is E.164 (e.g. +14155550123)."""

from __future__ import annotations

from typing import Optional

from .base import BaseNormalizer, blank_to_none
from .rules.ani_rules import AniNormalizingRules


class AniNormalizer(BaseNormalizer):
    def __init__(self, default_region: str = "US"):
        self.default_region = default_region

    def apply(self, value: str, region: Optional[str] = None) -> Optional[str]:
        value = blank_to_none(value)
        if value is None:
            return None
        return AniNormalizingRules.to_e164(value, region or self.default_region)


# module-level singleton — instantiated once
_normalizer = AniNormalizer()


def normalize_ani(value: str, region: str = "US") -> Optional[str]:
    """Normalize a phone number to E.164. Unparseable input -> ``None``."""
    return _normalizer.apply(value, region)
