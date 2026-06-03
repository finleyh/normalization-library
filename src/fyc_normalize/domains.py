"""Domain / hostname normalization. Canonical form is lowercase Punycode.

See ``domain_rules.py``. Internationalized domains are converted to their
ASCII A-label form; install the ``domain`` extra (``idna``) for full IDNA2008.
"""

from __future__ import annotations

from typing import Optional

from .base import BaseNormalizer, blank_to_none
from .rules.domain_rules import DomainNormalizingRules


class DomainNormalizer(BaseNormalizer):
    def apply(self, value: str) -> Optional[str]:
        value = blank_to_none(value)
        if value is None:
            return None
        return DomainNormalizingRules.to_canonical(value)


# module-level singleton — instantiated once
_normalizer = DomainNormalizer()


def normalize_domain(value: str) -> Optional[str]:
    """Normalize a domain/hostname to lowercase Punycode. Invalid -> ``None``."""
    return _normalizer.apply(value)
