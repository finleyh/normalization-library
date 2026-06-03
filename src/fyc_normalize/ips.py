"""IP-address normalization (IPv4 and IPv6), plus CIDR/network normalization.

Canonical form is the stdlib ``ipaddress`` representation: dotted-decimal for
IPv4, RFC 5952 (lowercase, zero-compressed) for IPv6. CIDR networks normalize
to ``network/prefix`` with host bits masked. See ``ip_rules.py``.
"""

from __future__ import annotations

from typing import Optional

from .base import BaseNormalizer, blank_to_none
from .rules.ip_rules import CidrNormalizingRules, IpNormalizingRules


class IpNormalizer(BaseNormalizer):
    def apply(self, value: str) -> Optional[str]:
        value = blank_to_none(value)
        if value is None:
            return None
        return IpNormalizingRules.to_canonical(value)


class CidrNormalizer(BaseNormalizer):
    def apply(self, value: str) -> Optional[str]:
        value = blank_to_none(value)
        if value is None:
            return None
        return CidrNormalizingRules.to_canonical(value)


# module-level singletons — instantiated once
_normalizer = IpNormalizer()
_cidr_normalizer = CidrNormalizer()


def normalize_ip(value: str) -> Optional[str]:
    """Normalize an IPv4 or IPv6 address to canonical form. Invalid -> ``None``."""
    return _normalizer.apply(value)


def normalize_cidr(value: str) -> Optional[str]:
    """Normalize a CIDR/network to ``network/prefix`` (host bits masked).

    A CIDR prefix is required; a bare address with no ``/prefix`` returns
    ``None`` (use ``normalize_ip`` for bare addresses). Invalid -> ``None``.
    """
    return _cidr_normalizer.apply(value)
